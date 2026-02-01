# # =============================
# # App_Bedelia – MQTT Client (mTLS)
# # =============================

# import ssl
# import json
# import uuid
# import time
# import os
# import paho.mqtt.client as mqtt


# def _env_bool(v: str, default: bool = False) -> bool:
#     if v is None:
#         return default
#     return str(v).strip().lower() in ("1", "true", "yes", "y", "on")


# class MQTTClient:
#     """
#     Cliente MQTT para publicar eventos hacia EMQX.
#     App_Bedelia solo publica eventos, no se suscribe.

#     mTLS:
#     - Verifica el broker con CA
#     - Presenta certificado de cliente (cert/key)
#     """

#     def __init__(
#         self,
#         host: str,
#         port: int,
#         tls_enabled: bool,
#         ca_cert: str | None,
#         client_cert: str | None,
#         client_key: str | None,
#         app_name: str = "App_Bedelia",
#     ):
#         self.host = host
#         self.port = int(port)
#         self.tls_enabled = tls_enabled

#         client_id = f"{app_name}-{uuid.uuid4()}"
#         self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

#         self.client.on_connect = self.on_connect
#         self.client.on_disconnect = self.on_disconnect
#         self.client.on_log = self.on_log

#         if self.tls_enabled:
#             if not (ca_cert and client_cert and client_key):
#                 raise RuntimeError(
#                     "TLS habilitado pero faltan rutas de certificados (CA/CERT/KEY)."
#                 )

#             ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
#             ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)
#             ctx.minimum_version = ssl.TLSVersion.TLSv1_2
#             self.client.tls_set_context(ctx)
#             self.client.tls_insecure_set(False)

#         # Conectar + loop
#         # OJO: connect() no garantiza handshake completo hasta que corre el loop.
#         self.client.connect(self.host, self.port, keepalive=60)
#         self.client.loop_start()

#         # Espera corta para estabilizar
#         for _ in range(30):
#             if self.client.is_connected():
#                 break
#             time.sleep(0.1)

#     def on_log(self, client, userdata, level, buf):
#         print(f"[MQTT LOG] {buf}")

#     def on_connect(self, client, userdata, flags, rc):
#         if rc != 0:
#             print(f"❌ MQTT CONNACK rc={rc}")
#         else:
#             print("✅ MQTT conectado")

#     def on_disconnect(self, client, userdata, rc):
#         if rc != 0:
#             print(f"⚠️ MQTT desconectado inesperadamente rc={rc}")

#     def publish(self, topic: str, payload: dict):
#         message = json.dumps(payload, default=str)
#         result = self.client.publish(topic, message, qos=1)
#         if result.rc != mqtt.MQTT_ERR_SUCCESS:
#             raise RuntimeError(f"Error publicando mensaje en {topic}: rc={result.rc}")
            
#     def _subscribe_to_topics(self):
#     """Suscribe a los tópicos relevantes para Bedelia"""
#     try:
#         # Bedelia escucha solicitudes de asignación
#         self.client.subscribe(TOPICS['ASIGNACION_AULA'], qos=1)
#         print(f"✅ Suscrito a: {TOPICS['ASIGNACION_AULA']}")
        
#         # Bedelia escucha solicitudes de liberación
#         self.client.subscribe(TOPICS['LIBERAR_AULA'], qos=1)
#         print(f"✅ Suscrito a: {TOPICS['LIBERAR_AULA']}")
        
#         # Bedelia puede escuchar métricas
#         self.client.subscribe(TOPICS['METRICAS_EMQX'], qos=0)
#         print(f"✅ Suscrito a: {TOPICS['METRICAS_EMQX']}")
        
#         # ✅ NUEVO: Escuchar notificaciones con wildcard
#         self.client.subscribe(TOPICS['NOTIFICACION_AULA_WILDCARD'], qos=0)
#         print(f"✅ Suscrito a: {TOPICS['NOTIFICACION_AULA_WILDCARD']}")
        
#     except Exception as e:
#         print(f"❌ Error al suscribirse a tópicos: {e}")


# # ---------- Lazy init (clave para que NO muera el contenedor) ----------
# _mqtt_client: MQTTClient | None = None


# def get_mqtt_client() -> MQTTClient | None:
#     """
#     Devuelve el cliente si pudo conectarse. Si no, devuelve None.
#     No mata el proceso: la app puede levantar igual y reintentar luego.
#     """
#     global _mqtt_client
#     if _mqtt_client is not None:
#         return _mqtt_client

#     host = os.getenv("MQTT_BROKER_HOST", "emqx")
#     port = int(os.getenv("MQTT_BROKER_PORT", "8883"))
#     tls_enabled = _env_bool(os.getenv("MQTT_TLS_ENABLED", "true"))

#     ca_cert = os.getenv("MQTT_TLS_CA_CERT")
#     client_cert = os.getenv("MQTT_TLS_CERT")
#     client_key = os.getenv("MQTT_TLS_KEY")
#     app_name = os.getenv("APP_NAME", "App_Bedelia")

