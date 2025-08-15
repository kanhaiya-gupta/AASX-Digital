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
        # All users have organization IDs - no independent users
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
    

    
    def get_user_projects(self) -> List[Dict[str, Any]]:
        """
        Get projects for current user - strict organization-only access
        
        Returns:
            List of project dictionaries
        """
        try:
            logger.info(f"get_user_projects called for user: {getattr(self.user_context, 'username', 'unknown')}")
            logger.info(f"User role: {getattr(self.user_context, 'role', 'unknown')}")
            logger.info(f"Organization ID: {self.organization_id}")
            logger.info(f"User context type: {type(self.user_context)}")
            logger.info(f"User context attributes: {dir(self.user_context)}")
            
            # All users are organization users - strict org filtering
            query = """
                SELECT p.*, puc.use_case_id, uc.name as use_case_name, uc.category as use_case_category
                FROM projects p
                LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
                LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
                WHERE p.org_id = ?
                ORDER BY p.created_at DESC
            """
            logger.info(f"Executing query with org_id: {self.organization_id}")
            projects = self.db_manager.execute_query(query, (self.organization_id,))
            logger.info(f"Organization user query returned: {len(projects) if projects else 0} projects")
            
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
                    "user_id": project["user_id"],
                    "org_id": project["org_id"],
                    "created_at": project["created_at"],
                    "updated_at": project["updated_at"],
                    "status": project.get("status", "active"),
                    "file_count": self.get_project_file_count(project["project_id"])
                }
                api_projects.append(api_project)
            
            return api_projects
            
        except Exception as e:
            logger.error(f"Error getting user projects: {e}")
            raise Exception(f"Failed to get user projects: {str(e)}")
    
    def get_projects_by_use_case(self, use_case_id: str) -> List[Dict[str, Any]]:
        """
        Get projects for a specific use case - strict organization-only access
        
        Args:
            use_case_id: Use case ID to filter projects
            
        Returns:
            List of project dictionaries
        """
        try:
            # All users are organization users - strict org filtering
            query = """
                SELECT p.*, puc.use_case_id, uc.name as use_case_name, uc.category as use_case_category
                FROM projects p
                LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
                LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
                WHERE puc.use_case_id = ? AND p.org_id = ?
                ORDER BY p.created_at DESC
            """
            projects = self.db_manager.execute_query(query, (use_case_id, self.organization_id))
            
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
                    "user_id": project["user_id"],
                    "org_id": project["org_id"],
                    "created_at": project["created_at"],
                    "updated_at": project["updated_at"],
                    "status": project.get("status", "active"),
                    "file_count": self.get_project_file_count(project["project_id"])
                }
                api_projects.append(api_project)
            
            return api_projects
            
        except Exception as e:
            logger.error(f"Error getting projects by use case: {e}")
            raise Exception(f"Failed to get projects by use case: {str(e)}")
    
    def get_user_files(self) -> List[Dict[str, Any]]:
        """
        Get files for current user - strict organization-only access
        
        Returns:
            List of file dictionaries
        """
        try:
            # All users are organization users - strict org filtering
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
                    "status": file.get("status", "active"),
                    "description": file.get("description", "")
                }
                api_files.append(api_file)
            
            return api_files
            
        except Exception as e:
            logger.error(f"Error getting user files: {e}")
            raise Exception(f"Failed to get user files: {str(e)}")
    
    def get_user_storage_usage(self) -> Dict[str, Any]:
        """
        Get storage usage for current user - organization-based
        
        Returns:
            Dictionary containing storage usage information
        """
        try:
            # All users are organization users - organization storage
            query = """
                SELECT SUM(size) as total_size, COUNT(*) as file_count
                FROM files f
                LEFT JOIN projects p ON f.project_id = p.project_id
                WHERE p.org_id = ?
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
        Get project limits for current user - organization-based
        
        Returns:
            Dictionary containing project limits information
        """
        try:
            # All users are organization users - organization project limits
            query = """
                SELECT COUNT(*) as project_count
                FROM projects
                WHERE org_id = ?
            """
            result = self.db_manager.execute_query(query, (self.organization_id,))
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
            project_data["user_id"] = self.user_id
            
            # All users are organization users - always set organization_id
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
        Check if user can access a specific project - strict organization-based
        
        Args:
            project_id: Project ID to check
            
        Returns:
            True if user can access, False otherwise
        """
        try:
            query = """
                SELECT user_id, org_id
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
            if project["user_id"] == self.user_id:
                return True
            
            # Check if user is in the same organization
            if project["org_id"] == self.organization_id:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking project access: {e}")
            return False
    
    def get_user_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific project if user can access it
        
        Args:
            project_id: Project ID to retrieve
            
        Returns:
            Project dictionary if accessible, None otherwise
        """
        try:
            if not self.can_access_project(project_id):
                return None
            
            query = """
                SELECT p.*, puc.use_case_id, uc.name as use_case_name, uc.category as use_case_category
                FROM projects p
                LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
                LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
                WHERE p.project_id = ?
            """
            result = self.db_manager.execute_query(query, (project_id,))
            
            if not result:
                return None
            
            project = result[0]
            
            # Transform to API format
            api_project = {
                "id": project["project_id"],
                "name": project["name"],
                "description": project.get("description", ""),
                "use_case_id": project["use_case_id"],
                "use_case_name": project.get("use_case_name", ""),
                "use_case_category": project.get("use_case_category", ""),
                "user_id": project["user_id"],
                "org_id": project.get("org_id"),
                "created_at": project.get("created_at"),
                "updated_at": project.get("updated_at"),
                "status": project.get("status", "active"),
                "tags": project.get("tags", "").split(",") if project.get("tags") else []
            }
            
            return api_project
            
        except Exception as e:
            logger.error(f"Error getting user project: {e}")
            return None
    
    def can_access_file(self, file_id: str) -> bool:
        """
        Check if user can access a specific file - strict organization-based
        
        Args:
            file_id: File ID to check
            
        Returns:
            True if user can access, False otherwise
        """
        try:
            query = """
                SELECT f.user_id, p.org_id, p.user_id as project_user_id, p.is_public
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
            if file["user_id"] == self.user_id:
                return True
            
            # Check if user created the project
            if file["project_user_id"] == self.user_id:
                return True
            
            # Check if user is in the same organization
            if file["org_id"] == self.organization_id:
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
        Get user-specific statistics - organization-based
        
        Returns:
            Dictionary containing user statistics
        """
        try:
            stats = {
                "user_type": "organization",  # All users are organization users
                "org_id": self.organization_id,
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

    def get_user_use_cases(self) -> List[Dict[str, Any]]:
        """
        Get use cases accessible to the current user - strict organization-only access
        
        Returns:
            List of use case dictionaries
        """
        try:
            logger.info(f"get_user_use_cases called for user: {getattr(self.user_context, 'username', 'unknown')}")
            logger.info(f"User role: {getattr(self.user_context, 'role', 'unknown')}")
            logger.info(f"Organization ID: {self.organization_id}")
            
            # Use the exact working query from the script
            query = """
                SELECT 
                    uc.use_case_id,
                    uc.name,
                    uc.description,
                    COUNT(p.project_id) as project_count
                FROM use_cases uc
                LEFT JOIN project_use_case_links pcl ON uc.use_case_id = pcl.use_case_id
                LEFT JOIN projects p ON pcl.project_id = p.project_id AND p.org_id = ?
                WHERE uc.use_case_id IN (
                    SELECT pcl2.use_case_id
                    FROM project_use_case_links pcl2
                    INNER JOIN projects p2 ON pcl2.project_id = p2.project_id
                    WHERE p2.org_id = ?
                    GROUP BY pcl2.use_case_id
                    HAVING COUNT(*) = (
                        SELECT COUNT(*)
                        FROM project_use_case_links pcl3
                        WHERE pcl3.use_case_id = pcl2.use_case_id
                    )
                    UNION
                    SELECT uc2.use_case_id
                    FROM use_cases uc2
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM project_use_case_links pcl4
                        INNER JOIN projects p4 ON pcl4.project_id = p4.project_id
                        WHERE pcl4.use_case_id = uc2.use_case_id
                    )
                )
                GROUP BY uc.use_case_id
                ORDER BY uc.name ASC
            """
            use_cases = self.db_manager.execute_query(query, (self.organization_id, self.organization_id))
            logger.info(f"Organization user query returned: {len(use_cases) if use_cases else 0} use cases")
            
            # Transform to API format
            api_use_cases = []
            for use_case in use_cases:
                api_use_case = {
                    "id": use_case["use_case_id"],
                    "name": use_case["name"],
                    "description": use_case.get("description", ""),
                    "category": use_case.get("category", ""),
                    "project_count": use_case["project_count"] or 0,
                    "created_at": use_case.get("created_at"),
                    "updated_at": use_case.get("updated_at")
                }
                api_use_cases.append(api_use_case)
            
            return api_use_cases
            
        except Exception as e:
            logger.error(f"Error getting user use cases: {e}")
            return []
    
    def get_user_file_by_path(self, use_case_name: str, project_name: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get file information by use case, project, and filename (if user can access it)
        
        Args:
            use_case_name: Name of the use case
            project_name: Name of the project
            filename: Name of the file
            
        Returns:
            File dictionary if accessible, None otherwise
        """
        try:
            # First get the use case ID
            use_case_query = """
                SELECT use_case_id FROM use_cases WHERE name = ?
            """
            use_case_result = self.db_manager.execute_query(use_case_query, (use_case_name,))
            
            if not use_case_result:
                return None
            
            use_case_id = use_case_result[0]["use_case_id"]
            
            # Then get the project ID
            project_query = """
                SELECT p.project_id, p.user_id, p.org_id
                FROM projects p
                LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
                WHERE puc.use_case_id = ? AND p.name = ?
            """
            project_result = self.db_manager.execute_query(project_query, (use_case_id, project_name))
            
            if not project_result:
                return None
            
            project = project_result[0]
            
            # Check if user can access this project
            if not self.can_access_project(project["project_id"]):
                return None
            
            # Finally get the file
            file_query = """
                SELECT f.*, p.name as project_name, uc.name as use_case_name
                FROM files f
                LEFT JOIN projects p ON f.project_id = p.project_id
                LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
                LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
                WHERE f.filename = ? AND p.project_id = ?
            """
            file_result = self.db_manager.execute_query(file_query, (filename, project["project_id"]))
            
            if not file_result:
                return None
            
            file_data = file_result[0]
            
            # Transform to API format
            api_file = {
                "id": file_data["file_id"],
                "filename": file_data["filename"],
                "file_path": file_data.get("file_path", ""),
                "file_size": file_data.get("size", 0),
                "file_type": file_data.get("file_type", ""),
                "project_id": file_data["project_id"],
                "project_name": file_data.get("project_name", ""),
                "use_case_name": file_data.get("use_case_name", ""),
                "status": file_data.get("status", "pending"),
                "created_at": file_data.get("created_at"),
                "updated_at": file_data.get("updated_at"),
                "metadata": file_data.get("metadata", {})
            }
            
            return api_file
            
        except Exception as e:
            logger.error(f"Error getting user file by path: {e}")
            return None
    
    def get_user_file_details(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed file information if user can access it
        
        Args:
            file_id: File ID to retrieve
            
        Returns:
            File dictionary with project and use case context if accessible, None otherwise
        """
        try:
            if not self.can_access_file(file_id):
                return None
            
            query = """
                SELECT f.*, p.name as project_name, p.description as project_description, 
                       uc.name as use_case_name, uc.category as use_case_category
                FROM files f
                LEFT JOIN projects p ON f.project_id = p.project_id
                LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
                LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
                WHERE f.file_id = ?
            """
            result = self.db_manager.execute_query(query, (file_id,))
            
            if not result:
                return None
            
            file_data = result[0]
            
            # Transform to API format
            api_file = {
                "id": file_data["file_id"],
                "filename": file_data["filename"],
                "original_filename": file_data.get("original_filename", ""),
                "file_path": file_data.get("file_path", ""),
                "file_size": file_data.get("size", 0),
                "file_type": file_data.get("file_type", ""),
                "project_id": file_data["project_id"],
                "project_name": file_data.get("project_name", ""),
                "project_description": file_data.get("project_description", ""),
                "use_case_name": file_data.get("use_case_name", ""),
                "use_case_category": file_data.get("use_case_category", ""),
                "status": file_data.get("status", "pending"),
                "created_at": file_data.get("created_at"),
                "updated_at": file_data.get("updated_at"),
                "metadata": file_data.get("metadata", {}),
                "user_id": file_data.get("user_id"),
                "org_id": file_data.get("org_id")
            }
            
            return api_file
            
        except Exception as e:
            logger.error(f"Error getting user file details: {e}")
            return None
