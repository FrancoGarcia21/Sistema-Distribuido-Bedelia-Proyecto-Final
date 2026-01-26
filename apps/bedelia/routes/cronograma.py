"""
Routes: Cronograma
Endpoints para gestión de cronogramas (asignaciones de aulas)
"""

from flask import request, jsonify
from datetime import date
from middleware.auth import require_jwt, require_roles
from services.cronograma_service import CronogramaService
from . import cronograma_bp

# Instanciar service
cronograma_service = CronogramaService()


@cronograma_bp.route('/', methods=['POST'])
@require_jwt
@require_roles(["administrador", "profesor"])
def crear_cronograma(jwt_payload):
    """
    POST /cronograma
    Crea un cronograma (asignación de aula con validaciones)
    
    Requiere: JWT con rol administrador o profesor
    
    Body:
    {
        "id_aula": "507f1f77bcf86cd799439011",
        "id_materia": "507f1f77bcf86cd799439012",
        "id_profesor": "507f1f77bcf86cd799439013",
        "id_carrera": "Ingeniería en Sistemas",
        "fecha": "2026-01-30",
        "hora_inicio": "14:00",
        "hora_fin": "16:00",
        "tipo": "teorica"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validar campos requeridos
        campos_requeridos = [
            "id_aula", "id_materia", "id_profesor", "id_carrera",
            "fecha", "hora_inicio", "hora_fin", "tipo"
        ]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "error": f"Campo '{campo}' es requerido"
                }), 400
        
        # Si es profesor, validar que sea su propio ID
        if jwt_payload["rol"] == "profesor" and jwt_payload["id_usuario"] != data["id_profesor"]:
            return jsonify({
                "error": "Un profesor solo puede crear cronogramas para sí mismo"
            }), 403
        
        resultado = cronograma_service.crear_cronograma(data)
        
        return jsonify(resultado), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@cronograma_bp.route('/<id_cronograma>', methods=['GET'])
@require_jwt
def obtener_cronograma(jwt_payload, id_cronograma):
    """
    GET /cronograma/{id_cronograma}
    Obtiene un cronograma por ID
    
    Requiere: JWT válido
    """
    try:
        cronograma = cronograma_service.obtener_cronograma(id_cronograma)
        
        if not cronograma:
            return jsonify({"error": "Cronograma no encontrado"}), 404
        
        return jsonify(cronograma), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@cronograma_bp.route('/aula/<id_aula>', methods=['GET'])
@require_jwt
def listar_por_aula(jwt_payload, id_aula):
    """
    GET /cronograma/aula/{id_aula}?fecha_desde=2026-01-30
    Lista cronogramas de un aula
    
    Requiere: JWT válido
    
    Query params:
    - fecha_desde: (opcional) formato YYYY-MM-DD
    """
    try:
        fecha_desde = None
        fecha_param = request.args.get('fecha_desde')
        
        if fecha_param:
            try:
                fecha_desde = date.fromisoformat(fecha_param)
            except ValueError:
                return jsonify({
                    "error": "Formato de fecha inválido. Use YYYY-MM-DD"
                }), 400
        
        cronogramas = cronograma_service.listar_por_aula(id_aula, fecha_desde)
        
        return jsonify({
            "total": len(cronogramas),
            "cronogramas": cronogramas
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@cronograma_bp.route('/profesor/<id_profesor>', methods=['GET'])
@require_jwt
def listar_por_profesor(jwt_payload, id_profesor):
    """
    GET /cronograma/profesor/{id_profesor}?activos=true
    Lista cronogramas de un profesor
    
    Requiere: JWT válido
    Restricción: Un profesor solo puede ver sus propios cronogramas
    
    Query params:
    - activos: (opcional) true/false (default: true)
    """
    try:
        # Validar que solo pueda ver sus propios cronogramas (excepto admin)
        if jwt_payload["rol"] == "profesor" and jwt_payload["id_usuario"] != id_profesor:
            return jsonify({
                "error": "Solo puedes ver tus propios cronogramas"
            }), 403
        
        solo_activos = request.args.get('activos', 'true').lower() == 'true'
        
        cronogramas = cronograma_service.listar_por_profesor(id_profesor, solo_activos)
        
        return jsonify({
            "total": len(cronogramas),
            "cronogramas": cronogramas
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@cronograma_bp.route('/carrera/<id_carrera>/materia/<id_materia>', methods=['GET'])
@require_jwt
def listar_por_carrera_materia(jwt_payload, id_carrera, id_materia):
    """
    GET /cronograma/carrera/{id_carrera}/materia/{id_materia}
    Lista cronogramas por carrera y materia (para alumnos)
    
    Requiere: JWT válido
    """
    try:
        cronogramas = cronograma_service.listar_por_carrera_materia(id_carrera, id_materia)
        
        return jsonify({
            "total": len(cronogramas),
            "cronogramas": cronogramas
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@cronograma_bp.route('/<id_cronograma>/finalizar', methods=['POST'])
@require_jwt
@require_roles(["administrador", "profesor"])
def finalizar_cronograma(jwt_payload, id_cronograma):
    """
    POST /cronograma/{id_cronograma}/finalizar
    Finaliza un cronograma y libera el aula
    
    Requiere: JWT con rol administrador o profesor
    """
    try:
        # Si es profesor, validar que sea su propio cronograma
        if jwt_payload["rol"] == "profesor":
            cronograma = cronograma_service.obtener_cronograma(id_cronograma)
            if not cronograma or cronograma["id_profesor"] != jwt_payload["id_usuario"]:
                return jsonify({
                    "error": "Solo puedes finalizar tus propios cronogramas"
                }), 403
        
        resultado = cronograma_service.finalizar_cronograma(id_cronograma)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@cronograma_bp.route('/<id_cronograma>/cancelar', methods=['POST'])
@require_jwt
@require_roles(["administrador", "profesor"])
def cancelar_cronograma(jwt_payload, id_cronograma):
    """
    POST /cronograma/{id_cronograma}/cancelar
    Cancela un cronograma y libera el aula
    
    Requiere: JWT con rol administrador o profesor
    
    Body (opcional):
    {
        "motivo": "Profesor enfermo"
    }
    """
    try:
        # Si es profesor, validar que sea su propio cronograma
        if jwt_payload["rol"] == "profesor":
            cronograma = cronograma_service.obtener_cronograma(id_cronograma)
            if not cronograma or cronograma["id_profesor"] != jwt_payload["id_usuario"]:
                return jsonify({
                    "error": "Solo puedes cancelar tus propios cronogramas"
                }), 403
        
        data = request.get_json() or {}
        motivo = data.get("motivo", "")
        
        resultado = cronograma_service.cancelar_cronograma(id_cronograma, motivo)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@cronograma_bp.route('/<id_cronograma>/cupo', methods=['GET'])
@require_jwt
def validar_cupo(jwt_payload, id_cronograma):
    """
    GET /cronograma/{id_cronograma}/cupo
    Valida si hay cupo disponible en un cronograma
    
    Requiere: JWT válido
    """
    try:
        resultado = cronograma_service.validar_cupo(id_cronograma)
        
        return jsonify(resultado), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
