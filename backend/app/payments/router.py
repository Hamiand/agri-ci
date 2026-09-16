import os
import uuid
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException,Header
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user,require_roles
from app.core.idempotency_service import begin_idempotent,complete_idempotent
from app.database.models import CollectionEvent,Farmer,LedgerEntry,Order,OrderAllocation,PaymentDeduction,PaymentIntent,User
from app.database.session import get_db
from app.payments.service import ALLOWED_DEDUCTIONS,add_ledger,compute_net,mark_provider_success

router=APIRouter(prefix="/payments",tags=["Payments"])

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
    allocation=db.scalar(select(OrderAllocation).where(OrderAllocation.order_id==order.id,
        OrderAllocation.farmer_id==farmer.id))
    if not allocation:raise HTTPException(status_code=409,detail="FARMER_NOT_ALLOCATED_TO_ORDER")
    existing=db.scalar(select(PaymentIntent).where(PaymentIntent.order_id==order.id,
        PaymentIntent.farmer_id==farmer.id))
    if existing:return existing
    if any(d.deduction_type not in ALLOWED_DEDUCTIONS for d in p.deductions):
        raise HTTPException(status_code=422,detail="INVALID_DEDUCTION_TYPE")
    amounts=[d.amount_xof for d in p.deductions]
    try:net=compute_net(p.gross_amount_xof,amounts)
    except ValueError:raise HTTPException(status_code=422,detail="INVALID_PAYMENT_AMOUNTS")
    total=sum(amounts,Decimal("0"))
    pay=PaymentIntent(payment_ref=f"PAY-{uuid.uuid4().hex[:10].upper()}",order_id=order.id,
        farmer_id=farmer.id,gross_amount_xof=p.gross_amount_xof,deductions_xof=total,
        net_amount_xof=net,currency="XOF",provider=p.provider,status="PENDING")
    db.add(pay);db.flush()
    add_ledger(db,pay,"GROSS",p.gross_amount_xof,"Gross commercial amount")
    for d in p.deductions:
        db.add(PaymentDeduction(payment_intent_id=pay.id,deduction_type=d.deduction_type,
            description=d.description,amount_xof=d.amount_xof))
        add_ledger(db,pay,"DEDUCTION",d.amount_xof,f"{d.deduction_type}: {d.description}")
    add_ledger(db,pay,"NET_DUE",net,"Net amount due to farmer")
    return pay

@router.post("",status_code=201)
def create_payment(p:PaymentCreate,db:Session=Depends(get_db),
                   user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN")),
                   idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,"/payments",idempotency_key,p.model_dump(mode="json"))
    if idem.response_body is not None:return idem.response_body
    pay=_create_payment(db,p);db.flush()
    body={"payment_id":str(pay.id),"payment_ref":pay.payment_ref,
      "gross_amount_xof":float(pay.gross_amount_xof),"deductions_xof":float(pay.deductions_xof),
      "net_amount_xof":float(pay.net_amount_xof),"provider":pay.provider,"status":pay.status}
    return complete_idempotent(db,idem,201,body)

class SettlementPrepare(BaseModel):
    price_xof_per_kg:Decimal=Field(gt=0)
    transport_xof:Decimal=Field(default=0,ge=0)
    service_xof:Decimal=Field(default=0,ge=0)
    other_xof:Decimal=Field(default=0,ge=0)
    provider:str=Field(min_length=2,max_length=50)

