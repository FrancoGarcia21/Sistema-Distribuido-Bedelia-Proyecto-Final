from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI no está configurado en app_alumno")
    _client = MongoClient(MONGO_URI)
    _db = _client[MONGO_DB_NAME]
    return _db

def find_user_by_username(username: str):
    db = get_db()
    return db.usuarios.find_one({"usuario": username, "estado": "activo"})

def find_user_carrera(user_id):
    """
    Devuelve id_carrera (string) para un alumno.
    Soporta 2 formas:
    1) usuarios.id_carrera (si lo agregaron)
    2) colección usuario_carrera: { id_usuario: ObjectId, id_carrera: "..." }
    """
    db = get_db()

    u = db.usuarios.find_one({"_id": user_id}, {"id_carrera": 1})
    if u and "id_carrera" in u and u["id_carrera"] is not None:
        return str(u["id_carrera"])

    # fallback a colección de dominio alumno (si existe)
    if "usuario_carrera" in db.list_collection_names():
        rel = db.usuario_carrera.find_one({"id_usuario": user_id}, {"id_carrera": 1})
        if rel and "id_carrera" in rel:
            return str(rel["id_carrera"])

    return None

def get_materias_de_carrera(id_carrera: str):
    db = get_db()
    doc = db.carrera_materias.find_one({"id_carrera": str(id_carrera)})
    if not doc:
        return []
    materias = doc.get("materias", [])
    # normalizamos keys para frontend
    out = []
    for m in materias:
        out.append({
            "id_materia": str(m.get("id_materia")),
            "nombre_materia": m.get("nombre_materia", ""),
            "horarios": m.get("horarios", {})
        })
    return out

def save_subscription(user_id, id_carrera: str, id_materia: str, subscribed: bool):
    """
    Persistimos la elección del alumno (anotarse/desanotarse) para recordar su selección.
    Colección: alumno_subs
    """
    db = get_db()
    key = {"id_usuario": user_id, "id_carrera": str(id_carrera), "id_materia": str(id_materia)}
    if subscribed:
        db.alumno_subs.update_one(key, {"$set": {**key, "subscribed": True}}, upsert=True)
    else:
        db.alumno_subs.delete_one(key)

def list_subscriptions(user_id, id_carrera: str):
    db = get_db()
    cur = db.alumno_subs.find({"id_usuario": user_id, "id_carrera": str(id_carrera)})
    return [ {"id_materia": str(x["id_materia"])} for x in cur ]

def find_materias_by_carrera(id_carrera: str):
    db = get_db()
    doc = db.carrera_materias.find_one(
        {"id_carrera": str(id_carrera)},
        {"_id": 0, "materias": 1}
    )
    if not doc:
        return []
    return doc.get("materias", [])
