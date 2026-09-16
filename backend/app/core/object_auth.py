from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import Buyer,Farmer,User

def farmer_for_user(db:Session,user:User)->Farmer:
    f=db.scalar(select(Farmer).where(Farmer.user_id==user.id))
    if not f:raise HTTPException(status_code=403,detail="FARMER_PROFILE_REQUIRED")
    return f

def buyer_for_user(db:Session,user:User)->Buyer:
    b=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    if not b:raise HTTPException(status_code=403,detail="BUYER_PROFILE_REQUIRED")
    return b

def require_farmer_owner(db:Session,user:User,farmer_id):
    if "ADMIN" in {r.code for r in user.roles}:return
    if farmer_for_user(db,user).id!=farmer_id:raise HTTPException(status_code=403,detail="OBJECT_FORBIDDEN")

def require_buyer_owner(db:Session,user:User,buyer_id):
    if "ADMIN" in {r.code for r in user.roles}:return
    if buyer_for_user(db,user).id!=buyer_id:raise HTTPException(status_code=403,detail="OBJECT_FORBIDDEN")
