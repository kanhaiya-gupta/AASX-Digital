"""
Data Governance Models - World-Class Implementation
==================================================

Pydantic models for data governance entities with enterprise-grade features:
- Data Lineage: Tracking data relationships and transformations
- Data Quality Metrics: Comprehensive quality monitoring and scoring
- Change Requests: Change management workflows and approval processes
- Data Versions: Data versioning and change history
- Governance Policies: Policy enforcement and compliance management

Features:
- Comprehensive validation and business rules
- Audit trail and compliance tracking
- Performance optimization and caching
- Enterprise patterns and extensibility
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from .base_model import BaseModel as EngineBaseModel


class DataLineage(EngineBaseModel):
    """
    Data lineage model for tracking data relationships and transformations.
    
    Tracks how data flows between entities, transformation processes,
    and dependency relationships for comprehensive data governance.
    """
    
    lineage_id: str = Field(..., description="Unique identifier for the lineage record")
    source_entity_type: str = Field(..., description="Type of source entity")
    source_entity_id: str = Field(..., description="ID of source entity")
    target_entity_type: str = Field(..., description="Type of target entity")
    target_entity_id: str = Field(..., description="ID of target entity")
    relationship_type: str = Field(..., description="Type of relationship between entities")
    lineage_depth: int = Field(default=1, description="How many levels deep this relationship goes")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this lineage relationship")
    transformation_type: str = Field(default="none", description="Type of transformation applied")
    transformation_details: Union[str, Dict[str, Any]] = Field(default="{}", description="Details about the transformation")
    lineage_metadata: Union[str, Dict[str, Any]] = Field(default="{}", description="Additional lineage information")
    is_active: bool = Field(default=True, description="Whether this lineage record is active")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    last_accessed: Optional[str] = Field(default=None, description="Last access timestamp")
    access_count: int = Field(default=0, ge=0, description="Number of times accessed")
    validation_status: str = Field(default="pending", description="Validation status of the lineage")
    transformation_steps: Union[str, List[Dict[str, Any]]] = Field(default="[]", description="Step-by-step transformation process")
    data_quality_impact: float = Field(default=0.0, ge=0.0, le=1.0, description="Impact on data quality scores")
    business_value_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Business value of this lineage")
    lineage_complexity: str = Field(default="simple", description="Complexity level of the lineage")
    validation_rules: Union[str, List[str]] = Field(default="[]", description="Validation rules applied")
    lineage_confidence_factors: Union[str, Dict[str, Any]] = Field(default="{}", description="Factors affecting confidence")
    lineage_impact_analysis: Union[str, Dict[str, Any]] = Field(default="{}", description="Impact analysis results")
    dependency_level: str = Field(default="direct", description="Level of dependency")
    dependency_criticality: str = Field(default="low", description="Criticality of the dependency")
    dependency_risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Risk assessment score")
    dependency_mitigation: Union[str, Dict[str, Any]] = Field(default="{}", description="Risk mitigation strategies")
    dependency_alerts: Union[str, List[Dict[str, Any]]] = Field(default="[]", description="Alert configurations")
    dependency_visualization: Union[str, Dict[str, Any]] = Field(default="{}", description="Visualization preferences")

    @validator('source_entity_type', 'target_entity_type')
    def validate_entity_type(cls, v):
        valid_types = ['file', 'project', 'use_case', 'user', 'organization']
        if v not in valid_types:
            raise ValueError(f'Entity type must be one of: {valid_types}')
        return v

    @validator('relationship_type')
    def validate_relationship_type(cls, v):
        valid_types = ['derived_from', 'depends_on', 'contains', 'belongs_to', 'processed_by', 'owned_by']
        if v not in valid_types:
            raise ValueError(f'Relationship type must be one of: {valid_types}')
        return v

    @validator('transformation_type')
    def validate_transformation_type(cls, v):
        valid_types = ['none', 'extraction', 'processing', 'aggregation', 'filtering', 'enrichment']
        if v not in valid_types:
            raise ValueError(f'Transformation type must be one of: {valid_types}')
        return v

    @validator('validation_status')
    def validate_validation_status(cls, v):
        valid_statuses = ['pending', 'validated', 'invalid', 'needs_review']
        if v not in valid_statuses:
            raise ValueError(f'Validation status must be one of: {valid_statuses}')
        return v

    @validator('lineage_complexity')
    def validate_lineage_complexity(cls, v):
        valid_complexities = ['simple', 'moderate', 'complex']
        if v not in valid_complexities:
            raise ValueError(f'Lineage complexity must be one of: {valid_complexities}')
        return v

    @validator('dependency_level')
    def validate_dependency_level(cls, v):
        valid_levels = ['direct', 'indirect', 'transitive']
        if v not in valid_levels:
            raise ValueError(f'Dependency level must be one of: {valid_levels}')
        return v

    @validator('dependency_criticality')
    def validate_dependency_criticality(cls, v):
        valid_criticalities = ['low', 'medium', 'high', 'critical']
        if v not in valid_criticalities:
            raise ValueError(f'Dependency criticality must be one of: {valid_criticalities}')
        return v


class DataQualityMetrics(EngineBaseModel):
    """
    Data quality metrics model for comprehensive quality monitoring.
    
    Tracks quality scores across multiple dimensions, identifies issues,
    and provides improvement recommendations for data governance.
    """
    
    quality_id: str = Field(..., description="Unique identifier for the quality metrics record")
    entity_type: str = Field(..., description="Type of entity being measured")
    entity_id: str = Field(..., description="ID of the entity being measured")
    metric_date: str = Field(..., description="Date when metrics were calculated")
    accuracy_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data accuracy score")
    completeness_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data completeness score")
    consistency_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data consistency score")
    timeliness_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data timeliness score")
    validity_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data validity score")
    uniqueness_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Data uniqueness score")
    overall_quality_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Weighted average of all dimensions")
    quality_threshold: float = Field(default=70.0, ge=0.0, le=100.0, description="Minimum acceptable quality score")
    quality_status: str = Field(default="unknown", description="Overall quality status")
    quality_issues: Union[str, List[Dict[str, Any]]] = Field(default="[]", description="List of quality issues found")
    quality_improvements: Union[str, List[str]] = Field(default="[]", description="Suggested improvements")
    quality_metadata: Union[str, Dict[str, Any]] = Field(default="{}", description="Additional quality information")
    calculated_by: Optional[str] = Field(default=None, description="User who calculated these metrics")
    calculation_method: str = Field(default="automated", description="How metrics were calculated")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    last_quality_check: Optional[str] = Field(default=None, description="Last quality check timestamp")
    quality_trend: Union[str, Dict[str, Any]] = Field(default="{}", description="Quality trend over time")

    @validator('entity_type')
    def validate_entity_type(cls, v):
        valid_types = ['file', 'project', 'use_case', 'user', 'organization']
        if v not in valid_types:
            raise ValueError(f'Entity type must be one of: {valid_types}')
        return v

    @validator('quality_status')
    def validate_quality_status(cls, v):
        valid_statuses = ['excellent', 'good', 'acceptable', 'poor', 'critical', 'unknown']
        if v not in valid_statuses:
            raise ValueError(f'Quality status must be one of: {valid_statuses}')
        return v

    @validator('calculation_method')
    def validate_calculation_method(cls, v):
        valid_methods = ['automated', 'manual', 'hybrid']
        if v not in valid_methods:
            raise ValueError(f'Calculation method must be one of: {valid_methods}')
        return v

    def calculate_overall_score(self) -> float:
        """Calculate overall quality score from individual dimension scores."""
        scores = [
            self.accuracy_score,
            self.completeness_score,
            self.consistency_score,
            self.timeliness_score,
            self.validity_score,
            self.uniqueness_score
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def update_quality_status(self):
        """Update quality status based on overall score and threshold."""
        if self.overall_quality_score >= 90:
            self.quality_status = "excellent"
        elif self.overall_quality_score >= 80:
            self.quality_status = "good"
        elif self.overall_quality_score >= 70:
            self.quality_status = "acceptable"
        elif self.overall_quality_score >= 50:
            self.quality_status = "poor"
        else:
            self.quality_status = "critical"


class ChangeRequest(EngineBaseModel):
    """
    Change request model for managing data change workflows.
    
    Tracks change requests, approval processes, implementation status,
    and provides comprehensive change management for data governance.
    """
    
    request_id: str = Field(..., description="Unique identifier for the change request")
    title: str = Field(..., description="Title of the change request")
    description: Optional[str] = Field(default=None, description="Description of the change request")
    change_type: str = Field(..., description="Type of change being requested")
    entity_type: str = Field(..., description="Type of entity being changed")
    entity_id: Optional[str] = Field(default=None, description="ID of the entity being changed")
    requested_by: str = Field(..., description="User who requested the change")
    requested_at: str = Field(..., description="When the change was requested")
    change_details: Union[str, Dict[str, Any]] = Field(default="{}", description="Specific changes requested")
    current_state: Union[str, Dict[str, Any]] = Field(default="{}", description="Current state before change")
    proposed_state: Union[str, Dict[str, Any]] = Field(default="{}", description="Proposed state after change")
    impact_analysis: Union[str, Dict[str, Any]] = Field(default="{}", description="Impact assessment")
    status: str = Field(default="pending", description="Current status of the change request")
    priority: str = Field(default="medium", description="Priority level of the change")
    urgency: str = Field(default="normal", description="Urgency level of the change")
    assigned_to: Optional[str] = Field(default=None, description="User assigned to review/approve")
    assigned_at: Optional[str] = Field(default=None, description="When the request was assigned")
    review_deadline: Optional[str] = Field(default=None, description="Deadline for review")
    approval_required: bool = Field(default=True, description="Whether approval is required")
    approval_chain: Union[str, List[str]] = Field(default="[]", description="Approval hierarchy")
    review_notes: Optional[str] = Field(default=None, description="Notes from review process")
    review_date: Optional[str] = Field(default=None, description="Date of review")
    reviewed_by: Optional[str] = Field(default=None, description="User who reviewed")
    approval_date: Optional[str] = Field(default=None, description="Date of approval")
    approved_by: Optional[str] = Field(default=None, description="User who approved")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection if applicable")
    implementation_notes: Optional[str] = Field(default=None, description="Notes from implementation")
    implementation_date: Optional[str] = Field(default=None, description="Date of implementation")
    implemented_by: Optional[str] = Field(default=None, description="User who implemented")
    rollback_plan: Union[str, Dict[str, Any]] = Field(default="{}", description="Rollback strategy")
    tags: Union[str, List[str]] = Field(default="[]", description="Tags for categorization")
    metadata: Union[str, Dict[str, Any]] = Field(default="{}", description="Additional information")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    @validator('change_type')
    def validate_change_type(cls, v):
        valid_types = ['create', 'update', 'delete', 'restore', 'bulk_update', 'schema_change']
        if v not in valid_types:
            raise ValueError(f'Change type must be one of: {valid_types}')
        return v

    @validator('entity_type')
    def validate_entity_type(cls, v):
        valid_types = ['file', 'project', 'use_case', 'user', 'organization', 'data_lineage', 'quality_metrics']
        if v not in valid_types:
            raise ValueError(f'Entity type must be one of: {valid_types}')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'under_review', 'approved', 'rejected', 'in_progress', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v

    @validator('urgency')
    def validate_urgency(cls, v):
        valid_urgencies = ['normal', 'high', 'urgent', 'emergency']
        if v not in valid_urgencies:
            raise ValueError(f'Urgency must be one of: {valid_urgencies}')
        return v


class DataVersion(EngineBaseModel):
    """
    Data version model for tracking data versioning and changes.
    
    Manages version history, change tracking, compliance status,
    and provides comprehensive versioning for data governance.
    """
    
    version_id: str = Field(..., description="Unique identifier for the version record")
    entity_type: str = Field(..., description="Type of entity being versioned")
    entity_id: str = Field(..., description="ID of the entity being versioned")
    version_number: str = Field(..., description="Semantic version number")
    version_type: str = Field(..., description="Type of version change")
    previous_version_id: Optional[str] = Field(default=None, description="Link to previous version")
    change_summary: Optional[str] = Field(default=None, description="Summary of changes in this version")
    change_details: Union[str, Dict[str, Any]] = Field(default="{}", description="Detailed change information")
    data_snapshot: Union[str, Dict[str, Any]] = Field(default="{}", description="Complete data state at this version")
    change_type: str = Field(..., description="Type of change made")
    change_reason: Optional[str] = Field(default=None, description="Why this change was made")
    change_request_id: Optional[str] = Field(default=None, description="Link to change request if applicable")
    created_by: str = Field(..., description="User who created this version")
    created_at: str = Field(..., description="Creation timestamp")
    is_current: bool = Field(default=False, description="Whether this is the current active version")
    is_deprecated: bool = Field(default=False, description="Whether this version is deprecated")
    deprecation_date: Optional[str] = Field(default=None, description="Date of deprecation")
    deprecation_reason: Optional[str] = Field(default=None, description="Reason for deprecation")
    last_accessed: Optional[str] = Field(default=None, description="Last access timestamp")
    access_count: int = Field(default=0, ge=0, description="Number of times accessed")
    storage_size: int = Field(default=0, ge=0, description="Size of version data in bytes")
    compliance_status: str = Field(default="unknown", description="Compliance status of this version")
    audit_notes: Optional[str] = Field(default=None, description="Audit notes")
    retention_expiry: Optional[str] = Field(default=None, description="When this version should be archived/deleted")

    @validator('entity_type')
    def validate_entity_type(cls, v):
        valid_types = ['file', 'project', 'use_case', 'user', 'organization', 'data_lineage', 'quality_metrics']
        if v not in valid_types:
            raise ValueError(f'Entity type must be one of: {valid_types}')
        return v

    @validator('version_type')
    def validate_version_type(cls, v):
        valid_types = ['major', 'minor', 'patch', 'hotfix']
        if v not in valid_types:
            raise ValueError(f'Version type must be one of: {valid_types}')
        return v

    @validator('change_type')
    def validate_change_type(cls, v):
        valid_types = ['create', 'update', 'delete', 'restore']
        if v not in valid_types:
            raise ValueError(f'Change type must be one of: {valid_types}')
        return v

    @validator('compliance_status')
    def validate_compliance_status(cls, v):
        valid_statuses = ['compliant', 'non_compliant', 'pending_review', 'unknown']
        if v not in valid_statuses:
            raise ValueError(f'Compliance status must be one of: {valid_statuses}')
        return v


class GovernancePolicy(EngineBaseModel):
    """
    Governance policy model for managing data governance policies.
    
    Defines policies, enforcement rules, compliance requirements,
    and provides comprehensive policy management for data governance.
    """
    
    policy_id: str = Field(..., description="Unique identifier for the policy")
    policy_name: str = Field(..., description="Name of the policy")
    policy_type: str = Field(..., description="Type of policy")
    policy_category: str = Field(..., description="Category of the policy")
    policy_description: str = Field(..., description="Description of the policy")
    policy_rules: Union[str, Dict[str, Any]] = Field(default="{}", description="Specific policy rules")
    policy_conditions: Union[str, List[str]] = Field(default="[]", description="Conditions when policy applies")
    policy_actions: Union[str, List[str]] = Field(default="[]", description="Actions to take when policy is violated")
    applicable_entities: Union[str, List[str]] = Field(default="[]", description="Entity types this policy applies to")
    applicable_organizations: Union[str, List[str]] = Field(default="[]", description="Organizations this policy applies to")
    applicable_users: Union[str, List[str]] = Field(default="[]", description="Users this policy applies to")
    geographic_scope: str = Field(default="global", description="Geographic scope of policy")
    enforcement_level: str = Field(default="monitor", description="Level of enforcement")
    compliance_required: bool = Field(default=True, description="Whether compliance is required")
    audit_required: bool = Field(default=True, description="Whether audit is required")
    auto_remediation: bool = Field(default=False, description="Whether auto-remediation is enabled")
    status: str = Field(default="draft", description="Current status of the policy")
    effective_date: Optional[str] = Field(default=None, description="Effective date of the policy")
    expiry_date: Optional[str] = Field(default=None, description="Expiry date of the policy")
    review_frequency: str = Field(default="monthly", description="How often to review policy")
    policy_owner: str = Field(..., description="User responsible for policy")
    policy_stewards: Union[str, List[str]] = Field(default="[]", description="Users who can modify policy")
    approval_required: bool = Field(default=True, description="Whether approval is required")
    approved_by: Optional[str] = Field(default=None, description="User who approved")
    approval_date: Optional[str] = Field(default=None, description="Date of approval")
    compliance_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Current compliance rate")
    violation_count: int = Field(default=0, ge=0, description="Number of violations")
    last_compliance_check: Optional[str] = Field(default=None, description="Last compliance check timestamp")
    compliance_trend: Union[str, Dict[str, Any]] = Field(default="{}", description="Compliance trend over time")
    tags: Union[str, List[str]] = Field(default="[]", description="Tags for categorization")
    metadata: Union[str, Dict[str, Any]] = Field(default="{}", description="Additional information")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    @validator('policy_type')
    def validate_policy_type(cls, v):
        valid_types = ['data_classification', 'access_control', 'retention', 'compliance', 'quality', 'lineage']
        if v not in valid_types:
            raise ValueError(f'Policy type must be one of: {valid_types}')
        return v

    @validator('policy_category')
    def validate_policy_category(cls, v):
        valid_categories = ['mandatory', 'recommended', 'optional', 'deprecated']
        if v not in valid_categories:
            raise ValueError(f'Policy category must be one of: {valid_categories}')
        return v

    @validator('enforcement_level')
    def validate_enforcement_level(cls, v):
        valid_levels = ['monitor', 'warn', 'block', 'auto_correct']
        if v not in valid_levels:
            raise ValueError(f'Enforcement level must be one of: {valid_levels}')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['draft', 'active', 'suspended', 'deprecated', 'archived']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v

    @validator('review_frequency')
    def validate_review_frequency(cls, v):
        valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        if v not in valid_frequencies:
            raise ValueError(f'Review frequency must be one of: {valid_frequencies}')
        return v
