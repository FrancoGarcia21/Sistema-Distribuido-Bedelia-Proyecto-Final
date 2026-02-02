"""
Routes: Carreras y Materias
Endpoints para gestión de carreras, materias y asignaciones
"""

from flask import request, jsonify
from middleware.auth import require_jwt, require_roles
from services.carrera_service import CarreraService
from . import carreras_bp

# Instanciar service
carrera_service = CarreraService()


# ========== MATERIAS ==========

@carreras_bp.route('/materias', methods=['POST'])
@require_jwt
@require_roles(["administrador"])
def crear_materia(jwt_payload):
    """
    POST /carreras/materias
    Crea una materia nueva
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "carrera": "Ingeniería en Sistemas",
        "materia": "Sistemas Distribuidos",
        "codigo_materia": "ING-401",
        "anio": 4,
        "cuatrimestre": 1,
        "carga_horaria": 6
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validar campos requeridos
        campos_requeridos = [
            "carrera", "materia", "codigo_materia",
            "anio", "cuatrimestre", "carga_horaria"
        ]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "error": f"Campo '{campo}' es requerido"
                }), 400
        
        resultado = carrera_service.crear_materia(data)
        
        return jsonify(resultado), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@carreras_bp.route('/materias/<id_materia>', methods=['GET'])
@require_jwt
def obtener_materia(jwt_payload, id_materia):
    """
    GET /carreras/materias/{id_materia}
    Obtiene una materia por ID
    
    Requiere: JWT válido
    """
    try:
        materia = carrera_service.obtener_materia(id_materia)
        
        if not materia:
            return jsonify({"error": "Materia no encontrada"}), 404
        
        return jsonify(materia), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@carreras_bp.route('/<carrera>/materias', methods=['GET'])
@require_jwt
def listar_materias_por_carrera(jwt_payload, carrera):
    """
    GET /carreras/{carrera}/materias?activas=true
    Lista materias de una carrera
    
    Requiere: JWT válido
    
    Query params:
    - activas: (opcional) true/false (default: true)
    """
    try:
        solo_activas = request.args.get('activas', 'true').lower() == 'true'
        
        materias = carrera_service.listar_materias_por_carrera(carrera, solo_activas)
        
        return jsonify({
            "carrera": carrera,
            "total": len(materias),
            "materias": materias
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@carreras_bp.route('/materias/<id_materia>', methods=['PUT'])
@require_jwt
@require_roles(["administrador"])
def actualizar_materia(jwt_payload, id_materia):
    """
    PUT /carreras/materias/{id_materia}
    Actualiza una materia existente
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "carga_horaria": 8,
        "activa": true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        resultado = carrera_service.actualizar_materia(id_materia, data)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ========== ASIGNACIONES PROFESOR-MATERIA ==========

