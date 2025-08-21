"""
Twin Registry Model

Updated to match our new comprehensive database schema with all 53 fields.
Supports both extraction and generation workflows with full twin lifecycle management.
"""

from src.shared.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid


class TwinRegistry(BaseModel):
    """Main twin registry model matching our new database schema"""
    
    # Primary Identification
    registry_id: str
    twin_id: str
    twin_name: str
    registry_name: str
    
    # Twin Classification & Metadata
    twin_category: str = "generic"  # manufacturing, energy, component, facility, process, generic
    twin_type: str = "physical"     # physical, virtual, hybrid, composite
    twin_priority: str = "normal"   # low, normal, high, critical, emergency
    twin_version: str = "1.0.0"    # Semantic versioning
    
    # Workflow Classification
    registry_type: str              # extraction, generation, hybrid
    workflow_source: str            # aasx_file, structured_data, both
    
    # Module Integration References
    aasx_integration_id: Optional[str] = None
    physics_modeling_id: Optional[str] = None
    federated_learning_id: Optional[str] = None
    data_pipeline_id: Optional[str] = None
    kg_neo4j_id: Optional[str] = None
    certificate_manager_id: Optional[str] = None
    
    # Integration Status & Health
    integration_status: str = "pending"  # pending, active, inactive, error, maintenance, deprecated
    overall_health_score: int = 0        # 0-100 health score
    health_status: str = "unknown"       # unknown, healthy, warning, critical, offline
    
    # Lifecycle Management
    lifecycle_status: str = "created"    # created, active, suspended, archived, retired
    lifecycle_phase: str = "development" # development, testing, production, maintenance, sunset
    
    # Operational Status
    operational_status: str = "stopped"  # running, stopped, paused, error, maintenance
    availability_status: str = "offline" # online, offline, degraded, maintenance
    
    # Synchronization & Data Management
    sync_status: str = "pending"         # pending, in_progress, completed, failed, scheduled
    sync_frequency: str = "daily"        # real_time, hourly, daily, weekly, manual
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None
    sync_error_count: int = 0
    sync_error_message: Optional[str] = None
    
    # Performance & Quality Metrics
    performance_score: float = 0.0       # 0.0-1.0 performance rating
    data_quality_score: float = 0.0     # 0.0-1.0 data quality rating
    reliability_score: float = 0.0      # 0.0-1.0 reliability rating
    compliance_score: float = 0.0       # 0.0-1.0 compliance rating
    
    # Security & Access Control
    security_level: str = "standard"     # public, internal, confidential, secret, top_secret
    access_control_level: str = "user"   # public, user, admin, system, restricted
    encryption_enabled: bool = False
    audit_logging_enabled: bool = True
    
    # User Management & Ownership
    user_id: str
    org_id: str
    owner_team: Optional[str] = None
    steward_user_id: Optional[str] = None
    
    # Timestamps & Audit
    created_at: datetime
    updated_at: datetime
    activated_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    last_modified_at: Optional[datetime] = None
    
    # Configuration & Metadata (JSON fields)
    registry_config: Dict[str, Any] = {}
    registry_metadata: Dict[str, Any] = {}
    custom_attributes: Dict[str, Any] = {}
    tags: List[str] = []
    
    # Relationships & Dependencies (JSON arrays)
    relationships: List[Dict[str, Any]] = []
    dependencies: List[Dict[str, Any]] = []
    instances: List[Dict[str, Any]] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create_registry(
        cls,
        twin_id: str,
        twin_name: str,
        registry_name: str,
        registry_type: str,
        workflow_source: str,
        user_id: str,
        org_id: str,
        **kwargs
    ) -> "TwinRegistry":
        """Create new twin registry entry"""
        now = datetime.now(timezone.utc)
        return cls(
            registry_id=str(uuid.uuid4()),
            twin_id=twin_id,
            twin_name=twin_name,
            registry_name=registry_name,
            registry_type=registry_type,
            workflow_source=workflow_source,
            user_id=user_id,
            org_id=org_id,
            created_at=now,
            updated_at=now,
            **kwargs
        )
    
    def update_status(self, new_status: str, status_type: str = "integration") -> None:
        """Update various status fields"""
        if status_type == "integration":
            self.integration_status = new_status
        elif status_type == "health":
            self.health_status = new_status
        elif status_type == "lifecycle":
            self.lifecycle_status = new_status
        elif status_type == "operational":
            self.operational_status = new_status
        elif status_type == "sync":
            self.sync_status = new_status
        
        self.updated_at = datetime.now(timezone.utc)
        self.last_modified_at = datetime.now(timezone.utc)
    
    def update_health_score(self, new_score: int) -> None:
        """Update overall health score"""
        if 0 <= new_score <= 100:
            self.overall_health_score = new_score
            self.updated_at = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the twin"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the twin"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now(timezone.utc)
    
    def add_relationship(self, relationship: Dict[str, Any]) -> None:
        """Add a relationship"""
        self.relationships.append(relationship)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_instance(self, instance: Dict[str, Any]) -> None:
        """Add an instance"""
        self.instances.append(instance)
        self.updated_at = datetime.now(timezone.utc)


class TwinRegistryQuery(BaseModel):
    """Query model for filtering twin registry entries"""
    
    twin_id: Optional[str] = None
    twin_name: Optional[str] = None
    registry_type: Optional[str] = None
    workflow_source: Optional[str] = None
    twin_category: Optional[str] = None
    integration_status: Optional[str] = None
    health_status: Optional[str] = None
    lifecycle_status: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TwinRegistrySummary(BaseModel):
    """Summary model for registry statistics"""
    
    total_registries: int
    active_registries: int
    registries_by_type: Dict[str, int]
    registries_by_workflow: Dict[str, int]
    registries_by_category: Dict[str, int]
    registries_by_status: Dict[str, int]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Keep backward compatibility for existing code
TwinRegistryMetadata = TwinRegistry 