import uuid
import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.database.models import User, Role, UserRole
from app.database.session import get_db

settings = get_settings()

def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="AUTHENTICATION_REQUIRED")
    try:
        payload = jwt.decode(authorization[7:], settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise ValueError("access token required")
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
    user = db.scalar(select(User).where(User.id == user_id))
    if not user or user.status != "ACTIVE":
        raise HTTPException(status_code=401, detail="USER_NOT_ACTIVE")
    return user

def require_roles(*allowed_roles: str):
    def dependency(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        role_names = set(db.scalars(
            select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user.id)
        ).all())
        if not role_names.intersection(allowed_roles):
            raise HTTPException(status_code=403, detail="INSUFFICIENT_ROLE")
        return user
    return dependency
