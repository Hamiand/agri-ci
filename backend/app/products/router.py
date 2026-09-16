import uuid
from fastapi import APIRouter,Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.models import Product,User
from app.database.session import get_db
router=APIRouter(prefix="/products",tags=["Products"])
class ProductOut(BaseModel):
    id:uuid.UUID
    code:str
    name_fr:str
    active:bool
    model_config={"from_attributes":True}
@router.get("",response_model=list[ProductOut])
def list_products(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return list(db.scalars(select(Product).where(Product.active.is_(True)).order_by(Product.name_fr)).all())
