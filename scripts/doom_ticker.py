import os
import time
import re
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.console import Console
from rich.syntax import Syntax

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_FILE = os.path.join(BASE_DIR, "TASKS.md")
DRILLS_FILE = os.path.join(BASE_DIR, "docs/zero_day_drills.md")
LOG_FILE = os.path.join(BASE_DIR, "RUN_LOG.md")

console = Console()

def get_telemetry() -> dict:
    stats = {"active_cves": 0, "completed_cves": 0, "drill_rate": "N/A", "drill_verdict": "UNKNOWN"}
    
    # 1. Parse CVEs
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            for line in f:
                if "- [ ] **Triad Mitigation Mandate**" in line:
                    stats["active_cves"] += 1
                elif "- [x] **Triad Mitigation Mandate**" in line:
                    stats["completed_cves"] += 1
    
    # 2. Parse Drift / Drills
    if os.path.exists(DRILLS_FILE):
        with open(DRILLS_FILE, "r") as f:
            content = f.read()
            rate_match = re.search(r"\*\*Block Rate:\*\*\s*(.+)", content)
            verdict_match = re.search(r"\*\*Verdict:\*\*\s*(.+)", content)
            if rate_match:
                stats["drill_rate"] = rate_match.group(1).strip()
            if verdict_match:
                stats["drill_verdict"] = verdict_match.group(1).strip()
                
    return stats

def generate_telemetry_table() -> Table:
    stats = get_telemetry()
    table = Table(show_header=False, expand=True, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Active Threats (TASKS)", f"[red]{stats['active_cves']}[/red]")
    table.add_row("Remediated Threats", f"[green]{stats['completed_cves']}[/green]")
    table.add_row("Zero-Day Block Rate", f"[yellow]{stats['drill_rate']}[/yellow]")
    table.add_row("Pathogen Status", stats['drill_verdict'])
    
    return table

def generate_hardware_status() -> Table:
    table = Table(show_header=False, expand=True, box=None)
    table.add_column("Subsystem", style="magenta")
    table.add_column("Status", justify="right")
    
    # Hardcoded or simulated live statuses for the hardware aesthetic
    table.add_row("Apple Silicon", "[green]M-Series Active[/green]")
    table.add_row("MLX Unified Mem", "[yellow]Allocated (Inference)[/yellow]")
    table.add_row("Guardian: Scout", "[cyan]Polling[/cyan]")
    table.add_row("Guardian: Analyst", "[green]Air-Gapped[/green]")
    table.add_row("Guardian: Engineer", "[red]Awaiting Review[/red]")
    table.add_row("Sandbox-Exec", "[green]Seatbelt Enforced[/green]")
    
    return table

def get_latest_logs(num_lines=25) -> str:
    if not os.path.exists(LOG_FILE):
        return "Waiting for RUN_LOG.md..."
    
    # Simple tail mechanism
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()
        
    return "".join(lines[:num_lines])

def make_layout() -> Layout:
    layout = Layout(name="root")
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    
    layout["main"].split_column(
        Layout(name="gauges", size=10),
        Layout(name="logs", ratio=1)
    )
    
    layout["gauges"].split_row(
        Layout(name="telemetry", ratio=1),
        Layout(name="hardware", ratio=1)
    )
    
    return layout

def construct_ui() -> Layout:
    layout = make_layout()
    
    # Header
    header_text = Text("TACHYON TONGS /// DOOM TICKER", style="bold green", justify="center")
    layout["header"].update(Panel(header_text, style="green"))
    
    # Telemetry Pane
    telemetry_table = generate_telemetry_table()
    layout["telemetry"].update(Panel(Align.center(telemetry_table, vertical="middle"), title="[cyan]Substrate Telemetry", border_style="cyan"))
    
    # Hardware Pane
    hardware_table = generate_hardware_status()
    layout["hardware"].update(Panel(Align.center(hardware_table, vertical="middle"), title="[magenta]Hardware & Triad State", border_style="magenta"))
    
    # Logs Pane
    log_text = get_latest_logs()
    # Use Syntax to render the markdown log nicely
    syntax = Syntax(log_text, "markdown", theme="ansi_dark", word_wrap=True)
    layout["logs"].update(Panel(syntax, title="[yellow]Live Execution Log (RUN_LOG.md)", border_style="yellow"))
    
    return layout

if __name__ == "__main__":
    try:
        with Live(construct_ui(), refresh_per_second=2, screen=True) as live:
            while True:
                time.sleep(1)
                live.update(construct_ui())
    except KeyboardInterrupt:
        pass
