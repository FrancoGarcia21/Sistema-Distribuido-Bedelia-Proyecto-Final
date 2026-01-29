from datetime import datetime, timedelta, timezone
import jwt

class JWTHelper:
    def __init__(self, secret: str, algorithm: str = "HS256", exp_minutes: int = 60):
        self.secret = secret
        self.algorithm = algorithm
        self.exp_minutes = exp_minutes

    def create_token(self, payload: dict) -> str:
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=self.exp_minutes)

        full_payload = {
            **payload,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }

        return jwt.encode(full_payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret, algorithms=[self.algorithm])
