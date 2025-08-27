"""
Twin Sync Service

Service for managing twin synchronization using JSON fields.
Updated for Phase 2: JSON field operations instead of separate tables.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.database_factory import DatabaseFactory, DatabaseType
from ..models.twin_sync import (
    TwinSyncHistory, 
    TwinSyncStatus, 
    TwinSyncConfiguration, 
    TwinSyncOperation
)
from ..repositories.twin_sync_repository import TwinSyncRepository

logger = logging.getLogger(__name__)


class TwinSyncService:
    """Service for managing twin synchronization"""
    
    def __init__(self):
        """Initialize the twin sync service"""
        # Use the same database infrastructure as other modules
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        # Initialize central database connection
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        
        # Initialize repository with database connection
        self.sync_repo = TwinSyncRepository(self.db_manager)
    
    async def initialize(self) -> None:
        """Initialize the service - no tables needed for JSON field approach"""
        try:
            # No table creation needed - all data stored in existing twin_registry tables
            logger.info("Twin Sync Service initialized successfully (JSON field mode)")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Sync Service: {e}")
            raise
    
    # ==================== Sync History Management ====================
    
    async def create_sync_history(
        self,
        registry_id: str,
        twin_id: str,
        sync_operation: TwinSyncOperation,
        sync_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        triggered_by: Optional[str] = None
    ) -> TwinSyncHistory:
        """Create a new sync history record"""
        try:
            # Create sync history object
            sync_history = TwinSyncHistory.create_sync_history(
                twin_id=twin_id,
                sync_operation=sync_operation,
                sync_data=sync_data or {},
                metadata=metadata or {},
                triggered_by=triggered_by
            )
            
            # Save to database using JSON field
            await self.sync_repo.create_sync_history(registry_id, sync_history)
            
            logger.info(f"Created sync history {sync_history.sync_id} for twin {twin_id} in registry {registry_id}")
            return sync_history
            
        except Exception as e:
            logger.error(f"Failed to create sync history for twin {twin_id}: {e}")
            raise
    
    async def get_sync_history(self, registry_id: str, sync_id: str) -> Optional[TwinSyncHistory]:
        """Get sync history by ID"""
        try:
            return await self.sync_repo.get_sync_history(registry_id, sync_id)
        except Exception as e:
            logger.error(f"Failed to get sync history {sync_id}: {e}")
            return None
    
    async def get_sync_history_by_twin(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinSyncHistory]:
        """Get sync history for a specific twin"""
        try:
            return await self.sync_repo.get_sync_history_by_twin(registry_id, twin_id, limit)
        except Exception as e:
            logger.error(f"Failed to get sync history for twin {twin_id}: {e}")
            return []
    
    # ==================== Sync Status Management ====================
    
    async def get_sync_status(self, registry_id: str) -> Optional[TwinSyncStatus]:
        """Get current sync status for a registry"""
        try:
            return await self.sync_repo.get_sync_status(registry_id)
        except Exception as e:
            logger.error(f"Failed to get sync status for registry {registry_id}: {e}")
            return None
    
    async def update_sync_status(
        self,
        registry_id: str,
        status: str,
        last_sync_at: Optional[datetime] = None,
        next_sync_at: Optional[datetime] = None,
        sync_error_count: Optional[int] = None,
        sync_error_message: Optional[str] = None
    ) -> bool:
        """Update sync status for a registry"""
        try:
            result = await self.sync_repo.update_sync_status(
                registry_id, 
                status, 
                last_sync_at, 
                next_sync_at, 
                sync_error_count, 
                sync_error_message
            )
            if result:
                logger.info(f"Updated sync status for registry {registry_id} to {status}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update sync status for registry {registry_id}: {e}")
            return False
    
    # ==================== Sync Operations ====================
    
    async def start_sync(self, registry_id: str, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Start synchronization for a twin"""
        try:
            # Create sync started history
            sync_history = await self.create_sync_history(
                registry_id=registry_id,
                twin_id=twin_id,
                sync_operation=TwinSyncOperation.SYNC_STARTED,
                triggered_by=triggered_by
            )
            
            # Update sync status
            await self.update_sync_status(
                registry_id=registry_id,
                status="syncing",
                last_sync_at=datetime.now()
            )
            
            logger.info(f"Started sync for twin {twin_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start sync for twin {twin_id}: {e}")
            return False
    
    async def complete_sync(self, registry_id: str, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Complete synchronization for a twin"""
        try:
            # Create sync completed history
            sync_history = await self.create_sync_history(
                registry_id=registry_id,
                twin_id=twin_id,
                sync_operation=TwinSyncOperation.SYNC_COMPLETED,
                triggered_by=triggered_by
            )
            
            # Update sync status
            await self.update_sync_status(
                registry_id=registry_id,
                status="synced",
                last_sync_at=datetime.now(),
                next_sync_at=datetime.now() + timedelta(hours=1)  # Default next sync in 1 hour
            )
            
            logger.info(f"Completed sync for twin {twin_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete sync for twin {twin_id}: {e}")
            return False
    
    async def fail_sync(self, registry_id: str, twin_id: str, error_message: str, triggered_by: Optional[str] = None) -> bool:
        """Mark synchronization as failed for a twin"""
        try:
            # Create sync failed history
            sync_history = await self.create_sync_history(
                registry_id=registry_id,
                twin_id=twin_id,
                sync_operation=TwinSyncOperation.SYNC_FAILED,
                sync_data={"error_message": error_message},
                triggered_by=triggered_by
            )
            
            # Get current error count and increment
            current_status = await self.get_sync_status(registry_id)
            current_error_count = current_status.sync_error_count if current_status else 0
            new_error_count = current_error_count + 1
            
            # Update sync status
            await self.update_sync_status(
                registry_id=registry_id,
                status="failed",
                last_sync_at=datetime.now(),
                sync_error_count=new_error_count,
                sync_error_message=error_message
            )
            
            logger.info(f"Marked sync as failed for twin {twin_id}: {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark sync as failed for twin {twin_id}: {e}")
            return False
    
    # ==================== Sync Queries ====================
    
    async def get_failed_syncs(self, registry_id: str, limit: int = 50) -> List[TwinSyncHistory]:
        """Get failed sync operations"""
        try:
            return await self.sync_repo.get_failed_syncs(registry_id, limit)
        except Exception as e:
            logger.error(f"Failed to get failed syncs: {e}")
            return []
    
    async def get_pending_syncs(self, registry_id: str) -> List[TwinSyncHistory]:
        """Get pending sync operations"""
        try:
            return await self.sync_repo.get_pending_syncs(registry_id)
        except Exception as e:
            logger.error(f"Failed to get pending syncs: {e}")
            return []
    
    async def get_syncs_in_date_range(
        self,
        registry_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[TwinSyncHistory]:
        """Get sync operations within a date range"""
        try:
            # This would need to be enhanced with proper date filtering
            # For now, get all sync history and filter
            all_syncs = await self.sync_repo.get_sync_history_by_twin(registry_id, "", 1000)
            
            filtered_syncs = []
            for sync in all_syncs:
                if start_date <= sync.timestamp <= end_date:
                    filtered_syncs.append(sync)
            
            return filtered_syncs
            
        except Exception as e:
            logger.error(f"Failed to get syncs in date range: {e}")
            return []
    
    # ==================== Sync Analytics ====================
    
    async def get_sync_summary(self, registry_id: str) -> Dict[str, Any]:
        """Get sync statistics and summary"""
        try:
            # Get all sync history
            all_syncs = await self.sync_repo.get_sync_history_by_twin(registry_id, "", 1000)
            
            total_syncs = len(all_syncs)
            successful_syncs = len([s for s in all_syncs if s.sync_operation == TwinSyncOperation.SYNC_COMPLETED])
            failed_syncs = len([s for s in all_syncs if s.sync_operation == TwinSyncOperation.SYNC_FAILED])
            pending_syncs = len([s for s in all_syncs if s.sync_operation == TwinSyncOperation.SYNC_STARTED])
            
            # Count by operation type
            syncs_by_operation = {}
            for sync in all_syncs:
                op_type = sync.sync_operation.value
                syncs_by_operation[op_type] = syncs_by_operation.get(op_type, 0) + 1
            
            # Count by twin
            syncs_by_twin = {}
            for sync in all_syncs:
                twin_id = sync.twin_id
                syncs_by_twin[twin_id] = syncs_by_twin.get(twin_id, 0) + 1
            
            return {
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "failed_syncs": failed_syncs,
                "pending_syncs": pending_syncs,
                "success_rate": (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0,
                "syncs_by_operation": syncs_by_operation,
                "syncs_by_twin": syncs_by_twin
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync summary: {e}")
            return {}
    
    # ==================== Sync Maintenance ====================
    
    async def cleanup_old_sync_history(self, registry_id: str, days_to_keep: int = 30) -> int:
        """Clean up old sync history records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            return await self.sync_repo.cleanup_old_sync_history(registry_id, cutoff_date)
        except Exception as e:
            logger.error(f"Failed to cleanup old sync history: {e}")
            return 0
    
    async def reset_sync_errors(self, registry_id: str) -> bool:
        """Reset sync error count and clear error message"""
        try:
            result = await self.update_sync_status(
                registry_id=registry_id,
                status="ready",
                sync_error_count=0,
                sync_error_message=None
            )
            if result:
                logger.info(f"Reset sync errors for registry {registry_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to reset sync errors for registry {registry_id}: {e}")
            return False
    
    # ==================== Sync Configuration ====================
    
    async def get_sync_configuration(self, registry_id: str) -> Optional[TwinSyncConfiguration]:
        """Get sync configuration for a registry"""
        try:
            # This would need to be implemented based on how sync configuration is stored
            # For now, return a default configuration
            return TwinSyncConfiguration(
                sync_frequency_minutes=60,
                max_retry_attempts=3,
                retry_delay_minutes=5,
                sync_timeout_seconds=300
            )
        except Exception as e:
            logger.error(f"Failed to get sync configuration for registry {registry_id}: {e}")
            return None
    
    async def update_sync_configuration(
        self,
        registry_id: str,
        config: TwinSyncConfiguration
    ) -> bool:
        """Update sync configuration for a registry"""
        try:
            # This would need to be implemented based on how sync configuration is stored
            # For now, just log the update
            logger.info(f"Updated sync configuration for registry {registry_id}: {config}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update sync configuration for registry {registry_id}: {e}")
            return False 