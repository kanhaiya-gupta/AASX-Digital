"""
Certificate Manager Organization Service
======================================

Handles organization-based data operations for the Certificate Manager module,
supporting multi-tenancy and organization-specific data management.
"""

import logging
from typing import Dict, List, Optional, Any
from src.engine.models.request_context import UserContext

logger = logging.getLogger(__name__)

class CertificateManagerOrganizationService:
    """Service for handling organization-based certificate operations."""
    
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
        logger.info(f"Initialized CertificateManagerOrganizationService for user {self.user_id} "
                   f"(type: {self.user_type}, independent: {self.is_independent})")
    
    def can_manage_organization(self) -> bool:
        """Check if user can manage organization settings."""
        required_permissions = ['admin', 'manage_organization']
        return any(perm in self.permissions for perm in required_permissions)
    
    async def get_organization_certificates(self) -> List[Dict[str, Any]]:
        """Get all certificates for the organization."""
        if self.is_independent:
            return []
        
        # Mock implementation
        return [
            {
                "id": f"cert_org_{self.organization_id}_1",
                "name": "Organization Certificate 1",
                "type": "organization",
                "status": "active",
                "created_by": "user_1",
                "organization_id": self.organization_id,
                "visibility": "organization"
            },
            {
                "id": f"cert_org_{self.organization_id}_2",
                "name": "Organization Certificate 2", 
                "type": "organization",
                "status": "active",
                "created_by": "user_2",
                "organization_id": self.organization_id,
                "visibility": "organization"
            }
        ]
    
    async def get_organization_members(self) -> List[Dict[str, Any]]:
        """Get organization members with their certificate access."""
        if self.is_independent:
            return []
        
        # Mock implementation
        return [
            {
                "user_id": "user_1",
                "username": "john.doe",
                "role": "admin",
                "certificates_count": 5,
                "last_active": "2024-01-15T10:30:00Z"
            },
            {
                "user_id": "user_2",
                "username": "jane.smith",
                "role": "user",
                "certificates_count": 3,
                "last_active": "2024-01-14T15:45:00Z"
            }
        ]
    
    async def get_organization_stats(self) -> Dict[str, Any]:
        """Get organization-wide certificate statistics."""
        if self.is_independent:
            return {}
        
        org_certificates = await self.get_organization_certificates()
        org_members = await self.get_organization_members()
        
        return {
            "total_certificates": len(org_certificates),
            "active_certificates": len([c for c in org_certificates if c["status"] == "active"]),
            "total_members": len(org_members),
            "admin_members": len([m for m in org_members if m["role"] == "admin"]),
            "organization_id": self.organization_id,
            "certificates_per_member": len(org_certificates) / len(org_members) if org_members else 0
        }
    
    async def get_organization_templates(self) -> List[Dict[str, Any]]:
        """Get organization-wide certificate templates."""
        if self.is_independent:
            return []
        
        # Mock implementation
        return [
            {
                "id": "template_org_1",
                "name": "Organization Template 1",
                "type": "organization",
                "created_by": "user_1",
                "organization_id": self.organization_id,
                "usage_count": 15
            },
            {
                "id": "template_org_2",
                "name": "Organization Template 2",
                "type": "organization", 
                "created_by": "user_2",
                "organization_id": self.organization_id,
                "usage_count": 8
            }
        ]
    
    async def get_organization_export_history(self) -> List[Dict[str, Any]]:
        """Get organization-wide export history."""
        if self.is_independent:
            return []
        
        # Mock implementation
        return [
            {
                "id": "export_org_1",
                "certificate_id": f"cert_org_{self.organization_id}_1",
                "format": "html",
                "exported_at": "2024-01-15T10:30:00Z",
                "user_id": "user_1",
                "organization_id": self.organization_id
            },
            {
                "id": "export_org_2",
                "certificate_id": f"cert_org_{self.organization_id}_2",
                "format": "pdf",
                "exported_at": "2024-01-14T15:45:00Z",
                "user_id": "user_2",
                "organization_id": self.organization_id
            }
        ]
    
    async def get_organization_settings(self) -> Dict[str, Any]:
        """Get organization certificate management settings."""
        if self.is_independent:
            return {}
        
        # Mock implementation
        return {
            "max_certificates_per_user": 100,
            "max_templates_per_user": 10,
            "max_exports_per_month": 1000,
            "storage_limit_mb": 10000,
            "auto_expiry_days": 365,
            "require_approval": False,
            "organization_id": self.organization_id
        }
    
    async def get_organization_health(self) -> Dict[str, Any]:
        """Get organization certificate health metrics."""
        if self.is_independent:
            return {}
        
        org_certificates = await self.get_organization_certificates()
        active_certificates = len([c for c in org_certificates if c["status"] == "active"])
        total_certificates = len(org_certificates)
        
        return {
            "total_certificates": total_certificates,
            "active_certificates": active_certificates,
            "expired_certificates": total_certificates - active_certificates,
            "health_score": (active_certificates / total_certificates * 100) if total_certificates > 0 else 100,
            "organization_id": self.organization_id
        }
    
    async def get_organization_performance(self) -> Dict[str, Any]:
        """Get organization certificate performance metrics."""
        if self.is_independent:
            return {}
        
        # Mock implementation
        return {
            "avg_certificate_creation_time": "2.5 minutes",
            "avg_export_time": "30 seconds",
            "total_exports_this_month": 150,
            "most_used_template": "Organization Template 1",
            "organization_id": self.organization_id
        }

