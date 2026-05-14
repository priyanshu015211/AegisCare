"""
backend/core/logging.py

Centralized logging configuration for AegisCare using Loguru.
Outputs structured logs with rotation and retention.
Import get_logger() in any module to get a named logger.
"""

import sys
from pathlib import Path
from loguru import logger as _loguru_logger

from backend.core.config import get_settings


def setup_logging() -> None:
    """
    Configure Loguru handlers.
    Call this once at application startup in main.py.
    """
    settings = get_settings()

    # Remove default handler
    _loguru_logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{message}"
    )

    # Console handler
    _loguru_logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
    )

    # File handler with rotation and retention
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    _loguru_logger.add(
        str(log_path),
        format=log_format,
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        enqueue=True,  # Thread-safe
        backtrace=True,
        diagnose=settings.debug,
    )

    _loguru_logger.info(
        f"Logging initialized | env={settings.app_env} | level={settings.log_level}"
    )


def get_logger(name: str):
    """
    Returns a Loguru logger bound to the given module name.

    Usage:
        from backend.core.logging import get_logger
        log = get_logger(__name__)
        log.info("Something happened")
    """
    return _loguru_logger.bind(name=name)
