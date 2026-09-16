import os
import threading
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.core.idempotency_service import begin_idempotent, complete_idempotent
from app.database.models import IdempotencyKey, User

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def _session_factory():
    engine = create_engine(os.environ["TEST_DATABASE_URL"], pool_pre_ping=True)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)


def test_completed_response_is_replayed_and_payload_change_rejected():
    engine, Session = _session_factory()
    suffix = uuid.uuid4().hex[:10]
    with Session.begin() as db:
        u = User(phone=f"+22505{suffix}", password_hash="test", preferred_language="fr", status="ACTIVE")
        db.add(u)
        db.flush()
        uid = u.id
    key = f"idem-{suffix}"
    endpoint = "/test/quantity"
    payload = {"quantity_kg": 400}
    with Session() as db:
        u = db.get(User, uid)
        row = begin_idempotent(db, u, endpoint, key, payload)
        assert row.response_body is None
        complete_idempotent(db, row, 201, {"reserved_kg": 400})
    with Session() as db:
        u = db.get(User, uid)
        replay = begin_idempotent(db, u, endpoint, key, payload)
        assert replay.response_status == 201
        assert replay.response_body == {"reserved_kg": 400}
    with Session() as db:
        u = db.get(User, uid)
        with pytest.raises(HTTPException) as exc:
            begin_idempotent(db, u, endpoint, key, {"quantity_kg": 401})
        assert exc.value.status_code == 409
        assert exc.value.detail == "IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_REQUEST"
    engine.dispose()


def test_concurrent_first_use_creates_one_operation_and_replays_one_response():
    """Concurrent first use may replay after the winner commits, but never executes twice."""
    engine, Session = _session_factory()
    suffix = uuid.uuid4().hex[:10]
    with Session.begin() as db:
        user = User(phone=f"+22506{suffix}", password_hash="test", preferred_language="fr", status="ACTIVE")
        db.add(user)
        db.flush()
        uid = user.id

    key = f"race-{suffix}"
    endpoint = "/test/concurrent-first-use"
    payload = {"quantity_kg": 400}
    barrier = threading.Barrier(2)
    results = []
    lock = threading.Lock()

    def worker(worker_id):
        with Session() as db:
            user = db.get(User, uid)
            barrier.wait(timeout=10)
            try:
                row = begin_idempotent(db, user, endpoint, key, payload)
                if row.response_body is not None:
                    # The competing request lost the INSERT race, waited for the
                    # winner to commit, and receives the winner's persisted reply.
                    result = ("replayed", row.response_body)
                else:
                    body = {"worker": worker_id, "reserved_kg": 400}
                    returned = complete_idempotent(db, row, 201, body)
                    result = ("executed", returned)
            except HTTPException as exc:
                db.rollback()
                result = ("http", exc.status_code, exc.detail)
            except Exception as exc:  # pragma: no cover - diagnostic if DB semantics regress
                db.rollback()
                result = ("unexpected", type(exc).__name__, str(exc))
        with lock:
            results.append(result)

    threads = [threading.Thread(target=worker, args=(i,)) for i in (1, 2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
        assert not thread.is_alive(), "Concurrent idempotency test deadlocked"

    assert not [r for r in results if r[0] == "unexpected"], results
    assert len(results) == 2, results
    executed = [r for r in results if r[0] == "executed"]
    replayed = [r for r in results if r[0] == "replayed"]
    in_progress = [r for r in results if r[0] == "http"]
    assert len(executed) == 1, results
    # Depending on PostgreSQL scheduling, the loser either observes the
    # completed response or receives an in-progress conflict. Both are safe.
    assert len(replayed) + len(in_progress) == 1, results
    if replayed:
        assert replayed[0][1] == executed[0][1], results
    if in_progress:
        assert in_progress[0][1:] == (409, "IDEMPOTENT_REQUEST_IN_PROGRESS"), results

    with Session() as db:
        count = db.scalar(select(func.count()).select_from(IdempotencyKey).where(
            IdempotencyKey.user_id == uid,
            IdempotencyKey.endpoint == endpoint,
            IdempotencyKey.key == key,
        ))
        assert count == 1
        persisted = db.scalar(select(IdempotencyKey).where(
            IdempotencyKey.user_id == uid,
            IdempotencyKey.endpoint == endpoint,
            IdempotencyKey.key == key,
        ))
        assert persisted.response_status == 201
        assert persisted.response_body == executed[0][1]
        assert persisted.response_body["reserved_kg"] == 400
    engine.dispose()
