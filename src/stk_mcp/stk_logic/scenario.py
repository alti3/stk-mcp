from .core import stk_available, IAgStkObjectRoot, IAgScenario

def setup_scenario_internal(
    stk_root: IAgStkObjectRoot,
    scenario_name: str,
    start_time: str,
    duration_hours: float
) -> tuple[bool, str, IAgScenario | None]:
    """
    Internal logic to create/configure an STK Scenario.

    Returns:
        tuple: (success_flag, status_message, scenario_object_or_None)
    """
    if not stk_available or not stk_root:
        return False, "STK Root object not available.", None

    try:
        # Close existing scenario if open
        if stk_root.Children.Count > 0:
            current_scen_name = stk_root.CurrentScenario.InstanceName
            print(f"  Closing existing scenario: {current_scen_name}")
            stk_root.CloseScenario()

        # Create new scenario
        print(f"  Creating new scenario: {scenario_name}")
        stk_root.NewScenario(scenario_name)
        scenario = stk_root.CurrentScenario

        if scenario is None:
             raise Exception("Failed to create or get the new scenario object.")

        # Set time period
        duration_str = f"+{duration_hours} hours"
        print(f"  Setting scenario time: Start='{start_time}', Duration='{duration_str}'")
        scenario.SetTimePeriod(start_time, duration_str)

        # Reset animation time
        stk_root.Rewind()

        # Optional: Maximize windows
        try:
            print("  Maximizing STK windows...")
            stk_root.ExecuteCommand('Application / Raise')
            stk_root.ExecuteCommand('Application / Maximize')
            # Consider checking for 3D window existence if needed
            # stk_root.ExecuteCommand('Window3D * Maximize')
        except Exception as cmd_e:
            print(f"  Warning: Could not execute maximize commands: {cmd_e}")

        return True, f"Successfully created and configured scenario: '{scenario_name}'", scenario

    except Exception as e:
        error_msg = f"Error setting up scenario '{scenario_name}': {e}"
        print(f"  {error_msg}")
        # import traceback
        # traceback.print_exc()
        return False, error_msg, None 