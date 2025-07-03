import secrets, jwt, uuid
from datetime import datetime, timedelta
from flask import request, jsonify, current_app, make_response, Blueprint
from app.models import RefreshToken, db, Usuario, ConfiguracionPago, Pago
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.email_utils import enviar_email  # ruta según tu estructura
from flask_cors import cross_origin
from app.utils.cors_utils import cors_jwt_route


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email y password requeridos"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not check_password_hash(usuario.password, password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Access token (15 min)
    access_payload = {
        "sub": usuario.id,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    access_token = jwt.encode(access_payload, current_app.config['SECRET_KEY'], algorithm="HS256")

    # Refresh token (aleatorio y largo)
    refresh_token_plano = secrets.token_urlsafe(64)
    refresh_token_hash = generate_password_hash(refresh_token_plano)

    nuevo_token = RefreshToken(
        token_hash=refresh_token_hash,
        usuario_id=usuario.id,
        expira_en=datetime.utcnow() + timedelta(days=7)
    )
    db.session.add(nuevo_token)
    db.session.commit()

    # 🔹 Incluir es_admin en la respuesta
    response = make_response(jsonify({
        "access_token": access_token,
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "es_admin": usuario.es_admin
        }
    }))
    response.set_cookie(
        "refresh_token", refresh_token_plano,
        httponly=True, secure=True, samesite='Strict',
        max_age=7 * 24 * 60 * 60
    )

    return response




