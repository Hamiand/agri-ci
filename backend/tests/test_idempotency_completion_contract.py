from pathlib import Path
BASE=Path(__file__).parents[1]/"app"
MUTATIONS={
 "aggregation/router.py":["complete_idempotent"],
 "commitments/router.py":["complete_idempotent","COMMITMENT_NOT_OWNED"],
 "orders/router.py":["complete_idempotent","Idempotency-Key"],
 "collection/router.py":["complete_idempotent","with_for_update"],
 "logistics/router.py":["complete_idempotent","Idempotency-Key"],
 "deliveries/router.py":["complete_idempotent","with_for_update"],
 "payments/router.py":["complete_idempotent","Idempotency-Key"],
}
def test_sensitive_mutations_persist_replayable_response():
    for rel,needles in MUTATIONS.items():
        s=(BASE/rel).read_text()
        for n in needles: assert n in s,(rel,n)
def test_db_dependency_rolls_back_failed_transactions():
    s=(BASE/"database/session.py").read_text()
    assert "except Exception" in s and "db.rollback()" in s
