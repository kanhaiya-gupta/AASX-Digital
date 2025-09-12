"""
AI/RAG User-Specific Service
Handles user-specific data operations and access control for the AI/RAG module.
Distinguishes between independent users and organization members.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.engine.models.request_context import UserContext

logger = logging.getLogger(__name__)

class AIRAGUserSpecificService:
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
        logger.info(f"Initialized AIRAGUserSpecificService for user {self.user_id} "
                   f"(type: {self.user_type}, independent: {self.is_independent})")

    def get_user_projects(self) -> List[Dict[str, Any]]:
        """Get projects accessible to the current user"""
        try:
            if self.is_independent:
                # Independent users see only their own projects
                # Mock implementation - replace with actual data retrieval
                return [
                    {
                        "id": "user_project_1",
                        "name": "Personal AI Project",
                        "description": "User's personal AI/RAG project",
                        "created_by": self.user_id,
                        "organization_id": None,
                        "is_private": True
                    }
                ]
            else:
                # Organization members see organization projects + their own
                # Mock implementation - replace with actual data retrieval
                return [
                    {
                        "id": "org_project_1",
                        "name": "Organization AI Project",
                        "description": "Shared organization AI/RAG project",
                        "created_by": "org_user_1",
                        "organization_id": self.organization_id,
                        "is_private": False
                    },
                    {
                        "id": "user_project_1",
                        "name": "My AI Project",
                        "description": "User's personal AI/RAG project",
                        "created_by": self.user_id,
                        "organization_id": self.organization_id,
                        "is_private": True
                    }
                ]
        except Exception as e:
            logger.error(f"Error getting user projects: {e}")
            return []

    def get_user_files(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get files accessible to the current user"""
        try:
            if self.is_independent:
                # Independent users see only their own files
                # Mock implementation - replace with actual data retrieval
                return [
                    {
                        "id": "user_file_1",
                        "name": "personal_document.pdf",
                        "project_id": project_id or "user_project_1",
                        "created_by": self.user_id,
                        "organization_id": None,
                        "is_private": True
                    }
                ]
            else:
                # Organization members see organization files + their own
                # Mock implementation - replace with actual data retrieval
                return [
                    {
                        "id": "org_file_1",
                        "name": "shared_document.pdf",
                        "project_id": project_id or "org_project_1",
                        "created_by": "org_user_1",
                        "organization_id": self.organization_id,
                        "is_private": False
                    },
                    {
                        "id": "user_file_1",
                        "name": "my_document.pdf",
                        "project_id": project_id or "user_project_1",
                        "created_by": self.user_id,
                        "organization_id": self.organization_id,
                        "is_private": True
                    }
                ]
        except Exception as e:
            logger.error(f"Error getting user files: {e}")
            return []

    def get_user_queries(self) -> List[Dict[str, Any]]:
        """Get AI/RAG queries performed by the current user"""
        try:
            # Mock implementation - replace with actual data retrieval
            return [
                {
                    "id": "query_1",
                    "query": "What is the status of project X?",
                    "technique_id": "technique_1",
                    "execution_time": 2.5,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": self.user_id,
                    "organization_id": self.organization_id
                }
            ]
        except Exception as e:
            logger.error(f"Error getting user queries: {e}")
            return []

    def get_user_statistics(self) -> Dict[str, Any]:
        """Get AI/RAG usage statistics for the current user"""
        try:
            user_projects = self.get_user_projects()
            user_files = self.get_user_files()
            user_queries = self.get_user_queries()
            
            return {
                "total_projects": len(user_projects),
                "total_files": len(user_files),
                "total_queries": len(user_queries),
                "user_id": self.user_id,
                "organization_id": self.organization_id,
                "is_independent": self.is_independent,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {}

    def can_access_project(self, project_id: str) -> bool:
        """Check if user can access a specific project"""
        try:
            user_projects = self.get_user_projects()
            return any(project["id"] == project_id for project in user_projects)
        except Exception as e:
            logger.error(f"Error checking project access: {e}")
            return False

    def can_access_file(self, file_id: str) -> bool:
        """Check if user can access a specific file"""
        try:
            user_files = self.get_user_files()
            return any(file["id"] == file_id for file in user_files)
        except Exception as e:
            logger.error(f"Error checking file access: {e}")
            return False

    def can_create_project(self) -> bool:
        """Check if user can create new projects"""
        required_permissions = ["write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_create_file(self) -> bool:
        """Check if user can create new files"""
        required_permissions = ["write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_delete_project(self, project_id: str) -> bool:
        """Check if user can delete a specific project"""
        if not self.can_access_project(project_id):
            return False
        
        # Check if user has delete permissions
        required_permissions = ["manage", "delete"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_delete_file(self, file_id: str) -> bool:
        """Check if user can delete a specific file"""
        if not self.can_access_file(file_id):
            return False
        
        # Check if user has delete permissions
        required_permissions = ["manage", "delete"]
        return any(perm in self.permissions for perm in required_permissions)

    def get_user_project_limits(self) -> Dict[str, Any]:
        """Get project creation limits for the current user"""
        if self.is_independent:
            return {
                "max_projects": 10,
                "max_files_per_project": 100,
                "max_storage_gb": 5.0
            }
        else:
            # Organization members may have different limits
            return {
                "max_projects": 50,
                "max_files_per_project": 500,
                "max_storage_gb": 25.0
            }

    # Enhanced query and analysis methods
    def can_access_enhanced_queries(self) -> bool:
        """Check if user can access enhanced query functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_auto_extraction(self) -> bool:
        """Check if user can access auto-extraction functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_file_extraction(self) -> bool:
        """Check if user can access file extraction functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_reverse_engineering(self) -> bool:
        """Check if user can access reverse engineering functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_file_context(self) -> bool:
        """Check if user can access file context functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_project_context(self) -> bool:
        """Check if user can access project context functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_use_case_context(self) -> bool:
        """Check if user can access use case context functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_digital_twin_context(self) -> bool:
        """Check if user can access digital twin context functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_related_files(self) -> bool:
        """Check if user can access related files functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_digital_twin_health(self) -> bool:
        """Check if user can access digital twin health functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_technique_comparison(self) -> bool:
        """Check if user can access technique comparison functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_technique_recommendations(self) -> bool:
        """Check if user can access technique recommendations functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    # System status and monitoring methods
    def can_access_system_status(self) -> bool:
        """Check if user can access system status information"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_etl_status(self) -> bool:
        """Check if user can access ETL status information"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_kg_status(self) -> bool:
        """Check if user can access knowledge graph status information"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_health_check(self) -> bool:
        """Check if user can access health check functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    # Data access methods
    def can_access_techniques(self) -> bool:
        """Check if user can access techniques information"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_collections(self) -> bool:
        """Check if user can access collections information"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_digital_twin_stats(self) -> bool:
        """Check if user can access digital twin statistics"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_vector_data_stats(self) -> bool:
        """Check if user can access vector data statistics"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_generator_config(self) -> bool:
        """Check if user can access generator configuration"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_models(self) -> bool:
        """Check if user can access models information"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_system_config(self) -> bool:
        """Check if user can access system configuration"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_query_config(self) -> bool:
        """Check if user can access query configuration"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_vector_config(self) -> bool:
        """Check if user can access vector configuration"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_vectors(self) -> bool:
        """Check if user can access vectors information"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_project_data(self) -> bool:
        """Check if user can access project data"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_vector_db_info(self) -> bool:
        """Check if user can access vector database information"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    # Additional functionality methods
    def can_access_demo(self) -> bool:
        """Check if user can access demo functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_search(self) -> bool:
        """Check if user can access search functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_manage_vector_data(self) -> bool:
        """Check if user can manage vector data (admin only)"""
        required_permissions = ["admin", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_aasx_analysis(self) -> bool:
        """Check if user can access AASX analysis functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_aasx_export(self) -> bool:
        """Check if user can access AASX export functionality"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    def can_access_documents(self) -> bool:
        """Check if user can access documents"""
        required_permissions = ["read", "write", "manage"]
        return any(perm in self.permissions for perm in required_permissions)

    # Data retrieval methods
    def get_user_documents(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get documents accessible to the current user"""
        try:
            if self.is_independent:
                # Independent users see only their own documents
                # Mock implementation - replace with actual data retrieval
                return [
                    {
                        "id": "user_doc_1",
                        "name": "personal_document.pdf",
                        "project_id": "user_project_1",
                        "created_by": self.user_id,
                        "organization_id": None,
                        "is_private": True
                    }
                ][:limit]
            else:
                # Organization members see organization documents + their own
                # Mock implementation - replace with actual data retrieval
                return [
                    {
                        "id": "org_doc_1",
                        "name": "shared_document.pdf",
                        "project_id": "org_project_1",
                        "created_by": "org_user_1",
                        "organization_id": self.organization_id,
                        "is_private": False
                    },
                    {
                        "id": "user_doc_1",
                        "name": "my_document.pdf",
                        "project_id": "user_project_1",
                        "created_by": self.user_id,
                        "organization_id": self.organization_id,
                        "is_private": True
                    }
                ][:limit]
        except Exception as e:
            logger.error(f"Error getting user documents: {e}")
            return []
