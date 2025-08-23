"""
Cryptographic Utilities

This module provides comprehensive cryptographic utilities for encryption, decryption,
hashing, and other cryptographic operations.
"""

import asyncio
import logging
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class CryptoAlgorithm(Enum):
    """Cryptographic algorithms"""
    AES = "aes"
    RSA = "rsa"
    ECDSA = "ecdsa"
    ED25519 = "ed25519"
    CHACHA20 = "chacha20"
    CAMELLIA = "camellia"
    BLOWFISH = "blowfish"
    TWOFISH = "twofish"
    SERPENT = "serpent"
    CAST5 = "cast5"


class CryptoMode(Enum):
    """Cryptographic modes of operation"""
    ECB = "ecb"
    CBC = "cbc"
    CFB = "cfb"
    OFB = "ofb"
    CTR = "ctr"
    GCM = "gcm"
    CCM = "ccm"
    XTS = "xts"
    OCB = "ocb"
    POLY1305 = "poly1305"


@dataclass
class CryptoConfig:
    """Configuration for cryptographic operations"""
    algorithm: CryptoAlgorithm = CryptoAlgorithm.AES
    mode: CryptoMode = CryptoMode.CBC
    key_size: int = 256
    iv_size: int = 16
    salt_size: int = 32
    iterations: int = 100000
    hash_algorithm: str = "sha256"
    padding: str = "pkcs7"


