import uuid
from datetime import datetime,timedelta,timezone
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import Aggregation,AggregationMember,Commitment,Demand,DomainEvent,Match,Offer

def _event(db,event_type,aggregate_type,aggregate_id,payload):
    db.add(DomainEvent(event_type=event_type,aggregate_type=aggregate_type,
        aggregate_id=str(aggregate_id),payload=payload))

def propose_from_matches(db:Session,demand:Demand)->Aggregation:
    existing=db.scalar(select(Aggregation).where(Aggregation.demand_id==demand.id,
        Aggregation.status.in_(["PROPOSING","AWAITING_COMMITMENTS","PARTIALLY_CONFIRMED","CONFIRMED"])))
    if existing: return existing

    agg=Aggregation(aggregation_ref=f"AGG-{uuid.uuid4().hex[:10].upper()}",
        demand_id=demand.id,target_quantity_kg=demand.quantity_required_kg,
        proposed_quantity_kg=0,accepted_quantity_kg=0,status="PROPOSING")
    db.add(agg); db.flush()

    matches=db.scalars(select(Match).where(Match.demand_id==demand.id).order_by(Match.total_score.desc())).all()
    remaining=Decimal(demand.quantity_required_kg)
    for match in matches:
        if remaining<=0: break
        offer=db.scalar(select(Offer).where(Offer.id==match.offer_id).with_for_update())
        if not offer or offer.status!="ACTIVE" or offer.quantity_available_kg<=0: continue
        qty=min(Decimal(offer.quantity_available_kg),remaining)
        offer.quantity_available_kg-=qty
        offer.quantity_proposed_kg+=qty
        offer.version+=1
        member=AggregationMember(aggregation_id=agg.id,offer_id=offer.id,
            proposed_quantity_kg=qty,accepted_quantity_kg=0,status="PROPOSED")
        db.add(member);db.flush()
        commitment=Commitment(commitment_ref=f"COM-{uuid.uuid4().hex[:10].upper()}",
            aggregation_id=agg.id,aggregation_member_id=member.id,offer_id=offer.id,
            farmer_id=offer.farmer_id,quantity_kg=qty,status="PENDING",
            expires_at=datetime.now(timezone.utc)+timedelta(hours=24))
        db.add(commitment)
        agg.proposed_quantity_kg+=qty
        remaining-=qty

    agg.status="AWAITING_COMMITMENTS" if agg.proposed_quantity_kg>0 else "INSUFFICIENT_SUPPLY"
    _event(db,"AGGREGATION_PROPOSED","AGGREGATION",agg.id,
           {"target_kg":float(agg.target_quantity_kg),"proposed_kg":float(agg.proposed_quantity_kg)})
    db.commit();db.refresh(agg)
    return agg

def refill_declined_quantity(db:Session,agg:Aggregation,excluded_offer_ids:set|None=None)->Decimal:
    excluded_offer_ids=excluded_offer_ids or set()
    missing=Decimal(agg.target_quantity_kg)-Decimal(agg.proposed_quantity_kg)
    if missing<=0:return Decimal("0")
    matches=db.scalars(select(Match).where(Match.demand_id==agg.demand_id).order_by(Match.total_score.desc())).all()
    added=Decimal("0")
    for match in matches:
        if missing<=0:break
        if match.offer_id in excluded_offer_ids:continue
        offer=db.scalar(select(Offer).where(Offer.id==match.offer_id).with_for_update())
        if not offer or offer.status!="ACTIVE" or offer.quantity_available_kg<=0:continue
        qty=min(Decimal(offer.quantity_available_kg),missing)
        offer.quantity_available_kg-=qty;offer.quantity_proposed_kg+=qty;offer.version+=1
        member=AggregationMember(aggregation_id=agg.id,offer_id=offer.id,proposed_quantity_kg=qty,
                                 accepted_quantity_kg=0,status="PROPOSED")
        db.add(member);db.flush()
        db.add(Commitment(commitment_ref=f"COM-{uuid.uuid4().hex[:10].upper()}",
            aggregation_id=agg.id,aggregation_member_id=member.id,offer_id=offer.id,
            farmer_id=offer.farmer_id,quantity_kg=qty,status="PENDING",
            expires_at=datetime.now(timezone.utc)+timedelta(hours=24)))
        agg.proposed_quantity_kg+=qty;added+=qty;missing-=qty
    _event(db,"AGGREGATION_REFILLED","AGGREGATION",agg.id,{"added_kg":float(added)})
    return added
