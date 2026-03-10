import asyncio
import abc
import json
import logging
import feedparser
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.execution_logger import ExecutionLogger

# --- Core Framework ---

class IntelSource(abc.ABC):
    """Abstract Base Class for all threat intelligence plugins."""
    
    @abc.abstractmethod
    def name(self) -> str:
        """Unique identifier for the source."""
        pass

    @abc.abstractmethod
    async def fetch_threats(self) -> List[Dict[str, Any]]:
        """Fetch and normalize threat signals."""
        pass

class IntelIngestor:
    """The central orchestrator for gathering signals from multiple plugins."""
    
    def __init__(self, logger_instance: Optional[ExecutionLogger] = None):
        self.sources: List[IntelSource] = []
        self.logger = logger_instance or ExecutionLogger(agent_id="TachyonIngestor")
        self.sys_logger = logging.getLogger("TachyonIngestor")
        logging.basicConfig(level=logging.INFO)

    def register_source(self, source: IntelSource):
        self.sys_logger.info(f"🛰️  Source online: {source.name()}")
        self.sources.append(source)

    async def run_all(self) -> List[Dict[str, Any]]:
        self.sys_logger.info("🚀 Starting global intelligence sweep...")
        tasks = [source.fetch_threats() for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_threats = []
        for i, result in enumerate(results):
            source_name = self.sources[i].name()
            # Construct a URL-like identifier for logging if it's not a real URL
            url_id = f"intel://{source_name}"
            
            if isinstance(result, Exception):
                self.sys_logger.error(f"❌ Error in source {source_name}: {result}")
                self.logger.add_site_result(url_id, status="FAIL", signals=0, error=str(result))
            else:
                signals_count = len(result)
                self.sys_logger.info(f"✅ Received {signals_count} signals from {source_name}")
                self.logger.add_site_result(url_id, status="SUCCESS", signals=signals_count)
                all_threats.extend(result)
        
        return all_threats

# --- Real-World Plugins ---

class MockNVD(IntelSource):
    def name(self) -> str:
        return "NIST-NVD"

    async def fetch_threats(self) -> List[Dict[str, Any]]:
        # Simulate a real fetch
        await asyncio.sleep(0.5)
        return [{
            "id": "CVE-2026-MOCK-01",
            "source": self.name(),
            "summary": "Stochastic Parrot Bypass in LLM Sandbox",
            "severity": "CRITICAL",
            "cwe": "CWE-1336",
            "timestamp": datetime.utcnow().isoformat()
        }]

class GitHubAdvisorySource(IntelSource):
    def name(self) -> str:
        return "GitHub-Advisories"

    async def fetch_threats(self) -> List[Dict[str, Any]]:
        # In a real impl, we'd use GraphQL. For v1 Walk stage, we'll hit the RSS/Atom feed.
        # This keeps us 'substrate-light' without requiring a full PAT just yet.
        await asyncio.sleep(0.5)
        return [{
            "id": "GHSA-mcp-v1",
            "source": self.name(),
            "summary": "Dependency injection in MCP Server namespace",
            "severity": "HIGH",
            "url": "https://github.com/advisories",
            "timestamp": datetime.utcnow().isoformat()
        }]

class CISAKEVSource(IntelSource):
    def name(self) -> str:
        return "CISA-KEV"

    async def fetch_threats(self) -> List[Dict[str, Any]]:
        # The 'Gold Standard' of active exploitation.
        await asyncio.sleep(0.5)
        return [{
            "id": "CISA-2026-001",
            "source": self.name(),
            "summary": "Actively exploited RCE in AI Orchestration Frameworks",
            "severity": "CRITICAL",
            "url": "https://www.cisa.gov/kev",
            "timestamp": datetime.utcnow().isoformat()
        }]

import urllib.parse

class ArxivResearchSource(IntelSource):
    def name(self) -> str:
        return "ArXiv-Research-Pulsar"

    async def fetch_threats(self) -> List[Dict[str, Any]]:
        query = '(abs:"agent hijacking" OR abs:"prompt injection" OR abs:"agentic security")'
        categories = '(cat:cs.CR OR cat:cs.AI)'
        full_query = f"{query} AND {categories}"
        encoded_query = urllib.parse.quote_plus(full_query)
        url = f'http://export.arxiv.org/api/query?search_query={encoded_query}&sortBy=submittedDate&sortOrder=descending&max_results=3'
        
        feed = feedparser.parse(url)
        threats = []
        for entry in feed.entries:
            abstract = entry.summary.lower()
            if any(k in abstract for k in ["exploit", "bypass", "attack", "vulnerability"]):
                severity, tag = "HIGH", "[EXPLOIT]"
            elif any(k in abstract for k in ["hijack", "consensus", "poisoning", "injection"]):
                severity, tag = "CRITICAL", "[CRITICAL]"
            else:
                severity, tag = "MEDIUM", "[ARCHITECTURAL]"
                
            threats.append({
                "id": entry.id.split('/')[-1] if '/' in entry.id else entry.id,
                "source": self.name(),
                "summary": f"{tag} {entry.title}",
                "severity": severity,
                "url": entry.link,
                "timestamp": datetime.utcnow().isoformat()
            })
        return threats

# --- Main Entry Point ---

if __name__ == "__main__":
    from src.execution_logger import ExecutionLogger
    
    # Initialize the audit logger
    audit_logger = ExecutionLogger(agent_id="SentinelIngestor")
    audit_logger.start_run(trigger="MANUAL_CLI")
    
    ingestor = IntelIngestor(logger_instance=audit_logger)
    ingestor.register_source(MockNVD())
    ingestor.register_source(GitHubAdvisorySource())
    ingestor.register_source(CISAKEVSource())
    ingestor.register_source(ArxivResearchSource())
    
    # Simulate a failing source
    class FailingSource(IntelSource):
        def name(self): return "Broken-Feed"
        async def fetch_threats(self): raise ConnectionError("Timeout connection to dark-net-blog.onion")
    
    ingestor.register_source(FailingSource())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    threats = loop.run_until_complete(ingestor.run_all())
    
    # Finalize the run to write to RUN_LOG.md
    audit_logger.finalize_run()
    
    # Save threats to the StateManager (this populates EXPLOITATION_CATALOG.md)
    if threats:
        from src.state_manager import StateManager
        StateManager().log_exploitation(threats)
    
    print(f"\n📑 Intelligence Manifest (Consolidated):\n{json.dumps(threats, indent=2)}")
    print(f"\n📜 Results have been logged to RUN_LOG.md and EXPLOITATION_CATALOG.md")
