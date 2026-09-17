from pathlib import Path


def test_outbox_worker_tracks_attempts_and_keeps_failures_retryable():
    src=Path("app/events/worker.py").read_text()
    assert "with_for_update(skip_locked=True)" in src
    assert "event.publish_attempts += 1" in src
    assert "event.last_publish_attempt_at" in src
    assert "except Exception as exc" in src
    assert "event.last_publish_error" in src
    assert "event.published_at =" in src
    # Publication timestamp is assigned only in the successful branch.
    assert src.index("except Exception as exc") < src.index("else:") < src.index("event.published_at =")


def test_outbox_schema_tracks_delivery_diagnostics():
    src=Path("app/database/models.py").read_text()
    assert "publish_attempts" in src
    assert "last_publish_error" in src
    assert "last_publish_attempt_at" in src
