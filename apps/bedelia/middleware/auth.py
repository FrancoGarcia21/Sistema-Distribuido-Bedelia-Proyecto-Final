"""
Middleware de Autenticación JWT
Decoradores para proteger endpoints
"""

from functools import wraps
from flask import request, jsonify
from typing import List, Optional
from utils.jwt_helper import JWTHelper


def require_jwt(f):
    """
    Decorador que requiere un JWT válido en el header Authorization
    
    El payload del JWT se pasa a la función decorada como argumento 'jwt_payload'
    
    Usage:
        @app.route('/protected')
        @require_jwt
        def protected_endpoint(jwt_payload):
            return {"usuario": jwt_payload["usuario"]}
    
    Returns:
        401 si no hay token o es inválido
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener header Authorization
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({
                "error": "Token no proporcionado",
                "mensaje": "Debe incluir el header 'Authorization: Bearer <token>'"
            }), 401
        
        # Extraer token
        token = JWTHelper.extraer_token_header(auth_header)
        
        if not token:
            return jsonify({
                "error": "Formato de token inválido",
                "mensaje": "El header debe ser 'Authorization: Bearer <token>'"
            }), 401
        
        # Validar token
        payload = JWTHelper.validar_token(token)
        
        if not payload:
            return jsonify({
                "error": "Token inválido o expirado",
                "mensaje": "El token no es válido o ha expirado (15 minutos)"
            }), 401
        
        # Pasar payload a la función
        return f(*args, jwt_payload=payload, **kwargs)
    
    return decorated_function


def require_roles(roles_permitidos: List[str]):
    """
    Decorador que requiere un JWT válido con un rol específico
    
    Debe usarse DESPUÉS de @require_jwt
    
    Args:
        roles_permitidos: Lista de roles permitidos (ej: ["administrador", "profesor"])
    
    Usage:
        @app.route('/admin-only')
        @require_jwt
        @require_roles(["administrador"])
        def admin_endpoint(jwt_payload):
            return {"mensaje": "Solo administradores"}
    
    Returns:
        403 si el rol no está permitido
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener payload del JWT (debe haber sido validado por @require_jwt)
            jwt_payload = kwargs.get("jwt_payload")
            
            if not jwt_payload:
                return jsonify({
                    "error": "Middleware incorrecto",
                    "mensaje": "@require_roles debe usarse después de @require_jwt"
                }), 500
            
            # Verificar rol
            if not JWTHelper.verificar_rol(jwt_payload, roles_permitidos):
                return jsonify({
                    "error": "Acceso denegado",
                    "mensaje": f"Se requiere uno de estos roles: {', '.join(roles_permitidos)}",
                    "tu_rol": jwt_payload.get("rol")
                }), 403
            
            # Rol válido, continuar
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def optional_jwt(f):
    """
    Decorador que permite JWT opcional
    Si hay token válido, lo pasa; si no, pasa None
    
    Útil para endpoints públicos que pueden mostrar contenido diferente si hay sesión
    
    Usage:
        @app.route('/public-or-private')
        @optional_jwt
        def endpoint(jwt_payload):
            if jwt_payload:
                return {"mensaje": f"Hola {jwt_payload['usuario']}"}
            else:
                return {"mensaje": "Hola invitado"}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener header Authorization
        auth_header = request.headers.get("Authorization")
        
        payload = None
        
        if auth_header:
            # Extraer token
            token = JWTHelper.extraer_token_header(auth_header)
            
            if token:
                # Validar token
                payload = JWTHelper.validar_token(token)
        
        # Pasar payload (puede ser None)
        return f(*args, jwt_payload=payload, **kwargs)
    
    return decorated_function