class CryptoUtils:
    """
    Cryptographic utilities and management service
    
    Handles:
    - Encryption and decryption operations
    - Hash generation and verification
    - Key derivation and management
    - Digital signature operations
    - Cryptographic key storage
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the cryptographic utilities service"""
        self.crypto_algorithms = list(CryptoAlgorithm)
        self.crypto_modes = list(CryptoMode)
        
        # Cryptographic storage and metadata
        self.encrypted_data: Dict[str, Dict[str, Any]] = {}
        self.crypto_keys: Dict[str, Dict[str, Any]] = {}
        self.crypto_history: List[Dict[str, Any]] = []
        
        # Cryptographic locks and queues
        self.crypto_locks: Dict[str, asyncio.Lock] = {}
        self.crypto_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.crypto_stats = {
            "total_operations": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0,
            "total_data_size": 0
        }
        
        # Initialize default configurations
        self._initialize_default_configs()
        
        logger.info("Cryptographic utilities service initialized successfully")
    
    async def encrypt_data(
        self,
        data: Union[str, bytes],
        key: Optional[str] = None,
        config: Optional[CryptoConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Encrypt data using the specified configuration
        
        Args:
            data: Data to encrypt
            key: Encryption key (optional, will generate if not provided)
            config: Cryptographic configuration
            metadata: Additional metadata for the encryption
            
        Returns:
            Dictionary containing encrypted data and metadata
        """
        start_time = time.time()
        crypto_id = f"crypto_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_encryption_params(data, config)
            
            # Prepare data for encryption
            prepared_data = await self._prepare_data_for_encryption(data)
            
            # Apply configuration
            crypto_config = config or self._get_default_config()
            
            # Generate or use provided key
            encryption_key = key or await self._generate_encryption_key(crypto_config)
            
            # Encrypt data (simulated)
            encrypted_data = await self._encrypt_data(prepared_data, encryption_key, crypto_config)
            
            # Create metadata
            crypto_metadata = await self._create_crypto_metadata(
                crypto_id, data, encryption_key, crypto_config, metadata
            )
            
            # Store encrypted data
            crypto_info = {
                "id": crypto_id,
                "original_data": prepared_data,
                "encrypted_data": encrypted_data,
                "key_hash": hashlib.sha256(encryption_key.encode()).hexdigest(),
                "config": crypto_config.__dict__,
                "metadata": crypto_metadata,
                "encrypted_at": time.time(),
                "size_bytes": len(str(encrypted_data)),
                "status": "success"
            }
            
            self.encrypted_data[crypto_id] = crypto_info
            self.crypto_history.append(crypto_info)
            
            # Update statistics
            await self._update_crypto_stats(True, time.time() - start_time, len(str(encrypted_data)))
            
            logger.info(f"Data encrypted successfully: {crypto_id}")
            return crypto_info
            
        except Exception as e:
            await self._update_crypto_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to encrypt data: {str(e)}")
            raise
    
    async def decrypt_data(
        self,
        crypto_id: str,
        key: str
    ) -> Dict[str, Any]:
        """
        Decrypt data using the provided key
        
        Args:
            crypto_id: ID of the encrypted data
            key: Decryption key
            
        Returns:
            Dictionary containing decrypted data and metadata
        """
        if crypto_id not in self.encrypted_data:
            raise ValueError(f"Encrypted data not found: {crypto_id}")
        
        crypto_info = self.encrypted_data[crypto_id]
        
        # Verify key
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        if key_hash != crypto_info.get("key_hash"):
            raise ValueError("Invalid decryption key")
        
        # Decrypt data (simulated)
        decrypted_data = await self._decrypt_data(
            crypto_info.get("encrypted_data"), key, crypto_info.get("config")
        )
        
        return {
            "crypto_id": crypto_id,
            "decrypted_data": decrypted_data,
            "decrypted_at": time.time(),
            "status": "success"
        }
    
    async def generate_hash(
        self,
        data: Union[str, bytes],
        hash_algorithm: str = "sha256",
        salt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate hash for the provided data
        
        Args:
            data: Data to hash
            hash_algorithm: Hash algorithm to use
            salt: Salt for the hash (optional)
            metadata: Additional metadata for the hash
            
        Returns:
            Dictionary containing hash and metadata
        """
        start_time = time.time()
        hash_id = f"hash_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_hash_params(data, hash_algorithm)
            
            # Prepare data for hashing
            prepared_data = await self._prepare_data_for_hashing(data, salt)
            
            # Generate hash
            hash_value = await self._generate_hash_value(prepared_data, hash_algorithm)
            
            # Create metadata
            hash_metadata = await self._create_hash_metadata(
                hash_id, data, hash_algorithm, salt, metadata
            )
            
            # Store hash information
            hash_info = {
                "id": hash_id,
                "original_data": prepared_data,
                "hash_value": hash_value,
                "hash_algorithm": hash_algorithm,
                "salt": salt,
                "metadata": hash_metadata,
                "generated_at": time.time(),
                "status": "success"
            }
            
            self.crypto_history.append(hash_info)
            
            # Update statistics
            await self._update_crypto_stats(True, time.time() - start_time, len(str(hash_value)))
            
            logger.info(f"Hash generated successfully: {hash_id}")
            return hash_info
            
        except Exception as e:
            await self._update_crypto_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to generate hash: {str(e)}")
            raise
    
    async def verify_hash(
        self,
        data: Union[str, bytes],
        expected_hash: str,
        hash_algorithm: str = "sha256",
        salt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify hash for the provided data
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            hash_algorithm: Hash algorithm used
            salt: Salt used for the hash (optional)
            
        Returns:
            Dictionary containing verification result
        """
        try:
            # Generate hash for the data
            hash_info = await self.generate_hash(data, hash_algorithm, salt)
            actual_hash = hash_info.get("hash_value")
            
            # Compare hashes
            is_valid = actual_hash == expected_hash
            
            return {
                "data": data,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
                "is_valid": is_valid,
                "verified_at": time.time(),
                "status": "verified"
            }
            
        except Exception as e:
            logger.error(f"Failed to verify hash: {str(e)}")
            raise
    
    async def generate_key_pair(
        self,
        algorithm: CryptoAlgorithm = CryptoAlgorithm.RSA,
        key_size: int = 2048,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a key pair for the specified algorithm
        
        Args:
            algorithm: Cryptographic algorithm to use
            key_size: Size of the key in bits
            metadata: Additional metadata for the key pair
            
        Returns:
            Dictionary containing public and private keys
        """
        start_time = time.time()
        key_pair_id = f"keypair_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_key_pair_params(algorithm, key_size)
            
            # Generate key pair (simulated)
            public_key, private_key = await self._generate_key_pair(algorithm, key_size)
            
            # Create metadata
            key_metadata = await self._create_key_pair_metadata(
                key_pair_id, algorithm, key_size, metadata
            )
            
            # Store key pair information
            key_pair_info = {
                "id": key_pair_id,
                "algorithm": algorithm.value,
                "key_size": key_size,
                "public_key": public_key,
                "private_key_hash": hashlib.sha256(private_key.encode()).hexdigest(),
                "metadata": key_metadata,
                "generated_at": time.time(),
                "status": "success"
            }
            
            self.crypto_keys[key_pair_id] = key_pair_info
            self.crypto_history.append(key_pair_info)
            
            # Update statistics
            await self._update_crypto_stats(True, time.time() - start_time, key_size // 8)
            
            logger.info(f"Key pair generated successfully: {key_pair_id}")
            return key_pair_info
            
        except Exception as e:
            await self._update_crypto_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to generate key pair: {str(e)}")
            raise
    
    async def get_crypto_info(self, crypto_id: str) -> Dict[str, Any]:
        """
        Get detailed information about cryptographic operations
        
        Args:
            crypto_id: ID of the cryptographic operation
            
        Returns:
            Cryptographic operation information
        """
        # Check encrypted data
        if crypto_id in self.encrypted_data:
            return self.encrypted_data[crypto_id]
        
        # Check crypto keys
        if crypto_id in self.crypto_keys:
            return self.crypto_keys[crypto_id]
        
        # Check crypto history
        for item in self.crypto_history:
            if item.get("id") == crypto_id:
                return item
        
        raise ValueError(f"Cryptographic operation not found: {crypto_id}")
    
    async def get_crypto_history(
        self,
        algorithm: Optional[CryptoAlgorithm] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get cryptographic operation history
        
        Args:
            algorithm: Filter by cryptographic algorithm
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of cryptographic operation history entries
        """
        history = self.crypto_history
        
        if algorithm:
            history = [h for h in history if h.get("algorithm") == algorithm.value]
        
        # Sort by operation time (newest first)
        history.sort(key=lambda x: x.get("encrypted_at", x.get("generated_at", 0)), reverse=True)
        
        return history[offset:offset + limit]
    
    async def get_crypto_statistics(self) -> Dict[str, Any]:
        """
        Get cryptographic operation statistics
        
        Returns:
            Cryptographic operation statistics
        """
        return self.crypto_stats.copy()
    
    async def cleanup_expired_crypto(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired cryptographic data
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of items cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_items = []
        
        # Check encrypted data
        for crypto_id, crypto_info in self.encrypted_data.items():
            if current_time - crypto_info.get("encrypted_at", 0) > max_age_seconds:
                expired_items.append(crypto_id)
        
        # Remove expired encrypted data
        for crypto_id in expired_items:
            del self.encrypted_data[crypto_id]
        
        # Check crypto keys
        expired_keys = []
        for key_id, key_info in self.crypto_keys.items():
            if current_time - key_info.get("generated_at", 0) > max_age_seconds:
                expired_keys.append(key_id)
        
        # Remove expired crypto keys
        for key_id in expired_keys:
            del self.crypto_keys[key_id]
        
        total_cleaned = len(expired_items) + len(expired_keys)
        logger.info(f"Cleaned up {total_cleaned} expired cryptographic items")
        return total_cleaned
    
    # Private helper methods
    
    def _initialize_default_configs(self):
        """Initialize default cryptographic configurations"""
        # Default AES configuration
        self.default_aes_config = CryptoConfig(
            algorithm=CryptoAlgorithm.AES,
            mode=CryptoMode.CBC,
            key_size=256,
            iv_size=16,
            salt_size=32,
            iterations=100000,
            hash_algorithm="sha256",
            padding="pkcs7"
        )
        
        # Default RSA configuration
        self.default_rsa_config = CryptoConfig(
            algorithm=CryptoAlgorithm.RSA,
            mode=CryptoMode.ECB,
            key_size=2048,
            iv_size=0,
            salt_size=32,
            iterations=100000,
            hash_algorithm="sha256",
            padding="pkcs1"
        )
    
    def _get_default_config(self) -> CryptoConfig:
        """Get default cryptographic configuration"""
        return self.default_aes_config
    
    async def _validate_encryption_params(
        self,
        data: Union[str, bytes],
        config: Optional[CryptoConfig]
    ):
        """Validate encryption parameters"""
        if not data:
            raise ValueError("Data cannot be empty")
        
        if config and not isinstance(config, CryptoConfig):
            raise ValueError("Invalid configuration object")
    
    async def _validate_hash_params(
        self,
        data: Union[str, bytes],
        hash_algorithm: str
    ):
        """Validate hash parameters"""
        if not data:
            raise ValueError("Data cannot be empty")
        
        if not hash_algorithm:
            raise ValueError("Hash algorithm cannot be empty")
    
    async def _validate_key_pair_params(
        self,
        algorithm: CryptoAlgorithm,
        key_size: int
    ):
        """Validate key pair parameters"""
        if not isinstance(algorithm, CryptoAlgorithm):
            raise ValueError("Invalid cryptographic algorithm")
        
        if key_size <= 0:
            raise ValueError("Key size must be positive")
    
    async def _prepare_data_for_encryption(
        self,
        data: Union[str, bytes]
    ) -> bytes:
        """Prepare data for encryption"""
        if isinstance(data, str):
            return data.encode('utf-8')
        elif isinstance(data, bytes):
            return data
        else:
            return str(data).encode('utf-8')
    
    async def _prepare_data_for_hashing(
        self,
        data: Union[str, bytes],
        salt: Optional[str]
    ) -> bytes:
        """Prepare data for hashing"""
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            data_bytes = str(data).encode('utf-8')
        
        if salt:
            salt_bytes = salt.encode('utf-8')
            return salt_bytes + data_bytes
        else:
            return data_bytes
    
    async def _generate_encryption_key(self, config: CryptoConfig) -> str:
        """Generate encryption key"""
        # Simulate key generation
        key_length = config.key_size // 8
        return secrets.token_hex(key_length)
    
    async def _encrypt_data(
        self,
        data: bytes,
        key: str,
        config: CryptoConfig
    ) -> str:
        """Encrypt data (simulated)"""
        # Simulate encryption
        encrypted = f"ENCRYPTED_{data.hex()}_{key}_{config.algorithm.value}_{config.mode.value}"
        return encrypted
    
    async def _decrypt_data(
        self,
        encrypted_data: str,
        key: str,
        config: Dict[str, Any]
    ) -> str:
        """Decrypt data (simulated)"""
        # Simulate decryption
        if encrypted_data.startswith("ENCRYPTED_"):
            parts = encrypted_data.split("_")
            if len(parts) >= 4:
                data_hex = parts[1]
                try:
                    return bytes.fromhex(data_hex).decode('utf-8')
                except:
                    return "DECRYPTED_DATA"
        return "DECRYPTION_FAILED"
    
    async def _generate_hash_value(
        self,
        data: bytes,
        hash_algorithm: str
    ) -> str:
        """Generate hash value"""
        if hash_algorithm.lower() == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif hash_algorithm.lower() == "sha512":
            return hashlib.sha512(data).hexdigest()
        elif hash_algorithm.lower() == "md5":
            return hashlib.md5(data).hexdigest()
        else:
            # Default to SHA256
            return hashlib.sha256(data).hexdigest()
    
    async def _generate_key_pair(
        self,
        algorithm: CryptoAlgorithm,
        key_size: int
    ) -> Tuple[str, str]:
        """Generate key pair (simulated)"""
        # Simulate key pair generation
        public_key = f"PUBLIC_KEY_{algorithm.value}_{key_size}_{secrets.token_hex(32)}"
        private_key = f"PRIVATE_KEY_{algorithm.value}_{key_size}_{secrets.token_hex(32)}"
        return public_key, private_key
    
    async def _create_crypto_metadata(
        self,
        crypto_id: str,
        data: Union[str, bytes],
        key: str,
        config: CryptoConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for cryptographic operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "algorithm": config.algorithm.value,
            "mode": config.mode.value,
            "key_size": config.key_size,
            "config_hash": hash(str(config.__dict__)),
            "data_hash": hash(str(data)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _create_hash_metadata(
        self,
        hash_id: str,
        data: Union[str, bytes],
        hash_algorithm: str,
        salt: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for hash operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "hash_algorithm": hash_algorithm,
            "salt_used": salt is not None,
            "data_hash": hash(str(data)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _create_key_pair_metadata(
        self,
        key_pair_id: str,
        algorithm: CryptoAlgorithm,
        key_size: int,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for key pair operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "algorithm": algorithm.value,
            "key_size": key_size,
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _update_crypto_stats(self, success: bool, operation_time: float, data_size: int):
        """Update cryptographic operation statistics"""
        self.crypto_stats["total_operations"] += 1
        
        if success:
            self.crypto_stats["successful"] += 1
            self.crypto_stats["total_data_size"] += data_size
        else:
            self.crypto_stats["failed"] += 1
        
        # Update average operation time
        total_successful = self.crypto_stats["successful"]
        if total_successful > 0:
            current_avg = self.crypto_stats["average_time"]
            self.crypto_stats["average_time"] = (
                (current_avg * (total_successful - 1) + operation_time) / total_successful
            )
