"""
Routes: Usuarios
Endpoints para gestión de usuarios y autenticación
"""

from flask import request, jsonify
from middleware.auth import require_jwt, require_roles
from services.usuario_service import UsuarioService
from . import usuarios_bp

# Instanciar service
usuario_service = UsuarioService()


@usuarios_bp.route('/login', methods=['POST'])
def login():
    """
    POST /usuarios/login
    Autentica un usuario y devuelve JWT
    
    No requiere JWT
    
    Body:
    {
        "usuario": "admin_test",
        "password": "admin123"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validar campos requeridos
        if 'usuario' not in data or 'password' not in data:
            return jsonify({
                "error": "Campos 'usuario' y 'password' son requeridos"
            }), 400
        
        resultado = usuario_service.autenticar(data['usuario'], data['password'])
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@usuarios_bp.route('/', methods=['POST'])
@require_jwt
@require_roles(["administrador"])
def crear_usuario(jwt_payload):
    """
    POST /usuarios
    Crea un usuario nuevo
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "usuario": "juan.perez",
        "nombre": "Juan Pérez",
        "email": "juan.perez@example.com",
        "password": "password123",
        "rol": "profesor"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validar campos requeridos
        campos_requeridos = ["usuario", "nombre", "email", "password", "rol"]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "error": f"Campo '{campo}' es requerido"
                }), 400
        
        resultado = usuario_service.crear_usuario(data)
        
        return jsonify(resultado), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@usuarios_bp.route('/<id_usuario>', methods=['GET'])
@require_jwt
def obtener_usuario(jwt_payload, id_usuario):
    """
    GET /usuarios/{id_usuario}
    Obtiene un usuario por ID
    
    Requiere: JWT válido
    """
    try:
        usuario = usuario_service.obtener_usuario(id_usuario)
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify(usuario), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@usuarios_bp.route('/rol/<rol>', methods=['GET'])
@require_jwt
@require_roles(["administrador"])
def listar_por_rol(jwt_payload, rol):
    """
    GET /usuarios/rol/{rol}?activos=true
    Lista usuarios por rol
    
    Requiere: JWT con rol administrador
    
    Query params:
    - activos: (opcional) true/false (default: true)
    """
    try:
        solo_activos = request.args.get('activos', 'true').lower() == 'true'
        
        usuarios = usuario_service.listar_por_rol(rol, solo_activos)
        
        return jsonify({
            "total": len(usuarios),
            "usuarios": usuarios
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@usuarios_bp.route('/<id_usuario>', methods=['PUT'])
@require_jwt
def actualizar_usuario(jwt_payload, id_usuario):
    """
    PUT /usuarios/{id_usuario}
    Actualiza un usuario existente
    
    Requiere: JWT válido
    Restricción: Solo puede actualizar su propio usuario, excepto administrador
    
    Body:
    {
        "nombre": "Juan Carlos Pérez",
        "email": "nuevo.email@example.com"
    }
    """
    try:
        # Validar que solo pueda actualizar su propio usuario (excepto admin)
        if jwt_payload["rol"] != "administrador" and jwt_payload["id_usuario"] != id_usuario:
            return jsonify({
                "error": "Solo puedes actualizar tu propio usuario"
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Restricción: usuarios normales no pueden cambiar su rol
        if jwt_payload["rol"] != "administrador" and "rol" in data:
            return jsonify({
                "error": "No tienes permiso para cambiar el rol"
            }), 403
        
        resultado = usuario_service.actualizar_usuario(id_usuario, data)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@usuarios_bp.route('/<id_usuario>/desactivar', methods=['PATCH'])
@require_jwt
@require_roles(["administrador"])
def desactivar_usuario(jwt_payload, id_usuario):
    """
    PATCH /usuarios/{id_usuario}/desactivar
    Desactiva un usuario (soft delete)
    
    Requiere: JWT con rol administrador
    """
    try:
        resultado = usuario_service.desactivar_usuario(id_usuario)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@usuarios_bp.route('/<id_usuario>/cambiar-password', methods=['POST'])
@require_jwt
def cambiar_password(jwt_payload, id_usuario):
    """
    POST /usuarios/{id_usuario}/cambiar-password
    Cambia la contraseña de un usuario
    
    Requiere: JWT válido
    Restricción: Solo puede cambiar su propia contraseña
    
    Body:
    {
        "password_actual": "oldpass123",
        "password_nueva": "newpass456"
    }
    """
    try:
        # Validar que solo pueda cambiar su propia contraseña
        if jwt_payload["id_usuario"] != id_usuario:
            return jsonify({
                "error": "Solo puedes cambiar tu propia contraseña"
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validar campos requeridos
        if 'password_actual' not in data or 'password_nueva' not in data:
            return jsonify({
                "error": "Campos 'password_actual' y 'password_nueva' son requeridos"
            }), 400
        
        resultado = usuario_service.cambiar_password(
            id_usuario,
            data['password_actual'],
            data['password_nueva']
        )
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@usuarios_bp.route('/me', methods=['GET'])
@require_jwt
def obtener_usuario_actual(jwt_payload):
    """
    GET /usuarios/me
    Obtiene información del usuario actual (del JWT)
    
    Requiere: JWT válido
    """
    try:
        usuario = usuario_service.obtener_usuario(jwt_payload["id_usuario"])
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify(usuario), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
