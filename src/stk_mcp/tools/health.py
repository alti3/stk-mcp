import logging
from collections import Counter
from mcp.server.fastmcp import Context
from mcp.server.fastmcp.exceptions import ResourceError

from ..app import mcp_server
from ..stk_logic.core import StkState, STK_LOCK
from ..stk_logic.decorators import require_stk_resource
from ..stk_logic.objects import list_objects_internal

logger = logging.getLogger(__name__)


@mcp_server.resource(
    "resource://stk/health",
    name="STK Health",
    title="STK Server Health",
    description=(
        "Report basic STK state: mode, current scenario, and object counts."
    ),
    mime_type="application/json",
)
@require_stk_resource
def health(ctx: Context):
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    if not lifespan_ctx:
        raise ResourceError("No lifespan context set.")

    mode = lifespan_ctx.mode.value if lifespan_ctx.mode else None
    scenario_name = None
    try:
        if lifespan_ctx.stk_root and lifespan_ctx.stk_root.CurrentScenario:
            scenario_name = lifespan_ctx.stk_root.CurrentScenario.InstanceName
    except Exception:
        scenario_name = None

    objects = []
    try:
        if lifespan_ctx.stk_root:
            with STK_LOCK:
                objects = list_objects_internal(lifespan_ctx.stk_root)
    except Exception:
        objects = []

    counts = Counter([o.get("type", "") for o in objects if o.get("type")])

    return {
        "mode": mode,
        "scenario": scenario_name,
        "counts": dict(counts),
    }
