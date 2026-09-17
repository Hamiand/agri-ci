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

    The authenticated AGRI-CI-001 HTTP flow runs earlier in this integration suite
    and creates real orders, farmers and payment intents. Reuse one valid
    order/farmer ownership pair so this proof exercises PostgreSQL with all foreign
    keys enabled rather than weakening database integrity for the test.
    """
    engine = create_engine(os.environ["TEST_DATABASE_URL"], pool_pre_ping=True)
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            seed = connection.execute(
                text("SELECT order_id, farmer_id FROM payment_intents ORDER BY created_at LIMIT 1")
            ).first()
            assert seed is not None, "AGRI-CI-001 payment fixture must exist"
            order_id, farmer_id = seed

            # Isolate this proof from the payments created by the full E2E flow.
            connection.execute(
                text("DELETE FROM ledger_entries WHERE payment_intent_id IN (SELECT id FROM payment_intents WHERE order_id=:order_id)"),
                {"order_id": order_id},
            )
            connection.execute(
                text("DELETE FROM payment_deductions WHERE payment_intent_id IN (SELECT id FROM payment_intents WHERE order_id=:order_id)"),
                {"order_id": order_id},
            )
            connection.execute(text("DELETE FROM payment_intents WHERE order_id=:order_id"), {"order_id": order_id})

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
