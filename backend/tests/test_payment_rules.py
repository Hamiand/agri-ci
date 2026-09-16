from decimal import Decimal
import pytest
from app.payments.service import compute_net

def test_reference_farmer_payment():
    gross=Decimal("150000")
    deductions=[Decimal("7000"),Decimal("4500"),Decimal("1500")]
    assert compute_net(gross,deductions)==Decimal("137000")

def test_deductions_cannot_exceed_gross():
    with pytest.raises(ValueError):
        compute_net(Decimal("1000"),[Decimal("1001")])
