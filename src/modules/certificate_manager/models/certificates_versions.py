"""
Certificate Versions Model
Version model for certificates_versions table with all components
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from uuid import uuid4
from enum import Enum

from pydantic import BaseModel, Field, validator, field_validator, computed_field, ConfigDict
from src.engine.models.base_model import EngineBaseModel, ModelObserver

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class VersionType(str, Enum):
    """Version type classification"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRE_RELEASE = "pre_release"
    RELEASE_CANDIDATE = "release_candidate"
    BETA = "beta"
    ALPHA = "alpha"
    HOTFIX = "hotfix"


class ApprovalStatus(str, Enum):
    """Approval workflow status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    UNDER_APPROVAL = "under_approval"


class ChangeImpact(str, Enum):
    """Change impact assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    BREAKING = "breaking"


class ChangeCategory(str, Enum):
    """Change category classification"""
    BUG_FIX = "bug_fix"
    FEATURE_ADDITION = "feature_addition"
    FEATURE_MODIFICATION = "feature_modification"
    FEATURE_REMOVAL = "feature_removal"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    SECURITY_UPDATE = "security_update"
    COMPLIANCE_UPDATE = "compliance_update"
    DOCUMENTATION_UPDATE = "documentation_update"
    INFRASTRUCTURE_CHANGE = "infrastructure_change"
    CONFIGURATION_CHANGE = "configuration_change"


class ReviewStatus(str, Enum):
    """Review process status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    REQUIRES_CHANGES = "requires_changes"


class PublicationStatus(str, Enum):
    """Publication status"""
    DRAFT = "draft"
    READY_FOR_PUBLICATION = "ready_for_publication"
    PUBLISHED = "published"
    PUBLICATION_FAILED = "publication_failed"
    ROLLED_BACK = "rolled_back"


class VersionStatus(str, Enum):
    """Version status classification"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ChangeType(str, Enum):
    """Change type classification"""
    ADDITION = "addition"
    MODIFICATION = "modification"
    REMOVAL = "removal"
    REFACTORING = "refactoring"


