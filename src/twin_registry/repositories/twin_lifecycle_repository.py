"""
Twin Lifecycle Repository

Data access layer for twin lifecycle management.
Handles lifecycle events, status tracking, and history.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.repositories.base_repository import BaseRepository
from src.twin_registry.models.twin_lifecycle import (
    TwinLifecycleEvent, 
    TwinLifecycleStatus, 
    LifecycleEventType,
    LifecycleStatus,
    TwinLifecycleQuery,
    TwinLifecycleSummary
)

logger = logging.getLogger(__name__)


class TwinLifecycleRepository(BaseRepository):
    """Repository for managing twin lifecycle events and status."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize the twin lifecycle repository."""
        super().__init__(db_manager)
        self.table_name = "twin_lifecycle"
        logger.info("Twin Lifecycle Repository initialized")
    
    async def initialize(self) -> None:
        """Initialize the repository and create tables if needed."""
        try:
            await self._create_tables()
            logger.info("Twin Lifecycle Repository tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Lifecycle Repository: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Create the twin lifecycle tables."""
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS twin_lifecycle_events (
            event_id TEXT PRIMARY KEY,
            twin_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT,
            event_metadata TEXT,
            timestamp TEXT NOT NULL,
            triggered_by TEXT,
            status TEXT DEFAULT 'completed',
            error_message TEXT
        );
        
        CREATE TABLE IF NOT EXISTS twin_lifecycle_status (
            twin_id TEXT PRIMARY KEY,
            current_status TEXT NOT NULL,
            last_event_id TEXT,
            last_updated TEXT NOT NULL,
            lifecycle_metadata TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_lifecycle_events_twin_id ON twin_lifecycle_events(twin_id);
        CREATE INDEX IF NOT EXISTS idx_lifecycle_events_timestamp ON twin_lifecycle_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_lifecycle_events_type ON twin_lifecycle_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_lifecycle_events_status ON twin_lifecycle_events(status);
        """
        
        async with self.db_manager.get_connection() as conn:
            await conn.execute(create_tables_sql)
            await conn.commit()
    
    async def create_event(self, event: TwinLifecycleEvent) -> TwinLifecycleEvent:
        """Create a new lifecycle event."""
        try:
            sql = """
            INSERT INTO twin_lifecycle_events 
            (event_id, twin_id, event_type, event_data, event_metadata, timestamp, triggered_by, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                event.event_id,
                event.twin_id,
                event.event_type.value,
                self._serialize_json(event.event_data),
                self._serialize_json(event.event_metadata),
                event.timestamp.isoformat(),
                event.triggered_by,
                event.status,
                event.error_message
            )
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Created lifecycle event: {event.event_id}")
            return event
            
        except Exception as e:
            logger.error(f"Failed to create lifecycle event: {e}")
            raise
    
    async def get_event_by_id(self, event_id: str) -> Optional[TwinLifecycleEvent]:
        """Get a lifecycle event by ID."""
        try:
            sql = "SELECT * FROM twin_lifecycle_events WHERE event_id = ?"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (event_id,)) as cursor:
                    row = await cursor.fetchone()
                    
            if row:
                return self._row_to_event(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle event {event_id}: {e}")
            raise
    
    async def get_events_by_twin_id(self, twin_id: str, limit: int = 50) -> List[TwinLifecycleEvent]:
        """Get lifecycle events for a specific twin."""
        try:
            sql = """
            SELECT * FROM twin_lifecycle_events 
            WHERE twin_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (twin_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_event(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle events for twin {twin_id}: {e}")
            raise
    
    async def query_events(self, query: TwinLifecycleQuery) -> List[TwinLifecycleEvent]:
        """Query lifecycle events with filters."""
        try:
            sql = "SELECT * FROM twin_lifecycle_events WHERE 1=1"
            params = []
            
            if query.twin_id:
                sql += " AND twin_id = ?"
                params.append(query.twin_id)
            
            if query.event_type:
                sql += " AND event_type = ?"
                params.append(query.event_type.value)
            
            if query.status:
                sql += " AND status = ?"
                params.append(query.status)
            
            if query.triggered_by:
                sql += " AND triggered_by = ?"
                params.append(query.triggered_by)
            
            if query.timestamp_after:
                sql += " AND timestamp >= ?"
                params.append(query.timestamp_after.isoformat())
            
            if query.timestamp_before:
                sql += " AND timestamp <= ?"
                params.append(query.timestamp_before.isoformat())
            
            sql += " ORDER BY timestamp DESC"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, params) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_event(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to query lifecycle events: {e}")
            raise
    
    async def update_event(self, event_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a lifecycle event."""
        try:
            # Build dynamic update SQL
            set_clauses = []
            params = []
            
            for key, value in update_data.items():
                if key in ['event_data', 'event_metadata']:
                    set_clauses.append(f"{key} = ?")
                    params.append(self._serialize_json(value))
                elif key == 'timestamp':
                    set_clauses.append(f"{key} = ?")
                    params.append(value.isoformat())
                else:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            sql = f"UPDATE twin_lifecycle_events SET {', '.join(set_clauses)} WHERE event_id = ?"
            params.append(event_id)
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Updated lifecycle event: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update lifecycle event {event_id}: {e}")
            raise
    
    async def get_lifecycle_status(self, twin_id: str) -> Optional[TwinLifecycleStatus]:
        """Get current lifecycle status for a twin."""
        try:
            sql = "SELECT * FROM twin_lifecycle_status WHERE twin_id = ?"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (twin_id,)) as cursor:
                    row = await cursor.fetchone()
                    
            if row:
                return self._row_to_status(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle status for twin {twin_id}: {e}")
            raise
    
    async def update_lifecycle_status(self, twin_id: str, status: TwinLifecycleStatus) -> bool:
        """Update lifecycle status for a twin."""
        try:
            sql = """
            INSERT OR REPLACE INTO twin_lifecycle_status 
            (twin_id, current_status, last_event_id, last_updated, lifecycle_metadata)
            VALUES (?, ?, ?, ?, ?)
            """
            
            params = (
                twin_id,
                status.current_status.value,
                status.last_event.event_id if status.last_event else None,
                status.last_updated.isoformat(),
                self._serialize_json(status.lifecycle_metadata)
            )
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Updated lifecycle status for twin: {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update lifecycle status for twin {twin_id}: {e}")
            raise
    
    async def get_lifecycle_summary(self, twin_id: str = None) -> TwinLifecycleSummary:
        """Get lifecycle summary statistics."""
        try:
            # Get total events
            total_sql = "SELECT COUNT(*) FROM twin_lifecycle_events"
            if twin_id:
                total_sql += " WHERE twin_id = ?"
            
            async with self.db_manager.get_connection() as conn:
                if twin_id:
                    async with conn.execute(total_sql, (twin_id,)) as cursor:
                        total_events = (await cursor.fetchone())[0]
                else:
                    async with conn.execute(total_sql) as cursor:
                        total_events = (await cursor.fetchone())[0]
            
            # Get events by type
            type_sql = """
            SELECT event_type, COUNT(*) as count 
            FROM twin_lifecycle_events
            """
            if twin_id:
                type_sql += " WHERE twin_id = ?"
            type_sql += " GROUP BY event_type"
            
            async with self.db_manager.get_connection() as conn:
                if twin_id:
                    async with conn.execute(type_sql, (twin_id,)) as cursor:
                        events_by_type = {row[0]: row[1] for row in await cursor.fetchall()}
                else:
                    async with conn.execute(type_sql) as cursor:
                        events_by_type = {row[0]: row[1] for row in await cursor.fetchall()}
            
            # Get events by status
            status_sql = """
            SELECT status, COUNT(*) as count 
            FROM twin_lifecycle_events
            """
            if twin_id:
                status_sql += " WHERE twin_id = ?"
            status_sql += " GROUP BY status"
            
            async with self.db_manager.get_connection() as conn:
                if twin_id:
                    async with conn.execute(status_sql, (twin_id,)) as cursor:
                        events_by_status = {row[0]: row[1] for row in await cursor.fetchall()}
                else:
                    async with conn.execute(status_sql) as cursor:
                        events_by_status = {row[0]: row[1] for row in await cursor.fetchall()}
            
            # Get recent events
            recent_sql = """
            SELECT * FROM twin_lifecycle_events
            """
            if twin_id:
                recent_sql += " WHERE twin_id = ?"
            recent_sql += " ORDER BY timestamp DESC LIMIT 10"
            
            async with self.db_manager.get_connection() as conn:
                if twin_id:
                    async with conn.execute(recent_sql, (twin_id,)) as cursor:
                        recent_events = [self._row_to_event(row) for row in await cursor.fetchall()]
                else:
                    async with conn.execute(recent_sql) as cursor:
                        recent_events = [self._row_to_event(row) for row in await cursor.fetchall()]
            
            # Get status distribution
            status_dist_sql = """
            SELECT current_status, COUNT(*) as count 
            FROM twin_lifecycle_status
            GROUP BY current_status
            """
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(status_dist_sql) as cursor:
                    status_distribution = {row[0]: row[1] for row in await cursor.fetchall()}
            
            return TwinLifecycleSummary(
                total_events=total_events,
                events_by_type=events_by_type,
                events_by_status=events_by_status,
                recent_events=recent_events,
                status_distribution=status_distribution
            )
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle summary: {e}")
            raise
    
    def _row_to_event(self, row) -> TwinLifecycleEvent:
        """Convert database row to TwinLifecycleEvent object."""
        return TwinLifecycleEvent(
            event_id=row[0],
            twin_id=row[1],
            event_type=LifecycleEventType(row[2]),
            event_data=self._deserialize_json(row[3]),
            event_metadata=self._deserialize_json(row[4]),
            timestamp=datetime.fromisoformat(row[5]),
            triggered_by=row[6],
            status=row[7],
            error_message=row[8]
        )
    
    def _row_to_status(self, row) -> TwinLifecycleStatus:
        """Convert database row to TwinLifecycleStatus object."""
        return TwinLifecycleStatus(
            twin_id=row[0],
            current_status=LifecycleStatus(row[1]),
            last_event=None,  # Would need to fetch separately if needed
            last_updated=datetime.fromisoformat(row[3]),
            lifecycle_metadata=self._deserialize_json(row[4])
        ) 