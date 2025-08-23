"""
Certificate Registry Model
Main certificate model for certificates_registry table with all components
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from uuid import uuid4
from enum import Enum

from pydantic import BaseModel, Field, validator, computed_field, ConfigDict

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class ModuleStatus(str, Enum):
    """Module operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class CertificateStatus(str, Enum):
    """Certificate lifecycle status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ARCHIVED = "archived"


class QualityLevel(str, Enum):
    """Data quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    PENDING_VERIFICATION = "pending_verification"


class SecurityLevel(str, Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ApprovalStatus(str, Enum):
    """Approval workflow status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"


# ============================================================================
# NESTED COMPONENT MODELS
# ============================================================================

class ModuleStatusTracking(BaseModel):
    """Real-time status of all 7 modules"""
    model_config = ConfigDict(from_attributes=True)
    
    # Core module statuses
    aasx_module: ModuleStatus = Field(default=ModuleStatus.UNKNOWN, description="AASX module status")
    certificate_manager: ModuleStatus = Field(default=ModuleStatus.UNKNOWN, description="Certificate Manager status")
    data_processor: ModuleStatus = Field(default=ModuleStatus.UNKNOWN, description="Data Processor status")
    analytics_engine: ModuleStatus = Field(default=ModuleStatus.UNKNOWN, description="Analytics Engine status")
    workflow_engine: ModuleStatus = Field(default=ModuleStatus.UNKNOWN, description="Workflow Engine status")
    integration_layer: ModuleStatus = Field(default=ModuleStatus.UNKNOWN, description="Integration Layer status")
    security_module: ModuleStatus = Field(default=ModuleStatus.UNKNOWN, description="Security Module status")
    
    # Status metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last status update timestamp")
    health_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall system health score")
    active_modules: int = Field(default=0, ge=0, le=7, description="Number of active modules")
    error_count: int = Field(default=0, ge=0, description="Total error count across modules")
    
    # Module-specific details
    module_details: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Detailed status per module")
    
    @computed_field
    @property
    def overall_status(self) -> ModuleStatus:
        """Calculate overall system status"""
        if self.error_count > 3:
            return ModuleStatus.ERROR
        elif self.active_modules == 7:
            return ModuleStatus.ACTIVE
        elif self.active_modules >= 5:
            return ModuleStatus.MAINTENANCE
        else:
            return ModuleStatus.OFFLINE
    
    @computed_field
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return self.health_score >= 80.0 and self.error_count <= 1


class QualityAssessment(BaseModel):
    """Data quality and completeness metrics"""
    model_config = ConfigDict(from_attributes=True)
    
    # Quality scores
    overall_quality_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall quality score")
    data_completeness: float = Field(default=0.0, ge=0.0, le=100.0, description="Data completeness percentage")
    data_accuracy: float = Field(default=0.0, ge=0.0, le=100.0, description="Data accuracy percentage")
    data_consistency: float = Field(default=0.0, ge=0.0, le=100.0, description="Data consistency percentage")
    data_timeliness: float = Field(default=0.0, ge=0.0, le=100.0, description="Data timeliness percentage")
    
    # Quality levels
    quality_level: QualityLevel = Field(default=QualityLevel.POOR, description="Overall quality level")
    
    # Validation metrics
    validation_passed: int = Field(default=0, ge=0, description="Number of validation checks passed")
    validation_failed: int = Field(default=0, ge=0, description="Number of validation checks failed")
    validation_total: int = Field(default=0, ge=0, description="Total validation checks")
    
    # Coverage metrics
    required_fields_present: int = Field(default=0, ge=0, description="Number of required fields present")
    required_fields_total: int = Field(default=0, ge=0, description="Total required fields")
    optional_fields_present: int = Field(default=0, ge=0, description="Number of optional fields present")
    optional_fields_total: int = Field(default=0, ge=0, description="Total optional fields")
    
    # Quality issues
    quality_issues: List[str] = Field(default_factory=list, description="List of quality issues found")
    critical_issues: int = Field(default=0, ge=0, description="Number of critical quality issues")
    
    @computed_field
    @property
    def validation_rate(self) -> float:
        """Calculate validation success rate"""
        if self.validation_total == 0:
            return 0.0
        return (self.validation_passed / self.validation_total) * 100
    
    @computed_field
    @property
    def completeness_rate(self) -> float:
        """Calculate required fields completeness rate"""
        if self.required_fields_total == 0:
            return 0.0
        return (self.required_fields_present / self.required_fields_total) * 100


class ComplianceTracking(BaseModel):
    """Audit dates, compliance scores, regulatory info"""
    model_config = ConfigDict(from_attributes=True)
    
    # Compliance status
    compliance_status: ComplianceStatus = Field(default=ComplianceStatus.PENDING_VERIFICATION, description="Overall compliance status")
    compliance_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Compliance score percentage")
    
    # Regulatory information
    regulatory_framework: str = Field(default="", description="Applicable regulatory framework")
    compliance_standards: List[str] = Field(default_factory=list, description="List of compliance standards")
    industry_requirements: List[str] = Field(default_factory=list, description="Industry-specific requirements")
    
    # Audit information
    last_audit_date: Optional[datetime] = Field(None, description="Date of last compliance audit")
    next_audit_date: Optional[datetime] = Field(None, description="Date of next scheduled audit")
    audit_frequency: str = Field(default="annual", description="Audit frequency (annual, quarterly, monthly)")
    auditor_name: Optional[str] = Field(None, description="Name of auditing organization")
    
    # Compliance checks
    compliance_checks_passed: int = Field(default=0, ge=0, description="Number of compliance checks passed")
    compliance_checks_failed: int = Field(default=0, ge=0, description="Number of compliance checks failed")
    compliance_checks_total: int = Field(default=0, ge=0, description="Total compliance checks")
    
    # Compliance issues
    compliance_issues: List[str] = Field(default_factory=list, description="List of compliance issues")
    critical_compliance_issues: int = Field(default=0, ge=0, description="Number of critical compliance issues")
    remediation_required: bool = Field(default=False, description="Whether remediation is required")
    
    # Certifications
    certifications: List[str] = Field(default_factory=list, description="List of obtained certifications")
    certification_expiry_dates: Dict[str, datetime] = Field(default_factory=dict, description="Certification expiry dates")
    
    @computed_field
    @property
    def compliance_rate(self) -> float:
        """Calculate compliance success rate"""
        if self.compliance_checks_total == 0:
            return 0.0
        return (self.compliance_checks_passed / self.compliance_checks_total) * 100
    
    @computed_field
    @property
    def days_until_next_audit(self) -> Optional[int]:
        """Calculate days until next audit"""
        if not self.next_audit_date:
            return None
        delta = self.next_audit_date - datetime.utcnow()
        return delta.days


class SecurityMetrics(BaseModel):
    """Security events, threat levels, security scores"""
    model_config = ConfigDict(from_attributes=True)
    
    # Security status
    security_level: SecurityLevel = Field(default=SecurityLevel.LOW, description="Current security threat level")
    security_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall security score")
    
    # Security events
    security_events_total: int = Field(default=0, ge=0, description="Total security events recorded")
    security_events_critical: int = Field(default=0, ge=0, description="Critical security events")
    security_events_high: int = Field(default=0, ge=0, description="High priority security events")
    security_events_medium: int = Field(default=0, ge=0, description="Medium priority security events")
    security_events_low: int = Field(default=0, ge=0, description="Low priority security events")
    
    # Threat indicators
    active_threats: int = Field(default=0, ge=0, description="Number of active threats")
    threat_level: SecurityLevel = Field(default=SecurityLevel.LOW, description="Current threat level")
    threat_sources: List[str] = Field(default_factory=list, description="Identified threat sources")
    
    # Security metrics
    authentication_failures: int = Field(default=0, ge=0, description="Authentication failure count")
    authorization_violations: int = Field(default=0, ge=0, description="Authorization violation count")
    data_breach_attempts: int = Field(default=0, ge=0, description="Data breach attempt count")
    malware_detections: int = Field(default=0, ge=0, description="Malware detection count")
    
    # Security controls
    security_controls_active: int = Field(default=0, ge=0, description="Number of active security controls")
    security_controls_total: int = Field(default=0, ge=0, description="Total security controls")
    security_controls_effective: int = Field(default=0, ge=0, description="Number of effective security controls")
    
    # Incident response
    incident_response_time_minutes: float = Field(default=0.0, ge=0.0, description="Average incident response time")
    incidents_resolved: int = Field(default=0, ge=0, description="Number of incidents resolved")
    incidents_pending: int = Field(default=0, ge=0, description="Number of incidents pending resolution")
    
    @computed_field
    @property
    def security_effectiveness(self) -> float:
        """Calculate security controls effectiveness"""
        if self.security_controls_total == 0:
            return 0.0
        return (self.security_controls_effective / self.security_controls_total) * 100
    
    @computed_field
    @property
    def threat_risk_level(self) -> SecurityLevel:
        """Calculate overall threat risk level"""
        if self.active_threats > 10 or self.security_events_critical > 5:
            return SecurityLevel.CRITICAL
        elif self.active_threats > 5 or self.security_events_high > 10:
            return SecurityLevel.HIGH
        elif self.active_threats > 2 or self.security_events_medium > 20:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW


class BusinessContext(BaseModel):
    """Tags, custom attributes, ownership, approval workflow"""
    model_config = ConfigDict(from_attributes=True)
    
    # Business ownership
    business_owner: str = Field(default="", description="Business owner of the certificate")
    business_unit: str = Field(default="", description="Business unit responsible")
    cost_center: str = Field(default="", description="Cost center for the certificate")
    budget_allocation: float = Field(default=0.0, ge=0.0, description="Budget allocated for the certificate")
    
    # Business classification
    business_priority: str = Field(default="medium", description="Business priority level")
    business_criticality: str = Field(default="normal", description="Business criticality level")
    business_impact: str = Field(default="low", description="Business impact level")
    
    # Tags and attributes
    business_tags: List[str] = Field(default_factory=list, description="Business classification tags")
    custom_attributes: Dict[str, Any] = Field(default_factory=dict, description="Custom business attributes")
    industry_sector: str = Field(default="", description="Industry sector")
    geographic_region: str = Field(default="", description="Geographic region")
    
    # Approval workflow
    approval_workflow: str = Field(default="standard", description="Approval workflow type")
    approval_required: bool = Field(default=True, description="Whether approval is required")
    approval_levels: List[str] = Field(default_factory=list, description="Required approval levels")
    current_approval_step: str = Field(default="", description="Current approval step")
    
    # Stakeholders
    stakeholders: List[str] = Field(default_factory=list, description="List of stakeholders")
    decision_makers: List[str] = Field(default_factory=list, description="List of decision makers")
    subject_matter_experts: List[str] = Field(default_factory=list, description="List of SMEs")
    
    # Business rules
    business_rules: List[str] = Field(default_factory=list, description="Applicable business rules")
    compliance_requirements: List[str] = Field(default_factory=list, description="Business compliance requirements")
    risk_assessment: str = Field(default="", description="Business risk assessment")
    
    @computed_field
    @property
    def has_approval_workflow(self) -> bool:
        """Check if approval workflow is configured"""
        return self.approval_required and len(self.approval_levels) > 0
    
    @computed_field
    @property
    def business_tags_count(self) -> int:
        """Get count of business tags"""
        return len(self.business_tags)


class ModuleSummaries(BaseModel):
    """Comprehensive module data summaries"""
    model_config = ConfigDict(from_attributes=True)
    
    # Module data summaries
    aasx_summary: Dict[str, Any] = Field(default_factory=dict, description="AASX module data summary")
    certificate_manager_summary: Dict[str, Any] = Field(default_factory=dict, description="Certificate Manager summary")
    data_processor_summary: Dict[str, Any] = Field(default_factory=dict, description="Data Processor summary")
    analytics_engine_summary: Dict[str, Any] = Field(default_factory=dict, description="Analytics Engine summary")
    workflow_engine_summary: Dict[str, Any] = Field(default_factory=dict, description="Workflow Engine summary")
    integration_layer_summary: Dict[str, Any] = Field(default_factory=dict, description="Integration Layer summary")
    security_module_summary: Dict[str, Any] = Field(default_factory=dict, description="Security Module summary")
    
    # Summary metadata
    summary_generated_at: datetime = Field(default_factory=datetime.utcnow, description="When summary was generated")
    summary_version: str = Field(default="1.0", description="Summary format version")
    summary_checksum: str = Field(default="", description="Summary data checksum")
    
    # Data coverage
    modules_with_data: int = Field(default=0, ge=0, le=7, description="Number of modules with data")
    total_data_records: int = Field(default=0, ge=0, description="Total data records across modules")
    data_freshness_hours: float = Field(default=0.0, ge=0.0, description="Data freshness in hours")
    
    # Summary statistics
    summary_statistics: Dict[str, Any] = Field(default_factory=dict, description="Statistical summary data")
    data_quality_indicators: Dict[str, Any] = Field(default_factory=dict, description="Data quality indicators")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    
    @computed_field
    @property
    def all_modules_summary(self) -> Dict[str, Any]:
        """Get summary of all modules"""
        return {
            "aasx": self.aasx_summary,
            "certificate_manager": self.certificate_manager_summary,
            "data_processor": self.data_processor_summary,
            "analytics_engine": self.analytics_engine_summary,
            "workflow_engine": self.workflow_engine_summary,
            "integration_layer": self.integration_layer_summary,
            "security_module": self.security_module_summary
        }
    
    @computed_field
    @property
    def data_coverage_percentage(self) -> float:
        """Calculate data coverage percentage"""
        if self.modules_with_data == 0:
            return 0.0
        return (self.modules_with_data / 7) * 100


class DigitalTrust(BaseModel):
    """Digital signatures, hashes, QR codes"""
    model_config = ConfigDict(from_attributes=True)
    
    # Digital signatures
    digital_signature: str = Field(default="", description="Digital signature of the certificate")
    signature_algorithm: str = Field(default="RSA-SHA256", description="Signature algorithm used")
    signature_timestamp: Optional[datetime] = Field(None, description="When signature was created")
    signer_identity: str = Field(default="", description="Identity of the signer")
    signer_certificate: str = Field(default="", description="Signer's certificate")
    
    # Cryptographic hashes
    content_hash: str = Field(default="", description="Hash of certificate content")
    hash_algorithm: str = Field(default="SHA-256", description="Hash algorithm used")
    hash_timestamp: Optional[datetime] = Field(None, description="When hash was calculated")
    
    # QR codes and identifiers
    qr_code_data: str = Field(default="", description="QR code data for the certificate")
    qr_code_format: str = Field(default="standard", description="QR code format")
    unique_identifier: str = Field(default="", description="Unique certificate identifier")
    
    # Verification data
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
    
    @computed_field
    @property
    def is_digitally_signed(self) -> bool:
        """Check if certificate is digitally signed"""
        return bool(self.digital_signature and self.signer_identity)
    
    @computed_field
    @property
    def is_hash_verified(self) -> bool:
        """Check if hash is verified"""
        return bool(self.content_hash and self.hash_timestamp)
    
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


# ============================================================================
# MAIN CERTIFICATE MODEL
# ============================================================================

class CertificateRegistry(BaseModel):
    """
    Main certificate model for certificates_registry table
    Comprehensive certificate data with all business components
    """
    model_config = ConfigDict(from_attributes=True)
    
    # ========================================================================
    # PRIMARY IDENTIFIERS
    # ========================================================================
    certificate_id: str = Field(..., description="Unique certificate identifier")
    
    # ========================================================================
    # CORE BUSINESS ENTITY RELATIONSHIPS (MANDATORY)
    # ========================================================================
    file_id: str = Field(..., description="Reference to the AASX file")
    user_id: str = Field(..., description="Creator user identifier")
    org_id: str = Field(..., description="Organization identifier")
    dept_id: str = Field(..., description="Department identifier for complete traceability")
    project_id: Optional[str] = Field(None, description="Project context identifier")
    twin_id: Optional[str] = Field(None, description="Digital twin reference")
    use_case_id: str = Field(..., description="Use case context identifier")
    
    # ========================================================================
    # CERTIFICATE METADATA
    # ========================================================================
    certificate_name: str = Field(..., description="Human-readable certificate name")
    certificate_type: str = Field(..., description="Type of certificate")
    certificate_version: str = Field(default="1.0.0", description="Certificate version")
    certificate_status: CertificateStatus = Field(default=CertificateStatus.DRAFT, description="Current status")
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    last_accessed_at: Optional[datetime] = Field(None, description="Last access timestamp")
    
    # ========================================================================
    # COMPONENT MODELS
    # ========================================================================
    module_status: ModuleStatusTracking = Field(default_factory=ModuleStatusTracking, description="Module status tracking")
    quality_assessment: QualityAssessment = Field(default_factory=QualityAssessment, description="Quality assessment data")
    compliance_tracking: ComplianceTracking = Field(default_factory=ComplianceTracking, description="Compliance tracking data")
    security_metrics: SecurityMetrics = Field(default_factory=SecurityMetrics, description="Security metrics data")
    business_context: BusinessContext = Field(default_factory=BusinessContext, description="Business context data")
    module_summaries: ModuleSummaries = Field(default_factory=ModuleSummaries, description="Module summaries data")
    digital_trust: DigitalTrust = Field(default_factory=DigitalTrust, description="Digital trust data")
    
    # ========================================================================
    # ADDITIONAL METADATA
    # ========================================================================
    description: Optional[str] = Field(None, description="Certificate description")
    tags: List[str] = Field(default_factory=list, description="Certificate tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # ========================================================================
    # AUDIT FIELDS
    # ========================================================================
    created_by: str = Field(..., description="User who created the certificate")
    updated_by: Optional[str] = Field(None, description="User who last updated")
    deleted_by: Optional[str] = Field(None, description="User who deleted (if soft deleted)")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp (if soft deleted)")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    
    # ========================================================================
    # COMPUTED FIELDS
    # ========================================================================
    
    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if certificate is active"""
        return self.certificate_status == CertificateStatus.ACTIVE
    
    @computed_field
    @property
    def is_expired(self) -> bool:
        """Check if certificate is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @computed_field
    @property
    def age_days(self) -> int:
        """Calculate certificate age in days"""
        delta = datetime.utcnow() - self.created_at
        return delta.days
    
    @computed_field
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until expiry"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return delta.days
    
    @computed_field
    @property
    def overall_health_score(self) -> float:
        """Calculate overall health score from components"""
        scores = [
            self.module_status.health_score,
            self.quality_assessment.overall_quality_score,
            self.compliance_tracking.compliance_score,
            self.security_metrics.security_score,
            self.digital_trust.trust_score
        ]
        return sum(scores) / len(scores)
    
    @computed_field
    @property
    def requires_attention(self) -> bool:
        """Check if certificate requires attention"""
        return (
            self.overall_health_score < 70 or
            self.quality_assessment.quality_level in [QualityLevel.POOR, QualityLevel.CRITICAL] or
            self.compliance_tracking.compliance_status == ComplianceStatus.NON_COMPLIANT or
            self.security_metrics.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]
        )
    
    # ========================================================================
    # VALIDATION METHODS
    # ========================================================================
    
    @validator('certificate_id')
    def validate_certificate_id(cls, v):
        """Validate certificate ID format"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Certificate ID cannot be empty')
        if len(v) > 255:
            raise ValueError('Certificate ID too long')
        return v.strip()
    
    @validator('certificate_name')
    def validate_certificate_name(cls, v):
        """Validate certificate name"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Certificate name cannot be empty')
        if len(v) > 500:
            raise ValueError('Certificate name too long')
        return v.strip()
    
    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        """Validate expiration date is after creation"""
        if v and 'created_at' in values:
            if v <= values['created_at']:
                raise ValueError('Expiration date must be after creation date')
        return v
    
    # ========================================================================
    # ASYNC METHODS
    # ========================================================================
    
    async def validate_integrity(self) -> bool:
        """Validate certificate data integrity"""
        try:
            # Validate required fields
            if not all([self.certificate_id, self.file_id, self.user_id, self.org_id, self.dept_id]):
                return False
            
            # Validate component models
            if not all([
                self.module_status,
                self.quality_assessment,
                self.compliance_tracking,
                self.security_metrics,
                self.business_context,
                self.module_summaries,
                self.digital_trust
            ]):
                return False
            
            # Validate business rules
            if self.is_expired and self.certificate_status == CertificateStatus.ACTIVE:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating certificate integrity: {e}")
            return False
    
    async def update_health_metrics(self) -> None:
        """Update health metrics based on current state"""
        try:
            # Update module status health
            self.module_status.health_score = self.overall_health_score
            
            # Update quality assessment
            if self.overall_health_score >= 90:
                self.quality_assessment.quality_level = QualityLevel.EXCELLENT
            elif self.overall_health_score >= 80:
                self.quality_assessment.quality_level = QualityLevel.GOOD
            elif self.overall_health_score >= 70:
                self.quality_assessment.quality_level = QualityLevel.FAIR
            elif self.overall_health_score >= 50:
                self.quality_assessment.quality_level = QualityLevel.POOR
            else:
                self.quality_assessment.quality_level = QualityLevel.CRITICAL
            
            # Update compliance status
            if self.compliance_tracking.compliance_score >= 90:
                self.compliance_tracking.compliance_status = ComplianceStatus.COMPLIANT
            elif self.compliance_tracking.compliance_score >= 70:
                self.compliance_tracking.compliance_status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                self.compliance_tracking.compliance_status = ComplianceStatus.NON_COMPLIANT
            
            # Update security level
            if self.security_metrics.security_score >= 90:
                self.security_metrics.security_level = SecurityLevel.LOW
            elif self.security_metrics.security_score >= 70:
                self.security_metrics.security_level = SecurityLevel.MEDIUM
            elif self.security_metrics.security_score >= 50:
                self.security_metrics.security_level = SecurityLevel.HIGH
            else:
                self.security_metrics.security_level = SecurityLevel.CRITICAL
            
            logger.info(f"Updated health metrics for certificate {self.certificate_id}")
            
        except Exception as e:
            logger.error(f"Error updating health metrics: {e}")
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive certificate summary"""
        try:
            await self.update_health_metrics()
            
            summary = {
                "certificate_id": self.certificate_id,
                "certificate_name": self.certificate_name,
                "status": self.certificate_status.value,
                "health_score": self.overall_health_score,
                "requires_attention": self.requires_attention,
                "age_days": self.age_days,
                "days_until_expiry": self.days_until_expiry,
                "module_status": {
                    "overall_status": self.module_status.overall_status.value,
                    "active_modules": self.module_status.active_modules,
                    "error_count": self.module_status.error_count
                },
                "quality_assessment": {
                    "quality_level": self.quality_assessment.quality_level.value,
                    "overall_score": self.quality_assessment.overall_quality_score,
                    "completeness": self.quality_assessment.data_completeness
                },
                "compliance_tracking": {
                    "status": self.compliance_tracking.compliance_status.value,
                    "score": self.compliance_tracking.compliance_score,
                    "next_audit_days": self.compliance_tracking.days_until_next_audit
                },
                "security_metrics": {
                    "security_level": self.security_metrics.security_level.value,
                    "security_score": self.security_metrics.security_score,
                    "active_threats": self.security_metrics.active_threats
                },
                "digital_trust": {
                    "trust_level": self.digital_trust.trust_level,
                    "trust_score": self.digital_trust.trust_score,
                    "is_signed": self.digital_trust.is_digitally_signed
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {}
    
    async def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export certificate data in specified format"""
        try:
            export_data = {
                "export_info": {
                    "format": format,
                    "exported_at": datetime.utcnow().isoformat(),
                    "certificate_id": self.certificate_id
                },
                "certificate_data": self.model_dump(),
                "summary": await self.generate_summary()
            }
            
            logger.info(f"Exported certificate {self.certificate_id} in {format} format")
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting certificate data: {e}")
            raise
