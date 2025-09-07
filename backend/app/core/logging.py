"""
Logging configuration.
"""
import structlog
import logging
import sys
from typing import Any, Dict

from app.core.config import settings


def setup_logging() -> None:
    """Setup structured logging configuration."""
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        stream=sys.stdout,
        format="%(message)s" if settings.LOG_FORMAT == "json" else "%(levelname)s:%(name)s:%(message)s",
    )
    
    # Configure structlog
    if settings.LOG_FORMAT == "json":
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, settings.LOG_LEVEL.upper())
            ),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, settings.LOG_LEVEL.upper())
            ),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
