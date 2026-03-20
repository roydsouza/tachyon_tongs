from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable
from textual.containers import Container, Grid

class TachyonDash(App):
    """The Tachyon Substrate TUI Dashboard."""
    
    CSS = """
    Screen {
        background: #0a0e14;
    }
    #manifolds {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 1fr 1fr;
        grid-columns: 1fr 1fr;
    }
    .manifold {
        border: double #82aaff;
        padding: 1;
        margin: 1;
    }
    """
    
    TITLE = "TACHYON SUBSTRATE DASHBOARD"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="manifolds"):
            yield Static("🛰️ TACTICAL OVERVIEW\nStatus: 🟢 OPERATIONAL\nIntegrity: ✓ VERIFIED", classes="manifold")
            yield Static("🤖 ACTIVE AGENTS\n- sentinel: RUNNING\n- guardian: RUNNING", classes="manifold")
            yield Static("📟 EVOLUTION FEED\n[07:12:34] Sentinel scan complete.\n[07:10:15] Guardian audit pass.", classes="manifold")
            yield Static("🧤 AIRLOCK QUEUE\n- patch-a3f92c: PENDING", classes="manifold")
        yield Footer()

if __name__ == "__main__":
    app = TachyonDash()
    app.run()
