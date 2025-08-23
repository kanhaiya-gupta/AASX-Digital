"""
AI RAG Registry Model
====================

Pydantic model for AI RAG registry operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from src.engine.models.base_model import BaseModel as EngineBaseModel


class AIRagRegistry(EngineBaseModel):
    """
    AI RAG Registry Model - Pure Async Implementation
    
    Represents the main AI RAG registry with 100+ fields from the schema.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    # Primary Identification
    registry_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique registry identifier")
    file_id: str = Field(..., description="Associated file ID")
    registry_name: str = Field(..., description="Registry name")
    
    # RAG Classification & Metadata
    rag_category: str = Field(default="generic", description="RAG category")
    rag_type: str = Field(default="basic", description="RAG type")
    rag_priority: str = Field(default="normal", description="RAG priority")
    rag_version: str = Field(default="1.0.0", description="RAG version")
    
    # Workflow Classification
    registry_type: str = Field(..., description="Registry type")
    workflow_source: str = Field(..., description="Workflow source")
    
    # Module Integration References (Framework Integration)
    aasx_integration_id: Optional[str] = Field(None, description="AASX integration ID")
    twin_registry_id: Optional[str] = Field(None, description="Twin registry ID")
    kg_neo4j_id: Optional[str] = Field(None, description="KG Neo4j ID")
    physics_modeling_id: Optional[str] = Field(None, description="Physics modeling ID")
    federated_learning_id: Optional[str] = Field(None, description="Federated learning ID")
    certificate_manager_id: Optional[str] = Field(None, description="Certificate manager ID")
    
    # Integration Status & Health (Framework Health)
    integration_status: str = Field(default="pending", description="Integration status")
    overall_health_score: int = Field(default=0, ge=0, le=100, description="Overall health score")
    health_status: str = Field(default="unknown", description="Health status")
    
    # Lifecycle Management (Framework Lifecycle)
    lifecycle_status: str = Field(default="created", description="Lifecycle status")
    lifecycle_phase: str = Field(default="development", description="Lifecycle phase")
    
    # Operational Status (Framework Operations)
    operational_status: str = Field(default="stopped", description="Operational status")
    availability_status: str = Field(default="offline", description="Availability status")
    
    # RAG-Specific Integration Status (Framework Integration Points)
    embedding_generation_status: str = Field(default="pending", description="Embedding generation status")
    vector_db_sync_status: str = Field(default="pending", description="Vector DB sync status")
    last_embedding_generated_at: Optional[str] = Field(None, description="Last embedding generation time")
    last_vector_db_sync_at: Optional[str] = Field(None, description="Last vector DB sync time")
    
    # RAG Configuration (Framework Configuration - NOT Raw Data)
    embedding_model: Optional[str] = Field(None, description="Embedding model name/version")
    vector_db_type: Optional[str] = Field(None, description="Vector database type")
    vector_collection_id: Optional[str] = Field(None, description="Vector collection identifier")
    
    # RAG Techniques Configuration (JSON for better framework flexibility)
    rag_techniques_config: Dict[str, Any] = Field(default_factory=dict, description="RAG techniques configuration")
    supported_file_types_config: Dict[str, Any] = Field(default_factory=dict, description="Supported file types configuration")
    processor_capabilities_config: Dict[str, Any] = Field(default_factory=dict, description="Processor capabilities configuration")
    
    # Performance & Quality Metrics (Framework Performance)
    performance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Performance score")
    data_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data quality score")
    reliability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Reliability score")
    compliance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Compliance score")
    
    # Security & Access Control (Framework Security)
    security_level: str = Field(default="standard", description="Security level")
    access_control_level: str = Field(default="user", description="Access control level")
    encryption_enabled: bool = Field(default=False, description="Encryption enabled")
    audit_logging_enabled: bool = Field(default=True, description="Audit logging enabled")
    
    # User Management & Ownership (Framework Access Control)
    user_id: str = Field(..., description="User ID")
    org_id: str = Field(..., description="Organization ID")
    dept_id: Optional[str] = Field(None, description="Department ID for complete traceability")
    owner_team: Optional[str] = Field(None, description="Owner team")
    steward_user_id: Optional[str] = Field(None, description="Steward user ID")
    
    # Timestamps & Audit (Framework Audit Trail)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    activated_at: Optional[str] = Field(None, description="Activation timestamp")
    last_accessed_at: Optional[str] = Field(None, description="Last access timestamp")
    last_modified_at: Optional[str] = Field(None, description="Last modification timestamp")
    
    # Configuration & Metadata (Framework Configuration - JSON)
    registry_config: Dict[str, Any] = Field(default_factory=dict, description="Registry configuration")
    registry_metadata: Dict[str, Any] = Field(default_factory=dict, description="Registry metadata")
    custom_attributes: Dict[str, Any] = Field(default_factory=dict, description="Custom attributes")
    tags_config: Dict[str, Any] = Field(default_factory=dict, description="Tags configuration")
    
    # Relationships & Dependencies (Framework Dependencies - JSON)
    relationships_config: Dict[str, Any] = Field(default_factory=dict, description="Relationships configuration")
    dependencies_config: Dict[str, Any] = Field(default_factory=dict, description="Dependencies configuration")
    rag_instances_config: Dict[str, Any] = Field(default_factory=dict, description="RAG instances configuration")
    
    # Additional fields for enhanced functionality
    description: Optional[str] = Field(None, description="Registry description")
    notes: Optional[str] = Field(None, description="Additional notes")
    version: str = Field(default="1.0.0", description="Model version")
    model_version: str = Field(default="1.0.0", description="Model version")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
        validate_assignment = True
        arbitrary_types_allowed = True
    
    # Validators
    @validator('rag_category')
    def validate_rag_category(cls, v):
        """Validate RAG category"""
        valid_categories = ['text', 'image', 'multimodal', 'hybrid', 'graph_enhanced']
        if v not in valid_categories:
            raise ValueError(f'RAG category must be one of: {valid_categories}')
        return v
    
    @validator('rag_type')
    def validate_rag_type(cls, v):
        """Validate RAG type"""
        valid_types = ['basic', 'advanced', 'graph', 'hybrid', 'multi_step']
        if v not in valid_types:
            raise ValueError(f'RAG type must be one of: {valid_types}')
        return v
    
    @validator('rag_priority')
    def validate_rag_priority(cls, v):
        """Validate RAG priority"""
        valid_priorities = ['low', 'normal', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'RAG priority must be one of: {valid_priorities}')
        return v
    
    @validator('registry_type')
    def validate_registry_type(cls, v):
        """Validate registry type"""
        valid_types = ['extraction', 'generation', 'hybrid']
        if v not in valid_types:
            raise ValueError(f'Registry type must be one of: {valid_types}')
        return v
    
    @validator('workflow_source')
    def validate_workflow_source(cls, v):
        """Validate workflow source"""
        valid_sources = ['aasx_file', 'structured_data', 'both']
        if v not in valid_sources:
            raise ValueError(f'Workflow source must be one of: {valid_sources}')
        return v
    
    @validator('integration_status')
    def validate_integration_status(cls, v):
        """Validate integration status"""
        valid_statuses = ['pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated']
        if v not in valid_statuses:
            raise ValueError(f'Integration status must be one of: {valid_statuses}')
        return v
    
    @validator('health_status')
    def validate_health_status(cls, v):
        """Validate health status"""
        valid_statuses = ['unknown', 'healthy', 'warning', 'critical', 'offline']
        if v not in valid_statuses:
            raise ValueError(f'Health status must be one of: {valid_statuses}')
        return v
    
    @validator('lifecycle_status')
    def validate_lifecycle_status(cls, v):
        """Validate lifecycle status"""
        valid_statuses = ['created', 'active', 'suspended', 'archived', 'retired']
        if v not in valid_statuses:
            raise ValueError(f'Lifecycle status must be one of: {valid_statuses}')
        return v
    
    @validator('lifecycle_phase')
    def validate_lifecycle_phase(cls, v):
        """Validate lifecycle phase"""
        valid_phases = ['development', 'testing', 'production', 'maintenance', 'sunset']
        if v not in valid_phases:
            raise ValueError(f'Lifecycle phase must be one of: {valid_phases}')
        return v
    
    @validator('operational_status')
    def validate_operational_status(cls, v):
        """Validate operational status"""
        valid_statuses = ['running', 'stopped', 'paused', 'error', 'maintenance']
        if v not in valid_statuses:
            raise ValueError(f'Operational status must be one of: {valid_statuses}')
        return v
    
    @validator('availability_status')
    def validate_availability_status(cls, v):
        """Validate availability status"""
        valid_statuses = ['online', 'offline', 'degraded', 'maintenance']
        if v not in valid_statuses:
            raise ValueError(f'Availability status must be one of: {valid_statuses}')
        return v
    
    @validator('embedding_generation_status')
    def validate_embedding_generation_status(cls, v):
        """Validate embedding generation status"""
        valid_statuses = ['pending', 'in_progress', 'completed', 'failed', 'scheduled']
        if v not in valid_statuses:
            raise ValueError(f'Embedding generation status must be one of: {valid_statuses}')
        return v
    
    @validator('vector_db_sync_status')
    def validate_vector_db_sync_status(cls, v):
        """Validate vector DB sync status"""
        valid_statuses = ['pending', 'in_progress', 'completed', 'failed', 'scheduled']
        if v not in valid_statuses:
            raise ValueError(f'Vector DB sync status must be one of: {valid_statuses}')
        return v
    
    @validator('security_level')
    def validate_security_level(cls, v):
        """Validate security level"""
        valid_levels = ['public', 'internal', 'confidential', 'secret', 'top_secret']
        if v not in valid_levels:
            raise ValueError(f'Security level must be one of: {valid_levels}')
        return v
    
    @validator('access_control_level')
    def validate_access_control_level(cls, v):
        """Validate access control level"""
        valid_levels = ['public', 'user', 'admin', 'system', 'restricted']
        if v not in valid_levels:
            raise ValueError(f'Access control level must be one of: {valid_levels}')
        return v
    
    @validator('overall_health_score')
    def validate_overall_health_score(cls, v):
        """Validate overall health score"""
        if not 0 <= v <= 100:
            raise ValueError('Overall health score must be between 0 and 100')
        return v
    
    @validator('performance_score', 'data_quality_score', 'reliability_score', 'compliance_score')
    def validate_score_fields(cls, v):
        """Validate score fields"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    # Async methods for database operations
    async def save_to_database(self) -> bool:
        """Save the registry to database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def update_in_database(self) -> bool:
        """Update the registry in database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def delete_from_database(self) -> bool:
        """Delete the registry from database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    # Business logic methods
    def calculate_health_score(self) -> int:
        """Calculate overall health score based on various metrics"""
        base_score = 50
        
        # Performance bonus (up to 25 points)
        performance_bonus = int(self.performance_score * 25)
        
        # Quality bonus (up to 25 points)
        quality_bonus = int(self.data_quality_score * 25)
        
        total_score = base_score + performance_bonus + quality_bonus
        return min(total_score, 100)
    
    def is_healthy(self) -> bool:
        """Check if the registry is healthy"""
        return self.overall_health_score >= 70
    
    def is_operational(self) -> bool:
        """Check if the registry is operational"""
        return self.operational_status == 'running' and self.availability_status == 'online'
    
    def get_rag_technique_config(self, technique_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific RAG technique"""
        return self.rag_techniques_config.get(technique_name)
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file types"""
        file_types = []
        for file_type, config in self.supported_file_types_config.items():
            if config.get('enabled', False):
                file_types.append(file_type)
        return file_types
    
    def get_processor_capabilities(self, processor_name: str) -> Optional[Dict[str, Any]]:
        """Get capabilities for a specific processor"""
        return self.processor_capabilities_config.get(processor_name)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIRagRegistry':
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AIRagRegistry':
        """Create model from JSON string"""
        data = json.loads(json_str)
        return cls(**data)
