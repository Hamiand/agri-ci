import hashlib
import hmac
import json
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def _signed_post(client, payload, secret):
    raw=json.dumps(payload,separators=(",",":")).encode()
    signature=hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
    return client.post("/payment-webhooks/provider",content=raw,headers={"Content-Type":"application/json","X-Signature":signature})


def _ops_headers(client):
    suffix=uuid.uuid4().hex[:8]
    phone=f"+225099{suffix}"
    password="Pilot-Test-Password-123!"
    reg=client.post("/auth/register",json={"phone":phone,"password":password,"preferred_language":"fr","role":"OPERATIONS_MANAGER"})
    assert reg.status_code==201,reg.text
    login=client.post("/auth/login",json={"phone":phone,"password":password})
    assert login.status_code==200,login.text
    return {"Authorization":f"Bearer {login.json()['access_token']}"}


def _prepare_replacement(client,ops_headers,order_id,key):
    response=client.post(
        f"/payments/orders/{order_id}/prepare",
        headers={**ops_headers,"Idempotency-Key":key},
        json={"price_xof_per_kg":"760","transport_xof":"0","service_xof":"0","other_xof":"0","provider":"PILOT_PROVIDER"},
    )
    assert response.status_code==200,response.text
    assert response.json()["settlement_mode"]=="INCREMENTAL_UNSETTLED_QUANTITY"
    return response.json()


def test_signed_webhook_failed_then_replacement_settlement_created():
    os.environ["PAYMENT_WEBHOOK_SECRET"]="integration-webhook-secret"
    from app.main import app
    from app.payments.router import _already_settled_quantity_by_farmer
    from app.database.session import SessionLocal

    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)
    with engine.begin() as connection:
        row=connection.execute(text("SELECT id,order_id,farmer_id,settled_quantity_kg FROM payment_intents WHERE status='PENDING' AND settled_quantity_kg IS NOT NULL ORDER BY created_at DESC LIMIT 1")).first()
    assert row is not None,"AGRI-CI-001 must leave a pending settlement payment"
    payment_id,order_id,farmer_id,quantity=row

    with SessionLocal() as db:
        reserved_before=_already_settled_quantity_by_farmer(db,order_id)
    assert reserved_before.get(farmer_id,0) >= quantity

    client=TestClient(app)
    ops_headers=_ops_headers(client)
    payload={"event":"payment.failed","payment_id":str(payment_id),"provider_reference":"FAIL-HTTP-001"}

    bad=client.post("/payment-webhooks/provider",json=payload,headers={"X-Signature":"bad"})
    assert bad.status_code==401
    assert bad.json()["error"]["code"]=="INVALID_WEBHOOK_SIGNATURE"

    response=_signed_post(client,payload,"integration-webhook-secret")
    assert response.status_code==200
    assert response.json()=={"accepted":True,"event":"payment.failed"}

    with engine.begin() as connection:
        state=connection.execute(text("SELECT status,provider_reference FROM payment_intents WHERE id=:id"),{"id":payment_id}).first()
        count_before=connection.execute(text("SELECT count(*) FROM payment_intents WHERE order_id=:order_id AND farmer_id=:farmer_id"),{"order_id":order_id,"farmer_id":farmer_id}).scalar_one()
    assert state==("FAILED","FAIL-HTTP-001")

    with SessionLocal() as db:
        reserved_after=_already_settled_quantity_by_farmer(db,order_id)
    assert reserved_after.get(farmer_id,0)==reserved_before.get(farmer_id,0)-quantity

    replacement=_prepare_replacement(client,ops_headers,order_id,f"retry-failed-{uuid.uuid4()}")
    farmer_rows=[p for p in replacement["prepared"] if p["farmer_id"]==str(farmer_id)]
    assert len(farmer_rows)==1
    assert farmer_rows[0]["delivered_quantity_kg"]==float(quantity)

    with engine.begin() as connection:
        count_after=connection.execute(text("SELECT count(*) FROM payment_intents WHERE order_id=:order_id AND farmer_id=:farmer_id"),{"order_id":order_id,"farmer_id":farmer_id}).scalar_one()
        latest=connection.execute(text("SELECT status,settled_quantity_kg FROM payment_intents WHERE order_id=:order_id AND farmer_id=:farmer_id ORDER BY created_at DESC LIMIT 1"),{"order_id":order_id,"farmer_id":farmer_id}).first()
    assert count_after==count_before+1
    assert latest==("PENDING",quantity)


def test_signed_webhook_refund_then_replacement_settlement_created():
    os.environ["PAYMENT_WEBHOOK_SECRET"]="integration-webhook-secret"
    from app.main import app

    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)
    with engine.begin() as connection:
        row=connection.execute(text("SELECT id,order_id,farmer_id,settled_quantity_kg FROM payment_intents WHERE status='PENDING' AND settled_quantity_kg IS NOT NULL ORDER BY created_at DESC LIMIT 1")).first()
    assert row is not None
    payment_id,order_id,farmer_id,quantity=row
    client=TestClient(app)
    ops_headers=_ops_headers(client)

    premature=_signed_post(client,{"event":"payment.refunded","payment_id":str(payment_id),"provider_reference":"REFUND-EARLY"},"integration-webhook-secret")
    assert premature.status_code==409
    assert premature.json()["error"]["code"]=="PAYMENT_NOT_SUCCESSFUL"

    success=_signed_post(client,{"event":"payment.success","payment_id":str(payment_id),"provider_reference":"SUCCESS-HTTP-001"},"integration-webhook-secret")
    assert success.status_code==200

    refund=_signed_post(client,{"event":"payment.refunded","payment_id":str(payment_id),"provider_reference":"REFUND-HTTP-001"},"integration-webhook-secret")
    assert refund.status_code==200
    with engine.begin() as connection:
        state=connection.execute(text("SELECT status,provider_reference FROM payment_intents WHERE id=:id"),{"id":payment_id}).first()
        count_before=connection.execute(text("SELECT count(*) FROM payment_intents WHERE order_id=:order_id AND farmer_id=:farmer_id"),{"order_id":order_id,"farmer_id":farmer_id}).scalar_one()
    assert state==("REFUNDED","REFUND-HTTP-001")

    replacement=_prepare_replacement(client,ops_headers,order_id,f"retry-refund-{uuid.uuid4()}")
    farmer_rows=[p for p in replacement["prepared"] if p["farmer_id"]==str(farmer_id)]
    assert len(farmer_rows)==1
    assert farmer_rows[0]["delivered_quantity_kg"]==float(quantity)

    with engine.begin() as connection:
        count_after=connection.execute(text("SELECT count(*) FROM payment_intents WHERE order_id=:order_id AND farmer_id=:farmer_id"),{"order_id":order_id,"farmer_id":farmer_id}).scalar_one()
        latest=connection.execute(text("SELECT status,settled_quantity_kg FROM payment_intents WHERE order_id=:order_id AND farmer_id=:farmer_id ORDER BY created_at DESC LIMIT 1"),{"order_id":order_id,"farmer_id":farmer_id}).first()
    assert count_after==count_before+1
    assert latest==("PENDING",quantity)
