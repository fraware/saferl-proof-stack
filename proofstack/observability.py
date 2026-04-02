"""Structured logging helpers."""

import json
import logging
from datetime import datetime, timezone
from typing import Any


def configure_logging() -> None:
    """Configure root logging once with a stable format."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_logger(name: str) -> logging.Logger:
    """Create a logger for a module."""
    return logging.getLogger(name)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Emit a structured JSON log event."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    logger.info(json.dumps(payload, default=str))
