"""
Project Management Service
Handles all project CRUD operations and business logic.
Enforces Use Case → Projects → Files hierarchy.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.repositories.use_case_repository import UseCaseRepository

logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self):
        from src.shared.database.connection_manager import DatabaseConnectionManager
        from pathlib import Path
        
        # Create data directory and set database path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        self.project_repo = ProjectRepository(self.db_manager)
        self.use_case_repo = UseCaseRepository(self.db_manager)
    
    def generate_project_id(self, name: str, use_case_name: str = None) -> str:
        """Generate a deterministic project ID based on name and use case context."""
        if use_case_name:
            # Include use case context to ensure uniqueness across use cases
            combined_name = f"{use_case_name}_{name}"
        else:
            # Fallback to just project name (for backward compatibility)
            combined_name = name
            
        namespace_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, 'physics-projects.aas-data-modeling.com')
        project_uuid = uuid.uuid5(namespace_uuid, combined_name.lower().replace(' ', '-'))
        return str(project_uuid)
    
    def list_projects(self, use_case_id: str = None) -> List[Dict[str, Any]]:
        """Get all projects, optionally filtered by use case"""
        try:
            if use_case_id:
                # Get projects for specific use case
                projects = self.project_repo.get_by_use_case_id(use_case_id)
            else:
                # Get all projects with their use case relationships
                projects = self.project_repo.get_all_with_use_cases()
            
            return [project.to_dict() if hasattr(project, 'to_dict') else project for project in projects]
        except Exception as e:
            raise Exception(f"Failed to list projects: {str(e)}")
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific project with its files and use case info"""
        try:
            project = self.project_repo.get_by_id(project_id)
            if not project:
                return None
            
            project_dict = project.to_dict() if hasattr(project, 'to_dict') else project
            project_dict["id"] = project_id
            
            # Get files for this project
            from src.shared.repositories.file_repository import FileRepository
            file_repo = FileRepository(self.db_manager)
            files = file_repo.get_by_project_id(project_id)
            project_dict["files"] = files
            
            # Get use case information for this project
            use_cases = self.project_repo.get_project_use_cases(project_id)
            if use_cases:
                project_dict["use_case"] = use_cases[0]  # Project should belong to one use case
            else:
                project_dict["use_case"] = None
            
            return project_dict
        except Exception as e:
            raise Exception(f"Failed to get project {project_id}: {str(e)}")
    
    def create_project(self, project_data: Dict[str, Any], use_case_id: str) -> str:
        """Create a new project and link it to a use case"""
        try:
            # Validate use case exists
            use_case = self.use_case_repo.get_by_id(use_case_id)
            if not use_case:
                raise Exception(f"Use case {use_case_id} not found")
            
            # Get use case name for ID generation
            use_case_name = use_case.name if hasattr(use_case, 'name') else use_case.get("name")
            
            # Generate unique project ID that includes use case context
            project_id = self.generate_project_id(project_data.get('name', 'Unnamed Project'), use_case_name)
            
            # Create project using repository
            project_data['id'] = project_id  # Set the generated ID
            project = self.project_repo.create(project_data)
            
            if not project:
                raise Exception("Failed to create project")
            
            # Link project to use case
            success = self.project_repo.link_to_use_case(project_id, use_case_id)
            if not success:
                # If linking fails, delete the project
                self.project_repo.delete(project_id)
                raise Exception(f"Failed to link project to use case {use_case_id}")
            
            return project_id
        except Exception as e:
            raise Exception(f"Failed to create project: {str(e)}")
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing project"""
        try:
            if not self.project_repo.get_by_id(project_id):
                raise Exception("Project not found")
            
            return self.project_repo.update(project_id, updates)
        except Exception as e:
            raise Exception(f"Failed to update project {project_id}: {str(e)}")
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its files"""
        try:
            if not self.project_repo.get_by_id(project_id):
                raise Exception("Project not found")
            
            # Delete all files in this project
            from src.shared.repositories.file_repository import FileRepository
            file_repo = FileRepository(self.db_manager)
            files = file_repo.get_by_project_id(project_id)
            for file_info in files:
                file_id = file_info.get('file_id')
                if file_id:
                    file_repo.delete(file_id)
            
            # Unlink from use case first
            use_cases = self.project_repo.get_project_use_cases(project_id)
            for use_case in use_cases:
                self.project_repo.unlink_from_use_case(project_id, use_case.get('use_case_id'))
            
            # Delete the project
            return self.project_repo.delete(project_id)
        except Exception as e:
            raise Exception(f"Failed to delete project {project_id}: {str(e)}")
    
    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists"""
        try:
            project = self.project_repo.get_by_id(project_id)
            return project is not None
        except Exception as e:
            raise Exception(f"Failed to check project existence: {str(e)}")
    
    def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all files for a specific project"""
        try:
            if not self.project_repo.get_by_id(project_id):
                raise Exception("Project not found")
            
            # Get files using FileRepository
            from src.shared.repositories.file_repository import FileRepository
            file_repo = FileRepository(self.db_manager)
            files = file_repo.get_by_project_id(project_id)
            
            return files
        except Exception as e:
            raise Exception(f"Failed to get files for project {project_id}: {str(e)}")
    
    def link_project_to_use_case(self, project_id: str, use_case_id: str) -> bool:
        """Link a project to a use case"""
        try:
            # Validate both exist
            if not self.project_repo.get_by_id(project_id):
                raise Exception("Project not found")
            
            if not self.use_case_repo.get_by_id(use_case_id):
                raise Exception("Use case not found")
            
            return self.project_repo.link_to_use_case(project_id, use_case_id)
        except Exception as e:
            raise Exception(f"Failed to link project {project_id} to use case {use_case_id}: {str(e)}")
    
    def unlink_project_from_use_case(self, project_id: str, use_case_id: str) -> bool:
        """Unlink a project from a use case"""
        try:
            return self.project_repo.unlink_from_use_case(project_id, use_case_id)
        except Exception as e:
            raise Exception(f"Failed to unlink project {project_id} from use case {use_case_id}: {str(e)}")
    
    def get_project_use_cases(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all use cases for a specific project"""
        try:
            return self.project_repo.get_project_use_cases(project_id)
        except Exception as e:
            raise Exception(f"Failed to get use cases for project {project_id}: {str(e)}")
    
    def validate_project_hierarchy(self, project_id: str) -> Dict[str, Any]:
        """Validate that a project is properly linked to a use case"""
        try:
            if not self.project_repo.get_by_id(project_id):
                return {"valid": False, "error": "Project not found"}
            
            use_cases = self.project_repo.get_project_use_cases(project_id)
            if not use_cases:
                return {"valid": False, "error": "Project not linked to any use case"}
            
            return {
                "valid": True,
                "use_case": use_cases[0],
                "project_id": project_id
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def refresh_project_status(self, project_id: str = None) -> Dict[str, Any]:
        """Refresh project and file statuses"""
        try:
            # TODO: Implement refresh functionality when FileRepository is updated
            return {"status": "refresh_not_implemented", "message": "Refresh functionality to be implemented"}
        except Exception as e:
            raise Exception(f"Failed to refresh project status: {str(e)}")

# Global instance
project_service = ProjectService() 