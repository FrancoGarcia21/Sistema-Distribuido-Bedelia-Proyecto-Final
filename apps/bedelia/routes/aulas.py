"""
Routes: Aulas
Endpoints para gestión de aulas
"""

from flask import request, jsonify
from middleware.auth import require_jwt, require_roles
from services.aula_service import AulaService
from . import aulas_bp

# Instanciar service
aula_service = AulaService()


@aulas_bp.route('/', methods=['POST'])
@require_jwt
@require_roles(["administrador"])
def crear_aula(jwt_payload):
    """
    POST /aulas
    Crea un aula nueva
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "nro_aula": 101,
        "piso": 1,
        "cupo": 30,
        "estado": "disponible",
        "descripcion": "Aula de teoría"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No se proporcionaron datos"
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ["nro_aula", "piso", "cupo", "estado"]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "error": f"Campo '{campo}' es requerido"
                }), 400
        
        resultado = aula_service.crear_aula(data)
        
        return jsonify(resultado), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@aulas_bp.route('/', methods=['GET'])
@require_jwt
def listar_aulas(jwt_payload):
    """
    GET /aulas?estado=disponible
    Lista todas las aulas con filtros opcionales
    
    Requiere: JWT válido
    
    Query params:
    - estado: (opcional) "disponible", "ocupada", "deshabilitada"
    """
    try:
        # Obtener filtros de query params
        filtros = {}
        
        estado = request.args.get('estado')
        if estado:
            filtros['estado'] = estado
        
        aulas = aula_service.listar_aulas(filtros if filtros else None)
        
        return jsonify({
            "total": len(aulas),
            "aulas": aulas
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@aulas_bp.route('/<id_aula>', methods=['GET'])
@require_jwt
def obtener_aula(jwt_payload, id_aula):
    """
    GET /aulas/{id_aula}
    Obtiene un aula por ID
    
    Requiere: JWT válido
    """
    try:
        aula = aula_service.obtener_aula(id_aula)
        
        if not aula:
            return jsonify({"error": "Aula no encontrada"}), 404
        
        return jsonify(aula), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@aulas_bp.route('/<id_aula>', methods=['PUT'])
@require_jwt
@require_roles(["administrador"])
def actualizar_aula(jwt_payload, id_aula):
    """
    PUT /aulas/{id_aula}
    Actualiza un aula existente
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "cupo": 35,
        "descripcion": "Aula renovada"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        resultado = aula_service.actualizar_aula(id_aula, data)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@aulas_bp.route('/<id_aula>/estado', methods=['PATCH'])
@require_jwt
@require_roles(["administrador"])
def cambiar_estado_aula(jwt_payload, id_aula):
    """
    PATCH /aulas/{id_aula}/estado
    Cambia el estado de un aula
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "estado": "deshabilitada"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'estado' not in data:
            return jsonify({
                "error": "Campo 'estado' es requerido"
            }), 400
        
        resultado = aula_service.cambiar_estado_aula(id_aula, data['estado'])
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@aulas_bp.route('/<id_aula>/asignar', methods=['POST'])
@require_jwt
@require_roles(["administrador"])
def asignar_aula(jwt_payload, id_aula):
    """
    POST /aulas/{id_aula}/asignar
    Asigna un aula a un cronograma
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "id_cronograma": "507f1f77bcf86cd799439011"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'id_cronograma' not in data:
            return jsonify({
                "error": "Campo 'id_cronograma' es requerido"
            }), 400
        
        resultado = aula_service.asignar_aula(id_aula, data['id_cronograma'])
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@aulas_bp.route('/<id_aula>/liberar', methods=['POST'])
@require_jwt
@require_roles(["administrador", "profesor"])
def liberar_aula(jwt_payload, id_aula):
    """
    POST /aulas/{id_aula}/liberar
    Libera un aula
    
    Requiere: JWT con rol administrador o profesor
    """
    try:
        resultado = aula_service.liberar_aula(id_aula)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@aulas_bp.route('/metricas', methods=['GET'])
@require_jwt
@require_roles(["administrador"])
def obtener_metricas(jwt_payload):
    """
    GET /aulas/metricas
    Obtiene métricas de estado de aulas
    
    Requiere: JWT con rol administrador
    """
    try:
        metricas = aula_service.obtener_metricas()
        
        return jsonify(metricas), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
