import uuid
from datetime import datetime,timezone
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException,Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user,require_roles
from app.core.idempotency_service import begin_idempotent,complete_idempotent
from app.database.models import CollectionEvent,DomainEvent,Lot,LotSource,Order,QualityCheck,TransportJob,TransportJobLot,User
from app.database.session import get_db

router=APIRouter(tags=["Logistics"])

class LotCreate(BaseModel):
    order_id:uuid.UUID
    quality_check_ids:list[uuid.UUID]

@router.post("/lots",status_code=201)
def create_lot(p:LotCreate,db:Session=Depends(get_db),user:User=Depends(require_roles("TRANSPORTER","OPERATIONS_MANAGER","ADMIN")),
               idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,"/lots",idempotency_key,p.model_dump(mode="json"))
    if idem.response_body is not None:return idem.response_body
    order=db.get(Order,p.order_id)
    if not order:raise HTTPException(status_code=404,detail="ORDER_NOT_FOUND")
    checks=[db.get(QualityCheck,x) for x in p.quality_check_ids]
    if not checks or any(x is None for x in checks):raise HTTPException(status_code=404,detail="QUALITY_CHECK_NOT_FOUND")
    collection_ids={x.collection_event_id for x in checks}
    collections=[db.get(CollectionEvent,x) for x in collection_ids]
    if any(c is None or c.order_id!=order.id for c in collections):
        raise HTTPException(status_code=409,detail="QUALITY_CHECK_NOT_FROM_ORDER")
    already_used=set(db.scalars(select(LotSource.quality_check_id).where(LotSource.quality_check_id.in_(p.quality_check_ids))).all())
    if already_used:raise HTTPException(status_code=409,detail="QUALITY_CHECK_ALREADY_LOTTED")
    grades={x.grade for x in checks}
    if len(grades)!=1:raise HTTPException(status_code=409,detail="LOT_MUST_HAVE_SINGLE_GRADE")
    qty=sum((Decimal(x.quantity_kg) for x in checks),Decimal("0"))
    lot=Lot(lot_ref=f"LOT-{uuid.uuid4().hex[:10].upper()}",order_id=order.id,product_id=order.product_id,
            grade=checks[0].grade,quantity_kg=qty,status="READY")
    db.add(lot);db.flush()
    for q in checks:db.add(LotSource(lot_id=lot.id,quality_check_id=q.id,quantity_kg=q.quantity_kg))
    db.flush()
    body={"lot_id":str(lot.id),"lot_ref":lot.lot_ref,"grade":lot.grade,"quantity_kg":float(lot.quantity_kg)}
    return complete_idempotent(db,idem,201,body)

class TransportCreate(BaseModel):
    order_id:uuid.UUID
    lot_ids:list[uuid.UUID]
    origin:str
    destination:str
    vehicle_ref:str|None=None
    driver_name:str|None=None

@router.post("/transport-jobs",status_code=201)
def create_transport(p:TransportCreate,db:Session=Depends(get_db),user:User=Depends(require_roles("TRANSPORTER","OPERATIONS_MANAGER","ADMIN")),
                     idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,"/transport-jobs",idempotency_key,p.model_dump(mode="json"))
    if idem.response_body is not None:return idem.response_body
    order=db.get(Order,p.order_id)
    if not order:raise HTTPException(status_code=404,detail="ORDER_NOT_FOUND")
    lots=[db.scalar(select(Lot).where(Lot.id==x).with_for_update()) for x in p.lot_ids]
    if not lots or any(x is None or x.order_id!=order.id or x.status!="READY" for x in lots):
        raise HTTPException(status_code=409,detail="INVALID_LOT_FOR_ORDER")
    assigned=set(db.scalars(select(TransportJobLot.lot_id).where(TransportJobLot.lot_id.in_(p.lot_ids))).all())
    if assigned:raise HTTPException(status_code=409,detail="LOT_ALREADY_ASSIGNED")
    job=TransportJob(transport_ref=f"TRN-{uuid.uuid4().hex[:10].upper()}",order_id=order.id,
        origin=p.origin,destination=p.destination,vehicle_ref=p.vehicle_ref,driver_name=p.driver_name,status="PLANNED")
    db.add(job);db.flush()
    for lot in lots:
        db.add(TransportJobLot(transport_job_id=job.id,lot_id=lot.id))
        lot.status="ASSIGNED"
    db.flush()
    body={"transport_job_id":str(job.id),"transport_ref":job.transport_ref,"status":job.status}
    return complete_idempotent(db,idem,201,body)

@router.post("/transport-jobs/{job_id}/depart")
def depart(job_id:uuid.UUID,db:Session=Depends(get_db),user:User=Depends(require_roles("TRANSPORTER","OPERATIONS_MANAGER","ADMIN")),
           idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,f"/transport-jobs/{job_id}/depart",idempotency_key,{"job_id":str(job_id)})
    if idem.response_body is not None:return idem.response_body
    job=db.get(TransportJob,job_id)
    if not job:raise HTTPException(status_code=404,detail="TRANSPORT_JOB_NOT_FOUND")
    if job.status!="PLANNED":raise HTTPException(status_code=409,detail="INVALID_TRANSPORT_STATE")
    job.status="IN_TRANSIT";job.departed_at=datetime.now(timezone.utc)
    lot_ids=list(db.scalars(select(TransportJobLot.lot_id).where(TransportJobLot.transport_job_id==job.id)).all())
    for lot in db.scalars(select(Lot).where(Lot.id.in_(lot_ids)).with_for_update()).all():lot.status="IN_TRANSIT"
    body={"transport_ref":job.transport_ref,"status":job.status}
    return complete_idempotent(db,idem,200,body)

# Pilot security boundary: until TransportJob carries an explicit transporter/user assignment,
# global operational listings are restricted to central operations. A TRANSPORTER must not be
# able to enumerate every lot or every transport job nationally merely because of the role.
@router.get("/lots")
def list_lots(order_id:uuid.UUID|None=None,db:Session=Depends(get_db),user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN"))):
    q=select(Lot).order_by(Lot.created_at.desc())
    if order_id:q=q.where(Lot.order_id==order_id)
    rows=db.scalars(q).all()
    return [{"id":str(x.id),"lot_ref":x.lot_ref,"order_id":str(x.order_id),"grade":x.grade,
      "quantity_kg":float(x.quantity_kg),"status":x.status} for x in rows]

@router.get("/transport-jobs")
def list_transport_jobs(order_id:uuid.UUID|None=None,db:Session=Depends(get_db),user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN"))):
    q=select(TransportJob).order_by(TransportJob.created_at.desc())
    if order_id:q=q.where(TransportJob.order_id==order_id)
    rows=db.scalars(q).all()
    return [{"id":str(x.id),"transport_ref":x.transport_ref,"order_id":str(x.order_id),
      "origin":x.origin,"destination":x.destination,"vehicle_ref":x.vehicle_ref,
      "driver_name":x.driver_name,"status":x.status} for x in rows]
