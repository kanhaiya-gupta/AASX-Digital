"""
Federated Learning Registry Model
================================

Data model for federated learning registry with integrated enterprise features.
Extends the engine's BaseModel for compatibility with the merged schema.
Uses pure async patterns for optimal performance.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from src.engine.models.base_model import BaseModel
from pydantic import Field, validator


class FederatedLearningRegistry(BaseModel):
    """Model for federated learning registry with enterprise features"""
    
    # Primary identification
    registry_id: str = Field(..., description="Unique registry identifier")
    federation_name: str = Field(..., description="Name of the federation")
    registry_name: str = Field(..., description="Registry name")
    federation_type: str = Field(..., description="Type of federation")
    federation_category: str = Field(..., description="Category of federation")
    
    # Integration IDs
    aasx_integration_id: Optional[str] = Field(None, description="AASX integration ID")
    twin_registry_id: Optional[str] = Field(None, description="Twin registry integration ID")
    kg_neo4j_id: Optional[str] = Field(None, description="Knowledge Graph Neo4j integration ID")
    physics_modeling_id: Optional[str] = Field(None, description="Physics modeling integration ID")
    ai_rag_id: Optional[str] = Field(None, description="AI RAG integration ID")
    certificate_manager_id: Optional[str] = Field(None, description="Certificate manager integration ID")
    
    # Status fields
    integration_status: str = Field(default="pending", description="Integration status")
    overall_health_score: float = Field(default=0.0, description="Overall health score")
    health_status: str = Field(default="unknown", description="Health status")
    lifecycle_status: str = Field(default="created", description="Lifecycle status")
    
    # Federation status
    federation_participation_status: str = Field(default="inactive", description="Federation participation status")
    aggregation_status: str = Field(default="pending", description="Model aggregation status")
    privacy_compliance_status: str = Field(default="pending", description="Privacy compliance status")
    algorithm_execution_status: str = Field(default="idle", description="Algorithm execution status")
    
    # Performance metrics
    performance_score: float = Field(default=0.0, description="Performance score")
    data_quality_score: float = Field(default=0.0, description="Data quality score")
    reliability_score: float = Field(default=0.0, description="Reliability score")
    compliance_score: float = Field(default=0.0, description="Compliance score")
    
    # Security fields
    security_level: str = Field(default="basic", description="Security level")
    access_control_level: str = Field(default="basic", description="Access control level")
    encryption_enabled: bool = Field(default=False, description="Whether encryption is enabled")
    
    # Enterprise Compliance (merged from enterprise table)
    compliance_framework: Optional[str] = Field(None, description="Compliance framework")
    compliance_status: Optional[str] = Field(None, description="Compliance status")
    last_audit_date: Optional[datetime] = Field(None, description="Last audit date")
    next_audit_date: Optional[datetime] = Field(None, description="Next audit date")
    audit_details: Optional[Dict[str, Any]] = Field(None, description="Audit details")
    risk_level: Optional[str] = Field(None, description="Risk level")
    
    # Enterprise Security (merged from enterprise table)
    security_score: Optional[float] = Field(None, description="Security score")
    threat_detection_score: Optional[float] = Field(None, description="Threat detection score")
    encryption_strength: Optional[str] = Field(None, description="Encryption strength")
    authentication_method: Optional[str] = Field(None, description="Authentication method")
    access_control_score: Optional[float] = Field(None, description="Access control score")
    data_protection_score: Optional[float] = Field(None, description="Data protection score")
    incident_response_time: Optional[float] = Field(None, description="Incident response time in minutes")
    security_audit_score: Optional[float] = Field(None, description="Security audit score")
    last_security_scan: Optional[datetime] = Field(None, description="Last security scan")
    security_details: Optional[Dict[str, Any]] = Field(None, description="Security details")
    
    # Enterprise Performance (merged from enterprise table)
    efficiency_score: Optional[float] = Field(None, description="Efficiency score")
    scalability_score: Optional[float] = Field(None, description="Scalability score")
    optimization_potential: Optional[float] = Field(None, description="Optimization potential")
    bottleneck_identification: Optional[str] = Field(None, description="Bottleneck identification")
    performance_trend: Optional[str] = Field(None, description="Performance trend")
    last_optimization_date: Optional[datetime] = Field(None, description="Last optimization date")
    optimization_suggestions: Optional[List[str]] = Field(None, description="Optimization suggestions")
    
    # User management
    user_id: Optional[str] = Field(None, description="User ID")
    org_id: Optional[str] = Field(None, description="Organization ID")
    dept_id: Optional[str] = Field(None, description="Department ID for traceability")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True
    
    @validator('overall_health_score', 'performance_score', 'data_quality_score', 'reliability_score', 'compliance_score')
    def validate_score_range(cls, v):
        """Validate score ranges"""
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError('Score must be between 0.0 and 100.0')
        return v
    
    @validator('federation_type')
    def validate_federation_type(cls, v):
        """Validate federation type"""
        valid_types = ['horizontal', 'vertical', 'federated_transfer', 'multi_task']
        if v not in valid_types:
            raise ValueError(f'Federation type must be one of: {valid_types}')
        return v
    
    async def calculate_overall_health(self) -> float:
        """Calculate overall health score based on various metrics (async)"""
        scores = [
            self.performance_score,
            self.data_quality_score,
            self.reliability_score,
            self.compliance_score
        ]
        
        # Filter out None values and calculate average
        valid_scores = [s for s in scores if s is not None]
        if not valid_scores:
            return 0.0
        
        return sum(valid_scores) / len(valid_scores)
    
    async def is_healthy(self) -> bool:
        """Check if the federation is healthy (async)"""
        health_score = await self.calculate_overall_health()
        return health_score >= 70.0 and self.health_status in ['healthy', 'warning']
    
    async def get_integration_status_summary(self) -> Dict[str, bool]:
        """Get summary of integration statuses (async)"""
        return {
            'aasx': self.aasx_integration_id is not None,
            'twin_registry': self.twin_registry_id is not None,
            'kg_neo4j': self.kg_neo4j_id is not None,
            'physics_modeling': self.physics_modeling_id is not None,
            'ai_rag': self.ai_rag_id is not None,
            'certificate_manager': self.certificate_manager_id is not None
        }
    
    async def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for display (async)"""
        health_score = await self.calculate_overall_health()
        is_healthy = await self.is_healthy()
        
        return {
            'registry_id': self.registry_id,
            'federation_name': self.federation_name,
            'federation_type': self.federation_type,
            'health_status': self.health_status,
            'overall_health_score': round(health_score, 2),
            'performance_score': round(self.performance_score, 2),
            'compliance_status': self.compliance_status,
            'security_level': self.security_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_healthy': is_healthy
        }
    
    async def update_health_status(self) -> None:
        """Update health status based on current metrics (async)"""
        health_score = await self.calculate_overall_health()
        
        if health_score >= 90.0:
            self.health_status = "excellent"
        elif health_score >= 80.0:
            self.health_status = "good"
        elif health_score >= 70.0:
            self.health_status = "healthy"
        elif health_score >= 50.0:
            self.health_status = "warning"
        else:
            self.health_status = "critical"
        
        self.overall_health_score = health_score
        self.updated_at = datetime.now()
    
    async def validate_compliance(self) -> Dict[str, Any]:
        """Validate compliance requirements (async)"""
        compliance_results = {
            'overall_compliance': 'pending',
            'details': {},
            'risk_level': 'unknown'
        }
        
        # Check basic compliance
        if self.compliance_framework:
            compliance_results['details']['framework'] = self.compliance_framework
            compliance_results['overall_compliance'] = self.compliance_status or 'pending'
        
        # Check security compliance
        if self.security_score is not None:
            if self.security_score >= 80.0:
                compliance_results['details']['security'] = 'compliant'
            else:
                compliance_results['details']['security'] = 'non_compliant'
        
        # Determine risk level
        if self.risk_level:
            compliance_results['risk_level'] = self.risk_level
        
        return compliance_results