@carreras_bp.route('/materias/asignar-profesor', methods=['POST'])
@require_jwt
@require_roles(["administrador"])
def asignar_profesor_materia(jwt_payload):
    """
    POST /carreras/materias/asignar-profesor
    Asigna un profesor a una materia
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "id_profesor": "507f1f77bcf86cd799439011",
        "id_materia": "507f1f77bcf86cd799439012",
        "carrera": "Ingeniería en Sistemas"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validar campos requeridos
        campos_requeridos = ["id_profesor", "id_materia", "carrera"]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "error": f"Campo '{campo}' es requerido"
                }), 400
        
        resultado = carrera_service.asignar_profesor_materia(data)
        
        return jsonify(resultado), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@carreras_bp.route('/profesores/<id_profesor>/materias', methods=['GET'])
@require_jwt
def listar_materias_profesor(jwt_payload, id_profesor):
    """
    GET /carreras/profesores/{id_profesor}/materias?activas=true
    Lista materias asignadas a un profesor
    
    Requiere: JWT válido
    Restricción: Un profesor solo puede ver sus propias materias
    
    Query params:
    - activas: (opcional) true/false (default: true)
    """
    try:
        # Validar que solo pueda ver sus propias materias (excepto admin)
        if jwt_payload["rol"] == "profesor" and jwt_payload["id_usuario"] != id_profesor:
            return jsonify({
                "error": "Solo puedes ver tus propias materias"
            }), 403
        
        solo_activas = request.args.get('activas', 'true').lower() == 'true'
        
        materias = carrera_service.listar_materias_profesor(id_profesor, solo_activas)
        
        return jsonify({
            "total": len(materias),
            "materias": materias
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@carreras_bp.route('/profesores/<id_profesor>/materias/<id_materia>', methods=['DELETE'])
@require_jwt
@require_roles(["administrador"])
def desasignar_profesor_materia(jwt_payload, id_profesor, id_materia):
    """
    DELETE /carreras/profesores/{id_profesor}/materias/{id_materia}
    Desasigna un profesor de una materia
    
    Requiere: JWT con rol administrador
    """
    try:
        resultado = carrera_service.desasignar_profesor_materia(id_profesor, id_materia)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ========== INSCRIPCIONES ALUMNO-CARRERA ==========

@carreras_bp.route('/inscribir-alumno', methods=['POST'])
@require_jwt
@require_roles(["administrador"])
def inscribir_alumno_carrera(jwt_payload):
    """
    POST /carreras/inscribir-alumno
    Inscribe un alumno a una carrera
    
    Requiere: JWT con rol administrador
    
    Body:
    {
        "id_usuario": "507f1f77bcf86cd799439011",
        "carrera": "Ingeniería en Sistemas",
        "anio_ingreso": 2026
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validar campos requeridos
        campos_requeridos = ["id_usuario", "carrera", "anio_ingreso"]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "error": f"Campo '{campo}' es requerido"
                }), 400
        
        resultado = carrera_service.inscribir_alumno_carrera(data)
        
        return jsonify(resultado), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@carreras_bp.route('/alumnos/<id_usuario>/carreras', methods=['GET'])
@require_jwt
def obtener_carreras_alumno(jwt_payload, id_usuario):
    """
    GET /carreras/alumnos/{id_usuario}/carreras
    Obtiene las carreras en las que está inscrito un alumno
    
    Requiere: JWT válido
    Restricción: Un alumno solo puede ver sus propias carreras
    """
    try:
        # Validar que solo pueda ver sus propias carreras (excepto admin)
        if jwt_payload["rol"] == "alumno" and jwt_payload["id_usuario"] != id_usuario:
            return jsonify({
                "error": "Solo puedes ver tus propias carreras"
            }), 403
        
        carreras = carrera_service.obtener_carreras_alumno(id_usuario)
        
        return jsonify({
            "total": len(carreras),
            "carreras": carreras
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@carreras_bp.route('/alumnos/<id_usuario>/materias/suscribir', methods=['POST'])
@require_jwt
def agregar_materia_suscrita(jwt_payload, id_usuario):
    """
    POST /carreras/alumnos/{id_usuario}/materias/suscribir
    Agrega una materia a las suscritas del alumno (para MQTT)
    
    Requiere: JWT válido
    Restricción: Un alumno solo puede suscribirse a sus propias materias
    
    Body:
    {
        "carrera": "Ingeniería en Sistemas",
        "id_materia": "507f1f77bcf86cd799439011"
    }
    """
    try:
        # Validar que solo pueda suscribirse a sus propias materias
        if jwt_payload["id_usuario"] != id_usuario:
            return jsonify({
                "error": "Solo puedes suscribirte a tus propias materias"
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validar campos requeridos
        if 'carrera' not in data or 'id_materia' not in data:
            return jsonify({
                "error": "Campos 'carrera' e 'id_materia' son requeridos"
            }), 400
        
        resultado = carrera_service.agregar_materia_suscrita(
            id_usuario,
            data['carrera'],
            data['id_materia']
        )
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
