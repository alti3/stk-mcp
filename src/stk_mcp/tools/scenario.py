from mcp.server.fastmcp import Context

# Use relative imports within the package
from .. import mcp_server # Import the server instance created in server.py
from ..stk_logic.core import StkState, stk_available
from ..stk_logic.scenario import setup_scenario_internal

@mcp_server.tool() # Decorate with the server instance
def setup_scenario(
    ctx: Context,
    scenario_name: str = "MCP_STK_Scenario",
    start_time: str = "20 Jan 2020 17:00:00.000", # Default UTCG start
    duration_hours: float = 48.0 # Default duration
) -> str:
    """
    MCP Tool: Creates/Configures an STK Scenario. Closes any existing scenario first.

    Args:
        ctx: The MCP context (provides access to stk_root via lifespan).
        scenario_name: Name for the new scenario.
        start_time: Scenario start time in STK UTCG format.
        duration_hours: Scenario duration in hours.

    Returns:
        A string indicating success or failure.
    """
    print(f"\nMCP Tool: Received request to set up scenario '{scenario_name}'")
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    if not stk_available:
        return "Error: STK is not available on this system or failed to load."
    if not lifespan_ctx or not lifespan_ctx.stk_root:
        return "Error: STK Root object not available. STK might not be running or initialized properly via lifespan."

    # Call the internal logic function
    success, message, _ = setup_scenario_internal(
        stk_root=lifespan_ctx.stk_root,
        scenario_name=scenario_name,
        start_time=start_time,
        duration_hours=duration_hours
    )

    return message # Return the status message from the internal function 