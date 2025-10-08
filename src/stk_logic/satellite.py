import os
from .core import stk_available, IAgStkObjectRoot, IAgScenario

# Import STK Objects specific to satellite creation if available
AgESTKObjectType = None
AgEVePropagatorType = None
AgEClassicalLocation = None
win32com_client = None

if stk_available and os.name == 'nt':
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
    except ImportError:
        print("Could not import specific STK object enums for satellite creation.")
        stk_available = False # Mark as unavailable if critical parts missing
    except Exception as e:
        print(f"Error importing win32com or specific STK enums: {e}")
        stk_available = False


# Constants
EARTH_RADIUS_KM = 6378.137

def create_satellite_internal(
    stk_root: IAgStkObjectRoot, # Although not directly used, good for context
    scenario: IAgScenario,
    name: str,
    apogee_alt_km: float,
    perigee_alt_km: float,
    raan_deg: float,
    inclination_deg: float
):
    """
    Internal logic to create/configure an STK satellite.

    Returns:
        tuple: (success_flag, status_message, satellite_object_or_None)

    Raises:
        ValueError: If input parameters are invalid (e.g., apogee < perigee).
        Exception: For COM or other STK errors.
    """
    if not stk_available or not scenario or win32com_client is None:
         raise RuntimeError("STK modules, active scenario, or win32com not available/initialized.")
    if AgESTKObjectType is None or AgEVePropagatorType is None or AgEClassicalLocation is None:
         raise RuntimeError("Required STK Object Enums not imported.")


    print(f"  Attempting internal satellite creation/configuration: {name}")

    if apogee_alt_km < perigee_alt_km:
        raise ValueError("Apogee altitude cannot be less than Perigee altitude.")

    # --- Calculate Semi-Major Axis (a) and Eccentricity (e) ---
    radius_apogee_km = apogee_alt_km + EARTH_RADIUS_KM
    radius_perigee_km = perigee_alt_km + EARTH_RADIUS_KM
    semi_major_axis_km = (radius_apogee_km + radius_perigee_km) / 2.0
    denominator = radius_apogee_km + radius_perigee_km
    eccentricity = 0.0 if denominator == 0 else (radius_apogee_km - radius_perigee_km) / denominator

    print(f"    Calculated Semi-Major Axis (a): {semi_major_axis_km:.3f} km")
    print(f"    Calculated Eccentricity (e): {eccentricity:.6f}")

    # --- Get or Create Satellite Object ---
    scenario_children = scenario.Children
    satellite = None
    if not scenario_children.Contains(AgESTKObjectType.eSatellite, name):
        print(f"    Creating new Satellite object: {name}")
        satellite = scenario_children.New(AgESTKObjectType.eSatellite, name)
    else:
        print(f"    Satellite '{name}' already exists. Getting reference.")
        satellite = scenario_children.Item(name)

    if satellite is None:
         raise Exception(f"Failed to create or retrieve satellite object '{name}'.")

    # --- Set Propagator to TwoBody ---
    print("    Setting propagator to TwoBody...")
    satellite.SetPropagatorType(AgEVePropagatorType.ePropagatorTwoBody)
    propagator = satellite.Propagator

    propagator_twobody = win32com_client.CastTo(propagator, "IAgVePropagatorTwoBody")
    if propagator_twobody is None:
        raise Exception("Failed to cast propagator to IAgVePropagatorTwoBody.")

    # --- Define Orbital Elements ---
    argp_deg = 0.0 # Assumed
    true_anom_deg = 0.0 # Assumed (starts at perigee)

    print(f"    Assigning Classical Elements (J2000):")
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
    print("    Propagating orbit...")
    propagator_twobody.Propagate()

    print(f"  Internal satellite configuration for '{name}' complete.")
    # Return success flag, message, and the object
    return True, f"Successfully created/configured satellite: '{satellite.InstanceName}'", satellite 