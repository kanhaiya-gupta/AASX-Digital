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
            
            logger.info("✓ Auth Database initialized with centralized system")
            
        except Exception as e:
            logger.error(f"Error initializing Auth Database: {e}")
            raise
    
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