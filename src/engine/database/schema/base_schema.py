"""
Abstract Base Schema Class
==========================

Defines the interface for all schema-related operations including table creation,
migration management, and validation. This ensures consistent behavior across
different database types and schema components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Set
from pathlib import Path
import logging
from datetime import datetime

from ..connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class BaseSchema(ABC):
    """Abstract base class for schema management operations"""
    
    def __init__(self, connection_manager: ConnectionManager, schema_name: str = "default"):
        """
        Initialize the base schema manager.
        
        Args:
            connection_manager: Database connection manager instance
            schema_name: Name of the schema to manage
        """
        self.connection_manager = connection_manager
        self.schema_name = schema_name
        self.logger = logging.getLogger(f"{__name__}.{schema_name}")
        self._initialized = False
        self._tables: Set[str] = set()
        self._migrations: List[Dict[str, Any]] = []
        
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the schema manager and create necessary metadata tables.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def create_table(self, table_name: str, table_definition: Dict[str, Any]) -> bool:
        """
        Create a new table in the database.
        
        Args:
            table_name: Name of the table to create
            table_definition: Table structure definition
            
        Returns:
            bool: True if table created successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def drop_table(self, table_name: str) -> bool:
        """
        Drop a table from the database.
        
        Args:
            table_name: Name of the table to drop
            
        Returns:
            bool: True if table dropped successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Optional[Dict[str, Any]]: Table information or None if not found
        """
        pass
    
    @abstractmethod
    async def get_all_tables(self) -> List[str]:
        """
        Get list of all tables in the schema.
        
        Returns:
            List[str]: List of table names
        """
        pass
    
    @abstractmethod
    async def validate_table_structure(self, table_name: str, expected_structure: Dict[str, Any]) -> bool:
        """
        Validate that a table matches the expected structure.
        
        Args:
            table_name: Name of the table to validate
            expected_structure: Expected table structure
            
        Returns:
            bool: True if structure matches, False otherwise
        """
        pass
    
    @abstractmethod
    async def execute_migration(self, migration_script: str, rollback_script: Optional[str] = None) -> bool:
        """
        Execute a database migration script.
        
        Args:
            migration_script: SQL script to execute
            rollback_script: Optional rollback script
            
        Returns:
            bool: True if migration successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of executed migrations.
        
        Returns:
            List[Dict[str, Any]]: List of migration records
        """
        pass
    
    @abstractmethod
    async def rollback_migration(self, migration_id: str) -> bool:
        """
        Rollback a specific migration.
        
        Args:
            migration_id: ID of the migration to rollback
            
        Returns:
            bool: True if rollback successful, False otherwise
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the schema manager.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            tables = await self.get_all_tables()
            migrations = await self.get_migration_history()
            
            return {
                "schema_name": self.schema_name,
                "status": "healthy" if self._initialized else "unhealthy",
                "initialized": self._initialized,
                "table_count": len(tables),
                "migration_count": len(migrations),
                "connection_status": self.connection_manager.is_connected,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "schema_name": self.schema_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def is_initialized(self) -> bool:
        """Check if the schema manager is initialized."""
        return self._initialized
    
    def get_schema_name(self) -> str:
        """Get the name of the managed schema."""
        return self.schema_name
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        pass
