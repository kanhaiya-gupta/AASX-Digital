"""
Multi-Factor Authentication Service
==================================

Comprehensive MFA service for the AAS data modeling engine.
Handles TOTP, QR codes, backup codes, and complete MFA workflows.
"""

import secrets
import base64
import hashlib
import time
import logging
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from io import BytesIO

try:
    import pyotp
    import qrcode
    PYTOTP_AVAILABLE = True
    QRCODE_AVAILABLE = True
except ImportError:
    PYTOTP_AVAILABLE = False
    QRCODE_AVAILABLE = False
    logging.warning("pyotp or qrcode not available. MFA features will be limited.")

logger = logging.getLogger(__name__)


@dataclass
class MFASecret:
    """MFA secret configuration"""
    secret: str
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30
    issuer: str = "AASX Framework"
    account_name: str = ""


@dataclass
class BackupCode:
    """Backup code configuration"""
    code: str
    used: bool = False
    used_at: Optional[datetime] = None


@dataclass
class MFASetupResult:
    """MFA setup result"""
    success: bool
    secret: Optional[str] = None
    qr_code: Optional[str] = None
    backup_codes: Optional[List[str]] = None
    error_message: Optional[str] = None


class TOTPService:
    """Time-based One-Time Password service"""
    
    def __init__(self):
        if not PYTOTP_AVAILABLE:
            logger.warning("pyotp not available. TOTP functionality will be limited.")
    
    def generate_secret(self, length: int = 32) -> str:
        """Generate a new TOTP secret"""
        if PYTOTP_AVAILABLE:
            return pyotp.random_base32()
        else:
            # Fallback to basic secret generation
            return secrets.token_hex(length // 2).upper()
    
    def verify_totp(self, secret: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code"""
        if not PYTOTP_AVAILABLE:
            logger.warning("pyotp not available. TOTP verification disabled.")
            return False
        
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {e}")
            return False
    
    def get_current_totp(self, secret: str) -> Optional[str]:
        """Get current TOTP code for testing purposes"""
        if not PYTOTP_AVAILABLE:
            return None
        
        try:
            totp = pyotp.TOTP(secret)
            return totp.now()
        except Exception as e:
            logger.error(f"Error generating current TOTP: {e}")
            return None
    
    def get_totp_uri(self, secret: str, account_name: str, issuer: str = "AASX Framework") -> str:
        """Generate TOTP URI for authenticator apps"""
        if not PYTOTP_AVAILABLE:
            return ""
        
        try:
            totp = pyotp.TOTP(secret)
            return totp.provisioning_uri(name=account_name, issuer_name=issuer)
        except Exception as e:
            logger.error(f"Error generating TOTP URI: {e}")
            return ""


class QRCodeService:
    """QR code generation service for MFA setup"""
    
    def __init__(self):
        if not QRCODE_AVAILABLE:
            logger.warning("qrcode not available. QR code generation will be disabled.")
    
    def generate_qr_code(self, totp_uri: str, size: int = 10, border: int = 5) -> Optional[str]:
        """Generate QR code as base64 string"""
        if not QRCODE_AVAILABLE:
            logger.warning("qrcode not available. Cannot generate QR code.")
            return None
        
        try:
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=size, border=border)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None


class BackupCodeService:
    """Backup code management service"""
    
    def __init__(self, code_length: int = 8, code_count: int = 10):
        self.code_length = code_length
        self.code_count = code_count
    
    def generate_backup_codes(self) -> List[str]:
        """Generate new backup codes"""
        codes = []
        for _ in range(self.code_count):
            # Generate alphanumeric codes
            code = secrets.token_hex(self.code_length // 2).upper()
            codes.append(code)
        return codes
    
    def verify_backup_code(self, provided_code: str, stored_codes: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Verify backup code and return (valid, used_code)"""
        if not provided_code:
            return False, None
        
        for code_data in stored_codes:
            if code_data.get('code') == provided_code and not code_data.get('used', False):
                return True, provided_code
        
        return False, None
    
    def mark_backup_code_used(self, code: str, stored_codes: List[Dict[str, Any]]) -> bool:
        """Mark a backup code as used"""
        for code_data in stored_codes:
            if code_data.get('code') == code:
                code_data['used'] = True
                code_data['used_at'] = datetime.now(timezone.utc).isoformat()
                return True
        return False


class MFAService:
    """Comprehensive MFA service"""
    
    def __init__(self):
        self.totp_service = TOTPService()
        self.qr_service = QRCodeService()
        self.backup_service = BackupCodeService()
        
        # MFA configuration
        self.config = {
            'backup_code_length': 8,
            'backup_code_count': 10,
            'totp_window': 1,
            'default_issuer': 'AASX Framework'
        }
    
    async def setup_mfa(self, user_id: str, username: str, mfa_type: str = "totp", 
                        issuer: str = None) -> MFASetupResult:
        """Setup MFA for a user"""
        try:
            if mfa_type != "totp":
                return MFASetupResult(
                    success=False,
                    error_message=f"Unsupported MFA type: {mfa_type}"
                )
            
            # Generate TOTP secret
            secret = self.totp_service.generate_secret()
            if not secret:
                return MFASetupResult(
                    success=False,
                    error_message="Failed to generate TOTP secret"
                )
            
            # Generate QR code
            totp_uri = self.totp_service.get_totp_uri(
                secret, username, issuer or self.config['default_issuer']
            )
            qr_code = self.qr_service.generate_qr_code(totp_uri)
            
            # Generate backup codes
            backup_codes = self.backup_service.generate_backup_codes()
            
            return MFASetupResult(
                success=True,
                secret=secret,
                qr_code=qr_code,
                backup_codes=backup_codes
            )
            
        except Exception as e:
            logger.error(f"Error setting up MFA for user {user_id}: {e}")
            return MFASetupResult(
                success=False,
                error_message=f"MFA setup failed: {str(e)}"
            )
    
    async def verify_mfa(self, secret: str, code: str, backup_codes: List[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Verify MFA code (TOTP or backup)"""
        try:
            # First try TOTP
            if self.totp_service.verify_totp(secret, code, self.config['totp_window']):
                return True, "totp"
            
            # Then try backup code
            if backup_codes:
                is_valid, used_code = self.backup_service.verify_backup_code(code, backup_codes)
                if is_valid:
                    # Mark backup code as used
                    self.backup_service.mark_backup_code_used(used_code, backup_codes)
                    return True, "backup"
            
            return False, "invalid"
            
        except Exception as e:
            logger.error(f"Error verifying MFA code: {e}")
            return False, "error"
    
    async def regenerate_backup_codes(self, user_id: str) -> List[str]:
        """Regenerate backup codes for a user"""
        try:
            return self.backup_service.generate_backup_codes()
        except Exception as e:
            logger.error(f"Error regenerating backup codes for user {user_id}: {e}")
            return []
    
    async def validate_mfa_setup(self, secret: str, test_code: str) -> bool:
        """Validate MFA setup by testing with a code"""
        try:
            # Get current TOTP code
            current_code = self.totp_service.get_current_totp(secret)
            if not current_code:
                return False
            
            # Verify the test code matches current code
            return self.totp_service.verify_totp(secret, test_code)
            
        except Exception as e:
            logger.error(f"Error validating MFA setup: {e}")
            return False


# Export main service
__all__ = [
    'MFAService',
    'TOTPService', 
    'QRCodeService',
    'BackupCodeService',
    'MFASecret',
    'BackupCode',
    'MFASetupResult'
]
