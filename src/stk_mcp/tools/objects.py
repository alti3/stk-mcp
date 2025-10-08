import logging
from mcp.server.fastmcp import Context
from mcp.server.fastmcp.exceptions import ResourceError

from ..app import mcp_server
from ..stk_logic.core import StkState, STK_LOCK
from ..stk_logic.decorators import require_stk_resource
from ..stk_logic.objects import list_objects_internal

logger = logging.getLogger(__name__)


@mcp_server.resource(
    "resource://stk/objects",
    name="STK Scenario Objects",
    title="List STK Objects",
    description=(
        "List all objects in the active STK scenario with their name and type. "
        "Returns JSON: [{name, type}, ...]."
    ),
    mime_type="application/json",
)
@require_stk_resource
def list_objects(ctx: Context):
    """
    MCP Resource: List all scenario objects as JSON records.
    """
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    try:
        with STK_LOCK:
            return list_objects_internal(lifespan_ctx.stk_root)
    except Exception as e:
        raise ResourceError(str(e))


@mcp_server.resource(
    "resource://stk/objects/{object_type}",
    name="STK Scenario Objects (Filtered)",
    title="List STK Objects by Type",
    description=(
        "List scenario objects filtered by type (e.g., satellite, facility, place, sensor). "
        "Returns JSON: [{name, type}, ...]."
    ),
    mime_type="application/json",
)
@require_stk_resource
def list_objects_by_type(ctx: Context, object_type: str):
    """
    MCP Resource: List scenario objects filtered by the provided type.
    """
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    try:
        with STK_LOCK:
            objects = list_objects_internal(lifespan_ctx.stk_root, filter_type=object_type)
        # If the filter was unrecognized, return empty with a hint instead of throwing
        if not objects:
            # We still return JSON for consistency
            return []
        return objects
    except Exception as e:
        raise ResourceError(str(e))
