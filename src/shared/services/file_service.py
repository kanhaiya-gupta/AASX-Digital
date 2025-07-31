"""
File Service
===========

Business logic for file management in the AAS Data Modeling framework.
Handles file uploads, duplication prevention, and hierarchy validation.
"""

from typing import List, Optional, Dict, Any
import os
import uuid
from .base_service import BaseService
from ..models.file import File
from ..repositories.file_repository import FileRepository
from ..repositories.project_repository import ProjectRepository
from ..repositories.digital_twin_repository import DigitalTwinRepository

class FileService(BaseService[File]):
    """Service for file business logic."""
    
    def __init__(self, db_manager, project_repository: ProjectRepository, digital_twin_repository: DigitalTwinRepository):
        super().__init__(db_manager)
        self.project_repository = project_repository
        self.digital_twin_repository = digital_twin_repository
    
    def get_repository(self) -> FileRepository:
        """Get the file repository."""
        return FileRepository(self.db_manager)
    
    def upload_file(self, file_data: Dict[str, Any], project_id: str, file_content: bytes) -> File:
        """Upload a file with business validation and duplication prevention."""
        # Validate business rules
        self._validate_file_upload(file_data, project_id)
        
        # Check for existing file with same name in project
        existing_file = self.get_repository().find_by_original_filename(
            file_data["original_filename"], project_id
        )
        
        if existing_file:
            # Update existing file instead of creating duplicate
            return self._update_existing_file(existing_file.file_id, file_data, file_content)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_data["file_id"] = file_id
        
        # Get use case information for better file organization
        project_use_cases = self.project_repository.get_project_use_cases(project_id)
        if not project_use_cases:
            self._raise_business_error(f"Project {project_id} is not linked to any use case")
        
        # Use the first (primary) use case for file organization
        primary_use_case = project_use_cases[0]
        use_case_name = primary_use_case['name'].replace(' ', '_').lower()
        project_name = file_data.get('project_name', 'unknown_project').replace(' ', '_').lower()
        
        # Generate required fields with hierarchy-based path
        file_data["filename"] = f"{file_id}_{file_data['original_filename']}"
        file_data["filepath"] = f"uploads/{use_case_name}/{project_name}/{file_data['filename']}"
        
        # Remove project_name from file_data as it's not a field in the File model
        file_data.pop("project_name", None)
        
        # Create file
        file = self.create(file_data)
        
        # Update project statistics
        files_in_project = self.get_repository().get_by_project(project_id)
        file_count = len(files_in_project)
        total_size = sum(f.size for f in files_in_project)
        
        self.project_repository.update_file_count(project_id, file_count)
        self.project_repository.update_total_size(project_id, total_size)
        
        self.logger.info(f"Uploaded file: {file.original_filename} to project: {project_name}")
        return file
    
    def get_file_with_trace(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file with complete trace information."""
        file = self.get_by_id(file_id)
        if not file:
            return None
        
        # Get trace information
        trace_info = self.get_repository().get_file_trace_info(file_id)
        
        return {
            "file": file,
            "trace_info": trace_info
        }
    
    def get_file_id_by_path(self, use_case_name: str, project_name: str, filename: str) -> Optional[str]:
        """Get file_id from use case, project, and filename.
        
        This is essential for file retrieval when using the hierarchy-based path structure.
        """
        try:
            # First, find the use case by name
            use_case = self.get_repository().get_use_case_by_name(use_case_name)
            if not use_case:
                self.logger.warning(f"Use case not found: {use_case_name}")
                return None
            
            # Find the project by name within the use case
            project = self.project_repository.get_project_by_name_and_use_case(project_name, use_case['id'])
            if not project:
                self.logger.warning(f"Project '{project_name}' not found in use case '{use_case_name}'")
                return None
            
            # Find the file by original filename in the project
            file = self.get_repository().find_by_original_filename(filename, project.id)
            if not file:
                self.logger.warning(f"File '{filename}' not found in project '{project_name}'")
                return None
            
            self.logger.info(f"Found file_id: {file.file_id} for path: {use_case_name}/{project_name}/{filename}")
            return file.file_id
            
        except Exception as e:
            self.logger.error(f"Error getting file_id by path {use_case_name}/{project_name}/{filename}: {e}")
            return None
    
    def get_file_by_path(self, use_case_name: str, project_name: str, filename: str) -> Optional[File]:
        """Get file object from use case, project, and filename."""
        file_id = self.get_file_id_by_path(use_case_name, project_name, filename)
        if file_id:
            return self.get_by_id(file_id)
        return None
    
    def get_file_path_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get the logical path information for a file (usecase/project/filename)."""
        file = self.get_by_id(file_id)
        if not file:
            return None
        
        # Get project information
        project_use_cases = self.project_repository.get_project_use_cases(file.project_id)
        if not project_use_cases:
            return None
        
        primary_use_case = project_use_cases[0]
        
        # Get actual project name
        project = self.project_repository.get_by_id(file.project_id)
        project_name = project.name if project else file.project_id
        
        return {
            "file_id": file_id,
            "use_case_name": primary_use_case['name'],
            "project_name": project_name,
            "filename": file.original_filename,
            "logical_path": f"{primary_use_case['name']}/{project_name}/{file.original_filename}",
            "physical_path": file.filepath
        }
    
    def get_files_by_project(self, project_id: str) -> List[File]:
        """Get all files in a project with hierarchy validation."""
        # Validate project hierarchy
        if not self.project_repository.validate_project_hierarchy(project_id):
            self._raise_business_error(f"Project {project_id} is not properly linked to a use case")
        
        return self.get_repository().get_by_project(project_id)
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file with cascading digital twin deletion."""
        # Validate file exists
        file = self.get_by_id(file_id)
        if not file:
            self._raise_business_error(f"File {file_id} not found")
        
        # Delete associated digital twin
        twin = self.digital_twin_repository.get_by_file_id(file_id)
        if twin:
            self.digital_twin_repository.delete(twin.id)
        
        # Delete the file
        success = self.delete(file_id)
        
        if success:
            # Update project statistics
            self.project_repository.update_file_count(file.project_id)
            self.project_repository.update_total_size(file.project_id)
            
            self.logger.warning(f"Deleted file: {file.original_filename}")
        
        return success
    
    def move_file(self, file_id: str, new_project_id: str) -> bool:
        """Move file to a different project."""
        # Validate file exists
        file = self.get_by_id(file_id)
        if not file:
            self._raise_business_error(f"File {file_id} not found")
        
        # Validate new project exists and has proper hierarchy
        if not self.project_repository.validate_project_hierarchy(new_project_id):
            self._raise_business_error(f"Target project {new_project_id} is not properly linked to a use case")
        
        # Check for duplicate filename in target project
        existing_file = self.get_repository().find_by_original_filename(
            file.original_filename, new_project_id
        )
        if existing_file:
            self._raise_business_error(f"File '{file.original_filename}' already exists in target project")
        
        # Update file project
        update_data = {"project_id": new_project_id}
        success = self.update(file_id, update_data)
        
        if success:
            # Update statistics for both projects
            self.project_repository.update_file_count(file.project_id)
            self.project_repository.update_total_size(file.project_id)
            self.project_repository.update_file_count(new_project_id)
            self.project_repository.update_total_size(new_project_id)
            
            self.logger.info(f"Moved file {file.original_filename} from project {file.project_id} to {new_project_id}")
        
        return success
    
    def get_file_statistics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get file statistics with optional project filtering."""
        if project_id:
            # Validate project hierarchy
            if not self.project_repository.validate_project_hierarchy(project_id):
                self._raise_business_error(f"Project {project_id} is not properly linked to a use case")
        
        stats = self.get_repository().get_file_statistics()
        
        if project_id:
            # Filter for specific project
            files = self.get_repository().get_by_project(project_id)
            stats["project_files"] = len(files)
            stats["project_total_size"] = sum(file.size for file in files)
        
        return stats
    
    def search_files(self, search_term: str, project_id: Optional[str] = None) -> List[File]:
        """Search files with optional project filtering."""
        if not search_term or len(search_term.strip()) < 2:
            self._raise_business_error("Search term must be at least 2 characters")
        
        files = self.get_repository().search_files(search_term.strip())
        
        # Filter by project if specified
        if project_id:
            if not self.project_repository.validate_project_hierarchy(project_id):
                self._raise_business_error(f"Project {project_id} is not properly linked to a use case")
            files = [f for f in files if f.project_id == project_id]
        
        return files
    
    def get_files_by_status(self, status: str) -> List[File]:
        """Get files by processing status."""
        return self.get_repository().get_by_status(status)
    
    def update_file_status(self, file_id: str, status: str) -> bool:
        """Update file processing status."""
        # Validate file exists
        file = self.get_by_id(file_id)
        if not file:
            self._raise_business_error(f"File {file_id} not found")
        
        # Validate status
        valid_statuses = ["uploaded", "processing", "processed", "error", "archived"]
        if status not in valid_statuses:
            self._raise_business_error(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        success = self.get_repository().update_status(file_id, status)
        
        if success:
            self.logger.info(f"Updated file {file_id} status to: {status}")
        
        return success
    
    # Business Logic Validation Methods
    
    def _validate_file_upload(self, file_data: Dict[str, Any], project_id: str) -> None:
        """Validate file upload business rules."""
        required_fields = ["original_filename", "size"]
        self._validate_required_fields(file_data, required_fields)
        
        # Validate filename length
        self._validate_field_length(file_data, "original_filename", 255)
        
        # Validate file size
        size = file_data.get("size", 0)
        if size <= 0:
            self._raise_business_error("File size must be greater than 0")
        
        # Validate project exists and has proper hierarchy
        if not self.project_repository.validate_project_hierarchy(project_id):
            self._raise_business_error(f"Project {project_id} is not properly linked to a use case")
        
        # Validate file extension
        filename = file_data.get("original_filename", "")
        if not self._is_valid_file_extension(filename):
            self._raise_business_error("Invalid file extension. Only .aasx files are allowed")
    
    def _update_existing_file(self, file_id: str, file_data: Dict[str, Any], file_content: bytes) -> File:
        """Update existing file instead of creating duplicate."""
        # Update file metadata
        update_data = {
            "size": file_data.get("size"),
            "description": file_data.get("description"),
            "upload_date": file_data.get("upload_date")
        }
        
        file = self.update(file_id, update_data)
        
        if file:
            self.logger.info(f"Updated existing file: {file.original_filename}")
        
        return file
    
    def _is_valid_file_extension(self, filename: str) -> bool:
        """Validate file extension."""
        if not filename:
            return False
        
        # Check for .aasx extension
        return filename.lower().endswith('.aasx')
    
    def _validate_file_size_limits(self, size: int, project_id: str) -> None:
        """Validate file size against project/organization limits."""
        # This would check against organization storage limits
        # For now, we'll implement a basic size check
        max_file_size = 100 * 1024 * 1024  # 100MB
        if size > max_file_size:
            self._raise_business_error(f"File size ({size} bytes) exceeds maximum allowed size ({max_file_size} bytes)")
    
    # Override base methods for file-specific logic
    
    def _validate_create(self, data: Dict[str, Any]) -> None:
        """Validate file creation."""
        # Note: This is called after _validate_file_upload, so we don't need to duplicate validation
        pass
    
    def _validate_update(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Validate file update."""
        # Check if file exists
        file = self.get_by_id(entity_id)
        if not file:
            self._raise_business_error(f"File {entity_id} not found")
        
        # Validate filename if being updated
        if "original_filename" in data:
            self._validate_field_length(data, "original_filename", 255)
            if not self._is_valid_file_extension(data["original_filename"]):
                self._raise_business_error("Invalid file extension. Only .aasx files are allowed")
    
    def _validate_delete(self, entity_id: str) -> None:
        """Validate file deletion."""
        # Check if file exists
        file = self.get_by_id(entity_id)
        if not file:
            self._raise_business_error(f"File {entity_id} not found")
    
    def _post_create(self, entity: File) -> None:
        """Post-creation logic for files."""
        self.logger.info(f"File '{entity.original_filename}' created in project {entity.project_id}")
    
    def _post_update(self, entity: File) -> None:
        """Post-update logic for files."""
        self.logger.info(f"File '{entity.original_filename}' updated")
    
    def _post_delete(self, entity_id: str) -> None:
        """Post-deletion logic for files."""
        self.logger.warning(f"File {entity_id} deleted - audit trail required") 