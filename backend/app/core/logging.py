import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("agrici")


def log_event(level: int, event: str, **fields: Any) -> None:
    """Emit one machine-readable event without serialising exception/request secrets."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **{key: value for key, value in fields.items() if value is not None},
    }
    logger.log(level, json.dumps(payload, ensure_ascii=False, default=str, separators=(",", ":")))
