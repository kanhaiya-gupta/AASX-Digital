#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Twin Synchronization Module
Phase 2.1: Real-Time Sync Foundation
Handles WebSocket connections and real-time twin updates.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Twin synchronization status"""
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"
    ERROR = "error"
    PENDING = "pending"

class TwinSyncManager:
    """Manages real-time twin synchronization via WebSockets"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.db_path = self.project_root / "data" / "twin_registry.db"
        
        # WebSocket connections
        self.active_connections: Set[WebSocket] = set()
        self.twin_subscriptions: Dict[str, Set[WebSocket]] = {}
        
        # Sync state
        self.twin_sync_status: Dict[str, Dict[str, Any]] = {}
        self.sync_intervals: Dict[str, int] = {}  # seconds
        
        # Initialize sync manager
        self._init_sync_manager()
    
    def _init_sync_manager(self):
        """Initialize the sync manager with database setup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create real-time sync tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS realtime_sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT NOT NULL,
                    sync_type TEXT NOT NULL,
                    sync_status TEXT NOT NULL,
                    data_size INTEGER,
                    sync_duration REAL,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twin_health_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT NOT NULL,
                    uptime_percentage REAL,
                    response_time_ms REAL,
                    error_rate REAL,
                    data_quality_score REAL,
                    last_health_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT UNIQUE NOT NULL,
                    sync_interval_seconds INTEGER DEFAULT 300,
                    last_sync TIMESTAMP,
                    next_sync TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Real-time sync manager initialized successfully")
            
            # Initialize twin statuses from database
            self._init_twin_statuses()
            
        except Exception as e:
            logger.error(f"Error initializing sync manager: {e}")
    
    def _init_twin_statuses(self):
        """Initialize twin statuses from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all active twins
            cursor.execute('''
                SELECT twin_id FROM twin_aasx_relationships 
                WHERE status = 'active'
            ''')
            
            twins = cursor.fetchall()
            conn.close()
            
            # Initialize status for each twin
            for (twin_id,) in twins:
                if twin_id not in self.twin_sync_status:
                    self.twin_sync_status[twin_id] = {
                        "status": SyncStatus.ONLINE.value,  # Default to online
                        "last_update": datetime.now().isoformat(),
                        "data": {}
                    }
            
            logger.info(f"Initialized status for {len(twins)} twins")
            
        except Exception as e:
            logger.error(f"Error initializing twin statuses: {e}")
    
    async def connect(self, websocket: WebSocket):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
        
        # Send initial sync status
        await self.send_initial_status(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        self.active_connections.discard(websocket)
        
        # Remove from twin subscriptions - create a copy to avoid iteration error
        twin_subscriptions_copy = dict(self.twin_subscriptions)
        for twin_id, connections in twin_subscriptions_copy.items():
            connections.discard(websocket)
            if not connections:
                del self.twin_subscriptions[twin_id]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_initial_status(self, websocket: WebSocket):
        """Send initial sync status to new connection"""
        try:
            # Get all twin sync statuses
            all_statuses = await self.get_all_twin_sync_status()
            
            await websocket.send_text(json.dumps({
                "type": "initial_status",
                "data": {
                    "twins": all_statuses,
                    "timestamp": datetime.now().isoformat()
                }
            }))
            
        except Exception as e:
            logger.error(f"Error sending initial status: {e}")
    
    async def subscribe_to_twin(self, websocket: WebSocket, twin_id: str):
        """Subscribe to updates for a specific twin"""
        if twin_id not in self.twin_subscriptions:
            self.twin_subscriptions[twin_id] = set()
        
        self.twin_subscriptions[twin_id].add(websocket)
        logger.info(f"Subscribed to twin {twin_id}. Total subscribers: {len(self.twin_subscriptions[twin_id])}")
    
    async def unsubscribe_from_twin(self, websocket: WebSocket, twin_id: str):
        """Unsubscribe from updates for a specific twin"""
        if twin_id in self.twin_subscriptions:
            self.twin_subscriptions[twin_id].discard(websocket)
            if not self.twin_subscriptions[twin_id]:
                del self.twin_subscriptions[twin_id]
    
    async def broadcast_twin_update(self, twin_id: str, update_data: Dict[str, Any]):
        """Broadcast twin update to all subscribed clients"""
        message = {
            "type": "twin_update",
            "twin_id": twin_id,
            "data": update_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all subscribers of this twin
        if twin_id in self.twin_subscriptions:
            disconnected = set()
            for websocket in self.twin_subscriptions[twin_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to subscriber: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected subscribers
            for websocket in disconnected:
                self.twin_subscriptions[twin_id].discard(websocket)
        
        # Also send to general dashboard subscribers
        await self.broadcast_to_all(message)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = set()
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def update_twin_sync_status(self, twin_id: str, status: SyncStatus, 
                                    additional_data: Optional[Dict[str, Any]] = None):
        """Update twin sync status and broadcast to subscribers"""
        current_time = datetime.now()
        
        # Update local status
        self.twin_sync_status[twin_id] = {
            "status": status.value,
            "last_update": current_time.isoformat(),
            "data": additional_data or {}
        }
        
        # Log to database
        await self._log_sync_status(twin_id, status.value, additional_data)
        
        # Broadcast update
        update_data = {
            "status": status.value,
            "last_update": current_time.isoformat(),
            "data": additional_data or {}
        }
        
        await self.broadcast_twin_update(twin_id, update_data)
        
        logger.info(f"Updated twin {twin_id} status to {status.value}")
    
    async def _log_sync_status(self, twin_id: str, status: str, data: Optional[Dict[str, Any]] = None):
        """Log sync status to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO realtime_sync_log 
                (twin_id, sync_type, sync_status, data_size, sync_duration, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                twin_id,
                data.get("sync_type", "status_update") if data else "status_update",
                status,
                data.get("data_size", 0) if data else 0,
                data.get("sync_duration", 0) if data else 0,
                data.get("error_message", None) if data else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging sync status: {e}")
    
    async def get_all_twin_sync_status(self) -> List[Dict[str, Any]]:
        """Get sync status for all twins"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all registered twins
            cursor.execute('''
                SELECT twin_id, twin_name, status, last_sync, data_points
                FROM twin_aasx_relationships
                WHERE status = 'active'
            ''')
            
            twins = cursor.fetchall()
            conn.close()
            
            # Build status list
            status_list = []
            for twin in twins:
                twin_id, twin_name, status, last_sync, data_points = twin
                
                # Get current sync status from memory or default
                current_status = self.twin_sync_status.get(twin_id, {
                    "status": SyncStatus.PENDING.value,
                    "last_update": datetime.now().isoformat(),
                    "data": {}
                })
                
                # Calculate actual data points if not available
                if not data_points or data_points == 0:
                    # Import here to avoid circular imports
                    from .aasx_integration import AASXIntegration
                    aasx_integration = AASXIntegration()
                    # Get the AASX filename for this twin
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT aasx_filename FROM twin_aasx_relationships WHERE twin_id = ?', (twin_id,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        aasx_filename = result[0]
                        data_points = aasx_integration._calculate_data_points(aasx_filename)
                
                # Get subscriber count
                subscriber_count = len(self.twin_subscriptions.get(twin_id, set()))
                
                status_list.append({
                    "twin_id": twin_id,
                    "twin_name": twin_name or f"Twin {twin_id}",
                    "sync_status": current_status["status"],
                    "last_sync": last_sync,
                    "data_points": data_points or 0,
                    "last_update": current_status["last_update"],
                    "subscribers": subscriber_count
                })
            
            return status_list
            
        except Exception as e:
            logger.error(f"Error getting twin sync status: {e}")
            return []
    
    async def start_twin_sync(self, twin_id: str, sync_type: str = "manual"):
        """Start synchronization for a specific twin"""
        try:
            # Update status to syncing
            await self.update_twin_sync_status(twin_id, SyncStatus.SYNCING, {
                "sync_type": sync_type,
                "start_time": datetime.now().isoformat()
            })
            
            # Simulate sync process (replace with actual sync logic)
            await asyncio.sleep(2)  # Simulate sync time
            
            # Update status to online
            await self.update_twin_sync_status(twin_id, SyncStatus.ONLINE, {
                "sync_type": sync_type,
                "sync_duration": 2.0,
                "data_size": 1024,  # Mock data size
                "end_time": datetime.now().isoformat()
            })
            
            logger.info(f"Completed sync for twin {twin_id}")
            
        except Exception as e:
            logger.error(f"Error syncing twin {twin_id}: {e}")
            await self.update_twin_sync_status(twin_id, SyncStatus.ERROR, {
                "sync_type": sync_type,
                "error_message": str(e)
            })
    
    async def handle_websocket_message(self, websocket: WebSocket, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                twin_id = data.get("twin_id")
                if twin_id:
                    await self.subscribe_to_twin(websocket, twin_id)
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "twin_id": twin_id,
                        "timestamp": datetime.now().isoformat()
                    }))
            
            elif message_type == "unsubscribe":
                twin_id = data.get("twin_id")
                if twin_id:
                    await self.unsubscribe_from_twin(websocket, twin_id)
                    await websocket.send_text(json.dumps({
                        "type": "unsubscribed",
                        "twin_id": twin_id,
                        "timestamp": datetime.now().isoformat()
                    }))
            
            elif message_type == "sync_request":
                twin_id = data.get("twin_id")
                if twin_id:
                    # Start sync in background
                    asyncio.create_task(self.start_twin_sync(twin_id, "manual"))
                    await websocket.send_text(json.dumps({
                        "type": "sync_started",
                        "twin_id": twin_id,
                        "timestamp": datetime.now().isoformat()
                    }))
            
            elif message_type == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

# Global sync manager instance
sync_manager = TwinSyncManager() 