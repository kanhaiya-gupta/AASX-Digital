"""
Twin Registry Service

Main service for orchestrating twin registry operations.
Provides high-level interface for twin lifecycle management.
"""

from src.shared.services.base_service import BaseService
from src.shared.services.digital_twin_service import DigitalTwinService
from ..repositories.twin_relationship_repository import TwinRelationshipRepository
from ..repositories.twin_instance_repository import TwinInstanceRepository
from ..repositories.twin_lifecycle_repository import TwinLifecycleRepository
from ..repositories.twin_registry_repository import TwinRegistryRepository
from ..models.twin_relationship import TwinRelationship, TwinRelationshipQuery
from ..models.twin_instance import TwinInstance, TwinInstanceQuery
from ..models.twin_lifecycle import TwinLifecycleEvent, LifecycleEventType, LifecycleStatus
from ..models.twin_registry import TwinRegistryMetadata, TwinRegistryQuery
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TwinRegistryService(BaseService):
    """Main service for twin registry operations"""
    
    def __init__(self):
        super().__init__()
        # Initialize repositories
        self.relationship_repo = TwinRelationshipRepository()
        self.instance_repo = TwinInstanceRepository()
        self.lifecycle_repo = TwinLifecycleRepository()
        self.registry_repo = TwinRegistryRepository()
        
        # Initialize shared services
        self.digital_twin_service = DigitalTwinService()
    
    async def initialize(self) -> None:
        """Initialize the service and create necessary tables"""
        try:
            await self.relationship_repo.create_table()
            await self.instance_repo.create_table()
            await self.lifecycle_repo.create_table()
            await self.registry_repo.create_table()
            logger.info("Twin Registry Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Registry Service: {e}")
            raise
    
    # ==================== Twin Registration ====================
    
    async def register_twin(self, twin_id: str, registry_name: str, registry_type: str = "aasx") -> TwinRegistryMetadata:
        """Register a twin in the registry"""
        try:
            # Verify twin exists
            twin = await self.digital_twin_service.get_digital_twin(twin_id)
            if not twin:
                raise ValueError(f"Twin {twin_id} not found")
            
            # Create registry metadata
            metadata = TwinRegistryMetadata.create_metadata(
                twin_id=twin_id,
                registry_name=registry_name,
                registry_type=registry_type
            )
            
            # Save to database
            await self.registry_repo.create_metadata(metadata)
            
            # Create initial lifecycle event
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.CREATED,
                event_data={"registry_name": registry_name, "registry_type": registry_type}
            )
            await self.lifecycle_repo.create_event(event)
            
            logger.info(f"Registered twin {twin_id} in registry")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to register twin {twin_id}: {e}")
            raise
    
    async def unregister_twin(self, twin_id: str) -> bool:
        """Unregister a twin from the registry"""
        try:
            # Create deletion event
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.DELETED
            )
            await self.lifecycle_repo.create_event(event)
            
            # Deactivate registry metadata
            metadata = await self.registry_repo.get_metadata_by_twin_id(twin_id)
            if metadata:
                metadata.deactivate()
                await self.registry_repo.update_metadata(metadata)
            
            logger.info(f"Unregistered twin {twin_id} from registry")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister twin {twin_id}: {e}")
            raise
    
    # ==================== Twin Lifecycle Management ====================
    
    async def start_twin(self, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Start a twin"""
        try:
            # Create start event
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.STARTED,
                triggered_by=triggered_by
            )
            await self.lifecycle_repo.create_event(event)
            
            # Update lifecycle status
            await self.lifecycle_repo.update_status(twin_id, LifecycleStatus.RUNNING, event)
            
            logger.info(f"Started twin {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start twin {twin_id}: {e}")
            raise
    
    async def stop_twin(self, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Stop a twin"""
        try:
            # Create stop event
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.STOPPED,
                triggered_by=triggered_by
            )
            await self.lifecycle_repo.create_event(event)
            
            # Update lifecycle status
            await self.lifecycle_repo.update_status(twin_id, LifecycleStatus.STOPPED, event)
            
            logger.info(f"Stopped twin {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop twin {twin_id}: {e}")
            raise
    
    async def sync_twin(self, twin_id: str, sync_data: Optional[Dict[str, Any]] = None, triggered_by: Optional[str] = None) -> bool:
        """Sync a twin"""
        try:
            # Create sync started event
            start_event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.SYNC_STARTED,
                event_data=sync_data,
                triggered_by=triggered_by
            )
            start_event.mark_in_progress()
            await self.lifecycle_repo.create_event(start_event)
            
            # Update lifecycle status
            await self.lifecycle_repo.update_status(twin_id, LifecycleStatus.SYNCING, start_event)
            
            # TODO: Implement actual sync logic here
            # For now, just mark as completed
            
            # Create sync completed event
            complete_event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.SYNC_COMPLETED,
                event_data=sync_data,
                triggered_by=triggered_by
            )
            await self.lifecycle_repo.create_event(complete_event)
            
            # Update lifecycle status back to running
            await self.lifecycle_repo.update_status(twin_id, LifecycleStatus.RUNNING, complete_event)
            
            logger.info(f"Synced twin {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync twin {twin_id}: {e}")
            # Create sync failed event
            failed_event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.SYNC_FAILED,
                event_data=sync_data,
                triggered_by=triggered_by
            )
            failed_event.mark_failed(str(e))
            await self.lifecycle_repo.create_event(failed_event)
            await self.lifecycle_repo.update_status(twin_id, LifecycleStatus.ERROR, failed_event)
            raise
    
    # ==================== Twin Relationships ====================
    
    async def create_relationship(
        self, 
        source_twin_id: str, 
        target_twin_id: str, 
        relationship_type: str,
        relationship_data: Optional[Dict[str, Any]] = None
    ) -> TwinRelationship:
        """Create a relationship between twins"""
        try:
            # Verify both twins exist
            source_twin = await self.digital_twin_service.get_digital_twin(source_twin_id)
            target_twin = await self.digital_twin_service.get_digital_twin(target_twin_id)
            
            if not source_twin:
                raise ValueError(f"Source twin {source_twin_id} not found")
            if not target_twin:
                raise ValueError(f"Target twin {target_twin_id} not found")
            
            # Create relationship
            relationship = TwinRelationship.create_relationship(
                source_twin_id=source_twin_id,
                target_twin_id=target_twin_id,
                relationship_type=relationship_type,
                relationship_data=relationship_data
            )
            
            # Save to database
            await self.relationship_repo.create_relationship(relationship)
            
            logger.info(f"Created relationship {relationship.relationship_id} between {source_twin_id} and {target_twin_id}")
            return relationship
            
        except Exception as e:
            logger.error(f"Failed to create relationship between {source_twin_id} and {target_twin_id}: {e}")
            raise
    
    async def get_twin_relationships(self, twin_id: str, query: Optional[TwinRelationshipQuery] = None) -> List[TwinRelationship]:
        """Get all relationships for a twin"""
        try:
            return await self.relationship_repo.get_relationships_by_twin(twin_id, query)
        except Exception as e:
            logger.error(f"Failed to get relationships for twin {twin_id}: {e}")
            raise
    
    # ==================== Twin Instances ====================
    
    async def create_instance(
        self,
        twin_id: str,
        instance_data: Dict[str, Any],
        instance_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> TwinInstance:
        """Create a new instance of a twin"""
        try:
            # Verify twin exists
            twin = await self.digital_twin_service.get_digital_twin(twin_id)
            if not twin:
                raise ValueError(f"Twin {twin_id} not found")
            
            # Create instance
            instance = TwinInstance.create_instance(
                twin_id=twin_id,
                instance_data=instance_data,
                instance_metadata=instance_metadata,
                created_by=created_by
            )
            
            # Save to database
            await self.instance_repo.create_instance(instance)
            
            logger.info(f"Created instance {instance.instance_id} for twin {twin_id}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create instance for twin {twin_id}: {e}")
            raise
    
    async def get_twin_instances(self, twin_id: str, query: Optional[TwinInstanceQuery] = None) -> List[TwinInstance]:
        """Get all instances of a twin"""
        try:
            return await self.instance_repo.get_instances_by_twin(twin_id, query)
        except Exception as e:
            logger.error(f"Failed to get instances for twin {twin_id}: {e}")
            raise
    
    # ==================== Registry Queries ====================
    
    async def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive registry summary"""
        try:
            # Get basic twin count
            twins = await self.digital_twin_service.get_all_digital_twins()
            total_twins = len(twins)
            
            # Get relationship summary
            relationship_summary = await self.relationship_repo.get_relationship_summary()
            
            # Get lifecycle summary
            lifecycle_summary = await self.lifecycle_repo.get_lifecycle_summary()
            
            # Get instance summary
            instance_summary = await self.instance_repo.get_instance_summary()
            
            return {
                "total_twins": total_twins,
                "relationships": relationship_summary.dict(),
                "lifecycle": lifecycle_summary.dict(),
                "instances": instance_summary.dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to get registry summary: {e}")
            raise
    
    async def search_twins(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search twins in the registry"""
        try:
            # Get all twins
            twins = await self.digital_twin_service.get_all_digital_twins()
            
            # Simple text search (can be enhanced with proper search engine)
            results = []
            query_lower = query.lower()
            
            for twin in twins:
                twin_dict = twin.dict()
                if (query_lower in twin_dict.get('name', '').lower() or
                    query_lower in twin_dict.get('description', '').lower() or
                    query_lower in twin_dict.get('twin_id', '').lower()):
                    results.append(twin_dict)
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search twins: {e}")
            raise 