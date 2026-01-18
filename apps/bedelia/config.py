# =============================
# App_Bedelia – Configuración Central
# =============================


import os
from dotenv import load_dotenv


# Carga variables de entorno desde .env si existe
load_dotenv()


# -----------------------------
# Configuración General
# -----------------------------


APP_NAME = "App_Bedelia"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


# -----------------------------
# MongoDB (Replica Set)
# -----------------------------


MONGO_URI = os.getenv(
"MONGO_URI",
"mongodb://mongo-primary:27017,mongo-secondary1:27017,mongo-secondary2:27017/"
"smartcampus?replicaSet=rs0"
)


MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "smartcampus")


# -----------------------------
# Redis
# -----------------------------


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))


# TTLs (en segundos) – acordados en el diseño
REDIS_TTL_AULA_CACHE = 300 # 5 minutos
REDIS_TTL_SESION = 43200 # 12 horas
REDIS_TTL_LOCK = 30 # 30 segundos


# -----------------------------
# EMQX / MQTT
# -----------------------------


MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "emqx")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 8883))


MQTT_TLS_ENABLED = True
MQTT_TLS_CA_CERT = os.getenv("MQTT_TLS_CA_CERT", "/opt/certs/ca.crt")
MQTT_TLS_CERT = os.getenv("MQTT_TLS_CERT", "/opt/certs/server.crt")
MQTT_TLS_KEY = os.getenv("MQTT_TLS_KEY", "/opt/certs/server.key")


# -----------------------------
# Seguridad
# -----------------------------


# Usado para sesiones Flask (más adelante)
SECRET_KEY = os.getenv("SECRET_KEY", "bedelia_secret_key")


# -----------------------------
if not MONGO_URI:
    raise RuntimeError("MONGO_URI no está configurado")