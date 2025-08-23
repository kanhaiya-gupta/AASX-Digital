"""
AI/RAG Organization Service
Handles organization-based data operations and supports multi-tenancy for the AI/RAG module.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from webapp.core.context.user_context import UserContext

logger = logging.getLogger(__name__)

class AIRAGOrganizationService:
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
        logger.info(f"Initialized AIRAGOrganizationService for user {self.user_id} "
                   f"(type: {self.user_type}, independent: {self.is_independent})")

    def get_organization_projects(self) -> List[Dict[str, Any]]:
        """Get all projects for the organization"""
        try:
            if self.is_independent:
                return []
            
            # Mock implementation - replace with actual data retrieval
            return [
                {
                    "id": "org_project_1",
                    "name": "Organization AI Project",
                    "description": "Shared organization AI/RAG project",
                    "created_by": "org_user_1",
                    "organization_id": self.organization_id,
                    "is_private": False,
                    "member_count": 5
                },
                {
                    "id": "org_project_2",
                    "name": "Team Collaboration Project",
                    "description": "Team-based AI/RAG collaboration",
                    "created_by": "org_user_2",
                    "organization_id": self.organization_id,
                    "is_private": False,
                    "member_count": 8
                }
            ]
        except Exception as e:
            logger.error(f"Error getting organization projects: {e}")
            return []

    def get_organization_files(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all files for the organization"""
        try:
            if self.is_independent:
                return []
            
            # Mock implementation - replace with actual data retrieval
            return [
                {
                    "id": "org_file_1",
                    "name": "shared_document.pdf",
                    "project_id": project_id or "org_project_1",
                    "created_by": "org_user_1",
                    "organization_id": self.organization_id,
                    "is_private": False,
                    "file_size_mb": 2.5
                },
                {
                    "id": "org_file_2",
                    "name": "team_report.pdf",
                    "project_id": project_id or "org_project_2",
                    "created_by": "org_user_2",
                    "organization_id": self.organization_id,
                    "is_private": False,
                    "file_size_mb": 1.8
                }
            ]
        except Exception as e:
            logger.error(f"Error getting organization files: {e}")
            return []

    def get_organization_members(self) -> List[Dict[str, Any]]:
        """Get organization members with their AI/RAG usage"""
        try:
            if self.is_independent:
                return []
            
            # Mock implementation - replace with actual data retrieval
            return [
                {
                    "user_id": "org_user_1",
                    "username": "john_doe",
                    "role": "manager",
                    "projects_created": 3,
                    "files_uploaded": 15,
                    "queries_performed": 45
                },
                {
                    "user_id": "org_user_2",
                    "username": "jane_smith",
                    "role": "user",
                    "projects_created": 1,
                    "files_uploaded": 8,
                    "queries_performed": 23
                }
            ]
        except Exception as e:
            logger.error(f"Error getting organization members: {e}")
            return []

    def get_organization_statistics(self) -> Dict[str, Any]:
        """Get organization-wide AI/RAG statistics"""
        try:
            if self.is_independent:
                return {}
            
            org_projects = self.get_organization_projects()
            org_files = self.get_organization_files()
            org_members = self.get_organization_members()
            
            return {
                "total_projects": len(org_projects),
                "total_files": len(org_files),
                "total_members": len(org_members),
                "organization_id": self.organization_id,
                "storage_used_gb": 15.5,
                "total_queries": 156,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting organization statistics: {e}")
            return {}

    def get_organization_settings(self) -> Dict[str, Any]:
        """Get organization AI/RAG settings and configuration"""
        try:
            if self.is_independent:
                return {}
            
            # Mock implementation - replace with actual data retrieval
            return {
                "organization_id": self.organization_id,
                "ai_model_whitelist": ["gpt-3.5-turbo", "gpt-4", "claude-3"],
                "max_file_size_mb": 100,
                "max_projects_per_user": 10,
                "enable_auto_scaling": True,
                "data_retention_days": 365,
                "enable_audit_logging": True
            }
        except Exception as e:
            logger.error(f"Error getting organization settings: {e}")
            return {}

    def get_organization_health(self) -> Dict[str, Any]:
        """Get organization AI/RAG system health metrics"""
        try:
            if self.is_independent:
                return {}
            
            # Mock implementation - replace with actual data retrieval
            return {
                "organization_id": self.organization_id,
                "system_status": "healthy",
                "uptime_percentage": 99.8,
                "response_time_ms": 150,
                "error_rate": 0.02,
                "last_maintenance": "2024-01-15T10:00:00Z",
                "next_maintenance": "2024-02-15T10:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error getting organization health: {e}")
            return {}

    def get_organization_performance(self) -> Dict[str, Any]:
        """Get organization AI/RAG performance metrics"""
        try:
            if self.is_independent:
                return {}
            
            # Mock implementation - replace with actual data retrieval
            return {
                "organization_id": self.organization_id,
                "queries_per_hour": 25,
                "average_response_time_ms": 180,
                "success_rate": 0.98,
                "peak_usage_hours": ["09:00", "14:00", "16:00"],
                "resource_utilization": 0.65,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting organization performance: {e}")
            return {}

    def can_manage_organization(self) -> bool:
        """Check if user can manage organization settings"""
        if self.is_independent:
            return False
        
        required_permissions = ["manage", "admin"]
        return any(perm in self.permissions for perm in required_permissions)

    def get_organization_limits(self) -> Dict[str, Any]:
        """Get organization AI/RAG usage limits"""
        if self.is_independent:
            return {}
        
        # Mock implementation - replace with actual data retrieval
        return {
            "max_projects": 100,
            "max_files_per_project": 1000,
            "max_storage_gb": 100.0,
            "max_concurrent_queries": 50,
            "max_users": 25
        }