#     print("[MQTT INIT] host=", host)
#     print("[MQTT INIT] port=", port)
#     print("[MQTT INIT] tls_enabled=", tls_enabled)
#     print("[MQTT INIT] ca_cert=", ca_cert)
#     print("[MQTT INIT] client_cert=", client_cert)
#     print("[MQTT INIT] client_key=", client_key)

#     try:
#         _mqtt_client = MQTTClient(
#             host=host,
#             port=port,
#             tls_enabled=tls_enabled,
#             ca_cert=ca_cert,
#             client_cert=client_cert,
#             client_key=client_key,
#             app_name=app_name,
#         )
#         return _mqtt_client
#     except Exception as e:
#         print(f"❌ No se pudo inicializar MQTT: {e}")
#         return None

# =============================
# App_Bedelia – MQTT Client (mTLS)
# =============================

import ssl
import json
import uuid
import time
import os
import paho.mqtt.client as mqtt


# ==========================================
# TOPICS MQTT - Según Prompt Maestro (Pág. 4)
# Formato: universidad/{dominio}/{accion}/{identificadores}
# ==========================================

TOPICS = {
    # ======================
    # ASIGNACIÓN Y GESTIÓN
    # ======================
    'ASIGNACION_AULA': 'universidad/aulas/asignacion',
    'LIBERAR_AULA': 'universidad/aulas/liberar',
    'NUEVA_AULA': 'universidad/aulas/nueva',
    
    # ======================
    # EVENTOS (con IDs dinámicos)
    # ======================
    'EVENTO_AULA_ASIGNADA': 'universidad/eventos/aula/asignada',
    'EVENTO_AULA_LIBERADA': 'universidad/eventos/aula/liberada',
    
    # ======================
    # NOTIFICACIONES (con IDs dinámicos)
    # ======================
    'NOTIFICACION_AULA': 'universidad/notificaciones/aula',
    'NOTIFICACION_AULA_WILDCARD': 'universidad/notificaciones/aula/+/+',
    
    # ======================
    # ERRORES (con IDs dinámicos)
    # ======================
    'ERROR_PROFESOR': 'universidad/errores/profesor',
    'ERROR_USUARIO': 'universidad/errores',
    
    # ======================
    # MÉTRICAS
    # ======================
    'METRICAS_EMQX': 'universidad/metricas/emqx',
    'METRICAS_AULAS': 'universidad/metricas/aulas',
    'METRICAS_USUARIOS': 'universidad/metricas/usuarios'
}


# ==============================================
# FUNCIONES HELPER PARA CONSTRUIR TOPICS DINÁMICOS
# ==============================================

def build_topic_evento_asignada(id_carrera: str, id_materia: str) -> str:
    """
    Construye el topic de evento de aula asignada
    Formato: universidad/eventos/aula/asignada/{id_carrera}/{id_materia}
    """
    return f"{TOPICS['EVENTO_AULA_ASIGNADA']}/{id_carrera}/{id_materia}"


def build_topic_evento_liberada(id_carrera: str, id_materia: str) -> str:
    """
    Construye el topic de evento de aula liberada
    Formato: universidad/eventos/aula/liberada/{id_carrera}/{id_materia}
    """
    return f"{TOPICS['EVENTO_AULA_LIBERADA']}/{id_carrera}/{id_materia}"


def build_topic_notificacion(id_carrera: str, id_materia: str) -> str:
    """
    Construye el topic de notificación de aula
    Formato: universidad/notificaciones/aula/{id_carrera}/{id_materia}
    """
    return f"{TOPICS['NOTIFICACION_AULA']}/{id_carrera}/{id_materia}"


def build_topic_error_profesor(id_profesor: str) -> str:
    """
    Construye el topic de error de profesor
    Formato: universidad/errores/profesor/{id_profesor}
    """
    return f"{TOPICS['ERROR_PROFESOR']}/{id_profesor}"


def build_topic_error_usuario(id_usuario: str) -> str:
    """
    Construye el topic de error de usuario
    Formato: universidad/errores/{id_usuario}
    """
    return f"{TOPICS['ERROR_USUARIO']}/{id_usuario}"


# ==============================================
# HELPER FUNCTION
# ==============================================

def _env_bool(v: str, default: bool = False) -> bool:
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")


# ==============================================
# CLASE MQTTClient (sin singleton)
# ==============================================

