import json
import logging
from datetime import datetime, timezone

_json_logger = logging.getLogger()

APP_NAME = "flask-app"

def _safe(v):
    if v is ...:
        return None
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return str(v)

def log_event(level: int, event: str, **fields) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "app": "flask-app",
        "debug_version": "v99-APP-TEST",
        "event": event,
    }
    for k, v in fields.items():
        payload[k] = _safe(v)

    _json_logger.log(level, json.dumps(payload, ensure_ascii=False))