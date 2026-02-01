# """
# MQTT Event Publisher - Helpers para publicar eventos en topics estructurados
# Según convención del prompt MAESTRO: universidad/{dominio}/{accion}/{identificadores}
# """

# import json
# from typing import Dict, Any, Optional
# from datetime import datetime


# class MQTTEventPublisher:
#     """
#     Helper para publicar eventos MQTT con topics estructurados
#     """
    
#     # Prefijo base para todos los topics
#     BASE_TOPIC = "universidad"
    
#     @staticmethod
#     def _get_mqtt_client():
#         """
#         Importación lazy de mqtt_client para evitar imports circulares
#         """
#         from mqtt_client import mqtt_client
#         return mqtt_client

#     @staticmethod
#     def _publicar(topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
#         """
#         Método interno para publicar en MQTT
        
#         Args:
#             topic: Topic completo
#             payload: Diccionario con los datos
#             qos: Quality of Service (0, 1, 2)
        
#         Returns:
#             True si se publicó correctamente, False si no
#         """
#         try:
#             # Agregar timestamp automático
#             payload["timestamp"] = datetime.utcnow().isoformat()
            
#             # Convertir a JSON
#             mensaje = json.dumps(payload, default=str)
            
#             # Obtener cliente MQTT
#             from mqtt_client import get_mqtt_client
#             mqtt_client = get_mqtt_client()
            
#             # Publicar
#             mqtt_client.publish(topic, mensaje, qos)
            
#             return True
#         except Exception as e:
#             print(f"❌ Error al publicar en MQTT: {e}")
#             return False
    
#     # ========== AULAS ==========
    
#     @staticmethod
#     def publicar_aula_nueva(id_aula: str, datos_aula: Dict[str, Any]) -> bool:
#         """
#         Publica evento de aula nueva
#         Topic: universidad/aulas/nueva
        
#         Args:
#             id_aula: ID del aula creada
#             datos_aula: Datos del aula (nro_aula, piso, cupo, etc.)
        
#         Returns:
#             True si se publicó correctamente
#         """
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/aulas/nueva"
        
#         payload = {
#             "evento": "aula_nueva",
#             "id_aula": id_aula,
#             **datos_aula
#         }
        
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     @staticmethod
#     def publicar_aula_asignada(id_aula: str, id_carrera: str, id_materia: str, datos_cronograma: Dict[str, Any]) -> bool:
#         """
#         Publica evento de aula asignada
#         Topic: universidad/eventos/aula/asignada/{id_carrera}/{id_materia}
        
#         Args:
#             id_aula: ID del aula asignada
#             id_carrera: ID de la carrera
#             id_materia: ID de la materia
#             datos_cronograma: Datos del cronograma (fecha, hora, profesor, etc.)
        
#         Returns:
#             True si se publicó correctamente
#         """
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/eventos/aula/asignada/{id_carrera}/{id_materia}"
        
#         payload = {
#             "evento": "aula_asignada",
#             "id_aula": id_aula,
#             "id_carrera": id_carrera,
#             "id_materia": id_materia,
#             **datos_cronograma
#         }
        
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     @staticmethod
#     def publicar_aula_liberada(id_aula: str, id_carrera: str, id_materia: str, id_cronograma: str) -> bool:
#         """
#         Publica evento de aula liberada
#         Topic: universidad/eventos/aula/liberada/{id_carrera}/{id_materia}
        
#         Args:
#             id_aula: ID del aula liberada
#             id_carrera: ID de la carrera
#             id_materia: ID de la materia
#             id_cronograma: ID del cronograma finalizado
        
#         Returns:
#             True si se publicó correctamente
#         """
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/eventos/aula/liberada/{id_carrera}/{id_materia}"
        
#         payload = {
#             "evento": "aula_liberada",
#             "id_aula": id_aula,
#             "id_carrera": id_carrera,
#             "id_materia": id_materia,
#             "id_cronograma": id_cronograma
#         }
        
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     # ========== NOTIFICACIONES ==========
    
#     @staticmethod
#     def publicar_notificacion_aula(id_carrera: str, id_materia: str, mensaje: str, tipo: str = "info") -> bool:
#         """
#         Publica notificación para alumnos de una carrera/materia
#         Topic: universidad/notificaciones/aula/{id_carrera}/{id_materia}
        
#         Args:
#             id_carrera: ID de la carrera
#             id_materia: ID de la materia
#             mensaje: Mensaje de notificación
#             tipo: Tipo de notificación ("info", "warning", "error")
        
