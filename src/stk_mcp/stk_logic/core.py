import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Union

from mcp.server.fastmcp import FastMCP
from ..cli import StkMode # Import the enum from the CLI

# --- Attempt STK Imports ---
stk_available = False
STKApplication = None
STKDesktop = None
STKEngine = None
IAgStkObjectRoot = None
IAgScenario = None

if os.name == "nt":
    try:
        from agi.stk12.stkdesktop import STKDesktop as STKDesktopImport, STKApplication as STKApplicationImport
        from agi.stk12.stkengine import STKEngine as STKEngineImport
        from agi.stk12.stkobjects import IAgStkObjectRoot as IAgStkObjectRootImport, IAgScenario as IAgScenarioImport
        
        STKDesktop = STKDesktopImport
        STKApplication = STKApplicationImport # This is the Desktop App
        STKEngine = STKEngineImport
        IAgStkObjectRoot = IAgStkObjectRootImport
        IAgScenario = IAgScenarioImport
        stk_available = True
        print("STK Desktop and Engine modules loaded successfully (Windows).")
    except ImportError:
        print("Failed to import STK modules on Windows. Functionality disabled.")
else: # Linux
    try:
        from agi.stk12.stkengine import STKEngine as STKEngineImport, IAgStkObjectRoot as IAgStkObjectRootImport
        from agi.stk12.stkobjects import IAgScenario as IAgScenarioImport
        
        STKEngine = STKEngineImport
        IAgStkObjectRoot = IAgStkObjectRootImport
        IAgScenario = IAgScenarioImport
        stk_available = True
        print("STK Engine modules loaded successfully (Linux). STK Desktop is unavailable.")
    except ImportError:
        print("Failed to import STK Engine modules. Functionality disabled.")

# A type hint for whichever application object is in use
StkAppType = Union[STKApplication, STKEngine, None]

@dataclass
class StkState:
    """Holds the state of the STK application connection."""
    stk_app: StkAppType = None
    stk_root: IAgStkObjectRoot | None = None
    mode: StkMode | None = None

def create_stk_lifespan(mode: StkMode):
    """
    A factory that returns an async context manager for the STK lifecycle.
    """
    @asynccontextmanager
    async def stk_lifespan_manager(server: FastMCP) -> AsyncIterator[StkState]:
        """
        Manages the STK application lifecycle based on the selected mode.
        """
        if not stk_available or IAgStkObjectRoot is None:
            print("STK is not available. MCP server will run without STK functionality.")
            yield StkState(mode=mode)
            return

        print(f"MCP Server Startup: Initializing STK in '{mode.value}' mode...")
        state = StkState(mode=mode)
        
        try:
            if mode == StkMode.DESKTOP:
                # --- Desktop Mode Logic ---
                print("   Attempting to attach to existing STK instance...")
                try:
                    state.stk_app = STKDesktop.AttachToApplication()
                    print("   Successfully attached to existing STK instance.")
                    state.stk_app.Visible = True
                except Exception:
                    print("   Could not attach. Launching new STK instance...")
                    state.stk_app = STKDesktop.StartApplication(visible=True, userControl=True)
                
                state.stk_root = state.stk_app.Root
                # Close any open scenario to start clean
                if state.stk_root and state.stk_root.Children.Count > 0:
                     print(f"   Closing existing scenario '{state.stk_root.CurrentScenario.InstanceName}'...")
                     state.stk_root.CloseScenario()

            elif mode == StkMode.ENGINE:
                # --- Engine Mode Logic ---
                print("   Starting new STK Engine instance...")
                state.stk_app = STKEngine.StartApplication(noGraphics=True)
                state.stk_root = state.stk_app.NewObjectRoot()
                print("   STK Engine instance started.")

            if state.stk_root is None:
                raise RuntimeError("Failed to obtain STK Root object.")

            print("STK Initialized. Providing STK context to tools.")
            yield state

        except Exception as e:
            print(f"FATAL: Failed to initialize STK in {mode.value} mode: {e}")
            yield StkState(mode=mode) # Yield empty state on failure
        
        finally:
            print(f"MCP Server Shutdown: Cleaning up STK ({mode.value} mode)...")
            if state.stk_app:
                try:
                    state.stk_app.Close()
                    print("   STK Application/Engine Closed.")
                except Exception as quit_e:
                    print(f"   Warning: Error closing STK: {quit_e}")
            print("STK Cleanup Complete.")

    return stk_lifespan_manager