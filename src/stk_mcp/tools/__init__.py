# Import the modules containing the tool definitions.
# This ensures the @mcp_server.tool() decorators run and register the tools.
from . import scenario
from . import satellite

# You can optionally define an __all__ if needed, but importing is usually sufficient
# for the decorators to register. 