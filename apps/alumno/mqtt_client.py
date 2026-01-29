import ssl
import json
import queue
import uuid
import threading
import paho.mqtt.client as mqtt

class MQTTBridge:
    """
    Puente MQTT -> Web (SSE).
    - Conecta a EMQX con TLS/mTLS
    - Se suscribe a tópicos
    - Cada mensaje recibido se mete en una cola para que la UI lo consuma por /events (SSE)
    """

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

        # Cola simple (MVP). Para producción se puede pasar a Redis streams, etc.
        self.events = queue.Queue(maxsize=500)

        # track de subs
        self.subscriptions = set()

    def _push_event(self, event: dict):
        try:
            self.events.put_nowait(event)
        except queue.Full:
            # si se llena, tiramos el más viejo implícitamente (MVP simple)
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
            return

        client_id = f"{client_id_prefix}-{uuid.uuid4()}"
        self._client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        # JWT en username/password según config (esto lo ajustamos cuando veamos tu emqx_auth_jwt.conf)
        if self.jwt_mode == "password":
            self._client.username_pw_set(username="jwt", password=jwt_token)
        elif self.jwt_mode == "username":
            self._client.username_pw_set(username=jwt_token, password="")
        else:
            # modo custom: por ahora dejamos password como default
            self._client.username_pw_set(username="jwt", password=jwt_token)

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._client.on_log = self._on_log

        if self.tls_enabled:
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.ca_cert)
            ctx.load_cert_chain(certfile=self.client_cert, keyfile=self.client_key)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_REQUIRED
            self._client.tls_set_context(ctx)

        # conectar (bloqueante) y luego loop en thread
        self._client.connect(self.host, self.port, keepalive=60)

        t = threading.Thread(target=self._client.loop_forever, daemon=True)
        t.start()

    def subscribe(self, topic: str, qos: int = 1):
        if not self._client or not self._connected:
            raise RuntimeError("MQTT no conectado. Conectá primero.")
        self._client.subscribe(topic, qos=qos)
        self.subscriptions.add(topic)

    def _on_connect(self, client, userdata, flags, rc):
        self._connected = (rc == 0)
        self._push_event({
            "type": "mqtt",
            "event": "connect",
            "rc": rc,
            "message": "Conectado a EMQX" if rc == 0 else f"Falló conexión (rc={rc})"
        })

        # re-subs automático si reconecta
        if rc == 0:
            for t in list(self.subscriptions):
                try:
                    client.subscribe(t, qos=1)
                except Exception:
                    pass

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        self._push_event({
            "type": "mqtt",
            "event": "disconnect",
            "rc": rc,
            "message": f"Desconectado (rc={rc})"
        })

    def _on_message(self, client, userdata, msg):
        payload = None
        try:
            payload = msg.payload.decode("utf-8")
            # si es JSON, lo parseamos
            try:
                payload_json = json.loads(payload)
                payload = payload_json
            except Exception:
                pass
        except Exception:
            payload = "<payload no decodificable>"

        self._push_event({
            "type": "mqtt",
            "event": "message",
            "topic": msg.topic,
            "qos": msg.qos,
            "payload": payload
        })

    def _on_log(self, client, userdata, level, buf):
        # útil para debug; lo mandamos como evento “log” (podés apagarlo después)
        self._push_event({
            "type": "mqtt",
            "event": "log",
            "message": buf
        })
