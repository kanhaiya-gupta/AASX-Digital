"""
Knowledge Graph Registry Model

Updated to match our comprehensive database schema with all fields.
Supports both extraction and generation workflows with full graph lifecycle management.
"""

from src.engine.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid


class KGGraphRegistry(BaseModel):
    """Main knowledge graph registry model matching our new database schema"""
    
    # Primary Identification
    graph_id: str
    file_id: str
    graph_name: str
    registry_name: str
    
    # Graph Classification & Metadata
    graph_category: str = "generic"  # aasx, structured_data, hybrid, custom
    graph_type: str = "asset_graph"  # asset_graph, relationship_graph, process_graph, composite
    graph_priority: str = "normal"   # low, normal, high, critical
    graph_version: str = "1.0.0"    # Semantic versioning
    
    # Workflow Classification
    registry_type: str              # extraction, generation, hybrid
    workflow_source: str            # aasx_file, structured_data, ai_rag, both
    
    # Module Integration References
    aasx_integration_id: Optional[str] = None
    twin_registry_id: Optional[str] = None
    physics_modeling_id: Optional[str] = None
    federated_learning_id: Optional[str] = None
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
    
    # Neo4j-Specific Status (NEW for Knowledge Graph)
    neo4j_import_status: str = "pending"    # pending, in_progress, completed, failed, scheduled
    neo4j_export_status: str = "pending"    # pending, in_progress, completed, failed, scheduled
    last_neo4j_sync_at: Optional[datetime] = None
    next_neo4j_sync_at: Optional[datetime] = None
    neo4j_sync_error_count: int = 0
    neo4j_sync_error_message: Optional[str] = None
    
    # Graph Data Metrics (NEW for Knowledge Graph)
    total_nodes: int = 0
    total_relationships: int = 0
    graph_complexity: str = "simple"  # simple, moderate, complex, very_complex
    
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
    dept_id: Optional[str] = None
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
    graph_instances: List[Dict[str, Any]] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __init__(self, **data):
        # Generate graph_id if not provided
        if 'graph_id' not in data:
            data['graph_id'] = f"kg_{uuid.uuid4().hex[:8]}"
        
        # Set timestamps if not provided
        if 'created_at' not in data:
            data['created_at'] = datetime.now(timezone.utc)
        if 'updated_at' not in data:
            data['updated_at'] = datetime.now(timezone.utc)
        
        super().__init__(**data)
    
    async def update_health_score(self, new_score: int) -> None:
        """Update the overall health score asynchronously"""
        self.overall_health_score = max(0, min(100, new_score))
        self.updated_at = datetime.now(timezone.utc)
        
        # Update health status based on score
        if self.overall_health_score >= 80:
            self.health_status = "healthy"
        elif self.overall_health_score >= 60:
            self.health_status = "warning"
        elif self.overall_health_score >= 40:
            self.health_status = "critical"
        else:
            self.health_status = "offline"
    
    async def update_neo4j_status(self, import_status: str, export_status: str = None) -> None:
        """Update Neo4j synchronization status asynchronously"""
        self.neo4j_import_status = import_status
        if export_status:
            self.neo4j_export_status = export_status
        self.updated_at = datetime.now(timezone.utc)
    
    async def increment_sync_error(self, error_message: str) -> None:
        """Increment sync error count and update error message asynchronously"""
        self.neo4j_sync_error_count += 1
        self.neo4j_sync_error_message = error_message
        self.updated_at = datetime.now(timezone.utc)
    
    async def update_graph_metrics(self, nodes: int, relationships: int) -> None:
        """Update graph data metrics asynchronously"""
        self.total_nodes = nodes
        self.total_relationships = relationships
        
        # Update complexity based on size
        total_elements = nodes + relationships
        if total_elements < 100:
            self.graph_complexity = "simple"
        elif total_elements < 1000:
            self.graph_complexity = "moderate"
        elif total_elements < 10000:
            self.graph_complexity = "complex"
        else:
            self.graph_complexity = "very_complex"
        
        self.updated_at = datetime.now(timezone.utc)
    
    @classmethod
    async def create_from_aasx_file(
        cls,
        file_id: str,
        graph_name: str,
        user_id: str,
        org_id: str,
        dept_id: Optional[str] = None,
        **kwargs
    ) -> "KGGraphRegistry":
        """Create a new graph registry entry from AASX file asynchronously"""
        return cls(
            file_id=file_id,
            graph_name=graph_name,
            registry_name=f"{graph_name}_registry",
            registry_type="extraction",
            workflow_source="aasx_file",
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            **kwargs
        )
    
    @classmethod
    async def create_from_structured_data(
        cls,
        graph_name: str,
        user_id: str,
        org_id: str,
        dept_id: Optional[str] = None,
        **kwargs
    ) -> "KGGraphRegistry":
        """Create a new graph registry entry from structured data asynchronously"""
        return cls(
            file_id="",  # No file for structured data
            graph_name=graph_name,
            registry_name=f"{graph_name}_registry",
            registry_type="generation",
            workflow_source="structured_data",
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            **kwargs
        )
    
    @classmethod
    async def create_from_ai_rag(
        cls,
        graph_name: str,
        ai_rag_id: str,
        user_id: str,
        org_id: str,
        dept_id: Optional[str] = None,
        **kwargs
    ) -> "KGGraphRegistry":
        """Create a new graph registry entry from AI RAG system asynchronously"""
        return cls(
            file_id="",  # No file for AI RAG
            graph_name=graph_name,
            registry_name=f"{graph_name}_registry",
            registry_type="generation",
            workflow_source="ai_rag",
            ai_rag_integration_id=ai_rag_id,  # Link to AI RAG system
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            **kwargs
        )


# Query and Summary models for API responses
class KGGraphRegistryQuery(BaseModel):
    """Query model for filtering graph registry entries"""
    graph_category: Optional[str] = None
    graph_type: Optional[str] = None
    workflow_source: Optional[str] = None
    integration_status: Optional[str] = None
    health_status: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    limit: int = 100
    offset: int = 0


class KGGraphRegistrySummary(BaseModel):
    """Summary model for graph registry overview"""
    total_graphs: int
    active_graphs: int
    healthy_graphs: int
    total_nodes: int
    total_relationships: int
    graphs_by_category: Dict[str, int]
    graphs_by_status: Dict[str, int]
