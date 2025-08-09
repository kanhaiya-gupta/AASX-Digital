"""
Session Management Service
=========================

Handles user sessions, device tracking, and session management for the auth module.
"""

import secrets
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from user_agents import parse

logger = logging.getLogger(__name__)

class SessionService:
    """Service for handling user sessions"""
    
    def __init__(self, auth_db):
        """Initialize session service with database connection"""
        self.auth_db = auth_db
        self.session_expiry_days = 30
        self.remember_me_expiry_days = 365
    
    def create_session(self, user_id: str, request, remember_me: bool = False) -> Dict[str, Any]:
        """Create a new user session"""
        try:
            # Generate session ID
            session_id = secrets.token_urlsafe(32)
            
            # Get device information
            device_info = self._extract_device_info(request)
            
            # Set expiry based on remember me
            if remember_me:
                expires_at = datetime.now() + timedelta(days=self.remember_me_expiry_days)
            else:
                expires_at = datetime.now() + timedelta(days=self.session_expiry_days)
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "device_info": device_info,
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("User-Agent"),
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "expires_at": expires_at,
                "is_active": True
            }
            
            # Store session in database
            self.auth_db.create_user_session(session_data)
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            return self.auth_db.get_user_session(session_id)
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""
        try:
            return self.auth_db.update_session_activity(session_id)
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            return False
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session"""
        try:
            return self.auth_db.revoke_user_session(session_id)
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            return False
    
    def revoke_all_user_sessions(self, user_id: str, exclude_session_id: str = None) -> bool:
        """Revoke all sessions for a user except the current one"""
        try:
            return self.auth_db.revoke_all_user_sessions(user_id, exclude_session_id)
        except Exception as e:
            logger.error(f"Error revoking all user sessions: {e}")
            return False
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        try:
            return self.auth_db.get_user_sessions(user_id)
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            return self.auth_db.cleanup_expired_sessions()
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    def is_session_valid(self, session_id: str) -> bool:
        """Check if session is valid and not expired"""
        try:
            session = self.get_session(session_id)
            if not session:
                return False
            
            # Check if session is active and not expired
            if not session.get("is_active", False):
                return False
            
            expires_at = session.get("expires_at")
            if expires_at and datetime.now() > expires_at:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking session validity: {e}")
            return False
    
    def _extract_device_info(self, request) -> Dict[str, Any]:
        """Extract device information from request"""
        try:
            user_agent_string = request.headers.get("User-Agent", "")
            user_agent = parse(user_agent_string)
            
            device_info = {
                "browser": user_agent.browser.family if user_agent.browser else "Unknown",
                "browser_version": user_agent.browser.version_string if user_agent.browser else "",
                "os": user_agent.os.family if user_agent.os else "Unknown",
                "os_version": user_agent.os.version_string if user_agent.os else "",
                "device": user_agent.device.family if user_agent.device else "Unknown",
                "is_mobile": user_agent.is_mobile,
                "is_tablet": user_agent.is_tablet,
                "is_pc": user_agent.is_pc
            }
            
            return device_info
            
        except Exception as e:
            logger.error(f"Error extracting device info: {e}")
            return {"browser": "Unknown", "os": "Unknown", "device": "Unknown"}
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address from request"""
        try:
            # Check for forwarded headers
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            
            # Check for real IP header
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip
            
            # Get from request client
            if request.client:
                return request.client.host
            
            return "Unknown"
            
        except Exception as e:
            logger.error(f"Error getting client IP: {e}")
            return "Unknown"
    
    def get_session_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get session statistics for a user"""
        try:
            sessions = self.get_user_sessions(user_id)
            
            stats = {
                "total_sessions": len(sessions),
                "active_sessions": len([s for s in sessions if s.get("is_active", False)]),
                "expired_sessions": len([s for s in sessions if not s.get("is_active", False)]),
                "devices": {},
                "locations": {}
            }
            
            # Count devices
            for session in sessions:
                device_info = session.get("device_info", {})
                device_key = f"{device_info.get('browser', 'Unknown')} on {device_info.get('os', 'Unknown')}"
                stats["devices"][device_key] = stats["devices"].get(device_key, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting session statistics: {e}")
            return {"total_sessions": 0, "active_sessions": 0, "expired_sessions": 0} 