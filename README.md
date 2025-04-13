# STK-MCP

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/) [![MCP Version](https://img.shields.io/pypi/v/mcp.svg)](https://pypi.org/project/mcp/)

STK-MCP is an MCP (Model Context Protocol) server designed to enable Large Language Models (LLMs) or other MCP clients to interact with [Ansys/AGI STK](https://www.ansys.com/products/missions/ansys-stk) (Systems Tool Kit) - the leading Digital Mission Engineering software.

This project allows controlling STK Desktop via MCP tools, leveraging the STK Python API. It utilizes `FastMCP` from the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). The server logic resides within the `src/stk_mcp` package.

## Overview

The primary goal of this project is to bridge the gap between programmatic or natural language interaction (via LLMs) and the powerful simulation capabilities of STK. By exposing STK functionalities through an MCP server, users can command STK simulations using MCP clients or potentially LLM-driven applications.

The MCP server, defined in `src/stk_mcp/server.py`, manages STK interaction and exposes functionality, showcasing how to:
*   Connect to a running STK Desktop instance or launch a new one via the server's lifecycle management (`src/stk_mcp/stk_logic/core.py`).
*   Expose STK operations as MCP tools (defined in `src/stk_mcp/tools/`).
*   Create and configure STK scenarios using the `setup_scenario` tool.
*   Programmatically add and configure Satellite objects using the `create_satellite` tool.
*   Define satellite orbits using common orbital parameters.
*   Utilize the TwoBody propagator for orbit simulation within the tools.

## Features (MCP Server)

*   **MCP Server Implementation:** Uses `FastMCP` within `src/stk_mcp/server.py`.
*   **Modular Structure:** Code organized into server setup (`server.py`), STK interaction logic (`stk_logic/`), and MCP tools (`tools/`).
*   **STK Desktop Integration:** Automatically connects to or starts STK 12 (requires Windows) when the server starts, managed via MCP lifespan.
*   **Scenario Management Tool (`setup_scenario`):** Creates new scenarios, sets analysis time periods, and closes any pre-existing scenario.
*   **Satellite Creation Tool (`create_satellite`):** Adds Satellite objects to the currently active scenario.
*   **Orbit Definition:** Configures satellite orbits using Apogee/Perigee Altitude, RAAN, and Inclination.
*   **TwoBody Propagation:** Sets up and runs the TwoBody propagator for created satellites.

## Prerequisites

*   **Operating System:** Windows (due to STK Desktop and `win32com` dependency).
*   **Python:** Version 3.12 or higher.
*   **Ansys/AGI STK:** Version 12.x Desktop installed.
*   **STK Python API:** The `agi.stk12` Python wheel corresponding to your STK installation must be installed. This typically involves:
    *   Locating the wheel file (e.g., `agi.stk12-py3-none-any.whl`) within your STK installation directory (often under `CodeSamples\Automation\Python`).
    *   Installing it using pip: `uv pip install path/to/agi.stk12-py3-none-any.whl`
*   **Project Dependencies:** Requires the `mcp` library (installed via `uv sync`).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stk-mcp
    ```
2.  **Ensure Prerequisites are met:** Install Python, STK Desktop, and the STK Python API wheel as described above.
3.  **Install project dependencies:**
    ```bash
    # Install dependencies defined in pyproject.toml (includes mcp[cli])
    uv sync
    ```

## Usage (MCP Server)

The MCP server logic is now structured within the `src/stk_mcp` directory. You interact with it using an MCP client or development tools.

1.  **Ensure STK Desktop is closed** (the server will launch its own instance via the lifespan manager).
2.  **Run the MCP server in development mode:**
    *   **Option A (Using the helper script):**
        ```bash
        python scripts/run_dev.py
        ```
    *   **Option B (Directly using `mcp` command from the project root):**
        ```bash
        mcp dev src/stk_mcp/server.py
        ```
    *   The server will start, attempt to launch/connect to STK, and print logs.
    *   STK Desktop should become visible.
    *   The server listens for MCP connections.
3.  **Interact with the Server (Example using MCP Inspector):**
    *   Open the MCP Inspector URL provided in the console (e.g., `http://127.0.0.1:8765`).
    *   Find the "STK Control" server.
    *   Use the "Tools" section to execute `setup_scenario` and `create_satellite` as before.
4.  **Stop the Server:** Press `Ctrl+C` in the terminal where the server is running. The lifespan manager will attempt to close STK.

## MCP Tools Available

*   **`setup_scenario`**: (Defined in `src/stk_mcp/tools/scenario.py`)
    *   Description: Creates/Configures an STK Scenario. Closes any existing scenario first.
    *   Arguments: `scenario_name` (str, default: "MCP_STK_Scenario"), `start_time` (str, default: "20 Jan 2020 17:00:00.000"), `duration_hours` (float, default: 48.0).
*   **`create_satellite`**: (Defined in `src/stk_mcp/tools/satellite.py`)
    *   Description: Creates or modifies an STK satellite. Assumes a scenario is active.
    *   Arguments: `name` (str), `apogee_alt_km` (float), `perigee_alt_km` (float), `raan_deg` (float), `inclination_deg` (float).

## Future Development (MCP Server & Expanded Automation)

Planned enhancements include:

*   **Adding Ground Locations:** MCP tool to add a Facility or Place object.
*   **Resource Endpoints:** Add MCP resources (e.g., `get_scenario_details`, `list_objects`) to query STK state.
*   **Enhanced Satellite/Object Definition:** More comprehensive configuration options.
*   **Access Analysis Tool:** Compute and report access between objects.
*   **Error Handling:** More robust error reporting back to the MCP client.

## Dependencies

*   `agi.stk12`: For interacting with STK Desktop (Requires manual installation from STK).
*   `mcp[cli]>=1.6.0`: Model Context Protocol library.
*   `pywin32`: Automatically installed on Windows; used for COM interactions via `win32com.client`.

## Limitations

*   **Windows Only:** Relies heavily on STK Desktop automation via COM.
*   **STK Desktop Required:** Does not currently support STK Engine.
*   **Basic Functionality:** Currently limited to scenario setup and basic satellite creation.
*   **Single Scenario Focus:** Assumes interaction with a single active scenario managed by the `setup_scenario` tool.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.
