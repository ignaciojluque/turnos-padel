from flask import Blueprint, request, jsonify, g, current_app, send_file, abort
from datetime import datetime, timedelta, time
from werkzeug.utils import secure_filename
import os, logging
from app.models import db, Turno, Comprobante
from app.utils.cors_utils import cors_jwt_route
from app.utils.jwt_utils import jwt_required
from app.utils.comprobantes_utils import procesar_comprobante
from app.utils.turnos_utils import revertir_turno
from calendar import monthrange
from flask_cors import cross_origin
from app.utils.fake_utils import procesar_comprobante_simulado
from sqlalchemy.exc import IntegrityError
from io import BytesIO


logger = logging.getLogger(__name__)

EXTENSIONES_PERMITIDAS = {'.pdf', '.png', '.jpg', '.jpeg', '.webp', '.bmp'}
MIMETYPES_PERMITIDOS = {
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/webp',
    'image/bmp'
}

turnos_bp = Blueprint('turnos', __name__)

VALOR_TUNO = 14000


@turnos_bp.route('/crear', methods=['POST'])
@jwt_required
def crear_turno():
    data = request.get_json()
    profesor_id = data.get('profesor_id')
    fecha_str = data.get('fecha')
    hora_str = data.get('hora')

    if not profesor_id or not fecha_str or not hora_str:
        return jsonify({"error": "Se requieren profesor_id, fecha y hora"}), 400

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora = datetime.strptime(hora_str, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

    nuevo_turno = Turno(
        fecha=fecha,
        hora=hora,
        estado="pendiente",
        profesor_id=profesor_id,
        usuario_id=g.usuario_actual.id
    )
    db.session.add(nuevo_turno)
    db.session.commit()

    return jsonify({"mensaje": "Turno creado correctamente"}), 201


@turnos_bp.route('/mios', methods=['GET'])
@jwt_required
def listar_turnos_del_usuario():
    usuario = g.usuario_actual

    turnos = Turno.query.filter_by(usuario_id=usuario.id).order_by(Turno.fecha, Turno.hora).all()

    resultados = []
    for turno in turnos:
        resultados.append({
            "id": turno.id,
            "fecha": turno.fecha.isoformat(),
            "hora": turno.hora.strftime("%H:%M"),
            "estado": turno.estado,
            "profesor_id": turno.profesor_id
        })

    return jsonify({"turnos": resultados}), 200


@turnos_bp.route('/<int:turno_id>/pagar', methods=['POST'])
@jwt_required
def generar_pago(turno_id):
    usuario = g.usuario_actual
    turno = Turno.query.filter_by(id=turno_id, usuario_id=usuario.id).first()

    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404

    if turno.estado != "pendiente":
        return jsonify({"error": "Este turno no está disponible para pagar"}), 400

    sdk = mercadopago.SDK(current_app.config['MERCADO_PAGO_TOKEN'])

    preferencia = {
        "items": [{
            "title": f"Turno con profesor {turno.profesor_id} el {turno.fecha} a las {turno.hora.strftime('%H:%M')}",
            "quantity": 1,
            "unit_price": VALOR_TUNO
        }],
        "external_reference": str(turno.id),
        "notification_url": "https://tuservidor.com/webhook/mercadopago"
    }

    resultado = sdk.preference().create(preferencia)
    link_pago = resultado["response"]["init_point"]

    return jsonify({"pago_url": link_pago}), 200


@turnos_bp.route('/<int:turno_id>/verificar-pago', methods=['GET'])
@jwt_required
def verificar_estado_pago(turno_id):
    usuario = g.usuario_actual
    turno = Turno.query.filter_by(id=turno_id, usuario_id=usuario.id).first()

    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404

    sdk = mercadopago.SDK(current_app.config['MERCADO_PAGO_TOKEN'])

    filtros = {
        "external_reference": str(turno.id)
    }
    resultado = sdk.payment().search(filtros)

    pagos = resultado["response"]["results"]

    if not pagos:
        return jsonify({"estado": "sin pagos asociados"}), 200

    ultimo_pago = pagos[0]["payment"]
    estado = ultimo_pago["status"]
    detalle = {
        "id_pago": ultimo_pago["id"],
        "estado": estado,
        "fecha": ultimo_pago["date_created"],
        "monto": ultimo_pago["transaction_amount"]
    }

    return jsonify({"pago": detalle}), 200


@turnos_bp.route('/disponibles', methods=['GET'])
@jwt_required
def turnos_disponibles():
    profesor_id = request.args.get('profesor_id', type=int)
    if not profesor_id:
        return jsonify({"error": "Se requiere profesor_id"}), 400

    inicio_str = request.args.get("inicio")
    fin_str = request.args.get("fin")

    if inicio_str and fin_str:
        try:
            inicio = datetime.strptime(inicio_str, "%Y-%m-%d").date()
            fin = datetime.strptime(fin_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Fechas inválidas"}), 400
    else:
        hoy = datetime.utcnow().date()
        _, dias_mes = monthrange(hoy.year, hoy.month)
        inicio = hoy
        fin = hoy + timedelta(days=dias_mes - hoy.day + 1)

    ahora = datetime.utcnow()

    turnos = Turno.query.filter(
        Turno.profesor_id == profesor_id,
        Turno.fecha >= inicio,
        Turno.fecha < fin,
        Turno.estado != "cancelado"
    ).all()

    resultado = []
    for turno in turnos:
        dt_turno = datetime.combine(turno.fecha, turno.hora)
        if dt_turno < ahora:
            continue  # ⏭️ saltamos turnos vencidos

        resultado.append({
            "id": turno.id,
            "fecha": turno.fecha.isoformat(),
            "hora": turno.hora.strftime("%H:%M"),
            "estado": "ocupado" if turno.estado != "libre" else "libre",
            "estado_pago": turno.estado_pago,
            "ocupado": turno.estado != "libre"
        })

    return jsonify({"turnos": resultado}), 200

@turnos_bp.route('/reservar', methods=['POST'])
@jwt_required
def reservar_turno():
    data = request.get_json()
    turno_id = data.get("turno_id")

    if not turno_id:
        return jsonify({"error": "Falta el turno_id"}), 400

    try:
        turno_id = int(turno_id)
    except ValueError:
        return jsonify({"error": "turno_id inválido"}), 400

    turno = Turno.query.get(turno_id)
    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404
    if turno.usuario_id != g.usuario_actual.id:
        return jsonify({"error": "Este turno ya fue reservado por otra persona."}), 403
    if turno.estado != "pendiente":
        return jsonify({"error": "El turno no está en estado pendiente"}), 400
    if turno.estado_pago != "subido":
        return jsonify({"error": "Antes de confirmar, necesitás subir el comprobante."}), 400

    turno.estado = "confirmado"
    turno.fecha_expiracion = None

    db.session.commit()

    return jsonify({"mensaje": "✅ Turno confirmado con éxito", "turno_id": turno.id})



@turnos_bp.route('/reservar-temporal', methods=['POST'])
@jwt_required
def reservar_temporal():
    data = request.get_json()
    turno_id = data.get("turno_id")

    if not turno_id:
        return jsonify({"error": "Falta el turno_id"}), 400

    try:
        turno_id = int(turno_id)
    except ValueError:
        return jsonify({"error": "turno_id inválido"}), 400

    turno = Turno.query.get(turno_id)
    if not turno or turno.estado != "libre":
        return jsonify({"error": "Turno inválido o no disponible"}), 400

    turno.usuario_id = g.usuario_actual.id
    turno.estado = "pendiente"
    turno.estado_pago = "pendiente"
    turno.fecha_expiracion = datetime.utcnow() + timedelta(minutes=15)

    db.session.commit()

    return jsonify({
        "mensaje": "Turno reservado temporalmente",
        "turno_id": turno.id,
        "alias": "turnospadel.alias.mp",
        "limite_minutos": 15
    })

@turnos_bp.route('/subir-comprobante', methods=['POST'])
@jwt_required
def subir_comprobante():
    from app.models import ConfiguracionPago  # asegurar import
    import tempfile

    usuario = g.usuario_actual
    usar_simulacion = usuario.modo_test or current_app.config.get("MODO_TEST_GLOBAL", False)

    turno_id = request.form.get("turno_id")
    try:
        turno_id = int(turno_id)
    except (TypeError, ValueError):
        return jsonify({"error": "turno_id inválido"}), 400

    archivo = request.files.get("comprobante")
    if not turno_id or not archivo:
        return jsonify({"error": "Faltan datos: seleccioná comprobante y turno."}), 400

    filename = secure_filename(archivo.filename)
    ext = os.path.splitext(filename)[1].lower()
    mimetype = archivo.mimetype

    if ext not in EXTENSIONES_PERMITIDAS:
        return jsonify({"error": f"Extensión no permitida ({ext})"}), 400
    if mimetype not in MIMETYPES_PERMITIDOS:
        return jsonify({"error": f"Mimetype no permitido ({mimetype})"}), 400

    # 🛡️ Límite de tamaño
    archivo.seek(0, os.SEEK_END)
    tamano_mb = archivo.tell() / (1024 * 1024)
    archivo.seek(0)
    MAX_MB = 3
    if tamano_mb > MAX_MB:
        return jsonify({"error": f"El archivo supera los {MAX_MB} MB permitidos"}), 400

    contenido = archivo.read()

    turno = Turno.query.get(turno_id)
    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404
    if turno.usuario_id != usuario.id:
        return jsonify({"error": "No tenés permiso para modificar este turno."}), 403

    if usar_simulacion:
        es_valido, datos, huella, motivos = procesar_comprobante_simulado(turno_id)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmpfile:
            tmpfile.write(contenido)
            ruta_temporal = tmpfile.name

        config = ConfiguracionPago.query.first()
        es_valido, datos, huella, motivos = procesar_comprobante(ruta_temporal, config=config, modo_flexible=True)
        os.remove(ruta_temporal)

    if not es_valido:
        revertir_turno(turno)
        return jsonify({
            "error": "Comprobante inválido",
            "motivos": motivos,
            "datos_detectados": datos
        }), 400

    if Comprobante.query.filter_by(hash_archivo=huella).first():
        revertir_turno(turno)
        return jsonify({"error": "Este comprobante ya fue usado"}), 409

    turno.estado_pago = "subido"

    if usar_simulacion:
        print("🧪 Modo test activado — no se guarda comprobante real")
        db.session.add(turno)
        db.session.commit()
        return jsonify({
            "mensaje": "✅ Comprobante simulado recibido (modo test)",
            "datos": datos
        }), 200

    nuevo = Comprobante(
        turno_id=turno.id,
        hash_archivo=huella,
        nro_operacion=datos.get("operacion"),
        fecha_detectada=datos.get("fecha_hora"),
        valido=True,
        timestamp_carga=datetime.now(),
        emisor_nombre=datos.get("emisor_nombre"),
        emisor_cbu=datos.get("emisor_cbu"),
        emisor_cuit=datos.get("emisor_cuit"),
        archivo_blob=contenido,
        nombre_archivo=filename,
        mimetype=mimetype
    )

    try:
        db.session.add(nuevo)
        db.session.add(turno)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Comprobante duplicado"}), 409

    return jsonify({
        "mensaje": "✅ Comprobante recibido y verificado",
        "datos": datos
    })


@turnos_bp.route('/<int:turno_id>/liberar-si-pendiente', methods=['POST'])
@jwt_required
def liberar_turno_si_pendiente(turno_id):
    turno = Turno.query.get(turno_id)

    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404

    usuario = g.usuario_actual

    # 🛡️ Ahora también permitimos que el admin libere
    if turno.usuario_id != usuario.id and not usuario.es_admin:
        return jsonify({"error": "No tenés permiso para modificar este turno"}), 403

    if turno.estado != "pendiente" or turno.estado_pago != "pendiente":
        return jsonify({"mensaje": "El turno no está en estado pendiente, no se liberó"}), 200

    turno.estado = "libre"
    turno.fecha_expiracion = None
    turno.estado_pago = "pendiente"
    turno.usuario_id = None 
    db.session.commit()

    return jsonify({"mensaje": "Turno liberado correctamente"}), 200

# 🔐 Handler protegido para GET real
@turnos_bp.route("/todos", methods=["GET"])
@cors_jwt_route(methods=["GET"])
def listar_todos_los_turnos():
    if not g.usuario_actual.es_admin:
        return jsonify({"error": "Acceso denegado"}), 403

    turnos = Turno.query.order_by(Turno.fecha.desc(), Turno.hora.asc()).all()

    data = []
    for t in turnos:
        data.append({
            "id": t.id,
            "profesor": t.profesor.nombre if t.profesor else None,
            "usuario": t.usuario.nombre if t.usuario else None,
            "fecha": t.fecha.isoformat(),
            "hora": t.hora.strftime("%H:%M"),
            "estado_pago": t.estado_pago,
            "ocupado": t.usuario_id is not None and t.estado_pago != "disponible"
        })
    return jsonify({"turnos": data})

# 👇 Este se mantiene igual, porque POST no necesita preflight si no usás headers especiales
@turnos_bp.route("/<int:id>/liberar", methods=["POST", "OPTIONS"])
@cors_jwt_route(methods=["POST"])
def liberar_turno_admin(id):
    turno = Turno.query.get(id)

    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404

    # Si ya está libre, no lo liberamos de nuevo
    if turno.estado == "libre":
        return jsonify({"mensaje": "El turno ya está libre"}), 200

    # Limpiar el turno completamente
    turno.estado = "libre"
    turno.estado_pago = "pendiente"
    turno.usuario_id = None
    turno.fecha_expiracion = None
    turno.comprobante_url = None

    db.session.commit()

    return jsonify({"mensaje": f"Turno #{id} liberado correctamente"}), 200

@turnos_bp.route("/<int:turno_id>/asignar-directo", methods=["POST"])
@cors_jwt_route(methods=["POST"])
def asignar_turno_directo(turno_id):
    if not g.usuario_actual.es_admin:
        return jsonify({"error": "Solo administradores pueden reservar directamente."}), 403

    turno = Turno.query.get(turno_id)
    if not turno:
        return jsonify({"error": "Turno no encontrado."}), 404

    turno.usuario_id = g.usuario_actual.id
    turno.estado = "ocupado"
    turno.estado_pago = "completo"

    db.session.commit()
    return jsonify({"mensaje": "Turno asignado directamente por admin."}), 200



@turnos_bp.route("/comprobantes/<int:turno_id>", methods=["GET", "OPTIONS"])
@cors_jwt_route(methods=["GET"])
def obtener_comprobante(turno_id):
    usuario = g.usuario_actual
    if not getattr(usuario, "es_admin", False):
        return abort(403, description="Solo accesible para administradores")

    comprobante = Comprobante.query.filter_by(turno_id=turno_id).first()
    if not comprobante or not comprobante.archivo_blob:
        return "Comprobante no disponible", 404

    return send_file(
        BytesIO(comprobante.archivo_blob),
        mimetype=comprobante.mimetype or "application/pdf",
        download_name=comprobante.nombre_archivo or "comprobante.pdf",
        as_attachment=False
    )
