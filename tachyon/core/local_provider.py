import httpx
import json
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("tachyon.core.local_provider")

class LocalModelProvider:
    """
    High-Assurance Local Model Provider using mlx_lm.
    Provides an OpenAI-compatible interface for local reasoning on Apple Silicon.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080/v1"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generates a completion using the local mlx_lm engine.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "local-model",
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": False
        }

        try:
            response = await self.client.post(f"{self.base_url}/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Local inference failed: {e}")
            raise

    async def is_healthy(self) -> bool:
        """Checks if the local mlx_lm engine is online and responding."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()
