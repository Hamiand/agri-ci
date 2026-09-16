import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.aggregation.service import refill_declined_quantity
from app.core.dependencies import get_current_user
from app.core.idempotency_service import begin_idempotent, complete_idempotent
from app.core.object_auth import farmer_for_user
from app.database.models import Aggregation, AggregationMember, Commitment, DomainEvent, Farmer, Offer, User
from app.database.session import get_db

router = APIRouter(prefix="/commitments", tags=["Commitments"])


def owned_commitment(db, user, commitment_id):
    farmer = farmer_for_user(db, user)
    commitment = db.scalar(
        select(Commitment).where(Commitment.id == commitment_id).with_for_update()
    )
    if not commitment:
        raise HTTPException(status_code=404, detail="COMMITMENT_NOT_FOUND")
    if not farmer or commitment.farmer_id != farmer.id:
        raise HTTPException(status_code=403, detail="COMMITMENT_NOT_OWNED")
    if commitment.status != "PENDING":
        raise HTTPException(status_code=409, detail="COMMITMENT_ALREADY_RESOLVED")
    if commitment.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=409, detail="COMMITMENT_EXPIRED")
    return commitment


@router.post("/{commitment_id}/accept")
def accept(commitment_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user),
           idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    idem = begin_idempotent(db, user, f"/commitments/{commitment_id}/accept", idempotency_key,
                            {"commitment_id": str(commitment_id), "action": "accept"})
    if idem.response_body is not None:
        return idem.response_body
    c = owned_commitment(db, user, commitment_id)
    offer = db.scalar(select(Offer).where(Offer.id == c.offer_id).with_for_update())
    member = db.get(AggregationMember, c.aggregation_member_id)
    agg = db.scalar(select(Aggregation).where(Aggregation.id == c.aggregation_id).with_for_update())
    if offer.quantity_proposed_kg < c.quantity_kg:
        raise HTTPException(status_code=409, detail="QUANTITY_CONFLICT")
    offer.quantity_proposed_kg -= c.quantity_kg
    offer.quantity_reserved_kg += c.quantity_kg
    offer.version += 1
    c.status = "ACCEPTED"
    c.responded_at = datetime.now(timezone.utc)
    member.status = "ACCEPTED"
    member.accepted_quantity_kg = c.quantity_kg
    agg.accepted_quantity_kg += c.quantity_kg
    agg.status = "CONFIRMED" if agg.accepted_quantity_kg >= agg.target_quantity_kg else "PARTIALLY_CONFIRMED"
    db.add(DomainEvent(event_type="COMMITMENT_ACCEPTED", aggregate_type="AGGREGATION",
                       aggregate_id=str(agg.id), payload={"commitment_id": str(c.id), "quantity_kg": float(c.quantity_kg)}))
    body = {"commitment_id": str(c.id), "status": "ACCEPTED", "aggregation_status": agg.status,
            "accepted_quantity_kg": float(agg.accepted_quantity_kg)}
    return complete_idempotent(db, idem, 200, body)


@router.post("/{commitment_id}/decline")
def decline(commitment_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user),
            idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    idem = begin_idempotent(db, user, f"/commitments/{commitment_id}/decline", idempotency_key,
                            {"commitment_id": str(commitment_id), "action": "decline"})
    if idem.response_body is not None:
        return idem.response_body
    c = owned_commitment(db, user, commitment_id)
    offer = db.scalar(select(Offer).where(Offer.id == c.offer_id).with_for_update())
    member = db.get(AggregationMember, c.aggregation_member_id)
    agg = db.scalar(select(Aggregation).where(Aggregation.id == c.aggregation_id).with_for_update())
    if offer.quantity_proposed_kg < c.quantity_kg:
        raise HTTPException(status_code=409, detail="QUANTITY_CONFLICT")
    offer.quantity_proposed_kg -= c.quantity_kg
    offer.quantity_available_kg += c.quantity_kg
    offer.version += 1
    c.status = "DECLINED"
    c.responded_at = datetime.now(timezone.utc)
    member.status = "DECLINED"
    agg.proposed_quantity_kg -= c.quantity_kg
    added = refill_declined_quantity(db, agg, {c.offer_id})
    agg.status = "AWAITING_COMMITMENTS"
    db.add(DomainEvent(event_type="COMMITMENT_DECLINED", aggregate_type="AGGREGATION",
                       aggregate_id=str(agg.id), payload={"commitment_id": str(c.id),
                                                         "returned_kg": float(c.quantity_kg),
                                                         "replacement_proposed_kg": float(added)}))
    body = {"commitment_id": str(c.id), "status": "DECLINED",
            "returned_to_available_kg": float(c.quantity_kg),
            "replacement_proposed_kg": float(added), "aggregation_status": agg.status}
    return complete_idempotent(db, idem, 200, body)


@router.get("")
def my_commitments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from app.database.models import Demand, Product
    farmer = farmer_for_user(db, user)
    if not farmer:
        raise HTTPException(status_code=400, detail="FARMER_PROFILE_REQUIRED")
    rows = db.execute(
        select(Commitment, Aggregation, Demand, Offer, Product)
        .join(Aggregation, Commitment.aggregation_id == Aggregation.id)
        .join(Demand, Aggregation.demand_id == Demand.id)
        .join(Offer, Commitment.offer_id == Offer.id)
        .join(Product, Demand.product_id == Product.id)
        .where(Commitment.farmer_id == farmer.id)
        .order_by(Commitment.created_at.desc())
    ).all()
    return [{"id": str(c.id), "commitment_ref": c.commitment_ref, "quantity_kg": float(c.quantity_kg),
             "status": c.status, "expires_at": c.expires_at.isoformat(), "aggregation_ref": a.aggregation_ref,
             "demand_ref": d.demand_ref, "product_name": p.name_fr, "destination_city": d.destination_city,
             "target_price_xof_per_kg": float(d.target_price_xof_per_kg) if d.target_price_xof_per_kg else None,
             "asking_price_xof_per_kg": float(o.asking_price_xof_per_kg) if o.asking_price_xof_per_kg else None}
            for c, a, d, o, p in rows]
