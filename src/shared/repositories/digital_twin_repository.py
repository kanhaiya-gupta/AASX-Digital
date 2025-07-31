"""
Digital Twin Repository
======================

Data access layer for digital twins in the AAS Data Modeling framework.
"""

from typing import List, Optional, Dict, Any
from ..database.base_manager import BaseDatabaseManager
from ..models.digital_twin import DigitalTwin
from .base_repository import BaseRepository

class DigitalTwinRepository(BaseRepository[DigitalTwin]):
    """Repository for digital twin operations."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        super().__init__(db_manager, DigitalTwin)
    
    def _get_table_name(self) -> str:
        return "digital_twins"
    
    def _get_columns(self) -> List[str]:
        return [
            "twin_id", "twin_name", "file_id", "status", "metadata", 
            "created_at", "updated_at"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for digital_twins table."""
        return "twin_id"
    
    def get_by_file_id(self, file_id: str) -> Optional[DigitalTwin]:
        """Get digital twin by file ID."""
        query = "SELECT * FROM digital_twins WHERE file_id = ?"
        results = self.db_manager.execute_query(query, (file_id,))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def get_by_status(self, status: str) -> List[DigitalTwin]:
        """Get digital twins by status."""
        query = "SELECT * FROM digital_twins WHERE status = ?"
        results = self.db_manager.execute_query(query, (status,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_active_twins(self) -> List[DigitalTwin]:
        """Get all active digital twins."""
        query = "SELECT * FROM digital_twins WHERE status = 'active'"
        results = self.db_manager.execute_query(query)
        return [self.model_class.from_dict(row) for row in results]
    
    def search_twins(self, search_term: str) -> List[DigitalTwin]:
        """Search digital twins by name."""
        query = "SELECT * FROM digital_twins WHERE twin_name LIKE ?"
        search_pattern = f"%{search_term}%"
        results = self.db_manager.execute_query(query, (search_pattern,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_twin_with_file_info(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin with complete file information."""
        query = """
            SELECT 
                dt.*,
                f.filename,
                f.original_filename,
                f.project_id,
                f.status as file_status,
                p.name as project_name,
                uc.name as use_case_name
            FROM digital_twins dt
            JOIN files f ON dt.file_id = f.file_id
            LEFT JOIN projects p ON f.project_id = p.project_id
            LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
            LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
            WHERE dt.twin_id = ?
        """
        results = self.db_manager.execute_query(query, (twin_id,))
        if results:
            return results[0]
        return None
    
    def update_status(self, twin_id: str, status: str) -> bool:
        """Update digital twin status."""
        query = "UPDATE digital_twins SET status = ?, updated_at = datetime('now') WHERE twin_id = ?"
        try:
            affected_rows = self.db_manager.execute_update(query, (status, twin_id))
            return affected_rows > 0
        except Exception:
            return False
    
    def get_twin_statistics(self) -> Dict[str, Any]:
        """Get digital twin statistics."""
        query = """
            SELECT 
                COUNT(*) as total_twins,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_twins,
                COUNT(CASE WHEN status = 'inactive' THEN 1 END) as inactive_twins,
                COUNT(CASE WHEN status = 'orphaned' THEN 1 END) as orphaned_twins
            FROM digital_twins
        """
        results = self.db_manager.execute_query(query)
        
        if results:
            return {
                "total_twins": results[0]["total_twins"] or 0,
                "active_twins": results[0]["active_twins"] or 0,
                "inactive_twins": results[0]["inactive_twins"] or 0,
                "orphaned_twins": results[0]["orphaned_twins"] or 0
            }
        return {
            "total_twins": 0,
            "active_twins": 0,
            "inactive_twins": 0,
            "orphaned_twins": 0
        }
    
    def check_twin_exists(self, file_id: str) -> bool:
        """Check if a digital twin exists for a file."""
        query = "SELECT COUNT(*) as count FROM digital_twins WHERE file_id = ?"
        results = self.db_manager.execute_query(query, (file_id,))
        return results[0]["count"] > 0 if results else False
    
    def create(self, project_id: str, file_id: str, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new digital twin for a file."""
        import json
        
        # twin_id should be the same as file_id for 1:1 relationship
        twin_id = file_id
        
        # Get file info to build proper twin name: "Use Case - Project Name - Filename"
        file_info = self._get_file_info(file_id)
        if file_info:
            use_case_name = file_info.get('use_case_name', 'Unknown Use Case')
            project_name = file_info.get('project_name', 'Unknown Project')
            filename = file_info.get('filename', 'Unknown File')
            twin_name = f"{use_case_name} - {project_name} - {filename}"
        else:
            # Fallback if file info not available
            twin_name = twin_data.get('twin_name', f'Digital Twin - {file_id}')
        
        twin_type = twin_data.get('twin_type', 'aasx')
        metadata = json.dumps(twin_data.get('metadata', {}))
        
        query = """
            INSERT INTO digital_twins (twin_id, twin_name, file_id, status, metadata, created_at, updated_at)
            VALUES (?, ?, ?, 'active', ?, datetime('now'), datetime('now'))
        """
        
        try:
            self.db_manager.execute_insert(query, (twin_id, twin_name, file_id, metadata))
            return {
                'twin_id': twin_id,
                'twin_name': twin_name,
                'file_id': file_id,
                'status': 'active',
                'metadata': twin_data.get('metadata', {})
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information with use case and project details for twin naming."""
        query = """
            SELECT 
                f.filename,
                p.name as project_name,
                uc.name as use_case_name
            FROM files f
            LEFT JOIN projects p ON f.project_id = p.project_id
            LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
            LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
            WHERE f.file_id = ?
        """
        results = self.db_manager.execute_query(query, (file_id,))
        if results:
            return results[0]
        return None 