"""
Modelo: Asignaciones
Gestiona relaciones usuario-carrera y profesor-materia
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError


class AsignacionModel:
    """
    Modelo para gestionar asignaciones de usuarios a carreras y profesores a materias
    """
    
    # ========== USUARIO_CARRERA (Alumno-Carrera) ==========
    
    @staticmethod
    def validar_usuario_carrera(data: Dict[str, Any], es_actualizacion: bool = False) -> Dict[str, Any]:
        """
        Valida los datos de asignación usuario-carrera
        
        Args:
            data: Diccionario con los datos
            es_actualizacion: Si True, permite campos opcionales
            
        Returns:
            Diccionario validado
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        errores = []
        
        if not es_actualizacion:
            if "id_usuario" not in data:
                errores.append("Campo 'id_usuario' es obligatorio")
            elif not isinstance(data["id_usuario"], ObjectId):
                try:
                    data["id_usuario"] = ObjectId(data["id_usuario"])
                except:
                    errores.append("'id_usuario' debe ser un ObjectId válido")
            
            if "carrera" not in data or not data["carrera"].strip():
                errores.append("Campo 'carrera' es obligatorio")
            
            if "anio_ingreso" not in data:
                errores.append("Campo 'anio_ingreso' es obligatorio")
            elif not isinstance(data["anio_ingreso"], int) or data["anio_ingreso"] < 2000:
                errores.append("'anio_ingreso' debe ser un año válido")
        
        if errores:
            raise ValueError("; ".join(errores))
        
        documento = {}
        
        if not es_actualizacion:
            documento = {
                "id_usuario": data["id_usuario"],
                "carrera": data["carrera"].strip(),
                "anio_ingreso": data["anio_ingreso"],
                "estado": data.get("estado", "cursando"),
                "materias_suscritas": data.get("materias_suscritas", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        else:
            if "carrera" in data:
                documento["carrera"] = data["carrera"].strip()
            if "anio_ingreso" in data:
                documento["anio_ingreso"] = data["anio_ingreso"]
            if "estado" in data:
                documento["estado"] = data["estado"]
            if "materias_suscritas" in data:
                documento["materias_suscritas"] = data["materias_suscritas"]
            
            documento["updated_at"] = datetime.utcnow()
        
        return documento
    
    @staticmethod
    def crear_indices_usuario_carrera(coleccion):
        """
        Crea índices para la colección usuario_carrera
        
        Args:
            coleccion: Instancia de la colección MongoDB
        """
        # Índice único compuesto
        coleccion.create_index(
            [("id_usuario", 1), ("carrera", 1)],
            unique=True,
            name="idx_usuario_carrera_unique"
        )
        
        # Índice para búsquedas por usuario
        coleccion.create_index(
            [("id_usuario", 1)],
            name="idx_usuario"
        )
        
        # Índice para búsquedas por carrera y estado
        coleccion.create_index(
            [("carrera", 1), ("estado", 1)],
            name="idx_carrera_estado"
        )
    
    @staticmethod
    def inscribir_usuario_carrera(coleccion, data: Dict[str, Any]) -> ObjectId:
        """
        Inscribe un usuario (alumno) a una carrera
        
        Args:
            coleccion: Colección usuario_carrera
            data: Datos de la inscripción
            
        Returns:
            ObjectId del documento creado
            
        Raises:
            ValueError: Si los datos no son válidos o ya está inscrito
        """
        documento = AsignacionModel.validar_usuario_carrera(data, es_actualizacion=False)
        
        try:
            resultado = coleccion.insert_one(documento)
            return resultado.inserted_id
        except DuplicateKeyError:
            raise ValueError("El usuario ya está inscrito en esta carrera")
    
    @staticmethod
    def agregar_materia_suscrita(coleccion, id_usuario: ObjectId, carrera: str, id_materia: ObjectId) -> bool:
        """
        Agrega una materia a la lista de suscritas del alumno
        
        Args:
            coleccion: Colección usuario_carrera
            id_usuario: ObjectId del usuario
            carrera: Nombre de la carrera
            id_materia: ObjectId de la materia
            
        Returns:
            True si se agregó correctamente
        """
        resultado = coleccion.update_one(
            {
                "id_usuario": id_usuario,
                "carrera": carrera,
                "materias_suscritas": {"$ne": id_materia}  # Solo si no está ya
            },
            {
                "$addToSet": {"materias_suscritas": id_materia},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return resultado.modified_count > 0
    
    @staticmethod
    def quitar_materia_suscrita(coleccion, id_usuario: ObjectId, carrera: str, id_materia: ObjectId) -> bool:
        """
        Quita una materia de la lista de suscritas del alumno
        
        Args:
            coleccion: Colección usuario_carrera
            id_usuario: ObjectId del usuario
            carrera: Nombre de la carrera
            id_materia: ObjectId de la materia
            
        Returns:
            True si se quitó correctamente
        """
        resultado = coleccion.update_one(
            {
                "id_usuario": id_usuario,
                "carrera": carrera
            },
            {
                "$pull": {"materias_suscritas": id_materia},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return resultado.modified_count > 0
    
    @staticmethod
    def obtener_carreras_usuario(coleccion, id_usuario: ObjectId) -> List[Dict[str, Any]]:
        """
        Obtiene las carreras en las que está inscrito un usuario
        
        Args:
            coleccion: Colección usuario_carrera
            id_usuario: ObjectId del usuario
            
        Returns:
            Lista de inscripciones
        """
        return list(coleccion.find({"id_usuario": id_usuario}))
    
    # ========== PROFESOR_CARRERA_MATERIA ==========
    
    @staticmethod
    def validar_profesor_materia(data: Dict[str, Any], es_actualizacion: bool = False) -> Dict[str, Any]:
        """
        Valida los datos de asignación profesor-materia
        
        Args:
            data: Diccionario con los datos
            es_actualizacion: Si True, permite campos opcionales
            
        Returns:
            Diccionario validado
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        errores = []
        
        if not es_actualizacion:
            if "id_profesor" not in data:
                errores.append("Campo 'id_profesor' es obligatorio")
            elif not isinstance(data["id_profesor"], ObjectId):
                try:
                    data["id_profesor"] = ObjectId(data["id_profesor"])
                except:
                    errores.append("'id_profesor' debe ser un ObjectId válido")
            
            if "id_materia" not in data:
                errores.append("Campo 'id_materia' es obligatorio")
            elif not isinstance(data["id_materia"], ObjectId):
                try:
                    data["id_materia"] = ObjectId(data["id_materia"])
                except:
                    errores.append("'id_materia' debe ser un ObjectId válido")
            
            if "carrera" not in data or not data["carrera"].strip():
                errores.append("Campo 'carrera' es obligatorio")
        
        if errores:
            raise ValueError("; ".join(errores))
        
        documento = {}
        
        if not es_actualizacion:
            documento = {
                "id_profesor": data["id_profesor"],
                "id_materia": data["id_materia"],
                "carrera": data["carrera"].strip(),
                "fecha_asignacion": data.get("fecha_asignacion", date.today()),
                "activa": data.get("activa", True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        else:
            if "fecha_asignacion" in data:
                documento["fecha_asignacion"] = data["fecha_asignacion"]
            if "activa" in data:
                documento["activa"] = bool(data["activa"])
            
            documento["updated_at"] = datetime.utcnow()
        
        return documento
    
    @staticmethod
    def crear_indices_profesor_materia(coleccion):
        """
        Crea índices para la colección profesor_carrera_materia
        
        Args:
            coleccion: Instancia de la colección MongoDB
        """
        # Índice único compuesto
        coleccion.create_index(
            [("id_profesor", 1), ("id_materia", 1)],
            unique=True,
            name="idx_profesor_materia_unique"
        )
        
        # Índice para búsquedas por profesor
        coleccion.create_index(
            [("id_profesor", 1)],
            name="idx_profesor"
        )
        
        # Índice compuesto para Rules Engine (restricción multicarrera)
        coleccion.create_index(
            [("id_profesor", 1), ("carrera", 1), ("activa", 1)],
            name="idx_profesor_carrera_activa"
        )
    
    @staticmethod
    def asignar_profesor_materia(coleccion, data: Dict[str, Any]) -> ObjectId:
        """
        Asigna un profesor a una materia
        
        Args:
            coleccion: Colección profesor_carrera_materia
            data: Datos de la asignación
            
        Returns:
            ObjectId del documento creado
            
        Raises:
            ValueError: Si los datos no son válidos o ya está asignado
        """
        documento = AsignacionModel.validar_profesor_materia(data, es_actualizacion=False)
        
        try:
            resultado = coleccion.insert_one(documento)
            return resultado.inserted_id
        except DuplicateKeyError:
            raise ValueError("El profesor ya está asignado a esta materia")
    
    @staticmethod
    def obtener_materias_profesor(coleccion, id_profesor: ObjectId, solo_activas: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene las materias asignadas a un profesor
        
        Args:
            coleccion: Colección profesor_carrera_materia
            id_profesor: ObjectId del profesor
            solo_activas: Si True, solo devuelve asignaciones activas
            
        Returns:
            Lista de asignaciones
        """
        query = {"id_profesor": id_profesor}
        
        if solo_activas:
            query["activa"] = True
        
        return list(coleccion.find(query))
    
    @staticmethod
    def verificar_profesor_en_carrera(coleccion, id_profesor: ObjectId, carrera: str) -> bool:
        """
        Verifica si un profesor pertenece a una carrera (para Rules Engine)
        
        Args:
            coleccion: Colección profesor_carrera_materia
            id_profesor: ObjectId del profesor
            carrera: Nombre de la carrera
            
        Returns:
            True si el profesor tiene al menos una materia activa en la carrera
        """
        resultado = coleccion.find_one({
            "id_profesor": id_profesor,
            "carrera": carrera,
            "activa": True
        })
        
        return resultado is not None
    
    @staticmethod
    def desactivar_asignacion(coleccion, id_profesor: ObjectId, id_materia: ObjectId) -> bool:
        """
        Desactiva una asignación profesor-materia
        
        Args:
            coleccion: Colección profesor_carrera_materia
            id_profesor: ObjectId del profesor
            id_materia: ObjectId de la materia
            
        Returns:
            True si se desactivó correctamente
        """
        resultado = coleccion.update_one(
            {
                "id_profesor": id_profesor,
                "id_materia": id_materia
            },
            {
                "$set": {
                    "activa": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return resultado.modified_count > 0
