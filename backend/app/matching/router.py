import uuid
from fastapi import APIRouter,Depends,HTTPException,Header
from sqlalchemy import delete,select
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.idempotency_service import begin_idempotent,complete_idempotent
from app.database.models import Buyer,Demand,Farmer,Harvest,Match,Offer,User
from app.database.session import get_db
from app.matching.engine import date_compatible,score_candidate

router=APIRouter(prefix="/demands",tags=["Matching"])

@router.post("/{demand_id}/match")
def run_matching(demand_id:uuid.UUID,db:Session=Depends(get_db),user:User=Depends(get_current_user),
                 idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    idem=begin_idempotent(db,user,f"/demands/{demand_id}/match",idempotency_key,{"demand_id":str(demand_id)})
    if idem.response_body is not None:return idem.response_body
    demand=db.scalar(select(Demand).where(Demand.id==demand_id))
    buyer=db.scalar(select(Buyer).where(Buyer.user_id==user.id))
    if not demand: raise HTTPException(status_code=404,detail="DEMAND_NOT_FOUND")
    if not buyer or demand.buyer_id!=buyer.id: raise HTTPException(status_code=403,detail="DEMAND_NOT_OWNED")
    offers=db.scalars(select(Offer).where(Offer.product_id==demand.product_id,Offer.status=="ACTIVE",
                                          Offer.quantity_available_kg>0)).all()
    db.execute(delete(Match).where(Match.demand_id==demand.id))
    results=[]
    for offer in offers:
        harvest=db.get(Harvest,offer.harvest_id)
        if not date_compatible(harvest.expected_start_date,harvest.expected_end_date,
                               demand.delivery_start_date,demand.delivery_end_date): continue
        if demand.quality_grades and offer.quality_grade not in demand.quality_grades: continue
        parts,total=score_candidate(available=offer.quantity_available_kg,required=demand.quantity_required_kg,
            asking=offer.asking_price_xof_per_kg,target=demand.target_price_xof_per_kg,
            grade=offer.quality_grade,required_grades=demand.quality_grades)
        compatible=min(offer.quantity_available_kg,demand.quantity_required_kg)
        m=Match(demand_id=demand.id,offer_id=offer.id,compatible_quantity_kg=compatible,
            date_score=parts["date"],price_score=parts["price"],logistics_score=parts["logistics"],
            quality_score=parts["quality"],reliability_score=parts["reliability"],
            volume_score=parts["volume"],total_score=total,explanation={k:float(v) for k,v in parts.items()})
        db.add(m)
        farmer=db.get(Farmer,offer.farmer_id)
        results.append({"offer_id":str(offer.id),"offer_ref":offer.offer_ref,
                        "farmer_name":farmer.display_name if farmer else "Producteur AGRI-CI",
                        "compatible_quantity_kg":float(compatible),
                        "asking_price_xof_per_kg":float(offer.asking_price_xof_per_kg) if offer.asking_price_xof_per_kg else None,
                        "quality_grade":offer.quality_grade,"total_score":float(total),"components":m.explanation})
    results.sort(key=lambda x:x["total_score"],reverse=True)
    body={"demand_id":str(demand.id),"requested_quantity_kg":float(demand.quantity_required_kg),
          "compatible_quantity_kg":sum(x["compatible_quantity_kg"] for x in results),"matches":results}
    return complete_idempotent(db,idem,200,body)
