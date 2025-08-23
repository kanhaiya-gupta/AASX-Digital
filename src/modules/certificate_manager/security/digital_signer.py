"""
Digital Signer for Certificate Manager

Handles digital signature generation and verification for certificates.
Provides cryptographic signing capabilities with multiple algorithms.
"""

import asyncio
import hashlib
import hmac
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class SignatureAlgorithm(Enum):
    """Supported signature algorithms"""
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"
    ECDSA_P256 = "ECDSA-P256"
    ECDSA_P384 = "ECDSA-P384"
    ECDSA_P521 = "ECDSA-P521"
    ED25519 = "ED25519"
    HMAC_SHA256 = "HMAC-SHA256"
    HMAC_SHA512 = "HMAC-SHA512"


class SignatureStatus(Enum):
    """Digital signature status"""
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNTRUSTED = "untrusted"
    UNKNOWN = "unknown"


class DigitalSigner:
    """
    Digital signature service for certificates
    
    Handles:
    - Digital signature generation
    - Signature verification
    - Certificate chain validation
    - Timestamp signing
    - Signature metadata management
    """
    
    def __init__(self):
        """Initialize the digital signer"""
        self.signature_algorithms = list(SignatureAlgorithm)
        self.active_signatures: Dict[str, Dict[str, Any]] = {}
        self.signature_history: List[Dict[str, Any]] = []
        self.signature_locks: Dict[str, asyncio.Lock] = {}
        
        # Initialize supported algorithms
        self._initialize_algorithms()
        
        logger.info("Digital Signer initialized successfully")
    
    def _initialize_algorithms(self) -> None:
        """Initialize supported signature algorithms"""
        self.algorithm_implementations = {
            SignatureAlgorithm.RSA_2048: self._rsa_sign,
            SignatureAlgorithm.RSA_4096: self._rsa_sign,
            SignatureAlgorithm.ECDSA_P256: self._ecdsa_sign,
            SignatureAlgorithm.ECDSA_P384: self._ecdsa_sign,
            SignatureAlgorithm.ECDSA_P521: self._ecdsa_sign,
            SignatureAlgorithm.ED25519: self._ed25519_sign,
            SignatureAlgorithm.HMAC_SHA256: self._hmac_sign,
            SignatureAlgorithm.HMAC_SHA512: self._hmac_sign
        }
        
        self.algorithm_verifiers = {
            SignatureAlgorithm.RSA_2048: self._rsa_verify,
            SignatureAlgorithm.RSA_4096: self._rsa_verify,
            SignatureAlgorithm.ECDSA_P256: self._ecdsa_verify,
            SignatureAlgorithm.ECDSA_P384: self._ecdsa_verify,
            SignatureAlgorithm.ECDSA_P521: self._ecdsa_verify,
            SignatureAlgorithm.ED25519: self._ed25519_verify,
            SignatureAlgorithm.HMAC_SHA256: self._hmac_verify,
            SignatureAlgorithm.HMAC_SHA512: self._hmac_verify
        }
    
    async def sign_certificate(
        self,
        certificate_data: Dict[str, Any],
        algorithm: SignatureAlgorithm = SignatureAlgorithm.RSA_2048,
        private_key: Optional[str] = None,
        passphrase: Optional[str] = None,
        include_timestamp: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sign a certificate with digital signature
        
        Args:
            certificate_data: Certificate data to sign
            algorithm: Signature algorithm to use
            private_key: Private key for signing
            passphrase: Passphrase for private key
            include_timestamp: Whether to include timestamp
            metadata: Additional metadata for signature
            
        Returns:
            Dictionary containing signature and metadata
        """
        certificate_id = certificate_data.get("certificate_id", "unknown")
        
        # Acquire signature lock
        async with await self._acquire_signature_lock(certificate_id):
            try:
                # Validate algorithm support
                if algorithm not in self.signature_algorithms:
                    raise ValueError(f"Unsupported signature algorithm: {algorithm}")
                
                # Prepare data for signing
                data_to_sign = await self._prepare_data_for_signing(
                    certificate_data, include_timestamp
                )
                
                # Generate signature
                signature_result = await self._generate_signature(
                    data_to_sign, algorithm, private_key, passphrase
                )
                
                # Create signature metadata
                signature_metadata = await self._create_signature_metadata(
                    certificate_data, algorithm, signature_result, metadata
                )
                
                # Store signature
                signature_id = f"sig_{certificate_id}_{asyncio.get_event_loop().time()}"
                signature_data = {
                    "signature_id": signature_id,
                    "certificate_id": certificate_id,
                    "algorithm": algorithm.value,
                    "signature": signature_result["signature"],
                    "public_key": signature_result.get("public_key"),
                    "timestamp": signature_result.get("timestamp"),
                    "metadata": signature_metadata,
                    "status": SignatureStatus.VALID.value,
                    "created_at": asyncio.get_event_loop().time()
                }
                
                # Store active signature
                self.active_signatures[signature_id] = signature_data
                
                # Record in history
                self.signature_history.append({
                    "timestamp": asyncio.get_event_loop().time(),
                    "action": "sign",
                    "certificate_id": certificate_id,
                    "algorithm": algorithm.value,
                    "signature_id": signature_id
                })
                
                logger.info(f"Certificate {certificate_id} signed with {algorithm.value}")
                
                return signature_data
                
            except Exception as e:
                error_msg = f"Digital signing failed: {str(e)}"
                logger.error(f"Failed to sign certificate {certificate_id}: {error_msg}")
                raise
    
    async def verify_signature(
        self,
        certificate_data: Dict[str, Any],
        signature: str,
        algorithm: SignatureAlgorithm,
        public_key: Optional[str] = None,
        verification_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Verify a digital signature
        
        Args:
            certificate_data: Certificate data to verify
            signature: Digital signature to verify
            algorithm: Signature algorithm used
            public_key: Public key for verification
            verification_level: Level of verification to perform
            
        Returns:
            Dictionary containing verification result
        """
        certificate_id = certificate_data.get("certificate_id", "unknown")
        
        try:
            # Validate algorithm support
            if algorithm not in self.signature_algorithms:
                raise ValueError(f"Unsupported signature algorithm: {algorithm}")
            
            # Prepare data for verification
            data_to_verify = await self._prepare_data_for_verification(certificate_data)
            
            # Perform signature verification
            verification_result = await self._verify_signature(
                data_to_verify, signature, algorithm, public_key
            )
            
            # Perform additional verification based on level
            if verification_level == "comprehensive":
                verification_result.update(
                    await self._perform_comprehensive_verification(
                        certificate_data, signature, algorithm
                    )
                )
            
            # Determine overall verification status
            verification_status = self._determine_verification_status(verification_result)
            verification_result["status"] = verification_status.value
            
            # Record verification
            self.signature_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "verify",
                "certificate_id": certificate_id,
                "algorithm": algorithm.value,
                "verification_status": verification_status.value,
                "verification_result": verification_result
            })
            
            logger.info(f"Signature verification for {certificate_id}: {verification_status.value}")
            
            return verification_result
            
        except Exception as e:
            error_msg = f"Signature verification failed: {str(e)}"
            logger.error(f"Failed to verify signature for {certificate_id}: {error_msg}")
            raise
    
    async def get_signature_status(self, signature_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a digital signature"""
        return self.active_signatures.get(signature_id)
    
    async def revoke_signature(self, signature_id: str, reason: str = "Unknown") -> bool:
        """Revoke a digital signature"""
        if signature_id in self.active_signatures:
            signature = self.active_signatures[signature_id]
            signature["status"] = SignatureStatus.REVOKED.value
            signature["revoked_at"] = asyncio.get_event_loop().time()
            signature["revocation_reason"] = reason
            
            # Record revocation
            self.signature_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "revoke",
                "signature_id": signature_id,
                "reason": reason
            })
            
            logger.info(f"Signature {signature_id} revoked: {reason}")
            return True
        
        return False
    
    async def get_signature_history(
        self,
        certificate_id: Optional[str] = None,
        algorithm: Optional[SignatureAlgorithm] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get signature history with optional filtering"""
        history = self.signature_history.copy()
        
        # Filter by certificate ID
        if certificate_id:
            history = [h for h in history if h.get("certificate_id") == certificate_id]
        
        # Filter by algorithm
        if algorithm:
            history = [h for h in history if h.get("algorithm") == algorithm.value]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def _acquire_signature_lock(self, certificate_id: str) -> asyncio.Lock:
        """Acquire a lock for signature operations"""
        if certificate_id not in self.signature_locks:
            self.signature_locks[certificate_id] = asyncio.Lock()
        return self.signature_locks[certificate_id]
    
    async def _prepare_data_for_signing(
        self,
        certificate_data: Dict[str, Any],
        include_timestamp: bool
    ) -> str:
        """Prepare certificate data for signing"""
        # Create a copy to avoid modifying original data
        data_to_sign = certificate_data.copy()
        
        # Add timestamp if requested
        if include_timestamp:
            data_to_sign["signature_timestamp"] = datetime.utcnow().isoformat()
        
        # Remove existing signature fields
        data_to_sign.pop("digital_signature", None)
        data_to_sign.pop("signature_timestamp", None)
        data_to_sign.pop("signature_algorithm", None)
        
        # Convert to canonical JSON string
        return json.dumps(data_to_sign, sort_keys=True, separators=(',', ':'))
    
    async def _prepare_data_for_verification(self, certificate_data: Dict[str, Any]) -> str:
        """Prepare certificate data for verification"""
        # Create a copy to avoid modifying original data
        data_to_verify = certificate_data.copy()
        
        # Remove signature fields for verification
        data_to_verify.pop("digital_signature", None)
        data_to_verify.pop("signature_timestamp", None)
        data_to_verify.pop("signature_algorithm", None)
        
        # Convert to canonical JSON string
        return json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
    
    async def _generate_signature(
        self,
        data: str,
        algorithm: SignatureAlgorithm,
        private_key: Optional[str],
        passphrase: Optional[str]
    ) -> Dict[str, Any]:
        """Generate digital signature using specified algorithm"""
        if algorithm in self.algorithm_implementations:
            signer = self.algorithm_implementations[algorithm]
            return await signer(data, private_key, passphrase)
        else:
            raise ValueError(f"No implementation for algorithm: {algorithm}")
    
    async def _verify_signature(
        self,
        data: str,
        signature: str,
        algorithm: SignatureAlgorithm,
        public_key: Optional[str]
    ) -> Dict[str, Any]:
        """Verify digital signature using specified algorithm"""
        if algorithm in self.algorithm_verifiers:
            verifier = self.algorithm_verifiers[algorithm]
            return await verifier(data, signature, public_key)
        else:
            raise ValueError(f"No verifier for algorithm: {algorithm}")
    
    async def _rsa_sign(
        self,
        data: str,
        private_key: Optional[str],
        passphrase: Optional[str]
    ) -> Dict[str, Any]:
        """Generate RSA signature (simulated)"""
        # In a real implementation, this would use actual RSA cryptography
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        signature = f"RSA_SIGNATURE_{data_hash[:16]}"
        
        return {
            "signature": signature,
            "public_key": "RSA_PUBLIC_KEY_SIMULATED",
            "timestamp": datetime.utcnow().isoformat(),
            "algorithm": "RSA"
        }
    
    async def _rsa_verify(
        self,
        data: str,
        signature: str,
        public_key: Optional[str]
    ) -> Dict[str, Any]:
        """Verify RSA signature (simulated)"""
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        expected_signature = f"RSA_SIGNATURE_{data_hash[:16]}"
        
        is_valid = signature == expected_signature
        
        return {
            "is_valid": is_valid,
            "algorithm": "RSA",
            "verification_method": "hash_comparison",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _ecdsa_sign(
        self,
        data: str,
        private_key: Optional[str],
        passphrase: Optional[str]
    ) -> Dict[str, Any]:
        """Generate ECDSA signature (simulated)"""
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        signature = f"ECDSA_SIGNATURE_{data_hash[:16]}"
        
        return {
            "signature": signature,
            "public_key": "ECDSA_PUBLIC_KEY_SIMULATED",
            "timestamp": datetime.utcnow().isoformat(),
            "algorithm": "ECDSA"
        }
    
    async def _ecdsa_verify(
        self,
        data: str,
        signature: str,
        public_key: Optional[str]
    ) -> Dict[str, Any]:
        """Verify ECDSA signature (simulated)"""
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        expected_signature = f"ECDSA_SIGNATURE_{data_hash[:16]}"
        
        is_valid = signature == expected_signature
        
        return {
            "is_valid": is_valid,
            "algorithm": "ECDSA",
            "verification_method": "hash_comparison",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _ed25519_sign(
        self,
        data: str,
        private_key: Optional[str],
        passphrase: Optional[str]
    ) -> Dict[str, Any]:
        """Generate Ed25519 signature (simulated)"""
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        signature = f"ED25519_SIGNATURE_{data_hash[:16]}"
        
        return {
            "signature": signature,
            "public_key": "ED25519_PUBLIC_KEY_SIMULATED",
            "timestamp": datetime.utcnow().isoformat(),
            "algorithm": "Ed25519"
        }
    
    async def _ed25519_verify(
        self,
        data: str,
        signature: str,
        public_key: Optional[str]
    ) -> Dict[str, Any]:
        """Verify Ed25519 signature (simulated)"""
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        expected_signature = f"ED25519_SIGNATURE_{data_hash[:16]}"
        
        is_valid = signature == expected_signature
        
        return {
            "is_valid": is_valid,
            "algorithm": "Ed25519",
            "verification_method": "hash_comparison",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _hmac_sign(
        self,
        data: str,
        private_key: Optional[str],
        passphrase: Optional[str]
    ) -> Dict[str, Any]:
        """Generate HMAC signature (simulated)"""
        key = private_key or "default_hmac_key"
        data_hash = hmac.new(
            key.encode(), data.encode(), hashlib.sha256
        ).hexdigest()
        signature = f"HMAC_SIGNATURE_{data_hash[:16]}"
        
        return {
            "signature": signature,
            "public_key": "HMAC_KEY_SIMULATED",
            "timestamp": datetime.utcnow().isoformat(),
            "algorithm": "HMAC"
        }
    
    async def _hmac_verify(
        self,
        data: str,
        signature: str,
        public_key: Optional[str]
    ) -> Dict[str, Any]:
        """Verify HMAC signature (simulated)"""
        key = public_key or "default_hmac_key"
        data_hash = hmac.new(
            key.encode(), data.encode(), hashlib.sha256
        ).hexdigest()
        expected_signature = f"HMAC_SIGNATURE_{data_hash[:16]}"
        
        is_valid = signature == expected_signature
        
        return {
            "is_valid": is_valid,
            "algorithm": "HMAC",
            "verification_method": "hash_comparison",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _create_signature_metadata(
        self,
        certificate_data: Dict[str, Any],
        algorithm: SignatureAlgorithm,
        signature_result: Dict[str, Any],
        additional_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create comprehensive signature metadata"""
        metadata = {
            "certificate_name": certificate_data.get("certificate_name"),
            "certificate_status": certificate_data.get("status"),
            "algorithm_used": algorithm.value,
            "signature_timestamp": signature_result.get("timestamp"),
            "key_fingerprint": await self._generate_key_fingerprint(signature_result.get("public_key")),
            "signature_version": "1.0"
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return metadata
    
    async def _generate_key_fingerprint(self, public_key: Optional[str]) -> str:
        """Generate key fingerprint for public key"""
        if public_key:
            return hashlib.sha256(public_key.encode()).hexdigest()[:16]
        return "unknown"
    
    async def _perform_comprehensive_verification(
        self,
        certificate_data: Dict[str, Any],
        signature: str,
        algorithm: SignatureAlgorithm
    ) -> Dict[str, Any]:
        """Perform comprehensive signature verification"""
        verification_details = {
            "certificate_integrity": await self._verify_certificate_integrity(certificate_data),
            "signature_freshness": await self._verify_signature_freshness(certificate_data),
            "algorithm_strength": await self._verify_algorithm_strength(algorithm),
            "key_validity": await self._verify_key_validity(certificate_data)
        }
        
        return verification_details
    
    async def _verify_certificate_integrity(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify certificate data integrity"""
        # Check for required fields
        required_fields = ["certificate_id", "certificate_name", "status"]
        missing_fields = [field for field in required_fields if field not in certificate_data]
        
        return {
            "is_valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "total_fields": len(certificate_data),
            "integrity_score": (len(certificate_data) - len(missing_fields)) / len(required_fields) * 100
        }
    
    async def _verify_signature_freshness(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify signature timestamp freshness"""
        signature_timestamp = certificate_data.get("signature_timestamp")
        
        if not signature_timestamp:
            return {
                "is_valid": False,
                "reason": "No signature timestamp found",
                "age_hours": None
            }
        
        try:
            # Parse timestamp and calculate age
            timestamp = datetime.fromisoformat(signature_timestamp.replace("Z", "+00:00"))
            age = datetime.utcnow() - timestamp.replace(tzinfo=None)
            age_hours = age.total_seconds() / 3600
            
            # Consider signature fresh if less than 24 hours old
            is_fresh = age_hours < 24
            
            return {
                "is_valid": is_fresh,
                "age_hours": age_hours,
                "max_age_hours": 24,
                "reason": "Signature is fresh" if is_fresh else "Signature is too old"
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "reason": f"Invalid timestamp format: {str(e)}",
                "age_hours": None
            }
    
    async def _verify_algorithm_strength(self, algorithm: SignatureAlgorithm) -> Dict[str, Any]:
        """Verify signature algorithm cryptographic strength"""
        # Define algorithm strength scores (1-10, 10 being strongest)
        strength_scores = {
            SignatureAlgorithm.RSA_2048: 6,
            SignatureAlgorithm.RSA_4096: 8,
            SignatureAlgorithm.ECDSA_P256: 7,
            SignatureAlgorithm.ECDSA_P384: 8,
            SignatureAlgorithm.ECDSA_P521: 9,
            SignatureAlgorithm.ED25519: 9,
            SignatureAlgorithm.HMAC_SHA256: 7,
            SignatureAlgorithm.HMAC_SHA512: 8
        }
        
        strength_score = strength_scores.get(algorithm, 5)
        is_strong = strength_score >= 7
        
        return {
            "is_valid": is_strong,
            "strength_score": strength_score,
            "min_required_score": 7,
            "algorithm": algorithm.value,
            "recommendation": "Use stronger algorithm" if not is_strong else "Algorithm strength adequate"
        }
    
    async def _verify_key_validity(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify cryptographic key validity"""
        # In a real implementation, this would check key expiration, revocation, etc.
        return {
            "is_valid": True,
            "key_status": "active",
            "expiration_date": None,
            "revocation_status": "not_revoked"
        }
    
    def _determine_verification_status(self, verification_result: Dict[str, Any]) -> SignatureStatus:
        """Determine overall verification status"""
        # Check basic signature validity
        if not verification_result.get("is_valid", False):
            return SignatureStatus.INVALID
        
        # Check comprehensive verification if available
        if "certificate_integrity" in verification_result:
            integrity_check = verification_result["certificate_integrity"]
            if not integrity_check.get("is_valid", False):
                return SignatureStatus.INVALID
        
        if "signature_freshness" in verification_result:
            freshness_check = verification_result["signature_freshness"]
            if not freshness_check.get("is_valid", False):
                return SignatureStatus.EXPIRED
        
        if "algorithm_strength" in verification_result:
            strength_check = verification_result["algorithm_strength"]
            if not strength_check.get("is_valid", False):
                return SignatureStatus.UNTRUSTED
        
        return SignatureStatus.VALID
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the digital signer"""
        return {
            "status": "healthy",
            "supported_algorithms": [alg.value for alg in self.signature_algorithms],
            "active_signatures": len(self.active_signatures),
            "signature_history_size": len(self.signature_history),
            "algorithm_implementations": len(self.algorithm_implementations),
            "algorithm_verifiers": len(self.algorithm_verifiers),
            "timestamp": asyncio.get_event_loop().time()
        }
