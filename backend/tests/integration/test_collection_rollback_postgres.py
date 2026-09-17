import os
import uuid
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import sessionmaker

from app.core.idempotency_service import begin_idempotent
from app.database.models import CollectionEvent, OrderAllocation, Role, User, UserRole

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def _register_ops(client):
    suffix=uuid.uuid4().hex[:8]
    phone=f"+225099{suffix}"
    password="Pilot-Test-Password-123!"
    reg=client.post("/auth/register",json={"phone":phone,"password":password,"preferred_language":"fr","role":"OPERATIONS_MANAGER"})
    assert reg.status_code==201,reg.text
    login=client.post("/auth/login",json={"phone":phone,"password":password})
    assert login.status_code==200,login.text
    return reg.json()["id"],{"Authorization":f"Bearer {login.json()['access_token']}"}


def test_failed_collection_mutation_rolls_back_business_and_idempotency_rows():
    """A rejected collection must leave neither business data nor a stuck replay row."""
    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)
    Session=sessionmaker(bind=engine,expire_on_commit=False)

    with Session() as db:
        allocation=db.scalar(select(OrderAllocation).order_by(OrderAllocation.created_at.desc()))
        user=db.scalar(
            select(User)
            .join(UserRole,UserRole.user_id==User.id)
            .join(Role,Role.id==UserRole.role_id)
            .where(Role.name.in_(["COLLECTION_AGENT","OPERATIONS_MANAGER","ADMIN"]))
            .limit(1)
        )
        assert allocation is not None and user is not None,"AGRI-CI-001 fixtures required"
        before=db.scalar(select(func.count(CollectionEvent.id)).where(CollectionEvent.order_allocation_id==allocation.id))
        key=f"rollback-proof-{uuid.uuid4()}"
        payload={"order_allocation_id":str(allocation.id),"received_quantity_kg":"999999.000","location_name":"rollback-proof"}

        try:
            begin_idempotent(db,user,"/collection",key,payload)
            locked=db.scalar(select(OrderAllocation).where(OrderAllocation.id==allocation.id).with_for_update())
            assert locked is not None
            already=db.scalar(select(func.coalesce(func.sum(CollectionEvent.received_quantity_kg),0)).where(CollectionEvent.order_allocation_id==allocation.id))
            if Decimal(already)+Decimal(payload["received_quantity_kg"])>Decimal(locked.quantity_kg):
                raise HTTPException(status_code=409,detail="COLLECTION_EXCEEDS_ALLOCATION")
            pytest.fail("oversized collection should have been rejected")
        except HTTPException as exc:
            assert exc.status_code==409
            db.rollback()

        after=db.scalar(select(func.count(CollectionEvent.id)).where(CollectionEvent.order_allocation_id==allocation.id))
        assert after==before

        retry=begin_idempotent(db,user,"/collection",key,payload)
        assert retry.response_body is None
        db.rollback()


def test_http_exception_rolls_back_request_session_and_idempotency_row(app_client):
    """FastAPI's get_db dependency must rollback the transaction after a rejected mutation."""
    client=app_client
    user_id,headers=_register_ops(client)
    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)

    with engine.begin() as connection:
        allocation=connection.execute(text("SELECT id,quantity_kg FROM order_allocations ORDER BY created_at DESC LIMIT 1")).first()
        assert allocation is not None,"AGRI-CI-001 fixtures required"
        allocation_id,allocated_quantity=allocation
        before=connection.execute(text("SELECT count(*) FROM collection_events WHERE order_allocation_id=:id"),{"id":allocation_id}).scalar_one()

    key=f"http-rollback-{uuid.uuid4()}"
    payload={"order_allocation_id":str(allocation_id),"received_quantity_kg":str(Decimal(allocated_quantity)+Decimal("999999")),"location_name":"HTTP rollback proof"}
    request_headers={**headers,"Idempotency-Key":key}

    first=client.post("/collection",headers=request_headers,json=payload)
    assert first.status_code==409,first.text
    assert first.json()["error"]["code"]=="COLLECTION_EXCEEDS_ALLOCATION"

    with engine.begin() as connection:
        after=connection.execute(text("SELECT count(*) FROM collection_events WHERE order_allocation_id=:id"),{"id":allocation_id}).scalar_one()
        poison=connection.execute(text("SELECT count(*) FROM idempotency_keys WHERE user_id=:user_id AND endpoint='/collection' AND key=:key"),{"user_id":uuid.UUID(user_id),"key":key}).scalar_one()
    assert after==before
    assert poison==0

    # The exact same request/key must reach the business rule again. If rollback
    # failed, begin_idempotent would instead return IDEMPOTENT_REQUEST_IN_PROGRESS.
    second=client.post("/collection",headers=request_headers,json=payload)
    assert second.status_code==409,second.text
    assert second.json()["error"]["code"]=="COLLECTION_EXCEEDS_ALLOCATION"

    with engine.begin() as connection:
        poison_after_retry=connection.execute(text("SELECT count(*) FROM idempotency_keys WHERE user_id=:user_id AND endpoint='/collection' AND key=:key"),{"user_id":uuid.UUID(user_id),"key":key}).scalar_one()
    assert poison_after_retry==0
