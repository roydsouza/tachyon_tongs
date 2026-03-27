import os
import uvicorn
import json
import asyncio
from typing import List, Set
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from tachyon.api.routes import router as api_v1_router

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Connection might be closed but not yet disconnected
                pass

manager = ConnectionManager()
background_tasks: Set[asyncio.Task] = set()

async def telemetry_broadcaster():
    """Background task to poll TelemetryBus and broadcast to all WebSockets."""
    from tachyon.core.telemetry import TelemetryBus
    bus = TelemetryBus()
    last_id = 0
    
    # Initialize last_id to current latest so we don't dump the whole history immediately
    try:
        latest = bus.forensic_store.query_latest(limit=1)
        if latest:
            last_id = latest[0]['id']
    except Exception:
        pass

    while True:
        try:
            new_events = bus.get_events_after(last_id)
            for event in new_events:
                await manager.broadcast(event)
                last_id = event['id']
        except Exception as e:
            # Avoid tight loop on error
            await asyncio.sleep(1)
            
        await asyncio.sleep(0.5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    task = asyncio.create_task(telemetry_broadcaster())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    yield
    # Shutdown logic
    for task in background_tasks:
        task.cancel()

app = FastAPI(
    title="Tachyon Tongs: Unified Substrate Daemon",
    version="1.0.0",
    description="Unified API for Substrate Control, PEP, and Airlock Telemetry.",
    lifespan=lifespan
)

# Parallel Tier: Unified V1 API
app.include_router(api_v1_router)

@app.websocket("/api/v1/logs/stream")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open and wait for messages from client (if any)
            await websocket.receive_text()
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