class MQTTClient:
    """
    Cliente MQTT para publicar eventos hacia EMQX.
    App_Bedelia publica eventos y se suscribe a tópicos relevantes.

    mTLS:
    - Verifica el broker con CA
    - Presenta certificado de cliente (cert/key)
    """

    def __init__(
        self,
        host: str,
        port: int,
        tls_enabled: bool,
        ca_cert: str | None,
        client_cert: str | None,
        client_key: str | None,
        app_name: str = "App_Bedelia",
    ):
        self.host = host
        self.port = int(port)
        self.tls_enabled = tls_enabled

        client_id = f"{app_name}-{uuid.uuid4()}"
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log

        if self.tls_enabled:
            if not (ca_cert and client_cert and client_key):
                raise RuntimeError(
                    "TLS habilitado pero faltan rutas de certificados (CA/CERT/KEY)."
                )

            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
            ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            self.client.tls_set_context(ctx)
            self.client.tls_insecure_set(False)

        # Conectar + loop
        # OJO: connect() no garantiza handshake completo hasta que corre el loop.
        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()

        # Espera corta para estabilizar
        for _ in range(30):
            if self.client.is_connected():
                break
            time.sleep(0.1)

    def on_log(self, client, userdata, level, buf):
        print(f"[MQTT LOG] {buf}")

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print(f"❌ MQTT CONNACK rc={rc}")
        else:
            print("✅ MQTT conectado")
            # Suscribirse a tópicos después de conectar
            self._subscribe_to_topics()

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"⚠️ MQTT desconectado inesperadamente rc={rc}")

    def on_message(self, client, userdata, msg):
        """Callback cuando llega un mensaje"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            print(f"📩 Mensaje recibido en {topic}: {payload[:100]}...")
            
            # Aquí puedes agregar lógica para procesar mensajes
            # Por ejemplo, actualizar Redis, notificar a WebSockets, etc.
            
        except Exception as e:
            print(f"❌ Error al procesar mensaje MQTT: {e}")

    def _subscribe_to_topics(self):
        """Suscribe a los tópicos relevantes para Bedelia"""
        try:
            # Bedelia escucha solicitudes de asignación
            self.client.subscribe(TOPICS['ASIGNACION_AULA'], qos=1)
            print(f"✅ Suscrito a: {TOPICS['ASIGNACION_AULA']}")
            
            # Bedelia escucha solicitudes de liberación
            self.client.subscribe(TOPICS['LIBERAR_AULA'], qos=1)
            print(f"✅ Suscrito a: {TOPICS['LIBERAR_AULA']}")
            
            # Bedelia puede escuchar métricas
            self.client.subscribe(TOPICS['METRICAS_EMQX'], qos=0)
            print(f"✅ Suscrito a: {TOPICS['METRICAS_EMQX']}")
            
            # Escuchar notificaciones con wildcard
            self.client.subscribe(TOPICS['NOTIFICACION_AULA_WILDCARD'], qos=0)
            print(f"✅ Suscrito a: {TOPICS['NOTIFICACION_AULA_WILDCARD']}")
            
        except Exception as e:
            print(f"❌ Error al suscribirse a tópicos: {e}")

    def publish(self, topic: str, payload: dict, qos: int = 1, retain: bool = False):
        """
        Publica un mensaje en un tópico MQTT
        
        Args:
            topic: Tópico MQTT
            payload: Diccionario con los datos a publicar
            qos: Quality of Service (0, 1, 2)
            retain: Si el mensaje debe ser retenido por el broker
        """
        message = json.dumps(payload, default=str)
        result = self.client.publish(topic, message, qos=qos, retain=retain)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Error publicando mensaje en {topic}: rc={result.rc}")
        return True


# ---------- Lazy init (clave para que NO muera el contenedor) ----------
_mqtt_client: MQTTClient | None = None


def get_mqtt_client() -> MQTTClient | None:
    """
    Devuelve el cliente si pudo conectarse. Si no, devuelve None.
    No mata el proceso: la app puede levantar igual y reintentar luego.
    """
    global _mqtt_client
    if _mqtt_client is not None:
        return _mqtt_client

    host = os.getenv("MQTT_BROKER_HOST", "emqx")
    port = int(os.getenv("MQTT_BROKER_PORT", "8883"))
    tls_enabled = _env_bool(os.getenv("MQTT_TLS_ENABLED", "true"))

    ca_cert = os.getenv("MQTT_TLS_CA_CERT")
    client_cert = os.getenv("MQTT_TLS_CERT")
    client_key = os.getenv("MQTT_TLS_KEY")
    app_name = os.getenv("APP_NAME", "App_Bedelia")

    print("[MQTT INIT] host=", host)
    print("[MQTT INIT] port=", port)
    print("[MQTT INIT] tls_enabled=", tls_enabled)
    print("[MQTT INIT] ca_cert=", ca_cert)
    print("[MQTT INIT] client_cert=", client_cert)
    print("[MQTT INIT] client_key=", client_key)

    try:
        _mqtt_client = MQTTClient(
            host=host,
            port=port,
            tls_enabled=tls_enabled,
            ca_cert=ca_cert,
            client_cert=client_cert,
            client_key=client_key,
            app_name=app_name,
        )
        return _mqtt_client
    except Exception as e:
        print(f"❌ No se pudo inicializar MQTT: {e}")
        return None
