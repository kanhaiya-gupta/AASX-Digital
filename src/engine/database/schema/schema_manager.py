"""
Schema Manager
==============

Main orchestrator for database schema management. Handles table creation,
migrations, validation, and provides a unified interface for all schema operations.
"""

import logging
from typing import Any, Dict, List, Optional, Union, Set
from pathlib import Path
import json
from datetime import datetime
import asyncio

from .base_schema import BaseSchema
from ..connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class SchemaManager(BaseSchema):
    """Main schema manager for orchestrating all schema operations"""
    
    def __init__(self, connection_manager: ConnectionManager, schema_name: str = "default"):
        """
        Initialize the schema manager.
        
        Args:
            connection_manager: Database connection manager instance
            schema_name: Name of the schema to manage
        """
        super().__init__(connection_manager, schema_name)
        self._metadata_tables_created = False
        self._table_definitions: Dict[str, Dict[str, Any]] = {}
        self._migration_history: List[Dict[str, Any]] = []
        self._validation_cache: Dict[str, bool] = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the schema manager and create necessary metadata tables.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if not self.connection_manager.is_connected:
                await self.connection_manager.connect_async()
            
            # Create metadata tables if they don't exist
            await self._create_metadata_tables()
            
            # Load existing table definitions
            await self._load_table_definitions()
            
            # Load migration history
            await self._load_migration_history()
            
            self._initialized = True
            self.logger.info(f"✅ Schema manager initialized for schema: {self.schema_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize schema manager: {e}")
            return False
    
    async def _create_metadata_tables(self) -> bool:
        """Create metadata tables for schema management."""
        try:
            # Table definitions table
            table_defs_sql = """
                CREATE TABLE IF NOT EXISTS schema_table_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT UNIQUE NOT NULL,
                    table_definition TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            # Migration history table
            migration_history_sql = """
                CREATE TABLE IF NOT EXISTS schema_migration_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_id TEXT UNIQUE NOT NULL,
                    migration_name TEXT NOT NULL,
                    migration_script TEXT NOT NULL,
                    rollback_script TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed',
                    execution_time_ms INTEGER,
                    error_message TEXT
                )
            """
            
            # Execute table creation
            await self.connection_manager.execute_update(table_defs_sql)
            await self.connection_manager.execute_update(migration_history_sql)
            
            self._metadata_tables_created = True
            self.logger.info("✅ Metadata tables created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create metadata tables: {e}")
            return False
    
    async def _load_table_definitions(self) -> bool:
        """Load existing table definitions from metadata."""
        try:
            query = "SELECT table_name, table_definition FROM schema_table_definitions"
            results = await self.connection_manager.execute_query(query)
            
            for row in results:
                table_name = row['table_name']
                table_def = json.loads(row['table_definition'])
                self._table_definitions[table_name] = table_def
                self._tables.add(table_name)
            
            self.logger.info(f"✅ Loaded {len(self._table_definitions)} table definitions")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load table definitions: {e}")
            return False
    
    async def _load_migration_history(self) -> bool:
        """Load migration history from metadata."""
        try:
            query = "SELECT * FROM schema_migration_history ORDER BY executed_at"
            results = await self.connection_manager.execute_query(query)
            
            self._migration_history = results
            self.logger.info(f"✅ Loaded {len(self._migration_history)} migration records")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load migration history: {e}")
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
            if await self.table_exists(table_name):
                self.logger.warning(f"⚠️ Table {table_name} already exists")
                return True
            
            # Generate CREATE TABLE SQL
            create_sql = self._generate_create_table_sql(table_name, table_definition)
            
            # Execute table creation
            await self.connection_manager.execute_update(create_sql)
            
            # Store table definition in metadata
            await self._store_table_definition(table_name, table_definition)
            
            # Update local state
            self._tables.add(table_name)
            self._table_definitions[table_name] = table_definition
            
            self.logger.info(f"✅ Created table: {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create table {table_name}: {e}")
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
            if not await self.table_exists(table_name):
                self.logger.warning(f"⚠️ Table {table_name} does not exist")
                return True
            
            # Drop the table
            drop_sql = f"DROP TABLE IF EXISTS {table_name}"
            await self.connection_manager.execute_update(drop_sql)
            
            # Remove from metadata
            await self._remove_table_definition(table_name)
            
            # Update local state
            self._tables.discard(table_name)
            self._table_definitions.pop(table_name, None)
            self._validation_cache.pop(table_name, None)
            
            self.logger.info(f"✅ Dropped table: {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to drop table {table_name}: {e}")
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
            # Check SQLite system tables
            query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """
            results = await self.connection_manager.execute_query(query, (table_name,))
            return len(results) > 0
            
        except Exception as e:
            self.logger.error(f"❌ Error checking if table {table_name} exists: {e}")
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
            if not await self.table_exists(table_name):
                return None
            
            # Get table structure
            pragma_query = f"PRAGMA table_info({table_name})"
            columns = await self.connection_manager.execute_query(pragma_query)
            
            # Get table definition from metadata
            table_def = self._table_definitions.get(table_name, {})
            
            return {
                "table_name": table_name,
                "columns": columns,
                "definition": table_def,
                "exists": True,
                "created_at": table_def.get("created_at"),
                "updated_at": table_def.get("updated_at")
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting table info for {table_name}: {e}")
            return None
    
    async def get_all_tables(self) -> List[str]:
        """
        Get list of all tables in the schema.
        
        Returns:
            List[str]: List of table names
        """
        try:
            query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """
            results = await self.connection_manager.execute_query(query)
            return [row['name'] for row in results]
            
        except Exception as e:
            self.logger.error(f"❌ Error getting all tables: {e}")
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
            # Check cache first
            cache_key = f"{table_name}_{hash(str(expected_structure))}"
            if cache_key in self._validation_cache:
                return self._validation_cache[cache_key]
            
            if not await self.table_exists(table_name):
                self._validation_cache[cache_key] = False
                return False
            
            # Get actual table structure
            actual_structure = await self.get_table_info(table_name)
            if not actual_structure:
                self._validation_cache[cache_key] = False
                return False
            
            # Compare structures (simplified validation)
            is_valid = self._compare_table_structures(
                expected_structure, 
                actual_structure.get("definition", {})
            )
            
            # Cache result
            self._validation_cache[cache_key] = is_valid
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"❌ Error validating table structure for {table_name}: {e}")
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
            migration_id = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            start_time = datetime.now()
            
            # Execute migration
            await self.connection_manager.execute_update(migration_script)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_milliseconds()
            
            # Record migration
            await self._record_migration(
                migration_id, 
                "Manual Migration", 
                migration_script, 
                rollback_script,
                execution_time
            )
            
            self.logger.info(f"✅ Migration executed successfully: {migration_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Migration failed: {e}")
            return False
    
    async def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of executed migrations.
        
        Returns:
            List[Dict[str, Any]]: List of migration records
        """
        return self._migration_history.copy()
    
    async def rollback_migration(self, migration_id: str) -> bool:
        """
        Rollback a specific migration.
        
        Args:
            migration_id: ID of the migration to rollback
            
        Returns:
            bool: True if rollback successful, False otherwise
        """
        try:
            # Find migration record
            migration_record = None
            for record in self._migration_history:
                if record['migration_id'] == migration_id:
                    migration_record = record
                    break
            
            if not migration_record:
                self.logger.error(f"❌ Migration {migration_id} not found")
                return False
            
            rollback_script = migration_record.get('rollback_script')
            if not rollback_script:
                self.logger.error(f"❌ No rollback script for migration {migration_id}")
                return False
            
            # Execute rollback
            await self.connection_manager.execute_update(rollback_script)
            
            # Update migration status
            await self._update_migration_status(migration_id, "rolled_back")
            
            self.logger.info(f"✅ Migration {migration_id} rolled back successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback migration {migration_id}: {e}")
            return False
    
    def _generate_create_table_sql(self, table_name: str, table_definition: Dict[str, Any]) -> str:
        """Generate CREATE TABLE SQL from table definition."""
        columns = table_definition.get("columns", [])
        constraints = table_definition.get("constraints", [])
        
        # Build column definitions
        column_defs = []
        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            if col.get('not_null'):
                col_def += " NOT NULL"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            if col.get('default') is not None:
                col_def += f" DEFAULT {col['default']}"
            column_defs.append(col_def)
        
        # Add constraints
        column_defs.extend(constraints)
        
        # Build final SQL
        sql = f"CREATE TABLE {table_name} (\n"
        sql += ",\n".join(f"    {col_def}" for col_def in column_defs)
        sql += "\n)"
        
        return sql
    
    def _compare_table_structures(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> bool:
        """Compare expected and actual table structures."""
        # Simplified comparison - can be enhanced
        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys())
        
        # Check if all expected keys exist
        if not expected_keys.issubset(actual_keys):
            return False
        
        # Basic structure validation
        return True
    
    async def _store_table_definition(self, table_name: str, table_definition: Dict[str, Any]) -> bool:
        """Store table definition in metadata."""
        try:
            # Add metadata
            table_definition["created_at"] = datetime.now().isoformat()
            table_definition["updated_at"] = datetime.now().isoformat()
            
            # Insert or update
            insert_sql = """
                INSERT OR REPLACE INTO schema_table_definitions 
                (table_name, table_definition, updated_at) 
                VALUES (?, ?, ?)
            """
            
            await self.connection_manager.execute_update(
                insert_sql, 
                (table_name, json.dumps(table_definition), table_definition["updated_at"])
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store table definition: {e}")
            return False
    
    async def _remove_table_definition(self, table_name: str) -> bool:
        """Remove table definition from metadata."""
        try:
            delete_sql = "DELETE FROM schema_table_definitions WHERE table_name = ?"
            await self.connection_manager.execute_update(delete_sql, (table_name,))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to remove table definition: {e}")
            return False
    
    async def _record_migration(self, migration_id: str, migration_name: str, 
                               migration_script: str, rollback_script: Optional[str], 
                               execution_time: int) -> bool:
        """Record migration in metadata."""
        try:
            insert_sql = """
                INSERT INTO schema_migration_history 
                (migration_id, migration_name, migration_script, rollback_script, execution_time_ms)
                VALUES (?, ?, ?, ?, ?)
            """
            
            await self.connection_manager.execute_update(
                insert_sql, 
                (migration_id, migration_name, migration_script, rollback_script, execution_time)
            )
            
            # Update local state
            self._migration_history.append({
                "migration_id": migration_id,
                "migration_name": migration_name,
                "migration_script": migration_script,
                "rollback_script": rollback_script,
                "execution_time_ms": execution_time,
                "status": "completed",
                "executed_at": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record migration: {e}")
            return False
    
    async def _update_migration_status(self, migration_id: str, status: str) -> bool:
        """Update migration status in metadata."""
        try:
            update_sql = "UPDATE schema_migration_history SET status = ? WHERE migration_id = ?"
            await self.connection_manager.execute_update(update_sql, (status, migration_id))
            
            # Update local state
            for record in self._migration_history:
                if record["migration_id"] == migration_id:
                    record["status"] = status
                    break
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update migration status: {e}")
            return False