@router.post("/orders/{order_id}/prepare")
def prepare_order_settlements(order_id:uuid.UUID,p:SettlementPrepare,db:Session=Depends(get_db),
                              user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN")),
                              idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,f"/payments/orders/{order_id}/prepare",idempotency_key,
        {"order_id":str(order_id),**p.model_dump(mode="json")})
    if idem.response_body is not None:return idem.response_body
    order=db.get(Order,order_id)
    if not order:raise HTTPException(status_code=404,detail="ORDER_NOT_FOUND")
    allocations=db.scalars(select(OrderAllocation).where(OrderAllocation.order_id==order.id)).all()
    if not allocations:raise HTTPException(status_code=409,detail="ORDER_HAS_NO_ALLOCATIONS")
    prepared=[]
    for allocation in allocations:
        received=Decimal(db.scalar(select(func.coalesce(func.sum(CollectionEvent.received_quantity_kg),0))
            .where(CollectionEvent.order_allocation_id==allocation.id)) or 0)
        if received<=0:continue
        gross=(received*p.price_xof_per_kg).quantize(Decimal("0.01"))
        # Operational deductions are distributed proportionally to the farmer's received share.
        share=received/Decimal(order.quantity_kg)
        deductions=[
          DeductionIn(deduction_type="TRANSPORT",description="Transport AGRI-CI",
                      amount_xof=(p.transport_xof*share).quantize(Decimal("0.01"))),
          DeductionIn(deduction_type="AGRI_CI_SERVICE",description="Service AGRI-CI",
                      amount_xof=(p.service_xof*share).quantize(Decimal("0.01"))),
          DeductionIn(deduction_type="OTHER_AUTHORIZED",description="Other authorized cost",
                      amount_xof=(p.other_xof*share).quantize(Decimal("0.01")))]
        pay=_create_payment(db,PaymentCreate(order_id=order.id,farmer_id=allocation.farmer_id,
            gross_amount_xof=gross,deductions=deductions,provider=p.provider))
        prepared.append({"payment_ref":pay.payment_ref,"farmer_id":str(allocation.farmer_id),
          "received_quantity_kg":float(received),"gross_amount_xof":float(pay.gross_amount_xof),
          "net_amount_xof":float(pay.net_amount_xof),"status":pay.status})
    if not prepared:raise HTTPException(status_code=409,detail="NO_COLLECTED_QUANTITY_TO_SETTLE")
    body={"order_id":str(order.id),"prepared":prepared}
    return complete_idempotent(db,idem,200,body)

@router.get("/farmer/me")
def farmer_payments(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    farmer=db.scalar(select(Farmer).where(Farmer.user_id==user.id))
    if not farmer:raise HTTPException(status_code=400,detail="FARMER_PROFILE_REQUIRED")
    rows=db.scalars(select(PaymentIntent).where(PaymentIntent.farmer_id==farmer.id)
      .order_by(PaymentIntent.created_at.desc())).all()
    return [{"id":str(x.id),"payment_ref":x.payment_ref,"order_id":str(x.order_id),
      "gross_amount_xof":float(x.gross_amount_xof),"deductions_xof":float(x.deductions_xof),
      "net_amount_xof":float(x.net_amount_xof),"provider":x.provider,"status":x.status} for x in rows]

@router.get("")
def list_payments(order_id:uuid.UUID|None=None,db:Session=Depends(get_db),
                  user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN"))):
    q=select(PaymentIntent).order_by(PaymentIntent.created_at.desc())
    if order_id:q=q.where(PaymentIntent.order_id==order_id)
    rows=db.scalars(q).all()
    return [{"id":str(x.id),"payment_ref":x.payment_ref,"order_id":str(x.order_id),
      "farmer_id":str(x.farmer_id),"gross_amount_xof":float(x.gross_amount_xof),
      "deductions_xof":float(x.deductions_xof),"net_amount_xof":float(x.net_amount_xof),
      "provider":x.provider,"status":x.status} for x in rows]

class ProviderSuccess(BaseModel):
    provider_reference:str

@router.post("/{payment_id}/provider-success")
def provider_success(payment_id:uuid.UUID,p:ProviderSuccess,db:Session=Depends(get_db),
                     user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN"))):
    if os.getenv("APP_ENV","development") == "production":
        raise HTTPException(status_code=404,detail="NOT_FOUND")
    pay=db.scalar(select(PaymentIntent).where(PaymentIntent.id==payment_id).with_for_update())
    if not pay:raise HTTPException(status_code=404,detail="PAYMENT_NOT_FOUND")
    pay=mark_provider_success(db,pay,p.provider_reference);db.commit()
    return {"payment_ref":pay.payment_ref,"status":pay.status,
      "provider_reference":pay.provider_reference,"net_amount_xof":float(pay.net_amount_xof)}

@router.get("/{payment_id}/ledger")
def ledger(payment_id:uuid.UUID,db:Session=Depends(get_db),
           user:User=Depends(require_roles("OPERATIONS_MANAGER","ADMIN"))):
    pay=db.get(PaymentIntent,payment_id)
    if not pay:raise HTTPException(status_code=404,detail="PAYMENT_NOT_FOUND")
    rows=db.scalars(select(LedgerEntry).where(LedgerEntry.payment_intent_id==payment_id)
      .order_by(LedgerEntry.created_at)).all()
    return {"payment_ref":pay.payment_ref,"entries":[{"entry_ref":r.entry_ref,"type":r.entry_type,
      "amount_xof":float(r.amount_xof),"description":r.description} for r in rows]}
