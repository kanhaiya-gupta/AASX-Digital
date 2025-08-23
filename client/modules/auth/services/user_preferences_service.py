"""
User Preferences Integration Service - Soft Connection to Backend
===============================================================

Thin integration layer that connects webapp to backend user preferences services.
Handles frontend-specific logic while delegating business logic to backend.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import from backend engine
from src.engine.services.auth.user_service import UserService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class UserPreferencesService:
    """Integration service for user preferences operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._auth_repo = None
        self._user_service = None
        
        logger.info("✅ User preferences integration service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            
            self._initialized = True
            logger.info("✅ User preferences integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize user preferences integration service: {e}")
            raise
    
    @property
    def auth_repo(self):
        """Get auth repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_repo
    
    @property
    def user_service(self):
        """Get user service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._user_service
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences from backend"""
        await self._ensure_initialized()
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                return None
            
            # Extract preferences from user model
            preferences = {}
            if hasattr(user, 'preferences') and user.preferences:
                try:
                    import json
                    preferences = json.loads(user.preferences) if isinstance(user.preferences, str) else user.preferences
                except:
                    preferences = {}
            
            # Return default preferences if none exist
            if not preferences:
                preferences = self._get_default_preferences()
            
            return preferences
        except Exception as e:
            logger.error(f"Error getting user preferences for user {user_id}: {e}")
            return self._get_default_preferences()
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences via backend"""
        await self._ensure_initialized()
        try:
            # Validate preferences structure
            validated_preferences = self._validate_preferences(preferences)
            
            # Update user with new preferences
            success = await self.user_service.update_user(user_id, {
                "preferences": validated_preferences
            })
            
            return success
        except Exception as e:
            logger.error(f"Error updating user preferences for user {user_id}: {e}")
            return False
    
    async def set_user_preference(self, user_id: str, key: str, value: Any) -> bool:
        """Set a specific user preference via backend"""
        await self._ensure_initialized()
        try:
            # Get current preferences
            current_preferences = await self.get_user_preferences(user_id)
            if current_preferences is None:
                current_preferences = self._get_default_preferences()
            
            # Update specific preference
            current_preferences[key] = value
            
            # Save updated preferences
            return await self.update_user_preferences(user_id, current_preferences)
        except Exception as e:
            logger.error(f"Error setting user preference {key} for user {user_id}: {e}")
            return False
    
    async def get_user_preference(self, user_id: str, key: str) -> Optional[Any]:
        """Get a specific user preference via backend"""
        await self._ensure_initialized()
        try:
            preferences = await self.get_user_preferences(user_id)
            if preferences and key in preferences:
                return preferences[key]
            return None
        except Exception as e:
            logger.error(f"Error getting user preference {key} for user {user_id}: {e}")
            return None
    
    async def reset_user_preferences(self, user_id: str) -> bool:
        """Reset user preferences to default via backend"""
        await self._ensure_initialized()
        try:
            default_preferences = self._get_default_preferences()
            return await self.update_user_preferences(user_id, default_preferences)
        except Exception as e:
            logger.error(f"Error resetting user preferences for user {user_id}: {e}")
            return False
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "notifications": {
                "email": True,
                "push": True,
                "sms": False,
                "frequency": "immediate"
            },
            "display": {
                "compact_mode": False,
                "show_avatars": True,
                "show_timestamps": True
            },
            "privacy": {
                "profile_visibility": "public",
                "show_online_status": True,
                "allow_contact": True
            },
            "accessibility": {
                "high_contrast": False,
                "large_text": False,
                "screen_reader": False
            }
        }
    
    def _validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize user preferences"""
        if not isinstance(preferences, dict):
            return self._get_default_preferences()
        
        # Ensure required keys exist
        default_prefs = self._get_default_preferences()
        validated = {}
        
        for key, default_value in default_prefs.items():
            if key in preferences:
                # Validate specific preference types
                if key == "theme" and preferences[key] in ["light", "dark", "auto"]:
                    validated[key] = preferences[key]
                elif key == "language" and preferences[key] in ["en", "es", "fr", "de", "zh", "ja"]:
                    validated[key] = preferences[key]
                elif key == "timezone" and isinstance(preferences[key], str):
                    validated[key] = preferences[key]
                elif key == "notifications" and isinstance(preferences[key], dict):
                    validated[key] = self._validate_notification_preferences(preferences[key])
                elif key == "display" and isinstance(preferences[key], dict):
                    validated[key] = self._validate_display_preferences(preferences[key])
                elif key == "privacy" and isinstance(preferences[key], dict):
                    validated[key] = self._validate_privacy_preferences(preferences[key])
                elif key == "accessibility" and isinstance(preferences[key], dict):
                    validated[key] = self._validate_accessibility_preferences(preferences[key])
                else:
                    validated[key] = default_value
            else:
                validated[key] = default_value
        
        return validated
    
    def _validate_notification_preferences(self, notifications: Dict[str, Any]) -> Dict[str, Any]:
        """Validate notification preferences"""
        default_notifications = self._get_default_preferences()["notifications"]
        validated = {}
        
        for key, default_value in default_notifications.items():
            if key in notifications:
                if key in ["email", "push", "sms"]:
                    validated[key] = bool(notifications[key])
                elif key == "frequency" and notifications[key] in ["immediate", "daily", "weekly"]:
                    validated[key] = notifications[key]
                else:
                    validated[key] = default_value
            else:
                validated[key] = default_value
        
        return validated
    
    def _validate_display_preferences(self, display: Dict[str, Any]) -> Dict[str, Any]:
        """Validate display preferences"""
        default_display = self._get_default_preferences()["display"]
        validated = {}
        
        for key, default_value in default_display.items():
            if key in display:
                if key in ["compact_mode", "show_avatars", "show_timestamps"]:
                    validated[key] = bool(display[key])
                else:
                    validated[key] = default_value
            else:
                validated[key] = default_value
        
        return validated
    
    def _validate_privacy_preferences(self, privacy: Dict[str, Any]) -> Dict[str, Any]:
        """Validate privacy preferences"""
        default_privacy = self._get_default_preferences()["privacy"]
        validated = {}
        
        for key, default_value in default_privacy.items():
            if key in privacy:
                if key == "profile_visibility" and privacy[key] in ["public", "private", "friends"]:
                    validated[key] = privacy[key]
                elif key in ["show_online_status", "allow_contact"]:
                    validated[key] = bool(privacy[key])
                else:
                    validated[key] = default_value
            else:
                validated[key] = default_value
        
        return validated
    
    def _validate_accessibility_preferences(self, accessibility: Dict[str, Any]) -> Dict[str, Any]:
        """Validate accessibility preferences"""
        default_accessibility = self._get_default_preferences()["accessibility"]
        validated = {}
        
        for key, default_value in default_accessibility.items():
            if key in accessibility:
                if key in ["high_contrast", "large_text", "screen_reader"]:
                    validated[key] = bool(accessibility[key])
                else:
                    validated[key] = default_value
            else:
                validated[key] = default_value
        
        return validated


# Export the integration service
__all__ = ['UserPreferencesService']
