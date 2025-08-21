"""
Abstract Base Database Connection Manager
========================================

Defines the interface for all database connection managers (SQLite, PostgreSQL, MySQL).
This ensures consistent behavior across different database types.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConnectionManager(ABC):
    """Abstract base class for database connection management"""
    
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
    def connect(self) -> bool:
        """
        Establish database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def connect_async(self) -> bool:
        """
        Establish database connection asynchronously.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Close database connection.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect_async(self) -> bool:
        """
        Close database connection asynchronously.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_connection(self) -> Any:
        """
        Get the active database connection.
        
        Returns:
            Database connection object
        """
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries representing query results
        """
        pass
    
    @abstractmethod
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Number of affected rows
        """
        pass
    
    @abstractmethod
    def execute_transaction(self, queries: List[tuple]) -> bool:
        """
        Execute multiple queries in a transaction.
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            bool: True if transaction successful, False otherwise
        """
        pass
    
    @abstractmethod
    def begin_transaction(self) -> bool:
        """
        Begin a new transaction.
        
        Returns:
            bool: True if transaction started successfully
        """
        pass
    
    @abstractmethod
    def commit_transaction(self) -> bool:
        """
        Commit the current transaction.
        
        Returns:
            bool: True if commit successful
        """
        pass
    
    @abstractmethod
    def rollback_transaction(self) -> bool:
        """
        Rollback the current transaction.
        
        Returns:
            bool: True if rollback successful
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the database connection is working.
        
        Returns:
            bool: True if connection test successful
        """
        pass
    
    @abstractmethod
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database version and connection information.
        
        Returns:
            Dictionary with database information
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._is_connected
    
    @property
    def connection_string(self) -> str:
        """Get the connection string (for logging/debugging)"""
        if isinstance(self.connection_config, (str, Path)):
            return str(self.connection_config)
        elif isinstance(self.connection_config, dict):
            return f"{self.connection_config.get('host', 'localhost')}:{self.connection_config.get('port', 'default')}/{self.connection_config.get('database', 'unknown')}"
        return "unknown"
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        try:
            # For async managers, we need to handle this differently
            if hasattr(self, 'disconnect_async'):
                # Schedule async disconnect (can't await in sync context)
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self.disconnect_async())
                except:
                    pass
            else:
                self.disconnect()
        except:
            pass
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            # For async managers, we need to handle this differently
            if hasattr(self, 'disconnect_async'):
                # Schedule async disconnect (can't await in sync context)
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self.disconnect_async())
                except:
                    pass
            else:
                self.disconnect()
        except:
            pass
