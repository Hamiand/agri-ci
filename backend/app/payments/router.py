import os
import uuid
from decimal import Decimal,ROUND_HALF_UP
from fastapi import APIRouter,Depends,HTTPException,Header
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user,require_roles
from app.core.idempotency_service import begin_idempotent,complete_idempotent
from app.database.models import (CollectionEvent,Delivery,Farmer,LedgerEntry,Lot,LotSource,Order,
    OrderAllocation,PaymentDeduction,PaymentIntent,QualityCheck,TransportJobLot,User)
from app.database.session import get_db
from app.payments.service import ALLOWED_DEDUCTIONS,add_ledger,compute_net,mark_provider_success

router=APIRouter(prefix="/payments",tags=["Payments"])
CENT=Decimal("0.01")

class DeductionIn(BaseModel):
    deduction_type:str
    description:str
    amount_xof:Decimal=Field(ge=0)

class PaymentCreate(BaseModel):
    order_id:uuid.UUID
    farmer_id:uuid.UUID
    gross_amount_xof:Decimal=Field(gt=0)
    deductions:list[DeductionIn]=Field(default_factory=list)
    provider:str=Field(min_length=2,max_length=50)

def _create_payment(db:Session,p:PaymentCreate):
    order=db.get(Order,p.order_id);farmer=db.get(Farmer,p.farmer_id)
    if not order:raise HTTPException(status_code=404,detail="ORDER_NOT_FOUND")
    if not farmer:raise HTTPException(status_code=404,detail="FARMER_NOT_FOUND")
    allocation=db.scalar(select(OrderAllocation).where(OrderAllocation.order_id==order.id,OrderAllocation.farmer_id==farmer.id))
    if not allocation:raise HTTPException(status_code=409,detail="FARMER_NOT_ALLOCATED_TO_ORDER")
    existing=db.scalar(select(PaymentIntent).where(PaymentIntent.order_id==order.id,PaymentIntent.farmer_id==farmer.id))
    if existing:return existing
    if any(d.deduction_type not in ALLOWED_DEDUCTIONS for d in p.deductions):raise HTTPException(status_code=422,detail="INVALID_DEDUCTION_TYPE")
    amounts=[d.amount_xof for d in p.deductions]
    try:net=compute_net(p.gross_amount_xof,amounts)
    except ValueError:raise HTTPException(status_code=422,detail="INVALID_PAYMENT_AMOUNTS")
    total=sum(amounts,Decimal("0"))
    pay=PaymentIntent(payment_ref=f"PAY-{uuid.uuid4().hex[:10].upper()}",order_id=order.id,farmer_id=farmer.id,gross_amount_xof=p.gross_amount_xof,deductions_xof=total,net_amount_xof=net,currency="XOF",provider=p.provider,status="PENDING")
    db.add(pay);db.flush();add_ledger(db,pay,"GROSS",p.gross_amount_xof,"Gross commercial amount")
    for d in p.deductions:
        db.add(PaymentDeduction(payment_intent_id=pay.id,deduction_type=d.deduction_type,description=d.description,amount_xof=d.amount_xof));add_ledger(db,pay,"DEDUCTION",d.amount_xof,f"{d.deduction_type}: {d.description}")
    add_ledger(db,pay,"NET_DUE",net,"Net amount due to farmer");return pay

