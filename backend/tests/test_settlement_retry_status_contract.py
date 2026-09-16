from pathlib import Path


def test_failed_and_refunded_payment_quantities_do_not_block_retry_settlement():
    router = Path("app/payments/router.py").read_text()
    settled_query = router.split("def _already_settled_quantity_by_farmer", 1)[1].split("@router.post", 1)[0]

    # Inspect the executable SQL contract rather than comments: only payment
    # states that still reserve money/quantity may count as already settled.
    sql = settled_query.split('rows=db.execute(text("', 1)[1].split('"),{"order_id"', 1)[0]
    assert "status IN ('PENDING','PROCESSING','SUCCESS','DISPUTED')" in sql
    assert "FAILED" not in sql
    assert "REFUNDED" not in sql
    assert "delivered_qty-already_settled.get" in router
    assert "NO_NEW_DELIVERED_QUANTITY_TO_SETTLE" in router
