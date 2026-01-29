import os

APP_NAME = os.getenv("APP_NAME", "App_Alumno")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# JWT (DEMO): después lo alineamos 1:1 con Bedelía/EMQX
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))

# MQTT / EMQX
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "emqx")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))

MQTT_TLS_ENABLED = os.getenv("MQTT_TLS_ENABLED", "true").lower() == "true"
MQTT_TLS_CA_CERT = os.getenv("MQTT_TLS_CA_CERT", "/opt/certs/ca.crt")
MQTT_TLS_CERT = os.getenv("MQTT_TLS_CERT", "/opt/certs/alumno.crt")
MQTT_TLS_KEY = os.getenv("MQTT_TLS_KEY", "/opt/certs/alumno.key")

# Cómo mandamos el JWT al broker:
# - "password": token va en password (común en EMQX JWT auth)
# - "username": token va en username (a veces se usa así)
MQTT_JWT_MODE = os.getenv("MQTT_JWT_MODE", "password")
