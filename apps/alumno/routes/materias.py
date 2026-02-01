from flask import Blueprint, request, jsonify
import bcrypt

from jwt_helper import JWTHelper
from db import find_user_by_username, find_user_carrera, find_materias_by_carrera  # <-- si no existe, te digo abajo
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES

bp = Blueprint("materias", __name__)

jwt_helper = JWTHelper(JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES)

def _verify_password(stored: str, provided: str) -> bool:
    """
    Soporta:
    - bcrypt: strings tipo $2b$12$...
    - texto plano (MVP)
    """
    if not stored or not provided:
        return False

    # bcrypt hashes suelen empezar con $2a$, $2b$, $2y$
    if stored.startswith("$2a$") or stored.startswith("$2b$") or stored.startswith("$2y$"):
        try:
            return bcrypt.checkpw(provided.encode("utf-8"), stored.encode("utf-8"))
        except ValueError:
            # hash corrupto / salt inválida
            return False

    # fallback: texto plano
    return stored == provided


def _read_credentials(data: dict) -> tuple[str, str]:
    """
    Acepta ambos formatos:
    - { "username": "...", "password": "..." }  (UI actual)
    - { "usuario": "...", "password": "..." }   (tus pruebas)
    """
    username = (data.get("username") or data.get("usuario") or "").strip()
    password = (data.get("password") or "").strip()
    return username, password


def _do_login():
    data = request.get_json(force=True, silent=True) or {}
    username, password = _read_credentials(data)

    if not username or not password:
        return jsonify({"error": "Faltan credenciales"}), 400

    user = find_user_by_username(username)
    if not user:
        return jsonify({"error": "Usuario no encontrado o inactivo"}), 401

    if user.get("rol") != "alumno":
        return jsonify({"error": "El usuario no es alumno"}), 403

    stored_pass = user.get("contraseña") or user.get("contrasena") or user.get("password") or ""
    if not _verify_password(stored_pass, password):
        return jsonify({"error": "credenciales_invalidas"}), 401

    user_id = user["_id"]
    id_carrera = user.get("id_carrera") or find_user_carrera(user_id)
    if not id_carrera:
        return jsonify({
            "error": "No se pudo determinar la carrera del alumno",
            "detalle": "Agregá usuarios.id_carrera o la colección usuario_carrera"
        }), 500

    payload = {
        "id_usuario": str(user_id),
        "usuario": username,
        "rol": "alumno",
        "id_carrera": str(id_carrera),
    }

    token = jwt_helper.create_token(payload)
    return jsonify({"status": "ok", "token": token, "payload": payload})


# ✅ 3 rutas para que no se te rompa nada según quién llame
@bp.post("/login")
def login():
    return _do_login()

@bp.post("/api/login")
def api_login():
    return _do_login()

@bp.post("/auth/login")
def auth_login():
    return _do_login()


def require_jwt(fn):
    """
    Decorador simple, sin depender de carpeta utils.
    Lee Authorization: Bearer <token> y lo valida con jwt_helper.
    """
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "token_no_proporcionado"}), 401

        token = auth.split(" ", 1)[1].strip()
        try:
            payload = jwt_helper.decode_token(token)
        except Exception:
            return jsonify({"error": "token_invalido"}), 401

        return fn(payload, *args, **kwargs)

    return wrapper


@bp.get("/api/materias")
@require_jwt
def api_materias(jwt_payload):
    id_carrera = jwt_payload.get("id_carrera")
    if not id_carrera:
        return jsonify({"materias": []})

    # ✅ Esta función la agregamos si no existe
    materias = find_materias_by_carrera(str(id_carrera))
    return jsonify({"materias": materias})
