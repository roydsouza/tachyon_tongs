from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
import httpx
import asyncio

SUBSTRATE_URL = "http://127.0.0.1:60461/api/v1"

class TachyonDash(App):
    """The Tachyon Substrate TUI Dashboard."""
    
    CSS = """
    Screen { background: #0a0e14; }
    #manifolds { layout: grid; grid-size: 2 2; }
    .manifold { border: double #82aaff; padding: 1; margin: 1; height: 100%; }
    .offline { border: double #f07178; color: #f07178; }
    """
    
    TITLE = "TACHYON SUBSTRATE DASHBOARD"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="manifolds"):
            yield Static("🛰️ TACTICAL OVERVIEW\nLoading...", id="overview", classes="manifold")
            yield Static("🤖 ACTIVE AGENTS\nLoading...", id="agents", classes="manifold")
            yield Static("📟 FORENSIC FEED\nStreaming...", id="forensics", classes="manifold")
            yield Static("🧤 AIRLOCK QUEUE\nLoading...", id="airlock", classes="manifold")
        yield Footer()

    async def on_mount(self) -> None:
        self.set_interval(2.0, self.refresh_data)
        await self.refresh_data()

    async def refresh_data(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                # Parallel fetch
                status_res, agents_res, airlock_res, forensics_res = await asyncio.gather(
                    client.get(f"{SUBSTRATE_URL}/status"),
                    client.get(f"{SUBSTRATE_URL}/agents"),
                    client.get(f"{SUBSTRATE_URL}/airlock"),
                    client.get(f"{SUBSTRATE_URL}/forensics")
                )
                
                health = status_res.json()
                agents = agents_res.json()
                patches = airlock_res.json()
                forensics = forensics_res.json()
                self.query_one("#overview").remove_class("offline")

        except Exception:
            # Phase 31.1: Local Diagnostic Fallback
            from tachyon.core.state import StateManager
            from tachyon.core.keys.operations import get_delegation_summary
            state = StateManager()
            import sqlite3
            with sqlite3.connect(state.db_path) as conn:
                att_count = conn.execute("SELECT COUNT(*) FROM package_attestations").fetchone()[0]
                wl_count = conn.execute("SELECT COUNT(*) FROM package_whitelist").fetchone()[0]
            delegations = get_delegation_summary()
            anchored = sum(1 for a in delegations.values() if a["status"] == "Anchored")

            health = {
                "status": "diagnostic (offline)",
                "integrity_verified": True,
                "uptime_seconds": 0,
                "supply_chain": f"{att_count}/{wl_count}",
                "keys": f"{anchored}/{len(delegations)}"
            }
            agents = [{"name": "Auditor", "status": "idle"}]
            patches = []
            forensics = []
            self.query_one("#overview").add_class("offline")

        # Update Manifolds
        self.query_one("#overview", Static).update(
            f"🛰️ TACTICAL OVERVIEW\n"
            f"Status: [bold yellow]{health['status'].upper()}[/bold yellow]\n"
            f"Integrity: {'[green]✓[/green]' if health['integrity_verified'] else '[red]✗[/red]'}\n"
            f"Supply Chain: [cyan]{health.get('supply_chain', '0/0')}[/cyan]\n"
            f"Agent Keys: [magenta]{health.get('keys', '0/3')}[/magenta]"
        )
        
        agent_list = "\n".join([f"- {a['name']}: {a['status'].upper()}" for a in agents])
        self.query_one("#agents", Static).update(f"🤖 ACTIVE AGENTS\n{agent_list}")

        patch_list = "\n".join([f"- {p['id']}: {p['status'].upper()}" for p in patches[:5]])
        self.query_one("#airlock", Static).update(f"🧤 AIRLOCK QUEUE\n{patch_list or 'No pending patches'}")

        alert_lines = []
        for f in forensics[:5]:
            color = "red" if any(x in f['topic'] for x in ["VIOLATION", "ANOMALY", "CRASH"]) else "yellow"
            alert_lines.append(f"- [{color}]{f['topic']}[/{color}]: {f['agent_id']}")
        
        self.query_one("#forensics", Static).update(f"📟 FORENSIC FEED\n" + ("\n".join(alert_lines) or "No active alerts"))

if __name__ == "__main__":
    TachyonDash().run()
