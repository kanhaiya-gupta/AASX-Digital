"""
Project Repository
=================

Data access layer for projects in the AAS Data Modeling framework.
"""

from typing import List, Optional, Dict, Any
from ..database.base_manager import BaseDatabaseManager
from ..models.project import Project
from .base_repository import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    """Repository for project operations."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        super().__init__(db_manager, Project)
    
    def _get_table_name(self) -> str:
        return "projects"
    
    def _get_columns(self) -> List[str]:
        return [
            "project_id", "name", "description", "tags", "file_count", "total_size",
            "is_public", "access_level", "user_id", "metadata", 
            "created_at", "updated_at"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for projects table."""
        return "project_id"
    
    def get_by_use_case(self, use_case_id: str) -> List[Project]:
        """Get projects linked to a specific use case."""
        query = """
            SELECT p.* FROM projects p
            JOIN project_use_case_links puc ON p.project_id = puc.project_id
            WHERE puc.use_case_id = ?
        """
        results = self.db_manager.execute_query(query, (use_case_id,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_by_use_case_id(self, use_case_id: str) -> List[Dict[str, Any]]:
        """Get projects linked to a specific use case as dictionaries."""
        query = """
            SELECT p.*, puc.use_case_id FROM projects p
            JOIN project_use_case_links puc ON p.project_id = puc.project_id
            WHERE puc.use_case_id = ?
        """
        results = self.db_manager.execute_query(query, (use_case_id,))
        return results
    
    def get_all_with_use_cases(self) -> List[Dict[str, Any]]:
        """Get all projects with their use case relationships."""
        query = """
            SELECT p.*, puc.use_case_id FROM projects p
            LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
        """
        results = self.db_manager.execute_query(query)
        return results
    
    def get_by_owner(self, user_id: str) -> List[Project]:
        """Get projects by user."""
        query = "SELECT * FROM projects WHERE user_id = ?"
        results = self.db_manager.execute_query(query, (user_id,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_public_projects(self) -> List[Project]:
        """Get all public projects."""
        query = "SELECT * FROM projects WHERE is_public = 1"
        results = self.db_manager.execute_query(query)
        return [self.model_class.from_dict(row) for row in results]
    
    def search_projects(self, search_term: str) -> List[Project]:
        """Search projects by name or description."""
        query = """
            SELECT * FROM projects 
            WHERE name LIKE ? OR description LIKE ?
        """
        search_pattern = f"%{search_term}%"
        results = self.db_manager.execute_query(query, (search_pattern, search_pattern))
        return [self.model_class.from_dict(row) for row in results]
    
    def link_to_use_case(self, project_id: str, use_case_id: str) -> bool:
        """Link a project to a use case."""
        query = """
            INSERT INTO project_use_case_links (project_id, use_case_id, created_at)
            VALUES (?, ?, datetime('now'))
        """
        try:
            self.db_manager.execute_insert(query, (project_id, use_case_id))
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to link project {project_id} to use case {use_case_id}: {e}")
            return False
    
    def unlink_from_use_case(self, project_id: str, use_case_id: str) -> bool:
        """Unlink a project from a use case."""
        query = """
            DELETE FROM project_use_case_links 
            WHERE project_id = ? AND use_case_id = ?
        """
        try:
            affected_rows = self.db_manager.execute_update(query, (project_id, use_case_id))
            return affected_rows > 0
        except Exception:
            return False
    
    def get_project_use_cases(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all use cases linked to a project."""
        query = """
            SELECT uc.* FROM use_cases uc
            JOIN project_use_case_links puc ON uc.use_case_id = puc.use_case_id
            WHERE puc.project_id = ?
        """
        results = self.db_manager.execute_query(query, (project_id,))
        return results
    
    def update_file_count(self, project_id: str, file_count: int) -> bool:
        """Update the file count for a project."""
        query = "UPDATE projects SET file_count = ? WHERE project_id = ?"
        try:
            affected_rows = self.db_manager.execute_update(query, (file_count, project_id))
            return affected_rows > 0
        except Exception:
            return False
    
    def update_total_size(self, project_id: str, total_size: int) -> bool:
        """Update the total size for a project."""
        query = "UPDATE projects SET total_size = ? WHERE project_id = ?"
        try:
            affected_rows = self.db_manager.execute_update(query, (total_size, project_id))
            return affected_rows > 0
        except Exception:
            return False
    
    def get_project_by_name_and_use_case(self, project_name: str, use_case_id: str) -> Optional[Project]:
        """Get project by name within a specific use case."""
        query = """
            SELECT p.* FROM projects p
            JOIN project_use_case_links puc ON p.project_id = puc.project_id
            WHERE p.name = ? AND puc.use_case_id = ?
        """
        results = self.db_manager.execute_query(query, (project_name, use_case_id))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def validate_project_hierarchy(self, project_id: str) -> bool:
        """Validate that a project exists and is linked to at least one use case."""
        # First check if the project exists
        project_query = "SELECT project_id FROM projects WHERE project_id = ?"
        project_results = self.db_manager.execute_query(project_query, (project_id,))
        
        if not project_results:
            return False
        
        # Then check if it's linked to at least one use case
        link_query = """
            SELECT COUNT(*) as link_count 
            FROM project_use_case_links 
            WHERE project_id = ?
        """
        link_results = self.db_manager.execute_query(link_query, (project_id,))
        
        return link_results[0]['link_count'] > 0
    
    def get_project_hierarchy_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project information with its linked use cases."""
        # Get project information
        project_query = "SELECT * FROM projects WHERE project_id = ?"
        project_results = self.db_manager.execute_query(project_query, (project_id,))
        
        if not project_results:
            return None
        
        project_data = project_results[0]
        project = self.model_class.from_dict(project_data)
        
        # Get linked use cases
        use_cases = self.get_project_use_cases(project_id)
        
        # Get primary use case (first one)
        primary_use_case = None
        if use_cases:
            primary_use_case = use_cases[0]
        
        return {
            "project": project,
            "use_cases": use_cases,
            "primary_use_case": primary_use_case
        } 