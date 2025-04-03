import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

# Attempt STK Imports
stk_available = False
STKApplication = None
STKDesktop = None
IAgStkObjectRoot = None
IAgScenario = None # Keep for type hints if needed elsewhere

if os.name == "nt":
    try:
        from agi.stk12.stkdesktop import STKDesktop as STKDesktopImport, STKApplication as STKApplicationImport
        # Import specific types needed for type hinting
        from agi.stk12.stkobjects import IAgStkObjectRoot as IAgStkObjectRootImport
        from agi.stk12.stkobjects import IAgScenario as IAgScenarioImport

        STKDesktop = STKDesktopImport
        STKApplication = STKApplicationImport
        IAgStkObjectRoot = IAgStkObjectRootImport
        IAgScenario = IAgScenarioImport # Assign for use
        stk_available = True
        print("STK modules loaded successfully.")
    except ImportError as e:
        print(f"Failed to import STK modules: {e}. STK functionality disabled.")
    except Exception as e:
        print(f"An unexpected error occurred during STK import: {e}. STK functionality disabled.")
else:
    print("STK Automation requires Windows. STK functionality disabled.")


@dataclass
class StkState:
    """Holds the state of the STK application connection."""
    stk_ui_app: STKApplication | None = None
    stk_root: IAgStkObjectRoot | None = None


@asynccontextmanager
async def stk_lifespan(server: FastMCP) -> AsyncIterator[StkState]:
    """
    Manages the STK application lifecycle for the MCP server.
    Starts/Attaches to STK on server startup and quits on shutdown.
    """
    if not stk_available or STKDesktop is None:
        print("STK is not available. MCP server will run without STK functionality.")
        yield StkState() # Yield empty state
        return

    print("MCP Server Startup: Initializing STK...")
    state = StkState()
    try:
        # Try attaching to existing STK
        print("   Attempting to attach to existing STK instance...")
        state.stk_ui_app = STKDesktop.AttachToApplication()
        state.stk_root = state.stk_ui_app.Root
        print("   Successfully attached to existing STK instance.")
        state.stk_ui_app.Visible = True
        # Close any open scenario to start clean
        if state.stk_root and state.stk_root.Children.Count > 0:
             print(f"   Closing existing scenario '{state.stk_root.CurrentScenario.InstanceName}'...")
             state.stk_root.CloseScenario()

    except Exception:
        print("   Could not attach. Launching new STK instance...")
        try:
            state.stk_ui_app = STKDesktop.StartApplication(visible=True, userControl=True)
            state.stk_root = state.stk_ui_app.Root
            print("   New STK instance started successfully.")
        except Exception as start_e:
            print(f"FATAL: Failed to start STK: {start_e}. Server will run without STK.")
            yield StkState() # Yield empty state if startup fails
            return

    if state.stk_root is None:
        print("FATAL: Could not obtain STK Root object. Server will run without STK.")
        yield StkState() # Yield empty state
        return

    print("STK Initialized. Providing STK Root to tools via context.")
    try:
        yield state # Provide the state to the server context
    finally:
        print("MCP Server Shutdown: Cleaning up STK...")
        if state.stk_ui_app:
            try:
                state.stk_ui_app.Quit()
                print("   STK Application Quit.")
            except Exception as quit_e:
                print(f"   Warning: Error quitting STK: {quit_e}")
        print("STK Cleanup Complete.") 