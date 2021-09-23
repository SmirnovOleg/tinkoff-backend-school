from asyncio import Lock
from typing import List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self.lock = Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self.lock:
            self.active_connections.remove(websocket)
            await websocket.close()

    async def broadcast(self, message: str) -> None:
        async with self.lock:
            for connection in self.active_connections:
                await connection.send_text(message)


manager = ConnectionManager()
