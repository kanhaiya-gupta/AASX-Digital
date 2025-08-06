"""
Twin Sync Repository

Data access layer for twin synchronization management.
Handles sync history, configurations, and status tracking.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.repositories.base_repository import BaseRepository
from src.twin_registry.models.twin_sync import TwinSyncHistory, TwinSyncStatus, TwinSyncConfiguration

logger = logging.getLogger(__name__)


class TwinSyncRepository(BaseRepository):
    """Repository for managing twin synchronization."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize the twin sync repository."""
        super().__init__(db_manager)
        self.table_name = "twin_sync"
        logger.info("Twin Sync Repository initialized")
    
    async def initialize(self) -> None:
        """Initialize the repository and create tables if needed."""
        try:
            await self._create_tables()
            logger.info("Twin Sync Repository tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Sync Repository: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Create the twin sync tables."""
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS twin_sync_history (
            id TEXT PRIMARY KEY,
            twin_id TEXT NOT NULL,
            sync_type TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            error_message TEXT,
            sync_data TEXT,
            metadata TEXT
        );
        
        CREATE TABLE IF NOT EXISTS twin_sync_status (
            twin_id TEXT PRIMARY KEY,
            last_sync_timestamp TEXT,
            last_sync_status TEXT DEFAULT 'unknown',
            last_sync_type TEXT,
            next_sync_timestamp TEXT,
            sync_configuration TEXT,
            metadata TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_sync_history_twin_id ON twin_sync_history(twin_id);
        CREATE INDEX IF NOT EXISTS idx_sync_history_status ON twin_sync_history(status);
        CREATE INDEX IF NOT EXISTS idx_sync_history_started_at ON twin_sync_history(started_at);
        """
        
        async with self.db_manager.get_connection() as conn:
            await conn.execute(create_tables_sql)
            await conn.commit()
    
    async def create_sync_history(self, sync_history: TwinSyncHistory) -> TwinSyncHistory:
        """Create a new sync history record."""
        try:
            sql = """
            INSERT INTO twin_sync_history 
            (id, twin_id, sync_type, status, started_at, completed_at, error_message, sync_data, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                sync_history.id,
                sync_history.twin_id,
                sync_history.sync_type,
                sync_history.status,
                sync_history.started_at,
                sync_history.completed_at,
                sync_history.error_message,
                self._serialize_json(sync_history.sync_data),
                self._serialize_json(sync_history.metadata)
            )
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Created sync history: {sync_history.id}")
            return sync_history
            
        except Exception as e:
            logger.error(f"Failed to create sync history: {e}")
            raise
    
    async def update_sync_history(self, sync_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a sync history record."""
        try:
            # Build dynamic update SQL
            set_clauses = []
            params = []
            
            for key, value in update_data.items():
                if key in ['sync_data', 'metadata']:
                    set_clauses.append(f"{key} = ?")
                    params.append(self._serialize_json(value))
                else:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            sql = f"UPDATE twin_sync_history SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(sync_id)
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Updated sync history: {sync_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update sync history {sync_id}: {e}")
            raise
    
    async def get_sync_history(self, twin_id: str, limit: int = 50) -> List[TwinSyncHistory]:
        """Get sync history for a twin."""
        try:
            sql = """
            SELECT * FROM twin_sync_history 
            WHERE twin_id = ? 
            ORDER BY started_at DESC 
            LIMIT ?
            """
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (twin_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_sync_history(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get sync history for twin {twin_id}: {e}")
            raise
    
    async def get_sync_status(self, twin_id: str) -> Optional[TwinSyncStatus]:
        """Get sync status for a twin."""
        try:
            sql = "SELECT * FROM twin_sync_status WHERE twin_id = ?"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (twin_id,)) as cursor:
                    row = await cursor.fetchone()
                    
            if row:
                return self._row_to_sync_status(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get sync status for twin {twin_id}: {e}")
            raise
    
    async def update_sync_status(self, twin_id: str, sync_status: TwinSyncStatus) -> bool:
        """Update sync status for a twin."""
        try:
            sql = """
            INSERT OR REPLACE INTO twin_sync_status 
            (twin_id, last_sync_timestamp, last_sync_status, last_sync_type, 
             next_sync_timestamp, sync_configuration, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                twin_id,
                sync_status.last_sync_timestamp,
                sync_status.last_sync_status,
                sync_status.last_sync_type,
                sync_status.next_sync_timestamp,
                self._serialize_json(sync_status.sync_configuration),
                self._serialize_json(sync_status.metadata)
            )
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Updated sync status for twin: {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update sync status for twin {twin_id}: {e}")
            raise
    
    async def get_failed_syncs(self, limit: int = 100) -> List[TwinSyncHistory]:
        """Get recent failed sync operations."""
        try:
            sql = """
            SELECT * FROM twin_sync_history 
            WHERE status = 'failed' 
            ORDER BY started_at DESC 
            LIMIT ?
            """
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_sync_history(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get failed syncs: {e}")
            raise
    
    async def get_pending_syncs(self) -> List[TwinSyncHistory]:
        """Get pending sync operations."""
        try:
            sql = """
            SELECT * FROM twin_sync_history 
            WHERE status = 'pending' 
            ORDER BY started_at ASC
            """
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_sync_history(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get pending syncs: {e}")
            raise
    
    async def cleanup_old_sync_history(self, days: int = 30) -> int:
        """Clean up old sync history records."""
        try:
            cutoff_date = (datetime.utcnow() - datetime.timedelta(days=days)).isoformat()
            
            sql = "DELETE FROM twin_sync_history WHERE started_at < ?"
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, (cutoff_date,))
                await conn.commit()
            
            logger.info(f"Cleaned up sync history older than {days} days")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup sync history: {e}")
            raise
    
    def _row_to_sync_history(self, row) -> TwinSyncHistory:
        """Convert database row to TwinSyncHistory object."""
        return TwinSyncHistory(
            id=row[0],
            twin_id=row[1],
            sync_type=row[2],
            status=row[3],
            started_at=row[4],
            completed_at=row[5],
            error_message=row[6],
            sync_data=self._deserialize_json(row[7]),
            metadata=self._deserialize_json(row[8])
        )
    
    def _row_to_sync_status(self, row) -> TwinSyncStatus:
        """Convert database row to TwinSyncStatus object."""
        return TwinSyncStatus(
            twin_id=row[0],
            last_sync_timestamp=row[1],
            last_sync_status=row[2],
            last_sync_type=row[3],
            next_sync_timestamp=row[4],
            sync_configuration=self._deserialize_json(row[5]),
            metadata=self._deserialize_json(row[6])
        ) 