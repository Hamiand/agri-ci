from pathlib import Path


def test_partial_delivery_keeps_transport_in_transit_until_full_capacity():
    router = Path("app/deliveries/router.py").read_text()

    # A partial receipt is recorded, but the truck/lot lifecycle closes only
    # when cumulative delivered quantity equals transported capacity.
    assert 'if Decimal(already)+p.delivered_quantity_kg==Decimal(capacity):' in router
    assert 'job.status="DELIVERED"' in router
    assert 'lot.status="DELIVERED"' in router
    assert 'if job.status!="IN_TRANSIT"' in router

    # Delivery creation is idempotent and its business mutation is committed
    # together with the replayable response.
    assert 'begin_idempotent(db,user,"/deliveries"' in router
    assert 'if idem.response_body is not None:return idem.response_body' in router
    assert 'complete_idempotent(db,idem,201,body)' in router
    assert 'db.commit(' not in router
