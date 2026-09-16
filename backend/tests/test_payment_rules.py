import uuid
from decimal import Decimal
import pytest
from app.payments.service import compute_net
from app.payments.router import _allocate_money_exact

def test_reference_farmer_payment():
    gross=Decimal("150000")
    deductions=[Decimal("7000"),Decimal("4500"),Decimal("1500")]
    assert compute_net(gross,deductions)==Decimal("137000")

def test_deductions_cannot_exceed_gross():
    with pytest.raises(ValueError):
        compute_net(Decimal("1000"),[Decimal("1001")])

def test_proportional_money_allocation_preserves_exact_total_with_rounding():
    farmers=[(uuid.UUID(int=1),Decimal("1")),(uuid.UUID(int=2),Decimal("1")),(uuid.UUID(int=3),Decimal("1"))]
    parts=_allocate_money_exact(Decimal("100.00"),farmers)
    assert sum(parts.values(),Decimal("0"))==Decimal("100.00")
    assert sorted(parts.values())==[Decimal("33.33"),Decimal("33.33"),Decimal("33.34")]

def test_agrici001_deduction_totals_are_preserved_exactly():
    weights=[(uuid.UUID(int=1),Decimal("400")),(uuid.UUID(int=2),Decimal("750")),(uuid.UUID(int=3),Decimal("600")),(uuid.UUID(int=4),Decimal("1250"))]
    assert sum(_allocate_money_exact(Decimal("70000"),weights).values(),Decimal("0"))==Decimal("70000.00")
    assert sum(_allocate_money_exact(Decimal("45000"),weights).values(),Decimal("0"))==Decimal("45000.00")
    assert sum(_allocate_money_exact(Decimal("15000"),weights).values(),Decimal("0"))==Decimal("15000.00")