#         Returns:
#             True si se publicó correctamente
#         """
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/notificaciones/aula/{id_carrera}/{id_materia}"
        
#         payload = {
#             "tipo": tipo,
#             "mensaje": mensaje,
#             "id_carrera": id_carrera,
#             "id_materia": id_materia
#         }
        
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     # ========== ERRORES ==========
    
#     @staticmethod
#     def publicar_error_profesor(id_profesor: str, motivo: str, detalles: Optional[Dict[str, Any]] = None) -> bool:
#         """
#         Publica error específico para un profesor
#         Topic: universidad/errores/profesor/{id_profesor}
        
#         Args:
#             id_profesor: ID del profesor
#             motivo: Motivo del error (ej: "cupo_excedido", "horario_invalido")
#             detalles: Detalles adicionales del error
        
#         Returns:
#             True si se publicó correctamente
#         """
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/errores/profesor/{id_profesor}"
        
#         payload = {
#             "evento": "error",
#             "id_profesor": id_profesor,
#             "motivo": motivo,
#             "detalles": detalles or {}
#         }
        
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     @staticmethod
#     def publicar_error_usuario(id_usuario: str, motivo: str, detalles: Optional[Dict[str, Any]] = None) -> bool:
#         """
#         Publica error genérico para un usuario
#         Topic: universidad/errores/{id_usuario}
        
#         Args:
#             id_usuario: ID del usuario
#             motivo: Motivo del error
#             detalles: Detalles adicionales del error
        
#         Returns:
#             True si se publicó correctamente
#         """
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/errores/{id_usuario}"
        
#         payload = {
#             "evento": "error",
#             "id_usuario": id_usuario,
#             "motivo": motivo,
#             "detalles": detalles or {}
#         }
        
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     # ========== MÉTRICAS ==========
    
#     @staticmethod
#     def publicar_metricas_aulas(total_aulas: int, disponibles: int, ocupadas: int, deshabilitadas: int) -> bool:
#         """
#         Publica métricas de estado de aulas
#         Topic: universidad/metricas/aulas
        
#         Args:
#             total_aulas: Total de aulas
#             disponibles: Aulas disponibles
#             ocupadas: Aulas ocupadas
#             deshabilitadas: Aulas deshabilitadas
        
#         Returns:
#             True si se publicó correctamente
#         """
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/metricas/aulas"
        
#         payload = {
#             "total_aulas": total_aulas,
#             "disponibles": disponibles,
#             "ocupadas": ocupadas,
#             "deshabilitadas": deshabilitadas
#         }
        
#         return MQTTEventPublisher._publicar(topic, payload, qos=0)  # QoS 0 para métricas

# """
# MQTT Event Publisher - Publica eventos de negocio en MQTT
# """

# import json
# from datetime import datetime
# from typing import Dict, Any


# class MQTTEventPublisher:
#     """
#     Publicador de eventos MQTT con topics estructurados
#     """
    
#     BASE_TOPIC = "universidad"
    
#     @staticmethod
#     def _get_mqtt_client():
#         """Importación lazy para evitar imports circulares"""
#         from mqtt_client import mqtt_client
#         return mqtt_client
    
#     @staticmethod
#     def _publicar(topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
#         """
#         Publica un mensaje en MQTT
        
#         Args:
#             topic: Topic completo (ej: universidad/aulas/nueva)
#             payload: Diccionario con datos del evento
#             qos: Quality of Service (default: 1)
            
#         Returns:
#             bool: True si se publicó correctamente
#         """
#         try:
#             mqtt_client = MQTTEventPublisher._get_mqtt_client()
            
#             if not mqtt_client.connected:
#                 print("⚠️  MQTT no conectado")
#                 return False
            
#             # Agregar timestamp automático
#             payload["timestamp"] = datetime.utcnow().isoformat()
            
#             # Convertir a JSON string
#             mensaje = json.dumps(payload, default=str)
            
#             # ✅ CORRECCIÓN: Pasar payload como string, no dict
#             resultado = mqtt_client.publish(topic, mensaje, qos)
            
#             if resultado:
#                 print(f"✅ Evento publicado en {topic}")
#             else:
#                 print(f"❌ Error al publicar en {topic}")
                
#             return resultado
            
#         except Exception as e:
#             print(f"❌ Error al publicar en MQTT: {e}")
#             return False
    
