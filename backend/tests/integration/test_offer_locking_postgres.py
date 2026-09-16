import os,threading,uuid,pytest
from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Farmer,Farm,Harvest,Offer,Plot,Product,User
from app.offers.reservation_service import InsufficientOfferQuantity,reserve_available_quantity

pytestmark=[pytest.mark.integration,pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="TEST_DATABASE_URL required")]

def test_two_sessions_cannot_both_reserve_koffis_same_400kg():
    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)
    Session=sessionmaker(bind=engine,expire_on_commit=False)
    suffix=uuid.uuid4().hex[:8]
    with Session.begin() as db:
        user=User(email=f"koffi-{suffix}@test.local",password_hash="test",full_name="Koffi Test",status="ACTIVE")
        db.add(user);db.flush()
        farmer=Farmer(user_id=user.id,farmer_ref=f"FAR-{suffix}",display_name="Koffi",status="VERIFIED")
        db.add(farmer);db.flush()
        farm=Farm(farmer_id=farmer.id,farm_ref=f"FRM-{suffix}",name="Koffi Farm",village="Village Test")
        db.add(farm);db.flush()
        plot=Plot(farm_id=farm.id,plot_ref=f"PLT-{suffix}",name="Tomato Plot",area_ha=Decimal("1"))
        product=Product(code=f"T{suffix[:5]}",name_fr="Tomate Test",active=True)
        db.add_all([plot,product]);db.flush()
        harvest=Harvest(harvest_ref=f"HAR-{suffix}",farmer_id=farmer.id,plot_id=plot.id,product_id=product.id,
            estimated_quantity_kg=Decimal("500"),expected_start_date=date(2027,5,16),
            expected_end_date=date(2027,5,18),status="CONFIRMED",version=1)
        db.add(harvest);db.flush()
        offer=Offer(offer_ref=f"OFF-{suffix}",harvest_id=harvest.id,farmer_id=farmer.id,product_id=product.id,
            quantity_total_kg=Decimal("400"),quantity_available_kg=Decimal("400"),
            quantity_proposed_kg=0,quantity_reserved_kg=0,quantity_sold_kg=0,
            asking_price_xof_per_kg=Decimal("750"),quality_grade="A",status="ACTIVE",version=1)
        db.add(offer);db.flush(); offer_id=offer.id

    barrier=threading.Barrier(2)
    results=[]; lock=threading.Lock()
    def buyer(name):
        db=Session()
        try:
            barrier.wait(timeout=5)
            reserve_available_quantity(db,offer_id,Decimal("400"))
            db.commit()
            result=(name,"SUCCESS")
        except InsufficientOfferQuantity:
            db.rollback();result=(name,"INSUFFICIENT")
        finally:
            db.close()
        with lock:results.append(result)

    a=threading.Thread(target=buyer,args=("BUYER_A",))
    c=threading.Thread(target=buyer,args=("BUYER_B",))
    a.start();c.start();a.join(10);c.join(10)
    assert not a.is_alive() and not c.is_alive()
    assert sorted(x[1] for x in results)==["INSUFFICIENT","SUCCESS"]

    with Session() as db:
        final=db.get(Offer,offer_id)
        assert Decimal(final.quantity_available_kg)==Decimal("0")
        assert Decimal(final.quantity_reserved_kg)==Decimal("400")
        assert final.version==2
