"""Structured logging utilities"""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional

def get_logger(name:str, level:Optional[str] = None) -> logging.Logger:
    """Return a logger configured for the given module name

    Args:
        name: Logger name(typically __name)
        level: Override log level; defaults to APP_LOG_LEVEL env var or INFO

    Returns:
        Configured logger instance:
    """
    log_level = level or os.getenv("APP_LOG_LEVEL", "INFO")

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
