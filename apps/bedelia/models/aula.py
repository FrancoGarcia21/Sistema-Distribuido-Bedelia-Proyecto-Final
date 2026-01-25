"""
Modelo: Aula
Gestiona la validación y operaciones sobre la colección 'aulas'
"""

from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError


class AulaModel:
    """
    Modelo de Aula con validaciones y helpers
    """
    
    ESTADOS_VALIDOS = ["disponible", "ocupada", "deshabilitada"]
    
    @staticmethod
    def validar_datos(data: Dict[str, Any], es_actualizacion: bool = False) -> Dict[str, Any]:
        """
        Valida los datos de entrada para crear/actualizar un aula
        
        Args:
            data: Diccionario con los datos del aula
            es_actualizacion: Si True, permite campos opcionales
            
        Returns:
            Diccionario validado y sanitizado
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        errores = []
        
        # Validaciones obligatorias para creación
        if not es_actualizacion:
            if "nro_aula" not in data:
                errores.append("Campo 'nro_aula' es obligatorio")
            elif not isinstance(data["nro_aula"], int) or data["nro_aula"] <= 0:
                errores.append("'nro_aula' debe ser un entero positivo")
            
            if "piso" not in data:
                errores.append("Campo 'piso' es obligatorio")
            elif not isinstance(data["piso"], int):
                errores.append("'piso' debe ser un entero")
            
            if "cupo" not in data:
                errores.append("Campo 'cupo' es obligatorio")
            elif not isinstance(data["cupo"], int) or data["cupo"] <= 0:
                errores.append("'cupo' debe ser un entero positivo")
            
            if "estado" not in data:
                errores.append("Campo 'estado' es obligatorio")
        
        # Validación de estado (si está presente)
        if "estado" in data:
            if data["estado"] not in AulaModel.ESTADOS_VALIDOS:
                errores.append(f"'estado' debe ser uno de: {', '.join(AulaModel.ESTADOS_VALIDOS)}")
        
        # Validación de cupo (si está presente en actualización)
        if es_actualizacion and "cupo" in data:
            if not isinstance(data["cupo"], int) or data["cupo"] <= 0:
                errores.append("'cupo' debe ser un entero positivo")
        
        if errores:
            raise ValueError("; ".join(errores))
        
        # Construir documento validado
        documento = {}
        
        if not es_actualizacion:
            documento = {
                "nro_aula": data["nro_aula"],
                "piso": data["piso"],
                "cupo": data["cupo"],
                "estado": data["estado"],
                "descripcion": data.get("descripcion", ""),
                "id_asignacion_actual": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        else:
            # Solo incluir campos presentes en actualización
            if "nro_aula" in data:
                documento["nro_aula"] = data["nro_aula"]
            if "piso" in data:
                documento["piso"] = data["piso"]
            if "cupo" in data:
                documento["cupo"] = data["cupo"]
            if "estado" in data:
                documento["estado"] = data["estado"]
            if "descripcion" in data:
                documento["descripcion"] = data["descripcion"]
            if "id_asignacion_actual" in data:
                documento["id_asignacion_actual"] = data["id_asignacion_actual"]
            
            documento["updated_at"] = datetime.utcnow()
        
        return documento
    
    @staticmethod
    def crear_indices(coleccion):
        """
        Crea los índices necesarios para la colección aulas
        
        Args:
            coleccion: Instancia de la colección MongoDB
        """
        # Índice único compuesto (nro_aula, piso)
        coleccion.create_index(
            [("nro_aula", 1), ("piso", 1)],
            unique=True,
            name="idx_aula_unique"
        )
        
        # Índice para búsquedas por estado
        coleccion.create_index(
            [("estado", 1)],
            name="idx_estado"
        )
        
        # Índice para asignaciones actuales
        coleccion.create_index(
            [("id_asignacion_actual", 1)],
            sparse=True,
            name="idx_asignacion_actual"
        )
    
    @staticmethod
    def crear(coleccion, data: Dict[str, Any]) -> ObjectId:
        """
        Crea un aula en la base de datos
        
        Args:
            coleccion: Colección MongoDB
            data: Datos del aula
            
        Returns:
            ObjectId del documento creado
            
        Raises:
            ValueError: Si los datos no son válidos
            DuplicateKeyError: Si ya existe un aula con ese nro_aula y piso
        """
        documento = AulaModel.validar_datos(data, es_actualizacion=False)
        
        try:
            resultado = coleccion.insert_one(documento)
            return resultado.inserted_id
        except DuplicateKeyError:
            raise ValueError(f"Ya existe un aula con número {data['nro_aula']} en el piso {data['piso']}")
    
    @staticmethod
    def actualizar(coleccion, id_aula: ObjectId, data: Dict[str, Any]) -> bool:
        """
        Actualiza un aula existente
        
        Args:
            coleccion: Colección MongoDB
            id_aula: ObjectId del aula
            data: Datos a actualizar
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si los datos no son válidos o el aula no existe
        """
        documento = AulaModel.validar_datos(data, es_actualizacion=True)
        
        resultado = coleccion.update_one(
            {"_id": id_aula},
            {"$set": documento}
        )
        
        if resultado.matched_count == 0:
            raise ValueError(f"No se encontró el aula con ID {id_aula}")
        
        return resultado.modified_count > 0
    
    @staticmethod
    def obtener_por_id(coleccion, id_aula: ObjectId) -> Optional[Dict[str, Any]]:
        """
        Obtiene un aula por su ID
        
        Args:
            coleccion: Colección MongoDB
            id_aula: ObjectId del aula
            
        Returns:
            Documento del aula o None si no existe
        """
        return coleccion.find_one({"_id": id_aula})
    
    @staticmethod
    def obtener_por_numero_piso(coleccion, nro_aula: int, piso: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un aula por número y piso
        
        Args:
            coleccion: Colección MongoDB
            nro_aula: Número de aula
            piso: Piso
            
        Returns:
            Documento del aula o None si no existe
        """
        return coleccion.find_one({"nro_aula": nro_aula, "piso": piso})
    
    @staticmethod
    def listar(coleccion, filtros: Optional[Dict[str, Any]] = None) -> list:
        """
        Lista aulas con filtros opcionales
        
        Args:
            coleccion: Colección MongoDB
            filtros: Diccionario de filtros (ej: {"estado": "disponible"})
            
        Returns:
            Lista de aulas
        """
        query = filtros if filtros else {}
        return list(coleccion.find(query).sort("nro_aula", 1))
    
    @staticmethod
    def cambiar_estado(coleccion, id_aula: ObjectId, nuevo_estado: str) -> bool:
        """
        Cambia el estado de un aula
        
        Args:
            coleccion: Colección MongoDB
            id_aula: ObjectId del aula
            nuevo_estado: Nuevo estado ("disponible" | "ocupada" | "deshabilitada")
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si el estado no es válido o el aula no existe
        """
        if nuevo_estado not in AulaModel.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(AulaModel.ESTADOS_VALIDOS)}")
        
        resultado = coleccion.update_one(
            {"_id": id_aula},
            {
                "$set": {
                    "estado": nuevo_estado,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if resultado.matched_count == 0:
            raise ValueError(f"No se encontró el aula con ID {id_aula}")
        
        return resultado.modified_count > 0
    
    @staticmethod
    def asignar(coleccion, id_aula: ObjectId, id_cronograma: ObjectId) -> bool:
        """
        Marca un aula como ocupada y registra la asignación actual
        
        Args:
            coleccion: Colección MongoDB
            id_aula: ObjectId del aula
            id_cronograma: ObjectId del cronograma asignado
            
        Returns:
            True si se actualizó correctamente
        """
        resultado = coleccion.update_one(
            {"_id": id_aula, "estado": "disponible"},
            {
                "$set": {
                    "estado": "ocupada",
                    "id_asignacion_actual": id_cronograma,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return resultado.modified_count > 0
    
    @staticmethod
    def liberar(coleccion, id_aula: ObjectId) -> bool:
        """
        Libera un aula (disponible, sin asignación)
        
        Args:
            coleccion: Colección MongoDB
            id_aula: ObjectId del aula
            
        Returns:
            True si se actualizó correctamente
        """
        resultado = coleccion.update_one(
            {"_id": id_aula},
            {
                "$set": {
                    "estado": "disponible",
                    "id_asignacion_actual": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return resultado.modified_count > 0
