import uuid
from fastapi import APIRouter,Depends,HTTPException,Header
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.idempotency_service import begin_idempotent,complete_idempotent
from app.database.models import Aggregation,Buyer,Demand,Order,OrderAllocation,User
from app.database.session import get_db
from app.orders.service import create_order_from_aggregation

router=APIRouter(prefix="/orders",tags=["Orders"])


def _allocation_body(a:OrderAllocation):
    return {"id":str(a.id),"farmer_id":str(a.farmer_id),"offer_id":str(a.offer_id),
            "quantity_kg":float(a.quantity_kg),"status":a.status}

@router.post("/from-aggregation/{aggregation_id}",status_code=201)
def create_order(aggregation_id:uuid.UUID,db:Session=Depends(get_db),user:User=Depends(get_current_user),
                 idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,f"/orders/from-aggregation/{aggregation_id}",idempotency_key,
        {"aggregation_id":str(aggregation_id)})
    if idem.response_body is not None:return idem.response_body
    agg=db.get(Aggregation,aggregation_id)
    if not agg:raise HTTPException(status_code=404,detail="AGGREGATION_NOT_FOUND")
    demand=db.get(Demand,agg.demand_id)
    buyer=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    if not buyer or demand.buyer_id!=buyer.id:raise HTTPException(status_code=403,detail="DEMAND_NOT_OWNED")
    order=create_order_from_aggregation(db,aggregation_id)
    allocations=db.scalars(select(OrderAllocation).where(OrderAllocation.order_id==order.id)).all()
    body={"order_id":str(order.id),"order_ref":order.order_ref,"status":order.status,
          "quantity_kg":float(order.quantity_kg),"allocations":[_allocation_body(a) for a in allocations]}
    return complete_idempotent(db,idem,201,body)

@router.get("/{order_id}")
def get_order(order_id:uuid.UUID,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    order=db.get(Order,order_id)
    if not order:raise HTTPException(status_code=404,detail="ORDER_NOT_FOUND")
    buyer=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    if not buyer or order.buyer_id!=buyer.id:raise HTTPException(status_code=403,detail="ORDER_NOT_OWNED")
    allocations=db.scalars(select(OrderAllocation).where(OrderAllocation.order_id==order.id)).all()
    return {"order_id":str(order.id),"order_ref":order.order_ref,"status":order.status,
            "quantity_kg":float(order.quantity_kg),"allocations":[_allocation_body(a) for a in allocations]}

@router.get("")
def my_orders(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    from app.database.models import Buyer,Product
    buyer=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    if not buyer:raise HTTPException(status_code=400,detail="BUYER_PROFILE_REQUIRED")
    rows=db.execute(select(Order,Product).join(Product,Order.product_id==Product.id)
        .where(Order.buyer_id==buyer.id).order_by(Order.created_at.desc())).all()
    return [{"id":str(o.id),"order_ref":o.order_ref,"product_name":p.name_fr,
      "quantity_kg":float(o.quantity_kg),"status":o.status} for o,p in rows]

@router.get("/{order_id}/operations")
def order_operations(order_id:uuid.UUID,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    from app.database.models import Buyer,CollectionEvent,Delivery,Lot,TransportJob
    order=db.get(Order,order_id)
    if not order:raise HTTPException(status_code=404,detail="ORDER_NOT_FOUND")
    buyer=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    if not buyer or order.buyer_id!=buyer.id:raise HTTPException(status_code=403,detail="ORDER_ACCESS_DENIED")
    collections=list(db.scalars(select(CollectionEvent).where(CollectionEvent.order_id==order.id)).all())
    lots=list(db.scalars(select(Lot).where(Lot.order_id==order.id)).all())
    jobs=list(db.scalars(select(TransportJob).where(TransportJob.order_id==order.id)).all())
    deliveries=list(db.scalars(select(Delivery).where(Delivery.order_id==order.id)).all())
    return {"order_ref":order.order_ref,"quantity_kg":float(order.quantity_kg),"status":order.status,
      "collected_quantity_kg":sum(float(x.received_quantity_kg) for x in collections),
      "lots_quantity_kg":sum(float(x.quantity_kg) for x in lots),
      "transport_jobs":[{"transport_ref":x.transport_ref,"status":x.status,"origin":x.origin,
        "destination":x.destination} for x in jobs],
      "delivered_quantity_kg":sum(float(x.delivered_quantity_kg) for x in deliveries)}
