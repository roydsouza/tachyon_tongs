import pytest
from typer.testing import CliRunner
from tachyon.cli.main import app
import json

runner = CliRunner()

def test_tt_ritual():
    """Verify the ritual boot ceremony command executes successfully."""
    result = runner.invoke(app, ["ritual"])
    assert result.exit_code == 0
    assert "Substrate Boot Ceremony" in result.stdout
    assert "Ritual Complete" in result.stdout

def test_tt_status_offline():
    """Verify status command handles offline daemon gracefully."""
    result = runner.invoke(app, ["status"])
    # Should show error message but exit 0 (graceful)
    assert "Error: Substrate Daemon is Offline" in result.stdout

def test_tt_status_json_offline():
    """Verify status --json handles offline daemon gracefully."""
    result = runner.invoke(app, ["status", "--json"])
    data = json.loads(result.stdout)
    assert data["error"] == "Substrate Offline"

def test_tt_airlock_offline():
    """Verify airlock command handles offline daemon gracefully."""
    result = runner.invoke(app, ["airlock"])
    assert "Daemon Offline" in result.stdout

def test_tt_dash_import():
    """Verify that the dash command can at least import its dependencies."""
    # We don't want to actually launch the TUI in a headless test
    # but we can check if the command exists and basic help works.
    result = runner.invoke(app, ["dash", "--help"])
    assert result.exit_code == 0
    assert "Launch the interactive TUI dashboard" in result.stdout
