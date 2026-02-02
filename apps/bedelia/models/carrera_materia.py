"""
Modelo: Carrera y Materia
Gestiona la relación entre carreras y materias
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError


class CarreraMateriaModel:
    """
    Modelo de Carrera-Materia
    """
    
    @staticmethod
    def validar_datos(data: Dict[str, Any], es_actualizacion: bool = False) -> Dict[str, Any]:
        """
        Valida los datos de entrada para crear/actualizar una materia
        
        Args:
            data: Diccionario con los datos de la materia
            es_actualizacion: Si True, permite campos opcionales
            
        Returns:
            Diccionario validado y sanitizado
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        errores = []
        
        # Validaciones obligatorias para creación
        if not es_actualizacion:
            if "carrera" not in data or not data["carrera"].strip():
                errores.append("Campo 'carrera' es obligatorio")
            
            if "materia" not in data or not data["materia"].strip():
                errores.append("Campo 'materia' es obligatorio")
            
            if "codigo_materia" not in data or not data["codigo_materia"].strip():
                errores.append("Campo 'codigo_materia' es obligatorio")
            
            if "anio" not in data:
                errores.append("Campo 'anio' es obligatorio")
            elif not isinstance(data["anio"], int) or data["anio"] < 1 or data["anio"] > 5:
                errores.append("'anio' debe ser un entero entre 1 y 5")
            
            if "cuatrimestre" not in data:
                errores.append("Campo 'cuatrimestre' es obligatorio")
            elif data["cuatrimestre"] not in [1, 2]:
                errores.append("'cuatrimestre' debe ser 1 o 2")
            
            if "carga_horaria" not in data:
                errores.append("Campo 'carga_horaria' es obligatorio")
            elif not isinstance(data["carga_horaria"], int) or data["carga_horaria"] <= 0:
                errores.append("'carga_horaria' debe ser un entero positivo")
        
        # Validaciones para actualización
        if es_actualizacion:
            if "anio" in data:
                if not isinstance(data["anio"], int) or data["anio"] < 1 or data["anio"] > 5:
                    errores.append("'anio' debe ser un entero entre 1 y 5")
            
            if "cuatrimestre" in data:
                if data["cuatrimestre"] not in [1, 2]:
                    errores.append("'cuatrimestre' debe ser 1 o 2")
            
            if "carga_horaria" in data:
                if not isinstance(data["carga_horaria"], int) or data["carga_horaria"] <= 0:
                    errores.append("'carga_horaria' debe ser un entero positivo")
        
        if errores:
            raise ValueError("; ".join(errores))
        
        # Construir documento validado
        documento = {}
        
        if not es_actualizacion:
            documento = {
                "carrera": data["carrera"].strip(),
                "materia": data["materia"].strip(),
                "codigo_materia": data["codigo_materia"].strip().upper(),
                "anio": data["anio"],
                "cuatrimestre": data["cuatrimestre"],
                "carga_horaria": data["carga_horaria"],
                "activa": data.get("activa", True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        else:
            if "carrera" in data:
                documento["carrera"] = data["carrera"].strip()
            if "materia" in data:
                documento["materia"] = data["materia"].strip()
            if "codigo_materia" in data:
                documento["codigo_materia"] = data["codigo_materia"].strip().upper()
            if "anio" in data:
                documento["anio"] = data["anio"]
            if "cuatrimestre" in data:
                documento["cuatrimestre"] = data["cuatrimestre"]
            if "carga_horaria" in data:
                documento["carga_horaria"] = data["carga_horaria"]
            if "activa" in data:
                documento["activa"] = bool(data["activa"])
            
            documento["updated_at"] = datetime.utcnow()
        
        return documento
    
    @staticmethod
    def crear_indices(coleccion):
        """
        Crea los índices necesarios para la colección carrera_materias
        
        Args:
            coleccion: Instancia de la colección MongoDB
        """
        # Índice único para código de materia
        coleccion.create_index(
            [("codigo_materia", 1)],
            unique=True,
            name="idx_codigo_materia_unique"
        )
        
        # Índice compuesto para búsquedas por carrera
        coleccion.create_index(
            [("carrera", 1), ("activa", 1)],
            name="idx_carrera_activa"
        )
        
        # Índice compuesto para búsquedas por carrera, año y cuatrimestre
        coleccion.create_index(
            [("carrera", 1), ("anio", 1), ("cuatrimestre", 1)],
            name="idx_carrera_anio_cuatri"
        )
    
    @staticmethod
    def crear(coleccion, data: Dict[str, Any]) -> ObjectId:
        """
        Crea una materia en la base de datos
        
        Args:
            coleccion: Colección MongoDB
            data: Datos de la materia
            
        Returns:
            ObjectId del documento creado
            
        Raises:
            ValueError: Si los datos no son válidos
            DuplicateKeyError: Si ya existe el código de materia
        """
        documento = CarreraMateriaModel.validar_datos(data, es_actualizacion=False)
        
        try:
            resultado = coleccion.insert_one(documento)
            return resultado.inserted_id
        except DuplicateKeyError:
            raise ValueError(f"Ya existe una materia con código '{data['codigo_materia']}'")
    
    @staticmethod
    def obtener_por_id(coleccion, id_materia: ObjectId) -> Optional[Dict[str, Any]]:
        """
        Obtiene una materia por su ID
        
        Args:
            coleccion: Colección MongoDB
            id_materia: ObjectId de la materia
            
        Returns:
            Documento de la materia o None si no existe
        """
        return coleccion.find_one({"_id": id_materia})
    
    @staticmethod
    def obtener_por_codigo(coleccion, codigo_materia: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una materia por su código
        
        Args:
            coleccion: Colección MongoDB
            codigo_materia: Código de la materia
            
        Returns:
            Documento de la materia o None si no existe
        """
        return coleccion.find_one({"codigo_materia": codigo_materia.strip().upper()})
    
    @staticmethod
    def listar_por_carrera(coleccion, carrera: str, solo_activas: bool = True) -> List[Dict[str, Any]]:
        """
        Lista materias de una carrera
        
        Args:
            coleccion: Colección MongoDB
            carrera: Nombre de la carrera
            solo_activas: Si True, solo devuelve materias activas
            
        Returns:
            Lista de materias
        """
        query = {"carrera": carrera}
        
        if solo_activas:
            query["activa"] = True
        
        return list(coleccion.find(query).sort([("anio", 1), ("cuatrimestre", 1)]))
    
    @staticmethod
    def listar_por_anio_cuatrimestre(coleccion, carrera: str, anio: int, cuatrimestre: int) -> List[Dict[str, Any]]:
        """
        Lista materias de un año y cuatrimestre específico
        
        Args:
            coleccion: Colección MongoDB
            carrera: Nombre de la carrera
            anio: Año de la carrera
            cuatrimestre: Cuatrimestre (1 o 2)
            
        Returns:
            Lista de materias
        """
        return list(coleccion.find({
            "carrera": carrera,
            "anio": anio,
            "cuatrimestre": cuatrimestre,
            "activa": True
        }).sort("materia", 1))
    
    @staticmethod
    def actualizar(coleccion, id_materia: ObjectId, data: Dict[str, Any]) -> bool:
        """
        Actualiza una materia existente
        
        Args:
            coleccion: Colección MongoDB
            id_materia: ObjectId de la materia
            data: Datos a actualizar
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si los datos no son válidos o la materia no existe
        """
        documento = CarreraMateriaModel.validar_datos(data, es_actualizacion=True)
        
        resultado = coleccion.update_one(
            {"_id": id_materia},
            {"$set": documento}
        )
        
        if resultado.matched_count == 0:
            raise ValueError(f"No se encontró la materia con ID {id_materia}")
        
        return resultado.modified_count > 0
    
    @staticmethod
    def desactivar(coleccion, id_materia: ObjectId) -> bool:
        """
        Desactiva una materia (soft delete)
        
        Args:
            coleccion: Colección MongoDB
            id_materia: ObjectId de la materia
            
        Returns:
            True si se desactivó correctamente
        """
        resultado = coleccion.update_one(
            {"_id": id_materia},
            {
                "$set": {
                    "activa": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return resultado.modified_count > 0
