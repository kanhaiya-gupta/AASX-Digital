"""
Organization Model
=================

Data model for organizations in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any
from .base_model import BaseModel
from pydantic import Field
import uuid

class Organization(BaseModel):
    """Organization data model with world-class tracing capabilities."""
    
    org_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique organization identifier")
    name: str = Field(..., description="Organization name")
    description: str = Field(default="", description="Organization description")
    domain: Optional[str] = Field(default=None, description="Organization domain")
    contact_email: Optional[str] = Field(default=None, description="Contact email")
    contact_phone: Optional[str] = Field(default=None, description="Contact phone")
    address: Optional[str] = Field(default=None, description="Organization address")
    is_active: bool = Field(default=True, description="Organization active status")
    subscription_tier: str = Field(default="basic", description="Subscription tier")
    max_users: int = Field(default=10, description="Maximum users allowed")
    max_projects: int = Field(default=100, description="Maximum projects allowed")
    max_storage_gb: int = Field(default=10, description="Maximum storage in GB")
    
    # Audit & Compliance Fields
    audit_log_enabled: bool = Field(default=True, description="Enable audit logging")
    audit_retention_days: int = Field(default=2555, description="Audit log retention period in days")
    compliance_framework: str = Field(default="ISO27001", description="Compliance framework")
    compliance_status: str = Field(default="pending", description="Compliance status")
    last_compliance_audit: Optional[str] = Field(default=None, description="Last compliance audit date")
    next_compliance_audit: Optional[str] = Field(default=None, description="Next compliance audit date")
    compliance_score: float = Field(default=0.0, description="Compliance score (0-100)")
    
    # Security & Access Control
    security_level: str = Field(default="standard", description="Security level")
    mfa_required: bool = Field(default=False, description="Multi-factor authentication required")
    session_timeout_minutes: int = Field(default=480, description="Session timeout in minutes")
    max_failed_logins: int = Field(default=5, description="Maximum failed login attempts")
    ip_whitelist: str = Field(default="[]", description="IP whitelist (JSON string)")
    vpn_required: bool = Field(default=False, description="VPN access required")
    
    # Data Governance
    data_classification: str = Field(default="internal", description="Data classification level")
    data_retention_policy: str = Field(default="{}", description="Data retention policy (JSON)")
    gdpr_compliant: bool = Field(default=False, description="GDPR compliance status")
    data_processing_consent: bool = Field(default=False, description="Data processing consent")
    data_export_restrictions: str = Field(default="[]", description="Data export restrictions (JSON)")
    
    # Operational Monitoring
    operational_status: str = Field(default="active", description="Operational status")
    health_score: float = Field(default=100.0, description="Health score (0-100)")
    last_health_check: Optional[str] = Field(default=None, description="Last health check date")
    uptime_percentage: float = Field(default=99.9, description="Uptime percentage")
    performance_metrics: str = Field(default="{}", description="Performance metrics (JSON)")
    
    # Business Intelligence
    industry_sector: Optional[str] = Field(default=None, description="Industry sector")
    company_size: str = Field(default="smb", description="Company size category")
    annual_revenue_range: str = Field(default="1M-10M", description="Annual revenue range")
    customer_count: int = Field(default=0, description="Number of customers")
    partner_ecosystem: str = Field(default="[]", description="Partner ecosystem (JSON)")
    
    # Advanced Tracing
    trace_id: Optional[str] = Field(default=None, description="Trace identifier")
    correlation_id: Optional[str] = Field(default=None, description="Correlation identifier")
    parent_org_id: Optional[str] = Field(default=None, description="Parent organization ID")
    subsidiary_count: int = Field(default=0, description="Number of subsidiaries")
    integration_partners: str = Field(default="[]", description="Integration partners (JSON)")
    api_usage_limits: str = Field(default="{}", description="API usage limits (JSON)")
    
    def validate(self) -> bool:
        """Validate organization data with world-class tracing fields."""
        if not self.name or not self.name.strip():
            raise ValueError("Organization name is required")
        
        if len(self.name) > 255:
            raise ValueError("Organization name must be less than 255 characters")
        
        if len(self.description) > 1000:
            raise ValueError("Organization description must be less than 1000 characters")
        
        if self.contact_email and len(self.contact_email) > 255:
            raise ValueError("Contact email must be less than 255 characters")
        
        if self.contact_phone and len(self.contact_phone) > 20:
            raise ValueError("Contact phone must be less than 20 characters")
        
        if self.address and len(self.address) > 500:
            raise ValueError("Address must be less than 500 characters")
        
        valid_tiers = ["basic", "professional", "enterprise", "custom"]
        if self.subscription_tier not in valid_tiers:
            raise ValueError(f"Subscription tier must be one of: {valid_tiers}")
        
        if self.max_users < 1:
            raise ValueError("Max users must be at least 1")
        
        if self.max_projects < 1:
            raise ValueError("Max projects must be at least 1")
        
        if self.max_storage_gb < 1:
            raise ValueError("Max storage must be at least 1 GB")
        
        # Validate new tracing fields
        valid_compliance_frameworks = ["ISO27001", "SOC2", "GDPR", "HIPAA", "PCI-DSS", "NIST", "custom"]
        if self.compliance_framework not in valid_compliance_frameworks:
            raise ValueError(f"Compliance framework must be one of: {valid_compliance_frameworks}")
        
        valid_compliance_statuses = ["pending", "compliant", "non_compliant", "under_review", "exempt"]
        if self.compliance_status not in valid_compliance_statuses:
            raise ValueError(f"Compliance status must be one of: {valid_compliance_statuses}")
        
        valid_security_levels = ["standard", "enhanced", "enterprise", "government", "military"]
        if self.security_level not in valid_security_levels:
            raise ValueError(f"Security level must be one of: {valid_security_levels}")
        
        valid_data_classifications = ["public", "internal", "confidential", "restricted", "top_secret"]
        if self.data_classification not in valid_data_classifications:
            raise ValueError(f"Data classification must be one of: {valid_data_classifications}")
        
        valid_operational_statuses = ["active", "maintenance", "suspended", "archived", "decommissioned"]
        if self.operational_status not in valid_operational_statuses:
            raise ValueError(f"Operational status must be one of: {valid_operational_statuses}")
        
        valid_company_sizes = ["startup", "smb", "mid_market", "enterprise", "government"]
        if self.company_size not in valid_company_sizes:
            raise ValueError(f"Company size must be one of: {valid_company_sizes}")
        
        valid_revenue_ranges = ["<1M", "1M-10M", "10M-100M", "100M-1B", ">1B"]
        if self.annual_revenue_range not in valid_revenue_ranges:
            raise ValueError(f"Annual revenue range must be one of: {valid_revenue_ranges}")
        
        if self.audit_retention_days < 0 or self.audit_retention_days > 36500:  # Max 100 years
            raise ValueError("Audit retention days must be between 0 and 36500")
        
        if self.session_timeout_minutes < 1 or self.session_timeout_minutes > 1440:  # Max 24 hours
            raise ValueError("Session timeout must be between 1 and 1440 minutes")
        
        if self.max_failed_logins < 1 or self.max_failed_logins > 100:
            raise ValueError("Max failed logins must be between 1 and 100")
        
        if self.health_score < 0.0 or self.health_score > 100.0:
            raise ValueError("Health score must be between 0.0 and 100.0")
        
        if self.uptime_percentage < 0.0 or self.uptime_percentage > 100.0:
            raise ValueError("Uptime percentage must be between 0.0 and 100.0")
        
        if self.compliance_score < 0.0 or self.compliance_score > 100.0:
            raise ValueError("Compliance score must be between 0.0 and 100.0")
        
        if self.customer_count < 0:
            raise ValueError("Customer count must be non-negative")
        
        if self.subsidiary_count < 0:
            raise ValueError("Subsidiary count must be non-negative")
        
        return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get organization usage statistics and tracing metrics."""
        return {
            "subscription_tier": self.subscription_tier,
            "max_users": self.max_users,
            "max_projects": self.max_projects,
            "max_storage_gb": self.max_storage_gb,
            "is_active": self.is_active,
            
            # Tracing & Compliance Stats
            "compliance_score": self.compliance_score,
            "health_score": self.health_score,
            "uptime_percentage": self.uptime_percentage,
            "operational_status": self.operational_status,
            "security_level": self.security_level,
            "audit_log_enabled": self.audit_log_enabled,
            "mfa_required": self.mfa_required,
            "gdpr_compliant": self.gdpr_compliant,
            
            # Business Metrics
            "company_size": self.company_size,
            "annual_revenue_range": self.annual_revenue_range,
            "customer_count": self.customer_count,
            "subsidiary_count": self.subsidiary_count
        }
    
    def get_tracing_summary(self) -> Dict[str, Any]:
        """Get comprehensive tracing and compliance summary."""
        return {
            "audit": {
                "enabled": self.audit_log_enabled,
                "retention_days": self.audit_retention_days,
                "framework": self.compliance_framework,
                "status": self.compliance_status,
                "score": self.compliance_score,
                "last_audit": self.last_compliance_audit,
                "next_audit": self.next_compliance_audit
            },
            "security": {
                "level": self.security_level,
                "mfa_required": self.mfa_required,
                "session_timeout": self.session_timeout_minutes,
                "max_failed_logins": self.max_failed_logins,
                "vpn_required": self.vpn_required,
                "ip_whitelist": self.ip_whitelist
            },
            "data_governance": {
                "classification": self.data_classification,
                "gdpr_compliant": self.gdpr_compliant,
                "processing_consent": self.data_processing_consent,
                "retention_policy": self.data_retention_policy,
                "export_restrictions": self.data_export_restrictions
            },
            "operational": {
                "status": self.operational_status,
                "health_score": self.health_score,
                "uptime": self.uptime_percentage,
                "last_health_check": self.last_health_check,
                "performance_metrics": self.performance_metrics
            },
            "business": {
                "sector": self.industry_sector,
                "size": self.company_size,
                "revenue_range": self.annual_revenue_range,
                "customers": self.customer_count,
                "partners": self.partner_ecosystem,
                "subsidiaries": self.subsidiary_count
            },
            "tracing": {
                "trace_id": self.trace_id,
                "correlation_id": self.correlation_id,
                "parent_org": self.parent_org_id,
                "integration_partners": self.integration_partners,
                "api_limits": self.api_usage_limits
            }
        }
    
    def is_high_security(self) -> bool:
        """Check if organization requires high security measures."""
        return self.security_level in ["enterprise", "government", "military"]
    
    def is_compliant(self) -> bool:
        """Check if organization is compliant with its framework."""
        return self.compliance_status == "compliant"
    
    def needs_audit_review(self) -> bool:
        """Check if organization needs compliance audit review."""
        return self.compliance_status in ["pending", "under_review", "non_compliant"]
    
    def get_risk_level(self) -> str:
        """Calculate organization risk level based on various factors."""
        risk_score = 0
        
        # Security factors
        if not self.mfa_required:
            risk_score += 20
        if self.security_level == "standard":
            risk_score += 15
        if not self.vpn_required:
            risk_score += 10
            
        # Compliance factors
        if not self.is_compliant():
            risk_score += 25
        if self.compliance_score < 70:
            risk_score += 20
            
        # Operational factors
        if self.health_score < 80:
            risk_score += 15
        if self.uptime_percentage < 99:
            risk_score += 10
            
        # Data sensitivity
        if self.data_classification in ["confidential", "restricted", "top_secret"]:
            risk_score += 20
            
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 40:
            return "medium"
        elif risk_score >= 20:
            return "low"
        else:
            return "minimal" 