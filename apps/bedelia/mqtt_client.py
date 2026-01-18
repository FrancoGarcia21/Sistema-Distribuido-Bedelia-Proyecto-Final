# =============================


import ssl
import json
import uuid
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
    """


    def __init__(self):
        client_id = f"{APP_NAME}-{uuid.uuid4()}"
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        if MQTT_TLS_ENABLED:
            self.client.tls_set(
                ca_certs=MQTT_TLS_CA_CERT,
                certfile=MQTT_TLS_CERT,
                keyfile=MQTT_TLS_KEY,
                tls_version=ssl.PROTOCOL_TLSv1_2,
            )
            self.client.tls_insecure_set(False)


            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect


            self.client.connect(
            MQTT_BROKER_HOST,
            MQTT_BROKER_PORT,
            keepalive=60,
            )


    # -----------------------------
    # Callbacks
    # -----------------------------


    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            raise RuntimeError(f"Error conectando a EMQX, código: {rc}")


    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Desconexión inesperada de EMQX")


    # -----------------------------
    # Publicación de eventos
    # -----------------------------


    def publish(self, topic: str, payload: dict):
        message = json.dumps(payload)
        result = self.client.publish(topic, message, qos=1)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Error publicando mensaje en {topic}")




# Instancia singleton
mqtt_client = MQTTClient()