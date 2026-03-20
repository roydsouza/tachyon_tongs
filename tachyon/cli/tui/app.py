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
            yield Static("📟 EVOLUTION FEED\nStreaming...", id="feed", classes="manifold")
            yield Static("🧤 AIRLOCK QUEUE\nLoading...", id="airlock", classes="manifold")
        yield Footer()

    async def on_mount(self) -> None:
        self.set_interval(2.0, self.refresh_data)
        await self.refresh_data()

    async def refresh_data(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                # Parallel fetch
                status_res, agents_res, airlock_res = await asyncio.gather(
                    client.get(f"{SUBSTRATE_URL}/status"),
                    client.get(f"{SUBSTRATE_URL}/agents"),
                    client.get(f"{SUBSTRATE_URL}/airlock")
                )
                
                health = status_res.json()
                agents = agents_res.json()
                patches = airlock_res.json()

                # Update Manifolds
                self.query_one("#overview", Static).update(
                    f"🛰️ TACTICAL OVERVIEW\n"
                    f"Status: [bold green]{health['status'].upper()}[/bold green]\n"
                    f"Integrity: {'✓ VERIFIED' if health['integrity_verified'] else '✗ COMPROMISED'}\n"
                    f"Uptime: {health['uptime_seconds']}s"
                )
                self.query_one("#overview").remove_class("offline")

                agent_list = "\n".join([f"- {a['name']}: {a['status'].upper()}" for a in agents])
                self.query_one("#agents", Static).update(f"🤖 ACTIVE AGENTS\n{agent_list}")

                patch_list = "\n".join([f"- {p['id']}: {p['status'].upper()}" for p in patches[:5]])
                self.query_one("#airlock", Static).update(f"🧤 AIRLOCK QUEUE\n{patch_list or 'No pending patches'}")

        except Exception as e:
            self.query_one("#overview", Static).update(f"🛰️ TACTICAL OVERVIEW\n[bold red]SUBSTRATE OFFLINE[/bold red]\n{e}")
            self.query_one("#overview").add_class("offline")

if __name__ == "__main__":
    TachyonDash().run()
