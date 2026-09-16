from decimal import Decimal

def proposal_plan(target,available):
    remaining=Decimal(target);out=[]
    for name,qty in available:
        if remaining<=0:break
        take=min(Decimal(qty),remaining);out.append((name,take));remaining-=take
    return out,remaining

def test_reference_initial_3000kg_plan():
    plan,missing=proposal_plan("3000",[("Koffi","400"),("Awa","750"),("Mariam","600"),("Yao","300"),("CoopA","1400")])
    assert plan==[("Koffi",Decimal("400")),("Awa",Decimal("750")),("Mariam",Decimal("600")),
                 ("Yao",Decimal("300")),("CoopA",Decimal("950"))]
    assert missing==0

def test_yahoo_decline_can_be_replaced_from_coop_reserve():
    accepted=Decimal("3000")-Decimal("300")
    coop_remaining=Decimal("1400")-Decimal("950")
    replacement=min(Decimal("3000")-accepted,coop_remaining)
    assert accepted+replacement==Decimal("3000")
    assert replacement==Decimal("300")
