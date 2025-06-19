from mcp.server.fastmcp import FastMCP
from .stk_logic.core import StkState

# Define the central MCP server instance.
# The lifespan will be attached dynamically by the CLI based on user selection.
mcp_server = FastMCP[StkState](
    "STK Control",
    description="An MCP server for controlling Ansys STK (Desktop or Engine)."
)

# Import the tools module.
# This triggers the execution of the @mcp_server.tool() decorators.
from . import tools