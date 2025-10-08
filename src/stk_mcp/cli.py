import os
import sys
import logging
import uvicorn
import typer
from rich.console import Console
from rich.table import Table

# --- Check for STK installation early ---
stk_installed = False
try:
    from agi.stk12.stkengine import STKEngine  # noqa: F401
    from agi.stk12.stkdesktop import STKDesktop  # noqa: F401
    stk_installed = True
except ImportError:
    print(
        "Warning: Ansys/AGI STK Python API not found. Please install it to use this application.",
        file=sys.stderr,
    )
    # Allow Typer to still show help, but commands will fail.

# --- Local imports (safe regardless of STK availability) ---
from stk_mcp.app import mcp_server
from stk_mcp.stk_logic.core import create_stk_lifespan, StkMode  # type: ignore


# --- Typer Application Setup ---
app = typer.Typer(
    name="stk-mcp",
    help="A CLI for running and interacting with the STK-MCP server.",
    add_completion=False,
)
console = Console()

def _validate_desktop_mode(mode: StkMode):
    """Callback to ensure 'desktop' mode is only used on Windows."""
    if mode == StkMode.DESKTOP and os.name != "nt":
        console.print(f"[bold red]Error:[/] STK Desktop mode is only available on Windows. Use '--mode {StkMode.ENGINE.value}'.")
        raise typer.Exit(code=1)
    return mode

@app.command()
def run(
    host: str = typer.Option("127.0.0.1", help="The host to bind the server to."),
    port: int = typer.Option(8765, help="The port to run the server on."),
    mode: StkMode = typer.Option(
        StkMode.ENGINE if os.name != "nt" else StkMode.DESKTOP,
        "--mode", "-m",
        case_sensitive=False,
        help="STK execution mode. 'desktop' is only available on Windows.",
        callback=_validate_desktop_mode,
    ),
    log_level: str = typer.Option(
        "info",
        help="Log level: critical, error, warning, info, debug",
    ),
):
    """
    Run the STK-MCP server.
    """
    if not stk_installed:
        console.print("[bold red]Error:[/] Cannot run server. STK Python API is not installed.")
        raise typer.Exit(code=1)
        
    # Configure logging
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console.print(f"[green]Starting STK-MCP server in[/] [bold cyan]{mode.value}[/] [green]mode...[/]")

    # Dynamically create the lifespan based on the selected mode
    stk_lifespan_manager = create_stk_lifespan(mode)

    # Attach the lifespan to the server instance
    mcp_server.lifespan = stk_lifespan_manager

    # Run the server using uvicorn
    uvicorn.run(
        mcp_server,
        host=host,
        port=port,
    )

@app.command(name="list-tools")
def list_tools():
    """
    List all available MCP tools and their descriptions.
    """
    if not stk_installed:
        console.print("[bold red]Error:[/] Cannot list tools. STK Python API is not installed.")
        raise typer.Exit(code=1)
        
    table = Table(title="[bold blue]STK-MCP Available Tools[/bold blue]")
    table.add_column("Tool Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    if not mcp_server.router.tools:
        console.print("[yellow]No tools have been registered on the server.[/yellow]")
        return
        
    for name, tool in sorted(mcp_server.router.tools.items()):
        description = tool.description or "No description provided."
        table.add_row(name, description.strip())

    console.print(table)


if __name__ == "__main__":
    app()
