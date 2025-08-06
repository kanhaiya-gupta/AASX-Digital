"""
Twin Sync Service

Manages twin synchronization including:
- Sync strategies (full, incremental, metadata)
- Sync conflict resolution
- Sync scheduling and automation
- Sync performance monitoring
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from src.shared.services.base_service import BaseService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.twin_registry.models.twin_sync import TwinSyncHistory, TwinSyncStatus, TwinSyncConfiguration, TwinSyncOperation
from src.twin_registry.repositories.twin_sync_repository import TwinSyncRepository

logger = logging.getLogger(__name__)


class TwinSyncService(BaseService):
    """
    Service for managing twin synchronization.
    
    Provides functionality for:
    - Sync strategies (full, incremental, metadata)
    - Sync conflict resolution
    - Sync scheduling and automation
    - Sync performance monitoring
    """
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize the twin sync service."""
        super().__init__(db_manager)
        self.sync_repo = TwinSyncRepository(db_manager)
        logger.info("Twin Sync Service initialized")
    
    async def initialize(self) -> None:
        """Initialize the sync service."""
        try:
            await self.sync_repo.initialize()
            logger.info("Twin Sync Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Sync Service: {e}")
            raise
    
    async def sync_twin(
        self,
        twin_id: str,
        sync_type: str = "full",
        sync_data: Optional[Dict[str, Any]] = None,
        triggered_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronize a twin.
        
        Args:
            twin_id: ID of the twin to sync
            sync_type: Type of sync ('full', 'incremental', 'metadata')
            sync_data: Data to sync
            triggered_by: User who triggered the sync
            
        Returns:
            Dictionary with sync status and results
        """
        try:
            logger.info(f"Starting sync for twin: {twin_id} (type: {sync_type})")
            
            # Create sync history record
            sync_history = TwinSyncHistory(
                id=str(uuid.uuid4()),
                twin_id=twin_id,
                sync_type=sync_type,
                status="running",
                started_at=datetime.utcnow().isoformat(),
                sync_data=sync_data or {},
                metadata={"triggered_by": triggered_by}
            )
            
            # Save initial history record
            await self.sync_repo.create_sync_history(sync_history)
            
            # Perform sync based on type
            if sync_type == "full":
                result = await self._perform_full_sync(twin_id, sync_data)
            elif sync_type == "incremental":
                result = await self._perform_incremental_sync(twin_id, sync_data)
            elif sync_type == "metadata":
                result = await self._perform_metadata_sync(twin_id, sync_data)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown sync type: {sync_type}"
                }
            
            # Update sync history
            completed_at = datetime.utcnow().isoformat()
            update_data = {
                "status": "completed" if result["success"] else "failed",
                "completed_at": completed_at,
                "error_message": result.get("error"),
                "sync_data": result.get("sync_data", {})
            }
            
            await self.sync_repo.update_sync_history(sync_history.id, update_data)
            
            # Update sync status
            await self._update_sync_status(twin_id, sync_type, result["success"])
            
            return {
                "success": result["success"],
                "sync_id": sync_history.id,
                "message": result.get("message", "Sync completed"),
                "error": result.get("error"),
                "sync_data": result.get("sync_data", {}),
                "started_at": sync_history.started_at,
                "completed_at": completed_at
            }
            
        except Exception as e:
            logger.error(f"Failed to sync twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "sync_id": None
            }
    
    async def get_sync_status(self, twin_id: str) -> Dict[str, Any]:
        """
        Get sync status for a twin.
        
        Args:
            twin_id: ID of the twin
            
        Returns:
            Dictionary with sync status
        """
        try:
            logger.info(f"Getting sync status for twin: {twin_id}")
            
            sync_status = await self.sync_repo.get_sync_status(twin_id)
            
            if sync_status:
                return {
                    "success": True,
                    "sync_status": {
                        "twin_id": sync_status.twin_id,
                        "last_sync_timestamp": sync_status.last_sync_timestamp,
                        "last_sync_status": sync_status.last_sync_status,
                        "last_sync_type": sync_status.last_sync_type,
                        "next_sync_timestamp": sync_status.next_sync_timestamp,
                        "sync_configuration": sync_status.sync_configuration,
                        "metadata": sync_status.metadata
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No sync status found",
                    "sync_status": None
                }
                
        except Exception as e:
            logger.error(f"Failed to get sync status for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "sync_status": None
            }
    
    async def get_sync_history(
        self,
        twin_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get sync history for a twin.
        
        Args:
            twin_id: ID of the twin
            limit: Maximum number of history records to return
            
        Returns:
            Dictionary with sync history
        """
        try:
            logger.info(f"Getting sync history for twin: {twin_id}")
            
            history = await self.sync_repo.get_sync_history(twin_id, limit)
            
            return {
                "success": True,
                "history": [self._convert_sync_history_to_dict(h) for h in history],
                "count": len(history),
                "twin_id": twin_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync history for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "history": [],
                "count": 0
            }
    
    async def update_sync_configuration(
        self,
        twin_id: str,
        configuration: TwinSyncConfiguration
    ) -> Dict[str, Any]:
        """
        Update sync configuration for a twin.
        
        Args:
            twin_id: ID of the twin
            configuration: New sync configuration
            
        Returns:
            Dictionary with update status
        """
        try:
            logger.info(f"Updating sync configuration for twin: {twin_id}")
            
            # Get current sync status
            current_status = await self.sync_repo.get_sync_status(twin_id)
            
            if current_status:
                # Update existing status
                current_status.sync_configuration = configuration
                success = await self.sync_repo.update_sync_status(twin_id, current_status)
            else:
                # Create new status
                new_status = TwinSyncStatus(
                    twin_id=twin_id,
                    sync_configuration=configuration
                )
                success = await self.sync_repo.update_sync_status(twin_id, new_status)
            
            return {
                "success": success,
                "message": "Sync configuration updated successfully" if success else "Failed to update configuration",
                "twin_id": twin_id
            }
            
        except Exception as e:
            logger.error(f"Failed to update sync configuration for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "twin_id": twin_id
            }
    
    async def get_failed_syncs(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get recent failed sync operations.
        
        Args:
            limit: Maximum number of failed syncs to return
            
        Returns:
            Dictionary with failed syncs
        """
        try:
            logger.info("Getting failed syncs")
            
            failed_syncs = await self.sync_repo.get_failed_syncs(limit)
            
            return {
                "success": True,
                "failed_syncs": [self._convert_sync_history_to_dict(s) for s in failed_syncs],
                "count": len(failed_syncs)
            }
            
        except Exception as e:
            logger.error(f"Failed to get failed syncs: {e}")
            return {
                "success": False,
                "error": str(e),
                "failed_syncs": [],
                "count": 0
            }
    
    async def cleanup_old_sync_history(self, days: int = 30) -> Dict[str, Any]:
        """
        Clean up old sync history records.
        
        Args:
            days: Number of days to keep history
            
        Returns:
            Dictionary with cleanup status
        """
        try:
            logger.info(f"Cleaning up sync history older than {days} days")
            
            await self.sync_repo.cleanup_old_sync_history(days)
            
            return {
                "success": True,
                "message": f"Cleaned up sync history older than {days} days"
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup sync history: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _perform_full_sync(self, twin_id: str, sync_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform a full sync for a twin."""
        try:
            logger.info(f"Performing full sync for twin: {twin_id}")
            
            # Simulate full sync process
            # In a real implementation, this would sync all twin data
            
            return {
                "success": True,
                "message": "Full sync completed successfully",
                "sync_data": {
                    "sync_type": "full",
                    "data_synced": True,
                    "metadata_synced": True,
                    "relationships_synced": True
                }
            }
            
        except Exception as e:
            logger.error(f"Full sync failed for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _perform_incremental_sync(self, twin_id: str, sync_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform an incremental sync for a twin."""
        try:
            logger.info(f"Performing incremental sync for twin: {twin_id}")
            
            # Simulate incremental sync process
            # In a real implementation, this would sync only changed data
            
            return {
                "success": True,
                "message": "Incremental sync completed successfully",
                "sync_data": {
                    "sync_type": "incremental",
                    "changes_synced": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Incremental sync failed for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _perform_metadata_sync(self, twin_id: str, sync_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform a metadata sync for a twin."""
        try:
            logger.info(f"Performing metadata sync for twin: {twin_id}")
            
            # Simulate metadata sync process
            # In a real implementation, this would sync only metadata
            
            return {
                "success": True,
                "message": "Metadata sync completed successfully",
                "sync_data": {
                    "sync_type": "metadata",
                    "metadata_synced": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Metadata sync failed for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_sync_status(self, twin_id: str, sync_type: str, success: bool) -> None:
        """Update sync status for a twin."""
        try:
            current_status = await self.sync_repo.get_sync_status(twin_id)
            
            if current_status:
                current_status.last_sync_timestamp = datetime.utcnow().isoformat()
                current_status.last_sync_status = "success" if success else "failed"
                current_status.last_sync_type = sync_type
                
                # Calculate next sync time if configuration exists
                if current_status.sync_configuration and current_status.sync_configuration.enabled:
                    next_sync = datetime.utcnow() + timedelta(seconds=current_status.sync_configuration.sync_interval)
                    current_status.next_sync_timestamp = next_sync.isoformat()
                
                await self.sync_repo.update_sync_status(twin_id, current_status)
            else:
                # Create new status
                new_status = TwinSyncStatus(
                    twin_id=twin_id,
                    last_sync_timestamp=datetime.utcnow().isoformat(),
                    last_sync_status="success" if success else "failed",
                    last_sync_type=sync_type
                )
                await self.sync_repo.update_sync_status(twin_id, new_status)
                
        except Exception as e:
            logger.error(f"Failed to update sync status for twin {twin_id}: {e}")
    
    def _convert_sync_history_to_dict(self, sync_history: TwinSyncHistory) -> Dict[str, Any]:
        """Convert a TwinSyncHistory object to dictionary."""
        return {
            "id": sync_history.id,
            "twin_id": sync_history.twin_id,
            "sync_type": sync_history.sync_type,
            "status": sync_history.status,
            "started_at": sync_history.started_at,
            "completed_at": sync_history.completed_at,
            "error_message": sync_history.error_message,
            "sync_data": sync_history.sync_data,
            "metadata": sync_history.metadata
        } 