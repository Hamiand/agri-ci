import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import Offer

class InsufficientOfferQuantity(Exception): pass

def reserve_available_quantity(db:Session,offer_id:uuid.UUID,quantity_kg:Decimal)->Offer:
    """
    Atomic quantity reservation primitive.
    PostgreSQL SELECT ... FOR UPDATE serializes concurrent consumers of one Offer row.
    Caller owns commit/rollback.
    """
    if quantity_kg<=0: raise ValueError("quantity_kg must be positive")
    offer=db.scalar(select(Offer).where(Offer.id==offer_id).with_for_update())
    if offer is None: raise LookupError("offer not found")
    available=Decimal(offer.quantity_available_kg)
    if available<quantity_kg: raise InsufficientOfferQuantity(
        f"requested={quantity_kg} available={available}")
    offer.quantity_available_kg=available-quantity_kg
    offer.quantity_reserved_kg=Decimal(offer.quantity_reserved_kg)+quantity_kg
    offer.version+=1
    db.flush()
    return offer
