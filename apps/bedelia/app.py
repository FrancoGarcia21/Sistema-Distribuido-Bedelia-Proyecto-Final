# =============================
# App_Bedelia – Application Entry Point
# =============================

from flask import Flask, jsonify, request
from config import APP_NAME, DEBUG
from db.mongo import mongo_db
from db.redis import redis_client
from mqtt_client import mqtt_client
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = DEBUG

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
    data = request.json

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

    result = mongo_db.aulas.insert_one(aula)
    aula_id = str(result.inserted_id)

    # Publicar evento MQTT
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

    return jsonify({"message": "Aula creada", "id": aula_id}), 201


@app.route("/aulas", methods=["GET"])
def listar_aulas():
    """
    Lista aulas (usa cache Redis si existe)
    """
    cached = redis_client.client.get("aulas:all")
    if cached:
        return jsonify({"source": "cache", "data": cached}), 200

    aulas = list(mongo_db.aulas.find({}, {"_id": 0}))
    redis_client.client.setex("aulas:all", 300, str(aulas))

    return jsonify({"source": "mongo", "data": aulas}), 200

# -----------------------------
# Arranque
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
