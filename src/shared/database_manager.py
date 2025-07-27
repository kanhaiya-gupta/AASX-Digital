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
                    'processing_results', 'twin_relationships', 'twin_configurations',
                    'twin_events', 'twin_health', 'sync_history'
                )
            """)
            tables = [row[0] for row in self.cursor.fetchall()]
            
            required_tables = [
                'users', 'organizations', 'projects', 'project_files', 
                'processing_results', 'twin_relationships', 'twin_configurations',
                'twin_events', 'twin_health', 'sync_history'
            ]
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                # Create missing tables
                self._create_missing_tables(missing_tables)
                
        except Exception as e:
            raise DatabaseManagerError(f"Failed to verify database schema: {e}")
    
    def _create_missing_tables(self, missing_tables: List[str]):
        """Create missing database tables"""
        try:
            for table in missing_tables:
                if table == 'users':
                    self.cursor.execute('''
                        CREATE TABLE users (
                            user_id TEXT PRIMARY KEY,
                            username TEXT UNIQUE NOT NULL,
                            email TEXT UNIQUE,
                            full_name TEXT,
                            organization_id TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (organization_id) REFERENCES organizations (org_id)
                        )
                    ''')
                elif table == 'organizations':
                    self.cursor.execute('''
                        CREATE TABLE organizations (
                            org_id TEXT PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                elif table == 'projects':
                    self.cursor.execute('''
                        CREATE TABLE projects (
                            project_id TEXT PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            owner_id TEXT,
                            organization_id TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            metadata TEXT,
                            FOREIGN KEY (owner_id) REFERENCES users (user_id),
                            FOREIGN KEY (organization_id) REFERENCES organizations (org_id)
                        )
                    ''')
                elif table == 'project_files':
                    self.cursor.execute('''
                        CREATE TABLE project_files (
                            file_id TEXT PRIMARY KEY,
                            project_id TEXT NOT NULL,
                            filename TEXT NOT NULL,
                            original_filename TEXT NOT NULL,
                            filepath TEXT NOT NULL,
                            file_type TEXT,
                            file_type_description TEXT,
                            size INTEGER,
                            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            description TEXT,
                            status TEXT DEFAULT 'not_processed',
                            processing_result TEXT,
                            metadata TEXT,
                            uploaded_by TEXT,
                            FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
                        )
                    ''')
                elif table == 'processing_results':
                    self.cursor.execute('''
                        CREATE TABLE processing_results (
                            result_id TEXT PRIMARY KEY,
                            file_id TEXT NOT NULL,
                            project_id TEXT NOT NULL,
                            processing_type TEXT NOT NULL,
                            status TEXT NOT NULL,
                            result_data TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (file_id) REFERENCES project_files (file_id) ON DELETE CASCADE,
                            FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
                        )
                    ''')
                elif table == 'twin_relationships':
                    self.cursor.execute('''
                        CREATE TABLE twin_relationships (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            twin_id TEXT NOT NULL UNIQUE,
                            aasx_filename TEXT NOT NULL,
                            project_id TEXT NOT NULL,
                            aas_id TEXT,
                            twin_name TEXT,
                            twin_type TEXT,
                            status TEXT DEFAULT 'active',
                            metadata TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            data_points INTEGER,
                            FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
                        )
                    ''')
                elif table == 'twin_configurations':
                    self.cursor.execute('''
                        CREATE TABLE twin_configurations (
                            twin_id TEXT PRIMARY KEY,
                            twin_name TEXT NOT NULL,
                            description TEXT,
                            twin_type TEXT,
                            version TEXT,
                            owner TEXT,
                            configuration_data TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                elif table == 'twin_events':
                    self.cursor.execute('''
                        CREATE TABLE twin_events (
                            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            twin_id TEXT NOT NULL,
                            event_type TEXT NOT NULL,
                            event_message TEXT,
                            severity TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            user TEXT
                        )
                    ''')
                elif table == 'twin_health':
                    self.cursor.execute('''
                        CREATE TABLE twin_health (
                            twin_id TEXT PRIMARY KEY,
                            overall_health REAL DEFAULT 100.0,
                            operational_health REAL DEFAULT 100.0,
                            performance_health REAL DEFAULT 100.0,
                            issues TEXT,
                            last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            health_data TEXT
                        )
                    ''')
                elif table == 'sync_history':
                    self.cursor.execute('''
                        CREATE TABLE sync_history (
                            sync_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            twin_id TEXT NOT NULL,
                            sync_type TEXT NOT NULL,
                            sync_status TEXT NOT NULL,
                            sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            sync_details TEXT
                        )
                    ''')
            
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            raise DatabaseManagerError(f"Failed to create missing tables: {e}")
    
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
            
            # Database-only approach - no JSON files needed
            
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
            # Database-only approach - no JSON files needed
            
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
            
            # Get column names
            columns = [description[0] for description in self.cursor.description]
            
            files = []
            for row in self.cursor.fetchall():
                # Create dictionary with column names as keys
                file_dict = dict(zip(columns, row))
                files.append(file_dict)
            
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
                        result_id, file_id, project_id, processing_type, status, result_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()), file_id, project_id, "etl", status, json.dumps(result)
                ))
            
            self.conn.commit()
            # Database-only approach - no JSON files needed
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
        """Sync all projects with disk and return summary"""
        try:
            all_projects = self.list_projects()
            results = {}
            total_files_synced = 0
            total_files_added = 0
            total_files_removed = 0
            
            for project in all_projects:
                project_id = project['project_id']
                result = self.sync_project_with_disk(project_id)
                results[project_id] = result
                total_files_synced += result.get('files_synced', 0)
                total_files_added += result.get('files_added', 0)
                total_files_removed += result.get('files_removed', 0)
            
            return {
                'success': True,
                'projects_synced': len(all_projects),
                'total_files_synced': total_files_synced,
                'total_files_added': total_files_added,
                'total_files_removed': total_files_removed,
                'project_results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'projects_synced': 0,
                'total_files_synced': 0,
                'total_files_added': 0,
                'total_files_removed': 0,
                'project_results': {}
            }

    # ==================== TWIN MANAGEMENT ====================
    
    def register_digital_twin(self, project_id: str, file_id: str, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a digital twin for a processed AASX file"""
        try:
            # Get file info
            file_info = self.get_file_info(project_id, file_id)
            if not file_info:
                return {'success': False, 'error': 'File not found'}
            
            # Check if twin already exists for this specific project and file
            existing_twin = self.get_twin_by_project_and_aasx(project_id, file_info['filename'])
            if existing_twin:
                return {'success': False, 'error': 'Twin already exists for this file in this project'}
            
            # Get project name for twin ID
            project_metadata = self.get_project_metadata(project_id)
            project_name = project_metadata.get('name', 'Unknown_Project').replace(' ', '_').replace('-', '_')
            
            # Generate human-readable twin ID: DT-{project_name}-{filename_without_extension}
            filename_without_ext = file_info['filename'].replace('.aasx', '')
            twin_id = f"DT-{project_name}-{filename_without_ext}"
            
            # Prepare twin data
            twin_record = {
                'twin_id': twin_id,
                'aasx_filename': file_info['filename'],
                'project_id': project_id,
                'aas_id': twin_data.get('aas_id'),
                'twin_name': twin_data.get('twin_name', f"Digital Twin - {project_name} - {filename_without_ext}"),
                'twin_type': twin_data.get('twin_type', 'aasx'),
                'status': 'active',
                'metadata': json.dumps(twin_data.get('metadata', {})),
                'data_points': twin_data.get('data_points', 0)
            }
            
            # Insert twin record
            self.cursor.execute("""
                INSERT INTO twin_relationships (
                    twin_id, aasx_filename, project_id, aas_id, twin_name, 
                    twin_type, status, metadata, data_points
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                twin_record['twin_id'], twin_record['aasx_filename'], 
                twin_record['project_id'], twin_record['aas_id'], 
                twin_record['twin_name'], twin_record['twin_type'], 
                twin_record['status'], twin_record['metadata'], 
                twin_record['data_points']
            ))
            
            self.conn.commit()
            
            return {
                'success': True,
                'twin_id': twin_id,
                'twin_name': twin_record['twin_name'],
                'aasx_filename': twin_record['aasx_filename'],
                'status': twin_record['status']
            }
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def update_digital_twin(self, project_id: str, file_id: str, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing digital twin with new data"""
        try:
            # Get file info
            file_info = self.get_file_info(project_id, file_id)
            if not file_info:
                return {'success': False, 'error': 'File not found'}
            
            # Find existing twin
            existing_twin = self.get_twin_by_aasx(file_info['filename'])
            if not existing_twin:
                return {'success': False, 'error': 'Twin not found for this file'}
            
            twin_id = existing_twin['twin_id']
            
            # Update twin data
            self.cursor.execute("""
                UPDATE twin_relationships 
                SET aas_id = ?, twin_name = ?, twin_type = ?, 
                    metadata = ?, data_points = ?, last_updated = CURRENT_TIMESTAMP
                WHERE twin_id = ?
            """, (
                twin_data.get('aas_id'),
                twin_data.get('twin_name', existing_twin['twin_name']),
                twin_data.get('twin_type', existing_twin['twin_type']),
                json.dumps(twin_data.get('metadata', {})),
                twin_data.get('data_points', existing_twin['data_points']),
                twin_id
            ))
            
            self.conn.commit()
            
            # Log the update event
            self.log_twin_event(
                twin_id, 
                'twin_updated', 
                f'Twin updated with AI/RAG insights. Data points: {twin_data.get("data_points", 0)}', 
                'info'
            )
            
            return {
                'success': True,
                'twin_id': twin_id,
                'twin_name': twin_data.get('twin_name', existing_twin['twin_name']),
                'aasx_filename': existing_twin['aasx_filename'],
                'status': 'updated'
            }
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def update_twin_status_to_orphaned(self, filename: str, project_id: str) -> Dict[str, Any]:
        """Update twin status to orphaned when file output is missing"""
        try:
            # Find twin by filename and project
            self.cursor.execute('''
                SELECT twin_id, twin_name FROM twin_relationships 
                WHERE aasx_filename = ? AND project_id = ?
            ''', (filename, project_id))
            
            twin = self.cursor.fetchone()
            if not twin:
                return {'success': False, 'error': 'Twin not found'}
            
            twin_id, twin_name = twin
            
            # Update twin status to orphaned
            self.cursor.execute('''
                UPDATE twin_relationships 
                SET status = 'orphaned', last_sync = CURRENT_TIMESTAMP
                WHERE twin_id = ?
            ''', (twin_id,))
            
            # Update health to reflect orphaned status
            self.cursor.execute('''
                UPDATE twin_health 
                SET overall_health = 0.0, operational_health = 0.0, 
                    issues = ?, last_check = CURRENT_TIMESTAMP
                WHERE twin_id = ?
            ''', (json.dumps(['Twin orphaned due to missing output files']), twin_id))
            
            # Log orphaned event
            self.cursor.execute('''
                INSERT INTO twin_events 
                (twin_id, event_type, event_message, severity, user)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                twin_id, 'twin_orphaned', 
                f'Twin {twin_name} orphaned due to missing output for {filename}',
                'warning', 'system'
            ))
            
            self.conn.commit()
            
            return {
                'success': True,
                'twin_id': twin_id,
                'twin_name': twin_name,
                'message': f'Twin {twin_name} marked as orphaned'
            }
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def update_twin_status_to_active(self, filename: str, project_id: str) -> Dict[str, Any]:
        """Update twin status to active when file output is restored"""
        try:
            # Find twin by filename and project
            self.cursor.execute('''
                SELECT twin_id, twin_name FROM twin_relationships 
                WHERE aasx_filename = ? AND project_id = ?
            ''', (filename, project_id))
            
            twin = self.cursor.fetchone()
            if not twin:
                return {'success': False, 'error': 'Twin not found'}
            
            twin_id, twin_name = twin
            
            # Update twin status to active
            self.cursor.execute('''
                UPDATE twin_relationships 
                SET status = 'active', last_sync = CURRENT_TIMESTAMP
                WHERE twin_id = ?
            ''', (twin_id,))
            
            # Reset health to active status
            self.cursor.execute('''
                UPDATE twin_health 
                SET overall_health = 100.0, operational_health = 100.0, 
                    issues = NULL, last_check = CURRENT_TIMESTAMP
                WHERE twin_id = ?
            ''', (twin_id,))
            
            # Log reactivation event
            self.cursor.execute('''
                INSERT INTO twin_events 
                (twin_id, event_type, event_message, severity, user)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                twin_id, 'twin_reactivated', 
                f'Twin {twin_name} reactivated - output files restored for {filename}',
                'info', 'system'
            ))
            
            self.conn.commit()
            
            return {
                'success': True,
                'twin_id': twin_id,
                'twin_name': twin_name,
                'message': f'Twin {twin_name} reactivated successfully'
            }
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_all_registered_twins(self) -> List[Dict[str, Any]]:
        """Get all registered twins from the database"""
        try:
            self.cursor.execute("""
                SELECT * FROM twin_relationships 
                ORDER BY created_at DESC
            """)
            rows = self.cursor.fetchall()
            
            twins = []
            for row in rows:
                twin = dict(row)
                # Parse metadata if it exists
                if twin.get('metadata'):
                    try:
                        twin['metadata'] = json.loads(twin['metadata'])
                    except json.JSONDecodeError:
                        twin['metadata'] = {}
                twins.append(twin)
            
            return twins
            
        except Exception as e:
            print(f"Error getting registered twins: {e}")
            return []
    
    def get_twin_statistics(self) -> Dict[str, Any]:
        """Get comprehensive twin statistics"""
        try:
            # Total twins
            self.cursor.execute("SELECT COUNT(*) FROM twin_relationships")
            total_twins = self.cursor.fetchone()[0]
            
            # Active twins
            self.cursor.execute("SELECT COUNT(*) FROM twin_relationships WHERE status = 'active'")
            active_twins = self.cursor.fetchone()[0]
            
            # Orphaned twins
            self.cursor.execute("SELECT COUNT(*) FROM twin_relationships WHERE status = 'orphaned'")
            orphaned_twins = self.cursor.fetchone()[0]
            
            # Twins by type
            self.cursor.execute('''
                SELECT twin_type, COUNT(*) as count 
                FROM twin_relationships 
                GROUP BY twin_type
            ''')
            twins_by_type = dict(self.cursor.fetchall())
            
            # Health statistics
            self.cursor.execute('''
                SELECT 
                    AVG(overall_health) as avg_health,
                    COUNT(CASE WHEN overall_health < 50 THEN 1 END) as unhealthy_count,
                    COUNT(CASE WHEN overall_health >= 50 THEN 1 END) as healthy_count
                FROM twin_health
            ''')
            health_stats = self.cursor.fetchone()
            
            return {
                'total_twins': total_twins,
                'active_twins': active_twins,
                'orphaned_twins': orphaned_twins,
                'twins_by_type': twins_by_type,
                'health_stats': {
                    'average_health': health_stats[0] or 0,
                    'unhealthy_count': health_stats[1] or 0,
                    'healthy_count': health_stats[2] or 0
                }
            }
            
        except Exception as e:
            return {
                'total_twins': 0,
                'active_twins': 0,
                'orphaned_twins': 0,
                'twins_by_type': {},
                'health_stats': {'average_health': 0, 'unhealthy_count': 0, 'healthy_count': 0},
                'error': str(e)
            }
    
    def reset_orphaned_twins(self) -> Dict[str, Any]:
        """Reset all orphaned twins to active status if their files are completed"""
        try:
            # Find orphaned twins with completed files
            self.cursor.execute('''
                SELECT t.twin_id, t.twin_name, t.aasx_filename, t.project_id
                FROM twin_relationships t
                JOIN project_files f ON t.project_id = f.project_id AND t.aasx_filename = f.filename
                WHERE t.status = 'orphaned' AND f.status = 'completed'
            ''')
            
            orphaned_twins = self.cursor.fetchall()
            reset_count = 0
            
            for twin in orphaned_twins:
                twin_id, twin_name, filename, project_id = twin
                
                # Reset twin status to active
                self.cursor.execute('''
                    UPDATE twin_relationships 
                    SET status = 'active', last_sync = CURRENT_TIMESTAMP
                    WHERE twin_id = ?
                ''', (twin_id,))
                
                # Reset health
                self.cursor.execute('''
                    UPDATE twin_health 
                    SET overall_health = 100.0, operational_health = 100.0, 
                        issues = NULL, last_check = CURRENT_TIMESTAMP
                    WHERE twin_id = ?
                ''', (twin_id,))
                
                # Log reset event
                self.cursor.execute('''
                    INSERT INTO twin_events 
                    (twin_id, event_type, event_message, severity, user)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    twin_id, 'twin_reactivated', 
                    f'Twin {twin_name} reactivated - output files restored',
                    'info', 'system'
                ))
                
                reset_count += 1
            
            self.conn.commit()
            
            return {
                'success': True,
                'reset_count': reset_count,
                'message': f'Reactivated {reset_count} orphaned twins'
            }
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_twin_by_aasx(self, aasx_filename: str) -> Optional[Dict[str, Any]]:
        """Get twin information by AASX filename"""
        try:
            self.cursor.execute('''
                SELECT t.*, tc.description, tc.version, tc.owner, tc.configuration_data
                FROM twin_relationships t
                LEFT JOIN twin_configurations tc ON t.twin_id = tc.twin_id
                WHERE t.aasx_filename = ?
            ''', (aasx_filename,))
            
            row = self.cursor.fetchone()
            if row:
                twin_dict = dict(row)
                # Parse JSON fields
                if twin_dict.get('metadata'):
                    twin_dict['metadata'] = json.loads(twin_dict['metadata'])
                if twin_dict.get('configuration_data'):
                    twin_dict['configuration_data'] = json.loads(twin_dict['configuration_data'])
                return twin_dict
            return None
            
        except Exception as e:
            print(f"Error getting twin by AASX: {e}")
            return None
    
    def get_twin_by_project_and_aasx(self, project_id: str, aasx_filename: str) -> Optional[Dict[str, Any]]:
        """Get twin by project ID and AASX filename"""
        try:
            self.cursor.execute('''
                SELECT t.*, tc.description, tc.version, tc.owner, tc.configuration_data
                FROM twin_relationships t
                LEFT JOIN twin_configurations tc ON t.twin_id = tc.twin_id
                WHERE t.project_id = ? AND t.aasx_filename = ?
            ''', (project_id, aasx_filename))
            
            row = self.cursor.fetchone()
            if row:
                twin_dict = dict(row)
                # Parse JSON fields
                if twin_dict.get('metadata'):
                    twin_dict['metadata'] = json.loads(twin_dict['metadata'])
                if twin_dict.get('configuration_data'):
                    twin_dict['configuration_data'] = json.loads(twin_dict['configuration_data'])
                return twin_dict
            return None
            
        except Exception as e:
            print(f"Error getting twin by project and AASX filename: {e}")
            return None
    
    def get_sync_status(self, twin_id: str) -> Dict[str, Any]:
        """Get sync status and history for a twin"""
        try:
            # Get twin basic info
            self.cursor.execute('''
                SELECT twin_id, twin_name, status, last_sync, data_points
                FROM twin_relationships 
                WHERE twin_id = ?
            ''', (twin_id,))
            
            twin = self.cursor.fetchone()
            if not twin:
                return {'success': False, 'error': 'Twin not found'}
            
            # Get recent sync history
            self.cursor.execute('''
                SELECT sync_type, sync_status, sync_timestamp, details
                FROM sync_history 
                WHERE twin_id = ?
                ORDER BY sync_timestamp DESC
                LIMIT 10
            ''', (twin_id,))
            
            sync_history = []
            for row in self.cursor.fetchall():
                sync_history.append({
                    'sync_type': row[0],
                    'sync_status': row[1],
                    'sync_timestamp': row[2],
                    'details': row[3]
                })
            
            return {
                'success': True,
                'twin_id': twin[0],
                'twin_name': twin[1],
                'status': twin[2],
                'last_sync': twin[3],
                'data_points': twin[4],
                'sync_history': sync_history
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def discover_processed_aasx_files(self) -> List[Dict[str, Any]]:
        """Discover AASX files that have been processed (status = 'completed')"""
        try:
            self.cursor.execute('''
                SELECT f.file_id, f.filename, f.project_id, f.upload_date, f.size,
                       p.name as project_name
                FROM project_files f
                JOIN projects p ON f.project_id = p.project_id
                WHERE f.status = 'completed' AND (f.file_type = '.aasx' OR f.filename LIKE '%.aasx')
                ORDER BY f.upload_date DESC
            ''')
            
            files = []
            for row in self.cursor.fetchall():
                files.append({
                    'file_id': row[0],
                    'filename': row[1],
                    'project_id': row[2],
                    'upload_date': row[3],
                    'size': row[4],
                    'project_name': row[5]
                })
            
            return files
            
        except Exception as e:
            print(f"Error discovering processed AASX files: {e}")
            return []
    
    def get_twin_configuration(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get twin configuration"""
        try:
            self.cursor.execute('''
                SELECT * FROM twin_configurations WHERE twin_id = ?
            ''', (twin_id,))
            
            row = self.cursor.fetchone()
            if row:
                config_dict = dict(row)
                # Parse JSON fields
                if config_dict.get('tags'):
                    config_dict['tags'] = json.loads(config_dict['tags'])
                if config_dict.get('settings'):
                    config_dict['settings'] = json.loads(config_dict['settings'])
                return config_dict
            return None
            
        except Exception as e:
            print(f"Error getting twin configuration: {e}")
            return None
    
    def update_twin_configuration(self, twin_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update twin configuration"""
        try:
            # Check if twin exists
            self.cursor.execute('SELECT twin_id FROM twin_relationships WHERE twin_id = ?', (twin_id,))
            if not self.cursor.fetchone():
                return {'success': False, 'error': 'Twin not found'}
            
            # Update configuration
            self.cursor.execute('''
                UPDATE twin_configurations 
                SET twin_name = ?, description = ?, twin_type = ?, version = ?, 
                    owner = ?, tags = ?, settings = ?, updated_at = ?
                WHERE twin_id = ?
            ''', (
                config.get('twin_name'),
                config.get('description'),
                config.get('twin_type'),
                config.get('version'),
                config.get('owner'),
                json.dumps(config.get('tags', [])),
                json.dumps(config.get('settings', {})),
                datetime.now().isoformat(),
                twin_id
            ))
            
            self.conn.commit()
            
            return {'success': True, 'message': 'Twin configuration updated'}
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_twin_health(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get twin health information"""
        try:
            self.cursor.execute('''
                SELECT * FROM twin_health WHERE twin_id = ?
            ''', (twin_id,))
            
            row = self.cursor.fetchone()
            if row:
                health_dict = dict(row)
                # Parse JSON fields
                if health_dict.get('issues'):
                    health_dict['issues'] = json.loads(health_dict['issues'])
                if health_dict.get('recommendations'):
                    health_dict['recommendations'] = json.loads(health_dict['recommendations'])
                return health_dict
            return None
            
        except Exception as e:
            print(f"Error getting twin health: {e}")
            return None
    
    def update_twin_health(self, twin_id: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update twin health information"""
        try:
            # Check if twin exists
            self.cursor.execute('SELECT twin_id FROM twin_relationships WHERE twin_id = ?', (twin_id,))
            if not self.cursor.fetchone():
                return {'success': False, 'error': 'Twin not found'}
            
            # Update health
            self.cursor.execute('''
                UPDATE twin_health 
                SET overall_health = ?, performance_health = ?, connectivity_health = ?,
                    data_health = ?, operational_health = ?, issues = ?, 
                    recommendations = ?, last_check = ?
                WHERE twin_id = ?
            ''', (
                health_data.get('overall_health', 100.0),
                health_data.get('performance_health', 100.0),
                health_data.get('connectivity_health', 100.0),
                health_data.get('data_health', 100.0),
                health_data.get('operational_health', 100.0),
                json.dumps(health_data.get('issues', [])),
                json.dumps(health_data.get('recommendations', [])),
                datetime.now().isoformat(),
                twin_id
            ))
            
            self.conn.commit()
            
            return {'success': True, 'message': 'Twin health updated'}
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_twin_events(self, twin_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get twin events"""
        try:
            self.cursor.execute('''
                SELECT event_type, event_message, severity, timestamp, user
                FROM twin_events 
                WHERE twin_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (twin_id, limit))
            
            events = []
            for row in self.cursor.fetchall():
                event_dict = {
                    'event_type': row[0],
                    'event_message': row[1],
                    'severity': row[2],
                    'timestamp': row[3],
                    'user': row[4],
                    'metadata': {}  # Default empty metadata since column doesn't exist
                }
                events.append(event_dict)
            
            return events
            
        except Exception as e:
            print(f"Error getting twin events: {e}")
            return []
    
    def log_twin_event(self, twin_id: str, event_type: str, message: str, severity: str, user: str = "system") -> Dict[str, Any]:
        """Log a twin event"""
        try:
            self.cursor.execute('''
                INSERT INTO twin_events 
                (twin_id, event_type, event_message, severity, user, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (twin_id, event_type, message, severity, user, datetime.now().isoformat()))
            
            self.conn.commit()
            return {'success': True, 'message': 'Event logged successfully'}
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}

    def log_sync_status(self, twin_id: str, status: str, data: Optional[Dict[str, Any]] = None):
        """Log sync status to database"""
        try:
            # Use existing twin event logging method
            self.log_twin_event(
                twin_id=twin_id,
                event_type="sync_status",
                message=f"Sync status: {status}",
                severity="info",
                user="system"
            )
            
        except Exception as e:
            print(f"Error logging sync status: {e}")

    def cleanup_twin_statuses(self) -> Dict[str, Any]:
        """Clean up twin statuses to match actual file processing status"""
        try:
            # Find all twins and check their file status
            self.cursor.execute('''
                SELECT t.twin_id, t.aasx_filename, t.project_id, t.status, f.status as file_status
                FROM twin_relationships t
                LEFT JOIN project_files f ON t.project_id = f.project_id AND t.aasx_filename = f.filename
            ''')
            
            twins = self.cursor.fetchall()
            updated_count = 0
            orphaned_count = 0
            
            for twin in twins:
                twin_id, filename, project_id, twin_status, file_status = twin
                
                # If file doesn't exist or is not completed, orphan the twin
                if not file_status or file_status != 'completed':
                    if twin_status == 'active':
                        self.cursor.execute('''
                            UPDATE twin_relationships 
                            SET status = 'orphaned', last_sync = CURRENT_TIMESTAMP
                            WHERE twin_id = ?
                        ''', (twin_id,))
                        
                        # Log the orphan event
                        self.cursor.execute('''
                            INSERT INTO twin_events 
                            (twin_id, event_type, event_message, severity, user, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            twin_id, 'twin_orphaned', 
                            f'Twin orphaned - file {filename} status: {file_status or "not found"}',
                            'warning', 'system', datetime.now().isoformat()
                        ))
                        
                        orphaned_count += 1
                        updated_count += 1
                
                # If file is completed but twin is orphaned, activate it
                elif file_status == 'completed' and twin_status == 'orphaned':
                    self.cursor.execute('''
                        UPDATE twin_relationships 
                        SET status = 'active', last_sync = CURRENT_TIMESTAMP
                        WHERE twin_id = ?
                    ''', (twin_id,))
                    
                    # Log the reactivation event
                    self.cursor.execute('''
                        INSERT INTO twin_events 
                        (twin_id, event_type, event_message, severity, user, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        twin_id, 'twin_reactivated', 
                        f'Twin reactivated - file {filename} is completed',
                        'info', 'system', datetime.now().isoformat()
                    ))
                    
                    updated_count += 1
            
            self.conn.commit()
            
            return {
                'success': True,
                'message': f'Cleanup completed: {updated_count} twins updated, {orphaned_count} orphaned',
                'updated_count': updated_count,
                'orphaned_count': orphaned_count
            }
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}

    def remove_duplicate_twins(self) -> Dict[str, Any]:
        """Remove duplicate twins for the same file in the same project"""
        try:
            # Find duplicate twins (same filename, same project)
            self.cursor.execute('''
                SELECT aasx_filename, project_id, COUNT(*) as count
                FROM twin_relationships
                GROUP BY aasx_filename, project_id
                HAVING COUNT(*) > 1
            ''')
            
            duplicates = self.cursor.fetchall()
            removed_count = 0
            
            for filename, project_id, count in duplicates:
                # Keep the first active twin, remove the rest
                self.cursor.execute('''
                    SELECT twin_id, status FROM twin_relationships
                    WHERE aasx_filename = ? AND project_id = ?
                    ORDER BY 
                        CASE WHEN status = 'active' THEN 1 ELSE 2 END,
                        twin_id
                ''', (filename, project_id))
                
                twins = self.cursor.fetchall()
                
                # Keep the first one, remove the rest
                for i, (twin_id, status) in enumerate(twins):
                    if i > 0:  # Remove duplicates (keep first)
                        # Remove twin and related data
                        self.cursor.execute('DELETE FROM twin_relationships WHERE twin_id = ?', (twin_id,))
                        self.cursor.execute('DELETE FROM twin_configurations WHERE twin_id = ?', (twin_id,))
                        self.cursor.execute('DELETE FROM twin_health WHERE twin_id = ?', (twin_id,))
                        self.cursor.execute('DELETE FROM twin_events WHERE twin_id = ?', (twin_id,))
                        
                        removed_count += 1
            
            self.conn.commit()
            
            return {
                'success': True,
                'message': f'Removed {removed_count} duplicate twins',
                'removed_count': removed_count
            }
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 