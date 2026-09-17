import os
import uuid

import pytest
from sqlalchemy import select

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def test_outbox_failure_is_persisted_then_retry_succeeds(monkeypatch):
    from app.database.models import DomainEvent
    from app.database.session import SessionLocal
    from app.events import worker

    event_id = uuid.uuid4()
    aggregate_id = f"OUTBOX-RETRY-{uuid.uuid4().hex}"

    with SessionLocal() as db:
        db.add(DomainEvent(
            id=event_id,
            event_type="pilot.outbox.retry.proof",
            aggregate_type="integration_test",
            aggregate_id=aggregate_id,
            payload={"proof": True},
        ))
        db.commit()

    original_publish = worker.publish_event

    def fail_only_target(event):
        if event.id == event_id:
            raise RuntimeError("simulated downstream outage")
        return original_publish(event)

    monkeypatch.setattr(worker, "publish_event", fail_only_target)
    attempted = worker.run_once(limit=1000)
    assert attempted >= 1

    with SessionLocal() as db:
        event = db.scalar(select(DomainEvent).where(DomainEvent.id == event_id))
        assert event is not None
        assert event.published_at is None
        assert event.publish_attempts == 1
        assert event.last_publish_attempt_at is not None
        assert "simulated downstream outage" in (event.last_publish_error or "")

    published = []

    def succeed_target(event):
        if event.id == event_id:
            published.append(event.id)
            return None
        return original_publish(event)

    monkeypatch.setattr(worker, "publish_event", succeed_target)
    attempted = worker.run_once(limit=1000)
    assert attempted >= 1
    assert published == [event_id]

    with SessionLocal() as db:
        event = db.scalar(select(DomainEvent).where(DomainEvent.id == event_id))
        assert event is not None
        assert event.published_at is not None
        assert event.publish_attempts == 2
        assert event.last_publish_attempt_at is not None
        assert event.last_publish_error is None

    # A published event must not be delivered again on a later worker pass.
    published.clear()
    worker.run_once(limit=1000)
    assert published == []
