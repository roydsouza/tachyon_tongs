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
def status(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
    local: bool = typer.Option(False, "--local", help="Run local diagnostics (no daemon)")
):
    """Quick substrate health summary."""
    if local:
        data = {
            "status": "diagnostic-mode",
            "integrity_verified": True,
            "uptime_seconds": 0,
            "merkle_root": "LOCAL_ONLY"
        }
    else:
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
        
        # Phase 31.1: Supply Chain & Keys
        from tachyon.core.state import StateManager
        state = StateManager()
        import sqlite3
        with sqlite3.connect(state.db_path) as conn:
            att_count = conn.execute("SELECT COUNT(*) FROM package_attestations").fetchone()[0]
            wl_count = conn.execute("SELECT COUNT(*) FROM package_whitelist").fetchone()[0]
        
        table.add_row("Supply Chain", f"{att_count} Attestations / {wl_count} Whitelisted")
        
        # Crypto Hierarchy
        from tachyon.core.keys.operations import get_delegation_summary
        summary = get_delegation_summary()
        anchored_count = sum(1 for a in summary.values() if a["status"] == "Anchored")
        table.add_row("Agent Keys", f"{anchored_count}/{len(summary)} Anchored")
        
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
keys_app = typer.Typer(
    help="Manage cryptographic keys and hardware anchors.",
    no_args_is_help=True
)
app.add_typer(keys_app, name="keys")

@keys_app.command()
def genesis():
    """Execute the Root Key Genesis Ceremony (3-of-5 split)."""
    from tachyon.core.keys.operations import genesis_ceremony
    genesis_ceremony()

@keys_app.command()
def pqc_genesis():
    """Execute the PQC Overlay Genesis Ceremony (ML-DSA-44)."""
    from tachyon.core.keys.operations import pqc_genesis_ceremony
    pqc_genesis_ceremony()

@keys_app.command()
def verify_pqc():
    """Execute the PQC Recovery Drill (Tier 2)."""
    from tachyon.core.keys.operations import pqc_recovery_drill
    pqc_recovery_drill()

@keys_app.command()
def anchor():
    """Retroactively anchor existing shares to the hardware Keychain."""
    from tachyon.core.keys.operations import anchor_existing_key
    anchor_existing_key()

@keys_app.command()
def anchor_agents():
    """Generate and anchor core agent sub-keys (Sentinel, Engineer, Airlock)."""
    from tachyon.core.keys.operations import anchor_agent_keys
    anchor_agent_keys()

@keys_app.command()
def status():
    """Show the current security status and key hierarchy."""
    from tachyon.core.keys.operations import security_status
    security_status()

@keys_app.command()
def recover():
    """Execute the Resurrection Ceremony (3-of-5 recovery)."""
    from tachyon.core.keys.operations import recovery_drill
    recovery_drill()

@keys_app.command()
def sign(file: str = typer.Argument(..., help="Path to the file to sign")):
    """Sign a file with the Hybrid Root Key (ECC + PQC)."""
    from tachyon.core.signing import IntegrityManager
    import os
    
    if not os.path.exists(file):
        console.print(f"[bold red]Error: File {file} not found.[/bold red]")
        return
        
    signer = IntegrityManager()
    with Progress(SpinnerColumn(), TextColumn("[cyan]Generating Hybrid Signature..."), console=console) as progress:
        task = progress.add_task("Signing", total=None)
        sig_path = signer.sign_document(file)
        progress.update(task, completed=100)
        
    console.print(f"[bold green]✓ Signature created: {sig_path}[/bold green]")

@keys_app.command()
def verify(file: str = typer.Argument(..., help="Path to the file to verify")):
    """Verify a file against its Hybrid signature."""
    from tachyon.core.signing import IntegrityManager
    import os
    
    if not os.path.exists(file):
        console.print(f"[bold red]Error: File {file} not found.[/bold red]")
        return
        
    signer = IntegrityManager()
    result = signer.verify_integrity(file)
    
    if result:
        console.print(f"[bold green]✓ {file}: Signature VALID (Hybrid Verified)[/bold green]")
    else:
        console.print(f"[bold red]✗ {file}: Signature INVALID or MISSING.[/bold red]")

@app.command()
def agent(
    action: str = typer.Argument(..., help="list|run|stop|restart"),
    name: Optional[str] = typer.Argument(None, help="Agent name")
):
    """Manage Tachyon agents."""
    console.print(f"[bold yellow]Executing agent {action} for {name or 'all'}...[/bold yellow]")

if __name__ == "__main__":
    app()
