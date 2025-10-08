import os
import logging
from . import core as core
from .core import IAgStkObjectRoot, IAgScenario
from .utils import timed_operation
from .config import get_config

logger = logging.getLogger(__name__)

# Import STK Objects specific to satellite creation if available (Windows Desktop/Engine)
AgESTKObjectType = None
AgEVePropagatorType = None
AgEClassicalLocation = None
win32com_client = None
satellite_capable = False

if core.stk_available and os.name == 'nt':
    try:
        from agi.stk12.stkobjects import (
            AgESTKObjectType as AgESTKObjectTypeImport,
            AgEVePropagatorType as AgEVePropagatorTypeImport,
            AgEClassicalLocation as AgEClassicalLocationImport,
        )
        import win32com.client as win32com_client_import
        AgESTKObjectType = AgESTKObjectTypeImport
        AgEVePropagatorType = AgEVePropagatorTypeImport
        AgEClassicalLocation = AgEClassicalLocationImport
        win32com_client = win32com_client_import
        satellite_capable = True
    except ImportError:
        logger.warning("Could not import STK COM types for satellite creation (Windows only feature).")
    except Exception as e:
        logger.error("Error importing win32com or STK enums: %s", e)


cfg = get_config()
EARTH_RADIUS_KM = cfg.earth_radius_km

@timed_operation
def create_satellite_internal(
    stk_root: IAgStkObjectRoot,  # Although not directly used, good for context
    scenario: IAgScenario,
    name: str,
    apogee_alt_km: float,
    perigee_alt_km: float,
    raan_deg: float,
    inclination_deg: float,
):
    """
    Internal logic to create/configure an STK satellite.

    Returns:
        tuple: (success_flag, status_message, satellite_object_or_None)

    Raises:
        ValueError: If input parameters are invalid (e.g., apogee < perigee).
        Exception: For COM or other STK errors.
    """
    if not core.stk_available or not scenario or win32com_client is None or not satellite_capable:
        raise RuntimeError("STK modules, active scenario, or win32com not available/initialized.")
    if AgESTKObjectType is None or AgEVePropagatorType is None or AgEClassicalLocation is None:
        raise RuntimeError("Required STK Object Enums not imported.")

    logger.info("  Attempting internal satellite creation/configuration: %s", name)

    if apogee_alt_km < perigee_alt_km:
        raise ValueError("Apogee altitude cannot be less than Perigee altitude.")

    # --- Calculate Semi-Major Axis (a) and Eccentricity (e) ---
    radius_apogee_km = apogee_alt_km + EARTH_RADIUS_KM
    radius_perigee_km = perigee_alt_km + EARTH_RADIUS_KM
    semi_major_axis_km = (radius_apogee_km + radius_perigee_km) / 2.0
    denominator = radius_apogee_km + radius_perigee_km
    eccentricity = 0.0 if denominator == 0 else (radius_apogee_km - radius_perigee_km) / denominator

    logger.debug("    Calculated Semi-Major Axis (a): %.3f km", semi_major_axis_km)
    logger.debug("    Calculated Eccentricity (e): %.6f", eccentricity)

    # --- Get or Create Satellite Object ---
    scenario_children = scenario.Children
    satellite = None
    if not scenario_children.Contains(AgESTKObjectType.eSatellite, name):
        logger.info("    Creating new Satellite object: %s", name)
        satellite = scenario_children.New(AgESTKObjectType.eSatellite, name)
    else:
        logger.info("    Satellite '%s' already exists. Getting reference.", name)
        satellite = scenario_children.Item(name)

    if satellite is None:
         raise Exception(f"Failed to create or retrieve satellite object '{name}'.")

    # --- Set Propagator to TwoBody ---
    logger.info("    Setting propagator to TwoBody...")
    satellite.SetPropagatorType(AgEVePropagatorType.ePropagatorTwoBody)
    propagator = satellite.Propagator

    propagator_twobody = win32com_client.CastTo(propagator, "IAgVePropagatorTwoBody")
    if propagator_twobody is None:
        raise Exception("Failed to cast propagator to IAgVePropagatorTwoBody.")

    # --- Define Orbital Elements ---
    argp_deg = 0.0 # Assumed
    true_anom_deg = 0.0 # Assumed (starts at perigee)

    logger.info("    Assigning Classical Elements (J2000):")
    # (Print statements omitted for brevity, add back if desired)

    orbit_state = propagator_twobody.InitialState.Representation
    classical_elements = win32com_client.CastTo(orbit_state, "IAgOrbitStateClassical")

    if classical_elements:
        classical_elements.AssignClassical(
            AgEClassicalLocation.eCoordinateSystemJ2000,
            semi_major_axis_km, eccentricity, inclination_deg,
            argp_deg, raan_deg, true_anom_deg
        )
    else:
        raise Exception("Failed to cast orbit state to IAgOrbitStateClassical.")

    # --- Propagate the Orbit ---
    logger.info("    Propagating orbit...")
    propagator_twobody.Propagate()

    logger.info("  Internal satellite configuration for '%s' complete.", name)
    # Return success flag, message, and the object
    return True, f"Successfully created/configured satellite: '{satellite.InstanceName}'", satellite 
