"""
Key Manager for Certificate Manager

Handles cryptographic key management, generation, storage, and lifecycle management.
Provides secure key operations for digital signatures and encryption.
"""

import asyncio
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class KeyType(Enum):
    """Supported key types"""
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"
    ECDSA_P256 = "ECDSA-P256"
    ECDSA_P384 = "ECDSA-P384"
    ECDSA_P521 = "ECDSA-P521"
    ED25519 = "ED25519"
    AES_128 = "AES-128"
    AES_256 = "AES-256"
    HMAC_SHA256 = "HMAC-SHA256"
    HMAC_SHA512 = "HMAC-SHA512"


class KeyStatus(Enum):
    """Key status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    GENERATING = "generating"
    ERROR = "error"


class KeyAlgorithm(Enum):
    """Key algorithm categories"""
    ASYMMETRIC = "asymmetric"  # RSA, ECDSA, Ed25519
    SYMMETRIC = "symmetric"    # AES, HMAC
    HASH = "hash"              # SHA family


class KeyManager:
    """
    Cryptographic key management service
    
    Handles:
    - Key generation and storage
    - Key lifecycle management
    - Key rotation and expiration
    - Key backup and recovery
    - Key access control
    - Key metadata management
    """
    
    def __init__(self):
        """Initialize the key manager"""
        self.supported_key_types = list(KeyType)
        self.key_statuses = list(KeyStatus)
        self.key_algorithms = list(KeyAlgorithm)
        
        # Key storage
        self.active_keys: Dict[str, Dict[str, Any]] = {}
        self.key_history: List[Dict[str, Any]] = []
        self.key_locks: Dict[str, asyncio.Lock] = {}
        
        # Key management settings
        self.key_settings = self._initialize_key_settings()
        
        # Key generation queue
        self.key_generation_queue: asyncio.Queue = asyncio.Queue()
        self.generation_processor_task: Optional[asyncio.Task] = None
        
        # Start key generation processor
        self._start_key_generation_processor()
        
        logger.info("Key Manager initialized successfully")
    
    def _initialize_key_settings(self) -> Dict[str, Any]:
        """Initialize key management settings"""
        return {
            "default_key_expiry_days": 365,
            "key_rotation_threshold_days": 30,
            "max_active_keys_per_type": 5,
            "key_backup_enabled": True,
            "key_encryption_enabled": True,
            "key_strength_requirements": {
                KeyType.RSA_2048: {"min_strength": 6, "recommended": True},
                KeyType.RSA_4096: {"min_strength": 8, "recommended": True},
                KeyType.ECDSA_P256: {"min_strength": 7, "recommended": True},
                KeyType.ECDSA_P384: {"min_strength": 8, "recommended": True},
                KeyType.ECDSA_P521: {"min_strength": 9, "recommended": True},
                KeyType.ED25519: {"min_strength": 9, "recommended": True},
                KeyType.AES_128: {"min_strength": 6, "recommended": False},
                KeyType.AES_256: {"min_strength": 8, "recommended": True},
                KeyType.HMAC_SHA256: {"min_strength": 7, "recommended": True},
                KeyType.HMAC_SHA512: {"min_strength": 8, "recommended": True}
            }
        }
    
    def _start_key_generation_processor(self) -> None:
        """Start the background key generation processor"""
        self.generation_processor_task = asyncio.create_task(self._process_key_generation_queue())
        logger.info("Key generation processor started")
    
    async def generate_key(
        self,
        key_type: KeyType,
        key_name: str,
        purpose: str = "general",
        expiry_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a new cryptographic key
        
        Args:
            key_type: Type of key to generate
            key_name: Human-readable name for the key
            purpose: Purpose of the key (e.g., 'signing', 'encryption')
            expiry_days: Days until key expires (uses default if None)
            metadata: Additional metadata for the key
            
        Returns:
            Dictionary containing key information and metadata
        """
        # Validate key type
        if key_type not in self.supported_key_types:
            raise ValueError(f"Unsupported key type: {key_type}")
        
        # Check key limits
        await self._check_key_limits(key_type)
        
        # Create key generation request
        key_request = {
            "key_type": key_type,
            "key_name": key_name,
            "purpose": purpose,
            "expiry_days": expiry_days or self.key_settings["default_key_expiry_days"],
            "metadata": metadata or {},
            "requested_at": asyncio.get_event_loop().time()
        }
        
        # Add to generation queue
        await self.key_generation_queue.put(key_request)
        
        # Create key record
        key_id = f"key_{key_type.value.lower()}_{secrets.token_hex(8)}"
        key_record = {
            "key_id": key_id,
            "key_type": key_type.value,
            "key_name": key_name,
            "purpose": purpose,
            "status": KeyStatus.PENDING.value,
            "requested_at": key_request["requested_at"],
            "metadata": metadata or {}
        }
        
        # Store key record
        self.active_keys[key_id] = key_record
        
        logger.info(f"Key generation requested: {key_id} ({key_type.value})")
        
        return key_record
    
    async def get_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get key information by ID"""
        return self.active_keys.get(key_id)
    
    async def get_keys_by_type(self, key_type: KeyType) -> List[Dict[str, Any]]:
        """Get all keys of a specific type"""
        return [
            key for key in self.active_keys.values()
            if key.get("key_type") == key_type.value
        ]
    
    async def get_active_keys(self, key_type: Optional[KeyType] = None) -> List[Dict[str, Any]]:
        """Get all active keys, optionally filtered by type"""
        active_keys = [
            key for key in self.active_keys.values()
            if key.get("status") == KeyStatus.ACTIVE.value
        ]
        
        if key_type:
            active_keys = [
                key for key in active_keys
                if key.get("key_type") == key_type.value
            ]
        
        return active_keys
    
    async def revoke_key(self, key_id: str, reason: str = "Administrative action") -> bool:
        """Revoke a key"""
        if key_id in self.active_keys:
            key = self.active_keys[key_id]
            key["status"] = KeyStatus.REVOKED.value
            key["revoked_at"] = asyncio.get_event_loop().time()
            key["revocation_reason"] = reason
            
            # Record in history
            self.key_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "revoke",
                "key_id": key_id,
                "reason": reason
            })
            
            logger.info(f"Key {key_id} revoked: {reason}")
            return True
        
        return False
    
    async def rotate_key(self, key_id: str, new_key_type: Optional[KeyType] = None) -> Dict[str, Any]:
        """Rotate an existing key"""
        if key_id not in self.active_keys:
            raise ValueError(f"Key not found: {key_id}")
        
        existing_key = self.active_keys[key_id]
        
        # Generate new key of same type (or specified type)
        new_key_type = new_key_type or KeyType(existing_key["key_type"])
        
        # Generate new key
        new_key = await self.generate_key(
            key_type=new_key_type,
            key_name=f"{existing_key['key_name']}_rotated",
            purpose=existing_key["purpose"],
            metadata={"rotated_from": key_id}
        )
        
        # Mark old key for rotation
        existing_key["status"] = KeyStatus.INACTIVE.value
        existing_key["rotated_to"] = new_key["key_id"]
        existing_key["rotated_at"] = asyncio.get_event_loop().time()
        
        logger.info(f"Key {key_id} rotated to {new_key['key_id']}")
        
        return new_key
    
    async def backup_key(self, key_id: str, backup_path: Path) -> bool:
        """Backup a key to secure storage"""
        if not self.key_settings["key_backup_enabled"]:
            logger.warning("Key backup is disabled")
            return False
        
        if key_id not in self.active_keys:
            logger.error(f"Key not found: {key_id}")
            return False
        
        try:
            key_data = self.active_keys[key_id]
            
            # Create backup data (in real implementation, this would encrypt the actual key material)
            backup_data = {
                "key_id": key_id,
                "key_type": key_data["key_type"],
                "key_name": key_data["key_name"],
                "purpose": key_data["purpose"],
                "backup_timestamp": asyncio.get_event_loop().time(),
                "backup_version": "1.0"
            }
            
            # Save backup
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Update key record
            key_data["last_backup"] = asyncio.get_event_loop().time()
            key_data["backup_path"] = str(backup_path)
            
            logger.info(f"Key {key_id} backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup key {key_id}: {e}")
            return False
    
    async def restore_key(self, backup_path: Path) -> Optional[Dict[str, Any]]:
        """Restore a key from backup"""
        try:
            # Load backup data
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Validate backup data
            required_fields = ["key_id", "key_type", "key_name", "purpose"]
            for field in required_fields:
                if field not in backup_data:
                    raise ValueError(f"Missing required field in backup: {field}")
            
            # Create key record
            key_record = {
                "key_id": backup_data["key_id"],
                "key_type": backup_data["key_type"],
                "key_name": backup_data["key_name"],
                "purpose": backup_data["purpose"],
                "status": KeyStatus.ACTIVE.value,
                "restored_at": asyncio.get_event_loop().time(),
                "backup_source": str(backup_path),
                "metadata": backup_data.get("metadata", {})
            }
            
            # Store restored key
            self.active_keys[key_record["key_id"]] = key_record
            
            # Record in history
            self.key_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "restore",
                "key_id": key_record["key_id"],
                "backup_source": str(backup_path)
            })
            
            logger.info(f"Key {key_record['key_id']} restored from backup")
            return key_record
            
        except Exception as e:
            logger.error(f"Failed to restore key from {backup_path}: {e}")
            return None
    
    async def get_key_statistics(self) -> Dict[str, Any]:
        """Get key management statistics"""
        total_keys = len(self.active_keys)
        active_keys = len([k for k in self.active_keys.values() if k.get("status") == KeyStatus.ACTIVE.value])
        expired_keys = len([k for k in self.active_keys.values() if k.get("status") == KeyStatus.EXPIRED.value])
        revoked_keys = len([k for k in self.active_keys.values() if k.get("status") == KeyStatus.REVOKED.value])
        
        # Count by type
        keys_by_type = {}
        for key in self.active_keys.values():
            key_type = key.get("key_type", "unknown")
            keys_by_type[key_type] = keys_by_type.get(key_type, 0) + 1
        
        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "expired_keys": expired_keys,
            "revoked_keys": revoked_keys,
            "keys_by_type": keys_by_type,
            "key_generation_queue_size": self.key_generation_queue.qsize(),
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def _check_key_limits(self, key_type: KeyType) -> None:
        """Check if key generation is within limits"""
        max_keys = self.key_settings["max_active_keys_per_type"]
        active_keys_of_type = await self.get_active_keys(key_type)
        
        if len(active_keys_of_type) >= max_keys:
            raise ValueError(f"Maximum active keys of type {key_type.value} reached ({max_keys})")
    
    async def _process_key_generation_queue(self) -> None:
        """Background task to process key generation queue"""
        try:
            while True:
                # Get next key generation request
                key_request = await self.key_generation_queue.get()
                
                try:
                    await self._generate_single_key(key_request)
                except Exception as e:
                    logger.error(f"Failed to generate key: {e}")
                    # Update key status to error
                    key_id = f"key_{key_request['key_type'].value.lower()}_{secrets.token_hex(8)}"
                    if key_id in self.active_keys:
                        self.active_keys[key_id]["status"] = KeyStatus.ERROR.value
                        self.active_keys[key_id]["error"] = str(e)
                
                finally:
                    # Mark task as done
                    self.key_generation_queue.task_done()
                    
        except asyncio.CancelledError:
            logger.info("Key generation processor cancelled")
        except Exception as e:
            logger.error(f"Key generation processor error: {e}")
    
    async def _generate_single_key(self, key_request: Dict[str, Any]) -> None:
        """Generate a single key based on request"""
        key_type = key_request["key_type"]
        key_name = key_request["key_name"]
        purpose = key_request["purpose"]
        expiry_days = key_request["expiry_days"]
        metadata = key_request["metadata"]
        
        # Find the key record for this request
        key_id = None
        for kid, key in self.active_keys.items():
            if (key.get("key_name") == key_name and 
                key.get("key_type") == key_type.value and
                key.get("status") == KeyStatus.PENDING.value):
                key_id = kid
                break
        
        if not key_id:
            logger.error(f"Key record not found for generation request: {key_name}")
            return
        
        try:
            # Update status to generating
            self.active_keys[key_id]["status"] = KeyStatus.GENERATING.value
            
            # Generate key material (simulated)
            key_material = await self._generate_key_material(key_type)
            
            # Calculate expiry
            expiry_date = datetime.utcnow() + timedelta(days=expiry_days)
            
            # Update key record
            self.active_keys[key_id].update({
                "status": KeyStatus.ACTIVE.value,
                "key_material": key_material,
                "generated_at": asyncio.get_event_loop().time(),
                "expires_at": expiry_date.isoformat(),
                "expiry_timestamp": expiry_date.timestamp(),
                "key_fingerprint": await self._generate_key_fingerprint(key_material),
                "algorithm": self._get_key_algorithm(key_type),
                "strength_score": self._get_key_strength_score(key_type)
            })
            
            # Record in history
            self.key_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "generate",
                "key_id": key_id,
                "key_type": key_type.value,
                "purpose": purpose
            })
            
            logger.info(f"Key {key_id} generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate key {key_id}: {e}")
            self.active_keys[key_id]["status"] = KeyStatus.ERROR.value
            self.active_keys[key_id]["error"] = str(e)
            raise
    
    async def _generate_key_material(self, key_type: KeyType) -> str:
        """Generate key material (simulated)"""
        # In a real implementation, this would generate actual cryptographic keys
        if key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
            key_size = int(key_type.value.split("-")[1])
            return f"RSA_PRIVATE_KEY_{key_size}_{secrets.token_hex(32)}"
        elif key_type in [KeyType.ECDSA_P256, KeyType.ECDSA_P384, KeyType.ECDSA_P521]:
            curve = key_type.value.split("-")[1]
            return f"ECDSA_PRIVATE_KEY_{curve}_{secrets.token_hex(32)}"
        elif key_type == KeyType.ED25519:
            return f"ED25519_PRIVATE_KEY_{secrets.token_hex(32)}"
        elif key_type in [KeyType.AES_128, KeyType.AES_256]:
            key_size = int(key_type.value.split("-")[1])
            return f"AES_KEY_{key_size}_{secrets.token_hex(key_size // 8)}"
        elif key_type in [KeyType.HMAC_SHA256, KeyType.HMAC_SHA512]:
            hash_type = key_type.value.split("-")[1]
            return f"HMAC_KEY_{hash_type}_{secrets.token_hex(32)}"
        else:
            return f"GENERIC_KEY_{secrets.token_hex(32)}"
    
    async def _generate_key_fingerprint(self, key_material: str) -> str:
        """Generate key fingerprint"""
        return hashlib.sha256(key_material.encode()).hexdigest()[:16]
    
    def _get_key_algorithm(self, key_type: KeyType) -> str:
        """Get algorithm category for key type"""
        if key_type in [KeyType.RSA_2048, KeyType.RSA_4096, KeyType.ECDSA_P256, KeyType.ECDSA_P384, KeyType.ECDSA_P521, KeyType.ED25519]:
            return KeyAlgorithm.ASYMMETRIC.value
        elif key_type in [KeyType.AES_128, KeyType.AES_256, KeyType.HMAC_SHA256, KeyType.HMAC_SHA512]:
            return KeyAlgorithm.SYMMETRIC.value
        else:
            return KeyAlgorithm.HASH.value
    
    def _get_key_strength_score(self, key_type: KeyType) -> int:
        """Get cryptographic strength score for key type"""
        strength_info = self.key_settings["key_strength_requirements"].get(key_type, {})
        return strength_info.get("min_strength", 5)
    
    async def cleanup_expired_keys(self) -> int:
        """Clean up expired keys and return count of cleaned keys"""
        current_time = asyncio.get_event_loop().time()
        expired_keys = []
        
        for key_id, key in self.active_keys.items():
            expiry_timestamp = key.get("expiry_timestamp")
            if expiry_timestamp and current_time > expiry_timestamp:
                expired_keys.append(key_id)
        
        # Mark expired keys
        for key_id in expired_keys:
            self.active_keys[key_id]["status"] = KeyStatus.EXPIRED.value
            self.active_keys[key_id]["expired_at"] = current_time
        
        if expired_keys:
            logger.info(f"Marked {len(expired_keys)} keys as expired")
        
        return len(expired_keys)
    
    async def get_key_history(
        self,
        key_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get key management history with optional filtering"""
        history = self.key_history.copy()
        
        # Filter by key ID
        if key_id:
            history = [h for h in history if h.get("key_id") == key_id]
        
        # Filter by action
        if action:
            history = [h for h in history if h.get("action") == action]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def stop_key_generation_processor(self) -> None:
        """Stop the key generation processor"""
        if self.generation_processor_task:
            self.generation_processor_task.cancel()
            try:
                await self.generation_processor_task
            except asyncio.CancelledError:
                pass
            self.generation_processor_task = None
            logger.info("Key generation processor stopped")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the key manager"""
        return {
            "status": "healthy",
            "supported_key_types": [kt.value for kt in self.supported_key_types],
            "active_keys_count": len(self.active_keys),
            "key_history_size": len(self.key_history),
            "key_generation_queue_size": self.key_generation_queue.qsize(),
            "generation_processor_running": self.generation_processor_task is not None and not self.generation_processor_task.done(),
            "key_settings": {
                "backup_enabled": self.key_settings["key_backup_enabled"],
                "encryption_enabled": self.key_settings["key_encryption_enabled"],
                "default_expiry_days": self.key_settings["default_key_expiry_days"]
            },
            "timestamp": asyncio.get_event_loop().time()
        }
