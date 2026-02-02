"""
CarreraService - Lógica de negocio para gestión de carreras y materias
Incluye: CRUD carreras/materias, asignaciones profesor-materia, inscripciones alumno-carrera
"""

import json
from typing import List, Dict, Any, Optional
from bson import ObjectId

from db.mongo import get_mongo_db
from db.redis import redis_client
from models.carrera_materia import CarreraMateriaModel
from models.asignacion import AsignacionModel
from utils.validators import Validators


class CarreraService:
    """
    Service para gestión de carreras, materias y asignaciones
    """
    
    CACHE_KEY_PREFIX_MATERIA = "materia:"
    CACHE_KEY_CARRERAS = "carreras:all"
    CACHE_TTL = 3600  # 1 hora
    
    def __init__(self):
        self.db = get_mongo_db()
        self.materias_collection = self.db.carrera_materias
        self.usuario_carrera_collection = self.db.usuario_carrera
        self.profesor_materia_collection = self.db.profesor_carrera_materia
    
    # ========== GESTIÓN DE MATERIAS ==========
    
    def crear_materia(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una materia nueva
        
        Args:
            data: Datos de la materia (carrera, materia, codigo_materia, anio, cuatrimestre, carga_horaria)
        
        Returns:
            Diccionario con id y mensaje de éxito
        
        Raises:
            ValueError: Si los datos son inválidos o ya existe
        """
        try:
            # Crear materia en MongoDB
            id_materia = CarreraMateriaModel.crear(self.materias_collection, data)
            
            # Invalidar caché de carreras
            redis_client.client.delete(self.CACHE_KEY_CARRERAS)
            
            return {
                "id": str(id_materia),
                "mensaje": "Materia creada correctamente"
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al crear materia: {e}")
    
    def obtener_materia(self, id_materia: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una materia por ID (con caché Redis)
        
        Args:
            id_materia: ID de la materia
        
        Returns:
            Diccionario con datos de la materia o None
        """
        try:
            # Intentar obtener de caché
            cache_key = f"{self.CACHE_KEY_PREFIX_MATERIA}{id_materia}"
            cached = redis_client.client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            # Consultar MongoDB
            obj_id = Validators.convertir_a_objectid(id_materia)
            materia = CarreraMateriaModel.obtener_por_id(self.materias_collection, obj_id)
            
            if materia:
                # Convertir ObjectId a string
                materia["_id"] = str(materia["_id"])
                
                # Guardar en caché
                redis_client.client.setex(
                    cache_key,
                    self.CACHE_TTL,
                    json.dumps(materia, default=str)
                )
            
            return materia
        
        except Exception as e:
            print(f"Error al obtener materia: {e}")
            return None
    
    def listar_materias_por_carrera(self, carrera: str, solo_activas: bool = True) -> List[Dict[str, Any]]:
        """
        Lista materias de una carrera
        
        Args:
            carrera: Nombre de la carrera
            solo_activas: Si True, solo devuelve materias activas
        
        Returns:
            Lista de materias
        """
        try:
            materias = CarreraMateriaModel.listar_por_carrera(
                self.materias_collection,
                carrera,
                solo_activas
            )
            
            # Convertir ObjectIds a strings
            for materia in materias:
                materia["_id"] = str(materia["_id"])
            
            return materias
        
        except Exception as e:
            print(f"Error al listar materias: {e}")
            return []
    
    def actualizar_materia(self, id_materia: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza una materia existente
        
        Args:
            id_materia: ID de la materia
            data: Datos a actualizar
        
        Returns:
            Diccionario con mensaje de éxito
        
        Raises:
            ValueError: Si la materia no existe o los datos son inválidos
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_materia)
            
            # Actualizar en MongoDB
            CarreraMateriaModel.actualizar(self.materias_collection, obj_id, data)
            
            # Invalidar caché
            redis_client.client.delete(f"{self.CACHE_KEY_PREFIX_MATERIA}{id_materia}")
            redis_client.client.delete(self.CACHE_KEY_CARRERAS)
            
            return {"mensaje": "Materia actualizada correctamente"}
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al actualizar materia: {e}")
    
    # ========== ASIGNACIONES PROFESOR-MATERIA ==========
    
    def asignar_profesor_materia(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asigna un profesor a una materia
        
        Args:
            data: Datos de la asignación (id_profesor, id_materia, carrera)
        
        Returns:
            Diccionario con id y mensaje de éxito
        
        Raises:
            ValueError: Si ya existe la asignación
        """
        try:
            id_asignacion = AsignacionModel.asignar_profesor_materia(
                self.profesor_materia_collection,
                data
            )
            
            return {
                "id": str(id_asignacion),
                "mensaje": "Profesor asignado a materia correctamente"
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al asignar profesor: {e}")
    
    def listar_materias_profesor(self, id_profesor: str, solo_activas: bool = True) -> List[Dict[str, Any]]:
        """
        Lista materias asignadas a un profesor
        
        Args:
            id_profesor: ID del profesor
            solo_activas: Si True, solo devuelve asignaciones activas
        
        Returns:
            Lista de asignaciones con datos de materias
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_profesor)
            
            asignaciones = AsignacionModel.obtener_materias_profesor(
                self.profesor_materia_collection,
                obj_id,
                solo_activas
            )
            
            # Enriquecer con datos de materias
            resultado = []
            for asig in asignaciones:
                materia = CarreraMateriaModel.obtener_por_id(
                    self.materias_collection,
                    asig["id_materia"]
                )
                
                if materia:
                    resultado.append({
                        "id_asignacion": str(asig["_id"]),
                        "id_materia": str(materia["_id"]),
                        "codigo_materia": materia["codigo_materia"],
                        "materia": materia["materia"],
                        "carrera": materia["carrera"],
                        "anio": materia["anio"],
                        "cuatrimestre": materia["cuatrimestre"],
                        "carga_horaria": materia["carga_horaria"],
                        "fecha_asignacion": str(asig["fecha_asignacion"])
                    })
            
            return resultado
        
        except Exception as e:
            print(f"Error al listar materias del profesor: {e}")
            return []
    
    def desasignar_profesor_materia(self, id_profesor: str, id_materia: str) -> Dict[str, Any]:
        """
        Desasigna un profesor de una materia
        
        Args:
            id_profesor: ID del profesor
            id_materia: ID de la materia
        
        Returns:
            Diccionario con mensaje de éxito
        """
        try:
            obj_id_profesor = Validators.convertir_a_objectid(id_profesor)
            obj_id_materia = Validators.convertir_a_objectid(id_materia)
            
            AsignacionModel.desactivar_asignacion(
                self.profesor_materia_collection,
                obj_id_profesor,
                obj_id_materia
            )
            
            return {"mensaje": "Profesor desasignado de la materia"}
        
        except Exception as e:
            raise Exception(f"Error al desasignar profesor: {e}")
    
    # ========== INSCRIPCIONES ALUMNO-CARRERA ==========
    
    def inscribir_alumno_carrera(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inscribe un alumno a una carrera
        
        Args:
            data: Datos de la inscripción (id_usuario, carrera, anio_ingreso)
        
        Returns:
            Diccionario con id y mensaje de éxito
        
        Raises:
            ValueError: Si ya está inscrito
        """
        try:
            id_inscripcion = AsignacionModel.inscribir_usuario_carrera(
                self.usuario_carrera_collection,
                data
            )
            
            return {
                "id": str(id_inscripcion),
                "mensaje": "Alumno inscrito a la carrera correctamente"
            }
        
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al inscribir alumno: {e}")
    
    def agregar_materia_suscrita(self, id_usuario: str, carrera: str, id_materia: str) -> Dict[str, Any]:
        """
        Agrega una materia a las suscritas del alumno (para MQTT)
        
        Args:
            id_usuario: ID del usuario (alumno)
            carrera: Nombre de la carrera
            id_materia: ID de la materia
        
        Returns:
            Diccionario con mensaje de éxito
        """
        try:
            obj_id_usuario = Validators.convertir_a_objectid(id_usuario)
            obj_id_materia = Validators.convertir_a_objectid(id_materia)
            
            resultado = AsignacionModel.agregar_materia_suscrita(
                self.usuario_carrera_collection,
                obj_id_usuario,
                carrera,
                obj_id_materia
            )
            
            if resultado:
                return {"mensaje": "Materia agregada a suscritas"}
            else:
                return {"mensaje": "La materia ya estaba suscrita"}
        
        except Exception as e:
            raise Exception(f"Error al agregar materia suscrita: {e}")
    
    def obtener_carreras_alumno(self, id_usuario: str) -> List[Dict[str, Any]]:
        """
        Obtiene las carreras en las que está inscrito un alumno
        
        Args:
            id_usuario: ID del usuario (alumno)
        
        Returns:
            Lista de inscripciones
        """
        try:
            obj_id = Validators.convertir_a_objectid(id_usuario)
            
            inscripciones = AsignacionModel.obtener_carreras_usuario(
                self.usuario_carrera_collection,
                obj_id
            )
            
            # Convertir ObjectIds a strings
            for insc in inscripciones:
                insc["_id"] = str(insc["_id"])
                insc["id_usuario"] = str(insc["id_usuario"])
                # Convertir lista de materias suscritas
                if "materias_suscritas" in insc:
                    insc["materias_suscritas"] = [str(m) for m in insc["materias_suscritas"]]
            
            return inscripciones
        
        except Exception as e:
            print(f"Error al obtener carreras del alumno: {e}")
            return []
