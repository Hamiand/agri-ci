from uuid import UUID
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=30)
    password: str = Field(min_length=10, max_length=128)
    preferred_language: str = "fr"
    role: str = "FARMER"
    roles: list[str] | None = None

class LoginRequest(BaseModel):
    phone: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    phone: str
    preferred_language: str
    status: str
    roles: list[str]
    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
