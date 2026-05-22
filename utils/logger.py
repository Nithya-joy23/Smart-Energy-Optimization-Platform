"""Logging helpers."""

from __future__ import annotations

import logging

from utils.config import LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """Return a configured application logger."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger(name)
