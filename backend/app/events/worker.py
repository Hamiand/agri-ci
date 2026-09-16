"""Minimal transactional-outbox worker.

Production deployment should replace `publish_event` with a real broker/notification adapter.
Rows are marked published only after the adapter succeeds.
"""
import time
from datetime import datetime, timezone
from sqlalchemy import select
from app.database.models import DomainEvent
from app.database.session import SessionLocal

def publish_event(event: DomainEvent) -> None:
    # Adapter seam: Redis Streams / RabbitMQ / Kafka / notification service.
    print(f"[AGRI-CI EVENT] {event.event_type} {event.aggregate_type}:{event.aggregate_id}")

def run_once(limit: int = 100) -> int:
    with SessionLocal() as db:
        events = list(db.scalars(
            select(DomainEvent).where(DomainEvent.published_at.is_(None))
            .order_by(DomainEvent.created_at).limit(limit).with_for_update(skip_locked=True)
        ).all())
        for event in events:
            publish_event(event)
            event.published_at = datetime.now(timezone.utc)
        db.commit()
        return len(events)

if __name__ == "__main__":
    while True:
        processed = run_once()
        time.sleep(1 if processed else 5)
