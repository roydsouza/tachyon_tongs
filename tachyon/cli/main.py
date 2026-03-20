import typer
from typing import Optional
import json
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="tt",
    help="Tachyon Tongs: Event-Horizon Command Bridge",
    add_completion=False,
)

console = Console()

@app.command()
def dash(refresh: int = typer.Option(2000, help="Refresh interval in ms")):
    """Launch the interactive TUI dashboard."""
    console.print(f"[bold blue]Launching Tachyon Dashboard (refresh={refresh}ms)...[/bold blue]")
    # TODO: Import and run Textual App
    from tachyon.cli.tui.app import TachyonDash
    TachyonDash().run()

@app.command()
def status(json_out: bool = typer.Option(False, "--json", help="Output in JSON format")):
    """Quick substrate health summary."""
    # Mock data for scaffolding
    data = {
        "status": "OPERATIONAL",
        "uptime": "3d 14h 22m",
        "integrity": "VERIFIED",
        "merkle": "a3f92c81d..."
    }
    
    if json_out:
        print(json.dumps(data))
    else:
        table = Table(title="Tachyon Substrate Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        for k, v in data.items():
            table.add_row(k.capitalize(), v)
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
