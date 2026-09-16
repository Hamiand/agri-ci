import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.models import Farm, Farmer, User
from app.database.session import get_db

router = APIRouter(prefix="/farms", tags=["Farms"])

class FarmCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    region: str | None = None
    department: str | None = None
    locality: str | None = None

class FarmOut(FarmCreate):
    id: uuid.UUID
    farmer_id: uuid.UUID
    model_config = {"from_attributes": True}

@router.post("", response_model=FarmOut, status_code=201)
def create_farm(payload: FarmCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    farmer = db.scalar(select(Farmer).where(Farmer.user_id == user.id))
    if not farmer: raise HTTPException(status_code=400, detail="FARMER_PROFILE_REQUIRED")
    farm = Farm(farmer_id=farmer.id, **payload.model_dump())
    db.add(farm); db.commit(); db.refresh(farm)
    return farm


@router.get("", response_model=list[FarmOut])
def list_my_farms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    farmer = db.scalar(select(Farmer).where(Farmer.user_id == user.id))
    if not farmer: raise HTTPException(status_code=400, detail="FARMER_PROFILE_REQUIRED")
    return list(db.scalars(select(Farm).where(Farm.farmer_id == farmer.id).order_by(Farm.name)).all())
