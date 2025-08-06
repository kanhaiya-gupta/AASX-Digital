"""
Twin Instance Repository

Data access layer for twin instance management.
Handles CRUD operations for twin instances and their metadata.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.repositories.base_repository import BaseRepository
from src.twin_registry.models.twin_instance import TwinInstance

logger = logging.getLogger(__name__)


class TwinInstanceRepository(BaseRepository):
    """Repository for managing twin instances."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize the twin instance repository."""
        super().__init__(db_manager)
        self.table_name = "twin_instances"
        logger.info("Twin Instance Repository initialized")
    
    async def initialize(self) -> None:
        """Initialize the repository and create tables if needed."""
        try:
            await self._create_tables()
            logger.info("Twin Instance Repository tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Instance Repository: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Create the twin instances tables."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS twin_instances (
            id TEXT PRIMARY KEY,
            twin_id TEXT NOT NULL,
            instance_data TEXT NOT NULL,
            instance_metadata TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            is_active BOOLEAN DEFAULT 1,
            version INTEGER DEFAULT 1
        );
        
        CREATE INDEX IF NOT EXISTS idx_twin_instances_twin_id ON twin_instances(twin_id);
        CREATE INDEX IF NOT EXISTS idx_twin_instances_created_at ON twin_instances(created_at);
        CREATE INDEX IF NOT EXISTS idx_twin_instances_is_active ON twin_instances(is_active);
        """
        
        async with self.db_manager.get_connection() as conn:
            await conn.execute(create_table_sql)
            await conn.commit()
    
    async def create(self, instance: TwinInstance) -> TwinInstance:
        """Create a new twin instance."""
        try:
            sql = """
            INSERT INTO twin_instances 
            (id, twin_id, instance_data, instance_metadata, created_by, created_at, updated_at, is_active, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                instance.id,
                instance.twin_id,
                self._serialize_json(instance.instance_data),
                self._serialize_json(instance.instance_metadata),
                instance.created_by,
                instance.created_at,
                instance.updated_at,
                instance.is_active,
                instance.version
            )
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Created twin instance: {instance.id}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create twin instance: {e}")
            raise
    
    async def get_by_id(self, instance_id: str) -> Optional[TwinInstance]:
        """Get a twin instance by ID."""
        try:
            sql = "SELECT * FROM twin_instances WHERE id = ?"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (instance_id,)) as cursor:
                    row = await cursor.fetchone()
                    
            if row:
                return self._row_to_instance(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get twin instance {instance_id}: {e}")
            raise
    
    async def get_by_twin_id(self, twin_id: str, active_only: bool = True) -> List[TwinInstance]:
        """Get all instances for a specific twin."""
        try:
            sql = "SELECT * FROM twin_instances WHERE twin_id = ?"
            params = [twin_id]
            
            if active_only:
                sql += " AND is_active = 1"
            
            sql += " ORDER BY created_at DESC"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, params) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_instance(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get instances for twin {twin_id}: {e}")
            raise
    
    async def get_active_instance(self, twin_id: str) -> Optional[TwinInstance]:
        """Get the currently active instance for a twin."""
        try:
            sql = """
            SELECT * FROM twin_instances 
            WHERE twin_id = ? AND is_active = 1 
            ORDER BY created_at DESC 
            LIMIT 1
            """
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (twin_id,)) as cursor:
                    row = await cursor.fetchone()
                    
            if row:
                return self._row_to_instance(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active instance for twin {twin_id}: {e}")
            raise
    
    async def update(self, instance_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a twin instance."""
        try:
            # Build dynamic update SQL
            set_clauses = []
            params = []
            
            for key, value in update_data.items():
                if key in ['instance_data', 'instance_metadata']:
                    set_clauses.append(f"{key} = ?")
                    params.append(self._serialize_json(value))
                elif key in ['updated_at']:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
                else:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            sql = f"UPDATE twin_instances SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(instance_id)
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Updated twin instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update twin instance {instance_id}: {e}")
            raise
    
    async def deactivate_instance(self, instance_id: str) -> bool:
        """Deactivate a twin instance."""
        try:
            sql = "UPDATE twin_instances SET is_active = 0, updated_at = ? WHERE id = ?"
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, (datetime.utcnow().isoformat(), instance_id))
                await conn.commit()
            
            logger.info(f"Deactivated twin instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate twin instance {instance_id}: {e}")
            raise
    
    async def delete(self, instance_id: str) -> bool:
        """Delete a twin instance."""
        try:
            sql = "DELETE FROM twin_instances WHERE id = ?"
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, (instance_id,))
                await conn.commit()
            
            logger.info(f"Deleted twin instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete twin instance {instance_id}: {e}")
            raise
    
    async def get_instance_history(self, twin_id: str, limit: int = 50) -> List[TwinInstance]:
        """Get instance history for a twin."""
        try:
            sql = """
            SELECT * FROM twin_instances 
            WHERE twin_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (twin_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_instance(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get instance history for twin {twin_id}: {e}")
            raise
    
    def _row_to_instance(self, row) -> TwinInstance:
        """Convert database row to TwinInstance object."""
        return TwinInstance(
            id=row[0],
            twin_id=row[1],
            instance_data=self._deserialize_json(row[2]),
            instance_metadata=self._deserialize_json(row[3]),
            created_by=row[4],
            created_at=row[5],
            updated_at=row[6],
            is_active=bool(row[7]),
            version=row[8]
        ) 