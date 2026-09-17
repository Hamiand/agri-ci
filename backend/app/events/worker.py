"""Retry-safe transactional-outbox worker.

`publish_event` remains the adapter seam for the pilot. A production deployment can
replace it with Redis Streams, RabbitMQ, Kafka, or a notification adapter without
changing the outbox state machine.
"""
import time
from datetime import datetime, timezone
from sqlalchemy import select
from app.database.models import DomainEvent
from app.database.session import SessionLocal


def publish_event(event: DomainEvent) -> None:
    print(f"[AGRI-CI EVENT] {event.event_type} {event.aggregate_type}:{event.aggregate_id}")


def run_once(limit: int = 100) -> int:
    """Attempt unpublished events once, recording both successes and failures.

    Failed events remain unpublished and are therefore eligible for a later retry.
    SKIP LOCKED lets multiple workers safely claim different rows.
    """
    attempted = 0
    with SessionLocal() as db:
        events = list(db.scalars(
            select(DomainEvent)
            .where(DomainEvent.published_at.is_(None))
            .order_by(DomainEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        ).all())
        for event in events:
            attempted += 1
            event.publish_attempts += 1
            event.last_publish_attempt_at = datetime.now(timezone.utc)
            try:
                publish_event(event)
            except Exception as exc:
                # Keep the row unpublished. Persist a bounded diagnostic and continue
                # so one bad downstream event cannot block the rest of the batch.
                event.last_publish_error = f"{type(exc).__name__}: {exc}"[:2000]
            else:
                event.published_at = datetime.now(timezone.utc)
                event.last_publish_error = None
        db.commit()
    return attempted


if __name__ == "__main__":
    while True:
        processed = run_once()
        time.sleep(1 if processed else 5)
