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
        """Upload a file to a project (must be in valid hierarchy) with comprehensive error handling."""
        try:
            # Validate project exists and is in proper hierarchy
            hierarchy_validation = self._validate_project_hierarchy(project_id)
            if not hierarchy_validation["valid"]:
                raise ValueError(f"Project hierarchy validation failed: {hierarchy_validation['error']}")
            
            # Validate file type
            if not file.filename.lower().endswith('.aasx'):
                raise ValueError("Only AASX files are allowed")
            
            # Check for duplicate file
            if self.check_duplicate_file(project_id, file.filename):
                raise ValueError(f"File '{file.filename}' already exists in this project")
            
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
            try:
                uploads_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise PermissionError(f"Cannot create upload directory: {str(e)}")
            except OSError as e:
                raise OSError(f"Failed to create upload directory: {str(e)}")
            
            # Use original filename (hierarchy is in directory structure)
            safe_filename = file.filename.replace(" ", "_").replace("/", "_").replace("&", "and")
            file_path = uploads_dir / safe_filename
            
            # Save the uploaded file with error handling
            try:
                with open(file_path, "wb") as buffer:
                    buffer.write(file.file.read())
            except PermissionError as e:
                raise PermissionError(f"Cannot write file to disk: {str(e)}")
            except OSError as e:
                raise OSError(f"Failed to save file to disk: {str(e)}")
            except Exception as e:
                raise Exception(f"Failed to save uploaded file: {str(e)}")
            
            # Create file data for repository
            from src.shared.models.file import File
            from datetime import datetime
            
            # Generate deterministic file ID following init script pattern
            def generate_file_id(filename: str, project_name: str, use_case_name: str) -> str:
                import uuid
                combined_name = f"{use_case_name}_{project_name}_{filename}"
                namespace_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, 'www.aasx-digital.de')
                file_uuid = uuid.uuid5(namespace_uuid, combined_name.lower().replace(' ', '-'))
                return str(file_uuid)
            
            # Generate file ID
            file_id = generate_file_id(safe_filename, project_name, use_case_name)
            
            file_data = {
                "file_id": file_id,  # Add the generated deterministic file ID
                "filename": safe_filename,
                "original_filename": file.filename,
                "project_id": project_id,
                "filepath": str(file_path),
                "size": file_path.stat().st_size,
                "description": description or "",
                "status": "not_processed",
                "file_type": "aasx",
                "file_type_description": "AASX Asset Administration Shell file",
                "user_id": None,  # No user authentication required for now
                "upload_date": datetime.now().isoformat(),  # Add upload_date
                "federated_learning": "not_allowed"  # Default: not allowed for privacy
            }
            
            # Create File model object
            file_obj = File(**file_data)
            
            print(f"🔧 File Service: Created File model object:")
            print(f"   📁 File ID: {getattr(file_obj, 'file_id', 'N/A')}")
            print(f"   📂 Filename: {file_obj.filename}")
            print(f"   📋 Original Filename: {file_obj.original_filename}")
            print(f"   📁 Project ID: {file_obj.project_id}")
            print(f"   📂 Filepath: {file_obj.filepath}")
            print(f"   📊 Size: {file_obj.size}")
            print(f"   🏷️  Status: {file_obj.status}")
            print(f"   📅 Upload Date: {file_obj.upload_date}")
            
            # Create file using repository with error handling
            print(f"🔧 File Service: About to create file in database...")
            try:
                created_file = self.file_repo.create(file_obj)
                print(f"🔧 File Service: Database creation result: {created_file is not None}")
            except Exception as db_error:
                # If database creation fails, clean up the uploaded file
                if file_path.exists():
                    try:
                        file_path.unlink()
                        print(f"🧹 Cleaned up uploaded file after database error: {file_path}")
                    except Exception as cleanup_error:
                        print(f"⚠️ Failed to clean up uploaded file: {cleanup_error}")
                raise Exception(f"Database error: Failed to create file record - {str(db_error)}")
            
            if not created_file:
                # If database creation fails, delete the uploaded file
                if file_path.exists():
                    try:
                        file_path.unlink()
                        print(f"🧹 Cleaned up uploaded file after failed creation: {file_path}")
                    except Exception as cleanup_error:
                        print(f"⚠️ Failed to clean up uploaded file: {cleanup_error}")
                raise Exception("Failed to create file record in database")
            
            # Update project's updated_at timestamp to reflect the file upload
            try:
                from datetime import datetime
                self.project_repo.update(project_id, {"updated_at": datetime.now().isoformat()})
                print(f"🔧 File Service: Updated project {project_id} timestamp")
            except Exception as update_error:
                print(f"⚠️ File Service: Failed to update project timestamp: {update_error}")
            
            # Convert to dictionary for response
            file_info = created_file.to_dict() if hasattr(created_file, 'to_dict') else created_file.__dict__
            
            # Add hierarchy information to response
            file_info["use_case"] = hierarchy_validation["use_case"]
            file_info["project_id"] = project_id
            
            print(f"✅ File uploaded successfully:")
            print(f"   📁 File ID: {file_info.get('file_id', 'N/A')}")
            print(f"   📂 Physical Path: {file_info.get('filepath', 'N/A')}")
            print(f"   📊 Size: {file_info.get('size', 'N/A')} bytes")
            print(f"   🏷️  Status: {file_info.get('status', 'N/A')}")
            print(f"   📋 Use Case: {hierarchy_validation['use_case'].get('name', 'N/A')}")
            print(f"   📁 Project: {project_name}")
            
            return file_info
                    
        except ValueError as e:
            # Handle validation errors
            raise ValueError(f"Validation error: {str(e)}")
        except PermissionError as e:
            # Handle permission errors
            raise PermissionError(f"Permission error: {str(e)}")
        except OSError as e:
            # Handle file system errors
            raise OSError(f"File system error: {str(e)}")
        except Exception as e:
            # Handle all other errors
            import logging
            logging.error(f"File upload failed for project {project_id}: {str(e)}")
            raise Exception(f"Upload failed: {str(e)}")
    
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
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific file by ID without project validation"""
        try:
            file_info = self.file_repo.get_by_id(file_id)
            if file_info:
                return file_info.to_dict() if hasattr(file_info, 'to_dict') else file_info
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
            
            # Delete the file
            delete_result = self.file_repo.delete(file_id)
            
            # Update project's updated_at timestamp to reflect the file deletion
            if delete_result:
                try:
                    from datetime import datetime
                    self.project_repo.update(project_id, {"updated_at": datetime.now().isoformat()})
                    print(f"🔧 File Service: Updated project {project_id} timestamp after file deletion")
                except Exception as update_error:
                    print(f"⚠️ File Service: Failed to update project timestamp after deletion: {update_error}")
            
            return delete_result
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
            
            # Update federated learning setting if provided
            if 'federated_learning' in updates:
                federated_setting = updates['federated_learning']
                if federated_setting not in ['allowed', 'not_allowed', 'conditional']:
                    raise Exception("Invalid federated_learning value. Must be 'allowed', 'not_allowed', or 'conditional'")
                self.file_repo.update_federated_learning(file_id, federated_setting)
            
            # Update project's updated_at timestamp to reflect the file update
            try:
                from datetime import datetime
                self.project_repo.update(project_id, {"updated_at": datetime.now().isoformat()})
                print(f"🔧 File Service: Updated project {project_id} timestamp after file update")
            except Exception as update_error:
                print(f"⚠️ File Service: Failed to update project timestamp after file update: {update_error}")
            
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
    
    def list_files_by_federated_status(self, federated_status: str = None) -> List[Dict[str, Any]]:
        """Get files filtered by federated learning status"""
        try:
            if federated_status and federated_status not in ['allowed', 'not_allowed', 'conditional']:
                raise Exception("Invalid federated_status. Must be 'allowed', 'not_allowed', 'conditional', or None for all")
            
            all_files = self.list_all_files()
            
            if federated_status:
                filtered_files = []
                for file_info in all_files:
                    if file_info.get('federated_learning') == federated_status:
                        filtered_files.append(file_info)
                return filtered_files
            
            return all_files
        except Exception as e:
            raise Exception(f"Failed to list files by federated status: {str(e)}")
    
    def get_federated_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about federated learning file distribution"""
        try:
            all_files = self.list_all_files()
            
            stats = {
                'total_files': len(all_files),
                'federated_allowed': 0,
                'federated_not_allowed': 0,
                'federated_conditional': 0,
                'percentage_allowed': 0.0,
                'percentage_not_allowed': 0.0,
                'percentage_conditional': 0.0
            }
            
            for file_info in all_files:
                status = file_info.get('federated_learning', 'not_allowed')
                if status == 'allowed':
                    stats['federated_allowed'] += 1
                elif status == 'not_allowed':
                    stats['federated_not_allowed'] += 1
                elif status == 'conditional':
                    stats['federated_conditional'] += 1
            
            # Calculate percentages
            if stats['total_files'] > 0:
                stats['percentage_allowed'] = (stats['federated_allowed'] / stats['total_files']) * 100
                stats['percentage_not_allowed'] = (stats['federated_not_allowed'] / stats['total_files']) * 100
                stats['percentage_conditional'] = (stats['federated_conditional'] / stats['total_files']) * 100
            
            return stats
        except Exception as e:
            raise Exception(f"Failed to get federated learning stats: {str(e)}")
    
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
    
    def get_file_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get file information by filename across all projects."""
        try:
            print(f"🔍 FileService: Looking for filename: {filename}")
            all_files = self.file_repo.get_all()
            for file in all_files:
                if file.filename == filename:
                    file_dict = file.__dict__
                    print(f"✅ FileService: Found file: {file_dict}")
                    return file_dict
            print(f"❌ FileService: File not found: {filename}")
            return None
        except Exception as e:
            print(f"💥 FileService: Error finding file by filename: {e}")
            return None
    
    def find_file_by_hierarchy(self, use_case_name: str, project_name: str, filename: str) -> Optional[Dict[str, Any]]:
        """Find file ID by use case name, project name, and filename"""
        try:
            print(f"🔍 File Service: Searching for file in hierarchy: {use_case_name}/{project_name}/{filename}")
            
            # First, find the use case by name
            use_case = self.file_repo.get_use_case_by_name(use_case_name)
            if not use_case:
                print(f"❌ File Service: Use case '{use_case_name}' not found")
                return None
            
            use_case_id = use_case.get('use_case_id') or use_case.get('id')
            print(f"✅ File Service: Found use case '{use_case_name}' with ID: {use_case_id}")
            
            # Find the project by name within the use case
            projects = self.project_repo.get_by_use_case(use_case_id)
            target_project = None
            
            for project in projects:
                project_dict = project.to_dict() if hasattr(project, 'to_dict') else project
                if project_dict.get('name') == project_name:
                    target_project = project_dict
                    break
            
            if not target_project:
                print(f"❌ File Service: Project '{project_name}' not found in use case '{use_case_name}'")
                return None
            
            project_id = target_project.get('project_id') or target_project.get('id')
            print(f"✅ File Service: Found project '{project_name}' with ID: {project_id}")
            
            # Find the file by original filename in the project
            file_info = self.file_repo.find_by_original_filename(filename, project_id)
            if not file_info:
                print(f"❌ File Service: File '{filename}' not found in project '{project_name}'")
                return None
            
            print(f"✅ File Service: Found file '{filename}' with ID: {file_info.get('file_id') or file_info.get('id')}")
            
            # Return complete file information with hierarchy
            result = {
                "file_id": file_info.get('file_id') or file_info.get('id'),
                "filename": file_info.get('filename'),
                "original_filename": file_info.get('original_filename'),
                "project_id": project_id,
                "project_name": project_name,
                "use_case_id": use_case_id,
                "use_case_name": use_case_name,
                "filepath": file_info.get('filepath'),
                "size": file_info.get('size'),
                "status": file_info.get('status'),
                "description": file_info.get('description'),
                "upload_date": file_info.get('upload_date'),
                "hierarchy_path": f"{use_case_name}/{project_name}/{filename}"
            }
            
            return result
            
        except Exception as e:
            print(f"❌ File Service: Error finding file by hierarchy: {str(e)}")
            raise Exception(f"Failed to find file by hierarchy: {str(e)}")
    
    def get_file_by_hierarchy_path(self, hierarchy_path: str) -> Optional[Dict[str, Any]]:
        """Get file by hierarchy path (e.g., 'Thermal Analysis and Heat Management/CPU Cooling System Analysis/test.aasx')"""
        try:
            # Parse hierarchy path
            path_parts = hierarchy_path.split('/')
            if len(path_parts) != 3:
                raise Exception("Hierarchy path must be in format: use_case/project/filename")
            
            use_case_name = path_parts[0]
            project_name = path_parts[1]
            filename = path_parts[2]
            
            return self.find_file_by_hierarchy(use_case_name, project_name, filename)
            
        except Exception as e:
            raise Exception(f"Failed to get file by hierarchy path: {str(e)}")
    
    def list_files_by_use_case(self, use_case_name: str) -> List[Dict[str, Any]]:
        """List all files in a use case across all projects"""
        try:
            # Find the use case by name
            use_case = self.file_repo.get_use_case_by_name(use_case_name)
            if not use_case:
                raise Exception(f"Use case '{use_case_name}' not found")
            
            use_case_id = use_case.get('use_case_id') or use_case.get('id')
            
            # Get all projects in this use case
            projects = self.project_repo.get_by_use_case(use_case_id)
            
            all_files = []
            for project in projects:
                project_dict = project.to_dict() if hasattr(project, 'to_dict') else project
                project_id = project_dict.get('project_id') or project_dict.get('id')
                project_name = project_dict.get('name')
                
                # Get files for this project
                files = self.file_repo.get_by_project_id(project_id)
                for file_info in files:
                    file_dict = file_info.to_dict() if hasattr(file_info, 'to_dict') else file_info
                    file_dict.update({
                        "project_name": project_name,
                        "use_case_name": use_case_name,
                        "hierarchy_path": f"{use_case_name}/{project_name}/{file_dict.get('original_filename')}"
                    })
                    all_files.append(file_dict)
            
            return all_files
            
        except Exception as e:
            raise Exception(f"Failed to list files by use case: {str(e)}")
    
    def get_file_id_by_path(self, use_case_name: str, project_name: str, filename: str) -> Optional[str]:
        """Get file_id from use case, project, and filename.
        
        This is essential for file retrieval when using the hierarchy-based path structure.
        """
        try:
            # First, find the use case by name
            use_case = self.file_repo.get_use_case_by_name(use_case_name)
            if not use_case:
                print(f"Use case not found: {use_case_name}")
                return None
            
            # Find the project by name within the use case
            project = self.project_repo.get_project_by_name_and_use_case(project_name, use_case['use_case_id'])
            if not project:
                print(f"Project '{project_name}' not found in use case '{use_case_name}'")
                return None
            
            # Find the file by original filename in the project
            file = self.file_repo.find_by_original_filename(filename, project.project_id)
            if not file:
                print(f"File '{filename}' not found in project '{project_name}'")
                return None
            
            print(f"Found file_id: {file.file_id} for path: {use_case_name}/{project_name}/{filename}")
            return file.file_id
            
        except Exception as e:
            print(f"Error getting file_id by path {use_case_name}/{project_name}/{filename}: {e}")
            return None
    
    def get_file_by_path(self, use_case_name: str, project_name: str, filename: str) -> Optional[Dict[str, Any]]:
        """Get file object from use case, project, and filename."""
        file_id = self.get_file_id_by_path(use_case_name, project_name, filename)
        if file_id:
            file_info = self.file_repo.get_by_id(file_id)
            if file_info:
                return file_info.to_dict() if hasattr(file_info, 'to_dict') else file_info
        return None
    
    def get_file_path_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get the logical path information for a file (usecase/project/filename)."""
        try:
            file_info = self.file_repo.get_by_id(file_id)
            if not file_info:
                return None
            
            # Get project information
            project_use_cases = self.project_repo.get_project_use_cases(file_info.project_id)
            if not project_use_cases:
                return None
            
            primary_use_case = project_use_cases[0]
            
            # Get actual project name
            project = self.project_repo.get_by_id(file_info.project_id)
            project_name = project.name if hasattr(project, 'name') else project.get("name", "Unknown Project")
            
            return {
                "file_id": file_id,
                "use_case_name": primary_use_case['name'],
                "project_name": project_name,
                "filename": file_info.original_filename,
                "logical_path": f"{primary_use_case['name']}/{project_name}/{file_info.original_filename}",
                "physical_path": file_info.filepath
            }
        except Exception as e:
            print(f"Error getting file path info for {file_id}: {e}")
            return None

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