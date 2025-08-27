"""
Database Schema Modules Package
==============================

This package contains all the modular database schema implementations.
Each module handles a specific domain of the database schema.
"""

from .ai_rag import AIRagSchema
from .aasx_etl import AasxEtlSchema
from .twin_registry import TwinRegistrySchema
from .kg_neo4j import KgNeo4jSchema
from .core_system import CoreSystemSchema
from .business_domain import BusinessDomainSchema
from .data_governance import DataGovernanceSchema
from .federated_learning import FederatedLearningSchema
from .physics_modeling import PhysicsModelingSchema
from .certificate_manager import CertificateManagerSchema
from .auth import AuthSchema

# Export all schema modules
__all__ = [
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
]

# Module registry for easy discovery
SCHEMA_MODULES = {
    'ai_rag': AIRagSchema,
    'aasx_etl': AasxEtlSchema,
    'twin_registry': TwinRegistrySchema,
    'kg_neo4j': KgNeo4jSchema,
    'core_system': CoreSystemSchema,
    'business_domain': BusinessDomainSchema,
    'data_governance': DataGovernanceSchema,
    'federated_learning': FederatedLearningSchema,
    'physics_modeling': PhysicsModelingSchema,
    'certificate_manager': CertificateManagerSchema,
    'auth': AuthSchema,
}


def get_schema_module(module_name: str):
    """
    Get a schema module by name.
    
    Args:
        module_name: Name of the module to retrieve
        
    Returns:
        Schema module class or None if not found
    """
    return SCHEMA_MODULES.get(module_name)

def get_all_schema_modules():
    """
    Get all available schema modules.
    
    Returns:
        Dict mapping module names to module classes
    """
    return SCHEMA_MODULES.copy()
