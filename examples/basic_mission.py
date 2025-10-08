"""
Example: Creating a basic Earth observation mission.

This demonstrates:
1. Setting up a scenario
2. Creating a ground facility
3. Creating a simple satellite (Windows/Desktop/Engine on Windows)

Run the server first, then invoke these tools from your MCP client.
"""

# This file is illustrative. Use an MCP client (e.g., MCP Inspector)
# to call the following tools in order:
#
# 1) setup_scenario(scenario_name="Demo", start_time="20 Jan 2020 17:00:00.000", duration_hours=12)
# 2) create_location(name="Boulder", latitude_deg=40.015, longitude_deg=-105.27, altitude_km=1.656, kind="facility")
# 3) create_satellite(name="DemoSat", apogee_alt_km=420, perigee_alt_km=410, raan_deg=51.6, inclination_deg=51.6)
# 4) resource: resource://stk/analysis/access/Satellite/DemoSat/Facility/Boulder
# 5) resource: resource://stk/reports/lla/Satellite/DemoSat

print(
    "Open the MCP client and try the listed tools/resources to run this example."
)

