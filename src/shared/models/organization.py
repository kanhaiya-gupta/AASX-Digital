"""
Organization Model
=================

Data model for organizations in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from .base_model import BaseModel
import uuid

@dataclass
class Organization(BaseModel):
    """Organization data model."""
    
    org_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    name: str
    description: str = ""
    domain: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    subscription_tier: str = "basic"
    max_users: int = 10
    max_projects: int = 100
    max_storage_gb: int = 10
    
    def validate(self) -> bool:
        """Validate organization data."""
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
        
        return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get organization usage statistics."""
        return {
            "subscription_tier": self.subscription_tier,
            "max_users": self.max_users,
            "max_projects": self.max_projects,
            "max_storage_gb": self.max_storage_gb,
            "is_active": self.is_active
        } 