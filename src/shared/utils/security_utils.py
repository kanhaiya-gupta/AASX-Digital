"""
Security Utilities
================

Security and encryption utilities for the AAS Data Modeling framework.
"""

import hashlib
import hmac
import secrets
import base64
import os
from typing import Optional, Tuple, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Utility class for security operations."""
    
    # Default encryption settings
    DEFAULT_KEY_LENGTH = 32  # 256 bits
    DEFAULT_SALT_LENGTH = 16
    DEFAULT_ITERATIONS = 100000
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            logger.error(f"Error generating secure token: {e}")
            raise
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a cryptographically secure password."""
        try:
            # Use a mix of characters for better security
            alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
            return ''.join(secrets.choice(alphabet) for _ in range(length))
        except Exception as e:
            logger.error(f"Error generating secure password: {e}")
            raise
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, bytes]:
        """Hash a password using PBKDF2 with a random salt."""
        try:
            if salt is None:
                salt = os.urandom(SecurityUtils.DEFAULT_SALT_LENGTH)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=SecurityUtils.DEFAULT_KEY_LENGTH,
                salt=salt,
                iterations=SecurityUtils.DEFAULT_ITERATIONS,
                backend=default_backend()
            )
            
            key = kdf.derive(password.encode('utf-8'))
            return base64.b64encode(key).decode('utf-8'), salt
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: bytes) -> bool:
        """Verify a password against its hash."""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=SecurityUtils.DEFAULT_KEY_LENGTH,
                salt=salt,
                iterations=SecurityUtils.DEFAULT_ITERATIONS,
                backend=default_backend()
            )
            
            key = kdf.derive(password.encode('utf-8'))
            return hmac.compare_digest(
                base64.b64encode(key).decode('utf-8'),
                hashed_password
            )
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def generate_encryption_key() -> bytes:
        """Generate a new encryption key."""
        try:
            return Fernet.generate_key()
        except Exception as e:
            logger.error(f"Error generating encryption key: {e}")
            raise
    
    @staticmethod
    def encrypt_data(data: str, key: bytes) -> str:
        """Encrypt data using Fernet symmetric encryption."""
        try:
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: bytes) -> str:
        """Decrypt data using Fernet symmetric encryption."""
        try:
            fernet = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    @staticmethod
    def encrypt_file(file_path: str, key: bytes, output_path: Optional[str] = None) -> str:
        """Encrypt a file using AES-256-CBC."""
        try:
            if output_path is None:
                output_path = file_path + '.encrypted'
            
            # Generate a random IV
            iv = os.urandom(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            with open(file_path, 'rb') as infile:
                with open(output_path, 'wb') as outfile:
                    # Write IV at the beginning
                    outfile.write(iv)
                    
                    # Read and encrypt data in chunks
                    while True:
                        chunk = infile.read(1024)
                        if not chunk:
                            break
                        
                        # Pad the last chunk if necessary
                        if len(chunk) % 16 != 0:
                            chunk += b'\0' * (16 - len(chunk) % 16)
                        
                        encrypted_chunk = encryptor.update(chunk)
                        outfile.write(encrypted_chunk)
                    
                    # Finalize encryption
                    outfile.write(encryptor.finalize())
            
            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error encrypting file {file_path}: {e}")
            raise
    
    @staticmethod
    def decrypt_file(encrypted_file_path: str, key: bytes, output_path: Optional[str] = None) -> str:
        """Decrypt a file using AES-256-CBC."""
        try:
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '.decrypted')
            
            with open(encrypted_file_path, 'rb') as infile:
                # Read IV from the beginning
                iv = infile.read(16)
                
                # Create cipher
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.CBC(iv),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                
                with open(output_path, 'wb') as outfile:
                    # Read and decrypt data in chunks
                    while True:
                        chunk = infile.read(1024)
                        if not chunk:
                            break
                        
                        decrypted_chunk = decryptor.update(chunk)
                        outfile.write(decrypted_chunk)
                    
                    # Finalize decryption
                    final_chunk = decryptor.finalize()
                    outfile.write(final_chunk)
            
            logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error decrypting file {encrypted_file_path}: {e}")
            raise
    
    @staticmethod
    def generate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """Generate a hash of a file."""
        try:
            hash_func = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Error generating file hash for {file_path}: {e}")
            raise
    
    @staticmethod
    def verify_file_integrity(file_path: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """Verify file integrity by comparing with expected hash."""
        try:
            actual_hash = SecurityUtils.generate_file_hash(file_path, algorithm)
            return hmac.compare_digest(actual_hash, expected_hash)
        except Exception as e:
            logger.error(f"Error verifying file integrity for {file_path}: {e}")
            return False
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key."""
        try:
            return secrets.token_urlsafe(32)
        except Exception as e:
            logger.error(f"Error generating API key: {e}")
            raise
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token."""
        try:
            return secrets.token_urlsafe(48)
        except Exception as e:
            logger.error(f"Error generating session token: {e}")
            raise
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not isinstance(input_string, str):
            return ""
        
        # Remove null bytes
        sanitized = input_string.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\t')
        
        # Limit length
        if len(sanitized) > 10000:  # Reasonable limit
            sanitized = sanitized[:10000]
        
        return sanitized
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format."""
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Check length (should be at least 32 characters)
        if len(api_key) < 32:
            return False
        
        # Check if it contains only valid characters
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        return all(char in valid_chars for char in api_key)
    
    @staticmethod
    def create_hmac_signature(data: str, secret_key: str) -> str:
        """Create HMAC signature for data integrity."""
        try:
            signature = hmac.new(
                secret_key.encode('utf-8'),
                data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"Error creating HMAC signature: {e}")
            raise
    
    @staticmethod
    def verify_hmac_signature(data: str, signature: str, secret_key: str) -> bool:
        """Verify HMAC signature."""
        try:
            expected_signature = SecurityUtils.create_hmac_signature(data, secret_key)
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying HMAC signature: {e}")
            return False
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = '*') -> str:
        """Mask sensitive data for logging."""
        if not data or len(data) < 4:
            return mask_char * len(data) if data else ""
        
        return data[:2] + mask_char * (len(data) - 4) + data[-2:]
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate a secure filename to prevent path traversal attacks."""
        import re
        
        # Remove path separators and other dangerous characters
        safe_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', original_filename)
        
        # Remove leading/trailing dots and spaces
        safe_filename = safe_filename.strip('. ')
        
        # Limit length
        if len(safe_filename) > 255:
            safe_filename = safe_filename[:255]
        
        # Add random suffix to prevent conflicts
        random_suffix = secrets.token_hex(4)
        name, ext = os.path.splitext(safe_filename)
        return f"{name}_{random_suffix}{ext}"
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """Check password strength and return detailed analysis."""
        analysis = {
            'score': 0,
            'length': len(password),
            'has_uppercase': False,
            'has_lowercase': False,
            'has_digits': False,
            'has_special': False,
            'is_common': False,
            'feedback': []
        }
        
        if len(password) < 8:
            analysis['feedback'].append("Password should be at least 8 characters long")
        else:
            analysis['score'] += 1
        
        if len(password) >= 12:
            analysis['score'] += 1
        
        if any(c.isupper() for c in password):
            analysis['has_uppercase'] = True
            analysis['score'] += 1
        else:
            analysis['feedback'].append("Password should contain uppercase letters")
        
        if any(c.islower() for c in password):
            analysis['has_lowercase'] = True
            analysis['score'] += 1
        else:
            analysis['feedback'].append("Password should contain lowercase letters")
        
        if any(c.isdigit() for c in password):
            analysis['has_digits'] = True
            analysis['score'] += 1
        else:
            analysis['feedback'].append("Password should contain numbers")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in password):
            analysis['has_special'] = True
            analysis['score'] += 1
        else:
            analysis['feedback'].append("Password should contain special characters")
        
        # Check for common patterns
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            analysis['is_common'] = True
            analysis['score'] = max(0, analysis['score'] - 2)
            analysis['feedback'].append("Password is too common")
        
        return analysis 