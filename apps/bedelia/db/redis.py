# =============================
# =============================


import redis
from config import (
REDIS_HOST,
REDIS_PORT,
REDIS_DB,
REDIS_TTL_AULA_CACHE,
REDIS_TTL_SESION,
REDIS_TTL_LOCK,
)


class RedisClient:
"""
Cliente Redis para cache, sesiones y locks distribuidos.
"""


def __init__(self):
try:
self.client = redis.Redis(
host=REDIS_HOST,
port=REDIS_PORT,
db=REDIS_DB,
decode_responses=True,
socket_connect_timeout=5,
)
# Validación de conexión
self.client.ping()
except redis.RedisError as e:
raise RuntimeError(f"No se pudo conectar a Redis: {e}")


# -----------------------------
# Cache de Aulas
# -----------------------------


def get_aula_cache(self, aula_id):
return self.client.get(f"aula:{aula_id}")


def set_aula_cache(self, aula_id, value):
self.client.setex(
f"aula:{aula_id}",
REDIS_TTL_AULA_CACHE,
value,
)


# -----------------------------
# Sesiones
# -----------------------------


def set_sesion(self, session_id, value):
self.client.setex(
f"session:{session_id}",
REDIS_TTL_SESION,
value,
)


def get_sesion(self, session_id):
return self.client.get(f"session:{session_id}")


# -----------------------------
# Locks Distribuidos
# -----------------------------


def acquire_lock(self, lock_key):
return self.client.set(
f"lock:{lock_key}",
"1",
nx=True,
ex=REDIS_TTL_LOCK,
)


def release_lock(self, lock_key):
self.client.delete(f"lock:{lock_key}")




# Instancia singleton
redis_client = RedisClient()