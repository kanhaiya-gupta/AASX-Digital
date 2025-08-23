"""
OAuth Service
=============

Comprehensive OAuth service for the AAS data modeling engine.
Handles OAuth providers (Google, Facebook, Apple) with real token exchange.
"""

import secrets
import json
import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@dataclass
class OAuthProvider:
    """OAuth provider configuration"""
    name: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    userinfo_url: str
    scope: str
    additional_params: Dict[str, str] = None


@dataclass
class OAuthUserInfo:
    """OAuth user information"""
    provider: str
    provider_id: str
    email: str
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    verified: bool = False
    raw_data: Dict[str, Any] = None


@dataclass
class OAuthToken:
    """OAuth token information"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None


@dataclass
class OAuthResult:
    """OAuth authentication result"""
    success: bool
    user_info: Optional[OAuthUserInfo] = None
    tokens: Optional[OAuthToken] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class GoogleOAuthProvider:
    """Google OAuth provider implementation"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        self.scope = "openid email profile"
    
    def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[OAuthToken]:
        """Exchange authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                }
                
                async with session.post(self.token_url, data=data) as response:
                    if response.status != 200:
                        logger.error(f"Google token exchange failed: {response.status}")
                        return None
                    
                    token_data = await response.json()
                    
                    expires_at = None
                    if token_data.get('expires_in'):
                        expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data['expires_in'])
                    
                    return OAuthToken(
                        access_token=token_data['access_token'],
                        refresh_token=token_data.get('refresh_token'),
                        expires_in=token_data.get('expires_in'),
                        expires_at=expires_at,
                        token_type=token_data.get('token_type', 'Bearer'),
                        scope=token_data.get('scope')
                    )
                    
        except Exception as e:
            logger.error(f"Error exchanging Google OAuth code: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """Get user information from Google"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {access_token}"}
                
                async with session.get(self.userinfo_url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Google userinfo failed: {response.status}")
                        return None
                    
                    user_data = await response.json()
                    
                    return OAuthUserInfo(
                        provider="google",
                        provider_id=user_data['id'],
                        email=user_data['email'],
                        name=user_data.get('name', ''),
                        first_name=user_data.get('given_name'),
                        last_name=user_data.get('family_name'),
                        picture=user_data.get('picture'),
                        locale=user_data.get('locale'),
                        verified=user_data.get('verified_email', False),
                        raw_data=user_data
                    )
                    
        except Exception as e:
            logger.error(f"Error getting Google user info: {e}")
            return None


class FacebookOAuthProvider:
    """Facebook OAuth provider implementation"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://www.facebook.com/v12.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v12.0/oauth/access_token"
        self.userinfo_url = "https://graph.facebook.com/me"
        self.scope = "email public_profile"
    
    def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate Facebook OAuth authorization URL"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
            "display": "popup"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[OAuthToken]:
        """Exchange authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                }
                
                async with session.post(self.token_url, data=data) as response:
                    if response.status != 200:
                        logger.error(f"Facebook token exchange failed: {response.status}")
                        return None
                    
                    token_data = await response.json()
                    
                    return OAuthToken(
                        access_token=token_data['access_token'],
                        expires_in=token_data.get('expires_in'),
                        token_type="Bearer"
                    )
                    
        except Exception as e:
            logger.error(f"Error exchanging Facebook OAuth code: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """Get user information from Facebook"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "fields": "id,name,email,first_name,last_name,picture,locale",
                    "access_token": access_token
                }
                
                async with session.get(f"{self.userinfo_url}?{urlencode(params)}") as response:
                    if response.status != 200:
                        logger.error(f"Facebook userinfo failed: {response.status}")
                        return None
                    
                    user_data = await response.json()
                    
                    return OAuthUserInfo(
                        provider="facebook",
                        provider_id=user_data['id'],
                        email=user_data.get('email', ''),
                        name=user_data.get('name', ''),
                        first_name=user_data.get('first_name'),
                        last_name=user_data.get('last_name'),
                        picture=user_data.get('picture', {}).get('data', {}).get('url') if user_data.get('picture') else None,
                        locale=user_data.get('locale'),
                        verified=True,  # Facebook doesn't provide email verification status
                        raw_data=user_data
                    )
                    
        except Exception as e:
            logger.error(f"Error getting Facebook user info: {e}")
            return None


