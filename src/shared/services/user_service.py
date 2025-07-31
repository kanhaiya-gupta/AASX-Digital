"""
User Service
===========

Business logic for user management in the AAS Data Modeling framework.
Handles authentication, permissions, and organization relationships.
"""

from typing import List, Optional, Dict, Any
from .base_service import BaseService
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..repositories.organization_repository import OrganizationRepository

class UserService(BaseService[User]):
    """Service for user business logic."""
    
    def __init__(self, db_manager, organization_repository: OrganizationRepository):
        super().__init__(db_manager)
        self.organization_repository = organization_repository
    
    def get_repository(self) -> UserRepository:
        """Get the user repository."""
        return UserRepository(self.db_manager)
    
    def create_user(self, data: Dict[str, Any]) -> User:
        """Create a new user with business validation."""
        # Validate business rules
        self._validate_user_creation(data)
        
        # Create user
        user = self.create(data)
        
        # Update last login
        user.update_last_login()
        
        self.logger.info(f"Created user: {user.username} in organization: {user.organization_id}")
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        # Get user by username
        user = self.get_repository().get_by_username(username)
        if not user:
            return None
        
        # Validate password (in real implementation, this would hash and compare)
        if not self._validate_password(password, user):
            return None
        
        # Update last login
        user.update_last_login()
        self.get_repository().update_last_login(user.id)
        
        self.logger.info(f"User {username} authenticated successfully")
        return user
    
    def get_user_with_permissions(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user with permission information."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        # Get organization information
        organization = None
        if user.organization_id:
            organization = self.organization_repository.get_by_id(user.organization_id)
        
        # Check permissions
        permissions = {
            "can_read": user.has_permission("read"),
            "can_write": user.has_permission("write"),
            "can_admin": user.has_permission("admin"),
            "can_manage_users": user.has_permission("manage_users"),
            "can_manage_organizations": user.has_permission("manage_organizations")
        }
        
        return {
            "user": user,
            "organization": organization,
            "permissions": permissions
        }
    
    def get_users_by_organization(self, organization_id: str) -> List[User]:
        """Get all users in an organization."""
        # Validate organization exists
        if not self.organization_repository.get_by_id(organization_id):
            self._raise_business_error(f"Organization {organization_id} not found")
        
        return self.get_repository().get_by_organization(organization_id)
    
    def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role."""
        valid_roles = ["user", "admin", "super_admin"]
        if role not in valid_roles:
            self._raise_business_error(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        return self.get_repository().get_by_role(role)
    
    def update_user_role(self, user_id: str, new_role: str) -> bool:
        """Update user role with business validation."""
        # Validate user exists
        user = self.get_by_id(user_id)
        if not user:
            self._raise_business_error(f"User {user_id} not found")
        
        # Validate role
        valid_roles = ["user", "admin", "super_admin"]
        if new_role not in valid_roles:
            self._raise_business_error(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Update role
        update_data = {"role": new_role}
        success = self.update(user_id, update_data)
        
        if success:
            self.logger.info(f"Updated user {user.username} role to: {new_role}")
        
        return success
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user."""
        # Validate user exists
        user = self.get_by_id(user_id)
        if not user:
            self._raise_business_error(f"User {user_id} not found")
        
        # Deactivate user
        update_data = {"is_active": False}
        success = self.update(user_id, update_data)
        
        if success:
            self.logger.warning(f"Deactivated user: {user.username}")
        
        return success
    
    def search_users(self, search_term: str, organization_id: Optional[str] = None) -> List[User]:
        """Search users with optional organization filtering."""
        if not search_term or len(search_term.strip()) < 2:
            self._raise_business_error("Search term must be at least 2 characters")
        
        users = self.get_repository().search_users(search_term.strip())
        
        # Filter by organization if specified
        if organization_id:
            if not self.organization_repository.get_by_id(organization_id):
                self._raise_business_error(f"Organization {organization_id} not found")
            users = [u for u in users if u.organization_id == organization_id]
        
        return users
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return self.get_repository().get_active_users()
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        return self.get_repository().get_user_statistics()
    
    def check_user_permissions(self, user_id: str, required_permission: str) -> bool:
        """Check if user has a specific permission."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        return user.has_permission(required_permission)
    
    def validate_user_access_to_project(self, user_id: str, project_id: str) -> bool:
        """Validate if user has access to a specific project."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        # Super admins have access to all projects
        if user.has_permission("admin"):
            return True
        
        # For regular users, check if they own the project or it's public
        # This would require project repository integration
        # For now, return True (implement based on your access control logic)
        return True
    
    # Business Logic Validation Methods
    
    def _validate_user_creation(self, data: Dict[str, Any]) -> None:
        """Validate user creation business rules."""
        required_fields = ["username", "email", "full_name"]
        self._validate_required_fields(data, required_fields)
        
        # Validate username length
        self._validate_field_length(data, "username", 50)
        
        # Validate email format
        email = data.get("email")
        if email and not self._is_valid_email(email):
            self._raise_business_error("Invalid email format")
        
        # Check for duplicate username
        if self.get_repository().check_username_exists(data["username"]):
            self._raise_business_error(f"Username '{data['username']}' already exists")
        
        # Check for duplicate email
        if email and self.get_repository().check_email_exists(email):
            self._raise_business_error(f"Email '{email}' already exists")
        
        # Validate organization if provided
        organization_id = data.get("organization_id")
        if organization_id:
            if not self.organization_repository.get_by_id(organization_id):
                self._raise_business_error(f"Organization {organization_id} not found")
    
    def _validate_password(self, password: str, user: User) -> bool:
        """Validate user password."""
        # In a real implementation, this would:
        # 1. Hash the provided password
        # 2. Compare with stored hash
        # 3. Check password complexity requirements
        
        # For now, we'll implement a simple check
        # In production, use proper password hashing (bcrypt, etc.)
        return len(password) >= 8
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def _validate_username_format(self, username: str) -> bool:
        """Validate username format."""
        import re
        # Username should be alphanumeric with underscores, 3-50 characters
        username_pattern = r'^[a-zA-Z0-9_]{3,50}$'
        return bool(re.match(username_pattern, username))
    
    # Override base methods for user-specific logic
    
    def _validate_create(self, data: Dict[str, Any]) -> None:
        """Validate user creation."""
        self._validate_user_creation(data)
    
    def _validate_update(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Validate user update."""
        # Check if user exists
        user = self.get_by_id(entity_id)
        if not user:
            self._raise_business_error(f"User {entity_id} not found")
        
        # Validate username if being updated
        if "username" in data:
            self._validate_field_length(data, "username", 50)
            if not self._validate_username_format(data["username"]):
                self._raise_business_error("Invalid username format")
            
            # Check for duplicate username (excluding current user)
            if self.get_repository().check_username_exists(data["username"]):
                existing_user = self.get_repository().get_by_username(data["username"])
                if existing_user and existing_user.id != entity_id:
                    self._raise_business_error(f"Username '{data['username']}' already exists")
        
        # Validate email if being updated
        if "email" in data:
            if not self._is_valid_email(data["email"]):
                self._raise_business_error("Invalid email format")
            
            # Check for duplicate email (excluding current user)
            if self.get_repository().check_email_exists(data["email"]):
                existing_user = self.get_repository().get_by_email(data["email"])
                if existing_user and existing_user.id != entity_id:
                    self._raise_business_error(f"Email '{data['email']}' already exists")
    
    def _validate_delete(self, entity_id: str) -> None:
        """Validate user deletion."""
        # Check if user exists
        user = self.get_by_id(entity_id)
        if not user:
            self._raise_business_error(f"User {entity_id} not found")
        
        # Check if user is the last admin in organization
        if user.role == "admin" and user.organization_id:
            admin_users = self.get_repository().get_by_role("admin")
            org_admins = [u for u in admin_users if u.organization_id == user.organization_id]
            if len(org_admins) <= 1:
                self._raise_business_error("Cannot delete the last admin user in an organization")
    
    def _post_create(self, entity: User) -> None:
        """Post-creation logic for users."""
        self.logger.info(f"User '{entity.username}' created")
    
    def _post_update(self, entity: User) -> None:
        """Post-update logic for users."""
        self.logger.info(f"User '{entity.username}' updated")
    
    def _post_delete(self, entity_id: str) -> None:
        """Post-deletion logic for users."""
        self.logger.warning(f"User {entity_id} deleted - audit trail required") 