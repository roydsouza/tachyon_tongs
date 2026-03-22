import asyncio
import httpx
import logging
from tachyon.core.local_provider import LocalModelProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_local")

async def test_live_local():
    provider = LocalModelProvider()
    print("--- LIVE LOCAL REASONING TEST ---")
    
    # 1. Health Check
    is_up = await provider.is_healthy()
    if not is_up:
        print("FAIL: mlx_lm engine is not running on port 8080.")
        return
    
    print("SUCCESS: mlx_lm engine is online.")
    
    # 2. Simple Reasoning Test
    try:
        response = await provider.generate(
            prompt="What is the current status of the Tachyon Tongs local reasoning substrate?",
            system_prompt="You are the Tachyon Tongs Local Reasoning Substrate."
        )
        print(f"RESPONSE: {response}")
        print("SUCCESS: Local reasoning confirmed.")
    except Exception as e:
        print(f"FAIL: Inference error: {e}")
    finally:
        await provider.close()

if __name__ == "__main__":
    asyncio.run(test_live_local())
