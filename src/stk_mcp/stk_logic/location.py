from __future__ import annotations

import logging
from typing import Literal

from .core import stk_available, IAgStkObjectRoot, IAgScenario

logger = logging.getLogger(__name__)

try:
    # Enums are available on both Desktop and Engine
    from agi.stk12.stkobjects import AgESTKObjectType
    enums_available = True
except Exception:
    AgESTKObjectType = None  # type: ignore[assignment]
    enums_available = False


def create_location_internal(
    stk_root: IAgStkObjectRoot,
    scenario: IAgScenario,
    name: str,
    latitude_deg: float,
    longitude_deg: float,
    altitude_km: float,
    kind: Literal["facility", "place"] = "facility",
):
    """
    Create or update a ground location in the active scenario.

    Uses the STK Object Model for creation and assigns position using object model
    where possible; falls back to STK Connect for position assignment to preserve
    cross-platform compatibility (Desktop/Engine).

    Returns:
        tuple[bool, str, object | None]: (success, message, created_or_found_object)
    """
    if not stk_available or not stk_root or not scenario:
        return False, "STK Root/Scenario is not available.", None

    kind = kind.lower().strip()
    if kind not in ("facility", "place"):
        return False, "Invalid kind. Use 'facility' or 'place'.", None

    if not enums_available:
        return False, "STK enums not available; cannot create object.", None

    obj_type = (
        AgESTKObjectType.eFacility if kind == "facility" else AgESTKObjectType.ePlace
    )

    try:
        children = scenario.Children
        if not children.Contains(obj_type, name):
            obj = children.New(obj_type, name)
            created = True
        else:
            obj = children.Item(name)
            created = False

        # Assign position via object model if available; otherwise use Connect
        try:
            # Most STK Python wrappers surface AssignGeodetic directly
            obj.Position.AssignGeodetic(latitude_deg, longitude_deg, altitude_km)
        except Exception:
            # Fallback to STK Connect: Geodetic lat lon alt km
            class_name = "Facility" if kind == "facility" else "Place"
            cmd = (
                f"SetPosition */{class_name}/{name} Geodetic "
                f"{latitude_deg} {longitude_deg} {altitude_km} km"
            )
            stk_root.ExecuteCommand(cmd)

        action = "created" if created else "updated"
        return True, f"Successfully {action} {kind}: '{name}'", obj
    except Exception as e:
        logger.error("Error creating %s '%s': %s", kind, name, e)
        return False, f"Error creating {kind} '{name}': {e}", None
