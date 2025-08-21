"""
Secret Management System

Provides secure storage, retrieval, and management of sensitive configuration
data including API keys, passwords, tokens, and other secrets.
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


@dataclass
class SecretMetadata:
    """Metadata for a stored secret."""
    name: str
    description: str
    created_at: str
    updated_at: str
    expires_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    version: int = 1


class SecretManager:
    """Manages secure storage and retrieval of secrets."""
    
    def __init__(self, 
                 master_key: Optional[str] = None,
                 secrets_file: Optional[str] = None,
                 auto_encrypt: bool = True):
        """
        Initialize the secret manager.
        
        Args:
            master_key: Master encryption key (auto-generated if None)
            secrets_file: Path to encrypted secrets file
            auto_encrypt: Whether to automatically encrypt new secrets
        """
        self.auto_encrypt = auto_encrypt
        self.secrets_file = secrets_file or os.path.join(
            os.path.expanduser("~"), ".aas_engine", "secrets.enc"
        )
        
        # Ensure secrets directory exists
        os.makedirs(os.path.dirname(self.secrets_file), exist_ok=True)
        
        # Initialize encryption
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = self._generate_master_key()
        
        self.fernet = self._create_fernet()
        self._secrets_cache: Dict[str, Any] = {}
        self._metadata_cache: Dict[str, SecretMetadata] = {}
        
        # Load existing secrets
        self._load_secrets()
    
    def _generate_master_key(self) -> bytes:
        """Generate a new master encryption key."""
        return Fernet.generate_key()
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet cipher for encryption/decryption."""
        try:
            return Fernet(self.master_key)
        except Exception as e:
            logger.error(f"Failed to create Fernet cipher: {e}")
            # Fallback to a new key
            self.master_key = self._generate_master_key()
            return Fernet(self.master_key)
    
    def _load_secrets(self):
        """Load encrypted secrets from file."""
        if not os.path.exists(self.secrets_file):
            return
        
        try:
            with open(self.secrets_file, 'rb') as f:
                encrypted_data = f.read()
            
            if encrypted_data:
                decrypted_data = self.fernet.decrypt(encrypted_data)
                data = json.loads(decrypted_data.decode())
                
                self._secrets_cache = data.get('secrets', {})
                metadata_dict = data.get('metadata', {})
                
                # Convert metadata back to objects
                for name, meta_dict in metadata_dict.items():
                    self._metadata_cache[name] = SecretMetadata(**meta_dict)
                    
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            self._secrets_cache = {}
            self._metadata_cache = {}
    
    def _save_secrets(self):
        """Save encrypted secrets to file."""
        try:
            # Convert metadata to dict for serialization
            metadata_dict = {}
            for name, metadata in self._metadata_cache.items():
                metadata_dict[name] = {
                    'name': metadata.name,
                    'description': metadata.description,
                    'created_at': metadata.created_at,
                    'updated_at': metadata.updated_at,
                    'expires_at': metadata.expires_at,
                    'tags': metadata.tags,
                    'version': metadata.version
                }
            
            data = {
                'secrets': self._secrets_cache,
                'metadata': metadata_dict
            }
            
            json_data = json.dumps(data, indent=2)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            logger.error(f"Failed to save secrets: {e}")
            raise
    
    def set_secret(self, 
                   name: str, 
                   value: str, 
                   description: str = "",
                   tags: Optional[List[str]] = None,
                   expires_at: Optional[str] = None) -> bool:
        """
        Store a secret securely.
        
        Args:
            name: Secret name/identifier
            value: Secret value
            description: Description of the secret
            tags: Tags for categorization
            expires_at: Expiration timestamp
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import datetime
            
            now = datetime.datetime.now().isoformat()
            
            # Create or update metadata
            if name in self._metadata_cache:
                metadata = self._metadata_cache[name]
                metadata.updated_at = now
                metadata.description = description or metadata.description
                metadata.tags = tags or metadata.tags
                metadata.expires_at = expires_at
                metadata.version += 1
            else:
                metadata = SecretMetadata(
                    name=name,
                    description=description,
                    created_at=now,
                    updated_at=now,
                    expires_at=expires_at,
                    tags=tags or [],
                    version=1
                )
                self._metadata_cache[name] = metadata
            
            # Store the secret
            self._secrets_cache[name] = value
            
            # Save to file
            self._save_secrets()
            
            logger.info(f"Secret '{name}' stored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store secret '{name}': {e}")
            return False
    
    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret.
        
        Args:
            name: Secret name/identifier
            default: Default value if secret not found
            
        Returns:
            Secret value or default
        """
        try:
            if name not in self._secrets_cache:
                return default
            
            # Check expiration
            metadata = self._metadata_cache.get(name)
            if metadata and metadata.expires_at:
                import datetime
                try:
                    expires_at = datetime.datetime.fromisoformat(metadata.expires_at)
                    if datetime.datetime.now() > expires_at:
                        logger.warning(f"Secret '{name}' has expired")
                        return default
                except ValueError:
                    pass
            
            return self._secrets_cache[name]
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{name}': {e}")
            return default
    
    def delete_secret(self, name: str) -> bool:
        """
        Delete a secret.
        
        Args:
            name: Secret name/identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if name in self._secrets_cache:
                del self._secrets_cache[name]
            
            if name in self._metadata_cache:
                del self._metadata_cache[name]
            
            self._save_secrets()
            logger.info(f"Secret '{name}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret '{name}': {e}")
            return False
    
    def list_secrets(self) -> List[str]:
        """List all secret names."""
        return list(self._secrets_cache.keys())
    
    def get_metadata(self, name: str) -> Optional[SecretMetadata]:
        """Get metadata for a secret."""
        return self._metadata_cache.get(name)
    
    def search_secrets(self, query: str) -> List[str]:
        """Search secrets by name, description, or tags."""
        results = []
        query_lower = query.lower()
        
        for name, metadata in self._metadata_cache.items():
            if (query_lower in name.lower() or 
                query_lower in metadata.description.lower() or
                any(query_lower in tag.lower() for tag in metadata.tags)):
                results.append(name)
        
        return results
    
    def rotate_secret(self, name: str, new_value: str) -> bool:
        """
        Rotate a secret with a new value.
        
        Args:
            name: Secret name/identifier
            new_value: New secret value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if name not in self._secrets_cache:
                return False
            
            # Store the new value
            success = self.set_secret(name, new_value)
            if success:
                logger.info(f"Secret '{name}' rotated successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rotate secret '{name}': {e}")
            return False


