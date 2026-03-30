import logging
from typing import Dict, Any, Optional
from event_horizon_core.providers.ollama_provider import OllamaProvider
from event_horizon_core.providers.mlx_provider import MLXProvider

logger = logging.getLogger("tachyon.core.local_provider")

class LocalModelProvider:
    """
    High-Assurance Local Model Provider (Re-routed to Event Horizon Core).
    Provides an OpenAI-compatible interface for local reasoning on Apple Silicon.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "llama3.2"):
        # By default, use Ollama as it is the most stable OpenAI-compatible bridge
        self.provider = OllamaProvider(base_url=base_url, model=model)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generates a completion using the local event-horizon-core engine.
        """
        try:
            # Note: Event Horizon Core providers are synchronous by design to 
            # match MLX/Ollama CLI behavior, so we wrap them for async compatibility if needed.
            return self.provider.generate(prompt, system_prompt=system_prompt, **kwargs)
        except Exception as e:
            logger.error(f"Local inference failed: {e}")
            raise

    async def is_healthy(self) -> bool:
        """Checks if the local engine is online."""
        return self.provider.is_healthy()

    async def close(self):
        """Cleanup."""
        pass
