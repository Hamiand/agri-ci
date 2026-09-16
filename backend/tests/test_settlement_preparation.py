from decimal import Decimal
def test_reference_single_farmer_net():
    received=Decimal("300")
    price=Decimal("500")
    gross=received*price
    assert gross==Decimal("150000")
    assert gross-Decimal("7000")-Decimal("4500")-Decimal("1500")==Decimal("137000")
def test_partial_collection_changes_gross():
    announced=Decimal("350")
    received=Decimal("327")
    price=Decimal("500")
    assert received<announced
    assert received*price==Decimal("163500")
