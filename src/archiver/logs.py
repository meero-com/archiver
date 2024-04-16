"""Bootstrap archiver logging.

Two output modes are available and configurable through
the following environment variables:
    - APP_DEBUG: set the log level to logging.DEBUG.
    - DEV_MODE: set the log output to ConsoleRenderer.

These attributes should be retrieved by the calling scope to avoid referencing
configuration directly from the utility `archiver.logs` submodule to enforce
explicit configuration from top-level.
"""
import logging

import structlog
from structlog.stdlib import BoundLogger
from structlog.processors import JSONRenderer
from structlog.dev import ConsoleRenderer


def bootstrap_logging(logger_name: str, enable_debug: bool, dev_mode: bool) -> BoundLogger:
    """Configure the logger `logger_name` with format and log level.

    Default behavior is to set the log level to logging.INFO and output to JSON.

    The `logger_name` allow to identify the logger and possibly cache it
    for further retrieval from this function.

    Set `enable_debug` to `True` to lower the default log level (logging.INFO) to
    the debug one (logging.DEBUG)

    Set `dev_mode` to `True` to allow human-readable console rendering
    through structlog's ConsoleRenderer.
    """
    log_level = logging.DEBUG if enable_debug else logging.INFO

    output_processor = ConsoleRenderer(event_key="message") if dev_mode else JSONRenderer()

    structlog.configure(
        processors=[
            # structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.ExceptionRenderer(),
            # structlog.processors.dict_tracebacks, # structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.EventRenamer('message'),
            output_processor,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    log: BoundLogger = structlog.get_logger(logger_name)
    return log
