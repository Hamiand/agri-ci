from app.core.idempotency_service import complete_idempotent
class Row:
    response_status=None
    response_body=None
class DB:
    committed=False
    def commit(self):self.committed=True
def test_complete_idempotent_persists_and_commits():
    db=DB();row=Row();body={"ok":True,"quantity_kg":3000}
    out=complete_idempotent(db,row,201,body)
    assert out==body
    assert row.response_status==201
    assert row.response_body==body
    assert db.committed
