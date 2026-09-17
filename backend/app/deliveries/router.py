import uuid
from datetime import datetime,timezone
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException,Header
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user,require_roles
from app.core.idempotency_service import begin_idempotent,complete_idempotent
from app.database.models import Delivery,DomainEvent,Order,TransportJob,TransportJobLot,Lot,User
from app.database.session import get_db

router=APIRouter(prefix="/deliveries",tags=["Deliveries"])

class DeliveryCreate(BaseModel):
    transport_job_id:uuid.UUID
    delivered_quantity_kg:Decimal=Field(gt=0)
    received_by:str=Field(min_length=1,max_length=200)

@router.post("",status_code=201)
def deliver(p:DeliveryCreate,db:Session=Depends(get_db),user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN")),
            idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    receiver=p.received_by.strip()
    if not receiver:raise HTTPException(status_code=422,detail="DELIVERY_RECEIVER_REQUIRED")
    idem=begin_idempotent(db,user,"/deliveries",idempotency_key,p.model_dump(mode="json"))
    if idem.response_body is not None:return idem.response_body
    job=db.scalar(select(TransportJob).where(TransportJob.id==p.transport_job_id).with_for_update())
    if not job:raise HTTPException(status_code=404,detail="TRANSPORT_JOB_NOT_FOUND")
    if job.status!="IN_TRANSIT":raise HTTPException(status_code=409,detail="TRANSPORT_NOT_IN_TRANSIT")
    lot_ids=list(db.scalars(select(TransportJobLot.lot_id).where(TransportJobLot.transport_job_id==job.id)).all())
    capacity=db.scalar(select(func.coalesce(func.sum(Lot.quantity_kg),0)).where(Lot.id.in_(lot_ids)))
    already=db.scalar(select(func.coalesce(func.sum(Delivery.delivered_quantity_kg),0)).where(Delivery.transport_job_id==job.id))
    if Decimal(already)+p.delivered_quantity_kg>Decimal(capacity):
        raise HTTPException(status_code=409,detail="DELIVERY_EXCEEDS_TRANSPORTED_QUANTITY")
    d=Delivery(delivery_ref=f"DEL-{uuid.uuid4().hex[:10].upper()}",order_id=job.order_id,
        transport_job_id=job.id,delivered_quantity_kg=p.delivered_quantity_kg,
        received_by=receiver,status="DELIVERED")
    db.add(d)
    if Decimal(already)+p.delivered_quantity_kg==Decimal(capacity):
        job.status="DELIVERED";job.arrived_at=datetime.now(timezone.utc)
        for lot in db.scalars(select(Lot).where(Lot.id.in_(lot_ids)).with_for_update()).all():lot.status="DELIVERED"
    db.add(DomainEvent(event_type="DELIVERY_RECORDED",aggregate_type="ORDER",aggregate_id=str(job.order_id),
        payload={"delivery_ref":d.delivery_ref,"delivered_kg":float(d.delivered_quantity_kg)}))
    db.flush()
    body={"delivery_id":str(d.id),"delivery_ref":d.delivery_ref,
          "delivered_quantity_kg":float(d.delivered_quantity_kg),"transport_status":job.status}
    return complete_idempotent(db,idem,201,body)
