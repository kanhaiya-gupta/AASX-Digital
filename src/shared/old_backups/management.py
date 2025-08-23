import os
import json
import shutil
import uuid
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from urllib.parse import urlparse
import requests

# Import the new database manager
try:
    from .database_manager import DatabaseProjectManager, DatabaseManagerError
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Warning: Database manager not available, using JSON-based system")

# Global configuration
DEFAULT_PROJECTS_DIR = Path("data/projects")
DEFAULT_OUTPUT_DIR = Path("output")
SUPPORTED_FILE_TYPES = {
    '.aasx': 'AASX Package',
    '.json': 'JSON Data',
    '.yaml': 'YAML Configuration',
    '.yml': 'YAML Configuration',
    '.xml': 'XML Data',
    '.csv': 'CSV Data',
    '.ttl': 'Turtle RDF',
    '.rdf': 'RDF Data',
    '.zip': 'Archive',
    '.tar.gz': 'Archive',
    '.pdf': 'Document',
    '.txt': 'Text Document'
}

class FileManagementError(Exception):
    """Custom exception for file management operations"""
    pass

class ProjectManager:
    """Centralized project and file management system with database integration"""
    
    def __init__(self, projects_dir: Path = None, output_dir: Path = None, use_database: bool = True):
        self.projects_dir = projects_dir or DEFAULT_PROJECTS_DIR
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database manager if available and requested
        self.use_database = use_database and DATABASE_AVAILABLE
        if self.use_database:
            try:
                self.db_manager = DatabaseProjectManager(projects_dir, output_dir)
                print("✅ Using database-driven project management")
            except Exception as e:
                print(f"⚠️ Database manager initialization failed: {e}")
                print("🔄 Falling back to JSON-based system")
                self.use_database = False
        
        if not self.use_database:
            print("📁 Using JSON-based project management")
    
    # ==================== PROJECT MANAGEMENT ====================
    
    def create_project(self, project_id: str, metadata: Dict[str, Any]) -> Path:
        """
        Create a project directory and project.json if not exists.
        Returns the project directory path.
        """
        if self.use_database:
            return self.db_manager.create_project(project_id, metadata)
        
        # Fallback to JSON-based approach
        project_dir = self.get_project_dir(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Set default metadata if not provided
        if 'created_at' not in metadata:
            metadata['created_at'] = datetime.now().isoformat()
        if 'updated_at' not in metadata:
            metadata['updated_at'] = datetime.now().isoformat()
        if 'file_count' not in metadata:
            metadata['file_count'] = 0
        if 'total_size' not in metadata:
            metadata['total_size'] = 0
        
        project_json = project_dir / "project.json"
        if not project_json.exists():
            with open(project_json, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        
        return project_dir
    
    def get_project_dir(self, project_id: str) -> Path:
        """Get the path to a project directory."""
        return self.projects_dir / project_id
    
    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists."""
        return self.db_manager.project_exists(project_id)

    def list_projects(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List all projects with their metadata."""
        return self.db_manager.list_projects(user_id)
    
    def get_project_metadata(self, project_id: str) -> Dict[str, Any]:
        """Get project metadata."""
        return self.db_manager.get_project_metadata(project_id)
    
    def update_project_metadata(self, project_id: str, updates: Dict[str, Any]):
        """Update project metadata."""
        self.db_manager.update_project_metadata(project_id, updates)
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its files."""
        try:
            # Use the database manager to delete the project (this handles both DB and filesystem)
            return self.db_manager.delete_project(project_id)
        except Exception as e:
            raise FileManagementError(f"Failed to delete project {project_id}: {e}")
    
    # ==================== FILE MANAGEMENT ====================
    # Remove load_files_manifest and save_files_manifest

    def register_file(self, project_id: str, file_info: Dict[str, Any]):
        """Register a file in the database."""
        self.db_manager.register_file(project_id, file_info)

    def unregister_file(self, project_id: str, file_id: str):
        """Remove a file entry from the database."""
        self.db_manager.unregister_file(project_id, file_id)

    def get_file_info(self, project_id: str, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information by ID from the database."""
        return self.db_manager.get_file_info(project_id, file_id)

    def list_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """List all files in a project from the database."""
        return self.db_manager.list_project_files(project_id)

    def check_duplicate_file(self, project_id: str, filename: str) -> bool:
        """Check if a file already exists in the project (database only)."""
        return self.db_manager.check_duplicate_file(project_id, filename)

    def update_file_status(self, project_id: str, file_id: str, status: str, result: Optional[Any] = None):
        """Update the status and processing result for a file in the database."""
        self.db_manager.update_file_status(project_id, file_id, status, result)

    def _update_project_stats(self, project_id: str):
        """Update project file count and total size in the database."""
        # This is now handled by the database manager
        pass

    # ==================== FILE UPLOAD OPERATIONS ====================
    
    def upload_file(self, project_id: str, file_path: Path, original_filename: str, 
                   description: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to a project."""
        if not self.project_exists(project_id):
            raise FileManagementError(f"Project {project_id} does not exist")
        
        # Validate file type
        file_ext = file_path.suffix.lower()
        if file_ext not in SUPPORTED_FILE_TYPES:
            raise FileManagementError(f"Unsupported file type: {file_ext}")
        
        # Generate unique filename
        final_filename = self._generate_unique_filename(project_id, original_filename)
        
        # Copy file to project directory
        project_dir = self.get_project_dir(project_id)
        destination_path = project_dir / final_filename
        
        try:
            shutil.copy2(file_path, destination_path)
        except Exception as e:
            raise FileManagementError(f"Failed to copy file: {e}")
        
        # Get file size
        file_size = destination_path.stat().st_size
        
        # Create file record
        file_id = str(uuid.uuid4())
        file_info = {
            "file_id": file_id,
            "filename": final_filename,
            "original_filename": original_filename,
            "project_id": project_id,
            "filepath": str(destination_path),
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "description": description,
            "status": "not_processed",
            "processing_result": None,
            "file_type": file_ext,
            "file_type_description": SUPPORTED_FILE_TYPES.get(file_ext, "Unknown")
        }
        
        # Register file
        self.register_file(project_id, file_info)
        
        return file_info
    
    def upload_file_from_url(self, project_id: str, url: str, 
                           description: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to a project from URL."""
        if not self.project_exists(project_id):
            raise FileManagementError(f"Project {project_id} does not exist")
        
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise FileManagementError("Invalid URL")
        
        try:
            # Download file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get filename from URL or Content-Disposition header
            filename = os.path.basename(parsed_url.path)
            if not filename:
                content_disposition = response.headers.get('content-disposition')
                if content_disposition:
                    match = re.search(r'filename="?([^"]+)"?', content_disposition)
                    if match:
                        filename = match.group(1)
            
            if not filename:
                raise FileManagementError("Could not determine filename from URL")
            
            # Validate file type
            file_ext = Path(filename).suffix.lower()
            if file_ext not in SUPPORTED_FILE_TYPES:
                raise FileManagementError(f"Unsupported file type: {file_ext}")
            
            # Generate unique filename
            final_filename = self._generate_unique_filename(project_id, filename)
            
            # Save file to project directory
            project_dir = self.get_project_dir(project_id)
            destination_path = project_dir / final_filename
            
            with open(destination_path, "wb") as buffer:
                for chunk in response.iter_content(chunk_size=8192):
                    buffer.write(chunk)
            
            # Get file size
            file_size = destination_path.stat().st_size
            
            # Create file record
            file_id = str(uuid.uuid4())
            file_info = {
                "file_id": file_id,
                "filename": final_filename,
                "original_filename": filename,
                "project_id": project_id,
                "filepath": str(destination_path),
                "size": file_size,
                "upload_date": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "description": description,
                "status": "not_processed",
                "processing_result": None,
                "file_type": file_ext,
                "file_type_description": SUPPORTED_FILE_TYPES.get(file_ext, "Unknown")
            }
            
            # Register file
            self.register_file(project_id, file_info)
            
            return file_info
            
        except requests.RequestException as e:
            raise FileManagementError(f"Failed to download file from URL: {e}")
        except Exception as e:
            raise FileManagementError(f"Failed to process file from URL: {e}")
    
    def _generate_unique_filename(self, project_id: str, original_filename: str) -> str:
        """Generate a unique filename for the project."""
        base_name = Path(original_filename).stem
        extension = Path(original_filename).suffix
        
        # Sanitize filename
        sanitized_base = re.sub(r'[^\w\-_.]', '_', base_name)
        sanitized_name = sanitized_base + extension
        
        # Handle filename collisions
        project_dir = self.get_project_dir(project_id)
        counter = 1
        final_filename = sanitized_name
        
        while (project_dir / final_filename).exists():
            final_filename = f"{sanitized_base}_{counter}{extension}"
            counter += 1
        
        return final_filename
    
    # ==================== FILE OPERATIONS ====================
    
    def delete_file(self, project_id: str, file_id: str) -> bool:
        """Delete a file from a project."""
        file_info = self.get_file_info(project_id, file_id)
        if not file_info:
            return False
        
        # Remove physical file
        file_path = Path(file_info["filepath"])
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                raise FileManagementError(f"Failed to delete physical file: {e}")
        
        # Remove from manifest
        self.unregister_file(project_id, file_id)
        
        return True
    
    def move_file(self, project_id: str, file_id: str, new_project_id: str) -> bool:
        """Move a file from one project to another."""
        if not self.project_exists(new_project_id):
            raise FileManagementError(f"Destination project {new_project_id} does not exist")
        
        file_info = self.get_file_info(project_id, file_id)
        if not file_info:
            return False
        
        # Generate new filename for destination project
        new_filename = self._generate_unique_filename(new_project_id, file_info["original_filename"])
        
        # Move physical file
        old_path = Path(file_info["filepath"])
        new_project_dir = self.get_project_dir(new_project_id)
        new_path = new_project_dir / new_filename
        
        try:
            shutil.move(str(old_path), str(new_path))
        except Exception as e:
            raise FileManagementError(f"Failed to move file: {e}")
        
        # Update file info
        file_info["project_id"] = new_project_id
        file_info["filename"] = new_filename
        file_info["filepath"] = str(new_path)
        file_info["updated_at"] = datetime.now().isoformat()
        
        # Register in new project and unregister from old project
        self.register_file(new_project_id, file_info)
        self.unregister_file(project_id, file_id)
        
        return True
    
    def copy_file(self, project_id: str, file_id: str, new_project_id: str) -> bool:
        """Copy a file from one project to another."""
        if not self.project_exists(new_project_id):
            raise FileManagementError(f"Destination project {new_project_id} does not exist")
        
        file_info = self.get_file_info(project_id, file_id)
        if not file_info:
            return False
        
        # Generate new filename for destination project
        new_filename = self._generate_unique_filename(new_project_id, file_info["original_filename"])
        
        # Copy physical file
        old_path = Path(file_info["filepath"])
        new_project_dir = self.get_project_dir(new_project_id)
        new_path = new_project_dir / new_filename
        
        try:
            shutil.copy2(str(old_path), str(new_path))
        except Exception as e:
            raise FileManagementError(f"Failed to copy file: {e}")
        
        # Create new file info
        new_file_id = str(uuid.uuid4())
        new_file_info = {
            "file_id": new_file_id,
            "filename": new_filename,
            "original_filename": file_info["original_filename"],
            "project_id": new_project_id,
            "filepath": str(new_path),
            "size": file_info["size"],
            "upload_date": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "description": f"Copy of {file_info.get('description', '')}",
            "status": "not_processed",
            "processing_result": None,
            "file_type": file_info.get("file_type"),
            "file_type_description": file_info.get("file_type_description")
        }
        
        # Register in new project
        self.register_file(new_project_id, new_file_info)
        
        return True
    
    # ==================== FILE SEARCH AND DISCOVERY ====================
    
    def find_file_by_name(self, project_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """Find a file by name within a project."""
        files = self.list_project_files(project_id)
        for file_info in files:
            if file_info.get("filename") == filename or file_info.get("original_filename") == filename:
                return file_info
        return None
    
    def search_files(self, project_id: str, query: str) -> List[Dict[str, Any]]:
        """Search files in a project by name or description."""
        files = self.list_project_files(project_id)
        query_lower = query.lower()
        
        results = []
        for file_info in files:
            filename = file_info.get("filename", "").lower()
            original_filename = file_info.get("original_filename", "").lower()
            description = file_info.get("description", "").lower()
            
            if (query_lower in filename or 
                query_lower in original_filename or 
                query_lower in description):
                results.append(file_info)
        
        return results
    
    def get_files_by_status(self, project_id: str, status: str) -> List[Dict[str, Any]]:
        """Get all files with a specific status in a project."""
        files = self.list_project_files(project_id)
        return [f for f in files if f.get("status") == status]
    
    def get_files_by_type(self, project_id: str, file_type: str) -> List[Dict[str, Any]]:
        """Get all files of a specific type in a project."""
        files = self.list_project_files(project_id)
        return [f for f in files if f.get("file_type") == file_type]
    
    # ==================== FILE STATUS MANAGEMENT ====================
    
    def check_file_output_exists(self, file_info: Dict[str, Any]) -> bool:
        """
        Check if output directory exists for a file.
        
        Args:
            file_info: File information dictionary
            
        Returns:
            bool: True if output exists, False otherwise
        """
        try:
            project_id = file_info.get('project_id')
            filename = file_info.get('filename', '')
            file_stem = Path(filename).stem  # Remove extension
            
            # Check multiple possible output locations based on actual ETL pipeline structure
            possible_outputs = [
                # Main ETL output structure: output/projects/{project_id}/{filename_stem}/
                self.output_dir / "projects" / project_id / file_stem,
                
                # Legacy output structure: output/{filename_stem}/
                self.output_dir / file_stem
            ]
            
            for output_dir in possible_outputs:
                if output_dir.exists():
                    # Check if there are any files in the output directory
                    if any(output_dir.iterdir()):
                        print(f"✅ Found output for {filename} in: {output_dir}")
                        return True
            
            print(f"❌ No output found for {filename}")
            return False
        except Exception as e:
            print(f"⚠️  Error checking output for {file_info.get('filename', 'unknown')}: {e}")
            return False
    
    def update_twin_status_to_orphaned(self, filename: str, project_id: str):
        """Update twin status to orphaned when file output is missing"""
        if self.use_database:
            return self.db_manager.update_twin_status_to_orphaned(filename, project_id)
        else:
            # Fallback for JSON-based system - just log the event
            print(f"⚠️ Twin orphaned: {filename} in project {project_id} (JSON mode)")
            return {'success': True, 'message': 'Twin orphaned (JSON mode)'}

    def reset_file_statuses_if_output_missing(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if completed files have missing output and reset them to not_processed.
        Also updates twin status to orphaned when output is missing.
        
        Args:
            project_id: Optional project ID to check only that project. If None, checks all projects.
            
        Returns:
            Dict with reset information
        """
        try:
            reset_count = 0
            reset_files = []
            orphaned_twins = 0
            
            # Determine which projects to check
            if project_id:
                projects_to_check = [project_id] if self.project_exists(project_id) else []
            else:
                projects_to_check = [p['project_id'] for p in self.list_projects()]
            
            # Check each project
            for pid in projects_to_check:
                files = self.list_project_files(pid)
                
                for file_info in files:
                    current_status = file_info.get('status', 'not_processed')
                    
                    if current_status in ['completed', 'processing']:
                        # Check if output directory exists for this file
                        output_exists = self.check_file_output_exists(file_info)
                        
                        if not output_exists:
                            # Reset status to not_processed
                            old_status = file_info['status']
                            file_info['status'] = 'not_processed'
                            file_info['processing_result'] = None  # Clear processing result
                            
                            # Get the correct file ID field
                            file_id = file_info['file_id']
                            
                            if file_id:
                                # Update the file in the manifest
                                self.update_file_status(pid, file_id, 'not_processed', None)
                                
                                reset_files.append({
                                    'project_id': pid,
                                    'file_id': file_id,
                                    'filename': file_info.get('filename', 'unknown'),
                                    'old_status': old_status
                                })
                                
                                reset_count += 1
                                print(f"🔄 Auto-reset {file_info.get('filename', 'unknown')} from '{old_status}' to 'not_processed' (output missing)")
                            else:
                                print(f"⚠️ Could not reset {file_info.get('filename', 'unknown')} - no file ID found")
                            
                            # Update twin status to orphaned using direct database update
                            if old_status == 'completed':
                                try:
                                    twin_result = self.update_twin_status_to_orphaned(
                                        file_info.get('filename', 'unknown'),
                                        pid
                                    )
                                    if twin_result.get('success', False):
                                        orphaned_twins += 1
                                        print(f"🔗 Updated twin status to orphaned for {file_info.get('filename', 'unknown')}")
                                    else:
                                        print(f"⚠️ Could not update twin status: {twin_result.get('error', 'Unknown error')}")
                                except Exception as e:
                                    print(f"⚠️ Error updating twin status: {e}")
            
            if reset_count > 0:
                print(f"✅ Auto-reset {reset_count} files due to missing output directories")
            if orphaned_twins > 0:
                print(f"🔗 Updated {orphaned_twins} twins to orphaned status")
            
            return {
                'success': True,
                'reset_count': reset_count,
                'reset_files': reset_files,
                'orphaned_twins': orphaned_twins,
                'message': f"Reset {reset_count} files from completed to not_processed, {orphaned_twins} twins orphaned",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in reset_file_statuses_if_output_missing: {e}")
            return {
                'success': False,
                'error': str(e),
                'reset_count': 0,
                'reset_files': [],
                'orphaned_twins': 0,
                'message': f"Error resetting file statuses: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def refresh_files_and_reset_statuses(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Refresh files and reset statuses if output is missing.
        This is a comprehensive refresh function that can be used across all modules.
        
        Args:
            project_id: Optional project ID to refresh only that project. If None, refreshes all projects.
            
        Returns:
            Dict with refresh and reset information
        """
        try:
            # First sync projects with disk to detect any new files
            if project_id:
                sync_result = self.sync_project_with_disk(project_id)
            else:
                sync_result = self.sync_all_projects()
            
            # Then reset file statuses if output is missing
            reset_result = self.reset_file_statuses_if_output_missing(project_id)
            
            return {
                'success': True,
                'sync_result': sync_result,
                'reset_result': reset_result,
                'message': f"Refreshed files and reset {reset_result['reset_count']} statuses",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in refresh_files_and_reset_statuses: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Error refreshing files: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    # ==================== PROJECT SYNCHRONIZATION ====================
    
    def sync_project_with_disk(self, project_id: str) -> Dict[str, Any]:
        """Synchronize project files with actual files on disk."""
        if not self.project_exists(project_id):
            raise FileManagementError(f"Project {project_id} does not exist")
        
        project_dir = self.get_project_dir(project_id)
        files = self.list_project_files(project_id)
        
        # Get actual files on disk
        disk_files = list(project_dir.glob("*"))
        disk_filenames = {f.name for f in disk_files if f.is_file() and f.name not in ["project.json", "files.json"]}
        
        # Get filenames from manifest
        manifest_filenames = {f.get("filename") for f in files}
        
        # Find orphaned files (in manifest but not on disk)
        orphaned_files = manifest_filenames - disk_filenames
        orphaned_count = len(orphaned_files)
        
        # Remove orphaned files from manifest
        if orphaned_files:
            # This part of the logic needs to be adapted to use the database manager
            # For now, we'll just print a warning and continue, as the database manager
            # doesn't have a direct 'unregister_file' method.
            # The original code had a fallback to JSON, which is removed.
            # This means orphaned files will not be removed from the manifest in the DB.
            print(f"⚠️ Orphaned files found in manifest but not on disk for project {project_id}: {orphaned_files}")
            print("⚠️ Orphaned files cannot be removed from manifest in the current DB-only implementation.")
        
        # Find new files (on disk but not in manifest)
        new_files = disk_filenames - manifest_filenames
        new_count = len(new_files)
        
        # Add new files to manifest
        for filename in new_files:
            file_path = project_dir / filename
            file_size = file_path.stat().st_size
            file_ext = file_path.suffix.lower()
            
            file_info = {
                "file_id": str(uuid.uuid4()),
                "filename": filename,
                "original_filename": filename,
                "project_id": project_id,
                "filepath": str(file_path),
                "size": file_size,
                "upload_date": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "description": f"Discovered file: {filename}",
                "status": "not_processed",
                "processing_result": None,
                "file_type": file_ext,
                "file_type_description": SUPPORTED_FILE_TYPES.get(file_ext, "Unknown")
            }
            
            files.append(file_info)
        
        if new_files:
            # This part of the logic needs to be adapted to use the database manager
            # For now, we'll just print a warning and continue, as the database manager
            # doesn't have a direct 'save_files_manifest' method.
            # The original code had a fallback to JSON, which is removed.
            print(f"⚠️ New files found on disk but not in manifest for project {project_id}: {new_files}")
            print("⚠️ New files cannot be added to manifest in the current DB-only implementation.")
        
        # Update project stats
        self._update_project_stats(project_id)
        
        return {
            "project_id": project_id,
            "orphaned_files_removed": orphaned_count,
            "new_files_discovered": new_count,
            "total_files": len(files)
        }
    
    def sync_all_projects(self) -> Dict[str, Any]:
        """Synchronize all projects with disk."""
        projects = self.list_projects()
        results = {
            "total_projects": len(projects),
            "synced_projects": [],
            "errors": []
        }
        
        for project in projects:
            try:
                sync_result = self.sync_project_with_disk(project["project_id"])
                results["synced_projects"].append(sync_result)
            except Exception as e:
                results["errors"].append({
                    "project_id": project["project_id"],
                    "error": str(e)
                })
        
        return results
    
    def close(self):
        """Close database connection if using database manager."""
        if self.use_database and hasattr(self, 'db_manager'):
            self.db_manager.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def register_digital_twin(self, project_id: str, file_id: str, twin_data: Dict[str, Any] = None):
        """Register a digital twin for the given file_id in the given project."""
        if self.use_database:
            # Use centralized DatabaseManager
            if twin_data is None:
                twin_data = {
                    'twin_name': f'Twin_{file_id}',
                    'twin_type': 'aasx_digital_twin',
                    'description': f'Digital twin for file {file_id}',
                    'version': '1.0.0',
                    'owner': 'system',
                    'tags': ['aasx', 'digital_twin'],
                    'settings': {},
                    'metadata': {}
                }
            return self.db_manager.register_digital_twin(project_id, file_id, twin_data)
        else:
            # Fallback for JSON-based system
            print(f"⚠️ Twin registration not supported in JSON mode for file {file_id}")
            return {'success': False, 'error': 'Twin registration not supported in JSON mode'}
    
    def update_digital_twin(self, project_id: str, file_id: str, twin_data: Dict[str, Any]):
        """Update an existing digital twin with new data."""
        if self.use_database:
            # Use centralized DatabaseManager
            return self.db_manager.update_digital_twin(project_id, file_id, twin_data)
        else:
            # Fallback for JSON-based system
            print(f"⚠️ Twin update not supported in JSON mode for file {file_id}")
            return {'success': False, 'error': 'Twin update not supported in JSON mode'}

# ==================== BACKWARD COMPATIBILITY FUNCTIONS ====================

# Keep existing functions for backward compatibility
def get_project_dir(base_dir: Path, project_id: str) -> Path:
    """Get the path to a project directory."""
    return base_dir / project_id

def create_project(base_dir: Path, project_id: str, metadata: Dict[str, Any]) -> Path:
    """Create a project directory and project.json if not exists."""
    manager = ProjectManager(base_dir)
    return manager.create_project(project_id, metadata)

def load_files_manifest(project_dir: Path) -> list:
    """Load files.json manifest as a list."""
    project_id = project_dir.name
    manager = ProjectManager(project_dir.parent)
    return manager.list_project_files(project_id) # Changed to list_project_files

def save_files_manifest(project_dir: Path, files: list):
    """Save the files.json manifest."""
    project_id = project_dir.name
    manager = ProjectManager(project_dir.parent)
    # This function is no longer needed as file management is DB-driven
    print(f"⚠️ save_files_manifest is deprecated. File management is now DB-driven for project {project_id}")
    # The original code had a fallback to JSON, which is removed.
    # This means saving files.json is not possible in the current DB-only implementation.

def register_file(project_dir: Path, file_info: Dict[str, Any]):
    """Add or update a file entry in files.json."""
    project_id = project_dir.name
    manager = ProjectManager(project_dir.parent)
    manager.register_file(project_id, file_info)

def check_duplicate_file(project_dir: Path, filename: str) -> bool:
    """Return True if file already exists in files.json."""
    project_id = project_dir.name
    manager = ProjectManager(project_dir.parent)
    return manager.check_duplicate_file(project_id, filename)

def update_processing_status(project_dir: Path, filename: str, status: str, result: Optional[Any] = None):
    """Update the status and processing result for a file in files.json."""
    project_id = project_dir.name
    manager = ProjectManager(project_dir.parent)
    
    # Find file by filename
    files = manager.list_project_files(project_id) # Changed to list_project_files
    for file_info in files:
        if file_info.get("filename") == filename:
            file_id = file_info.get('file_id')
            manager.update_file_status(project_id, file_id, status, result)
            break

def load_project_metadata(project_dir: Path) -> Dict[str, Any]:
    """Load project.json metadata."""
    project_id = project_dir.name
    manager = ProjectManager(project_dir.parent)
    return manager.get_project_metadata(project_id)

def save_project_metadata(project_dir: Path, metadata: Dict[str, Any]):
    """Save project.json metadata."""
    project_id = project_dir.name
    manager = ProjectManager(project_dir.parent)
    manager.update_project_metadata(project_id, metadata) 