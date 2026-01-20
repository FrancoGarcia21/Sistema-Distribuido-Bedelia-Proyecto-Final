import time
from pymongo import MongoClient, ReadPreference
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from ..config import MONGO_URI, MONGO_DB_NAME


class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._connect_with_retry()

    def _connect_with_retry(self):
        max_retries = 10
        base_delay = 2

        for attempt in range(max_retries):
            try:
                print(f"🔄 Intento {attempt + 1}/{max_retries} de conexión a MongoDB...")

                self.client = MongoClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000,
                    retryWrites=True,
                    read_preference=ReadPreference.PRIMARY_PREFERRED,
                )

                admin_db = self.client.admin
                admin_db.command("ping")

                # Si quieres exigir replica set sí o sí, deja esto:
                admin_db.command("replSetGetStatus")

                self.db = self.client[MONGO_DB_NAME]

                # colecciones (si las usas en otros lados)
                self.aulas = self.db.aulas
                self.usuarios = self.db.usuarios
                self.cronograma = self.db.cronograma

                # índices básicos
                self.aulas.create_index([("nro_aula", 1), ("piso", 1)], unique=True, name="idx_aula_unique")

                print("✅ MongoDB conectado")
                return

            except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"⚠️ Error MongoDB: {e}")
                    print(f"⏳ Reintentando en {delay} segundos...")
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"❌ No se pudo conectar a MongoDB: {e}")

    def close(self):
        if hasattr(self, "client"):
            self.client.close()


_mongo = MongoDB()

def get_mongo_db():
    return _mongo.db
