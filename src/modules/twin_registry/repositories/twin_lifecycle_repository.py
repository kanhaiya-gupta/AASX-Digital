"""
Twin Lifecycle Repository

Data access layer for twin lifecycle management using JSON fields.
Updated for Phase 2: JSON field operations instead of separate tables.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

from src.engine.database.connection_manager import ConnectionManager
from ..models.twin_lifecycle import TwinLifecycleEvent, TwinLifecycleStatus, TwinLifecycleSummary, LifecycleStatusEnum

logger = logging.getLogger(__name__)


class TwinLifecycleRepository:
    """Repository for managing twin lifecycle using JSON fields."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the twin lifecycle repository with engine connection manager."""
        self.connection_manager = connection_manager
        self.table_name = "twin_registry"
        logger.info("Twin Lifecycle Repository initialized (JSON field mode)")
    
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
        logger.info("Twin Lifecycle Repository initialized (JSON field mode)")
    
    async def create_event(self, registry_id: str, event: TwinLifecycleEvent) -> TwinLifecycleEvent:
        """Create a new lifecycle event by adding to the JSON field."""
        try:
            # Get current lifecycle events from metrics table
            current_events = await self._get_lifecycle_events_json(registry_id)
            
            # Add new event
            event_dict = {
                "event_id": event.event_id,
                "twin_id": event.twin_id,
                "event_type": event.event_type.value,
                "event_data": event.event_data or {},
                "event_metadata": event.event_metadata or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "triggered_by": event.triggered_by,
                "status": event.status,
                "error_message": event.error_message
            }
            
            current_events.append(event_dict)
            
            # Update the JSON field in metrics table
            query = """
            UPDATE twin_registry_metrics 
            SET lifecycle_events = :lifecycle_events, timestamp = CURRENT_TIMESTAMP
            WHERE registry_id = :registry_id
            """
            await self.connection_manager.execute_update(query, {"lifecycle_events": json.dumps(current_events), "registry_id": registry_id})
            
            # Also update the lifecycle status in main registry table
            await self._update_lifecycle_status(registry_id, event.event_type.value, event.status)
            
            logger.info(f"Created lifecycle event {event.event_id} in registry {registry_id}")
            return event
            
        except Exception as e:
            logger.error(f"Failed to create lifecycle event: {e}")
            raise
    
    async def get_event(self, registry_id: str, event_id: str) -> Optional[TwinLifecycleEvent]:
        """Get a lifecycle event by ID from the JSON field."""
        try:
            events = await self._get_lifecycle_events_json(registry_id)
            
            for event in events:
                if event.get("event_id") == event_id:
                    return self._dict_to_event(event)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle event {event_id}: {e}")
            return None
    
    async def get_events_by_twin(self, registry_id: str, twin_id: str, query: Optional[TwinLifecycleEvent] = None) -> List[TwinLifecycleEvent]:
        """Get all lifecycle events for a twin from the JSON field."""
        try:
            events = await self._get_lifecycle_events_json(registry_id)
            filtered_events = []
            
            for event in events:
                if event.get("twin_id") == twin_id:
                    # Apply filters if query provided
                    if query:
                        if query.event_type and event.get("event_type") != query.event_type.value:
                            continue
                        if query.status and event.get("status") != query.status:
                            continue
                        if query.triggered_by and event.get("triggered_by") != query.triggered_by:
                            continue
                        if query.timestamp_after:
                            event_timestamp = datetime.fromisoformat(event.get("timestamp", ""))
                            if event_timestamp < query.timestamp_after:
                                continue
                        if query.timestamp_before:
                            event_timestamp = datetime.fromisoformat(event.get("timestamp", ""))
                            if event_timestamp > query.timestamp_before:
                                continue
                    
                    filtered_events.append(event)
            
            # Sort by timestamp descending
            filtered_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return [self._dict_to_event(event) for event in filtered_events]
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle events for twin {twin_id}: {e}")
            return []
    
    async def get_lifecycle_status(self, registry_id: str) -> Optional[TwinLifecycleStatus]:
        """Get the current lifecycle status from the registry."""
        try:
            query = """
            SELECT lifecycle_status, lifecycle_phase, updated_at 
            FROM twin_registry 
            WHERE registry_id = :registry_id
            """
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                row = result[0]
                return TwinLifecycleStatus(
                    twin_id=registry_id,
                    lifecycle_status=row['lifecycle_status'],
                    lifecycle_phase=row['lifecycle_phase'],
                    last_updated=row['updated_at']
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle status for registry {registry_id}: {e}")
            return None
    
    async def update_lifecycle_status(self, registry_id: str, status: LifecycleStatusEnum, phase: str = None) -> bool:
        """Update the lifecycle status in the registry."""
        try:
            set_clauses = ["lifecycle_status = :lifecycle_status", "updated_at = CURRENT_TIMESTAMP"]
            params = {"lifecycle_status": status.value}
            
            if phase:
                set_clauses.append("lifecycle_phase = :lifecycle_phase")
                params["lifecycle_phase"] = phase
            
            params["registry_id"] = registry_id
            
            query = f"""
            UPDATE twin_registry 
            SET {', '.join(set_clauses)}
            WHERE registry_id = :registry_id
            """
            
            await self.connection_manager.execute_update(query, params)
            logger.info(f"Updated lifecycle status to {status.value} for registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update lifecycle status: {e}")
            return False
    
    async def get_lifecycle_summary(self, registry_id: str) -> TwinLifecycleSummary:
        """Get lifecycle statistics from the JSON fields."""
        try:
            events = await self._get_lifecycle_events_json(registry_id)
            status = await self.get_lifecycle_status(registry_id)
            
            total_events = len(events)
            
            # Count by type
            events_by_type = {}
            for event in events:
                event_type = event.get("event_type", "unknown")
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
            # Count by status
            events_by_status = {}
            for event in events:
                event_status = event.get("status", "unknown")
                events_by_status[event_status] = events_by_status.get(event_status, 0) + 1
            
            # Get recent events (last 10)
            recent_events = sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
            recent_events = [self._dict_to_event(event) for event in recent_events]
            
            # Status distribution (from main registry)
            status_distribution = {}
            if status:
                status_distribution[status.current_status.value] = 1
            
            return TwinLifecycleSummary(
                total_events=total_events,
                events_by_type=events_by_type,
                events_by_status=events_by_status,
                recent_events=recent_events,
                status_distribution=status_distribution
            )
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle summary: {e}")
            return TwinLifecycleSummary(
                total_events=0,
                events_by_type={},
                events_by_status={},
                recent_events=[],
                status_distribution={}
            )
    
    async def _get_lifecycle_events_json(self, registry_id: str) -> List[Dict[str, Any]]:
        """Get the lifecycle_events JSON field from the metrics table."""
        query = "SELECT lifecycle_events FROM twin_registry_metrics WHERE registry_id = :registry_id"
        result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
        
        if result and result[0].get("lifecycle_events"):
            try:
                return json.loads(result[0]["lifecycle_events"])
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in lifecycle_events field for registry {registry_id}")
                return []
        
        return []
    
    async def _update_lifecycle_status(self, registry_id: str, event_type: str, event_status: str) -> None:
        """Update lifecycle status based on event type."""
        try:
            # Map event types to lifecycle phases
            phase_mapping = {
                "created": "development",
                "started": "testing",
                "activated": "production",
                "suspended": "maintenance",
                "archived": "sunset"
            }
            
            new_phase = phase_mapping.get(event_type, "development")
            
            # Update the registry
            query = """
            UPDATE twin_registry 
            SET lifecycle_status = :event_status, lifecycle_phase = :new_phase, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = :registry_id
            """
            await self.connection_manager.execute_update(query, {"event_status": event_status, "new_phase": new_phase, "registry_id": registry_id})
            
        except Exception as e:
            logger.error(f"Failed to update lifecycle status: {e}")
    
    def _dict_to_event(self, event_dict: Dict[str, Any]) -> TwinLifecycleEvent:
        """Convert dictionary to TwinLifecycleEvent object."""
        return TwinLifecycleEvent(
            event_id=event_dict.get("event_id"),
            twin_id=event_dict.get("twin_id"),
            event_type=TwinLifecycleEvent.LifecycleEventType(event_dict.get("event_type", "created")),
            event_data=event_dict.get("event_data", {}),
            event_metadata=event_dict.get("event_metadata", {}),
            timestamp=datetime.fromisoformat(event_dict.get("timestamp", "")),
            triggered_by=event_dict.get("triggered_by"),
            status=event_dict.get("status", "completed"),
            error_message=event_dict.get("error_message")
        )
    
    async def execute_query(self, query: str, params: dict = None) -> List[Dict[str, Any]]:
        """Execute a query using the connection manager."""
        try:
            if query.strip().upper().startswith('SELECT'):
                return await self.connection_manager.execute_query(query, params or {})
            else:
                await self.connection_manager.execute_update(query, params or {})
                return []
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise
    
    async def fetch_one(self, query: str, params: dict = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row using the connection manager."""
        try:
            result = await self.connection_manager.execute_query(query, params or {})
            return result[0] if result and len(result) > 0 else None
        except Exception as e:
            logger.error(f"Failed to fetch one: {e}")
            return None 