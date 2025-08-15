"""
Organization Service for AASX Module
===================================

This service handles organization-based data operations and filtering
for multi-tenant support.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from webapp.core.context.user_context import UserContext

logger = logging.getLogger(__name__)

class OrganizationService:
    """
    Service for handling organization-based data operations
    """
    
    def __init__(self, user_context: UserContext):
        """
        Initialize service with user context
        
        Args:
            user_context: User context object containing user information
        """
        self.user_context = user_context
        self.user_id = getattr(user_context, 'user_id', None)
        self.organization_id = getattr(user_context, 'organization_id', None)
        # All users are organization users - no independent users
        self.user_type = getattr(user_context, 'get_user_type', lambda: 'organization')()
        
        # Initialize database connection
        from src.shared.database.connection_manager import DatabaseConnectionManager
        from src.shared.database.base_manager import BaseDatabaseManager
        
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        
        # Initialize repositories
        from src.shared.repositories.project_repository import ProjectRepository
        from src.shared.repositories.file_repository import FileRepository
        from src.shared.repositories.use_case_repository import UseCaseRepository
        
        self.project_repo = ProjectRepository(self.db_manager)
        self.file_repo = FileRepository(self.db_manager)
        self.use_case_repo = UseCaseRepository(self.db_manager)
    
    def get_organization_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects for the organization - organization-only access
        
        Returns:
            List of project dictionaries
        """
        try:
            # All users are organization users - get organization projects
            query = """
                SELECT p.*, puc.use_case_id, uc.name as use_case_name, uc.category as use_case_category
                FROM projects p
                LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
                LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
                WHERE p.org_id = ?
                ORDER BY p.created_at DESC
            """
            projects = self.db_manager.execute_query(query, (self.organization_id,))
            
            # Transform to API format
            api_projects = []
            for project in projects:
                api_project = {
                    "id": project["project_id"],
                    "name": project["name"],
                    "description": project["description"],
                    "use_case_id": project["use_case_id"],
                    "use_case_name": project["use_case_name"],
                    "use_case_category": project["use_case_category"],
                    "created_by": project["created_by"],
                    "organization_id": project["organization_id"],
                    "created_at": project["created_at"],
                    "updated_at": project["updated_at"],
                    "status": project["status"],
                    "file_count": self.get_project_file_count(project["project_id"])
                }
                api_projects.append(api_project)
            
            return api_projects
            
        except Exception as e:
            logger.error(f"Error getting organization projects: {e}")
            raise Exception(f"Failed to get organization projects: {str(e)}")
    
    def get_organization_files(self) -> List[Dict[str, Any]]:
        """
        Get all files for the organization - organization-only access
        
        Returns:
            List of file dictionaries
        """
        try:
            # All users are organization users - get organization files
            query = """
                SELECT f.*, p.name as project_name, uc.name as use_case_name
                FROM files f
                LEFT JOIN projects p ON f.project_id = p.project_id
                LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
                LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
                WHERE p.org_id = ?
                ORDER BY f.created_at DESC
            """
            files = self.db_manager.execute_query(query, (self.organization_id,))
            
            # Transform to API format
            api_files = []
            for file in files:
                api_file = {
                    "id": file["file_id"],
                    "filename": file["filename"],
                    "original_filename": file["original_filename"],
                    "project_id": file["project_id"],
                    "project_name": file["project_name"],
                    "use_case_name": file["use_case_name"],
                    "file_path": file["file_path"],
                    "file_size": file["size"],
                    "user_id": file["user_id"],
                    "created_at": file["created_at"],
                    "updated_at": file["updated_at"],
                    "status": file["status"],
                    "description": file["description"]
                }
                api_files.append(api_file)
            
            return api_files
            
        except Exception as e:
            logger.error(f"Error getting organization files: {e}")
            raise Exception(f"Failed to get organization files: {str(e)}")
    
    def get_organization_statistics(self) -> Dict[str, Any]:
        """
        Get organization statistics - organization-only access
        
        Returns:
            Dictionary containing organization statistics
        """
        try:
            # All users are organization users - get organization statistics
            # Get organization statistics
            project_query = """
                SELECT COUNT(*) as project_count
                FROM projects
                WHERE org_id = ?
            """
            project_result = self.db_manager.execute_query(project_query, (self.organization_id,))
            project_count = project_result[0]["project_count"] or 0
            
            file_query = """
                SELECT COUNT(*) as file_count, SUM(size) as total_storage
                FROM files f
                LEFT JOIN projects p ON f.project_id = p.project_id
                WHERE p.org_id = ?
            """
            file_result = self.db_manager.execute_query(file_query, (self.organization_id,))
            file_count = file_result[0]["file_count"] or 0
            total_storage = file_result[0]["total_storage"] or 0
            
            member_query = """
                SELECT COUNT(DISTINCT user_id) as member_count
                FROM projects
                WHERE p.org_id = ?
            """
            member_result = self.db_manager.execute_query(member_query, (self.organization_id,))
            member_count = member_result[0]["member_count"] or 0
            
            return {
                "organization_id": self.organization_id,
                "organization_name": getattr(self.user_context, 'organization_name', None),
                "total_projects": project_count,
                "total_files": file_count,
                "total_storage": total_storage,
                "total_storage_gb": round(total_storage / (1024 * 1024 * 1024), 2),
                "member_count": member_count,
                "is_organization": True,
                "storage_limit_gb": 100,
                "storage_usage_percentage": min(100, (total_storage / (100 * 1024 * 1024 * 1024)) * 100)
            }
            
        except Exception as e:
            logger.error(f"Error getting organization statistics: {e}")
            raise Exception(f"Failed to get organization statistics: {str(e)}")
    
    def get_organization_members(self) -> List[Dict[str, Any]]:
        """
        Get organization members - organization-only access
        
        Returns:
            List of member dictionaries
        """
        try:
            # All users are organization users - get organization members
            query = """
                SELECT DISTINCT p.created_by, COUNT(p.project_id) as project_count
                FROM projects p
                WHERE p.org_id = ?
                GROUP BY p.created_by
                ORDER BY project_count DESC
            """
            members = self.db_manager.execute_query(query, (self.organization_id,))
            
            # Transform to API format
            api_members = []
            for member in members:
                api_member = {
                    "user_id": member["created_by"],
                    "project_count": member["project_count"],
                    "is_current_user": member["created_by"] == self.user_id
                }
                api_members.append(api_member)
            
            return api_members
            
        except Exception as e:
            logger.error(f"Error getting organization members: {e}")
            raise Exception(f"Failed to get organization members: {str(e)}")
    
    def can_manage_organization(self) -> bool:
        """
        Check if user can manage the organization - organization-only access
        
        Returns:
            True if user can manage, False otherwise
        """
        try:
            # Super admins can manage everything
            user_role = getattr(self.user_context, 'role', 'viewer')
            if user_role == "super_admin":
                return True
            
            # Organization admins can manage their organization
            if user_role == "admin":
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking organization management permissions: {e}")
            return False
    
    def get_organization_settings(self) -> Dict[str, Any]:
        """
        Get organization settings - organization-only access
        
        Returns:
            Dictionary containing organization settings
        """
        try:
            # All users are organization users - get organization settings
            # Get organization settings from database
            query = """
                SELECT organization_id, organization_name, settings
                FROM organizations
                WHERE organization_id = ?
            """
            result = self.db_manager.execute_query(query, (self.organization_id,))
            
            if not result:
                return {
                    "organization_id": self.organization_id,
                    "organization_name": getattr(self.user_context, 'organization_name', None),
                    "settings": {},
                    "can_manage": self.can_manage_organization()
                }
            
            organization = result[0]
            settings = organization.get("settings", {})
            
            return {
                "organization_id": organization["organization_id"],
                "organization_name": organization["organization_name"],
                "settings": settings,
                "can_manage": self.can_manage_organization()
            }
            
        except Exception as e:
            logger.error(f"Error getting organization settings: {e}")
            raise Exception(f"Failed to get organization settings: {str(e)}")
    
    def update_organization_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update organization settings - organization-only access
        
        Args:
            settings: Settings dictionary to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.can_manage_organization():
                raise Exception("User does not have permission to manage organization")
            
            # All users are organization users - can update organization settings
            # Update organization settings in database
            query = """
                UPDATE organizations
                SET settings = ?
                WHERE organization_id = ?
            """
            self.db_manager.execute_query(query, (str(settings), self.organization_id))
            
            logger.info(f"Updated organization settings for {self.organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating organization settings: {e}")
            raise Exception(f"Failed to update organization settings: {str(e)}")
    
    def get_project_file_count(self, project_id: str) -> int:
        """
        Get file count for a project - organization-only access
        
        Args:
            project_id: Project ID
            
        Returns:
            File count
        """
        try:
            # All users are organization users - can access organization projects
            query = """
                SELECT COUNT(*) as file_count
                FROM files f
                LEFT JOIN projects p ON f.project_id = p.project_id
                WHERE p.project_id = ? AND (p.created_by = ? OR p.organization_id = ?)
            """
            result = self.db_manager.execute_query(query, (project_id, self.user_id, self.organization_id))
            
            return result[0]["file_count"] or 0
            
        except Exception as e:
            logger.error(f"Error getting project file count: {e}")
            return 0
