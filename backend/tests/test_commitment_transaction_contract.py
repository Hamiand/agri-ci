from pathlib import Path


def test_commitment_mutations_use_idempotent_application_transaction_boundary():
    router = Path("app/commitments/router.py").read_text()
    aggregation_service = Path("app/aggregation/service.py").read_text()

    # Both sensitive farmer decisions must be replay-safe before any stock mutation.
    assert 'begin_idempotent(db, user, f"/commitments/{commitment_id}/accept"' in router
    assert 'begin_idempotent(db, user, f"/commitments/{commitment_id}/decline"' in router
    assert router.count("if idem.response_body is not None:") >= 2
    assert router.count("complete_idempotent(db, idem, 200, body)") == 2

    # No inner commit may split stock/aggregation changes from the idempotency response.
    assert "db.commit(" not in router
    assert "db.commit(" not in aggregation_service
