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

import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

class MongoDB:
    def __init__(self):
        uri = "mongodb://mongo-primary:27017/?replicaSet=rs0"
        self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)

        for i in range(10):
            try:
                self.client.admin.command("ping")
                print("✅ MongoDB conectado")
                return
            except ServerSelectionTimeoutError:
                print(f"⏳ MongoDB no disponible, reintentando ({i+1}/10)...")
                time.sleep(3)

        raise RuntimeError("❌ No se pudo conectar a MongoDB luego de varios intentos")

    def get_db(self):
        return self.client["smartcampus"]