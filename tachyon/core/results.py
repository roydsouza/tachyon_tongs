from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field

class TachyonStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    DENIED = "DENIED"
    FATAL = "FATAL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

class TachyonResult(BaseModel):
    """
    Standardized result monad for all agent actions.
    Ensures type-safe and predictable error handling across the substrate.
    """
    status: TachyonStatus = Field(default=TachyonStatus.SUCCESS)
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def success(cls, data: Any = None, **metadata) -> "TachyonResult":
        """Helper to create a success result."""
        return cls(status=TachyonStatus.SUCCESS, data=data, metadata=metadata)

    @classmethod
    def failure(cls, error: str, status: TachyonStatus = TachyonStatus.ERROR, **metadata) -> "TachyonResult":
        """Helper to create a failure result."""
        return cls(status=status, error=error, metadata=metadata)

    def is_success(self) -> bool:
        """Return True if the result was successful."""
        return self.status == TachyonStatus.SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for legacy support or serialization."""
        return self.model_dump()
