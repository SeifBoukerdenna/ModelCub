"""WebSocket connection manager for real-time updates."""
from typing import Dict, Optional
from uuid import uuid4
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """Accept new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket connection

        Returns:
            Unique client ID
        """
        await websocket.accept()
        client_id = str(uuid4())
        self.active_connections[client_id] = websocket
        logger.info(
            f"Client {client_id} connected. "
            f"Total connections: {len(self.active_connections)}"
        )
        return client_id

    def disconnect(self, client_id: str) -> None:
        """Remove WebSocket connection.

        Args:
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(
                f"Client {client_id} disconnected. "
                f"Total connections: {len(self.active_connections)}"
            )

    async def send_to_client(self, client_id: str, message: dict) -> None:
        """Send message to specific client.

        Args:
            client_id: Target client ID
            message: Message data (will be JSON serialized)
        """
        websocket = self.active_connections.get(client_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict, exclude: Optional[str] = None) -> None:
        """Broadcast message to all connected clients.

        Args:
            message: Message data (will be JSON serialized)
            exclude: Optional client ID to exclude from broadcast
        """
        disconnected = []

        for client_id, websocket in self.active_connections.items():
            if client_id == exclude:
                continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)