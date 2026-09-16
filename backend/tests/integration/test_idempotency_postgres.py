import os,uuid,pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import User
from app.core.idempotency_service import begin_idempotent,complete_idempotent
pytestmark=[pytest.mark.integration,pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="TEST_DATABASE_URL required")]

def test_completed_response_is_replayed_and_payload_change_rejected():
    engine=create_engine(os.environ["TEST_DATABASE_URL"],pool_pre_ping=True)
    Session=sessionmaker(bind=engine,expire_on_commit=False)
    suffix=uuid.uuid4().hex[:10]
    with Session.begin() as db:
        u=User(phone=f"+22505{suffix}",password_hash="test",preferred_language="fr",status="ACTIVE")
        db.add(u);db.flush();uid=u.id
    key=f"idem-{suffix}"; endpoint="/test/quantity"; payload={"quantity_kg":400}
    with Session() as db:
        u=db.get(User,uid)
        row=begin_idempotent(db,u,endpoint,key,payload)
        assert row.response_body is None
        complete_idempotent(db,row,201,{"reserved_kg":400})
    with Session() as db:
        u=db.get(User,uid)
        replay=begin_idempotent(db,u,endpoint,key,payload)
        assert replay.response_status==201
        assert replay.response_body=={"reserved_kg":400}
    with Session() as db:
        u=db.get(User,uid)
        with pytest.raises(Exception):
            begin_idempotent(db,u,endpoint,key,{"quantity_kg":401})
