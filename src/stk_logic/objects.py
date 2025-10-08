from __future__ import annotations

from typing import Optional

from .core import stk_available, IAgStkObjectRoot


def _exec_lines(stk_root: IAgStkObjectRoot, cmd: str) -> list[str]:
    """
    Execute an STK Connect command and return the result lines.
    Safe helper that returns an empty list on failure.
    """
    try:
        res = stk_root.ExecuteCommand(cmd)
        # Typical AgExecCmdResult supports Count/Item(index)
        return [res.Item(i) for i in range(res.Count)]
    except Exception:
        return []


def _parse_all_instance_names(lines: list[str]) -> list[tuple[str, str]]:
    """
    Parse lines returned by the "AllInstanceNames" Connect command.

    Returns a list of tuples: (class_name, instance_name)
    """
    out: list[tuple[str, str]] = []
    for raw in lines:
        line = (raw or "").strip()
        if not line:
            continue
        # Heuristically skip headers if present
        lower = line.lower()
        if "number" in lower and ("object" in lower or "instance" in lower):
            continue

        # Paths often look like "/Class/Name" or "*/Class/Name" or longer
        parts = [p for p in line.split('/') if p]
        if len(parts) >= 2:
            cls = parts[-2]
            name = parts[-1]
            out.append((cls, name))
        else:
            # Fallback if the format is unexpected
            out.append(("", line))
    return out


_TOP_LEVEL_CLASSES = (
    # Common top-level object classes in STK
    "Satellite",
    "Facility",
    "Place",
    "Aircraft",
    "Ship",
    "GroundVehicle",
    "Missile",
    "LaunchVehicle",
    "Submarine",
    "AreaTarget",
    "LineTarget",
)

_SENSOR_PARENTS = (
    # Object classes that commonly host Sensors
    "Satellite",
    "Facility",
    "Aircraft",
    "Ship",
    "GroundVehicle",
    "Missile",
    "LaunchVehicle",
    "Submarine",
)


def _normalize_filter(filter_type: str) -> set[str] | None:
    """
    Normalize a user-provided filter type (case-insensitive) to a set of
    canonical STK class names. Returns None if the filter is unrecognized.
    """
    t = (filter_type or "").strip().lower()
    if not t:
        return None

    # Aliases and plural handling
    mapping: dict[str, set[str]] = {
        "sat": {"Satellite"},
        "satellite": {"Satellite"},
        "satellites": {"Satellite"},
        "facility": {"Facility"},
        "facilities": {"Facility"},
        "place": {"Place"},
        "places": {"Place"},
        "location": {"Facility", "Place"},
        "locations": {"Facility", "Place"},
        "sensor": {"Sensor"},
        "sensors": {"Sensor"},
        "aircraft": {"Aircraft"},
        "ship": {"Ship"},
        "ships": {"Ship"},
        "groundvehicle": {"GroundVehicle"},
        "groundvehicles": {"GroundVehicle"},
        "missile": {"Missile"},
        "missiles": {"Missile"},
        "areatarget": {"AreaTarget"},
        "areatargets": {"AreaTarget"},
        "linetarget": {"LineTarget"},
        "linetargets": {"LineTarget"},
        "launchvehicle": {"LaunchVehicle"},
        "launchvehicles": {"LaunchVehicle"},
        "submarine": {"Submarine"},
        "submarines": {"Submarine"},
    }
    return mapping.get(t)


def list_objects_internal(
    stk_root: IAgStkObjectRoot,
    filter_type: Optional[str] = None,
) -> list[dict[str, str]]:
    """
    Enumerate objects in the active scenario and return a list of
    {"name": <instance name>, "type": <class>} dictionaries.

    Uses STK Connect (AllInstanceNames) for broad compatibility with
    both STK Desktop and STK Engine.
    """
    if not stk_available or not stk_root:
        raise RuntimeError("STK Root is not available.")

    # Ensure there is an active scenario
    try:
        scenario = stk_root.CurrentScenario
        if scenario is None:
            raise RuntimeError("No active scenario found.")
    except Exception as e:
        raise RuntimeError(f"Could not access current scenario: {e}")

    normalized: set[str] | None = _normalize_filter(filter_type) if filter_type else None

    results: list[dict[str, str]] = []

    def add_from_cmd(cmd: str, expected_type: str | None = None) -> None:
        lines = _exec_lines(stk_root, cmd)
        for cls, name in _parse_all_instance_names(lines):
            typ = expected_type or (cls if cls else "")
            if not typ:
                continue
            if normalized is not None and typ not in normalized:
                continue
            results.append({"name": name, "type": typ})

    # Top-level classes
    for cls in _TOP_LEVEL_CLASSES:
        if normalized is not None and cls not in normalized:
            continue
        add_from_cmd(f"AllInstanceNames */{cls}", expected_type=cls)

    # Sensors (nested under multiple parents)
    # Only include if no filter, or if filter explicitly asks for sensors
    if normalized is None or ("Sensor" in normalized):
        for parent in _SENSOR_PARENTS:
            add_from_cmd(f"AllInstanceNames */{parent}/*/Sensor", expected_type="Sensor")

    return results