class QualityLevel(str, Enum):
    """Quality level classification"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance status classification"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"


# ============================================================================
# NESTED COMPONENT MODELS
# ============================================================================

class VersionMetadata(BaseModel):
    """Semantic versioning, descriptions, change reasons"""
    model_config = ConfigDict(from_attributes=True)
    
    # Semantic versioning
    major_version: int = Field(default=1, ge=0, description="Major version number")
    minor_version: int = Field(default=0, ge=0, description="Minor version number")
    patch_version: int = Field(default=0, ge=0, description="Patch version number")
    pre_release_label: Optional[str] = Field(None, description="Pre-release label (alpha, beta, rc)")
    pre_release_number: Optional[int] = Field(None, ge=0, description="Pre-release number")
    build_metadata: Optional[str] = Field(None, description="Build metadata")
    
    # Version information
    version_string: str = Field(default="", description="Full version string")
    version_description: str = Field(default="", description="Version description")
    release_notes: Optional[str] = Field(None, description="Release notes for this version")
    change_log: Optional[str] = Field(None, description="Detailed change log")
    
    # Version classification
    version_type: VersionType = Field(default=VersionType.PATCH, description="Type of version")
    is_stable: bool = Field(default=True, description="Whether this is a stable version")
    is_production_ready: bool = Field(default=True, description="Whether this is production ready")
    is_backward_compatible: bool = Field(default=True, description="Whether this is backward compatible")
    
    # Version lifecycle
    release_date: Optional[datetime] = Field(None, description="Planned release date")
    end_of_life_date: Optional[datetime] = Field(None, description="End of life date")
    support_duration_days: Optional[int] = Field(None, ge=0, description="Support duration in days")
    
    @computed_field
    @property
    def semantic_version(self) -> str:
        """Generate semantic version string"""
        version = f"{self.major_version}.{self.minor_version}.{self.patch_version}"
        if self.pre_release_label:
            version += f"-{self.pre_release_label}"
            if self.pre_release_number:
                version += f".{self.pre_release_number}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version
    
    @computed_field
    @property
    def is_pre_release(self) -> bool:
        """Check if this is a pre-release version"""
        return self.pre_release_label is not None
    
    @computed_field
    @property
    def days_until_release(self) -> Optional[int]:
        """Calculate days until release"""
        if not self.release_date:
            return None
        delta = self.release_date - datetime.utcnow()
        return delta.days


class DataSnapshots(BaseModel):
    """Complete module data at version creation"""
    model_config = ConfigDict(from_attributes=True)
    
    # Snapshot metadata
    snapshot_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique snapshot identifier")
    snapshot_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When snapshot was created")
    snapshot_type: str = Field(default="full", description="Type of snapshot (full, incremental, differential)")
    
    # Module data snapshots
    aasx_snapshot: Dict[str, Any] = Field(default_factory=dict, description="AASX module data snapshot")
    certificate_manager_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Certificate Manager snapshot")
    data_processor_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Data Processor snapshot")
    analytics_engine_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Analytics Engine snapshot")
    workflow_engine_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Workflow Engine snapshot")
    integration_layer_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Integration Layer snapshot")
    security_module_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Security Module snapshot")
    
    # Snapshot statistics
    total_data_size_bytes: int = Field(default=0, ge=0, description="Total data size in bytes")
    compressed_size_bytes: int = Field(default=0, ge=0, description="Compressed data size in bytes")
    data_records_count: int = Field(default=0, ge=0, description="Total number of data records")
    
    # Snapshot integrity
    snapshot_hash: str = Field(default="", description="Hash of snapshot data")
    hash_algorithm: str = Field(default="SHA-256", description="Hash algorithm used")
    compression_algorithm: str = Field(default="gzip", description="Compression algorithm used")
    
    # Storage information
    storage_location: str = Field(default="", description="Storage location for snapshot")
    backup_location: Optional[str] = Field(None, description="Backup storage location")
    retention_policy_days: int = Field(default=365, ge=0, description="Retention policy in days")
    
    @computed_field
    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio"""
        if self.total_data_size_bytes == 0:
            return 0.0
        return (1 - (self.compressed_size_bytes / self.total_data_size_bytes)) * 100
    
    @computed_field
    @property
    def all_module_snapshots(self) -> Dict[str, Any]:
        """Get all module snapshots"""
        return {
            "aasx": self.aasx_snapshot,
            "certificate_manager": self.certificate_manager_snapshot,
            "data_processor": self.data_processor_snapshot,
            "analytics_engine": self.analytics_engine_snapshot,
            "workflow_engine": self.workflow_engine_snapshot,
            "integration_layer": self.integration_layer_snapshot,
            "security_module": self.security_module_snapshot
        }
    
    @computed_field
    @property
    def is_compressed(self) -> bool:
        """Check if snapshot is compressed"""
        return self.compressed_size_bytes < self.total_data_size_bytes


class ChangeTracking(BaseModel):
    """Change summaries, diffs, impact analysis"""
    model_config = ConfigDict(from_attributes=True)
    
    # Change information
    change_summary: str = Field(default="", description="Summary of changes in this version")
    change_description: Optional[str] = Field(default="", description="Detailed description of changes")
    change_reason: str = Field(default="", description="Reason for the change")
    change_request_id: Optional[str] = Field(None, description="Change request identifier")
    
    # Change classification
    change_category: ChangeCategory = Field(default=ChangeCategory.BUG_FIX, description="Category of change")
    change_impact: ChangeImpact = Field(default=ChangeImpact.LOW, description="Impact of the change")
    change_priority: str = Field(default="medium", description="Priority of the change")
    
    # Change details
    files_changed: List[str] = Field(default_factory=list, description="List of files changed")
    lines_added: int = Field(default=0, ge=0, description="Number of lines added")
    lines_removed: int = Field(default=0, ge=0, description="Number of lines removed")
    lines_modified: int = Field(default=0, ge=0, description="Number of lines modified")
    
    # Change impact analysis
    affected_modules: List[str] = Field(default_factory=list, description="Modules affected by changes")
    breaking_changes: List[str] = Field(default_factory=list, description="List of breaking changes")
    migration_required: bool = Field(default=False, description="Whether migration is required")
    migration_notes: Optional[str] = Field(None, description="Migration notes and instructions")
    
    # Change dependencies
    dependencies_added: List[str] = Field(default_factory=list, description="Dependencies added")
    dependencies_removed: List[str] = Field(default_factory=list, description="Dependencies removed")
    dependencies_updated: List[str] = Field(default_factory=list, description="Dependencies updated")
    
    # Change testing
    tests_added: int = Field(default=0, ge=0, description="Number of tests added")
    tests_modified: int = Field(default=0, ge=0, description="Number of tests modified")
    test_coverage_change: float = Field(default=0.0, description="Change in test coverage percentage")
    
    @computed_field
    @property
    def total_lines_changed(self) -> int:
        """Calculate total lines changed"""
        return self.lines_added + self.lines_removed + self.lines_modified
    
    @computed_field
    @property
    def is_breaking_change(self) -> bool:
        """Check if this is a breaking change"""
        return (
            self.change_impact == ChangeImpact.BREAKING or
            len(self.breaking_changes) > 0 or
            self.migration_required
        )
    
    @computed_field
    @property
    def change_complexity(self) -> str:
        """Determine change complexity"""
        total_changes = self.total_lines_changed
        if total_changes > 1000:
            return "very_high"
        elif total_changes > 500:
            return "high"
        elif total_changes > 100:
            return "medium"
        elif total_changes > 50:
            return "low"
        else:
            return "very_low"
    
    @field_validator('change_description')
    @classmethod
    def validate_change_description(cls, v):
        """Validate change description - allow empty since it's optional"""
        if v is None:
            return None
        if v and len(v) > 2000:
            raise ValueError('Change description too long')
        return v.strip() if v else v


