"""
NOVA - Structured Logging Configuration
========================================

JSON-based logging for better parsing and monitoring.
"""

import logging
import structlog
import sys
from typing import Any

def configure_logging(service_name: str, level: str = "INFO") -> None:
    """
    Configure structured logging for a NOVA service.
    
    Args:
        service_name: Name of the service (e.g., "analyzer", "visualizer")
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    
    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level)
    )
    
    logger = structlog.get_logger()
    logger.info(
        "logging_configured",
        service=service_name,
        level=level
    )


def get_logger(name: str = None) -> Any:
    """
    Get a structured logger instance.
    
    Args:
        name: Optional logger name (defaults to module name)
    
    Returns:
        Structured logger with JSON output
    """
    return structlog.get_logger(name)
