import asyncio
import json
import logging
from typing import Set
from fastapi import WebSocket

logger = logging.getLogger("websocket_hub")


class WebSocketHub:
    """
    Manages active frontend WebSocket client connections and broadcasts
    live telemetry, frame states, alerts, and playlist updates.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Active clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Active clients: {len(self.active_connections)}")

    async def broadcast_json(self, data: dict):
        if not self.active_connections:
            return

        message = json.dumps(data)
        dead_connections = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.add(connection)

        for dead in dead_connections:
            self.active_connections.discard(dead)

    def broadcast_sync(self, data: dict):
        """Thread-safe synchronous broadcast for background worker threads."""
        if not self.active_connections:
            return

        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast_json(data), self._loop)


# Global WebSocket Hub Singleton
ws_hub = WebSocketHub()
