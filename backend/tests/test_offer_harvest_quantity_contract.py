from pathlib import Path


def test_offer_creation_locks_harvest_and_caps_cumulative_quantity():
    source = Path("app/offers/router.py").read_text()
    assert ".with_for_update()" in source
    assert "func.sum(Offer.quantity_total_kg)" in source
    assert 'Offer.status != "CANCELLED"' in source
    assert "harvest.estimated_quantity_kg - already_offered" in source
    assert "OFFER_EXCEEDS_HARVEST_AVAILABLE_QUANTITY" in source


def test_offer_creation_keeps_idempotency_and_atomic_completion():
    source = Path("app/offers/router.py").read_text()
    assert "begin_idempotent" in source
    assert "complete_idempotent" in source
    assert "db.commit(" not in source
