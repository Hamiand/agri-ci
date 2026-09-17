from pathlib import Path


def test_lot_creation_locks_sources_and_rejects_duplicate_payload_ids():
    router = Path("app/logistics/router.py").read_text()
    migration = Path("migrations/versions/0015_lot_source_uniqueness.py").read_text()

    assert "requested_ids=sorted(set(p.quality_check_ids),key=str)" in router
    assert 'detail="DUPLICATE_QUALITY_CHECK"' in router
    assert "QualityCheck.id.in_(requested_ids)" in router
    assert ".with_for_update()" in router
    assert 'detail="QUALITY_CHECK_ALREADY_LOTTED"' in router
    assert '"uq_lot_source_quality_check"' in migration
    assert '"quality_check_id"' in migration

    # Lot creation remains one application transaction with its replay record.
    lot_section = router.split('@router.post("/lots",status_code=201)', 1)[1].split("class TransportCreate", 1)[0]
    assert 'begin_idempotent(db,user,"/lots"' in lot_section
    assert "if idem.response_body is not None:return idem.response_body" in lot_section
    assert "complete_idempotent(db,idem,201,body)" in lot_section
    assert "db.commit(" not in lot_section
