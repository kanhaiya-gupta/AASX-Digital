"""
Multi-Factor Authentication Service
==================================

Handles MFA setup, verification, and management for the auth module.
"""

import secrets
import base64
import hashlib
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import pyotp
import qrcode
from io import BytesIO

logger = logging.getLogger(__name__)

class MFAService:
    """Service for handling Multi-Factor Authentication"""
    
    def __init__(self, auth_db):
        """Initialize MFA service with database connection"""
        self.auth_db = auth_db
        self.backup_code_length = 8
        self.backup_code_count = 10
    
    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret for authenticator apps"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, username: str, issuer: str = "AASX Framework") -> str:
        """Generate QR code for TOTP setup"""
        try:
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=username,
                issuer_name=issuer
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
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
    
    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {e}")
            return False
    
    def generate_backup_codes(self, user_id: str) -> List[str]:
        """Generate backup codes for MFA recovery"""
        try:
            codes = []
            for _ in range(self.backup_code_count):
                code = secrets.token_hex(self.backup_code_length // 2).upper()
                codes.append(code)
            
            # Store backup codes in database
            self.auth_db.store_backup_codes(user_id, codes)
            
            return codes
            
        except Exception as e:
            logger.error(f"Error generating backup codes: {e}")
            return []
    
    def verify_backup_code(self, user_id: str, code: str) -> bool:
        """Verify backup code"""
        try:
            return self.auth_db.verify_backup_code(user_id, code)
        except Exception as e:
            logger.error(f"Error verifying backup code: {e}")
            return False
    
    def setup_mfa(self, user_id: str, mfa_type: str, **kwargs) -> Dict[str, Any]:
        """Setup MFA for a user"""
        try:
            if mfa_type == "totp":
                return self._setup_totp(user_id)
            elif mfa_type == "sms":
                return self._setup_sms(user_id, kwargs.get('phone_number'))
            elif mfa_type == "email":
                return self._setup_email(user_id, kwargs.get('email'))
            else:
                raise ValueError(f"Unsupported MFA type: {mfa_type}")
                
        except Exception as e:
            logger.error(f"Error setting up MFA: {e}")
            return {"success": False, "error": str(e)}
    
    def _setup_totp(self, user_id: str) -> Dict[str, Any]:
        """Setup TOTP-based MFA"""
        try:
            # Generate secret
            secret = self.generate_totp_secret()
            
            # Get user info
            user = self.auth_db.get_user_by_id(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Generate QR code
            qr_code = self.generate_qr_code(secret, user.username)
            
            # Store secret in database
            self.auth_db.update_user_mfa_secret(user_id, secret)
            
            return {
                "success": True,
                "mfa_type": "totp",
                "secret": secret,
                "qr_code": qr_code,
                "backup_codes": self.generate_backup_codes(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error setting up TOTP: {e}")
            return {"success": False, "error": str(e)}
    
    def _setup_sms(self, user_id: str, phone_number: str) -> Dict[str, Any]:
        """Setup SMS-based MFA"""
        try:
            # Validate phone number
            if not phone_number:
                return {"success": False, "error": "Phone number required"}
            
            # Generate verification code
            code = secrets.token_hex(3).upper()
            
            # Store verification code
            self.auth_db.store_sms_verification_code(user_id, phone_number, code)
            
            # TODO: Send SMS with code (implement SMS service)
            
            return {
                "success": True,
                "mfa_type": "sms",
                "phone_number": phone_number,
                "message": "Verification code sent to phone"
            }
            
        except Exception as e:
            logger.error(f"Error setting up SMS MFA: {e}")
            return {"success": False, "error": str(e)}
    
    def _setup_email(self, user_id: str, email: str) -> Dict[str, Any]:
        """Setup email-based MFA"""
        try:
            # Validate email
            if not email:
                return {"success": False, "error": "Email required"}
            
            # Generate verification code
            code = secrets.token_hex(3).upper()
            
            # Store verification code
            self.auth_db.store_email_verification_code(user_id, email, code)
            
            # TODO: Send email with code (implement email service)
            
            return {
                "success": True,
                "mfa_type": "email",
                "email": email,
                "message": "Verification code sent to email"
            }
            
        except Exception as e:
            logger.error(f"Error setting up email MFA: {e}")
            return {"success": False, "error": str(e)}
    
    def verify_mfa(self, user_id: str, mfa_type: str, code: str) -> bool:
        """Verify MFA code"""
        try:
            if mfa_type == "totp":
                return self._verify_totp(user_id, code)
            elif mfa_type == "sms":
                return self._verify_sms(user_id, code)
            elif mfa_type == "email":
                return self._verify_email(user_id, code)
            elif mfa_type == "backup":
                return self.verify_backup_code(user_id, code)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error verifying MFA: {e}")
            return False
    
    def _verify_totp(self, user_id: str, code: str) -> bool:
        """Verify TOTP code"""
        try:
            # Get user's MFA secret
            secret = self.auth_db.get_user_mfa_secret(user_id)
            if not secret:
                return False
            
            return self.verify_totp_code(secret, code)
            
        except Exception as e:
            logger.error(f"Error verifying TOTP: {e}")
            return False
    
    def _verify_sms(self, user_id: str, code: str) -> bool:
        """Verify SMS code"""
        try:
            return self.auth_db.verify_sms_code(user_id, code)
        except Exception as e:
            logger.error(f"Error verifying SMS code: {e}")
            return False
    
    def _verify_email(self, user_id: str, code: str) -> bool:
        """Verify email code"""
        try:
            return self.auth_db.verify_email_code(user_id, code)
        except Exception as e:
            logger.error(f"Error verifying email code: {e}")
            return False
    
    def disable_mfa(self, user_id: str) -> bool:
        """Disable MFA for a user"""
        try:
            return self.auth_db.disable_user_mfa(user_id)
        except Exception as e:
            logger.error(f"Error disabling MFA: {e}")
            return False
    
    def get_mfa_status(self, user_id: str) -> Dict[str, Any]:
        """Get MFA status for a user"""
        try:
            return self.auth_db.get_user_mfa_status(user_id)
        except Exception as e:
            logger.error(f"Error getting MFA status: {e}")
            return {"mfa_enabled": False, "mfa_type": None} 