from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import get_settings

password_hash = PasswordHash.recommended()
settings = get_settings()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def create_access_token(subject: str, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject, "roles": roles, "type": "access",
        "iat": now, "exp": now + timedelta(minutes=settings.jwt_access_token_minutes)
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def create_refresh_token(subject: str, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject, "roles": roles, "type": "refresh",
        "iat": now, "exp": now + timedelta(days=settings.jwt_refresh_token_days)
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
