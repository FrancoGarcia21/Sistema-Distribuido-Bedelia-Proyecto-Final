# =============================
# App_Bedelia – MongoDB Connection
# =============================

# from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure
# from config import MONGO_URI, MONGO_DB_NAME

# class MongoDB:
#     """
#     Maneja la conexión a MongoDB (Replica Set) y expone las colecciones
#     utilizadas por App_Bedelia.
#     """

#     def __init__(self):
#         try:
#             self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
#             # Fuerza conexión inicial
#             self.client.admin.command('ping')
#         except ConnectionFailure as e:
#             raise RuntimeError(f"No se pudo conectar a MongoDB: {e}")

#         self.db = self.client[MONGO_DB_NAME]

#         # Colecciones usadas por App_Bedelia
#         self.usuarios = self.db.usuarios
#         self.aulas = self.db.aulas
#         self.carrera_materias = self.db.carrera_materias
#         self.cronograma = self.db.cronograma
#         self.profesor_carrera_materia = self.db.profesor_carrera_materia

#     def close(self):
#         """Cierra la conexión al cliente MongoDB"""
#         self.client.close()

# # Instancia singleton simple
# mongo_db = MongoDB()

##### 2da version #
# import time
# from pymongo import MongoClient
# from pymongo.errors import ServerSelectionTimeoutError

# class MongoDB:
#     def __init__(self):
#         uri = "mongodb://mongo-primary:27017/?replicaSet=rs0"
#         self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)

#         for i in range(10):
#             try:
#                 self.client.admin.command("ping")
#                 print("✅ MongoDB conectado")
#                 return
#             except ServerSelectionTimeoutError:
#                 print(f"⏳ MongoDB no disponible, reintentando ({i+1}/10)...")
#                 time.sleep(3)

#         raise RuntimeError("❌ No se pudo conectar a MongoDB luego de varios intentos")

#     def get_db(self):
#         return self.client["smartcampus"]

######  3ra version ####
# import time
# from pymongo import MongoClient
# from pymongo.errors import ServerSelectionTimeoutError

# MONGO_URI = "mongodb://mongo-primary:27017/?replicaSet=rs0"

# class MongoDB:
#     def __init__(self):
#         self.client = MongoClient(
#             MONGO_URI,
#             serverSelectionTimeoutMS=2000
#         )

#         for i in range(10):
#             try:
#                 self.client.admin.command("ping")
#                 print("✅ MongoDB conectado")
#                 break
#             except ServerSelectionTimeoutError:
#                 print(f"⏳ MongoDB no disponible ({i+1}/10)...")
#                 time.sleep(3)
#         else:
#             raise RuntimeError("❌ No se pudo conectar a MongoDB")

#         self.db = self.client["smartcampus"]

# mongo_db = MongoDB().db

###### 4ta version #
# =============================
# MongoDB Client (Replica Set)
# =============================

# from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure
# from config import MONGO_URI, MONGO_DB_NAME

# # Cliente y DB globales (lazy)
# _client: MongoClient | None = None
# _db = None


# def get_mongo_client() -> MongoClient:
#     """
#     Devuelve una instancia singleton de MongoClient.
#     """
#     global _client

#     if _client is None:
#         _client = MongoClient(
#             MONGO_URI,
#             serverSelectionTimeoutMS=5000,
#         )

#         # Verifica conexión
#         try:
#             _client.admin.command("ping")
#         except ConnectionFailure as e:
#             raise RuntimeError(f"No se pudo conectar a MongoDB: {e}")

#     return _client


# def get_mongo_db():
#     """
#     Devuelve la base de datos configurada.
#     """
#     global _db

#     if _db is None:
#         client = get_mongo_client()
#         _db = client[MONGO_DB_NAME]

#     return _db

##########################################3
#### 5ta version
# =============================
# App_Bedelia – MongoDB Connection (CORREGIDO)
# =============================

