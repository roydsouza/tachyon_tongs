from textual.widgets import Header, Footer, Static, ListView, ListItem, Label, Log, Input
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
import os
import json
import re

class ThreatItem(ListItem):
    def __init__(self, cve_id: str, description: str):
        super().__init__()
        self.cve_id = cve_id
        self.description = description
        self.proposal_path = None

    def compose(self) -> ComposeResult:
        yield Label(f"[bold red]![/bold red] {self.cve_id}")

class AirlockApp(App):
    """The Tachyon Tongs Airlock TUI."""

    CSS = """
    Screen {
        background: #0d1117;
    }

    #sidebar {
        width: 30%;
        border-right: solid #30363d;
        background: #161b22;
    }

    #main_content {
        width: 70%;
    }

    #proposal_viewer {
        height: 50%;
        border-bottom: solid #30363d;
        padding: 1;
    }

    #chat_section {
        height: 50%;
    }

    #chat_log {
        height: 80%;
        padding: 1;
    }

    #chat_input {
        height: 20%;
        border-top: solid #30363d;
        background: #0d1117;
    }

    .header-text {
        text-align: center;
        color: #58a6ff;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh Threats"),
        Binding("a", "authorize", "Authorize Patch", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="outer"):
            with Horizontal():
                with Vertical(id="sidebar"):
                    yield Label(" [bold cyan]ACTIVE THREATS[/bold cyan]", classes="header-text")
                    yield ListView(id="threat_list")
                with Vertical(id="main_content"):
                    yield Static("Select a threat to view proposal", id="proposal_viewer")
                    with Vertical(id="chat_section"):
                        yield Log(id="chat_log")
                        yield Input(placeholder="Interrogate the Engineer Agent...", id="chat_input")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "TACHYON TONGS /// AIRLOCK INTERFACE"
        self.refresh_threats()

    def refresh_threats(self) -> None:
        threat_list = self.query_one("#threat_list", ListView)
        threat_list.clear()
        
        # 1. Parse TASKS.md for [URGENT] mandates
        tasks_file = "TASKS.md"
        threats = []
        if os.path.exists(tasks_file):
            with open(tasks_file, "r") as f:
                for line in f:
                    if "- [ ]" in line and "CVE-" in line:
                        match = re.search(r"(CVE-\d+-\d+)", line)
                        if match:
                            cve = match.group(1)
                            threats.append((cve, "Awaiting analysis..."))

        # 2. Match with staged proposals in /tmp/tachyon_airlock
        staging_dir = "/tmp/tachyon_airlock"
        if os.path.exists(staging_dir):
            for filename in os.listdir(staging_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(staging_dir, filename), "r") as f:
                        data = json.load(f)
                        cve = data.get("cve_id")
                        # Update or add
                        found = False
                        for i, (t_cve, t_desc) in enumerate(threats):
                            if t_cve == cve:
                                threats[i] = (cve, data.get("description", "Staged for review"))
                                found = True
                                break
                        if not found:
                            threats.append((cve, data.get("description", "Staged for review")))
        
        for cve, desc in threats:
            item = ThreatItem(cve, desc)
            # Tag the item if it has a real proposal
            proposal_path = os.path.join(staging_dir, f"{cve.replace(' ', '_')}.json")
            if os.path.exists(proposal_path):
                item.proposal_path = proposal_path
            else:
                item.proposal_path = None
            threat_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, ThreatItem):
            viewer = self.query_one("#proposal_viewer", Static)
            if event.item.proposal_path:
                with open(event.item.proposal_path, "r") as f:
                    data = json.load(f)
                    
                patch_view = ""
                for file_path, content in data.get("patch_files", {}).items():
                    patch_view += f"[green]FILE:[/green] {file_path}\n"
                    patch_view += f"--- {file_path}\n"
                    patch_view += f"+++ {file_path}\n"
                    # In a real tool we'd generate a real diff here, for now showing preview
                    patch_view += "[blue]... patches synthesized ...[/blue]\n\n"

                critique = data.get("critique", {})
                critique_view = f"\n[bold magenta]SKEPTIC CRITIQUE:[/bold magenta]\n"
                critique_view += f"Verdict: {'[green]PASS[/green]' if critique.get('verdict') == 'pass' else '[red]FAIL[/red]'}\n"
                critique_view += f"Risk Score: {critique.get('risk_score', 0.0)}\n"
                for concern in critique.get("concerns", ["No structural flaws detected by current heuristics."]):
                    critique_view += f"- {concern}\n"

                viewer.update(
                    f"[bold yellow]PROPOSAL: {data['cve_id']}[/bold yellow]\n\n"
                    f"[cyan]Analysis:[/cyan] {data['description']}\n"
                    f"{critique_view}\n"
                    f"{patch_view}"
                )
                self.query_one("#chat_log", Log).write(f"> Loaded staged proposal for {data['cve_id']}")
                self.selected_cve = data['cve_id']
            else:
                viewer.update(f"[bold red]NO PROPOSAL STAGED FOR {event.item.cve_id}[/bold red]\n\nRun Sentinel to generate a mitigation strategy.")
                self.query_one("#chat_log", Log).write(f"> {event.item.cve_id} has no staged proposal.")
                self.selected_cve = None

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not event.value.strip():
            return
        
        chat_log = self.query_one("#chat_log", Log)
        chat_log.write(f"[bold white]You:[/bold white] {event.value}")
        
        # Simulating Engineer Agent response
        # In Phase 7.1 we'll wire this to a real LLM call via MetalAccelerator
        if self.selected_cve:
            chat_log.write(f"[bold cyan]Engineer Agent:[/bold cyan] Analyzing your request regarding {self.selected_cve}...")
            chat_log.write(f"[italic gray]Simulation: The agent would now explain its reasoning for the patch...[/italic gray]")
        else:
            chat_log.write(f"[bold cyan]Engineer Agent:[/bold cyan] Please select a threat context from the sidebar first.")
            
        event.input.value = ""

if __name__ == "__main__":
    app = AirlockApp()
    app.run()
