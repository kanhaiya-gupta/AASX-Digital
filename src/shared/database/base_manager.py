"""
Base Database Manager
====================

Base class for database operations with common functionality.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)

class BaseDatabaseManager:
    """Base class for database operations."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.db_path = connection_manager.db_path
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as dictionaries."""
        try:
            results = self.connection_manager.execute_query(query, params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update query and return affected rows."""
        try:
            return self.connection_manager.execute_update(query, params)
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            raise
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the last row ID."""
        try:
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Insert execution failed: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        results = self.execute_query(query, (table_name,))
        return len(results) > 0
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get the schema for a table."""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query, ())
    
    def begin_transaction(self):
        """Begin a database transaction."""
        self.connection_manager.get_connection().execute("BEGIN TRANSACTION")
    
    def commit_transaction(self):
        """Commit the current transaction."""
        self.connection_manager.get_connection().commit()
    
    def rollback_transaction(self):
        """Rollback the current transaction."""
        self.connection_manager.get_connection().rollback()
    
    def close(self):
        """Close the database connection."""
        self.connection_manager.close_connection()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 