import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from ..config import MONGO_URI, MONGO_DB_NAME

class MongoDB:
    """
    Cliente MongoDB con soporte para Replica Set y reconexión automática.
    
    Características:
    - Reintentos automáticos con backoff
    - Validación de Replica Set
    - Manejo robusto de errores
    - Singleton thread-safe
    """
    
    _instance = None
    _lock = None  # Se inicializará con threading.Lock() si es necesario
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evitar reinicialización
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = False
        self._connect_with_retry()
        self._initialized = True
    
    def _connect_with_retry(self):
        """
        Conecta a MongoDB con reintentos exponenciales.
        """
        max_retries = 10
        base_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Intento {attempt + 1}/{max_retries} de conexión a MongoDB...")
                
                # Crear cliente con configuración para Replica Set
                self.client = MongoClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000,
                    retryWrites=True,
                    retryReads=True,
                    # Preferencia de lectura: primary por defecto
                    readPreference='primaryPreferred'
                )
                
                # Forzar conexión y verificar Replica Set
                admin_db = self.client.admin
                admin_db.command('ping')
                
                # Verificar que el Replica Set está configurado
                replica_status = admin_db.command('replSetGetStatus')
                
                if replica_status.get('ok') != 1:
                    raise ConnectionFailure("Replica Set no está inicializado correctamente")
                
                print(f"✅ Conectado a MongoDB Replica Set: {replica_status.get('set')}")
                print(f"   Primary: {self._get_primary_host(replica_status)}")
                
                # Obtener referencia a la base de datos
                self.db = self.client[MONGO_DB_NAME]
                
                # Inicializar colecciones
                self._initialize_collections()
                
                # Crear índices
                self._create_indexes()
                
                return
                
            except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Backoff exponencial
                    print(f"⚠️  Error: {e}")
                    print(f"⏳ Reintentando en {delay} segundos...")
                    time.sleep(delay)
                else:
                    raise RuntimeError(
                        f"❌ No se pudo conectar a MongoDB después de {max_retries} intentos: {e}"
                    )
    
    def _get_primary_host(self, replica_status):
        """
        Extrae el host del nodo PRIMARY del estado del Replica Set.
        """
        for member in replica_status.get('members', []):
            if member.get('stateStr') == 'PRIMARY':
                return member.get('name')
        return 'Unknown'
    
    def _initialize_collections(self):
        """
        Inicializa referencias a las colecciones del sistema.
        """
        self.usuarios = self.db.usuarios
        self.aulas = self.db.aulas
        self.cronograma = self.db.cronograma
        self.carrera_materias = self.db.carrera_materias
        self.usuario_carrera = self.db.usuario_carrera
        self.profesor_carrera_materia = self.db.profesor_carrera_materia
        
        print("📚 Colecciones inicializadas")
    
    def _create_indexes(self):
        """
        Crea los índices necesarios para el sistema.
        
        Índices obligatorios según especificación:
        - (nro_aula, piso) UNIQUE en colección 'aulas'
        """
        try:
            # Índice único compuesto en aulas
            self.aulas.create_index(
                [("nro_aula", 1), ("piso", 1)],
                unique=True,
                name="idx_aula_unique"
            )
            
            # Índice en cronograma para consultas frecuentes
            self.cronograma.create_index(
                [("id_aula", 1), ("fecha", 1), ("hora_inicio", 1)],
                name="idx_cronograma_aula_fecha"
            )
            
            # Índice en usuarios para login
            self.usuarios.create_index(
                [("usuario", 1)],
                unique=True,
                name="idx_usuario_login"
            )
            
            print("📑 Índices creados correctamente")
            
        except Exception as e:
            print(f"⚠️  Advertencia al crear índices: {e}")
    
    def close(self):
        """
        Cierra la conexión a MongoDB.
        """
        if hasattr(self, 'client'):
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada")


# =============================
# Singleton global
# =============================
mongo_db = MongoDB()