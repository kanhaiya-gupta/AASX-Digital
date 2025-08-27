"""
Twin Lifecycle Service

Service for managing twin lifecycle events and status.
Updated for Phase 2: JSON field operations instead of separate tables.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.database_factory import DatabaseFactory, DatabaseType
from ..models.twin_lifecycle import (
    TwinLifecycleEvent, 
    TwinLifecycleStatus, 
    LifecycleEventType,
    LifecycleStatusEnum,
    TwinLifecycleQuery,
    TwinLifecycleSummary
)
from ..repositories.twin_lifecycle_repository import TwinLifecycleRepository

logger = logging.getLogger(__name__)


class TwinLifecycleService:
    """Service for managing twin lifecycle operations"""
    
    def __init__(self):
        """Initialize the twin lifecycle service"""
        # Use the same database infrastructure as other modules
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        # Initialize central database connection
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        
        # Initialize repository with database connection
        self.lifecycle_repo = TwinLifecycleRepository(self.db_manager)
    
    async def initialize(self) -> None:
        """Initialize the service - no tables needed for JSON field approach"""
        try:
            # No table creation needed - all data stored in existing twin_registry tables
            logger.info("Twin Lifecycle Service initialized successfully (JSON field mode)")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Lifecycle Service: {e}")
            raise
    
    # ==================== Lifecycle Events ====================
    
    async def create_event(
        self,
        registry_id: str,
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
            
            await self.lifecycle_repo.create_event(registry_id, event)
            logger.info(f"Created lifecycle event {event.event_id} for twin {twin_id} in registry {registry_id}")
            return event
            
        except Exception as e:
            logger.error(f"Failed to create lifecycle event for twin {twin_id}: {e}")
            raise
    
    async def get_events(
        self,
        registry_id: str,
        twin_id: Optional[str] = None,
        query: Optional[TwinLifecycleQuery] = None
    ) -> List[TwinLifecycleEvent]:
        """Get lifecycle events with optional filtering"""
        try:
            if twin_id:
                return await self.lifecycle_repo.get_events_by_twin(registry_id, twin_id, query)
            else:
                # For now, return empty list if no twin_id specified
                # Could be enhanced to get all events across registries
                return []
        except Exception as e:
            logger.error(f"Failed to get lifecycle events: {e}")
            raise
    
    async def get_recent_events(self, registry_id: str, twin_id: str, limit: int = 10) -> List[TwinLifecycleEvent]:
        """Get recent lifecycle events for a twin"""
        try:
            events = await self.lifecycle_repo.get_events_by_twin(registry_id, twin_id)
            return events[:limit]
        except Exception as e:
            logger.error(f"Failed to get recent events for twin {twin_id}: {e}")
            raise
    
    # ==================== Lifecycle Status ====================
    
    async def get_status(self, registry_id: str) -> Optional[TwinLifecycleStatus]:
        """Get current lifecycle status for a registry"""
        try:
            return await self.lifecycle_repo.get_lifecycle_status(registry_id)
        except Exception as e:
            logger.error(f"Failed to get status for registry {registry_id}: {e}")
            raise
    
    async def update_status(
        self,
        registry_id: str,
        new_status: LifecycleStatusEnum,
        phase: Optional[str] = None
    ) -> bool:
        """Update lifecycle status for a registry"""
        try:
            return await self.lifecycle_repo.update_lifecycle_status(registry_id, new_status, phase)
        except Exception as e:
            logger.error(f"Failed to update status for registry {registry_id}: {e}")
            raise
    
    # ==================== Lifecycle Operations ====================
    
    async def start_twin(self, registry_id: str, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Start a twin and update lifecycle"""
        try:
            # Create start event
            event = await self.create_event(
                registry_id=registry_id,
                twin_id=twin_id,
                event_type=LifecycleEventType.STARTED,
                triggered_by=triggered_by
            )
            
            # Update lifecycle status
            await self.update_status(registry_id, LifecycleStatusEnum.RUNNING, "production")
            
            logger.info(f"Started twin {twin_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start twin {twin_id}: {e}")
            raise
    
    async def stop_twin(self, registry_id: str, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Stop a twin and update lifecycle"""
        try:
            # Create stop event
            event = await self.create_event(
                registry_id=registry_id,
                twin_id=twin_id,
                event_type=LifecycleEventType.STOPPED,
                triggered_by=triggered_by
            )
            
            # Update lifecycle status
            await self.update_status(registry_id, LifecycleStatusEnum.STOPPED, "maintenance")
            
            logger.info(f"Stopped twin {twin_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop twin {twin_id}: {e}")
            raise
    
    async def activate_twin(self, registry_id: str, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Activate a twin and update lifecycle"""
        try:
            # Create activation event
            event = await self.create_event(
                registry_id=registry_id,
                twin_id=twin_id,
                event_type=LifecycleEventType.ACTIVATED,
                triggered_by=triggered_by
            )
            
            # Update lifecycle status
            await self.update_status(registry_id, LifecycleStatusEnum.ACTIVE, "production")
            
            logger.info(f"Activated twin {twin_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate twin {twin_id}: {e}")
            raise
    
    async def deactivate_twin(self, registry_id: str, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Deactivate a twin and update lifecycle"""
        try:
            # Create deactivation event
            event = await self.create_event(
                registry_id=registry_id,
                twin_id=twin_id,
                event_type=LifecycleEventType.DEACTIVATED,
                triggered_by=triggered_by
            )
            
            # Update lifecycle status
            await self.update_status(registry_id, LifecycleStatusEnum.INACTIVE, "maintenance")
            
            logger.info(f"Deactivated twin {twin_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate twin {twin_id}: {e}")
            raise
    
    async def archive_twin(self, registry_id: str, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Archive a twin and update lifecycle"""
        try:
            # Create archive event
            event = await self.create_event(
                registry_id=registry_id,
                twin_id=twin_id,
                event_type=LifecycleEventType.ARCHIVED,
                triggered_by=triggered_by
            )
            
            # Update lifecycle status
            await self.update_status(registry_id, LifecycleStatusEnum.ARCHIVED, "sunset")
            
            logger.info(f"Archived twin {twin_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive twin {twin_id}: {e}")
            raise
    
    # ==================== Lifecycle Analytics ====================
    
    async def get_lifecycle_summary(self, registry_id: str) -> TwinLifecycleSummary:
        """Get lifecycle summary for a registry"""
        try:
            return await self.lifecycle_repo.get_lifecycle_summary(registry_id)
        except Exception as e:
            logger.error(f"Failed to get lifecycle summary for registry {registry_id}: {e}")
            raise
    
    async def get_lifecycle_timeline(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinLifecycleEvent]:
        """Get lifecycle timeline for a twin"""
        try:
            events = await self.lifecycle_repo.get_events_by_twin(registry_id, twin_id)
            # Sort by timestamp and return most recent
            events.sort(key=lambda x: x.timestamp, reverse=True)
            return events[:limit]
        except Exception as e:
            logger.error(f"Failed to get lifecycle timeline for twin {twin_id}: {e}")
            raise 