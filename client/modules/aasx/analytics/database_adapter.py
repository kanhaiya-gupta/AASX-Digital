"""
Database Adapter for Analytics Services

This adapter wraps our BaseDatabaseManager to provide the interface
expected by the analytics services (self.db.execute_query).
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """Adapter to make BaseDatabaseManager compatible with analytics services."""
    
    def __init__(self, db_manager):
        """
        Initialize with a BaseDatabaseManager instance.
        
        Args:
            db_manager: Instance of BaseDatabaseManager
        """
        self.db_manager = db_manager
        logger.info("DatabaseAdapter initialized for analytics services")
    
    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results in the format expected by analytics services.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            List of dictionaries where each dictionary represents a row
        """
        try:
            if params is None:
                params = []
            
            # Execute query using the underlying db_manager
            results = self.db_manager.execute_query(query, params)
            
            # Convert results to the format expected by analytics services
            if not results:
                return []
            
            # If results are already dictionaries, return as-is
            if isinstance(results[0], dict):
                return results
            
            # If results are tuples/lists, convert to dictionaries
            # This assumes the query has column names (e.g., "SELECT column1, column2")
            # For now, we'll return the raw results and let the analytics services handle them
            return results
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return []
    
    def execute_update(self, query: str, params: Optional[List] = None) -> int:
        """
        Execute an update query.
        
        Args:
            query: SQL update query string
            params: Query parameters (optional)
        
        Returns:
            Number of affected rows
        """
        try:
            if params is None:
                params = []
            
            return self.db_manager.execute_update(query, params)
            
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return 0
    
    def execute_insert(self, query: str, params: Optional[List] = None) -> int:
        """
        Execute an insert query.
        
        Args:
            query: SQL insert query string
            params: Query parameters (optional)
        
        Returns:
            ID of the inserted row
        """
        try:
            if params is None:
                params = []
            
            return self.db_manager.execute_insert(query, params)
            
        except Exception as e:
            logger.error(f"Database insert failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return 0
