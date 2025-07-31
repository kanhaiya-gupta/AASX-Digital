"""
File Management Service
Handles all file CRUD operations and business logic.
Enforces Use Case → Projects → Files hierarchy.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import UploadFile
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository

class FileService:
    def __init__(self):
        from src.shared.database.connection_manager import DatabaseConnectionManager
        from pathlib import Path
        
        # Create data directory and set database path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        self.file_repo = FileRepository(self.db_manager)
        self.project_repo = ProjectRepository(self.db_manager)
    
    def upload_file(self, project_id: str, file: UploadFile, description: str = None) -> Dict[str, Any]:
        """Upload a file to a project (must be in valid hierarchy)"""
        try:
            # Validate project exists and is in proper hierarchy
            hierarchy_validation = self._validate_project_hierarchy(project_id)
            if not hierarchy_validation["valid"]:
                raise Exception(f"Project hierarchy validation failed: {hierarchy_validation['error']}")
            
            # Validate file type
            if not file.filename.lower().endswith('.aasx'):
                raise Exception("Only AASX files are allowed")
            
            # Check for duplicate file
            if self.check_duplicate_file(project_id, file.filename):
                raise Exception(f"File '{file.filename}' already exists in this project")
            
            # Create proper file storage path
            import os
            from datetime import datetime
            
            # Get use case and project names for directory structure
            use_case_name = hierarchy_validation["use_case"].get("name", "Unknown Use Case")
            project_info = self.project_repo.get_by_id(project_id)
            project_name = project_info.name if hasattr(project_info, 'name') else project_info.get("name", "Unknown Project")
            
            # Clean names for directory structure
            safe_use_case = use_case_name.replace(" ", "_").replace("/", "_").replace("&", "and")
            safe_project = project_name.replace(" ", "_").replace("/", "_").replace("&", "and")
            
            # Create hierarchical directory structure: data/{use_case_name}/{project_name}/
            uploads_dir = Path("data") / safe_use_case / safe_project
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            # Use original filename (hierarchy is in directory structure)
            safe_filename = file.filename.replace(" ", "_").replace("/", "_").replace("&", "and")
            file_path = uploads_dir / safe_filename
            
            # Save the uploaded file
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())
            
            # Create file data for repository
            file_data = {
                "filename": safe_filename,
                "original_filename": file.filename,
                "project_id": project_id,
                "filepath": str(file_path),
                "size": file_path.stat().st_size,
                "description": description or "",
                "status": "not_processed",
                "file_type": "aasx",
                "file_type_description": "AASX Asset Administration Shell file",
                "uploaded_by": "system"  # TODO: Get actual user from context
            }
            
            # Create file using repository
            file_obj = self.file_repo.create(file_data)
            
            if not file_obj:
                # If database creation fails, delete the uploaded file
                if file_path.exists():
                    file_path.unlink()
                raise Exception("Failed to create file record")
            
            # Convert to dictionary for response
            file_info = file_obj.to_dict() if hasattr(file_obj, 'to_dict') else file_data
            
            # Add hierarchy information to response
            file_info["use_case"] = hierarchy_validation["use_case"]
            file_info["project_id"] = project_id
            
            return file_info
                    
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def list_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all files for a project (with hierarchy validation)"""
        try:
            # Validate project hierarchy
            hierarchy_validation = self._validate_project_hierarchy(project_id)
            if not hierarchy_validation["valid"]:
                raise Exception(f"Project hierarchy validation failed: {hierarchy_validation['error']}")
            
            files = self.file_repo.get_by_project_id(project_id)
            
            # Add hierarchy information to each file
            for file_info in files:
                file_info["use_case"] = hierarchy_validation["use_case"]
                file_info["project_id"] = project_id
            
            return files
        except Exception as e:
            raise Exception(f"Failed to list files for project {project_id}: {str(e)}")
    
    def get_file(self, project_id: str, file_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific file (with hierarchy validation)"""
        try:
            # Validate project hierarchy
            hierarchy_validation = self._validate_project_hierarchy(project_id)
            if not hierarchy_validation["valid"]:
                raise Exception(f"Project hierarchy validation failed: {hierarchy_validation['error']}")
            
            file_info = self.file_repo.get_by_id(file_id)
            if file_info:
                file_dict = file_info.to_dict() if hasattr(file_info, 'to_dict') else file_info
                file_dict["use_case"] = hierarchy_validation["use_case"]
                file_dict["project_id"] = project_id
                return file_dict
            
            return None
        except Exception as e:
            raise Exception(f"Failed to get file {file_id}: {str(e)}")
    
    def delete_file(self, project_id: str, file_id: str) -> bool:
        """Delete a file from a project (with hierarchy validation)"""
        try:
            # Validate project hierarchy
            hierarchy_validation = self._validate_project_hierarchy(project_id)
            if not hierarchy_validation["valid"]:
                raise Exception(f"Project hierarchy validation failed: {hierarchy_validation['error']}")
            
            file_info = self.file_repo.get_by_id(file_id)
            if not file_info:
                raise Exception("File not found")
            
            return self.file_repo.delete(file_id)
        except Exception as e:
            raise Exception(f"Failed to delete file {file_id}: {str(e)}")
    
    def update_file(self, project_id: str, file_id: str, updates: Dict[str, Any]) -> bool:
        """Update file metadata (with hierarchy validation)"""
        try:
            # Validate project hierarchy
            hierarchy_validation = self._validate_project_hierarchy(project_id)
            if not hierarchy_validation["valid"]:
                raise Exception(f"Project hierarchy validation failed: {hierarchy_validation['error']}")
            
            file_info = self.file_repo.get_by_id(file_id)
            if not file_info:
                raise Exception("File not found")
            
            # Update file status if provided
            if 'status' in updates:
                self.file_repo.update_status(file_id, updates['status'])
            
            return True
        except Exception as e:
            raise Exception(f"Failed to update file {file_id}: {str(e)}")
    
    def move_file(self, file_id: str, from_project_id: str, to_project_id: str) -> bool:
        """Move a file from one project to another (with hierarchy validation)"""
        try:
            # Validate both project hierarchies
            from_hierarchy = self._validate_project_hierarchy(from_project_id)
            to_hierarchy = self._validate_project_hierarchy(to_project_id)
            
            if not from_hierarchy["valid"]:
                raise Exception(f"Source project hierarchy validation failed: {from_hierarchy['error']}")
            
            if not to_hierarchy["valid"]:
                raise Exception(f"Target project hierarchy validation failed: {to_hierarchy['error']}")
            
            # Get file info
            file_info = self.file_repo.get_by_id(file_id)
            if not file_info:
                raise Exception("File not found")
            
            # Check for duplicate in target project
            if self.check_duplicate_file(to_project_id, file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename')):
                raise Exception(f"File '{file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename')}' already exists in target project")
            
            # TODO: Implement file movement logic
            # This would involve updating the database record and moving the physical file
            
            raise Exception("File movement not yet implemented")
            
        except Exception as e:
            raise Exception(f"Failed to move file {file_id}: {str(e)}")
    
    def list_all_files(self) -> List[Dict[str, Any]]:
        """Get all files across all projects (with hierarchy information)"""
        try:
            all_files = []
            projects = self.project_repo.get_all()
            
            for project in projects:
                project_id = project.get('project_id') if isinstance(project, dict) else project.project_id if hasattr(project, 'project_id') else project.id
                if project_id:
                    # Validate project hierarchy
                    hierarchy_validation = self._validate_project_hierarchy(project_id)
                    if hierarchy_validation["valid"]:
                        files = self.file_repo.get_by_project_id(project_id)
                        for file_info in files:
                            file_info['project_name'] = project.get('name', 'Unknown') if isinstance(project, dict) else project.name if hasattr(project, 'name') else 'Unknown'
                            file_info['project_id'] = project_id
                            file_info['use_case'] = hierarchy_validation['use_case']
                            all_files.append(file_info)
                    else:
                        # Log orphaned projects
                        print(f"Warning: Project {project_id} is not in valid hierarchy: {hierarchy_validation['error']}")
            
            return all_files
        except Exception as e:
            raise Exception(f"Failed to list all files: {str(e)}")
    
    def reset_file_statuses(self) -> Dict[str, Any]:
        """Reset file statuses when outputs are missing"""
        try:
            # TODO: Implement reset functionality when FileRepository is updated
            return {"status": "reset_not_implemented", "message": "Reset functionality to be implemented"}
        except Exception as e:
            raise Exception(f"Failed to reset file statuses: {str(e)}")
    
    def check_duplicate_file(self, project_id: str, filename: str) -> bool:
        """Check if a file with the same name exists in the project"""
        try:
            file_info = self.file_repo.find_by_name_and_project(filename, project_id)
            return file_info is not None
        except Exception as e:
            raise Exception(f"Failed to check duplicate file: {str(e)}")
    
    def find_file_by_name(self, project_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """Find a file by name in a project"""
        try:
            return self.file_repo.find_by_name_and_project(filename, project_id)
        except Exception as e:
            raise Exception(f"Failed to find file by name: {str(e)}")
    
    def _validate_project_hierarchy(self, project_id: str) -> Dict[str, Any]:
        """Internal method to validate project hierarchy"""
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

# Global instance
file_service = FileService() 