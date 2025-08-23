"""
Encryption Service for Certificate Manager

Handles data encryption, decryption, and key management for certificates.
Provides secure encryption capabilities with multiple algorithms and modes.
"""

import asyncio
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime
import json
import base64
import itertools

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_128 = "AES-128"
    AES_256 = "AES-256"
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"
    CHACHA20 = "ChaCha20"
    CAMELLIA_128 = "Camellia-128"
    CAMELLIA_256 = "Camellia-256"


class EncryptionMode(Enum):
    """Encryption modes"""
    ECB = "ECB"           # Electronic Codebook (not recommended for most uses)
    CBC = "CBC"           # Cipher Block Chaining
    CFB = "CFB"           # Cipher Feedback
    OFB = "OFB"           # Output Feedback
    CTR = "CTR"           # Counter
    GCM = "GCM"           # Galois/Counter Mode
    CCM = "CCM"           # Counter with CBC-MAC


class EncryptionService:
    """
    Data encryption and decryption service
    
    Handles:
    - Data encryption with various algorithms
    - Data decryption and verification
    - Key derivation and management
    - Encryption metadata handling
    - Secure random generation
    - Encryption performance optimization
    """
    
    def __init__(self):
        """Initialize the encryption service"""
        self.supported_algorithms = list(EncryptionAlgorithm)
        self.encryption_modes = list(EncryptionMode)
        
        # Encryption storage and history
        self.encryption_records: Dict[str, Dict[str, Any]] = {}
        self.encryption_history: List[Dict[str, Any]] = []
        self.encryption_locks: Dict[str, asyncio.Lock] = {}
        
        # Encryption settings
        self.encryption_settings = self._initialize_encryption_settings()
        
        # Encryption queue for batch operations
        self.encryption_queue: asyncio.Queue = asyncio.Queue()
        self.encryption_processor_task: Optional[asyncio.Task] = None
        
        # Start encryption processor
        self._start_encryption_processor()
        
        logger.info("Encryption Service initialized successfully")
    
    def _initialize_encryption_settings(self) -> Dict[str, Any]:
        """Initialize encryption settings"""
        return {
            "default_algorithm": EncryptionAlgorithm.AES_256,
            "default_mode": EncryptionMode.GCM,
            "key_derivation_iterations": 100000,
            "salt_length": 32,
            "iv_length": 16,
            "tag_length": 16,
            "max_data_size_bytes": 100 * 1024 * 1024,  # 100MB
            "encryption_expiry_hours": 24,
            "algorithm_strength_scores": {
                EncryptionAlgorithm.AES_128: {"score": 7, "secure": True, "recommended": False},
                EncryptionAlgorithm.AES_256: {"score": 9, "secure": True, "recommended": True},
                EncryptionAlgorithm.RSA_2048: {"score": 6, "secure": True, "recommended": False},
                EncryptionAlgorithm.RSA_4096: {"score": 8, "secure": True, "recommended": True},
                EncryptionAlgorithm.CHACHA20: {"score": 9, "secure": True, "recommended": True},
                EncryptionAlgorithm.CAMELLIA_128: {"score": 7, "secure": True, "recommended": False},
                EncryptionAlgorithm.CAMELLIA_256: {"score": 9, "secure": True, "recommended": True}
            },
            "mode_security_scores": {
                EncryptionMode.ECB: {"score": 2, "secure": False, "recommended": False},
                EncryptionMode.CBC: {"score": 6, "secure": True, "recommended": False},
                EncryptionMode.CFB: {"score": 6, "secure": True, "recommended": False},
                EncryptionMode.OFB: {"score": 5, "secure": False, "recommended": False},
                EncryptionMode.CTR: {"score": 8, "secure": True, "recommended": True},
                EncryptionMode.GCM: {"score": 9, "secure": True, "recommended": True},
                EncryptionMode.CCM: {"score": 9, "secure": True, "recommended": True}
            }
        }
    
    def _start_encryption_processor(self) -> None:
        """Start the background encryption processor"""
        self.encryption_processor_task = asyncio.create_task(self._process_encryption_queue())
        logger.info("Encryption processor started")
    
    async def encrypt_data(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        algorithm: EncryptionAlgorithm = None,
        mode: EncryptionMode = None,
        key: Optional[str] = None,
        include_metadata: bool = True,
        compression: bool = False
    ) -> Dict[str, Any]:
        """
        Encrypt data using specified algorithm and mode
        
        Args:
            data: Data to encrypt
            algorithm: Encryption algorithm to use
            mode: Encryption mode to use
            key: Encryption key (generated if not provided)
            include_metadata: Whether to include encryption metadata
            compression: Whether to compress data before encryption
            
        Returns:
            Dictionary containing encrypted data and metadata
        """
        # Use defaults if not specified
        if algorithm is None:
            algorithm = self.encryption_settings["default_algorithm"]
        if mode is None:
            mode = self.encryption_settings["default_mode"]
        
        # Validate parameters
        await self._validate_encryption_parameters(algorithm, mode, data)
        
        # Generate encryption ID
        encryption_id = f"enc_{algorithm.value.lower()}_{secrets.token_hex(8)}"
        
        # Acquire encryption lock
        async with await self._acquire_encryption_lock(encryption_id):
            try:
                # Prepare data for encryption
                prepared_data = await self._prepare_data_for_encryption(data, compression)
                
                # Generate or use encryption key
                encryption_key = key or await self._generate_encryption_key(algorithm)
                
                # Generate initialization vector
                iv = await self._generate_iv(mode)
                
                # Perform encryption
                encryption_result = await self._perform_encryption(
                    prepared_data, algorithm, mode, encryption_key, iv
                )
                
                # Create encryption record
                encryption_record = {
                    "encryption_id": encryption_id,
                    "algorithm": algorithm.value,
                    "mode": mode.value,
                    "encrypted_data": encryption_result["encrypted_data"],
                    "iv": encryption_result["iv"],
                    "tag": encryption_result.get("tag"),
                    "key_fingerprint": await self._generate_key_fingerprint(encryption_key),
                    "data_size": len(prepared_data),
                    "encrypted_size": len(encryption_result["encrypted_data"]),
                    "compression_used": compression,
                    "encrypted_at": asyncio.get_event_loop().time(),
                    "status": "encrypted"
                }
                
                # Add metadata if requested
                if include_metadata:
                    encryption_record["metadata"] = await self._generate_encryption_metadata(
                        data, algorithm, mode, encryption_result, compression
                    )
                
                # Store encryption record
                self.encryption_records[encryption_id] = encryption_record
                
                # Record in history
                self.encryption_history.append({
                    "timestamp": asyncio.get_event_loop().time(),
                    "action": "encrypt",
                    "encryption_id": encryption_id,
                    "algorithm": algorithm.value,
                    "mode": mode.value,
                    "data_size": len(prepared_data)
                })
                
                logger.info(f"Data encrypted: {encryption_id} using {algorithm.value} in {mode.value} mode")
                
                return encryption_record
                
            except Exception as e:
                error_msg = f"Data encryption failed: {str(e)}"
                logger.error(f"Failed to encrypt data {encryption_id}: {error_msg}")
                
                # Store error record
                error_record = {
                    "encryption_id": encryption_id,
                    "algorithm": algorithm.value if algorithm else "unknown",
                    "mode": mode.value if mode else "unknown",
                    "status": "error",
                    "error": error_msg,
                    "encrypted_at": asyncio.get_event_loop().time()
                }
                self.encryption_records[encryption_id] = error_record
                
                raise
    
    async def decrypt_data(
        self,
        encryption_id: str,
        key: str,
        algorithm: Optional[EncryptionAlgorithm] = None,
        mode: Optional[EncryptionMode] = None
    ) -> Dict[str, Any]:
        """
        Decrypt data using encryption ID and key
        
        Args:
            encryption_id: ID of the encryption record
            key: Decryption key
            algorithm: Encryption algorithm used (auto-detected if not provided)
            mode: Encryption mode used (auto-detected if not provided)
            
        Returns:
            Dictionary containing decrypted data and metadata
        """
        # Get encryption record
        encryption_record = self.encryption_records.get(encryption_id)
        if not encryption_record:
            raise ValueError(f"Encryption record not found: {encryption_id}")
        
        # Use stored algorithm and mode if not provided
        if algorithm is None:
            algorithm = EncryptionAlgorithm(encryption_record["algorithm"])
        if mode is None:
            mode = EncryptionMode(encryption_record["mode"])
        
        try:
            # Verify key fingerprint
            key_fingerprint = await self._generate_key_fingerprint(key)
            if key_fingerprint != encryption_record["key_fingerprint"]:
                raise ValueError("Decryption key does not match encryption key")
            
            # Perform decryption
            decryption_result = await self._perform_decryption(
                encryption_record["encrypted_data"],
                algorithm,
                mode,
                key,
                encryption_record["iv"],
                encryption_record.get("tag")
            )
            
            # Create decryption record
            decryption_record = {
                "encryption_id": encryption_id,
                "algorithm": algorithm.value,
                "mode": mode.value,
                "decrypted_data": decryption_result["decrypted_data"],
                "data_size": len(decryption_result["decrypted_data"]),
                "decrypted_at": asyncio.get_event_loop().time(),
                "status": "decrypted"
            }
            
            # Record in history
            self.encryption_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "decrypt",
                "encryption_id": encryption_id,
                "algorithm": algorithm.value,
                "mode": mode.value,
                "data_size": len(decryption_result["decrypted_data"])
            })
            
            logger.info(f"Data decrypted: {encryption_id} using {algorithm.value} in {mode.value} mode")
            
            return decryption_record
            
        except Exception as e:
            error_msg = f"Data decryption failed: {str(e)}"
            logger.error(f"Failed to decrypt data {encryption_id}: {error_msg}")
            raise
    
    async def encrypt_batch_data(
        self,
        data_items: List[Union[str, bytes, Dict[str, Any]]],
        algorithm: EncryptionAlgorithm = None,
        mode: EncryptionMode = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Encrypt multiple data items in batch
        
        Args:
            data_items: List of data items to encrypt
            algorithm: Encryption algorithm to use
            mode: Encryption mode to use
            include_metadata: Whether to include encryption metadata
            
        Returns:
            List of encryption records
        """
        batch_results = []
        
        for i, data in enumerate(data_items):
            try:
                # Encrypt individual item
                encryption_result = await self.encrypt_data(
                    data, algorithm, mode, include_metadata=include_metadata
                )
                
                # Add batch index
                encryption_result["batch_index"] = i
                batch_results.append(encryption_result)
                
            except Exception as e:
                logger.error(f"Failed to encrypt batch item {i}: {e}")
                batch_results.append({
                    "batch_index": i,
                    "error": str(e),
                    "status": "error"
                })
        
        return batch_results
    
    async def generate_encryption_key(
        self,
        algorithm: EncryptionAlgorithm,
        key_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate encryption key for specified algorithm
        
        Args:
            algorithm: Encryption algorithm for key generation
            key_length: Key length in bits (auto-determined if not provided)
            
        Returns:
            Dictionary containing generated key and metadata
        """
        # Validate algorithm
        if algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
        
        # Determine key length
        if key_length is None:
            key_length = self._get_default_key_length(algorithm)
        
        # Generate key
        key = await self._generate_random_key(key_length)
        
        # Create key record
        key_record = {
            "algorithm": algorithm.value,
            "key_length": key_length,
            "key": key,
            "key_fingerprint": await self._generate_key_fingerprint(key),
            "generated_at": asyncio.get_event_loop().time(),
            "strength_score": self._get_algorithm_strength_score(algorithm)
        }
        
        logger.info(f"Encryption key generated for {algorithm.value} with {key_length} bits")
        
        return key_record
    
    async def derive_key_from_password(
        self,
        password: str,
        salt: Optional[str] = None,
        key_length: int = 256,
        iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if not provided)
            key_length: Desired key length in bits
            iterations: Number of iterations (uses default if not provided)
            
        Returns:
            Dictionary containing derived key and metadata
        """
        # Use default iterations if not provided
        if iterations is None:
            iterations = self.encryption_settings["key_derivation_iterations"]
        
        # Generate salt if not provided
        if salt is None:
            salt = await self._generate_random_salt()
        
        # Derive key using PBKDF2
        derived_key = await self._derive_pbkdf2_key(password, salt, key_length, iterations)
        
        # Create key record
        key_record = {
            "derivation_method": "PBKDF2",
            "key_length": key_length,
            "salt": salt,
            "iterations": iterations,
            "derived_key": derived_key,
            "key_fingerprint": await self._generate_key_fingerprint(derived_key),
            "derived_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"Key derived from password using PBKDF2 with {iterations} iterations")
        
        return key_record
    
    async def _validate_encryption_parameters(
        self,
        algorithm: EncryptionAlgorithm,
        mode: EncryptionMode,
        data: Union[str, bytes, Dict[str, Any]]
    ) -> None:
        """Validate encryption parameters"""
        # Validate algorithm
        if algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
        
        # Validate mode
        if mode not in self.encryption_modes:
            raise ValueError(f"Unsupported encryption mode: {mode}")
        
        # Check algorithm-mode compatibility
        if not self._is_algorithm_mode_compatible(algorithm, mode):
            raise ValueError(f"Algorithm {algorithm.value} is not compatible with mode {mode.value}")
        
        # Validate data size
        data_size = len(data) if isinstance(data, (str, bytes)) else len(str(data))
        max_size = self.encryption_settings["max_data_size_bytes"]
        if data_size > max_size:
            raise ValueError(f"Data size {data_size} bytes exceeds maximum {max_size} bytes")
    
    async def _prepare_data_for_encryption(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        compression: bool
    ) -> bytes:
        """Prepare data for encryption"""
        # Convert data to bytes
        if isinstance(data, bytes):
            data_bytes = data
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            # Convert dictionary to canonical JSON string
            json_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
            data_bytes = json_string.encode('utf-8')
        else:
            data_bytes = str(data).encode('utf-8')
        
        # Apply compression if requested
        if compression:
            # In a real implementation, this would use actual compression
            # For now, we'll simulate compression
            data_bytes = await self._simulate_compression(data_bytes)
        
        return data_bytes
    
    async def _simulate_compression(self, data: bytes) -> bytes:
        """Simulate data compression (placeholder)"""
        # In a real implementation, this would use zlib, gzip, or similar
        # For now, return the data as-is
        return data
    
    async def _generate_encryption_key(self, algorithm: EncryptionAlgorithm) -> str:
        """Generate encryption key for algorithm"""
        key_length = self._get_default_key_length(algorithm)
        return await self._generate_random_key(key_length)
    
    def _get_default_key_length(self, algorithm: EncryptionAlgorithm) -> int:
        """Get default key length for algorithm"""
        key_lengths = {
            EncryptionAlgorithm.AES_128: 128,
            EncryptionAlgorithm.AES_256: 256,
            EncryptionAlgorithm.RSA_2048: 2048,
            EncryptionAlgorithm.RSA_4096: 4096,
            EncryptionAlgorithm.CHACHA20: 256,
            EncryptionAlgorithm.CAMELLIA_128: 128,
            EncryptionAlgorithm.CAMELLIA_256: 256
        }
        return key_lengths.get(algorithm, 256)
    
    async def _generate_random_key(self, key_length: int) -> str:
        """Generate random key of specified length"""
        # Generate random bytes
        key_bytes = secrets.token_bytes(key_length // 8)
        # Convert to base64 for storage
        return base64.b64encode(key_bytes).decode('utf-8')
    
    async def _generate_iv(self, mode: EncryptionMode) -> str:
        """Generate initialization vector for mode"""
        iv_length = self.encryption_settings["iv_length"]
        iv_bytes = secrets.token_bytes(iv_length)
        return base64.b64encode(iv_bytes).decode('utf-8')
    
    async def _generate_random_salt(self) -> str:
        """Generate random salt for key derivation"""
        salt_length = self.encryption_settings["salt_length"]
        salt_bytes = secrets.token_bytes(salt_length)
        return base64.b64encode(salt_bytes).decode('utf-8')
    
    async def _perform_encryption(
        self,
        data: bytes,
        algorithm: EncryptionAlgorithm,
        mode: EncryptionMode,
        key: str,
        iv: str
    ) -> Dict[str, Any]:
        """Perform actual encryption (simulated)"""
        # In a real implementation, this would use actual cryptographic libraries
        # For now, we'll simulate encryption
        
        # Decode key and IV
        key_bytes = base64.b64decode(key.encode('utf-8'))
        iv_bytes = base64.b64decode(iv.encode('utf-8'))
        
        # Simulate encryption by XORing with key and IV
        encrypted_data = bytearray()
        key_cycle = itertools.cycle(key_bytes)
        iv_cycle = itertools.cycle(iv_bytes)
        
        for i, byte in enumerate(data):
            key_byte = next(key_cycle)
            iv_byte = next(iv_cycle)
            encrypted_byte = byte ^ key_byte ^ iv_byte
            encrypted_data.append(encrypted_byte)
        
        # Convert to base64 for storage
        encrypted_b64 = base64.b64encode(bytes(encrypted_data)).decode('utf-8')
        
        # Generate authentication tag for authenticated modes
        tag = None
        if mode in [EncryptionMode.GCM, EncryptionMode.CCM]:
            tag = await self._generate_auth_tag(encrypted_data, key_bytes, iv_bytes)
        
        return {
            "encrypted_data": encrypted_b64,
            "iv": iv,
            "tag": tag,
            "algorithm": algorithm.value,
            "mode": mode.value
        }
    
    async def _perform_decryption(
        self,
        encrypted_data: str,
        algorithm: EncryptionAlgorithm,
        mode: EncryptionMode,
        key: str,
        iv: str,
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform actual decryption (simulated)"""
        # In a real implementation, this would use actual cryptographic libraries
        # For now, we'll simulate decryption
        
        # Decode encrypted data, key, and IV
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        key_bytes = base64.b64decode(key.encode('utf-8'))
        iv_bytes = base64.b64decode(iv.encode('utf-8'))
        
        # Verify authentication tag if present
        if tag and mode in [EncryptionMode.GCM, EncryptionMode.CCM]:
            expected_tag = await self._generate_auth_tag(encrypted_bytes, key_bytes, iv_bytes)
            if tag != expected_tag:
                raise ValueError("Authentication tag verification failed")
        
        # Simulate decryption by XORing with key and IV
        decrypted_data = bytearray()
        key_cycle = itertools.cycle(key_bytes)
        iv_cycle = itertools.cycle(iv_bytes)
        
        for i, byte in enumerate(encrypted_bytes):
            key_byte = next(key_cycle)
            iv_byte = next(iv_cycle)
            decrypted_byte = byte ^ key_byte ^ iv_byte
            decrypted_data.append(decrypted_byte)
        
        return {
            "decrypted_data": bytes(decrypted_data),
            "algorithm": algorithm.value,
            "mode": mode.value
        }
    
    async def _generate_auth_tag(
        self,
        data: bytes,
        key: bytes,
        iv: bytes
    ) -> str:
        """Generate authentication tag for authenticated modes"""
        # In a real implementation, this would generate actual authentication tags
        # For now, we'll simulate by hashing the data with key and IV
        tag_data = data + key + iv
        tag_hash = hashlib.sha256(tag_data).digest()[:16]  # Use first 16 bytes
        return base64.b64encode(tag_hash).decode('utf-8')
    
    async def _derive_pbkdf2_key(
        self,
        password: str,
        salt: str,
        key_length: int,
        iterations: int
    ) -> str:
        """Derive key using PBKDF2 (simulated)"""
        # In a real implementation, this would use actual PBKDF2
        # For now, we'll simulate key derivation
        
        # Combine password and salt
        combined = password.encode('utf-8') + salt.encode('utf-8')
        
        # Simulate multiple iterations
        current = combined
        for i in range(iterations):
            current = hashlib.sha256(current).digest()
        
        # Truncate or extend to desired key length
        key_bytes = current[:key_length // 8]
        if len(key_bytes) < key_length // 8:
            # Extend key if needed
            while len(key_bytes) < key_length // 8:
                current = hashlib.sha256(current).digest()
                key_bytes += current[:min(len(current), key_length // 8 - len(key_bytes))]
        
        return base64.b64encode(key_bytes).decode('utf-8')
    
    async def _generate_encryption_metadata(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        algorithm: EncryptionAlgorithm,
        mode: EncryptionMode,
        encryption_result: Dict[str, Any],
        compression: bool
    ) -> Dict[str, Any]:
        """Generate metadata for encryption operation"""
        metadata = {
            "data_type": type(data).__name__,
            "algorithm_strength": self._get_algorithm_strength_score(algorithm),
            "mode_security": self._get_mode_security_score(mode),
            "compression_used": compression,
            "encryption_timestamp": asyncio.get_event_loop().time(),
            "key_length": self._get_default_key_length(algorithm)
        }
        
        # Add data-specific metadata
        if isinstance(data, dict):
            metadata["data_keys"] = list(data.keys())
            metadata["data_depth"] = await self._calculate_data_depth(data)
        
        return metadata
    
    async def _calculate_data_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate the maximum depth of nested data structures"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(
                await self._calculate_data_depth(value, current_depth + 1)
                for value in data.values()
            )
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(
                await self._calculate_data_depth(item, current_depth + 1)
                for item in data
            )
        else:
            return current_depth
    
    async def _generate_key_fingerprint(self, key: str) -> str:
        """Generate fingerprint for key"""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _is_algorithm_mode_compatible(self, algorithm: EncryptionAlgorithm, mode: EncryptionMode) -> bool:
        """Check if algorithm and mode are compatible"""
        # Define compatibility matrix
        compatibility = {
            EncryptionAlgorithm.AES_128: [EncryptionMode.ECB, EncryptionMode.CBC, EncryptionMode.CFB, EncryptionMode.OFB, EncryptionMode.CTR, EncryptionMode.GCM, EncryptionMode.CCM],
            EncryptionAlgorithm.AES_256: [EncryptionMode.ECB, EncryptionMode.CBC, EncryptionMode.CFB, EncryptionMode.OFB, EncryptionMode.CTR, EncryptionMode.GCM, EncryptionMode.CCM],
            EncryptionAlgorithm.RSA_2048: [EncryptionMode.ECB],  # RSA only supports ECB mode
            EncryptionAlgorithm.RSA_4096: [EncryptionMode.ECB],
            EncryptionAlgorithm.CHACHA20: [EncryptionMode.CTR],
            EncryptionAlgorithm.CAMELLIA_128: [EncryptionMode.ECB, EncryptionMode.CBC, EncryptionMode.CFB, EncryptionMode.OFB, EncryptionMode.CTR],
            EncryptionAlgorithm.CAMELLIA_256: [EncryptionMode.ECB, EncryptionMode.CBC, EncryptionMode.CFB, EncryptionMode.OFB, EncryptionMode.CTR]
        }
        
        return mode in compatibility.get(algorithm, [])
    
    def _get_algorithm_strength_score(self, algorithm: EncryptionAlgorithm) -> int:
        """Get strength score for algorithm"""
        strength_info = self.encryption_settings["algorithm_strength_scores"].get(algorithm, {})
        return strength_info.get("score", 5)
    
    def _get_mode_security_score(self, mode: EncryptionMode) -> int:
        """Get security score for mode"""
        security_info = self.encryption_settings["mode_security_scores"].get(mode, {})
        return security_info.get("score", 5)
    
    async def _acquire_encryption_lock(self, encryption_id: str) -> asyncio.Lock:
        """Acquire a lock for encryption operations"""
        if encryption_id not in self.encryption_locks:
            self.encryption_locks[encryption_id] = asyncio.Lock()
        return self.encryption_locks[encryption_id]
    
    async def _process_encryption_queue(self) -> None:
        """Background task to process encryption queue"""
        try:
            while True:
                # Get next encryption request
                encryption_request = await self.encryption_queue.get()
                
                try:
                    # Process encryption request (placeholder for future batch processing)
                    logger.debug(f"Processing encryption request: {encryption_request}")
                    
                except Exception as e:
                    logger.error(f"Failed to process encryption request: {e}")
                
                finally:
                    # Mark task as done
                    self.encryption_queue.task_done()
                    
        except asyncio.CancelledError:
            logger.info("Encryption processor cancelled")
        except Exception as e:
            logger.error(f"Encryption processor error: {e}")
    
    async def get_encryption_info(self, encryption_id: str) -> Optional[Dict[str, Any]]:
        """Get encryption information by ID"""
        return self.encryption_records.get(encryption_id)
    
    async def get_encryption_statistics(self) -> Dict[str, Any]:
        """Get encryption statistics"""
        total_encryptions = len(self.encryption_records)
        successful_encryptions = len([e for e in self.encryption_records.values() if e.get("status") == "encrypted"])
        error_encryptions = len([e for e in self.encryption_records.values() if e.get("status") == "error"])
        
        # Count by algorithm
        encryptions_by_algorithm = {}
        for record in self.encryption_records.values():
            algorithm = record.get("algorithm", "unknown")
            encryptions_by_algorithm[algorithm] = encryptions_by_algorithm.get(algorithm, 0) + 1
        
        # Count by mode
        encryptions_by_mode = {}
        for record in self.encryption_records.values():
            mode = record.get("mode", "unknown")
            encryptions_by_mode[mode] = encryptions_by_mode.get(mode, 0) + 1
        
        return {
            "total_encryptions": total_encryptions,
            "successful_encryptions": successful_encryptions,
            "error_encryptions": error_encryptions,
            "encryptions_by_algorithm": encryptions_by_algorithm,
            "encryptions_by_mode": encryptions_by_mode,
            "encryption_queue_size": self.encryption_queue.qsize(),
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def get_encryption_history(
        self,
        algorithm: Optional[EncryptionAlgorithm] = None,
        mode: Optional[EncryptionMode] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get encryption history with optional filtering"""
        history = self.encryption_history.copy()
        
        # Filter by algorithm
        if algorithm:
            history = [h for h in history if h.get("algorithm") == algorithm.value]
        
        # Filter by mode
        if mode:
            history = [h for h in history if h.get("mode") == mode.value]
        
        # Filter by action
        if action:
            history = [h for h in history if h.get("action") == action]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def cleanup_expired_encryptions(self) -> int:
        """Clean up expired encryptions and return count of cleaned encryptions"""
        current_time = asyncio.get_event_loop().time()
        expiry_hours = self.encryption_settings["encryption_expiry_hours"]
        expired_encryptions = []
        
        for encryption_id, record in self.encryption_records.items():
            encrypted_at = record.get("encrypted_at", 0)
            if current_time - encrypted_at > (expiry_hours * 3600):
                expired_encryptions.append(encryption_id)
        
        # Mark expired encryptions
        for encryption_id in expired_encryptions:
            self.encryption_records[encryption_id]["status"] = "expired"
            self.encryption_records[encryption_id]["expired_at"] = current_time
        
        if expired_encryptions:
            logger.info(f"Marked {len(expired_encryptions)} encryptions as expired")
        
        return len(expired_encryptions)
    
    async def stop_encryption_processor(self) -> None:
        """Stop the encryption processor"""
        if self.encryption_processor_task:
            self.encryption_processor_task.cancel()
            try:
                await self.encryption_processor_task
            except asyncio.CancelledError:
                pass
            self.encryption_processor_task = None
            logger.info("Encryption processor stopped")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the encryption service"""
        return {
            "status": "healthy",
            "supported_algorithms": [alg.value for alg in self.supported_algorithms],
            "encryption_modes": [mode.value for mode in self.encryption_modes],
            "encryption_records_count": len(self.encryption_records),
            "encryption_history_size": len(self.encryption_history),
            "encryption_queue_size": self.encryption_queue.qsize(),
            "encryption_processor_running": self.encryption_processor_task is not None and not self.encryption_processor_task.done(),
            "encryption_settings": {
                "default_algorithm": self.encryption_settings["default_algorithm"].value,
                "default_mode": self.encryption_settings["default_mode"].value,
                "max_data_size_bytes": self.encryption_settings["max_data_size_bytes"],
                "key_derivation_iterations": self.encryption_settings["key_derivation_iterations"]
            },
            "timestamp": asyncio.get_event_loop().time()
        }
