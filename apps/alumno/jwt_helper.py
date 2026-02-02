# /app/jwt_helper.py
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt  # PyJWT


class JWTHelper:
    """
    Helper JWT simple para Flask.

    - Se puede instanciar: JWTHelper(secret, algorithm, exp_minutes)
    - O usar como clase: JWTHelper.create(payload) leyendo env vars

    Env vars soportadas:
      JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES
    """

    def __init__(
        self,
        secret: Optional[str] = None,
        algorithm: Optional[str] = None,
        exp_minutes: Optional[int] = None,
    ):
        self.secret = secret or os.getenv("JWT_SECRET", "dev-secret-change-me")
        self.algorithm = algorithm or os.getenv("JWT_ALGORITHM", "HS256")
        self.exp_minutes = int(exp_minutes or os.getenv("JWT_EXP_MINUTES", "60"))

    # -------------------------
    # Métodos de instancia
    # -------------------------
    def encode(self, payload: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=(expires_minutes or self.exp_minutes))

        data = dict(payload)
        data["iat"] = int(now.timestamp())
        data["exp"] = int(exp.timestamp())

        token = jwt.encode(data, self.secret, algorithm=self.algorithm)

        # PyJWT a veces devuelve str, a veces bytes según versión/config
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    def decode(self, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        options = {"verify_exp": verify_exp}
        return jwt.decode(
            token,
            self.secret,
            algorithms=[self.algorithm],
            options=options,
        )

    def verify(self, token: str) -> bool:
        try:
            self.decode(token, verify_exp=True)
            return True
        except jwt.PyJWTError:
            return False

    # -------------------------
    # Atajos de clase (sin recursión)
    # -------------------------
    @classmethod
    def _default(cls) -> "JWTHelper":
        return cls()  # toma env vars

    @classmethod
    def create(cls, payload: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
        return cls._default().encode(payload, expires_minutes=expires_minutes)

    @classmethod
    def decode_token(cls, token: str) -> Dict[str, Any]:
        return cls._default().decode(token)

    @classmethod
    def verify_token(cls, token: str) -> bool:
        return cls._default().verify(token)
