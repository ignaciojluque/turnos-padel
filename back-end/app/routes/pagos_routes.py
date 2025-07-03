from flask import Blueprint, jsonify, request, g
from app.models import db, Pago, Usuario, Turno
from app.utils.cors_utils import cors_jwt_route

pagos_bp = Blueprint("pagos", __name__)

@pagos_bp.route("/pagos", methods=["GET", "OPTIONS"])
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

@pagos_bp.route("/pagos/<int:pago_id>/validar", methods=["POST", "OPTIONS"])
@cors_jwt_route(methods=["POST"])
def validar_pago(pago_id):
    pago = Pago.query.get_or_404(pago_id)

    if pago.estado == "validado":
        return jsonify({"mensaje": "El pago ya está validado."}), 200

    pago.estado = "validado"
    db.session.commit()

    return jsonify({"mensaje": "✅ Pago marcado como validado."}), 200

@pagos_bp.route("/pagos/pendientes", methods=["GET"])
@cors_jwt_route(methods=["GET"])
def pagos_pendientes():
    turnos = Turno.query.join(Usuario).filter(Turno.estado_pago == "subido",Turno.estado == "confirmado").add_columns(
        Turno.id,
        Turno.fecha,
        Turno.hora,
        Turno.comprobante_url,
        Usuario.email.label("usuario_email"),
        Usuario.nombre.label("usuario_nombre")
    ).order_by(Turno.fecha, Turno.hora).all()

    resultado = []
    for _, id, fecha, hora, comprobante_url, email, nombre in turnos:
        resultado.append({
            "id": id,
            "fecha": fecha.isoformat(),
            "hora": hora.strftime("%H:%M"),
            "usuario_email": email,
            "usuario_nombre": nombre,
            "comprobante_url": comprobante_url
        })

    return jsonify({"pendientes": resultado}), 200

@pagos_bp.route("/<int:turno_id>/confirmar-pago", methods=["POST", "OPTIONS"])
@cors_jwt_route(methods=["POST"])
def confirmar_pago(turno_id):
    usuario = g.usuario_actual
    if not getattr(usuario, "es_admin", False):
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    turno = Turno.query.get(turno_id)
    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404

    if not turno.comprobante_detalle:
      creador = turno.usuario
      if not getattr(creador, "modo_test", False):
          return jsonify({"error": "Este turno no tiene comprobante asociado"}), 400


    turno.estado_pago = "confirmado"
    db.session.add(turno)
    db.session.commit()

    return jsonify({"mensaje": "✅ Turno confirmado manualmente por el administrador"})
