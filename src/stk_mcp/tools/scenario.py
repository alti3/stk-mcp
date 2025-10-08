import logging
from mcp.server.fastmcp import Context

# Use relative imports within the package
from ..app import mcp_server  # Import the server instance created in server.py
from ..stk_logic.core import StkState, STK_LOCK
from ..stk_logic.decorators import require_stk_tool
from ..stk_logic.config import get_config
from ..stk_logic.scenario import setup_scenario_internal

logger = logging.getLogger(__name__)

@mcp_server.tool() # Decorate with the server instance
@require_stk_tool
def setup_scenario(
    ctx: Context,
    scenario_name: str | None = None,
    start_time: str | None = None, # Default UTCG start
    duration_hours: float | None = None # Default duration
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
    logger.info("MCP Tool: setup_scenario '%s'", scenario_name)
    lifespan_ctx: StkState | None = ctx.request_context.lifespan_context

    # Basic input validation
    cfg = get_config()
    if scenario_name is None:
        scenario_name = cfg.default_scenario_name
    if start_time is None:
        start_time = cfg.default_start_time
    if duration_hours is None:
        duration_hours = cfg.default_duration_hours

    if not scenario_name or not isinstance(scenario_name, str):
        return "Error: scenario_name must be a non-empty string."
    if duration_hours <= 0:
        return "Error: duration_hours must be positive."

    # Call the internal logic function
    with STK_LOCK:
        success, message, _ = setup_scenario_internal(
            stk_root=lifespan_ctx.stk_root,
            scenario_name=scenario_name,
            start_time=start_time,
            duration_hours=duration_hours,
        )

    return message # Return the status message from the internal function 
