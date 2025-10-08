import logging
from mcp.server.fastmcp import Context
from mcp.server.fastmcp.exceptions import ResourceError

from ..app import mcp_server
from ..stk_logic.core import StkState, STK_LOCK
from ..stk_logic.decorators import require_stk_resource
from ..stk_logic.analysis import (
    compute_access_intervals_internal,
    get_lla_ephemeris_internal,
)

logger = logging.getLogger(__name__)


@mcp_server.resource(
    "resource://stk/analysis/access/{object1}/{object2}",
    name="STK Access",
    title="Compute Access Intervals",
    description=(
        "Compute access intervals between two objects."
        " Provide paths like 'Satellite/SatA' and 'Facility/FacB'"
        " (with or without leading '*/')."
    ),
    mime_type="application/json",
)
@require_stk_resource
def compute_access(ctx: Context, object1: str, object2: str):
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context
    if not lifespan_ctx or not lifespan_ctx.stk_root:
        raise ResourceError("STK Root unavailable.")

    with STK_LOCK:
        return compute_access_intervals_internal(lifespan_ctx.stk_root, object1, object2)


@mcp_server.resource(
    "resource://stk/reports/lla/{satellite}",
    name="STK LLA Ephemeris",
    title="Satellite LLA Ephemeris",
    description=(
        "Return satellite LLA ephemeris over the scenario interval."
        " Provide path like 'Satellite/SatA' (with or without leading '*/')."
    ),
    mime_type="application/json",
)
@require_stk_resource
def get_satellite_lla(ctx: Context, satellite: str):
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context
    if not lifespan_ctx or not lifespan_ctx.stk_root:
        raise ResourceError("STK Root unavailable.")

    with STK_LOCK:
        return get_lla_ephemeris_internal(lifespan_ctx.stk_root, satellite, 60.0)
