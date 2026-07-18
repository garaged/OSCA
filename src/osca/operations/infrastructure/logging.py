from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, TextIO

_SENSITIVE_PARTS = ("secret", "password", "token", "credential", "private_key")
_STANDARD_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__)


def _redact(value: Any, key: str = "") -> Any:
    normalized = key.casefold()
    if any(part in normalized for part in _SENSITIVE_PARTS):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {
            str(item_key): _redact(item_value, str(item_key))
            for item_key, item_value in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_RECORD_FIELDS and not key.startswith("_")
        }
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            **fields,
        }
        return json.dumps(_redact(payload), sort_keys=True, default=str)


def configure_json_logging(stream: TextIO, *, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("osca")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(level)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger
