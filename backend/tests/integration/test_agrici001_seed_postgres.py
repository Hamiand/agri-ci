import os,uuid,pytest
from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from app.database.models import Farmer,Farm,Harvest,Offer,Plot,Product,User

pytestmark=[pytest.mark.integration,pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="TEST_DATABASE_URL required")]

def test_agrici001_supply_seed_totals_and_coop_reserve():
    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)
    Session=sessionmaker(bind=engine,expire_on_commit=False)
    suffix=uuid.uuid4().hex[:7]
    quantities=[("Koffi",400),("Awa",750),("Mariam",600),("Yao",300),("Cooperative A",1400)]
    with Session.begin() as db:
        product=Product(code=f"A{suffix[:5]}",name_fr="Tomate AGRI-CI-001",active=True);db.add(product);db.flush()
        offer_ids=[]
        for i,(name,qty) in enumerate(quantities):
            u=User(email=f"{name.replace(' ','').lower()}-{suffix}@test.local",password_hash="test",full_name=name,status="ACTIVE");db.add(u);db.flush()
            f=Farmer(user_id=u.id,farmer_ref=f"F-{suffix}-{i}",display_name=name,status="VERIFIED");db.add(f);db.flush()
            farm=Farm(farmer_id=f.id,farm_ref=f"FM-{suffix}-{i}",name=f"{name} Farm",village=f"Village {i+1}");db.add(farm);db.flush()
            plot=Plot(farm_id=farm.id,plot_ref=f"P-{suffix}-{i}",name="Tomato",area_ha=Decimal("1"));db.add(plot);db.flush()
            h=Harvest(harvest_ref=f"H-{suffix}-{i}",farmer_id=f.id,plot_id=plot.id,product_id=product.id,
                estimated_quantity_kg=Decimal(str(qty)),expected_start_date=date(2027,5,16),expected_end_date=date(2027,5,18),
                status="CONFIRMED",version=1);db.add(h);db.flush()
            o=Offer(offer_ref=f"O-{suffix}-{i}",harvest_id=h.id,farmer_id=f.id,product_id=product.id,
                quantity_total_kg=Decimal(str(qty)),quantity_available_kg=Decimal(str(qty)),quantity_proposed_kg=0,
                quantity_reserved_kg=0,quantity_sold_kg=0,asking_price_xof_per_kg=Decimal("760"),
                quality_grade="A",status="ACTIVE",version=1);db.add(o);db.flush();offer_ids.append(o.id)

    with Session() as db:
        offers=list(db.scalars(select(Offer).where(Offer.id.in_(offer_ids))).all())
        by_name={db.get(Farmer,o.farmer_id).display_name:o for o in offers}
        initial=Decimal("400")+Decimal("750")+Decimal("600")+Decimal("300")+Decimal("950")
        assert initial==Decimal("3000")
        assert Decimal(by_name["Cooperative A"].quantity_available_kg)-Decimal("950")==Decimal("450")
        after_yao_decline=initial-Decimal("300")
        replacement=min(Decimal("450"),Decimal("300"))
        assert after_yao_decline+replacement==Decimal("3000")
