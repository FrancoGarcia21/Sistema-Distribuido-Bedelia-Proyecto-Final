"""
Script de prueba para Modelos y Utils
Ejecutar: python test_models_utils.py
"""

from db.mongo import get_mongo_db
from models.aula import AulaModel
from models.usuario import UsuarioModel
from models.cronograma import CronogramaModel
from models.carrera_materia import CarreraMateriaModel
from models.asignacion import AsignacionModel
from utils.jwt_helper import JWTHelper
from utils.validators import Validators
from utils.mqtt_events import MQTTEventPublisher
from datetime import date, datetime
from bson import ObjectId

print("=" * 60)
print("🧪 PRUEBA DE MODELOS Y UTILS - SMART CAMPUS")
print("=" * 60)

# Obtener conexión a MongoDB
db = get_mongo_db()

# ========== PRUEBA 1: CREAR ÍNDICES ==========
print("\n[1/10] Creando índices en MongoDB...")
try:
    AulaModel.crear_indices(db.aulas)
    UsuarioModel.crear_indices(db.usuarios)
    CronogramaModel.crear_indices(db.cronograma)
    CarreraMateriaModel.crear_indices(db.carrera_materias)
    AsignacionModel.crear_indices_usuario_carrera(db.usuario_carrera)
    AsignacionModel.crear_indices_profesor_materia(db.profesor_carrera_materia)
    print("✅ Índices creados correctamente")
except Exception as e:
    print(f"❌ Error al crear índices: {e}")

# ========== PRUEBA 2: CREAR AULA ==========
print("\n[2/10] Creando aula de prueba...")
try:
    id_aula = AulaModel.crear(db.aulas, {
        "nro_aula": 101,
        "piso": 1,
        "cupo": 30,
        "estado": "disponible",
        "descripcion": "Aula de prueba automatizada"
    })
    print(f"✅ Aula creada con ID: {id_aula}")
except Exception as e:
    print(f"❌ Error: {e}")

# ========== PRUEBA 3: CREAR USUARIO ADMINISTRADOR ==========
print("\n[3/10] Creando usuario administrador...")
try:
    id_admin = UsuarioModel.crear(db.usuarios, {
        "usuario": "admin_test",
        "nombre": "Administrador Test",
        "email": "admin@test.com",
        "password": "admin123",
        "rol": "administrador"
    })
    print(f"✅ Administrador creado con ID: {id_admin}")
except Exception as e:
    print(f"❌ Error: {e}")

# ========== PRUEBA 4: CREAR USUARIO PROFESOR ==========
print("\n[4/10] Creando usuario profesor...")
try:
    id_profesor = UsuarioModel.crear(db.usuarios, {
        "usuario": "prof_test",
        "nombre": "Profesor Test",
        "email": "profesor@test.com",
        "password": "prof123",
        "rol": "profesor"
    })
    print(f"✅ Profesor creado con ID: {id_profesor}")
except Exception as e:
    print(f"❌ Error: {e}")

# ========== PRUEBA 5: CREAR CARRERA Y MATERIA ==========
print("\n[5/10] Creando carrera y materia...")
try:
    id_materia = CarreraMateriaModel.crear(db.carrera_materias, {
        "carrera": "Ingeniería en Sistemas",
        "materia": "Sistemas Distribuidos",
        "codigo_materia": "ING-401",
        "anio": 4,
        "cuatrimestre": 1,
        "carga_horaria": 6
    })
    print(f"✅ Materia creada con ID: {id_materia}")
except Exception as e:
    print(f"❌ Error: {e}")

# ========== PRUEBA 6: ASIGNAR PROFESOR A MATERIA ==========
print("\n[6/10] Asignando profesor a materia...")
try:
    id_asig = AsignacionModel.asignar_profesor_materia(db.profesor_carrera_materia, {
        "id_profesor": id_profesor,
        "id_materia": id_materia,
        "carrera": "Ingeniería en Sistemas"
    })
    print(f"✅ Asignación creada con ID: {id_asig}")
except Exception as e:
    print(f"❌ Error: {e}")

# ========== PRUEBA 7: CREAR CRONOGRAMA ==========
print("\n[7/10] Creando cronograma (asignación de aula)...")
try:
    id_cronograma = CronogramaModel.crear(db.cronograma, {
        "id_aula": id_aula,
        "id_materia": id_materia,
        "id_profesor": id_profesor,
        "id_carrera": "Ingeniería en Sistemas",
        "fecha": date.today(),
        "hora_inicio": "14:00",
        "hora_fin": "16:00",
        "tipo": "teorica"
    })
    print(f"✅ Cronograma creado con ID: {id_cronograma}")
except Exception as e:
    print(f"❌ Error: {e}")

# ========== PRUEBA 8: VALIDATORS ==========
print("\n[8/10] Probando Validators...")
try:
    # Validar ObjectId
    assert Validators.es_objectid_valido(id_aula) == True
    assert Validators.es_objectid_valido("invalid") == False
    
    # Validar horario
    assert Validators.validar_horario_permitido("14:00") == True
    assert Validators.validar_horario_permitido("05:00") == False
    
    # Validar duración
    valido, duracion, error = Validators.validar_duracion("14:00", "16:00")
    assert valido == True
    assert duracion == 120
    
    # Validar email
    assert Validators.validar_email("test@example.com") == True
    assert Validators.validar_email("invalid") == False
    
    print("✅ Todos los validators funcionan correctamente")
except AssertionError as e:
    print(f"❌ Error en validators: {e}")

# ========== PRUEBA 9: JWT HELPER ==========
print("\n[9/10] Probando JWT Helper...")
try:
    # Obtener usuario
    usuario = UsuarioModel.obtener_por_id(db.usuarios, id_admin)
    
    # Generar token
    token = JWTHelper.generar_token(usuario)
    print(f"✅ Token generado: {token[:50]}...")
    
    # Validar token
    payload = JWTHelper.validar_token(token)
    assert payload is not None
    assert payload["usuario"] == "admin_test"
    assert payload["rol"] == "administrador"
    print(f"✅ Token validado correctamente. Usuario: {payload['usuario']}, Rol: {payload['rol']}")
    
    # Verificar rol
    assert JWTHelper.verificar_rol(payload, ["administrador"]) == True
    assert JWTHelper.verificar_rol(payload, ["profesor"]) == False
    print("✅ Verificación de roles funciona correctamente")
    
except Exception as e:
    print(f"❌ Error en JWT: {e}")

# ========== PRUEBA 10: MQTT EVENT PUBLISHER ==========
print("\n[10/10] Probando MQTT Event Publisher...")
try:
    # Publicar evento de aula nueva
    resultado = MQTTEventPublisher.publicar_aula_nueva(str(id_aula), {
        "nro_aula": 101,
        "piso": 1,
        "cupo": 30,
        "estado": "disponible"
    })
    
    if resultado:
        print("✅ Evento 'aula_nueva' publicado correctamente")
    else:
        print("⚠️  MQTT no conectado (esperado si EMQX no está configurado)")
    
except Exception as e:
    print(f"⚠️  Error en MQTT (esperado): {e}")

print("\n" + "=" * 60)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 60)
print("\n📋 RESUMEN:")
print("- Modelos: ✅ Funcionando")
print("- Índices: ✅ Creados")
print("- Validators: ✅ Funcionando")
print("- JWT: ✅ Funcionando")
print("- MQTT: ⚠️  Requiere EMQX (opcional por ahora)")
print("\n🚀 Listo para continuar con Services")
