"""
Security and Authentication Module
================================

Comprehensive security system including authentication, authorization,
encryption, and security utilities for the AAS data modeling engine.
"""

from .authentication import (
    Authenticator,
    AsyncAuthenticator,
    JWTAuthenticator,
    OAuthAuthenticator,
    LDAPAuthenticator,
    MultiFactorAuthenticator
)

from .authorization import (
    AuthorizationManager,
    AsyncAuthorizationManager,
    RoleBasedAccessControl,
    PermissionManager,
    PolicyEngine
)

from .encryption import (
    EncryptionManager,
    AsyncEncryptionManager,
    SymmetricEncryption,
    AsymmetricEncryption,
    HashManager,
    KeyManager
)

from .security_utils import (
    SecurityUtils,
    PasswordManager,
    TokenManager,
    SecurityValidator,
    AuditLogger
)

from .models import (
    User,
    Role,
    Permission,
    SecurityPolicy,
    SecurityContext,
    AuthenticationResult,
    AuthorizationResult,
    PermissionLevel,
    UserStatus,
    AuthenticationMethod
)

from .middleware import (
    SecurityMiddleware,
    AuthenticationMiddleware,
    AuthorizationMiddleware,
    RateLimitMiddleware,
    AuditMiddleware,
    SecurityMiddlewareChain
)

__all__ = [
    # Authentication
    'Authenticator',
    'AsyncAuthenticator', 
    'JWTAuthenticator',
    'OAuthAuthenticator',
    'LDAPAuthenticator',
    'MultiFactorAuthenticator',
    
    # Authorization
    'AuthorizationManager',
    'AsyncAuthorizationManager',
    'RoleBasedAccessControl',
    'PermissionManager',
    'PolicyEngine',
    
    # Encryption
    'EncryptionManager',
    'AsyncEncryptionManager',
    'SymmetricEncryption',
    'AsymmetricEncryption',
    'HashManager',
    'KeyManager',
    
    # Security Utils
    'SecurityUtils',
    'PasswordManager',
    'TokenManager',
    'SecurityValidator',
    'AuditLogger',
    
    # Models
    'User',
    'Role',
    'Permission',
    'SecurityPolicy',
    'SecurityContext',
    'AuthenticationResult',
    'AuthorizationResult',
    'PermissionLevel',
    'UserStatus',
    'AuthenticationMethod',
    
    # Middleware
    'SecurityMiddleware',
    'AuthenticationMiddleware',
    'AuthorizationMiddleware',
    'RateLimitMiddleware',
    'AuditMiddleware',
    'SecurityMiddlewareChain'
]
