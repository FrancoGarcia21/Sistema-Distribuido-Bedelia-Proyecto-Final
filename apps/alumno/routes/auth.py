from flask import Blueprint, request, jsonify
import bcrypt

from db import find_user_by_username
from jwt_helper import JWTHelper

bp = Blueprint("auth", __name__)
@bp.post("/auth/login")
@bp.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    usuario = (data.get("usuario") or "").strip()
    password = data.get("password") or ""

    if not usuario or not password:
        return jsonify({"error": "faltan_campos", "mensaje": "usuario y password son obligatorios"}), 400

    u = find_user_by_username(usuario)

    if not u:
        return jsonify({"error": "credenciales_invalidas"}), 401

    if u.get("rol") != "alumno":
        return jsonify({"error": "rol_no_permitido"}), 403

    stored_hash = u.get("contraseña") or ""
    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception:
        ok = False

    if not ok:
        return jsonify({"error": "credenciales_invalidas"}), 401

    payload = {
        "id_usuario": str(u.get("_id")),
        "usuario": u.get("usuario"),
        "rol": u.get("rol"),
        "id_carrera": str(u.get("id_carrera")) if u.get("id_carrera") is not None else None,
    }

    token = JWTHelper.create(payload)
    return jsonify({"status": "ok", "token": token, "payload": payload})
