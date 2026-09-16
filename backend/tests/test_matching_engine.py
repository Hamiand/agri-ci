from datetime import date
from decimal import Decimal
from app.matching.engine import date_compatible,score_candidate

def test_date_overlap():
    assert date_compatible(date(2027,5,15),date(2027,5,18),date(2027,5,16),date(2027,5,18))

def test_incompatible_dates():
    assert not date_compatible(date(2027,5,1),date(2027,5,10),date(2027,5,16),date(2027,5,18))

def test_score_is_explainable_and_bounded():
    parts,total=score_candidate(available=Decimal("400"),required=Decimal("3000"),
        asking=Decimal("740"),target=Decimal("760"),grade="A",required_grades=["A","B"])
    assert set(parts)=={"date","price","logistics","quality","reliability","volume"}
    assert Decimal("0") <= total <= Decimal("100")
