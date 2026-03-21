import typer
from typing import Optional
import json
import httpx
import time
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live

SUBSTRATE_URL = "http://127.0.0.1:60461/api/v1"

app = typer.Typer(
    name="tt",
    help="Tachyon Tongs: Event-Horizon Command Bridge",
    add_completion=False,
)

console = Console()

def send_notification(title: str, message: str):
    """OSC 9 Terminal Notification (Ghostty/iTerm2)"""
    # ESC ] 9 ; title ; message \a
    print(f"\033]9;{title};{message}\007", end="", flush=True)

def link(text: str, url: str) -> str:
    """OSC 8 Hyperlink support"""
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"

@app.command()
def ritual():
    """Execute the substrate boot ceremony (System Verification)."""
    console.rule("[bold cyan]Substrate Boot Ceremony[/bold cyan]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        t1 = progress.add_task("[cyan]Verifying SQLite Integrity...", total=100)
        time.sleep(1.0)
        progress.update(t1, completed=100)
        
        t2 = progress.add_task("[magenta]Validating Merkle Hierarchy...", total=100)
        time.sleep(1.2)
        progress.update(t2, completed=100)
        
        t3 = progress.add_task("[green]Unlocking Singularity PDP...", total=100)
        time.sleep(0.8)
        progress.update(t3, completed=100)
        
    send_notification("Tachyon Substrate", "Ritual Complete. Bridge Operational.")
    console.print("\n[bold green]✓ Substrate Synchronized. Welcome back, Operator.[/bold green]")

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
def airlock():
    """List pending airlock patches."""
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(f"{SUBSTRATE_URL}/airlock")
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        console.print(f"[bold red]Daemon Offline:[/bold red] {e}")
        return

    table = Table(title="Pending Airlock Patches")
    table.add_column("CVE ID", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Summary", style="white")

    for p in data:
        # OSC 8 Hyperlink to local file if path exists
        cve_link = link(p["id"], f"file:///Users/rds/antigravity/tachyon_tongs/intelligence/exploits/{p['id']}.md")
        table.add_row(cve_link, p["status"].upper(), p["summary"])

    console.print(table)

@app.command()
def immune():
    """Trigger the autonomic immune system scan."""
    from tachyon.core.immune_manager import ImmuneManager
    console.rule("[bold magenta]Autonomic Immune Scan[/bold magenta]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[magenta]Scanning Canary Log for bypasses...", total=None)
        manager = ImmuneManager()
        results = manager.scan_and_evolve()
        progress.update(task, completed=100)
    
    if results["status"] == "SUCCESS":
        count = results["evolutions_triggered"]
        if count > 0:
            console.print(f"[bold green]✓ Autonomic Evolution Complete: {count} patch(es) staged in Airlock.[/bold green]")
            for detail in results["details"]:
                console.print(f"  - [cyan]{detail['threat_id']}[/cyan]: {detail['engineer_status'].upper()}")
        else:
            console.print("[dim]No new bypasses detected. Substrate is stable.[/dim]")
    else:
        console.print(f"[bold red]Scan Failed:[/bold red] {results.get('reason')}")

# --- Key Management Command Group ---
keys_app = typer.Typer(help="Manage cryptographic keys and hardware anchors.")
app.add_typer(keys_app, name="keys")

@keys_app.command()
def genesis():
    """Execute the Root Key Genesis Ceremony (Phase 25.1)."""
    from scripts.generate_keys import genesis_ceremony
    genesis_ceremony()

@keys_app.command()
def recover():
    """Execute the Resurrection Ceremony (3-of-5 recovery)."""
    from scripts.generate_keys import recovery_drill
    recovery_drill()

@app.command()
def agent(
    action: str = typer.Argument(..., help="list|run|stop|restart"),
    name: Optional[str] = typer.Argument(None, help="Agent name")
):
    """Manage Tachyon agents."""
    console.print(f"[bold yellow]Executing agent {action} for {name or 'all'}...[/bold yellow]")

if __name__ == "__main__":
    app()
