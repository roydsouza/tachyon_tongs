import pytest
import os
import sqlite3
from tachyon.api.pep import PEPLayer, ToolRequest
from tachyon.core.forensics import ForensicStore

@pytest.mark.asyncio
async def test_transit_tagging():
    """INT-02: Verify that requests from external tenants are tagged as transit."""
    pep = PEPLayer()
    
    # Internal Request (default tenant)
    req_internal = ToolRequest(
        agent_id="sentinel",
        action="GenericAction",
        parameters={"foo": "bar"},
        tenant_id="default"
    )
    await pep.execute(req_internal)
    
    # Transit Request (external tenant)
    req_transit = ToolRequest(
        agent_id="external-agent-X",
        action="GenericAction",
        parameters={"foo": "baz"},
        tenant_id="external-tenant-001"
    )
    await pep.execute(req_transit)
    
    # Query Forensics to verify tagging
    store = ForensicStore()
    latest = store.query_latest(limit=2)
    
    # Note: query_latest returns most recent first
    # So index 0 should be transit, index 1 should be internal
    
    # Before INT-02 implementation, 'source' column won't exist or won't be in the dict
    # This test will likely fail with KeyError or by finding "internal" in both if defaulted.
    
    transit_event = latest[0]
    internal_event = latest[1]
    
    assert "source" in transit_event, "Forensic event should have a 'source' field."
    assert transit_event["source"] == "transit", f"Expected 'transit', got {transit_event['source']}"
    assert internal_event["source"] == "internal", f"Expected 'internal', got {internal_event['source']}"

def test_forensic_store_source_column():
    """INT-02: Verify that the 'source' column exists in the database schema."""
    store = ForensicStore()
    with sqlite3.connect(store.db_path) as conn:
        cursor = conn.execute("PRAGMA table_info(forensic_log)")
        columns = [row[1] for row in cursor.fetchall()]
        assert "source" in columns, f"'source' column missing from forensic_log table. Found: {columns}"
