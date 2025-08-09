"""
Social Login Service
===================

Handles social login integration with OAuth providers (Google, Facebook, Apple).
"""

import secrets
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import requests
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class SocialLoginService:
    """Service for handling social login with OAuth providers"""
    
    def __init__(self, auth_db):
        """Initialize social login service with database connection"""
        self.auth_db = auth_db
        self.providers = {
            "google": {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "openid email profile"
            },
            "facebook": {
                "auth_url": "https://www.facebook.com/v12.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v12.0/oauth/access_token",
                "userinfo_url": "https://graph.facebook.com/me",
                "scope": "email public_profile"
            },
            "apple": {
                "auth_url": "https://appleid.apple.com/auth/authorize",
                "token_url": "https://appleid.apple.com/auth/token",
                "userinfo_url": "https://appleid.apple.com/auth/userinfo",
                "scope": "name email"
            }
        }
    
    def get_auth_url(self, provider: str, redirect_uri: str, state: str = None) -> str:
        """Generate OAuth authorization URL for the specified provider"""
        try:
            if provider not in self.providers:
                raise ValueError(f"Unsupported provider: {provider}")
            
            provider_config = self.providers[provider]
            
            # Generate state if not provided
            if not state:
                state = secrets.token_urlsafe(32)
            
            # Build authorization URL
            params = {
                "client_id": self._get_client_id(provider),
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": provider_config["scope"],
                "state": state
            }
            
            # Add provider-specific parameters
            if provider == "google":
                params["access_type"] = "offline"
                params["prompt"] = "consent"
            elif provider == "facebook":
                params["display"] = "popup"
            elif provider == "apple":
                params["response_mode"] = "form_post"
            
            auth_url = f"{provider_config['auth_url']}?{urlencode(params)}"
            
            logger.info(f"Generated {provider} auth URL")
            return auth_url
            
        except Exception as e:
            logger.error(f"Error generating auth URL for {provider}: {e}")
            raise
    
    async def handle_callback(self, provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for user info"""
        try:
            if provider not in self.providers:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Exchange code for access token
            access_token = await self._exchange_code_for_token(provider, code, redirect_uri)
            
            # Get user info from provider
            user_info = await self._get_user_info(provider, access_token)
            
            # Process user info and create/update user
            user = await self._process_user_info(provider, user_info, access_token)
            
            return {
                "success": True,
                "user": user,
                "access_token": access_token,
                "provider": provider
            }
            
        except Exception as e:
            logger.error(f"Error handling {provider} callback: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _exchange_code_for_token(self, provider: str, code: str, redirect_uri: str) -> str:
        """Exchange authorization code for access token"""
        try:
            provider_config = self.providers[provider]
            
            # Prepare token request
            token_data = {
                "client_id": self._get_client_id(provider),
                "client_secret": self._get_client_secret(provider),
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
            
            # Make token request
            response = requests.post(provider_config["token_url"], data=token_data)
            response.raise_for_status()
            
            token_response = response.json()
            access_token = token_response.get("access_token")
            
            if not access_token:
                raise ValueError("No access token received")
            
            return access_token
            
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise
    
    async def _get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Get user information from the OAuth provider"""
        try:
            provider_config = self.providers[provider]
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            if provider == "facebook":
                # Facebook requires fields parameter
                response = requests.get(
                    f"{provider_config['userinfo_url']}?fields=id,name,email,picture",
                    headers=headers
                )
            else:
                response = requests.get(provider_config["userinfo_url"], headers=headers)
            
            response.raise_for_status()
            user_info = response.json()
            
            # Normalize user info
            normalized_info = self._normalize_user_info(provider, user_info)
            
            return normalized_info
            
        except Exception as e:
            logger.error(f"Error getting user info from {provider}: {e}")
            raise
    
    def _normalize_user_info(self, provider: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize user info from different providers"""
        normalized = {
            "provider": provider,
            "provider_user_id": user_info.get("id") or user_info.get("sub"),
            "email": user_info.get("email"),
            "display_name": user_info.get("name") or user_info.get("display_name"),
            "avatar_url": None
        }
        
        # Extract avatar URL based on provider
        if provider == "google":
            normalized["avatar_url"] = user_info.get("picture")
        elif provider == "facebook":
            picture = user_info.get("picture", {})
            if isinstance(picture, dict):
                normalized["avatar_url"] = picture.get("data", {}).get("url")
        elif provider == "apple":
            # Apple doesn't provide avatar by default
            pass
        
        return normalized
    
    async def _process_user_info(self, provider: str, user_info: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Process user info and create/update user in database"""
        try:
            # Check if user already exists with this social account
            existing_user = self.auth_db.get_user_by_social_account(provider, user_info["provider_user_id"])
            
            if existing_user:
                # Update existing user's social account info
                self.auth_db.update_social_account(existing_user["user_id"], provider, user_info, access_token)
                return existing_user
            
            # Check if user exists with same email
            if user_info["email"]:
                existing_user = self.auth_db.get_user_by_email(user_info["email"])
                if existing_user:
                    # Link social account to existing user
                    self.auth_db.link_social_account(existing_user["user_id"], provider, user_info, access_token)
                    return existing_user
            
            # Create new user
            new_user_data = {
                "username": f"{provider}_{user_info['provider_user_id']}",
                "email": user_info["email"],
                "full_name": user_info["display_name"],
                "role": "user",
                "is_active": True
            }
            
            new_user = self.auth_db.create_user(new_user_data)
            
            if new_user:
                # Link social account to new user
                self.auth_db.link_social_account(new_user["user_id"], provider, user_info, access_token)
                return new_user
            
            raise ValueError("Failed to create user")
            
        except Exception as e:
            logger.error(f"Error processing user info: {e}")
            raise
    
    def _get_client_id(self, provider: str) -> str:
        """Get OAuth client ID for the provider"""
        # This should be configured in environment variables or settings
        client_ids = {
            "google": "your-google-client-id",
            "facebook": "your-facebook-client-id",
            "apple": "your-apple-client-id"
        }
        return client_ids.get(provider, "")
    
    def _get_client_secret(self, provider: str) -> str:
        """Get OAuth client secret for the provider"""
        # This should be configured in environment variables or settings
        client_secrets = {
            "google": "your-google-client-secret",
            "facebook": "your-facebook-client-secret",
            "apple": "your-apple-client-secret"
        }
        return client_secrets.get(provider, "")
    
    def get_social_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all social accounts linked to a user"""
        try:
            return self.auth_db.get_user_social_accounts(user_id)
        except Exception as e:
            logger.error(f"Error getting social accounts: {e}")
            return []
    
    def unlink_social_account(self, user_id: str, provider: str) -> bool:
        """Unlink a social account from a user"""
        try:
            return self.auth_db.unlink_social_account(user_id, provider)
        except Exception as e:
            logger.error(f"Error unlinking social account: {e}")
            return False 