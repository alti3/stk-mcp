"""Register MCP tools and resources.

Importing modules ensures the @mcp_server.tool() and .resource() decorators
run and register endpoints with the server.
"""

from . import scenario  # noqa: F401
from . import satellite  # noqa: F401
from . import location  # noqa: F401
from . import objects  # noqa: F401
from . import health  # noqa: F401

# You can optionally define an __all__ if needed, but importing is usually sufficient
# for the decorators to register. 
