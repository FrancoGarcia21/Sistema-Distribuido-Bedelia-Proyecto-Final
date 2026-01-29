import ssl
import json
import queue
import uuid
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

        self._client: mqtt.Client | None = None
        self._connected = False

        # Cola simple (MVP)
        self.events = queue.Queue(maxsize=500)

        # track de subs
        self.subscriptions = set()

    def _push_event(self, event: dict):
        try:
            self.events.put_nowait(event)
        except queue.Full:
            # Si se llena, descartamos uno viejo y seguimos (MVP)
            try:
                _ = self.events.get_nowait()
            except queue.Empty:
                pass
            try:
                self.events.put_nowait(event)
            except queue.Full:
                pass

    def connect(self, jwt_token: str, client_id_prefix: str = "alumno"):
        """
        Conecta (si no está conectado).
        Usa loop_start() (thread interno de paho) para estabilidad.
        """
        if self._client and self._connected:
            self._push_event({
                "type": "mqtt",
                "event": "connect_skip",
                "message": "Ya estaba conectado"
            })
            return

        client_id = f"{client_id_prefix}-{uuid.uuid4()}"
        self._client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        # Callbacks principales
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.on_log = self._on_log

        # Callbacks extra para confirmar SUBACK/PUBACK
        self._client.on_subscribe = self._on_subscribe
        self._client.on_publish = self._on_publish

        # JWT en username/password según config (esto lo ajustamos cuando veamos tu emqx_auth_jwt.conf)
        if self.jwt_mode == "password":
            # común: username fijo + token en password
            self._client.username_pw_set(username="jwt", password=jwt_token)
        elif self.jwt_mode == "username":
            # alternativa: token en username
            self._client.username_pw_set(username=jwt_token, password="")
        else:
            self._client.username_pw_set(username="jwt", password=jwt_token)

        # TLS/mTLS
        if self.tls_enabled:
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.ca_cert)
            ctx.load_cert_chain(certfile=self.client_cert, keyfile=self.client_key)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_REQUIRED
            self._client.tls_set_context(ctx)

        # Conectar y arrancar loop interno
        self._client.connect(self.host, self.port, keepalive=60)
        self._client.loop_start()

        self._push_event({
            "type": "mqtt",
            "event": "connect_start",
            "client_id": client_id,
            "message": "connect() ejecutado + loop_start()"
        })

    def subscribe(self, topic: str, qos: int = 1):
        if not self._client or not self._connected:
            raise RuntimeError("MQTT no conectado. Conectá primero.")

        result, mid = self._client.subscribe(topic, qos=qos)

        self._push_event({
            "type": "mqtt",
            "event": "subscribe_request",
            "topic": topic,
            "qos": qos,
            "result": int(result),
            "mid": int(mid),
        })

        # guardamos para re-subscribe en reconexión
        self.subscriptions.add(topic)

    # -------------------------
    # Callbacks MQTT
    # -------------------------

    def _on_connect(self, client, userdata, flags, rc):
        self._connected = (rc == 0)

        self._push_event({
            "type": "mqtt",
            "event": "connect",
            "rc": int(rc),
            "message": "Conectado a EMQX" if rc == 0 else f"Falló conexión (rc={rc})"
        })

        # re-subs automático si reconecta
        if rc == 0:
            for t in list(self.subscriptions):
                try:
                    client.subscribe(t, qos=1)
                    self._push_event({
                        "type": "mqtt",
                        "event": "resubscribe",
                        "topic": t
                    })
                except Exception as e:
                    self._push_event({
                        "type": "mqtt",
                        "event": "resubscribe_error",
                        "topic": t,
                        "error": str(e)
                    })

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        self._push_event({
            "type": "mqtt",
            "event": "disconnect",
            "rc": int(rc),
            "message": f"Desconectado (rc={rc})"
        })

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        # Esta es la confirmación real de SUBACK
        self._push_event({
            "type": "mqtt",
            "event": "subscribed",
            "mid": int(mid),
            "granted_qos": list(granted_qos)
        })

    def _on_publish(self, client, userdata, mid):
        self._push_event({
            "type": "mqtt",
            "event": "published_ack",
            "mid": int(mid)
        })

    def _on_message(self, client, userdata, msg):
        # Marker para confirmar que el callback corre
        self._push_event({"type": "debug", "event": "on_message_called"})

        payload = None
        try:
            raw = msg.payload.decode("utf-8", errors="replace")
            # si es JSON, lo parseamos
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
        # log crudo de paho (útil para debug)
        self._push_event({
            "type": "mqtt",
            "event": "log",
            "message": buf
        })
