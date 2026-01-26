"""
Routes - Endpoints REST
"""

from flask import Blueprint

# Crear blueprints
aulas_bp = Blueprint('aulas', __name__, url_prefix='/aulas')
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')
cronograma_bp = Blueprint('cronograma', __name__, url_prefix='/cronograma')
carreras_bp = Blueprint('carreras', __name__, url_prefix='/carreras')

# Importar routes (después de crear blueprints para evitar imports circulares)
from . import aulas
from . import usuarios
from . import cronograma
from . import carreras

__all__ = [
    'aulas_bp',
    'usuarios_bp',
    'cronograma_bp',
    'carreras_bp'
]
