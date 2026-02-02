"""
AulaService - Lógica de negocio para gestión de aulas
Incluye: CRUD, asignación, liberación, caché Redis, eventos MQTT
"""

import json
from typing import List, Dict, Any, Optional
from bson import ObjectId
from datetime import datetime

from db.mongo import get_mongo_db
from db.redis import redis_client
from models.aula import AulaModel
from utils.validators import Validators
from utils.mqtt_events import MQTTEventPublisher


class AulaService:
    """
    Service para gestión de aulas con Redis y MQTT
    """
    
    CACHE_KEY_PREFIX = "aula:"
    CACHE_KEY_ALL = "aulas:all"
    CACHE_TTL = 300  # 5 minutos
    LOCK_KEY_PREFIX = "lock:aula:"
    LOCK_TTL = 30  # 30 segundos
    
    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db.aulas
    
    def crear_aula(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un aula nueva
        
        Args:
            data: Datos del aula (nro_aula, piso, cupo, estado, descripcion)
        
        Returns:
            Diccionario con id y mensaje de éxito
        
        Raises:
            ValueError: Si los datos son inválidos o ya existe
        """
        try:
            # Crear aula en MongoDB
            id_aula = AulaModel.crear(self.collection, data)
            
            # Invalidar caché de lista de aulas
            redis_client.client.delete(self.CACHE_KEY_ALL)
            
            # Obtener aula creada
            aula = AulaModel.obtener_por_id(self.collection, id_aula)
            
            # Publicar evento MQTT
            try:
                MQTTEventPublisher.publicar_aula_nueva(
                    str(id_aula),
                    {
                        "nro_aula": aula["nro_aula"],
                        "piso": aula["piso"],
                        "cupo": aula["cupo"],
                        "estado": aula["estado"]
                    }
                )
            except Exception as e:
                print(f"⚠️  Error al publicar evento MQTT: {e}")
            
            return {
                "id": str(id_aula),
                "mensaje": "Aula creada correctamente"
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al crear aula: {e}")
    
    def obtener_aula(self, id_aula: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un aula por ID (con caché Redis)
        
        Args:
            id_aula: ID del aula (string)
        
        Returns:
            Diccionario con datos del aula o None si no existe
        """
        try:
            # Intentar obtener de caché
            cache_key = f"{self.CACHE_KEY_PREFIX}{id_aula}"
            cached = redis_client.client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            # Si no está en caché, consultar MongoDB
            obj_id = Validators.convertir_a_objectid(id_aula)
            aula = AulaModel.obtener_por_id(self.collection, obj_id)
            
            if aula:
                # Convertir ObjectId a string para JSON
                aula["_id"] = str(aula["_id"])
                if aula.get("id_asignacion_actual"):
                    aula["id_asignacion_actual"] = str(aula["id_asignacion_actual"])
                
                # Guardar en caché
                redis_client.client.setex(
                    cache_key,
                    self.CACHE_TTL,
                    json.dumps(aula, default=str)
                )
            
            return aula
        
        except Exception as e:
            print(f"Error al obtener aula: {e}")
            return None
    
    def listar_aulas(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lista aulas con filtros opcionales (con caché Redis)
        
        Args:
            filtros: Diccionario de filtros (ej: {"estado": "disponible"})
        
        Returns:
            Lista de aulas
        """
        try:
            # Si no hay filtros, intentar obtener de caché
            if not filtros:
                cached = redis_client.client.get(self.CACHE_KEY_ALL)
                
                if cached:
                    return json.loads(cached)
            
            # Consultar MongoDB
            aulas = AulaModel.listar(self.collection, filtros)
            
            # Convertir ObjectIds a strings
            for aula in aulas:
                aula["_id"] = str(aula["_id"])
                if aula.get("id_asignacion_actual"):
                    aula["id_asignacion_actual"] = str(aula["id_asignacion_actual"])
            
            # Si no hay filtros, guardar en caché
            if not filtros:
                redis_client.client.setex(
                    self.CACHE_KEY_ALL,
                    self.CACHE_TTL,
                    json.dumps(aulas, default=str)
                )
            
            return aulas
        
        except Exception as e:
            print(f"Error al listar aulas: {e}")
            return []
    
    def actualizar_aula(self, id_aula: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un aula existente
        
        Args:
            id_aula: ID del aula
            data: Datos a actualizar
        
        Returns:
            Diccionario con mensaje de éxito
        
        Raises:
            ValueError: Si el aula no existe o los datos son inválidos
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_aula)
            
            # Actualizar en MongoDB
            AulaModel.actualizar(self.collection, obj_id, data)
            
            # Invalidar caché
            redis_client.client.delete(f"{self.CACHE_KEY_PREFIX}{id_aula}")
            redis_client.client.delete(self.CACHE_KEY_ALL)
            
            return {"mensaje": "Aula actualizada correctamente"}
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al actualizar aula: {e}")
    
    def cambiar_estado_aula(self, id_aula: str, nuevo_estado: str) -> Dict[str, Any]:
        """
        Cambia el estado de un aula (disponible, ocupada, deshabilitada)
        
        Args:
            id_aula: ID del aula
            nuevo_estado: Nuevo estado
        
        Returns:
            Diccionario con mensaje de éxito
        
        Raises:
            ValueError: Si el estado es inválido o el aula no existe
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_aula)
            
            # Cambiar estado en MongoDB
            AulaModel.cambiar_estado(self.collection, obj_id, nuevo_estado)
            
            # Invalidar caché
            redis_client.client.delete(f"{self.CACHE_KEY_PREFIX}{id_aula}")
            redis_client.client.delete(self.CACHE_KEY_ALL)
            
            return {
                "mensaje": f"Estado del aula cambiado a '{nuevo_estado}'"
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al cambiar estado: {e}")
    
    def asignar_aula(self, id_aula: str, id_cronograma: str) -> Dict[str, Any]:
        """
        Asigna un aula a un cronograma (con lock distribuido)
        
        Args:
            id_aula: ID del aula
            id_cronograma: ID del cronograma
        
        Returns:
            Diccionario con mensaje de éxito
        
        Raises:
            ValueError: Si el aula no está disponible o hay conflicto
        """
        lock_key = f"{self.LOCK_KEY_PREFIX}{id_aula}"
        
        try:
            # Intentar adquirir lock
            lock_adquirido = redis_client.acquire_lock(lock_key)
            
            if not lock_adquirido:
                raise ValueError("El aula está siendo procesada por otra operación. Intente nuevamente.")
            
            # Convertir IDs
            obj_id_aula = Validators.convertir_a_objectid(id_aula)
            obj_id_cronograma = Validators.convertir_a_objectid(id_cronograma)
            
            # Asignar en MongoDB
            resultado = AulaModel.asignar(self.collection, obj_id_aula, obj_id_cronograma)
            
            if not resultado:
                raise ValueError("El aula no está disponible para asignación")
            
            # Invalidar caché
            redis_client.client.delete(f"{self.CACHE_KEY_PREFIX}{id_aula}")
            redis_client.client.delete(self.CACHE_KEY_ALL)
            
            return {"mensaje": "Aula asignada correctamente"}
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al asignar aula: {e}")
        finally:
            # Liberar lock
            redis_client.release_lock(lock_key)
    
    def liberar_aula(self, id_aula: str, publicar_evento: bool = True) -> Dict[str, Any]:
        """
        Libera un aula (disponible, sin asignación)
        
        Args:
            id_aula: ID del aula
            publicar_evento: Si debe publicar evento MQTT
        
        Returns:
            Diccionario con mensaje de éxito
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_aula)
            
            # Liberar en MongoDB
            AulaModel.liberar(self.collection, obj_id)
            
            # Invalidar caché
            redis_client.client.delete(f"{self.CACHE_KEY_PREFIX}{id_aula}")
            redis_client.client.delete(self.CACHE_KEY_ALL)
            
            # Publicar evento MQTT (si se solicita)
            if publicar_evento:
                try:
                    # Aquí deberías tener los datos del cronograma para publicar correctamente
                    # Por ahora, se omite para evitar dependencias circulares
                    pass
                except Exception as e:
                    print(f"⚠️  Error al publicar evento MQTT: {e}")
            
            return {"mensaje": "Aula liberada correctamente"}
        
        except Exception as e:
            raise Exception(f"Error al liberar aula: {e}")
    
    def obtener_metricas(self) -> Dict[str, int]:
        """
        Obtiene métricas de estado de aulas
        
        Returns:
            Diccionario con total, disponibles, ocupadas, deshabilitadas
        """
        try:
            total = self.collection.count_documents({})
            disponibles = self.collection.count_documents({"estado": "disponible"})
            ocupadas = self.collection.count_documents({"estado": "ocupada"})
            deshabilitadas = self.collection.count_documents({"estado": "deshabilitada"})
            
            metricas = {
                "total_aulas": total,
                "disponibles": disponibles,
                "ocupadas": ocupadas,
                "deshabilitadas": deshabilitadas
            }
            
            # Publicar métricas a MQTT (opcional)
            try:
                MQTTEventPublisher.publicar_metricas_aulas(
                    total, disponibles, ocupadas, deshabilitadas
                )
            except Exception as e:
                print(f"⚠️  Error al publicar métricas MQTT: {e}")
            
            return metricas
        
        except Exception as e:
            print(f"Error al obtener métricas: {e}")
            return {
                "total_aulas": 0,
                "disponibles": 0,
                "ocupadas": 0,
                "deshabilitadas": 0
            }
