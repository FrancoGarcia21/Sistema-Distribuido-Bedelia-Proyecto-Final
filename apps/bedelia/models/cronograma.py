"""
Modelo: Cronograma
Gestiona asignaciones de aulas con horarios y validaciones del Rules Engine
"""

from datetime import datetime, date, time
from typing import Optional, Dict, Any, List
from bson import ObjectId


class CronogramaModel:
    """
    Modelo de Cronograma con validaciones para Rules Engine
    """
    
    TIPOS_VALIDOS = ["teorica", "practica", "laboratorio"]
    ESTADOS_VALIDOS = ["programada", "activa", "finalizada", "cancelada"]
    
    DURACION_MIN_MINUTOS = 45
    DURACION_MAX_MINUTOS = 240  # 4 horas
    
    @staticmethod
    def calcular_duracion(hora_inicio: str, hora_fin: str) -> int:
        """
        Calcula la duración en minutos entre dos horarios
        
        Args:
            hora_inicio: Formato "HH:MM"
            hora_fin: Formato "HH:MM"
            
        Returns:
            Duración en minutos
            
        Raises:
            ValueError: Si el formato es inválido
        """
        try:
            h_inicio = datetime.strptime(hora_inicio, "%H:%M")
            h_fin = datetime.strptime(hora_fin, "%H:%M")
            
            if h_fin <= h_inicio:
                raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
            
            delta = h_fin - h_inicio
            return int(delta.total_seconds() / 60)
        except ValueError as e:
            raise ValueError(f"Formato de hora inválido: {e}")
    
    @staticmethod
    def validar_horario_permitido(hora_inicio: str) -> bool:
        """
        Valida que la hora esté en el rango permitido (06:00 - 23:00)
        Requerido por Rules Engine
        
        Args:
            hora_inicio: Formato "HH:MM"
            
        Returns:
            True si está en horario permitido
        """
        try:
            h = datetime.strptime(hora_inicio, "%H:%M")
            hora = h.hour
            return 6 <= hora < 23
        except ValueError:
            return False
    
    @staticmethod
    def validar_datos(data: Dict[str, Any], es_actualizacion: bool = False) -> Dict[str, Any]:
        """
        Valida los datos de entrada para crear/actualizar un cronograma
        
        Args:
            data: Diccionario con los datos del cronograma
            es_actualizacion: Si True, permite campos opcionales
            
        Returns:
            Diccionario validado y sanitizado
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        errores = []
        
        # Validaciones obligatorias para creación
        if not es_actualizacion:
            if "id_aula" not in data:
                errores.append("Campo 'id_aula' es obligatorio")
            elif not isinstance(data["id_aula"], ObjectId):
                try:
                    data["id_aula"] = ObjectId(data["id_aula"])
                except:
                    errores.append("'id_aula' debe ser un ObjectId válido")
            
            if "id_materia" not in data:
                errores.append("Campo 'id_materia' es obligatorio")
            elif not isinstance(data["id_materia"], ObjectId):
                try:
                    data["id_materia"] = ObjectId(data["id_materia"])
                except:
                    errores.append("'id_materia' debe ser un ObjectId válido")
            
            if "id_profesor" not in data:
                errores.append("Campo 'id_profesor' es obligatorio")
            elif not isinstance(data["id_profesor"], ObjectId):
                try:
                    data["id_profesor"] = ObjectId(data["id_profesor"])
                except:
                    errores.append("'id_profesor' debe ser un ObjectId válido")
            
            if "id_carrera" not in data or not data["id_carrera"].strip():
                errores.append("Campo 'id_carrera' es obligatorio")
            
            if "fecha" not in data:
                errores.append("Campo 'fecha' es obligatorio")
            else:
                try:
                    if isinstance(data["fecha"], str):
                        data["fecha"] = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
                    elif not isinstance(data["fecha"], date):
                        errores.append("'fecha' debe estar en formato YYYY-MM-DD")
                except ValueError:
                    errores.append("'fecha' debe estar en formato YYYY-MM-DD")
            
            if "hora_inicio" not in data:
                errores.append("Campo 'hora_inicio' es obligatorio")
            elif not CronogramaModel.validar_horario_permitido(data["hora_inicio"]):
                errores.append("'hora_inicio' debe estar entre 06:00 y 23:00")
            
            if "hora_fin" not in data:
                errores.append("Campo 'hora_fin' es obligatorio")
            
            # Validación de duración
            if "hora_inicio" in data and "hora_fin" in data:
                try:
                    duracion = CronogramaModel.calcular_duracion(data["hora_inicio"], data["hora_fin"])
                    if duracion < CronogramaModel.DURACION_MIN_MINUTOS:
                        errores.append(f"La duración mínima es {CronogramaModel.DURACION_MIN_MINUTOS} minutos")
                    elif duracion > CronogramaModel.DURACION_MAX_MINUTOS:
                        errores.append(f"La duración máxima es {CronogramaModel.DURACION_MAX_MINUTOS} minutos")
                except ValueError as e:
                    errores.append(str(e))
            
            if "tipo" not in data:
                errores.append("Campo 'tipo' es obligatorio")
        
        # Validación de tipo (si está presente)
        if "tipo" in data:
            if data["tipo"] not in CronogramaModel.TIPOS_VALIDOS:
                errores.append(f"'tipo' debe ser uno de: {', '.join(CronogramaModel.TIPOS_VALIDOS)}")
        
        # Validación de estado (si está presente)
        if "estado" in data:
            if data["estado"] not in CronogramaModel.ESTADOS_VALIDOS:
                errores.append(f"'estado' debe ser uno de: {', '.join(CronogramaModel.ESTADOS_VALIDOS)}")
        
        if errores:
            raise ValueError("; ".join(errores))
        
        # Construir documento validado
        documento = {}
        
        if not es_actualizacion:
            duracion = CronogramaModel.calcular_duracion(data["hora_inicio"], data["hora_fin"])
            dia_semana = data["fecha"].weekday()  # 0=Lunes, 6=Domingo
            fecha_valor = data["fecha"]
            if isinstance(fecha_valor, date) and not isinstance(fecha_valor, datetime):
                fecha_valor = datetime.combine(fecha_valor, datetime.min.time())
            
            documento = {
                "id_aula": data["id_aula"],
                "id_materia": data["id_materia"],
                "id_profesor": data["id_profesor"],
                "id_carrera": data["id_carrera"].strip(),
                "fecha": fecha_valor,
                "hora_inicio": data["hora_inicio"],
                "hora_fin": data["hora_fin"],
                "duracion_minutos": duracion,
                "dia_semana": dia_semana,
                "tipo": data["tipo"],
                "estado": data.get("estado", "programada"),
                "cupo_actual": data.get("cupo_actual", 0),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "liberado_at": None
            }
        else:
            # Actualización parcial
            campos_permitidos = [
                "id_aula", "id_materia", "id_profesor", "id_carrera",
                "fecha", "hora_inicio", "hora_fin", "tipo", "estado", "cupo_actual"
            ]
            
            for campo in campos_permitidos:
                if campo in data:
                    documento[campo] = data[campo]
            
            # Recalcular duración si cambiaron los horarios
            if "hora_inicio" in data or "hora_fin" in data:
                # Necesitamos ambos para calcular
                if "hora_inicio" in data and "hora_fin" in data:
                    documento["duracion_minutos"] = CronogramaModel.calcular_duracion(
                        data["hora_inicio"],
                        data["hora_fin"]
                    )
            
            # Recalcular día de semana si cambió la fecha
            if "fecha" in data:
                documento["dia_semana"] = data["fecha"].weekday()
            
            documento["updated_at"] = datetime.utcnow()
        
        return documento
    
    @staticmethod
    def crear_indices(coleccion):
        """
        Crea los índices necesarios para la colección cronograma
        
        Args:
            coleccion: Instancia de la colección MongoDB
        """
        # Índice único compuesto para evitar doble reserva
        coleccion.create_index(
            [("id_aula", 1), ("fecha", 1), ("hora_inicio", 1)],
            unique=True,
            name="idx_aula_fecha_hora_unique"
        )
        
        # Índice para búsquedas por profesor
        coleccion.create_index(
            [("id_profesor", 1)],
            name="idx_profesor"
        )
        
        # Índice para búsquedas por fecha y estado
        coleccion.create_index(
            [("fecha", 1), ("estado", 1)],
            name="idx_fecha_estado"
        )
        
        # Índice para búsquedas por carrera (Rules Engine)
        coleccion.create_index(
            [("id_carrera", 1)],
            name="idx_carrera"
        )
        
        # Índice para búsquedas por materia
        coleccion.create_index(
            [("id_materia", 1)],
            name="idx_materia"
        )
        
        # Índice compuesto para consultas frecuentes del Rules Engine
        coleccion.create_index(
            [("id_carrera", 1), ("id_materia", 1), ("estado", 1)],
            name="idx_carrera_materia_estado"
        )
    
    @staticmethod
    def crear(coleccion, data: Dict[str, Any]) -> ObjectId:
        """
        Crea un cronograma en la base de datos
        
        Args:
            coleccion: Colección MongoDB
            data: Datos del cronograma
            
        Returns:
            ObjectId del documento creado
            
        Raises:
            ValueError: Si los datos no son válidos o hay conflicto de horario
        """
        from pymongo.errors import DuplicateKeyError
        
        documento = CronogramaModel.validar_datos(data, es_actualizacion=False)
        
        try:
            resultado = coleccion.insert_one(documento)
            return resultado.inserted_id
        except DuplicateKeyError:
            raise ValueError(
                f"Ya existe una asignación para el aula en esa fecha y hora"
            )
    
    @staticmethod
    def obtener_por_id(coleccion, id_cronograma: ObjectId) -> Optional[Dict[str, Any]]:
        """
        Obtiene un cronograma por su ID
        
        Args:
            coleccion: Colección MongoDB
            id_cronograma: ObjectId del cronograma
            
        Returns:
            Documento del cronograma o None si no existe
        """
        return coleccion.find_one({"_id": id_cronograma})
    
    @staticmethod
    def listar_por_aula(coleccion, id_aula: ObjectId, fecha_desde: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Lista cronogramas de un aula
        
        Args:
            coleccion: Colección MongoDB
            id_aula: ObjectId del aula
            fecha_desde: Fecha desde la cual buscar (opcional)
            
        Returns:
            Lista de cronogramas
        """
        query = {"id_aula": id_aula}
        
        if fecha_desde:
            query["fecha"] = {"$gte": fecha_desde}
        
        return list(coleccion.find(query).sort("fecha", 1))
    
    @staticmethod
    def listar_por_profesor(coleccion, id_profesor: ObjectId, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """
        Lista cronogramas de un profesor
        
        Args:
            coleccion: Colección MongoDB
            id_profesor: ObjectId del profesor
            solo_activos: Si True, solo devuelve los activos (programada o activa)
            
        Returns:
            Lista de cronogramas
        """
        query = {"id_profesor": id_profesor}
        
        if solo_activos:
            query["estado"] = {"$in": ["programada", "activa"]}
        
        return list(coleccion.find(query).sort("fecha", 1))
    
    @staticmethod
    def listar_por_carrera_materia(coleccion, id_carrera: str, id_materia: ObjectId) -> List[Dict[str, Any]]:
        """
        Lista cronogramas por carrera y materia (para alumnos)
        
        Args:
            coleccion: Colección MongoDB
            id_carrera: Nombre de la carrera
            id_materia: ObjectId de la materia
            
        Returns:
            Lista de cronogramas
        """
        return list(coleccion.find({
            "id_carrera": id_carrera,
            "id_materia": id_materia,
            "estado": {"$in": ["programada", "activa"]}
        }).sort("fecha", 1))
    
    @staticmethod
    def actualizar(coleccion, id_cronograma: ObjectId, data: Dict[str, Any]) -> bool:
        """
        Actualiza un cronograma existente
        
        Args:
            coleccion: Colección MongoDB
            id_cronograma: ObjectId del cronograma
            data: Datos a actualizar
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si los datos no son válidos o el cronograma no existe
        """
        documento = CronogramaModel.validar_datos(data, es_actualizacion=True)
        
        resultado = coleccion.update_one(
            {"_id": id_cronograma},
            {"$set": documento}
        )
        
        if resultado.matched_count == 0:
            raise ValueError(f"No se encontró el cronograma con ID {id_cronograma}")
        
        return resultado.modified_count > 0
    
    @staticmethod
    def cambiar_estado(coleccion, id_cronograma: ObjectId, nuevo_estado: str) -> bool:
        """
        Cambia el estado de un cronograma
        
        Args:
            coleccion: Colección MongoDB
            id_cronograma: ObjectId del cronograma
            nuevo_estado: Nuevo estado
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si el estado no es válido o el cronograma no existe
        """
        if nuevo_estado not in CronogramaModel.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(CronogramaModel.ESTADOS_VALIDOS)}")
        
        update_doc = {
            "estado": nuevo_estado,
            "updated_at": datetime.utcnow()
        }
        
        # Si se finaliza, registrar timestamp de liberación
        if nuevo_estado == "finalizada":
            update_doc["liberado_at"] = datetime.utcnow()
        
        resultado = coleccion.update_one(
            {"_id": id_cronograma},
            {"$set": update_doc}
        )
        
        if resultado.matched_count == 0:
            raise ValueError(f"No se encontró el cronograma con ID {id_cronograma}")
        
        return resultado.modified_count > 0
    
    @staticmethod
    def incrementar_cupo(coleccion, id_cronograma: ObjectId) -> bool:
        """
        Incrementa el cupo actual en 1 (cuando un alumno se suscribe)
        
        Args:
            coleccion: Colección MongoDB
            id_cronograma: ObjectId del cronograma
            
        Returns:
            True si se incrementó correctamente
        """
        resultado = coleccion.update_one(
            {"_id": id_cronograma},
            {
                "$inc": {"cupo_actual": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return resultado.modified_count > 0
    
    @staticmethod
    def decrementar_cupo(coleccion, id_cronograma: ObjectId) -> bool:
        """
        Decrementa el cupo actual en 1 (cuando un alumno se desuscribe)
        
        Args:
            coleccion: Colección MongoDB
            id_cronograma: ObjectId del cronograma
            
        Returns:
            True si se decrementó correctamente
        """
        resultado = coleccion.update_one(
            {"_id": id_cronograma, "cupo_actual": {"$gt": 0}},
            {
                "$inc": {"cupo_actual": -1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return resultado.modified_count > 0
