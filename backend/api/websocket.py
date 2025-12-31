"""
NOVA Visualizer Backend - WebSocket API

Real-time WebSocket endpoint for streaming vessel updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import asyncio
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept new connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        if not self.active_connections:
            return
        
        # Send to all connections
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                dead_connections.add(connection)
        
        # Remove dead connections
        for conn in dead_connections:
            self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Sends two types of messages:
    1. vessel_update: Position updates
    2. anomaly_detected: New anomaly events
    """
    await manager.connect(websocket)
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for client message (ping/pong for keep-alive)
            data = await websocket.receive_text()
            
            # Echo pong
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_vessel_update(vessel_data: dict):
    """
    Broadcast vessel position update to all connected clients.
    
    Called by NATS subscriber when new data arrives.
    """
    message = {
        "type": "vessel_update",
        "data": vessel_data
    }
    await manager.broadcast(message)


async def broadcast_anomaly(anomaly_data: dict):
    """
    Broadcast anomaly detection to all connected clients.
    
    Called by NATS subscriber when anomaly is detected.
    """
    message = {
        "type": "anomaly_detected",
        "data": anomaly_data
    }
    await manager.broadcast(message)
