import asyncio
import json
import logging
from collections import defaultdict
from fastapi import WebSocket, WebSocketDisconnect
from app.schemas import WSEvent
logger = logging.getLogger(__name__)
class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[job_id].add(websocket)
        logger.debug("WS connect: job=%s total_sockets=%d", job_id, len(self._connections[job_id]))
    def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        self._connections[job_id].discard(websocket)
        if not self._connections[job_id]:
            del self._connections[job_id]
    async def broadcast(self, job_id: str, event: WSEvent) -> None:
        if job_id not in self._connections:
            return
        payload = event.model_dump_json()
        dead: set[WebSocket] = set()
        for ws in self._connections[job_id]:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(job_id, ws)
    async def broadcast_dict(self, job_id: str, data: dict) -> None:
        if job_id not in self._connections:
            return
        payload = json.dumps(data)
        dead: set[WebSocket] = set()
        for ws in self._connections[job_id]:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(job_id, ws)
    @property
    def active_jobs(self) -> list[str]:
        return list(self._connections.keys())
ws_manager = ConnectionManager()
