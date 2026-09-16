from dataclasses import dataclass
@dataclass
class Offer:
    name:str;available:int;proposed:int=0;reserved:int=0
def propose(o,kg):
    assert o.available>=kg;o.available-=kg;o.proposed+=kg
def accept(o,kg):
    assert o.proposed>=kg;o.proposed-=kg;o.reserved+=kg
def decline(o,kg):
    assert o.proposed>=kg;o.proposed-=kg;o.available+=kg
def test_agrici001_exact_commercial_state_machine():
    x={n:Offer(n,q) for n,q in [("Koffi",400),("Awa",750),("Mariam",600),("Yao",300),("CoopA",1400)]}
    initial={"Koffi":400,"Awa":750,"Mariam":600,"Yao":300,"CoopA":950}
    for n,q in initial.items():propose(x[n],q)
    assert sum(o.proposed for o in x.values())==3000
    for n in ["Koffi","Awa","Mariam","CoopA"]:accept(x[n],initial[n])
    decline(x["Yao"],300)
    assert sum(o.reserved for o in x.values())==2700
    assert x["CoopA"].available==450
    propose(x["CoopA"],300);accept(x["CoopA"],300)
    assert sum(o.reserved for o in x.values())==3000
    assert x["CoopA"].available==150
    received=327;grades={"A":220,"B":91,"C":16}
    assert sum(grades.values())==received
    gross=150000;deductions=7000+4500+1500
    assert gross-deductions==137000
