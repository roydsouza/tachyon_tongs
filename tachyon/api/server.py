import os
import uvicorn
import json
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from tachyon.api.routes import router as api_v1_router

app = FastAPI(
    title="Tachyon Tongs: Unified Substrate Daemon",
    version="1.0.0",
    description="Unified API for Substrate Control, PEP, and Airlock Telemetry."
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

# Parallel Tier: Unified V1 API
app.include_router(api_v1_router)

@app.websocket("/api/v1/logs/stream")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Simple heartbeat/streaming pulse
            await asyncio.sleep(1)
            # In a real impl, this would poll StateManager for new EVOLUTION.md entries
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health():
    return {"status": "ok", "engine": "Metal 4 / Apple Silicon"}

def main():
    port = int(os.environ.get("TACHYON_PORT", 60461))
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    main()
