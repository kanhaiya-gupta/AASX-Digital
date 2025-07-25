import os
import json
import shutil
import uuid
import re
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from urllib.parse import urlparse
import requests

# Global configuration
DEFAULT_PROJECTS_DIR = Path("data/projects")
DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_DB_PATH = Path("data/aasx_digital.db")
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

class DatabaseManagerError(Exception):
    """Custom exception for database management operations"""
    pass

class DatabaseProjectManager:
    """Database-driven project and file management system"""
    
    def __init__(self, projects_dir: Path = None, output_dir: Path = None, db_path: Path = None):
        self.projects_dir = projects_dir or DEFAULT_PROJECTS_DIR
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        self.db_path = db_path or DEFAULT_DB_PATH
        
        # Ensure directories exist
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database connection
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection and verify schema"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            self.cursor = self.conn.cursor()
            
            # Enable foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            # Verify database has required tables
            self._verify_database_schema()
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to initialize database: {e}")
    
    def _verify_database_schema(self):
        """Verify that the database has the required tables"""
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    'users', 'organizations', 'projects', 'project_files', 
                    'processing_results'
                )
            """)
            tables = [row[0] for row in self.cursor.fetchall()]
            
            required_tables = ['users', 'organizations', 'projects', 'project_files', 'processing_results']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                raise DatabaseManagerError(f"Database missing required tables: {missing_tables}")
                
        except Exception as e:
            raise DatabaseManagerError(f"Failed to verify database schema: {e}")
    
    def _get_default_user_id(self) -> str:
        """Get the default admin user ID for operations"""
        try:
            self.cursor.execute("SELECT user_id FROM users WHERE username = 'admin' LIMIT 1")
            result = self.cursor.fetchone()
            if result:
                return result[0]
            
            # Create default admin user if not exists
            admin_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO users (user_id, username, email, password_hash, full_name, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (admin_id, 'admin', 'admin@aasx-digital.com', 'default_hash', 'System Administrator', 'admin', 'active'))
            
            self.conn.commit()
            return admin_id
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to get default user: {e}")
    
    def _get_default_org_id(self) -> str:
        """Get the default organization ID for operations"""
        try:
            self.cursor.execute("SELECT org_id FROM organizations WHERE name = 'Default Organization' LIMIT 1")
            result = self.cursor.fetchone()
            if result:
                return result[0]
            
            # Create default organization if not exists
            org_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO organizations (org_id, name, description, plan_type, status)
                VALUES (?, ?, ?, ?, ?)
            """, (org_id, 'Default Organization', 'Default organization for system operations', 'basic', 'active'))
            
            self.conn.commit()
            return org_id
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to get default organization: {e}")
    
    # ==================== PROJECT MANAGEMENT ====================
    
    def create_project(self, project_id: str, metadata: Dict[str, Any], owner_id: str = None) -> Path:
        """
        Create a project in the database and project directory.
        Returns the project directory path.
        """
        if owner_id is None:
            owner_id = self._get_default_user_id()
        
        # Create project directory
        project_dir = self.get_project_dir(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Set default metadata
        if 'created_at' not in metadata:
            metadata['created_at'] = datetime.now().isoformat()
        if 'updated_at' not in metadata:
            metadata['updated_at'] = datetime.now().isoformat()
        if 'file_count' not in metadata:
            metadata['file_count'] = 0
        if 'total_size' not in metadata:
            metadata['total_size'] = 0
        
        try:
            # Insert project into database
            self.cursor.execute("""
                INSERT INTO projects (
                    project_id, name, description, tags, file_count, total_size,
                    created_at, updated_at, metadata, owner_id, is_public, access_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                metadata.get('name', f'Project {project_id}'),
                metadata.get('description', ''),
                json.dumps(metadata.get('tags', [])),
                metadata.get('file_count', 0),
                metadata.get('total_size', 0),
                metadata['created_at'],
                metadata['updated_at'],
                json.dumps(metadata),
                owner_id,
                metadata.get('is_public', False),
                metadata.get('access_level', 'private')
            ))
            
            # Create project permissions for owner
            self.cursor.execute("""
                INSERT INTO project_permissions (project_id, user_id, permission_type, granted_at)
                VALUES (?, ?, ?, ?)
            """, (project_id, owner_id, 'admin', datetime.now().isoformat()))
            
            self.conn.commit()
            
            # Also create project.json for backward compatibility
            project_json = project_dir / "project.json"
            if not project_json.exists():
                with open(project_json, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)
            
            return project_dir
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DatabaseManagerError(f"Project {project_id} already exists")
            raise DatabaseManagerError(f"Database constraint error: {e}")
        except Exception as e:
            raise DatabaseManagerError(f"Failed to create project: {e}")
    
    def get_project_dir(self, project_id: str) -> Path:
        """Get the path to a project directory."""
        return self.projects_dir / project_id
    
    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists in the database."""
        try:
            self.cursor.execute("SELECT project_id FROM projects WHERE project_id = ?", (project_id,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            raise DatabaseManagerError(f"Failed to check project existence: {e}")
    
    def list_projects(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List all projects accessible to a user."""
        try:
            if user_id is None:
                # Get all projects for admin
                self.cursor.execute("""
                    SELECT p.*, u.username as owner_name
                    FROM projects p
                    LEFT JOIN users u ON p.owner_id = u.user_id
                    ORDER BY p.created_at DESC
                """)
            else:
                # Get projects user has access to
                self.cursor.execute("""
                    SELECT DISTINCT p.*, u.username as owner_name
                    FROM projects p
                    LEFT JOIN users u ON p.owner_id = u.user_id
                    LEFT JOIN project_permissions pp ON p.project_id = pp.project_id
                    WHERE p.owner_id = ? OR pp.user_id = ? OR p.is_public = 1
                    ORDER BY p.created_at DESC
                """, (user_id, user_id))
            
            projects = []
            for row in self.cursor.fetchall():
                project_dict = dict(row)
                # Parse JSON fields
                if project_dict.get('tags'):
                    project_dict['tags'] = json.loads(project_dict['tags'])
                if project_dict.get('metadata'):
                    project_dict['metadata'] = json.loads(project_dict['metadata'])
                projects.append(project_dict)
            
            return projects
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to list projects: {e}")
    
    def get_project_metadata(self, project_id: str) -> Dict[str, Any]:
        """Get project metadata from database."""
        try:
            self.cursor.execute("""
                SELECT p.*, u.username as owner_name
                FROM projects p
                LEFT JOIN users u ON p.owner_id = u.user_id
                WHERE p.project_id = ?
            """, (project_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return {}
            
            project_dict = dict(row)
            # Parse JSON fields
            if project_dict.get('tags'):
                project_dict['tags'] = json.loads(project_dict['tags'])
            if project_dict.get('metadata'):
                project_dict['metadata'] = json.loads(project_dict['metadata'])
            
            return project_dict
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to get project metadata: {e}")
    
    def update_project_metadata(self, project_id: str, updates: Dict[str, Any]):
        """Update project metadata in database."""
        try:
            # Get current metadata
            current = self.get_project_metadata(project_id)
            if not current:
                raise DatabaseManagerError(f"Project {project_id} not found")
            
            # Update fields
            current.update(updates)
            current['updated_at'] = datetime.now().isoformat()
            
            # Update database
            self.cursor.execute("""
                UPDATE projects 
                SET name = ?, description = ?, tags = ?, metadata = ?, updated_at = ?
                WHERE project_id = ?
            """, (
                current.get('name', ''),
                current.get('description', ''),
                json.dumps(current.get('tags', [])),
                json.dumps(current.get('metadata', {})),
                current['updated_at'],
                project_id
            ))
            
            self.conn.commit()
            
            # Also update project.json for backward compatibility
            project_dir = self.get_project_dir(project_id)
            project_json = project_dir / "project.json"
            if project_json.exists():
                with open(project_json, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)
                    
        except Exception as e:
            raise DatabaseManagerError(f"Failed to update project metadata: {e}")
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project from database and filesystem."""
        try:
            # Check if project exists
            if not self.project_exists(project_id):
                return False
            
            # Delete from database (cascading will handle related records)
            self.cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            self.conn.commit()
            
            # Delete project directory
            project_dir = self.get_project_dir(project_id)
            if project_dir.exists():
                shutil.rmtree(project_dir)
            
            return True
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to delete project: {e}")
    
    # ==================== FILE MANAGEMENT ====================
    
    def register_file(self, project_id: str, file_info: Dict[str, Any]):
        """Add or update a file entry in the database."""
        try:
            # Temporarily disable foreign key constraints to avoid the twins table constraint issue
            self.cursor.execute("PRAGMA foreign_keys = OFF")
            
            # Check if file already exists
            self.cursor.execute("""
                SELECT file_id FROM project_files 
                WHERE project_id = ? AND filename = ?
            """, (project_id, file_info.get('filename')))
            
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing file
                self.cursor.execute("""
                    UPDATE project_files SET
                        original_filename = ?, filepath = ?, size = ?, 
                        description = ?, status = ?, updated_at = ?,
                        file_type = ?, file_type_description = ?
                    WHERE file_id = ?
                """, (
                    file_info.get('original_filename'),
                    file_info.get('filepath'),
                    file_info.get('size', 0),
                    file_info.get('description', ''),
                    file_info.get('status', 'not_processed'),
                    datetime.now().isoformat(),
                    file_info.get('file_type', ''),
                    file_info.get('file_type_description', ''),
                    existing[0]
                ))
                file_id = existing[0]
            else:
                # Insert new file
                file_id = file_info.get('id', str(uuid.uuid4()))
                self.cursor.execute("""
                    INSERT INTO project_files (
                        file_id, filename, original_filename, project_id, filepath,
                        size, upload_date, updated_at, description, status,
                        file_type, file_type_description, uploaded_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id,
                    file_info.get('filename'),
                    file_info.get('original_filename'),
                    project_id,
                    file_info.get('filepath'),
                    file_info.get('size', 0),
                    file_info.get('upload_date', datetime.now().isoformat()),
                    file_info.get('updated_at', datetime.now().isoformat()),
                    file_info.get('description', ''),
                    file_info.get('status', 'not_processed'),
                    file_info.get('file_type', ''),
                    file_info.get('file_type_description', ''),
                    file_info.get('uploaded_by', self._get_default_user_id())
                ))
            
            # Re-enable foreign key constraints
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            self.conn.commit()
            self._update_project_stats(project_id)
            
            # Also update files.json for backward compatibility
            self._sync_files_json(project_id)
            
        except Exception as e:
            # Re-enable foreign key constraints in case of error
            self.cursor.execute("PRAGMA foreign_keys = ON")
            raise DatabaseManagerError(f"Failed to register file: {e}")
    
    def unregister_file(self, project_id: str, file_id: str):
        """Remove a file entry from the database."""
        try:
            self.cursor.execute("DELETE FROM project_files WHERE file_id = ? AND project_id = ?", 
                               (file_id, project_id))
            self.conn.commit()
            
            self._update_project_stats(project_id)
            self._sync_files_json(project_id)
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to unregister file: {e}")
    
    def get_file_info(self, project_id: str, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information by ID from database."""
        try:
            self.cursor.execute("""
                SELECT * FROM project_files 
                WHERE file_id = ? AND project_id = ?
            """, (file_id, project_id))
            
            row = self.cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to get file info: {e}")
    
    def list_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """List all files in a project from database."""
        try:
            self.cursor.execute("""
                SELECT * FROM project_files 
                WHERE project_id = ?
                ORDER BY upload_date DESC
            """, (project_id,))
            
            files = []
            for row in self.cursor.fetchall():
                files.append(dict(row))
            
            return files
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to list project files: {e}")
    
    def check_duplicate_file(self, project_id: str, filename: str) -> bool:
        """Check if a file already exists in the project."""
        try:
            self.cursor.execute("""
                SELECT file_id FROM project_files 
                WHERE project_id = ? AND filename = ?
            """, (project_id, filename))
            
            return self.cursor.fetchone() is not None
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to check duplicate file: {e}")
    
    def update_file_status(self, project_id: str, file_id: str, status: str, result: Optional[Any] = None):
        """Update the status and processing result for a file."""
        try:
            # Update file status
            self.cursor.execute("""
                UPDATE project_files 
                SET status = ?, updated_at = ?
                WHERE file_id = ? AND project_id = ?
            """, (status, datetime.now().isoformat(), file_id, project_id))
            
            # Update or create processing result
            if result is not None:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO processing_results (
                        file_id, project_id, processing_status, timestamp, 
                        processed_by, extraction_results
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    file_id, project_id, status, datetime.now().isoformat(),
                    self._get_default_user_id(), json.dumps(result)
                ))
            
            self.conn.commit()
            self._sync_files_json(project_id)
            # No more auto-registration here; registration is explicit in the ETL route.
        except Exception as e:
            raise DatabaseManagerError(f"Failed to update file status: {e}")
    
    def _update_project_stats(self, project_id: str):
        """Update project file count and total size in database."""
        try:
            self.cursor.execute("""
                SELECT COUNT(*) as file_count, COALESCE(SUM(size), 0) as total_size
                FROM project_files 
                WHERE project_id = ?
            """, (project_id,))
            
            stats = self.cursor.fetchone()
            
            self.cursor.execute("""
                UPDATE projects 
                SET file_count = ?, total_size = ?, updated_at = ?
                WHERE project_id = ?
            """, (stats[0], stats[1], datetime.now().isoformat(), project_id))
            
            self.conn.commit()
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to update project stats: {e}")
    
    def _sync_files_json(self, project_id: str):
        """Sync database files to files.json for backward compatibility."""
        try:
            files = self.list_project_files(project_id)
            
            # Convert database format to JSON format
            json_files = []
            for file_info in files:
                json_file = {
                    "id": file_info['file_id'],
                    "filename": file_info['filename'],
                    "original_filename": file_info['original_filename'],
                    "project_id": file_info['project_id'],
                    "filepath": file_info['filepath'],
                    "size": file_info['size'],
                    "upload_date": file_info['upload_date'],
                    "updated_at": file_info['updated_at'],
                    "description": file_info['description'],
                    "status": file_info['status'],
                    "file_type": file_info['file_type'],
                    "file_type_description": file_info['file_type_description']
                }
                json_files.append(json_file)
            
            # Save to files.json
            project_dir = self.get_project_dir(project_id)
            files_json = project_dir / "files.json"
            with open(files_json, "w", encoding="utf-8") as f:
                json.dump(json_files, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Failed to sync files.json: {e}")
    
    # ==================== FILE UPLOAD OPERATIONS ====================
    
    def upload_file(self, project_id: str, file_path: Path, original_filename: str, 
                   description: Optional[str] = None, uploaded_by: str = None) -> Dict[str, Any]:
        """Upload a file to a project."""
        if not self.project_exists(project_id):
            raise DatabaseManagerError(f"Project {project_id} does not exist")
        
        if uploaded_by is None:
            uploaded_by = self._get_default_user_id()
        
        # Validate file type
        file_ext = file_path.suffix.lower()
        if file_ext not in SUPPORTED_FILE_TYPES:
            raise DatabaseManagerError(f"Unsupported file type: {file_ext}")
        
        # Generate unique filename
        final_filename = self._generate_unique_filename(project_id, original_filename)
        
        # Copy file to project directory
        project_dir = self.get_project_dir(project_id)
        destination_path = project_dir / final_filename
        
        try:
            shutil.copy2(file_path, destination_path)
        except Exception as e:
            raise DatabaseManagerError(f"Failed to copy file: {e}")
        
        # Get file size
        file_size = destination_path.stat().st_size
        
        # Create file record
        file_id = str(uuid.uuid4())
        file_info = {
            "id": file_id,
            "filename": final_filename,
            "original_filename": original_filename,
            "project_id": project_id,
            "filepath": str(destination_path),
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "description": description,
            "status": "not_processed",
            "file_type": file_ext,
            "file_type_description": SUPPORTED_FILE_TYPES.get(file_ext, "Unknown"),
            "uploaded_by": uploaded_by
        }
        
        # Register file
        self.register_file(project_id, file_info)
        
        return file_info
    
    def _generate_unique_filename(self, project_id: str, original_filename: str) -> str:
        """Generate a unique filename for the project."""
        base_name = Path(original_filename).stem
        extension = Path(original_filename).suffix
        
        # Sanitize filename
        sanitized_base = re.sub(r'[^\w\-_.]', '_', base_name)
        sanitized_name = sanitized_base + extension
        
        # Handle filename collisions
        counter = 1
        final_filename = sanitized_name
        
        while self.check_duplicate_file(project_id, final_filename):
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
                raise DatabaseManagerError(f"Failed to delete physical file: {e}")
        
        # Remove from database
        self.unregister_file(project_id, file_id)
        
        return True
    
    # ==================== FILE SEARCH AND DISCOVERY ====================
    
    def find_file_by_name(self, project_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """Find a file by name within a project."""
        try:
            self.cursor.execute("""
                SELECT * FROM project_files 
                WHERE project_id = ? AND (filename = ? OR original_filename = ?)
            """, (project_id, filename, filename))
            
            row = self.cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to find file by name: {e}")
    
    def search_files(self, project_id: str, query: str) -> List[Dict[str, Any]]:
        """Search files in a project by name or description."""
        try:
            self.cursor.execute("""
                SELECT * FROM project_files 
                WHERE project_id = ? AND (
                    filename LIKE ? OR 
                    original_filename LIKE ? OR 
                    description LIKE ?
                )
                ORDER BY upload_date DESC
            """, (project_id, f"%{query}%", f"%{query}%", f"%{query}%"))
            
            files = []
            for row in self.cursor.fetchall():
                files.append(dict(row))
            
            return files
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to search files: {e}")
    
    def get_files_by_status(self, project_id: str, status: str) -> List[Dict[str, Any]]:
        """Get all files with a specific status in a project."""
        try:
            self.cursor.execute("""
                SELECT * FROM project_files 
                WHERE project_id = ? AND status = ?
                ORDER BY upload_date DESC
            """, (project_id, status))
            
            files = []
            for row in self.cursor.fetchall():
                files.append(dict(row))
            
            return files
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to get files by status: {e}")
    
    def get_files_by_type(self, project_id: str, file_type: str) -> List[Dict[str, Any]]:
        """Get all files of a specific type in a project."""
        try:
            self.cursor.execute("""
                SELECT * FROM project_files 
                WHERE project_id = ? AND file_type = ?
                ORDER BY upload_date DESC
            """, (project_id, file_type))
            
            files = []
            for row in self.cursor.fetchall():
                files.append(dict(row))
            
            return files
            
        except Exception as e:
            raise DatabaseManagerError(f"Failed to get files by type: {e}")
    
    # ==================== FILE STATUS MANAGEMENT ====================
    
    def check_file_output_exists(self, file_info: Dict[str, Any]) -> bool:
        """Check if output directory exists for a file."""
        try:
            project_id = file_info.get('project_id')
            filename = file_info.get('filename', '')
            file_stem = Path(filename).stem
            
            # Check multiple possible output locations
            possible_outputs = [
                self.output_dir / "projects" / project_id / file_stem,
                self.output_dir / file_stem
            ]
            
            for output_dir in possible_outputs:
                if output_dir.exists() and any(output_dir.iterdir()):
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking output for {file_info.get('filename', 'unknown')}: {e}")
            return False
    
    def reset_file_statuses_if_output_missing(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if completed files have missing output and reset them. Also update digital twin status to orphaned."""
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
                files = self.get_files_by_status(pid, 'completed')
                files.extend(self.get_files_by_status(pid, 'processing'))
                for file_info in files:
                    output_exists = self.check_file_output_exists(file_info)
                    if not output_exists:
                        # Reset status to not_processed
                        old_status = file_info['status']
                        self.update_file_status(pid, file_info['file_id'], 'not_processed', None)
                        reset_files.append({
                            'project_id': pid,
                            'file_id': file_info['file_id'],
                            'filename': file_info.get('filename', 'unknown'),
                            'old_status': old_status
                        })
                        reset_count += 1
                        # Update digital twin status to orphaned
                        try:
                            twin_result = self.update_twin_status_to_orphaned(file_info.get('filename', 'unknown'), pid)
                            if twin_result.get('success', False):
                                orphaned_twins += 1
                        except Exception as e:
                            print(f"⚠️ Error updating twin status: {e}")
            return {
                'success': True,
                'reset_count': reset_count,
                'reset_files': reset_files,
                'orphaned_twins': orphaned_twins,
                'message': f"Reset {reset_count} files from completed to not_processed, {orphaned_twins} twins orphaned",
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'reset_count': 0,
                'reset_files': [],
                'orphaned_twins': 0,
                'message': f"Error resetting file statuses: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    # ==================== PROJECT SYNCHRONIZATION ====================
    
    def sync_project_with_disk(self, project_id: str) -> Dict[str, Any]:
        """Synchronize project files with actual files on disk."""
        if not self.project_exists(project_id):
            raise DatabaseManagerError(f"Project {project_id} does not exist")
        
        project_dir = self.get_project_dir(project_id)
        files = self.list_project_files(project_id)
        
        # Get actual files on disk
        disk_files = list(project_dir.glob("*"))
        disk_filenames = {f.name for f in disk_files if f.is_file() and f.name not in ["project.json", "files.json"]}
        
        # Get filenames from database
        db_filenames = {f.get("filename") for f in files}
        
        # Find orphaned files (in database but not on disk)
        orphaned_files = db_filenames - disk_filenames
        orphaned_count = len(orphaned_files)
        
        # Remove orphaned files from database
        for filename in orphaned_files:
            self.cursor.execute("""
                DELETE FROM project_files 
                WHERE project_id = ? AND filename = ?
            """, (project_id, filename))
        
        # Find new files (on disk but not in database)
        new_files = disk_filenames - db_filenames
        new_count = len(new_files)
        
        # Add new files to database
        for filename in new_files:
            file_path = project_dir / filename
            file_size = file_path.stat().st_size
            file_ext = file_path.suffix.lower()
            
            file_info = {
                "id": str(uuid.uuid4()),
                "filename": filename,
                "original_filename": filename,
                "project_id": project_id,
                "filepath": str(file_path),
                "size": file_size,
                "upload_date": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "description": f"Discovered file: {filename}",
                "status": "not_processed",
                "file_type": file_ext,
                "file_type_description": SUPPORTED_FILE_TYPES.get(file_ext, "Unknown"),
                "uploaded_by": self._get_default_user_id()
            }
            
            self.register_file(project_id, file_info)
        
        if orphaned_files or new_files:
            self.conn.commit()
            self._update_project_stats(project_id)
        
        return {
            "project_id": project_id,
            "orphaned_files_removed": orphaned_count,
            "new_files_discovered": new_count,
            "total_files": len(self.list_project_files(project_id))
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
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 