"""
User Repository
==============

Data access layer for users in the AAS Data Modeling framework.
"""

from typing import List, Optional, Dict, Any
from ..database.base_manager import BaseDatabaseManager
from ..models.user import User
from .base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    """Repository for user operations."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        super().__init__(db_manager, User)
    
    def _get_table_name(self) -> str:
        return "users"
    
    def _get_columns(self) -> List[str]:
        return [
            "id", "username", "email", "full_name", "organization_id", 
            "role", "is_active", "last_login", "created_at", "updated_at"
        ]
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        query = "SELECT * FROM users WHERE username = ?"
        results = self.db_manager.execute_query(query, (username,))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = "SELECT * FROM users WHERE email = ?"
        results = self.db_manager.execute_query(query, (email,))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def get_by_organization(self, organization_id: str) -> List[User]:
        """Get users by organization."""
        query = "SELECT * FROM users WHERE organization_id = ?"
        results = self.db_manager.execute_query(query, (organization_id,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_by_role(self, role: str) -> List[User]:
        """Get users by role."""
        query = "SELECT * FROM users WHERE role = ?"
        results = self.db_manager.execute_query(query, (role,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        query = "SELECT * FROM users WHERE is_active = 1"
        results = self.db_manager.execute_query(query)
        return [self.model_class.from_dict(row) for row in results]
    
    def search_users(self, search_term: str) -> List[User]:
        """Search users by username, email, or full name."""
        query = """
            SELECT * FROM users 
            WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ?
        """
        search_pattern = f"%{search_term}%"
        results = self.db_manager.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [self.model_class.from_dict(row) for row in results]
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        query = "UPDATE users SET last_login = datetime('now'), updated_at = datetime('now') WHERE id = ?"
        try:
            affected_rows = self.db_manager.execute_update(query, (user_id,))
            return affected_rows > 0
        except Exception:
            return False
    
    def get_user_statistics(self, organization_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user statistics."""
        if organization_id:
            query = """
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
                    COUNT(CASE WHEN is_active = 0 THEN 1 END) as inactive_users,
                    role,
                    COUNT(*) as role_count
                FROM users 
                WHERE organization_id = ?
                GROUP BY role
            """
            results = self.db_manager.execute_query(query, (organization_id,))
        else:
            query = """
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
                    COUNT(CASE WHEN is_active = 0 THEN 1 END) as inactive_users,
                    role,
                    COUNT(*) as role_count
                FROM users 
                GROUP BY role
            """
            results = self.db_manager.execute_query(query)
        
        stats = {
            "total_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "roles": {}
        }
        
        for row in results:
            stats["total_users"] = row["total_users"]
            stats["active_users"] = row["active_users"]
            stats["inactive_users"] = row["inactive_users"]
            if row["role"]:
                stats["roles"][row["role"]] = row["role_count"]
        
        return stats
    
    def check_username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        query = "SELECT COUNT(*) as count FROM users WHERE username = ?"
        results = self.db_manager.execute_query(query, (username,))
        return results[0]["count"] > 0 if results else False
    
    def check_email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        query = "SELECT COUNT(*) as count FROM users WHERE email = ?"
        results = self.db_manager.execute_query(query, (email,))
        return results[0]["count"] > 0 if results else False 