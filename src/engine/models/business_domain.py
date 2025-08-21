"""
Business Domain Models
======================

Pydantic models for business domain entities in the AAS Data Modeling Engine.
These models represent the core business objects: organizations, use cases, projects, files, and their relationships.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import uuid

from .base_model import BaseModel as BaseModelParent


class Organization(BaseModelParent):
    """Organization data model with comprehensive business and compliance fields."""
    
    # Required fields (no defaults)
    org_id: str = Field(..., description="Unique organization identifier")
    name: str = Field(..., description="Organization name")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    # Optional fields with defaults
    description: Optional[str] = Field(default=None, description="Organization description")
    domain: Optional[str] = Field(default=None, description="Business domain")
    contact_email: Optional[str] = Field(default=None, description="Primary contact email")
    contact_phone: Optional[str] = Field(default=None, description="Primary contact phone")
    address: Optional[str] = Field(default=None, description="Physical address")
    is_active: Optional[bool] = Field(default=True, description="Active status")
    subscription_tier: Optional[str] = Field(default="basic", description="Subscription level")
    max_users: Optional[int] = Field(default=10, description="Maximum allowed users")
    max_projects: Optional[int] = Field(default=100, description="Maximum allowed projects")
    max_storage_gb: Optional[int] = Field(default=10, description="Maximum storage in GB")
    
    # Audit & Compliance Fields
    audit_log_enabled: Optional[bool] = Field(default=True, description="Audit logging enabled")
    audit_retention_days: Optional[int] = Field(default=2555, description="Audit log retention days")
    compliance_framework: Optional[str] = Field(default="ISO27001", description="Compliance framework")
    compliance_status: Optional[str] = Field(default="pending", description="Compliance status")
    last_compliance_audit: Optional[str] = Field(default=None, description="Last compliance audit date")
    next_compliance_audit: Optional[str] = Field(default=None, description="Next compliance audit date")
    compliance_score: Optional[float] = Field(default=0.0, description="Compliance score")
    
    # Security & Access Control
    security_level: Optional[str] = Field(default="standard", description="Security level")
    mfa_required: Optional[bool] = Field(default=False, description="MFA requirement")
    session_timeout_minutes: Optional[int] = Field(default=480, description="Session timeout in minutes")
    max_failed_logins: Optional[int] = Field(default=5, description="Maximum failed login attempts")
    ip_whitelist: Optional[str] = Field(default="[]", description="IP whitelist")
    vpn_required: Optional[bool] = Field(default=False, description="VPN requirement")
    
    # Data Governance
    data_classification: Optional[str] = Field(default="internal", description="Data classification")
    data_retention_policy: Optional[str] = Field(default="{}", description="Data retention policy")
    gdpr_compliant: Optional[bool] = Field(default=False, description="GDPR compliance")
    data_processing_consent: Optional[bool] = Field(default=False, description="Data processing consent")
    data_export_restrictions: Optional[str] = Field(default="[]", description="Data export restrictions")
    
    # Operational Monitoring
    operational_status: Optional[str] = Field(default="active", description="Operational status")
    health_score: Optional[float] = Field(default=100.0, description="Health score")
    last_health_check: Optional[str] = Field(default=None, description="Last health check")
    uptime_percentage: Optional[float] = Field(default=99.9, description="Uptime percentage")
    performance_metrics: Optional[str] = Field(default="{}", description="Performance metrics")
    
    # Business Intelligence
    industry_sector: Optional[str] = Field(default=None, description="Industry sector")
    company_size: Optional[str] = Field(default="smb", description="Company size")
    annual_revenue_range: Optional[str] = Field(default="1M-10M", description="Annual revenue range")
    customer_count: Optional[int] = Field(default=0, description="Customer count")
    partner_ecosystem: Optional[str] = Field(default="[]", description="Partner ecosystem")
    
    # Advanced Tracing
    trace_id: Optional[str] = Field(default=None, description="Trace identifier")
    correlation_id: Optional[str] = Field(default=None, description="Correlation identifier")
    parent_org_id: Optional[str] = Field(default=None, description="Parent organization ID")
    subsidiary_count: Optional[int] = Field(default=0, description="Subsidiary count")
    integration_partners: Optional[str] = Field(default="[]", description="Integration partners")
    api_usage_limits: Optional[str] = Field(default="{}", description="API usage limits")

    def add_partner(self, partner: str) -> None:
        """Add a partner to the organization."""
        # This would need to be implemented based on how partners are stored
        # For now, this is a placeholder method
        pass

    def remove_partner(self, partner: str) -> None:
        """Remove a partner from the organization."""
        # This would need to be implemented based on how partners are stored
        # For now, this is a placeholder method
        pass


class Department(BaseModelParent):
    """Department data model with comprehensive organizational hierarchy fields."""
    
    # Required fields (no defaults)
    dept_id: str = Field(..., description="Unique department identifier")
    name: str = Field(..., description="Department name")
    display_name: str = Field(..., description="Human-readable display name")
    org_id: str = Field(..., description="Parent organization ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    # Optional fields with defaults
    parent_dept_id: Optional[str] = Field(default=None, description="Parent department ID")
    description: Optional[str] = Field(default=None, description="Department description")
    manager_id: Optional[str] = Field(default=None, description="Manager user ID")
    budget: Optional[float] = Field(default=0.0, description="Department budget")
    headcount: Optional[int] = Field(default=0, description="Number of employees")
    location: Optional[str] = Field(default=None, description="Physical location")
    is_active: Optional[bool] = Field(default=True, description="Active status")
    dept_type: Optional[str] = Field(default="department", description="Department type")
    status: Optional[str] = Field(default="active", description="Department status")
    metadata: Optional[str] = Field(default="{}", description="Additional metadata")
    
    # Organizational Hierarchy Fields
    hierarchy_level: Optional[int] = Field(default=1, description="Hierarchy level in organization")
    hierarchy_path: Optional[str] = Field(default="", description="Hierarchy path string")
    sort_order: Optional[int] = Field(default=0, description="Sort order for display")
    
    # Business Intelligence Fields
    cost_center: Optional[str] = Field(default=None, description="Cost center code")
    profit_center: Optional[str] = Field(default=None, description="Profit center code")
    business_unit: Optional[str] = Field(default=None, description="Business unit identifier")
    strategic_priority: Optional[str] = Field(default="medium", description="Strategic priority level")
    
    # Performance Metrics
    performance_score: Optional[float] = Field(default=0.0, description="Performance score")
    efficiency_rating: Optional[float] = Field(default=0.0, description="Efficiency rating")
    last_performance_review: Optional[str] = Field(default=None, description="Last performance review date")
    
    # Compliance & Governance
    compliance_status: Optional[str] = Field(default="pending", description="Compliance status")
    audit_frequency: Optional[str] = Field(default="annual", description="Audit frequency")
    last_audit_date: Optional[str] = Field(default=None, description="Last audit date")
    next_audit_date: Optional[str] = Field(default=None, description="Next audit date")

    @field_validator('dept_type')
    @classmethod
    def validate_dept_type(cls, v):
        """Validate department type field."""
        valid_types = ['department', 'division', 'team', 'unit', 'branch']
        if v and v not in valid_types:
            raise ValueError(f"dept_type must be one of {valid_types}")
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate department status field."""
        valid_statuses = ['active', 'inactive', 'suspended', 'merged', 'dissolved']
        if v and v not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")
        return v

    @field_validator('strategic_priority')
    @classmethod
    def validate_strategic_priority(cls, v):
        """Validate strategic priority field."""
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v and v not in valid_priorities:
            raise ValueError(f"strategic_priority must be one of {valid_priorities}")
        return v

    @field_validator('compliance_status')
    @classmethod
    def validate_compliance_status(cls, v):
        """Validate compliance status field."""
        valid_statuses = ['pending', 'compliant', 'non_compliant', 'under_review']
        if v and v not in valid_statuses:
            raise ValueError(f"compliance_status must be one of {valid_statuses}")
        return v

    @field_validator('audit_frequency')
    @classmethod
    def validate_audit_frequency(cls, v):
        """Validate audit frequency field."""
        valid_frequencies = ['monthly', 'quarterly', 'semi_annual', 'annual']
        if v and v not in valid_frequencies:
            raise ValueError(f"audit_frequency must be one of {valid_frequencies}")
        return v


