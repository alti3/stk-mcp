import logging
from mcp.server.fastmcp import Context

# Use relative imports within the package
from ..app import mcp_server  # Import the server instance
from ..stk_logic.core import StkState, STK_LOCK
from ..stk_logic.decorators import require_stk_tool
from ..stk_logic.satellite import create_satellite_internal

logger = logging.getLogger(__name__)

@mcp_server.tool() # Decorate with the server instance
@require_stk_tool
def create_satellite(
    ctx: Context,
    name: str,
    apogee_alt_km: float,
    perigee_alt_km: float,
    raan_deg: float,
    inclination_deg: float
) -> str:
    """
    MCP Tool: Creates/modifies an STK satellite using Apogee/Perigee altitudes, RAAN, and Inclination.
    Assumes a scenario is already open.

    Args:
        ctx: The MCP context.
        name: Desired name for the satellite.
        apogee_alt_km: Apogee altitude (km).
        perigee_alt_km: Perigee altitude (km).
        raan_deg: RAAN (degrees).
        inclination_deg: Inclination (degrees).

    Returns:
        A string indicating success or failure.

    Examples:
        >>> create_satellite(ctx, "ISS", apogee_alt_km=420, perigee_alt_km=410, raan_deg=51.6, inclination_deg=51.6)
        "Successfully created/configured satellite: 'ISS'"
    """
    logger.info("MCP Tool: create_satellite '%s'", name)
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    # Get the current scenario from the STK root object
    try:
         scenario = lifespan_ctx.stk_root.CurrentScenario
         if scenario is None:
             return "Error: No active scenario found in STK. Use 'setup_scenario' tool first."
         logger.info("  Operating within scenario: %s", scenario.InstanceName)
    except Exception as e:
         return f"Error accessing current scenario: {e}. Use 'setup_scenario' tool first."

    # Input validation
    if apogee_alt_km < perigee_alt_km:
        return "Error: apogee_alt_km cannot be less than perigee_alt_km."
    if not (0.0 <= inclination_deg <= 180.0):
        return "Error: inclination_deg must be within [0, 180] degrees."
    # RAAN wraps; accept 0..360 inclusive
    if not (0.0 <= raan_deg <= 360.0):
        return "Error: raan_deg must be within [0, 360] degrees."
    if perigee_alt_km < -0.5 or apogee_alt_km < -0.5:
        return "Error: perigee/apogee altitudes must be >= -0.5 km."

    # Call the internal logic function
    try:
        with STK_LOCK:
            success, message, _ = create_satellite_internal(
                stk_root=lifespan_ctx.stk_root,
                scenario=scenario,
                name=name,
                apogee_alt_km=apogee_alt_km,
                perigee_alt_km=perigee_alt_km,
                raan_deg=raan_deg,
                inclination_deg=inclination_deg,
            )
        return message # Return the message from the internal function

    except ValueError as ve:
        error_msg = f"Configuration Error for satellite '{name}': {ve}"
        logger.error("  %s", error_msg)
        return error_msg
    except Exception as e:
        # Catch potential errors from the internal function (e.g., COM errors)
        error_msg = f"Error creating satellite '{name}': {e}"
        logger.error("  %s", error_msg)
        # import traceback
        # traceback.print_exc()
        return error_msg 
