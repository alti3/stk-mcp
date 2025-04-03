# STK-MCP

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)

STK-MCP is envisioned as an MCP (Model Context Protocol) server designed to enable Large Language Models (LLMs) to interact with [Ansys/AGI STK](https://www.ansys.com/products/missions/ansys-stk) (Systems Tool Kit) - the leading Digital Mission Engineering software.

This project started with the goal of creating simple MCP tools capable of launching STK Desktop and opening a new scenario. It has since evolved to include direct Python automation capabilities.

Currently, this repository contains a foundational Python script (`main.py`) demonstrating direct automation of STK Desktop using its Python API.

## Overview

The primary goal of this project is to bridge the gap between natural language interaction (via LLMs) and the powerful simulation capabilities of STK. By exposing STK functionalities through an MCP server, users could potentially command STK simulations using intuitive language prompts processed by an LLM.

The included `main.py` script serves as a proof-of-concept and utility for STK automation, showcasing how to:
*   Connect to a running STK Desktop instance or launch a new one.
*   Create and configure STK scenarios (e.g., setting time periods).
*   Programmatically add and configure Satellite objects.
*   Define satellite orbits using common orbital parameters like Apogee/Perigee altitude, RAAN, and Inclination.
*   Utilize the TwoBody propagator for orbit simulation.

## Features (Current Script)

*   **STK Desktop Integration:** Connects to or starts STK 12 (requires Windows).
*   **Scenario Management:** Creates new scenarios and sets analysis time periods.
*   **Satellite Creation:** Adds Satellite objects to the scenario.
*   **Orbit Definition:** Configures satellite orbits using Apogee/Perigee Altitude, RAAN, and Inclination (defaults to J2000, ArgP=0, TrueAnomaly=0).
*   **TwoBody Propagation:** Sets up and runs the TwoBody propagator for created satellites.
*   **Example Orbits:** Demonstrates creation of LEO, GEO, and Molniya satellites.

## Prerequisites

*   **Operating System:** Windows (due to STK Desktop and `win32com` dependency).
*   **Python:** Version 3.12 or higher.
*   **Ansys/AGI STK:** Version 12.x Desktop installed.
*   **STK Python API:** The `agi.stk12` Python wheel corresponding to your STK installation must be installed. This typically involves:
    *   Locating the wheel file (e.g., `agi.stk12-py3-none-any.whl`) within your STK installation directory (often under `CodeSamples\Automation\Python`).
    *   Installing it using pip: `pip install path/to/agi.stk12-py3-none-any.whl`
*   **Project Dependencies:** Requires the `mcp` library.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stk-mcp
    ```
2.  **Ensure Prerequisites are met:** Install Python, STK Desktop, and the STK Python API wheel as described above.
3.  **Install project dependencies:**
    ```bash
    pip install .
    # Or, if you include the optional CLI dependency defined in pyproject.toml:
    # pip install .[cli]
    ```
    *(Note: Based on `pyproject.toml`, this installs `mcp[cli]>=1.6.0`)*

## Usage (Current Script)

The `main.py` script provides a demonstration of STK automation capabilities.

1.  **Ensure STK Desktop is closed** or be prepared for the script to potentially close existing scenarios if it attaches to a running instance.
2.  **Run the script from the project root directory:**
    ```bash
    python main.py
    ```
3.  **Observe:** The script will:
    *   Attempt to attach to an existing STK instance or launch a new one.
    *   Create a new scenario named "Python_Automation_Demo_Refactored".
    *   Set the scenario time period.
    *   Add three satellites: `LEO_Sat`, `GEO_Sat`, and `Molniya_Sat` with predefined orbital parameters.
    *   Print progress messages to the console.
    *   Leave the STK application running with the configured scenario.

## Future Development (MCP Server & Expanded Automation)

The next phase of development will focus on implementing the MCP server component, allowing interaction with STK via MCP commands, potentially driven by LLMs. Planned enhancements also include expanding the direct automation capabilities:

*   **Adding Ground Locations:** Functionality to add a Facility or Place object at specified geographic coordinates (latitude, longitude, altitude).
*   **Enhanced Satellite Definition:** More comprehensive satellite creation, potentially including different orbit propagators or additional parameters beyond the current Apogee/Perigee/RAAN/Inclination method.
*   **Access Analysis:** Capabilities to compute and generate access reports between specified satellites and ground locations (or other objects).

Usage instructions for the server and new automation features will be added as they are implemented.

## Dependencies

*   `agi.stk12`: For interacting with STK Desktop (Requires manual installation from STK).
*   `mcp[cli]>=1.6.0`: Mission Control Platform library.
*   `pywin32`: Automatically installed on Windows; used for COM interactions via `win32com.client`.

## Limitations

*   **Windows Only:** The current implementation relies heavily on STK Desktop automation via COM, which is specific to Windows.
*   **STK Desktop Required:** Does not currently support STK Engine on other platforms.
*   **Limited Functionality:** The script currently only demonstrates scenario setup and basic satellite creation with the TwoBody propagator.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project, including reporting issues and submitting pull requests.
