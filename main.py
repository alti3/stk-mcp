import os
import sys # Import sys for exit

try:
    # Import STK Desktop if on Windows
    if os.name == "nt":
        from agi.stk12.stkdesktop import STKDesktop
        import win32com.client
    # Import STK Objects
    from agi.stk12.stkobjects import (
        AgESTKObjectType,
        AgEVePropagatorType,
        AgEClassicalLocation,
        # AgESurfaceReference # Removed as it's commented out later
    )
except Exception as e: # Catch specific exception if known, or broader one like this
    print(f"Failed to import required modules: {e}")
    print("Ensure STK is installed and the Python API wheel (e.g., agi.stk12-py3-none-any.whl) is installed.")
    sys.exit(1) # Use sys.exit for better practice


# Constants
EARTH_RADIUS_KM = 6378.137 # Standard Earth radius

############################################################################
# Function to Create/Configure Satellite
############################################################################

def create_satellite_ap_pe_raan_inc(stk_root, scenario, name, apogee_alt_km, perigee_alt_km, raan_deg, inclination_deg):
    """
    Creates or modifies an STK satellite using Apogee/Perigee altitudes, RAAN, and Inclination.

    Args:
        stk_root: The STK application root object (IAgStkObjectRoot).
        scenario: The active STK scenario object (IAgScenario).
        name (str): The desired name for the satellite.
        apogee_alt_km (float): Apogee altitude in kilometers above the Earth's surface.
        perigee_alt_km (float): Perigee altitude in kilometers above the Earth's surface.
        raan_deg (float): Right Ascension of the Ascending Node in degrees.
        inclination_deg (float): Orbit inclination in degrees.

    Returns:
        The STK Satellite object (IAgSatellite) or None if creation fails.

    Raises:
        ValueError: If apogee altitude is less than perigee altitude.
        Exception: Can raise exceptions from COM interactions if STK encounters errors.

    Assumptions:
        - Propagator: TwoBody
        - Coordinate System: J2000 (Using AgEClassicalLocation.eCoordinateSystemJ2000)
        - Argument of Perigee: 0 degrees
        - True Anomaly: 0 degrees (starts at perigee)
        - Epoch: Scenario default
    """
    print(f"\nAttempting to create/configure satellite: {name}")

    if apogee_alt_km < perigee_alt_km:
        raise ValueError("Apogee altitude cannot be less than Perigee altitude.")

    try:
        # --- Calculate Semi-Major Axis (a) and Eccentricity (e) ---
        radius_apogee_km = apogee_alt_km + EARTH_RADIUS_KM
        radius_perigee_km = perigee_alt_km + EARTH_RADIUS_KM

        semi_major_axis_km = (radius_apogee_km + radius_perigee_km) / 2.0
        # Avoid division by zero if radii are equal (circular orbit)
        if radius_apogee_km + radius_perigee_km == 0:
             eccentricity = 0.0
        else:
             eccentricity = (radius_apogee_km - radius_perigee_km) / (radius_apogee_km + radius_perigee_km)


        print(f"  Calculated Semi-Major Axis (a): {semi_major_axis_km:.3f} km")
        print(f"  Calculated Eccentricity (e): {eccentricity:.6f}")

        # --- Get or Create Satellite Object ---
        scenario_children = scenario.Children
        satellite = None # Initialize satellite to None
        if not scenario_children.Contains(AgESTKObjectType.eSatellite, name):
            print(f"  Creating new Satellite object: {name}")
            satellite = scenario_children.New(AgESTKObjectType.eSatellite, name)
        else:
            print(f"  Satellite '{name}' already exists. Getting reference.")
            satellite = scenario_children.Item(name)

        # Check if satellite object was successfully created/retrieved
        if satellite is None:
             raise Exception(f"Failed to create or retrieve satellite object '{name}'.")


        # --- Set Propagator to TwoBody ---
        print("  Setting propagator to TwoBody...")
        satellite.SetPropagatorType(AgEVePropagatorType.ePropagatorTwoBody)
        propagator = satellite.Propagator
        propagator_twobody = None # Initialize propagator_twobody
        # Ensure win32com is only used on Windows
        if os.name == 'nt':
            propagator_twobody = win32com.client.CastTo(propagator, "IAgVePropagatorTwoBody")
        else:
            # Handle non-Windows case or raise error if needed
            print("Warning: CastTo requires win32com.client, skipping propagator configuration.")
            return satellite # Or return None, or raise an error

        # Check if cast was successful
        if propagator_twobody is None:
            raise Exception("Failed to cast propagator to IAgVePropagatorTwoBody.")


        # --- Define Orbital Elements (using assumption for ArgP, TrueA) ---
        argp_deg = 0.0 # Assumed
        true_anom_deg = 0.0 # Assumed (starts at perigee)

        print(f"  Assigning Classical Elements (J2000):")
        print(f"    SemiMajorAxis: {semi_major_axis_km:.3f} km")
        print(f"    Eccentricity:  {eccentricity:.6f}")
        print(f"    Inclination:   {inclination_deg:.3f} deg")
        print(f"    ArgOfPerigee:  {argp_deg:.3f} deg (Assumed)")
        print(f"    RAAN:          {raan_deg:.3f} deg")
        print(f"    TrueAnomaly:   {true_anom_deg:.3f} deg (Assumed)")

        # Access the Initial State object and assign the classical elements
        orbit_state = propagator_twobody.InitialState.Representation
        classical_elements = None # Initialize classical_elements
        # Ensure win32com is only used on Windows
        if os.name == 'nt':
            classical_elements = win32com.client.CastTo(orbit_state, "IAgOrbitStateClassical")
            if classical_elements: # Check if cast was successful
                classical_elements.AssignClassical(
                    AgEClassicalLocation.eCoordinateSystemJ2000, # Coordinate System Enum
                    semi_major_axis_km,     # Element 1: Semi-Major Axis (km)
                    eccentricity,           # Element 2: Eccentricity
                    inclination_deg,        # Element 3: Inclination (deg)
                    argp_deg,               # Element 4: Argument of Perigee (deg)
                    raan_deg,               # Element 5: RAAN (deg)
                    true_anom_deg           # Element 6: True Anomaly (deg)
                )
            else:
                raise Exception("Failed to cast orbit state to IAgOrbitStateClassical.")
        else:
            print("Warning: CastTo requires win32com.client, skipping orbit state assignment.")


        # --- Propagate the Orbit ---
        print("  Propagating orbit...")
        # Ensure propagator_twobody exists before calling Propagate
        if propagator_twobody is not None:
             propagator_twobody.Propagate()
        else:
             print("Warning: Propagator not fully configured, skipping propagation.")

        print(f"Satellite '{name}' configuration attempted.") # Changed message slightly

        return satellite

    except ValueError as ve:
        print(f"ERROR: {ve}")
        return None
    except Exception as e:
        # Use f-string for cleaner formatting
        print(f"ERROR configuring satellite '{name}': {e}")
        # Consider logging the full traceback for debugging
        # import traceback
        # traceback.print_exc()
        return None


