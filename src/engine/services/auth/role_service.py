"""
Role Service - Handles role and permission management.

This service provides business logic for role operations including:
- Role and permission management
- Role assignment workflows
- Permission validation
- Role hierarchy management
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum

from ...repositories.auth_repository import AuthRepository
from ...models.auth import User
from ..base.base_service import BaseService

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for role-based access control."""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class Permission:
    """Permission definition for role-based access control."""
    resource: str
    action: str
    level: PermissionLevel
    conditions: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


@dataclass
class Role:
    """Role definition with permissions and metadata."""
    role_id: str
    name: str
    display_name: str
    description: str
    permissions: List[Permission]
    parent_role_id: Optional[str] = None
    is_active: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = None
    created_at: str = None
    updated_at: str = None


@dataclass
class RoleAssignment:
    """Role assignment to a user."""
    assignment_id: str
    user_id: str
    role_id: str
    assigned_by: str
    assigned_at: str
    org_id: Optional[str] = None
    dept_id: Optional[str] = None
    expires_at: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = None


class RoleService(BaseService):
    """
    Service for managing roles, permissions, and role assignments.
    
    Handles role lifecycle, permission validation, role hierarchy,
    and role assignment workflows across the system.
    """
    
    def __init__(self, auth_repository: AuthRepository):
        """
        Initialize the RoleService.
        
        Args:
            auth_repository: Repository for role data operations
        """
        super().__init__()
        self.auth_repository = auth_repository
        
        # In-memory data structures for fast access
        self._roles: Dict[str, Role] = {}
        self._role_assignments: Dict[str, RoleAssignment] = {}
        self._user_roles: Dict[str, Set[str]] = {}  # user_id -> set of role_ids
        self._role_hierarchy: Dict[str, List[str]] = {}  # role_id -> list of child role_ids
        self._permission_cache: Dict[str, Dict[str, PermissionLevel]] = {}  # user_id -> resource -> permission_level
        
        # Default system roles
        self._default_roles = {
            "super_admin": Role(
                role_id="super_admin",
                name="super_admin",
                display_name="Super Administrator",
                description="Full system access with all permissions",
                permissions=[],
                priority=1000,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            "org_admin": Role(
                role_id="org_admin",
                name="org_admin",
                display_name="Organization Administrator",
                description="Organization-level administrative access",
                permissions=[],
                priority=900,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            "dept_manager": Role(
                role_id="dept_manager",
                name="dept_manager",
                display_name="Department Manager",
                description="Department-level management access",
                permissions=[],
                priority=800,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            "user": Role(
                role_id="user",
                name="user",
                display_name="Standard User",
                description="Basic user access with limited permissions",
                permissions=[],
                priority=100,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        }
        
        # Load initial data
        asyncio.create_task(self._initialize_service_resources())
    
    async def create_role(self, role_data: Dict[str, Any]) -> Optional[Role]:
        """
        Create a new role with permissions.
        
        Args:
            role_data: Role creation data
            
        Returns:
            Created role or None if failed
        """
        try:
            self._log_operation("create_role", f"name: {role_data.get('name')}")
            
            # Validate required fields
            required_fields = ['role_id', 'name', 'display_name', 'description']
            for field in required_fields:
                if not role_data.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Check if role already exists
            if role_data['role_id'] in self._roles:
                raise ValueError(f"Role already exists: {role_data['role_id']}")
            
            # Create permissions list
            permissions = []
            for perm_data in role_data.get('permissions', []):
                permission = Permission(
                    resource=perm_data['resource'],
                    action=perm_data['action'],
                    level=PermissionLevel(perm_data['level']),
                    conditions=perm_data.get('conditions'),
                    metadata=perm_data.get('metadata')
                )
                permissions.append(permission)
            
            # Create role
            role = Role(
                role_id=role_data['role_id'],
                name=role_data['name'],
                display_name=role_data['display_name'],
                description=role_data['description'],
                permissions=permissions,
                parent_role_id=role_data.get('parent_role_id'),
                is_active=role_data.get('is_active', True),
                priority=role_data.get('priority', 100),
                metadata=role_data.get('metadata'),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Save to repository (if implemented)
            # await self.auth_repository.create_role(role)
            
            # Update in-memory structures
            self._roles[role.role_id] = role
            self._role_hierarchy[role.role_id] = []
            
            # Update parent role hierarchy
            if role.parent_role_id:
                if role.parent_role_id not in self._role_hierarchy:
                    self._role_hierarchy[role.parent_role_id] = []
                self._role_hierarchy[role.parent_role_id].append(role.role_id)
            
            logger.info(f"Role created successfully: {role.name}")
            return role
            
        except Exception as e:
            self.handle_error("create_role", e)
            return None
    
    async def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """
        Get role by ID.
        
        Args:
            role_id: Role identifier
            
        Returns:
            Role object or None if not found
        """
        try:
            # Check in-memory first
            if role_id in self._roles:
                return self._roles[role_id]
            
            # Check default roles
            if role_id in self._default_roles:
                return self._default_roles[role_id]
            
            # Fetch from repository (if implemented)
            # role = await self.auth_repository.get_role_by_id(role_id)
            # if role:
            #     self._roles[role_id] = role
            #     return role
            
            return None
            
        except Exception as e:
            self.handle_error("get_role_by_id", e)
            return None
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """
        Get role by name.
        
        Args:
            name: Role name to search for
            
        Returns:
            Role object or None if not found
        """
        try:
            # Check in-memory first
            for role in self._roles.values():
                if role.name == name:
                    return role
            
            # Check default roles
            for role in self._default_roles.values():
                if role.name == name:
                    return role
            
            return None
            
        except Exception as e:
            self.handle_error("get_role_by_name", e)
            return None
    
    async def assign_role_to_user(self, user_id: str, role_id: str, 
                                assigned_by: str, org_id: str = None, 
                                dept_id: str = None, expires_at: str = None) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User identifier
            role_id: Role identifier
            assigned_by: User ID who assigned the role
            org_id: Organization context (optional)
            dept_id: Department context (optional)
            expires_at: Role expiration timestamp (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("assign_role_to_user", f"user_id: {user_id}, role_id: {role_id}")
            
            # Validate role exists
            role = await self.get_role_by_id(role_id)
            if not role:
                raise ValueError(f"Role not found: {role_id}")
            
            # Create assignment
            assignment_id = f"{user_id}_{role_id}_{datetime.now().timestamp()}"
            assignment = RoleAssignment(
                assignment_id=assignment_id,
                user_id=user_id,
                role_id=role_id,
                org_id=org_id,
                dept_id=dept_id,
                assigned_by=assigned_by,
                assigned_at=datetime.now().isoformat(),
                expires_at=expires_at,
                is_active=True
            )
            
            # Save to repository (if implemented)
            # await self.auth_repository.create_role_assignment(assignment)
            
            # Update in-memory structures
            self._role_assignments[assignment_id] = assignment
            
            if user_id not in self._user_roles:
                self._user_roles[user_id] = set()
            self._user_roles[user_id].add(role_id)
            
            # Clear permission cache for this user
            self._permission_cache.pop(user_id, None)
            
            logger.info(f"Role {role_id} assigned to user {user_id}")
            return True
            
        except Exception as e:
            self.handle_error("assign_role_to_user", e)
            return False
    
    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """
        Remove a role assignment from a user.
        
        Args:
            user_id: User identifier
            role_id: Role identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("remove_role_from_user", f"user_id: {user_id}, role_id: {role_id}")
            
            # Find and deactivate assignment
            assignment_found = False
            for assignment_id, assignment in self._role_assignments.items():
                if (assignment.user_id == user_id and 
                    assignment.role_id == role_id and 
                    assignment.is_active):
                    
                    assignment.is_active = False
                    assignment_found = True
                    
                    # Update repository (if implemented)
                    # await self.auth_repository.update_role_assignment(assignment_id, {"is_active": False})
            
            if assignment_found:
                # Update in-memory structures
                if user_id in self._user_roles:
                    self._user_roles[user_id].discard(role_id)
                
                # Clear permission cache for this user
                self._permission_cache.pop(user_id, None)
                
                logger.info(f"Role {role_id} removed from user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            self.handle_error("remove_role_from_user", e)
            return False
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """
        Get all roles assigned to a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of roles assigned to the user
        """
        try:
            if user_id not in self._user_roles:
                return []
            
            roles = []
            for role_id in self._user_roles[user_id]:
                role = await self.get_role_by_id(role_id)
                if role:
                    roles.append(role)
            
            return roles
            
        except Exception as e:
            self.handle_error("get_user_roles", e)
            return []
    
    async def get_role_users(self, role_id: str) -> List[str]:
        """
        Get all users assigned to a role.
        
        Args:
            role_id: Role identifier
            
        Returns:
            List of user IDs assigned to the role
        """
        try:
            user_ids = set()
            for assignment in self._role_assignments.values():
                if (assignment.role_id == role_id and 
                    assignment.is_active):
                    user_ids.add(assignment.user_id)
            
            return list(user_ids)
            
        except Exception as e:
            self.handle_error("get_role_users", e)
            return []
    
    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """
        Check if a user has permission for a specific resource and action.
        
        Args:
            user_id: User identifier
            resource: Resource to check permission for
            action: Action to check permission for
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            # Check permission cache first
            if user_id in self._permission_cache:
                user_perms = self._permission_cache[user_id]
                if resource in user_perms:
                    return user_perms[resource] != PermissionLevel.NONE
            
            # Get user roles
            user_roles = await self.get_user_roles(user_id)
            if not user_roles:
                return False
            
            # Check permissions across all roles
            max_permission_level = PermissionLevel.NONE
            for role in user_roles:
                for permission in role.permissions:
                    if (permission.resource == resource and 
                        permission.action == action):
                        if permission.level.value > max_permission_level.value:
                            max_permission_level = permission.level
            
            # Cache the result
            if user_id not in self._permission_cache:
                self._permission_cache[user_id] = {}
            self._permission_cache[user_id][resource] = max_permission_level
            
            return max_permission_level != PermissionLevel.NONE
            
        except Exception as e:
            self.handle_error("check_permission", e)
            return False
    
    async def get_user_permissions(self, user_id: str) -> Dict[str, PermissionLevel]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary mapping resources to permission levels
        """
        try:
            if user_id in self._permission_cache:
                return self._permission_cache[user_id].copy()
            
            # Get user roles and build permission map
            user_roles = await self.get_user_roles(user_id)
            permissions = {}
            
            for role in user_roles:
                for permission in role.permissions:
                    resource_key = f"{permission.resource}:{permission.action}"
                    if (resource_key not in permissions or 
                        permission.level.value > permissions[resource_key].value):
                        permissions[resource_key] = permission.level
            
            # Cache the result
            self._permission_cache[user_id] = permissions
            
            return permissions.copy()
            
        except Exception as e:
            self.handle_error("get_user_permissions", e)
            return {}
    
    async def get_role_hierarchy(self, role_id: str) -> List[str]:
        """
        Get the hierarchy of roles (parent and child roles).
        
        Args:
            role_id: Role identifier
            
        Returns:
            List of role IDs in the hierarchy
        """
        try:
            hierarchy = [role_id]
            
            # Add child roles
            if role_id in self._role_hierarchy:
                for child_role_id in self._role_hierarchy[role_id]:
                    hierarchy.extend(await self.get_role_hierarchy(child_role_id))
            
            return hierarchy
            
        except Exception as e:
            self.handle_error("get_role_hierarchy", e)
            return [role_id]
    
    async def update_role(self, role_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update role information.
        
        Args:
            role_id: Role identifier
            updates: Role updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("update_role", f"role_id: {role_id}")
            
            # Get current role
            role = await self.get_role_by_id(role_id)
            if not role:
                raise ValueError(f"Role not found: {role_id}")
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(role, field):
                    setattr(role, field, value)
            
            role.updated_at = datetime.now().isoformat()
            
            # Update repository (if implemented)
            # await self.auth_repository.update_role(role_id, updates)
            
            # Update in-memory structures
            self._roles[role_id] = role
            
            # Clear permission cache for all users with this role
            role_users = await self.get_role_users(role_id)
            for user_id in role_users:
                self._permission_cache.pop(user_id, None)
            
            logger.info(f"Role updated successfully: {role_id}")
            return True
            
        except Exception as e:
            self.handle_error("update_role", e)
            return False
    
    async def delete_role(self, role_id: str) -> bool:
        """
        Delete a role.
        
        Args:
            role_id: Role identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("delete_role", f"role_id: {role_id}")
            
            # Check if role is assigned to any users
            role_users = await self.get_role_users(role_id)
            if role_users:
                raise ValueError(f"Cannot delete role {role_id}: assigned to {len(role_users)} users")
            
            # Delete from repository (if implemented)
            # await self.auth_repository.delete_role(role_id)
            
            # Clean up in-memory structures
            self._roles.pop(role_id, None)
            self._role_hierarchy.pop(role_id, None)
            
            # Remove from parent role hierarchy
            for parent_role_id, child_roles in self._role_hierarchy.items():
                if role_id in child_roles:
                    child_roles.remove(role_id)
            
            logger.info(f"Role deleted successfully: {role_id}")
            return True
            
        except Exception as e:
            self.handle_error("delete_role", e)
            return False
    
    def _load_roles(self) -> None:
        """Load roles from repository into memory."""
        try:
            # Initialize with default roles
            for role_id, role in self._default_roles.items():
                self._roles[role_id] = role
                self._role_hierarchy[role_id] = []
            
            logger.info("Role service initialized with default roles")
            
        except Exception as e:
            logger.error(f"Failed to load roles: {e}")
    
    async def _initialize_service_resources(self) -> None:
        """Initialize service-specific resources."""
        try:
            # Initialize role-related resources
            self._roles = {}
            self._role_assignments = {}
            self._user_roles = {}
            self._role_hierarchy = {}
            self._permission_cache = {}
            
            # Load initial data
            self._load_roles()
            logger.info("Role service resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize role service resources: {e}")
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        return {
            "service_name": "RoleService",
            "service_type": "authentication",
            "status": "active" if self.is_active else "inactive",
            "start_time": self.start_time.isoformat(),
            "total_roles": len(self._roles),
            "role_assignments": len(self._role_assignments),
            "users_with_roles": len(self._user_roles),
            "role_hierarchy_levels": len(self._role_hierarchy),
            "permission_cache_size": len(self._permission_cache),
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat(),
            "dependencies": self.dependencies,
            "performance_metrics": self.get_performance_summary()
        }
    
    async def _cleanup_service_resources(self) -> None:
        """Clean up service resources."""
        try:
            # Clear in-memory structures
            self._roles.clear()
            self._role_assignments.clear()
            self._user_roles.clear()
            self._role_hierarchy.clear()
            self._permission_cache.clear()
            
            logger.info("Role service resources cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup role service resources: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the role service."""
        try:
            await self._cleanup_service_resources()
            logger.info("Role service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during role service shutdown: {e}")
