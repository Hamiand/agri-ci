from app.orders.service import order_gate_open
def test_agrici_001_order_gate_exact_target():
    assert order_gate_open(3000,3000)
def test_agrici_001_order_gate_stays_closed_at_2700():
    assert not order_gate_open(2700,3000)
def test_reference_collection_farmer_0047():
    announced=350
    received=327
    grades={"A":220,"B":91,"C":16}
    assert received<=announced
    assert sum(grades.values())==received
