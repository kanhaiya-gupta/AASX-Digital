"""
Hash Generator for Certificate Manager

Handles hash generation, verification, and management for certificates.
Provides cryptographic hash functions and integrity checking capabilities.
"""

import asyncio
import hashlib
import hmac
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime
import json
import secrets

logger = logging.getLogger(__name__)


class HashAlgorithm(Enum):
    """Supported hash algorithms"""
    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA224 = "SHA224"
    SHA256 = "SHA256"
    SHA384 = "SHA384"
    SHA512 = "SHA512"
    SHA3_224 = "SHA3-224"
    SHA3_256 = "SHA3-256"
    SHA3_384 = "SHA3-384"
    SHA3_512 = "SHA3-512"
    BLAKE2B = "BLAKE2B"
    BLAKE2S = "BLAKE2S"


class HashStatus(Enum):
    """Hash operation status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    PROCESSING = "processing"
    ERROR = "error"
    EXPIRED = "expired"


class HashGenerator:
    """
    Hash generation and verification service
    
    Handles:
    - Hash generation for various algorithms
    - Hash verification and integrity checking
    - HMAC generation and verification
    - Hash collision detection
    - Hash performance optimization
    - Hash metadata management
    """
    
    def __init__(self):
        """Initialize the hash generator"""
        self.supported_algorithms = list(HashAlgorithm)
        self.hash_statuses = list(HashStatus)
        
        # Hash storage and history
        self.generated_hashes: Dict[str, Dict[str, Any]] = {}
        self.hash_history: List[Dict[str, Any]] = []
        self.hash_locks: Dict[str, asyncio.Lock] = {}
        
        # Hash algorithm implementations
        self.hash_implementations = self._initialize_hash_implementations()
        
        # Hash settings and thresholds
        self.hash_settings = self._initialize_hash_settings()
        
        # Hash generation queue for batch operations
        self.hash_generation_queue: asyncio.Queue = asyncio.Queue()
        self.generation_processor_task: Optional[asyncio.Task] = None
        
        # Start hash generation processor
        self._start_hash_generation_processor()
        
        logger.info("Hash Generator initialized successfully")
    
    def _initialize_hash_implementations(self) -> Dict[HashAlgorithm, Any]:
        """Initialize hash algorithm implementations"""
        return {
            HashAlgorithm.MD5: hashlib.md5,
            HashAlgorithm.SHA1: hashlib.sha1,
            HashAlgorithm.SHA224: hashlib.sha224,
            HashAlgorithm.SHA256: hashlib.sha256,
            HashAlgorithm.SHA384: hashlib.sha384,
            HashAlgorithm.SHA512: hashlib.sha512,
            HashAlgorithm.SHA3_224: hashlib.sha3_224,
            HashAlgorithm.SHA3_256: hashlib.sha3_256,
            HashAlgorithm.SHA3_384: hashlib.sha3_384,
            HashAlgorithm.SHA3_512: hashlib.sha3_512,
            HashAlgorithm.BLAKE2B: hashlib.blake2b,
            HashAlgorithm.BLAKE2S: hashlib.blake2s
        }
    
    def _initialize_hash_settings(self) -> Dict[str, Any]:
        """Initialize hash generation settings"""
        return {
            "default_algorithm": HashAlgorithm.SHA256,
            "hash_expiry_hours": 24,
            "max_hash_size_bytes": 1024 * 1024,  # 1MB
            "batch_processing_enabled": True,
            "collision_detection_enabled": True,
            "performance_optimization": True,
            "algorithm_strength_scores": {
                HashAlgorithm.MD5: {"score": 2, "secure": False, "deprecated": True},
                HashAlgorithm.SHA1: {"score": 3, "secure": False, "deprecated": True},
                HashAlgorithm.SHA224: {"score": 6, "secure": True, "deprecated": False},
                HashAlgorithm.SHA256: {"score": 8, "secure": True, "deprecated": False},
                HashAlgorithm.SHA384: {"score": 9, "secure": True, "deprecated": False},
                HashAlgorithm.SHA512: {"score": 9, "secure": True, "deprecated": False},
                HashAlgorithm.SHA3_224: {"score": 8, "secure": True, "deprecated": False},
                HashAlgorithm.SHA3_256: {"score": 9, "secure": True, "deprecated": False},
                HashAlgorithm.SHA3_384: {"score": 9, "secure": True, "deprecated": False},
                HashAlgorithm.SHA3_512: {"score": 10, "secure": True, "deprecated": False},
                HashAlgorithm.BLAKE2B: {"score": 9, "secure": True, "deprecated": False},
                HashAlgorithm.BLAKE2S: {"score": 8, "secure": True, "deprecated": False}
            }
        }
    
    def _start_hash_generation_processor(self) -> None:
        """Start the background hash generation processor"""
        self.generation_processor_task = asyncio.create_task(self._process_hash_generation_queue())
        logger.info("Hash generation processor started")
    
    async def generate_hash(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        algorithm: HashAlgorithm = None,
        include_metadata: bool = True,
        salt: Optional[str] = None,
        iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Generate hash for data using specified algorithm
        
        Args:
            data: Data to hash (string, bytes, or dictionary)
            algorithm: Hash algorithm to use (defaults to SHA256)
            include_metadata: Whether to include hash metadata
            salt: Optional salt for hash generation
            iterations: Number of hash iterations
            
        Returns:
            Dictionary containing hash and metadata
        """
        # Use default algorithm if none specified
        if algorithm is None:
            algorithm = self.hash_settings["default_algorithm"]
        
        # Validate algorithm
        if algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        # Generate hash ID
        hash_id = f"hash_{algorithm.value.lower()}_{secrets.token_hex(8)}"
        
        # Acquire hash lock
        async with await self._acquire_hash_lock(hash_id):
            try:
                # Prepare data for hashing
                prepared_data = await self._prepare_data_for_hashing(data)
                
                # Validate data size
                await self._validate_data_size(prepared_data)
                
                # Generate hash
                hash_result = await self._generate_single_hash(
                    prepared_data, algorithm, salt, iterations
                )
                
                # Create hash record
                hash_record = {
                    "hash_id": hash_id,
                    "algorithm": algorithm.value,
                    "hash_value": hash_result["hash"],
                    "data_size": len(prepared_data),
                    "salt": salt,
                    "iterations": iterations,
                    "generated_at": asyncio.get_event_loop().time(),
                    "status": HashStatus.VALID.value,
                    "strength_score": self._get_algorithm_strength_score(algorithm),
                    "secure": self._is_algorithm_secure(algorithm),
                    "deprecated": self._is_algorithm_deprecated(algorithm)
                }
                
                # Add metadata if requested
                if include_metadata:
                    hash_record["metadata"] = await self._generate_hash_metadata(
                        data, algorithm, hash_result
                    )
                
                # Store hash record
                self.generated_hashes[hash_id] = hash_record
                
                # Record in history
                self.hash_history.append({
                    "timestamp": asyncio.get_event_loop().time(),
                    "action": "generate",
                    "hash_id": hash_id,
                    "algorithm": algorithm.value,
                    "data_size": len(prepared_data)
                })
                
                logger.info(f"Hash generated: {hash_id} using {algorithm.value}")
                
                return hash_record
                
            except Exception as e:
                error_msg = f"Hash generation failed: {str(e)}"
                logger.error(f"Failed to generate hash {hash_id}: {error_msg}")
                
                # Store error record
                error_record = {
                    "hash_id": hash_id,
                    "algorithm": algorithm.value if algorithm else "unknown",
                    "status": HashStatus.ERROR.value,
                    "error": error_msg,
                    "generated_at": asyncio.get_event_loop().time()
                }
                self.generated_hashes[hash_id] = error_record
                
                raise
    
    async def generate_hmac(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        key: str,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ) -> Dict[str, Any]:
        """
        Generate HMAC for data using specified key and algorithm
        
        Args:
            data: Data to hash
            key: Secret key for HMAC generation
            algorithm: Hash algorithm to use
            
        Returns:
            Dictionary containing HMAC and metadata
        """
        # Validate algorithm
        if algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        # Generate HMAC ID
        hmac_id = f"hmac_{algorithm.value.lower()}_{secrets.token_hex(8)}"
        
        try:
            # Prepare data for hashing
            prepared_data = await self._prepare_data_for_hashing(data)
            
            # Generate HMAC
            hmac_result = await self._generate_single_hmac(prepared_data, key, algorithm)
            
            # Create HMAC record
            hmac_record = {
                "hash_id": hmac_id,
                "algorithm": f"HMAC-{algorithm.value}",
                "hash_value": hmac_result["hmac"],
                "key_fingerprint": await self._generate_key_fingerprint(key),
                "data_size": len(prepared_data),
                "generated_at": asyncio.get_event_loop().time(),
                "status": HashStatus.VALID.value,
                "type": "hmac"
            }
            
            # Store HMAC record
            self.generated_hashes[hmac_id] = hmac_record
            
            # Record in history
            self.hash_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "generate_hmac",
                "hash_id": hmac_id,
                "algorithm": f"HMAC-{algorithm.value}",
                "data_size": len(prepared_data)
            })
            
            logger.info(f"HMAC generated: {hmac_id} using {algorithm.value}")
            
            return hmac_record
            
        except Exception as e:
            error_msg = f"HMAC generation failed: {str(e)}"
            logger.error(f"Failed to generate HMAC {hmac_id}: {error_msg}")
            raise
    
    async def verify_hash(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        expected_hash: str,
        algorithm: HashAlgorithm,
        salt: Optional[str] = None,
        iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Verify hash against data
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            salt: Salt used in hash generation
            iterations: Number of iterations used
            
        Returns:
            Dictionary containing verification result
        """
        try:
            # Generate hash for verification
            verification_hash = await self.generate_hash(
                data, algorithm, include_metadata=False, salt=salt, iterations=iterations
            )
            
            # Compare hashes
            is_valid = verification_hash["hash_value"] == expected_hash
            
            # Create verification result
            verification_result = {
                "is_valid": is_valid,
                "expected_hash": expected_hash,
                "actual_hash": verification_hash["hash_value"],
                "algorithm": algorithm.value,
                "verification_timestamp": asyncio.get_event_loop().time(),
                "data_size": verification_hash["data_size"]
            }
            
            # Record verification
            self.hash_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "verify",
                "algorithm": algorithm.value,
                "verification_result": verification_result
            })
            
            logger.info(f"Hash verification: {'PASSED' if is_valid else 'FAILED'} using {algorithm.value}")
            
            return verification_result
            
        except Exception as e:
            error_msg = f"Hash verification failed: {str(e)}"
            logger.error(f"Failed to verify hash: {error_msg}")
            raise
    
    async def verify_hmac(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        expected_hmac: str,
        key: str,
        algorithm: HashAlgorithm
    ) -> Dict[str, Any]:
        """
        Verify HMAC against data and key
        
        Args:
            data: Data to verify
            expected_hmac: Expected HMAC value
            key: Secret key used
            algorithm: Hash algorithm used
            
        Returns:
            Dictionary containing verification result
        """
        try:
            # Generate HMAC for verification
            verification_hmac = await self.generate_hmac(data, key, algorithm)
            
            # Compare HMACs
            is_valid = verification_hmac["hash_value"] == expected_hmac
            
            # Create verification result
            verification_result = {
                "is_valid": is_valid,
                "expected_hmac": expected_hmac,
                "actual_hmac": verification_hmac["hash_value"],
                "algorithm": f"HMAC-{algorithm.value}",
                "verification_timestamp": asyncio.get_event_loop().time(),
                "data_size": verification_hmac["data_size"]
            }
            
            # Record verification
            self.hash_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "verify_hmac",
                "algorithm": f"HMAC-{algorithm.value}",
                "verification_result": verification_result
            })
            
            logger.info(f"HMAC verification: {'PASSED' if is_valid else 'FAILED'} using {algorithm.value}")
            
            return verification_result
            
        except Exception as e:
            error_msg = f"HMAC verification failed: {str(e)}"
            logger.error(f"Failed to verify HMAC: {error_msg}")
            raise
    
    async def generate_batch_hashes(
        self,
        data_items: List[Union[str, bytes, Dict[str, Any]]],
        algorithm: HashAlgorithm = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate hashes for multiple data items
        
        Args:
            data_items: List of data items to hash
            algorithm: Hash algorithm to use
            include_metadata: Whether to include hash metadata
            
        Returns:
            List of hash records
        """
        batch_results = []
        
        for i, data in enumerate(data_items):
            try:
                # Generate hash for individual item
                hash_result = await self.generate_hash(
                    data, algorithm, include_metadata
                )
                
                # Add batch index
                hash_result["batch_index"] = i
                batch_results.append(hash_result)
                
            except Exception as e:
                logger.error(f"Failed to generate hash for batch item {i}: {e}")
                batch_results.append({
                    "batch_index": i,
                    "error": str(e),
                    "status": HashStatus.ERROR.value
                })
        
        return batch_results
    
    async def get_hash_info(self, hash_id: str) -> Optional[Dict[str, Any]]:
        """Get hash information by ID"""
        return self.generated_hashes.get(hash_id)
    
    async def get_hash_statistics(self) -> Dict[str, Any]:
        """Get hash generation statistics"""
        total_hashes = len(self.generated_hashes)
        valid_hashes = len([h for h in self.generated_hashes.values() if h.get("status") == HashStatus.VALID.value])
        error_hashes = len([h for h in self.generated_hashes.values() if h.get("status") == HashStatus.ERROR.value])
        
        # Count by algorithm
        hashes_by_algorithm = {}
        for hash_record in self.generated_hashes.values():
            algorithm = hash_record.get("algorithm", "unknown")
            hashes_by_algorithm[algorithm] = hashes_by_algorithm.get(algorithm, 0) + 1
        
        # Count by type
        hmac_count = len([h for h in self.generated_hashes.values() if h.get("type") == "hmac"])
        regular_hash_count = total_hashes - hmac_count
        
        return {
            "total_hashes": total_hashes,
            "valid_hashes": valid_hashes,
            "error_hashes": error_hashes,
            "regular_hashes": regular_hash_count,
            "hmac_hashes": hmac_count,
            "hashes_by_algorithm": hashes_by_algorithm,
            "hash_generation_queue_size": self.hash_generation_queue.qsize(),
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def _acquire_hash_lock(self, hash_id: str) -> asyncio.Lock:
        """Acquire a lock for hash operations"""
        if hash_id not in self.hash_locks:
            self.hash_locks[hash_id] = asyncio.Lock()
        return self.hash_locks[hash_id]
    
    async def _prepare_data_for_hashing(self, data: Union[str, bytes, Dict[str, Any]]) -> bytes:
        """Prepare data for hashing"""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode('utf-8')
        elif isinstance(data, dict):
            # Convert dictionary to canonical JSON string
            json_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
            return json_string.encode('utf-8')
        else:
            return str(data).encode('utf-8')
    
    async def _validate_data_size(self, data: bytes) -> None:
        """Validate data size for hashing"""
        max_size = self.hash_settings["max_hash_size_bytes"]
        if len(data) > max_size:
            raise ValueError(f"Data size {len(data)} bytes exceeds maximum {max_size} bytes")
    
    async def _generate_single_hash(
        self,
        data: bytes,
        algorithm: HashAlgorithm,
        salt: Optional[str],
        iterations: int
    ) -> Dict[str, Any]:
        """Generate hash for data using specified algorithm"""
        # Get hash implementation
        hash_impl = self.hash_implementations.get(algorithm)
        if not hash_impl:
            raise ValueError(f"No implementation for algorithm: {algorithm}")
        
        # Apply salt if provided
        if salt:
            salted_data = salt.encode('utf-8') + data
        else:
            salted_data = data
        
        # Generate hash with iterations
        current_hash = salted_data
        for i in range(iterations):
            hash_obj = hash_impl()
            hash_obj.update(current_hash)
            current_hash = hash_obj.digest()
        
        # Convert to hex string
        hash_hex = current_hash.hex()
        
        return {
            "hash": hash_hex,
            "algorithm": algorithm.value,
            "salt": salt,
            "iterations": iterations,
            "data_size": len(data)
        }
    
    async def _generate_single_hmac(
        self,
        data: bytes,
        key: str,
        algorithm: HashAlgorithm
    ) -> Dict[str, Any]:
        """Generate HMAC for data using specified key and algorithm"""
        # Get hash implementation
        hash_impl = self.hash_implementations.get(algorithm)
        if not hash_impl:
            raise ValueError(f"No implementation for algorithm: {algorithm}")
        
        # Generate HMAC
        key_bytes = key.encode('utf-8')
        hmac_obj = hmac.new(key_bytes, data, hash_impl)
        hmac_result = hmac_obj.hexdigest()
        
        return {
            "hmac": hmac_result,
            "algorithm": f"HMAC-{algorithm.value}",
            "key_fingerprint": await self._generate_key_fingerprint(key),
            "data_size": len(data)
        }
    
    async def _generate_hash_metadata(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        algorithm: HashAlgorithm,
        hash_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate metadata for hash operation"""
        metadata = {
            "data_type": type(data).__name__,
            "algorithm_strength": self._get_algorithm_strength_score(algorithm),
            "algorithm_secure": self._is_algorithm_secure(algorithm),
            "algorithm_deprecated": self._is_algorithm_deprecated(algorithm),
            "hash_length": len(hash_result["hash"]),
            "generation_timestamp": asyncio.get_event_loop().time()
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
    
    def _get_algorithm_strength_score(self, algorithm: HashAlgorithm) -> int:
        """Get strength score for algorithm"""
        strength_info = self.hash_settings["algorithm_strength_scores"].get(algorithm, {})
        return strength_info.get("score", 5)
    
    def _is_algorithm_secure(self, algorithm: HashAlgorithm) -> bool:
        """Check if algorithm is considered secure"""
        strength_info = self.hash_settings["algorithm_strength_scores"].get(algorithm, {})
        return strength_info.get("secure", False)
    
    def _is_algorithm_deprecated(self, algorithm: HashAlgorithm) -> bool:
        """Check if algorithm is deprecated"""
        strength_info = self.hash_settings["algorithm_strength_scores"].get(algorithm, {})
        return strength_info.get("deprecated", False)
    
    async def _process_hash_generation_queue(self) -> None:
        """Background task to process hash generation queue"""
        try:
            while True:
                # Get next hash generation request
                hash_request = await self.hash_generation_queue.get()
                
                try:
                    # Process hash request (placeholder for future batch processing)
                    logger.debug(f"Processing hash request: {hash_request}")
                    
                except Exception as e:
                    logger.error(f"Failed to process hash request: {e}")
                
                finally:
                    # Mark task as done
                    self.hash_generation_queue.task_done()
                    
        except asyncio.CancelledError:
            logger.info("Hash generation processor cancelled")
        except Exception as e:
            logger.error(f"Hash generation processor error: {e}")
    
    async def get_hash_history(
        self,
        algorithm: Optional[HashAlgorithm] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get hash generation history with optional filtering"""
        history = self.hash_history.copy()
        
        # Filter by algorithm
        if algorithm:
            history = [h for h in history if h.get("algorithm") == algorithm.value]
        
        # Filter by action
        if action:
            history = [h for h in history if h.get("action") == action]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def cleanup_expired_hashes(self) -> int:
        """Clean up expired hashes and return count of cleaned hashes"""
        current_time = asyncio.get_event_loop().time()
        expiry_hours = self.hash_settings["hash_expiry_hours"]
        expired_hashes = []
        
        for hash_id, hash_record in self.generated_hashes.items():
            generated_at = hash_record.get("generated_at", 0)
            if current_time - generated_at > (expiry_hours * 3600):
                expired_hashes.append(hash_id)
        
        # Mark expired hashes
        for hash_id in expired_hashes:
            self.generated_hashes[hash_id]["status"] = HashStatus.EXPIRED.value
            self.generated_hashes[hash_id]["expired_at"] = current_time
        
        if expired_hashes:
            logger.info(f"Marked {len(expired_hashes)} hashes as expired")
        
        return len(expired_hashes)
    
    async def stop_hash_generation_processor(self) -> None:
        """Stop the hash generation processor"""
        if self.generation_processor_task:
            self.generation_processor_task.cancel()
            try:
                await self.generation_processor_task
            except asyncio.CancelledError:
                pass
            self.generation_processor_task = None
            logger.info("Hash generation processor stopped")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the hash generator"""
        return {
            "status": "healthy",
            "supported_algorithms": [alg.value for alg in self.supported_algorithms],
            "generated_hashes_count": len(self.generated_hashes),
            "hash_history_size": len(self.hash_history),
            "hash_generation_queue_size": self.hash_generation_queue.qsize(),
            "generation_processor_running": self.generation_processor_task is not None and not self.generation_processor_task.done(),
            "hash_settings": {
                "default_algorithm": self.hash_settings["default_algorithm"].value,
                "max_data_size_bytes": self.hash_settings["max_hash_size_bytes"],
                "batch_processing_enabled": self.hash_settings["batch_processing_enabled"],
                "collision_detection_enabled": self.hash_settings["collision_detection_enabled"]
            },
            "timestamp": asyncio.get_event_loop().time()
        }
