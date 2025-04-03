from mcp.server.fastmcp import FastMCP

# Import the lifespan manager and the state dataclass
from .stk_logic.core import stk_lifespan, StkState

# Define the server instance *before* importing tools that use its decorator
mcp_server = FastMCP[StkState]( # Type hint the lifespan context if desired
    "STK Control",
    lifespan=stk_lifespan
)

# Import the tools module AFTER the server instance is created.
# This triggers the execution of the @mcp_server.tool() decorators inside those files.
from . import tools

# No further code needed here usually.
# Running this file via `mcp dev src/stk_mcp/server.py` will start the server. 