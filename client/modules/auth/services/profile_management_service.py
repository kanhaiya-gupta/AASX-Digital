"""
Profile Management Integration Service - Soft Connection to Backend
================================================================

Thin integration layer that connects webapp to backend profile management services.
Handles frontend-specific logic while delegating business logic to backend.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import from backend engine
from src.engine.services.auth.user_service import UserService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class ProfileManagementService:
    """Integration service for profile management operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._auth_repo = None
        self._user_service = None
        
        logger.info("✅ Profile management integration service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            
            self._initialized = True
            logger.info("✅ Profile management integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize profile management integration service: {e}")
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
    
    async def get_public_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's public profile from backend"""
        await self._ensure_initialized()
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                return None
            
            # Extract public profile data from user model
            public_profile = {
                "user_id": user.user_id,
                "username": user.username,
                "full_name": user.full_name,
                "bio": getattr(user, 'bio', None),
                "location": getattr(user, 'location', None),
                "website": getattr(user, 'website', None),
                "skills": self._parse_json_field(getattr(user, 'skills', '{}')),
                "interests": self._parse_json_field(getattr(user, 'interests', '{}')),
                "is_public_profile": getattr(user, 'is_public_profile', False),
                "social_links": self._parse_json_field(getattr(user, 'social_links', '{}')),
                "avatar_url": getattr(user, 'avatar_url', None),
                "created_at": getattr(user, 'created_at', None),
                "last_active": getattr(user, 'last_login', None)
            }
            
            # Only return if profile is public
            if public_profile.get("is_public_profile", False):
                return public_profile
            return None
            
        except Exception as e:
            logger.error(f"Error getting public profile for user {user_id}: {e}")
            return None
    
    async def get_public_profile_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get public profile by username from backend"""
        await self._ensure_initialized()
        try:
            user = await self.user_service.get_user_by_username(username)
            if not user:
                return None
            
            return await self.get_public_profile(user.user_id)
            
        except Exception as e:
            logger.error(f"Error getting public profile for username {username}: {e}")
            return None
    
    async def create_public_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Create or update public profile via backend"""
        await self._ensure_initialized()
        try:
            # Validate profile data
            validated_data = self._validate_profile_data(profile_data)
            
            # Update user with profile data
            update_data = {
                "bio": validated_data.get("bio"),
                "location": validated_data.get("location"),
                "website": validated_data.get("website"),
                "skills": validated_data.get("skills", {}),
                "interests": validated_data.get("interests", {}),
                "is_public_profile": True,
                "social_links": validated_data.get("social_links", {}),
                "avatar_url": validated_data.get("avatar_url")
            }
            
            # Convert dict fields to JSON strings for storage
            for field in ["skills", "interests", "social_links"]:
                if update_data[field]:
                    update_data[field] = self._serialize_json_field(update_data[field])
            
            success = await self.user_service.update_user(user_id, update_data)
            return success
            
        except Exception as e:
            logger.error(f"Error creating public profile for user {user_id}: {e}")
            return False
    
    async def update_public_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update public profile via backend"""
        await self._ensure_initialized()
        try:
            # Get current profile
            current_profile = await self.get_public_profile(user_id)
            if not current_profile:
                # Create new profile if none exists
                return await self.create_public_profile(user_id, profile_data)
            
            # Validate and merge profile data
            validated_data = self._validate_profile_data(profile_data)
            
            # Update user with new profile data
            update_data = {}
            for key, value in validated_data.items():
                if value is not None:
                    if key in ["skills", "interests", "social_links"]:
                        update_data[key] = self._serialize_json_field(value)
                    else:
                        update_data[key] = value
            
            success = await self.user_service.update_user(user_id, update_data)
            return success
            
        except Exception as e:
            logger.error(f"Error updating public profile for user {user_id}: {e}")
            return False
    
    async def delete_public_profile(self, user_id: str) -> bool:
        """Delete public profile via backend"""
        await self._ensure_initialized()
        try:
            # Set profile to private
            update_data = {
                "is_public_profile": False,
                "bio": None,
                "location": None,
                "website": None,
                "skills": "{}",
                "interests": "{}",
                "social_links": "{}"
            }
            
            success = await self.user_service.update_user(user_id, update_data)
            return success
            
        except Exception as e:
            logger.error(f"Error deleting public profile for user {user_id}: {e}")
            return False
    
    async def get_public_profiles(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all public profiles from backend"""
        await self._ensure_initialized()
        try:
            # Get all users and filter for public profiles
            users = await self.user_service.get_all_users()
            public_profiles = []
            
            for user in users:
                if getattr(user, 'is_public_profile', False):
                    profile = await self.get_public_profile(user.user_id)
                    if profile:
                        public_profiles.append(profile)
                        
                        # Apply pagination
                        if len(public_profiles) >= limit:
                            break
            
            # Apply offset
            return public_profiles[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error getting public profiles: {e}")
            return []
    
    async def search_public_profiles(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search public profiles from backend"""
        await self._ensure_initialized()
        try:
            if not query or len(query.strip()) < 2:
                return []
            
            query = query.strip().lower()
            all_profiles = await self.get_public_profiles(limit=1000)  # Get more for search
            matching_profiles = []
            
            for profile in all_profiles:
                # Search in various fields
                searchable_text = [
                    profile.get("username", ""),
                    profile.get("full_name", ""),
                    profile.get("bio", ""),
                    profile.get("location", ""),
                    str(profile.get("skills", {})),
                    str(profile.get("interests", {}))
                ]
                
                searchable_text = " ".join(searchable_text).lower()
                
                if query in searchable_text:
                    matching_profiles.append(profile)
                    
                    if len(matching_profiles) >= limit:
                        break
            
            return matching_profiles
            
        except Exception as e:
            logger.error(f"Error searching public profiles: {e}")
            return []
    
    async def upload_avatar(self, user_id: str, avatar_data: bytes, filename: str) -> Optional[str]:
        """Upload user avatar via backend"""
        await self._ensure_initialized()
        try:
            # Validate file type
            if not self._is_valid_avatar_file(filename):
                logger.error(f"Invalid avatar file type: {filename}")
                return None
            
            # Generate unique filename
            import uuid
            import os
            file_extension = os.path.splitext(filename)[1].lower()
            avatar_filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
            
            # Save avatar file
            avatar_path = f"webapp/static/avatars/{avatar_filename}"
            os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
            
            with open(avatar_path, "wb") as f:
                f.write(avatar_data)
            
            # Update user's avatar_url
            avatar_url = f"/static/avatars/{avatar_filename}"
            success = await self.user_service.update_user(user_id, {"avatar_url": avatar_url})
            
            if success:
                return avatar_url
            else:
                # Clean up file if database update fails
                if os.path.exists(avatar_path):
                    os.remove(avatar_path)
                return None
                
        except Exception as e:
            logger.error(f"Error uploading avatar for user {user_id}: {e}")
            return None
    
    async def remove_avatar(self, user_id: str) -> bool:
        """Remove user avatar via backend"""
        await self._ensure_initialized()
        try:
            # Get current avatar URL
            user = await self.user_service.get_user_by_id(user_id)
            if not user or not getattr(user, 'avatar_url', None):
                return True  # No avatar to remove
            
            avatar_url = user.avatar_url
            avatar_path = f"webapp/static/avatars/{os.path.basename(avatar_url)}"
            
            # Remove avatar file if it exists
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                except Exception as e:
                    logger.warning(f"Failed to delete avatar file {avatar_path}: {e}")
            
            # Update user's avatar_url
            success = await self.user_service.update_user(user_id, {"avatar_url": None})
            return success
            
        except Exception as e:
            logger.error(f"Error removing avatar for user {user_id}: {e}")
            return False
    
    def _validate_profile_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize profile data"""
        if not isinstance(profile_data, dict):
            return {}
        
        validated = {}
        
        # Validate bio
        if "bio" in profile_data and profile_data["bio"]:
            bio = str(profile_data["bio"]).strip()
            if len(bio) <= 500:  # Max 500 characters
                validated["bio"] = bio
        
        # Validate location
        if "location" in profile_data and profile_data["location"]:
            location = str(profile_data["location"]).strip()
            if len(location) <= 100:  # Max 100 characters
                validated["location"] = location
        
        # Validate website
        if "website" in profile_data and profile_data["website"]:
            website = str(profile_data["website"]).strip()
            if self._is_valid_url(website):
                validated["website"] = website
        
        # Validate skills
        if "skills" in profile_data and profile_data["skills"]:
            if isinstance(profile_data["skills"], (list, dict)):
                validated["skills"] = profile_data["skills"]
        
        # Validate interests
        if "interests" in profile_data and profile_data["interests"]:
            if isinstance(profile_data["interests"], (list, dict)):
                validated["interests"] = profile_data["interests"]
        
        # Validate social links
        if "social_links" in profile_data and profile_data["social_links"]:
            if isinstance(profile_data["social_links"], dict):
                validated["social_links"] = profile_data["social_links"]
        
        # Validate avatar URL
        if "avatar_url" in profile_data and profile_data["avatar_url"]:
            avatar_url = str(profile_data["avatar_url"]).strip()
            if self._is_valid_url(avatar_url):
                validated["avatar_url"] = avatar_url
        
        return validated
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
    
    def _is_valid_avatar_file(self, filename: str) -> bool:
        """Check if avatar file is valid"""
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        import os
        file_extension = os.path.splitext(filename)[1].lower()
        return file_extension in allowed_extensions
    
    def _parse_json_field(self, field_value: Any) -> Any:
        """Parse JSON field from user model"""
        if not field_value:
            return {}
        
        if isinstance(field_value, str):
            try:
                import json
                return json.loads(field_value)
            except:
                return {}
        
        return field_value if isinstance(field_value, (dict, list)) else {}
    
    def _serialize_json_field(self, field_value: Any) -> str:
        """Serialize field value to JSON string"""
        if not field_value:
            return "{}"
        
        try:
            import json
            return json.dumps(field_value)
        except:
            return "{}"


# Export the integration service
__all__ = ['ProfileManagementService']
