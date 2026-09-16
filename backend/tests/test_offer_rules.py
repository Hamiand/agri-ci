from decimal import Decimal

def can_offer(estimated, already_offered, requested):
    return requested > 0 and requested <= (estimated - already_offered)

def test_koffi_can_offer_400_from_500():
    assert can_offer(Decimal("500"), Decimal("0"), Decimal("400"))

def test_farmer_cannot_offer_more_than_remaining_harvest():
    assert not can_offer(Decimal("500"), Decimal("400"), Decimal("101"))
