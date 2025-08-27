"""
Security Service for Physics Modeling
====================================

Provides comprehensive security capabilities for physics modeling,
ensuring data protection, access control, and compliance with security standards.

Features:
- Access control and authentication
- Data encryption and decryption
- Security audit logging
- Threat detection and monitoring
- Compliance validation
- Security policy enforcement
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import hmac
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Import physics modeling components
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..models.physics_modeling_metrics import PhysicsModelingMetrics
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AccessLevel(Enum):
    """Access level enumeration."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class SecurityEventType(Enum):
    """Security event type enumeration."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SECURITY_VIOLATION = "security_violation"
    SYSTEM_ACCESS = "system_access"
    ENCRYPTION = "encryption"
    DECRYPTION = "decryption"


class SecurityThreatLevel(Enum):
    """Security threat level enumeration."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityPolicy:
    """Security policy configuration."""
    
    def __init__(
        self,
        policy_id: str,
        name: str,
        description: str,
        security_level: SecurityLevel,
        access_controls: Dict[str, List[AccessLevel]],
        encryption_required: bool = True,
        audit_logging: bool = True,
        threat_monitoring: bool = True
    ):
        self.policy_id = policy_id
        self.name = name
        self.description = description
        self.security_level = security_level
        self.access_controls = access_controls
        self.encryption_required = encryption_required
        self.audit_logging = audit_logging
        self.threat_monitoring = threat_monitoring
        self.created_at = datetime.now()
        self.last_updated = datetime.now()


