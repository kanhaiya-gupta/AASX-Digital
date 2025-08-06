"""
Use Case Repository

This module provides data access layer for use case management
with database integration capabilities.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json


class UseCaseRepository:
    """
    Repository for managing use case data persistence.
    
    This class provides data access methods for use cases,
    including CRUD operations and query capabilities.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the use case repository.
        
        Args:
            connection_string: Database connection string (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.connection_string = connection_string
        self._use_cases: Dict[str, Dict[str, Any]] = {}  # In-memory storage for now
        
    def save_use_case(self, use_case_data: Dict[str, Any]) -> bool:
        """
        Save a use case to the repository.
        
        Args:
            use_case_data: Use case data to save
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            use_case_id = use_case_data.get('use_case_id')
            if not use_case_id:
                self.logger.error("Use case data missing use_case_id")
                return False
            
            # Add metadata
            use_case_data['created_at'] = use_case_data.get('created_at', datetime.now().isoformat())
            use_case_data['updated_at'] = datetime.now().isoformat()
            
            self._use_cases[use_case_id] = use_case_data.copy()
            self.logger.info(f"Saved use case: {use_case_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving use case: {str(e)}")
            return False
    
    def get_use_case(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a use case by ID.
        
        Args:
            use_case_id: Use case identifier
            
        Returns:
            Use case data or None if not found
        """
        return self._use_cases.get(use_case_id)
    
    def get_use_cases_by_physics_type(self, physics_type_id: str) -> List[Dict[str, Any]]:
        """
        Get use cases by physics type.
        
        Args:
            physics_type_id: Physics type identifier
            
        Returns:
            List of use cases for the specified physics type
        """
        return [
            use_case for use_case in self._use_cases.values()
            if use_case.get('physics_type_id') == physics_type_id
        ]
    
    def get_use_cases_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get use cases by status.
        
        Args:
            status: Use case status
            
        Returns:
            List of use cases with the specified status
        """
        return [
            use_case for use_case in self._use_cases.values()
            if use_case.get('status') == status
        ]
    
    def get_all_use_cases(self) -> List[Dict[str, Any]]:
        """
        Get all use cases.
        
        Returns:
            List of all use cases
        """
        return list(self._use_cases.values())
    
    def update_use_case(self, use_case_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a use case.
        
        Args:
            use_case_id: Use case identifier
            updates: Updates to apply
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            if use_case_id not in self._use_cases:
                self.logger.error(f"Use case not found: {use_case_id}")
                return False
            
            # Update the use case
            self._use_cases[use_case_id].update(updates)
            self._use_cases[use_case_id]['updated_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Updated use case: {use_case_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating use case: {str(e)}")
            return False
    
    def delete_use_case(self, use_case_id: str) -> bool:
        """
        Delete a use case.
        
        Args:
            use_case_id: Use case identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if use_case_id in self._use_cases:
            del self._use_cases[use_case_id]
            self.logger.info(f"Deleted use case: {use_case_id}")
            return True
        return False
    
    def search_use_cases(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search use cases based on criteria.
        
        Args:
            query: Search criteria
            
        Returns:
            List of matching use cases
        """
        results = []
        
        for use_case in self._use_cases.values():
            match = True
            
            for key, value in query.items():
                if key not in use_case or use_case[key] != value:
                    match = False
                    break
            
            if match:
                results.append(use_case)
        
        return results
    
    def get_use_case_statistics(self) -> Dict[str, Any]:
        """
        Get use case statistics.
        
        Returns:
            Dictionary containing use case statistics
        """
        total_count = len(self._use_cases)
        status_counts = {}
        physics_type_counts = {}
        
        for use_case in self._use_cases.values():
            status = use_case.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            physics_type = use_case.get('physics_type_id', 'unknown')
            physics_type_counts[physics_type] = physics_type_counts.get(physics_type, 0) + 1
        
        return {
            'total_count': total_count,
            'status_counts': status_counts,
            'physics_type_counts': physics_type_counts
        }
    
    def export_use_cases(self, use_case_ids: Optional[List[str]] = None) -> str:
        """
        Export use cases to JSON format.
        
        Args:
            use_case_ids: List of use case IDs to export (None for all)
            
        Returns:
            JSON string representation
        """
        if use_case_ids is None:
            data_to_export = self._use_cases
        else:
            data_to_export = {
                use_case_id: use_case_data
                for use_case_id, use_case_data in self._use_cases.items()
                if use_case_id in use_case_ids
            }
        
        return json.dumps(data_to_export, indent=2)
    
    def import_use_cases(self, use_cases_json: str) -> bool:
        """
        Import use cases from JSON format.
        
        Args:
            use_cases_json: JSON string representation
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            use_cases_data = json.loads(use_cases_json)
            
            for use_case_id, use_case_data in use_cases_data.items():
                self.save_use_case(use_case_data)
            
            self.logger.info("Successfully imported use cases")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing use cases: {str(e)}")
            return False 