class ApprovalWorkflow(BaseModel):
    """Review, approval, and publication tracking"""
    model_config = ConfigDict(from_attributes=True)
    
    # Workflow status
    workflow_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Current workflow status")
    workflow_step: str = Field(default="submitted", description="Current workflow step")
    workflow_progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Workflow progress percentage")
    
    # Review process
    review_status: ReviewStatus = Field(default=ReviewStatus.NOT_STARTED, description="Review process status")
    review_started_at: Optional[datetime] = Field(None, description="When review started")
    review_completed_at: Optional[datetime] = Field(None, description="When review completed")
    review_duration_hours: Optional[float] = Field(None, ge=0.0, description="Review duration in hours")
    
    # Reviewers
    assigned_reviewers: List[str] = Field(default_factory=list, description="Assigned reviewers")
    completed_reviews: List[str] = Field(default_factory=list, description="Completed reviews")
    pending_reviews: List[str] = Field(default_factory=list, description="Pending reviews")
    
    # Review feedback
    review_comments: List[Dict[str, Any]] = Field(default_factory=list, description="Review comments and feedback")
    review_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Overall review score")
    review_decision: Optional[str] = Field(None, description="Review decision")
    
    # Approval process
    approval_required: bool = Field(default=True, description="Whether approval is required")
    approval_levels: List[str] = Field(default_factory=list, description="Required approval levels")
    approved_by: List[str] = Field(default_factory=list, description="Users who approved")
    approved_at: List[datetime] = Field(default_factory=list, description="Approval timestamps")
    
    # Publication tracking
    publication_status: PublicationStatus = Field(default=PublicationStatus.DRAFT, description="Publication status")
    publication_date: Optional[datetime] = Field(None, description="When version was published")
    publication_notes: Optional[str] = Field(None, description="Publication notes")
    
    # Workflow metadata
    workflow_started_at: datetime = Field(default_factory=datetime.utcnow, description="When workflow started")
    workflow_completed_at: Optional[datetime] = Field(None, description="When workflow completed")
    workflow_duration_hours: Optional[float] = Field(None, ge=0.0, description="Total workflow duration")
    
    @computed_field
    @property
    def is_workflow_complete(self) -> bool:
        """Check if workflow is complete"""
        return self.workflow_status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]
    
    @computed_field
    @property
    def review_completion_rate(self) -> float:
        """Calculate review completion rate"""
        if not self.assigned_reviewers:
            return 0.0
        return (len(self.completed_reviews) / len(self.assigned_reviewers)) * 100
    
    @computed_field
    @property
    def approval_completion_rate(self) -> float:
        """Calculate approval completion rate"""
        if not self.approval_levels:
            return 100.0
        return (len(self.approved_by) / len(self.approval_levels)) * 100


