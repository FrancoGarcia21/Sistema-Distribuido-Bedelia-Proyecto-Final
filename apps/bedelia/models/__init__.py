"""
Modelos de datos para Smart Campus - Bedelia
Expone las clases de modelo para importación centralizada
"""

from .aula import AulaModel
from .usuario import UsuarioModel
from .cronograma import CronogramaModel
from .carrera_materia import CarreraMateriaModel
from .asignacion import AsignacionModel

__all__ = [
    'AulaModel',
    'UsuarioModel',
    'CronogramaModel',
    'CarreraMateriaModel',
    'AsignacionModel'
]
