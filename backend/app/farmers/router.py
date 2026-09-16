import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.models import AuditLog, Farmer, User
from app.database.session import get_db

router = APIRouter(prefix="/farmers", tags=["Farmers"])

class FarmerCreate(BaseModel):
    display_name: str = Field(min_length=2, max_length=150)

class FarmerOut(BaseModel):
    id: uuid.UUID
    farmer_ref: str
    display_name: str
    status: str
    model_config = {"from_attributes": True}

@router.post("", response_model=FarmerOut, status_code=201)
def create_farmer(payload: FarmerCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if db.scalar(select(Farmer).where(Farmer.user_id == user.id)):
        raise HTTPException(status_code=409, detail="FARMER_PROFILE_ALREADY_EXISTS")
    farmer = Farmer(user_id=user.id, farmer_ref=f"AGR-P-{uuid.uuid4().hex[:8].upper()}", display_name=payload.display_name)
    db.add(farmer); db.flush()
    db.add(AuditLog(actor_user_id=user.id, action="FARMER_CREATED", entity_type="FARMER",
                    entity_id=str(farmer.id), request_id=request.state.request_id))
    db.commit(); db.refresh(farmer)
    return farmer
