"""
Knowledge Graph Registry Model

Comprehensive knowledge graph registry model matching the database schema.
Supports both extraction and generation workflows with full graph lifecycle management.
Enhanced with enterprise-grade computed fields and business intelligence methods.
"""

from src.engine.models.engine_base_model import EngineBaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import Field, ConfigDict, computed_field
import uuid
import asyncio


class KGGraphRegistry(EngineBaseModel):
    """
    Main knowledge graph registry model for comprehensive graph lifecycle management.
    
    This model represents the kg_graph_registry table with all fields from the database schema.
    Supports both extraction and generation workflows with ML training capabilities,
    Neo4j integration, and enterprise-grade features.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Primary Identification
    graph_id: str = Field(..., description="Unique graph identifier")
    file_id: str = Field(..., description="Reference to source file")
    graph_name: str = Field(..., description="Human-readable graph name")
    registry_name: str = Field(..., description="Registry instance name")
    
    # Graph Classification & Metadata
    graph_category: str = Field(default="generic", description="Graph category: aasx, structured_data, hybrid, custom")
    graph_type: str = Field(default="asset_graph", description="Graph type: asset_graph, relationship_graph, process_graph, composite")
    graph_priority: str = Field(default="normal", description="Graph priority: low, normal, high, critical")
    graph_version: str = Field(default="1.0.0", description="Semantic versioning for the graph")
    
    # Workflow Classification (CRITICAL for dual workflow support)
    registry_type: str = Field(..., description="Registry type: extraction, generation, hybrid")
    workflow_source: str = Field(default="aasx_file", description="Workflow source: aasx_file, structured_data, both")
    
    # ML Training Status (NEW for ML traceability)
    ml_training_enabled: bool = Field(default=False, description="Whether ML training is enabled for this graph")
    active_ml_sessions: int = Field(default=0, description="Number of active ML training sessions")
    total_models_trained: int = Field(default=0, description="Total number of models trained for this graph")
    ml_model_count: int = Field(default=0, description="Current number of ML models associated with this graph")
    
    # Schema Management (NEW for schema traceability)
    schema_version: str = Field(default="1.0.0", description="Current schema version")
    ontology_version: str = Field(default="1.0.0", description="Current ontology version")
    validation_rules_count: int = Field(default=0, description="Number of validation rules")
    schema_validation_status: str = Field(default="pending", description="Schema validation status: pending, validated, failed, outdated")
    
    # Data Quality Management (NEW for quality traceability)
    quality_rules_count: int = Field(default=0, description="Number of quality rules")
    validation_status: str = Field(default="pending", description="Validation status: pending, validated, failed, outdated")
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data completeness score (0.0-1.0)")
    data_quality_status: str = Field(default="unknown", description="Data quality status: unknown, excellent, good, fair, poor")
    
    # External Storage References (NEW for ML traceability - NO data storage)
    model_storage_path: Optional[str] = Field(default=None, description="Path to ML model storage (external)")
    dataset_storage_path: Optional[str] = Field(default=None, description="Path to dataset storage (external)")
    config_storage_path: Optional[str] = Field(default=None, description="Path to configuration storage (external)")
    schema_storage_path: Optional[str] = Field(
        default=None, 
        description="Path to schema storage (external)"
    )
    ontology_storage_path: Optional[str] = Field(
        default=None, 
        description="Path to ontology storage (external)"
    )
    
    # Module Integration References (Links to other modules - NO data duplication)
    aasx_integration_id: Optional[str] = Field(
        default=None, 
        description="Reference to aasx_processing table"
    )
    twin_registry_id: Optional[str] = Field(
        default=None, 
        description="Reference to twin_registry table"
    )
    physics_modeling_id: Optional[str] = Field(
        default=None, 
        description="Reference to physics_modeling table"
    )
    federated_learning_id: Optional[str] = Field(
        default=None, 
        description="Reference to federated_learning table"
    )
    ai_rag_id: Optional[str] = Field(
        default=None, 
        description="Reference to ai_rag_registry table"
    )
    certificate_manager_id: Optional[str] = Field(
        default=None, 
        description="Reference to certificate module"
    )
    
    # Integration Status & Health
    integration_status: str = Field(
        default="pending", 
        description="Integration status: pending, active, inactive, error, maintenance, deprecated"
    )
    overall_health_score: int = Field(
        default=0, 
        ge=0, 
        le=100, 
        description="Overall health score (0-100)"
    )
    health_status: str = Field(
        default="unknown", 
        description="Health status: unknown, healthy, warning, critical, offline"
    )
    
    # Lifecycle Management
    lifecycle_status: str = Field(
        default="created", 
        description="Lifecycle status: created, active, suspended, archived, retired"
    )
    lifecycle_phase: str = Field(
        default="development", 
        description="Lifecycle phase: development, testing, production, maintenance, sunset"
    )
    
    # Operational Status
    operational_status: str = Field(default="stopped", description="Operational status: running, stopped, paused, error, maintenance")
    availability_status: str = Field(default="offline", description="Availability status: online, offline, degraded, maintenance")
    
    # Neo4j-Specific Status (NEW for Knowledge Graph)
    neo4j_import_status: str = Field(default="pending", description="Neo4j import status: pending, in_progress, completed, failed, scheduled")
    neo4j_export_status: str = Field(default="pending", description="Neo4j export status: pending, in_progress, completed, failed, scheduled")
    last_neo4j_sync_at: Optional[datetime] = Field(default=None, description="Last Neo4j synchronization timestamp")
    next_neo4j_sync_at: Optional[datetime] = Field(default=None, description="Next scheduled Neo4j synchronization")
    neo4j_sync_error_count: int = Field(default=0, description="Count of consecutive Neo4j sync failures")
    neo4j_sync_error_message: Optional[str] = Field(default=None, description="Last Neo4j sync error message")
    
    # Graph Data Metrics (NEW for Knowledge Graph)
    total_nodes: int = Field(default=0, description="Total number of nodes in the graph")
    total_relationships: int = Field(default=0, description="Total number of relationships in the graph")
    graph_complexity: str = Field(default="simple", description="Graph complexity: simple, moderate, complex, very_complex")
    
    # Multiple Graph Support (CONSOLIDATED from multiple sources)
    graphs_json: Dict[str, Any] = Field(default={}, description="JSON object storing multiple graphs with unique IDs as keys")
    graph_count: int = Field(default=0, description="Total number of graphs stored in graphs_json")
    graph_types: Dict[str, Any] = Field(default={}, description="JSON object of graph types with counts")
    graph_sources: Dict[str, Any] = Field(default={}, description="JSON object of graph sources with counts")
    
    # Performance & Quality Metrics
    performance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Performance score (0.0-1.0)")
    data_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data quality score (0.0-1.0)")
    reliability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Reliability score (0.0-1.0)")
    
    # Security & Access Control
    security_level: str = Field(default="standard", description="Security level: public, internal, confidential, secret, top_secret")
    access_control_level: str = Field(default="user", description="Access control level: public, user, admin, system, restricted")
    encryption_enabled: bool = Field(default=False, description="Whether graph data is encrypted")
    audit_logging_enabled: bool = Field(default=True, description="Whether audit logging is enabled")
    
    # Enterprise Compliance & Security (Merged from enterprise tables)
    compliance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Compliance score (0.0-1.0)")
    security_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Security score (0.0-1.0)")
    overall_health_score: int = Field(default=0, ge=0, le=100, description="Overall health score (0-100)")
    risk_level: str = Field(default="low", description="Risk level: low, medium, high, critical")
    threat_level: str = Field(default="low", description="Threat level: low, medium, high, critical")
    security_status: str = Field(default="secure", description="Security status: secure, warning, compromised, unknown")
    compliance_status: str = Field(default="compliant", description="Compliance status: compliant, warning, non_compliant, unknown")
    last_security_scan: Optional[datetime] = Field(default=None, description="Last security scan timestamp")
    last_compliance_check: Optional[datetime] = Field(default=None, description="Last compliance check timestamp")
    security_incidents_count: int = Field(default=0, description="Number of security incidents")
    security_patches_count: int = Field(default=0, description="Number of security patches applied")
    security_vulnerabilities_count: int = Field(default=0, description="Number of known vulnerabilities")
    
    # Additional Enterprise Fields (Missing from schema)
    metric_type: str = Field(default="standard", description="Type of metric being tracked")
    metric_timestamp: Optional[datetime] = Field(default=None, description="Specific timestamp for the metric")
    compliance_type: str = Field(default="standard", description="Type of compliance being tracked")
    last_compliance_audit: Optional[datetime] = Field(default=None, description="Last compliance audit date")
    next_compliance_audit: Optional[datetime] = Field(default=None, description="Next scheduled compliance audit")
    compliance_audit_details: Dict[str, Any] = Field(default={}, description="JSON: detailed compliance audit information")
    compliance_rules_count: int = Field(default=0, description="Number of active compliance rules")
    compliance_violations_count: int = Field(default=0, description="Number of compliance violations")
    security_threat_level: str = Field(default="low", description="Security threat level: low, medium, high, critical")
    security_event_type: str = Field(default="none", description="Type of security event")
    threat_assessment: str = Field(default="low", description="Detailed threat assessment description")
    security_scan_details: Dict[str, Any] = Field(default={}, description="JSON: detailed security scan results")
    
    # User Management & Ownership
    user_id: str = Field(..., description="Current user who owns/accesses this graph")
    org_id: str = Field(..., description="Organization this graph belongs to")
    dept_id: Optional[str] = Field(default=None, description="Department for complete traceability")
    owner_team: Optional[str] = Field(default=None, description="Team responsible for this graph")
    steward_user_id: Optional[str] = Field(default=None, description="Data steward for this graph")
    
    # Timestamps & Audit
    created_at: datetime = Field(..., description="When the graph was created")
    updated_at: datetime = Field(..., description="When the graph was last updated")
    activated_at: Optional[datetime] = Field(default=None, description="When graph was first activated")
    last_accessed_at: Optional[datetime] = Field(default=None, description="Last time any user accessed this graph")
    last_modified_at: Optional[datetime] = Field(default=None, description="Last time graph data was modified")
    
    # Configuration & Metadata (JSON fields for flexibility)
    registry_config: Dict[str, Any] = Field(default={}, description="Registry configuration settings")
    registry_metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    custom_attributes: Dict[str, Any] = Field(default={}, description="User-defined custom attributes")
    tags: List[str] = Field(default=[], description="List of tags for categorization")
    
    # Relationships & Dependencies (JSON objects)
    relationships: List[Dict[str, Any]] = Field(default=[], description="List of relationship objects")
    dependencies: List[Dict[str, Any]] = Field(default=[], description="List of dependency objects")
    graph_instances: List[Dict[str, Any]] = Field(default=[], description="List of graph instance objects")

    # Computed Fields for Business Intelligence
    @computed_field
    def overall_score(self) -> float:
        """Calculate overall composite score from all metrics"""
        scores = [
            self.performance_score,
            self.data_quality_score,
            self.reliability_score,
            self.compliance_score,
            self.completeness_score
        ]
        return sum(scores) / len(scores) if scores else 0.0

    @computed_field
    def enterprise_health_status(self) -> str:
        """Determine enterprise health status based on multiple factors"""
        if self.overall_health_score >= 80 and self.overall_score >= 0.8:
            return "excellent"
        elif self.overall_health_score >= 60 and self.overall_score >= 0.6:
            return "good"
        elif self.overall_health_score >= 40 and self.overall_score >= 0.4:
            return "fair"
        else:
            return "poor"

    @computed_field
    def risk_assessment(self) -> str:
        """Assess overall risk level based on multiple factors"""
        risk_factors = []
        if self.security_threat_level in ["high", "critical"]:
            risk_factors.append("security")
        if self.compliance_score < 0.7:
            risk_factors.append("compliance")
        if self.neo4j_sync_error_count > 5:
            risk_factors.append("sync_errors")
        if self.overall_health_score < 50:
            risk_factors.append("health")
        
        if not risk_factors:
            return "low"
        elif len(risk_factors) <= 2:
            return "medium"
        else:
            return "high"

    @computed_field
    def graph_complexity_score(self) -> float:
        """Calculate graph complexity score based on size and structure"""
        base_score = min(1.0, (self.total_nodes + self.total_relationships) / 10000)
        if self.graph_complexity == "very_complex":
            return min(1.0, base_score * 1.5)
        elif self.graph_complexity == "complex":
            return min(1.0, base_score * 1.2)
        elif self.graph_complexity == "moderate":
            return min(1.0, base_score * 1.0)
        else:
            return min(1.0, base_score * 0.8)

    @computed_field
    def ml_maturity_score(self) -> float:
        """Calculate ML maturity score based on training capabilities"""
        if not self.ml_training_enabled:
            return 0.0
        
        scores = []
        if self.active_ml_sessions > 0:
            scores.append(0.3)
        if self.total_models_trained > 0:
            scores.append(0.3)
        if self.ml_model_count > 0:
            scores.append(0.2)
        if self.schema_validation_status == "validated":
            scores.append(0.2)
        
        return sum(scores) if scores else 0.0

    @computed_field
    def optimization_priority(self) -> str:
        """Determine optimization priority based on performance and health"""
        if self.overall_score < 0.5 or self.overall_health_score < 40:
            return "critical"
        elif self.overall_score < 0.7 or self.overall_health_score < 60:
            return "high"
        elif self.overall_score < 0.8 or self.overall_health_score < 80:
            return "medium"
        else:
            return "low"

    @computed_field
    def maintenance_schedule(self) -> str:
        """Determine maintenance schedule based on health and performance"""
        if self.health_status in ["critical", "warning"] or self.overall_health_score < 30:
            return "immediate"
        elif self.overall_health_score < 60 or self.neo4j_sync_error_count > 3:
            return "scheduled"
        else:
            return "routine"

    @computed_field
    def graph_maturity_score(self) -> float:
        """Calculate graph maturity score based on lifecycle and operational status"""
        maturity_factors = {
            'development': 0.2, 'testing': 0.4, 'production': 0.7,
            'maintenance': 0.8, 'sunset': 0.3
        }
        return maturity_factors.get(self.lifecycle_phase, 0.0)

    @computed_field
    def integration_maturity_score(self) -> float:
        """Calculate integration maturity score based on connected modules"""
        integrations = [
            self.aasx_integration_id,
            self.twin_registry_id,
            self.physics_modeling_id,
            self.federated_learning_id,
            self.ai_rag_id,
            self.certificate_manager_id
        ]
        active_integrations = sum(1 for i in integrations if i is not None)
        return (active_integrations / len(integrations)) * 100

    @computed_field
    def data_quality_assessment(self) -> str:
        """Assess data quality based on completeness and validation scores"""
        if self.completeness_score >= 0.9 and self.validation_status == "validated":
            return "excellent"
        elif self.completeness_score >= 0.7 and self.validation_status == "validated":
            return "good"
        elif self.completeness_score >= 0.5:
            return "fair"
        else:
            return "poor"

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
    
    # Asynchronous Enterprise Methods for Business Intelligence
    async def update_enterprise_metrics(self) -> None:
        """Update enterprise metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        self.metric_timestamp = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    async def update_compliance_status(self) -> None:
        """Update compliance status asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        if self.compliance_score >= 0.9:
            self.compliance_status = "compliant"
        elif self.compliance_score >= 0.7:
            self.compliance_status = "requires_review"
        else:
            self.compliance_status = "non_compliant"
        self.updated_at = datetime.now(timezone.utc)

    async def update_security_status(self) -> None:
        """Update security status asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        if self.security_score >= 0.9:
            self.security_threat_level = "low"
        elif self.security_score >= 0.7:
            self.security_threat_level = "medium"
        elif self.security_score >= 0.5:
            self.security_threat_level = "high"
        else:
            self.security_threat_level = "critical"
        self.updated_at = datetime.now(timezone.utc)

    async def calculate_performance_trend(self) -> Dict[str, Any]:
        """Calculate performance trends asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return {
            "overall_trend": "improving" if self.overall_score > 0.7 else "stable" if self.overall_score > 0.5 else "declining",
            "health_trend": "improving" if self.overall_health_score > 70 else "stable" if self.overall_health_score > 50 else "declining",
            "quality_trend": "improving" if self.data_quality_score > 0.7 else "stable" if self.data_quality_score > 0.5 else "declining"
        }

    async def generate_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        suggestions = []
        
        if self.overall_score < 0.7:
            suggestions.append("Review and optimize graph structure and relationships")
        if self.overall_health_score < 70:
            suggestions.append("Investigate health score factors and implement improvements")
        if self.compliance_score < 0.8:
            suggestions.append("Review compliance requirements and update validation rules")
        if self.security_score < 0.8:
            suggestions.append("Conduct security audit and implement security measures")
        if self.neo4j_sync_error_count > 3:
            suggestions.append("Investigate Neo4j synchronization issues and optimize sync process")
        
        return suggestions

    async def get_enterprise_summary(self) -> Dict[str, Any]:
        """Get comprehensive enterprise summary asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return {
            "graph_id": self.graph_id,
            "overall_score": self.overall_score,
            "enterprise_health_status": self.enterprise_health_status,
            "risk_assessment": self.risk_assessment,
            "graph_complexity_score": self.graph_complexity_score,
            "ml_maturity_score": self.ml_maturity_score,
            "optimization_priority": self.optimization_priority,
            "maintenance_schedule": self.maintenance_schedule,
            "performance_metrics": {
                "performance_score": self.performance_score,
                "data_quality_score": self.data_quality_score,
                "reliability_score": self.reliability_score,
                "compliance_score": self.compliance_score
            },
            "health_metrics": {
                "overall_health_score": self.overall_health_score,
                "health_status": self.health_status,
                "operational_status": self.operational_status,
                "availability_status": self.availability_status
            },
            "ml_metrics": {
                "ml_training_enabled": self.ml_training_enabled,
                "active_ml_sessions": self.active_ml_sessions,
                "total_models_trained": self.total_models_trained,
                "ml_model_count": self.ml_model_count
            },
            "compliance_metrics": {
                "compliance_status": self.compliance_status,
                "compliance_score": self.compliance_score,
                "compliance_rules_count": self.compliance_rules_count,
                "compliance_violations_count": self.compliance_violations_count
            },
            "security_metrics": {
                "security_threat_level": self.security_threat_level,
                "security_score": self.security_score,
                "security_incidents_count": self.security_incidents_count,
                "security_vulnerabilities_count": self.security_vulnerabilities_count
            }
        }

    async def validate_enterprise_compliance(self) -> Dict[str, Any]:
        """Validate enterprise compliance asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        compliance_results = {
            "overall_compliance": self.compliance_score >= 0.8,
            "security_compliance": self.security_score >= 0.8,
            "data_quality_compliance": self.data_quality_score >= 0.8,
            "performance_compliance": self.performance_score >= 0.7,
            "health_compliance": self.overall_health_score >= 70,
            "ml_compliance": self.ml_maturity_score >= 0.6 if self.ml_training_enabled else True
        }
        
        compliance_results["all_compliant"] = all(compliance_results.values())
        return compliance_results

    async def get_knowledge_graph_analysis(self) -> Dict[str, Any]:
        """Get comprehensive knowledge graph analysis asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return {
            "graph_scale": {
                "total_nodes": self.total_nodes,
                "total_relationships": self.total_relationships,
                "graph_complexity": self.graph_complexity,
                "graph_count": self.graph_count
            },
            "workflow_analysis": {
                "registry_type": self.registry_type,
                "workflow_source": self.workflow_source,
                "lifecycle_status": self.lifecycle_status,
                "lifecycle_phase": self.lifecycle_phase
            },
            "integration_analysis": {
                "integration_status": self.integration_status,
                "neo4j_import_status": self.neo4j_import_status,
                "neo4j_export_status": self.neo4j_export_status,
                "sync_health": "healthy" if self.neo4j_sync_error_count == 0 else "warning" if self.neo4j_sync_error_count <= 3 else "critical"
            },
            "ml_analysis": {
                "ml_enabled": self.ml_training_enabled,
                "ml_maturity": self.ml_maturity_score,
                "training_capability": "active" if self.active_ml_sessions > 0 else "available" if self.ml_training_enabled else "disabled"
            }
        }

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
            ai_rag_id=ai_rag_id,  # Link to AI RAG system
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            **kwargs
        )

    # ========================================================================
    # ADDITIONAL ASYNC METHODS (Matching Certificate Manager)
    # ========================================================================
    
    async def validate_integrity(self) -> bool:
        """Validate graph data integrity"""
        try:
            # Validate required fields
            if not all([self.graph_id, self.file_id, self.user_id, self.org_id]):
                return False
            
            # Validate business rules
            if self.overall_health_score < 0 or self.overall_health_score > 100:
                return False
            
            if self.performance_score < 0.0 or self.performance_score > 1.0:
                return False
            
            if self.data_quality_score < 0.0 or self.data_quality_score > 1.0:
                return False
            
            if self.compliance_score < 0.0 or self.compliance_score > 1.0:
                return False
            
            return True
            
        except Exception as e:
            return False
    
    async def update_health_metrics(self) -> None:
        """Update health metrics based on current state"""
        try:
            # Update health status based on overall health score
            if self.overall_health_score >= 80:
                self.health_status = "healthy"
            elif self.overall_health_score >= 60:
                self.health_status = "warning"
            elif self.overall_health_score >= 40:
                self.health_status = "critical"
            else:
                self.health_status = "offline"
            
            # Update operational status based on health
            if self.health_status == "offline":
                self.operational_status = "error"
            elif self.health_status == "critical":
                self.operational_status = "maintenance"
            elif self.health_status == "warning":
                self.operational_status = "paused"
            else:
                self.operational_status = "running"
            
            # Update availability status
            if self.operational_status == "running":
                self.availability_status = "online"
            elif self.operational_status == "error":
                self.availability_status = "offline"
            else:
                self.availability_status = "degraded"
            
            self.updated_at = datetime.now(timezone.utc)
            
        except Exception as e:
            pass
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive graph summary"""
        try:
            await self.update_health_metrics()
            
            summary = {
                "graph_id": self.graph_id,
                "graph_name": self.graph_name,
                "health_score": self.overall_health_score,
                "health_status": self.health_status,
                "operational_status": self.operational_status,
                "availability_status": self.availability_status,
                "overall_score": self.overall_score,
                "enterprise_health_status": self.enterprise_health_status,
                "risk_assessment": self.risk_assessment,
                "optimization_priority": self.optimization_priority,
                "maintenance_schedule": self.maintenance_schedule,
                "graph_scale": {
                    "total_nodes": self.total_nodes,
                    "total_relationships": self.total_relationships,
                    "graph_complexity": self.graph_complexity,
                    "graph_count": self.graph_count
                },
                "ml_capabilities": {
                    "ml_training_enabled": self.ml_training_enabled,
                    "active_ml_sessions": self.active_ml_sessions,
                    "total_models_trained": self.total_models_trained,
                    "ml_model_count": self.ml_model_count
                },
                "performance_metrics": {
                    "performance_score": self.performance_score,
                    "data_quality_score": self.data_quality_score,
                    "reliability_score": self.reliability_score,
                    "compliance_score": self.compliance_score
                },
                "compliance_security": {
                    "compliance_status": self.compliance_status,
                    "security_threat_level": self.security_threat_level,
                    "security_score": self.security_score
                },
                "neo4j_integration": {
                    "import_status": self.neo4j_import_status,
                    "export_status": self.neo4j_export_status,
                    "sync_errors": self.neo4j_sync_error_count
                }
            }
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to generate summary: {str(e)}"}
    
    async def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export graph data in specified format"""
        try:
            if format.lower() == "json":
                return {
                    "graph_id": self.graph_id,
                    "graph_name": self.graph_name,
                    "graph_category": self.graph_category,
                    "graph_type": self.graph_type,
                    "registry_type": self.registry_type,
                    "workflow_source": self.workflow_source,
                    "overall_health_score": self.overall_health_score,
                    "health_status": self.health_status,
                    "lifecycle_status": self.lifecycle_status,
                    "lifecycle_phase": self.lifecycle_phase,
                    "operational_status": self.operational_status,
                    "availability_status": self.availability_status,
                    "performance_metrics": {
                        "performance_score": self.performance_score,
                        "data_quality_score": self.data_quality_score,
                        "reliability_score": self.reliability_score,
                        "compliance_score": self.compliance_score,
                        "completeness_score": self.completeness_score
                    },
                    "graph_metrics": {
                        "total_nodes": self.total_nodes,
                        "total_relationships": self.total_relationships,
                        "graph_complexity": self.graph_complexity,
                        "graph_count": self.graph_count
                    },
                    "ml_capabilities": {
                        "ml_training_enabled": self.ml_training_enabled,
                        "active_ml_sessions": self.active_ml_sessions,
                        "total_models_trained": self.total_models_trained,
                        "ml_model_count": self.ml_model_count
                    },
                    "neo4j_integration": {
                        "import_status": self.neo4j_import_status,
                        "export_status": self.neo4j_export_status,
                        "last_sync": self.last_neo4j_sync_at.isoformat() if self.last_neo4j_sync_at else None,
                        "sync_errors": self.neo4j_sync_error_count
                    },
                    "compliance_security": {
                        "compliance_status": self.compliance_status,
                        "security_threat_level": self.security_threat_level,
                        "security_score": self.security_score,
                        "encryption_enabled": self.encryption_enabled
                    },
                    "computed_fields": {
                        "overall_score": self.overall_score,
                        "enterprise_health_status": self.enterprise_health_status,
                        "risk_assessment": self.risk_assessment,
                        "graph_complexity_score": self.graph_complexity_score,
                        "ml_maturity_score": self.ml_maturity_score,
                        "optimization_priority": self.optimization_priority,
                        "maintenance_schedule": self.maintenance_schedule,
                        "graph_maturity_score": self.graph_maturity_score,
                        "integration_maturity_score": self.integration_maturity_score,
                        "data_quality_assessment": self.data_quality_assessment
                    },
                    "timestamps": {
                        "created_at": self.created_at.isoformat() if self.created_at else None,
                        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                        "activated_at": self.activated_at.isoformat() if self.activated_at else None
                    }
                }
            else:
                return {"error": f"Unsupported format: {format}"}
                
        except Exception as e:
            return {"error": f"Failed to export data: {str(e)}"}


