from pathlib import Path


def test_failed_and_refunded_payment_quantities_do_not_block_retry_settlement():
    router = Path("app/payments/router.py").read_text()
    settled_query = router.split("def _already_settled_quantity_by_farmer", 1)[1].split("@router.post", 1)[0]

    # Only payment states that still reserve money/quantity may count as already
    # settled. Inspect the ORM query contract without depending on raw-SQL syntax.
    assert 'PaymentIntent.status.in_(["PENDING","PROCESSING","SUCCESS","DISPUTED"])' in settled_query
    assert "FAILED" not in settled_query
    assert "REFUNDED" not in settled_query
    assert "func.sum(PaymentIntent.settled_quantity_kg)" in settled_query
    assert "delivered_qty-already_settled.get" in router
    assert "NO_NEW_DELIVERED_QUANTITY_TO_SETTLE" in router
