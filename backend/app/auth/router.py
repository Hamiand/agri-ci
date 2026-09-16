import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.database.models import AuditLog, Role, User, UserRole
from app.database.session import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

def roles_for(db: Session, user_id):
    stmt = select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
    return list(db.scalars(stmt).all())

@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.phone == payload.phone)):
        raise HTTPException(status_code=409, detail="PHONE_ALREADY_REGISTERED")
    role = db.scalar(select(Role).where(Role.name == payload.role))
    if not role:
        raise HTTPException(status_code=400, detail="INVALID_ROLE")
    user = User(phone=payload.phone, password_hash=hash_password(payload.password),
                preferred_language=payload.preferred_language, status="ACTIVE")
    db.add(user)
    db.flush()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.add(AuditLog(actor_user_id=user.id, action="USER_REGISTERED", entity_type="USER",
                    entity_id=str(user.id), request_id=request.state.request_id))
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, phone=user.phone, preferred_language=user.preferred_language,
                        status=user.status, roles=[role.name])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.phone == payload.phone))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_CREDENTIALS")
    roles = roles_for(db, user.id)
    token = create_access_token, create_refresh_token(str(user.id), roles)
    return TokenResponse(access_token=token,
        user=UserResponse(id=user.id, phone=user.phone, preferred_language=user.preferred_language,
                          status=user.status, roles=roles))

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    from app.core.config import get_settings
    import jwt
    settings = get_settings()
    try:
        decoded = jwt.decode(payload.refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="INVALID_TOKEN_TYPE")
    user = db.get(User, uuid.UUID(decoded["sub"]))
    if not user or user.status != "ACTIVE":
        raise HTTPException(status_code=401, detail="USER_NOT_ACTIVE")
    roles = list(db.scalars(select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user.id)).all())
    return {"access_token": create_access_token(str(user.id), roles),
            "refresh_token": create_refresh_token(str(user.id), roles),
            "token_type": "bearer"}
