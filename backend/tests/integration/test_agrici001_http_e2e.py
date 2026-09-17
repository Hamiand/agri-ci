import os
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Match, Offer, Product

pytestmark = [pytest.mark.integration,pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="TEST_DATABASE_URL required")]

def _auth(client,phone,password):
    response=client.post("/auth/login",json={"phone":phone,"password":password});assert response.status_code==200,response.text
    return {"Authorization":f"Bearer {response.json()['access_token']}"}

def _register(client,phone,password,role):
    response=client.post("/auth/register",json={"phone":phone,"password":password,"preferred_language":"fr","role":role})
    assert response.status_code==201,response.text
    return response.json()["id"]

def test_agrici001_http_security_and_idempotency_smoke(app_client):
    assert app_client.get("/health").status_code==200
    assert app_client.get("/farmers/me").status_code in (401,403)

def test_mutation_without_auth_is_rejected_before_business_processing(app_client):
    assert app_client.post("/demands/00000000-0000-0000-0000-000000000001/aggregate").status_code in (401,403)

def test_agrici001_exact_3000kg_authenticated_http_flow(app_client):
    client=app_client;suffix=uuid.uuid4().hex[:8];password="Pilot-Test-Password-123!"
    buyer_phone=f"+225010{suffix}";ops_phone=f"+225099{suffix}";transporter_phone=f"+225088{suffix}";other_transporter_phone=f"+225087{suffix}"
    farmer_specs=[("Koffi","400"),("Awa","750"),("Mariam","600"),("Yao","300"),("Cooperative A","1400")]
    _register(client,buyer_phone,password,"BUYER");buyer_headers=_auth(client,buyer_phone,password)
    assert client.post("/buyers",headers=buyer_headers,json={"display_name":"Acheteur Abidjan","buyer_type":"WHOLESALER","city":"Abidjan"}).status_code==201
    _register(client,ops_phone,password,"OPERATIONS_MANAGER");ops_headers=_auth(client,ops_phone,password)
    transporter_user_id=_register(client,transporter_phone,password,"TRANSPORTER");transporter_headers=_auth(client,transporter_phone,password)
    _register(client,other_transporter_phone,password,"TRANSPORTER");other_transporter_headers=_auth(client,other_transporter_phone,password)
    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True);Session=sessionmaker(bind=engine,expire_on_commit=False)
    product_code=f"T{suffix[:6]}"
    with Session.begin() as db:db.add(Product(code=product_code,name_fr="Tomate AGRI-CI-001 HTTP",name_en="AGRI-CI-001 HTTP Tomato",active=True))
    farmer_tokens={};offer_ids={}
    for index,(name,quantity) in enumerate(farmer_specs):
        phone=f"+22507{index}{suffix}";_register(client,phone,password,"FARMER");headers=_auth(client,phone,password);farmer_tokens[name]=headers
        f=client.post("/farmers",headers=headers,json={"display_name":name});assert f.status_code==201,f.text
        farm=client.post("/farms",headers=headers,json={"name":f"Exploitation {name}","locality":f"Village {index+1}"});assert farm.status_code==201,farm.text
        plot=client.post("/plots",headers=headers,json={"farm_id":farm.json()["id"],"plot_ref":f"P-{suffix}-{index}","name":"Tomate","area_ha":"1.0"});assert plot.status_code==201,plot.text
        harvest=client.post("/harvests",headers=headers,json={"plot_id":plot.json()["id"],"product_code":product_code,"expected_start_date":"2027-05-16","expected_end_date":"2027-05-18","estimated_quantity_kg":quantity});assert harvest.status_code==201,harvest.text
        offer_headers={**headers,"Idempotency-Key":f"offer-{suffix}-{index}"};offer_payload={"harvest_id":harvest.json()["id"],"quantity_kg":quantity,"asking_price_xof_per_kg":"760","quality_grade":"A"}
        offer=client.post("/offers",headers=offer_headers,json=offer_payload);assert offer.status_code==201,offer.text
        offer_replay=client.post("/offers",headers=offer_headers,json=offer_payload);assert offer_replay.status_code==201 and offer_replay.json()==offer.json()
        offer_ids[name]=uuid.UUID(offer.json()["id"])
    demand_headers={**buyer_headers,"Idempotency-Key":f"demand-{suffix}"};demand_payload={"product_code":product_code,"quantity_required_kg":"3000","delivery_start_date":"2027-05-16","delivery_end_date":"2027-05-18","target_price_xof_per_kg":"760","quality_grades":["A","B"],"destination_city":"Abidjan"}
    demand=client.post("/demands",headers=demand_headers,json=demand_payload);assert demand.status_code==201,demand.text
    demand_replay=client.post("/demands",headers=demand_headers,json=demand_payload);assert demand_replay.status_code==201 and demand_replay.json()==demand.json()
    demand_id=uuid.UUID(demand.json()["id"]);scores={"Koffi":Decimal("99"),"Awa":Decimal("98"),"Mariam":Decimal("97"),"Yao":Decimal("96"),"Cooperative A":Decimal("95")}
    with Session.begin() as db:
        for name,_ in farmer_specs:
            offer=db.get(Offer,offer_ids[name]);db.add(Match(demand_id=demand_id,offer_id=offer_ids[name],compatible_quantity_kg=offer.quantity_available_kg,date_score=100,price_score=100,logistics_score=70,quality_score=100,reliability_score=70,volume_score=70,total_score=scores[name],explanation={"reference_scenario":True}))
    agg=client.post(f"/demands/{demand_id}/aggregate",headers={**buyer_headers,"Idempotency-Key":f"agg-{suffix}"});assert agg.status_code==200,agg.text
    aggregation_id=uuid.UUID(agg.json()["aggregation_id"]);assert agg.json()["target_quantity_kg"]==3000.0 and agg.json()["proposed_quantity_kg"]==3000.0
    aggregation=client.get(f"/aggregations/{aggregation_id}",headers=buyer_headers);assert aggregation.status_code==200
    assert {m["farmer_name"]:m["proposed_quantity_kg"] for m in aggregation.json()["members"]}=={"Koffi":400.0,"Awa":750.0,"Mariam":600.0,"Yao":300.0,"Cooperative A":950.0}
    early=client.post(f"/orders/from-aggregation/{aggregation_id}",headers={**buyer_headers,"Idempotency-Key":f"order-early-{suffix}"});assert early.status_code==409
    yao=client.get("/commitments",headers=farmer_tokens["Yao"]);pending=[c for c in yao.json() if c["status"]=="PENDING"];assert len(pending)==1
    decline=client.post(f"/commitments/{pending[0]['id']}/decline",headers={**farmer_tokens["Yao"],"Idempotency-Key":f"decline-yao-{suffix}"});assert decline.status_code==200 and decline.json()["replacement_proposed_kg"]==300.0
    for name in ["Koffi","Awa","Mariam","Cooperative A"]:
        commitments=client.get("/commitments",headers=farmer_tokens[name]);pending=[c for c in commitments.json() if c["status"]=="PENDING"]
        assert len(pending)==(2 if name=="Cooperative A" else 1)
        for item in pending:
            accepted=client.post(f"/commitments/{item['id']}/accept",headers={**farmer_tokens[name],"Idempotency-Key":f"accept-{item['id']}"});assert accepted.status_code==200,accepted.text
    final=client.get(f"/aggregations/{aggregation_id}",headers=buyer_headers);assert final.json()["accepted_quantity_kg"]==3000.0 and final.json()["status"]=="CONFIRMED"
    order_response=client.post(f"/orders/from-aggregation/{aggregation_id}",headers={**buyer_headers,"Idempotency-Key":f"order-final-{suffix}"});assert order_response.status_code==201,order_response.text
    order=order_response.json();order_id=order["order_id"];assert order["quantity_kg"]==3000.0 and sum(x["quantity_kg"] for x in order["allocations"])==3000.0
    replay=client.post(f"/orders/from-aggregation/{aggregation_id}",headers={**buyer_headers,"Idempotency-Key":f"order-final-{suffix}"});assert replay.status_code==201 and replay.json()["order_id"]==order_id
    quality_ids=[]
    for allocation in order["allocations"]:
        qty=allocation["quantity_kg"];col=client.post("/collection",headers={**ops_headers,"Idempotency-Key":f"collect-{allocation['id']}"},json={"order_allocation_id":allocation["id"],"received_quantity_kg":qty,"location_name":"Centre de collecte AGRI-CI-001"});assert col.status_code==201,col.text
        q=client.post(f"/collection/{col.json()['collection_id']}/quality",headers={**ops_headers,"Idempotency-Key":f"quality-{col.json()['collection_id']}"},json={"grade":"A","quantity_kg":qty,"notes":"AGRI-CI-001 acceptance"});assert q.status_code==201,q.text;quality_ids.append(q.json()["quality_check_id"])
    lot=client.post("/lots",headers={**ops_headers,"Idempotency-Key":f"lot-{suffix}"},json={"order_id":order_id,"quality_check_ids":quality_ids});assert lot.status_code==201,lot.text;lot=lot.json();assert lot["quantity_kg"]==3000.0
    transport=client.post("/transport-jobs",headers={**ops_headers,"Idempotency-Key":f"transport-{suffix}"},json={"order_id":order_id,"lot_ids":[lot["lot_id"]],"transporter_user_id":transporter_user_id,"origin":"Centre de collecte AGRI-CI-001","destination":"Abidjan","vehicle_ref":"AGRI-CI-TRUCK-001","driver_name":"Pilote AGRI-CI"});assert transport.status_code==201,transport.text
    transport_id=transport.json()["transport_job_id"];assert transport.json()["transporter_user_id"]==transporter_user_id
    mine=client.get("/transport-jobs",headers=transporter_headers);assert mine.status_code==200 and [x["id"] for x in mine.json()]==[transport_id]
    other_mine=client.get("/transport-jobs",headers=other_transporter_headers);assert other_mine.status_code==200 and transport_id not in [x["id"] for x in other_mine.json()]
    forbidden_depart=client.post(f"/transport-jobs/{transport_id}/depart",headers={**other_transporter_headers,"Idempotency-Key":f"wrong-transporter-depart-{suffix}"});assert forbidden_depart.status_code==403,forbidden_depart.text
    ops_jobs=client.get("/transport-jobs",headers=ops_headers);assert ops_jobs.status_code==200 and transport_id in [x["id"] for x in ops_jobs.json()]
    departed=client.post(f"/transport-jobs/{transport_id}/depart",headers={**transporter_headers,"Idempotency-Key":f"depart-{suffix}"});assert departed.status_code==200 and departed.json()["status"]=="IN_TRANSIT"

    tranche_payload={"price_xof_per_kg":760,"transport_xof":35000,"service_xof":22500,"other_xof":7500,"provider":"PILOT_PROVIDER"}
    no_delivery=client.post(f"/payments/orders/{order_id}/prepare",headers={**ops_headers,"Idempotency-Key":f"settlement-before-delivery-{suffix}"},json=tranche_payload);assert no_delivery.status_code==409,no_delivery.text;assert no_delivery.json()["detail"]=="NO_DELIVERED_QUANTITY_TO_SETTLE"

    first_delivery=client.post("/deliveries",headers={**ops_headers,"Idempotency-Key":f"delivery-1-{suffix}"},json={"transport_job_id":transport_id,"delivered_quantity_kg":1500,"received_by":"Acheteur Abidjan"});assert first_delivery.status_code==201,first_delivery.text
    partial_jobs=client.get("/transport-jobs",headers=transporter_headers);partial_job=next(x for x in partial_jobs.json() if x["id"]==transport_id);assert partial_job["status"]=="IN_TRANSIT"
    first_headers={**ops_headers,"Idempotency-Key":f"settlement-1-{suffix}"};first_settlement=client.post(f"/payments/orders/{order_id}/prepare",headers=first_headers,json=tranche_payload);assert first_settlement.status_code==200,first_settlement.text
    assert first_settlement.json()["settlement_basis"]=="DELIVERED_QUANTITY" and first_settlement.json()["settlement_mode"]=="INCREMENTAL_UNSETTLED_QUANTITY"
    first_prepared=first_settlement.json()["prepared"]
    assert len(first_prepared)==4 and all(x["status"]=="PENDING" for x in first_prepared)
    assert sum(x["delivered_quantity_kg"] for x in first_prepared)==1500.0 and sorted(x["delivered_quantity_kg"] for x in first_prepared)==[200.0,300.0,375.0,625.0]
    assert sum(x["gross_amount_xof"] for x in first_prepared)==1140000.0
    first_replay=client.post(f"/payments/orders/{order_id}/prepare",headers=first_headers,json=tranche_payload);assert first_replay.status_code==200 and first_replay.json()==first_settlement.json()
    blocked=client.post(f"/payments/orders/{order_id}/prepare",headers={**ops_headers,"Idempotency-Key":f"settlement-no-new-{suffix}"},json=tranche_payload);assert blocked.status_code==409,blocked.text;assert blocked.json()["detail"]=="NO_NEW_DELIVERED_QUANTITY_TO_SETTLE"

    second_delivery=client.post("/deliveries",headers={**ops_headers,"Idempotency-Key":f"delivery-2-{suffix}"},json={"transport_job_id":transport_id,"delivered_quantity_kg":1500,"received_by":"Acheteur Abidjan"});assert second_delivery.status_code==201,second_delivery.text
    completed_jobs=client.get("/transport-jobs",headers=transporter_headers);completed_job=next(x for x in completed_jobs.json() if x["id"]==transport_id);assert completed_job["status"]=="DELIVERED"
    second_headers={**ops_headers,"Idempotency-Key":f"settlement-2-{suffix}"};second_settlement=client.post(f"/payments/orders/{order_id}/prepare",headers=second_headers,json=tranche_payload);assert second_settlement.status_code==200,second_settlement.text
    second_prepared=second_settlement.json()["prepared"]
    assert len(second_prepared)==4 and all(x["status"]=="PENDING" for x in second_prepared)
    assert sum(x["delivered_quantity_kg"] for x in second_prepared)==1500.0 and sorted(x["delivered_quantity_kg"] for x in second_prepared)==[200.0,300.0,375.0,625.0]
    assert sum(x["gross_amount_xof"] for x in second_prepared)==1140000.0
    second_replay=client.post(f"/payments/orders/{order_id}/prepare",headers=second_headers,json=tranche_payload);assert second_replay.status_code==200 and second_replay.json()==second_settlement.json()

    payments=client.get(f"/payments?order_id={order_id}",headers=ops_headers);assert payments.status_code==200 and len(payments.json())==8 and all(x["status"]=="PENDING" for x in payments.json())
    total_gross=Decimal("0");total_deductions=Decimal("0");total_net=Decimal("0");deduction_totals={"TRANSPORT":Decimal("0"),"AGRI_CI_SERVICE":Decimal("0"),"OTHER_AUTHORIZED":Decimal("0")}
    for payment in payments.json():
        gross=Decimal(str(payment["gross_amount_xof"]));deductions=Decimal(str(payment["deductions_xof"]));net=Decimal(str(payment["net_amount_xof"]));assert gross-deductions==net
        ledger=client.get(f"/payments/{payment['id']}/ledger",headers=ops_headers);assert ledger.status_code==200,ledger.text;entries=ledger.json()["entries"]
        assert [entry["type"] for entry in entries].count("GROSS")==1 and [entry["type"] for entry in entries].count("DEDUCTION")==3 and [entry["type"] for entry in entries].count("NET_DUE")==1
        ledger_gross=sum((Decimal(str(e["amount_xof"])) for e in entries if e["type"]=="GROSS"),Decimal("0"));ledger_deductions=sum((Decimal(str(e["amount_xof"])) for e in entries if e["type"]=="DEDUCTION"),Decimal("0"));ledger_net=sum((Decimal(str(e["amount_xof"])) for e in entries if e["type"]=="NET_DUE"),Decimal("0"))
        assert ledger_gross==gross and ledger_deductions==deductions and ledger_net==net and ledger_gross-ledger_deductions==ledger_net
        for entry in entries:
            if entry["type"]=="DEDUCTION":deduction_totals[entry["description"].split(":",1)[0]]+=Decimal(str(entry["amount_xof"]))
        total_gross+=gross;total_deductions+=deductions;total_net+=net
    assert total_gross==Decimal("2280000.00") and deduction_totals=={"TRANSPORT":Decimal("70000.00"),"AGRI_CI_SERVICE":Decimal("45000.00"),"OTHER_AUTHORIZED":Decimal("15000.00")}
    assert total_deductions==Decimal("130000.00") and total_net==Decimal("2150000.00")
    first_payment=payments.json()[0];success_headers={**ops_headers,"Idempotency-Key":f"provider-success-{suffix}"};success_payload={"provider_reference":f"PILOT-{suffix}"}
    success=client.post(f"/payments/{first_payment['id']}/provider-success",headers=success_headers,json=success_payload);assert success.status_code==200,success.text
    assert success.json()["status"]=="SUCCESS" and success.json()["provider_reference"]==success_payload["provider_reference"]
    success_replay=client.post(f"/payments/{first_payment['id']}/provider-success",headers=success_headers,json=success_payload);assert success_replay.status_code==200 and success_replay.json()==success.json()
    engine.dispose()
