from __future__ import annotations

import logging
from typing import Any

from .core import IAgStkObjectRoot
from .utils import timed_operation

logger = logging.getLogger(__name__)


def _normalize_path(path: str) -> str:
    p = (path or "").strip()
    if not p:
        raise ValueError("Object path must be non-empty.")
    if p.startswith("*/"):
        return p
    if p.startswith("/"):
        return f"*{p}"
    # Require explicit class/name from users for reliability
    return f"*/{p}"


@timed_operation
def compute_access_intervals_internal(
    stk_root: IAgStkObjectRoot,
    object1_path: str,
    object2_path: str,
) -> dict[str, Any]:
    """Compute access intervals between two STK objects using the Object Model.

    Returns a dictionary with input paths and a list of {start, stop} intervals.
    """
    p1 = _normalize_path(object1_path)
    p2 = _normalize_path(object2_path)

    from_obj = stk_root.GetObjectFromPath(p1)
    to_obj = stk_root.GetObjectFromPath(p2)

    access = from_obj.GetAccessToObject(to_obj)
    access.ComputeAccess()

    intervals = access.AccessIntervals
    out: list[dict[str, str]] = []
    for i in range(intervals.Count):
        ivl = intervals.Item(i)
        out.append({"start": ivl.StartTime, "stop": ivl.StopTime})

    return {"from": p1, "to": p2, "intervals": out}


@timed_operation
def get_lla_ephemeris_internal(
    stk_root: IAgStkObjectRoot,
    satellite_path: str,
    step_sec: float = 60.0,
) -> dict[str, Any]:
    """Fetch LLA ephemeris for a satellite over the scenario interval using Data Providers.

    Returns a dictionary: {satellite, step_sec, records:[{time, lat_deg, lon_deg, alt_km}...]}
    """
    p = _normalize_path(satellite_path)
    sat = stk_root.GetObjectFromPath(p)

    scenario = stk_root.CurrentScenario
    if scenario is None:
        raise RuntimeError("No active scenario.")

    start = scenario.StartTime
    stop = scenario.StopTime

    # Data provider name and elements are standard for satellites
    dp_group = sat.DataProviders.Item("LLA State")
    dp = dp_group.Group.Item("Fixed")
    res = dp.ExecElements(start, stop, step_sec, ["Time", "Lat", "Lon", "Alt"])

    time_vals = list(res.DataSets.GetDataSetByName("Time").GetValues())
    lat_vals = list(res.DataSets.GetDataSetByName("Lat").GetValues())
    lon_vals = list(res.DataSets.GetDataSetByName("Lon").GetValues())
    alt_vals = list(res.DataSets.GetDataSetByName("Alt").GetValues())

    records: list[dict[str, float | str]] = []
    for i in range(len(time_vals)):
        records.append(
            {
                "time": time_vals[i],
                "lat_deg": float(lat_vals[i]),
                "lon_deg": float(lon_vals[i]),
                "alt_km": float(alt_vals[i]),
            }
        )

    return {"satellite": p, "step_sec": step_sec, "records": records}

