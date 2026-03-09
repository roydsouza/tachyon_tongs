import asyncio
import abc
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

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
    
    def __init__(self):
        self.sources: List[IntelSource] = []
        self.logger = logging.getLogger("TachyonIngestor")
        logging.basicConfig(level=logging.INFO)

    def register_source(self, source: IntelSource):
        self.logger.info(f"🛰️  Source online: {source.name()}")
        self.sources.append(source)

    async def run_all(self) -> List[Dict[str, Any]]:
        self.logger.info("🚀 Starting global intelligence sweep...")
        tasks = [source.fetch_threats() for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_threats = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Error in source {self.sources[i].name()}: {result}")
            else:
                self.logger.info(f"✅ Received {len(result)} signals from {self.sources[i].name()}")
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

# --- Main Entry Point ---

if __name__ == "__main__":
    ingestor = IntelIngestor()
    ingestor.register_source(MockNVD())
    ingestor.register_source(GitHubAdvisorySource())
    ingestor.register_source(CISAKEVSource())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    threats = loop.run_until_complete(ingestor.run_all())
    
    print(f"\n📑 Intelligence Manifest (Consolidated):\n{json.dumps(threats, indent=2)}")
