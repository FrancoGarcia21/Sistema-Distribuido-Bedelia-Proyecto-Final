from flask import Blueprint, jsonify, request
from bson import ObjectId

from mqtt_client import mqtt_bridge
from jwt_helper import JWTHelper
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES
from db import save_subscription

bp = Blueprint("mqtt_api", __name__, url_prefix="/mqtt")
jwt_helper = JWTHelper(JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES)

def require_jwt():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise ValueError("Falta Authorization: Bearer <token>")
    token = auth.split(" ", 1)[1].strip()
    return token, jwt_helper.verify_token(token)

@bp.post("/connect")
def connect():
    try:
        token, payload = require_jwt()
        mqtt_bridge.connect(jwt_token=token, client_id_prefix="alumno")
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.post("/subscribe")
def subscribe():
    try:
        _, p = require_jwt()
        id_carrera = str(p["id_carrera"])
        user_id = ObjectId(p["id_usuario"])

        data = request.get_json(force=True, silent=True) or {}
        id_materia = str(data.get("id_materia"))

        topic = f"universidad/notificaciones/aula/{id_carrera}/{id_materia}"
        mqtt_bridge.subscribe(topic, qos=1)
        save_subscription(user_id, id_carrera, id_materia, subscribed=True)

        return jsonify({"status": "ok", "topic": topic}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.post("/unsubscribe")
def unsubscribe():
    try:
        _, p = require_jwt()
        id_carrera = str(p["id_carrera"])
        user_id = ObjectId(p["id_usuario"])

        data = request.get_json(force=True, silent=True) or {}
        id_materia = str(data.get("id_materia"))

        topic = f"universidad/notificaciones/aula/{id_carrera}/{id_materia}"

        if not mqtt_bridge._client or not mqtt_bridge._connected:
            return jsonify({"error": "MQTT no conectado"}), 400

        mqtt_bridge._client.unsubscribe(topic)
        if topic in mqtt_bridge.subscriptions:
            mqtt_bridge.subscriptions.remove(topic)

        save_subscription(user_id, id_carrera, id_materia, subscribed=False)

        return jsonify({"status": "ok", "topic": topic}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
