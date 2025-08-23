"""
Use Case Model
==============

Data model for use cases in the AAS Data Modeling framework.
"""

from typing import Optional, List, Dict, Any
from .base_model import BaseModel
from pydantic import Field
import json
import uuid

class UseCase(BaseModel):
    """Use case data model with comprehensive governance and management fields."""
    
    use_case_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique use case identifier")
    name: str = Field(..., description="Use case name")
    description: str = Field(default="", description="Use case description")
    category: str = Field(default="general", description="Use case category")
    is_active: bool = Field(default=True, description="Active status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Use case metadata")
    
    # Data Governance Fields
    data_domain: str = Field(default="general", description="Data domain classification")
    business_criticality: str = Field(default="low", description="Business criticality level")
    data_volume_estimate: str = Field(default="unknown", description="Estimated data volume")
    update_frequency: str = Field(default="on_demand", description="Data update frequency")
    retention_policy: Dict[str, Any] = Field(default_factory=dict, description="Data retention policies")
    compliance_requirements: Dict[str, Any] = Field(default_factory=dict, description="Compliance requirements")
    data_owners: Dict[str, Any] = Field(default_factory=dict, description="Data ownership information")
    stakeholders: Dict[str, Any] = Field(default_factory=dict, description="Stakeholder details")
    
    def validate(self) -> bool:
        """Validate use case data."""
        if not self.name or not self.name.strip():
            raise ValueError("Use case name is required")
        
        if len(self.name) > 255:
            raise ValueError("Use case name must be less than 255 characters")
        
        if len(self.description) > 1000:
            raise ValueError("Use case description must be less than 1000 characters")
        
        valid_categories = ["thermal", "structural", "fluid_dynamics", "multi_physics", "industrial", "general", 
                           "environmental", "advanced_analytics", "iot_analytics", "manufacturing", 
                           "quality_control", "supply_chain"]
        if self.category not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        
        # Validate governance fields
        valid_domains = ["general", "thermal", "structural", "fluid_dynamics", "electrical", "mechanical", 
                        "chemical", "biological", "environmental", "other"]
        if self.data_domain not in valid_domains:
            raise ValueError(f"Data domain must be one of: {valid_domains}")
        
        valid_criticality = ["low", "medium", "high", "critical"]
        if self.business_criticality not in valid_criticality:
            raise ValueError(f"Business criticality must be one of: {valid_criticality}")
        
        valid_volumes = ["small", "medium", "large", "enterprise"]
        if self.data_volume_estimate not in valid_volumes:
            raise ValueError(f"Data volume estimate must be one of: {valid_volumes}")
        
        valid_frequencies = ["real_time", "hourly", "daily", "weekly", "monthly", "on_demand"]
        if self.update_frequency not in valid_frequencies:
            raise ValueError(f"Update frequency must be one of: {valid_frequencies}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        # Map use_case_id to the database column name
        if self.use_case_id:
            data['use_case_id'] = self.use_case_id
        data['metadata'] = json.dumps(self.metadata) if self.metadata else "{}"
        
        # Handle JSON fields for governance data
        data['retention_policy'] = json.dumps(self.retention_policy) if self.retention_policy else "{}"
        data['compliance_requirements'] = json.dumps(self.compliance_requirements) if self.compliance_requirements else "{}"
        data['data_owners'] = json.dumps(self.data_owners) if self.data_owners else "{}"
        data['stakeholders'] = json.dumps(self.stakeholders) if self.stakeholders else "{}"
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UseCase':
        """Create from dictionary from database."""
        # Parse metadata JSON
        if 'metadata' in data and isinstance(data['metadata'], str):
            try:
                data['metadata'] = json.loads(data['metadata'])
            except json.JSONDecodeError:
                data['metadata'] = {}
        
        # Parse governance JSON fields
        json_fields = ['retention_policy', 'compliance_requirements', 'data_owners', 'stakeholders']
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    data[field] = {}
        
        return super().from_dict(data) 