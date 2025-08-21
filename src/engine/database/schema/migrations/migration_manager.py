"""
Migration Manager
================

Handles database schema evolution through versioned migrations.
Provides rollback capabilities and migration history tracking.
"""

import logging
from typing import Any, Dict, List, Optional, Union, Set
from pathlib import Path
import json
from datetime import datetime
import asyncio
import hashlib

from ..base_schema import BaseSchema
from ...connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class MigrationManager(BaseSchema):
    """Manages database schema migrations and versioning"""
    
    def __init__(self, connection_manager: ConnectionManager, schema_name: str = "default"):
        """
        Initialize the migration manager.
        
        Args:
            connection_manager: Database connection manager instance
            schema_name: Name of the schema to manage
        """
        super().__init__(connection_manager, schema_name)
        self._migrations_dir: Optional[Path] = None
        self._applied_migrations: Set[str] = set()
        self._pending_migrations: List[Dict[str, Any]] = []
        self._migration_scripts: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the migration manager and create necessary metadata tables.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if not self.connection_manager.is_connected:
                await self.connection_manager.connect_async()
            
            # Create metadata tables if they don't exist
            await self._create_migration_tables()
            
            # Load applied migrations
            await self._load_applied_migrations()
            
            # Scan for migration scripts
            await self._scan_migration_scripts()
            
            # Determine pending migrations
            await self._determine_pending_migrations()
            
            self._initialized = True
            self.logger.info(f"✅ Migration manager initialized for schema: {self.schema_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize migration manager: {e}")
            return False
    
    def set_migrations_directory(self, migrations_dir: Union[str, Path]) -> None:
        """Set the directory containing migration scripts."""
        self._migrations_dir = Path(migrations_dir)
        self.logger.info(f"📁 Migration scripts directory set to: {self._migrations_dir}")
    
    async def _create_migration_tables(self) -> bool:
        """Create migration metadata tables."""
        try:
            # Migration registry table
            migration_registry_sql = """
                CREATE TABLE IF NOT EXISTS migration_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_id TEXT UNIQUE NOT NULL,
                    version TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    script_path TEXT,
                    checksum TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied_by TEXT DEFAULT 'system',
                    execution_time_ms INTEGER,
                    status TEXT DEFAULT 'applied',
                    rollback_script TEXT,
                    dependencies TEXT
                )
            """
            
            # Migration dependencies table
            migration_dependencies_sql = """
                CREATE TABLE IF NOT EXISTS migration_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_id TEXT NOT NULL,
                    dependency_id TEXT NOT NULL,
                    dependency_type TEXT DEFAULT 'required',
                    FOREIGN KEY (migration_id) REFERENCES migration_registry (migration_id),
                    UNIQUE (migration_id, dependency_id)
                )
            """
            
            # Execute table creation
            await self.connection_manager.execute_update(migration_registry_sql)
            await self.connection_manager.execute_update(migration_dependencies_sql)
            
            self.logger.info("✅ Migration metadata tables created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create migration tables: {e}")
            return False
    
    async def _load_applied_migrations(self) -> bool:
        """Load list of already applied migrations."""
        try:
            query = "SELECT migration_id FROM migration_registry WHERE status = 'applied'"
            results = await self.connection_manager.execute_query(query)
            
            self._applied_migrations = {row['migration_id'] for row in results}
            self.logger.info(f"✅ Loaded {len(self._applied_migrations)} applied migrations")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load applied migrations: {e}")
            return False
    
    async def _scan_migration_scripts(self) -> bool:
        """Scan migration scripts directory for available migrations."""
        try:
            if not self._migrations_dir or not self._migrations_dir.exists():
                self.logger.warning("⚠️ No migrations directory set or directory doesn't exist")
                return True
            
            # Look for migration files (e.g., 001_initial_schema.sql, 002_add_users.sql)
            migration_files = sorted(
                self._migrations_dir.glob("*.sql"),
                key=lambda x: x.stem.split('_')[0] if x.stem.split('_') else '0'
            )
            
            for migration_file in migration_files:
                try:
                    migration_info = await self._parse_migration_file(migration_file)
                    if migration_info:
                        migration_id = migration_info['migration_id']
                        self._migration_scripts[migration_id] = migration_info
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to parse migration file {migration_file}: {e}")
            
            self.logger.info(f"✅ Scanned {len(self._migration_scripts)} migration scripts")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to scan migration scripts: {e}")
            return False
    
    async def _parse_migration_file(self, migration_file: Path) -> Optional[Dict[str, Any]]:
        """Parse a migration file and extract metadata."""
        try:
            # Extract version and name from filename (e.g., 001_initial_schema.sql)
            filename_parts = migration_file.stem.split('_', 1)
            if len(filename_parts) < 2:
                self.logger.warning(f"⚠️ Invalid migration filename format: {migration_file.name}")
                return None
            
            version = filename_parts[0]
            name = filename_parts[1].replace('_', ' ').title()
            
            # Read migration script
            script_content = migration_file.read_text(encoding='utf-8')
            
            # Calculate checksum
            checksum = hashlib.sha256(script_content.encode()).hexdigest()
            
            # Parse script for rollback section
            rollback_script = self._extract_rollback_script(script_content)
            
            # Extract dependencies from comments
            dependencies = self._extract_dependencies(script_content)
            
            migration_id = f"{version}_{name.lower().replace(' ', '_')}"
            
            return {
                'migration_id': migration_id,
                'version': version,
                'name': name,
                'description': f"Migration {version}: {name}",
                'script_path': str(migration_file),
                'script_content': script_content,
                'checksum': checksum,
                'rollback_script': rollback_script,
                'dependencies': dependencies,
                'filename': migration_file.name
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to parse migration file {migration_file}: {e}")
            return None
    
    def _extract_rollback_script(self, script_content: str) -> Optional[str]:
        """Extract rollback script from migration file."""
        try:
            # Look for rollback section (-- ROLLBACK: or similar markers)
            rollback_markers = ['-- ROLLBACK:', '-- ROLLBACK', '/* ROLLBACK */']
            
            for marker in rollback_markers:
                if marker in script_content:
                    # Extract content after rollback marker
                    parts = script_content.split(marker, 1)
                    if len(parts) > 1:
                        rollback_content = parts[1].strip()
                        # Remove any trailing comments
                        if '--' in rollback_content:
                            rollback_content = rollback_content.split('--')[0].strip()
                        return rollback_content
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to extract rollback script: {e}")
            return None
    
    def _extract_dependencies(self, script_content: str) -> List[str]:
        """Extract migration dependencies from script comments."""
        try:
            dependencies = []
            
            # Look for dependency markers
            dependency_markers = ['-- DEPENDS:', '-- DEPENDS ON:', '/* DEPENDS: */']
            
            for marker in dependency_markers:
                if marker in script_content:
                    # Extract dependency information
                    parts = script_content.split(marker, 1)
                    if len(parts) > 1:
                        dep_line = parts[1].split('\n')[0].strip()
                        # Parse comma-separated dependencies
                        deps = [dep.strip() for dep in dep_line.split(',')]
                        dependencies.extend(deps)
            
            return dependencies
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to extract dependencies: {e}")
            return []
    
    async def _determine_pending_migrations(self) -> bool:
        """Determine which migrations are pending (not yet applied)."""
        try:
            self._pending_migrations = []
            
            for migration_id, migration_info in self._migration_scripts.items():
                if migration_id not in self._applied_migrations:
                    # Check if dependencies are satisfied
                    if await self._check_dependencies_satisfied(migration_info):
                        self._pending_migrations.append(migration_info)
            
            # Sort by version
            self._pending_migrations.sort(key=lambda x: x['version'])
            
            self.logger.info(f"✅ Found {len(self._pending_migrations)} pending migrations")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to determine pending migrations: {e}")
            return False
    
    async def _check_dependencies_satisfied(self, migration_info: Dict[str, Any]) -> bool:
        """Check if all dependencies for a migration are satisfied."""
        try:
            dependencies = migration_info.get('dependencies', [])
            
            for dependency in dependencies:
                if dependency not in self._applied_migrations:
                    self.logger.debug(f"⚠️ Migration {migration_info['migration_id']} depends on {dependency} (not applied)")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to check dependencies: {e}")
            return False
    
    async def get_pending_migrations(self) -> List[Dict[str, Any]]:
        """Get list of pending migrations."""
        return self._pending_migrations.copy()
    
    async def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """Get list of applied migrations."""
        try:
            query = """
                SELECT migration_id, version, name, applied_at, execution_time_ms, status
                FROM migration_registry 
                WHERE status = 'applied'
                ORDER BY version
            """
            results = await self.connection_manager.execute_query(query)
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get applied migrations: {e}")
            return []
    
    async def apply_migration(self, migration_id: str) -> bool:
        """Apply a specific migration."""
        try:
            if migration_id not in self._migration_scripts:
                self.logger.error(f"❌ Migration {migration_id} not found")
                return False
            
            if migration_id in self._applied_migrations:
                self.logger.warning(f"⚠️ Migration {migration_id} already applied")
                return True
            
            migration_info = self._migration_scripts[migration_id]
            
            # Check dependencies again
            if not await self._check_dependencies_satisfied(migration_info):
                self.logger.error(f"❌ Dependencies not satisfied for migration {migration_id}")
                return False
            
            self.logger.info(f"🚀 Applying migration: {migration_info['name']}")
            
            # Execute migration
            start_time = datetime.now()
            await self.connection_manager.execute_update(migration_info['script_content'])
            execution_time = (datetime.now() - start_time).total_milliseconds()
            
            # Record migration
            await self._record_migration_application(migration_info, execution_time)
            
            # Update local state
            self._applied_migrations.add(migration_id)
            self._pending_migrations = [m for m in self._pending_migrations if m['migration_id'] != migration_id]
            
            self.logger.info(f"✅ Migration {migration_id} applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply migration {migration_id}: {e}")
            return False
    
    async def apply_all_pending_migrations(self) -> Dict[str, Any]:
        """Apply all pending migrations."""
        try:
            total_migrations = len(self._pending_migrations)
            successful_migrations = 0
            failed_migrations = []
            
            self.logger.info(f"🚀 Applying {total_migrations} pending migrations...")
            
            for migration_info in self._pending_migrations:
                migration_id = migration_info['migration_id']
                
                try:
                    success = await self.apply_migration(migration_id)
                    if success:
                        successful_migrations += 1
                    else:
                        failed_migrations.append(migration_id)
                        
                except Exception as e:
                    self.logger.error(f"❌ Exception applying migration {migration_id}: {e}")
                    failed_migrations.append(migration_id)
            
            # Summary
            result = {
                'total_migrations': total_migrations,
                'successful_migrations': successful_migrations,
                'failed_migrations': failed_migrations,
                'all_successful': len(failed_migrations) == 0
            }
            
            if result['all_successful']:
                self.logger.info(f"🎉 All {total_migrations} migrations applied successfully!")
            else:
                self.logger.warning(f"⚠️ {successful_migrations}/{total_migrations} migrations applied successfully")
                self.logger.error(f"❌ Failed migrations: {failed_migrations}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply pending migrations: {e}")
            return {
                'total_migrations': 0,
                'successful_migrations': 0,
                'failed_migrations': [],
                'all_successful': False,
                'error': str(e)
            }
    
    async def rollback_migration(self, migration_id: str) -> bool:
        """Rollback a specific migration."""
        try:
            if migration_id not in self._applied_migrations:
                self.logger.error(f"❌ Migration {migration_id} not applied")
                return False
            
            # Get migration info
            query = "SELECT * FROM migration_registry WHERE migration_id = ?"
            results = await self.connection_manager.execute_query(query, (migration_id,))
            
            if not results:
                self.logger.error(f"❌ Migration {migration_id} not found in registry")
                return False
            
            migration_record = results[0]
            rollback_script = migration_record.get('rollback_script')
            
            if not rollback_script:
                self.logger.error(f"❌ No rollback script for migration {migration_id}")
                return False
            
            self.logger.info(f"🔄 Rolling back migration: {migration_id}")
            
            # Execute rollback
            await self.connection_manager.execute_update(rollback_script)
            
            # Update migration status
            await self._update_migration_status(migration_id, "rolled_back")
            
            # Update local state
            self._applied_migrations.discard(migration_id)
            
            self.logger.info(f"✅ Migration {migration_id} rolled back successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback migration {migration_id}: {e}")
            return False
    
    async def _record_migration_application(self, migration_info: Dict[str, Any], execution_time: int) -> bool:
        """Record a migration application in the registry."""
        try:
            insert_sql = """
                INSERT INTO migration_registry 
                (migration_id, version, name, description, script_path, checksum, 
                 execution_time_ms, rollback_script, dependencies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            dependencies_json = json.dumps(migration_info.get('dependencies', []))
            
            await self.connection_manager.execute_update(
                insert_sql, 
                (
                    migration_info['migration_id'],
                    migration_info['version'],
                    migration_info['name'],
                    migration_info['description'],
                    migration_info['script_path'],
                    migration_info['checksum'],
                    execution_time,
                    migration_info.get('rollback_script'),
                    dependencies_json
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record migration application: {e}")
            return False
    
    async def _update_migration_status(self, migration_id: str, status: str) -> bool:
        """Update migration status in registry."""
        try:
            update_sql = "UPDATE migration_registry SET status = ? WHERE migration_id = ?"
            await self.connection_manager.execute_update(update_sql, (status, migration_id))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update migration status: {e}")
            return False
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status."""
        try:
            applied = await self.get_applied_migrations()
            pending = await self.get_pending_migrations()
            
            return {
                'schema_name': self.schema_name,
                'total_applied': len(applied),
                'total_pending': len(pending),
                'applied_migrations': applied,
                'pending_migrations': [m['migration_id'] for m in pending],
                'last_applied': applied[-1]['applied_at'] if applied else None,
                'status': 'up_to_date' if len(pending) == 0 else 'pending_migrations'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get migration status: {e}")
            return {
                'schema_name': self.schema_name,
                'error': str(e),
                'status': 'error'
            }
    
    # Implement missing abstract methods from BaseSchema
    
    async def create_table(self, table_name: str, table_definition: Dict[str, Any]) -> bool:
        """Create a new table in the database."""
        try:
            # For migration manager, we'll use the connection manager directly
            # This is a simplified implementation - in practice, you might want to delegate to SchemaManager
            sql = self._generate_create_table_sql(table_name, table_definition)
            await self.connection_manager.execute_update(sql)
            self.logger.info(f"✅ Table {table_name} created successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create table {table_name}: {e}")
            return False
    
    async def drop_table(self, table_name: str) -> bool:
        """Drop a table from the database."""
        try:
            sql = f"DROP TABLE IF EXISTS {table_name}"
            await self.connection_manager.execute_update(sql)
            self.logger.info(f"✅ Table {table_name} dropped successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to drop table {table_name}: {e}")
            return False
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            # SQLite-specific check
            sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = await self.connection_manager.execute_query(sql, (table_name,))
            return len(result) > 0
        except Exception as e:
            self.logger.error(f"❌ Failed to check table existence for {table_name}: {e}")
            return False
    
    async def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a table."""
        try:
            if not await self.table_exists(table_name):
                return None
            
            # Get table schema
            sql = f"PRAGMA table_info({table_name})"
            columns = await self.connection_manager.execute_query(sql)
            
            # Get table constraints
            sql = f"PRAGMA index_list({table_name})"
            indexes = await self.connection_manager.execute_query(sql)
            
            return {
                'exists': True,
                'table_name': table_name,
                'columns': columns,
                'indexes': indexes,
                'schema_name': self.schema_name
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get table info for {table_name}: {e}")
            return None
    
    async def get_all_tables(self) -> List[str]:
        """Get list of all tables in the schema."""
        try:
            sql = "SELECT name FROM sqlite_master WHERE type='table'"
            results = await self.connection_manager.execute_query(sql)
            return [row['name'] for row in results if row['name'] != 'sqlite_sequence']
        except Exception as e:
            self.logger.error(f"❌ Failed to get all tables: {e}")
            return []
    
    async def validate_table_structure(self, table_name: str, expected_structure: Dict[str, Any]) -> bool:
        """Validate that a table matches the expected structure."""
        try:
            actual_info = await self.get_table_info(table_name)
            if not actual_info:
                return False
            
            # Basic validation - check if columns exist
            expected_columns = expected_structure.get('columns', [])
            actual_columns = actual_info.get('columns', [])
            
            if len(expected_columns) != len(actual_columns):
                return False
            
            # More detailed validation could be added here
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to validate table structure for {table_name}: {e}")
            return False
    
    async def execute_migration(self, migration_script: str, rollback_script: Optional[str] = None) -> bool:
        """Execute a database migration script."""
        try:
            await self.connection_manager.execute_update(migration_script)
            self.logger.info("✅ Migration script executed successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to execute migration script: {e}")
            return False
    
    async def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get the history of executed migrations."""
        try:
            return await self.get_applied_migrations()
        except Exception as e:
            self.logger.error(f"❌ Failed to get migration history: {e}")
            return []
    
    def _generate_create_table_sql(self, table_name: str, table_definition: Dict[str, Any]) -> str:
        """Generate CREATE TABLE SQL from table definition."""
        columns = table_definition.get('columns', [])
        constraints = table_definition.get('constraints', [])
        
        # Build column definitions
        column_defs = []
        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            if col.get('not_null'):
                col_def += " NOT NULL"
            if col.get('default'):
                col_def += f" DEFAULT {col['default']}"
            
            column_defs.append(col_def)
        
        # Add constraints
        column_defs.extend(constraints)
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  "
        sql += ",\n  ".join(column_defs)
        sql += "\n)"
        
        return sql
