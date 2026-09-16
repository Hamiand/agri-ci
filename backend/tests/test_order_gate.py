from decimal import Decimal
from app.orders.service import order_gate_open

def test_2999_does_not_open_3000_gate():
    assert not order_gate_open(Decimal("2999"),Decimal("3000"))

def test_3000_opens_3000_gate():
    assert order_gate_open(Decimal("3000"),Decimal("3000"))
