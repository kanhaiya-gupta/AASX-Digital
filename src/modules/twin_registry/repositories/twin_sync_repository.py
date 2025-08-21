"""
Twin Sync Repository

Data access layer for twin synchronization management using JSON fields.
Updated for Phase 2: JSON field operations instead of separate tables.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.base_repository import BaseRepository
from src.twin_registry.models.twin_sync import TwinSyncHistory, TwinSyncStatus, TwinSyncConfiguration

logger = logging.getLogger(__name__)


class TwinSyncRepository(BaseRepository[TwinSyncHistory]):
    """Repository for managing twin synchronization using JSON fields."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        """Initialize the twin sync repository."""
        super().__init__(db_manager, TwinSyncHistory)
        logger.info("Twin Sync Repository initialized (JSON field mode)")
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return "twin_registry"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for this table."""
        return [
            "registry_id", "twin_id", "twin_name", "registry_name", "twin_category", "twin_type",
            "twin_priority", "twin_version", "registry_type", "workflow_source", "aasx_integration_id",
            "physics_modeling_id", "federated_learning_id", "data_pipeline_id", "kg_neo4j_id",
            "certificate_manager_id", "integration_status", "overall_health_score", "health_status",
            "lifecycle_status", "lifecycle_phase", "operational_status", "availability_status",
            "sync_status", "sync_frequency", "last_sync_at", "next_sync_at", "sync_error_count",
            "sync_error_message", "performance_score", "data_quality_score", "reliability_score",
            "compliance_score", "security_level", "access_control_level", "encryption_enabled",
            "audit_logging_enabled", "user_id", "org_id", "owner_team", "steward_user_id",
            "created_at", "updated_at", "activated_at", "last_accessed_at", "last_modified_at",
            "registry_config", "registry_metadata", "custom_attributes", "tags", "relationships",
            "dependencies", "instances"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for twin registry table."""
        return "registry_id"
    
    async def initialize(self) -> None:
        """Initialize the repository - no tables needed for JSON field approach."""
        logger.info("Twin Sync Repository initialized (JSON field mode)")
    
    async def create_sync_history(self, registry_id: str, sync_history: TwinSyncHistory) -> TwinSyncHistory:
        """Create a new sync history record by adding to the JSON field."""
        try:
            # Get current sync history from the registry
            current_history = await self._get_sync_history_json(registry_id)
            
            # Add new sync history
            history_dict = {
                "id": sync_history.id,
                "twin_id": sync_history.twin_id,
                "sync_type": sync_history.sync_type,
                "status": sync_history.status,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": sync_history.completed_at,
                "error_message": sync_history.error_message,
                "sync_data": sync_history.sync_data or {},
                "metadata": sync_history.metadata or {}
            }
            
            current_history.append(history_dict)
            
            # Update the JSON field
            query = """
            UPDATE twin_registry 
            SET sync_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            await self.execute_query(query, (json.dumps(current_history), registry_id))
            
            # Also update the sync status fields
            await self._update_sync_status(registry_id, sync_history.status, sync_history.sync_type)
            
            logger.info(f"Created sync history {sync_history.id} in registry {registry_id}")
            return sync_history
            
        except Exception as e:
            logger.error(f"Failed to create sync history: {e}")
            raise
    
    async def get_sync_history(self, registry_id: str, sync_id: str) -> Optional[TwinSyncHistory]:
        """Get a sync history record by ID from the JSON field."""
        try:
            history = await self._get_sync_history_json(registry_id)
            
            for record in history:
                if record.get("id") == sync_id:
                    return self._dict_to_sync_history(record)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get sync history {sync_id}: {e}")
            return None
    
    async def get_sync_history_by_twin(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinSyncHistory]:
        """Get sync history for a specific twin from the JSON field."""
        try:
            history = await self._get_sync_history_json(registry_id)
            
            # Filter by twin_id and limit results
            twin_history = [record for record in history if record.get("twin_id") == twin_id]
            twin_history.sort(key=lambda x: x.get("started_at", ""), reverse=True)
            
            return [self._dict_to_sync_history(record) for record in twin_history[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get sync history for twin {twin_id}: {e}")
            return []
    
    async def get_sync_status(self, registry_id: str) -> Optional[TwinSyncStatus]:
        """Get the current sync status from the registry."""
        try:
            query = """
            SELECT sync_status, sync_frequency, last_sync_at, next_sync_at, sync_error_count, sync_error_message
            FROM twin_registry 
            WHERE registry_id = ?
            """
            result = await self.fetch_one(query, (registry_id,))
            
            if result:
                return TwinSyncStatus(
                    twin_id=registry_id,
                    last_sync_timestamp=result.get("last_sync_at"),
                    last_sync_status=result.get("sync_status", "unknown"),
                    last_sync_type="auto",  # Default type
                    next_sync_timestamp=result.get("next_sync_at"),
                    sync_configuration={"frequency": result.get("sync_frequency", "daily")},
                    metadata={
                        "error_count": result.get("sync_error_count", 0),
                        "error_message": result.get("sync_error_message")
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get sync status for registry {registry_id}: {e}")
            return None
    
    async def update_sync_status(self, registry_id: str, sync_status: TwinSyncStatus) -> bool:
        """Update the sync status in the registry."""
        try:
            # Update sync-related fields
            query = """
            UPDATE twin_registry 
            SET sync_status = ?, sync_frequency = ?, last_sync_at = ?, next_sync_at = ?, 
                sync_error_count = ?, sync_error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            
            # Extract values from sync_status
            frequency = sync_status.sync_configuration.get("frequency", "daily") if sync_status.sync_configuration else "daily"
            error_count = sync_status.metadata.get("error_count", 0) if sync_status.metadata else 0
            error_message = sync_status.metadata.get("error_message") if sync_status.metadata else None
            
            params = (
                sync_status.last_sync_status,
                frequency,
                sync_status.last_sync_timestamp,
                sync_status.next_sync_timestamp,
                error_count,
                error_message,
                registry_id
            )
            
            await self.execute_query(query, params)
            logger.info(f"Updated sync status for registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update sync status for registry {registry_id}: {e}")
            return False
    
    async def get_failed_syncs(self, registry_id: str, limit: int = 100) -> List[TwinSyncHistory]:
        """Get recent failed sync operations from the JSON field."""
        try:
            history = await self._get_sync_history_json(registry_id)
            
            # Filter failed syncs and limit results
            failed_syncs = [record for record in history if record.get("status") == "failed"]
            failed_syncs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
            
            return [self._dict_to_sync_history(record) for record in failed_syncs[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get failed syncs: {e}")
            return []
    
    async def get_pending_syncs(self, registry_id: str) -> List[TwinSyncHistory]:
        """Get pending sync operations from the JSON field."""
        try:
            history = await self._get_sync_history_json(registry_id)
            
            # Filter pending syncs
            pending_syncs = [record for record in history if record.get("status") == "pending"]
            pending_syncs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
            
            return [self._dict_to_sync_history(record) for record in pending_syncs]
            
        except Exception as e:
            logger.error(f"Failed to get pending syncs: {e}")
            return []
    
    async def cleanup_old_sync_history(self, registry_id: str, days: int = 30) -> int:
        """Clean up old sync history records from the JSON field."""
        try:
            history = await self._get_sync_history_json(registry_id)
            cutoff_date = (datetime.now(timezone.utc) - datetime.timedelta(days=days)).isoformat()
            
            # Filter out old records
            original_count = len(history)
            history = [record for record in history if record.get("started_at", "") >= cutoff_date]
            
            if len(history) < original_count:
                # Update the JSON field
                query = """
                UPDATE twin_registry 
                SET sync_status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE registry_id = ?
                """
                await self.execute_query(query, (json.dumps(history), registry_id))
                
                cleaned_count = original_count - len(history)
                logger.info(f"Cleaned up {cleaned_count} old sync history records from registry {registry_id}")
                return cleaned_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup sync history: {e}")
            return 0
    
    async def _get_sync_history_json(self, registry_id: str) -> List[Dict[str, Any]]:
        """Get the sync_status JSON field from the registry."""
        query = "SELECT sync_status FROM twin_registry WHERE registry_id = ?"
        result = await self.fetch_one(query, (registry_id,))
        
        if result and result.get("sync_status"):
            try:
                return json.loads(result["sync_status"])
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in sync_status field for registry {registry_id}")
                return []
        
        return []
    
    async def _update_sync_status(self, registry_id: str, status: str, sync_type: str) -> None:
        """Update sync status fields based on sync history."""
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            # Update sync status fields
            query = """
            UPDATE twin_registry 
            SET sync_status = ?, last_sync_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            await self.execute_query(query, (status, now, registry_id))
            
            # Update error count if failed
            if status == "failed":
                error_query = """
                UPDATE twin_registry 
                SET sync_error_count = sync_error_count + 1, updated_at = CURRENT_TIMESTAMP
                WHERE registry_id = ?
                """
                await self.execute_query(error_query, (registry_id,))
            
        except Exception as e:
            logger.error(f"Failed to update sync status: {e}")
    
    def _dict_to_sync_history(self, history_dict: Dict[str, Any]) -> TwinSyncHistory:
        """Convert dictionary to TwinSyncHistory object."""
        return TwinSyncHistory(
            id=history_dict.get("id"),
            twin_id=history_dict.get("twin_id"),
            sync_type=history_dict.get("sync_type"),
            status=history_dict.get("status"),
            started_at=history_dict.get("started_at"),
            completed_at=history_dict.get("completed_at"),
            error_message=history_dict.get("error_message"),
            sync_data=history_dict.get("sync_data", {}),
            metadata=history_dict.get("metadata", {})
        ) 