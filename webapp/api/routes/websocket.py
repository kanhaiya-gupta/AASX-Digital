"""
WebSocket routes for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging
from datetime import datetime

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "general": [],
            "twin_registry": [],
            "ai_rag": [],
            "kg_neo4j": [],
            "qi_analytics": [],
            "certificate_manager": [],
            "federated_learning": [],
            "physics_modeling": [],
            "aasx": []
        }
    
    async def connect(self, websocket: WebSocket, channel: str = "general"):
        """Connect a WebSocket to a specific channel"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logging.info(f"WebSocket connected to channel: {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str = "general"):
        """Disconnect a WebSocket from a channel"""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
        logging.info(f"WebSocket disconnected from channel: {channel}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        await websocket.send_text(message)
    
    async def broadcast_to_channel(self, message: str, channel: str = "general"):
        """Broadcast a message to all connections in a channel"""
        if channel in self.active_connections:
            disconnected = []
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[channel].remove(connection)
    
    async def broadcast_to_all(self, message: str):
        """Broadcast a message to all connections across all channels"""
        for channel in self.active_connections:
            await self.broadcast_to_channel(message, channel)

# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """General WebSocket endpoint"""
    await manager.connect(websocket, "general")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}),
                    websocket
                )
            elif message.get("type") == "broadcast":
                await manager.broadcast_to_channel(
                    json.dumps({
                        "type": "broadcast",
                        "message": message.get("message"),
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    "general"
                )
            else:
                # Echo back the message
                await manager.send_personal_message(
                    json.dumps({
                        "type": "echo",
                        "data": message,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, "general")


@router.websocket("/ws/{channel}")
async def websocket_channel_endpoint(websocket: WebSocket, channel: str):
    """Channel-specific WebSocket endpoint"""
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle channel-specific messages
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({
                        "type": "pong", 
                        "channel": channel,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
            elif message.get("type") == "broadcast":
                await manager.broadcast_to_channel(
                    json.dumps({
                        "type": "broadcast",
                        "channel": channel,
                        "message": message.get("message"),
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    channel
                )
            else:
                # Echo back the message with channel info
                await manager.send_personal_message(
                    json.dumps({
                        "type": "echo",
                        "channel": channel,
                        "data": message,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    status = {}
    for channel, connections in manager.active_connections.items():
        status[channel] = len(connections)
    
    return {
        "status": "active",
        "connections": status,
        "total_connections": sum(len(conns) for conns in manager.active_connections.values()),
        "timestamp": datetime.utcnow().isoformat()
    } 