import os
import platform
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Union
from enum import Enum  # <--- IMPORT Enum
from threading import Lock

from pydantic import BaseModel
from typing import NamedTuple, Optional
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# --- Define shared data types here ---

class StkMode(str, Enum):
    """Enumeration for selecting the STK execution mode."""
    DESKTOP = "desktop"
    ENGINE = "engine"

# --- Attempt STK Imports ---
stk_available = False
STKApplication = None
STKDesktop = None
STKEngine = None
IAgStkObjectRoot = None
IAgScenario = None

_platform = platform.system()
if _platform == "Windows":
    try:
        from agi.stk12.stkdesktop import STKDesktop as STKDesktopImport, STKApplication as STKApplicationImport
        from agi.stk12.stkengine import STKEngine as STKEngineImport
        from agi.stk12.stkobjects import IAgStkObjectRoot as IAgStkObjectRootImport, IAgScenario as IAgScenarioImport

        STKDesktop = STKDesktopImport
        STKApplication = STKApplicationImport  # Desktop App
        STKEngine = STKEngineImport
        IAgStkObjectRoot = IAgStkObjectRootImport
        IAgScenario = IAgScenarioImport
        stk_available = True
        logger.info("STK Desktop and Engine modules loaded successfully (Windows).")
    except ImportError:
        logger.warning("Failed to import STK modules on Windows. Functionality disabled.")
elif _platform == "Linux":
    try:
        from agi.stk12.stkengine import STKEngine as STKEngineImport, IAgStkObjectRoot as IAgStkObjectRootImport
        from agi.stk12.stkobjects import IAgScenario as IAgScenarioImport

        STKEngine = STKEngineImport
        IAgStkObjectRoot = IAgStkObjectRootImport
        IAgScenario = IAgScenarioImport
        stk_available = True
        logger.info("STK Engine modules loaded successfully (Linux). STK Desktop is unavailable.")
    except ImportError:
        logger.warning("Failed to import STK Engine modules. Functionality disabled.")
elif _platform == "Darwin":
    # STK Engine is not supported on macOS
    logger.error("Detected macOS (Darwin). STK Engine/Desktop are not supported on this platform.")
else:
    logger.warning("Unknown platform '%s'. STK availability undetermined.", _platform)

# A type hint for whichever application object is in use
StkAppType = object | None

class StkState(BaseModel):
    """Holds the state of the STK application connection."""
    stk_app: StkAppType = None
    stk_root: object | None = None
    mode: StkMode | None = None

# Global lock to serialize all STK access across tools/resources
STK_LOCK: Lock = Lock()


class OperationResult(NamedTuple):
    """Standard result type for STK operations."""
    success: bool
    message: str
    data: Optional[dict] = None

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
            logger.warning("STK is not available. MCP server will run without STK functionality.")
            yield StkState(mode=mode)
            return

        logger.info("MCP Server Startup: Initializing STK in '%s' mode...", mode.value)
        state = StkState(mode=mode)
        
        try:
            if mode == StkMode.DESKTOP:
                # --- Desktop Mode Logic ---
                logger.info("   Attempting to attach to existing STK instance...")
                try:
                    state.stk_app = STKDesktop.AttachToApplication()
                    logger.info("   Successfully attached to existing STK instance.")
                    state.stk_app.Visible = True
                except Exception:
                    logger.info("   Could not attach. Launching new STK instance...")
                    state.stk_app = STKDesktop.StartApplication(visible=True, userControl=True)
                
                state.stk_root = state.stk_app.Root
                # Close any open scenario to start clean
                if state.stk_root and state.stk_root.Children.Count > 0:
                     logger.info("   Closing existing scenario '%s'...", state.stk_root.CurrentScenario.InstanceName)
                     state.stk_root.CloseScenario()

            elif mode == StkMode.ENGINE:
                # --- Engine Mode Logic ---
                logger.info("   Starting new STK Engine instance...")
                state.stk_app = STKEngine.StartApplication(noGraphics=True)
                state.stk_root = state.stk_app.NewObjectRoot()
                logger.info("   STK Engine instance started.")

            if state.stk_root is None:
                raise RuntimeError("Failed to obtain STK Root object.")

            logger.info("STK Initialized. Providing STK context to tools.")
            yield state

        except Exception as e:
            logger.exception("FATAL: Failed to initialize STK in %s mode: %s", mode.value, e)
            yield StkState(mode=mode) # Yield empty state on failure
        
        finally:
            logger.info("MCP Server Shutdown: Cleaning up STK (%s mode)...", mode.value)
            if state.stk_app:
                try:
                    state.stk_app.Close()
                    logger.info("   STK Application/Engine Closed.")
                except Exception as quit_e:
                    logger.warning("   Error closing STK: %s", quit_e)
            logger.info("STK Cleanup Complete.")

    return stk_lifespan_manager
