from flask import Flask, jsonify, request, Response, render_template
import json
import time

from config import (
    APP_NAME, DEBUG,
    JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES,
    MQTT_BROKER_HOST, MQTT_BROKER_PORT,
    MQTT_TLS_ENABLED, MQTT_TLS_CA_CERT, MQTT_TLS_CERT, MQTT_TLS_KEY,
    MQTT_JWT_MODE,
)
from jwt_helper import JWTHelper
from mqtt_client import MQTTBridge

app = Flask(__name__)
app.config["DEBUG"] = DEBUG

jwt_helper = JWTHelper(JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES)

# 2 usuarios demo (carreras distintas)
USERS = {
    "alumnoA": {"password": "1234", "id_usuario": 1001, "rol": "alumno", "id_carrera": 1},
    "alumnoB": {"password": "1234", "id_usuario": 2001, "rol": "alumno", "id_carrera": 2},
}

# Materias mock por carrera (MVP)
MATERIAS = {
    1: [
        {"id_materia": 101, "nombre": "Álgebra"},
        {"id_materia": 102, "nombre": "Programación I"},
    ],
    2: [
        {"id_materia": 201, "nombre": "Bases de Datos"},
        {"id_materia": 202, "nombre": "Redes I"},
    ],
}

mqtt_bridge = MQTTBridge(
    host=MQTT_BROKER_HOST,
    port=MQTT_BROKER_PORT,
    tls_enabled=MQTT_TLS_ENABLED,
    ca_cert=MQTT_TLS_CA_CERT,
    client_cert=MQTT_TLS_CERT,
    client_key=MQTT_TLS_KEY,
    jwt_mode=MQTT_JWT_MODE,
)

# Estado simple en memoria (para UI)
STATE = {
    "last_by_topic": {},   # topic -> last payload
    "recent": []           # lista de últimos eventos "message"
}
RECENT_MAX = 50


@app.get("/")
def home():
    return render_template("index.html", app_name=APP_NAME)


@app.get("/health")
def health():
    return jsonify({"app": APP_NAME, "status": "ok"})


@app.post("/auth/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Faltan credenciales"}), 400

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Credenciales inválidas"}), 401

    payload = {
        "usuario": username,
        "id_usuario": user["id_usuario"],
        "rol": user["rol"],
        "id_carrera": user["id_carrera"],
    }
    token = jwt_helper.create_token(payload)
    return jsonify({"token": token, "payload": payload})


def _get_token_payload_from_request() -> dict:
    """
    Espera: Authorization: Bearer <token>
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise ValueError("Falta Authorization: Bearer <token>")
    token = auth.split(" ", 1)[1].strip()
    return jwt_helper.verify_token(token)


@app.get("/api/materias")
def api_materias():
    try:
        payload = _get_token_payload_from_request()
        id_carrera = int(payload["id_carrera"])
        return jsonify({"id_carrera": id_carrera, "materias": MATERIAS.get(id_carrera, [])})
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@app.get("/api/state")
def api_state():
    # para refrescar UI (opcional)
    return jsonify({
        "last_by_topic": STATE["last_by_topic"],
        "recent": STATE["recent"]
    })


@app.post("/mqtt/connect")
def mqtt_connect():
    data = request.get_json(force=True, silent=True) or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "Falta token"}), 400

    try:
        mqtt_bridge.connect(jwt_token=token, client_id_prefix="alumno")
        return jsonify({"status": "ok", "message": "Intentando conexión MQTT (mirá /events)"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/mqtt/subscribe")
def mqtt_subscribe():
    data = request.get_json(force=True, silent=True) or {}
    id_carrera = data.get("id_carrera")
    id_materia = data.get("id_materia")

    if id_carrera is None or id_materia is None:
        return jsonify({"error": "Falta id_carrera o id_materia"}), 400

    topic = f"universidad/notificaciones/aula/{id_carrera}/{id_materia}"
    try:
        mqtt_bridge.subscribe(topic, qos=1)
        return jsonify({"status": "ok", "topic": topic}), 200
    except Exception as e:
        return jsonify({"error": str(e), "topic": topic}), 500


@app.post("/mqtt/unsubscribe")
def mqtt_unsubscribe():
    data = request.get_json(force=True, silent=True) or {}
    id_carrera = data.get("id_carrera")
    id_materia = data.get("id_materia")

    if id_carrera is None or id_materia is None:
        return jsonify({"error": "Falta id_carrera o id_materia"}), 400

    topic = f"universidad/notificaciones/aula/{id_carrera}/{id_materia}"
    try:
        if not mqtt_bridge._client or not mqtt_bridge._connected:
            return jsonify({"error": "MQTT no conectado"}), 400

        result, mid = mqtt_bridge._client.unsubscribe(topic)
        if topic in mqtt_bridge.subscriptions:
            mqtt_bridge.subscriptions.remove(topic)

        return jsonify({"status": "ok", "topic": topic, "result": int(result), "mid": int(mid)}), 200
    except Exception as e:
        return jsonify({"error": str(e), "topic": topic}), 500


@app.get("/events")
def events():
    """
    Server-Sent Events: el navegador escucha mensajes en vivo.
    Además, guardamos estado para UI (último por topic + feed reciente).
    """
    def stream():
        yield f"data: {json.dumps({'type':'sse','event':'open','message':'SSE conectado'})}\n\n"

        while True:
            try:
                event = mqtt_bridge.events.get(timeout=15)

                # Si es mensaje MQTT, actualizamos STATE
                if event.get("type") == "mqtt" and event.get("event") == "message":
                    topic = event.get("topic")
                    payload = event.get("payload")
                    if topic:
                        STATE["last_by_topic"][topic] = payload
                    STATE["recent"].insert(0, event)
                    if len(STATE["recent"]) > RECENT_MAX:
                        STATE["recent"] = STATE["recent"][:RECENT_MAX]

                yield f"data: {json.dumps(event, default=str)}\n\n"
            except Exception:
                yield f"data: {json.dumps({'type':'sse','event':'keepalive','ts':time.time()})}\n\n"

    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=DEBUG)
