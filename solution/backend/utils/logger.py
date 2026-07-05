"""
Centralized logger — writes to data/logs/ with rotating file handler.
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.utils.config_loader import get_storage_path


def get_logger(name: str) -> logging.Logger:
    log_dir = get_storage_path("logs_path")
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)

    # File handler with rotation
    fh = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
