from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class Verdict(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ERROR = "ERROR"

@dataclass
class PolicyVerdict:
    verdict: Verdict
    reason: str
    engine_id: str
    metadata: Optional[Dict[str, Any]] = None

class PolicyEngine(ABC):
    """
    Abstract Policy Engine Interface for Tachyon Tongs.
    All plugins (Rego, Cedar, etc.) must implement this contract.
    """
    
    @abstractmethod
    def evaluate(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        """
        Evaluate an action against the engine's policy set.
        """
        pass

    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Unique identifier for this engine."""
        pass
