import uuid

import pytest
from fastapi import HTTPException

from app.aggregation.router import _require_aggregation_buyer
from app.database.models import Aggregation, Buyer, Demand, User


class FakeDB:
    def __init__(self, demand, buyer):
        self.demand = demand
        self.buyer = buyer

    def get(self, model, object_id):
        return self.demand if model is Demand and self.demand.id == object_id else None

    def scalar(self, statement):
        return self.buyer


def _objects(owner=True):
    buyer_id = uuid.uuid4()
    buyer = Buyer(
        id=buyer_id,
        user_id=uuid.uuid4(),
        buyer_ref="BUY-AUTH-TEST",
        display_name="Buyer",
        buyer_type="WHOLESALER",
        status="ACTIVE",
    )
    demand = Demand(
        id=uuid.uuid4(),
        demand_ref="DEM-AUTH-TEST",
        buyer_id=buyer_id if owner else uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity_required_kg=100,
        delivery_start_date=__import__("datetime").date(2027, 5, 16),
        delivery_end_date=__import__("datetime").date(2027, 5, 18),
        quality_grades=["A"],
        status="PUBLISHED",
    )
    aggregation = Aggregation(
        aggregation_ref="AGG-AUTH-TEST",
        demand_id=demand.id,
        target_quantity_kg=100,
        proposed_quantity_kg=100,
        accepted_quantity_kg=0,
        status="AWAITING_COMMITMENTS",
    )
    user = User(id=buyer.user_id, phone="+2250100000000", password_hash="test-only", status="ACTIVE")
    return FakeDB(demand, buyer), user, aggregation, buyer


def test_owning_buyer_can_read_aggregation():
    db, user, aggregation, buyer = _objects(owner=True)
    assert _require_aggregation_buyer(db, user, aggregation) is buyer


def test_non_owner_is_denied_aggregation_details():
    db, user, aggregation, _ = _objects(owner=False)
    with pytest.raises(HTTPException) as exc:
        _require_aggregation_buyer(db, user, aggregation)
    assert exc.value.status_code == 403
    assert exc.value.detail == "AGGREGATION_ACCESS_DENIED"
