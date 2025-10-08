from __future__ import annotations

import logging
from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec

from mcp.server.fastmcp import Context
from mcp.server.fastmcp.exceptions import ResourceError

from .core import stk_available

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def require_stk_tool(func: Callable[P, T]) -> Callable[P, T]:
    """Ensure STK is available and initialized for MCP tools.

    Returns a user-friendly error string if unavailable.
    Expects first parameter to be `ctx: Context`.
    """

    @wraps(func)
    def wrapper(ctx: Context, *args: P.args, **kwargs: P.kwargs) -> T:  # type: ignore[override]
        lifespan_ctx = ctx.request_context.lifespan_context

        if not stk_available:
            return "Error: STK is not available on this system."  # type: ignore[return-value]
        if not lifespan_ctx or not lifespan_ctx.stk_root:
            return "Error: STK Root not available. Initialize via server lifespan."  # type: ignore[return-value]

        return func(ctx, *args, **kwargs)

    return wrapper


def require_stk_resource(func: Callable[P, T]) -> Callable[P, T]:
    """Ensure STK is available and initialized for MCP resources.

    Raises ResourceError if unavailable. Expects first parameter `ctx: Context`.
    """

    @wraps(func)
    def wrapper(ctx: Context, *args: P.args, **kwargs: P.kwargs) -> T:  # type: ignore[override]
        lifespan_ctx = ctx.request_context.lifespan_context
        if not stk_available:
            raise ResourceError("STK is not available on this system.")
        if not lifespan_ctx or not lifespan_ctx.stk_root:
            raise ResourceError("STK Root not available. Initialize via server lifespan.")
        return func(ctx, *args, **kwargs)

    return wrapper

