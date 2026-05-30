"""Structured Logging Utility — Production Observability Layer.

THE PATTERN: Observer Pattern / Centralized Logging
  Every module gets a named logger via get_logger(__name__).
  All loggers feed into one rotating file at ~/.contextflow/logs/contextflow.log
  and optionally to the console (controlled by CONTEXTFLOW_LOG_LEVEL env var).

WHY THIS EXISTS:
  print() statements disappear when the session ends.
  Silent except blocks hide crashes permanently.
  A structured logger writes timestamped, searchable records to disk —
  so when something breaks at 2am, you open the log and see exactly
  what happened, in which file, at what line.

USAGE:
  from src.utils.logger import get_logger

  logger = get_logger(__name__)      # __name__ = "src.agents.observer" etc.

  logger.info("Observer started")
  logger.warning("Low confidence: %.2f", confidence)
  logger.error("API key missing")
  logger.exception("Unexpected crash")  # captures full stack trace automatically

LOG LEVELS (in order of severity):
  DEBUG   — fine-grained detail (node entry/exit, variable values)
  INFO    — normal events (capture started, API success)
  WARNING — something unexpected but recoverable (rate limit, low confidence)
  ERROR   — something failed but app continues (store_capture failed)
  CRITICAL — app cannot continue (rare)

LOG FILE: ~/.contextflow/logs/contextflow.log
  Rotates at 5MB, keeps last 3 files — never fills your disk.
  Set CONTEXTFLOW_LOG_LEVEL=DEBUG to see all events in terminal too.
"""

import logging
import logging.handlers
import os
from pathlib import Path


LOG_DIR = Path.home() / ".contextflow" / "logs"
LOG_FILE = LOG_DIR / "contextflow.log"
MAX_BYTES = 5 * 1024 * 1024   # 5MB per file
BACKUP_COUNT = 3               # keep last 3 rotated files


def setup_logging() -> None:
    """Configure the root logging system once at application startup.

    Call this as the very first line of main() before anything else runs.
    Idempotent — safe to call multiple times (only configures once).

    Sets up:
    - A rotating file handler → ~/.contextflow/logs/contextflow.log
    - A console handler (only if CONTEXTFLOW_LOG_LEVEL is set)
    - JSON-style formatting with timestamp, level, module, message
    """
    root_logger = logging.getLogger()

    # Idempotent — don't add duplicate handlers if called again
    if root_logger.handlers:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Determine log level from environment (default: WARNING for clean terminal)
    level_name = os.getenv("CONTEXTFLOW_LOG_LEVEL", "WARNING").upper()
    level = getattr(logging, level_name, logging.WARNING)
    root_logger.setLevel(logging.DEBUG)  # root captures everything; handlers filter

    # Format: timestamp | level | module | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler — always writes at DEBUG level to the file
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler — only shown if user sets CONTEXTFLOW_LOG_LEVEL env var
    if os.getenv("CONTEXTFLOW_LOG_LEVEL"):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger for a module.

    Args:
        name: Pass __name__ — Python automatically sets this to the
              module's dotted path (e.g. "src.agents.observer").

    Returns:
        A configured Logger instance for this module.

    Usage:
        logger = get_logger(__name__)
        logger.info("Observer started")
    """
    return logging.getLogger(name)
