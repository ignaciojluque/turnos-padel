from flask import Blueprint, jsonify, request, g
from app.models import Usuario, db
from app.utils.cors_utils import cors_jwt_route

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("/usuarios", methods=["GET"])
@cors_jwt_route(methods=["GET"])
def listar_usuarios():
    if not g.usuario_actual.es_admin:
        return jsonify({"error": "Acceso denegado"}), 403

    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    resultado = [
        {
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "telefono": u.telefono,
            "es_admin": u.es_admin,
            "modo_test": u.modo_test
        } for u in usuarios
    ]
    return jsonify({"usuarios": resultado}), 200

@usuarios_bp.route("/usuarios/<int:usuario_id>/modo-test", methods=["POST"])
@cors_jwt_route(methods=["POST"])
def cambiar_modo_test(usuario_id):
    if not g.usuario_actual.es_admin:
        return jsonify({"error": "Acceso denegado"}), 403

    data = request.get_json()
    activar = data.get("activar", True)

    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.modo_test = activar
    db.session.commit()

    return jsonify({"mensaje": f"Modo test {'activado' if activar else 'desactivado'} para {usuario.email}"}), 200
