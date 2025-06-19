# STK-MCP

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/) [![MCP Version](https://img.shields.io/pypi/v/mcp.svg)](https://pypi.org/project/mcp/)

STK-MCP is an MCP (Model Context Protocol) server designed to enable Large Language Models (LLMs) or other MCP clients to interact with [Ansys/AGI STK](https://www.ansys.com/products/missions/ansys-stk) (Systems Tool Kit) - the leading Digital Mission Engineering software.


This project allows controlling STK via an MCP server, supporting both STK Desktop (Windows only) and STK Engine (Windows & Linux). It utilizes `FastMCP` from the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).

## Overview

The primary goal of this project is to bridge the gap between programmatic interaction and the powerful simulation capabilities of STK. By exposing STK functionalities through a robust CLI and an MCP server, users can command STK simulations using simple commands or LLM-driven applications.

The MCP application, defined in `src/stk_mcp/app.py`, exposes STK operations as MCP tools, which are dynamically managed by a CLI entry point in `src/stk_mcp/cli.py`.

## Features

*   **CLI Entry Point:** A professional command-line interface powered by `Typer`.
*   **Dual Mode Operation:** Supports both STK Engine (for headless automation on Windows/Linux) and STK Desktop (for visual interaction on Windows).
*   **OS-Aware:** Automatically detects the operating system and disables STK Desktop mode on non-Windows platforms.
*   **Dynamic Lifecycle:** The STK application (Engine or Desktop) is started and stopped automatically with the server.
*   **Tool Discovery:** A built-in `list-tools` command to easily see all available MCP tools.
*   **Modular Architecture:** Clear separation between the CLI (`cli.py`), MCP application (`app.py`), STK logic (`stk_logic/`), and MCP tools (`tools/`).

## Prerequisites

*   **Operating System:** Windows or Linux. STK Desktop mode requires Windows.
*   **Python:** Version 3.12 or higher.
*   **Ansys/AGI STK:** Version 12.x Desktop or Engine installed.
*   **STK Python API:** The `agi.stk12` Python wheel corresponding to your STK installation must be installed. This typically involves:
    *   Locating the wheel file (e.g., `agi.stk12-py3-none-any.whl`) within your STK installation directory (often under `CodeSamples\Automation\Python`).
    *   Installing it using `uv pip` or `pip`.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stk-mcp
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    # Create the virtual environment
    uv venv

    # Activate it
    # On Windows (in PowerShell/CMD):
    # .venv\Scripts\activate
    # On Linux (in bash/zsh):
    source .venv/bin/activate
    ```
3.  **Install STK Python API:**
    Install the wheel file from your STK installation.
    ```bash
    uv pip install "path/to/your/stk/CodeSamples/Automation/Python/agi.stk12-py3-none-any.whl"
    ```
4.  **Install the project in editable mode:**
    This command installs all dependencies from `pyproject.toml` and makes the `stk-mcp` command available in your terminal.
    ```bash
    uv pip install -e .
    ```

## Usage

This project is a command-line application. Ensure your virtual environment is activated before running commands.

### Listing Available Tools

To see a list of all MCP tools the server can expose, run:
```bash
stk-mcp list-tools
```
This will print a table of tool names and their functions.

### Running the MCP Server

Use the `run` command to start the MCP server. The server will automatically start and manage an STK instance.

**1. Run with STK Engine (Recommended for automation, works on Windows/Linux):**
```bash
stk-mcp run --mode engine
```

**2. Run with STK Desktop (Windows Only, shows the GUI):**
Ensure STK Desktop is closed, as the server will launch and manage its own instance.
```bash
stk-mcp run --mode desktop
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
3.  Navigate to the "Tools" section to execute `setup_scenario` and `create_satellite`.

### Stopping the Server
Press `Ctrl+C` in the terminal where the server is running. The lifecycle manager will automatically close the STK Engine or Desktop instance.

## MCP Tools Available

*   **`setup_scenario`**: Creates/Configures an STK Scenario.
*   **`create_satellite`**: Creates or modifies an STK satellite in the active scenario.

## Dependencies

*   `agi.stk12`: For interacting with STK (Requires manual installation from STK).
*   `mcp[cli]>=1.6.0`: Model Context Protocol library.
*   `typer[all]>=0.12.0`: For building the command-line interface.
*   `pywin32`: Required for STK Desktop COM interaction on Windows.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.