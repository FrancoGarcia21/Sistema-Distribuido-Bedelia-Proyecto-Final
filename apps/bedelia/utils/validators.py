"""
Validators - Validaciones comunes reutilizables
"""

from datetime import datetime, time
from typing import Any
from bson import ObjectId


class Validators:
    """
    Validaciones comunes para el sistema
    """
    
    @staticmethod
    def es_objectid_valido(valor: Any) -> bool:
        """
        Valida si un valor es un ObjectId válido
        
        Args:
            valor: Valor a validar
        
        Returns:
            True si es ObjectId válido, False si no
        """
        if isinstance(valor, ObjectId):
            return True
        
        try:
            ObjectId(valor)
            return True
        except:
            return False
    
    @staticmethod
    def convertir_a_objectid(valor: Any) -> ObjectId:
        """
        Convierte un valor a ObjectId
        
        Args:
            valor: Valor a convertir (string o ObjectId)
        
        Returns:
            ObjectId
        
        Raises:
            ValueError: Si el valor no es un ObjectId válido
        """
        if isinstance(valor, ObjectId):
            return valor
        
        try:
            return ObjectId(valor)
        except Exception as e:
            raise ValueError(f"ID inválido: {valor}")
    
    @staticmethod
    def validar_formato_hora(hora: str) -> bool:
        """
        Valida que una hora tenga el formato HH:MM
        
        Args:
            hora: String con la hora (ej: "14:30")
        
        Returns:
            True si el formato es válido, False si no
        """
        try:
            datetime.strptime(hora, "%H:%M")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_horario_permitido(hora: str) -> bool:
        """
        Valida que una hora esté en el rango permitido (06:00 - 23:00)
        Según Rules Engine del prompt MAESTRO
        
        Args:
            hora: String con la hora (ej: "14:30")
        
        Returns:
            True si está en el rango permitido, False si no
        """
        try:
            h = datetime.strptime(hora, "%H:%M")
            hora_num = h.hour
            return 6 <= hora_num < 23
        except ValueError:
            return False
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """
        Validación básica de email
        
        Args:
            email: String con el email
        
        Returns:
            True si el formato es válido, False si no
        """
        if not email or "@" not in email:
            return False
        
        partes = email.split("@")
        if len(partes) != 2:
            return False
        
        if not partes[0] or not partes[1]:
            return False
        
        if "." not in partes[1]:
            return False
        
        return True
    
    @staticmethod
    def validar_duracion(hora_inicio: str, hora_fin: str, min_minutos: int = 45, max_minutos: int = 240) -> tuple:
        """
        Valida que la duración entre dos horarios esté en el rango permitido
        
        Args:
            hora_inicio: Hora de inicio (formato HH:MM)
            hora_fin: Hora de fin (formato HH:MM)
            min_minutos: Duración mínima en minutos (default 45)
            max_minutos: Duración máxima en minutos (default 240 = 4 horas)
        
        Returns:
            Tuple (es_valido: bool, duracion_minutos: int, mensaje_error: str)
        
        Example:
            valido, duracion, error = Validators.validar_duracion("14:00", "16:00")
            if not valido:
                print(error)
        """
        try:
            h_inicio = datetime.strptime(hora_inicio, "%H:%M")
            h_fin = datetime.strptime(hora_fin, "%H:%M")
            
            if h_fin <= h_inicio:
                return (False, 0, "La hora de fin debe ser posterior a la hora de inicio")
            
            delta = h_fin - h_inicio
            duracion = int(delta.total_seconds() / 60)
            
            if duracion < min_minutos:
                return (False, duracion, f"La duración mínima es {min_minutos} minutos")
            
            if duracion > max_minutos:
                return (False, duracion, f"La duración máxima es {max_minutos} minutos")
            
            return (True, duracion, "")
        
        except ValueError as e:
            return (False, 0, f"Formato de hora inválido: {e}")
    
    @staticmethod
    def sanitizar_string(valor: str) -> str:
        """
        Sanitiza un string (trim y lowercase si aplica)
        
        Args:
            valor: String a sanitizar
        
        Returns:
            String sanitizado
        """
        if not valor:
            return ""
        
        return valor.strip()
    
    @staticmethod
    def validar_estado_aula(estado: str) -> bool:
        """
        Valida que el estado de un aula sea válido
        
        Args:
            estado: Estado a validar
        
        Returns:
            True si es válido, False si no
        """
        estados_validos = ["disponible", "ocupada", "deshabilitada"]
        return estado in estados_validos
    
    @staticmethod
    def validar_rol_usuario(rol: str) -> bool:
        """
        Valida que el rol de un usuario sea válido
        
        Args:
            rol: Rol a validar
        
        Returns:
            True si es válido, False si no
        """
        roles_validos = ["administrador", "profesor", "alumno"]
        return rol in roles_validos
