# utils/jwt_utils.py
import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from app.models import Usuario
from jwt import ExpiredSignatureError, InvalidTokenError

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token de acceso no proporcionado"}), 401

        token = auth_header.split(' ')[1]

        try:
            decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            usuario_id = decoded.get('sub')
            usuario = Usuario.query.get(usuario_id)

            if not usuario:
                return jsonify({"error": "Usuario no válido"}), 404

            # Guardar el usuario en el contexto global de Flask
            g.usuario_actual = usuario

        except ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 403

        return f(*args, **kwargs)

    return decorated_function
