"""
File Repository
==============

Data access layer for files in the AAS Data Modeling framework.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from ..database.base_manager import BaseDatabaseManager
from ..models.file import File
from .base_repository import BaseRepository

class FileRepository(BaseRepository[File]):
    """Repository for file operations."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        super().__init__(db_manager, File)
    
    def _get_table_name(self) -> str:
        return "files"
    
    def _get_columns(self) -> List[str]:
        return [
            "file_id", "filename", "original_filename", "project_id", "filepath",
            "size", "description", "status", "file_type", "file_type_description",
            "user_id", "upload_date", "created_at", "updated_at"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for files table."""
        return "file_id"
    
    def get_by_project(self, project_id: str) -> List[File]:
        """Get all files in a project."""
        query = "SELECT * FROM files WHERE project_id = ?"
        results = self.db_manager.execute_query(query, (project_id,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_by_status(self, status: str) -> List[File]:
        """Get files by status."""
        query = "SELECT * FROM files WHERE status = ?"
        results = self.db_manager.execute_query(query, (status,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_by_user(self, user_id: str) -> List[File]:
        """Get files by user."""
        query = "SELECT * FROM files WHERE user_id = ?"
        results = self.db_manager.execute_query(query, (user_id,))
        return [self.model_class.from_dict(row) for row in results]
    
    def find_by_original_filename(self, original_filename: str, project_id: str) -> Optional[File]:
        """Find a file by its original filename in a project."""
        query = "SELECT * FROM files WHERE project_id = ? AND original_filename = ?"
        results = self.db_manager.execute_query(query, (project_id, original_filename))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def search_files(self, search_term: str) -> List[File]:
        """Search files by filename or description."""
        query = """
            SELECT * FROM files 
            WHERE filename LIKE ? OR original_filename LIKE ? OR description LIKE ?
        """
        search_pattern = f"%{search_term}%"
        results = self.db_manager.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_file_statistics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get file statistics."""
        if project_id:
            query = """
                SELECT 
                    COUNT(*) as total_files,
                    COUNT(CASE WHEN status = 'processed' THEN 1 END) as processed_files,
                    COUNT(CASE WHEN status = 'not_processed' THEN 1 END) as pending_files,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_files,
                    SUM(size) as total_size
                FROM files 
                WHERE project_id = ?
            """
            results = self.db_manager.execute_query(query, (project_id,))
        else:
            query = """
                SELECT 
                    COUNT(*) as total_files,
                    COUNT(CASE WHEN status = 'processed' THEN 1 END) as processed_files,
                    COUNT(CASE WHEN status = 'not_processed' THEN 1 END) as pending_files,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_files,
                    SUM(size) as total_size
                FROM files
            """
            results = self.db_manager.execute_query(query)
        
        if results:
            return {
                "total_files": results[0]["total_files"] or 0,
                "processed_files": results[0]["processed_files"] or 0,
                "pending_files": results[0]["pending_files"] or 0,
                "failed_files": results[0]["failed_files"] or 0,
                "total_size": results[0]["total_size"] or 0
            }
        return {
            "total_files": 0,
            "processed_files": 0,
            "pending_files": 0,
            "failed_files": 0,
            "total_size": 0
        }
    
    def update_status(self, file_id: str, status: str) -> bool:
        """Update file status."""
        query = "UPDATE files SET status = ?, updated_at = datetime('now') WHERE file_id = ?"
        try:
            affected_rows = self.db_manager.execute_update(query, (status, file_id))
            return affected_rows > 0
        except Exception:
            return False
    
    def get_file_trace_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get complete trace information for a file."""
        query = """
            SELECT 
                f.*,
                p.name as project_name,
                uc.name as use_case_name,
                uc.category as use_case_category
            FROM files f
            JOIN projects p ON f.project_id = p.project_id
            JOIN project_use_case_links puc ON p.project_id = puc.project_id
            JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
            WHERE f.file_id = ?
        """
        results = self.db_manager.execute_query(query, (file_id,))
        if results:
            return results[0]
        return None
    
    def get_use_case_by_name(self, use_case_name: str) -> Optional[Dict[str, Any]]:
        """Get use case by name."""
        query = "SELECT * FROM use_cases WHERE name = ?"
        results = self.db_manager.execute_query(query, (use_case_name,))
        if results:
            return results[0]
        return None
    
    def find_by_name_and_project(self, filename: str, project_id: str) -> Optional[Dict[str, Any]]:
        """Find a file by filename in a specific project."""
        query = "SELECT * FROM files WHERE project_id = ? AND filename = ?"
        results = self.db_manager.execute_query(query, (project_id, filename))
        if results:
            return results[0]
        return None
    
    def get_by_project_id(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all files in a project as dictionaries."""
        query = "SELECT * FROM files WHERE project_id = ?"
        results = self.db_manager.execute_query(query, (project_id,))
        return results 