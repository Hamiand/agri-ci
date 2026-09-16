import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.models import Farmer, Harvest, Offer, User
from app.database.session import get_db

router = APIRouter(prefix="/offers", tags=["Offers"])

class OfferCreate(BaseModel):
    harvest_id: uuid.UUID
    quantity_kg: Decimal = Field(gt=0)
    asking_price_xof_per_kg: Decimal | None = Field(default=None, gt=0)
    quality_grade: str | None = None

class OfferOut(BaseModel):
    id: uuid.UUID
    offer_ref: str
    quantity_total_kg: Decimal
    quantity_available_kg: Decimal
    quantity_proposed_kg: Decimal
    quantity_reserved_kg: Decimal
    quantity_sold_kg: Decimal
    status: str
    version: int
    model_config = {"from_attributes": True}

@router.post("", response_model=OfferOut, status_code=201)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    farmer = db.scalar(select(Farmer).where(Farmer.user_id == user.id))
    harvest = db.scalar(select(Harvest).where(Harvest.id == payload.harvest_id))
    if not farmer or not harvest or harvest.farmer_id != farmer.id:
        raise HTTPException(status_code=403, detail="HARVEST_NOT_OWNED")
    already_offered = db.scalar(select(func.coalesce(func.sum(Offer.quantity_total_kg), 0)).where(
        Offer.harvest_id == harvest.id, Offer.status != "CANCELLED"))
    remaining = harvest.estimated_quantity_kg - already_offered
    if payload.quantity_kg > remaining:
        raise HTTPException(status_code=409, detail="OFFER_EXCEEDS_HARVEST_AVAILABLE_QUANTITY")
    offer = Offer(offer_ref=f"OFF-{uuid.uuid4().hex[:10].upper()}", harvest_id=harvest.id,
        farmer_id=farmer.id, product_id=harvest.product_id, quantity_total_kg=payload.quantity_kg,
        quantity_available_kg=payload.quantity_kg, quantity_proposed_kg=0, quantity_reserved_kg=0,
        quantity_sold_kg=0, asking_price_xof_per_kg=payload.asking_price_xof_per_kg,
        quality_grade=payload.quality_grade, status="ACTIVE")
    db.add(offer); db.commit(); db.refresh(offer)
    return offer
