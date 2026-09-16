import uuid
from fastapi import APIRouter,Depends,HTTPException,Header
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.aggregation.service import propose_from_matches
from app.core.dependencies import get_current_user
from app.core.idempotency_service import begin_idempotent,complete_idempotent
from app.database.models import Aggregation,AggregationMember,Buyer,Commitment,Demand,Farmer,Offer,User
from app.database.session import get_db

router=APIRouter(tags=["Aggregation"])

@router.post("/demands/{demand_id}/aggregate")
def aggregate(demand_id:uuid.UUID,db:Session=Depends(get_db),user:User=Depends(get_current_user),
              idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,f"/demands/{demand_id}/aggregate",idempotency_key,{"demand_id":str(demand_id)})
    if idem.response_body is not None:return idem.response_body
    demand=db.get(Demand,demand_id);buyer=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    if not demand:raise HTTPException(status_code=404,detail="DEMAND_NOT_FOUND")
    if not buyer or demand.buyer_id!=buyer.id:raise HTTPException(status_code=403,detail="DEMAND_NOT_OWNED")
    agg=propose_from_matches(db,demand)
    body={"aggregation_id":str(agg.id),"aggregation_ref":agg.aggregation_ref,
            "target_quantity_kg":float(agg.target_quantity_kg),
            "proposed_quantity_kg":float(agg.proposed_quantity_kg),
            "accepted_quantity_kg":float(agg.accepted_quantity_kg),"status":agg.status}
    return complete_idempotent(db,idem,200,body)

@router.get("/aggregations/{aggregation_id}")
def get_aggregation(aggregation_id:uuid.UUID,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    agg=db.get(Aggregation,aggregation_id)
    if not agg:raise HTTPException(status_code=404,detail="AGGREGATION_NOT_FOUND")
    members=db.execute(select(AggregationMember,Offer,Farmer,Commitment)
        .join(Offer,AggregationMember.offer_id==Offer.id)
        .join(Farmer,Offer.farmer_id==Farmer.id)
        .join(Commitment,Commitment.aggregation_member_id==AggregationMember.id)
        .where(AggregationMember.aggregation_id==agg.id)
        .order_by(AggregationMember.created_at)).all()
    return {"id":str(agg.id),"ref":agg.aggregation_ref,"target_quantity_kg":float(agg.target_quantity_kg),
            "proposed_quantity_kg":float(agg.proposed_quantity_kg),
            "accepted_quantity_kg":float(agg.accepted_quantity_kg),"status":agg.status,
            "members":[{"farmer_name":f.display_name,"offer_ref":o.offer_ref,
              "proposed_quantity_kg":float(m.proposed_quantity_kg),"accepted_quantity_kg":float(m.accepted_quantity_kg),
              "member_status":m.status,"commitment_status":c.status} for m,o,f,c in members]}