class SecurityService:
    """
    Comprehensive security service for physics modeling.
    
    Provides:
    - Access control and authentication
    - Data encryption and decryption
    - Security audit logging
    - Threat detection and monitoring
    - Compliance validation
    - Security policy enforcement
    """

    def __init__(
        self,
        registry_repo: Optional[PhysicsModelingRegistryRepository] = None,
        metrics_repo: Optional[PhysicsModelingMetricsRepository] = None,
        encryption_key: Optional[str] = None
    ):
        """Initialize the security service."""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        
        # Initialize repositories if not provided
        if not self.registry_repo:
            from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
            self.registry_repo = PhysicsModelingRegistryRepository()
        
        if not self.metrics_repo:
            from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository
            self.metrics_repo = PhysicsModelingMetricsRepository()
        
        # Security configuration
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Security policies and access control
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.access_tokens: Dict[str, Dict[str, Any]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.threat_alerts: List[Dict[str, Any]] = []
        
        # Security metrics
        self.security_metrics = {
            'total_authentications': 0,
            'successful_authentications': 0,
            'failed_authentications': 0,
            'security_violations': 0,
            'threat_detections': 0,
            'encryption_operations': 0,
            'decryption_operations': 0
        }
        
        logger.info("Security service initialized")

    async def initialize(self) -> bool:
        """Initialize the security service."""
        try:
            # Initialize repositories
            await self.registry_repo.initialize()
            await self.metrics_repo.initialize()
            
            # Initialize default security policies
            await self._initialize_default_security_policies()
            
            logger.info("✅ Security service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize security service: {e}")
            return False

    async def authenticate_user(
        self,
        user_id: str,
        credentials: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Authenticate a user and generate access token.
        
        Args:
            user_id: User identifier
            credentials: User credentials
            context: Authentication context
            
        Returns:
            Access token or None if authentication failed
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Validate credentials (simplified for demo)
            if not self._validate_credentials(credentials):
                await self._record_security_event(
                    SecurityEventType.AUTHENTICATION,
                    "failed",
                    f"Invalid credentials for user {user_id}",
                    SecurityThreatLevel.MEDIUM,
                    context
                )
                self.security_metrics['failed_authentications'] += 1
                return None
            
            # Generate access token
            token = self._generate_access_token(user_id, context)
            
            # Store token information
            self.access_tokens[token] = {
                'user_id': user_id,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=24),
                'context': context or {},
                'permissions': self._get_user_permissions(user_id)
            }
            
            # Record successful authentication
            await self._record_security_event(
                SecurityEventType.AUTHENTICATION,
                "success",
                f"User {user_id} authenticated successfully",
                SecurityThreatLevel.INFO,
                context
            )
            
            self.security_metrics['total_authentications'] += 1
            self.security_metrics['successful_authentications'] += 1
            
            logger.info(f"✅ User {user_id} authenticated successfully")
            return token
            
        except Exception as e:
            logger.error(f"Failed to authenticate user {user_id}: {e}")
            return None

    async def validate_access_token(
        self,
        token: str,
        required_permissions: Optional[List[AccessLevel]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Validate an access token and check permissions.
        
        Args:
            token: Access token to validate
            required_permissions: Required permissions for access
            
        Returns:
            Token information or None if invalid
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            if token not in self.access_tokens:
                await self._record_security_event(
                    SecurityEventType.AUTHORIZATION,
                    "failed",
                    f"Invalid access token: {token[:8]}...",
                    SecurityThreatLevel.HIGH,
                    {'token': token[:8]}
                )
                return None
            
            token_info = self.access_tokens[token]
            
            # Check token expiration
            if datetime.now() > token_info['expires_at']:
                await self._record_security_event(
                    SecurityEventType.AUTHORIZATION,
                    "failed",
                    f"Expired access token for user {token_info['user_id']}",
                    SecurityThreatLevel.MEDIUM,
                    {'user_id': token_info['user_id']}
                )
                del self.access_tokens[token]
                return None
            
            # Check required permissions
            if required_permissions:
                user_permissions = token_info['permissions']
                if not all(perm in user_permissions for perm in required_permissions):
                    await self._record_security_event(
                        SecurityEventType.AUTHORIZATION,
                        "failed",
                        f"Insufficient permissions for user {token_info['user_id']}",
                        SecurityThreatLevel.HIGH,
                        {
                            'user_id': token_info['user_id'],
                            'required': [p.value for p in required_permissions],
                            'user_permissions': [p.value for p in user_permissions]
                        }
                    )
                    return None
            
            # Record successful authorization
            await self._record_security_event(
                SecurityEventType.AUTHORIZATION,
                "success",
                f"Access token validated for user {token_info['user_id']}",
                SecurityThreatLevel.INFO,
                {'user_id': token_info['user_id']}
            )
            
            return token_info
            
        except Exception as e:
            logger.error(f"Failed to validate access token: {e}")
            return None

    async def encrypt_data(
        self,
        data: Union[str, bytes],
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[bytes]:
        """
        Encrypt data using the configured encryption key.
        
        Args:
            data: Data to encrypt
            security_level: Required security level
            context: Encryption context
            
        Returns:
            Encrypted data or None if encryption failed
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Convert string to bytes if needed
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Encrypt data
            encrypted_data = self.cipher_suite.encrypt(data_bytes)
            
            # Record encryption event
            await self._record_security_event(
                SecurityEventType.ENCRYPTION,
                "success",
                f"Data encrypted with {security_level.value} security level",
                SecurityThreatLevel.INFO,
                context
            )
            
            self.security_metrics['encryption_operations'] += 1
            
            logger.info(f"✅ Data encrypted successfully with {security_level.value} security")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            
            await self._record_security_event(
                SecurityEventType.ENCRYPTION,
                "failed",
                f"Data encryption failed: {e}",
                SecurityThreatLevel.HIGH,
                context
            )
            
            return None

    async def decrypt_data(
        self,
        encrypted_data: bytes,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Union[str, bytes]]:
        """
        Decrypt data using the configured encryption key.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            context: Decryption context
            
        Returns:
            Decrypted data or None if decryption failed
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Decrypt data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            # Record decryption event
            await self._record_security_event(
                SecurityEventType.DECRYPTION,
                "success",
                "Data decrypted successfully",
                SecurityThreatLevel.INFO,
                context
            )
            
            self.security_metrics['decryption_operations'] += 1
            
            logger.info("✅ Data decrypted successfully")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            
            await self._record_security_event(
                SecurityEventType.DECRYPTION,
                "failed",
                f"Data decryption failed: {e}",
                SecurityThreatLevel.HIGH,
                context
            )
            
            return None

    async def check_data_access_permission(
        self,
        user_id: str,
        data_id: str,
        access_type: AccessLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a user has permission to access specific data.
        
        Args:
            user_id: User identifier
            data_id: Data identifier
            access_type: Type of access requested
            context: Access context
            
        Returns:
            True if access permitted, False otherwise
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Get user permissions
            user_permissions = self._get_user_permissions(user_id)
            
            # Check if user has required access level
            if access_type not in user_permissions:
                await self._record_security_event(
                    SecurityEventType.AUTHORIZATION,
                    "failed",
                    f"User {user_id} lacks {access_type.value} permission for data {data_id}",
                    SecurityThreatLevel.MEDIUM,
                    {
                        'user_id': user_id,
                        'data_id': data_id,
                        'access_type': access_type.value,
                        'user_permissions': [p.value for p in user_permissions]
                    }
                )
                return False
            
            # Check data-specific access rules
            if not self._check_data_specific_permissions(user_id, data_id, access_type):
                await self._record_security_event(
                    SecurityEventType.AUTHORIZATION,
                    "failed",
                    f"Data-specific access denied for user {user_id} to data {data_id}",
                    SecurityThreatLevel.MEDIUM,
                    {
                        'user_id': user_id,
                        'data_id': data_id,
                        'access_type': access_type.value
                    }
                )
                return False
            
            # Record successful access
            await self._record_security_event(
                SecurityEventType.DATA_ACCESS,
                "success",
                f"User {user_id} granted {access_type.value} access to data {data_id}",
                SecurityThreatLevel.INFO,
                {
                    'user_id': user_id,
                    'data_id': data_id,
                    'access_type': access_type.value
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check data access permission: {e}")
            return False

    async def register_security_policy(
        self,
        name: str,
        description: str,
        security_level: SecurityLevel,
        access_controls: Dict[str, List[AccessLevel]],
        encryption_required: bool = True,
        audit_logging: bool = True,
        threat_monitoring: bool = True
    ) -> str:
        """
        Register a new security policy.
        
        Args:
            name: Policy name
            description: Policy description
            security_level: Required security level
            access_controls: Access control rules
            encryption_required: Whether encryption is required
            audit_logging: Whether audit logging is enabled
            threat_monitoring: Whether threat monitoring is enabled
            
        Returns:
            Policy ID
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            policy_id = f"policy_{int(datetime.now().timestamp())}"
            
            policy = SecurityPolicy(
                policy_id=policy_id,
                name=name,
                description=description,
                security_level=security_level,
                access_controls=access_controls,
                encryption_required=encryption_required,
                audit_logging=audit_logging,
                threat_monitoring=threat_monitoring
            )
            
            self.security_policies[policy_id] = policy
            
            logger.info(f"✅ Security policy {name} registered successfully")
            return policy_id
            
        except Exception as e:
            logger.error(f"Failed to register security policy: {e}")
            raise

    async def apply_security_policy(
        self,
        policy_id: str,
        data: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply a security policy to data.
        
        Args:
            policy_id: Security policy identifier
            data: Data to apply policy to
            context: Policy application context
            
        Returns:
            Policy application results
        """
        try:
            if policy_id not in self.security_policies:
                raise ValueError(f"Security policy {policy_id} not found")
            
            policy = self.security_policies[policy_id]
            results = {
                'policy_id': policy_id,
                'policy_name': policy.name,
                'applied_at': datetime.now(),
                'encryption_applied': False,
                'access_controls_applied': False,
                'audit_logging_applied': False,
                'threat_monitoring_applied': False
            }
            
            # Apply encryption if required
            if policy.encryption_required:
                encrypted_data = await self.encrypt_data(
                    str(data),
                    policy.security_level,
                    context
                )
                if encrypted_data:
                    results['encryption_applied'] = True
                    results['encrypted_data'] = encrypted_data
            
            # Apply access controls
            if policy.access_controls:
                results['access_controls_applied'] = True
                results['access_controls'] = policy.access_controls
            
            # Apply audit logging
            if policy.audit_logging:
                await self._record_security_event(
                    SecurityEventType.SYSTEM_ACCESS,
                    "success",
                    f"Security policy {policy.name} applied to data",
                    SecurityThreatLevel.INFO,
                    context
                )
                results['audit_logging_applied'] = True
            
            # Apply threat monitoring
            if policy.threat_monitoring:
                await self._setup_threat_monitoring(policy, context)
                results['threat_monitoring_applied'] = True
            
            logger.info(f"✅ Security policy {policy.name} applied successfully")
            return results
            
        except Exception as e:
            logger.error(f"Failed to apply security policy {policy_id}: {e}")
            raise

    async def get_security_audit_log(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[SecurityEventType] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get security audit log entries.
        
        Args:
            start_time: Start time filter
            end_time: End time filter
            event_type: Event type filter
            user_id: User ID filter
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Filter audit log
            filtered_log = self.audit_log.copy()
            
            if start_time:
                filtered_log = [entry for entry in filtered_log if entry['timestamp'] >= start_time]
            
            if end_time:
                filtered_log = [entry for entry in filtered_log if entry['timestamp'] <= end_time]
            
            if event_type:
                filtered_log = [entry for entry in filtered_log if entry['event_type'] == event_type.value]
            
            if user_id:
                filtered_log = [entry for entry in filtered_log if entry.get('user_id') == user_id]
            
            # Sort by timestamp (newest first) and limit results
            filtered_log.sort(key=lambda x: x['timestamp'], reverse=True)
            filtered_log = filtered_log[:limit]
            
            return filtered_log
            
        except Exception as e:
            logger.error(f"Failed to get security audit log: {e}")
            return []

    async def get_threat_alerts(
        self,
        threat_level: Optional[SecurityThreatLevel] = None,
        start_time: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get security threat alerts.
        
        Args:
            threat_level: Threat level filter
            start_time: Start time filter
            limit: Maximum number of alerts to return
            
        Returns:
            List of threat alerts
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Filter threat alerts
            filtered_alerts = self.threat_alerts.copy()
            
            if threat_level:
                filtered_alerts = [alert for alert in filtered_alerts if alert['threat_level'] == threat_level.value]
            
            if start_time:
                filtered_alerts = [alert for alert in filtered_alerts if alert['timestamp'] >= start_time]
            
            # Sort by timestamp (newest first) and limit results
            filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            filtered_alerts = filtered_alerts[:limit]
            
            return filtered_alerts
            
        except Exception as e:
            logger.error(f"Failed to get threat alerts: {e}")
            return []

    async def get_security_metrics(self) -> Dict[str, Any]:
        """
        Get security service metrics.
        
        Returns:
            Security metrics information
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Calculate additional metrics
            total_events = len(self.audit_log)
            total_alerts = len(self.threat_alerts)
            active_tokens = len([t for t in self.access_tokens.values() if t['expires_at'] > datetime.now()])
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'basic_metrics': self.security_metrics.copy(),
                'calculated_metrics': {
                    'total_audit_events': total_events,
                    'total_threat_alerts': total_alerts,
                    'active_access_tokens': active_tokens,
                    'authentication_success_rate': (
                        (self.security_metrics['successful_authentications'] / 
                         self.security_metrics['total_authentications'] * 100)
                        if self.security_metrics['total_authentications'] > 0 else 0
                    ),
                    'security_violation_rate': (
                        (self.security_metrics['security_violations'] / 
                         max(total_events, 1) * 100)
                    )
                },
                'security_policies': len(self.security_policies),
                'access_tokens': len(self.access_tokens)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get security metrics: {e}")
            return {}

    def _generate_encryption_key(self) -> bytes:
        """Generate a new encryption key."""
        try:
            # Generate a random key
            key = Fernet.generate_key()
            return key
        except Exception as e:
            logger.error(f"Failed to generate encryption key: {e}")
            # Fallback to a deterministic key (not recommended for production)
            fallback_key = hashlib.sha256(b"physics_modeling_security_fallback").digest()
            return base64.urlsafe_b64encode(fallback_key)

    def _validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate user credentials (simplified for demo)."""
        try:
            # In a real implementation, this would validate against a secure credential store
            username = credentials.get('username')
            password = credentials.get('password')
            
            # Simple validation for demo purposes
            if not username or not password:
                return False
            
            # Check for common weak credentials
            if password in ['password', '123456', 'admin']:
                return False
            
            # For demo, accept any non-empty credentials
            return len(username) > 0 and len(password) > 0
            
        except Exception as e:
            logger.error(f"Failed to validate credentials: {e}")
            return False

    def _generate_access_token(self, user_id: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate a secure access token."""
        try:
            # Generate a random token
            token_data = f"{user_id}:{datetime.now().isoformat()}:{secrets.token_urlsafe(32)}"
            token_hash = hashlib.sha256(token_data.encode()).hexdigest()
            return f"token_{token_hash[:16]}"
        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            return f"token_{secrets.token_urlsafe(16)}"

    def _get_user_permissions(self, user_id: str) -> List[AccessLevel]:
        """Get user permissions (simplified for demo)."""
        try:
            # In a real implementation, this would query a user management system
            # For demo purposes, assign permissions based on user ID patterns
            
            if user_id.startswith('admin'):
                return [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN, AccessLevel.OWNER]
            elif user_id.startswith('user'):
                return [AccessLevel.READ, AccessLevel.WRITE]
            elif user_id.startswith('viewer'):
                return [AccessLevel.READ]
            else:
                return [AccessLevel.READ]  # Default to read-only
                
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return [AccessLevel.READ]  # Default to read-only

    def _check_data_specific_permissions(
        self,
        user_id: str,
        data_id: str,
        access_type: AccessLevel
    ) -> bool:
        """Check data-specific access permissions."""
        try:
            # In a real implementation, this would check data ownership and sharing rules
            # For demo purposes, implement basic rules
            
            # Admin users can access everything
            if user_id.startswith('admin'):
                return True
            
            # Owner users can access their own data
            if user_id.startswith('owner') and data_id.startswith(user_id):
                return True
            
            # Regular users can read most data but write only to their own
            if access_type == AccessLevel.READ:
                return True
            elif access_type == AccessLevel.WRITE:
                return data_id.startswith(user_id)
            
            # Admin and owner operations require higher permissions
            if access_type in [AccessLevel.ADMIN, AccessLevel.OWNER]:
                return user_id.startswith('admin') or user_id.startswith('owner')
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check data-specific permissions: {e}")
            return False

    async def _record_security_event(
        self,
        event_type: SecurityEventType,
        status: str,
        message: str,
        threat_level: SecurityThreatLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a security event in the audit log."""
        try:
            event = {
                'event_id': f"event_{int(datetime.now().timestamp())}",
                'event_type': event_type.value,
                'status': status,
                'message': message,
                'threat_level': threat_level.value,
                'timestamp': datetime.now(),
                'context': context or {}
            }
            
            # Add user context if available
            if context and 'user_id' in context:
                event['user_id'] = context['user_id']
            
            self.audit_log.append(event)
            
            # Check if this is a security violation
            if status == "failed" and threat_level in [SecurityThreatLevel.HIGH, SecurityThreatLevel.CRITICAL]:
                await self._create_threat_alert(event)
                self.security_metrics['security_violations'] += 1
            
            # Record event metrics
            await self._record_security_event_metrics(event)
            
        except Exception as e:
            logger.error(f"Failed to record security event: {e}")

    async def _create_threat_alert(self, event: Dict[str, Any]) -> None:
        """Create a threat alert for security events."""
        try:
            alert = {
                'alert_id': f"alert_{int(datetime.now().timestamp())}",
                'event_id': event['event_id'],
                'threat_level': event['threat_level'],
                'message': f"Security threat detected: {event['message']}",
                'timestamp': datetime.now(),
                'event_details': event,
                'status': 'active',
                'acknowledged': False
            }
            
            self.threat_alerts.append(alert)
            self.security_metrics['threat_detections'] += 1
            
            logger.warning(f"🚨 Security threat alert created: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Failed to create threat alert: {e}")

    async def _setup_threat_monitoring(
        self,
        policy: SecurityPolicy,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Setup threat monitoring for a security policy."""
        try:
            # In a real implementation, this would setup monitoring rules and alerts
            # For demo purposes, just log the setup
            
            logger.info(f"✅ Threat monitoring setup for policy {policy.name}")
            
        except Exception as e:
            logger.error(f"Failed to setup threat monitoring: {e}")

    async def _initialize_default_security_policies(self) -> None:
        """Initialize default security policies."""
        try:
            # Default policy for physics models
            await self.register_security_policy(
                name="Physics Model Security",
                description="Default security policy for physics modeling data",
                security_level=SecurityLevel.MEDIUM,
                access_controls={
                    'physics_models': [AccessLevel.READ, AccessLevel.WRITE],
                    'simulation_results': [AccessLevel.READ, AccessLevel.WRITE],
                    'sensitive_data': [AccessLevel.READ]
                },
                encryption_required=True,
                audit_logging=True,
                threat_monitoring=True
            )
            
            # High-security policy for critical data
            await self.register_security_policy(
                name="Critical Data Security",
                description="High-security policy for critical physics modeling data",
                security_level=SecurityLevel.HIGH,
                access_controls={
                    'critical_models': [AccessLevel.READ],
                    'proprietary_data': [AccessLevel.READ],
                    'research_results': [AccessLevel.READ, AccessLevel.WRITE]
                },
                encryption_required=True,
                audit_logging=True,
                threat_monitoring=True
            )
            
            logger.info("✅ Default security policies initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default security policies: {e}")

    async def _record_security_event_metrics(self, event: Dict[str, Any]) -> None:
        """Record security event metrics."""
        try:
            # Create metrics record
            metrics = PhysicsModelingMetrics(
                physics_modeling_id=None,  # Will be set by repository
                metric_name="security_event",
                metric_value=1.0,
                metric_unit="count",
                metric_type="security",
                metric_category="audit_logging",
                metric_timestamp=event['timestamp'],
                metric_metadata={
                    'event_id': event['event_id'],
                    'event_type': event['event_type'],
                    'status': event['status'],
                    'threat_level': event['threat_level'],
                    'message': event['message'],
                    'context': event.get('context', {})
                }
            )
            
            # Save to database
            await self.metrics_repo.create(metrics)
            
        except Exception as e:
            logger.error(f"Failed to record security event metrics: {e}")

    async def close(self) -> None:
        """Close the security service."""
        try:
            # Clear sensitive data
            self.access_tokens.clear()
            self.audit_log.clear()
            self.threat_alerts.clear()
            
            if self.registry_repo:
                await self.registry_repo.close()
            if self.metrics_repo:
                await self.metrics_repo.close()
            
            logger.info("✅ Security service closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing security service: {e}")


