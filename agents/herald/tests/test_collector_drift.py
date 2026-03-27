import pytest
import os
import re
from agents.herald.collectors.engine import FileLogCollector

def test_collector_drift_warning_success(capsys, tmp_path):
    """TDAD: Verifies that FileLogCollector now prints a warning on regex drift."""
    # Create a non-empty file with some text
    log_file = tmp_path / "DRIFT.md"
    log_file.write_text("This text does NOT match the regex pattern at all.\n" * 10) # > 100 bytes
    
    # regex that won't match
    collector = FileLogCollector(str(log_file), r"## \[(.*?)\] (.*?)\n")
    
    # Trigger collection
    events = collector.collect()
    
    assert len(events) == 0
    
    # Now it SHOULD print a warning
    captured = capsys.readouterr()
    assert "[FileLogCollector] WARNING" in captured.out
    assert "Pattern potential drift" in captured.out
