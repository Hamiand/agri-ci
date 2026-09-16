from pathlib import Path


def test_offer_creation_is_idempotent_atomic_and_locks_harvest():
    router = Path("app/offers/router.py").read_text()

    assert 'begin_idempotent(db, user, "/offers"' in router
    assert 'if idem.response_body is not None:' in router
    assert 'select(Harvest).where(Harvest.id == payload.harvest_id).with_for_update()' in router
    assert 'complete_idempotent(db, idem, 201, body)' in router
    assert 'db.commit(' not in router
