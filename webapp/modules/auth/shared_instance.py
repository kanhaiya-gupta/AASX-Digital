"""
Shared AuthDatabase instance for consistent JWT token creation and verification.
This ensures all parts of the auth system use the same secret key and database connection.
"""

from .database import AuthDatabase

# Create a single, shared instance of AuthDatabase
# This ensures consistent JWT secret keys across all auth operations
shared_auth_db = AuthDatabase()

# Export the shared instance
__all__ = ['shared_auth_db']
