"""
Organization Service
===================

Business logic for organization management in the AAS Data Modeling framework.
Handles subscription management, usage tracking, and multi-tenant operations.
"""

from typing import List, Optional, Dict, Any
from .base_service import BaseService
from ..models.organization import Organization
from ..repositories.organization_repository import OrganizationRepository
from ..repositories.user_repository import UserRepository

class OrganizationService(BaseService[Organization]):
    """Service for organization business logic."""
    
    def __init__(self, db_manager, user_repository: UserRepository):
        super().__init__(db_manager)
        self.user_repository = user_repository
    
    def get_repository(self) -> OrganizationRepository:
        """Get the organization repository."""
        return OrganizationRepository(self.db_manager)
    
    def create_organization(self, data: Dict[str, Any]) -> Organization:
        """Create a new organization with business validation."""
        # Validate business rules
        self._validate_organization_creation(data)
        
        # Create organization
        organization = self.create(data)
        
        # Post-creation: Set up default limits if not provided
        if not data.get('max_users'):
            self._set_default_limits(organization.id)
        
        return organization
    
    def get_organization_with_usage(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization with current usage statistics."""
        organization = self.get_by_id(organization_id)
        if not organization:
            return None
        
        usage = self.get_repository().get_organization_usage(organization_id)
        
        return {
            "organization": organization,
            "usage": usage,
            "is_within_limits": self._check_usage_limits(usage)
        }
    
    def update_subscription_tier(self, organization_id: str, tier: str, limits: Dict[str, int]) -> bool:
        """Update organization subscription tier with business validation."""
        # Validate the organization exists
        organization = self.get_by_id(organization_id)
        if not organization:
            self._raise_business_error(f"Organization {organization_id} not found")
        
        # Validate tier and limits
        self._validate_subscription_tier(tier, limits)
        
        # Check if new limits accommodate current usage
        current_usage = self.get_repository().get_organization_usage(organization_id)
        self._validate_limits_against_usage(limits, current_usage)
        
        # Update subscription
        success = self.get_repository().update_subscription_tier(organization_id, tier, limits)
        
        if success:
            self.logger.info(f"Updated subscription tier for organization {organization_id} to {tier}")
        
        return success
    
    def get_active_organizations(self) -> List[Organization]:
        """Get all active organizations."""
        return self.get_repository().get_active_organizations()
    
    def search_organizations(self, search_term: str) -> List[Organization]:
        """Search organizations by name, description, or domain."""
        if not search_term or len(search_term.strip()) < 2:
            self._raise_business_error("Search term must be at least 2 characters")
        
        return self.get_repository().search_organizations(search_term.strip())
    
    def get_organization_statistics(self) -> Dict[str, Any]:
        """Get comprehensive organization statistics."""
        return self.get_repository().get_organization_statistics()
    
    def check_organization_limits(self, organization_id: str) -> Dict[str, bool]:
        """Check if organization is within its limits."""
        usage = self.get_repository().get_organization_usage(organization_id)
        return self._check_usage_limits(usage)
    
    def deactivate_organization(self, organization_id: str) -> bool:
        """Deactivate an organization with business validation."""
        # Check if organization has active users
        active_users = self.user_repository.get_by_organization(organization_id)
        if active_users:
            self._raise_business_error(f"Cannot deactivate organization with {len(active_users)} active users")
        
        # Deactivate organization
        data = {"is_active": False}
        organization = self.update(organization_id, data)
        
        return organization is not None
    
    # Business Logic Validation Methods
    
    def _validate_organization_creation(self, data: Dict[str, Any]) -> None:
        """Validate organization creation business rules."""
        required_fields = ["name", "domain"]
        self._validate_required_fields(data, required_fields)
        
        # Validate name length
        self._validate_field_length(data, "name", 100)
        
        # Validate domain format
        domain = data.get("domain")
        if domain and not self._is_valid_domain(domain):
            self._raise_business_error("Invalid domain format")
        
        # Check for duplicate name
        if self.get_repository().check_name_exists(data["name"]):
            self._raise_business_error(f"Organization name '{data['name']}' already exists")
        
        # Check for duplicate domain
        if domain and self.get_repository().check_domain_exists(domain):
            self._raise_business_error(f"Domain '{domain}' already exists")
    
    def _validate_subscription_tier(self, tier: str, limits: Dict[str, int]) -> None:
        """Validate subscription tier and limits."""
        valid_tiers = ["basic", "professional", "enterprise", "custom"]
        if tier not in valid_tiers:
            self._raise_business_error(f"Invalid subscription tier. Must be one of: {', '.join(valid_tiers)}")
        
        # Validate limits
        if limits.get("max_users", 0) < 1:
            self._raise_business_error("max_users must be at least 1")
        
        if limits.get("max_projects", 0) < 1:
            self._raise_business_error("max_projects must be at least 1")
        
        if limits.get("max_storage_gb", 0) < 1:
            self._raise_business_error("max_storage_gb must be at least 1")
    
    def _validate_limits_against_usage(self, limits: Dict[str, int], usage: Dict[str, Any]) -> None:
        """Validate that new limits accommodate current usage."""
        if usage["user_count"] > limits.get("max_users", 0):
            self._raise_business_error(f"Current user count ({usage['user_count']}) exceeds new limit ({limits.get('max_users', 0)})")
        
        if usage["project_count"] > limits.get("max_projects", 0):
            self._raise_business_error(f"Current project count ({usage['project_count']}) exceeds new limit ({limits.get('max_projects', 0)})")
        
        if usage["total_storage_gb"] > limits.get("max_storage_gb", 0):
            self._raise_business_error(f"Current storage usage ({usage['total_storage_gb']}GB) exceeds new limit ({limits.get('max_storage_gb', 0)}GB)")
    
    def _check_usage_limits(self, usage: Dict[str, Any]) -> Dict[str, bool]:
        """Check if usage is within limits."""
        return {
            "users_within_limit": usage["user_usage_percent"] <= 100,
            "projects_within_limit": usage["project_usage_percent"] <= 100,
            "storage_within_limit": usage["storage_usage_percent"] <= 100,
            "overall_within_limit": all([
                usage["user_usage_percent"] <= 100,
                usage["project_usage_percent"] <= 100,
                usage["storage_usage_percent"] <= 100
            ])
        }
    
    def _set_default_limits(self, organization_id: str) -> None:
        """Set default limits for new organization."""
        default_limits = {
            "max_users": 10,
            "max_projects": 100,
            "max_storage_gb": 10
        }
        self.get_repository().update_subscription_tier(organization_id, "basic", default_limits)
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format."""
        import re
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, domain))
    
    # Override base methods for organization-specific logic
    
    def _validate_delete(self, entity_id: str) -> None:
        """Validate organization deletion."""
        # Check if organization has any users
        users = self.user_repository.get_by_organization(entity_id)
        if users:
            self._raise_business_error(f"Cannot delete organization with {len(users)} users")
    
    def _post_delete(self, entity_id: str) -> None:
        """Post-deletion cleanup for organizations."""
        # Log organization deletion for audit
        self.logger.warning(f"Organization {entity_id} deleted - audit trail required") 