#     # ==================== EVENTOS DE AULAS ====================
    
#     @staticmethod
#     def publicar_aula_nueva(id_aula: str, datos_aula: Dict[str, Any]) -> bool:
#         """Publica evento cuando se crea una nueva aula"""
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/aulas/nueva"
#         payload = {
#             "evento": "aula_nueva",
#             "id_aula": id_aula,
#             "datos": datos_aula
#         }
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     @staticmethod
#     def publicar_aula_asignada(id_aula: str, id_cronograma: str, datos: Dict[str, Any]) -> bool:
#         """Publica evento cuando se asigna un aula"""
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/aulas/asignada"
#         payload = {
#             "evento": "aula_asignada",
#             "id_aula": id_aula,
#             "id_cronograma": id_cronograma,
#             "datos": datos
#         }
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     @staticmethod
#     def publicar_aula_liberada(id_aula: str, id_cronograma: str, motivo: str = "finalizado") -> bool:
#         """Publica evento cuando se libera un aula"""
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/aulas/liberada"
#         payload = {
#             "evento": "aula_liberada",
#             "id_aula": id_aula,
#             "id_cronograma": id_cronograma,
#             "motivo": motivo
#         }
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     # ==================== NOTIFICACIONES ====================
    
#     @staticmethod
#     def notificar_alumnos(carrera: str, id_materia: str, mensaje: str, datos: Dict[str, Any]) -> bool:
#         """Notifica a alumnos de una carrera/materia específica"""
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/notificaciones/{carrera}/{id_materia}"
#         payload = {
#             "evento": "notificacion_alumnos",
#             "carrera": carrera,
#             "id_materia": id_materia,
#             "mensaje": mensaje,
#             "datos": datos
#         }
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     @staticmethod
#     def notificar_profesor(id_profesor: str, mensaje: str, datos: Dict[str, Any]) -> bool:
#         """Notifica a un profesor específico"""
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/notificaciones/profesor/{id_profesor}"
#         payload = {
#             "evento": "notificacion_profesor",
#             "id_profesor": id_profesor,
#             "mensaje": mensaje,
#             "datos": datos
#         }
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     # ==================== ERRORES Y ALERTAS ====================
    
#     @staticmethod
#     def publicar_error_profesor(id_profesor: str, error: str, contexto: Dict[str, Any]) -> bool:
#         """Publica error específico de un profesor"""
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/errores/profesor/{id_profesor}"
#         payload = {
#             "evento": "error_profesor",
#             "id_profesor": id_profesor,
#             "error": error,
#             "contexto": contexto
#         }
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     @staticmethod
#     def publicar_error_usuario(id_usuario: str, error: str, contexto: Dict[str, Any]) -> bool:
#         """Publica error de un usuario"""
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/errores/usuario/{id_usuario}"
#         payload = {
#             "evento": "error_usuario",
#             "id_usuario": id_usuario,
#             "error": error,
#             "contexto": contexto
#         }
#         return MQTTEventPublisher._publicar(topic, payload)
    
#     # ==================== MÉTRICAS ====================
    
#     @staticmethod
#     def publicar_metricas_aulas(metricas: Dict[str, Any]) -> bool:
#         """Publica métricas de uso de aulas"""
#         topic = f"{MQTTEventPublisher.BASE_TOPIC}/metricas/aulas"
#         payload = {
#             "evento": "metricas_aulas",
#             "metricas": metricas
#         }
#         return MQTTEventPublisher._publicar(topic, payload)
"""
MQTT Event Publisher - Publica eventos de negocio en MQTT
"""

