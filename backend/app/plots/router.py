import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.models import Farm, Farmer, Plot, User
from app.database.session import get_db

router = APIRouter(prefix="/plots", tags=["Plots"])

class PlotCreate(BaseModel):
    farm_id: uuid.UUID
    plot_ref: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=150)
    area_ha: Decimal = Field(gt=0)

class PlotOut(PlotCreate):
    id: uuid.UUID
    model_config = {"from_attributes": True}

@router.post("", response_model=PlotOut, status_code=201)
def create_plot(payload: PlotCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    farmer = db.scalar(select(Farmer).where(Farmer.user_id == user.id))
    farm = db.scalar(select(Farm).where(Farm.id == payload.farm_id))
    if not farmer or not farm or farm.farmer_id != farmer.id:
        raise HTTPException(status_code=403, detail="FARM_NOT_OWNED")
    plot = Plot(**payload.model_dump())
    db.add(plot); db.commit(); db.refresh(plot)
    return plot


@router.get("", response_model=list[PlotOut])
def list_my_plots(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    farmer = db.scalar(select(Farmer).where(Farmer.user_id == user.id))
    if not farmer: raise HTTPException(status_code=400, detail="FARMER_PROFILE_REQUIRED")
    return list(db.scalars(select(Plot).join(Farm, Plot.farm_id == Farm.id)
        .where(Farm.farmer_id == farmer.id).order_by(Plot.name)).all())
