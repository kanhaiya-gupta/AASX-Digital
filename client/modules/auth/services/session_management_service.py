"""
Session Management Integration Service - Soft Connection to Backend
=================================================================

Thin integration layer that connects webapp to backend session management services.
Handles frontend-specific logic while delegating session operations to backend.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Import from backend engine
from src.engine.services.auth.auth_service import AuthService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class SessionManagementService:
    """Integration service for session management operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._auth_repo = None
        self._auth_service = None
        
        logger.info("✅ Session management integration service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._auth_service = AuthService(self._auth_repo, None, None)
            
            self._initialized = True
            logger.info("✅ Session management integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize session management integration service: {e}")
            raise
    
    @property
    def auth_repo(self):
        """Get auth repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_repo
    
    @property
    def auth_service(self):
        """Get auth service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_service
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user via backend"""
        await self._ensure_initialized()
        try:
            # Get user sessions from backend service
            sessions = await self.auth_service.get_user_sessions(user_id)
            
            if not sessions:
                return []
            
            # Convert to list of dictionaries
            session_list = []
            for session in sessions:
                session_dict = {
                    "session_id": getattr(session, 'session_id', None),
                    "user_id": getattr(session, 'user_id', user_id),
                    "token": getattr(session, 'token', None),
                    "ip_address": getattr(session, 'ip_address', None),
                    "user_agent": getattr(session, 'user_agent', None),
                    "created_at": getattr(session, 'created_at', None),
                    "last_activity": getattr(session, 'last_activity', None),
                    "expires_at": getattr(session, 'expires_at', None),
                    "is_active": getattr(session, 'is_active', True),
                    "device_info": self._parse_device_info(getattr(session, 'user_agent', None)),
                    "location": getattr(session, 'location', None)
                }
                session_list.append(session_dict)
            
            return session_list
            
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
    
    async def create_session(self, user_id: str, ip_address: str = None, 
                           user_agent: str = None) -> Optional[Dict[str, Any]]:
        """Create a new session for a user via backend"""
        await self._ensure_initialized()
        try:
            # Create session via backend service
            session = await self.auth_service.create_user_session(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if not session:
                return None
            
            # Convert to dictionary
            session_dict = {
                "session_id": getattr(session, 'session_id', None),
                "user_id": getattr(session, 'user_id', user_id),
                "token": getattr(session, 'token', None),
                "ip_address": getattr(session, 'ip_address', ip_address),
                "user_agent": getattr(session, 'user_agent', user_agent),
                "created_at": getattr(session, 'created_at', datetime.utcnow().isoformat()),
                "last_activity": getattr(session, 'last_activity', datetime.utcnow().isoformat()),
                "expires_at": getattr(session, 'expires_at', None),
                "is_active": True,
                "device_info": self._parse_device_info(user_agent),
                "location": getattr(session, 'location', None)
            }
            
            logger.info(f"Session created for user {user_id}")
            return session_dict
            
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {e}")
            return None
    
    async def validate_session(self, session_id: str, token: str) -> Optional[Dict[str, Any]]:
        """Validate a session via backend"""
        await self._ensure_initialized()
        try:
            # Validate session via backend service
            session = await self.auth_service.validate_session(session_id, token)
            
            if not session:
                return None
            
            # Check if session is expired
            if hasattr(session, 'expires_at') and session.expires_at:
                if datetime.utcnow() > session.expires_at:
                    logger.warning(f"Session {session_id} has expired")
                    return None
            
            # Update last activity
            await self.update_session_activity(session_id)
            
            # Convert to dictionary
            session_dict = {
                "session_id": getattr(session, 'session_id', session_id),
                "user_id": getattr(session, 'user_id', None),
                "token": getattr(session, 'token', token),
                "ip_address": getattr(session, 'ip_address', None),
                "user_agent": getattr(session, 'user_agent', None),
                "created_at": getattr(session, 'created_at', None),
                "last_activity": getattr(session, 'last_activity', None),
                "expires_at": getattr(session, 'expires_at', None),
                "is_active": getattr(session, 'is_active', True),
                "device_info": self._parse_device_info(getattr(session, 'user_agent', None)),
                "location": getattr(session, 'location', None)
            }
            
            return session_dict
            
        except Exception as e:
            logger.error(f"Error validating session {session_id}: {e}")
            return None
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a specific session via backend"""
        await self._ensure_initialized()
        try:
            # Revoke session via backend service
            success = await self.auth_service.revoke_session(session_id)
            
            if success:
                logger.info(f"Session {session_id} revoked successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error revoking session {session_id}: {e}")
            return False
    
    async def revoke_all_user_sessions(self, user_id: str) -> bool:
        """Revoke all sessions for a user via backend"""
        await self._ensure_initialized()
        try:
            # Get all user sessions
            sessions = await self.get_user_sessions(user_id)
            
            if not sessions:
                logger.info(f"No active sessions found for user {user_id}")
                return True
            
            # Revoke each session
            revoked_count = 0
            for session in sessions:
                if await self.revoke_session(session["session_id"]):
                    revoked_count += 1
            
            logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
            return revoked_count == len(sessions)
            
        except Exception as e:
            logger.error(f"Error revoking all sessions for user {user_id}: {e}")
            return False
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity timestamp via backend"""
        await self._ensure_initialized()
        try:
            # Update session activity via backend service
            success = await self.auth_service.update_session_activity(session_id)
            
            if success:
                logger.debug(f"Session {session_id} activity updated")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating session activity for {session_id}: {e}")
            return False
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a session via backend"""
        await self._ensure_initialized()
        try:
            # Get session from backend service
            session = await self.auth_service.get_session_by_id(session_id)
            
            if not session:
                return None
            
            # Convert to dictionary with additional info
            session_dict = {
                "session_id": getattr(session, 'session_id', session_id),
                "user_id": getattr(session, 'user_id', None),
                "token": getattr(session, 'token', None),
                "ip_address": getattr(session, 'ip_address', None),
                "user_agent": getattr(session, 'user_agent', None),
                "created_at": getattr(session, 'created_at', None),
                "last_activity": getattr(session, 'last_activity', None),
                "expires_at": getattr(session, 'expires_at', None),
                "is_active": getattr(session, 'is_active', True),
                "device_info": self._parse_device_info(getattr(session, 'user_agent', None)),
                "location": getattr(session, 'location', None),
                "security_info": {
                    "is_secure": getattr(session, 'is_secure', False),
                    "is_http_only": getattr(session, 'is_http_only', True),
                    "same_site": getattr(session, 'same_site', 'Lax')
                }
            }
            
            return session_dict
            
        except Exception as e:
            logger.error(f"Error getting session info for {session_id}: {e}")
            return None
    
    async def extend_session(self, session_id: str, extension_hours: int = 24) -> bool:
        """Extend session expiration time via backend"""
        await self._ensure_initialized()
        try:
            # Calculate new expiration time
            new_expires_at = datetime.utcnow() + timedelta(hours=extension_hours)
            
            # Update session expiration via backend service
            success = await self.auth_service.update_session_expiration(session_id, new_expires_at)
            
            if success:
                logger.info(f"Session {session_id} extended by {extension_hours} hours")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error extending session {session_id}: {e}")
            return False
    
    async def get_active_sessions_count(self, user_id: str) -> int:
        """Get count of active sessions for a user via backend"""
        await self._ensure_initialized()
        try:
            sessions = await self.get_user_sessions(user_id)
            return len([s for s in sessions if s.get("is_active", False)])
        except Exception as e:
            logger.error(f"Error getting active sessions count for user {user_id}: {e}")
            return 0
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions via backend"""
        await self._ensure_initialized()
        try:
            # Get all sessions and filter expired ones
            all_sessions = await self.auth_service.get_all_sessions()
            
            if not all_sessions:
                return 0
            
            expired_count = 0
            current_time = datetime.utcnow()
            
            for session in all_sessions:
                if hasattr(session, 'expires_at') and session.expires_at:
                    if current_time > session.expires_at:
                        # Revoke expired session
                        if await self.revoke_session(session.session_id):
                            expired_count += 1
            
            logger.info(f"Cleaned up {expired_count} expired sessions")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    def _parse_device_info(self, user_agent: str) -> Dict[str, Any]:
        """Parse user agent string to extract device information"""
        if not user_agent:
            return {
                "browser": "Unknown",
                "browser_version": "Unknown",
                "os": "Unknown",
                "os_version": "Unknown",
                "device_type": "Unknown",
                "is_mobile": False
            }
        
        try:
            # Simple user agent parsing (in production, use a proper library like user-agents)
            user_agent_lower = user_agent.lower()
            
            # Detect browser
            browser = "Unknown"
            browser_version = "Unknown"
            if "chrome" in user_agent_lower:
                browser = "Chrome"
            elif "firefox" in user_agent_lower:
                browser = "Firefox"
            elif "safari" in user_agent_lower:
                browser = "Safari"
            elif "edge" in user_agent_lower:
                browser = "Edge"
            elif "opera" in user_agent_lower:
                browser = "Opera"
            
            # Detect OS
            os_name = "Unknown"
            os_version = "Unknown"
            if "windows" in user_agent_lower:
                os_name = "Windows"
            elif "mac" in user_agent_lower:
                os_name = "macOS"
            elif "linux" in user_agent_lower:
                os_name = "Linux"
            elif "android" in user_agent_lower:
                os_name = "Android"
            elif "ios" in user_agent_lower:
                os_name = "iOS"
            
            # Detect device type
            device_type = "Desktop"
            is_mobile = False
            if any(mobile in user_agent_lower for mobile in ["mobile", "android", "iphone", "ipad"]):
                device_type = "Mobile"
                is_mobile = True
            elif "tablet" in user_agent_lower:
                device_type = "Tablet"
                is_mobile = True
            
            return {
                "browser": browser,
                "browser_version": browser_version,
                "os": os_name,
                "os_version": os_version,
                "device_type": device_type,
                "is_mobile": is_mobile,
                "raw_user_agent": user_agent
            }
            
        except Exception as e:
            logger.warning(f"Error parsing user agent '{user_agent}': {e}")
            return {
                "browser": "Unknown",
                "browser_version": "Unknown",
                "os": "Unknown",
                "os_version": "Unknown",
                "device_type": "Unknown",
                "is_mobile": False,
                "raw_user_agent": user_agent
            }


# Export the integration service
__all__ = ['SessionManagementService']
