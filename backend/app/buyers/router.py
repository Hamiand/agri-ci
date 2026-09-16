import uuid
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.models import Buyer, User
from app.database.session import get_db

router=APIRouter(prefix="/buyers",tags=["Buyers"])
BuyerType=Literal["INDIVIDUAL","RESTAURANT","HOTEL","WHOLESALER","RETAILER","SUPERMARKET","PROCESSOR","CANTEEN","INSTITUTION","OTHER"]

class BuyerCreate(BaseModel):
    display_name:str=Field(min_length=2,max_length=180)
    buyer_type:BuyerType
    city:str|None=None

class BuyerOut(BuyerCreate):
    id:uuid.UUID
    buyer_ref:str
    status:str
    model_config={"from_attributes":True}

@router.post("",response_model=BuyerOut,status_code=201)
def create_buyer(payload:BuyerCreate,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if db.scalar(select(Buyer).where(Buyer.user_id==user.id)):
        raise HTTPException(status_code=409,detail="BUYER_PROFILE_ALREADY_EXISTS")
    buyer=Buyer(user_id=user.id,buyer_ref=f"AGR-B-{uuid.uuid4().hex[:8].upper()}",**payload.model_dump())
    db.add(buyer);db.commit();db.refresh(buyer)
    return buyer