@router.post("",status_code=201)
def create_payment(p:PaymentCreate,db:Session=Depends(get_db),user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN")),idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,"/payments",idempotency_key,p.model_dump(mode="json"))
    if idem.response_body is not None:return idem.response_body
    pay=_create_payment(db,p);db.flush();body={"payment_id":str(pay.id),"payment_ref":pay.payment_ref,"gross_amount_xof":float(pay.gross_amount_xof),"deductions_xof":float(pay.deductions_xof),"net_amount_xof":float(pay.net_amount_xof),"provider":pay.provider,"status":pay.status};return complete_idempotent(db,idem,201,body)

class SettlementPrepare(BaseModel):
    price_xof_per_kg:Decimal=Field(gt=0);transport_xof:Decimal=Field(default=0,ge=0);service_xof:Decimal=Field(default=0,ge=0);other_xof:Decimal=Field(default=0,ge=0);provider:str=Field(min_length=2,max_length=50)

def _attribute_delivery_sources(capacities,delivered,sources)->dict[uuid.UUID,Decimal]:
    result:dict[uuid.UUID,Decimal]={}
    for job_id,farmer_id,source_qty in sources:
        capacity=Decimal(capacities.get(job_id) or 0);delivered_qty=Decimal(delivered.get(job_id) or 0)
        if capacity<=0 or delivered_qty<=0:continue
        fraction=min(Decimal("1"),delivered_qty/capacity);attributable=(Decimal(source_qty)*fraction).quantize(Decimal("0.001"));result[farmer_id]=result.get(farmer_id,Decimal("0"))+attributable
    return result

def _allocate_money_exact(total:Decimal,weighted_items:list[tuple[uuid.UUID,Decimal]])->dict[uuid.UUID,Decimal]:
    """Proportionally allocate money while guaranteeing the rounded parts equal the rounded total."""
    target=Decimal(total).quantize(CENT,rounding=ROUND_HALF_UP)
    if not weighted_items:return {}
    weight_total=sum((Decimal(weight) for _,weight in weighted_items),Decimal("0"))
    if weight_total<=0:return {key:Decimal("0.00") for key,_ in weighted_items}
    ordered=sorted(weighted_items,key=lambda item:str(item[0]));result={};allocated=Decimal("0.00")
    for key,weight in ordered[:-1]:
        part=(target*Decimal(weight)/weight_total).quantize(CENT,rounding=ROUND_HALF_UP);result[key]=part;allocated+=part
    result[ordered[-1][0]]=(target-allocated).quantize(CENT);return result

def _delivered_quantity_by_farmer(db:Session,order_id:uuid.UUID)->dict[uuid.UUID,Decimal]:
    capacities=dict(db.execute(select(TransportJobLot.transport_job_id,func.sum(Lot.quantity_kg)).join(Lot,Lot.id==TransportJobLot.lot_id).where(Lot.order_id==order_id).group_by(TransportJobLot.transport_job_id)).all())
    delivered=dict(db.execute(select(Delivery.transport_job_id,func.sum(Delivery.delivered_quantity_kg)).where(Delivery.order_id==order_id,Delivery.status=="DELIVERED").group_by(Delivery.transport_job_id)).all())
    sources=db.execute(select(TransportJobLot.transport_job_id,OrderAllocation.farmer_id,LotSource.quantity_kg).join(Lot,Lot.id==TransportJobLot.lot_id).join(LotSource,LotSource.lot_id==Lot.id).join(QualityCheck,QualityCheck.id==LotSource.quality_check_id).join(CollectionEvent,CollectionEvent.id==QualityCheck.collection_event_id).join(OrderAllocation,OrderAllocation.id==CollectionEvent.order_allocation_id).where(Lot.order_id==order_id)).all()
    return _attribute_delivery_sources(capacities,delivered,sources)

@router.post("/orders/{order_id}/prepare")
def prepare_order_settlements(order_id:uuid.UUID,p:SettlementPrepare,db:Session=Depends(get_db),user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN")),idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,f"/payments/orders/{order_id}/prepare",idempotency_key,{"order_id":str(order_id),**p.model_dump(mode="json")})
    if idem.response_body is not None:return idem.response_body
    order=db.get(Order,order_id)
    if not order:raise HTTPException(status_code=404,detail="ORDER_NOT_FOUND")
    if not db.scalars(select(OrderAllocation).where(OrderAllocation.order_id==order.id)).all():raise HTTPException(status_code=409,detail="ORDER_HAS_NO_ALLOCATIONS")
    delivered_by_farmer=_delivered_quantity_by_farmer(db,order.id);prepared=[];total_delivered=sum(delivered_by_farmer.values(),Decimal("0"))
    if total_delivered<=0:raise HTTPException(status_code=409,detail="NO_DELIVERED_QUANTITY_TO_SETTLE")
    weights=list(delivered_by_farmer.items());transport_parts=_allocate_money_exact(p.transport_xof,weights);service_parts=_allocate_money_exact(p.service_xof,weights);other_parts=_allocate_money_exact(p.other_xof,weights)
    for farmer_id,delivered_qty in weights:
        gross=(delivered_qty*p.price_xof_per_kg).quantize(CENT,rounding=ROUND_HALF_UP)
        deductions=[DeductionIn(deduction_type="TRANSPORT",description="Transport AGRI-CI",amount_xof=transport_parts[farmer_id]),DeductionIn(deduction_type="AGRI_CI_SERVICE",description="Service AGRI-CI",amount_xof=service_parts[farmer_id]),DeductionIn(deduction_type="OTHER_AUTHORIZED",description="Other authorized cost",amount_xof=other_parts[farmer_id])]
        pay=_create_payment(db,PaymentCreate(order_id=order.id,farmer_id=farmer_id,gross_amount_xof=gross,deductions=deductions,provider=p.provider));prepared.append({"payment_ref":pay.payment_ref,"farmer_id":str(farmer_id),"delivered_quantity_kg":float(delivered_qty),"gross_amount_xof":float(pay.gross_amount_xof),"net_amount_xof":float(pay.net_amount_xof),"status":pay.status})
    return complete_idempotent(db,idem,200,{"order_id":str(order.id),"settlement_basis":"DELIVERED_QUANTITY","prepared":prepared})

@router.get("/farmer/me")
def farmer_payments(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    farmer=db.scalar(select(Farmer).where(Farmer.user_id==user.id))
    if not farmer:raise HTTPException(status_code=400,detail="FARMER_PROFILE_REQUIRED")
    rows=db.scalars(select(PaymentIntent).where(PaymentIntent.farmer_id==farmer.id).order_by(PaymentIntent.created_at.desc())).all();return [{"id":str(x.id),"payment_ref":x.payment_ref,"order_id":str(x.order_id),"gross_amount_xof":float(x.gross_amount_xof),"deductions_xof":float(x.deductions_xof),"net_amount_xof":float(x.net_amount_xof),"provider":x.provider,"status":x.status} for x in rows]

@router.get("")
def list_payments(order_id:uuid.UUID|None=None,db:Session=Depends(get_db),user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN"))):
    q=select(PaymentIntent).order_by(PaymentIntent.created_at.desc());q=q.where(PaymentIntent.order_id==order_id) if order_id else q;rows=db.scalars(q).all();return [{"id":str(x.id),"payment_ref":x.payment_ref,"order_id":str(x.order_id),"farmer_id":str(x.farmer_id),"gross_amount_xof":float(x.gross_amount_xof),"deductions_xof":float(x.deductions_xof),"net_amount_xof":float(x.net_amount_xof),"provider":x.provider,"status":x.status} for x in rows]

class ProviderSuccess(BaseModel):provider_reference:str

@router.post("/{payment_id}/provider-success")
def provider_success(payment_id:uuid.UUID,p:ProviderSuccess,db:Session=Depends(get_db),user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN")),idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    if os.getenv("APP_ENV","development")=="production":raise HTTPException(status_code=404,detail="NOT_FOUND")
    endpoint=f"/payments/{payment_id}/provider-success";idem=begin_idempotent(db,user,endpoint,idempotency_key,{"payment_id":str(payment_id),**p.model_dump(mode="json")})
    if idem.response_body is not None:return idem.response_body
    pay=db.scalar(select(PaymentIntent).where(PaymentIntent.id==payment_id).with_for_update())
    if not pay:raise HTTPException(status_code=404,detail="PAYMENT_NOT_FOUND")
    pay=mark_provider_success(db,pay,p.provider_reference);db.flush();return complete_idempotent(db,idem,200,{"payment_ref":pay.payment_ref,"status":pay.status,"provider_reference":pay.provider_reference,"net_amount_xof":float(pay.net_amount_xof)})

@router.get("/{payment_id}/ledger")
def ledger(payment_id:uuid.UUID,db:Session=Depends(get_db),user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN"))):
    pay=db.get(PaymentIntent,payment_id)
    if not pay:raise HTTPException(status_code=404,detail="PAYMENT_NOT_FOUND")
    rows=db.scalars(select(LedgerEntry).where(LedgerEntry.payment_intent_id==payment_id).order_by(LedgerEntry.created_at)).all();return {"payment_ref":pay.payment_ref,"entries":[{"entry_ref":r.entry_ref,"type":r.entry_type,"amount_xof":float(r.amount_xof),"description":r.description} for r in rows]}
