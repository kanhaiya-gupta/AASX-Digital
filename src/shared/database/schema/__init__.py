"""
Database Schema Package
======================

This package provides a modular approach to database schema management.
It includes the base schema class and all domain-specific schema modules.
"""

from .base_schema import BaseSchemaModule
from .modules import AIRagSchema, AasxEtlSchema, TwinRegistrySchema, KgNeo4jSchema, CoreSystemSchema, BusinessDomainSchema, DataGovernanceSchema, FederatedLearningSchema, PhysicsModelingSchema, CertificateManagerSchema, AuthSchema, get_schema_module, get_all_schema_modules

# Export main classes and utilities
__all__ = [
    'BaseSchemaModule',
    'AIRagSchema',
    'AasxEtlSchema',
    'TwinRegistrySchema',
    'KgNeo4jSchema',
    'CoreSystemSchema',
    'BusinessDomainSchema',
    'DataGovernanceSchema',
    'FederatedLearningSchema',
    'PhysicsModelingSchema',
    'CertificateManagerSchema',
    'AuthSchema',
    'get_schema_module',
    'get_all_schema_modules',
]
