# =============================
# App_Bedelia – Application Entry Point (CORREGIDO)
# =============================

from flask import Flask, jsonify, request
from datetime import datetime
import json

from config import APP_NAME, DEBUG
from db.redis import redis_client
from mqtt_client import mqtt_client

# Mantengo tu import actual para respetar que NO quieres tocar mongo.py aún
from db.mongo import get_mongo_db

mongo_db = get_mongo_db()

app = Flask(__name__)
app.config["DEBUG"] = DEBUG


# -----------------------------
# Utilidad: serialización JSON segura
# -----------------------------
def _json_dumps(obj):
    """
    json.dumps tolerante: convierte tipos no serializables (datetime, etc.) a string.
    """
    return json.dumps(obj, default=str)


# -----------------------------
# Healthcheck
# -----------------------------
@app.route("/health", methods=["GET"])
def healthcheck():
    """
    Endpoint de salud para Docker / Nginx / monitoreo
    """
    return jsonify({
        "app": APP_NAME,
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


# -----------------------------
# Aulas – CRUD Básico (síncrono)
# -----------------------------
@app.route("/aulas", methods=["POST"])
def crear_aula():
    """
    Crea un aula en MongoDB y publica evento MQTT
    """
    data = request.get_json(silent=True) or {}

    required_fields = ["nro_aula", "piso", "cupo", "estado"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Datos incompletos"}), 400

    aula = {
        "nro_aula": data["nro_aula"],
        "piso": data["piso"],
        "descripcion": data.get("descripcion", ""),
        "cupo": data["cupo"],
        "estado": data["estado"],
        "created_at": datetime.utcnow()
    }

    # Inserta en Mongo
    result = mongo_db.aulas.insert_one(aula)
    aula_id = str(result.inserted_id)

    # Invalidar cache listado (si existe)
    try:
        redis_client.client.delete("aulas:all")
    except Exception:
        # no hago fallar el request por Redis
        pass

    # Publicar evento MQTT (NO quiero que una caída de EMQX tumbe el POST)
    try:
        mqtt_client.publish(
            topic="universidad/aulas/nueva",
            payload={
                "id_aula": aula_id,
                "nro_aula": aula["nro_aula"],
                "piso": aula["piso"],
                "cupo": aula["cupo"],
                "estado": aula["estado"],
            }
        )
    except Exception as e:
        # Importante: devolvemos creado igual, pero avisamos que el evento no salió
        return jsonify({
            "message": "Aula creada",
            "id": aula_id,
            "warning": f"No se pudo publicar evento MQTT: {str(e)}"
        }), 201

    return jsonify({"message": "Aula creada", "id": aula_id}), 201


@app.route("/aulas", methods=["GET"])
def listar_aulas():
    """
    Lista aulas (usa cache Redis si existe)
    """
    # 1) Intento cache
    try:
        cached = redis_client.client.get("aulas:all")
        if cached:
            return jsonify({"source": "cache", "data": json.loads(cached)}), 200
    except Exception:
        # si Redis falla, seguimos a Mongo sin cortar
        pass

    # 2) Mongo
    aulas = list(mongo_db.aulas.find({}, {"_id": 0}))

    # 3) Guardar cache como JSON válido
    try:
        redis_client.client.setex("aulas:all", 300, _json_dumps(aulas))
    except Exception:
        pass

    return jsonify({"source": "mongo", "data": aulas}), 200


# -----------------------------
# Arranque
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