############################################################################
# Function to Setup STK Application and Scenario
############################################################################
def setup_stk_scenario(scenario_name="Python_Automation_Demo"):
    """
    Starts or attaches to STK Desktop and creates/configures a new scenario.

    Requires STK Desktop installation on Windows.

    Args:
        scenario_name (str): The name for the new STK scenario.

    Returns:
        tuple: A tuple containing (stkRoot, scenario) objects, or (None, None) if setup fails.
               stkRoot: The STK application root object (IAgStkObjectRoot).
               scenario: The active STK scenario object (IAgScenario).
    """
    if os.name != "nt":
        print("Automation samples require STK Desktop on Windows.")
        print("For STK Engine examples on other platforms, see Custom Applications documentation.")
        raise Exception("Automation samples require STK Desktop on Windows.")

    print('...Opening the STK application')
    stkUiApplication = None # Initialize to None
    stkRoot = None # Initialize to None

    try:
        # Grab an existing instance of STK
        print("   Attempting to attach to existing STK instance...")
        stkUiApplication = STKDesktop.AttachToApplication()
        stkRoot = stkUiApplication.Root
        print("   Successfully attached to existing STK instance.")
        # Check if a scenario is open
        checkempty = stkRoot.Children.Count
        if checkempty == 0:
            # If a Scenario is not open, create a new scenario later
            print("   No scenario open in attached instance.")
            stkUiApplication.Visible = True # Make sure it's visible
        else:
            # If a Scenario is open, close it to start fresh
            print(f"   Scenario '{stkRoot.CurrentScenario.InstanceName}' is open. Closing it to start fresh.")
            stkRoot.CloseScenario()
            stkUiApplication.Visible = True # Ensure visibility after closing

    except Exception as e:
        # STK is not running or couldn't attach
        print(f"   Could not attach to existing STK instance ({e}). Launching new instance...")
        try:
            stkUiApplication = STKDesktop.StartApplication(visible=True, userControl=True)
            stkRoot = stkUiApplication.Root
            print("   New STK instance started successfully.")
        except Exception as start_e:
            print(f"FATAL: Failed to start a new STK instance: {start_e}")
            print("Ensure STK Desktop is installed correctly.")
            return None, None # Return None if STK cannot be started

    # Ensure we have a valid stkRoot before proceeding
    if stkRoot is None:
        print("FATAL: Could not obtain STK Root object.")
        return None, None

    print(f'...Creating new scenario: {scenario_name}')
    # Check if scenario exists before creating
    try:
        # Close any potentially open blank scenario first (might happen on new instance)
        if stkRoot.Children.Count > 0 and stkRoot.CurrentScenario.InstanceName == "Untitled":
             stkRoot.CloseScenario()
    except Exception: # Ignore error if no scenario is open or accessible
        pass

    try:
        stkRoot.NewScenario(scenario_name)
    except Exception as scen_e:
        print(f"Error creating new scenario '{scenario_name}': {scen_e}")
        # Attempt to get current if creation failed but maybe one exists?
        try:
            if stkRoot.Children.Count > 0:
                print(f"Attempting to use existing scenario: {stkRoot.CurrentScenario.InstanceName}")
            else:
                 print("No scenario available.")
                 return stkRoot, None # Return root but no scenario
        except Exception:
             return stkRoot, None # Return root but no scenario


    # Set scenario time interval
    scenario = stkRoot.CurrentScenario
    if scenario is None:
         print("FATAL: Failed to get current scenario object.")
         return stkRoot, None

    # Use ISO 8601 format for clarity if preferred, though STK format is fine
    # scenario.SetTimePeriod('2020-01-20T17:00:00.000Z', '+48 hours')
    scenario.SetTimePeriod('20 Jan 2020 17:00:00.000', '+48 hours') # times are UTCG

    # Reset animation time to new scenario start time
    stkRoot.Rewind()

    # Set scenario global reference to MSL (optional, default is usually WGS84 Ellipsoid)
    # print("...Setting Surface Reference to Mean Sea Level (MSL)")
    # scenario.VO.SurfaceReference = AgESurfaceReference.eMeanSeaLevel


    try:
        # Maximize application window
        print("...Maximizing STK windows")
        stkRoot.ExecuteCommand('Application / Raise')
        stkRoot.ExecuteCommand('Application / Maximize')

        # Maximize 3D window (ensure one exists)
        stkRoot.ExecuteCommand('Window3D * Maximize')
    except Exception as cmd_e:
        print(f"Warning: Could not execute maximize commands: {cmd_e}")

    return stkRoot, scenario


