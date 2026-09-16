import os
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Match, Offer, Product

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def _auth(client, phone, password):
    response = client.post("/auth/login", json={"phone": phone, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _register(client, phone, password, role):
    response = client.post("/auth/register", json={
        "phone": phone, "password": password, "preferred_language": "fr", "role": role,
    })
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_agrici001_http_security_and_idempotency_smoke(app_client):
    health = app_client.get("/health")
    assert health.status_code == 200
    protected = app_client.get("/farmers/me")
    assert protected.status_code in (401, 403)


def test_mutation_without_auth_is_rejected_before_business_processing(app_client):
    response = app_client.post("/demands/00000000-0000-0000-0000-000000000001/aggregate")
    assert response.status_code in (401, 403)


def test_agrici001_exact_3000kg_authenticated_http_flow(app_client):
    """Reference AGRI-CI-001 commercial flow through authenticated HTTP/PostgreSQL."""
    client = app_client
    suffix = uuid.uuid4().hex[:8]
    password = "Pilot-Test-Password-123!"
    buyer_phone = f"+225010{suffix}"
    farmer_specs = [
        ("Koffi", "400"), ("Awa", "750"), ("Mariam", "600"),
        ("Yao", "300"), ("Cooperative A", "1400"),
    ]

    _register(client, buyer_phone, password, "BUYER")
    buyer_headers = _auth(client, buyer_phone, password)
    buyer_response = client.post("/buyers", headers=buyer_headers, json={
        "display_name": "Acheteur Abidjan", "buyer_type": "WHOLESALER", "city": "Abidjan",
    })
    assert buyer_response.status_code == 201, buyer_response.text

    engine = create_engine(os.environ["TEST_DATABASE_URL"], pool_pre_ping=True)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    product_code = f"T{suffix[:6]}"
    with Session.begin() as db:
        db.add(Product(code=product_code, name_fr="Tomate AGRI-CI-001 HTTP",
                       name_en="AGRI-CI-001 HTTP Tomato", active=True))

    farmer_tokens = {}
    offer_ids = {}
    for index, (name, quantity) in enumerate(farmer_specs):
        phone = f"+22507{index}{suffix}"
        _register(client, phone, password, "FARMER")
        headers = _auth(client, phone, password)
        farmer_tokens[name] = headers
        farmer_response = client.post("/farmers", headers=headers, json={"display_name": name})
        assert farmer_response.status_code == 201, farmer_response.text
        farm_response = client.post("/farms", headers=headers, json={
            "name": f"Exploitation {name}", "locality": f"Village {index + 1}",
        })
        assert farm_response.status_code == 201, farm_response.text
        plot_response = client.post("/plots", headers=headers, json={
            "farm_id": farm_response.json()["id"], "plot_ref": f"P-{suffix}-{index}",
            "name": "Tomate", "area_ha": "1.0",
        })
        assert plot_response.status_code == 201, plot_response.text
        harvest_response = client.post("/harvests", headers=headers, json={
            "plot_id": plot_response.json()["id"], "product_code": product_code,
            "expected_start_date": "2027-05-16", "expected_end_date": "2027-05-18",
            "estimated_quantity_kg": quantity,
        })
        assert harvest_response.status_code == 201, harvest_response.text
        offer_response = client.post("/offers", headers=headers, json={
            "harvest_id": harvest_response.json()["id"], "quantity_kg": quantity,
            "asking_price_xof_per_kg": "760", "quality_grade": "A",
        })
        assert offer_response.status_code == 201, offer_response.text
        offer_ids[name] = uuid.UUID(offer_response.json()["id"])

    demand_response = client.post("/demands", headers=buyer_headers, json={
        "product_code": product_code, "quantity_required_kg": "3000",
        "delivery_start_date": "2027-05-16", "delivery_end_date": "2027-05-18",
        "target_price_xof_per_kg": "760", "quality_grades": ["A", "B"],
        "destination_city": "Abidjan",
    })
    assert demand_response.status_code == 201, demand_response.text
    demand_id = uuid.UUID(demand_response.json()["id"])

    score_by_name = {"Koffi": Decimal("99"), "Awa": Decimal("98"), "Mariam": Decimal("97"),
                     "Yao": Decimal("96"), "Cooperative A": Decimal("95")}
    with Session.begin() as db:
        for name, _ in farmer_specs:
            offer = db.get(Offer, offer_ids[name])
            db.add(Match(demand_id=demand_id, offer_id=offer_ids[name],
                         compatible_quantity_kg=offer.quantity_available_kg,
                         date_score=100, price_score=100, logistics_score=70, quality_score=100,
                         reliability_score=70, volume_score=70, total_score=score_by_name[name],
                         explanation={"reference_scenario": True}))

    aggregate_response = client.post(f"/demands/{demand_id}/aggregate",
        headers={**buyer_headers, "Idempotency-Key": f"agg-{suffix}"})
    assert aggregate_response.status_code == 200, aggregate_response.text
    aggregation_id = uuid.UUID(aggregate_response.json()["aggregation_id"])
    assert aggregate_response.json()["target_quantity_kg"] == 3000.0
    assert aggregate_response.json()["proposed_quantity_kg"] == 3000.0

    aggregation = client.get(f"/aggregations/{aggregation_id}", headers=buyer_headers)
    assert aggregation.status_code == 200, aggregation.text
    initial = {m["farmer_name"]: m["proposed_quantity_kg"] for m in aggregation.json()["members"]}
    assert initial == {"Koffi": 400.0, "Awa": 750.0, "Mariam": 600.0,
                       "Yao": 300.0, "Cooperative A": 950.0}

    premature_order = client.post(f"/orders/from-aggregation/{aggregation_id}",
        headers={**buyer_headers, "Idempotency-Key": f"order-early-{suffix}"})
    assert premature_order.status_code == 409
    assert premature_order.json()["error"]["code"] == "ORDER_GATE_NOT_READY"

    yao_commitments = client.get("/commitments", headers=farmer_tokens["Yao"])
    assert yao_commitments.status_code == 200, yao_commitments.text
    yao_pending = [c for c in yao_commitments.json() if c["status"] == "PENDING"]
    assert len(yao_pending) == 1
    decline = client.post(f"/commitments/{yao_pending[0]['id']}/decline",
        headers={**farmer_tokens["Yao"], "Idempotency-Key": f"decline-yao-{suffix}"})
    assert decline.status_code == 200, decline.text
    assert decline.json()["returned_to_available_kg"] == 300.0
    assert decline.json()["replacement_proposed_kg"] == 300.0

    for name in ["Koffi", "Awa", "Mariam", "Cooperative A"]:
        commitments = client.get("/commitments", headers=farmer_tokens[name])
        assert commitments.status_code == 200, commitments.text
        pending = [c for c in commitments.json() if c["status"] == "PENDING"]
        assert len(pending) == (2 if name == "Cooperative A" else 1), (name, commitments.json())
        for item in pending:
            accepted = client.post(f"/commitments/{item['id']}/accept", headers={
                **farmer_tokens[name], "Idempotency-Key": f"accept-{item['id']}",
            })
            assert accepted.status_code == 200, accepted.text

    final_aggregation = client.get(f"/aggregations/{aggregation_id}", headers=buyer_headers)
    assert final_aggregation.status_code == 200, final_aggregation.text
    assert final_aggregation.json()["accepted_quantity_kg"] == 3000.0
    assert final_aggregation.json()["status"] == "CONFIRMED"

    order_response = client.post(f"/orders/from-aggregation/{aggregation_id}",
        headers={**buyer_headers, "Idempotency-Key": f"order-final-{suffix}"})
    assert order_response.status_code == 201, order_response.text
    order = order_response.json()
    assert order["status"] == "CONFIRMED"
    assert order["quantity_kg"] == 3000.0
    assert sum(item["quantity_kg"] for item in order["allocations"]) == 3000.0

    replay = client.post(f"/orders/from-aggregation/{aggregation_id}",
        headers={**buyer_headers, "Idempotency-Key": f"order-final-{suffix}"})
    assert replay.status_code == 201, replay.text
    assert replay.json()["order_id"] == order["order_id"]
