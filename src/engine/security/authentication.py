"""
Authentication Module
===================

Core authentication functionality including JWT, OAuth, LDAP, and MFA support.
"""

import asyncio
import logging
import time
import jwt
import hashlib
import secrets
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

from .models import (
    User, UserStatus, AuthenticationResult, SecurityContext,
    AuthenticationMethod
)

logger = logging.getLogger(__name__)


class Authenticator(ABC):
    """Abstract base class for authentication"""
    
    def __init__(self, name: str = "Authenticator"):
        self.name = name
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._failed_attempts: Dict[str, int] = {}
        self._lockout_threshold = 5
        self._lockout_duration = 300  # 5 minutes
        
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """Authenticate user with credentials"""
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> Optional[SecurityContext]:
        """Validate authentication token"""
        pass
    
    def create_user(self, username: str, email: str, password: str, 
                   roles: List[str] = None) -> User:
        """Create a new user"""
        if username in self._users:
            raise ValueError(f"User {username} already exists")
        
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            salt=salt,
            roles=roles or []
        )
        
        self._users[username] = user
        logger.info(f"Created user: {username}")
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self._users.get(username)
    
    def update_user(self, username: str, **kwargs) -> bool:
        """Update user information"""
        if username not in self._users:
            return False
        
        user = self._users[username]
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.now(timezone.utc)
        logger.info(f"Updated user: {username}")
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete user"""
        if username not in self._users:
            return False
        
        del self._users[username]
        logger.info(f"Deleted user: {username}")
        return True
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _verify_password(self, password: str, salt: str, hash_value: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password, salt) == hash_value
    
    def _check_account_lockout(self, username: str) -> bool:
        """Check if account is locked out"""
        if username not in self._failed_attempts:
            return False
        
        attempts = self._failed_attempts[username]
        if attempts >= self._lockout_threshold:
            # Check if lockout period has expired
            if username in self._sessions:
                lockout_time = self._sessions[username].get('lockout_until')
                if lockout_time and datetime.now(timezone.utc) < lockout_time:
                    return True
                else:
                    # Lockout expired, reset
                    del self._failed_attempts[username]
                    if username in self._sessions:
                        del self._sessions[username]['lockout_until']
        
        return False
    
    def _record_failed_attempt(self, username: str) -> None:
        """Record failed authentication attempt"""
        if username not in self._failed_attempts:
            self._failed_attempts[username] = 0
        
        self._failed_attempts[username] += 1
        
        if self._failed_attempts[username] >= self._lockout_threshold:
            lockout_until = datetime.now(timezone.utc) + timedelta(seconds=self._lockout_duration)
            if username not in self._sessions:
                self._sessions[username] = {}
            self._sessions[username]['lockout_until'] = lockout_until
            logger.warning(f"Account locked: {username} until {lockout_until}")
    
    def _reset_failed_attempts(self, username: str) -> None:
        """Reset failed authentication attempts"""
        if username in self._failed_attempts:
            del self._failed_attempts[username]
        if username in self._sessions and 'lockout_until' in self._sessions[username]:
            del self._sessions[username]['lockout_until']


class AsyncAuthenticator(Authenticator):
    """Asynchronous authenticator base class"""
    
    async def authenticate_async(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """Authenticate user asynchronously"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.authenticate, credentials
        )
    
    async def validate_token_async(self, token: str) -> Optional[SecurityContext]:
        """Validate authentication token asynchronously"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.validate_token, token
        )


class JWTAuthenticator(Authenticator):
    """JWT-based authentication"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 token_expiry: int = 3600, refresh_expiry: int = 86400):
        super().__init__("JWTAuthenticator")
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry = token_expiry
        self.refresh_expiry = refresh_expiry
    
    def authenticate(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """Authenticate user with username/password and return JWT token"""
        username = credentials.get('username')
        password = credentials.get('password')
        
        if not username or not password:
            return AuthenticationResult(
                success=False,
                message="Username and password required",
                error_code="MISSING_CREDENTIALS"
            )
        
        # Check account lockout
        if self._check_account_lockout(username):
            return AuthenticationResult(
                success=False,
                message="Account temporarily locked",
                error_code="ACCOUNT_LOCKED"
            )
        
        # Verify user exists and password is correct
        user = self.get_user(username)
        if not user:
            self._record_failed_attempt(username)
            return AuthenticationResult(
                success=False,
                message="Invalid credentials",
                error_code="INVALID_CREDENTIALS"
            )
        
        if not user.is_active():
            return AuthenticationResult(
                success=False,
                message="Account is not active",
                error_code="ACCOUNT_INACTIVE"
            )
        
        if not self._verify_password(password, user.salt, user.password_hash):
            self._record_failed_attempt(username)
            return AuthenticationResult(
                success=False,
                message="Invalid credentials",
                error_code="INVALID_CREDENTIALS"
            )
        
        # Authentication successful
        self._reset_failed_attempts(username)
        user.last_login = datetime.now(timezone.utc)
        
        # Generate tokens
        access_token = self._generate_token(user, self.token_expiry)
        refresh_token = self._generate_token(user, self.refresh_expiry, is_refresh=True)
        
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.token_expiry)
        
        logger.info(f"User authenticated: {username}")
        
        return AuthenticationResult(
            success=True,
            user=user,
            token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            message="Authentication successful"
        )
    
    def validate_token(self, token: str) -> Optional[SecurityContext]:
        """Validate JWT token and return security context"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None
            
            # Check if it's a refresh token
            if payload.get('type') == 'refresh':
                return None
            
            user_id = payload.get('user_id')
            username = payload.get('username')
            
            if not user_id or not username:
                return None
            
            user = self.get_user(username)
            if not user or not user.is_active():
                return None
            
            # Create security context
            context = SecurityContext(
                user_id=user_id,
                username=username,
                roles=user.roles,
                session_id=payload.get('session_id'),
                timestamp=datetime.now(timezone.utc)
            )
            
            return context
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> AuthenticationResult:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if it's actually a refresh token
            if payload.get('type') != 'refresh':
                return AuthenticationResult(
                    success=False,
                    message="Invalid refresh token",
                    error_code="INVALID_REFRESH_TOKEN"
                )
            
            # Check if token is expired
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return AuthenticationResult(
                    success=False,
                    message="Refresh token expired",
                    error_code="REFRESH_TOKEN_EXPIRED"
                )
            
            username = payload.get('username')
            user = self.get_user(username)
            
            if not user or not user.is_active():
                return AuthenticationResult(
                    success=False,
                    message="User not found or inactive",
                    error_code="USER_INACTIVE"
                )
            
            # Generate new access token
            access_token = self._generate_token(user, self.token_expiry)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.token_expiry)
            
            return AuthenticationResult(
                success=True,
                user=user,
                token=access_token,
                expires_at=expires_at,
                message="Token refreshed successfully"
            )
            
        except jwt.InvalidTokenError:
            return AuthenticationResult(
                success=False,
                message="Invalid refresh token",
                error_code="INVALID_REFRESH_TOKEN"
            )
    
    def _generate_token(self, user: User, expiry: int, is_refresh: bool = False) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'roles': user.roles,
            'type': 'refresh' if is_refresh else 'access',
            'session_id': secrets.token_hex(16),
            'exp': int(time.time()) + expiry,
            'iat': int(time.time())
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)


class OAuthAuthenticator(Authenticator):
    """OAuth-based authentication"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 redirect_uri: str, auth_url: str, token_url: str):
        super().__init__("OAuthAuthenticator")
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = auth_url
        self.token_url = token_url
    
    def authenticate(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """Authenticate using OAuth code"""
        code = credentials.get('code')
        if not code:
            return AuthenticationResult(
                success=False,
                message="OAuth authorization code required",
                error_code="MISSING_OAUTH_CODE"
            )
        
        # In a real implementation, you would exchange the code for tokens
        # and validate the user with the OAuth provider
        # For now, we'll simulate this process
        
        # Simulate OAuth token exchange
        user_info = self._exchange_code_for_user_info(code)
        if not user_info:
            return AuthenticationResult(
                success=False,
                message="Failed to exchange OAuth code",
                error_code="OAUTH_EXCHANGE_FAILED"
            )
        
        # Find or create user
        user = self._get_or_create_oauth_user(user_info)
        
        # Generate session token
        session_token = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Store session
        self._sessions[session_token] = {
            'user_id': user.id,
            'username': user.username,
            'expires_at': expires_at,
            'oauth_provider': user_info.get('provider')
        }
        
        return AuthenticationResult(
            success=True,
            user=user,
            token=session_token,
            expires_at=expires_at,
            message="OAuth authentication successful"
        )
    
    def validate_token(self, token: str) -> Optional[SecurityContext]:
        """Validate OAuth session token"""
        if token not in self._sessions:
            return None
        
        session = self._sessions[token]
        if session['expires_at'] < datetime.now(timezone.utc):
            del self._sessions[token]
            return None
        
        user = self.get_user(session['username'])
        if not user or not user.is_active():
            return None
        
        return SecurityContext(
            user_id=session['user_id'],
            username=session['username'],
            roles=user.roles,
            session_id=token,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _exchange_code_for_user_info(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange OAuth code for user information (simulated)"""
        # In real implementation, make HTTP request to OAuth provider
        # For now, return mock user info
        return {
            'provider': 'google',
            'email': 'user@example.com',
            'name': 'Test User',
            'sub': '12345'
        }
    
    def _get_or_create_oauth_user(self, user_info: Dict[str, Any]) -> User:
        """Get existing user or create new one from OAuth info"""
        email = user_info['email']
        
        # Check if user exists by email
        for user in self._users.values():
            if user.email == email:
                return user
        
        # Create new user
        username = email.split('@')[0]
        user = User(
            username=username,
            email=email,
            status=UserStatus.ACTIVE
        )
        
        self._users[username] = user
        return user


class LDAPAuthenticator(Authenticator):
    """LDAP-based authentication"""
    
    def __init__(self, server_url: str, base_dn: str, bind_dn: str = None, 
                 bind_password: str = None):
        super().__init__("LDAPAuthenticator")
        self.server_url = server_url
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_password = bind_password
    
    def authenticate(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """Authenticate user against LDAP server"""
        username = credentials.get('username')
        password = credentials.get('password')
        
        if not username or not password:
            return AuthenticationResult(
                success=False,
                message="Username and password required",
                error_code="MISSING_CREDENTIALS"
            )
        
        # Check account lockout
        if self._check_account_lockout(username):
            return AuthenticationResult(
                success=False,
                message="Account temporarily locked",
                error_code="ACCOUNT_LOCKED"
            )
        
        # Attempt LDAP authentication
        if not self._authenticate_ldap(username, password):
            self._record_failed_attempt(username)
            return AuthenticationResult(
                success=False,
                message="Invalid credentials",
                error_code="INVALID_CREDENTIALS"
            )
        
        # Authentication successful
        self._reset_failed_attempts(username)
        
        # Get or create user
        user = self._get_or_create_ldap_user(username)
        user.last_login = datetime.now(timezone.utc)
        
        # Generate session token
        session_token = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        self._sessions[session_token] = {
            'user_id': user.id,
            'username': user.username,
            'expires_at': expires_at,
            'auth_method': 'ldap'
        }
        
        return AuthenticationResult(
            success=True,
            user=user,
            token=session_token,
            expires_at=expires_at,
            message="LDAP authentication successful"
        )
    
    def validate_token(self, token: str) -> Optional[SecurityContext]:
        """Validate LDAP session token"""
        if token not in self._sessions:
            return None
        
        session = self._sessions[token]
        if session['expires_at'] < datetime.now(timezone.utc):
            del self._sessions[token]
            return None
        
        user = self.get_user(session['username'])
        if not user or not user.is_active():
            return None
        
        return SecurityContext(
            user_id=session['user_id'],
            username=session['username'],
            roles=user.roles,
            session_id=token,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _authenticate_ldap(self, username: str, password: str) -> bool:
        """Authenticate against LDAP server (simulated)"""
        # In real implementation, use ldap3 or similar library
        # For now, simulate successful authentication for test users
        return username in ['admin', 'user', 'test'] and password == 'password'
    
    def _get_or_create_ldap_user(self, username: str) -> User:
        """Get existing user or create new one from LDAP"""
        if username in self._users:
            return self._users[username]
        
        # Create new user from LDAP
        user = User(
            username=username,
            email=f"{username}@example.com",
            status=UserStatus.ACTIVE
        )
        
        self._users[username] = user
        return user


class MultiFactorAuthenticator(Authenticator):
    """Multi-factor authentication support"""
    
    def __init__(self, base_authenticator: Authenticator):
        super().__init__("MultiFactorAuthenticator")
        self.base_authenticator = base_authenticator
        self._mfa_codes: Dict[str, Dict[str, Any]] = {}
    
    def authenticate(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """Authenticate with MFA if enabled"""
        # First, authenticate with base authenticator
        base_result = self.base_authenticator.authenticate(credentials)
        
        if not base_result.success:
            return base_result
        
        user = base_result.user
        if not user.mfa_enabled:
            return base_result
        
        # MFA is enabled, check if MFA code provided
        mfa_code = credentials.get('mfa_code')
        if not mfa_code:
            return AuthenticationResult(
                success=False,
                message="MFA code required",
                error_code="MFA_CODE_REQUIRED",
                metadata={'requires_mfa': True, 'user_id': user.id}
            )
        
        # Validate MFA code
        if not self._validate_mfa_code(user.id, mfa_code):
            return AuthenticationResult(
                success=False,
                message="Invalid MFA code",
                error_code="INVALID_MFA_CODE"
            )
        
        # MFA successful, return original result
        return base_result
    
    def generate_mfa_code(self, user_id: str) -> str:
        """Generate MFA code for user"""
        code = secrets.token_hex(3).upper()[:6]  # 6-character hex code
        
        self._mfa_codes[user_id] = {
            'code': code,
            'expires_at': datetime.now(timezone.utc) + timedelta(minutes=5),
            'attempts': 0
        }
        
        return code
    
    def _validate_mfa_code(self, user_id: str, code: str) -> bool:
        """Validate MFA code"""
        if user_id not in self._mfa_codes:
            return False
        
        mfa_data = self._mfa_codes[user_id]
        
        # Check if code expired
        if mfa_data['expires_at'] < datetime.now(timezone.utc):
            del self._mfa_codes[user_id]
            return False
        
        # Check attempts
        if mfa_data['attempts'] >= 3:
            del self._mfa_codes[user_id]
            return False
        
        # Validate code
        if mfa_data['code'] == code:
            del self._mfa_codes[user_id]
            return True
        
        # Increment attempts
        mfa_data['attempts'] += 1
        return False
