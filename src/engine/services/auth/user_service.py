"""
User Service - Handles user management operations.

This service provides business logic for user operations including:
- User CRUD operations
- User profile management
- User preferences and settings
- User activity tracking
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict

from ...repositories.auth_repository import AuthRepository
from ...models.auth import User
from ..base.base_service import BaseService

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile information for service operations."""
    user_id: str
    username: str
    email: str
    full_name: str
    org_id: Optional[str] = None
    dept_id: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    preferences: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


@dataclass
class UserPreferences:
    """User preferences and settings."""
    user_id: str
    theme: str = "light"
    language: str = "en"
    timezone: str = "UTC"
    notifications: Dict[str, bool] = None
    ui_settings: Dict[str, Any] = None
    workflow_preferences: Dict[str, Any] = None


class UserService(BaseService):
    """
    Service for managing user operations and business logic.
    
    Handles user lifecycle, profile management, preferences,
    and activity tracking across the system.
    """
    
    def __init__(self, auth_repository: AuthRepository):
        """
        Initialize the UserService.
        
        Args:
            auth_repository: Repository for user data operations
        """
        super().__init__()
        self.auth_repository = auth_repository
        
        # In-memory data structures for fast access
        self._users: Dict[str, User] = {}
        self._user_profiles: Dict[str, UserProfile] = {}
        self._user_preferences: Dict[str, UserPreferences] = {}
        self._user_activity: Dict[str, List[Dict[str, Any]]] = {}
        self._active_users: Set[str] = set()
        self._user_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Load initial data
        asyncio.create_task(self._initialize_service_resources())
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Create a new user with profile and preferences.
        
        Args:
            user_data: User creation data (must include 'password' for plain text password)
            
        Returns:
            Created user or None if failed
        """
        try:
            self._log_operation("create_user", f"username: {user_data.get('username')}")
            
            # Validate required fields
            required_fields = ['username', 'email', 'full_name', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate password hash
            password_hash = User.hash_password(user_data['password'])
            
            # Create user model
            user = User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                password_hash=password_hash,
                org_id=user_data.get('org_id'),
                dept_id=user_data.get('dept_id'),
                role=user_data.get('role', 'user'),
                is_active=user_data.get('is_active', True),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Save to repository
            created_user = await self.auth_repository.create_user(user)
            if not created_user:
                raise Exception("Failed to create user in repository")
            
            # Update in-memory structures
            self._users[user.user_id] = created_user
            self._user_profiles[user.user_id] = UserProfile(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                org_id=user.org_id,
                dept_id=user.dept_id,
                role=user.role,
                is_active=user.is_active
            )
            
            # Initialize preferences
            self._user_preferences[user.user_id] = UserPreferences(
                user_id=user.user_id
            )
            
            # Initialize activity tracking
            self._user_activity[user.user_id] = []
            self._active_users.add(user.user_id)
            
            logger.info(f"User created successfully: {user.username}")
            return created_user
            
        except Exception as e:
            self.handle_error("create_user", e)
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User object or None if not found
        """
        try:
            # Check in-memory first
            if user_id in self._users:
                return self._users[user_id]
            
            # Fetch from repository
            user = await self.auth_repository.get_user_by_id(user_id)
            if user:
                self._users[user_id] = user
                return user
            
            return None
            
        except Exception as e:
            self.handle_error("get_user_by_id", e)
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        try:
            # Check in-memory first
            for user in self._users.values():
                if user.username == username:
                    return user
            
            # Fetch from repository
            user = await self.auth_repository.get_user_by_username(username)
            if user:
                self._users[user.user_id] = user
                return user
            
            return None
            
        except Exception as e:
            self.handle_error("get_user_by_username", e)
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User object or None if not found
        """
        try:
            # Check in-memory first
            for user in self._users.values():
                if user.email == email:
                    return user
            
            # Fetch from repository
            user = await self.auth_repository.get_user_by_email(email)
            if user:
                self._users[user.user_id] = user
                return user
            
            return None
            
        except Exception as e:
            self.handle_error("get_user_by_email", e)
            return None
    
    async def get_users_by_organization(self, org_id: str) -> List[User]:
        """
        Get all users belonging to an organization.
        
        Args:
            org_id: Organization identifier
            
        Returns:
            List of users in the organization
        """
        try:
            # Check in-memory first
            org_users = [user for user in self._users.values() if user.org_id == org_id]
            if org_users:
                return org_users
            
            # Fetch from repository
            users = await self.auth_repository.get_users_by_organization(org_id)
            for user in users:
                self._users[user.user_id] = user
            
            return users
            
        except Exception as e:
            self.handle_error("get_users_by_organization", e)
            return []
    
    async def get_users_by_department(self, dept_id: str) -> List[User]:
        """
        Get all users belonging to a department.
        
        Args:
            dept_id: Department identifier
            
        Returns:
            List of users in the department
        """
        try:
            # Check in-memory first
            dept_users = [user for user in self._users.values() if user.dept_id == dept_id]
            if dept_users:
                return dept_users
            
            # Fetch from repository
            users = await self.auth_repository.get_users_by_department(dept_id)
            for user in users:
                self._users[user.user_id] = user
            
            return users
            
        except Exception as e:
            self.handle_error("get_users_by_department", e)
            return []
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update user profile information.
        
        Args:
            user_id: User identifier
            updates: Profile updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("update_user_profile", f"user_id: {user_id}")
            
            # Get current user
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.now().isoformat()
            
            # Update repository
            success = await self.auth_repository.update_user(user_id, updates)
            if not success:
                raise Exception("Failed to update user in repository")
            
            # Update in-memory structures
            self._users[user_id] = user
            if user_id in self._user_profiles:
                profile = self._user_profiles[user_id]
                for field, value in updates.items():
                    if hasattr(profile, field):
                        setattr(profile, field, value)
            
            logger.info(f"User profile updated successfully: {user_id}")
            return True
            
        except Exception as e:
            self.handle_error("update_user_profile", e)
            return False
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences and settings.
        
        Args:
            user_id: User identifier
            preferences: Preference updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("update_user_preferences", f"user_id: {user_id}")
            
            if user_id not in self._user_preferences:
                self._user_preferences[user_id] = UserPreferences(user_id=user_id)
            
            # Apply preference updates
            current_prefs = self._user_preferences[user_id]
            for key, value in preferences.items():
                if hasattr(current_prefs, key):
                    setattr(current_prefs, key, value)
            
            logger.info(f"User preferences updated successfully: {user_id}")
            return True
            
        except Exception as e:
            self.handle_error("update_user_preferences", e)
            return False
    
    async def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Get user preferences and settings.
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences or None if not found
        """
        try:
            if user_id in self._user_preferences:
                return self._user_preferences[user_id]
            
            # Initialize default preferences if not exists
            self._user_preferences[user_id] = UserPreferences(user_id=user_id)
            return self._user_preferences[user_id]
            
        except Exception as e:
            self.handle_error("get_user_preferences", e)
            return None
    
    async def track_user_activity(self, user_id: str, activity_type: str, details: Dict[str, Any] = None) -> bool:
        """
        Track user activity for analytics and monitoring.
        
        Args:
            user_id: User identifier
            activity_type: Type of activity (login, logout, action, etc.)
            details: Additional activity details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_id not in self._user_activity:
                self._user_activity[user_id] = []
            
            activity_record = {
                "timestamp": datetime.now().isoformat(),
                "type": activity_type,
                "details": details or {},
                "session_id": self._user_sessions.get(user_id, {}).get("session_id")
            }
            
            self._user_activity[user_id].append(activity_record)
            
            # Keep only last 1000 activities per user
            if len(self._user_activity[user_id]) > 1000:
                self._user_activity[user_id] = self._user_activity[user_id][-1000:]
            
            logger.debug(f"User activity tracked: {user_id} - {activity_type}")
            return True
            
        except Exception as e:
            self.handle_error("track_user_activity", e)
            return False
    
    async def get_user_activity(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get user activity history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of activities to return
            
        Returns:
            List of user activities
        """
        try:
            if user_id in self._user_activity:
                activities = self._user_activity[user_id][-limit:]
                return activities[::-1]  # Return in reverse chronological order
            
            return []
            
        except Exception as e:
            self.handle_error("get_user_activity", e)
            return []
    
    async def activate_user(self, user_id: str) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("activate_user", f"user_id: {user_id}")
            
            success = await self.update_user_profile(user_id, {"is_active": True})
            if success:
                self._active_users.add(user_id)
                await self.track_user_activity(user_id, "account_activated")
            
            return success
            
        except Exception as e:
            self.handle_error("activate_user", e)
            return False
    
    async def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("deactivate_user", f"user_id: {user_id}")
            
            success = await self.update_user_profile(user_id, {"is_active": False})
            if success:
                self._active_users.discard(user_id)
                await self.track_user_activity(user_id, "account_deactivated")
            
            return success
            
        except Exception as e:
            self.handle_error("deactivate_user", e)
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user account.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("delete_user", f"user_id: {user_id}")
            
            # Delete from repository
            success = await self.auth_repository.delete_user(user_id)
            if not success:
                raise Exception("Failed to delete user from repository")
            
            # Clean up in-memory structures
            self._users.pop(user_id, None)
            self._user_profiles.pop(user_id, None)
            self._user_preferences.pop(user_id, None)
            self._user_activity.pop(user_id, None)
            self._active_users.discard(user_id)
            self._user_sessions.pop(user_id, None)
            
            logger.info(f"User deleted successfully: {user_id}")
            return True
            
        except Exception as e:
            self.handle_error("delete_user", e)
            return False
    
    async def get_active_users_count(self) -> int:
        """
        Get count of active users.
        
        Returns:
            Number of active users
        """
        return len(self._active_users)
    
    async def get_total_users_count(self) -> int:
        """
        Get total count of users.
        
        Returns:
            Total number of users
        """
        return len(self._users)
    
    def _load_users(self) -> None:
        """Load users from repository into memory."""
        try:
            # This would typically load from repository
            # For now, we'll start with empty structures
            logger.info("User service initialized with empty user cache")
            
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
    
    async def _initialize_service_resources(self) -> None:
        """Initialize service-specific resources."""
        try:
            # Initialize user-related resources
            self._users = {}
            self._user_profiles = {}
            self._user_preferences = {}
            self._user_activity = {}
            self._active_users = set()
            self._user_sessions = {}
            
            # Load initial data
            self._load_users()
            logger.info("User service resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize user service resources: {e}")
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        return {
            "service_name": "UserService",
            "service_type": "authentication",
            "status": "active" if self.is_active else "inactive",
            "start_time": self.start_time.isoformat(),
            "total_users": len(self._users),
            "active_users": len(self._active_users),
            "user_profiles": len(self._user_profiles),
            "user_preferences": len(self._user_preferences),
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat(),
            "dependencies": self.dependencies,
            "performance_metrics": self.get_performance_summary()
        }
    
    async def _cleanup_service_resources(self) -> None:
        """Clean up service resources."""
        try:
            # Clear in-memory structures
            self._users.clear()
            self._user_profiles.clear()
            self._user_preferences.clear()
            self._user_activity.clear()
            self._active_users.clear()
            self._user_sessions.clear()
            
            logger.info("User service resources cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup user service resources: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the user service."""
        try:
            await self._cleanup_service_resources()
            logger.info("User service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during user service shutdown: {e}")