class EnvironmentSecretManager:
    """Manages secrets from environment variables."""
    
    def __init__(self, prefix: str = "AAS_ENGINE_"):
        """
        Initialize environment secret manager.
        
        Args:
            prefix: Prefix for environment variable names
        """
        self.prefix = prefix
        self._env_cache: Dict[str, str] = {}
        self._load_environment_secrets()
    
    def _load_environment_secrets(self):
        """Load secrets from environment variables."""
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                secret_name = key[len(self.prefix):].lower()
                self._env_cache[secret_name] = value
    
    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from environment variable.
        
        Args:
            name: Secret name (will be prefixed)
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        env_key = f"{self.prefix}{name.upper()}"
        return os.environ.get(env_key, default)
    
    def set_secret(self, name: str, value: str) -> bool:
        """
        Set secret in environment variable.
        
        Args:
            name: Secret name
            value: Secret value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            env_key = f"{self.prefix}{name.upper()}"
            os.environ[env_key] = value
            self._env_cache[name] = value
            return True
        except Exception as e:
            logger.error(f"Failed to set environment secret '{name}': {e}")
            return False
    
    def list_secrets(self) -> List[str]:
        """List all environment secret names."""
        return list(self._env_cache.keys())
    
    def refresh(self):
        """Refresh environment secrets cache."""
        self._env_cache.clear()
        self._load_environment_secrets()


class SecretValidator:
    """Validates secret strength and compliance."""
    
    @staticmethod
    def validate_password_strength(password: str, 
                                 min_length: int = 8,
                                 require_uppercase: bool = True,
                                 require_lowercase: bool = True,
                                 require_digits: bool = True,
                                 require_special: bool = True) -> Dict[str, Any]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            min_length: Minimum length requirement
            require_uppercase: Require uppercase letters
            require_lowercase: Require lowercase letters
            require_digits: Require digits
            require_special: Require special characters
            
        Returns:
            Validation result with score and details
        """
        result = {
            'valid': True,
            'score': 0,
            'issues': [],
            'strengths': []
        }
        
        # Length check
        if len(password) < min_length:
            result['valid'] = False
            result['issues'].append(f"Password must be at least {min_length} characters")
        else:
            result['score'] += 20
            result['strengths'].append("Good length")
        
        # Character type checks
        if require_uppercase and not any(c.isupper() for c in password):
            result['valid'] = False
            result['issues'].append("Password must contain uppercase letters")
        else:
            result['score'] += 20
        
        if require_lowercase and not any(c.islower() for c in password):
            result['valid'] = False
            result['issues'].append("Password must contain lowercase letters")
        else:
            result['score'] += 20
        
        if require_digits and not any(c.isdigit() for c in password):
            result['valid'] = False
            result['issues'].append("Password must contain digits")
        else:
            result['score'] += 20
        
        if require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            result['valid'] = False
            result['issues'].append("Password must contain special characters")
        else:
            result['score'] += 20
        
        # Additional strength checks
        if len(password) > 12:
            result['score'] += 10
            result['strengths'].append("Very long password")
        
        if len(set(password)) > len(password) * 0.8:
            result['score'] += 10
            result['strengths'].append("Good character variety")
        
        return result
    
    @staticmethod
    def validate_api_key_format(api_key: str, expected_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
            expected_length: Expected length of the key
            
        Returns:
            Validation result
        """
        result = {
            'valid': True,
            'issues': [],
            'strengths': []
        }
        
        if not api_key:
            result['valid'] = False
            result['issues'].append("API key cannot be empty")
            return result
        
        if expected_length and len(api_key) != expected_length:
            result['valid'] = False
            result['issues'].append(f"API key must be {expected_length} characters")
        
        # Check for common weak patterns
        if api_key.lower() in ['test', 'demo', 'example', 'key']:
            result['valid'] = False
            result['issues'].append("API key appears to be a placeholder")
        
        if len(api_key) < 16:
            result['issues'].append("API key is relatively short")
        else:
            result['strengths'].append("Good key length")
        
        return result


# Global secret manager instance
_global_secret_manager: Optional[SecretManager] = None


def get_global_secret_manager() -> SecretManager:
    """Get the global secret manager instance."""
    global _global_secret_manager
    if _global_secret_manager is None:
        _global_secret_manager = SecretManager()
    return _global_secret_manager


def set_global_secret_manager(manager: SecretManager):
    """Set the global secret manager instance."""
    global _global_secret_manager
    _global_secret_manager = manager


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get a secret using the global secret manager."""
    return get_global_secret_manager().get_secret(name, default)


def set_secret(name: str, value: str, **kwargs) -> bool:
    """Set a secret using the global secret manager."""
    return get_global_secret_manager().set_secret(name, value, **kwargs)
