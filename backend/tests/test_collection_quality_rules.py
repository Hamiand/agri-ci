from decimal import Decimal

def test_farmer_0047_reference_weighing():
    announced=Decimal("350");received=Decimal("327")
    grades={"A":Decimal("220"),"B":Decimal("91"),"C":Decimal("16")}
    assert received<=announced
    assert sum(grades.values())==received

def test_quality_cannot_exceed_received():
    received=Decimal("327")
    graded=Decimal("320")
    next_grade=Decimal("8")
    assert graded+next_grade>received
