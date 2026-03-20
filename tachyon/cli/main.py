import typer
from typing import Optional
import json
import httpx
from rich.console import Console
from rich.table import Table

SUBSTRATE_URL = "http://127.0.0.1:60461/api/v1"

app = typer.Typer(
    name="tt",
    help="Tachyon Tongs: Event-Horizon Command Bridge",
    add_completion=False,
)

console = Console()

@app.command()
def dash(refresh: int = typer.Option(2000, help="Refresh interval in ms")):
    """Launch the interactive TUI dashboard."""
    from tachyon.cli.tui.app import TachyonDash
    TachyonDash().run()

@app.command()
def status(json_out: bool = typer.Option(False, "--json", help="Output in JSON format")):
    """Quick substrate health summary."""
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(f"{SUBSTRATE_URL}/status")
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        if json_out:
            print(json.dumps({"error": "Substrate Offline", "detail": str(e)}))
        else:
            console.print("[bold red]Error: Substrate Daemon is Offline.[/bold red]")
            console.print(f"[dim]{e}[/dim]")
        return

    if json_out:
        print(json.dumps(data, indent=2))
    else:
        table = Table(title="Tachyon Substrate Health")
        table.add_column("Property", style="cyan")
        table.add_column("Status/Value", style="magenta")
        
        status_color = "green" if data["status"] == "operational" else "yellow"
        table.add_row("Status", f"[bold {status_color}]{data['status'].upper()}[/bold {status_color}]")
        table.add_row("Integrity", "✓ VERIFIED" if data["integrity_verified"] else "✗ COMPROMISED")
        table.add_row("Uptime (sec)", str(data.get("uptime_seconds", 0)))
        table.add_row("Merkle Root", f"[dim]{data.get('merkle_root', 'N/A')}[/dim]")
        
        console.print(table)

@app.command()
def agent(
    action: str = typer.Argument(..., help="list|run|stop|restart"),
    name: Optional[str] = typer.Argument(None, help="Agent name")
):
    """Manage Tachyon agents."""
    console.print(f"[bold yellow]Executing agent {action} for {name or 'all'}...[/bold yellow]")

if __name__ == "__main__":
    app()
