import os
import uuid
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.core.idempotency_service import begin_idempotent
from app.database.models import CollectionEvent, OrderAllocation, Role, User, UserRole

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


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

        # The same key must be usable again after rollback: no IN_PROGRESS poison row survived.
        retry=begin_idempotent(db,user,"/collection",key,payload)
        assert retry.response_body is None
        db.rollback()