@auth_bp.route('/refresh', methods=['POST'])
def refresh_access_token():
    refresh_token_cookie = request.cookies.get('refresh_token')

    if not refresh_token_cookie:
        return jsonify({"error": "No se proporcionó refresh token"}), 401

    # Buscar todos los tokens no revocados
    tokens_activos = RefreshToken.query.filter_by(revocado=False).all()

    # Buscar si alguno coincide
    token_valido = None
    for token in tokens_activos:
        if token.verificar_token(refresh_token_cookie):
            token_valido = token
            break

    if not token_valido:
        return jsonify({"error": "Refresh token inválido o revocado"}), 403

    if datetime.utcnow() > token_valido.expira_en:
        return jsonify({"error": "Refresh token expirado"}), 403

    usuario = Usuario.query.get(token_valido.usuario_id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Emitir nuevo access token
    access_payload = {
        "sub": usuario.id,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }

    nuevo_access_token = jwt.encode(access_payload, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "access_token": nuevo_access_token,
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    refresh_token_cookie = request.cookies.get('refresh_token')

    if not refresh_token_cookie:
        return jsonify({"mensaje": "No había token para cerrar sesión"}), 200

    # Buscar y revocar el token si está activo
    tokens = RefreshToken.query.filter_by(revocado=False).all()

    for token in tokens:
        if token.verificar_token(refresh_token_cookie):
            token.revocado = True
            token.expira_en = datetime.utcnow()  # invalida de inmediato
            db.session.commit()
            break

    # Borrar la cookie del lado del cliente
    response = make_response(jsonify({"mensaje": "Sesión cerrada exitosamente"}))
    response.set_cookie("refresh_token", "", expires=0, httponly=True, secure=True, samesite='Strict')

    return response

@auth_bp.route("/registro", methods=["POST"])
def registrar_usuario():
    print("📥 Llegó una solicitud a /registro")

    try:
        data = request.get_json()
        print("📨 Datos recibidos:", data)

        nombre = data.get("nombre")
        telefono = data.get("telefono")
        email = data.get("email")
        password = data.get("password")

        if not nombre or not telefono or not email or not password:
            print("⚠️ Falta algún campo")
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        if Usuario.query.filter_by(email=email).first():
            print("⚠️ Usuario ya existe:", email)
            return jsonify({"error": "Ese usuario ya existe"}), 409

        usuario = Usuario(
            nombre=nombre,
            telefono=telefono,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(usuario)
        db.session.commit()

        print("✅ Usuario guardado:", email)
        return jsonify({"mensaje": "Usuario creado correctamente"}), 201

    except Exception as e:
        print("🔥 Error al registrar:", e)
        return jsonify({"error": "Error interno al registrar"}), 500


    

@auth_bp.route('/recuperar', methods=['POST'])
def recuperar_password():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Falta el email"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "Ese correo no está registrado"}), 404

    # Generar token único
    token = str(uuid.uuid4())
    usuario.token_recuperacion = token
    usuario.token_expira = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    # Armá el enlace con tu dominio real
    enlace = f"https://tusitio.com/restablecer.html?token={token}"

    # Email en formato texto (también podés usar msg.html)
    mensaje = f"""
Hola {usuario.nombre or "Usuario"},

Recibimos una solicitud para restablecer tu contraseña en Turnos Pádel 🎾

Para crear una nueva, hacé clic en el siguiente enlace:

{enlace}

Este enlace expira en 1 hora. Si no solicitaste este cambio, ignorá este mensaje.

— El equipo de Turnos Pádel
"""

    try:
        enviar_email(destinatario=usuario.email, asunto="Recuperá tu contraseña", cuerpo=mensaje)
        return jsonify({"mensaje": "Te enviamos un correo con instrucciones para restablecer tu contraseña"}), 200
    except Exception as e:
        return jsonify({"error": "No se pudo enviar el correo. Intentá más tarde."}), 500


@auth_bp.route('/configuracion-pago', methods=["GET", "OPTIONS"])
@cors_jwt_route(methods=["GET"])
def obtener_configuracion_pago():
    config = ConfiguracionPago.query.first()

    if not config:
        # Se crea por primera vez con valores por defecto
        config = ConfiguracionPago(
            destinatario="CHANGEIT",
            cbu="000000000000CHANGEIT",
            monto_esperado=0.0,
            tiempo_maximo_minutos=30
        )
        db.session.add(config)
        db.session.commit()

    return jsonify({
        "destinatario": config.destinatario,
        "cbu": config.cbu,
        "monto_esperado": config.monto_esperado,
        "tiempo_maximo_minutos": config.tiempo_maximo_minutos
    }), 200

# 💾 Guardar o actualizar configuración
@auth_bp.route('/configuracion-pago', methods=["POST", "OPTIONS"])
@cors_jwt_route(methods=["POST"])
def guardar_configuracion_pago():
    data = request.get_json()
    config = ConfiguracionPago.query.first()

    if not config:
        config = ConfiguracionPago()
        db.session.add(config)

    config.destinatario = data.get("destinatario", "")
    config.cbu = data.get("cbu", "")
    config.monto_esperado = data.get("monto_esperado", 0.0)
    config.tiempo_maximo_minutos = data.get("tiempo_maximo_minutos", 30)

    db.session.commit()

    return jsonify({"mensaje": "Configuración guardada correctamente ✅"}), 200

@auth_bp.route("/pagos", methods=["GET", "OPTIONS"])
@cors_jwt_route(methods=["GET"])
def listar_pagos():
    pagos = Pago.query.join(Usuario).add_columns(
        Pago.id,
        Pago.fecha,
        Pago.monto,
        Pago.estado,
        Pago.cbu,
        Usuario.email.label("usuario_email")
    ).order_by(Pago.fecha.desc()).all()

    resultado = []
    for _, id, fecha, monto, estado, cbu, usuario_email in pagos:
        resultado.append({
            "id": id,
            "fecha": fecha.isoformat() if fecha else None,
            "monto": monto,
            "estado": estado,
            "cbu": cbu,
            "usuario_email": usuario_email
        })

    return jsonify(resultado), 200

@auth_bp.route("/pagos/<int:pago_id>/validar", methods=["POST", "OPTIONS"])
@cors_jwt_route(methods=["POST"])
def validar_pago(pago_id):
    pago = Pago.query.get_or_404(pago_id)

    if pago.estado == "validado":
        return jsonify({"mensaje": "El pago ya está validado."}), 200

    pago.estado = "validado"
    db.session.commit()

    return jsonify({"mensaje": "✅ Pago marcado como validado."}), 200
