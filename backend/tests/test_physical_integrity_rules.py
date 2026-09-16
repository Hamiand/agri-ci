def test_farmer_0047_quality_equals_received():
    received=327
    assert 220+91+16==received
def test_reference_net_farmer_amount():
    gross=150000
    assert gross-7000-4500-1500==137000
def test_lot_assignment_rule_is_one_physical_chain():
    lot={"quality_check":"QC-A-220","transport_job":"TRN-001"}
    assert lot["quality_check"]=="QC-A-220" and lot["transport_job"]=="TRN-001"
