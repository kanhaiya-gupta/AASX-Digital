"""
Custom Role Integration Service - Soft Connection to Backend
==========================================================

Thin integration layer that connects webapp to backend custom role services.
Handles frontend-specific logic while delegating role management to backend.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import from backend engine
from src.engine.services.auth.role_service import RoleService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class CustomRoleService:
    """Integration service for custom role operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._auth_repo = None
        self._role_service = None
        
        logger.info("✅ Custom role integration service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._role_service = RoleService(self._auth_repo)
            
            self._initialized = True
            logger.info("✅ Custom role integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize custom role integration service: {e}")
            raise
    
    @property
    def auth_repo(self):
        """Get auth repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_repo
    
    @property
    def role_service(self):
        """Get role service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._role_service
    
    async def get_custom_roles_by_organization(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get custom roles for an organization via backend"""
        await self._ensure_initialized()
        try:
            # Get all roles and filter for custom roles in the organization
            all_roles = await self.role_service.get_all_roles()
            custom_roles = []
            
            for role in all_roles:
                if (hasattr(role, 'role_type') and role.role_type == 'custom' and
                    hasattr(role, 'organization_id') and role.organization_id == organization_id):
                    
                    custom_roles.append({
                        "role_id": role.role_id,
                        "role_name": role.role_name,
                        "role_description": getattr(role, 'role_description', ''),
                        "role_level": getattr(role, 'role_level', 1),
                        "is_active": getattr(role, 'is_active', True),
                        "organization_id": role.organization_id,
                        "created_at": getattr(role, 'created_at', None),
                        "updated_at": getattr(role, 'updated_at', None),
                        "created_by": getattr(role, 'created_by', None),
                        "updated_by": getattr(role, 'updated_by', None),
                        "role_metadata": self._parse_json_field(getattr(role, 'role_metadata', '{}'))
                    })
            
            return custom_roles
            
        except Exception as e:
            logger.error(f"Error getting custom roles for organization {organization_id}: {e}")
            return []
    
    async def get_custom_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific custom role via backend"""
        await self._ensure_initialized()
        try:
            role = await self.role_service.get_role_by_id(role_id)
            if not role:
                return None
            
            # Check if it's a custom role
            if not (hasattr(role, 'role_type') and role.role_type == 'custom'):
                logger.warning(f"Role {role_id} is not a custom role")
                return None
            
            return {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "role_description": getattr(role, 'role_description', ''),
                "role_type": role.role_type,
                "role_level": getattr(role, 'role_level', 1),
                "is_active": getattr(role, 'is_active', True),
                "organization_id": getattr(role, 'organization_id', None),
                "created_at": getattr(role, 'created_at', None),
                "updated_at": getattr(role, 'updated_at', None),
                "created_by": getattr(role, 'created_by', None),
                "updated_by": getattr(role, 'updated_by', None),
                "role_metadata": self._parse_json_field(getattr(role, 'role_metadata', '{}'))
            }
            
        except Exception as e:
            logger.error(f"Error getting custom role {role_id}: {e}")
            return None
    
    async def create_custom_role(self, organization_id: str, role_data: Dict[str, Any]) -> Optional[str]:
        """Create a custom role via backend"""
        await self._ensure_initialized()
        try:
            # Validate role data
            validated_data = self._validate_role_data(role_data)
            
            # Prepare role data for creation
            role_create_data = {
                "role_name": validated_data["role_name"],
                "role_type": "custom",
                "role_description": validated_data.get("role_description", ""),
                "role_level": validated_data.get("role_level", 1),
                "is_active": validated_data.get("is_active", True),
                "organization_id": organization_id,
                "role_metadata": self._serialize_json_field(validated_data.get("role_metadata", {}))
            }
            
            # Create role via backend service
            role = await self.role_service.create_role(role_create_data)
            
            if role:
                logger.info(f"Custom role created: {role.role_id}")
                return role.role_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating custom role: {e}")
            return None
    
    async def update_custom_role(self, role_id: str, role_data: Dict[str, Any]) -> bool:
        """Update a custom role via backend"""
        await self._ensure_initialized()
        try:
            # Get existing role to validate
            existing_role = await self.get_custom_role(role_id)
            if not existing_role:
                logger.warning(f"Custom role {role_id} not found")
                return False
            
            # Validate update data
            validated_data = self._validate_role_data(role_data, is_update=True)
            
            # Prepare update data
            update_data = {}
            for key, value in validated_data.items():
                if key in ["role_name", "role_description", "role_level", "is_active"]:
                    update_data[key] = value
                elif key == "role_metadata":
                    update_data[key] = self._serialize_json_field(value)
            
            # Update role via backend service
            success = await self.role_service.update_role(role_id, update_data)
            
            if success:
                logger.info(f"Custom role updated: {role_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating custom role {role_id}: {e}")
            return False
    
    async def delete_custom_role(self, role_id: str) -> bool:
        """Delete a custom role via backend"""
        await self._ensure_initialized()
        try:
            # Get existing role to validate
            existing_role = await self.get_custom_role(role_id)
            if not existing_role:
                logger.warning(f"Custom role {role_id} not found")
                return False
            
            # Check if role is assigned to any users
            assigned_users = await self.get_users_with_role(role_id)
            if assigned_users:
                logger.warning(f"Cannot delete role {role_id} - assigned to {len(assigned_users)} users")
                return False
            
            # Delete role via backend service
            success = await self.role_service.delete_role(role_id)
            
            if success:
                logger.info(f"Custom role deleted: {role_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting custom role {role_id}: {e}")
            return False
    
    async def assign_role_to_user(self, user_id: str, role_id: str, 
                                organization_id: str, assigned_by: str) -> bool:
        """Assign a role to a user via backend"""
        await self._ensure_initialized()
        try:
            # Validate role assignment
            role = await self.get_custom_role(role_id)
            if not role:
                logger.warning(f"Role {role_id} not found")
                return False
            
            if role["organization_id"] != organization_id:
                logger.warning(f"Role {role_id} does not belong to organization {organization_id}")
                return False
            
            # Create role assignment via backend service
            assignment_data = {
                "user_id": user_id,
                "role_id": role_id,
                "assignment_type": "direct",
                "organization_id": organization_id,
                "assigned_by": assigned_by,
                "is_active": True
            }
            
            success = await self.role_service.assign_role_to_user(assignment_data)
            
            if success:
                logger.info(f"Role {role_id} assigned to user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error assigning role {role_id} to user {user_id}: {e}")
            return False
    
    async def remove_role_from_user(self, user_id: str, role_id: str, 
                                  organization_id: str) -> bool:
        """Remove a role from a user via backend"""
        await self._ensure_initialized()
        try:
            # Get role assignment
            assignments = await self.get_user_roles(user_id, organization_id)
            target_assignment = next((a for a in assignments if a["role_id"] == role_id), None)
            
            if not target_assignment:
                logger.warning(f"Role {role_id} not assigned to user {user_id}")
                return False
            
            # Remove role assignment via backend service
            success = await self.role_service.remove_role_from_user(
                user_id, role_id, organization_id
            )
            
            if success:
                logger.info(f"Role {role_id} removed from user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing role {role_id} from user {user_id}: {e}")
            return False
    
    async def get_user_roles(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get all roles assigned to a user via backend"""
        await self._ensure_initialized()
        try:
            # Get role assignments via backend service
            assignments = await self.role_service.get_user_role_assignments(user_id)
            
            user_roles = []
            for assignment in assignments:
                if assignment.organization_id == organization_id:
                    # Get role details
                    role = await self.get_custom_role(assignment.role_id)
                    if role:
                        user_roles.append({
                            "assignment_id": assignment.assignment_id,
                            "role_id": assignment.role_id,
                            "role_name": role["role_name"],
                            "role_description": role["role_description"],
                            "assignment_type": assignment.assignment_type,
                            "assigned_at": assignment.assigned_at,
                            "expires_at": getattr(assignment, 'expires_at', None),
                            "assigned_by": assignment.assigned_by,
                            "is_active": assignment.is_active
                        })
            
            return user_roles
            
        except Exception as e:
            logger.error(f"Error getting roles for user {user_id}: {e}")
            return []
    
    async def get_users_with_role(self, role_id: str) -> List[Dict[str, Any]]:
        """Get all users assigned to a specific role via backend"""
        await self._ensure_initialized()
        try:
            # Get role assignments via backend service
            assignments = await self.role_service.get_role_assignments(role_id)
            
            users_with_role = []
            for assignment in assignments:
                if assignment.is_active:
                    # Get user details
                    user = await self.role_service.get_user_by_id(assignment.user_id)
                    if user:
                        users_with_role.append({
                            "user_id": user.user_id,
                            "username": user.username,
                            "full_name": user.full_name,
                            "email": user.email,
                            "assignment_id": assignment.assignment_id,
                            "assigned_at": assignment.assigned_at,
                            "assigned_by": assignment.assigned_by
                        })
            
            return users_with_role
            
        except Exception as e:
            logger.error(f"Error getting users with role {role_id}: {e}")
            return []
    
    def _validate_role_data(self, role_data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate and sanitize role data"""
        if not isinstance(role_data, dict):
            raise ValueError("Role data must be a dictionary")
        
        validated = {}
        
        # Validate role name
        if "role_name" in role_data:
            role_name = str(role_data["role_name"]).strip()
            if len(role_name) < 2 or len(role_name) > 50:
                raise ValueError("Role name must be between 2 and 50 characters")
            validated["role_name"] = role_name
        elif not is_update:
            raise ValueError("Role name is required")
        
        # Validate role description
        if "role_description" in role_data:
            description = str(role_data["role_description"]).strip()
            if len(description) > 500:
                raise ValueError("Role description must be less than 500 characters")
            validated["role_description"] = description
        
        # Validate role level
        if "role_level" in role_data:
            try:
                level = int(role_data["role_level"])
                if level < 1 or level > 10:
                    raise ValueError("Role level must be between 1 and 10")
                validated["role_level"] = level
            except (ValueError, TypeError):
                raise ValueError("Role level must be a valid integer")
        
        # Validate is_active
        if "is_active" in role_data:
            validated["is_active"] = bool(role_data["is_active"])
        
        # Validate role metadata
        if "role_metadata" in role_data:
            if isinstance(role_data["role_metadata"], dict):
                validated["role_metadata"] = role_data["role_metadata"]
            else:
                validated["role_metadata"] = {}
        
        return validated
    
    def _parse_json_field(self, field_value: Any) -> Any:
        """Parse JSON field from role model"""
        if not field_value:
            return {}
        
        if isinstance(field_value, str):
            try:
                import json
                return json.loads(field_value)
            except:
                return {}
        
        return field_value if isinstance(field_value, (dict, list)) else {}
    
    def _serialize_json_field(self, field_value: Any) -> str:
        """Serialize field value to JSON string"""
        if not field_value:
            return "{}"
        
        try:
            import json
            return json.dumps(field_value)
        except:
            return "{}"


# Export the integration service
__all__ = ['CustomRoleService']
