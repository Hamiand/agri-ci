import os
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.payments.router import _already_settled_quantity_by_farmer

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def test_failed_and_refunded_payments_release_quantity_for_retry():
    """Commercial invariant: failed/refunded attempts must not consume delivered kg.

    PENDING/PROCESSING/SUCCESS/DISPUTED still reserve their represented quantity,
    while FAILED/REFUNDED become eligible for a new settlement attempt.
    """
    engine = create_engine(os.environ["TEST_DATABASE_URL"], pool_pre_ping=True)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    order_id = uuid.uuid4()
    farmer_id = uuid.uuid4()

    # This test exercises the real PostgreSQL query used by settlement preparation.
    # Foreign keys make isolated inserts intentionally cumbersome, so use the
    # already-migrated table inside one rolled-back transaction with constraints
    # deferred only for this test fixture.
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET CONSTRAINTS ALL DEFERRED"))
            statuses = [
                ("PENDING", Decimal("10.000")),
                ("PROCESSING", Decimal("20.000")),
                ("SUCCESS", Decimal("30.000")),
                ("DISPUTED", Decimal("40.000")),
                ("FAILED", Decimal("50.000")),
                ("REFUNDED", Decimal("60.000")),
            ]
            for index, (status, qty) in enumerate(statuses):
                connection.execute(
                    text(
                        "INSERT INTO payment_intents "
                        "(id,payment_ref,order_id,farmer_id,gross_amount_xof,deductions_xof,net_amount_xof,currency,provider,status,settled_quantity_kg,created_at,updated_at) "
                        "VALUES (:id,:ref,:order_id,:farmer_id,1,0,1,'XOF','TEST',:status,:qty,now(),now())"
                    ),
                    {
                        "id": uuid.uuid4(),
                        "ref": f"PAY-RETRY-{index}-{uuid.uuid4().hex[:6]}",
                        "order_id": order_id,
                        "farmer_id": farmer_id,
                        "status": status,
                        "qty": qty,
                    },
                )

            db = Session(bind=connection)
            try:
                reserved = _already_settled_quantity_by_farmer(db, order_id)
            finally:
                db.close()

            # Only 10+20+30+40 kg remain reserved. FAILED 50 kg and REFUNDED
            # 60 kg are deliberately absent, making 110 kg payable again.
            assert reserved == {farmer_id: Decimal("100.000")}
        finally:
            transaction.rollback()
