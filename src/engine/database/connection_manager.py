"""
Abstract Base Database Connection Manager
========================================

Defines the interface for all database connection managers (SQLite, PostgreSQL, MySQL).
This ensures consistent behavior across different database types.
All methods are pure async for modern async-first architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConnectionManager(ABC):
    """Abstract base class for database connection management - Pure Async"""
    
    def __init__(self, connection_config: Union[str, Path, Dict[str, Any]]):
        """
        Initialize the connection manager.
        
        Args:
            connection_config: Database connection configuration
                - For SQLite: Path to database file
                - For PostgreSQL/MySQL: Connection parameters dict
        """
        self.connection_config = connection_config
        self._connection = None
        self._connection_pool = None
        self._is_connected = False
        
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish database connection asynchronously.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Close database connection asynchronously.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_connection(self) -> Any:
        """
        Get the active database connection asynchronously.
        
        Returns:
            Database connection object
        """
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query asynchronously.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries representing query results
        """
        pass
    
    @abstractmethod
    async def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query asynchronously.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Number of affected rows
        """
        pass
    
    @abstractmethod
    async def execute_transaction(self, queries: List[tuple]) -> bool:
        """
        Execute multiple queries in a transaction asynchronously.
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            bool: True if transaction successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def begin_transaction(self) -> bool:
        """
        Begin a new transaction asynchronously.
        
        Returns:
            bool: True if transaction started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def commit_transaction(self) -> bool:
        """
        Commit the current transaction asynchronously.
        
        Returns:
            bool: True if commit successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def rollback_transaction(self) -> bool:
        """
        Rollback the current transaction asynchronously.
        
        Returns:
            bool: True if rollback successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test if the database connection is working asynchronously.
        
        Returns:
            bool: True if connection test successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information asynchronously.
        
        Returns:
            Dictionary containing database information
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database connection asynchronously.
        
        Returns:
            Dictionary containing health status information
        """
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Any:
        """
        Get performance metrics asynchronously.
        
        Returns:
            Metrics object or dictionary
        """
        pass
    
    @abstractmethod
    async def reset_metrics(self) -> None:
        """
        Reset performance metrics asynchronously.
        """
        pass
    
    @abstractmethod
    async def get_cursor_async(self):
        """
        Get an async cursor context manager.
        
        Returns:
            Async context manager for database operations
        """
        pass
