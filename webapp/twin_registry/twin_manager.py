"""
Enhanced Twin Management Module
Phase 2.2.2: Complete Twin Registry Management
Handles twin lifecycle, operations, configuration, and advanced monitoring
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TwinStatus(Enum):
    """Twin operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TwinOperation(Enum):
    """Twin operations"""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    UPDATE = "update"
    DELETE = "delete"
    CONFIGURE = "configure"

@dataclass
class TwinConfiguration:
    """Twin configuration settings"""
    twin_id: str
    twin_name: str
    description: str
    twin_type: str
    version: str
    owner: str
    tags: List[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class TwinEvent:
    """Twin event log entry"""
    twin_id: str
    event_type: str
    event_message: str
    severity: str
    timestamp: datetime
    user: str
    metadata: Dict[str, Any]

@dataclass
class TwinHealth:
    """Comprehensive twin health data"""
    twin_id: str
    overall_health: float
    performance_health: float
    connectivity_health: float
    data_health: float
    operational_health: float
    last_check: datetime
    issues: List[str]
    recommendations: List[str]

class TwinManager:
    """Enhanced twin management system"""
    
    def __init__(self, db_path: str = "data/twin_registry.db"):
        self.db_path = db_path
        self.active_twins: Dict[str, Dict[str, Any]] = {}
        self.twin_operations: Dict[str, asyncio.Task] = {}
        
        # Initialize database
        self._init_database()
        
        # Load active twins
        self._load_active_twins()
    
    def _init_database(self):
        """Initialize enhanced twin management database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Twin configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twin_configurations (
                    twin_id TEXT PRIMARY KEY,
                    twin_name TEXT NOT NULL,
                    description TEXT,
                    twin_type TEXT NOT NULL,
                    version TEXT DEFAULT '1.0.0',
                    owner TEXT DEFAULT 'system',
                    tags TEXT,  -- JSON array of tags
                    settings TEXT,  -- JSON object of settings
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Twin events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twin_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    user TEXT DEFAULT 'system',
                    metadata TEXT,  -- JSON object of metadata
                    FOREIGN KEY (twin_id) REFERENCES twin_aasx_relationships (twin_id)
                )
            ''')
            
            # Twin health table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twin_health (
                    twin_id TEXT PRIMARY KEY,
                    overall_health REAL NOT NULL,
                    performance_health REAL NOT NULL,
                    connectivity_health REAL NOT NULL,
                    data_health REAL NOT NULL,
                    operational_health REAL NOT NULL,
                    last_check TEXT DEFAULT CURRENT_TIMESTAMP,
                    issues TEXT,  -- JSON array of issues
                    recommendations TEXT,  -- JSON array of recommendations
                    FOREIGN KEY (twin_id) REFERENCES twin_aasx_relationships (twin_id)
                )
            ''')
            
            # Twin relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twin_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_twin_id TEXT NOT NULL,
                    child_twin_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_twin_id) REFERENCES twin_aasx_relationships (twin_id),
                    FOREIGN KEY (child_twin_id) REFERENCES twin_aasx_relationships (twin_id)
                )
            ''')
            
            # Twin operations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twin_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT,
                    result TEXT,
                    error_message TEXT,
                    user TEXT DEFAULT 'system',
                    FOREIGN KEY (twin_id) REFERENCES twin_aasx_relationships (twin_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Enhanced twin management database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing twin management database: {e}")
    
    def _load_active_twins(self):
        """Load active twins from database and existing system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load from twin_aasx_relationships table
            cursor.execute('''
                SELECT twin_id, twin_name, status, last_sync, data_points
                FROM twin_aasx_relationships
                WHERE status = 'active'
            ''')
            
            twins = cursor.fetchall()
            conn.close()
            
            for twin in twins:
                twin_id, twin_name, status, last_sync, data_points = twin
                self.active_twins[twin_id] = {
                    "twin_id": twin_id,
                    "twin_name": twin_name,
                    "status": TwinStatus.ACTIVE.value,
                    "last_sync": last_sync,
                    "data_points": data_points,
                    "operational_status": "running",
                    "last_operation": None
                }
            
            logger.info(f"Loaded {len(self.active_twins)} active twins from database")
            
        except Exception as e:
            logger.error(f"Error loading active twins: {e}")
    
    async def create_twin(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new twin with configuration"""
        try:
            twin_id = twin_data.get("twin_id")
            twin_name = twin_data.get("twin_name")
            description = twin_data.get("description", "")
            twin_type = twin_data.get("twin_type", "generic")
            version = twin_data.get("version", "1.0.0")
            owner = twin_data.get("owner", "system")
            tags = twin_data.get("tags", [])
            settings = twin_data.get("settings", {})
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert twin configuration
            cursor.execute('''
                INSERT INTO twin_configurations 
                (twin_id, twin_name, description, twin_type, version, owner, tags, settings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                twin_id,
                twin_name,
                description,
                twin_type,
                version,
                owner,
                json.dumps(tags),
                json.dumps(settings)
            ))
            
            # Insert into twin relationships (if not exists)
            cursor.execute('''
                INSERT OR IGNORE INTO twin_aasx_relationships 
                (twin_id, twin_name, status, last_sync, data_points)
                VALUES (?, ?, 'active', CURRENT_TIMESTAMP, 0)
            ''', (twin_id, twin_name))
            
            # Log twin creation event
            cursor.execute('''
                INSERT INTO twin_events 
                (twin_id, event_type, event_message, severity, user)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                twin_id,
                "twin_created",
                f"Twin {twin_name} created successfully",
                "info",
                owner
            ))
            
            # Initialize twin health
            cursor.execute('''
                INSERT INTO twin_health 
                (twin_id, overall_health, performance_health, connectivity_health, data_health, operational_health)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                twin_id,
                100.0,  # Initial health scores
                100.0,
                100.0,
                100.0,
                100.0
            ))
            
            conn.commit()
            conn.close()
            
            # Add to active twins
            self.active_twins[twin_id] = {
                "twin_id": twin_id,
                "twin_name": twin_name,
                "status": TwinStatus.ACTIVE.value,
                "operational_status": "running",
                "last_operation": "created"
            }
            
            logger.info(f"Created twin: {twin_name} ({twin_id})")
            
            return {
                "success": True,
                "twin_id": twin_id,
                "message": f"Twin {twin_name} created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating twin: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_twin(self, twin_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update twin configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update configuration fields
            update_fields = []
            params = []
            
            for field, value in update_data.items():
                if field in ["twin_name", "description", "twin_type", "version", "owner", "tags", "settings"]:
                    update_fields.append(f"{field} = ?")
                    if field in ["tags", "settings"]:
                        params.append(json.dumps(value))
                    else:
                        params.append(value)
            
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                params.append(twin_id)
                
                cursor.execute(f'''
                    UPDATE twin_configurations 
                    SET {', '.join(update_fields)}
                    WHERE twin_id = ?
                ''', params)
                
                # Log update event
                cursor.execute('''
                    INSERT INTO twin_events 
                    (twin_id, event_type, event_message, severity, user)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    twin_id,
                    "twin_updated",
                    f"Twin configuration updated",
                    "info",
                    update_data.get("user", "system")
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Updated twin: {twin_id}")
                
                return {
                    "success": True,
                    "message": f"Twin {twin_id} updated successfully"
                }
            else:
                return {"success": False, "error": "No valid fields to update"}
                
        except Exception as e:
            logger.error(f"Error updating twin: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """Delete a twin and its configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if twin exists
            cursor.execute('SELECT twin_name FROM twin_aasx_relationships WHERE twin_id = ?', (twin_id,))
            result = cursor.fetchone()
            
            if not result:
                return {"success": False, "error": "Twin not found"}
            
            twin_name = result[0]
            
            # Delete from all tables
            cursor.execute('DELETE FROM twin_configurations WHERE twin_id = ?', (twin_id,))
            cursor.execute('DELETE FROM twin_health WHERE twin_id = ?', (twin_id,))
            cursor.execute('DELETE FROM twin_relationships WHERE parent_twin_id = ? OR child_twin_id = ?', (twin_id, twin_id))
            cursor.execute('DELETE FROM twin_aasx_relationships WHERE twin_id = ?', (twin_id,))
            
            # Log deletion event
            cursor.execute('''
                INSERT INTO twin_events 
                (twin_id, event_type, event_message, severity, user)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                twin_id,
                "twin_deleted",
                f"Twin {twin_name} deleted",
                "warning",
                user
            ))
            
            conn.commit()
            conn.close()
            
            # Remove from active twins
            if twin_id in self.active_twins:
                del self.active_twins[twin_id]
            
            logger.info(f"Deleted twin: {twin_name} ({twin_id})")
            
            return {
                "success": True,
                "message": f"Twin {twin_name} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting twin: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """Start a twin operation"""
        return await self._perform_twin_operation(twin_id, TwinOperation.START, user)
    
    async def stop_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """Stop a twin operation"""
        return await self._perform_twin_operation(twin_id, TwinOperation.STOP, user)
    
    async def restart_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """Restart a twin operation"""
        return await self._perform_twin_operation(twin_id, TwinOperation.RESTART, user)
    
    async def _perform_twin_operation(self, twin_id: str, operation: TwinOperation, user: str) -> Dict[str, Any]:
        """Perform a twin operation"""
        try:
            # Check if twin exists in active twins or database
            if twin_id not in self.active_twins:
                # Check database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT twin_name FROM twin_aasx_relationships WHERE twin_id = ?', (twin_id,))
                result = cursor.fetchone()
                conn.close()
                
                if not result:
                    return {"success": False, "error": "Twin not found or not active"}
                
                # Add to active twins
                self.active_twins[twin_id] = {
                    "twin_id": twin_id,
                    "twin_name": result[0],
                    "status": TwinStatus.ACTIVE.value,
                    "operational_status": "stopped",
                    "last_operation": None
                }
            
            # Log operation start
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO twin_operations 
                (twin_id, operation_type, status, user)
                VALUES (?, ?, 'running', ?)
            ''', (twin_id, operation.value, user))
            
            operation_id = cursor.lastrowid
            
            # Log event
            cursor.execute('''
                INSERT INTO twin_events 
                (twin_id, event_type, event_message, severity, user)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                twin_id,
                f"twin_{operation.value}",
                f"Twin {operation.value} operation initiated",
                "info",
                user
            ))
            
            conn.commit()
            conn.close()
            
            # Simulate operation (in real system, this would interact with actual twin)
            await asyncio.sleep(2)  # Simulate operation time
            
            # Update twin status
            if operation == TwinOperation.START:
                self.active_twins[twin_id]["operational_status"] = "running"
                self.active_twins[twin_id]["status"] = TwinStatus.ACTIVE.value
            elif operation == TwinOperation.STOP:
                self.active_twins[twin_id]["operational_status"] = "stopped"
                self.active_twins[twin_id]["status"] = TwinStatus.INACTIVE.value
            elif operation == TwinOperation.RESTART:
                self.active_twins[twin_id]["operational_status"] = "running"
                self.active_twins[twin_id]["status"] = TwinStatus.ACTIVE.value
            
            self.active_twins[twin_id]["last_operation"] = operation.value
            
            # Log operation completion
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE twin_operations 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP, result = 'success'
                WHERE id = ?
            ''', (operation_id,))
            
            cursor.execute('''
                INSERT INTO twin_events 
                (twin_id, event_type, event_message, severity, user)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                twin_id,
                f"twin_{operation.value}_completed",
                f"Twin {operation.value} operation completed successfully",
                "info",
                user
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Completed {operation.value} operation for twin: {twin_id}")
            
            return {
                "success": True,
                "operation": operation.value,
                "message": f"Twin {operation.value} operation completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error performing twin operation: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_twin_configuration(self, twin_id: str) -> Optional[TwinConfiguration]:
        """Get twin configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT twin_id, twin_name, description, twin_type, version, owner, tags, settings, created_at, updated_at
                FROM twin_configurations
                WHERE twin_id = ?
            ''', (twin_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                twin_id, twin_name, description, twin_type, version, owner, tags, settings, created_at, updated_at = row
                
                # Parse JSON fields
                tags_list = json.loads(tags) if tags else []
                settings_dict = json.loads(settings) if settings else {}
                
                # Parse timestamps
                created_dt = datetime.fromisoformat(created_at) if created_at else datetime.now()
                updated_dt = datetime.fromisoformat(updated_at) if updated_at else datetime.now()
                
                return TwinConfiguration(
                    twin_id=twin_id,
                    twin_name=twin_name,
                    description=description or "",
                    twin_type=twin_type,
                    version=version or "1.0.0",
                    owner=owner or "system",
                    tags=tags_list,
                    settings=settings_dict,
                    created_at=created_dt,
                    updated_at=updated_dt
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting twin configuration: {e}")
            return None
    
    async def get_twin_events(self, twin_id: str, limit: int = 50) -> List[TwinEvent]:
        """Get twin event history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT twin_id, event_type, event_message, severity, timestamp, user, metadata
                FROM twin_events
                WHERE twin_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (twin_id, limit))
            
            events = cursor.fetchall()
            conn.close()
            
            result = []
            for event in events:
                try:
                    result.append(TwinEvent(
                        twin_id=event[0],
                        event_type=event[1],
                        event_message=event[2],
                        severity=event[3],
                        timestamp=datetime.fromisoformat(event[4]) if event[4] else datetime.now(),
                        user=event[5] or "system",
                        metadata=json.loads(event[6]) if event[6] else {}
                    ))
                except Exception as e:
                    logger.error(f"Error parsing event {event}: {e}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting twin events: {e}")
            return []
    
    async def get_twin_health(self, twin_id: str) -> Optional[TwinHealth]:
        """Get twin health data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT overall_health, performance_health, connectivity_health, data_health, operational_health, 
                       last_check, issues, recommendations
                FROM twin_health
                WHERE twin_id = ?
            ''', (twin_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                overall_health, performance_health, connectivity_health, data_health, operational_health, last_check, issues, recommendations = row
                
                # Parse JSON fields
                issues_list = json.loads(issues) if issues else []
                recommendations_list = json.loads(recommendations) if recommendations else []
                
                # Parse timestamp
                last_check_dt = datetime.fromisoformat(last_check) if last_check else datetime.now()
                
                return TwinHealth(
                    twin_id=twin_id,
                    overall_health=overall_health or 85.0,
                    performance_health=performance_health or 90.0,
                    connectivity_health=connectivity_health or 95.0,
                    data_health=data_health or 88.0,
                    operational_health=operational_health or 92.0,
                    last_check=last_check_dt,
                    issues=issues_list,
                    recommendations=recommendations_list
                )
            else:
                # Generate default health data if none exists
                return TwinHealth(
                    twin_id=twin_id,
                    overall_health=85.0,
                    performance_health=90.0,
                    connectivity_health=95.0,
                    data_health=88.0,
                    operational_health=92.0,
                    last_check=datetime.now(),
                    issues=[],
                    recommendations=[]
                )
            
        except Exception as e:
            logger.error(f"Error getting twin health: {e}")
            # Return default health data on error
            return TwinHealth(
                twin_id=twin_id,
                overall_health=85.0,
                performance_health=90.0,
                connectivity_health=95.0,
                data_health=88.0,
                operational_health=92.0,
                last_check=datetime.now(),
                issues=[],
                recommendations=[]
            )
    
    async def get_all_twins_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all twins with enhanced information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all twins from twin_aasx_relationships
            cursor.execute('''
                SELECT 
                    tr.twin_id,
                    tr.twin_name,
                    tr.status,
                    tr.last_sync,
                    tr.data_points,
                    tc.twin_type,
                    tc.version,
                    tc.owner,
                    tc.tags,
                    th.overall_health,
                    th.operational_health
                FROM twin_aasx_relationships tr
                LEFT JOIN twin_configurations tc ON tr.twin_id = tc.twin_id
                LEFT JOIN twin_health th ON tr.twin_id = th.twin_id
                ORDER BY tr.twin_name
            ''')
            
            twins = cursor.fetchall()
            conn.close()
            
            result = []
            for twin in twins:
                twin_id, twin_name, status, last_sync, data_points, twin_type, version, owner, tags, overall_health, operational_health = twin
                
                # Get operational status from active twins
                operational_status = "unknown"
                if twin_id in self.active_twins:
                    operational_status = self.active_twins[twin_id].get("operational_status", "unknown")
                
                result.append({
                    "twin_id": twin_id,
                    "twin_name": twin_name,
                    "status": status,
                    "last_sync": last_sync,
                    "data_points": data_points,
                    "twin_type": twin_type or "generic",
                    "version": version or "1.0.0",
                    "owner": owner or "system",
                    "tags": json.loads(tags) if tags else [],
                    "overall_health": overall_health or 0.0,
                    "operational_health": operational_health or 0.0,
                    "operational_status": operational_status
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting twins summary: {e}")
            return []

# Global twin manager instance
twin_manager = TwinManager() 