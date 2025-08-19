"""
Governance Policy Model
======================

Data model for managing data governance policies in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any, List
from .base_model import BaseModel
from pydantic import Field
import json
import uuid
from datetime import datetime

class GovernancePolicy(BaseModel):
    """Governance policy model for managing data governance policies."""
    
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique policy identifier")
    policy_name: str = Field(..., description="Policy name")
    policy_type: str = Field(..., description="Type of governance policy")
    policy_category: str = Field(..., description="Policy category and priority")
    
    # Policy Content
    policy_description: str = Field(..., description="Detailed policy description")
    policy_rules: Dict[str, Any] = Field(default_factory=dict, description="Specific policy rules")
    policy_conditions: List[str] = Field(default_factory=list, description="Conditions when policy applies")
    policy_actions: List[str] = Field(default_factory=list, description="Actions to take when policy is violated")
    
    # Policy Scope
    applicable_entities: List[str] = Field(default_factory=list, description="Entity types this policy applies to")
    applicable_organizations: List[str] = Field(default_factory=list, description="Organizations this policy applies to")
    applicable_users: List[str] = Field(default_factory=list, description="Users this policy applies to")
    geographic_scope: str = Field(default="global", description="Geographic scope of policy")
    
    # Policy Enforcement
    enforcement_level: str = Field(default="monitor", description="Level of policy enforcement")
    compliance_required: bool = Field(default=True, description="Whether compliance is required")
    audit_required: bool = Field(default=True, description="Whether auditing is required")
    auto_remediation: bool = Field(default=False, description="Whether automatic remediation is enabled")
    
    # Policy Status
    status: str = Field(default="draft", description="Current policy status")
    effective_date: Optional[str] = Field(default=None, description="When policy becomes effective")
    expiry_date: Optional[str] = Field(default=None, description="When policy expires")
    review_frequency: str = Field(default="monthly", description="How often to review policy")
    
    # Policy Ownership
    policy_owner: str = Field(..., description="User responsible for policy")
    policy_stewards: List[str] = Field(default_factory=list, description="Users who can modify policy")
    approval_required: bool = Field(default=True, description="Whether approval is required")
    approved_by: Optional[str] = Field(default=None, description="User who approved the policy")
    approval_date: Optional[str] = Field(default=None, description="Policy approval date")
    
    # Policy Metrics
    compliance_rate: float = Field(default=0.0, description="Current compliance rate")
    violation_count: int = Field(default=0, description="Number of violations")
    last_compliance_check: Optional[str] = Field(default=None, description="Last compliance check date")
    compliance_trend: Dict[str, Any] = Field(default_factory=dict, description="Compliance trend over time")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional information")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    
    def validate(self) -> bool:
        """Validate governance policy data."""
        valid_policy_types = ["data_classification", "access_control", "retention", "compliance", "quality", "lineage"]
        if self.policy_type not in valid_policy_types:
            raise ValueError(f"Policy type must be one of: {valid_policy_types}")
        
        valid_categories = ["mandatory", "recommended", "optional", "deprecated"]
        if self.policy_category not in valid_categories:
            raise ValueError(f"Policy category must be one of: {valid_categories}")
        
        valid_enforcement_levels = ["monitor", "warn", "block", "auto_correct"]
        if self.enforcement_level not in valid_enforcement_levels:
            raise ValueError(f"Enforcement level must be one of: {valid_enforcement_levels}")
        
        valid_statuses = ["draft", "active", "suspended", "deprecated", "archived"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        
        valid_review_frequencies = ["daily", "weekly", "monthly", "quarterly", "annually", "on_demand"]
        if self.review_frequency not in valid_review_frequencies:
            raise ValueError(f"Review frequency must be one of: {valid_review_frequencies}")
        
        if not self.policy_name or not self.policy_name.strip():
            raise ValueError("Policy name is required")
        
        if not self.policy_description or not self.policy_description.strip():
            raise ValueError("Policy description is required")
        
        if not self.policy_owner:
            raise ValueError("Policy owner is required")
        
        if len(self.policy_name) > 255:
            raise ValueError("Policy name must be less than 255 characters")
        
        if len(self.policy_description) > 2000:
            raise ValueError("Policy description must be less than 2000 characters")
        
        if self.compliance_rate < 0.0 or self.compliance_rate > 100.0:
            raise ValueError("Compliance rate must be between 0.0 and 100.0")
        
        if self.violation_count < 0:
            raise ValueError("Violation count cannot be negative")
        
        return True
    
    def is_active(self) -> bool:
        """Check if policy is currently active."""
        if self.status != "active":
            return False
        
        current_time = datetime.now().isoformat()
        
        if self.effective_date and current_time < self.effective_date:
            return False
        
        if self.expiry_date and current_time > self.expiry_date:
            return False
        
        return True
    
    def is_applicable_to_entity(self, entity_type: str, organization_id: str = None, user_id: str = None) -> bool:
        """Check if policy applies to a specific entity."""
        if not self.is_active():
            return False
        
        # Check entity type
        if entity_type not in self.applicable_entities:
            return False
        
        # Check organization scope
        if self.applicable_organizations and organization_id not in self.applicable_organizations:
            return False
        
        # Check user scope
        if self.applicable_users and user_id not in self.applicable_users:
            return False
        
        return True
    
    def can_user_modify(self, user_id: str) -> bool:
        """Check if a user can modify this policy."""
        return user_id == self.policy_owner or user_id in self.policy_stewards
    
    def update_compliance_rate(self, new_rate: float, check_date: str = None) -> None:
        """Update compliance rate and tracking information."""
        if new_rate < 0.0 or new_rate > 100.0:
            raise ValueError("Compliance rate must be between 0.0 and 100.0")
        
        self.compliance_rate = new_rate
        self.last_compliance_check = check_date or datetime.now().isoformat()
        
        # Update compliance trend
        if "history" not in self.compliance_trend:
            self.compliance_trend["history"] = []
        
        self.compliance_trend["history"].append({
            "date": self.last_compliance_check,
            "rate": new_rate,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 entries
        if len(self.compliance_trend["history"]) > 100:
            self.compliance_trend["history"] = self.compliance_trend["history"][-100:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        
        # Handle JSON fields
        data['policy_rules'] = json.dumps(self.policy_rules) if self.policy_rules else "{}"
        data['policy_conditions'] = json.dumps(self.policy_conditions) if self.policy_conditions else "[]"
        data['policy_actions'] = json.dumps(self.policy_actions) if self.policy_actions else "[]"
        data['applicable_entities'] = json.dumps(self.applicable_entities) if self.applicable_entities else "[]"
        data['applicable_organizations'] = json.dumps(self.applicable_organizations) if self.applicable_organizations else "[]"
        data['applicable_users'] = json.dumps(self.applicable_users) if self.applicable_users else "[]"
        data['policy_stewards'] = json.dumps(self.policy_stewards) if self.policy_stewards else "[]"
        data['compliance_trend'] = json.dumps(self.compliance_trend) if self.compliance_trend else "{}"
        data['tags'] = json.dumps(self.tags) if self.tags else "[]"
        data['metadata'] = json.dumps(self.metadata) if self.metadata else "{}"
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GovernancePolicy':
        """Create from dictionary from database."""
        # Parse JSON fields
        json_fields = [
            'policy_rules', 'policy_conditions', 'policy_actions', 'applicable_entities',
            'applicable_organizations', 'applicable_users', 'policy_stewards',
            'compliance_trend', 'tags', 'metadata'
        ]
        
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    if field in ['policy_conditions', 'policy_actions', 'applicable_entities', 
                               'applicable_organizations', 'applicable_users', 'policy_stewards', 'tags']:
                        data[field] = []
                    else:
                        data[field] = {}
        
        return super().from_dict(data)
