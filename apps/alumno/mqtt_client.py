import ssl
import json
import queue
import uuid
import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER_HOST, MQTT_BROKER_PORT,
    MQTT_TLS_ENABLED, MQTT_TLS_CA_CERT, MQTT_TLS_CERT, MQTT_TLS_KEY,
    MQTT_JWT_MODE
)

class MQTTBridge:
    def __init__(self, host: str, port: int, tls_enabled: bool,
                 ca_cert: str, client_cert: str, client_key: str,
                 jwt_mode: str = "password"):
        self.host = host
        self.port = port
        self.tls_enabled = tls_enabled
        self.ca_cert = ca_cert
        self.client_cert = client_cert
        self.client_key = client_key
        self.jwt_mode = jwt_mode

        self._client = None
        self._connected = False
        self.events = queue.Queue(maxsize=500)
        self.subscriptions = set()

    def _push_event(self, event: dict):
        try:
            self.events.put_nowait(event)
        except queue.Full:
            try:
                _ = self.events.get_nowait()
            except queue.Empty:
                pass
            try:
                self.events.put_nowait(event)
            except queue.Full:
                pass

    def connect(self, jwt_token: str, client_id_prefix: str = "alumno"):
        if self._client and self._connected:
            self._push_event({"type": "mqtt", "event": "connect_skip"})
            return

        client_id = f"{client_id_prefix}-{uuid.uuid4()}"
        self._client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.on_log = self._on_log
        self._client.on_subscribe = self._on_subscribe

        if self.jwt_mode == "password":
            self._client.username_pw_set(username="jwt", password=jwt_token)
        elif self.jwt_mode == "username":
            self._client.username_pw_set(username=jwt_token, password="")
        else:
            self._client.username_pw_set(username="jwt", password=jwt_token)

        if self.tls_enabled:
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.ca_cert)
            ctx.load_cert_chain(certfile=self.client_cert, keyfile=self.client_key)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_REQUIRED
            self._client.tls_set_context(ctx)

        self._client.connect(self.host, self.port, keepalive=60)
        self._client.loop_start()

        self._push_event({"type": "mqtt", "event": "connect_start", "client_id": client_id})

    def subscribe(self, topic: str, qos: int = 1):
        if not self._client or not self._connected:
            raise RuntimeError("MQTT no conectado. Conectá primero.")
        self._client.subscribe(topic, qos=qos)
        self.subscriptions.add(topic)

    def _on_connect(self, client, userdata, flags, rc):
        self._connected = (rc == 0)
        self._push_event({"type": "mqtt", "event": "connect", "rc": int(rc)})

        if rc == 0:
            for t in list(self.subscriptions):
                try:
                    client.subscribe(t, qos=1)
                    self._push_event({"type": "mqtt", "event": "resubscribe", "topic": t})
                except Exception:
                    pass

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        self._push_event({"type": "mqtt", "event": "disconnect", "rc": int(rc)})

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        self._push_event({"type": "mqtt", "event": "subscribed", "mid": int(mid), "granted_qos": list(granted_qos)})

    def _on_message(self, client, userdata, msg):
        self._push_event({"type": "debug", "event": "on_message_called"})

        try:
            raw = msg.payload.decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except Exception:
                payload = raw
        except Exception as e:
            payload = f"<error decoding payload: {e}>"

        self._push_event({
            "type": "mqtt",
            "event": "message",
            "topic": msg.topic,
            "qos": int(msg.qos),
            "retain": bool(msg.retain),
            "payload": payload
        })

    def _on_log(self, client, userdata, level, buf):
        self._push_event({"type": "mqtt", "event": "log", "message": buf})

mqtt_bridge = MQTTBridge(
    host=MQTT_BROKER_HOST,
    port=MQTT_BROKER_PORT,
    tls_enabled=MQTT_TLS_ENABLED,
    ca_cert=MQTT_TLS_CA_CERT,
    client_cert=MQTT_TLS_CERT,
    client_key=MQTT_TLS_KEY,
    jwt_mode=MQTT_JWT_MODE,
)
