import uuid
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import (Aggregation,AggregationMember,Buyer,Demand,DomainEvent,
                                 Offer,Order,OrderAllocation)

def order_gate_open(accepted:Decimal,target:Decimal)->bool:
    return accepted >= target and target > 0

def create_order_from_aggregation(db:Session,aggregation_id):
    agg=db.scalar(select(Aggregation).where(Aggregation.id==aggregation_id).with_for_update())
    if not agg: raise HTTPException(status_code=404,detail="AGGREGATION_NOT_FOUND")
    existing=db.scalar(select(Order).where(Order.aggregation_id==agg.id))
    if existing:return existing
    if not order_gate_open(Decimal(agg.accepted_quantity_kg),Decimal(agg.target_quantity_kg)):
        raise HTTPException(status_code=409,detail="ORDER_GATE_NOT_READY")
    demand=db.get(Demand,agg.demand_id)
    members=db.scalars(select(AggregationMember).where(
        AggregationMember.aggregation_id==agg.id,AggregationMember.status=="ACCEPTED")).all()
    total=sum((Decimal(m.accepted_quantity_kg) for m in members),Decimal("0"))
    if total < Decimal(agg.target_quantity_kg):
        raise HTTPException(status_code=409,detail="ALLOCATION_TOTAL_INSUFFICIENT")

    # If accepted supply ever exceeds target, allocate only the exact target.
    remaining=Decimal(agg.target_quantity_kg)
    order=Order(order_ref=f"ORD-{uuid.uuid4().hex[:10].upper()}",aggregation_id=agg.id,
        demand_id=demand.id,buyer_id=demand.buyer_id,product_id=demand.product_id,
        quantity_kg=agg.target_quantity_kg,status="CONFIRMED")
    db.add(order);db.flush()
    for m in members:
        if remaining<=0:break
        qty=min(Decimal(m.accepted_quantity_kg),remaining)
        offer=db.scalar(select(Offer).where(Offer.id==m.offer_id).with_for_update())
        if offer.quantity_reserved_kg < qty:
            raise HTTPException(status_code=409,detail="RESERVED_QUANTITY_CONFLICT")
        db.add(OrderAllocation(order_id=order.id,offer_id=offer.id,farmer_id=offer.farmer_id,
                               quantity_kg=qty,status="ALLOCATED"))
        remaining-=qty
    if remaining!=0:
        raise HTTPException(status_code=409,detail="ORDER_ALLOCATION_FAILED")
    agg.status="ORDERED"
    demand.status="CONFIRMED"
    db.add(DomainEvent(event_type="ORDER_CONFIRMED",aggregate_type="ORDER",aggregate_id=str(order.id),
        payload={"order_ref":order.order_ref,"quantity_kg":float(order.quantity_kg)}))
    # The HTTP boundary owns the commit. Keeping this service commit-free makes
    # order creation, allocations, stock checks and the persisted idempotency
    # response one atomic transaction in /orders/from-aggregation/{id}.
    db.flush()
    return order
