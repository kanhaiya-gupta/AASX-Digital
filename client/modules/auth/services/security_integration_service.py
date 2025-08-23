"""
Security Integration Service - Soft Connection to Backend
========================================================

Thin integration layer that connects webapp to backend security services.
Handles frontend-specific logic while delegating security operations to backend.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Import from backend engine security module
from src.engine.security.mfa_service import MFAService, MFASetupResult
from src.engine.security.oauth_service import OAuthService, OAuthResult
from src.engine.security.authentication import MultiFactorAuthenticator
from src.engine.security.security_utils import SecurityUtils, PasswordManager

logger = logging.getLogger(__name__)


class SecurityIntegrationService:
    """Integration service for security operations"""
    
    def __init__(self, oauth_config: Dict[str, Dict[str, str]] = None):
        """
        Initialize with backend security services
        
        Args:
            oauth_config: OAuth provider configurations
        """
        try:
            # Initialize backend security services
            self.mfa_service = MFAService()
            self.oauth_service = OAuthService(oauth_config or {})
            self.security_utils = SecurityUtils()
            self.password_manager = PasswordManager()
            
            logger.info("✅ Security integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize security integration service: {e}")
            raise
    
    # MFA Integration Methods
    async def setup_mfa(self, user_id: str, username: str, mfa_type: str = "totp", 
                        issuer: str = None) -> MFASetupResult:
        """Setup MFA for user via backend"""
        try:
            return await self.mfa_service.setup_mfa(user_id, username, mfa_type, issuer)
        except Exception as e:
            logger.error(f"Error setting up MFA for user {user_id}: {e}")
            return MFASetupResult(
                success=False,
                error_message=f"MFA setup failed: {str(e)}"
            )
    
    async def verify_mfa(self, secret: str, code: str, backup_codes: List[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Verify MFA code via backend"""
        try:
            return await self.mfa_service.verify_mfa(secret, code, backup_codes)
        except Exception as e:
            logger.error(f"Error verifying MFA code: {e}")
            return False, "error"
    
    async def regenerate_backup_codes(self, user_id: str) -> List[str]:
        """Regenerate backup codes via backend"""
        try:
            return await self.mfa_service.regenerate_backup_codes(user_id)
        except Exception as e:
            logger.error(f"Error regenerating backup codes for user {user_id}: {e}")
            return []
    
    async def validate_mfa_setup(self, secret: str, test_code: str) -> bool:
        """Validate MFA setup via backend"""
        try:
            return await self.mfa_service.validate_mfa_setup(secret, test_code)
        except Exception as e:
            logger.error(f"Error validating MFA setup: {e}")
            return False
    
    # OAuth Integration Methods
    def get_supported_oauth_providers(self) -> List[str]:
        """Get supported OAuth providers from backend"""
        try:
            return self.oauth_service.get_supported_providers()
        except Exception as e:
            logger.error(f"Error getting OAuth providers: {e}")
            return []
    
    def get_oauth_auth_url(self, provider: str, redirect_uri: str, state: str = None) -> Optional[str]:
        """Get OAuth authorization URL from backend"""
        try:
            return self.oauth_service.get_auth_url(provider, redirect_uri, state)
        except Exception as e:
            logger.error(f"Error getting OAuth auth URL for {provider}: {e}")
            return None
    
    async def handle_oauth_callback(self, provider: str, code: str, redirect_uri: str) -> OAuthResult:
        """Handle OAuth callback via backend"""
        try:
            return await self.oauth_service.handle_oauth_callback(provider, code, redirect_uri)
        except Exception as e:
            logger.error(f"Error handling OAuth callback for {provider}: {e}")
            return OAuthResult(
                success=False,
                error_message=f"OAuth callback failed: {str(e)}",
                error_code="INTEGRATION_ERROR"
            )
    
    # Password Security Methods - Using Backend Services
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength via backend SecurityUtils"""
        try:
            return self.security_utils.validate_password_strength(password)
        except Exception as e:
            logger.error(f"Error validating password strength: {e}")
            return {
                "valid": False,
                "score": 0,
                "feedback": ["Password validation failed"]
            }
    
    def is_password_acceptable(self, password: str) -> bool:
        """Check if password meets policy requirements via backend PasswordManager"""
        try:
            return self.password_manager.is_password_acceptable(password)
        except Exception as e:
            logger.error(f"Error checking password acceptability: {e}")
            return False
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate secure password via backend SecurityUtils"""
        try:
            return self.security_utils.generate_secure_password(length)
        except Exception as e:
            logger.error(f"Error generating secure password: {e}")
            return ""
    
    # Security Utility Methods
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate secure token via backend"""
        try:
            return self.security_utils.generate_secure_token(length)
        except Exception as e:
            logger.error(f"Error generating secure token: {e}")
            # Fallback to basic token generation
            import secrets
            return secrets.token_urlsafe(length)
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input via backend"""
        try:
            return self.security_utils.sanitize_input(input_data)
        except Exception as e:
            logger.error(f"Error sanitizing input: {e}")
            # Fallback to basic sanitization
            import html
            return html.escape(input_data)


# Export the integration service
__all__ = ['SecurityIntegrationService']
