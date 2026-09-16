from pathlib import Path


def test_failed_and_refunded_payment_quantities_do_not_block_retry_settlement():
    router = Path("app/payments/router.py").read_text()

    assert "status IN ('PENDING','PROCESSING','SUCCESS','DISPUTED')" in router
    settled_query = router.split("def _already_settled_quantity_by_farmer", 1)[1].split("@router.post", 1)[0]
    assert "FAILED" not in settled_query
    assert "REFUNDED" not in settled_query
    assert "delivered_qty-already_settled.get" in router
    assert "NO_NEW_DELIVERED_QUANTITY_TO_SETTLE" in router
