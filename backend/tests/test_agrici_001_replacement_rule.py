def choose_replacement(candidates, declined_offer_id, missing):
    selected=[]
    for offer_id,available in candidates:
        if offer_id==declined_offer_id or missing<=0: continue
        qty=min(available,missing)
        if qty>0: selected.append((offer_id,qty));missing-=qty
    return selected
def test_same_previously_used_coop_can_supply_replacement():
    # CoopA was already used for 950 kg, but still has 450 kg available.
    candidates=[("YAO",300),("COOPA",450)]
    assert choose_replacement(candidates,"YAO",300)==[("COOPA",300)]
