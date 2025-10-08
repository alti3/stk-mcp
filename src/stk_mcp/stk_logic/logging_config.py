from __future__ import annotations

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure structured logging for STK-MCP.

    Example format:
    2025-01-01 12:00:00 | INFO     | stk_mcp.module:function:42 - Message
    """
    fmt = (
        "%(asctime)s | %(levelname)-8s | "
        "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    datefmt = "%Y-%m-%d %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)

    lvl = getattr(logging, str(level).upper(), logging.INFO)
    root.setLevel(lvl)