class DigitalVerification(BaseModel):
    """Version signatures, hashes, integrity checks"""
    model_config = ConfigDict(from_attributes=True)
    
    # Digital signatures
    digital_signature: str = Field(default="", description="Digital signature of the version")
    signature_algorithm: str = Field(default="RSA-SHA256", description="Signature algorithm used")
    signature_timestamp: Optional[datetime] = Field(None, description="When signature was created")
    signer_identity: str = Field(default="", description="Identity of the signer")
    signer_certificate: str = Field(default="", description="Signer's certificate")
    
    # Content verification
    content_hash: str = Field(default="", description="Hash of version content")
    hash_algorithm: str = Field(default="SHA-256", description="Hash algorithm used")
    hash_timestamp: Optional[datetime] = Field(None, description="When hash was calculated")
    
    # Integrity checks
    integrity_check_passed: bool = Field(default=False, description="Whether integrity check passed")
    integrity_check_timestamp: Optional[datetime] = Field(None, description="When integrity check was performed")
    integrity_check_result: str = Field(default="", description="Integrity check result details")
    
    # Verification status
    verification_status: str = Field(default="pending", description="Digital verification status")
    verification_timestamp: Optional[datetime] = Field(None, description="When verification was performed")
    verification_result: str = Field(default="", description="Verification result details")
    
    # Trust indicators
    trust_level: str = Field(default="unknown", description="Digital trust level")
    trust_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Digital trust score")
    trust_factors: List[str] = Field(default_factory=list, description="Factors contributing to trust")
    
    # Blockchain integration
    blockchain_hash: Optional[str] = Field(None, description="Blockchain hash if stored")
    blockchain_timestamp: Optional[datetime] = Field(None, description="Blockchain timestamp")
    blockchain_network: str = Field(default="", description="Blockchain network used")
    
    # Verification metadata
    verification_method: str = Field(default="", description="Method used for verification")
    verification_tools: List[str] = Field(default_factory=list, description="Tools used for verification")
    verification_environment: str = Field(default="", description="Environment where verification was performed")
    
    @computed_field
    @property
    def is_digitally_signed(self) -> bool:
        """Check if version is digitally signed"""
        return bool(self.digital_signature and self.signer_identity)
    
    @computed_field
    @property
    def is_hash_verified(self) -> bool:
        """Check if hash is verified"""
        return bool(self.content_hash and self.hash_timestamp)
    
    @computed_field
    @property
    def is_integrity_verified(self) -> bool:
        """Check if integrity is verified"""
        return self.integrity_check_passed
    
    @computed_field
    @property
    def trust_indicator(self) -> str:
        """Get trust indicator based on trust score"""
        if self.trust_score >= 90:
            return "high"
        elif self.trust_score >= 70:
            return "medium"
        elif self.trust_score >= 50:
            return "low"
        else:
            return "untrusted"


class BusinessIntelligence(BaseModel):
    """Consolidated business insights"""
    model_config = ConfigDict(from_attributes=True)
    
    # Business metrics
    business_value_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Business value score")
    roi_estimate: Optional[float] = Field(None, description="Return on investment estimate")
    cost_benefit_analysis: Dict[str, Any] = Field(default_factory=dict, description="Cost-benefit analysis data")
    
    # Stakeholder insights
    stakeholder_satisfaction: float = Field(default=0.0, ge=0.0, le=100.0, description="Stakeholder satisfaction score")
    stakeholder_feedback: List[Dict[str, Any]] = Field(default_factory=list, description="Stakeholder feedback")
    stakeholder_priorities: List[str] = Field(default_factory=list, description="Stakeholder priorities")
    
    # Market analysis
    market_relevance: float = Field(default=0.0, ge=0.0, le=100.0, description="Market relevance score")
    competitive_advantage: List[str] = Field(default_factory=list, description="Competitive advantages")
    market_positioning: str = Field(default="", description="Market positioning strategy")
    
    # Risk assessment
    business_risk_level: str = Field(default="low", description="Business risk level")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    risk_mitigation: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    
    # Performance indicators
    kpi_metrics: Dict[str, float] = Field(default_factory=dict, description="Key performance indicators")
    sla_compliance: float = Field(default=0.0, ge=0.0, le=100.0, description="SLA compliance percentage")
    performance_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Performance trends")
    
    # Strategic insights
    strategic_alignment: float = Field(default=0.0, ge=0.0, le=100.0, description="Strategic alignment score")
    strategic_objectives: List[str] = Field(default_factory=list, description="Strategic objectives")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics")
    
    # Business intelligence metadata
    insights_generated_at: datetime = Field(default_factory=datetime.utcnow, description="When insights were generated")
    insights_version: str = Field(default="1.0", description="Insights format version")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used for insights")
    
    @computed_field
    @property
    def overall_business_score(self) -> float:
        """Calculate overall business score"""
        scores = [
            self.business_value_score,
            self.stakeholder_satisfaction,
            self.market_relevance,
            self.strategic_alignment
        ]
        return sum(scores) / len(scores)
    
    @computed_field
    @property
    def risk_assessment_level(self) -> str:
        """Determine risk assessment level"""
        if len(self.risk_factors) > 5:
            return "high"
        elif len(self.risk_factors) > 2:
            return "medium"
        else:
            return "low"
    
    @computed_field
    @property
    def is_strategically_aligned(self) -> bool:
        """Check if version is strategically aligned"""
        return self.strategic_alignment >= 80.0