class UseCase(BaseModelParent):
    """Use case data model with comprehensive governance fields."""
    
    # Required fields (no defaults)
    use_case_id: str = Field(..., description="Unique use case identifier")
    name: str = Field(..., description="Use case name")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    # Optional fields with defaults
    description: Optional[str] = Field(default=None, description="Use case description")
    category: Optional[str] = Field(default="general", description="Use case category")
    is_active: Optional[bool] = Field(default=True, description="Active status")
    metadata: Optional[str] = Field(default="{}", description="Additional metadata")
    created_by: Optional[str] = Field(default=None, description="Creator user ID")
    org_id: Optional[str] = Field(default=None, description="Organization ID")
    dept_id: Optional[str] = Field(default=None, description="Department ID")
    
    # Data Governance Fields
    data_domain: Optional[str] = Field(default="general", description="Data domain")
    business_criticality: Optional[str] = Field(default="low", description="Business criticality")
    data_volume_estimate: Optional[str] = Field(default="unknown", description="Data volume estimate")
    update_frequency: Optional[str] = Field(default="on_demand", description="Update frequency")
    retention_policy: Optional[str] = Field(default="{}", description="Retention policy")
    compliance_requirements: Optional[str] = Field(default="{}", description="Compliance requirements")
    data_owners: Optional[str] = Field(default="{}", description="Data ownership information")
    stakeholders: Optional[str] = Field(default="{}", description="Stakeholder details")

    @field_validator('data_domain')
    @classmethod
    def validate_data_domain(cls, v):
        """Validate data domain field."""
        valid_domains = ['general', 'thermal', 'structural', 'fluid_dynamics', 'electrical', 'mechanical', 'chemical', 'biological', 'environmental', 'other']
        if v and v not in valid_domains:
            raise ValueError(f"data_domain must be one of {valid_domains}")
        return v

    @field_validator('business_criticality')
    @classmethod
    def validate_business_criticality(cls, v):
        """Validate business criticality field."""
        valid_levels = ['low', 'medium', 'high', 'critical']
        if v and v not in valid_levels:
            raise ValueError(f"business_criticality must be one of {valid_levels}")
        return v

    @field_validator('data_volume_estimate')
    @classmethod
    def validate_data_volume_estimate(cls, v):
        """Validate data volume estimate field."""
        valid_estimates = ['small', 'medium', 'large', 'enterprise']
        if v and v not in valid_estimates:
            raise ValueError(f"data_volume_estimate must be one of {valid_estimates}")
        return v

    @field_validator('update_frequency')
    @classmethod
    def validate_update_frequency(cls, v):
        """Validate update frequency field."""
        valid_frequencies = ['real_time', 'hourly', 'daily', 'weekly', 'monthly', 'on_demand']
        if v and v not in valid_frequencies:
            raise ValueError(f"update_frequency must be one of {valid_frequencies}")
        return v


