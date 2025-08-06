"""
Twin Registry Repository

Data access layer for twin registry metadata and configuration.
Handles registry metadata, configuration, and summary statistics.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.repositories.base_repository import BaseRepository
from src.twin_registry.models.twin_registry import (
    TwinRegistryMetadata,
    TwinRegistryQuery,
    TwinRegistrySummary,
    TwinRegistryConfig
)

logger = logging.getLogger(__name__)


class TwinRegistryRepository(BaseRepository):
    """Repository for managing twin registry metadata and configuration."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize the twin registry repository."""
        super().__init__(db_manager)
        self.table_name = "twin_registry"
        logger.info("Twin Registry Repository initialized")
    
    async def initialize(self) -> None:
        """Initialize the repository and create tables if needed."""
        try:
            await self._create_tables()
            logger.info("Twin Registry Repository tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Registry Repository: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Create the twin registry tables."""
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS twin_registry_metadata (
            registry_id TEXT PRIMARY KEY,
            twin_id TEXT NOT NULL,
            registry_name TEXT NOT NULL,
            registry_type TEXT NOT NULL,
            registry_config TEXT,
            registry_metadata TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            is_active BOOLEAN DEFAULT 1,
            version TEXT DEFAULT '1.0.0'
        );
        
        CREATE TABLE IF NOT EXISTS twin_registry_config (
            config_id TEXT PRIMARY KEY,
            auto_sync_enabled BOOLEAN DEFAULT 0,
            sync_interval_minutes INTEGER DEFAULT 30,
            health_check_enabled BOOLEAN DEFAULT 1,
            health_check_interval_minutes INTEGER DEFAULT 5,
            max_instances_per_twin INTEGER DEFAULT 10,
            retention_days INTEGER DEFAULT 90,
            backup_enabled BOOLEAN DEFAULT 1,
            backup_interval_hours INTEGER DEFAULT 24,
            created_at TEXT NOT NULL,
            updated_at TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_registry_metadata_twin_id ON twin_registry_metadata(twin_id);
        CREATE INDEX IF NOT EXISTS idx_registry_metadata_type ON twin_registry_metadata(registry_type);
        CREATE INDEX IF NOT EXISTS idx_registry_metadata_active ON twin_registry_metadata(is_active);
        CREATE INDEX IF NOT EXISTS idx_registry_metadata_created_at ON twin_registry_metadata(created_at);
        """
        
        async with self.db_manager.get_connection() as conn:
            await conn.execute(create_tables_sql)
            await conn.commit()
    
    async def create_metadata(self, metadata: TwinRegistryMetadata) -> TwinRegistryMetadata:
        """Create new registry metadata."""
        try:
            sql = """
            INSERT INTO twin_registry_metadata 
            (registry_id, twin_id, registry_name, registry_type, registry_config, registry_metadata, 
             created_at, updated_at, is_active, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                metadata.registry_id,
                metadata.twin_id,
                metadata.registry_name,
                metadata.registry_type,
                self._serialize_json(metadata.registry_config),
                self._serialize_json(metadata.registry_metadata),
                metadata.created_at.isoformat(),
                metadata.updated_at.isoformat() if metadata.updated_at else None,
                metadata.is_active,
                metadata.version
            )
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Created registry metadata: {metadata.registry_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to create registry metadata: {e}")
            raise
    
    async def get_metadata_by_id(self, registry_id: str) -> Optional[TwinRegistryMetadata]:
        """Get registry metadata by ID."""
        try:
            sql = "SELECT * FROM twin_registry_metadata WHERE registry_id = ?"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (registry_id,)) as cursor:
                    row = await cursor.fetchone()
                    
            if row:
                return self._row_to_metadata(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get registry metadata {registry_id}: {e}")
            raise
    
    async def get_metadata_by_twin_id(self, twin_id: str) -> List[TwinRegistryMetadata]:
        """Get all registry metadata for a specific twin."""
        try:
            sql = """
            SELECT * FROM twin_registry_metadata 
            WHERE twin_id = ? 
            ORDER BY created_at DESC
            """
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, (twin_id,)) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_metadata(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get registry metadata for twin {twin_id}: {e}")
            raise
    
    async def query_metadata(self, query: TwinRegistryQuery) -> List[TwinRegistryMetadata]:
        """Query registry metadata with filters."""
        try:
            sql = "SELECT * FROM twin_registry_metadata WHERE 1=1"
            params = []
            
            if query.twin_id:
                sql += " AND twin_id = ?"
                params.append(query.twin_id)
            
            if query.registry_type:
                sql += " AND registry_type = ?"
                params.append(query.registry_type)
            
            if query.registry_name:
                sql += " AND registry_name LIKE ?"
                params.append(f"%{query.registry_name}%")
            
            if query.is_active is not None:
                sql += " AND is_active = ?"
                params.append(query.is_active)
            
            if query.created_after:
                sql += " AND created_at >= ?"
                params.append(query.created_after.isoformat())
            
            if query.created_before:
                sql += " AND created_at <= ?"
                params.append(query.created_before.isoformat())
            
            sql += " ORDER BY created_at DESC"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql, params) as cursor:
                    rows = await cursor.fetchall()
                    
            return [self._row_to_metadata(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to query registry metadata: {e}")
            raise
    
    async def update_metadata(self, registry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update registry metadata."""
        try:
            # Build dynamic update SQL
            set_clauses = []
            params = []
            
            for key, value in update_data.items():
                if key in ['registry_config', 'registry_metadata']:
                    set_clauses.append(f"{key} = ?")
                    params.append(self._serialize_json(value))
                elif key in ['created_at', 'updated_at']:
                    set_clauses.append(f"{key} = ?")
                    params.append(value.isoformat())
                else:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            sql = f"UPDATE twin_registry_metadata SET {', '.join(set_clauses)} WHERE registry_id = ?"
            params.append(registry_id)
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Updated registry metadata: {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update registry metadata {registry_id}: {e}")
            raise
    
    async def delete_metadata(self, registry_id: str) -> bool:
        """Delete registry metadata."""
        try:
            sql = "DELETE FROM twin_registry_metadata WHERE registry_id = ?"
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, (registry_id,))
                await conn.commit()
            
            logger.info(f"Deleted registry metadata: {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete registry metadata {registry_id}: {e}")
            raise
    
    async def get_registry_summary(self) -> TwinRegistrySummary:
        """Get registry summary statistics."""
        try:
            # Get total registries
            total_sql = "SELECT COUNT(*) FROM twin_registry_metadata"
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(total_sql) as cursor:
                    total_registries = (await cursor.fetchone())[0]
            
            # Get active registries
            active_sql = "SELECT COUNT(*) FROM twin_registry_metadata WHERE is_active = 1"
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(active_sql) as cursor:
                    active_registries = (await cursor.fetchone())[0]
            
            # Get registries by type
            type_sql = """
            SELECT registry_type, COUNT(*) as count 
            FROM twin_registry_metadata 
            GROUP BY registry_type
            """
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(type_sql) as cursor:
                    registries_by_type = {row[0]: row[1] for row in await cursor.fetchall()}
            
            # Get registries by name
            name_sql = """
            SELECT registry_name, COUNT(*) as count 
            FROM twin_registry_metadata 
            GROUP BY registry_name
            """
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(name_sql) as cursor:
                    registries_by_name = {row[0]: row[1] for row in await cursor.fetchall()}
            
            return TwinRegistrySummary(
                total_registries=total_registries,
                active_registries=active_registries,
                registries_by_type=registries_by_type,
                registries_by_name=registries_by_name
            )
            
        except Exception as e:
            logger.error(f"Failed to get registry summary: {e}")
            raise
    
    async def get_default_config(self) -> TwinRegistryConfig:
        """Get default registry configuration."""
        try:
            sql = "SELECT * FROM twin_registry_config WHERE config_id = 'default'"
            
            async with self.db_manager.get_connection() as conn:
                async with conn.execute(sql) as cursor:
                    row = await cursor.fetchone()
                    
            if row:
                return self._row_to_config(row)
            else:
                # Create default config if it doesn't exist
                default_config = TwinRegistryConfig()
                await self.save_config("default", default_config)
                return default_config
                
        except Exception as e:
            logger.error(f"Failed to get default config: {e}")
            raise
    
    async def save_config(self, config_id: str, config: TwinRegistryConfig) -> bool:
        """Save registry configuration."""
        try:
            sql = """
            INSERT OR REPLACE INTO twin_registry_config 
            (config_id, auto_sync_enabled, sync_interval_minutes, health_check_enabled,
             health_check_interval_minutes, max_instances_per_twin, retention_days,
             backup_enabled, backup_interval_hours, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.utcnow()
            params = (
                config_id,
                config.auto_sync_enabled,
                config.sync_interval_minutes,
                config.health_check_enabled,
                config.health_check_interval_minutes,
                config.max_instances_per_twin,
                config.retention_days,
                config.backup_enabled,
                config.backup_interval_hours,
                now.isoformat(),
                now.isoformat()
            )
            
            async with self.db_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Saved registry config: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save registry config {config_id}: {e}")
            raise
    
    def _row_to_metadata(self, row) -> TwinRegistryMetadata:
        """Convert database row to TwinRegistryMetadata object."""
        return TwinRegistryMetadata(
            registry_id=row[0],
            twin_id=row[1],
            registry_name=row[2],
            registry_type=row[3],
            registry_config=self._deserialize_json(row[4]),
            registry_metadata=self._deserialize_json(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]) if row[7] else None,
            is_active=bool(row[8]),
            version=row[9]
        )
    
    def _row_to_config(self, row) -> TwinRegistryConfig:
        """Convert database row to TwinRegistryConfig object."""
        return TwinRegistryConfig(
            auto_sync_enabled=bool(row[1]),
            sync_interval_minutes=row[2],
            health_check_enabled=bool(row[3]),
            health_check_interval_minutes=row[4],
            max_instances_per_twin=row[5],
            retention_days=row[6],
            backup_enabled=bool(row[7]),
            backup_interval_hours=row[8]
        ) 