# ============================================================================
# MAIN VERSION MODEL
# ============================================================================

class CertificateVersions(EngineBaseModel):
    """
    Version model for certificates_versions table
    Comprehensive version tracking with all business components
    """
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),  # Disable protected namespace warnings for Pydantic v2
        arbitrary_types_allowed=True,
        extra="allow"  # Allow extra fields to prevent validation errors
    )
    
    # ========================================================================
    # PRIMARY IDENTIFIERS
    # ========================================================================
    version_id: str = Field(..., description="Unique version identifier")
    certificate_id: str = Field(..., description="Reference to the certificate")
    
    # ========================================================================
    # VERSION METADATA
    # ========================================================================
    version_number: str = Field(..., description="Version number string")
    version_status: Optional[str] = Field(default="draft", description="Version status")
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp (if soft deleted)")
    
    # ========================================================================
    # COMPONENT MODELS
    # ========================================================================
    version_metadata: VersionMetadata = Field(default_factory=VersionMetadata, description="Version metadata")
    data_snapshots: DataSnapshots = Field(default_factory=DataSnapshots, description="Data snapshots")
    change_tracking: ChangeTracking = Field(default_factory=ChangeTracking, description="Change tracking")
    approval_workflow: ApprovalWorkflow = Field(default_factory=ApprovalWorkflow, description="Approval workflow")
    digital_verification: DigitalVerification = Field(default_factory=DigitalVerification, description="Digital verification")
    business_intelligence: BusinessIntelligence = Field(default_factory=BusinessIntelligence, description="Business intelligence")
    
    # ========================================================================
    # WORKFLOW FIELDS
    # ========================================================================
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Approval status")
    is_approved: bool = Field(default=False, description="Whether this version is approved")
    is_rejected: bool = Field(default=False, description="Whether this version is rejected")
    is_pending_approval: bool = Field(default=True, description="Whether this version is pending approval")
    approval_notes: Optional[str] = Field(None, description="Approval notes")
    
    rejected_by: Optional[str] = Field(None, description="User who rejected")
    rejected_at: Optional[datetime] = Field(None, description="When rejected")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")
    
    # ========================================================================
    # AUDIT FIELDS
    # ========================================================================
    created_by: str = Field(..., description="User who created the version")
    updated_by: Optional[str] = Field(None, description="User who last updated")
    deleted_by: Optional[str] = Field(None, description="User who deleted (if soft deleted)")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    
    # ========================================================================
    # ADDITIONAL METADATA
    # ========================================================================
    tags: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Version tags")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    # ========================================================================
    # SCHEMA FIELDS (Direct database fields - only new fields not in nested models)
    # ========================================================================
    
    # Version Information (from schema - new fields only)
    version_name: Optional[str] = Field(None, description="Human-readable version name")
    version_description: Optional[str] = Field(None, description="Description of what this version contains")
    
    # Complete Data Snapshot (JSON from schema - new fields only)
    module_data_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Complete data from ALL modules at this version")
    consolidated_summary: Dict[str, Any] = Field(default_factory=dict, description="Consolidated view at this version")
    change_summary: Dict[str, Any] = Field(default_factory=dict, description="JSON: what changed in this version")
    diff_summary: Dict[str, Any] = Field(default_factory=dict, description="JSON: detailed changes from previous version")
    
    # Version Metadata (from schema - new fields only)
    change_reason: Optional[str] = Field(None, description="Why this version was created")
    change_request_id: Optional[str] = Field(None, description="Reference to change request")
    change_priority: str = Field(default="normal", description="Priority of the change")
    
    # Approval & Review (from schema - new fields only)
    approval_timestamp: Optional[datetime] = Field(None, description="When approval was given")
    reviewer_user_id: Optional[str] = Field(None, description="User who reviewed this version")
    
    # Digital Trust (from schema - new fields only)
    version_signature: Optional[str] = Field(None, description="Digital signature for this version")
    version_hash: Optional[str] = Field(None, description="Hash for integrity verification")
    signature_timestamp: Optional[datetime] = Field(None, description="When signature was applied")
    
    # Quality & Validation (from schema - new fields only)
    version_quality_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Version quality score")
    validation_status: str = Field(default="pending", description="Validation status")
    validation_notes: Optional[str] = Field(None, description="Notes from validation process")
    
    # Timestamps & Audit (from schema - new fields only)
    created_from: Optional[str] = Field(None, description="Source of version creation (manual, auto, system)")
    review_timestamp: Optional[datetime] = Field(None, description="When version was reviewed")
    published_at: Optional[datetime] = Field(None, description="When version was published")
    
    # Environment Management (new fields)
    deployment_environment: str = Field(default="development", description="Current deployment environment")
    deployment_status: str = Field(default="not_deployed", description="Deployment status")
    is_deployed: bool = Field(default=False, description="Whether this version is deployed")
    deployment_timestamp: Optional[datetime] = Field(None, description="When deployed to environment")
    environment_promotion_history: Dict[str, Any] = Field(default_factory=dict, description="JSON: history of environment promotions")
    
    # Performance & Analytics (new fields)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="JSON: performance data")
    usage_statistics: Dict[str, Any] = Field(default_factory=dict, description="JSON: usage analytics")
    storage_optimization_data: Dict[str, Any] = Field(default_factory=dict, description="JSON: storage optimization info")
    
    # Security & Access Control (new fields)
    version_permissions: Dict[str, Any] = Field(default_factory=dict, description="JSON: version-specific permissions")
    access_control_list: Dict[str, Any] = Field(default_factory=dict, description="JSON: ACL data")
    security_level: str = Field(default="standard", description="Security level")
    is_high_security: bool = Field(default=False, description="Whether this version has high security level")
    encryption_status: str = Field(default="none", description="Encryption status")
    is_encrypted: bool = Field(default=False, description="Whether this version data is encrypted")
    
    # Reporting & Compliance (new fields)
    compliance_status: Dict[str, Any] = Field(default_factory=dict, description="JSON: compliance data")
    audit_trail_data: Dict[str, Any] = Field(default_factory=dict, description="JSON: audit trail")
    reporting_metadata: Dict[str, Any] = Field(default_factory=dict, description="JSON: reporting metadata")
    
    # Version Lifecycle Management (new fields)
    archive_status: str = Field(default="active", description="Archive status")
    is_archived: bool = Field(default=False, description="Whether this version is archived")
    archive_timestamp: Optional[datetime] = Field(None, description="When version was archived")
    archive_reason: Optional[str] = Field(None, description="Reason for archiving")
    restore_timestamp: Optional[datetime] = Field(None, description="When version was restored")
    
    # ========================================================================
    # COMPUTED FIELDS
    # ========================================================================
    
    @computed_field
    @property
    def age_hours(self) -> float:
        """Calculate version age in hours"""
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds() / 3600
    
    @computed_field
    @property
    def workflow_duration_hours(self) -> Optional[float]:
        """Calculate workflow duration in hours"""
        if not self.approval_workflow.workflow_completed_at:
            return None
        delta = self.approval_workflow.workflow_completed_at - self.approval_workflow.workflow_started_at
        return delta.total_seconds() / 3600
    
    @computed_field
    @property
    def overall_quality_score(self) -> float:
        """Calculate overall quality score from components"""
        scores = [
            self.digital_verification.trust_score,
            self.business_intelligence.overall_business_score,
            self.approval_workflow.workflow_progress
        ]
        return sum(scores) / len(scores)
    
    # ========================================================================
    # NEW COMPUTED FIELDS FOR BUSINESS DOMAIN METHODS
    # ========================================================================
    
    @computed_field
    @property
    def deployment_age_hours(self) -> Optional[float]:
        """Calculate deployment age in hours"""
        if not self.deployment_timestamp:
            return None
        delta = datetime.utcnow() - self.deployment_timestamp
        return delta.total_seconds() / 3600
    
    @computed_field
    @property
    def archive_age_hours(self) -> Optional[float]:
        """Calculate archive age in hours"""
        if not self.archive_timestamp:
            return None
        delta = datetime.utcnow() - self.archive_timestamp
        return delta.total_seconds() / 3600
    
    @computed_field
    @property
    def requires_attention(self) -> bool:
        """Check if version requires attention"""
        return (
            self.overall_quality_score < 70 or
            self.change_tracking.is_breaking_change or
            self.approval_workflow.workflow_status == ApprovalStatus.REJECTED or
            not self.digital_verification.integrity_check_passed
        )
    
    # ========================================================================
    # VALIDATION METHODS
    # ========================================================================
    
    @field_validator('version_id')
    @classmethod
    def validate_version_id(cls, v):
        """Validate version ID format"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Version ID cannot be empty')
        if len(v) > 255:
            raise ValueError('Version ID too long')
        return v.strip()
    
    @field_validator('version_number')
    @classmethod
    def validate_version_number(cls, v):
        """Validate version number format"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Version number cannot be empty')
        if len(v) > 100:
            raise ValueError('Version number too long')
        return v.strip()
    

    
    # ========================================================================
    # ASYNC METHODS
    # ========================================================================
    
    async def validate_integrity(self) -> bool:
        """Validate version data integrity"""
        try:
            # Validate required fields
            if not all([self.version_id, self.certificate_id, self.version_number]):
                return False
            
            # Validate component models
            if not all([
                self.version_metadata,
                self.data_snapshots,
                self.change_tracking,
                self.approval_workflow,
                self.digital_verification,
                self.business_intelligence
            ]):
                return False
            
            # Validate business rules
            if self.is_approved and not self.approval_workflow.approved_by:
                return False
            
            if self.is_rejected and not self.rejection_reason:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating version integrity: {e}")
            return False
    
    async def update_workflow_progress(self) -> None:
        """Update workflow progress based on current state"""
        try:
            # Calculate workflow progress
            total_steps = 4  # submitted, review, approval, publication
            completed_steps = 0
            
            if self.approval_workflow.review_status == ReviewStatus.COMPLETED:
                completed_steps += 1
            
            if self.is_approved:
                completed_steps += 1
            
            if self.digital_verification.verification_status == "completed":
                completed_steps += 1
            
            if self.approval_workflow.publication_status == PublicationStatus.PUBLISHED:
                completed_steps += 1
            
            # Update workflow progress
            self.approval_workflow.workflow_progress = (completed_steps / total_steps) * 100
            
            # Update workflow status
            if self.approval_workflow.workflow_progress == 100:
                self.approval_workflow.workflow_status = ApprovalStatus.APPROVED
                self.approval_workflow.workflow_completed_at = datetime.utcnow()
            
            logger.info(f"Updated workflow progress for version {self.version_id}: {self.approval_workflow.workflow_progress}%")
            
        except Exception as e:
            logger.error(f"Error updating workflow progress: {e}")
    
    async def generate_version_summary(self) -> Dict[str, Any]:
        """Generate comprehensive version summary"""
        try:
            await self.update_workflow_progress()
            
            summary = {
                "version_id": self.version_id,
                "version_number": self.version_number,
                "version_type": self.version_type.value,
                "status": self.approval_status.value,
                "quality_score": self.overall_quality_score,
                "requires_attention": self.requires_attention,
                "age_hours": self.age_hours,
                "workflow_progress": self.approval_workflow.workflow_progress,
                "change_impact": self.change_impact.value,
                "change_category": self.change_category.value,
                "is_breaking_change": self.change_tracking.is_breaking_change,
                "digital_verification": {
                    "is_signed": self.digital_verification.is_digitally_signed,
                    "trust_score": self.digital_verification.trust_score,
                    "integrity_verified": self.digital_verification.is_integrity_verified
                },
                "business_intelligence": {
                    "business_score": self.business_intelligence.overall_business_score,
                    "risk_level": self.business_intelligence.risk_assessment_level,
                    "strategic_alignment": self.business_intelligence.strategic_alignment
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating version summary: {e}")
            return {}
    
    async def export_version_data(self, format: str = "json") -> Dict[str, Any]:
        """Export version data in specified format"""
        try:
            export_data = {
                "export_info": {
                    "format": format,
                    "exported_at": datetime.utcnow().isoformat(),
                    "version_id": self.version_id
                },
                "version_data": self.model_dump(),
                "summary": await self.generate_version_summary()
            }
            
            logger.info(f"Exported version {self.version_id} in {format} format")
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting version data: {e}")
            raise
