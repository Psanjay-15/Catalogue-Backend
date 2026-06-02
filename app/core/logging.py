from __future__ import annotations
import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    fmt = "%(asctime)s  %(levelname)-7s  %(name)-30s  %(message)s"
    logging.basicConfig(
        level=level,
        format=fmt,
        stream=sys.stdout,
    )
    # Tame chatty loggers
    logging.getLogger("httpx").setLevel("WARNING")
    logging.getLogger("httpcore").setLevel("WARNING")
    logging.getLogger("sqlalchemy.engine").setLevel("WARNING")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
