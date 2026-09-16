import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field,model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.models import Buyer,Demand,Product,User
from app.database.session import get_db

router=APIRouter(prefix="/demands",tags=["Demands"])

class DemandCreate(BaseModel):
    product_code:str
    quantity_required_kg:Decimal=Field(gt=0)
    delivery_start_date:date
    delivery_end_date:date
    target_price_xof_per_kg:Decimal|None=Field(default=None,gt=0)
    quality_grades:list[str]=Field(default_factory=list)
    destination_city:str|None=None
    @model_validator(mode="after")
    def validate_dates(self):
        if self.delivery_end_date<self.delivery_start_date: raise ValueError("Invalid delivery window")
        return self

class DemandOut(BaseModel):
    id:uuid.UUID
    demand_ref:str
    quantity_required_kg:Decimal
    delivery_start_date:date
    delivery_end_date:date
    quality_grades:list[str]
    status:str
    model_config={"from_attributes":True}

@router.post("",response_model=DemandOut,status_code=201)
def create_demand(payload:DemandCreate,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    buyer=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    product=db.scalar(select(Product).where(Product.code==payload.product_code,Product.active.is_(True)))
    if not buyer: raise HTTPException(status_code=400,detail="BUYER_PROFILE_REQUIRED")
    if not product: raise HTTPException(status_code=404,detail="PRODUCT_NOT_FOUND")
    demand=Demand(demand_ref=f"DEM-{uuid.uuid4().hex[:10].upper()}",buyer_id=buyer.id,product_id=product.id,
        quantity_required_kg=payload.quantity_required_kg,delivery_start_date=payload.delivery_start_date,
        delivery_end_date=payload.delivery_end_date,target_price_xof_per_kg=payload.target_price_xof_per_kg,
        quality_grades=payload.quality_grades,destination_city=payload.destination_city,status="PUBLISHED")
    db.add(demand);db.commit();db.refresh(demand)
    return demand

class MarketDemandOut(BaseModel):
    id:uuid.UUID
    demand_ref:str
    product_code:str
    product_name:str
    quantity_required_kg:Decimal
    delivery_start_date:date
    delivery_end_date:date
    target_price_xof_per_kg:Decimal|None
    quality_grades:list[str]
    destination_city:str|None
    status:str

@router.get("",response_model=list[MarketDemandOut])
def list_market_demands(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    rows=db.execute(select(Demand,Product).join(Product,Demand.product_id==Product.id)
        .where(Demand.status.in_(["PUBLISHED","MATCHING","PARTIALLY_MATCHED","MATCHED","PENDING_CONFIRMATION"]))
        .order_by(Demand.delivery_start_date)).all()
    return [MarketDemandOut(id=d.id,demand_ref=d.demand_ref,product_code=p.code,product_name=p.name_fr,
        quantity_required_kg=d.quantity_required_kg,delivery_start_date=d.delivery_start_date,
        delivery_end_date=d.delivery_end_date,target_price_xof_per_kg=d.target_price_xof_per_kg,
        quality_grades=d.quality_grades or [],destination_city=d.destination_city,status=d.status) for d,p in rows]

@router.get("/mine")
def my_demands(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    from app.database.models import Aggregation
    buyer=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    if not buyer:raise HTTPException(status_code=400,detail="BUYER_PROFILE_REQUIRED")
    rows=db.execute(select(Demand,Product).join(Product,Demand.product_id==Product.id)
        .where(Demand.buyer_id==buyer.id).order_by(Demand.created_at.desc())).all()
    out=[]
    for d,p in rows:
        agg=db.scalar(select(Aggregation).where(Aggregation.demand_id==d.id).order_by(Aggregation.created_at.desc()))
        out.append({"id":str(d.id),"demand_ref":d.demand_ref,"product_name":p.name_fr,
          "quantity_required_kg":float(d.quantity_required_kg),"delivery_start_date":d.delivery_start_date.isoformat(),
          "delivery_end_date":d.delivery_end_date.isoformat(),"destination_city":d.destination_city,
          "target_price_xof_per_kg":float(d.target_price_xof_per_kg) if d.target_price_xof_per_kg else None,
          "status":d.status,"aggregation_id":str(agg.id) if agg else None,
          "aggregation_ref":agg.aggregation_ref if agg else None,
          "aggregation_status":agg.status if agg else None,
          "accepted_quantity_kg":float(agg.accepted_quantity_kg) if agg else 0})
    return out
