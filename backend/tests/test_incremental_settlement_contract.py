from pathlib import Path


def test_incremental_settlement_tracks_and_subtracts_already_settled_quantity():
    router = Path("app/payments/router.py").read_text()
    migration = Path("migrations/versions/0013_payment_settlement_quantity.py").read_text()
    models = Path("app/database/models.py").read_text()

    assert 'settled_quantity_kg' in migration
    assert 'settled_quantity_kg: Mapped[Decimal|None]' in models
    assert 'def _already_settled_quantity_by_farmer' in router
    assert 'func.sum(PaymentIntent.settled_quantity_kg)' in router
    assert 'delivered_qty-already_settled.get' in router
    assert 'NO_NEW_DELIVERED_QUANTITY_TO_SETTLE' in router
    assert 'allow_additional=True' in router
    assert '.with_for_update()' in router
    assert '"settlement_basis":"DELIVERED_QUANTITY"' in router
    assert '"settlement_mode":"INCREMENTAL_UNSETTLED_QUANTITY"' in router
