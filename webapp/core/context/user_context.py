"""
User Context for AASX Digital Twin Analytics Framework
====================================================

This module provides user context functionality for request processing,
including user information, permissions, and data scope.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class UserContext:
    """User context for request processing"""
    
    def __init__(self, user_data: Dict[str, Any]):
        """
        Initialize user context from user data
        
        Args:
            user_data: Dictionary containing user information
        """
        self.user_id = user_data.get('user_id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.full_name = user_data.get('full_name')
        self.role = user_data.get('role', 'viewer')
        self.organization_id = user_data.get('organization_id')
        self.organization_name = user_data.get('organization_name')
        self.permissions = user_data.get('permissions', [])
        self.is_active = user_data.get('is_active', True)
        self.is_independent = self.organization_id is None
        
        # Additional user data
        self.phone = user_data.get('phone')
        self.job_title = user_data.get('job_title')
        self.department = user_data.get('department')
        self.bio = user_data.get('bio')
        self.mfa_enabled = user_data.get('mfa_enabled', False)
        self.email_verified = user_data.get('email_verified', False)
        self.phone_verified = user_data.get('phone_verified', False)
        self.last_login = user_data.get('last_login')
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission
        
        Args:
            permission: Permission to check (e.g., 'read', 'write', 'manage')
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """
        Check if user has specific role
        
        Args:
            role: Role to check (e.g., 'admin', 'manager', 'user', 'viewer')
            
        Returns:
            bool: True if user has role, False otherwise
        """
        return self.role == role
    
    def can_access_module(self, module: str) -> bool:
        """
        Check if user can access specific module
        
        Args:
            module: Module name (e.g., 'aasx-etl', 'twin-registry', 'ai-rag')
            
        Returns:
            bool: True if user can access module, False otherwise
        """
        module_permissions = {
            'aasx-etl': ['read', 'write'],
            'twin-registry': ['read', 'write'],
            'ai-rag': ['read', 'write'],
            'kg-neo4j': ['read', 'write'],
            'certificate-manager': ['read', 'write', 'manage'],
            'federated-learning': ['read', 'write', 'manage'],
            'physics-modeling': ['read', 'write', 'manage']
        }
        
        required_permissions = module_permissions.get(module, ['read'])
        return any(self.has_permission(perm) for perm in required_permissions)
    
    def get_user_type(self) -> str:
        """
        Get user type: 'independent', 'organization_member', 'super_admin'
        
        Returns:
            str: User type
        """
        if self.role == 'super_admin':
            return 'super_admin'
        elif self.is_independent:
            return 'independent'
        else:
            return 'organization_member'
    
    def get_data_scope(self) -> Dict[str, Any]:
        """
        Get data scope for the user
        
        Returns:
            dict: Data scope information
        """
        if self.role == 'super_admin':
            return {
                'scope': 'all',
                'organization_id': None,
                'user_id': None,
                'description': 'Access to all data across all organizations'
            }
        elif self.is_independent:
            return {
                'scope': 'user_only',
                'user_id': self.user_id,
                'organization_id': None,
                'description': 'Access to personal data only'
            }
        else:
            return {
                'scope': 'organization',
                'user_id': self.user_id,
                'organization_id': self.organization_id,
                'description': f'Access to organization data (ID: {self.organization_id})'
            }
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information for the user
        
        Returns:
            dict: Storage information
        """
        if self.role == 'super_admin':
            return {
                'type': 'unlimited',
                'limit_gb': -1,
                'used_gb': 0,
                'available_gb': -1,
                'description': 'Unlimited storage'
            }
        elif self.is_independent:
            return {
                'type': 'personal',
                'limit_gb': 5,
                'used_gb': 0,  # Will be calculated by storage service
                'available_gb': 5,
                'description': 'Personal storage (5GB limit)'
            }
        else:
            return {
                'type': 'organization',
                'limit_gb': 100,
                'used_gb': 0,  # Will be calculated by storage service
                'available_gb': 100,
                'description': f'Organization storage (100GB limit) - {self.organization_name or "Unknown Organization"}'
            }
    
    def get_project_limits(self) -> Dict[str, Any]:
        """
        Get project limits for the user
        
        Returns:
            dict: Project limits information
        """
        if self.role == 'super_admin':
            return {
                'type': 'unlimited',
                'limit': -1,
                'used': 0,
                'available': -1,
                'description': 'Unlimited projects'
            }
        elif self.is_independent:
            return {
                'type': 'personal',
                'limit': -1,  # Unlimited for independent users
                'used': 0,
                'available': -1,
                'description': 'Unlimited personal projects'
            }
        else:
            return {
                'type': 'organization',
                'limit': -1,  # Unlimited for organization users
                'used': 0,
                'available': -1,
                'description': f'Unlimited organization projects - {self.organization_name or "Unknown Organization"}'
            }
    
    def can_manage_users(self) -> bool:
        """
        Check if user can manage other users
        
        Returns:
            bool: True if user can manage users, False otherwise
        """
        return self.role in ['super_admin', 'admin']
    
    def can_manage_organization(self) -> bool:
        """
        Check if user can manage organization settings
        
        Returns:
            bool: True if user can manage organization, False otherwise
        """
        return self.role in ['super_admin', 'admin'] and not self.is_independent
    
    def can_create_projects(self) -> bool:
        """
        Check if user can create projects
        
        Returns:
            bool: True if user can create projects, False otherwise
        """
        return self.has_permission('write') or self.role in ['super_admin', 'admin', 'manager', 'user']
    
    def can_delete_projects(self) -> bool:
        """
        Check if user can delete projects
        
        Returns:
            bool: True if user can delete projects, False otherwise
        """
        return self.has_permission('manage') or self.role in ['super_admin', 'admin']
    
    def can_share_data(self) -> bool:
        """
        Check if user can share data
        
        Returns:
            bool: True if user can share data, False otherwise
        """
        # Independent users cannot share data
        if self.is_independent:
            return False
        
        return self.has_permission('write') or self.role in ['super_admin', 'admin', 'manager']
    
    def get_accessible_modules(self) -> List[str]:
        """
        Get list of modules user can access
        
        Returns:
            list: List of accessible module names
        """
        all_modules = [
            'aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j',
            'certificate-manager', 'federated-learning', 'physics-modeling'
        ]
        
        accessible_modules = []
        for module in all_modules:
            if self.can_access_module(module):
                accessible_modules.append(module)
        
        return accessible_modules
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user context to dictionary
        
        Returns:
            dict: User context as dictionary
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'organization_id': self.organization_id,
            'organization_name': self.organization_name,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'is_independent': self.is_independent,
            'user_type': self.get_user_type(),
            'data_scope': self.get_data_scope(),
            'storage_info': self.get_storage_info(),
            'project_limits': self.get_project_limits(),
            'accessible_modules': self.get_accessible_modules(),
            'phone': self.phone,
            'job_title': self.job_title,
            'department': self.department,
            'bio': self.bio,
            'mfa_enabled': self.mfa_enabled,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'last_login': self.last_login,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __str__(self) -> str:
        """String representation of user context"""
        return f"UserContext(user_id={self.user_id}, username={self.username}, role={self.role}, type={self.get_user_type()})"
    
    def __repr__(self) -> str:
        """Representation of user context"""
        return self.__str__()

