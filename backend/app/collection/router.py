import uuid
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException,Header
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user,require_roles
from app.core.idempotency_service import begin_idempotent,complete_idempotent
from app.database.models import CollectionEvent,DomainEvent,Farmer,OrderAllocation,QualityCheck,User
from app.database.session import get_db

router=APIRouter(prefix="/collection",tags=["Collection"])

class CollectionCreate(BaseModel):
    order_allocation_id:uuid.UUID
    received_quantity_kg:Decimal=Field(gt=0)
    location_name:str|None=None

@router.post("",status_code=201)
def collect(p:CollectionCreate,db:Session=Depends(get_db),user:User=Depends(require_roles("COLLECTION_AGENT","OPERATIONS_MANAGER","ADMIN")),
            idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,"/collection",idempotency_key,p.model_dump(mode="json"))
    if idem.response_body is not None:return idem.response_body
    allocation=db.scalar(select(OrderAllocation).where(OrderAllocation.id==p.order_allocation_id).with_for_update())
    if not allocation:raise HTTPException(status_code=404,detail="ORDER_ALLOCATION_NOT_FOUND")
    already=db.scalar(select(func.coalesce(func.sum(CollectionEvent.received_quantity_kg),0)).where(
        CollectionEvent.order_allocation_id==allocation.id))
    if Decimal(already)+p.received_quantity_kg>Decimal(allocation.quantity_kg):
        raise HTTPException(status_code=409,detail="COLLECTION_EXCEEDS_ALLOCATION")
    c=CollectionEvent(collection_ref=f"COL-{uuid.uuid4().hex[:10].upper()}",order_id=allocation.order_id,
        order_allocation_id=allocation.id,farmer_id=allocation.farmer_id,
        received_quantity_kg=p.received_quantity_kg,
        location_name=p.location_name or "AGRI-CI collection point")
    db.add(c);db.flush()
    db.add(DomainEvent(event_type="COLLECTION_RECORDED",aggregate_type="ORDER",aggregate_id=str(allocation.order_id),
        payload={"collection_ref":c.collection_ref,"received_kg":float(c.received_quantity_kg)}))
    db.flush()
    body={"collection_id":str(c.id),"collection_ref":c.collection_ref,
          "announced_quantity_kg":float(allocation.quantity_kg),"received_quantity_kg":float(c.received_quantity_kg)}
    return complete_idempotent(db,idem,201,body)

class QualityCreate(BaseModel):
    grade:str=Field(pattern="^[ABC]$")
    quantity_kg:Decimal=Field(gt=0)
    notes:str|None=None

@router.post("/{collection_id}/quality",status_code=201)
def quality(collection_id:uuid.UUID,p:QualityCreate,db:Session=Depends(get_db),user:User=Depends(require_roles("COLLECTION_AGENT","OPERATIONS_MANAGER","ADMIN")),
            idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,f"/collection/{collection_id}/quality",idempotency_key,
        {"collection_id":str(collection_id),**p.model_dump(mode="json")})
    if idem.response_body is not None:return idem.response_body
    c=db.scalar(select(CollectionEvent).where(CollectionEvent.id==collection_id).with_for_update())
    if not c:raise HTTPException(status_code=404,detail="COLLECTION_NOT_FOUND")
    graded=db.scalar(select(func.coalesce(func.sum(QualityCheck.quantity_kg),0)).where(
        QualityCheck.collection_event_id==c.id))
    if Decimal(graded)+p.quantity_kg>Decimal(c.received_quantity_kg):
        raise HTTPException(status_code=409,detail="QUALITY_QUANTITY_EXCEEDS_RECEIVED")
    q=QualityCheck(collection_event_id=c.id,grade=p.grade,quantity_kg=p.quantity_kg,notes=p.notes)
    db.add(q);db.flush()
    body={"quality_check_id":str(q.id),"grade":q.grade,"quantity_kg":float(q.quantity_kg)}
    return complete_idempotent(db,idem,201,body)

@router.get("/my-allocations")
def my_allocations(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    from app.database.models import Order,OrderAllocation,Product
    farmer=db.scalar(select(Farmer).where(Farmer.user_id==user.id))
    if not farmer:raise HTTPException(status_code=400,detail="FARMER_PROFILE_REQUIRED")
    rows=db.execute(select(OrderAllocation,Order,Product)
        .join(Order,OrderAllocation.order_id==Order.id).join(Product,Order.product_id==Product.id)
        .where(OrderAllocation.farmer_id==farmer.id).order_by(Order.created_at.desc())).all()
    out=[]
    for a,o,p in rows:
        collected=sum(float(x) for x in db.scalars(select(CollectionEvent.received_quantity_kg)
          .where(CollectionEvent.order_allocation_id==a.id)).all())
        out.append({"allocation_id":str(a.id),"order_ref":o.order_ref,"product_name":p.name_fr,
          "allocated_quantity_kg":float(a.quantity_kg),"collected_quantity_kg":collected,
          "remaining_quantity_kg":float(a.quantity_kg)-collected,"status":a.status})
    return out

@router.get("/pending")
def pending_collection_allocations(db:Session=Depends(get_db),user:User=Depends(require_roles("COLLECTION_AGENT","OPERATIONS_MANAGER","ADMIN"))):
    from app.database.models import Order,Product
    rows=db.execute(select(OrderAllocation,Order,Product,Farmer)
        .join(Order,OrderAllocation.order_id==Order.id).join(Product,Order.product_id==Product.id)
        .join(Farmer,OrderAllocation.farmer_id==Farmer.id).order_by(Order.created_at.desc())).all()
    out=[]
    for a,o,p,f in rows:
        collected=db.scalar(select(func.coalesce(func.sum(CollectionEvent.received_quantity_kg),0))
          .where(CollectionEvent.order_allocation_id==a.id))
        remaining=Decimal(a.quantity_kg)-Decimal(collected)
        if remaining<=0:continue
        out.append({"allocation_id":str(a.id),"order_id":str(o.id),"order_ref":o.order_ref,
          "product_name":p.name_fr,"farmer_name":f.display_name,"allocated_quantity_kg":float(a.quantity_kg),
          "collected_quantity_kg":float(collected),"remaining_quantity_kg":float(remaining)})
    return out

@router.get("/operations")
def collection_operations(db:Session=Depends(get_db),user:User=Depends(require_roles("COLLECTION_AGENT","OPERATIONS_MANAGER","ADMIN"))):
    from app.database.models import Order,Product
    rows=db.execute(select(CollectionEvent,Order,Product)
        .join(Order,CollectionEvent.order_id==Order.id).join(Product,Order.product_id==Product.id)
        .order_by(CollectionEvent.collected_at.desc())).all()
    out=[]
    for c,o,p in rows:
        graded=db.scalar(select(func.coalesce(func.sum(QualityCheck.quantity_kg),0))
          .where(QualityCheck.collection_event_id==c.id))
        checks=db.scalars(select(QualityCheck).where(QualityCheck.collection_event_id==c.id)
          .order_by(QualityCheck.checked_at)).all()
        out.append({"collection_id":str(c.id),"collection_ref":c.collection_ref,"order_id":str(o.id),
          "order_ref":o.order_ref,"product_name":p.name_fr,"received_quantity_kg":float(c.received_quantity_kg),
          "graded_quantity_kg":float(graded),"remaining_to_grade_kg":float(c.received_quantity_kg)-float(graded),
          "location_name":c.location_name,"quality_checks":[{"id":str(q.id),"grade":q.grade,
          "quantity_kg":float(q.quantity_kg)} for q in checks]})
    return out
