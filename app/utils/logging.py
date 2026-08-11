"""Structured logging configuration."""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "beverage_vision",
    level: Optional[str] = None,
) -> logging.Logger:
    """Configure and return a structured logger instance."""
    logger = logging.getLogger(name)
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger


logger = setup_logger()