import json
from datetime import datetime
from typing import Dict, Any

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
    # Formato: universidad/eventos/aula/{tipo}/{id_carrera}/{id_materia}
    'EVENTO_AULA_ASIGNADA': 'universidad/eventos/aula/asignada',  # Base, se completa con IDs
    'EVENTO_AULA_LIBERADA': 'universidad/eventos/aula/liberada',   # Base, se completa con IDs
    
    # ======================
    # NOTIFICACIONES (con IDs dinámicos)
    # ======================
    # Formato: universidad/notificaciones/aula/{id_carrera}/{id_materia}
    'NOTIFICACION_AULA': 'universidad/notificaciones/aula',  # Base, se completa con IDs
    'NOTIFICACION_AULA_WILDCARD': 'universidad/notificaciones/aula/+/+',  # Suscripción a todas
    
    # ======================
    # ERRORES (con IDs dinámicos)
    # ======================
    'ERROR_PROFESOR': 'universidad/errores/profesor',  # Base, se completa con id_profesor
    'ERROR_USUARIO': 'universidad/errores',  # Base, se completa con id_usuario
    
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
    
    Args:
        id_carrera: ID de la carrera (string o ObjectId convertido)
        id_materia: ID de la materia (string o ObjectId convertido)
    
    Returns:
        Topic completo: "universidad/eventos/aula/asignada/{id_carrera}/{id_materia}"
    
    Ejemplo:
        >>> build_topic_evento_asignada("507f1f77bcf86cd799439011", "507f191e810c19729de860ea")
        'universidad/eventos/aula/asignada/507f1f77bcf86cd799439011/507f191e810c19729de860ea'
    """
    return f"{TOPICS['EVENTO_AULA_ASIGNADA']}/{id_carrera}/{id_materia}"


def build_topic_evento_liberada(id_carrera: str, id_materia: str) -> str:
    """
    Construye el topic de evento de aula liberada
    Formato: universidad/eventos/aula/liberada/{id_carrera}/{id_materia}
    
    Args:
        id_carrera: ID de la carrera (string o ObjectId convertido)
        id_materia: ID de la materia (string o ObjectId convertido)
    
    Returns:
        Topic completo: "universidad/eventos/aula/liberada/{id_carrera}/{id_materia}"
    """
    return f"{TOPICS['EVENTO_AULA_LIBERADA']}/{id_carrera}/{id_materia}"


def build_topic_notificacion(id_carrera: str, id_materia: str) -> str:
    """
    Construye el topic de notificación de aula
    Formato: universidad/notificaciones/aula/{id_carrera}/{id_materia}
    
    Args:
        id_carrera: ID de la carrera (string o ObjectId convertido)
        id_materia: ID de la materia (string o ObjectId convertido)
    
    Returns:
        Topic completo: "universidad/notificaciones/aula/{id_carrera}/{id_materia}"
    """
    return f"{TOPICS['NOTIFICACION_AULA']}/{id_carrera}/{id_materia}"


def build_topic_error_profesor(id_profesor: str) -> str:
    """
    Construye el topic de error de profesor
    Formato: universidad/errores/profesor/{id_profesor}
    
    Args:
        id_profesor: ID del profesor (string o ObjectId convertido)
    
    Returns:
        Topic completo: "universidad/errores/profesor/{id_profesor}"
    """
    return f"{TOPICS['ERROR_PROFESOR']}/{id_profesor}"


def build_topic_error_usuario(id_usuario: str) -> str:
    """
    Construye el topic de error de usuario
    Formato: universidad/errores/{id_usuario}
    
    Args:
        id_usuario: ID del usuario (string o ObjectId convertido)
    
    Returns:
        Topic completo: "universidad/errores/{id_usuario}"
    """
    return f"{TOPICS['ERROR_USUARIO']}/{id_usuario}"

class MQTTEventPublisher:
    """
    Publicador de eventos MQTT con topics estructurados
    """
    
    BASE_TOPIC = "universidad"
    
    @staticmethod
    def _get_mqtt_client():
        """Importación lazy para evitar imports circulares"""
        from mqtt_client import get_mqtt_client  # ✅ CORRECCIÓN 1: Importar función, no variable
        return get_mqtt_client()
    
    @staticmethod
    def _publicar(topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
        """
        Publica un mensaje en MQTT
        
        Args:
            topic: Topic completo (ej: universidad/aulas/nueva)
            payload: Diccionario con datos del evento
            qos: Quality of Service (default: 1)
            
        Returns:
            bool: True si se publicó correctamente
        """
        try:
            mqtt_client = MQTTEventPublisher._get_mqtt_client()
            
            # ✅ CORRECCIÓN 2: Verificar que el cliente exista y esté conectado
            if not mqtt_client or not mqtt_client.client.is_connected():
                print("⚠️  MQTT no conectado")
                return False
            
            # Agregar timestamp automático
            payload["timestamp"] = datetime.utcnow().isoformat()
            
            # Convertir a JSON
            mensaje = json.dumps(payload, default=str)
            
            # Publicar
            mqtt_client.publish(topic, payload)
            print(f"✅ Evento publicado en {topic}")
            return True
            
        except Exception as e:
            print(f"❌ Error al publicar en MQTT: {e}")
            return False
    
    # ==================== EVENTOS DE AULAS ====================
    
    @staticmethod
    def publicar_aula_nueva(id_aula: str, datos_aula: Dict[str, Any]) -> bool:
        """Publica evento cuando se crea una nueva aula"""
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/aulas/nueva"
        payload = {
            "evento": "aula_nueva",
            "id_aula": id_aula,
            "datos": datos_aula
        }
        return MQTTEventPublisher._publicar(topic, payload)
    
    @staticmethod
    def publicar_aula_asignada(id_aula: str, id_carrera: int, id_materia: int, datos: Dict[str, Any]) -> bool:
        """
        Publica evento cuando se asigna un aula a una carrera/materia
        
        Topic: universidad/eventos/aula/asignada/{id_carrera}/{id_materia}
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/eventos/aula/asignada/{id_carrera}/{id_materia}"
        payload = {
            "evento": "aula_asignada",
            "id_aula": id_aula,
            "id_carrera": id_carrera,
            "id_materia": id_materia,
            "datos": datos
        }
        return MQTTEventPublisher._publicar(topic, payload)
    
    @staticmethod
    def publicar_aula_liberada(id_aula: str, id_cronograma: str, motivo: str = "finalizado") -> bool:
        """Publica evento cuando se libera un aula"""
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/aulas/liberada"
        payload = {
            "evento": "aula_liberada",
            "id_aula": id_aula,
            "id_cronograma": id_cronograma,
            "motivo": motivo
        }
        return MQTTEventPublisher._publicar(topic, payload)
    
    # ==================== NOTIFICACIONES ====================
    
    @staticmethod
    def notificar_alumnos(id_carrera: int, id_materia: int, mensaje: str, datos: Dict[str, Any]) -> bool:
        """
        Notifica a alumnos de una carrera/materia específica
        
        Args:
            id_carrera: ID numérico de la carrera (ej: 1, 2, 3)
            id_materia: ID numérico de la materia (ej: 101, 102)
            mensaje: Mensaje de notificación
            datos: Datos adicionales
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/notificaciones/aula/{id_carrera}/{id_materia}"
        payload = {
            "evento": "notificacion_alumnos",
            "id_carrera": id_carrera,
            "id_materia": id_materia,
            "mensaje": mensaje,
            "datos": datos
        }
        return MQTTEventPublisher._publicar(topic, payload)
    
    @staticmethod
    def notificar_profesor(id_profesor: str, mensaje: str, datos: Dict[str, Any]) -> bool:
        """Notifica a un profesor específico"""
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/notificaciones/profesor/{id_profesor}"
        payload = {
            "evento": "notificacion_profesor",
            "id_profesor": id_profesor,
            "mensaje": mensaje,
            "datos": datos
        }
        return MQTTEventPublisher._publicar(topic, payload)
    
    # ==================== ERRORES Y ALERTAS ====================
    
    @staticmethod
    def publicar_error_profesor(id_profesor: str, error: str, contexto: Dict[str, Any]) -> bool:
        """Publica error específico de un profesor"""
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/errores/profesor/{id_profesor}"
        payload = {
            "evento": "error_profesor",
            "id_profesor": id_profesor,
            "error": error,
            "contexto": contexto
        }
        return MQTTEventPublisher._publicar(topic, payload)
    
    @staticmethod
    def publicar_error_usuario(id_usuario: str, error: str, contexto: Dict[str, Any]) -> bool:
        """Publica error de un usuario"""
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/errores/usuario/{id_usuario}"
        payload = {
            "evento": "error_usuario",
            "id_usuario": id_usuario,
            "error": error,
            "contexto": contexto
        }
        return MQTTEventPublisher._publicar(topic, payload)
    
    # ==================== MÉTRICAS ====================
    
    @staticmethod
    def publicar_metricas_aulas(total: int, disponibles: int, ocupadas: int, deshabilitadas: int) -> bool:
        """
        Publica métricas de uso de aulas
        
        Args:
            total: Total de aulas
            disponibles: Aulas disponibles
            ocupadas: Aulas ocupadas
            deshabilitadas: Aulas deshabilitadas
            
        Returns:
            bool: True si se publicó correctamente
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/metricas/aulas"
        payload = {
            "evento": "metricas_aulas",
            "total_aulas": total,
            "disponibles": disponibles,
            "ocupadas": ocupadas,
            "deshabilitadas": deshabilitadas
        }
        return MQTTEventPublisher._publicar(topic, payload, qos=0)  # QoS 0 para métricas