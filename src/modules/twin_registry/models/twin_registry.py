"""
Twin Registry Model

Updated to match our new comprehensive database schema with all 53 fields.
Supports both extraction and generation workflows with full twin lifecycle management.
Pure async implementation for modern architecture.
"""

from src.engine.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import asyncio


class TwinRegistry(BaseModel):
    """Main twin registry model matching our new database schema - Pure async implementation"""
    
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
    dept_id: Optional[str] = None       # Department ID for complete traceability
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
    async def create_twin_registry(
        cls,
        twin_id: str,
        twin_name: str,
        registry_name: str,
        registry_type: str,
        workflow_source: str,
        user_id: str,
        org_id: str,
        dept_id: Optional[str] = None,
        **kwargs
    ) -> "TwinRegistry":
        """Create new twin registry entry asynchronously"""
        now = datetime.now(timezone.utc)
        # Simulate async operation
        await asyncio.sleep(0.001)
        return cls(
            registry_id=str(uuid.uuid4()),
            twin_id=twin_id,
            twin_name=twin_name,
            registry_name=registry_name,
            registry_type=registry_type,
            workflow_source=workflow_source,
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            created_at=now,
            updated_at=now,
            **kwargs
        )
    
    async def update_health_score(self, new_score: int) -> None:
        """Update overall health score asynchronously"""
        if 0 <= new_score <= 100:
            self.overall_health_score = new_score
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_lifecycle_status(self, new_status: str) -> None:
        """Update lifecycle status asynchronously"""
        valid_statuses = ['created', 'active', 'suspended', 'archived', 'retired']
        if new_status in valid_statuses:
            self.lifecycle_status = new_status
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_operational_status(self, new_status: str) -> None:
        """Update operational status asynchronously"""
        valid_statuses = ['running', 'stopped', 'paused', 'error', 'maintenance']
        if new_status in valid_statuses:
            self.operational_status = new_status
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_relationship(self, relationship: Dict[str, Any]) -> None:
        """Add a new relationship asynchronously"""
        if isinstance(relationship, dict):
            self.relationships.append(relationship)
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_dependency(self, dependency: Dict[str, Any]) -> None:
        """Add a new dependency asynchronously"""
        if isinstance(dependency, dict):
            self.dependencies.append(dependency)
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def add_instance(self, instance: Dict[str, Any]) -> None:
        """Add a new instance asynchronously"""
        if isinstance(instance, dict):
            self.instances.append(instance)
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_sync_status(self, status: str, error_message: Optional[str] = None) -> None:
        """Update synchronization status asynchronously"""
        valid_statuses = ['pending', 'in_progress', 'completed', 'failed', 'scheduled']
        if status in valid_statuses:
            self.sync_status = status
            if error_message:
                self.sync_error_message = error_message
            if status == 'failed':
                self.sync_error_count += 1
            self.updated_at = datetime.now(timezone.utc)
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return {
            'overall_health_score': self.overall_health_score,
            'health_status': self.health_status,
            'performance_score': self.performance_score,
            'data_quality_score': self.data_quality_score,
            'reliability_score': self.reliability_score,
            'compliance_score': self.compliance_score,
            'sync_status': self.sync_status,
            'operational_status': self.operational_status,
            'lifecycle_status': self.lifecycle_status
        }
    
    async def is_healthy(self) -> bool:
        """Check if twin is healthy asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return (
            self.overall_health_score >= 80 and
            self.health_status in ['healthy', 'warning'] and
            self.sync_status != 'failed' and
            self.operational_status != 'error'
        )
    
    async def requires_maintenance(self) -> bool:
        """Check if twin requires maintenance asynchronously"""
        # Simulate async operation
        await asyncio.sleep(0.001)
        return (
            self.overall_health_score < 50 or
            self.health_status == 'critical' or
            self.sync_error_count > 5 or
            self.operational_status == 'maintenance'
        )
    
    async def validate(self) -> bool:
        """Validate twin registry data asynchronously"""
        # Simulate async validation
        await asyncio.sleep(0.001)
        return (
            bool(self.registry_id) and
            bool(self.twin_id) and
            bool(self.twin_name) and
            bool(self.registry_name) and
            bool(self.registry_type) and
            bool(self.workflow_source) and
            bool(self.user_id) and
            bool(self.org_id)
        )


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
    dept_id: Optional[str] = None  # Added dept_id for complete traceability
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    async def validate(self) -> bool:
        """Validate query parameters asynchronously"""
        # Simulate async validation
        await asyncio.sleep(0.001)
        return True


class TwinRegistrySummary(BaseModel):
    """Summary model for registry statistics"""
    
    total_registries: int
    active_registries: int
    registries_by_type: Dict[str, int]
    registries_by_workflow: Dict[str, int]
    registries_by_category: Dict[str, int]
    registries_by_status: Dict[str, int]
    registries_by_department: Dict[str, int]  # Added department breakdown
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    async def calculate_totals(self) -> None:
        """Calculate totals asynchronously"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        self.total_registries = sum(self.registries_by_type.values())
        self.active_registries = sum(
            count for status, count in self.registries_by_status.items() 
            if status in ['active', 'running']
        )


# Keep backward compatibility for existing code
TwinRegistryMetadata = TwinRegistry 