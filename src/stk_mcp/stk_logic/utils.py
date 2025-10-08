from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec

from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def timed_operation(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to log operation duration for diagnostics."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            logger.info("%s completed in %.3fs", func.__name__, duration)
            return result
        except Exception as e:  # pragma: no cover - diagnostic path
            duration = time.perf_counter() - start
            logger.error("%s failed after %.3fs: %s", func.__name__, duration, e)
            raise

    return wrapper


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), reraise=True)
def safe_stk_command(stk_root: Any, command: str):
    """Execute an STK Connect command with basic retry logic."""
    return stk_root.ExecuteCommand(command)


def safe_exec_lines(stk_root: Any, command: str) -> list[str]:
    """Execute a Connect command and return result lines; returns [] on failure."""
    try:
        res = safe_stk_command(stk_root, command)
        return [res.Item(i) for i in range(res.Count)]
    except Exception:  # pragma: no cover - depends on STK runtime
        logger.debug("Connect command failed: %s", command)
        return []