class Project(BaseModelParent):
    """Project data model with comprehensive governance fields."""
    
    # Required fields (no defaults)
    project_id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    # Optional fields with defaults
    description: Optional[str] = Field(default=None, description="Project description")
    tags: Optional[str] = Field(default="[]", description="Project tags")
    file_count: Optional[int] = Field(default=0, description="File count")
    total_size: Optional[int] = Field(default=0, description="Total size in bytes")
    is_public: Optional[bool] = Field(default=False, description="Public visibility")
    access_level: Optional[str] = Field(default="private", description="Access level")
    user_id: Optional[str] = Field(default=None, description="Owner user ID")
    org_id: Optional[str] = Field(default=None, description="Organization ID")
    dept_id: Optional[str] = Field(default=None, description="Department ID")
    metadata: Optional[str] = Field(default="{}", description="Additional metadata")
    
    # Project Governance Fields
    project_phase: Optional[str] = Field(default="planning", description="Project phase")
    priority_level: Optional[str] = Field(default="medium", description="Priority level")
    estimated_completion: Optional[str] = Field(default=None, description="Estimated completion date")
    actual_completion: Optional[str] = Field(default=None, description="Actual completion date")
    budget_allocation: Optional[float] = Field(default=0.0, description="Budget allocation")
    resource_requirements: Optional[str] = Field(default="{}", description="Resource requirements")
    dependencies: Optional[str] = Field(default="[]", description="Project dependencies")
    risk_mitigation: Optional[str] = Field(default="{}", description="Risk mitigation strategies")

    @field_validator('project_phase')
    @classmethod
    def validate_project_phase(cls, v):
        """Validate project phase field."""
        valid_phases = ['planning', 'development', 'testing', 'deployment', 'maintenance', 'completed', 'on_hold']
        if v and v not in valid_phases:
            raise ValueError(f"project_phase must be one of {valid_phases}")
        return v

    @field_validator('priority_level')
    @classmethod
    def validate_priority_level(cls, v):
        """Validate priority level field."""
        valid_levels = ['low', 'medium', 'high', 'critical']
        if v and v not in valid_levels:
            raise ValueError(f"priority_level must be one of {valid_levels}")
        return v

    def add_tag(self, tag: str) -> None:
        """Add a tag to the project."""
        # This would need to be implemented based on how tags are stored
        # For now, this is a placeholder method
        pass

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the project."""
        # This would need to be implemented based on how tags are stored
        # For now, this is a placeholder method
        pass

    def update_phase(self, new_phase: str) -> None:
        """Update project phase."""
        self.project_phase = new_phase
        if new_phase == "completed":
            self.actual_completion = datetime.now().isoformat()

    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.project_phase == "completed"


class File(BaseModelParent):
    """File data model with comprehensive file management fields."""
    
    # Required fields (no defaults)
    filename: str = Field(..., description="File name")
    original_filename: str = Field(..., description="Original file name")
    project_id: str = Field(..., description="Project ID")
    filepath: str = Field(..., description="File path")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    # Optional fields with defaults
    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique file identifier")
    size: int = Field(default=0, description="File size in bytes")
    description: str = Field(default="", description="File description")
    status: str = Field(default="not_processed", description="Processing status")
    file_type: str = Field(default="", description="File type")
    file_type_description: str = Field(default="", description="File type description")
    source_type: str = Field(default="manual_upload", description="Source type")
    source_url: Optional[str] = Field(default=None, description="Source URL")
    user_id: Optional[str] = Field(default=None, description="Uploader user ID")
    upload_date: Optional[str] = Field(default=None, description="Upload date")
    
    # Additional file management fields
    org_id: Optional[str] = Field(default=None, description="Organization ID")
    dept_id: Optional[str] = Field(default=None, description="Department ID")
    use_case_id: Optional[str] = Field(default=None, description="Use case ID")
    job_type: Optional[str] = Field(default=None, description="Job type")
    tags: Optional[str] = Field(default=None, description="File tags")
    metadata: Optional[Union[str, Dict[str, Any]]] = Field(default=None, description="File metadata")

    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v):
        """Validate source type field."""
        valid_types = ['manual_upload', 'url_upload']
        if v and v not in valid_types:
            raise ValueError(f"source_type must be one of {valid_types}")
        return v


class ProjectUseCaseLink(BaseModelParent):
    """Project-use case relationship model."""
    
    # Required fields (no defaults)
    project_id: str = Field(..., description="Project ID")
    use_case_id: str = Field(..., description="Use case ID")
    created_at: str = Field(..., description="Creation timestamp")
    
    # Optional fields with defaults
    id: Optional[int] = Field(default=None, description="Auto-incrementing primary key")
