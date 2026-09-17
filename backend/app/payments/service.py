import uuid
from datetime import datetime,timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import DomainEvent,LedgerEntry,PaymentDeduction,PaymentIntent

ALLOWED_DEDUCTIONS={"TRANSPORT","AGRI_CI_SERVICE","OTHER_AUTHORIZED"}

def compute_net(gross:Decimal,deductions:list[Decimal])->Decimal:
    gross=Decimal(gross)
    total=sum((Decimal(x) for x in deductions),Decimal("0"))
    if gross<0 or total<0 or total>gross: raise ValueError("Invalid payment amounts")
    return gross-total

def add_ledger(db,payment,entry_type,amount,description):
    db.add(LedgerEntry(entry_ref=f"LED-{uuid.uuid4().hex[:10].upper()}",
        payment_intent_id=payment.id,entry_type=entry_type,amount_xof=amount,
        currency="XOF",description=description))

def mark_provider_success(db:Session,payment:PaymentIntent,provider_reference:str):
    if payment.status=="SUCCESS":
        if payment.provider_reference != provider_reference:
            raise HTTPException(status_code=409,detail="PAYMENT_PROVIDER_REFERENCE_CONFLICT")
        return payment
    if payment.status not in {"PENDING","PROCESSING"}:
        raise HTTPException(status_code=409,detail="INVALID_PAYMENT_STATE")
    payment.status="SUCCESS";payment.provider_reference=provider_reference
    payment.updated_at=datetime.now(timezone.utc)
    add_ledger(db,payment,"NET_PAID",payment.net_amount_xof,"Net amount paid by licensed payment provider")
    db.add(DomainEvent(event_type="PAYMENT_SUCCESS",aggregate_type="PAYMENT",
        aggregate_id=str(payment.id),payload={"payment_ref":payment.payment_ref,
        "net_amount_xof":float(payment.net_amount_xof),"provider":payment.provider}))
    return payment
