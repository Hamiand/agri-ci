from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.idempotency import request_hash
from app.database.models import IdempotencyKey,User

def begin_idempotent(db:Session,user:User,endpoint:str,key:str|None,payload:dict):
    if not key:raise HTTPException(status_code=400,detail="IDEMPOTENCY_KEY_REQUIRED")
    h=request_hash(payload)
    row=db.scalar(select(IdempotencyKey).where(IdempotencyKey.user_id==user.id,
        IdempotencyKey.endpoint==endpoint,IdempotencyKey.key==key).with_for_update())
    if row:
        if row.request_hash!=h:raise HTTPException(status_code=409,detail="IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_REQUEST")
        if row.response_body is not None:return row
        raise HTTPException(status_code=409,detail="IDEMPOTENT_REQUEST_IN_PROGRESS")
    row=IdempotencyKey(user_id=user.id,endpoint=endpoint,key=key,request_hash=h)
    db.add(row);db.flush()
    return row

def finish_idempotent(row:IdempotencyKey,status:int,body:dict):
    row.response_status=status;row.response_body=body
    return body

def complete_idempotent(db:Session,row:IdempotencyKey,status:int,body:dict):
    """Persist business mutation + replayable response atomically."""
    finish_idempotent(row,status,body)
    db.commit()
    return body
