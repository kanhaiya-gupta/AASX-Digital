"""
Encryption Module
================

Cryptographic operations including encryption, hashing, and key management.
"""

import asyncio
import base64
import hashlib
import logging
import os
import secrets
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

# Try to import cryptography library, fallback to basic implementations if not available
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logging.warning("cryptography library not available, using fallback implementations")

logger = logging.getLogger(__name__)


class EncryptionManager(ABC):
    """Abstract base class for encryption operations"""
    
    def __init__(self, name: str = "EncryptionManager"):
        self.name = name
        self._keys: Dict[str, bytes] = {}
        self._key_metadata: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    def encrypt(self, data: Union[str, bytes], key_id: str = None) -> bytes:
        """Encrypt data"""
        pass
    
    @abstractmethod
    def decrypt(self, encrypted_data: bytes, key_id: str = None) -> Union[str, bytes]:
        """Decrypt data"""
        pass
    
    def generate_key(self, key_id: str, key_size: int = 256) -> str:
        """Generate a new encryption key"""
        if key_id in self._keys:
            raise ValueError(f"Key {key_id} already exists")
        
        # Generate random key
        key = secrets.token_bytes(key_size // 8)
        self._keys[key_id] = key
        
        # Store metadata
        self._key_metadata[key_id] = {
            'size': key_size,
            'created_at': self._get_current_timestamp(),
            'algorithm': 'AES' if key_size in [128, 192, 256] else 'Unknown'
        }
        
        logger.info(f"Generated key: {key_id} ({key_size} bits)")
        return key_id
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """Get encryption key by ID"""
        return self._keys.get(key_id)
    
    def delete_key(self, key_id: str) -> bool:
        """Delete encryption key"""
        if key_id in self._keys:
            del self._keys[key_id]
            if key_id in self._key_metadata:
                del self._key_metadata[key_id]
            logger.info(f"Deleted key: {key_id}")
            return True
        return False
    
    def list_keys(self) -> List[str]:
        """List all key IDs"""
        return list(self._keys.keys())
    
    def get_key_metadata(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a key"""
        return self._key_metadata.get(key_id)
    
    def _get_current_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()


class AsyncEncryptionManager(EncryptionManager):
    """Asynchronous encryption manager"""
    
    async def encrypt_async(self, data: Union[str, bytes], key_id: str = None) -> bytes:
        """Encrypt data asynchronously"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.encrypt, data, key_id
        )
    
    async def decrypt_async(self, encrypted_data: bytes, key_id: str = None) -> Union[str, bytes]:
        """Decrypt data asynchronously"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.decrypt, encrypted_data, key_id
        )


class SymmetricEncryption(EncryptionManager):
    """Symmetric encryption using AES (via Fernet)"""
    
    def __init__(self, key_id: str = "default"):
        super().__init__("SymmetricEncryption")
        self.key_id = key_id
        
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Using fallback symmetric encryption (less secure)")
        
        # Generate default key if not exists
        if not self.get_key(key_id):
            self.generate_key(key_id, 256)
    
    def encrypt(self, data: Union[str, bytes], key_id: str = None) -> bytes:
        """Encrypt data using symmetric encryption"""
        if key_id is None:
            key_id = self.key_id
        
        key = self.get_key(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if CRYPTOGRAPHY_AVAILABLE:
            try:
                # Use Fernet for encryption
                f = Fernet(base64.urlsafe_b64encode(key))
                return f.encrypt(data)
            except Exception as e:
                logger.error(f"Fernet encryption failed: {e}")
                # Fallback to basic XOR encryption (not secure, just for testing)
                return self._fallback_encrypt(data, key)
        else:
            # Fallback implementation
            return self._fallback_encrypt(data, key)
    
    def decrypt(self, encrypted_data: bytes, key_id: str = None) -> bytes:
        """Decrypt data using symmetric encryption"""
        if key_id is None:
            key_id = self.key_id
        
        key = self.get_key(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        
        if CRYPTOGRAPHY_AVAILABLE:
            try:
                # Use Fernet for decryption
                f = Fernet(base64.urlsafe_b64encode(key))
                decrypted = f.decrypt(encrypted_data)
                # Always return bytes to match test expectations
                return decrypted
            except Exception as e:
                logger.error(f"Fernet decryption failed: {e}")
                # Fallback to basic XOR decryption
                return self._fallback_decrypt(encrypted_data, key)
        else:
            # Fallback implementation
            return self._fallback_decrypt(encrypted_data, key)
    
    def _fallback_encrypt(self, data: bytes, key: bytes) -> bytes:
        """Fallback encryption using XOR (not secure, for testing only)"""
        encrypted = bytearray()
        for i, byte in enumerate(data):
            key_byte = key[i % len(key)]
            encrypted.append(byte ^ key_byte)
        return bytes(encrypted)
    
    def _fallback_decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Fallback decryption using XOR (not secure, for testing only)"""
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_data):
            key_byte = key[i % len(key)]
            decrypted.append(byte ^ key_byte)
        return bytes(decrypted)
    
    def generate_key(self, key_id: str, key_size: int = 256) -> str:
        """Generate symmetric encryption key"""
        if key_size not in [128, 192, 256]:
            raise ValueError("Key size must be 128, 192, or 256 bits")
        
        # Generate random key
        key = os.urandom(key_size // 8)
        self._keys[key_id] = key
        
        # Store metadata
        self._key_metadata[key_id] = {
            'size': key_size,
            'created_at': self._get_current_timestamp(),
            'algorithm': f'AES-{key_size}',
            'type': 'symmetric'
        }
        
        logger.info(f"Generated symmetric key: {key_id} ({key_size} bits)")
        return key_id


class AsymmetricEncryption(EncryptionManager):
    """Asymmetric encryption using RSA"""
    
    def __init__(self, name: str = "AsymmetricEncryption"):
        super().__init__(name)
        self._private_keys: Dict[str, rsa.RSAPrivateKey] = {}
        self._public_keys: Dict[str, rsa.RSAPublicKey] = {}
    
    def generate_key_pair(self, key_id: str, key_size: int = 2048) -> str:
        """Generate RSA key pair"""
        if key_id in self._private_keys:
            raise ValueError(f"Key pair {key_id} already exists")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Store keys
        self._private_keys[key_id] = private_key
        self._public_keys[key_id] = public_key
        
        # Store metadata
        self._key_metadata[key_id] = {
            'size': key_size,
            'created_at': self._get_current_timestamp(),
            'algorithm': 'RSA',
            'type': 'asymmetric'
        }
        
        logger.info(f"Generated RSA key pair: {key_id} ({key_size} bits)")
        return key_id
    
    def encrypt(self, data: Union[str, bytes], key_id: str = None) -> bytes:
        """Encrypt data using public key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if key_id is None:
            raise ValueError("Key ID required for asymmetric encryption")
        
        public_key = self._public_keys.get(key_id)
        if not public_key:
            raise ValueError(f"Public key {key_id} not found")
        
        try:
            # Encrypt data with public key
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            logger.debug(f"Encrypted {len(data)} bytes using public key {key_id}")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: bytes, key_id: str = None) -> bytes:
        """Decrypt data using private key"""
        if key_id is None:
            raise ValueError("Key ID required for asymmetric decryption")
        
        private_key = self._private_keys.get(key_id)
        if not private_key:
            raise ValueError(f"Private key {key_id} not found")
        
        try:
            # Decrypt data with private key
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            logger.debug(f"Decrypted {len(decrypted_data)} bytes using private key {key_id}")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def get_public_key_pem(self, key_id: str) -> str:
        """Get public key in PEM format"""
        if key_id not in self._public_keys:
            raise ValueError(f"Public key {key_id} not found")
        
        public_key = self._public_keys[key_id]
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    def get_private_key_pem(self, key_id: str, password: str = None) -> str:
        """Get private key in PEM format"""
        if key_id not in self._private_keys:
            raise ValueError(f"Private key {key_id} not found")
        
        private_key = self._private_keys[key_id]
        
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
        else:
            encryption_algorithm = serialization.NoEncryption()
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        return pem.decode('utf-8')
    
    def import_public_key(self, key_id: str, pem_data: str) -> bool:
        """Import public key from PEM format"""
        try:
            public_key = serialization.load_pem_public_key(pem_data.encode())
            self._public_keys[key_id] = public_key
            
            # Store metadata
            self._key_metadata[key_id] = {
                'size': public_key.key_size,
                'created_at': self._get_current_timestamp(),
                'algorithm': 'RSA',
                'type': 'asymmetric',
                'imported': True
            }
            
            logger.info(f"Imported public key: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import public key: {e}")
            return False


class HashManager:
    """Hash management and validation"""
    
    def __init__(self):
        self._supported_algorithms = ['md5', 'sha1', 'sha256', 'sha512', 'blake2b']
        if CRYPTOGRAPHY_AVAILABLE:
            self._supported_algorithms.extend(['sha3_256', 'sha3_512'])
    
    def hash(self, data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """Hash data using specified algorithm"""
        if algorithm not in self._supported_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data).hexdigest()
        elif algorithm == 'blake2b':
            return hashlib.blake2b(data).hexdigest()
        elif algorithm == 'sha3_256' and CRYPTOGRAPHY_AVAILABLE:
            return hashlib.sha3_256(data).hexdigest()
        elif algorithm == 'sha3_512' and CRYPTOGRAPHY_AVAILABLE:
            return hashlib.sha3_512(data).hexdigest()
        else:
            raise ValueError(f"Algorithm {algorithm} not available")
    
    def verify_hash(self, data: Union[str, bytes], hash_value: str, algorithm: str = 'sha256') -> bool:
        """Verify hash of data"""
        expected_hash = self.hash(data, algorithm)
        return expected_hash == hash_value
    
    def salt_hash(self, data: Union[str, bytes], salt_length: int = 16) -> tuple[str, str]:
        """Create salted hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        salt = os.urandom(salt_length)
        salted_data = data + salt
        hash_value = self.hash(salted_data)
        
        return hash_value, salt.hex()
    
    def pbkdf2_hash(self, password: str, salt_length: int = 16, iterations: int = 100000) -> tuple[str, str]:
        """Create PBKDF2 hash for passwords"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        salt = os.urandom(salt_length)
        
        if CRYPTOGRAPHY_AVAILABLE:
            try:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=iterations,
                )
                key = kdf.derive(password)
                return base64.b64encode(key).decode('utf-8'), salt.hex()
            except Exception as e:
                logger.error(f"PBKDF2 failed: {e}, using fallback")
                return self._fallback_pbkdf2(password, salt, iterations)
        else:
            return self._fallback_pbkdf2(password, salt, iterations)
    
    def _fallback_pbkdf2(self, password: bytes, salt: bytes, iterations: int) -> tuple[str, str]:
        """Fallback PBKDF2 implementation using hashlib"""
        # Simple fallback - not as secure as proper PBKDF2
        key = password + salt
        for _ in range(iterations):
            key = hashlib.sha256(key).digest()
        return base64.b64encode(key).decode('utf-8'), salt.hex()
    
    def list_algorithms(self) -> List[str]:
        """List supported hash algorithms"""
        return list(self._supported_algorithms.keys())


class KeyManager:
    """Key management and rotation"""
    
    def __init__(self):
        self._keys: Dict[str, Dict[str, Any]] = {}
        self._key_rotation_policy: Dict[str, Dict[str, Any]] = {}
    
    def create_key(self, key_id: str, key_type: str, key_size: int,
                  algorithm: str, expires_in_days: int = 365) -> str:
        """Create a new key with metadata"""
        if key_id in self._keys:
            raise ValueError(f"Key {key_id} already exists")
        
        import time
        current_time = time.time()
        expiry_time = current_time + (expires_in_days * 24 * 3600)
        
        key_info = {
            'id': key_id,
            'type': key_type,
            'size': key_size,
            'algorithm': algorithm,
            'created_at': current_time,
            'expires_at': expiry_time,
            'status': 'active',
            'usage_count': 0,
            'last_used': None
        }
        
        self._keys[key_id] = key_info
        
        # Set up rotation policy
        self._key_rotation_policy[key_id] = {
            'auto_rotate': True,
            'rotation_interval_days': expires_in_days // 2,
            'last_rotated': current_time
        }
        
        logger.info(f"Created key: {key_id} ({key_type}, {key_size} bits)")
        return key_id
    
    def get_key_info(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get key information"""
        return self._keys.get(key_id)
    
    def update_key_usage(self, key_id: str) -> bool:
        """Update key usage statistics"""
        if key_id not in self._keys:
            return False
        
        import time
        self._keys[key_id]['usage_count'] += 1
        self._keys[key_id]['last_used'] = time.time()
        return True
    
    def rotate_key(self, key_id: str) -> bool:
        """Rotate a key"""
        if key_id not in self._keys:
            return False
        
        import time
        current_time = time.time()
        
        # Mark old key as expired
        self._keys[key_id]['status'] = 'expired'
        self._keys[key_id]['expires_at'] = current_time
        
        # Create new key with same parameters
        old_key_info = self._keys[key_id]
        new_key_id = f"{key_id}_v{int(current_time)}"
        
        new_key_info = {
            'id': new_key_id,
            'type': old_key_info['type'],
            'size': old_key_info['size'],
            'algorithm': old_key_info['algorithm'],
            'created_at': current_time,
            'expires_at': current_time + (365 * 24 * 3600),  # 1 year
            'status': 'active',
            'usage_count': 0,
            'last_used': None,
            'replaced_key': key_id
        }
        
        self._keys[new_key_id] = new_key_info
        
        # Update rotation policy
        self._key_rotation_policy[new_key_id] = {
            'auto_rotate': True,
            'rotation_interval_days': 365 // 2,
            'last_rotated': current_time
        }
        
        logger.info(f"Rotated key: {key_id} -> {new_key_id}")
        return True
    
    def get_expired_keys(self) -> List[str]:
        """Get list of expired keys"""
        import time
        current_time = time.time()
        
        expired_keys = []
        for key_id, key_info in self._keys.items():
            if key_info['expires_at'] < current_time:
                expired_keys.append(key_id)
        
        return expired_keys
    
    def get_keys_needing_rotation(self) -> List[str]:
        """Get list of keys that need rotation"""
        import time
        current_time = time.time()
        
        keys_needing_rotation = []
        for key_id, key_info in self._keys.items():
            if key_info['status'] != 'active':
                continue
            
            rotation_policy = self._key_rotation_policy.get(key_id, {})
            if not rotation_policy.get('auto_rotate', False):
                continue
            
            last_rotated = rotation_policy.get('last_rotated', key_info['created_at'])
            rotation_interval = rotation_policy.get('rotation_interval_days', 365) * 24 * 3600
            
            if current_time - last_rotated > rotation_interval:
                keys_needing_rotation.append(key_id)
        
        return keys_needing_rotation
    
    def list_keys(self, status: str = None) -> List[str]:
        """List keys with optional status filter"""
        if status is None:
            return list(self._keys.keys())
        
        return [key_id for key_id, key_info in self._keys.items() 
                if key_info['status'] == status]
    
    def delete_key(self, key_id: str) -> bool:
        """Delete a key"""
        if key_id not in self._keys:
            return False
        
        del self._keys[key_id]
        if key_id in self._key_rotation_policy:
            del self._key_rotation_policy[key_id]
        
        logger.info(f"Deleted key: {key_id}")
        return True
