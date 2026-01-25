"""
MQTT Event Publisher - Helpers para publicar eventos en topics estructurados
Según convención del prompt MAESTRO: universidad/{dominio}/{accion}/{identificadores}
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from mqtt_client import mqtt_client


class MQTTEventPublisher:
    """
    Helper para publicar eventos MQTT con topics estructurados
    """
    
    # Prefijo base para todos los topics
    BASE_TOPIC = "universidad"
    
    @staticmethod
    def _publicar(topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
        """
        Método interno para publicar en MQTT
        
        Args:
            topic: Topic completo
            payload: Diccionario con los datos
            qos: Quality of Service (0, 1, 2)
        
        Returns:
            True si se publicó correctamente, False si no
        """
        try:
            # Agregar timestamp automático
            payload["timestamp"] = datetime.utcnow().isoformat()
            
            # Convertir a JSON
            mensaje = json.dumps(payload, default=str)
            
            # Publicar
            resultado = mqtt_client.publish(topic, mensaje, qos)
            
            return resultado
        except Exception as e:
            print(f"❌ Error al publicar en MQTT: {e}")
            return False
    
    # ========== AULAS ==========
    
    @staticmethod
    def publicar_aula_nueva(id_aula: str, datos_aula: Dict[str, Any]) -> bool:
        """
        Publica evento de aula nueva
        Topic: universidad/aulas/nueva
        
        Args:
            id_aula: ID del aula creada
            datos_aula: Datos del aula (nro_aula, piso, cupo, etc.)
        
        Returns:
            True si se publicó correctamente
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/aulas/nueva"
        
        payload = {
            "evento": "aula_nueva",
            "id_aula": id_aula,
            **datos_aula
        }
        
        return MQTTEventPublisher._publicar(topic, payload)
    
    @staticmethod
    def publicar_aula_asignada(id_aula: str, id_carrera: str, id_materia: str, datos_cronograma: Dict[str, Any]) -> bool:
        """
        Publica evento de aula asignada
        Topic: universidad/eventos/aula/asignada/{id_carrera}/{id_materia}
        
        Args:
            id_aula: ID del aula asignada
            id_carrera: ID de la carrera
            id_materia: ID de la materia
            datos_cronograma: Datos del cronograma (fecha, hora, profesor, etc.)
        
        Returns:
            True si se publicó correctamente
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/eventos/aula/asignada/{id_carrera}/{id_materia}"
        
        payload = {
            "evento": "aula_asignada",
            "id_aula": id_aula,
            "id_carrera": id_carrera,
            "id_materia": id_materia,
            **datos_cronograma
        }
        
        return MQTTEventPublisher._publicar(topic, payload)
    
    @staticmethod
    def publicar_aula_liberada(id_aula: str, id_carrera: str, id_materia: str, id_cronograma: str) -> bool:
        """
        Publica evento de aula liberada
        Topic: universidad/eventos/aula/liberada/{id_carrera}/{id_materia}
        
        Args:
            id_aula: ID del aula liberada
            id_carrera: ID de la carrera
            id_materia: ID de la materia
            id_cronograma: ID del cronograma finalizado
        
        Returns:
            True si se publicó correctamente
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/eventos/aula/liberada/{id_carrera}/{id_materia}"
        
        payload = {
            "evento": "aula_liberada",
            "id_aula": id_aula,
            "id_carrera": id_carrera,
            "id_materia": id_materia,
            "id_cronograma": id_cronograma
        }
        
        return MQTTEventPublisher._publicar(topic, payload)
    
    # ========== NOTIFICACIONES ==========
    
    @staticmethod
    def publicar_notificacion_aula(id_carrera: str, id_materia: str, mensaje: str, tipo: str = "info") -> bool:
        """
        Publica notificación para alumnos de una carrera/materia
        Topic: universidad/notificaciones/aula/{id_carrera}/{id_materia}
        
        Args:
            id_carrera: ID de la carrera
            id_materia: ID de la materia
            mensaje: Mensaje de notificación
            tipo: Tipo de notificación ("info", "warning", "error")
        
        Returns:
            True si se publicó correctamente
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/notificaciones/aula/{id_carrera}/{id_materia}"
        
        payload = {
            "tipo": tipo,
            "mensaje": mensaje,
            "id_carrera": id_carrera,
            "id_materia": id_materia
        }
        
        return MQTTEventPublisher._publicar(topic, payload)
    
    # ========== ERRORES ==========
    
    @staticmethod
    def publicar_error_profesor(id_profesor: str, motivo: str, detalles: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publica error específico para un profesor
        Topic: universidad/errores/profesor/{id_profesor}
        
        Args:
            id_profesor: ID del profesor
            motivo: Motivo del error (ej: "cupo_excedido", "horario_invalido")
            detalles: Detalles adicionales del error
        
        Returns:
            True si se publicó correctamente
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/errores/profesor/{id_profesor}"
        
        payload = {
            "evento": "error",
            "id_profesor": id_profesor,
            "motivo": motivo,
            "detalles": detalles or {}
        }
        
        return MQTTEventPublisher._publicar(topic, payload)
    
    @staticmethod
    def publicar_error_usuario(id_usuario: str, motivo: str, detalles: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publica error genérico para un usuario
        Topic: universidad/errores/{id_usuario}
        
        Args:
            id_usuario: ID del usuario
            motivo: Motivo del error
            detalles: Detalles adicionales del error
        
        Returns:
            True si se publicó correctamente
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/errores/{id_usuario}"
        
        payload = {
            "evento": "error",
            "id_usuario": id_usuario,
            "motivo": motivo,
            "detalles": detalles or {}
        }
        
        return MQTTEventPublisher._publicar(topic, payload)
    
    # ========== MÉTRICAS ==========
    
    @staticmethod
    def publicar_metricas_aulas(total_aulas: int, disponibles: int, ocupadas: int, deshabilitadas: int) -> bool:
        """
        Publica métricas de estado de aulas
        Topic: universidad/metricas/aulas
        
        Args:
            total_aulas: Total de aulas
            disponibles: Aulas disponibles
            ocupadas: Aulas ocupadas
            deshabilitadas: Aulas deshabilitadas
        
        Returns:
            True si se publicó correctamente
        """
        topic = f"{MQTTEventPublisher.BASE_TOPIC}/metricas/aulas"
        
        payload = {
            "total_aulas": total_aulas,
            "disponibles": disponibles,
            "ocupadas": ocupadas,
            "deshabilitadas": deshabilitadas
        }
        
        return MQTTEventPublisher._publicar(topic, payload, qos=0)  # QoS 0 para métricas
