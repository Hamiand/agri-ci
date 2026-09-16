import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.models import Farmer, Harvest, HarvestForecast, Plot, Product, User
from app.database.session import get_db

router = APIRouter(prefix="/harvests", tags=["Future Harvests"])

class HarvestCreate(BaseModel):
    plot_id: uuid.UUID
    product_code: str
    expected_start_date: date
    expected_end_date: date
    estimated_quantity_kg: Decimal = Field(gt=0)
    @model_validator(mode="after")
    def dates_valid(self):
        if self.expected_end_date < self.expected_start_date:
            raise ValueError("expected_end_date must be on or after expected_start_date")
        return self

class HarvestOut(BaseModel):
    id: uuid.UUID
    harvest_ref: str
    estimated_quantity_kg: Decimal
    expected_start_date: date
    expected_end_date: date
    status: str
    version: int
    model_config = {"from_attributes": True}

@router.post("", response_model=HarvestOut, status_code=201)
def create_harvest(payload: HarvestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    farmer = db.scalar(select(Farmer).where(Farmer.user_id == user.id))
    plot = db.scalar(select(Plot).where(Plot.id == payload.plot_id))
    product = db.scalar(select(Product).where(Product.code == payload.product_code, Product.active.is_(True)))
    if not farmer: raise HTTPException(status_code=400, detail="FARMER_PROFILE_REQUIRED")
    if not plot: raise HTTPException(status_code=404, detail="PLOT_NOT_FOUND")
    if plot.farm.farmer_id != farmer.id: raise HTTPException(status_code=403, detail="PLOT_NOT_OWNED")
    if not product: raise HTTPException(status_code=404, detail="PRODUCT_NOT_FOUND")
    harvest = Harvest(harvest_ref=f"HAR-{uuid.uuid4().hex[:10].upper()}", farmer_id=farmer.id,
        plot_id=plot.id, product_id=product.id, expected_start_date=payload.expected_start_date,
        expected_end_date=payload.expected_end_date, estimated_quantity_kg=payload.estimated_quantity_kg)
    db.add(harvest); db.flush()
    db.add(HarvestForecast(harvest_id=harvest.id, revision_no=1,
        estimated_quantity_kg=harvest.estimated_quantity_kg, expected_start_date=harvest.expected_start_date,
        expected_end_date=harvest.expected_end_date))
    db.commit(); db.refresh(harvest)
    return harvest


@router.get("", response_model=list[HarvestOut])
def list_my_harvests(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    farmer = db.scalar(select(Farmer).where(Farmer.user_id == user.id))
    if not farmer: raise HTTPException(status_code=400, detail="FARMER_PROFILE_REQUIRED")
    return list(db.scalars(select(Harvest).where(Harvest.farmer_id == farmer.id)
        .order_by(Harvest.expected_start_date.desc())).all())