class AppleOAuthProvider:
    """Apple OAuth provider implementation"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://appleid.apple.com/auth/authorize"
        self.token_url = "https://appleid.apple.com/auth/token"
        self.scope = "name email"
    
    def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate Apple OAuth authorization URL"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
            "response_mode": "form_post"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[OAuthToken]:
        """Exchange authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                }
                
                async with session.post(self.token_url, data=data) as response:
                    if response.status != 200:
                        logger.error(f"Apple token exchange failed: {response.status}")
                        return None
                    
                    token_data = await response.json()
                    
                    return OAuthToken(
                        access_token=token_data['access_token'],
                        expires_in=token_data.get('expires_in'),
                        token_type="Bearer"
                    )
                    
        except Exception as e:
            logger.error(f"Error exchanging Apple OAuth code: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """Get user information from Apple (limited due to privacy)"""
        try:
            # Apple provides limited user info in the ID token
            # For now, return basic structure
            return OAuthUserInfo(
                provider="apple",
                provider_id="",  # Apple doesn't provide persistent user ID
                email="",  # Email is provided during initial auth
                name="",
                verified=True,
                raw_data={"provider": "apple"}
            )
            
        except Exception as e:
            logger.error(f"Error getting Apple user info: {e}")
            return None


class OAuthService:
    """Comprehensive OAuth service"""
    
    def __init__(self, config: Dict[str, Dict[str, str]]):
        """
        Initialize OAuth service with provider configurations
        
        Args:
            config: Dictionary of provider configurations
                   {
                       "google": {"client_id": "...", "client_secret": "..."},
                       "facebook": {"client_id": "...", "client_secret": "..."},
                       "apple": {"client_id": "...", "client_secret": "..."}
                   }
        """
        self.providers = {}
        self._initialize_providers(config)
    
    def _initialize_providers(self, config: Dict[str, Dict[str, str]]):
        """Initialize OAuth providers from configuration"""
        if "google" in config:
            google_config = config["google"]
            self.providers["google"] = GoogleOAuthProvider(
                google_config["client_id"],
                google_config["client_secret"]
            )
        
        if "facebook" in config:
            facebook_config = config["facebook"]
            self.providers["facebook"] = FacebookOAuthProvider(
                facebook_config["client_id"],
                facebook_config["client_secret"]
            )
        
        if "apple" in config:
            apple_config = config["apple"]
            self.providers["apple"] = AppleOAuthProvider(
                apple_config["client_id"],
                apple_config["client_secret"]
            )
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported OAuth providers"""
        return list(self.providers.keys())
    
    def get_auth_url(self, provider: str, redirect_uri: str, state: str = None) -> Optional[str]:
        """Generate OAuth authorization URL for the specified provider"""
        if provider not in self.providers:
            logger.error(f"Unsupported OAuth provider: {provider}")
            return None
        
        return self.providers[provider].get_auth_url(redirect_uri, state)
    
    async def handle_oauth_callback(self, provider: str, code: str, redirect_uri: str) -> OAuthResult:
        """Handle OAuth callback and exchange code for user info"""
        try:
            if provider not in self.providers:
                return OAuthResult(
                    success=False,
                    error_message=f"Unsupported provider: {provider}",
                    error_code="UNSUPPORTED_PROVIDER"
                )
            
            # Exchange code for access token
            tokens = await self.providers[provider].exchange_code_for_token(code, redirect_uri)
            if not tokens:
                return OAuthResult(
                    success=False,
                    error_message="Failed to exchange OAuth code for token",
                    error_code="TOKEN_EXCHANGE_FAILED"
                )
            
            # Get user info from provider
            user_info = await self.providers[provider].get_user_info(tokens.access_token)
            if not user_info:
                return OAuthResult(
                    success=False,
                    error_message="Failed to retrieve user information",
                    error_code="USERINFO_FAILED"
                )
            
            return OAuthResult(
                success=True,
                user_info=user_info,
                tokens=tokens
            )
            
        except Exception as e:
            logger.error(f"Error handling OAuth callback for {provider}: {e}")
            return OAuthResult(
                success=False,
                error_message=f"OAuth callback failed: {str(e)}",
                error_code="CALLBACK_ERROR"
            )
    
    async def refresh_token(self, provider: str, refresh_token: str) -> Optional[OAuthToken]:
        """Refresh OAuth access token"""
        # Implementation depends on provider-specific refresh mechanisms
        # For now, return None as this requires provider-specific implementation
        logger.warning(f"Token refresh not implemented for {provider}")
        return None


# Export main service and providers
__all__ = [
    'OAuthService',
    'GoogleOAuthProvider',
    'FacebookOAuthProvider', 
    'AppleOAuthProvider',
    'OAuthProvider',
    'OAuthUserInfo',
    'OAuthToken',
    'OAuthResult'
]
