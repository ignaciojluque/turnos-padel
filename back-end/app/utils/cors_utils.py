from functools import wraps
from flask import request, jsonify
from flask_cors import cross_origin
from app.utils.jwt_utils import jwt_required

def cors_jwt_route(methods=["GET", "POST"]):
    def decorator(f):
        @cross_origin()
        @jwt_required
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.method == "OPTIONS":
                return '', 200
            return f(*args, **kwargs)
        wrapped.provide_automatic_options = False  # evita duplicación con Flask
        wrapped.methods = set(methods + ["OPTIONS"])
        return wrapped
    return decorator
