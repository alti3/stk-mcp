from mcp.server.fastmcp import Context

# Use relative imports within the package
from .. import mcp_server # Import the server instance
from ..stk_logic.core import StkState, stk_available
from ..stk_logic.satellite import create_satellite_internal

@mcp_server.tool() # Decorate with the server instance
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
    """
    print(f"\nMCP Tool: Received request to create satellite '{name}'")
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    if not stk_available:
        return "Error: STK is not available on this system or failed to load."
    if not lifespan_ctx or not lifespan_ctx.stk_root:
        return "Error: STK Root object not available. STK might not be running or initialized properly via lifespan."

    # Get the current scenario from the STK root object
    try:
         scenario = lifespan_ctx.stk_root.CurrentScenario
         if scenario is None:
             return "Error: No active scenario found in STK. Use 'setup_scenario' tool first."
         print(f"  Operating within scenario: {scenario.InstanceName}")
    except Exception as e:
         return f"Error accessing current scenario: {e}. Use 'setup_scenario' tool first."

    # Call the internal logic function
    try:
        success, message, _ = create_satellite_internal(
            stk_root=lifespan_ctx.stk_root,
            scenario=scenario,
            name=name,
            apogee_alt_km=apogee_alt_km,
            perigee_alt_km=perigee_alt_km,
            raan_deg=raan_deg,
            inclination_deg=inclination_deg
        )
        return message # Return the message from the internal function

    except ValueError as ve:
        error_msg = f"Configuration Error for satellite '{name}': {ve}"
        print(f"  {error_msg}")
        return error_msg
    except Exception as e:
        # Catch potential errors from the internal function (e.g., COM errors)
        error_msg = f"Error creating satellite '{name}': {e}"
        print(f"  {error_msg}")
        # import traceback
        # traceback.print_exc()
        return error_msg 