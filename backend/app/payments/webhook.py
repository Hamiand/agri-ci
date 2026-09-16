import hashlib,hmac,json,os,uuid
from fastapi import APIRouter,Header,HTTPException,Request
from sqlalchemy import select
from app.database.models import PaymentIntent
from app.database.session import SessionLocal
from app.payments.service import mark_provider_success
from app.core.rate_limit import rate_limit

router=APIRouter(prefix="/payment-webhooks",tags=["Payment Webhooks"])

def valid_signature(raw:bytes,signature:str|None)->bool:
    secret=os.getenv("PAYMENT_WEBHOOK_SECRET","")
    if not secret or not signature:return False
    expected=hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected,signature)

@router.post("/provider")
async def provider_webhook(request:Request,x_signature:str|None=Header(default=None,alias="X-Signature")):
    rate_limit(request,"payment-webhook",limit=120)
    raw=await request.body()
    if not valid_signature(raw,x_signature):raise HTTPException(status_code=401,detail="INVALID_WEBHOOK_SIGNATURE")
    try:data=json.loads(raw)
    except Exception:raise HTTPException(status_code=400,detail="INVALID_WEBHOOK_BODY")
    if data.get("event")!="payment.success":return {"accepted":True,"ignored":True}
    payment_id=data.get("payment_id");provider_ref=data.get("provider_reference")
    if not payment_id or not provider_ref:raise HTTPException(status_code=422,detail="MISSING_PAYMENT_FIELDS")
    with SessionLocal() as db:
        pay=db.scalar(select(PaymentIntent).where(PaymentIntent.id==uuid.UUID(payment_id)).with_for_update())
        if not pay:raise HTTPException(status_code=404,detail="PAYMENT_NOT_FOUND")
        mark_provider_success(db,pay,provider_ref);db.commit()
    return {"accepted":True}
