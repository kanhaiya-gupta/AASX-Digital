"""
Authorization Module
==================

Role-based access control (RBAC) and permission management system.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone

from .models import (
    User, Role, Permission, SecurityContext, AuthorizationResult,
    PermissionLevel
)

logger = logging.getLogger(__name__)


class AuthorizationManager(ABC):
    """Abstract base class for authorization management"""
    
    def __init__(self, name: str = "AuthorizationManager"):
        self.name = name
        self._roles: Dict[str, Role] = {}
        self._permissions: Dict[str, Permission] = {}
        self._role_hierarchy: Dict[str, Set[str]] = {}  # Role inheritance
        self._user_roles: Dict[str, List[str]] = {}  # user_id -> role_ids
        
    @abstractmethod
    def check_permission(self, context: SecurityContext, 
                        resource: str, action: str) -> AuthorizationResult:
        """Check if security context has permission for resource/action"""
        pass
    
    @abstractmethod
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user"""
        pass
    
    def create_role(self, name: str, description: str = "", 
                   permissions: List[Permission] = None,
                   parent_roles: List[str] = None) -> Role:
        """Create a new role"""
        if name in self._roles:
            raise ValueError(f"Role {name} already exists")
        
        role = Role(
            name=name,
            description=description,
            permissions=permissions or [],
            parent_roles=parent_roles or []
        )
        
        self._roles[name] = role
        self._role_hierarchy[name] = set(parent_roles or [])
        
        logger.info(f"Created role: {name}")
        return role
    
    def get_role(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self._roles.get(name)
    
    def update_role(self, name: str, **kwargs) -> bool:
        """Update role information"""
        if name not in self._roles:
            return False
        
        role = self._roles[name]
        for key, value in kwargs.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        role.updated_at = datetime.now(timezone.utc)
        logger.info(f"Updated role: {name}")
        return True
    
    def delete_role(self, name: str) -> bool:
        """Delete role (if not system role)"""
        if name not in self._roles:
            return False
        
        role = self._roles[name]
        if role.is_system:
            logger.warning(f"Cannot delete system role: {name}")
            return False
        
        del self._roles[name]
        if name in self._role_hierarchy:
            del self._role_hierarchy[name]
        
        logger.info(f"Deleted role: {name}")
        return True
    
    def create_permission(self, name: str, description: str, 
                         resource: str, actions: List[str],
                         level: PermissionLevel = PermissionLevel.READ) -> Permission:
        """Create a new permission"""
        if name in self._permissions:
            raise ValueError(f"Permission {name} already exists")
        
        permission = Permission(
            name=name,
            description=description,
            resource=resource,
            actions=actions,
            level=level
        )
        
        self._permissions[name] = permission
        logger.info(f"Created permission: {name}")
        return permission
    
    def get_permission(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        return self._permissions.get(name)
    
    def assign_permission_to_role(self, role_name: str, permission_name: str) -> bool:
        """Assign permission to role"""
        if role_name not in self._roles:
            return False
        
        if permission_name not in self._permissions:
            return False
        
        role = self._roles[role_name]
        permission = self._permissions[permission_name]
        
        role.add_permission(permission)
        logger.info(f"Assigned permission {permission_name} to role {role_name}")
        return True
    
    def remove_permission_from_role(self, role_name: str, permission_name: str) -> bool:
        """Remove permission from role"""
        if role_name not in self._roles:
            return False
        
        role = self._roles[role_name]
        permission = self._permissions.get(permission_name)
        
        if permission:
            return role.remove_permission(permission.id)
        
        return False
    
    async def get_inherited_roles(self, role_name: str) -> Set[str]:
        """Get all inherited roles (transitive closure)"""
        if role_name not in self._role_hierarchy:
            return set()
        
        inherited = set()
        to_process = {role_name}
        
        while to_process:
            current = to_process.pop()
            if current in self._role_hierarchy:
                for parent in self._role_hierarchy[current]:
                    if parent not in inherited:
                        inherited.add(parent)
                        to_process.add(parent)
        
        return inherited
    
    async def get_all_role_permissions(self, role_name: str) -> List[Permission]:
        """Get all permissions for a role including inherited ones"""
        if role_name not in self._roles:
            return []
        
        role = self._roles[role_name]
        permissions = list(role.permissions)
        
        # Add inherited permissions
        inherited_roles = await self.get_inherited_roles(role_name)
        for inherited_role_name in inherited_roles:
            inherited_role = self._roles.get(inherited_role_name)
            if inherited_role:
                permissions.extend(inherited_role.permissions)
        
        return permissions

    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        if role_name not in self._roles:
            return False
        
        if user_id not in self._user_roles:
            self._user_roles[user_id] = []
        
        if role_name not in self._user_roles[user_id]:
            self._user_roles[user_id].append(role_name)
            logger.info(f"Assigned role {role_name} to user {user_id}")
        
        return True
    
    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """Remove role from user"""
        if user_id not in self._user_roles:
            return False
        
        if role_name in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role_name)
            logger.info(f"Removed role {role_name} from user {user_id}")
            return True
        
        return False
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """Get all roles for a user"""
        if user_id not in self._user_roles:
            return []
        
        return self._user_roles.copy()
    
    def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role"""
        if user_id not in self._user_roles:
            return False
        
        return role_name in self._user_roles[user_id]
    
    async def check_permission_base(self, context: SecurityContext, 
                             resource: str, action: str) -> AuthorizationResult:
        """Base permission check implementation"""
        if not context.user_id:
            return AuthorizationResult(
                allowed=False,
                resource=resource,
                action=action,
                message="No user context provided",
                error_code="NO_USER_CONTEXT"
            )
        
        # Get user's roles
        user_roles = await self.get_user_roles(context.user_id)
        
        # Check direct permissions in context
        for permission in context.permissions:
            if permission.resource == resource and permission.has_action(action):
                return AuthorizationResult(
                    allowed=True,
                    user_id=context.user_id,
                    resource=resource,
                    action=action,
                    granted_permissions=[permission.name],
                    message="Permission granted via direct context"
                )
        
        # Check role-based permissions
        required_permissions = []
        granted_permissions = []
        
        for role_name in user_roles:
            role = self.get_role(role_name)
            if role:
                # Check direct role permissions
                for permission in role.permissions:
                    if permission.resource == resource and permission.has_action(action):
                        granted_permissions.append(permission.name)
                
                # Check inherited role permissions
                inherited_permissions = await self.get_all_role_permissions(role_name)
                for permission in inherited_permissions:
                    if permission.resource == resource and permission.has_action(action):
                        granted_permissions.append(permission.name)
        
        if granted_permissions:
            return AuthorizationResult(
                allowed=True,
                user_id=context.user_id,
                resource=resource,
                action=action,
                required_permissions=required_permissions,
                granted_permissions=list(set(granted_permissions)),  # Remove duplicates
                message="Permission granted via role-based access control"
            )
        
        return AuthorizationResult(
            allowed=False,
            user_id=context.user_id,
            resource=resource,
            action=action,
            required_permissions=required_permissions,
            granted_permissions=[],
            message="Access denied - insufficient permissions",
            error_code="INSUFFICIENT_PERMISSIONS"
        )


class AsyncAuthorizationManager(AuthorizationManager):
    """Asynchronous authorization manager"""
    
    async def check_permission_async(self, context: SecurityContext,
                                   resource: str, action: str) -> AuthorizationResult:
        """Check permission asynchronously"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.check_permission, context, resource, action
        )
    
    async def get_user_permissions_async(self, user_id: str) -> List[Permission]:
        """Get user permissions asynchronously"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.get_user_permissions, user_id
        )


class RoleBasedAccessControl(AuthorizationManager):
    """Role-Based Access Control implementation"""
    
    def __init__(self, create_defaults: bool = False):
        super().__init__()
        self._create_defaults = create_defaults
    
    async def initialize(self):
        """Initialize the authorization system with defaults if requested"""
        if self._create_defaults:
            await self._create_default_roles()
    
    async def _create_default_roles(self):
        """Create default system roles"""
        # Admin role
        admin_role = self.create_role("admin", "System administrator")
        admin_role.is_system = True
        
        # User role
        user_role = self.create_role("user", "Regular user")
        user_role.is_system = True
        
        # Processor role
        processor_role = self.create_role("processor", "Data processor")
        processor_role.is_system = True
        
        # System role
        system_role = self.create_role("system", "System service")
        system_role.is_system = True
        
        # Create default permissions
        read_users = self.create_permission(
            "read_users", "Read user data", "users", ["read", "list"]
        )
        write_users = self.create_permission(
            "write_users", "Write user data", "users", ["create", "update", "delete"]
        )
        
        # AASX Processing permissions
        aasx_create = self.create_permission(
            "aasx_create", "Create AASX processing jobs", "aasx_processing", ["create"]
        )
        aasx_read = self.create_permission(
            "aasx_read", "Read AASX processing jobs", "aasx_processing", ["read", "list"]
        )
        aasx_update = self.create_permission(
            "aasx_update", "Update AASX processing jobs", "aasx_processing", ["update"]
        )
        aasx_delete = self.create_permission(
            "aasx_delete", "Delete AASX processing jobs", "aasx_processing", ["delete"]
        )
        
        # Twin Registry permissions
        twin_registry_create = self.create_permission(
            "twin_registry_create", "Create twin registry entries", "twin_registry", ["create"]
        )
        twin_registry_read = self.create_permission(
            "twin_registry_read", "Read twin registry entries", "twin_registry", ["read", "list"]
        )
        twin_registry_update = self.create_permission(
            "twin_registry_update", "Update twin registry entries", "twin_registry", ["update"]
        )
        twin_registry_delete = self.create_permission(
            "twin_registry_delete", "Delete twin registry entries", "twin_registry", ["delete"]
        )
        
        # KG Registry permissions
        kg_registry_create = self.create_permission(
            "kg_registry_create", "Create KG registry entries", "kg_registry", ["create"]
        )
        kg_registry_read = self.create_permission(
            "kg_registry_read", "Read KG registry entries", "kg_registry", ["read", "list"]
        )
        kg_registry_update = self.create_permission(
            "kg_registry_update", "Update KG registry entries", "kg_registry", ["update"]
        )
        kg_registry_delete = self.create_permission(
            "kg_registry_delete", "Delete KG registry entries", "kg_registry", ["delete"]
        )
        
        # AI RAG Registry permissions
        ai_rag_create = self.create_permission(
            "ai_rag_create", "Create AI RAG entries", "ai_rag", ["create"]
        )
        ai_rag_read = self.create_permission(
            "ai_rag_read", "Read AI RAG entries", "ai_rag", ["read", "list"]
        )
        ai_rag_update = self.create_permission(
            "ai_rag_update", "Update AI RAG entries", "ai_rag", ["update"]
        )
        ai_rag_delete = self.create_permission(
            "ai_rag_delete", "Delete AI RAG entries", "ai_rag", ["delete"]
        )
        
        # Federated Learning permissions
        federated_learning_create = self.create_permission(
            "federated_learning_create", "Create federated learning entries", "federated_learning", ["create"]
        )
        federated_learning_read = self.create_permission(
            "federated_learning_read", "Read federated learning entries", "federated_learning", ["read", "list"]
        )
        federated_learning_update = self.create_permission(
            "federated_learning_update", "Update federated learning entries", "federated_learning", ["update"]
        )
        federated_learning_delete = self.create_permission(
            "federated_learning_delete", "Delete federated learning entries", "federated_learning", ["delete"]
        )
        
        # Physics Modeling permissions
        physics_modeling_create = self.create_permission(
            "physics_modeling_create", "Create physics modeling entries", "physics_modeling", ["create"]
        )
        physics_modeling_read = self.create_permission(
            "physics_modeling_read", "Read physics modeling entries", "physics_modeling", ["read", "list"]
        )
        physics_modeling_update = self.create_permission(
            "physics_modeling_update", "Update physics modeling entries", "physics_modeling", ["update"]
        )
        physics_modeling_delete = self.create_permission(
            "physics_modeling_delete", "Delete physics modeling entries", "physics_modeling", ["delete"]
        )
        
        # Certificate Manager permissions
        certificate_manager_create = self.create_permission(
            "certificate_manager_create", "Create certificate manager entries", "certificate_manager", ["create"]
        )
        certificate_manager_read = self.create_permission(
            "certificate_manager_read", "Read certificate manager entries", "certificate_manager", ["read", "list"]
        )
        certificate_manager_update = self.create_permission(
            "certificate_manager_update", "Update certificate manager entries", "certificate_manager", ["update"]
        )
        certificate_manager_delete = self.create_permission(
            "certificate_manager_delete", "Delete certificate manager entries", "certificate_manager", ["delete"]
        )
        
        # Assign permissions to roles
        self.assign_permission_to_role("user", "read_users")
        self.assign_permission_to_role("admin", "read_users")
        self.assign_permission_to_role("admin", "write_users")
        
        # AASX permissions
        self.assign_permission_to_role("user", "aasx_read")
        self.assign_permission_to_role("processor", "aasx_create")
        self.assign_permission_to_role("processor", "aasx_read")
        self.assign_permission_to_role("processor", "aasx_update")
        self.assign_permission_to_role("admin", "aasx_create")
        self.assign_permission_to_role("admin", "aasx_read")
        self.assign_permission_to_role("admin", "aasx_update")
        self.assign_permission_to_role("admin", "aasx_delete")
        self.assign_permission_to_role("system", "aasx_create")
        self.assign_permission_to_role("system", "aasx_read")
        self.assign_permission_to_role("system", "aasx_update")
        
        # Twin Registry permissions
        self.assign_permission_to_role("user", "twin_registry_read")
        self.assign_permission_to_role("processor", "twin_registry_create")
        self.assign_permission_to_role("processor", "twin_registry_read")
        self.assign_permission_to_role("processor", "twin_registry_update")
        self.assign_permission_to_role("admin", "twin_registry_create")
        self.assign_permission_to_role("admin", "twin_registry_read")
        self.assign_permission_to_role("admin", "twin_registry_update")
        self.assign_permission_to_role("admin", "twin_registry_delete")
        self.assign_permission_to_role("system", "twin_registry_create")
        self.assign_permission_to_role("system", "twin_registry_read")
        self.assign_permission_to_role("system", "twin_registry_update")
        
        # KG Registry permissions
        self.assign_permission_to_role("user", "kg_registry_read")
        self.assign_permission_to_role("processor", "kg_registry_create")
        self.assign_permission_to_role("processor", "kg_registry_read")
        self.assign_permission_to_role("processor", "kg_registry_update")
        self.assign_permission_to_role("admin", "kg_registry_create")
        self.assign_permission_to_role("admin", "kg_registry_read")
        self.assign_permission_to_role("admin", "kg_registry_update")
        self.assign_permission_to_role("admin", "kg_registry_delete")
        self.assign_permission_to_role("system", "kg_registry_create")
        self.assign_permission_to_role("system", "kg_registry_read")
        self.assign_permission_to_role("system", "kg_registry_update")
        
        # AI RAG Registry permissions
        self.assign_permission_to_role("user", "ai_rag_read")
        self.assign_permission_to_role("processor", "ai_rag_create")
        self.assign_permission_to_role("processor", "ai_rag_read")
        self.assign_permission_to_role("processor", "ai_rag_update")
        self.assign_permission_to_role("admin", "ai_rag_create")
        self.assign_permission_to_role("admin", "ai_rag_read")
        self.assign_permission_to_role("admin", "ai_rag_update")
        self.assign_permission_to_role("admin", "ai_rag_delete")
        self.assign_permission_to_role("system", "ai_rag_create")
        self.assign_permission_to_role("system", "ai_rag_read")
        self.assign_permission_to_role("system", "ai_rag_update")
        self.assign_permission_to_role("system", "ai_rag_delete")
        
        # Federated Learning permissions
        self.assign_permission_to_role("user", "federated_learning_read")
        self.assign_permission_to_role("processor", "federated_learning_create")
        self.assign_permission_to_role("processor", "federated_learning_read")
        self.assign_permission_to_role("processor", "federated_learning_update")
        self.assign_permission_to_role("admin", "federated_learning_create")
        self.assign_permission_to_role("admin", "federated_learning_read")
        self.assign_permission_to_role("admin", "federated_learning_update")
        self.assign_permission_to_role("admin", "federated_learning_delete")
        self.assign_permission_to_role("system", "federated_learning_create")
        self.assign_permission_to_role("system", "federated_learning_read")
        self.assign_permission_to_role("system", "federated_learning_update")
        
        # Physics Modeling permissions
        self.assign_permission_to_role("user", "physics_modeling_read")
        self.assign_permission_to_role("processor", "physics_modeling_create")
        self.assign_permission_to_role("processor", "physics_modeling_read")
        self.assign_permission_to_role("processor", "physics_modeling_update")
        self.assign_permission_to_role("admin", "physics_modeling_create")
        self.assign_permission_to_role("admin", "physics_modeling_read")
        self.assign_permission_to_role("admin", "physics_modeling_update")
        self.assign_permission_to_role("admin", "physics_modeling_delete")
        self.assign_permission_to_role("system", "physics_modeling_create")
        self.assign_permission_to_role("system", "physics_modeling_read")
        self.assign_permission_to_role("system", "physics_modeling_update")
        
        # Certificate Manager permissions
        self.assign_permission_to_role("user", "certificate_manager_read")
        self.assign_permission_to_role("processor", "certificate_manager_create")
        self.assign_permission_to_role("processor", "certificate_manager_read")
        self.assign_permission_to_role("processor", "certificate_manager_update")
        self.assign_permission_to_role("admin", "certificate_manager_create")
        self.assign_permission_to_role("admin", "certificate_manager_read")
        self.assign_permission_to_role("admin", "certificate_manager_update")
        self.assign_permission_to_role("admin", "certificate_manager_delete")
        self.assign_permission_to_role("system", "certificate_manager_create")
        self.assign_permission_to_role("system", "certificate_manager_read")
        self.assign_permission_to_role("system", "certificate_manager_update")
        
        # Assign default users to roles
        await self.assign_role_to_user("admin", "admin")
        await self.assign_role_to_user("system", "system")
        await self.assign_role_to_user("user", "user")
        await self.assign_role_to_user("user1", "user")  # Add user1 for testing
        await self.assign_role_to_user("processor", "processor")
    
    async def check_permission(self, context: SecurityContext, 
                        resource: str, action: str) -> AuthorizationResult:
        """Check permission with role inheritance"""
        # First, check direct permissions and roles assigned to the user in the base class
        result = await self.check_permission_base(context, resource, action)
        
        if result.allowed:
            return result
        
        # If not allowed by direct assignment, check role inheritance
        user_roles = await self.get_user_roles(context.user_id)
        for role_name in user_roles:
            role = self.get_role(role_name)
            if not role:
                continue
            
            # Check parent roles for inherited permissions
            for parent_role_name in role.parent_roles:
                parent_role = self.get_role(parent_role_name)
                if not parent_role:
                    continue
                
                for permission in parent_role.permissions:
                    if (permission.resource == resource and 
                        permission.has_action(action)):
                        return AuthorizationResult(
                            allowed=True,
                            user_id=context.user_id,
                            resource=resource,
                            action=action,
                            granted_permissions=[permission.name],
                            message="Permission granted through role inheritance"
                        )
        
        return result # Return the original result if no inherited permission found
    
    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user"""
        if user_id not in self._user_roles:
            return []
        
        user_roles = self._user_roles[user_id]
        all_permissions = []
        
        for role_name in user_roles:
            role_permissions = await self.get_all_role_permissions(role_name)
            all_permissions.extend(role_permissions)
        
        # Remove duplicates based on permission ID
        unique_permissions = {}
        for permission in all_permissions:
            unique_permissions[permission.id] = permission
        
        return list(unique_permissions.values())
    
    async def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        if role_name not in self._roles:
            return False
        
        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()
        
        self._user_roles[user_id].add(role_name)
        logger.info(f"Assigned role {role_name} to user {user_id}")
        return True
    
    async def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """Remove role from user"""
        if user_id not in self._user_roles:
            return False
        
        if role_name in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role_name)
            logger.info(f"Removed role {role_name} from user {user_id}")
            return True
        
        return False
    
    async def get_user_roles(self, user_id: str) -> List[str]:
        """Get all roles for a user"""
        if user_id not in self._user_roles:
            return []
        
        return list(self._user_roles[user_id])
    
    async def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role"""
        if user_id not in self._user_roles:
            return False
        
        return role_name in self._user_roles[user_id]
    
    async def get_health(self) -> Dict[str, Any]:
        """Get health status of the authorization system"""
        try:
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "roles_count": len(self._roles),
                "permissions_count": len(self._permissions),
                "users_count": len(self._user_roles),
                "message": "Authorization system is operational"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "message": "Authorization system has errors"
            }


class PermissionManager:
    """Permission management and validation"""
    
    def __init__(self):
        self._permissions: Dict[str, Permission] = {}
        self._resource_permissions: Dict[str, List[Permission]] = {}
        self._action_permissions: Dict[str, List[Permission]] = {}
    
    def add_permission(self, permission: Permission) -> None:
        """Add permission to manager"""
        self._permissions[permission.id] = permission
        
        # Index by resource
        if permission.resource not in self._resource_permissions:
            self._resource_permissions[permission.resource] = []
        self._resource_permissions[permission.resource].append(permission)
        
        # Index by actions
        for action in permission.actions:
            if action not in self._action_permissions:
                self._action_permissions[action] = []
            self._action_permissions[action].append(permission)
    
    def get_permissions_for_resource(self, resource: str) -> List[Permission]:
        """Get all permissions for a specific resource"""
        return self._resource_permissions.get(resource, [])
    
    def get_permissions_for_action(self, action: str) -> List[Permission]:
        """Get all permissions that allow a specific action"""
        return self._action_permissions.get(action, [])
    
    def check_permission(self, permission_name: str, resource: str, action: str) -> bool:
        """Check if a specific permission allows the action on resource"""
        permission = self._permissions.get(permission_name)
        if not permission:
            return False
        
        return permission.resource == resource and permission.has_action(action)
    
    def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        for permission in self._permissions.values():
            if permission.name == name:
                return permission
        return None
    
    def list_permissions(self) -> List[Permission]:
        """List all permissions"""
        return list(self._permissions.values())


class PolicyEngine:
    """Policy-based authorization engine"""
    
    def __init__(self):
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._policy_rules: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_policy(self, name: str, policy: Dict[str, Any]) -> None:
        """Add a policy"""
        self._policies[name] = policy
        
        # Extract rules from policy
        rules = policy.get('rules', [])
        self._policy_rules[name] = rules
        
        logger.info(f"Added policy: {name} with {len(rules)} rules")
    
    def evaluate_policy(self, policy_name: str, context: Dict[str, Any]) -> bool:
        """Evaluate a policy against a context"""
        if policy_name not in self._policies:
            return False
        
        policy = self._policies[policy_name]
        rules = self._policy_rules[policy_name]
        
        # Check if policy is active
        if not policy.get('active', True):
            return False
        
        # Evaluate all rules
        for rule in rules:
            if not self._evaluate_rule(rule, context):
                return False
        
        return True
    
    def _evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a single rule"""
        rule_type = rule.get('type')
        
        if rule_type == 'condition':
            return self._evaluate_condition(rule, context)
        elif rule_type == 'time_based':
            return self._evaluate_time_rule(rule, context)
        elif rule_type == 'location_based':
            return self._evaluate_location_rule(rule, context)
        elif rule_type == 'role_based':
            return self._evaluate_role_rule(rule, context)
        else:
            logger.warning(f"Unknown rule type: {rule_type}")
            return False
    
    def _evaluate_condition(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition rule"""
        field = rule.get('field')
        operator = rule.get('operator')
        value = rule.get('value')
        
        if field not in context:
            return False
        
        context_value = context[field]
        
        if operator == 'equals':
            return context_value == value
        elif operator == 'not_equals':
            return context_value != value
        elif operator == 'contains':
            return value in context_value if isinstance(context_value, (list, str)) else False
        elif operator == 'greater_than':
            return context_value > value
        elif operator == 'less_than':
            return context_value < value
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _evaluate_time_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a time-based rule"""
        current_time = datetime.now(timezone.utc)
        start_time = rule.get('start_time')
        end_time = rule.get('end_time')
        
        if start_time:
            # Ensure start_time is timezone-aware
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            if current_time < start_time:
                return False
        
        if end_time:
            # Ensure end_time is timezone-aware
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=timezone.utc)
            if current_time > end_time:
                return False
        
        return True
    
    def _evaluate_location_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a location-based rule"""
        allowed_locations = rule.get('allowed_locations', [])
        user_location = context.get('location')
        
        if not user_location:
            return False
        
        return user_location in allowed_locations
    
    def _evaluate_role_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a role-based rule"""
        required_roles = rule.get('required_roles', [])
        user_roles = context.get('roles', [])
        
        if not required_roles:
            return True
        
        return any(role in user_roles for role in required_roles)
    
    def get_policy(self, name: str) -> Optional[Dict[str, Any]]:
        """Get policy by name"""
        return self._policies.get(name)
    
    def list_policies(self) -> List[str]:
        """List all policy names"""
        return list(self._policies.keys())
    
    def remove_policy(self, name: str) -> bool:
        """Remove a policy"""
        if name in self._policies:
            del self._policies[name]
            if name in self._policy_rules:
                del self._policy_rules[name]
            logger.info(f"Removed policy: {name}")
            return True
        return False
