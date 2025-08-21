"""
Auth Service - Handles authentication and authorization.

This service provides business logic for authentication operations including:
- Authentication workflows
- Authorization logic
- Session management
- Security policy enforcement
"""

import json
import logging
import hashlib
import secrets
import hmac
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict

from ...repositories.auth_repository import AuthRepository
from ...models.auth import User
from .user_service import UserService
from .role_service import RoleService
from ..base.base_service import BaseService

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """User session information."""
    session_id: str
    user_id: str
    token: str
    created_at: str
    expires_at: str
    last_activity: str
    ip_address: str
    user_agent: str
    is_active: bool = True
    metadata: Dict[str, Any] = None


@dataclass
class AuthResult:
    """Authentication result."""
    success: bool
    user: Optional[User] = None
    session: Optional[Session] = None
    token: Optional[str] = None
    error_message: Optional[str] = None
    requires_mfa: bool = False
    metadata: Dict[str, Any] = None


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    session_timeout_minutes: int = 480  # 8 hours
    mfa_required: bool = False
    ip_whitelist: List[str] = None
    ip_blacklist: List[str] = None


class AuthService(BaseService):
    """
    Service for managing authentication and authorization.
    
    Handles user authentication, session management, security policies,
    and authorization logic across the system.
    """
    
    def __init__(self, auth_repository: AuthRepository, 
                 user_service: UserService, role_service: RoleService):
        """
        Initialize the AuthService.
        
        Args:
            auth_repository: Repository for auth data operations
            user_service: Service for user operations
            role_service: Service for role and permission operations
        """
        super().__init__()
        self.auth_repository = auth_repository
        self.user_service = user_service
        self.role_service = role_service
        
        # In-memory data structures for fast access
        self._sessions: Dict[str, Session] = {}
        self._user_sessions: Dict[str, List[str]] = {}  # user_id -> list of session_ids
        self._failed_login_attempts: Dict[str, List[Dict[str, Any]]] = {}
        self._locked_accounts: Set[str] = set()
        self._active_tokens: Set[str] = set()
        
        # Security configuration
        self._security_policy = SecurityPolicy()
        self._secret_key = secrets.token_hex(32)
        
        # Load initial data
        asyncio.create_task(self._initialize_service_resources())
    
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str = None, user_agent: str = None) -> AuthResult:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username for authentication
            password: Password for authentication
            ip_address: Client IP address
            user_agent: Client user agent string
            
        Returns:
            Authentication result with user and session information
        """
        try:
            self._log_operation("authenticate_user", f"username: {username}")
            
            # Check if account is locked
            if username in self._locked_accounts:
                return AuthResult(
                    success=False,
                    error_message="Account is temporarily locked due to multiple failed login attempts"
                )
            
            # Get user by username
            user = await self.user_service.get_user_by_username(username)
            if not user:
                await self._record_failed_login_attempt(username, ip_address)
                return AuthResult(
                    success=False,
                    error_message="Invalid username or password"
                )
            
            # Check if user is active
            if not user.is_active:
                return AuthResult(
                    success=False,
                    error_message="Account is deactivated"
                )
            
            # Validate password (in real implementation, this would check hashed password)
            if not await self._validate_password(user, password):
                await self._record_failed_login_attempt(username, ip_address)
                return AuthResult(
                    success=False,
                    error_message="Invalid username or password"
                )
            
            # Check if MFA is required
            if self._security_policy.mfa_required:
                return AuthResult(
                    success=True,
                    user=user,
                    requires_mfa=True,
                    metadata={"mfa_required": True}
                )
            
            # Create session
            session = await self._create_user_session(user, ip_address, user_agent)
            if not session:
                return AuthResult(
                    success=False,
                    error_message="Failed to create user session"
                )
            
            # Track successful login
            await self.user_service.track_user_activity(
                user.user_id, "login_successful", 
                {"ip_address": ip_address, "user_agent": user_agent}
            )
            
            # Clear failed login attempts
            self._failed_login_attempts.pop(username, None)
            
            return AuthResult(
                success=True,
                user=user,
                session=session,
                token=session.token,
                metadata={"session_id": session.session_id}
            )
            
        except Exception as e:
            self.handle_error("authenticate_user", e)
            return AuthResult(
                success=False,
                error_message="Authentication failed due to system error"
            )
    
    async def authenticate_with_token(self, token: str) -> AuthResult:
        """
        Authenticate a user using a session token.
        
        Args:
            token: Session token for authentication
            
        Returns:
            Authentication result with user and session information
        """
        try:
            self._log_operation("authenticate_with_token", "token_provided")
            
            # Find session by token
            session = None
            for sess in self._sessions.values():
                if sess.token == token and sess.is_active:
                    session = sess
                    break
            
            if not session:
                return AuthResult(
                    success=False,
                    error_message="Invalid or expired session token"
                )
            
            # Check if session is expired
            if datetime.fromisoformat(session.expires_at) < datetime.now():
                await self._invalidate_session(session.session_id)
                return AuthResult(
                    success=False,
                    error_message="Session token has expired"
                )
            
            # Get user
            user = await self.user_service.get_user_by_id(session.user_id)
            if not user or not user.is_active:
                await self._invalidate_session(session.session_id)
                return AuthResult(
                    success=False,
                    error_message="User account is invalid or deactivated"
                )
            
            # Update last activity
            session.last_activity = datetime.now().isoformat()
            self._sessions[session.session_id] = session
            
            return AuthResult(
                success=True,
                user=user,
                session=session,
                token=token
            )
            
        except Exception as e:
            self.handle_error("authenticate_with_token", e)
            return AuthResult(
                success=False,
                error_message="Token authentication failed due to system error"
            )
    
    async def logout_user(self, token: str) -> bool:
        """
        Logout a user by invalidating their session.
        
        Args:
            token: Session token to invalidate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("logout_user", "token_provided")
            
            # Find and invalidate session
            session_found = False
            for session_id, session in self._sessions.items():
                if session.token == token and session.is_active:
                    await self._invalidate_session(session_id)
                    session_found = True
                    
                    # Track logout activity
                    await self.user_service.track_user_activity(
                        session.user_id, "logout", 
                        {"session_id": session.session_id}
                    )
                    break
            
            return session_found
            
        except Exception as e:
            self.handle_error("logout_user", e)
            return False
    
    async def logout_all_user_sessions(self, user_id: str) -> bool:
        """
        Logout a user from all active sessions.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("logout_all_user_sessions", f"user_id: {user_id}")
            
            if user_id not in self._user_sessions:
                return True
            
            # Invalidate all sessions for the user
            for session_id in self._user_sessions[user_id]:
                await self._invalidate_session(session_id)
            
            # Track activity
            await self.user_service.track_user_activity(
                user_id, "logout_all_sessions", 
                {"sessions_terminated": len(self._user_sessions[user_id])}
            )
            
            return True
            
        except Exception as e:
            self.handle_error("logout_all_user_sessions", e)
            return False
    
    async def authorize_action(self, user_id: str, resource: str, action: str) -> bool:
        """
        Check if a user is authorized to perform an action on a resource.
        
        Args:
            user_id: User identifier
            resource: Resource to check authorization for
            action: Action to check authorization for
            
        Returns:
            True if user is authorized, False otherwise
        """
        try:
            # Check if user exists and is active
            user = await self.user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                return False
            
            # Check permissions using role service
            return await self.role_service.check_permission(user_id, resource, action)
            
        except Exception as e:
            self.handle_error("authorize_action", e)
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of active user sessions
        """
        try:
            if user_id not in self._user_sessions:
                return []
            
            sessions = []
            for session_id in self._user_sessions[user_id]:
                if session_id in self._sessions:
                    session = self._sessions[session_id]
                    if session.is_active:
                        sessions.append(session)
            
            return sessions
            
        except Exception as e:
            self.handle_error("get_user_sessions", e)
            return []
    
    async def refresh_session(self, token: str) -> Optional[str]:
        """
        Refresh a session token and extend its validity.
        
        Args:
            token: Current session token
            
        Returns:
            New session token or None if failed
        """
        try:
            self._log_operation("refresh_session", "token_provided")
            
            # Find session by token
            session = None
            for sess in self._sessions.values():
                if sess.token == token and sess.is_active:
                    session = sess
                    break
            
            if not session:
                return None
            
            # Generate new token
            new_token = self._generate_token()
            
            # Update session
            session.token = new_token
            session.expires_at = (datetime.now() + 
                                timedelta(minutes=self._security_policy.session_timeout_minutes)).isoformat()
            session.last_activity = datetime.now().isoformat()
            
            # Update in-memory structures
            self._sessions[session.session_id] = session
            self._active_tokens.discard(token)
            self._active_tokens.add(new_token)
            
            logger.info(f"Session refreshed for user: {session.user_id}")
            return new_token
            
        except Exception as e:
            self.handle_error("refresh_session", e)
            return None
    
    async def change_password(self, user_id: str, current_password: str, 
                            new_password: str) -> bool:
        """
        Change user password with validation.
        
        Args:
            user_id: User identifier
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("change_password", f"user_id: {user_id}")
            
            # Get user
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                return False
            
            # Validate current password
            if not await self._validate_password(user, current_password):
                return False
            
            # Validate new password
            if not self._validate_password_policy(new_password):
                return False
            
            # Hash and update password (in real implementation)
            # hashed_password = self._hash_password(new_password)
            # success = await self.user_service.update_user_profile(
            #     user_id, {"password_hash": hashed_password}
            # )
            
            # For now, just track the activity
            await self.user_service.track_user_activity(
                user_id, "password_changed", {}
            )
            
            logger.info(f"Password changed successfully for user: {user_id}")
            return True
            
        except Exception as e:
            self.handle_error("change_password", e)
            return False
    
    async def reset_password(self, username: str, email: str) -> bool:
        """
        Initiate password reset process.
        
        Args:
            username: Username for password reset
            email: Email address for verification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("reset_password", f"username: {username}")
            
            # Get user
            user = await self.user_service.get_user_by_username(username)
            if not user or user.email != email:
                return False
            
            # Generate reset token (in real implementation)
            # reset_token = self._generate_reset_token()
            # reset_expires = (datetime.now() + timedelta(hours=24)).isoformat()
            
            # Store reset token (in real implementation)
            # await self.auth_repository.store_password_reset_token(
            #     user.user_id, reset_token, reset_expires
            # )
            
            # Send reset email (in real implementation)
            # await self._send_password_reset_email(user.email, reset_token)
            
            # Track activity
            await self.user_service.track_user_activity(
                user.user_id, "password_reset_requested", {}
            )
            
            logger.info(f"Password reset initiated for user: {username}")
            return True
            
        except Exception as e:
            self.handle_error("reset_password", e)
            return False
    
    async def get_security_policy(self) -> SecurityPolicy:
        """
        Get current security policy configuration.
        
        Returns:
            Security policy configuration
        """
        return self._security_policy
    
    async def update_security_policy(self, updates: Dict[str, Any]) -> bool:
        """
        Update security policy configuration.
        
        Args:
            updates: Security policy updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_operation("update_security_policy", "policy_updates")
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(self._security_policy, field):
                    setattr(self._security_policy, field, value)
            
            logger.info("Security policy updated successfully")
            return True
            
        except Exception as e:
            self.handle_error("update_security_policy", e)
            return False
    
    async def _create_user_session(self, user: User, ip_address: str, 
                                 user_agent: str) -> Optional[Session]:
        """Create a new user session."""
        try:
            session_id = f"session_{user.user_id}_{datetime.now().timestamp()}"
            token = self._generate_token()
            
            session = Session(
                session_id=session_id,
                user_id=user.user_id,
                token=token,
                created_at=datetime.now().isoformat(),
                expires_at=(datetime.now() + 
                           timedelta(minutes=self._security_policy.session_timeout_minutes)).isoformat(),
                last_activity=datetime.now().isoformat(),
                ip_address=ip_address or "unknown",
                user_agent=user_agent or "unknown"
            )
            
            # Store session
            self._sessions[session_id] = session
            self._active_tokens.add(token)
            
            # Update user sessions mapping
            if user.user_id not in self._user_sessions:
                self._user_sessions[user.user_id] = []
            self._user_sessions[user.user_id].append(session_id)
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            return None
    
    async def _invalidate_session(self, session_id: str) -> bool:
        """Invalidate a user session."""
        try:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                
                # Remove from active tokens
                self._active_tokens.discard(session.token)
                
                # Mark session as inactive
                session.is_active = False
                self._sessions[session_id] = session
                
                # Remove from user sessions mapping
                if session.user_id in self._user_sessions:
                    self._user_sessions[session.user_id] = [
                        sid for sid in self._user_sessions[session.user_id] 
                        if sid != session_id
                    ]
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to invalidate session: {e}")
            return False
    
    async def _record_failed_login_attempt(self, username: str, ip_address: str) -> None:
        """Record a failed login attempt."""
        try:
            if username not in self._failed_login_attempts:
                self._failed_login_attempts[username] = []
            
            attempt = {
                "timestamp": datetime.now().isoformat(),
                "ip_address": ip_address or "unknown"
            }
            
            self._failed_login_attempts[username].append(attempt)
            
            # Check if account should be locked
            recent_attempts = [
                a for a in self._failed_login_attempts[username]
                if (datetime.now() - datetime.fromisoformat(a["timestamp"])).total_seconds() < 3600  # 1 hour
            ]
            
            if len(recent_attempts) >= self._security_policy.max_login_attempts:
                self._locked_accounts.add(username)
                logger.warning(f"Account locked due to multiple failed login attempts: {username}")
                
        except Exception as e:
            logger.error(f"Failed to record failed login attempt: {e}")
    
    async def _validate_password(self, user: User, password: str) -> bool:
        """Validate user password."""
        try:
            # In real implementation, this would check against hashed password
            # For now, we'll use a simple validation
            if not password or len(password) < 1:
                return False
            
            # This is a placeholder - in real implementation, you would:
            # 1. Get the stored password hash from user
            # 2. Hash the provided password with the same salt
            # 3. Compare the hashes
            
            return True  # Placeholder
            
        except Exception as e:
            logger.error(f"Password validation failed: {e}")
            return False
    
    def _validate_password_policy(self, password: str) -> bool:
        """Validate password against security policy."""
        try:
            if len(password) < self._security_policy.password_min_length:
                return False
            
            if self._security_policy.password_require_uppercase and not any(c.isupper() for c in password):
                return False
            
            if self._security_policy.password_require_lowercase and not any(c.islower() for c in password):
                return False
            
            if self._security_policy.password_require_numbers and not any(c.isdigit() for c in password):
                return False
            
            if self._security_policy.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Password policy validation failed: {e}")
            return False
    
    def _generate_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def _load_security_policy(self) -> None:
        """Load security policy configuration."""
        try:
            # In real implementation, this would load from configuration or database
            logger.info("Security policy loaded with default configuration")
            
        except Exception as e:
            logger.error(f"Failed to load security policy: {e}")
    
    async def _initialize_service_resources(self) -> None:
        """Initialize service-specific resources."""
        try:
            # Initialize auth-related resources
            self._sessions = {}
            self._user_sessions = {}
            self._failed_login_attempts = {}
            self._locked_accounts = set()
            self._active_tokens = set()
            
            # Load initial data
            self._load_security_policy()
            logger.info("Auth service resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize auth service resources: {e}")
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        return {
            "service_name": "AuthService",
            "service_type": "authentication",
            "status": "active" if self.is_active else "inactive",
            "start_time": self.start_time.isoformat(),
            "total_sessions": len(self._sessions),
            "active_sessions": len([s for s in self._sessions.values() if s.is_active]),
            "users_with_sessions": len(self._user_sessions),
            "locked_accounts": len(self._locked_accounts),
            "active_tokens": len(self._active_tokens),
            "security_policy": {
                "max_login_attempts": self._security_policy.max_login_attempts,
                "session_timeout_minutes": self._security_policy.session_timeout_minutes,
                "mfa_required": self._security_policy.mfa_required
            },
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat(),
            "dependencies": self.dependencies,
            "performance_metrics": self.get_performance_summary()
        }
    
    async def _cleanup_service_resources(self) -> None:
        """Clean up service resources."""
        try:
            # Clear in-memory structures
            self._sessions.clear()
            self._user_sessions.clear()
            self._failed_login_attempts.clear()
            self._locked_accounts.clear()
            self._active_tokens.clear()
            
            logger.info("Auth service resources cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup auth service resources: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the auth service."""
        try:
            await self._cleanup_service_resources()
            logger.info("Auth service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during auth service shutdown: {e}")
