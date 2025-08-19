"""
Authentication and Authorization Schema Module
============================================

Defines tables for user authentication, authorization, and security metrics.
Follows the same 2-table pattern as other modules: Users (Registry) + User Metrics.
"""

import logging
from ..base_schema import BaseSchemaModule

logger = logging.getLogger(__name__)


class AuthSchema(BaseSchemaModule):
    """Authentication and authorization schema module"""
    
    def __init__(self, db_manager=None):
        super().__init__(db_manager)
    
    def create_tables(self) -> bool:
        """Create all authentication tables"""
        success = True
        
        # Create tables in dependency order
        success &= self._create_users_table()             # FIRST - no dependencies
        success &= self._create_custom_roles_table()      # Depends on users
        success &= self._create_role_assignments_table()  # Depends on users + custom_roles
        success &= self._create_user_metrics_table()      # Depends on users
        
        # Add foreign key constraints after all tables exist
        if success:
            success &= self._add_foreign_key_constraints()
        
        return success
    
    def get_module_description(self) -> str:
        return "Authentication and authorization system tables"
    
    def get_table_names(self) -> list:
        return ["custom_roles", "role_assignments", "users", "user_metrics"]
    
    def _create_custom_roles_table(self) -> bool:
        """Create the custom roles table for role management"""
        query = """
        CREATE TABLE IF NOT EXISTS custom_roles (
            role_id TEXT PRIMARY KEY,
            role_name TEXT UNIQUE NOT NULL,
            role_description TEXT,
            role_type TEXT NOT NULL,  -- system, custom, inherited
            role_level INTEGER DEFAULT 1,  -- Hierarchy level
            is_active BOOLEAN DEFAULT TRUE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            created_by TEXT,
            updated_by TEXT,
            role_metadata TEXT DEFAULT '{}',  -- JSON additional role data
            
            -- Foreign key constraints
            FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
        )
        """
        return self.create_table("custom_roles", query)
    
    def _create_role_assignments_table(self) -> bool:
        """Create the role assignments table for user-role mapping"""
        query = """
        CREATE TABLE IF NOT EXISTS role_assignments (
            assignment_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            organization_id TEXT,  -- Made nullable to avoid cross-module dependencies
            assignment_type TEXT NOT NULL,  -- direct, inherited, temporary
            assigned_at TEXT NOT NULL,
            expires_at TEXT,
            assigned_by TEXT,  -- Made nullable to handle cascade deletes properly
            is_active BOOLEAN DEFAULT TRUE,
            assignment_metadata TEXT DEFAULT '{}',  -- JSON additional assignment data
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            
            -- Foreign key constraints (only within auth module)
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES custom_roles(role_id),
            FOREIGN KEY (assigned_by) REFERENCES users(user_id) ON DELETE SET NULL
            -- Note: organization_id foreign key removed to avoid cross-module dependency
        )
        """
        return self.create_table("role_assignments", query)
    
    def _create_users_table(self) -> bool:
        """Create the consolidated users table with business + authentication data"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            -- Core user identification
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            org_id TEXT,
            last_login TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            
            -- Business profile information
            bio TEXT,
            location TEXT,
            website TEXT,
            skills TEXT DEFAULT '{}',  -- JSON object of skills: {"primary": ["Python", "SQL"], "secondary": ["JavaScript"]}
            interests TEXT DEFAULT '{}',  -- JSON object of interests: {"technical": ["AI", "ML"], "personal": ["reading"]}
            is_public_profile BOOLEAN DEFAULT FALSE,
            
            -- MFA and security settings
            mfa_enabled BOOLEAN DEFAULT FALSE,
            mfa_secret TEXT,
            mfa_backup_codes TEXT DEFAULT '{}',  -- JSON object of backup codes: {"codes": ["123456", "789012"], "used": ["123456"]}
            mfa_last_used TEXT,
            
            -- Verification and password management
            email_verified BOOLEAN DEFAULT FALSE,
            email_verification_code TEXT,
            email_verification_expires TEXT,
            password_reset_code TEXT,
            password_reset_expires TEXT,
            password_changed_at TEXT,
            password_expires_at TEXT,
            
            -- Social authentication
            social_provider TEXT,  -- google, github, etc.
            social_provider_id TEXT,
            social_access_token TEXT,
            social_refresh_token TEXT,
            social_token_expires TEXT,
            social_profile_data TEXT DEFAULT '{}',  -- JSON profile data
            social_links TEXT DEFAULT '{}',  -- JSON social media links
            
            -- Role and permission management
            custom_role_id TEXT,
            role_assignment_id TEXT,
            permissions TEXT DEFAULT '{}',  -- JSON object: {"read": true, "write": false, "admin": false}
            role_inheritance TEXT DEFAULT '{}',  -- JSON object: {"inherited_roles": ["user", "moderator"], "role_hierarchy": ["user", "moderator", "admin"]}
            
            -- Organization settings
            org_settings TEXT DEFAULT '{}',  -- JSON organization-specific settings
            org_permissions TEXT DEFAULT '{}',  -- JSON org-level permissions: {"read": true, "write": false}
            org_role TEXT,
            
            -- Security and compliance
            security_questions TEXT DEFAULT '{}',  -- JSON object: {"q1": {"question": "What was your first pet?", "answer": "hashed_answer"}, "q2": {"question": "City of birth?", "answer": "hashed_answer"}}
            two_factor_method TEXT,  -- sms, email, app, etc.
            login_history TEXT DEFAULT '{}',  -- JSON object: {"recent_logins": [{"timestamp": "2024-01-15T10:30:00Z", "ip": "192.168.1.1", "success": true, "location": "New York"}], "failed_attempts": [{"timestamp": "2024-01-15T09:00:00Z", "ip": "192.168.1.1", "reason": "wrong_password"}]}
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
            preferences TEXT DEFAULT '{}',  -- JSON user preferences: {"theme": "dark", "dashboard_layout": "grid", "default_view": "list"}
            notification_settings TEXT DEFAULT '{}',  -- JSON notification config: {"email": true, "sms": false, "push": true, "frequency": "immediate"}
            language TEXT DEFAULT 'en',
            timezone TEXT DEFAULT 'UTC',
            
            -- Foreign key constraints
            FOREIGN KEY (org_id) REFERENCES organizations(org_id),
            FOREIGN KEY (custom_role_id) REFERENCES custom_roles(role_id),
            FOREIGN KEY (role_assignment_id) REFERENCES role_assignments(assignment_id),
            FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
        )
        """
        return self.create_table("users", query)
    
    def _create_user_metrics_table(self) -> bool:
        """Create the user metrics table for performance and security tracking"""
        query = """
        CREATE TABLE IF NOT EXISTS user_metrics (
            -- Primary identification
            metric_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            metric_type TEXT NOT NULL,  -- login, password_change, role_change, etc.
            metric_timestamp TEXT NOT NULL,
            
            -- Authentication metrics
            login_attempts INTEGER DEFAULT 0,
            successful_logins INTEGER DEFAULT 0,
            failed_logins INTEGER DEFAULT 0,
            login_duration_ms INTEGER,  -- Time taken for login
            login_source TEXT,  -- web, mobile, api, etc.
            login_ip_address TEXT,
            login_user_agent TEXT,
            
            -- MFA metrics
            mfa_attempts INTEGER DEFAULT 0,
            mfa_successful INTEGER DEFAULT 0,
            mfa_failed INTEGER DEFAULT 0,
            mfa_method_used TEXT,  -- sms, email, app, backup_code
            mfa_response_time_ms INTEGER,
            
            -- Security metrics
            password_changes INTEGER DEFAULT 0,
            password_strength_score INTEGER,  -- 1-10 scale
            password_compliance_status TEXT,  -- compliant, non_compliant
            security_events_count INTEGER DEFAULT 0,
            security_event_types TEXT DEFAULT '{}',  -- JSON object of event types: {"failed_logins": 5, "password_resets": 2, "suspicious_activity": 1}
            
            -- Role and permission metrics
            role_changes INTEGER DEFAULT 0,
            permission_changes INTEGER DEFAULT 0,
            access_denied_count INTEGER DEFAULT 0,
            elevated_access_count INTEGER DEFAULT 0,
            
            -- Performance metrics
            response_time_ms INTEGER,
            session_duration_seconds INTEGER,
            concurrent_sessions INTEGER DEFAULT 0,
            peak_concurrent_users INTEGER DEFAULT 0,
            
            -- Compliance metrics
            gdpr_compliance_status TEXT,  -- compliant, non_compliant, pending
            data_retention_status TEXT,  -- active, archived, deleted
            audit_trail_completeness REAL,  -- 0.0-1.0 percentage
            compliance_score REAL,  -- 0.0-100.0 percentage
            
            -- Error and failure metrics
            error_count INTEGER DEFAULT 0,
            error_types TEXT DEFAULT '{}',  -- JSON object of error types: {"authentication": 3, "authorization": 1, "database": 2}
            failure_rate REAL,  -- 0.0-1.0 percentage
            recovery_time_ms INTEGER,
            
            -- User behavior metrics
            session_frequency REAL,  -- Average sessions per day
            feature_usage TEXT DEFAULT '{}',  -- JSON feature usage stats: {"dashboard_views": 15, "file_uploads": 3, "reports_generated": 2}
            user_engagement_score REAL,  -- 0.0-100.0 score
            last_activity TEXT,
            
            -- System health metrics
            system_uptime_percentage REAL,
            database_response_time_ms INTEGER,
            cache_hit_rate REAL,
            memory_usage_mb INTEGER,
            cpu_usage_percentage REAL,
            
            -- Business metrics
            user_retention_rate REAL,
            conversion_rate REAL,  -- For business-critical actions
            customer_satisfaction_score REAL,
            support_ticket_count INTEGER DEFAULT 0,
            
            -- Metadata
            metric_version TEXT DEFAULT '1.0',
            data_source TEXT,  -- system, external, manual
            confidence_score REAL,  -- 0.0-1.0 data quality score
            notes TEXT,
            
            -- Foreign key constraints
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """
        return self.create_table("user_metrics", query)
    
    def _drop_existing_tables(self) -> bool:
        """Drop existing auth tables to ensure clean recreation"""
        try:
            drop_queries = [
                "DROP TABLE IF EXISTS user_metrics",
                "DROP TABLE IF EXISTS users", 
                "DROP TABLE IF EXISTS role_assignments",
                "DROP TABLE IF EXISTS custom_roles"
            ]
            
            for query in drop_queries:
                self.db_manager.execute_query(query)
            
            logger.info("✅ Dropped existing auth tables")
            return True
        except Exception as e:
            logger.warning(f"Could not drop existing tables: {e}")
            return True  # Not critical for table creation
    
    def _add_foreign_key_constraints(self) -> bool:
        """Add any additional foreign key constraints after all tables are created"""
        # All foreign keys are now defined inline, so this method is minimal
        return True
