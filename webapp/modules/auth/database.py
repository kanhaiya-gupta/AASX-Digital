"""
Authentication Database Interface
================================

Uses the centralized database system directly, consistent with other modules.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import jwt
from passlib.context import CryptContext
import secrets
import json
import uuid

# Import centralized database system (same as other modules)
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.user_repository import UserRepository
from src.shared.repositories.organization_repository import OrganizationRepository
from src.shared.models.user import User as SharedUser

logger = logging.getLogger(__name__)

class AuthDatabase:
    """Authentication database using centralized system (consistent with other modules)"""
    
    def __init__(self):
        """Initialize with centralized database system (same pattern as other modules)"""
        try:
            # Create data directory and set database path (same as other modules)
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "aasx_database.db"
            
            # Initialize central database connection (same as other modules)
            self.connection_manager = DatabaseConnectionManager(db_path)
            self.db_manager = BaseDatabaseManager(self.connection_manager)
            
            # Initialize user repository (same as other modules)
            self.user_repo = UserRepository(self.db_manager)
            
            # Initialize organization repository
            self.org_repo = OrganizationRepository(self.db_manager)
            
            # Initialize password hashing
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # JWT settings
            self.secret_key = "your-secret-key-here"  # Should be from environment
            self.algorithm = "HS256"
            self.access_token_expire_minutes = 30
            
            # Create MFA-related tables if they don't exist
            self._create_mfa_tables()
            
            logger.info("✓ Auth Database initialized with centralized system")
            
        except Exception as e:
            logger.error(f"Error initializing Auth Database: {e}")
            raise

    def _create_mfa_tables(self):
        """Create MFA-related tables"""
        try:
            # Create mfa_backup_codes table
            mfa_backup_codes_sql = """
            CREATE TABLE IF NOT EXISTS mfa_backup_codes (
                code_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                backup_code TEXT NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                used_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
            self.db_manager.execute_query(mfa_backup_codes_sql)
            
            # Create user_verification_codes table
            user_verification_codes_sql = """
            CREATE TABLE IF NOT EXISTS user_verification_codes (
                code_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                code_type TEXT NOT NULL,
                code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                used_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
            self.db_manager.execute_query(user_verification_codes_sql)
            
            # Create social_accounts table
            social_accounts_sql = """
            CREATE TABLE IF NOT EXISTS social_accounts (
                account_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                provider_user_id TEXT NOT NULL,
                email TEXT,
                display_name TEXT,
                avatar_url TEXT,
                access_token TEXT,
                refresh_token TEXT,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
            self.db_manager.execute_query(social_accounts_sql)
            
            # Create password_history table
            password_history_sql = """
            CREATE TABLE IF NOT EXISTS password_history (
                history_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
            self.db_manager.execute_query(password_history_sql)
            
            # Create public_profiles table
            public_profiles_sql = """
            CREATE TABLE IF NOT EXISTS public_profiles (
                profile_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE,
                location TEXT,
                website TEXT,
                social_links TEXT DEFAULT '{}',
                skills TEXT DEFAULT '[]',
                interests TEXT DEFAULT '[]',
                is_public BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
            self.db_manager.execute_query(public_profiles_sql)
            
            # Create profile_verifications table
            profile_verifications_sql = """
            CREATE TABLE IF NOT EXISTS profile_verifications (
                verification_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                verification_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                verification_data TEXT DEFAULT '{}',
                verification_code TEXT,
                expires_at TEXT,
                verified_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
            self.db_manager.execute_query(profile_verifications_sql)
            
            # Create custom_roles table
            custom_roles_sql = """
            CREATE TABLE IF NOT EXISTS custom_roles (
                role_id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                permissions TEXT DEFAULT '[]',
                inherits_from TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
            )
            """
            self.db_manager.execute_query(custom_roles_sql)
            
            # Create role_assignments table
            role_assignments_sql = """
            CREATE TABLE IF NOT EXISTS role_assignments (
                assignment_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                role_id TEXT NOT NULL,
                organization_id TEXT NOT NULL,
                assigned_by TEXT NOT NULL,
                assigned_at TEXT NOT NULL,
                expires_at TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
            )
            """
            self.db_manager.execute_query(role_assignments_sql)
            
            # Create organization_settings table
            organization_settings_sql = """
            CREATE TABLE IF NOT EXISTS organization_settings (
                settings_id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL UNIQUE,
                branding TEXT DEFAULT '{}',
                configuration TEXT DEFAULT '{}',
                notifications TEXT DEFAULT '{}',
                security TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
            )
            """
            self.db_manager.execute_query(organization_settings_sql)
            
            # Create organization_analytics table
            organization_analytics_sql = """
            CREATE TABLE IF NOT EXISTS organization_analytics (
                analytics_id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL UNIQUE,
                user_analytics TEXT DEFAULT '{}',
                usage_analytics TEXT DEFAULT '{}',
                performance_metrics TEXT DEFAULT '{}',
                activity_insights TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
            )
            """
            self.db_manager.execute_query(organization_analytics_sql)
            
            # Create organization_billing table
            organization_billing_sql = """
            CREATE TABLE IF NOT EXISTS organization_billing (
                billing_id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL UNIQUE,
                subscription TEXT DEFAULT '{}',
                billing_info TEXT DEFAULT '{}',
                usage_billing TEXT DEFAULT '{}',
                payment_history TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
            )
            """
            self.db_manager.execute_query(organization_billing_sql)
            
            logger.info("✓ MFA and related tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating MFA tables: {e}")
            raise

    def _add_mfa_columns_to_users(self):
        """Add MFA-related columns and profile fields to users table if they don't exist"""
        try:
            # Check if columns exist
            check_columns_sql = "PRAGMA table_info(users)"
            results = self.db_manager.execute_query(check_columns_sql)
            existing_columns = [row['name'] for row in results]
            
            # Add missing columns
            columns_to_add = [
                ("email_verified", "BOOLEAN DEFAULT FALSE"),
                ("phone_verified", "BOOLEAN DEFAULT FALSE"),
                ("mfa_enabled", "BOOLEAN DEFAULT FALSE"),
                ("mfa_secret", "TEXT"),
                ("last_password_change", "TEXT"),
                ("failed_login_attempts", "INTEGER DEFAULT 0"),
                ("account_locked_until", "TEXT"),
                ("preferences", "TEXT DEFAULT '{}'"),
                ("avatar_url", "TEXT"),
                ("timezone", "TEXT DEFAULT 'UTC'"),
                ("language", "TEXT DEFAULT 'en'"),
                # New profile fields
                ("phone", "TEXT"),
                ("job_title", "TEXT"),
                ("department", "TEXT"),
                ("bio", "TEXT")
            ]
            
            for column_name, column_def in columns_to_add:
                if column_name not in existing_columns:
                    add_column_sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                    self.db_manager.execute_query(add_column_sql)
                    logger.info(f"✓ Added column {column_name} to users table")
                    
        except Exception as e:
            logger.error(f"Error adding columns to users table: {e}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[SharedUser]:
        """Get user by username using centralized repository"""
        try:
            return self.user_repo.get_by_username(username)
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[SharedUser]:
        """Get user by email using centralized repository"""
        try:
            return self.user_repo.get_by_email(email)
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[SharedUser]:
        """Get user by ID using centralized repository"""
        try:
            return self.user_repo.get_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def create_user(self, user_data: dict) -> Optional[SharedUser]:
        """Create a new user using centralized repository"""
        try:
            # Remove user_id if present (it's auto-generated)
            user_data.pop('user_id', None)
            
            # Map organization_id to org_id if present
            if 'organization_id' in user_data:
                user_data['org_id'] = user_data.pop('organization_id')
            
            # Extract password for separate handling
            password = user_data.pop('password', None)
            if not password:
                raise ValueError("Password is required")
            
            # Create user object (without password)
            user = SharedUser(**user_data)
            user.validate()
            
            # Save to database with password hash
            created_user = self.user_repo.create_with_password(user, password)
            logger.info(f"User created successfully: {created_user.username}")
            return created_user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def update_user(self, user_id: str, updates: dict) -> Optional[SharedUser]:
        """Update user using centralized repository"""
        try:
            # Hash password if provided
            if 'new_password' in updates:
                updates['password_hash'] = self.get_password_hash(updates['new_password'])
                del updates['new_password']
            
            updated_user = self.user_repo.update(user_id, updates)
            if updated_user:
                logger.info(f"User updated successfully: {updated_user.username}")
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            return self.user_repo.update_last_login(user_id)
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    def get_all_users(self) -> List[SharedUser]:
        """Get all users from the database"""
        try:
            return self.user_repo.get_all()
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def get_active_organizations(self) -> List:
        """Get all active organizations from the database"""
        try:
            return self.org_repo.get_active_organizations()
        except Exception as e:
            logger.error(f"Error getting active organizations: {e}")
            return []
    
    def get_active_users(self) -> List[SharedUser]:
        """Get all active users"""
        try:
            return self.user_repo.get_active_users()
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    def search_users(self, search_term: str) -> List[SharedUser]:
        """Search users by username, email, or full name"""
        try:
            return self.user_repo.search_users(search_term)
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def check_username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        try:
            return self.user_repo.check_username_exists(username)
        except Exception as e:
            logger.error(f"Error checking username existence: {e}")
            return False
    
    def check_email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        try:
            return self.user_repo.check_email_exists(email)
        except Exception as e:
            logger.error(f"Error checking email existence: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[SharedUser]:
        """Authenticate user with username and password"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return None
            
            # Get user with password hash from database
            query = "SELECT * FROM users WHERE username = ?"
            results = self.db_manager.execute_query(query, (username,))
            if not results:
                return None
            
            user_data = results[0]
            password_hash = user_data.get('password_hash')
            
            if not password_hash:
                return None
            
            # Verify password
            if self.verify_password(password, password_hash):
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def log_user_activity(self, user_id: str, activity_type: str, 
                         resource_type: str = None, resource_id: str = None, 
                         details: dict = None, ip_address: str = None, 
                         user_agent: str = None) -> bool:
        """Log user activity"""
        try:
            # This would typically go to a separate activity log table
            # For now, we'll just log it
            logger.info(f"User activity: {user_id} - {activity_type} - {resource_type} - {resource_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging user activity: {e}")
            return False
    
    def get_user_statistics(self, organization_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            return self.user_repo.get_user_statistics(organization_id)
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {}
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user (soft delete by setting is_active to False)"""
        try:
            updates = {"is_active": False}
            updated_user = self.user_repo.update(user_id, updates)
            if updated_user:
                logger.info(f"User deactivated successfully: {updated_user.username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    # ============================================================================
    # MFA-RELATED METHODS (Phase 2: Authentication Enhancement)
    # ============================================================================

    def update_user_mfa_secret(self, user_id: str, secret: str) -> bool:
        """Update user's MFA secret"""
        try:
            query = "UPDATE users SET mfa_secret = ?, mfa_enabled = TRUE WHERE user_id = ?"
            self.db_manager.execute_query(query, (secret, user_id))
            logger.info(f"MFA secret updated for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating MFA secret: {e}")
            return False

    def get_user_mfa_secret(self, user_id: str) -> Optional[str]:
        """Get user's MFA secret"""
        try:
            query = "SELECT mfa_secret FROM users WHERE user_id = ? AND mfa_enabled = TRUE"
            results = self.db_manager.execute_query(query, (user_id,))
            if results:
                return results[0].get('mfa_secret')
            return None
        except Exception as e:
            logger.error(f"Error getting MFA secret: {e}")
            return None

    def disable_user_mfa(self, user_id: str) -> bool:
        """Disable MFA for a user"""
        try:
            query = "UPDATE users SET mfa_enabled = FALSE, mfa_secret = NULL WHERE user_id = ?"
            self.db_manager.execute_query(query, (user_id,))
            logger.info(f"MFA disabled for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error disabling MFA: {e}")
            return False

    def get_user_mfa_status(self, user_id: str) -> Dict[str, Any]:
        """Get MFA status for a user"""
        try:
            query = "SELECT mfa_enabled, mfa_secret FROM users WHERE user_id = ?"
            results = self.db_manager.execute_query(query, (user_id,))
            if results:
                user_data = results[0]
                return {
                    "mfa_enabled": user_data.get('mfa_enabled', False),
                    "mfa_type": "totp" if user_data.get('mfa_secret') else None
                }
            return {"mfa_enabled": False, "mfa_type": None}
        except Exception as e:
            logger.error(f"Error getting MFA status: {e}")
            return {"mfa_enabled": False, "mfa_type": None}

    def store_backup_codes(self, user_id: str, codes: List[str]) -> bool:
        """Store backup codes for a user"""
        try:
            # First, delete existing backup codes
            delete_query = "DELETE FROM mfa_backup_codes WHERE user_id = ?"
            self.db_manager.execute_query(delete_query, (user_id,))
            
            # Insert new backup codes
            for code in codes:
                code_id = f"backup_{user_id}_{secrets.token_hex(8)}"
                insert_query = """
                    INSERT INTO mfa_backup_codes (code_id, user_id, backup_code, is_used, created_at)
                    VALUES (?, ?, ?, FALSE, ?)
                """
                self.db_manager.execute_query(insert_query, (code_id, user_id, code, datetime.now().isoformat()))
            
            logger.info(f"Backup codes stored for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing backup codes: {e}")
            return False

    def verify_backup_code(self, user_id: str, code: str) -> bool:
        """Verify a backup code"""
        try:
            query = """
                SELECT code_id FROM mfa_backup_codes 
                WHERE user_id = ? AND backup_code = ? AND is_used = FALSE
            """
            results = self.db_manager.execute_query(query, (user_id, code))
            if results:
                # Mark code as used
                code_id = results[0]['code_id']
                update_query = "UPDATE mfa_backup_codes SET is_used = TRUE, used_at = ? WHERE code_id = ?"
                self.db_manager.execute_query(update_query, (datetime.now().isoformat(), code_id))
                logger.info(f"Backup code used for user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error verifying backup code: {e}")
            return False

    def store_sms_verification_code(self, user_id: str, phone_number: str, code: str) -> bool:
        """Store SMS verification code"""
        try:
            # Store in a temporary table or use existing mechanism
            # For now, we'll use a simple approach
            query = """
                INSERT OR REPLACE INTO user_verification_codes 
                (user_id, code_type, code, expires_at)
                VALUES (?, 'sms', ?, ?)
            """
            expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
            self.db_manager.execute_query(query, (user_id, phone_number, code, expires_at))
            logger.info(f"SMS verification code stored for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing SMS verification code: {e}")
            return False

    def verify_sms_code(self, user_id: str, code: str) -> bool:
        """Verify SMS code"""
        try:
            query = """
                SELECT code_id FROM user_verification_codes 
                WHERE user_id = ? AND code_type = 'sms' AND code = ? 
                AND expires_at > ? AND is_used = FALSE
            """
            results = self.db_manager.execute_query(query, (user_id, code, datetime.now().isoformat()))
            if results:
                # Mark code as used
                code_id = results[0]['code_id']
                update_query = "UPDATE user_verification_codes SET is_used = TRUE, used_at = ? WHERE code_id = ?"
                self.db_manager.execute_query(update_query, (datetime.now().isoformat(), code_id))
                logger.info(f"SMS code verified for user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error verifying SMS code: {e}")
            return False

    def store_email_verification_code(self, user_id: str, email: str, code: str) -> bool:
        """Store email verification code"""
        try:
            query = """
                INSERT OR REPLACE INTO user_verification_codes 
                (user_id, code_type, code, expires_at)
                VALUES (?, 'email', ?, ?)
            """
            expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
            self.db_manager.execute_query(query, (user_id, email, code, expires_at))
            logger.info(f"Email verification code stored for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing email verification code: {e}")
            return False

    def verify_email_code(self, user_id: str, code: str) -> bool:
        """Verify email code"""
        try:
            query = """
                SELECT code_id FROM user_verification_codes 
                WHERE user_id = ? AND code_type = 'email' AND code = ? 
                AND expires_at > ? AND is_used = FALSE
            """
            results = self.db_manager.execute_query(query, (user_id, code, datetime.now().isoformat()))
            if results:
                # Mark code as used
                code_id = results[0]['code_id']
                update_query = "UPDATE user_verification_codes SET is_used = TRUE, used_at = ? WHERE code_id = ?"
                self.db_manager.execute_query(update_query, (datetime.now().isoformat(), code_id))
                logger.info(f"Email code verified for user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error verifying email code: {e}")
            return False

    # ============================================================================
    # SOCIAL ACCOUNT METHODS (Phase 2: Social Login Integration)
    # ============================================================================

    def get_user_by_social_account(self, provider: str, provider_user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by social account provider and provider user ID"""
        try:
            query = """
                SELECT u.* FROM users u
                JOIN social_accounts sa ON u.user_id = sa.user_id
                WHERE sa.provider = ? AND sa.provider_user_id = ?
            """
            results = self.db_manager.execute_query(query, (provider, provider_user_id))
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user by social account: {e}")
            return None

    def link_social_account(self, user_id: str, provider: str, user_info: Dict[str, Any], access_token: str) -> bool:
        """Link a social account to a user"""
        try:
            # Check if social account already exists
            existing_query = """
                SELECT account_id FROM social_accounts 
                WHERE provider = ? AND provider_user_id = ?
            """
            existing = self.db_manager.execute_query(existing_query, (provider, user_info["provider_user_id"]))
            
            if existing:
                # Update existing social account
                update_query = """
                    UPDATE social_accounts 
                    SET email = ?, display_name = ?, avatar_url = ?, access_token = ?, updated_at = ?
                    WHERE provider = ? AND provider_user_id = ?
                """
                self.db_manager.execute_query(update_query, (
                    user_info["email"],
                    user_info["display_name"],
                    user_info["avatar_url"],
                    access_token,
                    datetime.now().isoformat(),
                    provider,
                    user_info["provider_user_id"]
                ))
            else:
                # Create new social account
                insert_query = """
                    INSERT INTO social_accounts (
                        account_id, user_id, provider, provider_user_id, email, 
                        display_name, avatar_url, access_token, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                account_id = f"social_{provider}_{user_info['provider_user_id']}"
                self.db_manager.execute_query(insert_query, (
                    account_id,
                    user_id,
                    provider,
                    user_info["provider_user_id"],
                    user_info["email"],
                    user_info["display_name"],
                    user_info["avatar_url"],
                    access_token,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            
            logger.info(f"Social account linked for user: {user_id}, provider: {provider}")
            return True
        except Exception as e:
            logger.error(f"Error linking social account: {e}")
            return False

    def update_social_account(self, user_id: str, provider: str, user_info: Dict[str, Any], access_token: str) -> bool:
        """Update an existing social account"""
        try:
            update_query = """
                UPDATE social_accounts 
                SET email = ?, display_name = ?, avatar_url = ?, access_token = ?, updated_at = ?
                WHERE user_id = ? AND provider = ?
            """
            self.db_manager.execute_query(update_query, (
                user_info["email"],
                user_info["display_name"],
                user_info["avatar_url"],
                access_token,
                datetime.now().isoformat(),
                user_id,
                provider
            ))
            logger.info(f"Social account updated for user: {user_id}, provider: {provider}")
            return True
        except Exception as e:
            logger.error(f"Error updating social account: {e}")
            return False

    def get_user_social_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all social accounts for a user"""
        try:
            query = """
                SELECT provider, provider_user_id, email, display_name, avatar_url, created_at
                FROM social_accounts 
                WHERE user_id = ?
            """
            results = self.db_manager.execute_query(query, (user_id,))
            return results or []
        except Exception as e:
            logger.error(f"Error getting user social accounts: {e}")
            return []

    def unlink_social_account(self, user_id: str, provider: str) -> bool:
        """Unlink a social account from a user"""
        try:
            delete_query = "DELETE FROM social_accounts WHERE user_id = ? AND provider = ?"
            self.db_manager.execute_query(delete_query, (user_id, provider))
            logger.info(f"Social account unlinked for user: {user_id}, provider: {provider}")
            return True
        except Exception as e:
            logger.error(f"Error unlinking social account: {e}")
            return False

    # ============================================================================
    # RATE LIMITING AND SECURITY METHODS (Phase 4: Security Enhancement)
    # ============================================================================

    def increment_failed_login_attempts(self, username: str) -> bool:
        """Increment failed login attempts for a user"""
        try:
            update_query = """
                UPDATE users 
                SET failed_login_attempts = failed_login_attempts + 1 
                WHERE username = ?
            """
            self.db_manager.execute_query(update_query, (username,))
            logger.info(f"Incremented failed login attempts for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error incrementing failed login attempts: {e}")
            return False

    def reset_failed_login_attempts(self, username: str) -> bool:
        """Reset failed login attempts for a user"""
        try:
            update_query = """
                UPDATE users 
                SET failed_login_attempts = 0 
                WHERE username = ?
            """
            self.db_manager.execute_query(update_query, (username,))
            logger.info(f"Reset failed login attempts for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error resetting failed login attempts: {e}")
            return False

    def update_user_lockout(self, username: str, lockout_until: datetime) -> bool:
        """Update user lockout until timestamp"""
        try:
            update_query = """
                UPDATE users 
                SET account_locked_until = ? 
                WHERE username = ?
            """
            self.db_manager.execute_query(update_query, (lockout_until.isoformat(), username))
            logger.info(f"Updated lockout for user: {username} until {lockout_until}")
            return True
        except Exception as e:
            logger.error(f"Error updating user lockout: {e}")
            return False

    def unlock_account(self, username: str) -> bool:
        """Unlock a user account"""
        try:
            update_query = """
                UPDATE users 
                SET account_locked_until = NULL, failed_login_attempts = 0 
                WHERE username = ?
            """
            self.db_manager.execute_query(update_query, (username,))
            logger.info(f"Unlocked account for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error unlocking account: {e}")
            return False

    def get_user_security_status(self, username: str) -> Dict[str, Any]:
        """Get user security status including failed attempts and lockout"""
        try:
            query = """
                SELECT failed_login_attempts, account_locked_until 
                FROM users 
                WHERE username = ?
            """
            result = self.db_manager.execute_query(query, (username,))
            if result:
                user_data = result[0]
                return {
                    'failed_login_attempts': user_data.get('failed_login_attempts', 0),
                    'account_locked_until': user_data.get('account_locked_until'),
                    'is_locked': user_data.get('account_locked_until') is not None
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting user security status: {e}")
            return {}

    def log_security_event(self, user_id: str, event_type: str, ip_address: str = None, 
                          user_agent: str = None, details: dict = None) -> bool:
        """Log a security event"""
        try:
            # Use the existing log_user_activity method with security event type
            return self.log_user_activity(
                user_id=user_id,
                activity_type=f"security_{event_type}",
                resource_type="security",
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            return False
    
    def get_user_activity_logs(self, user_id: str = None, activity_type: str = None,
                              start_date: datetime = None, end_date: datetime = None,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get user activity logs with optional filtering
        
        Args:
            user_id: Filter by user ID
            activity_type: Filter by activity type
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of logs to return
        """
        try:
            # Build query conditions
            conditions = []
            params = []
            
            if user_id:
                conditions.append("user_id = ?")
                params.append(user_id)
            
            if activity_type:
                conditions.append("activity_type LIKE ?")
                params.append(f"%{activity_type}%")
            
            if start_date:
                conditions.append("created_at >= ?")
                params.append(start_date.isoformat())
            
            if end_date:
                conditions.append("created_at <= ?")
                params.append(end_date.isoformat())
            
            # Build query
            query = """
                SELECT user_id, activity_type, resource_type, resource_id, 
                       details, ip_address, user_agent, created_at
                FROM user_activity_log
            """
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            # Execute query
            results = self.db_manager.execute_query(query, tuple(params))
            
            # Parse results
            logs = []
            for row in results:
                try:
                    details = json.loads(row['details']) if row['details'] else {}
                except:
                    details = {}
                
                logs.append({
                    'user_id': row['user_id'],
                    'activity_type': row['activity_type'],
                    'resource_type': row['resource_type'],
                    'resource_id': row['resource_id'],
                    'details': details,
                    'ip_address': row['ip_address'],
                    'user_agent': row['user_agent'],
                    'created_at': row['created_at'],
                    'timestamp': row['created_at']
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting user activity logs: {e}")
            return []
    
    def cleanup_old_activity_logs(self, cutoff_date: datetime) -> bool:
        """
        Clean up old activity logs
        
        Args:
            cutoff_date: Date before which logs should be deleted
        """
        try:
            delete_query = """
                DELETE FROM user_activity_log 
                WHERE created_at < ?
            """
            
            self.db_manager.execute_query(delete_query, (cutoff_date.isoformat(),))
            
            logger.info(f"Cleaned up activity logs older than {cutoff_date}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up old activity logs: {e}")
            return False
    
    def get_audit_logs_summary(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Get summary of audit logs for reporting
        
        Args:
            start_date: Start date for summary
            end_date: End date for summary
        """
        try:
            conditions = []
            params = []
            
            if start_date:
                conditions.append("created_at >= ?")
                params.append(start_date.isoformat())
            
            if end_date:
                conditions.append("created_at <= ?")
                params.append(end_date.isoformat())
            
            # Build query
            query = """
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(DISTINCT user_id) as unique_users,
                    activity_type,
                    COUNT(*) as event_count
                FROM user_activity_log
            """
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " GROUP BY activity_type ORDER BY event_count DESC"
            
            # Execute query
            results = self.db_manager.execute_query(query, tuple(params))
            
            # Process results
            summary = {
                'total_events': 0,
                'unique_users': 0,
                'event_types': {},
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
            
            for row in results:
                summary['total_events'] += row['event_count']
                summary['event_types'][row['activity_type']] = row['event_count']
            
            # Get unique users count
            unique_users_query = """
                SELECT COUNT(DISTINCT user_id) as unique_users
                FROM user_activity_log
            """
            
            if conditions:
                unique_users_query += " WHERE " + " AND ".join(conditions)
            
            unique_users_result = self.db_manager.execute_query(unique_users_query, tuple(params))
            if unique_users_result:
                summary['unique_users'] = unique_users_result[0]['unique_users']
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting audit logs summary: {e}")
            return {}
    
    def get_security_events_summary(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get summary of security events"""
        try:
            # Build query with optional date filtering
            query = """
                SELECT 
                    activity_type,
                    COUNT(*) as count,
                    MIN(created_at) as first_event,
                    MAX(created_at) as last_event
                FROM user_activity_log 
                WHERE activity_type IN ('login_failed', 'login_success', 'password_changed', 'account_locked', 'mfa_enabled', 'mfa_disabled')
            """
            params = []
            
            if start_date or end_date:
                query += " AND 1=1"  # Placeholder for date conditions
                if start_date:
                    query = query.replace("AND 1=1", "AND created_at >= ? AND 1=1")
                    params.append(start_date.isoformat())
                if end_date:
                    query = query.replace("AND 1=1", "AND created_at <= ? AND 1=1")
                    params.append(end_date.isoformat())
            
            query += " GROUP BY activity_type ORDER BY count DESC"
            
            results = self.db_manager.execute_query(query, tuple(params))
            
            # Process results
            summary = {
                'total_events': sum(row['count'] for row in results),
                'events_by_type': {row['activity_type']: {
                    'count': row['count'],
                    'first_event': row['first_event'],
                    'last_event': row['last_event']
                } for row in results}
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting security events summary: {e}")
            return {}

    # Password History and Expiration Methods
    def store_password_history(self, user_id: str, password_hash: str) -> bool:
        """Store password in history"""
        try:
            history_id = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()
            
            query = """
                INSERT INTO password_history (history_id, user_id, password_hash, created_at)
                VALUES (?, ?, ?, ?)
            """
            self.db_manager.execute_query(query, (history_id, user_id, password_hash, created_at))
            
            logger.info(f"✓ Password history stored for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing password history: {e}")
            return False

    def get_password_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get password history for a user"""
        try:
            query = """
                SELECT history_id, password_hash, created_at
                FROM password_history 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            results = self.db_manager.execute_query(query, (user_id, limit))
            
            return [
                {
                    'history_id': row['history_id'],
                    'password_hash': row['password_hash'],
                    'created_at': row['created_at']
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting password history: {e}")
            return []

    def check_password_in_history(self, user_id: str, password_hash: str, limit: int = 5) -> bool:
        """Check if password exists in recent history"""
        try:
            query = """
                SELECT COUNT(*) as count
                FROM password_history 
                WHERE user_id = ? AND password_hash = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            results = self.db_manager.execute_query(query, (user_id, password_hash, limit))
            
            return results[0]['count'] > 0 if results else False
            
        except Exception as e:
            logger.error(f"Error checking password history: {e}")
            return False

    def update_password_with_history(self, user_id: str, new_password: str) -> bool:
        """Update password and store in history"""
        try:
            # Get current password hash before updating
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            # Hash the new password
            new_password_hash = self.get_password_hash(new_password)
            
            # Check if password is in recent history
            if self.check_password_in_history(user_id, new_password_hash, limit=5):
                logger.warning(f"Password reuse detected for user {user_id}")
                return False
            
            # Update password in users table
            update_query = """
                UPDATE users 
                SET password_hash = ?, last_password_change = ?
                WHERE user_id = ?
            """
            current_time = datetime.utcnow().isoformat()
            self.db_manager.execute_query(update_query, (new_password_hash, current_time, user_id))
            
            # Store in password history
            self.store_password_history(user_id, new_password_hash)
            
            logger.info(f"✓ Password updated and stored in history for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating password with history: {e}")
            return False

    def check_password_expiration(self, user_id: str, max_days: int = 90) -> Dict[str, Any]:
        """Check if password has expired"""
        try:
            query = """
                SELECT last_password_change
                FROM users 
                WHERE user_id = ?
            """
            results = self.db_manager.execute_query(query, (user_id,))
            
            if not results or not results[0]['last_password_change']:
                # No password change recorded, consider as expired
                return {
                    'expired': True,
                    'days_remaining': 0,
                    'last_change': None,
                    'expires_at': None
                }
            
            last_change = datetime.fromisoformat(results[0]['last_password_change'].replace('Z', '+00:00'))
            current_time = datetime.utcnow()
            days_since_change = (current_time - last_change).days
            days_remaining = max_days - days_since_change
            
            expires_at = last_change + timedelta(days=max_days)
            
            return {
                'expired': days_remaining <= 0,
                'days_remaining': max(0, days_remaining),
                'last_change': last_change.isoformat(),
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking password expiration: {e}")
            return {
                'expired': False,
                'days_remaining': max_days,
                'last_change': None,
                'expires_at': None
            }

    def cleanup_old_password_history(self, days_to_keep: int = 365) -> bool:
        """Clean up old password history records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_date_str = cutoff_date.isoformat()
            
            query = """
                DELETE FROM password_history 
                WHERE created_at < ?
            """
            self.db_manager.execute_query(query, (cutoff_date_str,))
            
            logger.info(f"Cleaned up password history older than {days_to_keep} days")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up password history: {e}")
            return False

    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences from database"""
        try:
            query = "SELECT preferences FROM users WHERE user_id = ?"
            results = self.db_manager.execute_query(query, (user_id,))
            
            if not results:
                return None
            
            preferences_json = results[0].get('preferences', '{}')
            if not preferences_json:
                return {}
            
            try:
                preferences = json.loads(preferences_json)
                return preferences
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in preferences for user {user_id}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences in database"""
        try:
            # Get current preferences
            current_preferences = self.get_user_preferences(user_id) or {}
            
            # Merge with new preferences
            updated_preferences = {**current_preferences, **preferences}
            
            # Convert to JSON
            preferences_json = json.dumps(updated_preferences)
            
            # Update database
            query = "UPDATE users SET preferences = ? WHERE user_id = ?"
            self.db_manager.execute_query(query, (preferences_json, user_id))
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False

    def reset_user_preferences(self, user_id: str) -> bool:
        """Reset user preferences to default"""
        try:
            # Set preferences to empty JSON object
            query = "UPDATE users SET preferences = '{}' WHERE user_id = ?"
            self.db_manager.execute_query(query, (user_id,))
            
            logger.info(f"Reset preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting user preferences: {e}")
            return False

    def get_user_preferences_by_key(self, user_id: str, key: str) -> Optional[Any]:
        """Get a specific preference value for a user"""
        try:
            preferences = self.get_user_preferences(user_id)
            if preferences is None:
                return None
            
            return preferences.get(key)
            
        except Exception as e:
            logger.error(f"Error getting user preference {key}: {e}")
            return None

    def set_user_preference(self, user_id: str, key: str, value: Any) -> bool:
        """Set a specific preference value for a user"""
        try:
            preferences = self.get_user_preferences(user_id) or {}
            preferences[key] = value
            
            return self.update_user_preferences(user_id, preferences)
            
        except Exception as e:
            logger.error(f"Error setting user preference {key}: {e}")
            return False

    # Public Profiles Methods
    def get_public_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get public profile for a user"""
        try:
            # Get user information
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Get public profile data
            query = "SELECT * FROM public_profiles WHERE user_id = ?"
            results = self.db_manager.execute_query(query, (user_id,))
            
            public_profile = {
                "user_id": user.user_id,
                "username": user.username,
                "full_name": user.full_name,
                "job_title": getattr(user, 'job_title', None),
                "department": getattr(user, 'department', None),
                "bio": getattr(user, 'bio', None),
                "avatar_url": getattr(user, 'avatar_url', None),
                "organization_name": None,
                "location": None,
                "website": None,
                "social_links": {},
                "skills": [],
                "interests": [],
                "is_public": False,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
            # Get organization name
            if user.org_id:
                org_query = "SELECT name FROM organizations WHERE org_id = ?"
                org_results = self.db_manager.execute_query(org_query, (user.org_id,))
                if org_results:
                    public_profile["organization_name"] = org_results[0].get('name')
            
            # Get public profile data if exists
            if results:
                profile_data = results[0]
                public_profile.update({
                    "location": profile_data.get('location'),
                    "website": profile_data.get('website'),
                    "social_links": json.loads(profile_data.get('social_links', '{}')),
                    "skills": json.loads(profile_data.get('skills', '[]')),
                    "interests": json.loads(profile_data.get('interests', '[]')),
                    "is_public": profile_data.get('is_public', False),
                    "created_at": profile_data.get('created_at'),
                    "updated_at": profile_data.get('updated_at')
                })
            
            return public_profile
            
        except Exception as e:
            logger.error(f"Error getting public profile for user {user_id}: {e}")
            return None

    def create_public_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Create or update public profile for a user"""
        try:
            # Check if profile already exists
            existing_query = "SELECT profile_id FROM public_profiles WHERE user_id = ?"
            existing_results = self.db_manager.execute_query(existing_query, (user_id,))
            
            current_time = datetime.now().isoformat()
            
            if existing_results:
                # Update existing profile
                update_query = """
                    UPDATE public_profiles 
                    SET location = ?, website = ?, social_links = ?, skills = ?, 
                        interests = ?, is_public = ?, updated_at = ?
                    WHERE user_id = ?
                """
                self.db_manager.execute_query(update_query, (
                    profile_data.get('location'),
                    profile_data.get('website'),
                    json.dumps(profile_data.get('social_links', {})),
                    json.dumps(profile_data.get('skills', [])),
                    json.dumps(profile_data.get('interests', [])),
                    profile_data.get('is_public', False),
                    current_time,
                    user_id
                ))
            else:
                # Create new profile
                profile_id = str(uuid.uuid4())
                insert_query = """
                    INSERT INTO public_profiles (
                        profile_id, user_id, location, website, social_links, 
                        skills, interests, is_public, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.db_manager.execute_query(insert_query, (
                    profile_id,
                    user_id,
                    profile_data.get('location'),
                    profile_data.get('website'),
                    json.dumps(profile_data.get('social_links', {})),
                    json.dumps(profile_data.get('skills', [])),
                    json.dumps(profile_data.get('interests', [])),
                    profile_data.get('is_public', False),
                    current_time,
                    current_time
                ))
            
            logger.info(f"✓ Public profile {'updated' if existing_results else 'created'} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating/updating public profile for user {user_id}: {e}")
            return False

    def update_public_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update public profile for a user"""
        return self.create_public_profile(user_id, profile_data)

    def delete_public_profile(self, user_id: str) -> bool:
        """Delete public profile for a user"""
        try:
            query = "DELETE FROM public_profiles WHERE user_id = ?"
            self.db_manager.execute_query(query, (user_id,))
            
            logger.info(f"✓ Public profile deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting public profile for user {user_id}: {e}")
            return False

    def get_public_profiles(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all public profiles"""
        try:
            query = """
                SELECT 
                    u.user_id, u.username, u.full_name, u.job_title, u.department, u.bio,
                    u.avatar_url, u.organization_id, u.created_at, u.updated_at,
                    pp.location, pp.website, pp.social_links, pp.skills, pp.interests, pp.is_public,
                    o.name as organization_name
                FROM users u
                LEFT JOIN public_profiles pp ON u.user_id = pp.user_id
                LEFT JOIN organizations o ON u.organization_id = o.organization_id
                WHERE pp.is_public = TRUE
                ORDER BY u.created_at DESC
                LIMIT ? OFFSET ?
            """
            results = self.db_manager.execute_query(query, (limit, offset))
            return self._process_public_profiles_results(results)
        except Exception as e:
            logger.error(f"Error getting public profiles: {e}")
            return []

    def search_public_profiles(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search public profiles by various fields"""
        try:
            query = """
                SELECT 
                    u.user_id, u.username, u.full_name, u.job_title, u.department, u.bio,
                    u.avatar_url, u.organization_id, u.created_at, u.updated_at,
                    pp.location, pp.website, pp.social_links, pp.skills, pp.interests, pp.is_public,
                    o.name as organization_name
                FROM users u
                LEFT JOIN public_profiles pp ON u.user_id = pp.user_id
                LEFT JOIN organizations o ON u.organization_id = o.organization_id
                WHERE pp.is_public = TRUE AND (
                    u.username LIKE ? OR 
                    u.full_name LIKE ? OR 
                    u.job_title LIKE ? OR 
                    u.department LIKE ? OR 
                    u.bio LIKE ? OR 
                    pp.location LIKE ? OR 
                    pp.skills LIKE ? OR 
                    pp.interests LIKE ?
                )
                ORDER BY u.created_at DESC
                LIMIT ?
            """
            search_pattern = f"%{search_term}%"
            results = self.db_manager.execute_query(query, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern, search_pattern, search_pattern, search_pattern, limit
            ))
            return self._process_public_profiles_results(results)
        except Exception as e:
            logger.error(f"Error searching public profiles: {e}")
            return []

    def _process_public_profiles_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process public profiles results"""
        processed_results = []
        for row in results:
            # Parse JSON fields
            social_links = {}
            if row.get('social_links'):
                try:
                    social_links = json.loads(row['social_links'])
                except (json.JSONDecodeError, TypeError):
                    pass

            skills = []
            if row.get('skills'):
                try:
                    skills = json.loads(row['skills'])
                except (json.JSONDecodeError, TypeError):
                    pass

            interests = []
            if row.get('interests'):
                try:
                    interests = json.loads(row['interests'])
                except (json.JSONDecodeError, TypeError):
                    pass

            processed_results.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'full_name': row['full_name'],
                'job_title': row['job_title'],
                'department': row['department'],
                'bio': row['bio'],
                'avatar_url': row['avatar_url'],
                'organization_name': row['organization_name'],
                'location': row['location'],
                'website': row['website'],
                'social_links': social_links,
                'skills': skills,
                'interests': interests,
                'is_public': row['is_public'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        return processed_results

    # Profile Verification Methods
    def create_profile_verification(self, user_id: str, verification_type: str, 
                                  verification_data: Dict[str, Any] = None) -> bool:
        """Create a new profile verification record"""
        try:
            verification_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Generate verification code for email/phone
            verification_code = None
            expires_at = None
            if verification_type in ['email', 'phone']:
                verification_code = secrets.token_hex(3).upper()
                expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
            
            query = """
                INSERT INTO profile_verifications 
                (verification_id, user_id, verification_type, status, verification_data, 
                 verification_code, expires_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db_manager.execute_query(query, (
                verification_id, user_id, verification_type, 'pending',
                json.dumps(verification_data or {}), verification_code, expires_at, now, now
            ))
            
            logger.info(f"Profile verification created for user {user_id}, type: {verification_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating profile verification: {e}")
            return False

    def get_profile_verification(self, user_id: str, verification_type: str) -> Optional[Dict[str, Any]]:
        """Get profile verification by user_id and type"""
        try:
            query = """
                SELECT * FROM profile_verifications 
                WHERE user_id = ? AND verification_type = ?
                ORDER BY created_at DESC LIMIT 1
            """
            results = self.db_manager.execute_query(query, (user_id, verification_type))
            
            if results:
                row = results[0]
                verification_data = {}
                if row.get('verification_data'):
                    try:
                        verification_data = json.loads(row['verification_data'])
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                return {
                    'verification_id': row['verification_id'],
                    'user_id': row['user_id'],
                    'verification_type': row['verification_type'],
                    'status': row['status'],
                    'verification_data': verification_data,
                    'verification_code': row['verification_code'],
                    'expires_at': row['expires_at'],
                    'verified_at': row['verified_at'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting profile verification: {e}")
            return None

    def verify_profile_verification(self, user_id: str, verification_type: str, 
                                  verification_code: str = None) -> bool:
        """Verify a profile verification"""
        try:
            verification = self.get_profile_verification(user_id, verification_type)
            if not verification:
                return False
            
            # Check if verification is expired
            if verification['expires_at'] and verification['expires_at'] < datetime.now().isoformat():
                # Update status to expired
                self.update_profile_verification_status(verification['verification_id'], 'expired')
                return False
            
            # For email/phone verification, check the code
            if verification_type in ['email', 'phone'] and verification_code:
                if verification['verification_code'] != verification_code:
                    return False
            
            # Update verification status
            now = datetime.now().isoformat()
            query = """
                UPDATE profile_verifications 
                SET status = 'verified', verified_at = ?, updated_at = ?
                WHERE verification_id = ?
            """
            self.db_manager.execute_query(query, (now, now, verification['verification_id']))
            
            # Update user table verification status
            if verification_type == 'email':
                self.db_manager.execute_query(
                    "UPDATE users SET email_verified = TRUE WHERE user_id = ?", 
                    (user_id,)
                )
            elif verification_type == 'phone':
                self.db_manager.execute_query(
                    "UPDATE users SET phone_verified = TRUE WHERE user_id = ?", 
                    (user_id,)
                )
            
            logger.info(f"Profile verification completed for user {user_id}, type: {verification_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying profile verification: {e}")
            return False

    def update_profile_verification_status(self, verification_id: str, status: str) -> bool:
        """Update profile verification status"""
        try:
            query = """
                UPDATE profile_verifications 
                SET status = ?, updated_at = ?
                WHERE verification_id = ?
            """
            self.db_manager.execute_query(query, (status, datetime.now().isoformat(), verification_id))
            return True
        except Exception as e:
            logger.error(f"Error updating profile verification status: {e}")
            return False

    def get_profile_verification_status(self, user_id: str) -> Dict[str, Any]:
        """Get overall profile verification status for a user"""
        try:
            # Get all verification types for the user
            query = """
                SELECT verification_type, status, verified_at 
                FROM profile_verifications 
                WHERE user_id = ? AND status = 'verified'
            """
            results = self.db_manager.execute_query(query, (user_id,))
            
            # Initialize status
            status = {
                'user_id': user_id,
                'email_verified': False,
                'phone_verified': False,
                'identity_verified': False,
                'address_verified': False,
                'overall_verification_status': 'unverified',
                'verification_score': 0,
                'last_verification_update': None
            }
            
            # Update based on verified types
            verified_count = 0
            last_update = None
            
            for row in results:
                verification_type = row['verification_type']
                if verification_type == 'email':
                    status['email_verified'] = True
                    verified_count += 1
                elif verification_type == 'phone':
                    status['phone_verified'] = True
                    verified_count += 1
                elif verification_type == 'identity':
                    status['identity_verified'] = True
                    verified_count += 1
                elif verification_type == 'address':
                    status['address_verified'] = True
                    verified_count += 1
                
                if row['verified_at'] and (not last_update or row['verified_at'] > last_update):
                    last_update = row['verified_at']
            
            # Calculate overall status and score
            if verified_count == 0:
                status['overall_verification_status'] = 'unverified'
                status['verification_score'] = 0
            elif verified_count < 4:
                status['overall_verification_status'] = 'partial'
                status['verification_score'] = verified_count * 25
            else:
                status['overall_verification_status'] = 'verified'
                status['verification_score'] = 100
            
            status['last_verification_update'] = last_update
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting profile verification status: {e}")
            return {
                'user_id': user_id,
                'email_verified': False,
                'phone_verified': False,
                'identity_verified': False,
                'address_verified': False,
                'overall_verification_status': 'unverified',
                'verification_score': 0,
                'last_verification_update': None
            } 

    # Custom Roles Methods
    def create_custom_role(self, organization_id: str, role_data: Dict[str, Any]) -> Optional[str]:
        """Create a custom role for an organization"""
        try:
            role_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            query = """
                INSERT INTO custom_roles 
                (role_id, organization_id, name, description, permissions, inherits_from, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db_manager.execute_query(query, (
                role_id,
                organization_id,
                role_data['name'],
                role_data.get('description'),
                json.dumps(role_data.get('permissions', [])),
                role_data.get('inherits_from'),
                role_data.get('is_active', True),
                now,
                now
            ))
            
            logger.info(f"✓ Custom role '{role_data['name']}' created for organization {organization_id}")
            return role_id
            
        except Exception as e:
            logger.error(f"Error creating custom role: {e}")
            return None

    def get_custom_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Get custom role by ID"""
        try:
            query = "SELECT * FROM custom_roles WHERE role_id = ?"
            results = self.db_manager.execute_query(query, (role_id,))
            
            if results:
                row = results[0]
                permissions = []
                if row.get('permissions'):
                    try:
                        permissions = json.loads(row['permissions'])
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                return {
                    'role_id': row['role_id'],
                    'organization_id': row['organization_id'],
                    'name': row['name'],
                    'description': row['description'],
                    'permissions': permissions,
                    'inherits_from': row['inherits_from'],
                    'is_active': row['is_active'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting custom role: {e}")
            return None

    def get_custom_roles_by_organization(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all custom roles for an organization"""
        try:
            query = "SELECT * FROM custom_roles WHERE organization_id = ? ORDER BY created_at DESC"
            results = self.db_manager.execute_query(query, (organization_id,))
            
            roles = []
            for row in results:
                permissions = []
                if row.get('permissions'):
                    try:
                        permissions = json.loads(row['permissions'])
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                roles.append({
                    'role_id': row['role_id'],
                    'organization_id': row['organization_id'],
                    'name': row['name'],
                    'description': row['description'],
                    'permissions': permissions,
                    'inherits_from': row['inherits_from'],
                    'is_active': row['is_active'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            return roles
            
        except Exception as e:
            logger.error(f"Error getting custom roles: {e}")
            return []

    def update_custom_role(self, role_id: str, role_data: Dict[str, Any]) -> bool:
        """Update a custom role"""
        try:
            now = datetime.now().isoformat()
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            if 'name' in role_data:
                update_fields.append("name = ?")
                params.append(role_data['name'])
            
            if 'description' in role_data:
                update_fields.append("description = ?")
                params.append(role_data['description'])
            
            if 'permissions' in role_data:
                update_fields.append("permissions = ?")
                params.append(json.dumps(role_data['permissions']))
            
            if 'inherits_from' in role_data:
                update_fields.append("inherits_from = ?")
                params.append(role_data['inherits_from'])
            
            if 'is_active' in role_data:
                update_fields.append("is_active = ?")
                params.append(role_data['is_active'])
            
            update_fields.append("updated_at = ?")
            params.append(now)
            params.append(role_id)
            
            query = f"""
                UPDATE custom_roles 
                SET {', '.join(update_fields)}
                WHERE role_id = ?
            """
            
            self.db_manager.execute_query(query, tuple(params))
            
            logger.info(f"✓ Custom role {role_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating custom role: {e}")
            return False

    def delete_custom_role(self, role_id: str) -> bool:
        """Delete a custom role"""
        try:
            # Check if role is assigned to any users
            assignment_query = "SELECT COUNT(*) as count FROM role_assignments WHERE role_id = ? AND is_active = TRUE"
            results = self.db_manager.execute_query(assignment_query, (role_id,))
            
            if results and results[0]['count'] > 0:
                logger.warning(f"Cannot delete role {role_id} - it is assigned to {results[0]['count']} users")
                return False
            
            query = "DELETE FROM custom_roles WHERE role_id = ?"
            self.db_manager.execute_query(query, (role_id,))
            
            logger.info(f"✓ Custom role {role_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting custom role: {e}")
            return False

    # Role Assignment Methods
    def assign_role_to_user(self, user_id: str, role_id: str, organization_id: str, assigned_by: str) -> bool:
        """Assign a role to a user"""
        try:
            assignment_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Check if user already has this role
            existing_query = """
                SELECT assignment_id FROM role_assignments 
                WHERE user_id = ? AND role_id = ? AND organization_id = ? AND is_active = TRUE
            """
            existing_results = self.db_manager.execute_query(existing_query, (user_id, role_id, organization_id))
            
            if existing_results:
                logger.info(f"User {user_id} already has role {role_id}")
                return True
            
            query = """
                INSERT INTO role_assignments 
                (assignment_id, user_id, role_id, organization_id, assigned_by, assigned_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, TRUE)
            """
            
            self.db_manager.execute_query(query, (
                assignment_id,
                user_id,
                role_id,
                organization_id,
                assigned_by,
                now
            ))
            
            logger.info(f"✓ Role {role_id} assigned to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning role to user: {e}")
            return False

    def remove_role_from_user(self, user_id: str, role_id: str, organization_id: str) -> bool:
        """Remove a role from a user"""
        try:
            query = """
                UPDATE role_assignments 
                SET is_active = FALSE 
                WHERE user_id = ? AND role_id = ? AND organization_id = ? AND is_active = TRUE
            """
            
            self.db_manager.execute_query(query, (user_id, role_id, organization_id))
            
            logger.info(f"✓ Role {role_id} removed from user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing role from user: {e}")
            return False

    def get_user_roles(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get all roles assigned to a user in an organization"""
        try:
            query = """
                SELECT ra.*, cr.name as role_name, cr.description as role_description, cr.permissions
                FROM role_assignments ra
                LEFT JOIN custom_roles cr ON ra.role_id = cr.role_id
                WHERE ra.user_id = ? AND ra.organization_id = ? AND ra.is_active = TRUE
                ORDER BY ra.assigned_at DESC
            """
            
            results = self.db_manager.execute_query(query, (user_id, organization_id))
            
            roles = []
            for row in results:
                permissions = []
                if row.get('permissions'):
                    try:
                        permissions = json.loads(row['permissions'])
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                roles.append({
                    'assignment_id': row['assignment_id'],
                    'role_id': row['role_id'],
                    'role_name': row['role_name'] or row['role_id'],  # Use custom role name or role_id for built-in roles
                    'role_description': row['role_description'],
                    'permissions': permissions,
                    'assigned_by': row['assigned_by'],
                    'assigned_at': row['assigned_at'],
                    'expires_at': row['expires_at'],
                    'is_active': row['is_active']
                })
            
            return roles
            
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return [] 

    # Organization Settings Methods
    def get_organization_settings(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization settings"""
        try:
            query = "SELECT * FROM organization_settings WHERE organization_id = ?"
            results = self.db_manager.execute_query(query, (organization_id,))
            
            if results:
                row = results[0]
                return {
                    'settings_id': row['settings_id'],
                    'organization_id': row['organization_id'],
                    'branding': json.loads(row['branding']) if row['branding'] else {},
                    'configuration': json.loads(row['configuration']) if row['configuration'] else {},
                    'notifications': json.loads(row['notifications']) if row['notifications'] else {},
                    'security': json.loads(row['security']) if row['security'] else {},
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting organization settings: {e}")
            return None

    def create_organization_settings(self, organization_id: str, settings_data: Dict[str, Any]) -> bool:
        """Create organization settings"""
        try:
            settings_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            query = """
                INSERT INTO organization_settings 
                (settings_id, organization_id, branding, configuration, notifications, security, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db_manager.execute_query(query, (
                settings_id,
                organization_id,
                json.dumps(settings_data.get('branding', {})),
                json.dumps(settings_data.get('configuration', {})),
                json.dumps(settings_data.get('notifications', {})),
                json.dumps(settings_data.get('security', {})),
                now,
                now
            ))
            
            logger.info(f"✓ Organization settings created for organization {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating organization settings: {e}")
            return False

    def update_organization_settings(self, organization_id: str, settings_data: Dict[str, Any]) -> bool:
        """Update organization settings"""
        try:
            now = datetime.now().isoformat()
            
            # Get existing settings
            existing_settings = self.get_organization_settings(organization_id)
            if not existing_settings:
                return self.create_organization_settings(organization_id, settings_data)
            
            # Merge with existing settings
            merged_settings = {
                'branding': {**existing_settings['branding'], **settings_data.get('branding', {})},
                'configuration': {**existing_settings['configuration'], **settings_data.get('configuration', {})},
                'notifications': {**existing_settings['notifications'], **settings_data.get('notifications', {})},
                'security': {**existing_settings['security'], **settings_data.get('security', {})}
            }
            
            query = """
                UPDATE organization_settings 
                SET branding = ?, configuration = ?, notifications = ?, security = ?, updated_at = ?
                WHERE organization_id = ?
            """
            
            self.db_manager.execute_query(query, (
                json.dumps(merged_settings['branding']),
                json.dumps(merged_settings['configuration']),
                json.dumps(merged_settings['notifications']),
                json.dumps(merged_settings['security']),
                now,
                organization_id
            ))
            
            logger.info(f"✓ Organization settings updated for organization {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating organization settings: {e}")
            return False

    # Organization Analytics Methods
    def get_organization_analytics(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization analytics"""
        try:
            query = "SELECT * FROM organization_analytics WHERE organization_id = ?"
            results = self.db_manager.execute_query(query, (organization_id,))
            
            if results:
                row = results[0]
                return {
                    'analytics_id': row['analytics_id'],
                    'organization_id': row['organization_id'],
                    'user_analytics': json.loads(row['user_analytics']) if row['user_analytics'] else {},
                    'usage_analytics': json.loads(row['usage_analytics']) if row['usage_analytics'] else {},
                    'performance_metrics': json.loads(row['performance_metrics']) if row['performance_metrics'] else {},
                    'activity_insights': json.loads(row['activity_insights']) if row['activity_insights'] else {},
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting organization analytics: {e}")
            return None

    def update_organization_analytics(self, organization_id: str, analytics_data: Dict[str, Any]) -> bool:
        """Update organization analytics"""
        try:
            now = datetime.now().isoformat()
            
            # Check if analytics exist
            existing_analytics = self.get_organization_analytics(organization_id)
            
            if existing_analytics:
                # Update existing analytics
                query = """
                    UPDATE organization_analytics 
                    SET user_analytics = ?, usage_analytics = ?, performance_metrics = ?, 
                        activity_insights = ?, updated_at = ?
                    WHERE organization_id = ?
                """
                
                self.db_manager.execute_query(query, (
                    json.dumps(analytics_data.get('user_analytics', {})),
                    json.dumps(analytics_data.get('usage_analytics', {})),
                    json.dumps(analytics_data.get('performance_metrics', {})),
                    json.dumps(analytics_data.get('activity_insights', {})),
                    now,
                    organization_id
                ))
            else:
                # Create new analytics
                analytics_id = str(uuid.uuid4())
                query = """
                    INSERT INTO organization_analytics 
                    (analytics_id, organization_id, user_analytics, usage_analytics, 
                     performance_metrics, activity_insights, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                self.db_manager.execute_query(query, (
                    analytics_id,
                    organization_id,
                    json.dumps(analytics_data.get('user_analytics', {})),
                    json.dumps(analytics_data.get('usage_analytics', {})),
                    json.dumps(analytics_data.get('performance_metrics', {})),
                    json.dumps(analytics_data.get('activity_insights', {})),
                    now,
                    now
                ))
            
            logger.info(f"✓ Organization analytics updated for organization {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating organization analytics: {e}")
            return False

    # Organization Billing Methods
    def get_organization_billing(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get organization billing information"""
        try:
            query = "SELECT * FROM organization_billing WHERE organization_id = ?"
            results = self.db_manager.execute_query(query, (organization_id,))
            
            if results:
                row = results[0]
                return {
                    'billing_id': row['billing_id'],
                    'organization_id': row['organization_id'],
                    'subscription': json.loads(row['subscription']) if row['subscription'] else {},
                    'billing_info': json.loads(row['billing_info']) if row['billing_info'] else {},
                    'usage_billing': json.loads(row['usage_billing']) if row['usage_billing'] else {},
                    'payment_history': json.loads(row['payment_history']) if row['payment_history'] else [],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting organization billing: {e}")
            return None

    def update_organization_billing(self, organization_id: str, billing_data: Dict[str, Any]) -> bool:
        """Update organization billing information"""
        try:
            now = datetime.now().isoformat()
            
            # Check if billing exists
            existing_billing = self.get_organization_billing(organization_id)
            
            if existing_billing:
                # Update existing billing
                query = """
                    UPDATE organization_billing 
                    SET subscription = ?, billing_info = ?, usage_billing = ?, 
                        payment_history = ?, updated_at = ?
                    WHERE organization_id = ?
                """
                
                self.db_manager.execute_query(query, (
                    json.dumps(billing_data.get('subscription', {})),
                    json.dumps(billing_data.get('billing_info', {})),
                    json.dumps(billing_data.get('usage_billing', {})),
                    json.dumps(billing_data.get('payment_history', [])),
                    now,
                    organization_id
                ))
            else:
                # Create new billing
                billing_id = str(uuid.uuid4())
                query = """
                    INSERT INTO organization_billing 
                    (billing_id, organization_id, subscription, billing_info, 
                     usage_billing, payment_history, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                self.db_manager.execute_query(query, (
                    billing_id,
                    organization_id,
                    json.dumps(billing_data.get('subscription', {})),
                    json.dumps(billing_data.get('billing_info', {})),
                    json.dumps(billing_data.get('usage_billing', {})),
                    json.dumps(billing_data.get('payment_history', [])),
                    now,
                    now
                ))
            
            logger.info(f"✓ Organization billing updated for organization {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating organization billing: {e}")
            return False 