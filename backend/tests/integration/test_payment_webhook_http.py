import hashlib
import hmac
import json
import os

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


def test_signed_webhook_failed_then_retry_eligible():
    os.environ["PAYMENT_WEBHOOK_SECRET"]="integration-webhook-secret"
    from app.main import app
    from app.payments.router import _already_settled_quantity_by_farmer
    from app.database.session import SessionLocal

    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)
    with engine.begin() as connection:
        row=connection.execute(text("SELECT id,order_id,farmer_id,settled_quantity_kg FROM payment_intents WHERE status='PENDING' AND settled_quantity_kg IS NOT NULL ORDER BY created_at DESC LIMIT 1")).first()
    assert row is not None,"AGRI-CI-001 must leave a pending settlement payment"
    payment_id,order_id,farmer_id,quantity=row

    client=TestClient(app)
    payload={"event":"payment.failed","payment_id":str(payment_id),"provider_reference":"FAIL-HTTP-001"}

    bad=client.post("/payment-webhooks/provider",json=payload,headers={"X-Signature":"bad"})
    assert bad.status_code==401
    assert bad.json()["error"]["code"]=="INVALID_WEBHOOK_SIGNATURE"

    response=_signed_post(client,payload,"integration-webhook-secret")
    assert response.status_code==200
    assert response.json()=={"accepted":True,"event":"payment.failed"}

    with engine.begin() as connection:
        state=connection.execute(text("SELECT status,provider_reference FROM payment_intents WHERE id=:id"),{"id":payment_id}).first()
    assert state==("FAILED","FAIL-HTTP-001")

    # The failed attempt must no longer reserve its represented kilograms.
    with SessionLocal() as db:
        reserved=_already_settled_quantity_by_farmer(db,order_id)
    assert reserved.get(farmer_id,0) < quantity or farmer_id not in reserved


def test_signed_webhook_refund_requires_success():
    os.environ["PAYMENT_WEBHOOK_SECRET"]="integration-webhook-secret"
    from app.main import app

    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)
    with engine.begin() as connection:
        row=connection.execute(text("SELECT id FROM payment_intents WHERE status='PENDING' ORDER BY created_at DESC LIMIT 1")).first()
    assert row is not None
    payment_id=row[0]
    client=TestClient(app)

    premature=_signed_post(client,{"event":"payment.refunded","payment_id":str(payment_id),"provider_reference":"REFUND-EARLY"},"integration-webhook-secret")
    assert premature.status_code==409
    assert premature.json()["error"]["code"]=="PAYMENT_NOT_SUCCESSFUL"

    success=_signed_post(client,{"event":"payment.success","payment_id":str(payment_id),"provider_reference":"SUCCESS-HTTP-001"},"integration-webhook-secret")
    assert success.status_code==200

    refund=_signed_post(client,{"event":"payment.refunded","payment_id":str(payment_id),"provider_reference":"REFUND-HTTP-001"},"integration-webhook-secret")
    assert refund.status_code==200
    with engine.begin() as connection:
        state=connection.execute(text("SELECT status,provider_reference FROM payment_intents WHERE id=:id"),{"id":payment_id}).first()
    assert state==("REFUNDED","REFUND-HTTP-001")
