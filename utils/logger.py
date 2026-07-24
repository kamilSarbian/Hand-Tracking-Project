import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from utils.paths import get_user_data_dir


def setup_logger(
    name: str = "gesture_app",
    log_path: str | Path | None = None,
) -> logging.Logger:
    """Configure console and rotating file logging for the application.

    Args:
        name: Logger name.
        log_path: Optional destination log file. When omitted, the log is
            written under the application user-data directory.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%H:%M:%S"
    )

    if sys.stderr is not None:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    resolved_log_path = (
        Path(log_path)
        if log_path is not None
        else get_user_data_dir() / "logs" / "application.log"
    )
    try:
        resolved_log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            resolved_log_path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
    except OSError as exc:
        logger.error(
            "Could not initialize file logging at %s: %s",
            resolved_log_path,
            exc,
        )
    else:
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