# Query Models for API Operations
class KGGraphRegistryQuery(BaseModel):
    """Query model for filtering KG graph registries"""
    
    # Basic filters
    graph_name: Optional[str] = None
    graph_category: Optional[str] = None
    graph_type: Optional[str] = None
    registry_type: Optional[str] = None
    workflow_source: Optional[str] = None
    
    # Status filters
    integration_status: Optional[str] = None
    health_status: Optional[str] = None
    lifecycle_status: Optional[str] = None
    operational_status: Optional[str] = None
    
    # Performance filters
    min_overall_score: Optional[float] = None
    max_overall_score: Optional[float] = None
    min_performance_score: Optional[float] = None
    max_performance_score: Optional[float] = None
    
    # Enterprise filters
    risk_assessment: Optional[str] = None
    compliance_status: Optional[str] = None
    security_level: Optional[str] = None
    
    # User filters
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    dept_id: Optional[str] = None
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    
    # Pagination
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"


# Summary Models for Analytics
class KGGraphRegistrySummary(BaseModel):
    """Summary model for KG graph registry analytics"""
    
    # Counts
    total_graphs: int
    active_graphs: int
    inactive_graphs: int
    critical_graphs: int
    
    # Performance averages
    avg_overall_score: float
    avg_performance_score: float
    avg_data_quality_score: float
    avg_reliability_score: float
    avg_compliance_score: float
    
    # Status distribution
    status_distribution: Dict[str, int]
    health_distribution: Dict[str, int]
    lifecycle_distribution: Dict[str, int]
    
    # Graph metrics
    total_nodes: int
    total_relationships: int
    total_ml_models: int
    
    # Enterprise metrics
    avg_security_score: float
    avg_compliance_score: float
    avg_integration_maturity: float
    
    # Risk assessment
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    
    # Integration metrics
    avg_graph_maturity: float
    most_common_graph_type: str
    
    # Timestamps
    summary_generated_at: datetime
    data_from_date: Optional[datetime] = None
    data_to_date: Optional[datetime] = None
