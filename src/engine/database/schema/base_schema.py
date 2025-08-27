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
        
    async def initialize(self) -> bool:
        """
        Initialize the schema manager and create necessary metadata tables.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Check if child class has create_tables method
            if hasattr(self, 'create_tables'):
                if await self.create_tables():
                    self._initialized = True
                    return True
                else:
                    return False
            else:
                # Basic implementation - child classes should override this
                self.logger.warning("initialize not implemented in base class")
                self._initialized = True  # Set to True for basic initialization
                return True
        except Exception as e:
            self.logger.error(f"Failed to initialize schema: {e}")
            return False
    
    async def create_table(self, table_name: str, table_definition: Dict[str, Any]) -> bool:
        """
        Create a new table in the database.
        
        Args:
            table_name: Name of the table to create
            table_definition: Table structure definition
            
        Returns:
            bool: True if table created successfully, False otherwise
        """
        try:
            # Basic implementation - child classes should override this
            self.logger.warning(f"create_table not implemented in base class for {table_name}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to create table {table_name}: {e}")
            return False
    
    async def drop_table(self, table_name: str) -> bool:
        """
        Drop a table from the database.
        
        Args:
            table_name: Name of the table to drop
            
        Returns:
            bool: True if table dropped successfully, False otherwise
        """
        try:
            # Basic implementation - child classes should override this
            self.logger.warning(f"drop_table not implemented in base class for {table_name}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to drop table {table_name}: {e}")
            return False
    
    async def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        try:
            # Use SQLite-specific query for table existence
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = await self.connection_manager.execute_query(query, (table_name,))
            return len(result) > 0
        except Exception as e:
            self.logger.error(f"Failed to check table existence for {table_name}: {e}")
            return False
    
    async def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Optional[Dict[str, Any]]: Table information or None if not found
        """
        try:
            # Check if table exists first
            if not await self.table_exists(table_name):
                self.logger.warning(f"Table {table_name} does not exist")
                return None
            
            # Get table structure using PRAGMA - PRAGMA doesn't support parameterized queries
            query = f"PRAGMA table_info({table_name})"
            self.logger.debug(f"Executing PRAGMA query: {query}")
            
            columns = await self.connection_manager.execute_query(query)
            self.logger.debug(f"PRAGMA result: {columns}")
            
            if not columns:
                self.logger.warning(f"No column information returned for table {table_name}")
                return None
            
            # Format column information - handle both tuple and dictionary formats
            column_info = []
            for col in columns:
                if isinstance(col, dict):
                    # Dictionary format (what we're getting from SQLite manager)
                    column_info.append({
                        "name": col.get('name'),
                        "type": col.get('type'), 
                        "not_null": bool(col.get('notnull', 0)),
                        "default": col.get('dflt_value'),
                        "primary_key": bool(col.get('pk', 0))
                    })
                elif isinstance(col, (list, tuple)) and len(col) >= 6:
                    # Tuple format (fallback for other database managers)
                    column_info.append({
                        "name": col[1],
                        "type": col[2], 
                        "not_null": bool(col[3]),
                        "default": col[4],
                        "primary_key": bool(col[5])
                    })
                else:
                    self.logger.warning(f"Unexpected column format: {col}")
            
            if not column_info:
                self.logger.warning(f"No valid column information found for table {table_name}")
                return None
            
            result = {
                "name": table_name,
                "columns": column_info,
                "column_count": len(column_info)
            }
            
            self.logger.debug(f"Returning table info: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {e}")
            return None
    
    async def get_all_tables(self) -> List[str]:
        """
        Get list of all tables in the schema.
        
        Returns:
            List[str]: List of table names
        """
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            result = await self.connection_manager.execute_query(query)
            
            # Handle both dictionary and tuple formats
            table_names = []
            for row in result:
                if isinstance(row, dict):
                    # Dictionary format (what we're getting from SQLite manager)
                    table_name = row.get('name')
                elif isinstance(row, (list, tuple)) and len(row) > 0:
                    # Tuple format (fallback for other database managers)
                    table_name = row[0]
                else:
                    continue
                
                if table_name and table_name != 'sqlite_sequence':
                    table_names.append(table_name)
            
            return table_names
            
        except Exception as e:
            self.logger.error(f"Failed to get all tables: {e}")
            return []
    
    async def validate_table_structure(self, table_name: str, expected_structure: Dict[str, Any]) -> bool:
        """
        Validate that a table matches the expected structure.
        
        Args:
            table_name: Name of the table to validate
            expected_structure: Expected table structure
            
        Returns:
            bool: True if structure matches, False otherwise
        """
        try:
            # Get actual table info
            actual_info = await self.get_table_info(table_name)
            if not actual_info:
                return False
            
            # Basic validation - check if expected columns exist
            if 'columns' in expected_structure:
                expected_columns = set(expected_structure['columns'])
                actual_columns = set(col['name'] for col in actual_info['columns'])
                
                # Check if all expected columns exist
                if not expected_columns.issubset(actual_columns):
                    self.logger.warning(f"Table {table_name} missing expected columns: {expected_columns - actual_columns}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate table structure for {table_name}: {e}")
            return False
    
    async def execute_migration(self, migration_script: str, rollback_script: Optional[str] = None) -> bool:
        """
        Execute a database migration script.
        
        Args:
            migration_script: SQL script to execute
            rollback_script: Optional rollback script
            
        Returns:
            bool: True if migration successful, False otherwise
        """
        try:
            # Basic implementation - child classes should override this
            self.logger.warning(f"execute_migration not implemented in base class")
            return False
        except Exception as e:
            self.logger.error(f"Failed to execute migration: {e}")
            return False
    
    async def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of executed migrations.
        
        Returns:
            List[Dict[str, Any]]: List of migration records
        """
        try:
            # Basic implementation - child classes should override this
            self.logger.warning("get_migration_history not implemented in base class")
            return []
        except Exception as e:
            self.logger.error(f"Failed to get migration history: {e}")
            return []
    
    async def rollback_migration(self, migration_id: str) -> bool:
        """
        Rollback a specific migration.
        
        Args:
            migration_id: ID of the migration to rollback
            
        Returns:
            bool: True if rollback successful, False otherwise
        """
        try:
            # Basic implementation - child classes should override this
            self.logger.warning(f"rollback_migration not implemented in base class for {migration_id}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to rollback migration {migration_id}: {e}")
            return False
    
    async def create_indexes(self, table_name: str, index_queries: List[str]) -> bool:
        """
        Create indexes for a table.
        
        Args:
            table_name: Name of the table to create indexes for
            index_queries: List of CREATE INDEX SQL statements
            
        Returns:
            bool: True if indexes created successfully, False otherwise
        """
        try:
            if not index_queries:
                self.logger.info(f"No indexes to create for table {table_name}")
                return True
            
            self.logger.info(f"Creating {len(index_queries)} indexes for table {table_name}")
            
            for i, index_query in enumerate(index_queries):
                try:
                    await self.connection_manager.execute_query(index_query)
                    self.logger.debug(f"Created index {i+1}/{len(index_queries)} for {table_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to create index {i+1} for {table_name}: {e}")
                    # Continue with other indexes
            
            self.logger.info(f"✅ Index creation completed for table {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create indexes for table {table_name}: {e}")
            return False
    
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
