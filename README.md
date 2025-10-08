# STK-MCP

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/) [![MCP Version](https://img.shields.io/pypi/v/mcp.svg)](https://pypi.org/project/mcp/)

STK-MCP is an MCP (Model Context Protocol) server designed to enable Large Language Models (LLMs) or other MCP clients to interact with [Ansys/AGI STK](https://www.ansys.com/products/missions/ansys-stk) (Systems Tool Kit) - the leading Digital Mission Engineering software.


This project allows controlling STK via an MCP server, supporting both STK Desktop (Windows only) and STK Engine (Windows & Linux). It utilizes `FastMCP` from the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).

## Overview

The primary goal of this project is to bridge the gap between programmatic interaction and the powerful simulation capabilities of STK. By exposing STK functionalities through a robust CLI and an MCP server, users can command STK simulations using simple commands or LLM-driven applications.

The MCP application, defined in `src/stk_mcp/app.py`, exposes STK operations as MCP tools, which are dynamically managed by a CLI entry point in `src/stk_mcp/cli.py`.

## Features

*   CLI entry point powered by `Typer`.
*   Dual mode operation: STK Engine (Windows/Linux) and STK Desktop (Windows).
*   OS-aware: Desktop mode auto-disabled on non-Windows platforms.
*   Managed lifecycle: STK instance is started/stopped with the MCP server.
*   Tool discovery: `list-tools` command enumerates available MCP tools.
*   Modular architecture: CLI (`cli.py`), MCP (`app.py`), STK logic (`stk_logic/`), and MCP tools (`tools/`).

## Prerequisites

*   **Operating System:** Windows or Linux. STK Desktop mode requires Windows.
*   **Python:** Version 3.12 or higher.
*   **Ansys/AGI STK:** Version 12.x Desktop or Engine installed.
*   **STK Python API:** The `agi.stk12` Python wheel corresponding to your STK installation must be available. Typically found under `CodeSamples\Automation\Python` in your STK install.

## Installation

1.  Clone the repository
    ```bash
    git clone <repository-url>
    cd stk-mcp
    ```
2.  Create and activate a virtual environment
    ```bash
    # Create the virtual environment
    uv venv

    # Activate it
    # On Windows (in PowerShell/CMD):
    # .venv\Scripts\activate
    # On Linux (in bash/zsh):
    source .venv/bin/activate
    ```
3.  Add dependencies with uv (preferred)
    - Add the STK Python wheel from your STK installation (local file):
    ```bash
    uv add ./agi.stk12-12.10.0-py3-none-any.whl
    # or: uv add path/to/your/STK/CodeSamples/Automation/Python/agi.stk12-*.whl
    
    # Windows only: COM bridge for Desktop automation
    uv add "pywin32; platform_system == 'Windows'"
    ```
4.  Sync the environment (installs deps from `pyproject.toml`)
    ```bash
    uv sync
    ```

## Usage

This project is a command-line application. Ensure your virtual environment is activated before running commands.

### Listing Available Tools

```bash
uv run -m stk_mcp.cli list-tools
```
Prints a table of tool names and their descriptions.

### Running the MCP Server

Use the `run` command to start the MCP server. The server will automatically start and manage an STK instance.

Run with `uv run` so you don’t need to install the package into site-packages.

**1) STK Engine (recommended for automation, Windows/Linux):**
```bash
uv run -m stk_mcp.cli run --mode engine
```

**2) STK Desktop (Windows only, shows GUI):**
Ensure STK Desktop is closed; the server will launch and manage its own instance.
```bash
uv run -m stk_mcp.cli run --mode desktop
```

The server will start, initialize STK, and listen for MCP connections on `http://127.0.0.1:8765` by default.

**3. Command Options:**
You can see all options with the `--help` flag:
```bash
stk-mcp run --help
```

### Interacting with the Server
Once the server is running, you can connect to it using any MCP client, such as the MCP Inspector.

1.  Open the MCP Inspector URL provided in the console (e.g., `http://127.0.0.1:8765`).
2.  Find the "STK Control" server in the list.
3.  Use the "Tools" section to execute `setup_scenario`, `create_location`, and `create_satellite`.

### Stopping the Server
Press `Ctrl+C` in the terminal where the server is running. The lifecycle manager will automatically close the STK Engine or Desktop instance.

## MCP Tools and Resources

The server exposes the following MCP tools/resources.

| Name             | Kind     | Description                                                                                   | Desktop (Windows) | Engine (Windows) | Engine (Linux) |
|------------------|----------|-----------------------------------------------------------------------------------------------|-------------------|------------------|----------------|
| `setup_scenario` | Tool     | Create/configure an STK Scenario; sets time period and rewinds animation.                    | Yes               | Yes              | Yes            |
| `create_location`| Tool     | Create/update a `Facility` (default) or `Place` at latitude/longitude/altitude (km).         | Yes               | Yes              | Yes            |
| `create_satellite`| Tool    | Create/configure a satellite from apogee/perigee (km), RAAN, and inclination; TwoBody prop.  | Yes               | Yes              | No             |

Notes:
- `create_satellite` on Linux Engine is not yet supported because it relies on COM-specific casts; a Connect-based fallback is planned.

Resources:

| Name | Kind | Description | Desktop (Windows) | Engine (Windows) | Engine (Linux) |
|------|------|-------------|-------------------|------------------|----------------|
| —    | —    | No resources are currently exposed. | — | — | — |

## Dependencies

Managed with `uv`:

*   `agi.stk12` (local wheel from your STK install)
*   `mcp[cli]>=1.6.0`
*   `typer>=0.15.2`
*   `pydantic>=2.11.7`
*   `pywin32` (Windows only)

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.