############################################################################
# Main Script Execution
############################################################################
def main():
    """Main function to set up STK and create satellites."""
    stk_root, scenario = setup_stk_scenario("Python_Automation_Demo_Refactored")

    # Exit if STK setup failed
    if stk_root is None or scenario is None:
        print("\nSTK setup failed. Exiting.")
        sys.exit(1)

    # Create Satellites using the function
    # Example Satellite 1: LEO
    print('\n...Adding LEO Satellite')
    leo_sat = create_satellite_ap_pe_raan_inc(
        stk_root=stk_root,
        scenario=scenario,
        name="LEO_Sat",
        apogee_alt_km=550.0,
        perigee_alt_km=500.0,
        raan_deg=45.0,
        inclination_deg=51.6
    )
    if leo_sat:
        print(f"Successfully added/configured {leo_sat.InstanceName}")
    else:
        print("Failed to add LEO satellite.")


    # Example Satellite 2: GEO
    print('\n...Adding GEO Satellite')
    geo_sat = create_satellite_ap_pe_raan_inc(
        stk_root=stk_root,
        scenario=scenario,
        name="GEO_Sat",
        apogee_alt_km=35786.0,
        perigee_alt_km=35786.0, # Circular orbit
        raan_deg=120.0,
        inclination_deg=0.1 # Slightly inclined GEO
    )
    if geo_sat:
        print(f"Successfully added/configured {geo_sat.InstanceName}")
    else:
        print("Failed to add GEO satellite.")

    # Example Satellite 3: Molniya Orbit
    print('\n...Adding Molniya Satellite')
    molniya_sat = create_satellite_ap_pe_raan_inc(
        stk_root=stk_root,
        scenario=scenario,
        name="Molniya_Sat",
        apogee_alt_km=39360.0,
        perigee_alt_km=1000.0,
        raan_deg=270.0,
        inclination_deg=63.4
    )
    if molniya_sat:
        print(f"Successfully added/configured {molniya_sat.InstanceName}")
    else:
        print("Failed to add Molniya satellite.")


    ### End of Script
    print('\n...Scenario setup complete!')
    # Optional: Keep script running to interact with STK manually
    # input("Press Enter to close STK and exit...")
    # if stkUiApplication: # Need to handle how stkUiApplication is accessed if needed here
    #     # One way: Return it from setup_stk_scenario as well
    #     # setup_stk_scenario(...) might need to return (stkRoot, scenario, stkUiApplication)
    #     stkUiApplication.Quit()


# Standard Python entry point
if __name__ == "__main__":
    main()