"""
Use Case Service
===============

Business logic for use case management in the AAS Data Modeling framework.
Handles use case categorization, project hierarchy, and validation.
"""

from typing import List, Optional, Dict, Any
from .base_service import BaseService
from ..models.use_case import UseCase
from ..repositories.use_case_repository import UseCaseRepository
from ..repositories.project_repository import ProjectRepository

class UseCaseService(BaseService[UseCase]):
    """Service for use case business logic."""
    
    def __init__(self, db_manager, project_repository: ProjectRepository):
        super().__init__(db_manager)
        self.project_repository = project_repository
    
    def get_repository(self) -> UseCaseRepository:
        """Get the use case repository."""
        return UseCaseRepository(self.db_manager)
    
    def create_use_case(self, data: Dict[str, Any]) -> UseCase:
        """Create a new use case with business validation."""
        # Validate business rules
        self._validate_use_case_creation(data)
        
        # Create use case
        use_case = self.create(data)
        
        self.logger.info(f"Created use case: {use_case.name} (Category: {use_case.category})")
        return use_case
    
    def get_use_case_with_projects(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """Get use case with all its projects."""
        use_case = self.get_by_id(use_case_id)
        if not use_case:
            return None
        
        projects = self.project_repository.get_by_use_case(use_case_id)
        
        return {
            "use_case": use_case,
            "projects": projects,
            "project_count": len(projects)
        }
    
    def get_use_case_statistics(self, use_case_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a use case."""
        use_case = self.get_by_id(use_case_id)
        if not use_case:
            return {}
        
        # Get basic statistics from repository
        stats = self.get_repository().get_use_case_statistics()
        
        # Get projects for this use case
        projects = self.project_repository.get_by_use_case(use_case_id)
        
        # Calculate additional metrics
        total_files = sum(project.file_count for project in projects)
        total_size = sum(project.total_size for project in projects)
        
        return {
            **stats,
            "use_case": use_case,
            "project_count": len(projects),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "average_files_per_project": round(total_files / len(projects), 2) if projects else 0
        }
    
    def get_use_cases_by_category(self, category: str) -> List[UseCase]:
        """Get all use cases in a specific category."""
        if not category:
            self._raise_business_error("Category is required")
        
        return self.get_repository().get_by_category(category)
    
    def get_active_use_cases(self) -> List[UseCase]:
        """Get all active use cases."""
        return self.get_repository().get_active_use_cases()
    
    def search_use_cases(self, search_term: str) -> List[UseCase]:
        """Search use cases by name or description."""
        if not search_term or len(search_term.strip()) < 2:
            self._raise_business_error("Search term must be at least 2 characters")
        
        return self.get_repository().search_use_cases(search_term.strip())
    
    def update_use_case(self, use_case_id: str, data: Dict[str, Any]) -> Optional[UseCase]:
        """Update use case with business validation."""
        # Validate business rules
        self._validate_use_case_update(use_case_id, data)
        
        # Update use case
        use_case = self.update(use_case_id, data)
        
        if use_case:
            self.logger.info(f"Updated use case: {use_case.name}")
        
        return use_case
    
    def delete_use_case(self, use_case_id: str) -> bool:
        """Delete use case with cascading project deletion."""
        # Validate deletion
        self._validate_use_case_deletion(use_case_id)
        
        # Get all projects in this use case
        projects = self.project_repository.get_by_use_case(use_case_id)
        
        # Delete all projects (this will cascade to files)
        for project in projects:
            self.project_repository.delete(project.id)
        
        # Delete the use case
        success = self.delete(use_case_id)
        
        if success:
            self.logger.warning(f"Deleted use case {use_case_id} with {len(projects)} projects")
        
        return success
    
    def get_use_case_hierarchy(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """Get complete hierarchy for a use case."""
        use_case = self.get_by_id(use_case_id)
        if not use_case:
            return None
        
        projects = self.project_repository.get_by_use_case(use_case_id)
        
        # Build hierarchy
        hierarchy = {
            "use_case": use_case,
            "projects": []
        }
        
        for project in projects:
            project_data = {
                "project": project,
                "files": []  # Would be populated by FileService
            }
            hierarchy["projects"].append(project_data)
        
        return hierarchy
    
    def validate_use_case_exists(self, use_case_id: str) -> bool:
        """Validate that a use case exists and is active."""
        use_case = self.get_by_id(use_case_id)
        return use_case is not None and use_case.is_active
    
    # Business Logic Validation Methods
    
    def _validate_use_case_creation(self, data: Dict[str, Any]) -> None:
        """Validate use case creation business rules."""
        required_fields = ["name", "category"]
        self._validate_required_fields(data, required_fields)
        
        # Validate name length
        self._validate_field_length(data, "name", 100)
        
        # Validate category
        valid_categories = ["fluid_dynamics", "structural", "thermal", "multi_physics", "industrial", "other"]
        category = data.get("category")
        if category not in valid_categories:
            self._raise_business_error(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        # Check for duplicate name in same category
        existing = self.get_repository().get_by_name(data["name"])
        if existing and existing.category == category:
            self._raise_business_error(f"Use case '{data['name']}' already exists in category '{category}'")
    
    def _validate_use_case_update(self, use_case_id: str, data: Dict[str, Any]) -> None:
        """Validate use case update business rules."""
        # Check if use case exists
        existing = self.get_by_id(use_case_id)
        if not existing:
            self._raise_business_error(f"Use case {use_case_id} not found")
        
        # Validate name if being updated
        if "name" in data:
            self._validate_field_length(data, "name", 100)
            
            # Check for duplicate name in same category
            category = data.get("category", existing.category)
            duplicate = self.get_repository().get_by_name(data["name"])
            if duplicate and duplicate.id != use_case_id and duplicate.category == category:
                self._raise_business_error(f"Use case '{data['name']}' already exists in category '{category}'")
        
        # Validate category if being updated
        if "category" in data:
            valid_categories = ["fluid_dynamics", "structural", "thermal", "multi_physics", "industrial", "other"]
            if data["category"] not in valid_categories:
                self._raise_business_error(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    def _validate_use_case_deletion(self, use_case_id: str) -> None:
        """Validate use case deletion business rules."""
        # Check if use case exists
        use_case = self.get_by_id(use_case_id)
        if not use_case:
            self._raise_business_error(f"Use case {use_case_id} not found")
        
        # Check if use case has projects
        projects = self.project_repository.get_by_use_case(use_case_id)
        if projects:
            self.logger.warning(f"Deleting use case {use_case_id} with {len(projects)} projects - cascading deletion will occur")
    
    # Override base methods for use case-specific logic
    
    def _validate_create(self, data: Dict[str, Any]) -> None:
        """Validate use case creation."""
        self._validate_use_case_creation(data)
    
    def _validate_update(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Validate use case update."""
        self._validate_use_case_update(entity_id, data)
    
    def _validate_delete(self, entity_id: str) -> None:
        """Validate use case deletion."""
        self._validate_use_case_deletion(entity_id)
    
    def _post_create(self, entity: UseCase) -> None:
        """Post-creation logic for use cases."""
        self.logger.info(f"Use case '{entity.name}' created in category '{entity.category}'")
    
    def _post_update(self, entity: UseCase) -> None:
        """Post-update logic for use cases."""
        self.logger.info(f"Use case '{entity.name}' updated")
    
    def _post_delete(self, entity_id: str) -> None:
        """Post-deletion logic for use cases."""
        self.logger.warning(f"Use case {entity_id} deleted - audit trail required") 