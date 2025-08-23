"""
Certificate Manager User-Specific Service
========================================

Handles user-specific data operations for the Certificate Manager module,
distinguishing between independent users and organization members.
"""

import logging
from typing import Dict, List, Optional, Any
from webapp.core.context.user_context import UserContext

logger = logging.getLogger(__name__)

class CertificateManagerUserSpecificService:
    """Service for handling user-specific certificate operations."""
    
    def __init__(self, user_context: UserContext):
        self.user_context = user_context
        self.user_id = getattr(user_context, 'user_id', None)
        self.organization_id = getattr(user_context, 'organization_id', None)
        user_is_independent = getattr(user_context, 'is_independent', None)
        if user_is_independent is None:
            self.is_independent = self.organization_id is None
        else:
            self.is_independent = user_is_independent
        self.user_type = getattr(user_context, 'get_user_type', lambda: 'independent')()
        self.role = getattr(user_context, 'role', 'viewer')
        self.permissions = getattr(user_context, 'permissions', [])
        logger.info(f"Initialized CertificateManagerUserSpecificService for user {self.user_id} "
                   f"(type: {self.user_type}, independent: {self.is_independent})")
    
    def can_access_certificate(self, certificate_id: str) -> bool:
        """Check if user can access a specific certificate."""
        # Mock implementation - in real system, check certificate ownership/permissions
        return True
    
    def can_create_certificate(self) -> bool:
        """Check if user can create certificates."""
        required_permissions = ['create', 'write']
        return any(perm in self.permissions for perm in required_permissions)
    
    def can_update_certificate(self, certificate_id: str) -> bool:
        """Check if user can update a specific certificate."""
        required_permissions = ['update', 'write']
        return any(perm in self.permissions for perm in required_permissions)
    
    def can_delete_certificate(self, certificate_id: str) -> bool:
        """Check if user can delete a specific certificate."""
        required_permissions = ['delete', 'admin']
        return any(perm in self.permissions for perm in required_permissions)
    
    def can_export_certificate(self, certificate_id: str) -> bool:
        """Check if user can export a specific certificate."""
        required_permissions = ['read', 'export']
        return any(perm in self.permissions for perm in required_permissions)
    
    async def get_user_certificates(self) -> List[Dict[str, Any]]:
        """Get certificates accessible to the current user."""
        # Mock implementation
        if self.is_independent:
            return [
                {
                    "id": f"cert_{self.user_id}_1",
                    "name": "Personal Certificate 1",
                    "type": "personal",
                    "status": "active",
                    "created_by": self.user_id,
                    "organization_id": None,
                    "visibility": "private"
                },
                {
                    "id": f"cert_{self.user_id}_2", 
                    "name": "Personal Certificate 2",
                    "type": "personal",
                    "status": "active",
                    "created_by": self.user_id,
                    "organization_id": None,
                    "visibility": "private"
                }
            ]
        else:
            return [
                {
                    "id": f"cert_org_{self.organization_id}_1",
                    "name": "Organization Certificate 1",
                    "type": "organization",
                    "status": "active",
                    "created_by": self.user_id,
                    "organization_id": self.organization_id,
                    "visibility": "organization"
                }
            ]
    
    async def get_user_certificate_stats(self) -> Dict[str, Any]:
        """Get certificate statistics for the current user."""
        user_certificates = await self.get_user_certificates()
        total_certificates = len(user_certificates)
        active_certificates = len([c for c in user_certificates if c["status"] == "active"])
        
        return {
            "total_certificates": total_certificates,
            "active_certificates": active_certificates,
            "expired_certificates": 0,
            "pending_certificates": 0,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "is_independent": self.is_independent
        }
    
    async def get_user_templates(self) -> List[Dict[str, Any]]:
        """Get certificate templates accessible to the current user."""
        # Mock implementation
        if self.is_independent:
            return [
                {
                    "id": "template_personal_1",
                    "name": "Personal Template 1",
                    "type": "personal",
                    "created_by": self.user_id,
                    "organization_id": None
                }
            ]
        else:
            return [
                {
                    "id": "template_org_1",
                    "name": "Organization Template 1", 
                    "type": "organization",
                    "created_by": self.user_id,
                    "organization_id": self.organization_id
                }
            ]
    
    async def get_user_export_history(self) -> List[Dict[str, Any]]:
        """Get export history for the current user."""
        # Mock implementation
        return [
            {
                "id": f"export_{self.user_id}_1",
                "certificate_id": f"cert_{self.user_id}_1",
                "format": "html",
                "exported_at": "2024-01-15T10:30:00Z",
                "user_id": self.user_id,
                "organization_id": self.organization_id
            }
        ]
    
    def get_user_certificate_limits(self) -> Dict[str, Any]:
        """Get certificate limits for the current user."""
        if self.is_independent:
            return {
                "max_certificates": 10,
                "max_templates": 5,
                "max_exports_per_month": 50,
                "storage_limit_mb": 100
            }
        else:
            return {
                "max_certificates": 1000,
                "max_templates": 50,
                "max_exports_per_month": 5000,
                "storage_limit_mb": 10000
            }

