# =============================
# App_Bedelia – MQTT Client (mTLS)
# =============================

import ssl
import json
import uuid
import time
import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TLS_ENABLED,
    MQTT_TLS_CA_CERT,
    MQTT_TLS_CERT,
    MQTT_TLS_KEY,
    APP_NAME,
)


class MQTTClient:
    """
    Cliente MQTT para publicar eventos hacia EMQX.
    App_Bedelia solo publica eventos, no se suscribe.

    mTLS:
    - Verifica el broker con CA (ca_certs)
    - Presenta certificado de cliente (certfile/keyfile)
    """

    def __init__(self):
        client_id = f"{APP_NAME}-{uuid.uuid4()}"
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        # Callbacks siempre
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        if MQTT_TLS_ENABLED:
            # mTLS: CA + cert/key de cliente
            self.client.tls_set(
                ca_certs=MQTT_TLS_CA_CERT,
                certfile=MQTT_TLS_CERT,
                keyfile=MQTT_TLS_KEY,
                tls_version=ssl.PROTOCOL_TLSv1_2,
            )
            # Importante: el broker usa CA propia -> no "insecure"
            self.client.tls_insecure_set(False)

        # Conectar + loop (sin loop no hay handshake/ACKs/callbacks)
        self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        self.client.loop_start()

        # Opcional: pequeña espera para que conecte al boot (reduce fallos al primer publish)
        # No bloquea mucho, solo mejora estabilidad.
        for _ in range(20):
            if self.client.is_connected():
                break
            time.sleep(0.1)

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            raise RuntimeError(f"Error conectando a EMQX, código: {rc}")
        print("✅ MQTT conectado (mTLS)")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("⚠️ Desconexión inesperada de EMQX")

    def publish(self, topic: str, payload: dict):
        message = json.dumps(payload, default=str)
        result = self.client.publish(topic, message, qos=1)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Error publicando mensaje en {topic}")


# Instancia singleton
mqtt_client = MQTTClient()
