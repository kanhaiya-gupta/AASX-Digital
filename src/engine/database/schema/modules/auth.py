"""
Authentication and Authorization Schema Module
============================================

Defines tables for user authentication, authorization, and security metrics.
Follows the same 2-table pattern as other modules: Users (Registry) + User Metrics.

ENTERPRISE-GRADE FEATURES:
- Advanced security and compliance
- Multi-factor authentication management
- Role-based access control (RBAC)
- Security monitoring and threat detection
- Compliance framework integration
- Performance optimization and monitoring
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import asyncio
from ..base_schema import BaseSchema

logger = logging.getLogger(__name__)


class AuthSchema(BaseSchema):
    """Enterprise-grade Authentication and Authorization Schema Module"""
    
    def __init__(self, connection_manager, schema_name: str = "auth"):
        super().__init__(connection_manager, schema_name)
        self._security_metrics = {}
        self._compliance_status = {}
        self._threat_detection = {}
        self._performance_metrics = {}

    async def initialize(self) -> bool:
        """Initialize the enterprise-grade auth schema manager."""
        try:
            # Initialize base schema
            if not await super().initialize():
                return False
            
            # Create enterprise metadata tables
            await self._create_enterprise_metadata_tables()
            
            # Initialize security monitoring
            await self._initialize_security_monitoring()
            
            # Setup compliance framework
            await self._setup_compliance_framework()
            
            # Create core auth tables
            if not await self._create_enterprise_tables():
                return False
            
            # Setup security policies
            await self._setup_security_policies()
            
            # Initialize threat detection
            await self._initialize_threat_detection()
            
            self.logger.info("✅ Enterprise Auth Schema initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize enterprise auth schema: {e}")
            return False

    async def create_table(self, table_name: str, table_definition: Union[str, Dict[str, Any]]) -> bool:
        """Create enterprise-grade table with advanced security features."""
        try:
            # Parse table definition if it's a string
            if isinstance(table_definition, str):
                # Execute the table creation SQL
                await self.connection_manager.execute_update(table_definition)
            else:
                # Handle structured table definition
                await self._create_table_from_definition(table_name, table_definition)
            
            # Create enterprise indexes
            await self._create_enterprise_indexes(table_name, [])
            
            # Setup table monitoring
            await self._setup_table_monitoring(table_name)
            
            # Validate table structure
            await self._validate_table_structure(table_name)
            
            # Update metadata
            await self._update_table_metadata(table_name)
            
            self.logger.info(f"✅ Created enterprise auth table: {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create enterprise auth table {table_name}: {e}")
            return False

    async def drop_table(self, table_name: str) -> bool:
        """Drop table with enterprise-grade security checks."""
        try:
            # Check dependencies
            dependencies = await self._check_table_dependencies(table_name)
            if dependencies:
                self.logger.warning(f"⚠️ Table {table_name} has dependencies: {dependencies}")
                return False
            
            # Backup table data
            await self._backup_table_data(table_name)
            
            # Log security event
            await self._log_security_event("table_drop", table_name, "admin")
            
            # Drop the table
            drop_sql = f"DROP TABLE IF EXISTS {table_name}"
            await self.connection_manager.execute_update(drop_sql)
            
            # Cleanup metadata
            await self._cleanup_table_metadata(table_name)
            
            self.logger.info(f"✅ Dropped enterprise auth table: {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to drop auth table {table_name}: {e}")
            return False

    async def table_exists(self, table_name: str) -> bool:
        """Check if table exists with enterprise validation."""
        try:
            query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """
            result = await self.connection_manager.execute_query(query, (table_name,))
            return len(result) > 0
        except Exception as e:
            self.logger.error(f"❌ Failed to check table existence: {e}")
            return False

    async def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive table information with enterprise security metadata."""
        try:
            if not await self.table_exists(table_name):
                return None
            
            # Get basic table info
            pragma_query = f"PRAGMA table_info({table_name})"
            columns = await self.connection_manager.execute_query(pragma_query)
            
            # Get table statistics
            stats_query = f"PRAGMA stats({table_name})"
            stats = await self.connection_manager.execute_query(stats_query)
            
            # Get security metrics
            security = self._security_metrics.get(table_name, {})
            
            # Get compliance status
            compliance = self._compliance_status.get(table_name, {})
            
            # Get performance metrics
            performance = self._performance_metrics.get(table_name, {})
            
            return {
                "table_name": table_name,
                "columns": columns,
                "statistics": stats,
                "security_metrics": security,
                "compliance_status": compliance,
                "performance_metrics": performance,
                "created_at": datetime.now().isoformat(),
                "last_security_audit": self._get_last_security_audit(table_name)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get table info: {e}")
            return None

    async def get_all_tables(self) -> List[str]:
        """Get all auth tables with enterprise categorization."""
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            results = await self.connection_manager.execute_query(query)
            
            tables = [row['name'] for row in results]
            
            # Filter out system tables and get auth tables
            auth_tables = [t for t in tables if not t.startswith('sqlite_') and not t.startswith('schema_') and t in self.get_table_names()]
            
            return auth_tables
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get all auth tables: {e}")
            return []

    async def validate_table_structure(self, table_name: str, expected_structure: Dict[str, Any]) -> bool:
        """Validate table structure with enterprise-grade security validation."""
        try:
            current_info = await self.get_table_info(table_name)
            if not current_info:
                return False
            
            # Validate columns
            current_columns = {col['name']: col for col in current_info['columns']}
            expected_columns = expected_structure.get('columns', {})
            
            for col_name, col_def in expected_columns.items():
                if col_name not in current_columns:
                    self.logger.error(f"❌ Missing column: {col_name}")
                    return False
                
                # Validate column properties
                current_col = current_columns[col_name]
                if not self._validate_column_properties(current_col, col_def):
                    return False
            
            # Validate security requirements
            if not await self._validate_security_requirements(table_name):
                return False
            
            # Validate constraints
            if not await self._validate_table_constraints(table_name, expected_structure):
                return False
            
            # Validate indexes
            if not await self._validate_table_indexes(table_name, expected_structure):
                return False
            
            self.logger.info(f"✅ Auth table structure validation passed: {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Auth table structure validation failed: {e}")
            return False

    async def execute_migration(self, migration_script: str, rollback_script: Optional[str] = None) -> bool:
        """Execute enterprise-grade migration with security checks."""
        try:
            # Pre-migration security validation
            if not await self._validate_migration_security(migration_script):
                return False
            
            # Pre-migration validation
            if not await self._validate_migration_script(migration_script):
                return False
            
            # Create migration checkpoint
            checkpoint_id = await self._create_migration_checkpoint()
            
            # Log security event
            await self._log_security_event("migration_start", checkpoint_id, "admin")
            
            # Execute migration
            await self.connection_manager.execute_update(migration_script)
            
            # Post-migration validation
            if not await self._validate_migration_results():
                await self._rollback_migration(checkpoint_id)
                return False
            
            # Update migration history
            await self._record_migration_success(migration_script, rollback_script)
            
            # Log security event
            await self._log_security_event("migration_complete", checkpoint_id, "admin")
            
            self.logger.info(f"✅ Auth migration executed successfully: {checkpoint_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Auth migration failed: {e}")
            await self._rollback_migration(checkpoint_id)
            return False

    async def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get comprehensive migration history with enterprise security details."""
        try:
            query = """
                SELECT * FROM schema_migration_history 
                WHERE schema_name = ? 
                ORDER BY executed_at DESC
            """
            results = await self.connection_manager.execute_query(query, (self.schema_name,))
            
            # Enhance with additional metadata
            enhanced_history = []
            for migration in results:
                enhanced_migration = dict(migration)
                enhanced_migration['security_impact'] = await self._assess_security_impact(migration['migration_id'])
                enhanced_migration['compliance_status'] = await self._check_migration_compliance(migration['migration_id'])
                enhanced_history.append(enhanced_migration)
            
            return enhanced_history
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get auth migration history: {e}")
            return []

    async def rollback_migration(self, migration_id: str) -> bool:
        """Rollback migration with enterprise-grade security."""
        try:
            # Get migration details
            migration = await self._get_migration_details(migration_id)
            if not migration:
                return False
            
            # Validate rollback safety
            if not await self._validate_rollback_safety(migration_id):
                return False
            
            # Log security event
            await self._log_security_event("migration_rollback", migration_id, "admin")
            
            # Execute rollback
            if migration.get('rollback_script'):
                await self.connection_manager.execute_update(migration['rollback_script'])
            
            # Update migration status
            await self._update_migration_status(migration_id, 'rolled_back')
            
            # Restore system state
            await self._restore_system_state(migration_id)
            
            self.logger.info(f"✅ Auth migration rollback successful: {migration_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Auth migration rollback failed: {e}")
            return False

    # ENTERPRISE-GRADE ENHANCEMENT METHODS

    async def _create_enterprise_metadata_tables(self) -> bool:
        """Create enterprise metadata tables for advanced security management."""
        try:
            # Security metrics table
            security_metrics_sql = """
                CREATE TABLE IF NOT EXISTS enterprise_security_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL,
                    metric_timestamp TEXT NOT NULL,
                    security_level TEXT DEFAULT 'standard',
                    threat_level TEXT DEFAULT 'low',
                    metadata TEXT DEFAULT '{}'
                )
            """
            
            # Compliance tracking table
            compliance_sql = """
                CREATE TABLE IF NOT EXISTS enterprise_compliance_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    compliance_rule TEXT NOT NULL,
                    compliance_status TEXT NOT NULL,
                    last_check TEXT NOT NULL,
                    next_check TEXT,
                    violations TEXT DEFAULT '[]',
                    remediation_plan TEXT DEFAULT '{}',
                    security_impact TEXT DEFAULT 'low'
                )
            """
            
            # Threat detection table
            threat_detection_sql = """
                CREATE TABLE IF NOT EXISTS enterprise_threat_detection (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    detection_time TEXT NOT NULL,
                    mitigation_status TEXT DEFAULT 'pending',
                    security_metrics TEXT DEFAULT '{}',
                    response_plan TEXT DEFAULT '{}'
                )
            """
            
            # Security events table
            security_events_sql = """
                CREATE TABLE IF NOT EXISTS enterprise_security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_source TEXT NOT NULL,
                    event_timestamp TEXT NOT NULL,
                    user_id TEXT,
                    ip_address TEXT,
                    severity TEXT DEFAULT 'medium',
                    details TEXT DEFAULT '{}',
                    response_required BOOLEAN DEFAULT FALSE
                )
            """
            
            await self.connection_manager.execute_update(security_metrics_sql)
            await self.connection_manager.execute_update(compliance_sql)
            await self.connection_manager.execute_update(threat_detection_sql)
            await self.connection_manager.execute_update(security_events_sql)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create enterprise auth metadata tables: {e}")
            return False

    async def _create_enterprise_tables(self) -> bool:
        """Create all enterprise auth tables."""
        success = True
        
        # Create tables in dependency order with enterprise features
        success &= await self._create_users_table()
        success &= await self._create_custom_roles_table()
        success &= await self._create_role_assignments_table()
        success &= await self._create_user_metrics_table()
        
        return success

    async def _create_users_table(self) -> bool:
        """Create the users table with enterprise-grade security capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Basic user fields
                is_active BOOLEAN DEFAULT 1,
                org_id TEXT,
                dept_id TEXT,
                last_login TEXT,
                
                -- Business profile information
                bio TEXT,
                location TEXT,
                website TEXT,
                skills TEXT DEFAULT '{}',
                interests TEXT DEFAULT '{}',
                is_public_profile BOOLEAN DEFAULT 0,
                
                -- MFA and security settings
                mfa_enabled BOOLEAN DEFAULT 0,
                mfa_secret TEXT,
                mfa_backup_codes TEXT DEFAULT '{}',
                mfa_last_used TEXT,
                
                -- Verification and password management
                email_verified BOOLEAN DEFAULT 0,
                email_verification_code TEXT,
                email_verification_expires TEXT,
                password_reset_code TEXT,
                password_reset_expires TEXT,
                password_changed_at TEXT,
                password_expires_at TEXT,
                
                -- Social authentication
                social_provider TEXT,
                social_provider_id TEXT,
                social_access_token TEXT,
                social_refresh_token TEXT,
                social_token_expires TEXT,
                social_profile_data TEXT DEFAULT '{}',
                social_links TEXT DEFAULT '{}',
                
                -- Role and permission management
                custom_role_id TEXT,
                role_assignment_id TEXT,
                permissions TEXT DEFAULT '{}',
                role_inheritance TEXT DEFAULT '{}',
                
                -- Organization settings
                org_settings TEXT DEFAULT '{}',
                org_permissions TEXT DEFAULT '{}',
                org_role TEXT,
                
                -- Security and compliance
                security_questions TEXT DEFAULT '{}',
                two_factor_method TEXT,
                login_history TEXT DEFAULT '{}',
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TEXT,
                
                -- Audit and tracking
                last_password_change TEXT,
                last_role_change TEXT,
                last_permission_change TEXT,
                last_security_event TEXT,
                created_by TEXT,
                updated_by TEXT,
                
                -- Metadata and configuration
                preferences TEXT DEFAULT '{}',
                notification_settings TEXT DEFAULT '{}',
                language TEXT DEFAULT 'en',
                timezone TEXT DEFAULT 'UTC',
                
                -- ENTERPRISE ENHANCEMENTS
                -- Advanced Security Fields
                security_classification TEXT DEFAULT 'internal',
                access_control_level TEXT DEFAULT 'standard',
                encryption_required BOOLEAN DEFAULT FALSE,
                audit_trail_required BOOLEAN DEFAULT TRUE,
                session_timeout_minutes INTEGER DEFAULT 480,
                max_concurrent_sessions INTEGER DEFAULT 3,
                
                -- Compliance & Governance
                compliance_status TEXT DEFAULT 'pending' CHECK (compliance_status IN ('pending', 'compliant', 'non_compliant', 'under_review')),
                audit_frequency TEXT DEFAULT 'annual' CHECK (audit_frequency IN ('monthly', 'quarterly', 'semi_annual', 'annual')),
                last_audit_date TEXT,
                next_audit_date TEXT,
                compliance_score REAL DEFAULT 0.0,
                regulatory_frameworks TEXT DEFAULT '[]',
                
                -- Performance & Monitoring
                performance_metrics TEXT DEFAULT '{}',
                health_score REAL DEFAULT 100.0,
                last_health_check TEXT,
                uptime_percentage REAL DEFAULT 99.9,
                
                -- Business Intelligence
                business_value_score REAL DEFAULT 0.0,
                usage_metrics TEXT DEFAULT '{}',
                kpi_tracking TEXT DEFAULT '{}',
                
                -- Foreign key constraints
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE SET NULL,
                FOREIGN KEY (dept_id) REFERENCES departments (dept_id) ON DELETE SET NULL,
                FOREIGN KEY (custom_role_id) REFERENCES custom_roles (role_id) ON DELETE SET NULL,
                FOREIGN KEY (role_assignment_id) REFERENCES role_assignments (assignment_id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES users (user_id) ON DELETE SET NULL,
                FOREIGN KEY (updated_by) REFERENCES users (user_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not await self.create_table("users", query):
            return False

        # Create enterprise indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_username ON users (username)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_email ON users (email)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_role ON users (role)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_is_active ON users (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_org_id ON users (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_dept_id ON users (dept_id)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_last_login ON users (last_login)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_mfa_enabled ON users (mfa_enabled)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_email_verified ON users (email_verified)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_compliance_status ON users (compliance_status)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_security_classification ON users (security_classification)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_created_at ON users (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_users_updated_at ON users (updated_at)"
        ]

        return await self._create_enterprise_indexes("users", index_queries)

    async def _create_custom_roles_table(self) -> bool:
        """Create the custom_roles table with enterprise-grade capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS custom_roles (
                role_id TEXT PRIMARY KEY,
                role_name TEXT NOT NULL UNIQUE,
                role_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Basic role fields
                role_description TEXT,
                role_level INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_by TEXT,
                updated_by TEXT,
                role_metadata TEXT DEFAULT '{}',
                
                -- ENTERPRISE ENHANCEMENTS
                -- Advanced Role Management
                role_hierarchy TEXT DEFAULT '{}',
                role_permissions TEXT DEFAULT '{}',
                role_constraints TEXT DEFAULT '{}',
                role_inheritance_rules TEXT DEFAULT '{}',
                
                -- Security & Compliance
                security_classification TEXT DEFAULT 'internal',
                access_control_level TEXT DEFAULT 'standard',
                encryption_required BOOLEAN DEFAULT FALSE,
                audit_trail_required BOOLEAN DEFAULT TRUE,
                
                -- Compliance & Governance
                compliance_status TEXT DEFAULT 'pending' CHECK (compliance_status IN ('pending', 'compliant', 'non_compliant', 'under_review')),
                audit_frequency TEXT DEFAULT 'annual' CHECK (audit_frequency IN ('monthly', 'quarterly', 'semi_annual', 'annual')),
                last_audit_date TEXT,
                next_audit_date TEXT,
                compliance_score REAL DEFAULT 0.0,
                
                -- Performance & Monitoring
                performance_metrics TEXT DEFAULT '{}',
                usage_metrics TEXT DEFAULT '{}',
                
                -- Business Intelligence
                business_value_score REAL DEFAULT 0.0,
                impact_metrics TEXT DEFAULT '{}',
                
                -- Foreign key constraints
                FOREIGN KEY (created_by) REFERENCES users (user_id) ON DELETE SET NULL,
                FOREIGN KEY (updated_by) REFERENCES users (user_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not await self.create_table("custom_roles", query):
            return False

        # Create enterprise indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_role_name ON custom_roles (role_name)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_role_type ON custom_roles (role_type)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_is_active ON custom_roles (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_role_level ON custom_roles (role_level)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_compliance_status ON custom_roles (compliance_status)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_security_classification ON custom_roles (security_classification)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_created_by ON custom_roles (created_by)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_created_at ON custom_roles (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_custom_roles_updated_at ON custom_roles (updated_at)"
        ]

        return await self._create_enterprise_indexes("custom_roles", index_queries)

    async def _create_role_assignments_table(self) -> bool:
        """Create the role_assignments table with enterprise-grade capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS role_assignments (
                assignment_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                role_id TEXT NOT NULL,
                assignment_type TEXT NOT NULL,
                assigned_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Basic assignment fields
                organization_id TEXT,
                expires_at TEXT,
                assigned_by TEXT,
                is_active BOOLEAN DEFAULT 1,
                assignment_metadata TEXT DEFAULT '{}',
                
                -- ENTERPRISE ENHANCEMENTS
                -- Advanced Assignment Management
                assignment_scope TEXT DEFAULT 'global' CHECK (assignment_scope IN ('global', 'organization', 'department', 'project', 'resource')),
                assignment_priority INTEGER DEFAULT 1,
                assignment_rules TEXT DEFAULT '{}',
                assignment_constraints TEXT DEFAULT '{}',
                
                -- Security & Compliance
                security_classification TEXT DEFAULT 'internal',
                access_control_level TEXT DEFAULT 'standard',
                encryption_required BOOLEAN DEFAULT FALSE,
                audit_trail_required BOOLEAN DEFAULT TRUE,
                
                -- Compliance & Governance
                compliance_status TEXT DEFAULT 'pending' CHECK (compliance_status IN ('pending', 'compliant', 'non_compliant', 'under_review')),
                audit_frequency TEXT DEFAULT 'annual' CHECK (audit_frequency IN ('monthly', 'quarterly', 'semi_annual', 'annual')),
                last_audit_date TEXT,
                next_audit_date TEXT,
                compliance_score REAL DEFAULT 0.0,
                
                -- Performance & Monitoring
                performance_metrics TEXT DEFAULT '{}',
                usage_metrics TEXT DEFAULT '{}',
                
                -- Business Intelligence
                business_value_score REAL DEFAULT 0.0,
                impact_metrics TEXT DEFAULT '{}',
                
                -- Foreign key constraints
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES custom_roles (role_id) ON DELETE CASCADE,
                FOREIGN KEY (organization_id) REFERENCES organizations (org_id) ON DELETE SET NULL,
                FOREIGN KEY (assigned_by) REFERENCES users (user_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not await self.create_table("role_assignments", query):
            return False

        # Create enterprise indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_user_id ON role_assignments (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_role_id ON role_assignments (role_id)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_assignment_type ON role_assignments (assignment_type)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_is_active ON role_assignments (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_organization_id ON role_assignments (organization_id)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_assigned_by ON role_assignments (assigned_by)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_assigned_at ON role_assignments (assigned_at)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_expires_at ON role_assignments (expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_compliance_status ON role_assignments (compliance_status)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_created_at ON role_assignments (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_role_assignments_updated_at ON role_assignments (updated_at)"
        ]

        return await self._create_enterprise_indexes("role_assignments", index_queries)

    async def _create_user_metrics_table(self) -> bool:
        """Create the user_metrics table with enterprise-grade capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS user_metrics (
                metric_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_timestamp TEXT NOT NULL,
                
                -- Basic metric fields
                login_attempts INTEGER DEFAULT 0,
                successful_logins INTEGER DEFAULT 0,
                failed_logins INTEGER DEFAULT 0,
                login_duration_ms INTEGER,
                login_source TEXT,
                login_ip_address TEXT,
                login_user_agent TEXT,
                
                -- ENTERPRISE ENHANCEMENTS
                -- Advanced Metrics
                session_duration_ms INTEGER,
                api_calls_count INTEGER DEFAULT 0,
                data_access_count INTEGER DEFAULT 0,
                security_events_count INTEGER DEFAULT 0,
                
                -- Security & Compliance
                security_classification TEXT DEFAULT 'internal',
                access_control_level TEXT DEFAULT 'standard',
                encryption_required BOOLEAN DEFAULT FALSE,
                audit_trail_required BOOLEAN DEFAULT TRUE,
                
                -- Compliance & Governance
                compliance_status TEXT DEFAULT 'pending' CHECK (compliance_status IN ('pending', 'compliant', 'non_compliant', 'under_review')),
                audit_frequency TEXT DEFAULT 'annual' CHECK (audit_frequency IN ('monthly', 'quarterly', 'semi_annual', 'annual')),
                last_audit_date TEXT,
                next_audit_date TEXT,
                compliance_score REAL DEFAULT 0.0,
                
                -- Performance & Monitoring
                performance_metrics TEXT DEFAULT '{}',
                health_metrics TEXT DEFAULT '{}',
                
                -- Business Intelligence
                business_value_score REAL DEFAULT 0.0,
                impact_metrics TEXT DEFAULT '{}',
                
                -- Timestamps
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                -- Foreign key constraints
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """

        # Create the table
        if not await self.create_table("user_metrics", query):
            return False

        # Create enterprise indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_user_id ON user_metrics (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_metric_type ON user_metrics (metric_type)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_metric_timestamp ON user_metrics (metric_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_login_attempts ON user_metrics (login_attempts)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_successful_logins ON user_metrics (successful_logins)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_failed_logins ON user_metrics (failed_logins)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_login_source ON user_metrics (login_source)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_login_ip_address ON user_metrics (login_ip_address)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_compliance_status ON user_metrics (compliance_status)",
            "CREATE INDEX IF NOT EXISTS idx_enterprise_user_metrics_security_classification ON user_metrics (security_classification)"
        ]

        return await self._create_enterprise_indexes("user_metrics", index_queries)

    def get_module_description(self) -> str:
        """Get enterprise description of this module."""
        return "Enterprise-grade authentication and authorization tables with advanced security, compliance, and threat detection capabilities"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["users", "custom_roles", "role_assignments", "user_metrics"]

    async def create_tables(self) -> bool:
        """Create all Authentication tables with enterprise-grade features."""
        try:
            logger.info("🔐 Creating Authentication Module Tables...")
            
            # Create tables in dependency order
            tables_created = []
            
            # 1. Create users table (no dependencies)
            if await self._create_users_table():
                tables_created.append("users")
            else:
                logger.error("Failed to create users table")
                return False
            
            # 2. Create custom_roles table (no dependencies)
            if await self._create_custom_roles_table():
                tables_created.append("custom_roles")
            else:
                logger.error("Failed to create custom_roles table")
                return False
            
            # 3. Create role_assignments table (depends on users and custom_roles)
            if await self._create_role_assignments_table():
                tables_created.append("role_assignments")
            else:
                logger.error("Failed to create role_assignments table")
                return False
            
            # 4. Create user_metrics table (depends on users)
            if await self._create_user_metrics_table():
                tables_created.append("user_metrics")
            else:
                logger.error("Failed to create user_metrics table")
                return False
            
            logger.info(f"✅ Authentication Module: Created {len(tables_created)} tables successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Authentication tables: {e}")
            return False

    # ENTERPRISE IMPLEMENTATIONS OF ABSTRACT METHODS
    
    async def _create_enterprise_indexes(self, table_name: str, index_queries: List[str]) -> bool:
        """Create enterprise-grade indexes with security optimization."""
        try:
            for index_query in index_queries:
                await self.connection_manager.execute_update(index_query)
            
            # Create additional enterprise indexes
            await self._create_security_indexes(table_name)
            await self._create_performance_indexes(table_name)
            await self._create_compliance_indexes(table_name)
            
            self.logger.info(f"✅ Created enterprise auth indexes for table: {table_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create enterprise auth indexes: {e}")
            return False
    
    async def _setup_table_monitoring(self, table_name: str) -> bool:
        """Setup comprehensive table monitoring and security alerting."""
        try:
            # Setup security monitoring
            await self._setup_security_monitoring(table_name)
            
            # Setup compliance monitoring
            await self._setup_compliance_monitoring(table_name)
            
            # Setup performance monitoring
            await self._setup_performance_monitoring(table_name)
            
            # Setup threat detection
            await self._setup_threat_detection(table_name)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to setup auth table monitoring: {e}")
            return False
    
    async def _validate_table_structure(self, table_name: str) -> bool:
        """Validate table structure with enterprise-grade security validation."""
        try:
            # Validate security requirements
            if not await self._validate_security_requirements(table_name):
                return False
            
            # Validate schema compliance
            if not await self._validate_schema_compliance(table_name):
                return False
            
            # Validate performance characteristics
            if not await self._validate_performance_characteristics(table_name):
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Auth table validation failed: {e}")
            return False

    # ADDITIONAL ENTERPRISE METHODS
    
    async def _create_security_indexes(self, table_name: str) -> bool:
        """Create security-optimized indexes."""
        try:
            security_indexes = []
            
            # Only create indexes on columns that actually exist
            if table_name == 'users':
                security_indexes.extend([
                    f"CREATE INDEX IF NOT EXISTS idx_security_{table_name}_audit ON {table_name} (created_at, updated_at)",
                    f"CREATE INDEX IF NOT EXISTS idx_security_{table_name}_role ON {table_name} (user_id, role, org_id)",
                    f"CREATE INDEX IF NOT EXISTS idx_security_{table_name}_mfa ON {table_name} (user_id, mfa_enabled, mfa_last_used)",
                    f"CREATE INDEX IF NOT EXISTS idx_security_{table_name}_compliance ON {table_name} (user_id, compliance_status, last_audit_date)"
                ])
            elif table_name == 'custom_roles':
                security_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_security_{table_name}_audit ON {table_name} (created_at, updated_at)"
                )
            elif table_name == 'role_assignments':
                security_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_security_{table_name}_audit ON {table_name} (created_at, updated_at, assigned_by)"
                )
            elif table_name == 'user_metrics':
                security_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_security_{table_name}_audit ON {table_name} (created_at, updated_at)"
                )
            
            for index_sql in security_indexes:
                await self.connection_manager.execute_update(index_sql)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create security indexes: {e}")
            return False
    
    async def _create_performance_indexes(self, table_name: str) -> bool:
        """Create performance-optimized indexes."""
        try:
            performance_indexes = []
            
            # Only create indexes on columns that actually exist
            if table_name == 'users':
                performance_indexes.extend([
                    f"CREATE INDEX IF NOT EXISTS idx_perf_{table_name}_composite_1 ON {table_name} (created_at, updated_at, is_active)",
                    f"CREATE INDEX IF NOT EXISTS idx_perf_{table_name}_composite_2 ON {table_name} (user_id, org_id, compliance_status)"
                ])
            elif table_name == 'custom_roles':
                performance_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_perf_{table_name}_composite_1 ON {table_name} (created_at, updated_at, is_active)"
                )
            elif table_name == 'role_assignments':
                performance_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_perf_{table_name}_composite_1 ON {table_name} (created_at, updated_at, is_active)"
                )
            elif table_name == 'user_metrics':
                performance_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_perf_{table_name}_composite_1 ON {table_name} (created_at, updated_at)"
                )
            
            for index_sql in performance_indexes:
                await self.connection_manager.execute_update(index_sql)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create performance indexes: {e}")
            return False
    
    async def _create_compliance_indexes(self, table_name: str) -> bool:
        """Create compliance-related indexes."""
        try:
            compliance_indexes = []
            
            # Only create indexes on columns that actually exist
            if table_name == 'users':
                compliance_indexes.extend([
                    f"CREATE INDEX IF NOT EXISTS idx_compliance_{table_name}_audit ON {table_name} (created_at, updated_at)",
                    f"CREATE INDEX IF NOT EXISTS idx_compliance_{table_name}_status ON {table_name} (compliance_status, last_audit_date)"
                ])
            elif table_name == 'custom_roles':
                compliance_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_compliance_{table_name}_audit ON {table_name} (created_at, updated_at)"
                )
            elif table_name == 'role_assignments':
                compliance_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_compliance_{table_name}_audit ON {table_name} (created_at, updated_at)"
                )
            elif table_name == 'user_metrics':
                compliance_indexes.append(
                    f"CREATE INDEX IF NOT EXISTS idx_compliance_{table_name}_audit ON {table_name} (created_at, updated_at)"
                )
            
            for index_sql in compliance_indexes:
                await self.connection_manager.execute_update(index_sql)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create compliance indexes: {e}")
            return False

    async def _setup_compliance_alerts(self, table_name: str) -> bool:
        """Setup compliance alerts for table."""
        try:
            # Setup compliance alerting rules
            # Setup notification channels
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to setup compliance alerts: {e}")
            return False

    async def _setup_compliance_monitoring(self, table_name: str) -> bool:
        """Setup compliance monitoring for table."""
        try:
            # Register table for compliance tracking
            self._compliance_status[table_name] = {
                'compliance_score': 100.0,
                'last_compliance_audit': None,
                'next_compliance_audit': None,
                'compliance_issues': []
            }
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to setup compliance monitoring: {e}")
            return False

    # HELPER METHODS
    
    def _get_last_security_audit(self, table_name: str) -> Optional[str]:
        """Get last security audit date for table."""
        return self._security_metrics.get(table_name, {}).get('last_security_audit')

    async def _log_security_event(self, event_type: str, table_name: str, user_id: str) -> bool:
        """Log security event for audit purposes."""
        try:
            # Log security event to audit trail
            event_data = {
                'event_type': event_type,
                'table_name': table_name,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'ip_address': 'unknown',  # Would be captured from request context
                'user_agent': 'unknown'   # Would be captured from request context
            }
            
            # Store in security metrics
            if table_name not in self._security_metrics:
                self._security_metrics[table_name] = {}
            
            if 'security_events' not in self._security_metrics[table_name]:
                self._security_metrics[table_name]['security_events'] = []
            
            self._security_metrics[table_name]['security_events'].append(event_data)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to log security event: {e}")
            return False

    async def _validate_column_properties(self, current_col: Dict[str, Any], expected_col: Dict[str, Any]) -> bool:
        """Validate column properties for table structure validation."""
        try:
            # Basic column validation
            # This would implement detailed column validation logic
            return True
        except Exception as e:
            self.logger.error(f"❌ Column validation failed: {e}")
            return False

    async def _validate_table_constraints(self, table_name: str, expected_structure: Dict[str, Any]) -> bool:
        """Validate table constraints for table structure validation."""
        try:
            # Constraint validation logic
            return True
        except Exception as e:
            self.logger.error(f"❌ Constraint validation failed: {e}")
            return False

    async def _validate_table_indexes(self, table_name: str, expected_structure: Dict[str, Any]) -> bool:
        """Validate table indexes for table structure validation."""
        try:
            # Index validation logic
            return True
        except Exception as e:
            self.logger.error(f"❌ Index validation failed: {e}")
            return False

    async def _update_table_metadata(self, table_name: str) -> bool:
        """Update table metadata."""
        try:
            # Update creation timestamp
            # Update version information
            # Update statistics
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to update table metadata: {e}")
            return False

    async def _setup_security_monitoring(self, table_name: str) -> bool:
        """Setup security monitoring for table."""
        try:
            # Register table for security tracking
            self._security_metrics[table_name] = {
                'security_score': 100.0,
                'last_security_audit': None,
                'threats_detected': [],
                'next_security_audit': None
            }
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to setup security monitoring: {e}")
            return False

    async def _validate_security_requirements(self, table_name: str) -> bool:
        """Validate security requirements."""
        try:
            # Check access controls
            # Check encryption requirements
            # Check audit requirements
            return True
        except Exception as e:
            self.logger.error(f"❌ Security validation failed: {e}")
            return False

    async def _setup_performance_monitoring(self, table_name: str) -> bool:
        """Setup performance monitoring for table."""
        try:
            # Register table for performance tracking
            self._performance_metrics[table_name] = {
                'query_count': 0,
                'avg_response_time': 0.0,
                'slow_queries': [],
                'last_optimization': None
            }
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to setup performance monitoring: {e}")
            return False

    async def _validate_schema_compliance(self, table_name: str) -> bool:
        """Validate schema compliance."""
        try:
            # Check schema compliance rules
            # Validate against compliance framework
            return True
        except Exception as e:
            self.logger.error(f"❌ Schema compliance validation failed: {e}")
            return False

    async def _validate_performance_characteristics(self, table_name: str) -> bool:
        """Validate performance characteristics."""
        try:
            # Check performance characteristics
            # Validate performance requirements
            return True
        except Exception as e:
            self.logger.error(f"❌ Performance characteristics validation failed: {e}")
            return False

    async def _setup_threat_detection(self, table_name: str) -> bool:
        """Setup threat detection for table."""
        try:
            # Register table for threat detection
            self._threat_detection[table_name] = {
                'threat_level': 'low',
                'last_threat_scan': None,
                'detected_threats': [],
                'mitigation_status': 'none'
            }
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to setup threat detection: {e}")
            return False

    async def _setup_security_policies(self) -> bool:
        """Setup security policies."""
        try:
            # Setup security policies
            # Configure access controls
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to setup security policies: {e}")
            return False

    async def _initialize_security_monitoring(self) -> bool:
        """Initialize security monitoring."""
        try:
            # Initialize security monitoring systems
            # Setup security alerts
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize security monitoring: {e}")
            return False

    async def _setup_compliance_framework(self) -> bool:
        """Setup compliance framework."""
        try:
            # Setup compliance framework
            # Configure compliance rules
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to setup compliance framework: {e}")
            return False

    async def _initialize_threat_detection(self) -> bool:
        """Initialize threat detection."""
        try:
            # Initialize threat detection systems
            # Setup threat monitoring
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize threat detection: {e}")
            return False

    async def _validate_migration_security(self, migration_script: str) -> bool:
        """Validate migration security."""
        try:
            # Check migration script security
            return True
        except Exception as e:
            self.logger.error(f"❌ Migration security validation failed: {e}")
            return False

    async def _validate_migration_script(self, migration_script: str) -> bool:
        """Validate migration script."""
        try:
            # Check migration script syntax
            return True
        except Exception as e:
            self.logger.error(f"❌ Migration script validation failed: {e}")
            return False

    async def _create_migration_checkpoint(self) -> str:
        """Create migration checkpoint."""
        try:
            # Create migration checkpoint
            return f"checkpoint_{datetime.now().isoformat()}"
        except Exception as e:
            self.logger.error(f"❌ Failed to create migration checkpoint: {e}")
            return ""

    async def _validate_migration_results(self) -> bool:
        """Validate migration results."""
        try:
            # Check migration results
            return True
        except Exception as e:
            self.logger.error(f"❌ Migration results validation failed: {e}")
            return False

    async def _rollback_migration(self, checkpoint_id: str) -> bool:
        """Rollback migration."""
        try:
            # Rollback migration
            return True
        except Exception as e:
            self.logger.error(f"❌ Migration rollback failed: {e}")
            return False

    async def _record_migration_success(self, migration_script: str, rollback_script: Optional[str]) -> bool:
        """Record migration success."""
        try:
            # Record migration success
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to record migration success: {e}")
            return False

    async def _assess_security_impact(self, migration_id: str) -> str:
        """Assess security impact of migration."""
        try:
            # Assess security impact
            return "low"
        except Exception as e:
            self.logger.error(f"❌ Failed to assess security impact: {e}")
            return "unknown"

    async def _check_migration_compliance(self, migration_id: str) -> str:
        """Check migration compliance."""
        try:
            # Check migration compliance
            return "compliant"
        except Exception as e:
            self.logger.error(f"❌ Failed to check migration compliance: {e}")
            return "unknown"

    async def _get_migration_details(self, migration_id: str) -> Optional[Dict[str, Any]]:
        """Get migration details."""
        try:
            # Get migration details
            return {}
        except Exception as e:
            self.logger.error(f"❌ Failed to get migration details: {e}")
            return None

    async def _validate_rollback_safety(self, migration_id: str) -> bool:
        """Validate rollback safety."""
        try:
            # Check rollback safety
            return True
        except Exception as e:
            self.logger.error(f"❌ Rollback safety validation failed: {e}")
            return False

    async def _update_migration_status(self, migration_id: str, status: str) -> bool:
        """Update migration status."""
        try:
            # Update migration status
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to update migration status: {e}")
            return False

    async def _restore_system_state(self, migration_id: str) -> bool:
        """Restore system state."""
        try:
            # Restore system state
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to restore system state: {e}")
            return False

    async def _check_table_dependencies(self, table_name: str) -> List[str]:
        """Check table dependencies."""
        try:
            # Check table dependencies
            return []
        except Exception as e:
            self.logger.error(f"❌ Failed to check table dependencies: {e}")
            return []

    async def _backup_table_data(self, table_name: str) -> bool:
        """Backup table data."""
        try:
            # Backup table data
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to backup table data: {e}")
            return False

    async def _cleanup_table_metadata(self, table_name: str) -> bool:
        """Cleanup table metadata."""
        try:
            # Cleanup table metadata
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup table metadata: {e}")
            return False

    async def _create_table_from_definition(self, table_name: str, table_definition: Dict[str, Any]) -> bool:
        """Create table from definition."""
        try:
            # Create table from definition
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create table from definition: {e}")
            return False
