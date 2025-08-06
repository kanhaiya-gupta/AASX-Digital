"""
Twin Lifecycle Service

Service for managing twin lifecycle events and status.
"""

from src.shared.services.base_service import BaseService
from ..repositories.twin_lifecycle_repository import TwinLifecycleRepository
from ..models.twin_lifecycle import (
    TwinLifecycleEvent, TwinLifecycleStatus, TwinLifecycleQuery, TwinLifecycleSummary,
    LifecycleEventType, LifecycleStatus
)
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TwinLifecycleService(BaseService):
    """Service for managing twin lifecycle"""
    
    def __init__(self):
        super().__init__()
        self.lifecycle_repo = TwinLifecycleRepository()
    
    async def initialize(self) -> None:
        """Initialize the service"""
        try:
            await self.lifecycle_repo.create_table()
            logger.info("Twin Lifecycle Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Lifecycle Service: {e}")
            raise
    
    # ==================== Lifecycle Events ====================
    
    async def create_event(
        self,
        twin_id: str,
        event_type: LifecycleEventType,
        event_data: Optional[Dict[str, Any]] = None,
        event_metadata: Optional[Dict[str, Any]] = None,
        triggered_by: Optional[str] = None
    ) -> TwinLifecycleEvent:
        """Create a new lifecycle event"""
        try:
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=event_type,
                event_data=event_data,
                event_metadata=event_metadata,
                triggered_by=triggered_by
            )
            
            await self.lifecycle_repo.create_event(event)
            logger.info(f"Created lifecycle event {event.event_id} for twin {twin_id}")
            return event
            
        except Exception as e:
            logger.error(f"Failed to create lifecycle event for twin {twin_id}: {e}")
            raise
    
    async def get_events(
        self,
        twin_id: Optional[str] = None,
        query: Optional[TwinLifecycleQuery] = None
    ) -> List[TwinLifecycleEvent]:
        """Get lifecycle events with optional filtering"""
        try:
            if twin_id:
                return await self.lifecycle_repo.get_events_by_twin(twin_id, query)
            else:
                return await self.lifecycle_repo.get_events(query)
        except Exception as e:
            logger.error(f"Failed to get lifecycle events: {e}")
            raise
    
    async def get_recent_events(self, twin_id: str, limit: int = 10) -> List[TwinLifecycleEvent]:
        """Get recent lifecycle events for a twin"""
        try:
            return await self.lifecycle_repo.get_recent_events(twin_id, limit)
        except Exception as e:
            logger.error(f"Failed to get recent events for twin {twin_id}: {e}")
            raise
    
    # ==================== Lifecycle Status ====================
    
    async def get_status(self, twin_id: str) -> Optional[TwinLifecycleStatus]:
        """Get current lifecycle status for a twin"""
        try:
            return await self.lifecycle_repo.get_status(twin_id)
        except Exception as e:
            logger.error(f"Failed to get status for twin {twin_id}: {e}")
            raise
    
    async def update_status(
        self,
        twin_id: str,
        new_status: LifecycleStatus,
        event: Optional[TwinLifecycleEvent] = None
    ) -> TwinLifecycleStatus:
        """Update lifecycle status for a twin"""
        try:
            return await self.lifecycle_repo.update_status(twin_id, new_status, event)
        except Exception as e:
            logger.error(f"Failed to update status for twin {twin_id}: {e}")
            raise
    
    async def get_all_statuses(self) -> List[TwinLifecycleStatus]:
        """Get lifecycle status for all twins"""
        try:
            return await self.lifecycle_repo.get_all_statuses()
        except Exception as e:
            logger.error(f"Failed to get all statuses: {e}")
            raise
    
    # ==================== Lifecycle Operations ====================
    
    async def start_twin(self, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Start a twin and update lifecycle"""
        try:
            # Create start event
            event = await self.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.STARTED,
                triggered_by=triggered_by
            )
            
            # Update status
            await self.update_status(twin_id, LifecycleStatus.RUNNING, event)
            
            logger.info(f"Started twin {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start twin {twin_id}: {e}")
            raise
    
    async def stop_twin(self, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Stop a twin and update lifecycle"""
        try:
            # Create stop event
            event = await self.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.STOPPED,
                triggered_by=triggered_by
            )
            
            # Update status
            await self.update_status(twin_id, LifecycleStatus.STOPPED, event)
            
            logger.info(f"Stopped twin {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop twin {twin_id}: {e}")
            raise
    
    async def sync_twin(
        self,
        twin_id: str,
        sync_data: Optional[Dict[str, Any]] = None,
        triggered_by: Optional[str] = None
    ) -> bool:
        """Sync a twin and update lifecycle"""
        try:
            # Create sync started event
            start_event = await self.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.SYNC_STARTED,
                event_data=sync_data,
                triggered_by=triggered_by
            )
            start_event.mark_in_progress()
            await self.lifecycle_repo.update_event(start_event)
            
            # Update status to syncing
            await self.update_status(twin_id, LifecycleStatus.SYNCING, start_event)
            
            # TODO: Implement actual sync logic here
            # For now, just mark as completed
            
            # Create sync completed event
            complete_event = await self.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.SYNC_COMPLETED,
                event_data=sync_data,
                triggered_by=triggered_by
            )
            
            # Update status back to running
            await self.update_status(twin_id, LifecycleStatus.RUNNING, complete_event)
            
            logger.info(f"Synced twin {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync twin {twin_id}: {e}")
            # Create sync failed event
            failed_event = await self.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.SYNC_FAILED,
                event_data=sync_data,
                triggered_by=triggered_by
            )
            failed_event.mark_failed(str(e))
            await self.lifecycle_repo.update_event(failed_event)
            await self.update_status(twin_id, LifecycleStatus.ERROR, failed_event)
            raise
    
    async def mark_error(
        self,
        twin_id: str,
        error_message: str,
        triggered_by: Optional[str] = None
    ) -> bool:
        """Mark a twin as having an error"""
        try:
            # Create error event
            event = await self.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.ERROR,
                event_data={"error_message": error_message},
                triggered_by=triggered_by
            )
            event.mark_failed(error_message)
            await self.lifecycle_repo.update_event(event)
            
            # Update status
            await self.update_status(twin_id, LifecycleStatus.ERROR, event)
            
            logger.info(f"Marked twin {twin_id} as error: {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark twin {twin_id} as error: {e}")
            raise
    
    # ==================== Lifecycle Analytics ====================
    
    async def get_lifecycle_summary(self) -> TwinLifecycleSummary:
        """Get lifecycle statistics"""
        try:
            return await self.lifecycle_repo.get_lifecycle_summary()
        except Exception as e:
            logger.error(f"Failed to get lifecycle summary: {e}")
            raise
    
    async def get_status_distribution(self) -> Dict[str, int]:
        """Get distribution of twin statuses"""
        try:
            statuses = await self.get_all_statuses()
            distribution = {}
            
            for status in statuses:
                status_str = status.current_status.value
                distribution[status_str] = distribution.get(status_str, 0) + 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to get status distribution: {e}")
            raise
    
    async def get_twin_health(self, twin_id: str) -> Dict[str, Any]:
        """Get health information for a twin"""
        try:
            # Get current status
            status = await self.get_status(twin_id)
            
            # Get recent events
            recent_events = await self.get_recent_events(twin_id, limit=5)
            
            # Calculate health score based on recent events
            health_score = 100
            error_count = 0
            
            for event in recent_events:
                if event.event_type in [LifecycleEventType.ERROR, LifecycleEventType.SYNC_FAILED]:
                    error_count += 1
                    health_score -= 20
                elif event.event_type == LifecycleEventType.SYNC_COMPLETED:
                    health_score += 5
                elif event.event_type == LifecycleEventType.STARTED:
                    health_score += 10
            
            health_score = max(0, min(100, health_score))
            
            return {
                "twin_id": twin_id,
                "current_status": status.current_status.value if status else "unknown",
                "health_score": health_score,
                "error_count": error_count,
                "recent_events": [event.dict() for event in recent_events],
                "last_updated": status.last_updated.isoformat() if status else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get health for twin {twin_id}: {e}")
            raise 