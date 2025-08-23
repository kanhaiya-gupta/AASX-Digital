"""
Profile Verification Integration Service - Soft Connection to Backend
==================================================================

Thin integration layer that connects webapp to backend profile verification services.
Handles frontend-specific logic while delegating verification operations to backend.
"""

import logging
import secrets
import string
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Import from backend engine
from src.engine.services.auth.user_service import UserService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class ProfileVerificationService:
    """Integration service for profile verification operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._auth_repo = None
        self._user_service = None
        
        logger.info("✅ Profile verification integration service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            
            self._initialized = True
            logger.info("✅ Profile verification integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize profile verification integration service: {e}")
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
    
    async def create_verification_request(self, user_id: str, verification_type: str, 
                                        verification_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a verification request via backend"""
        await self._ensure_initialized()
        try:
            # Validate verification type
            if verification_type not in ['email', 'phone', 'identity', 'address']:
                raise ValueError(f"Unsupported verification type: {verification_type}")
            
            # Generate verification code
            verification_code = self._generate_verification_code(verification_type)
            
            # Create verification record
            verification_record = {
                "verification_id": self._generate_verification_id(),
                "user_id": user_id,
                "verification_type": verification_type,
                "verification_data": verification_data,
                "verification_code": verification_code,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "attempts": 0,
                "max_attempts": 3
            }
            
            # Store verification record (in production, this would go to a database)
            # For now, we'll simulate storage
            success = await self._store_verification_record(verification_record)
            
            if success:
                # Send verification code (in production, this would send email/SMS)
                await self._send_verification_code(verification_type, verification_data, verification_code)
                
                return {
                    "verification_id": verification_record["verification_id"],
                    "verification_type": verification_type,
                    "status": "pending",
                    "expires_at": verification_record["expires_at"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating verification request for user {user_id}: {e}")
            return None
    
    async def verify_verification_code(self, user_id: str, verification_type: str, 
                                     verification_code: str) -> bool:
        """Verify a verification code via backend"""
        await self._ensure_initialized()
        try:
            # Get verification record
            verification_record = await self._get_verification_record(user_id, verification_type)
            if not verification_record:
                logger.warning(f"No verification record found for user {user_id}, type {verification_type}")
                return False
            
            # Check if verification has expired
            if self._is_verification_expired(verification_record):
                logger.warning(f"Verification expired for user {user_id}, type {verification_type}")
                return False
            
            # Check if max attempts exceeded
            if verification_record["attempts"] >= verification_record["max_attempts"]:
                logger.warning(f"Max verification attempts exceeded for user {user_id}, type {verification_type}")
                return False
            
            # Increment attempts
            verification_record["attempts"] += 1
            
            # Check if code matches
            if verification_record["verification_code"] == verification_code:
                # Mark as verified
                verification_record["status"] = "verified"
                verification_record["verified_at"] = datetime.utcnow().isoformat()
                
                # Update verification record
                await self._update_verification_record(verification_record)
                
                # Update user verification status
                await self._update_user_verification_status(user_id, verification_type, True)
                
                logger.info(f"Verification successful for user {user_id}, type {verification_type}")
                return True
            else:
                # Update verification record with failed attempt
                await self._update_verification_record(verification_record)
                
                logger.warning(f"Invalid verification code for user {user_id}, type {verification_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying verification code for user {user_id}: {e}")
            return False
    
    async def get_verification_status(self, user_id: str) -> Dict[str, Any]:
        """Get verification status for a user via backend"""
        await self._ensure_initialized()
        try:
            # Get all verification records for user
            verification_records = await self._get_user_verification_records(user_id)
            
            # Build status summary
            status_summary = {
                "user_id": user_id,
                "verifications": {},
                "overall_status": "unverified"
            }
            
            verification_types = ['email', 'phone', 'identity', 'address']
            verified_count = 0
            
            for vtype in verification_types:
                record = next((r for r in verification_records if r["verification_type"] == vtype), None)
                
                if record:
                    status_summary["verifications"][vtype] = {
                        "status": record["status"],
                        "verified_at": record.get("verified_at"),
                        "created_at": record["created_at"],
                        "expires_at": record["expires_at"]
                    }
                    
                    if record["status"] == "verified":
                        verified_count += 1
                else:
                    status_summary["verifications"][vtype] = {
                        "status": "not_requested",
                        "verified_at": None,
                        "created_at": None,
                        "expires_at": None
                    }
            
            # Determine overall status
            if verified_count == len(verification_types):
                status_summary["overall_status"] = "fully_verified"
            elif verified_count > 0:
                status_summary["overall_status"] = "partially_verified"
            
            return status_summary
            
        except Exception as e:
            logger.error(f"Error getting verification status for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "verifications": {},
                "overall_status": "unknown"
            }
    
    async def resend_verification_code(self, user_id: str, verification_type: str) -> bool:
        """Resend verification code via backend"""
        await self._ensure_initialized()
        try:
            # Get existing verification record
            verification_record = await self._get_verification_record(user_id, verification_type)
            if not verification_record:
                logger.warning(f"No verification record found for user {user_id}, type {verification_type}")
                return False
            
            # Check if verification is still pending
            if verification_record["status"] != "pending":
                logger.warning(f"Verification not pending for user {user_id}, type {verification_type}")
                return False
            
            # Generate new verification code
            new_verification_code = self._generate_verification_code(verification_type)
            
            # Update verification record
            verification_record["verification_code"] = new_verification_code
            verification_record["created_at"] = datetime.utcnow().isoformat()
            verification_record["expires_at"] = (datetime.utcnow() + timedelta(hours=24)).isoformat()
            verification_record["attempts"] = 0
            
            # Update record
            success = await self._update_verification_record(verification_record)
            
            if success:
                # Send new verification code
                await self._send_verification_code(
                    verification_type, 
                    verification_record["verification_data"], 
                    new_verification_code
                )
                
                logger.info(f"Verification code resent for user {user_id}, type {verification_type}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resending verification code for user {user_id}: {e}")
            return False
    
    async def cancel_verification(self, user_id: str, verification_type: str) -> bool:
        """Cancel a verification request via backend"""
        await self._ensure_initialized()
        try:
            # Get verification record
            verification_record = await self._get_verification_record(user_id, verification_type)
            if not verification_record:
                return True  # Nothing to cancel
            
            # Mark as cancelled
            verification_record["status"] = "cancelled"
            verification_record["cancelled_at"] = datetime.utcnow().isoformat()
            
            # Update record
            success = await self._update_verification_record(verification_record)
            
            if success:
                logger.info(f"Verification cancelled for user {user_id}, type {verification_type}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling verification for user {user_id}: {e}")
            return False
    
    def _generate_verification_code(self, verification_type: str) -> str:
        """Generate verification code based on type"""
        if verification_type == 'email':
            # 6-digit numeric code for email
            return ''.join(secrets.choice(string.digits) for _ in range(6))
        elif verification_type == 'phone':
            # 6-digit numeric code for phone
            return ''.join(secrets.choice(string.digits) for _ in range(6))
        elif verification_type == 'identity':
            # 8-character alphanumeric code for identity
            return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        elif verification_type == 'address':
            # 6-character alphanumeric code for address
            return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        else:
            # Default 6-digit numeric code
            return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    def _generate_verification_id(self) -> str:
        """Generate unique verification ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def _store_verification_record(self, verification_record: Dict[str, Any]) -> bool:
        """Store verification record (simulated)"""
        await self._ensure_initialized()
        try:
            # In production, this would store to a database
            # For now, we'll simulate successful storage
            logger.info(f"Storing verification record: {verification_record['verification_id']}")
            return True
        except Exception as e:
            logger.error(f"Error storing verification record: {e}")
            return False
    
    async def _get_verification_record(self, user_id: str, verification_type: str) -> Optional[Dict[str, Any]]:
        """Get verification record (simulated)"""
        await self._ensure_initialized()
        try:
            # In production, this would retrieve from a database
            # For now, we'll simulate retrieval
            logger.info(f"Getting verification record for user {user_id}, type {verification_type}")
            
            # Return a mock record for testing
            return {
                "verification_id": "mock_id",
                "user_id": user_id,
                "verification_type": verification_type,
                "verification_code": "123456",
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "attempts": 0,
                "max_attempts": 3
            }
        except Exception as e:
            logger.error(f"Error getting verification record: {e}")
            return None
    
    async def _get_user_verification_records(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all verification records for a user (simulated)"""
        await self._ensure_initialized()
        try:
            # In production, this would retrieve from a database
            # For now, we'll simulate retrieval
            logger.info(f"Getting verification records for user {user_id}")
            return []
        except Exception as e:
            logger.error(f"Error getting user verification records: {e}")
            return []
    
    async def _update_verification_record(self, verification_record: Dict[str, Any]) -> bool:
        """Update verification record (simulated)"""
        await self._ensure_initialized()
        try:
            # In production, this would update a database
            # For now, we'll simulate successful update
            logger.info(f"Updating verification record: {verification_record['verification_id']}")
            return True
        except Exception as e:
            logger.error(f"Error updating verification record: {e}")
            return False
    
    async def _update_user_verification_status(self, user_id: str, verification_type: str, verified: bool) -> bool:
        """Update user verification status via backend"""
        await self._ensure_initialized()
        try:
            # Update user model with verification status
            update_data = {}
            
            if verification_type == 'email':
                update_data['email_verified'] = verified
            elif verification_type == 'phone':
                update_data['phone_verified'] = verified
            elif verification_type == 'identity':
                update_data['identity_verified'] = verified
            elif verification_type == 'address':
                update_data['address_verified'] = verified
            
            if update_data:
                success = await self.user_service.update_user(user_id, update_data)
                return success
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user verification status: {e}")
            return False
    
    async def _send_verification_code(self, verification_type: str, verification_data: Dict[str, Any], 
                                    verification_code: str) -> bool:
        """Send verification code (simulated)"""
        await self._ensure_initialized()
        try:
            # In production, this would send email/SMS
            if verification_type == 'email':
                email = verification_data.get('email')
                logger.info(f"Sending verification code {verification_code} to email: {email}")
            elif verification_type == 'phone':
                phone = verification_data.get('phone')
                logger.info(f"Sending verification code {verification_code} to phone: {phone}")
            else:
                logger.info(f"Sending verification code {verification_code} for {verification_type}")
            
            return True
        except Exception as e:
            logger.error(f"Error sending verification code: {e}")
            return False
    
    def _is_verification_expired(self, verification_record: Dict[str, Any]) -> bool:
        """Check if verification has expired"""
        try:
            expires_at = datetime.fromisoformat(verification_record["expires_at"])
            return datetime.utcnow() > expires_at
        except Exception as e:
            logger.error(f"Error checking verification expiration: {e}")
            return True


# Export the integration service
__all__ = ['ProfileVerificationService']
