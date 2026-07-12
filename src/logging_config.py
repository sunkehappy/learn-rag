import logging
import os
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_NOISY_LOGGERS = ("httpx", "httpcore", "chromadb", "openai", "urllib3")


def setup_logging(level: str | None = None) -> None:
    log_level_name = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(log_level)
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    for logger_name in _NOISY_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def log_progress(message: str) -> None:
    """Log to stderr and print to stdout so CLI users see progress immediately."""
    logging.getLogger("smartkb").info(message)
    print(f"→ {message}", flush=True)
