from decimal import Decimal

def aggregate(target,offers):
    remaining=Decimal(target);proposals=[];left={}
    for name,qty in offers:
        qty=Decimal(qty);take=min(qty,remaining)
        if take>0: proposals.append([name,take])
        left[name]=qty-take;remaining-=take
    return proposals,left,remaining

def test_agrici_001_3000kg_reference_scenario():
    offers=[("Koffi","400"),("Awa","750"),("Mariam","600"),("Yao","300"),("CoopA","1400")]
    proposals,left,missing=aggregate("3000",offers)
    assert proposals==[["Koffi",Decimal("400")],["Awa",Decimal("750")],
                       ["Mariam",Decimal("600")],["Yao",Decimal("300")],
                       ["CoopA",Decimal("950")]]
    assert missing==0
    # Yao declines; 2,700 kg remain accepted.
    accepted=sum(q for n,q in proposals if n!="Yao")
    assert accepted==Decimal("2700")
    # Cooperative A had 450 kg outside the initial proposal; replace 300 kg.
    replacement=min(Decimal("3000")-accepted,left["CoopA"])
    assert replacement==Decimal("300")
    accepted+=replacement
    assert accepted==Decimal("3000")
    # Order gate can now open for exactly 3,000 kg.
    assert accepted>=Decimal("3000")
