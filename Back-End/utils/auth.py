from functools import wraps
from flask import request, jsonify
from models import Usuario

def requiere_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "No autorizado"}), 401

        token = auth_header.replace("Bearer ", "")
        if not token.startswith("tok_"):
            return jsonify({"message": "No autorizado"}), 401

        email = token.replace("tok_", "", 1)
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario is None:
            return jsonify({"message": "No autorizado"}), 401

        request.usuario_actual = usuario
        return f(*args, **kwargs)
    return wrapper

