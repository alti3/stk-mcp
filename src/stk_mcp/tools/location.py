import logging
from mcp.server.fastmcp import Context

from ..app import mcp_server
from ..stk_logic.core import StkState, STK_LOCK
from ..stk_logic.decorators import require_stk_tool
from ..stk_logic.location import create_location_internal

logger = logging.getLogger(__name__)


@mcp_server.tool()
@require_stk_tool
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

    Examples:
        >>> create_location(ctx, name="Boulder", latitude_deg=40.015, longitude_deg=-105.27, altitude_km=1.656, kind="facility")
        "Successfully created facility: 'Boulder'"
    """
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    try:
        scenario = lifespan_ctx.stk_root.CurrentScenario
        if scenario is None:
            return "Error: No active scenario found. Use 'setup_scenario' first."
    except Exception as e:
        return f"Error: Could not access current scenario: {e}"

    # Input validation
    if not (-90.0 <= latitude_deg <= 90.0):
        return "Error: latitude_deg must be within [-90, 90] degrees."
    if not (-180.0 <= longitude_deg <= 180.0):
        return "Error: longitude_deg must be within [-180, 180] degrees."
    if altitude_km < -0.5:
        return "Error: altitude_km must be >= -0.5 km."
    if kind.lower() not in ("facility", "place"):
        return "Error: kind must be 'facility' or 'place'."

    with STK_LOCK:
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
