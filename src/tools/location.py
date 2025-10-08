from mcp.server.fastmcp import Context

from ..app import mcp_server
from ..stk_logic.core import StkState, stk_available
from ..stk_logic.location import create_location_internal


@mcp_server.tool()
def create_location(
    ctx: Context,
    name: str,
    latitude_deg: float,
    longitude_deg: float,
    altitude_km: float = 0.0,
    kind: str = "facility",
) -> str:
    """
    Create or update a ground location in the active scenario.

    Args:
        ctx: MCP request context (provides STK lifespan state).
        name: Object name (e.g., "Boulder").
        latitude_deg: Geodetic latitude in degrees [-90, 90].
        longitude_deg: Geodetic longitude in degrees [-180, 180].
        altitude_km: Altitude above mean sea level in kilometers.
        kind: Object kind: "facility" (default) or "place".

    Returns:
        Status message indicating success or error details.
    """
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    if not stk_available:
        return "Error: STK is not available on this system or failed to load."
    if not lifespan_ctx or not lifespan_ctx.stk_root:
        return "Error: STK Root object not available. Initialize via 'run' first."

    try:
        scenario = lifespan_ctx.stk_root.CurrentScenario
        if scenario is None:
            return "Error: No active scenario found. Use 'setup_scenario' first."
    except Exception as e:
        return f"Error: Could not access current scenario: {e}"

    ok, msg, _ = create_location_internal(
        stk_root=lifespan_ctx.stk_root,
        scenario=scenario,
        name=name,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        altitude_km=altitude_km,
        kind=kind,
    )
    return msg

