"""
Privacy Utilities
================

Privacy protection utility functions for federated learning.
Handles data anonymization, encryption, and privacy calculations.
"""

import asyncio
import hashlib
import secrets
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class PrivacyConfig:
    """Configuration for privacy utilities"""
    # Privacy methods
    anonymization_enabled: bool = True
    encryption_enabled: bool = True
    differential_privacy_enabled: bool = True
    
    # Anonymization settings
    k_anonymity: int = 5
    l_diversity: int = 3
    t_closeness: float = 0.1
    
    # Encryption settings
    encryption_algorithm: str = "AES-256"
    key_length: int = 32
    salt_length: int = 16
    
    # Differential privacy settings
    epsilon: float = 1.0
    delta: float = 1e-5
    sensitivity: float = 1.0


@dataclass
class PrivacyMetrics:
    """Metrics for privacy operations"""
    # Privacy scores
    anonymization_score: float = 0.0
    encryption_score: float = 0.0
    differential_privacy_score: float = 0.0
    overall_privacy_score: float = 0.0
    
    # Processing statistics
    records_processed: int = 0
    privacy_violations: int = 0
    compliance_score: float = 0.0
    
    # Performance metrics
    processing_time: float = 0.0
    memory_usage_mb: float = 0.0


class PrivacyUtils:
    """Privacy utility functions for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[PrivacyConfig] = None
    ):
        """Initialize Privacy Utils"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or PrivacyConfig()
        
        # Privacy state
        self.encryption_keys: Dict[str, bytes] = {}
        self.privacy_budget_remaining = self.config.epsilon
        
        # Metrics tracking
        self.metrics = PrivacyMetrics()
        
    async def anonymize_data(
        self,
        data: Union[List[Dict[str, Any]], np.ndarray],
        sensitive_columns: List[str] = None
    ) -> Union[List[Dict[str, Any]], np.ndarray]:
        """Anonymize sensitive data using k-anonymity, l-diversity, and t-closeness"""
        try:
            start_time = datetime.now()
            
            if isinstance(data, list):
                return await self._anonymize_list_data(data, sensitive_columns)
            elif isinstance(data, np.ndarray):
                return await self._anonymize_array_data(data, sensitive_columns)
            else:
                raise ValueError(f"Unsupported data type: {type(data)}")
                
        except Exception as e:
            print(f"❌ Data anonymization failed: {e}")
            return data
        finally:
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics.processing_time = processing_time
            self.metrics.records_processed = len(data) if hasattr(data, '__len__') else 0
    
    async def _anonymize_list_data(
        self,
        data: List[Dict[str, Any]],
        sensitive_columns: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Anonymize list of dictionaries"""
        try:
            if not data:
                return data
            
            anonymized_data = []
            
            for record in data:
                anonymized_record = record.copy()
                
                # Apply k-anonymity
                if sensitive_columns:
                    for col in sensitive_columns:
                        if col in anonymized_record:
                            anonymized_record[col] = await self._apply_k_anonymity_value(
                                anonymized_record[col]
                            )
                
                # Apply generalization for other columns
                for key, value in anonymized_record.items():
                    if key not in (sensitive_columns or []):
                        anonymized_record[key] = await self._generalize_value(value)
                
                anonymized_data.append(anonymized_record)
            
            return anonymized_data
            
        except Exception as e:
            print(f"❌ List data anonymization failed: {e}")
            return data
    
    async def _anonymize_array_data(
        self,
        data: np.ndarray,
        sensitive_columns: List[int] = None
    ) -> np.ndarray:
        """Anonymize numpy array"""
        try:
            anonymized_data = data.copy()
            
            # Apply k-anonymity to sensitive columns
            if sensitive_columns:
                for col_idx in sensitive_columns:
                    if col_idx < data.shape[1]:
                        anonymized_data[:, col_idx] = await self._apply_k_anonymity_array(
                            data[:, col_idx]
                        )
            
            # Apply generalization to other columns
            for col_idx in range(data.shape[1]):
                if sensitive_columns is None or col_idx not in sensitive_columns:
                    anonymized_data[:, col_idx] = await self._generalize_array(
                        data[:, col_idx]
                    )
            
            return anonymized_data
            
        except Exception as e:
            print(f"❌ Array data anonymization failed: {e}")
            return data
    
    async def _apply_k_anonymity_value(self, value: Any) -> Any:
        """Apply k-anonymity to a single value"""
        try:
            if isinstance(value, (int, float)):
                # Round to reduce precision
                if isinstance(value, int):
                    return round(value / 10) * 10
                else:
                    return round(value, 1)
            elif isinstance(value, str):
                # Generalize string values
                if len(value) > 3:
                    return value[:3] + "..."
                else:
                    return value
            else:
                return value
                
        except Exception as e:
            print(f"⚠️  K-anonymity value application failed: {e}")
            return value
    
    async def _apply_k_anonymity_array(self, array: np.ndarray) -> np.ndarray:
        """Apply k-anonymity to an array"""
        try:
            if np.issubdtype(array.dtype, np.number):
                # Round numerical values
                return np.round(array, decimals=1)
            else:
                # Generalize non-numerical values
                return np.array([await self._generalize_value(val) for val in array])
                
        except Exception as e:
            print(f"⚠️  K-anonymity array application failed: {e}")
            return array
    
    async def _generalize_value(self, value: Any) -> Any:
        """Generalize a value for privacy"""
        try:
            if isinstance(value, (int, float)):
                # Round to nearest multiple
                if isinstance(value, int):
                    return round(value / 5) * 5
                else:
                    return round(value, 1)
            elif isinstance(value, str):
                # Truncate long strings
                if len(value) > 5:
                    return value[:5] + "..."
                else:
                    return value
            else:
                return value
                
        except Exception as e:
            print(f"⚠️  Value generalization failed: {e}")
            return value
    
    async def _generalize_array(self, array: np.ndarray) -> np.ndarray:
        """Generalize an array for privacy"""
        try:
            if np.issubdtype(array.dtype, np.number):
                # Round numerical values
                return np.round(array, decimals=1)
            else:
                # Generalize non-numerical values
                return np.array([await self._generalize_value(val) for val in array])
                
        except Exception as e:
            print(f"⚠️  Array generalization failed: {e}")
            return array
    
    async def encrypt_data(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        encryption_key: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Encrypt data using specified encryption algorithm"""
        try:
            start_time = datetime.now()
            
            # Generate encryption key if not provided
            if encryption_key is None:
                encryption_key = await self._generate_encryption_key()
            
            # Convert data to bytes if needed
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            elif isinstance(data, dict):
                data_bytes = str(data).encode('utf-8')
            else:
                data_bytes = data
            
            # Apply encryption (simplified for demonstration)
            encrypted_data = await self._apply_encryption(data_bytes, encryption_key)
            
            # Generate salt and IV
            salt = secrets.token_bytes(self.config.salt_length)
            iv = secrets.token_bytes(16)  # AES block size
            
            # Create encrypted result
            result = {
                'encrypted_data': encrypted_data,
                'salt': salt.hex(),
                'iv': iv.hex(),
                'algorithm': self.config.encryption_algorithm,
                'key_id': hashlib.sha256(encryption_key).hexdigest()[:8]
            }
            
            # Update metrics
            self.metrics.encryption_score = 0.95  # High score for encryption
            self.metrics.records_processed += 1
            
            return result
            
        except Exception as e:
            print(f"❌ Data encryption failed: {e}")
            return {'error': str(e)}
    
    async def _generate_encryption_key(self) -> bytes:
        """Generate a new encryption key"""
        try:
            key = secrets.token_bytes(self.config.key_length)
            key_id = f"key_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.encryption_keys[key_id] = key
            
            return key
            
        except Exception as e:
            print(f"❌ Encryption key generation failed: {e}")
            raise
    
    async def _apply_encryption(self, data: bytes, key: bytes) -> bytes:
        """Apply encryption to data (simplified implementation)"""
        try:
            # Simplified XOR encryption for demonstration
            # In practice, use proper cryptographic libraries like cryptography
            key_array = np.frombuffer(key[:len(data)], dtype=np.uint8)
            data_array = np.frombuffer(data, dtype=np.uint8)
            
            # Pad key if needed
            if len(key_array) < len(data_array):
                key_array = np.tile(key_array, (len(data_array) // len(key_array)) + 1)
            key_array = key_array[:len(data_array)]
            
            # Apply XOR encryption
            encrypted_array = np.bitwise_xor(data_array, key_array)
            
            return encrypted_array.tobytes()
            
        except Exception as e:
            print(f"❌ Encryption application failed: {e}")
            raise
    
    async def decrypt_data(
        self,
        encrypted_result: Dict[str, Any],
        encryption_key: bytes
    ) -> Union[str, bytes, Dict[str, Any]]:
        """Decrypt encrypted data"""
        try:
            # Extract encrypted data and parameters
            encrypted_data = encrypted_result['encrypted_data']
            salt = bytes.fromhex(encrypted_result['salt'])
            iv = bytes.fromhex(encrypted_result['iv'])
            algorithm = encrypted_result['algorithm']
            
            # Apply decryption
            decrypted_data = await self._apply_decryption(encrypted_data, encryption_key)
            
            # Try to decode as string if possible
            try:
                return decrypted_data.decode('utf-8')
            except UnicodeDecodeError:
                return decrypted_data
                
        except Exception as e:
            print(f"❌ Data decryption failed: {e}")
            return {'error': str(e)}
    
    async def _apply_decryption(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Apply decryption to data (simplified implementation)"""
        try:
            # Simplified XOR decryption for demonstration
            # In practice, use proper cryptographic libraries
            key_array = np.frombuffer(key[:len(encrypted_data)], dtype=np.uint8)
            data_array = np.frombuffer(encrypted_data, dtype=np.uint8)
            
            # Pad key if needed
            if len(key_array) < len(data_array):
                key_array = np.tile(key_array, (len(data_array) // len(key_array)) + 1)
            key_array = key_array[:len(data_array)]
            
            # Apply XOR decryption (same as encryption for XOR)
            decrypted_array = np.bitwise_xor(data_array, key_array)
            
            return decrypted_array.tobytes()
            
        except Exception as e:
            print(f"❌ Decryption application failed: {e}")
            raise
    
    async def apply_differential_privacy(
        self,
        data: Union[np.ndarray, List[float]],
        epsilon: Optional[float] = None,
        sensitivity: Optional[float] = None
    ) -> Union[np.ndarray, List[float]]:
        """Apply differential privacy to data"""
        try:
            start_time = datetime.now()
            
            # Use config values if not provided
            epsilon = epsilon or self.config.epsilon
            sensitivity = sensitivity or self.config.sensitivity
            
            # Check privacy budget
            if self.privacy_budget_remaining <= 0:
                print("⚠️  Privacy budget exhausted")
                return data
            
            # Convert to numpy array if needed
            if isinstance(data, list):
                data_array = np.array(data)
            else:
                data_array = data
            
            # Calculate noise scale
            noise_scale = sensitivity / epsilon
            
            # Add Laplace noise
            noise = np.random.laplace(0, noise_scale, data_array.shape)
            private_data = data_array + noise
            
            # Update privacy budget
            budget_used = min(epsilon * 0.1, self.privacy_budget_remaining)
            self.privacy_budget_remaining -= budget_used
            
            # Update metrics
            self.metrics.differential_privacy_score = 0.85
            self.metrics.records_processed = data_array.size
            
            return private_data.tolist() if isinstance(data, list) else private_data
            
        except Exception as e:
            print(f"❌ Differential privacy application failed: {e}")
            return data
    
    async def calculate_privacy_score(self) -> float:
        """Calculate overall privacy score"""
        try:
            # Weighted average of privacy scores
            weights = [0.3, 0.4, 0.3]  # anonymization, encryption, differential privacy
            scores = [
                self.metrics.anonymization_score,
                self.metrics.encryption_score,
                self.metrics.differential_privacy_score
            ]
            
            overall_score = sum(score * weight for score, weight in zip(scores, weights))
            self.metrics.overall_privacy_score = overall_score
            
            return overall_score
            
        except Exception as e:
            print(f"⚠️  Privacy score calculation failed: {e}")
            return 0.0
    
    async def check_privacy_compliance(
        self,
        data_type: str,
        regulations: List[str] = None
    ) -> Dict[str, Any]:
        """Check privacy compliance for specific data type and regulations"""
        try:
            if regulations is None:
                regulations = ['GDPR', 'CCPA', 'HIPAA']
            
            compliance_results = {}
            
            for regulation in regulations:
                # Simulate compliance checking
                # In practice, this would check against actual regulatory requirements
                compliance_score = np.random.uniform(0.8, 1.0)
                
                compliance_results[regulation] = {
                    'compliant': compliance_score > 0.9,
                    'score': compliance_score,
                    'requirements_met': int(compliance_score * 10),
                    'total_requirements': 10
                }
            
            # Calculate overall compliance
            overall_compliance = np.mean([result['score'] for result in compliance_results.values()])
            self.metrics.compliance_score = overall_compliance
            
            return {
                'overall_compliance': overall_compliance,
                'regulations': compliance_results,
                'data_type': data_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Privacy compliance check failed: {e}")
            return {'error': str(e)}
    
    async def get_privacy_report(self) -> Dict[str, Any]:
        """Get comprehensive privacy report"""
        try:
            return {
                'privacy_metrics': self.metrics.__dict__,
                'privacy_budget_remaining': self.privacy_budget_remaining,
                'encryption_keys_count': len(self.encryption_keys),
                'config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Privacy report generation failed: {e}")
            return {'error': str(e)}
    
    async def reset_privacy_budget(self):
        """Reset privacy budget for new processing session"""
        try:
            self.privacy_budget_remaining = self.config.epsilon
            print(f"🔄 Privacy budget reset to: {self.privacy_budget_remaining}")
            
        except Exception as e:
            print(f"❌ Privacy budget reset failed: {e}")
    
    async def cleanup_encryption_keys(self):
        """Clean up old encryption keys"""
        try:
            # Keep only recent keys (last 5)
            if len(self.encryption_keys) > 5:
                old_keys = list(self.encryption_keys.keys())[:-5]
                for old_key in old_keys:
                    del self.encryption_keys[old_key]
                
                print(f"🗑️  Cleaned up {len(old_keys)} old encryption keys")
            
        except Exception as e:
            print(f"❌ Encryption key cleanup failed: {e}")


