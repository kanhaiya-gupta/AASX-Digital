"""
Database Connection Manager
==========================

Handles database connections, connection pooling, and connection lifecycle.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """Manages database connections and provides connection pooling."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection, creating one if it doesn't exist."""
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        try:
            # Handle in-memory database
            if str(self.db_path) == ":memory:":
                connection = sqlite3.connect(":memory:")
            else:
                # Ensure database directory exists for file-based databases
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                connection = sqlite3.connect(str(self.db_path))
            
            # Configure connection
            connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
            
            # Only use WAL mode for file-based databases
            if str(self.db_path) != ":memory:":
                connection.execute("PRAGMA journal_mode = WAL")  # Use WAL mode for better concurrency
            
            logger.info(f"Database connection established: {self.db_path}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    def close_connection(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursors."""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a query and return results."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update query and return affected rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connection() 