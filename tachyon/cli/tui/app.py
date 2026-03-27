from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Log, Input
from textual.containers import Container, Grid, Vertical, Horizontal
from textual.reactive import reactive
from textual.message import Message
import json
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional

SUBSTRATE_URL = "http://127.0.0.1:60461/api/v1"

class TacticalOverview(Static):
    """Widget for Substrate health and traffic metrics."""
    def update_metrics(self, health: dict, traffic: dict) -> None:
        status_val = health.get("status", "offline").upper()
        status_color = "green" if status_val == "ACTIVE" else "yellow"
        status_label = " [OK]" if status_val == "ACTIVE" else ""
        integrity = "[green]VERIFIED [OK][/green]" if health.get("integrity_verified") else "[red]COMPROMISED [FAIL][/red]"
        
        self.update(
            f"[bold blue]🛰️ TACTICAL OVERVIEW[/bold blue]\n\n"
            f"Status:    [{status_color}]{status_val}{status_label}[/{status_color}]\n"
            f"Integrity: {integrity}\n"
            f"Uptime:    [cyan]{health.get('uptime_seconds', 0)}s[/cyan]\n\n"
            f"[bold blue]🚦 TRAFFIC SUMMARY[/bold blue]\n\n"
            f"Total:     [white]{traffic.get('total', 0)}[/white]\n"
            f"Internal:  [green]{traffic.get('internal', 0)}[/green]\n"
            f"Transit:   [bold magenta][T] {traffic.get('transit', 0)}[/bold magenta]\n"
            f"Blocked:   [red]{traffic.get('deny', 0)}[/red]"
        )

class AgentInventory(Static):
    """Widget for listing active agent status."""
    def update_agents(self, agents: List[Dict[str, Any]]) -> None:
        lines = ["[bold blue]🤖 ACTIVE AGENTS[/bold blue]\n"]
        for a in agents:
            status = a.get("status", "idle").upper()
            status_text = f"{status} [OK]" if status == "RUNNING" else f"{status} [WAIT]"
            color = "green" if status == "RUNNING" else "yellow"
            lines.append(f"- [bold]{a['name']:<12}[/bold] [{color}]{status_text:<12}[/{color}] [cyan]{a.get('last_action', 'Idle')}[/cyan]")
        self.update("\n".join(lines))

class HeraldLog(Log):
    """Rich log for real-time forensic events."""
    def add_event(self, event: Dict[str, Any]) -> None:
        ts = event.get("timestamp", "").split("T")[-1][:8]
        source = event.get("source", "internal")
        badge = " [bold magenta][T][/bold magenta]" if source == "transit" else ""
        topic = event.get("event_type", "UNKNOWN")
        agent = event.get("agent_id", "system")
        
        color = "white"
        prefix = ""
        if any(x in topic for x in ["VIOLATION", "FAILURE", "BLOCKED", "ERROR"]):
            color = "red"
            prefix = "[!] "
        elif "SIGNATURE" in topic:
            color = "cyan"
            prefix = "[*] "
            
        self.write_line(f"[{ts}] {badge}[{color}]{prefix}{topic:<15}[/{color}] | {agent:<12} | {event.get('action')}")

class AirlockQueue(Static):
    """Widget for pending patches and quarantine status."""
    def update_patches(self, patches: List[Dict[str, Any]]) -> None:
        lines = ["[bold blue]🧤 AIRLOCK QUEUE[/bold blue]\n"]
        if not patches:
            lines.append("[italic white]No pending patches[/italic white]")
        else:
            for p in patches[:5]:
                status = p.get("status", "pending").upper()
                lines.append(f"- [bold]{p['id']}[/bold] [{status}]")
        self.update("\n".join(lines))

class CommandShell(Input):
    """Secure command input with signed command routing."""
    def on_mount(self) -> None:
        self.placeholder = "Enter signed command (e.g. tt sentinel start)..."
        self.border_title = "COMMAND SHELL"

    async def action_submit(self) -> None:
        cmd = self.value
        if cmd.strip():
            self.app.query_one("#forensics", HeraldLog).write_line(f"[bold cyan][CMD][/bold cyan] {cmd}")
            # Placeholder for actual 'tt' subprocess integration
        self.value = ""

class TachyonDash(App):
    """The Tachyon Substrate SPOG Dashboard (v2)."""
    
    CSS = """
    Screen { background: #0a0e14; }
    #manifolds { layout: grid; grid-size: 2 2; height: 1fr; }
    .manifold { border: double #82aaff; padding: 1; margin: 0; height: 100%; }
    #overview { row-span: 1; }
    #agents { row-span: 1; }
    #forensics { row-span: 1; column-span: 2; height: 100%; border: double #82aaff; }
    #airlock { row-span: 1; }
    
    #shell { border: double #82aaff; margin: 0; background: #0c111a; }
    Log { background: #0c111a; border: none; }
    Static { color: #82aaff; }
    """
    
    TITLE = "TACHYON SUBSTRATE DASHBOARD"
    SUB_TITLE = "Single Pane of Glass | [T] = Transit Traffic"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Force Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="manifolds"):
            yield TacticalOverview(id="overview", classes="manifold")
            yield AgentInventory(id="agents", classes="manifold")
            yield HeraldLog(id="forensics", classes="manifold")
            yield AirlockQueue(id="airlock", classes="manifold")
        yield CommandShell(id="shell")
        yield Footer()

    async def on_mount(self) -> None:
        self.last_seen_id = 0
        self.set_interval(0.5, self.poll_telemetry)
        self.set_interval(2.0, self.refresh_metadata)
        
        # Initial query for historical context
        await self.refresh_metadata()

    async def poll_telemetry(self) -> None:
        """Polls for new forensic events using incremental ID tracking."""
        try:
            async with httpx.AsyncClient(timeout=0.2) as client:
                # We use the implicit get_events functionality if query_after route is not exposed,
                # but we'll try to fetch latest forensics
                res = await client.get(f"{SUBSTRATE_URL}/forensics?limit=5")
                events = res.json()
                # events is sorted latest first. Reverse to append in order.
                for event in reversed(events):
                    eid = event.get('id', 0)
                    if eid > self.last_seen_id:
                        self.query_one("#forensics", HeraldLog).add_event(event)
                        self.last_seen_id = eid
        except Exception:
            pass

    async def refresh_metadata(self) -> None:
        """Refreshes status, agents, and airlock metrics."""
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                # Parallel fetch of core metrics
                status_task = client.get(f"{SUBSTRATE_URL}/status")
                agents_task = client.get(f"{SUBSTRATE_URL}/agents")
                airlock_task = client.get(f"{SUBSTRATE_URL}/airlock")
                traffic_task = client.get(f"{SUBSTRATE_URL}/traffic/summary")
                
                results = await asyncio.gather(
                    status_task, agents_task, airlock_task, traffic_task,
                    return_exceptions=True
                )
                
                if isinstance(results[0], httpx.Response):
                    self.query_one("#overview", TacticalOverview).update_metrics(
                        results[0].json(), 
                        results[3].json() if not isinstance(results[3], Exception) else {}
                    )
                
                if isinstance(results[1], httpx.Response):
                    self.query_one("#agents", AgentInventory).update_agents(results[1].json())
                    
                if isinstance(results[2], httpx.Response):
                    self.query_one("#airlock", AirlockQueue).update_patches(results[2].json())

        except Exception as e:
            # Silent failure for transients; fallbacks handled in UI if needed
            pass

if __name__ == "__main__":
    TachyonDash().run()
