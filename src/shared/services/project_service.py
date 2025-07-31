"""
Project Service
==============

Business logic for project management in the AAS Data Modeling framework.
Handles project hierarchy, file management, and access control.
"""

from typing import List, Optional, Dict, Any
import uuid
from .base_service import BaseService
from ..models.project import Project
from ..repositories.project_repository import ProjectRepository
from ..repositories.use_case_repository import UseCaseRepository
from ..repositories.file_repository import FileRepository

class ProjectService(BaseService[Project]):
    """Service for project business logic."""
    
    def __init__(self, db_manager, use_case_repository: UseCaseRepository, file_repository: FileRepository):
        super().__init__(db_manager)
        self.use_case_repository = use_case_repository
        self.file_repository = file_repository
    
    def get_repository(self) -> ProjectRepository:
        """Get the project repository."""
        return ProjectRepository(self.db_manager)
    
    def create_project(self, data: Dict[str, Any], use_case_id: str) -> Project:
        """Create a new project with hierarchy validation."""
        # Validate business rules
        self._validate_project_creation(data, use_case_id)
        
        # Generate project ID using use case context
        use_case = self.use_case_repository.get_by_id(use_case_id)
        if not use_case:
            self._raise_business_error(f"Use case {use_case_id} not found")
        
        # Generate unique project ID
        project_id = self._generate_project_id(data["name"], use_case.name)
        data["project_id"] = project_id
        
        # Create project
        project = self.create(data)
        
        # Link to use case
        self.get_repository().link_to_use_case(project.project_id, use_case_id)
        
        self.logger.info(f"Created project: {project.name} in use case: {use_case.name}")
        return project
    
    def get_project_with_files(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project with all its files."""
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        # Validate hierarchy
        self._validate_project_hierarchy(project_id)
        
        files = self.file_repository.get_by_project(project_id)
        
        return {
            "project": project,
            "files": files,
            "file_count": len(files),
            "total_size": sum(file.size for file in files)
        }
    
    def get_projects_by_use_case(self, use_case_id: str) -> List[Project]:
        """Get all projects in a specific use case."""
        # Validate use case exists
        if not self.use_case_repository.get_by_id(use_case_id):
            self._raise_business_error(f"Use case {use_case_id} not found")
        
        return self.get_repository().get_by_use_case(use_case_id)
    
    def get_project_hierarchy_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project with its use case hierarchy information."""
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        # Get use cases this project belongs to
        use_cases = self.get_repository().get_project_use_cases(project_id)
        
        return {
            "project": project,
            "use_cases": use_cases,
            "primary_use_case": use_cases[0] if use_cases else None
        }
    
    def move_project_to_use_case(self, project_id: str, new_use_case_id: str) -> bool:
        """Move project to a different use case."""
        # Validate project exists
        project = self.get_by_id(project_id)
        if not project:
            self._raise_business_error(f"Project {project_id} not found")
        
        # Validate new use case exists
        new_use_case = self.use_case_repository.get_by_id(new_use_case_id)
        if not new_use_case:
            self._raise_business_error(f"Use case {new_use_case_id} not found")
        
        # Get current use cases
        current_use_cases = self.get_repository().get_project_use_cases(project_id)
        
        # Unlink from current use cases
        for use_case in current_use_cases:
            self.get_repository().unlink_from_use_case(project_id, use_case.id)
        
        # Link to new use case
        success = self.get_repository().link_to_use_case(project_id, new_use_case_id)
        
        if success:
            self.logger.info(f"Moved project {project.name} to use case {new_use_case.name}")
        
        return success
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project with cascading file deletion."""
        # Validate project exists
        project = self.get_by_id(project_id)
        if not project:
            self._raise_business_error(f"Project {project_id} not found")
        
        # Get all files in this project
        files = self.file_repository.get_by_project(project_id)
        
        # Delete all files
        for file in files:
            self.file_repository.delete(file.id)
        
        # Unlink from use cases
        use_cases = self.get_repository().get_project_use_cases(project_id)
        for use_case in use_cases:
            self.get_repository().unlink_from_use_case(project_id, use_case.id)
        
        # Delete the project
        success = self.delete(project_id)
        
        if success:
            self.logger.warning(f"Deleted project {project.name} with {len(files)} files")
        
        return success
    
    def update_project_statistics(self, project_id: str) -> bool:
        """Update project file count and total size."""
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        # Get current file statistics
        files = self.file_repository.get_by_project(project_id)
        file_count = len(files)
        total_size = sum(file.size for file in files)
        
        # Update project
        update_data = {
            "file_count": file_count,
            "total_size": total_size
        }
        
        success = self.update(project_id, update_data)
        
        if success:
            self.logger.debug(f"Updated project {project_id} statistics: {file_count} files, {total_size} bytes")
        
        return success
    
    def search_projects(self, search_term: str, use_case_id: Optional[str] = None) -> List[Project]:
        """Search projects with optional use case filtering."""
        if not search_term or len(search_term.strip()) < 2:
            self._raise_business_error("Search term must be at least 2 characters")
        
        projects = self.get_repository().search_projects(search_term.strip())
        
        # Filter by use case if specified
        if use_case_id:
            projects = [p for p in projects if self._project_belongs_to_use_case(p.id, use_case_id)]
        
        return projects
    
    def get_public_projects(self) -> List[Project]:
        """Get all public projects."""
        return self.get_repository().get_public_projects()
    
    def validate_project_hierarchy(self, project_id: str) -> bool:
        """Validate that project belongs to at least one use case."""
        return self._validate_project_hierarchy(project_id)
    
    # Business Logic Validation Methods
    
    def _validate_project_creation(self, data: Dict[str, Any], use_case_id: str) -> None:
        """Validate project creation business rules."""
        required_fields = ["name"]
        self._validate_required_fields(data, required_fields)
        
        # Validate name length
        self._validate_field_length(data, "name", 100)
        
        # Validate use case exists
        use_case = self.use_case_repository.get_by_id(use_case_id)
        if not use_case:
            self._raise_business_error(f"Use case {use_case_id} not found")
        
        # Check for duplicate project name in same use case
        existing_projects = self.get_repository().get_by_use_case(use_case_id)
        for project in existing_projects:
            if project.name == data["name"]:
                self._raise_business_error(f"Project '{data['name']}' already exists in use case '{use_case.name}'")
    
    def _validate_project_hierarchy(self, project_id: str) -> bool:
        """Validate that project belongs to at least one use case."""
        use_cases = self.get_repository().get_project_use_cases(project_id)
        if not use_cases:
            self._raise_business_error(f"Project {project_id} is not linked to any use case")
        return True
    
    def _project_belongs_to_use_case(self, project_id: str, use_case_id: str) -> bool:
        """Check if project belongs to a specific use case."""
        use_cases = self.get_repository().get_project_use_cases(project_id)
        return any(uc.id == use_case_id for uc in use_cases)
    
    def _generate_project_id(self, project_name: str, use_case_name: str) -> str:
        """Generate unique project ID using project name and use case name."""
        # Create a namespace using use case name
        namespace = uuid.uuid5(uuid.NAMESPACE_DNS, use_case_name)
        
        # Generate project ID using project name and namespace
        project_id = uuid.uuid5(namespace, project_name)
        
        return str(project_id)
    
    # Override base methods for project-specific logic
    
    def _validate_create(self, data: Dict[str, Any]) -> None:
        """Validate project creation."""
        # Note: This is called after _validate_project_creation, so we don't need to duplicate validation
        pass
    
    def _validate_update(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Validate project update."""
        # Check if project exists
        project = self.get_by_id(entity_id)
        if not project:
            self._raise_business_error(f"Project {entity_id} not found")
        
        # Validate name if being updated
        if "name" in data:
            self._validate_field_length(data, "name", 100)
    
    def _validate_delete(self, entity_id: str) -> None:
        """Validate project deletion."""
        # Check if project exists
        project = self.get_by_id(entity_id)
        if not project:
            self._raise_business_error(f"Project {entity_id} not found")
        
        # Check if project has files
        files = self.file_repository.get_by_project(entity_id)
        if files:
            self.logger.warning(f"Deleting project {entity_id} with {len(files)} files - cascading deletion will occur")
    
    def _post_create(self, entity: Project) -> None:
        """Post-creation logic for projects."""
        self.logger.info(f"Project '{entity.name}' created")
    
    def _post_update(self, entity: Project) -> None:
        """Post-update logic for projects."""
        self.logger.info(f"Project '{entity.name}' updated")
    
    def _post_delete(self, entity_id: str) -> None:
        """Post-deletion logic for projects."""
        self.logger.warning(f"Project {entity_id} deleted - audit trail required") 