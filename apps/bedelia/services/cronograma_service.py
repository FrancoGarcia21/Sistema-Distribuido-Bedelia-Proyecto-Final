"""
CronogramaService - Lógica de negocio para gestión de cronogramas
Incluye: CRUD, validaciones de horario/cupo/profesor, eventos MQTT
"""

from typing import List, Dict, Any, Optional
from bson import ObjectId
from datetime import date, datetime

from db.mongo import get_mongo_db
from models.cronograma import CronogramaModel
from models.aula import AulaModel
from models.asignacion import AsignacionModel
from utils.validators import Validators
from utils.mqtt_events import MQTTEventPublisher


class CronogramaService:
    """
    Service para gestión de cronogramas con validaciones del Rules Engine
    """
    
    def __init__(self):
        self.db = get_mongo_db()
        self.collection = self.db.cronograma
        self.aulas_collection = self.db.aulas
        self.profesor_materia_collection = self.db.profesor_carrera_materia
    
    def crear_cronograma(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un cronograma (asignación de aula) con validaciones
        
        Validaciones implementadas:
        - Horario permitido (06:00 - 23:00)
        - Duración (45min - 4h)
        - Profesor pertenece a la carrera
        - Aula disponible
        - No hay conflicto de horario
        
        Args:
            data: Datos del cronograma
        
        Returns:
            Diccionario con id y mensaje de éxito
        
        Raises:
            ValueError: Si las validaciones fallan
        """
        try:
            # Validación 1: Horario permitido (Rules Engine)
            if not Validators.validar_horario_permitido(data.get("hora_inicio", "")):
                raise ValueError("Horario no permitido. Solo se permiten asignaciones entre 06:00 y 23:00")
            
            # Validación 2: Duración (Rules Engine)
            valido, duracion, error = Validators.validar_duracion(
                data.get("hora_inicio", ""),
                data.get("hora_fin", "")
            )
            if not valido:
                raise ValueError(error)
            
            # Validación 3: Profesor pertenece a la carrera (Rules Engine)
            id_profesor = Validators.convertir_a_objectid(data.get("id_profesor"))
            carrera = data.get("id_carrera")
            
            pertenece = AsignacionModel.verificar_profesor_en_carrera(
                self.profesor_materia_collection,
                id_profesor,
                carrera
            )
            
            if not pertenece:
                raise ValueError(f"El profesor no está asignado a la carrera '{carrera}'")
            
            # Validación 4: Aula disponible y no deshabilitada (Rules Engine)
            id_aula = Validators.convertir_a_objectid(data.get("id_aula"))
            aula = AulaModel.obtener_por_id(self.aulas_collection, id_aula)
            
            if not aula:
                raise ValueError("Aula no encontrada")
            
            if aula["estado"] == "deshabilitada":
                raise ValueError("El aula está deshabilitada y no puede ser asignada")
            
            if aula["estado"] == "ocupada":
                raise ValueError("El aula está ocupada actualmente")
            
            # Crear cronograma en MongoDB
            id_cronograma = CronogramaModel.crear(self.collection, data)
            
            # Marcar aula como ocupada
            AulaModel.asignar(self.aulas_collection, id_aula, id_cronograma)
            
            # Publicar evento MQTT (aula asignada)
            try:
                cronograma = CronogramaModel.obtener_por_id(self.collection, id_cronograma)
                
                MQTTEventPublisher.publicar_aula_asignada(
                    str(id_aula),
                    data.get("id_carrera"),
                    str(data.get("id_materia")),
                    {
                        "id_cronograma": str(id_cronograma),
                        "id_profesor": str(id_profesor),
                        "fecha": str(cronograma["fecha"]),
                        "hora_inicio": cronograma["hora_inicio"],
                        "hora_fin": cronograma["hora_fin"],
                        "tipo": cronograma["tipo"]
                    }
                )
            except Exception as e:
                print(f"⚠️  Error al publicar evento MQTT: {e}")
            
            return {
                "id": str(id_cronograma),
                "mensaje": "Cronograma creado correctamente"
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al crear cronograma: {e}")
    
    def obtener_cronograma(self, id_cronograma: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un cronograma por ID
        
        Args:
            id_cronograma: ID del cronograma
        
        Returns:
            Diccionario con datos del cronograma o None
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_cronograma)
            cronograma = CronogramaModel.obtener_por_id(self.collection, obj_id)
            
            if cronograma:
                # Convertir ObjectIds a strings
                cronograma["_id"] = str(cronograma["_id"])
                cronograma["id_aula"] = str(cronograma["id_aula"])
                cronograma["id_materia"] = str(cronograma["id_materia"])
                cronograma["id_profesor"] = str(cronograma["id_profesor"])
            
            return cronograma
        
        except Exception as e:
            print(f"Error al obtener cronograma: {e}")
            return None
    
    def listar_por_aula(self, id_aula: str, fecha_desde: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Lista cronogramas de un aula
        
        Args:
            id_aula: ID del aula
            fecha_desde: Fecha desde la cual buscar (opcional)
        
        Returns:
            Lista de cronogramas
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_aula)
            cronogramas = CronogramaModel.listar_por_aula(self.collection, obj_id, fecha_desde)
            
            # Convertir ObjectIds a strings
            for crono in cronogramas:
                crono["_id"] = str(crono["_id"])
                crono["id_aula"] = str(crono["id_aula"])
                crono["id_materia"] = str(crono["id_materia"])
                crono["id_profesor"] = str(crono["id_profesor"])
            
            return cronogramas
        
        except Exception as e:
            print(f"Error al listar cronogramas por aula: {e}")
            return []
    
    def listar_por_profesor(self, id_profesor: str, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """
        Lista cronogramas de un profesor
        
        Args:
            id_profesor: ID del profesor
            solo_activos: Si True, solo devuelve cronogramas activos
        
        Returns:
            Lista de cronogramas
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_profesor)
            cronogramas = CronogramaModel.listar_por_profesor(self.collection, obj_id, solo_activos)
            
            # Convertir ObjectIds a strings
            for crono in cronogramas:
                crono["_id"] = str(crono["_id"])
                crono["id_aula"] = str(crono["id_aula"])
                crono["id_materia"] = str(crono["id_materia"])
                crono["id_profesor"] = str(crono["id_profesor"])
            
            return cronogramas
        
        except Exception as e:
            print(f"Error al listar cronogramas por profesor: {e}")
            return []
    
    def listar_por_carrera_materia(self, id_carrera: str, id_materia: str) -> List[Dict[str, Any]]:
        """
        Lista cronogramas por carrera y materia (para alumnos)
        
        Args:
            id_carrera: Nombre de la carrera
            id_materia: ID de la materia
        
        Returns:
            Lista de cronogramas
        """
        try:
            obj_id_materia = Validators.convertir_a_objectid(id_materia)
            cronogramas = CronogramaModel.listar_por_carrera_materia(
                self.collection,
                id_carrera,
                obj_id_materia
            )
            
            # Convertir ObjectIds a strings
            for crono in cronogramas:
                crono["_id"] = str(crono["_id"])
                crono["id_aula"] = str(crono["id_aula"])
                crono["id_materia"] = str(crono["id_materia"])
                crono["id_profesor"] = str(crono["id_profesor"])
            
            return cronogramas
        
        except Exception as e:
            print(f"Error al listar cronogramas por carrera/materia: {e}")
            return []
    
    def finalizar_cronograma(self, id_cronograma: str) -> Dict[str, Any]:
        """
        Finaliza un cronograma y libera el aula
        
        Args:
            id_cronograma: ID del cronograma
        
        Returns:
            Diccionario con mensaje de éxito
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_cronograma)
            
            # Obtener cronograma
            cronograma = CronogramaModel.obtener_por_id(self.collection, obj_id)
            
            if not cronograma:
                raise ValueError("Cronograma no encontrado")
            
            # Cambiar estado a finalizada
            CronogramaModel.cambiar_estado(self.collection, obj_id, "finalizada")
            
            # Liberar aula
            AulaModel.liberar(self.aulas_collection, cronograma["id_aula"])
            
            # Publicar evento MQTT (aula liberada)
            try:
                MQTTEventPublisher.publicar_aula_liberada(
                    str(cronograma["id_aula"]),
                    cronograma["id_carrera"],
                    str(cronograma["id_materia"]),
                    str(id_cronograma)
                )
            except Exception as e:
                print(f"⚠️  Error al publicar evento MQTT: {e}")
            
            return {"mensaje": "Cronograma finalizado y aula liberada"}
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al finalizar cronograma: {e}")
    
    def cancelar_cronograma(self, id_cronograma: str, motivo: str = "") -> Dict[str, Any]:
        """
        Cancela un cronograma y libera el aula
        
        Args:
            id_cronograma: ID del cronograma
            motivo: Motivo de la cancelación (opcional)
        
        Returns:
            Diccionario con mensaje de éxito
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_cronograma)
            
            # Obtener cronograma
            cronograma = CronogramaModel.obtener_por_id(self.collection, obj_id)
            
            if not cronograma:
                raise ValueError("Cronograma no encontrado")
            
            # Cambiar estado a cancelada
            CronogramaModel.cambiar_estado(self.collection, obj_id, "cancelada")
            
            # Liberar aula
            AulaModel.liberar(self.aulas_collection, cronograma["id_aula"])
            
            # Notificar a alumnos suscritos
            try:
                mensaje = f"La clase ha sido cancelada"
                if motivo:
                    mensaje += f". Motivo: {motivo}"
                
                MQTTEventPublisher.publicar_notificacion_aula(
                    cronograma["id_carrera"],
                    str(cronograma["id_materia"]),
                    mensaje,
                    "warning"
                )
            except Exception as e:
                print(f"⚠️  Error al publicar notificación MQTT: {e}")
            
            return {"mensaje": "Cronograma cancelado y aula liberada"}
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al cancelar cronograma: {e}")
    
    def validar_cupo(self, id_cronograma: str) -> Dict[str, Any]:
        """
        Valida si hay cupo disponible en un cronograma
        
        Args:
            id_cronograma: ID del cronograma
        
        Returns:
            Diccionario con información de cupo
        
        Raises:
            ValueError: Si no hay cupo disponible
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_cronograma)
            
            # Obtener cronograma
            cronograma = CronogramaModel.obtener_por_id(self.collection, obj_id)
            
            if not cronograma:
                raise ValueError("Cronograma no encontrado")
            
            # Obtener aula
            aula = AulaModel.obtener_por_id(self.aulas_collection, cronograma["id_aula"])
            
            if not aula:
                raise ValueError("Aula no encontrada")
            
            cupo_disponible = aula["cupo"] - cronograma["cupo_actual"]
            
            return {
                "cupo_total": aula["cupo"],
                "cupo_actual": cronograma["cupo_actual"],
                "cupo_disponible": cupo_disponible,
                "hay_cupo": cupo_disponible > 0
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al validar cupo: {e}")
