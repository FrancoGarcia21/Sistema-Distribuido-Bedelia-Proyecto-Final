"""
JWT Helper - Generación y validación de tokens JWT
Algoritmo: HS256
Expiración: 15 minutos 
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from config import SECRET_KEY


class JWTHelper:
    """
    Helper para manejo de JWT con HS256
    """
    
    ALGORITHM = "HS256"
    EXPIRATION_MINUTES = 15  # Según prompt MAESTRO
    
    @staticmethod
    def generar_token(usuario_data: Dict[str, Any]) -> str:
        """
        Genera un token JWT
        
        Args:
            usuario_data: Diccionario con datos del usuario
                Debe contener: usuario, rol, _id
        
        Returns:
            Token JWT como string
        
        Example:
            token = JWTHelper.generar_token({
                "usuario": "juan.perez",
                "rol": "profesor",
                "_id": "507f1f77bcf86cd799439011"
            })
        """
        # Payload del token
        payload = {
            "usuario": usuario_data.get("usuario"),
            "rol": usuario_data.get("rol"),
            "id_usuario": str(usuario_data.get("_id")),
            "nombre": usuario_data.get("nombre"),
            "iat": datetime.utcnow(),  # Issued at
            "exp": datetime.utcnow() + timedelta(minutes=JWTHelper.EXPIRATION_MINUTES)
        }
        
        # Generar token
        token = jwt.encode(payload, SECRET_KEY, algorithm=JWTHelper.ALGORITHM)
        
        return token
    
    @staticmethod
    def validar_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Valida un token JWT y devuelve el payload
        
        Args:
            token: Token JWT como string
        
        Returns:
            Payload del token si es válido, None si no lo es
        
        Example:
            payload = JWTHelper.validar_token(token)
            if payload:
                print(f"Usuario: {payload['usuario']}, Rol: {payload['rol']}")
        """
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[JWTHelper.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            return None
    
    @staticmethod
    def extraer_token_header(authorization_header: Optional[str]) -> Optional[str]:
        """
        Extrae el token del header Authorization
        
        Args:
            authorization_header: Header Authorization (ej: "Bearer eyJ...")
        
        Returns:
            Token sin el prefijo "Bearer ", o None si no es válido
        
        Example:
            token = JWTHelper.extraer_token_header(request.headers.get("Authorization"))
        """
        if not authorization_header:
            return None
        
        # Formato esperado: "Bearer <token>"
        parts = authorization_header.split()
        
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        return parts[1]
    
    @staticmethod
    def verificar_rol(payload: Dict[str, Any], roles_permitidos: list) -> bool:
        """
        Verifica si el rol del usuario está en la lista de roles permitidos
        
        Args:
            payload: Payload del token JWT
            roles_permitidos: Lista de roles permitidos (ej: ["administrador", "profesor"])
        
        Returns:
            True si el rol está permitido, False si no
        
        Example:
            if JWTHelper.verificar_rol(payload, ["administrador"]):
                # Usuario es administrador
        """
        rol_usuario = payload.get("rol")
        return rol_usuario in roles_permitidos
