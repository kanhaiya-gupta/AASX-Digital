"""
Use Case Repository
==================

Data access layer for use cases in the AAS Data Modeling framework.
"""

from typing import List, Optional, Dict, Any
from ..database.base_manager import BaseDatabaseManager
from ..models.use_case import UseCase
from .base_repository import BaseRepository

class UseCaseRepository(BaseRepository[UseCase]):
    """Repository for use case operations."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        super().__init__(db_manager, UseCase)
    
    def _get_table_name(self) -> str:
        return "use_cases"
    
    def _get_columns(self) -> List[str]:
        return [
            "use_case_id", "name", "description", "category", "is_active", 
            "metadata", "created_at", "updated_at"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for use_cases table."""
        return "use_case_id"
    
    def get_by_category(self, category: str) -> List[UseCase]:
        """Get use cases by category."""
        query = "SELECT * FROM use_cases WHERE category = ?"
        results = self.db_manager.execute_query(query, (category,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_active_use_cases(self) -> List[UseCase]:
        """Get all active use cases."""
        query = "SELECT * FROM use_cases WHERE is_active = 1"
        results = self.db_manager.execute_query(query)
        return [self.model_class.from_dict(row) for row in results]
    
    def get_by_name(self, name: str) -> Optional[UseCase]:
        """Get use case by name."""
        query = "SELECT * FROM use_cases WHERE name = ?"
        results = self.db_manager.execute_query(query, (name,))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def search_use_cases(self, search_term: str) -> List[UseCase]:
        """Search use cases by name or description."""
        query = """
            SELECT * FROM use_cases 
            WHERE name LIKE ? OR description LIKE ?
        """
        search_pattern = f"%{search_term}%"
        results = self.db_manager.execute_query(query, (search_pattern, search_pattern))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_use_case_statistics(self) -> Dict[str, Any]:
        """Get use case statistics."""
        query = """
            SELECT 
                COUNT(*) as total_use_cases,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_use_cases,
                COUNT(CASE WHEN is_active = 0 THEN 1 END) as inactive_use_cases,
                category,
                COUNT(*) as category_count
            FROM use_cases 
            GROUP BY category
        """
        results = self.db_manager.execute_query(query)
        
        stats = {
            "total_use_cases": 0,
            "active_use_cases": 0,
            "inactive_use_cases": 0,
            "categories": {}
        }
        
        for row in results:
            stats["total_use_cases"] = row["total_use_cases"]
            stats["active_use_cases"] = row["active_use_cases"]
            stats["inactive_use_cases"] = row["inactive_use_cases"]
            if row["category"]:
                stats["categories"][row["category"]] = row["category_count"]
        
        return stats 