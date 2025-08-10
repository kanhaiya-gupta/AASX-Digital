"""
User-Specific Service for AASX Module
====================================

This service handles user-specific data operations based on user context,
including independent users and organization members.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from webapp.core.context.user_context import UserContext

logger = logging.getLogger(__name__)

class UserSpecificService:
    """
    Service for handling user-specific data operations
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
        # Check if user is independent based on organization_id
        user_is_independent = getattr(user_context, 'is_independent', None)
        if user_is_independent is None:
            self.is_independent = self.organization_id is None
        else:
            self.is_independent = user_is_independent
        self.user_type = getattr(user_context, 'get_user_type', lambda: 'independent')()
        
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
    
    def get_user_projects(self) -> List[Dict[str, Any]]:
        """
        Get projects for current user based on user type
        
        Returns:
            List of project dictionaries
        """
        try:
            if self.is_independent:
                # Independent users only see their own projects
                query = """
                    SELECT p.*, uc.name as use_case_name, uc.category as use_case_category
                    FROM projects p
                    LEFT JOIN use_cases uc ON p.use_case_id = uc.use_case_id
                    WHERE p.created_by = ?
                    ORDER BY p.created_at DESC
                """
                projects = self.db_manager.execute_query(query, (self.user_id,))
            else:
                # Organization users see organization projects and their own projects
                query = """
                    SELECT p.*, uc.name as use_case_name, uc.category as use_case_category
                    FROM projects p
                    LEFT JOIN use_cases uc ON p.use_case_id = uc.use_case_id
                    WHERE p.created_by = ? OR p.organization_id = ?
                    ORDER BY p.created_at DESC
                """
                projects = self.db_manager.execute_query(query, (
                    self.user_id,
                    self.organization_id
                ))
            
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
            logger.error(f"Error getting user projects: {e}")
            raise Exception(f"Failed to get user projects: {str(e)}")
    
    def get_user_files(self) -> List[Dict[str, Any]]:
        """
        Get files for current user based on user type
        
        Returns:
            List of file dictionaries
        """
        try:
            if self.is_independent:
                # Independent users only see their own files
                query = """
                    SELECT f.*, p.name as project_name, uc.name as use_case_name
                    FROM files f
                    LEFT JOIN projects p ON f.project_id = p.project_id
                    LEFT JOIN use_cases uc ON p.use_case_id = uc.use_case_id
                    WHERE f.created_by = ?
                    ORDER BY f.created_at DESC
                """
                files = self.db_manager.execute_query(query, (self.user_id,))
            else:
                # Organization users see organization files and their own files
                query = """
                    SELECT f.*, p.name as project_name, uc.name as use_case_name
                    FROM files f
                    LEFT JOIN projects p ON f.project_id = p.project_id
                    LEFT JOIN use_cases uc ON p.use_case_id = uc.use_case_id
                    WHERE f.created_by = ? OR p.organization_id = ?
                    ORDER BY f.created_at DESC
                """
                files = self.db_manager.execute_query(query, (
                    self.user_id,
                    self.organization_id
                ))
            
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
                    "file_size": file["file_size"],
                    "created_by": file["created_by"],
                    "created_at": file["created_at"],
                    "updated_at": file["updated_at"],
                    "status": file["status"],
                    "description": file["description"]
                }
                api_files.append(api_file)
            
            return api_files
            
        except Exception as e:
            logger.error(f"Error getting user files: {e}")
            raise Exception(f"Failed to get user files: {str(e)}")
    
    def get_user_storage_usage(self) -> Dict[str, Any]:
        """
        Get storage usage for current user
        
        Returns:
            Dictionary containing storage usage information
        """
        try:
            if self.is_independent:
                # Independent users have personal storage limits
                query = """
                    SELECT SUM(file_size) as total_size, COUNT(*) as file_count
                    FROM files f
                    LEFT JOIN projects p ON f.project_id = p.project_id
                    WHERE f.created_by = ?
                """
                result = self.db_manager.execute_query(query, (self.user_id,))
                
                total_size = result[0]["total_size"] or 0
                file_count = result[0]["file_count"] or 0
                
                return {
                    "total_size": total_size,
                    "file_count": file_count,
                    "limit_gb": 5,  # Independent users get 5GB
                    "limit_type": "personal",
                    "used_gb": round(total_size / (1024 * 1024 * 1024), 2),
                    "available_gb": 5 - round(total_size / (1024 * 1024 * 1024), 2),
                    "usage_percentage": min(100, (total_size / (5 * 1024 * 1024 * 1024)) * 100)
                }
            else:
                # Organization users share organization storage
                query = """
                    SELECT SUM(file_size) as total_size, COUNT(*) as file_count
                    FROM files f
                    LEFT JOIN projects p ON f.project_id = p.project_id
                    WHERE p.organization_id = ?
                """
                result = self.db_manager.execute_query(query, (self.organization_id,))
                
                total_size = result[0]["total_size"] or 0
                file_count = result[0]["file_count"] or 0
                
                return {
                    "total_size": total_size,
                    "file_count": file_count,
                    "limit_gb": 100,  # Organization users get 100GB
                    "limit_type": "organization",
                    "used_gb": round(total_size / (1024 * 1024 * 1024), 2),
                    "available_gb": 100 - round(total_size / (1024 * 1024 * 1024), 2),
                    "usage_percentage": min(100, (total_size / (100 * 1024 * 1024 * 1024)) * 100)
                }
                
        except Exception as e:
            logger.error(f"Error getting user storage usage: {e}")
            raise Exception(f"Failed to get user storage usage: {str(e)}")
    
    def get_user_project_limits(self) -> Dict[str, Any]:
        """
        Get project limits for current user
        
        Returns:
            Dictionary containing project limits information
        """
        try:
            if self.is_independent:
                # Independent users have unlimited projects
                query = """
                    SELECT COUNT(*) as project_count
                    FROM projects
                    WHERE created_by = ?
                """
                result = self.db_manager.execute_query(query, (self.user_id,))
                project_count = result[0]["project_count"] or 0
                
                return {
                    "type": "personal",
                    "limit": -1,  # Unlimited for independent users
                    "used": project_count,
                    "available": -1,
                    "description": "Unlimited personal projects"
                }
            else:
                # Organization users have unlimited projects
                query = """
                    SELECT COUNT(*) as project_count
                    FROM projects
                    WHERE organization_id = ? OR created_by = ?
                """
                result = self.db_manager.execute_query(query, (
                    self.organization_id,
                    self.user_id
                ))
                project_count = result[0]["project_count"] or 0
                
                return {
                    "type": "organization",
                    "limit": -1,  # Unlimited for organization users
                    "used": project_count,
                    "available": -1,
                    "description": f"Unlimited organization projects - {getattr(self.user_context, 'organization_name', 'Unknown Organization')}"
                }
                
        except Exception as e:
            logger.error(f"Error getting user project limits: {e}")
            raise Exception(f"Failed to get user project limits: {str(e)}")
    
    def create_user_project(self, project_data: Dict[str, Any]) -> str:
        """
        Create project for current user
        
        Args:
            project_data: Project data dictionary
            
        Returns:
            Project ID
        """
        try:
            # Add user context to project data
            project_data["created_by"] = self.user_id
            
            if self.is_independent:
                # Independent users don't have organization_id
                project_data["organization_id"] = None
            else:
                project_data["organization_id"] = self.organization_id
            
            # Create project using repository
            project_id = self.project_repo.create(project_data)
            
            logger.info(f"Created project {project_id} for user {self.user_id}")
            return project_id
            
        except Exception as e:
            logger.error(f"Error creating user project: {e}")
            raise Exception(f"Failed to create project: {str(e)}")
    
    def can_access_project(self, project_id: str) -> bool:
        """
        Check if user can access a specific project
        
        Args:
            project_id: Project ID to check
            
        Returns:
            True if user can access, False otherwise
        """
        try:
            query = """
                SELECT created_by, organization_id
                FROM projects
                WHERE project_id = ?
            """
            result = self.db_manager.execute_query(query, (project_id,))
            
            if not result:
                return False
            
            project = result[0]
            
            # Super admins can access everything
            user_role = getattr(self.user_context, 'role', 'viewer')
            if user_role == "super_admin":
                return True
            
            # Check if user created the project
            if project["created_by"] == self.user_id:
                return True
            
            # Check if user is in the same organization
            if not self.is_independent and project["organization_id"] == self.organization_id:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking project access: {e}")
            return False
    
    def can_access_file(self, file_id: str) -> bool:
        """
        Check if user can access a specific file
        
        Args:
            file_id: File ID to check
            
        Returns:
            True if user can access, False otherwise
        """
        try:
            query = """
                SELECT f.created_by, p.organization_id, p.created_by as project_created_by
                FROM files f
                LEFT JOIN projects p ON f.project_id = p.project_id
                WHERE f.file_id = ?
            """
            result = self.db_manager.execute_query(query, (file_id,))
            
            if not result:
                return False
            
            file = result[0]
            
            # Super admins can access everything
            user_role = getattr(self.user_context, 'role', 'viewer')
            if user_role == "super_admin":
                return True
            
            # Check if user created the file
            if file["created_by"] == self.user_id:
                return True
            
            # Check if user created the project
            if file["project_created_by"] == self.user_id:
                return True
            
            # Check if user is in the same organization
            if not self.is_independent and file["organization_id"] == self.organization_id:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking file access: {e}")
            return False
    
    def get_project_file_count(self, project_id: str) -> int:
        """
        Get file count for a project (if user can access it)
        
        Args:
            project_id: Project ID
            
        Returns:
            File count
        """
        try:
            if not self.can_access_project(project_id):
                return 0
            
            query = """
                SELECT COUNT(*) as file_count
                FROM files
                WHERE project_id = ?
            """
            result = self.db_manager.execute_query(query, (project_id,))
            return result[0]["file_count"] or 0
            
        except Exception as e:
            logger.error(f"Error getting project file count: {e}")
            return 0
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user-specific statistics
        
        Returns:
            Dictionary containing user statistics
        """
        try:
            stats = {
                "user_type": self.user_type,
                "is_independent": self.is_independent,
                "organization_id": self.organization_id,
                "organization_name": getattr(self.user_context, 'organization_name', None),
                "storage_usage": self.get_user_storage_usage(),
                "project_limits": self.get_user_project_limits(),
                "total_projects": len(self.get_user_projects()),
                "total_files": len(self.get_user_files()),
                "role": getattr(self.user_context, 'role', 'viewer'),
                "permissions": getattr(self.user_context, 'permissions', [])
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            raise Exception(f"Failed to get user statistics: {str(e)}")
