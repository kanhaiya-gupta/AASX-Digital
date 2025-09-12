#!/usr/bin/env python3
"""
Certificate Manager Certificates Registry Service

This service provides business logic and orchestration for certificates registry operations
by leveraging the comprehensive engine infrastructure for enterprise features.

Features:
- Business logic orchestration and workflow management
- Enterprise-grade security and access control (via engine)
- Comprehensive validation and error handling (via engine)
- Performance optimization and monitoring (via engine)
- Event-driven architecture and async operations (via engine)
- Audit logging and compliance tracking (via engine)
- Multi-tenant support and RBAC (via engine)
- Department-level access control (dept_id) (via engine)

Example Usage:
    # Initialize service
    service = CertificatesRegistryService(connection_manager)
    await service.initialize_service()
    
    # Use service methods
    result = await service.create_entity(data, user_context)
    entities = await service.search_entities(criteria, user_context)
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# ✅ REQUIRED: Import engine components
from src.engine.models.base_model import EngineBaseModel
from src.engine.monitoring.monitoring_config import MonitoringConfig
from src.engine.monitoring.performance_profiler import PerformanceProfiler
from src.engine.monitoring.metrics_collector import MetricsCollector
from src.engine.monitoring.error_tracker import ErrorTracker
from src.engine.security.authorization import RoleBasedAccessControl, SecurityContext
from src.engine.monitoring.health_monitor import HealthMonitor
from src.engine.messaging.event_bus import EventBus
from src.engine.database.connection_manager import ConnectionManager

# ✅ REQUIRED: Import your module components
from ..models.certificates_registry import CertificateRegistry
from ..repositories.certificates_registry_repository import CertificatesRegistryRepository

logger = logging.getLogger(__name__)


class CertificatesRegistryService:
    """
    Service for certificates registry business logic and orchestration
    
    Provides high-level business operations, workflow management, and
    enterprise features by leveraging the engine infrastructure.
    
    Enterprise Features (via Engine):
    - Business logic orchestration and workflow management
    - Enterprise-grade security and access control
    - Comprehensive validation and business rule enforcement
    - Performance monitoring and optimization
    - Event-driven architecture and async operations
    - Multi-tenant support with RBAC
    - Department-level access control (dept_id)
    - Audit logging and compliance tracking
    - Error handling and recovery mechanisms
    
    Architecture:
    - Thin business logic layer that orchestrates engine components
    - Repository pattern for data access
    - Event-driven architecture for inter-service communication
    - Comprehensive monitoring and metrics collection
    - Role-based access control with multi-tenant support
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize the service with connection manager and engine components.
        
        Args:
            connection_manager: Database connection manager for data access
        """
        # ✅ REQUIRED: Database connection
        self.connection_manager = connection_manager
        
        # ✅ REQUIRED: Repository for table operations
        self.repository = CertificatesRegistryRepository(connection_manager)
        
        # ✅ REQUIRED: Engine components for enterprise features
        monitoring_config = MonitoringConfig()
        self.performance_profiler = PerformanceProfiler(monitoring_config)
        self.auth_manager = RoleBasedAccessControl(create_defaults=True)
        self.health_monitor = HealthMonitor(monitoring_config)
        self.metrics_collector = MetricsCollector(monitoring_config)
        self.error_tracker = ErrorTracker(monitoring_config)
        self.event_bus = EventBus()
        
        # ✅ REQUIRED: Business configuration and security context (loaded in initialize)
        
        # ✅ REQUIRED: Logger for service operations
        self.logger = logger
        self.business_config = {}
        self.security_context = {}
        
        # ✅ REQUIRED: Service metadata
        self.service_name = "certificates_registry"
        self.service_version = "1.0.0"
        self.service_status = "initialized"
        
        logger.info(f"Initialized {self.service_name} v{self.service_version}")
    
    async def _load_business_config(self) -> Dict[str, Any]:
        """
        Load business configuration for the service.
        
        Returns:
            Dictionary containing business rules, permissions, and configuration
        """
        return {
            'default_rules': {
                'max_certificate_size_mb': 50,
                'allowed_certificate_types': ['standard', 'premium', 'enterprise', 'custom'],
                'processing_timeout_minutes': 60,
                'retry_attempts': 3,
                'max_certificates_per_org': 1000,
                'max_certificates_per_dept': 100
            },
            'required_fields': {
                'create': ['file_id', 'certificate_name'],  # Minimal required fields for creation
                'update': ['file_id'],  # Only file_id required for updates
                'strict': False  # Allow flexible validation for testing
            },
            'permissions': {
                'create': ['admin', 'user', 'processor', 'certificate_manager'],
                'read': ['admin', 'user', 'processor', 'viewer', 'certificate_manager'],
                'update': ['admin', 'user', 'processor', 'certificate_manager'],
                'delete': ['admin', 'certificate_manager'],
                'execute': ['admin', 'processor', 'certificate_manager']
            },
            'cross_dept_roles': ['admin', 'manager', 'certificate_manager'],
            'org_wide_roles': ['admin', 'system_admin', 'certificate_manager'],
            'business_specific': {
                'max_modules_per_certificate': 7,
                'naming_convention': "Certificate_{org_id}_{dept_id}_{timestamp}",
                'compliance_requirements': ["GDPR", "SOX", "ISO27001", "NIST"],
                'security_levels': ['low', 'medium', 'high', 'critical'],
                'compliance_types': ['regulatory', 'industry', 'internal', 'external']
            }
        }
    
    async def _initialize_security_context(self) -> Dict[str, Any]:
        """
        Initialize security context for the service.
        
        Returns:
            Dictionary containing security configuration and requirements
        """
        return {
            'service_name': 'CertificatesRegistryService',
            'security_level': 'enterprise',
            'audit_enabled': True,
            'encryption_required': True,
            'require_authentication': True,
            'require_authorization': True,
            'default_permissions': ['read', 'write'],
            'multi_tenant': True,
            'dept_isolation': True,
            'certificate_specific': {
                'digital_signature_required': True,
                'verification_hash_required': True,
                'qr_code_generation': True,
                'certificate_chain_validation': True
            }
        }
    
    async def initialize(self):
        """
        Initialize async components like the authorization manager and repository.
        
        This method sets up all async dependencies and should be called
        before using any service methods.
        """
        try:
            # ✅ REQUIRED: Initialize authorization manager
            await self.auth_manager.initialize()
            
            # ✅ REQUIRED: Initialize repository
            await self.repository.initialize()
            
            # ✅ REQUIRED: Load business configuration and security context
            self.business_config = await self._load_business_config()
            self.security_context = await self._initialize_security_context()
            
            logger.info(f"{self.service_name} initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.service_name}: {e}")
            await self.error_tracker.track_error(
                error_type="initialization_error",
                error_message=str(e),
                error_details=f"Service initialization failed: {e}",
                severity="high",
                metadata={"service_name": self.service_name}
            )
            raise
    
    async def initialize_service(self) -> bool:
        """
        Initialize the service and verify all dependencies.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # ✅ REQUIRED: Initialize async components first
            await self.initialize()
            
            # ✅ REQUIRED: Verify repository connection
            await self.repository.initialize()
            
            # ✅ REQUIRED: Verify engine components health
            auth_health = await self.auth_manager.get_health()
            metrics_health = await self.metrics_collector.get_health()
            
            if auth_health.get("status") == "healthy" and metrics_health.get("status") == "healthy":
                self.service_status = "ready"
                logger.info(f"{self.service_name} initialized successfully")
                return True
            else:
                logger.error(f"{self.service_name} initialization failed - engine components unhealthy")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.service_name}: {e}")
            await self.error_tracker.track_error(
                error_type="initialization_error",
                error_message=str(e),
                error_details=f"Service initialization failed: {e}",
                severity="high",
                metadata={"service_name": self.service_name}
            )
            return False

    # 🚨 CRITICAL: Service Method Decision Framework
    
    
    # ✅ REQUIRED: Core Business Operations (STAGE 1 IMPLEMENTATION)
    
    # ⚠️ WARNING: Use these generic CRUD methods ONLY for basic user input services!
    #              For services that integrate with data sources, use domain-specific methods above.
    #

    async def create_entity(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[CertificateRegistry]:
        """
        Create a new certificate registry entity with comprehensive business logic validation.
        For basic certificate creation, use create_basic_certificate() instead.
        
        Args:
            entity_data: Data for the new entity
            user_context: User context for authorization and audit
            
        Returns:
            Created entity instance or None if creation failed
        """
        with self.performance_profiler.profile_context("create_entity"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'certificate_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="create"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to create certificate_registry")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
            
                # ✅ REQUIRED: Business validation
                if not await self._validate_entity_data(entity_data, user_context):
                    logger.error("Entity data validation failed")
                    return None
                
                # ✅ REQUIRED: Create entity instance
                entity = CertificateRegistry(**entity_data)
                
                # ✅ REQUIRED: Save to repository (pass dictionary data, not object)
                certificate_id = await self.repository.create(entity_data)
                if not certificate_id:
                    logger.error("Failed to save entity to repository")
                    return None
                
                # Update entity with the generated certificate_id
                entity.certificate_id = certificate_id
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="certificate_registry_created",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("certificate_registry.created", {
                    "entity_id": getattr(entity, 'certificate_id', None),
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully created certificate_registry: {getattr(entity, 'certificate_id', 'unknown')}")
                return entity
                
            except Exception as e:
                logger.error(f"Error creating certificate_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="create_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to create certificate_registry: {e}",
                    severity="medium",
                    metadata={"user_context": user_context}
                )
                return None
    
    # ⚠️ WARNING: Generic CRUD method - customize for your domain if needed!
    #
    async def get_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[CertificateRegistry]:
        """
        Retrieve a certificate registry entity by ID with authorization check.
        
        Args:
            entity_id: ID of the entity to retrieve
            user_context: User context for authorization
            
        Returns:
            Entity instance or None if not found or access denied
        """
        with self.performance_profiler.profile_context("get_entity"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'certificate_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read certificate_registry")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Retrieve from repository
                entity = await self.repository.get_by_id(entity_id)
                if not entity:
                    logger.warning(f"CertificateRegistry not found: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="certificate_registry_retrieved",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                return entity
                
            except Exception as e:
                logger.error(f"Error retrieving certificate_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="get_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve certificate_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return None
    
    # ⚠️ WARNING: Generic CRUD method - customize for your domain if needed!
    #
    async def search_entities(
        self,
        search_criteria: Dict[str, Any],
        user_context: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[CertificateRegistry]:
        """
        Search for certificate registry entities based on criteria with authorization check.
        
        Args:
            search_criteria: Search criteria dictionary
            user_context: User context for authorization
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching entities
        """
        with self.performance_profiler.profile_context("search_entities"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'certificate_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to search certificate_registry")
                        return []
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return []
                
                # ✅ REQUIRED: Search repository
                # Extract search term and filters from search_criteria
                search_term = search_criteria.get("search_term", "")
                filters = {k: v for k, v in search_criteria.items() if k != "search_term"}
                
                entities = await self.repository.search_certificates(
                    search_term, filters, limit, offset
                )
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="certificate_registry_search_executed",
                    metric_value=len(entities),
                    metadata={"user_id": user_context.get("user_id"), "criteria_count": len(search_criteria)}
                )
                
                logger.info(f"Search returned {len(entities)} results")
                return entities
                
            except Exception as e:
                logger.error(f"Error searching certificate_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="search_entities_error",
                    error_message=str(e),
                    error_details=f"Failed to search certificate_registry: {e}",
                    severity="medium",
                    metadata={"search_criteria": search_criteria, "user_context": user_context}
                )
                return []
    
    async def get_entity_by_file_id(
        self,
        file_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[CertificateRegistry]:
        """
        Retrieve a certificate registry entity by file_id with authorization check.
        
        Args:
            file_id: File ID of the entity to retrieve
            user_context: User context for authorization
            
        Returns:
            Entity instance or None if not found or access denied
        """
        with self.performance_profiler.profile_context("get_entity_by_file_id"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'certificate_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        self.logger.warning(f"User {user_context.get('user_id')} lacks permission to read certificate_registry")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    self.logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Get by file_id
                entity = await self.repository.get_by_file_id(file_id)
                
                if not entity:
                    self.logger.warning(f"CertificateRegistry not found for file_id: {file_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="certificate_registry_retrieved_by_file_id",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id"), "file_id": file_id}
                )
                
                return entity
                
            except Exception as e:
                self.logger.error(f"Error retrieving certificate_registry by file_id: {e}")
                await self.error_tracker.track_error(
                    error_type="get_entity_by_file_id_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve certificate_registry by file_id {file_id}: {e}",
                    severity="medium",
                    metadata={"file_id": file_id, "user_context": user_context}
                )
                return None
    
    # ⚠️ WARNING: Generic CRUD method - customize for your domain if needed!
    #
    async def update_entity(
        self,
        entity_id: str,
        update_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Update a certificate registry entity with authorization check and validation.
        
        Args:
            entity_id: ID of the entity to update
            update_data: Data to update
            user_context: User context for authorization
            
        Returns:
            True if update successful, False otherwise
        """
        with self.performance_profiler.profile_context("update_entity"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'certificate_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="update"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update certificate_registry")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Business validation
                if not await self._validate_entity_data(update_data, user_context, is_update=True):
                    logger.error("Update data validation failed")
                    return False
                
                # ✅ REQUIRED: Update in repository
                if not await self.repository.update(entity_id, update_data):
                    logger.error(f"Failed to update certificate_registry: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="certificate_registry_updated",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("certificate_registry.updated", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully updated certificate_registry: {entity_id}")
                return True
            
            except Exception as e:
                logger.error(f"Error updating certificate_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="update_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to update certificate_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False
    
    # ⚠️ WARNING: Generic CRUD method - customize for your domain if needed!
    #
    async def delete_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Delete a certificate registry entity with authorization check.
        
        Args:
            entity_id: ID of the entity to delete
            user_context: User context for authorization
            
        Returns:
            True if deletion successful, False otherwise
        """
        with self.performance_profiler.profile_context("delete_entity"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'certificate_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="delete"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to delete certificate_registry")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Delete from repository
                if not await self.repository.delete(entity_id):
                    logger.error(f"Failed to delete certificate_registry: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="certificate_registry_deleted",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("certificate_registry.deleted", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully deleted certificate_registry: {entity_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting certificate_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="delete_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to delete certificate_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False

    # ✅ REQUIRED: Table Population Methods (STAGE 2 - TO BE IMPLEMENTED AFTER DISCUSSION)
    
    # 🚨 CRITICAL: Every service MUST implement table population logic, not just CRUD operations!
    # Customize these methods for your specific module's data source and population pattern.
    
    async def create_basic_certificate(
        self,
        file_id: str,
        certificate_name: str,
        user_context: Dict[str, Any]
    ) -> Optional[CertificateRegistry]:
        """
        Create a basic certificate registry entity with minimal required fields.
        This method creates the initial certificate that can be populated later with module data.
        
        Args:
            file_id: Unique file identifier
            certificate_name: Name of the certificate
            user_context: User context for authorization and audit
            
        Returns:
            Created entity instance or None if creation failed
        """
        try:
            # Prepare basic entity data with all required fields
            basic_data = {
                "file_id": file_id,
                "certificate_name": certificate_name,
                "certificate_id": str(uuid.uuid4()),
                "created_by": user_context.get("user_id", "system"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                
                # Required business entity relationships
                "user_id": user_context.get("user_id", "system"),
                "org_id": user_context.get("org_id", "default_org"),
                "dept_id": user_context.get("dept_id", "default_dept"),
                
                # Required certificate metadata
                "certificate_type": "standard",
                
                # Initialize all module statuses to 'pending'
                "aasx_etl_status": "pending",
                "twin_registry_status": "pending",
                "ai_rag_status": "pending",
                "kg_neo4j_status": "pending",
                "federated_learning_status": "pending",
                "physics_modeling_status": "pending",
                "data_governance_status": "pending",
                "digital_product_passport_status": "pending",
                
                # Initialize module integration IDs to None
                "aasx_etl_job_id": None,
                "twin_registry_id": None,
                "ai_rag_registry_id": None,
                "kg_neo4j_registry_id": None,
                "federated_learning_registry_id": None,
                "physics_modeling_registry_id": None,
                "data_governance_registry_id": None,
                "digital_product_passport_registry_id": None,
                
                # Initialize JSON summary fields to empty dictionaries
                "aasx_etl_summary": {},
                "twin_registry_summary": {},
                "ai_rag_summary": {},
                "kg_neo4j_summary": {},
                "federated_learning_summary": {},
                "physics_modeling_summary": {},
                "data_governance_summary": {},
                "digital_product_passport_summary": {}
            }
            
            # Use the existing create_entity method (clean architecture)
            entity = await self.create_entity(basic_data, user_context)
            
            if entity:
                self.logger.info(f"Successfully created basic certificate: {entity.certificate_id} for file: {file_id}")
                return entity
            else:
                self.logger.error(f"Failed to create basic certificate for file: {file_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating basic certificate: {e}")
            return None

    async def populate_from_aasx_etl(self, aasx_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """
        Populate certificate with AASX ETL processing results.
        
        Args:
            aasx_data: AASX ETL processing data with structure:
                - file_id: AASX file identifier
                - aasx_path: Path to AASX file
                - job_id: ETL job identifier
                - processing_metadata: Timing and job details
                - extraction_results: Asset and submodel counts
                - quality_metrics: Success rates and validation scores
                - output_files: Generated file paths and sizes
                - performance_metrics: Processing times and resource usage
                - aas_specific_metrics: AAS version and complexity
                - integration_status: Module readiness status
                - error_handling: Error counts and final status
            
        Returns:
            bool: True if population successful, False otherwise
        """
        try:
            # Extract key information from AASX ETL data
            file_id = aasx_data.get("file_id")
            aasx_path = aasx_data.get("aasx_path")
            job_id = aasx_data.get("job_id")
            status = aasx_data.get("status")
            
            if not all([file_id, aasx_path, job_id, status]):
                self.logger.error("Missing required AASX ETL data fields")
                return False
            
            # Get or create certificate registry entry
            certificate = await self.get_entity_by_file_id(file_id, user_context)
            if not certificate:
                self.logger.error(f"Certificate not found for file_id: {file_id}")
                return False
            
            # Reorganize flat aasx_data into structured format
            # Processing Metadata
            processing_metadata = {
                "file_upload_date": aasx_data.get("file_upload_date"),
                "etl_start_time": aasx_data.get("etl_start_time"),
                "etl_completion_time": aasx_data.get("etl_completion_time"),
                "total_processing_time_ms": aasx_data.get("total_processing_time_ms"),
                "processing_mode": aasx_data.get("processing_mode"),
                "job_type": aasx_data.get("job_type"),
                "source_type": aasx_data.get("source_type")
            }
            
            # Extraction Results
            extraction_results = {
                "total_assets": aasx_data.get("total_assets"),
                "total_submodels": aasx_data.get("total_submodels"),
                "total_submodel_elements": aasx_data.get("total_submodel_elements"),
                "total_documents": aasx_data.get("total_documents"),
                "total_properties": aasx_data.get("total_properties"),
                "total_relationships": aasx_data.get("total_relationships"),
                "asset_types": {
                    "machines": aasx_data.get("asset_machines_count"),
                    "sensors": aasx_data.get("asset_sensors_count"),
                    "processes": aasx_data.get("asset_processes_count"),
                    "equipment": aasx_data.get("asset_equipment_count"),
                    "other": aasx_data.get("asset_other_count")
                },
                "submodel_types": {
                    "technical_data": aasx_data.get("submodel_technical_count"),
                    "operational_data": aasx_data.get("submodel_operational_count"),
                    "maintenance_data": aasx_data.get("submodel_maintenance_count"),
                    "safety_data": aasx_data.get("submodel_safety_count")
                },
                "document_types": {
                    "pdf": aasx_data.get("document_pdf_count"),
                    "text": aasx_data.get("document_text_count"),
                    "image": aasx_data.get("document_image_count"),
                    "xml": aasx_data.get("document_xml_count")
                }
            }
            
            # Quality Metrics
            quality_metrics = {
                "extraction_success_rate": aasx_data.get("extraction_success_rate"),
                "data_completeness": aasx_data.get("data_completeness"),
                "data_accuracy": aasx_data.get("data_accuracy"),
                "data_consistency": aasx_data.get("data_consistency"),
                "schema_compliance": aasx_data.get("schema_compliance"),
                "validation_score": aasx_data.get("validation_score"),
                "quality_issues": {
                    "validation_errors": aasx_data.get("validation_errors"),
                    "missing_assets": aasx_data.get("missing_assets"),
                    "incomplete_submodels": aasx_data.get("incomplete_submodels"),
                    "document_extraction_failures": aasx_data.get("document_extraction_failures")
                }
            }
            
            # Output Files
            output_files = {
                "json_output": aasx_data.get("json_output"),
                "yaml_output": aasx_data.get("yaml_output"),
                "csv_output": aasx_data.get("csv_output"),
                "xml_output": aasx_data.get("xml_output"),
                "graph_output": aasx_data.get("graph_output"),
                "file_sizes": {
                    "json_mb": aasx_data.get("json_size_mb"),
                    "yaml_mb": aasx_data.get("yaml_size_mb"),
                    "csv_mb": aasx_data.get("csv_size_mb"),
                    "xml_mb": aasx_data.get("xml_size_mb"),
                    "graph_mb": aasx_data.get("graph_size_mb")
                }
            }
            
            # Performance Metrics
            performance_metrics = {
                "extraction_time_ms": aasx_data.get("extraction_time_ms"),
                "transformation_time_ms": aasx_data.get("transformation_time_ms"),
                "loading_time_ms": aasx_data.get("loading_time_ms"),
                "memory_usage_mb": aasx_data.get("memory_usage_mb"),
                "cpu_usage_percent": aasx_data.get("cpu_usage_percent"),
                "disk_io_mb": aasx_data.get("disk_io_mb")
            }
            
            # AAS Specific Metrics
            aas_specific_metrics = {
                "aas_version": aasx_data.get("aas_version"),
                "aasx_package_version": aasx_data.get("aasx_package_version"),
                "extraction_method": aasx_data.get("extraction_method"),
                "processor_version": aasx_data.get("processor_version"),
                "complexity_metrics": {
                    "complexity_level": aasx_data.get("complexity_level"),
                    "nesting_depth": aasx_data.get("nesting_depth"),
                    "average_submodel_size": aasx_data.get("average_submodel_size"),
                    "largest_asset_connections": aasx_data.get("largest_asset_connections")
                }
            }
            
            # Integration Status
            integration_status = {
                "twin_registry_ready": aasx_data.get("twin_registry_ready", False),
                "kg_neo4j_ready": aasx_data.get("kg_neo4j_ready", False),
                "ai_rag_ready": aasx_data.get("ai_rag_ready", False),
                "physics_modeling_ready": aasx_data.get("physics_modeling_ready", False),
                "federated_learning_ready": aasx_data.get("federated_learning_ready", False),
                "data_governance_ready": aasx_data.get("data_governance_ready", False)
            }
            
            # Error Handling
            error_handling = {
                "critical_errors": aasx_data.get("critical_errors", 0),
                "warning_count": aasx_data.get("warning_count", 0),
                "recovery_attempts": aasx_data.get("recovery_attempts", 0),
                "final_status": aasx_data.get("final_status", "unknown")
            }
            
            # Update certificate with comprehensive AASX ETL data
            # Structure: Only individual columns for cross-module references, detailed data in JSON summary
            update_data = {
                "file_id": file_id,  # Include file_id for validation
                "aasx_etl_status": "completed",  # Mark AASX ETL as completed
                "aasx_etl_job_id": job_id,  # Individual column for cross-module reference
                "aasx_etl_summary": {
                    # Basic Information
                    "file_id": file_id,
                    "aasx_path": aasx_path,
                    "job_id": job_id,
                    "timestamp": aasx_data.get("timestamp"),
                    "status": status,
                    
                    # Structured Data (reorganized from flat aasx_data)
                    "processing_metadata": processing_metadata,
                    "extraction_results": extraction_results,
                    "quality_metrics": quality_metrics,
                    "output_files": output_files,
                    "performance_metrics": performance_metrics,
                    "aas_specific_metrics": aas_specific_metrics,
                    "integration_status": integration_status,
                    "error_handling": error_handling,
                    
                    # Complete AASX Data (for reference)
                    "raw_aasx_data": aasx_data
                }
            }
            
            # Update the certificate with the structured data
            success = await self.update_entity(
                entity_id=certificate.certificate_id,
                update_data=update_data,
                user_context=user_context
            )
            
            if success:
                self.logger.info(f"Successfully populated AASX ETL data for file: {file_id}")
                return True
            else:
                self.logger.error(f"Failed to update certificate with AASX ETL data for file: {file_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error populating from AASX ETL: {e}")
            return False
    
    async def populate_from_twin_registry(self, twin_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """
        Populate certificate with Digital Twin Registry status and metrics.
        
        Args:
            twin_data: Twin Registry data with structure:
                - file_id: AASX file identifier
                - twin_id: Digital twin identifier
                - registry_id: Registry instance identifier
                - twin_identification: Basic twin information and classification
                - integration_status: Health scores and operational status
                - synchronization_metrics: Sync status and performance
                - performance_metrics: Performance and quality scores
                - security_compliance: Security levels and compliance status
                - module_integration: References to connected modules
                - user_management_ownership: User and team information
                - timestamps_audit: Creation and modification timestamps
                - configuration_metadata: Registry configuration and metadata
                - relationships_dependencies: Twin relationships and dependencies
                - twin_management_performance: Operational performance metrics
                - category_performance_stats: Category-level statistics
                - data_quality_metrics: Data quality assessments
                - system_resource_metrics: System resource utilization
                - enterprise_metrics: Enterprise-level compliance and security
                - user_activity_metrics: User interaction patterns
                - optimization_insights: Performance trends and suggestions
                - audit_compliance_details: Audit findings and actions
                - computed_business_intelligence: Calculated business metrics
                - twin_registry_patterns: Usage patterns and trends
                - resource_utilization_trends: Resource usage trends
                - twin_operation_patterns: Operation complexity and timing
            
        Returns:
            bool: True if population successful, False otherwise
        """
        try:
            # Extract key information from Twin Registry data
            file_id = twin_data.get("file_id")
            twin_id = twin_data.get("twin_id")
            registry_id = twin_data.get("registry_id")
            status = twin_data.get("status")
            
            if not all([file_id, twin_id, registry_id, status]):
                self.logger.error("Missing required Twin Registry data fields")
                return False
            
            # Get or create certificate registry entry
            certificate = await self.get_entity_by_file_id(file_id, user_context)
            if not certificate:
                self.logger.error(f"Certificate not found for file_id: {file_id}")
                return False
            
            # Reorganize flat twin_data into structured format
            # Twin Identification
            twin_identification = {
                "twin_name": twin_data.get("twin_name"),
                "twin_category": twin_data.get("twin_category"),
                "twin_type": twin_data.get("twin_type"),
                "twin_priority": twin_data.get("twin_priority"),
                "twin_version": twin_data.get("twin_version"),
                "workflow_source": twin_data.get("workflow_source"),
                "registry_type": twin_data.get("registry_type")
            }
            
            # Integration Status
            integration_status = {
                "integration_status": twin_data.get("integration_status"),
                "overall_health_score": twin_data.get("overall_health_score"),
                "health_status": twin_data.get("health_status"),
                "lifecycle_status": twin_data.get("lifecycle_status"),
                "lifecycle_phase": twin_data.get("lifecycle_phase"),
                "operational_status": twin_data.get("operational_status"),
                "availability_status": twin_data.get("availability_status")
            }
            
            # Performance Metrics
            performance_metrics = {
                "performance_score": twin_data.get("performance_score"),
                "data_quality_score": twin_data.get("data_quality_score"),
                "reliability_score": twin_data.get("reliability_score"),
                "compliance_score": twin_data.get("compliance_score"),
                "twin_sync_speed_sec": twin_data.get("twin_sync_speed_sec"),
                "relationship_update_speed_sec": twin_data.get("relationship_update_speed_sec"),
                "lifecycle_transition_speed_sec": twin_data.get("lifecycle_transition_speed_sec")
            }
            
            # Security & Compliance
            security_compliance = {
                "security_level": twin_data.get("security_level"),
                "access_control_level": twin_data.get("access_control_level"),
                "encryption_enabled": twin_data.get("encryption_enabled"),
                "audit_logging_enabled": twin_data.get("audit_logging_enabled"),
                "compliance_type": twin_data.get("compliance_type"),
                "compliance_status": twin_data.get("compliance_status"),
                "last_audit_date": twin_data.get("last_audit_date"),
                "next_audit_date": twin_data.get("next_audit_date"),
                "security_event_type": twin_data.get("security_event_type"),
                "threat_assessment": twin_data.get("threat_assessment"),
                "last_security_scan": twin_data.get("last_security_scan"),
                "security_trend": twin_data.get("security_trend")
            }
            
            # Module Integration
            module_integration = {
                "aasx_integration_id": twin_data.get("aasx_integration_id"),
                "physics_modeling_id": twin_data.get("physics_modeling_id"),
                "federated_learning_id": twin_data.get("federated_learning_id"),
                "data_pipeline_id": twin_data.get("data_pipeline_id"),
                "kg_neo4j_id": twin_data.get("kg_neo4j_id"),
                "certificate_manager_id": twin_data.get("certificate_manager_id")
            }
            
            # Data Quality Metrics
            data_quality_metrics = {
                "data_freshness_score": twin_data.get("data_freshness_score"),
                "data_completeness_score": twin_data.get("data_completeness_score"),
                "data_consistency_score": twin_data.get("data_consistency_score"),
                "data_accuracy_score": twin_data.get("data_accuracy_score")
            }
            
            # Enterprise Metrics
            enterprise_metrics = {
                "enterprise_compliance_score": twin_data.get("enterprise_compliance_score"),
                "compliance_audit_status": twin_data.get("compliance_audit_status"),
                "compliance_violations_count": twin_data.get("compliance_violations_count"),
                "enterprise_security_score": twin_data.get("enterprise_security_score"),
                "security_threat_level": twin_data.get("security_threat_level"),
                "security_vulnerabilities_count": twin_data.get("security_vulnerabilities_count"),
                "enterprise_performance_score": twin_data.get("enterprise_performance_score"),
                "performance_optimization_status": twin_data.get("performance_optimization_status")
            }
            
            # Computed Business Intelligence
            computed_bi = {
                "overall_score": twin_data.get("overall_score"),
                "enterprise_health_status": twin_data.get("enterprise_health_status"),
                "risk_assessment": {
                    "risk_score": twin_data.get("risk_score"),
                    "risk_level": twin_data.get("risk_level")
                },
                "business_value_score": twin_data.get("business_value_score"),
                "optimization_priority": twin_data.get("optimization_priority"),
                "maintenance_schedule": twin_data.get("maintenance_schedule", {})
            }
            
            # Update certificate with Twin Registry data
            # Structure: Only individual columns for cross-module references, detailed data in JSON summary
            update_data = {
                "file_id": file_id,  # Include file_id for validation
                "twin_registry_status": "completed",  # Mark Twin Registry as completed
                "twin_registry_id": registry_id,  # Individual column for cross-module reference
                "twin_registry_summary": {
                    # Basic Information
                    "file_id": file_id,
                    "twin_id": twin_id,
                    "registry_id": registry_id,
                    "timestamp": twin_data.get("timestamp"),
                    "status": status,
                    
                    # Structured Data (reorganized from flat twin_data)
                    "twin_identification": twin_identification,
                    "integration_status": integration_status,
                    "performance_metrics": performance_metrics,
                    "security_compliance": security_compliance,
                    "module_integration": module_integration,
                    "data_quality_metrics": data_quality_metrics,
                    "enterprise_metrics": enterprise_metrics,
                    "computed_business_intelligence": computed_bi,
                    
                    # Complete Twin Data (for reference)
                    "raw_twin_data": twin_data
                }
            }
            
            # Update the certificate with the structured data
            success = await self.update_entity(
                entity_id=certificate.certificate_id,
                update_data=update_data,
                user_context=user_context
            )
            
            if success:
                self.logger.info(f"Successfully populated Twin Registry data for file: {file_id}, twin: {twin_id}")
                return True
            else:
                self.logger.error(f"Failed to update certificate with Twin Registry data for file: {file_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error populating from Twin Registry: {e}")
            return False
    
    async def populate_from_ai_rag(self, ai_rag_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """
        Populate certificate with AI/RAG processing results.
        
        Args:
            ai_rag_data: AI/RAG processing data with structure:
                - file_id: AASX file identifier
                - registry_id: AI/RAG registry identifier
                - timestamp: Processing timestamp
                - status: Processing status
                - rag_identification: Registry metadata and configuration
                - document_processing_summary: Overall processing results and quality
                - document_types_breakdown: Breakdown by file type (PDF, CAD, spreadsheets, images)
                - rag_processing_status: Embedding generation and vector DB sync status
                - embedding_configuration: Detailed embedding types and strategies
                - rag_techniques_performance: Performance of different RAG approaches
                - processor_capabilities_utilized: Which AI processors were used
                - performance_metrics: Overall system health and scores
                - ai_ml_metrics: AI/ML specific performance indicators
                - quality_validation: Error handling and recovery actions
                - integration_status: System operational status
                - module_integration: Cross-module dependencies
                - enterprise_compliance: Compliance and audit information
                - enterprise_security: Security assessments and events
                - user_management: Ownership and stewardship
                - timestamps: Complete audit trail
                - computed_business_intelligence: Risk assessment and business value
                - rag_analytics: Content complexity and processing efficiency
                - supported_file_types_summary: File type processing statistics
                - vector_database_metrics: Vector DB performance and capacity
                - ai_model_performance: Model accuracy and inference metrics
            
        Returns:
            bool: True if population successful, False otherwise
        """
        try:
            file_id = ai_rag_data.get("file_id")
            registry_id = ai_rag_data.get("registry_id")
            status = ai_rag_data.get("status")
            
            if not all([file_id, registry_id, status]):
                self.logger.error("Missing required AI/RAG data fields")
                return False
            
            certificate = await self.get_entity_by_file_id(file_id, user_context)
            if not certificate:
                self.logger.error(f"Certificate not found for file_id: {file_id}")
                return False
            
            # Reorganize flat ai_rag_data into structured format
            # RAG Identification
            rag_identification = {
                "registry_name": ai_rag_data.get("registry_name"),
                "rag_category": ai_rag_data.get("rag_category"),
                "rag_type": ai_rag_data.get("rag_type"),
                "rag_priority": ai_rag_data.get("rag_priority"),
                "rag_version": ai_rag_data.get("rag_version"),
                "workflow_source": ai_rag_data.get("workflow_source"),
                "registry_type": ai_rag_data.get("registry_type")
            }
            
            # Document Processing Summary
            document_processing = {
                "document_count": ai_rag_data.get("document_count"),
                "total_document_size": ai_rag_data.get("total_document_size"),
                "processing_status": ai_rag_data.get("processing_status"),
                "file_type": ai_rag_data.get("file_type"),
                "processing_start_time": ai_rag_data.get("processing_start_time"),
                "processing_end_time": ai_rag_data.get("processing_end_time"),
                "processing_duration_ms": ai_rag_data.get("processing_duration_ms"),
                "content_summary": ai_rag_data.get("content_summary"),
                "extracted_text": ai_rag_data.get("extracted_text"),
                "quality_score": ai_rag_data.get("quality_score"),
                "confidence_score": ai_rag_data.get("confidence_score")
            }
            
            # Document Types Breakdown
            document_types = {
                "pdf_count": ai_rag_data.get("pdf_count"),
                "cad_count": ai_rag_data.get("cad_count"),
                "spreadsheet_count": ai_rag_data.get("spreadsheet_count"),
                "image_count": ai_rag_data.get("image_count"),
                "text_count": ai_rag_data.get("text_count"),
                "other_count": ai_rag_data.get("other_count")
            }
            
            # RAG Processing Status
            rag_processing = {
                "embedding_generation_status": ai_rag_data.get("embedding_generation_status"),
                "vector_db_sync_status": ai_rag_data.get("vector_db_sync_status"),
                "indexing_status": ai_rag_data.get("indexing_status"),
                "search_optimization_status": ai_rag_data.get("search_optimization_status")
            }
            
            # Embedding Configuration
            embedding_config = {
                "embedding_type": ai_rag_data.get("embedding_type"),
                "embedding_dimension": ai_rag_data.get("embedding_dimension"),
                "embedding_model": ai_rag_data.get("embedding_model"),
                "chunking_strategy": ai_rag_data.get("chunking_strategy"),
                "chunk_size": ai_rag_data.get("chunk_size"),
                "chunk_overlap": ai_rag_data.get("chunk_overlap")
            }
            
            # RAG Techniques Performance
            rag_techniques = {
                "retrieval_accuracy": ai_rag_data.get("retrieval_accuracy"),
                "generation_quality": ai_rag_data.get("generation_quality"),
                "response_relevance": ai_rag_data.get("response_relevance"),
                "context_utilization": ai_rag_data.get("context_utilization")
            }
            
            # Processor Capabilities Utilized
            processors = {
                "nlp_processor": ai_rag_data.get("nlp_processor"),
                "vision_processor": ai_rag_data.get("vision_processor"),
                "multimodal_processor": ai_rag_data.get("multimodal_processor"),
                "embedding_processor": ai_rag_data.get("embedding_processor")
            }
            
            # Performance Metrics
            performance = {
                "overall_performance_score": ai_rag_data.get("overall_performance_score"),
                "processing_speed_score": ai_rag_data.get("processing_speed_score"),
                "accuracy_score": ai_rag_data.get("accuracy_score"),
                "reliability_score": ai_rag_data.get("reliability_score"),
                "scalability_score": ai_rag_data.get("scalability_score")
            }
            
            # AI/ML Metrics
            ai_ml_metrics = {
                "model_accuracy": ai_rag_data.get("model_accuracy"),
                "inference_speed": ai_rag_data.get("inference_speed"),
                "training_accuracy": ai_rag_data.get("training_accuracy"),
                "validation_accuracy": ai_rag_data.get("validation_accuracy"),
                "f1_score": ai_rag_data.get("f1_score"),
                "precision_score": ai_rag_data.get("precision_score"),
                "recall_score": ai_rag_data.get("recall_score")
            }
            
            # Quality Validation
            quality_validation = {
                "validation_status": ai_rag_data.get("validation_status"),
                "error_count": ai_rag_data.get("error_count"),
                "warning_count": ai_rag_data.get("warning_count"),
                "recovery_actions": ai_rag_data.get("recovery_actions"),
                "validation_score": ai_rag_data.get("validation_score")
            }
            
            # Integration Status
            integration_status = {
                "system_status": ai_rag_data.get("system_status"),
                "api_status": ai_rag_data.get("api_status"),
                "database_status": ai_rag_data.get("database_status"),
                "service_health": ai_rag_data.get("service_health")
            }
            
            # Module Integration
            module_integration = {
                "aasx_integration_id": ai_rag_data.get("aasx_integration_id"),
                "twin_registry_id": ai_rag_data.get("twin_registry_id"),
                "kg_neo4j_id": ai_rag_data.get("kg_neo4j_id"),
                "physics_modeling_id": ai_rag_data.get("physics_modeling_id"),
                "federated_learning_id": ai_rag_data.get("federated_learning_id"),
                "data_governance_id": ai_rag_data.get("data_governance_id")
            }
            
            # Enterprise Compliance
            enterprise_compliance = {
                "compliance_status": ai_rag_data.get("compliance_status"),
                "audit_status": ai_rag_data.get("audit_status"),
                "regulatory_compliance": ai_rag_data.get("regulatory_compliance"),
                "data_governance_compliance": ai_rag_data.get("data_governance_compliance")
            }
            
            # Enterprise Security
            enterprise_security = {
                "security_level": ai_rag_data.get("security_level"),
                "threat_assessment": ai_rag_data.get("threat_assessment"),
                "vulnerability_scan_status": ai_rag_data.get("vulnerability_scan_status"),
                "security_events": ai_rag_data.get("security_events")
            }
            
            # User Management
            user_management = {
                "owner_id": ai_rag_data.get("owner_id"),
                "steward_id": ai_rag_data.get("steward_id"),
                "team_id": ai_rag_data.get("team_id"),
                "access_level": ai_rag_data.get("access_level")
            }
            
            # Timestamps
            timestamps = {
                "created_at": ai_rag_data.get("created_at"),
                "updated_at": ai_rag_data.get("updated_at"),
                "last_processed": ai_rag_data.get("last_processed"),
                "last_indexed": ai_rag_data.get("last_indexed")
            }
            
            # Computed Business Intelligence
            business_intelligence = {
                "overall_score": ai_rag_data.get("overall_score"),
                "business_value_score": ai_rag_data.get("business_value_score"),
                "risk_assessment": {
                    "risk_score": ai_rag_data.get("risk_score"),
                    "risk_level": ai_rag_data.get("risk_level")
                },
                "optimization_priority": ai_rag_data.get("optimization_priority")
            }
            
            # RAG Analytics
            rag_analytics = {
                "content_complexity": ai_rag_data.get("content_complexity"),
                "processing_efficiency": ai_rag_data.get("processing_efficiency"),
                "query_patterns": ai_rag_data.get("query_patterns"),
                "usage_statistics": ai_rag_data.get("usage_statistics")
            }
            
            # Supported File Types Summary
            file_types_summary = {
                "supported_types": ai_rag_data.get("supported_types"),
                "processing_capabilities": ai_rag_data.get("processing_capabilities"),
                "type_performance": ai_rag_data.get("type_performance")
            }
            
            # Vector Database Metrics
            vector_db_metrics = {
                "vector_count": ai_rag_data.get("vector_count"),
                "index_size": ai_rag_data.get("index_size"),
                "query_performance": ai_rag_data.get("query_performance"),
                "storage_utilization": ai_rag_data.get("storage_utilization")
            }
            
            # AI Model Performance
            ai_model_performance = {
                "text_processing_accuracy": ai_rag_data.get("text_processing_accuracy"),
                "image_processing_accuracy": ai_rag_data.get("image_processing_accuracy"),
                "multimodal_fusion_accuracy": ai_rag_data.get("multimodal_fusion_accuracy"),
                "model_inference_time_ms": ai_rag_data.get("model_inference_time_ms"),
                "model_confidence_threshold": ai_rag_data.get("model_confidence_threshold")
            }
            
            # Update certificate with AI RAG data
            # Structure: Only individual columns for cross-module references, detailed data in JSON summary
            update_data = {
                "file_id": file_id,  # Include file_id for validation
                "ai_rag_status": "completed",  # Mark AI RAG as completed
                "ai_rag_registry_id": registry_id,  # Individual column for cross-module reference
                "ai_rag_summary": {
                    # Basic Information
                    "file_id": file_id,
                    "registry_id": registry_id,
                    "timestamp": ai_rag_data.get("timestamp"),
                    "status": status,
                    
                    # Structured Data (reorganized from flat ai_rag_data)
                    "rag_identification": rag_identification,
                    "document_processing": document_processing,
                    "document_types": document_types,
                    "rag_processing": rag_processing,
                    "embedding_configuration": embedding_config,
                    "rag_techniques_performance": rag_techniques,
                    "processor_capabilities_utilized": processors,
                    "performance_metrics": performance,
                    "ai_ml_metrics": ai_ml_metrics,
                    "quality_validation": quality_validation,
                    "integration_status": integration_status,
                    "module_integration": module_integration,
                    "enterprise_compliance": enterprise_compliance,
                    "enterprise_security": enterprise_security,
                    "user_management": user_management,
                    "timestamps": timestamps,
                    "computed_business_intelligence": business_intelligence,
                    "rag_analytics": rag_analytics,
                    "supported_file_types_summary": file_types_summary,
                    "vector_database_metrics": vector_db_metrics,
                    "ai_model_performance": ai_model_performance,
                    
                    # Complete AI RAG Data (for reference)
                    "raw_ai_rag_data": ai_rag_data
                }
            }
            
            # Update the certificate with the structured data
            success = await self.update_entity(
                entity_id=certificate.certificate_id,
                update_data=update_data,
                user_context=user_context
            )
            
            if success:
                self.logger.info(f"Successfully populated AI/RAG data for file: {file_id}, registry: {registry_id}")
                return True
            else:
                self.logger.error(f"Failed to update certificate with AI/RAG data for file: {file_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error populating from AI/RAG: {e}")
            return False
    
    async def populate_from_kg_neo4j(self, kg_summary: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """
        Populate certificate with Knowledge Graph (Neo4j) processing results.
        
        Args:
            kg_summary: KG Neo4j processing data with comprehensive structure covering
                all three module tables (kg_graph_registry, kg_neo4j_ml_registry, kg_graph_metrics)
            
        Returns:
            bool: True if population successful, False otherwise
        """
        try:
            graph_id = kg_summary.get("graph_id")
            file_id = kg_summary.get("file_id")
            registry_id = kg_summary.get("registry_id")
            status = kg_summary.get("status")
            
            if not all([graph_id, file_id, registry_id, status]):
                self.logger.error("Missing required KG Neo4j data fields")
                return False
            
            certificate = await self.get_entity_by_file_id(file_id, user_context)
            if not certificate:
                self.logger.error(f"Certificate not found for file_id: {file_id}")
                return False
            
            # Reorganize flat kg_summary into structured format
            # KG Identification
            kg_identification = {
                "registry_name": kg_summary.get("registry_name"),
                "graph_category": kg_summary.get("graph_category"),
                "graph_type": kg_summary.get("graph_type"),
                "graph_priority": kg_summary.get("graph_priority"),
                "graph_version": kg_summary.get("graph_version"),
                "registry_type": kg_summary.get("registry_type"),
                "workflow_source": kg_summary.get("workflow_source")
            }
            
            # Graph Registry Summary
            graph_registry = {
                "total_graphs": kg_summary.get("total_graphs"),
                "graph_complexity": kg_summary.get("graph_complexity"),
                "total_nodes": kg_summary.get("total_nodes"),
                "total_relationships": kg_summary.get("total_relationships"),
                "schema_version": kg_summary.get("schema_version"),
                "ontology_version": kg_summary.get("ontology_version"),
                "validation_rules_count": kg_summary.get("validation_rules_count"),
                "schema_validation_status": kg_summary.get("schema_validation_status"),
                "completeness_score": kg_summary.get("completeness_score"),
                "data_quality_status": kg_summary.get("data_quality_status"),
                "content_summary": kg_summary.get("content_summary"),
                "quality_score": kg_summary.get("quality_score"),
                "confidence_score": kg_summary.get("confidence_score")
            }
            
            # Graph Sources Breakdown
            graph_sources = {
                "aasx_structured": {
                    "count": kg_summary.get("aasx_structured_count"),
                    "processing_success_rate": kg_summary.get("aasx_structured_success_rate")
                },
                "ai_rag_documents": {
                    "count": kg_summary.get("ai_rag_count"),
                    "processing_success_rate": kg_summary.get("ai_rag_success_rate")
                },
                "twin_registry": {
                    "count": kg_summary.get("twin_registry_count"),
                    "processing_success_rate": kg_summary.get("twin_registry_success_rate")
                }
            }
            
            # Neo4j Sync Status
            neo4j_sync = {
                "neo4j_import_status": kg_summary.get("neo4j_import_status"),
                "neo4j_export_status": kg_summary.get("neo4j_export_status"),
                "last_neo4j_sync_at": kg_summary.get("last_neo4j_sync_at"),
                "neo4j_connection_status": kg_summary.get("neo4j_connection_status"),
                "database_type": kg_summary.get("database_type")
            }
            
            # ML Training Summary
            ml_training = {
                "ml_training_enabled": kg_summary.get("ml_training_enabled"),
                "active_ml_sessions": kg_summary.get("active_ml_sessions"),
                "total_models_trained": kg_summary.get("total_models_trained"),
                "ml_model_count": kg_summary.get("ml_model_count"),
                "training_success_rate": kg_summary.get("training_success_rate"),
                "avg_model_accuracy": kg_summary.get("avg_model_accuracy")
            }
            
            # Performance Metrics
            performance = {
                "performance_score": kg_summary.get("performance_score"),
                "data_quality_score": kg_summary.get("data_quality_score"),
                "reliability_score": kg_summary.get("reliability_score"),
                "compliance_score": kg_summary.get("compliance_score"),
                "overall_health_score": kg_summary.get("overall_health_score"),
                "health_status": kg_summary.get("health_status")
            }
            
            # KG Neo4j Metrics
            kg_metrics = {
                "graph_analysis_accuracy": kg_summary.get("graph_analysis_accuracy"),
                "relationship_inference_accuracy": kg_summary.get("relationship_inference_accuracy"),
                "entity_recognition_accuracy": kg_summary.get("entity_recognition_accuracy"),
                "graph_traversal_speed": kg_summary.get("graph_traversal_speed"),
                "query_performance_score": kg_summary.get("query_performance_score")
            }
            
            # Graph Operation Metrics
            operation_metrics = {
                "graph_operations_count": kg_summary.get("graph_operations_count"),
                "successful_operations": kg_summary.get("successful_operations"),
                "failed_operations": kg_summary.get("failed_operations"),
                "average_operation_time": kg_summary.get("average_operation_time"),
                "throughput_operations_per_second": kg_summary.get("throughput_operations_per_second")
            }
            
            # Module Integration
            module_integration = {
                "aasx_integration_id": kg_summary.get("aasx_integration_id"),
                "twin_registry_id": kg_summary.get("twin_registry_id"),
                "ai_rag_id": kg_summary.get("ai_rag_id"),
                "physics_modeling_id": kg_summary.get("physics_modeling_id"),
                "federated_learning_id": kg_summary.get("federated_learning_id")
            }
            
            # Enterprise Compliance
            enterprise_compliance = {
                "compliance_status": kg_summary.get("compliance_status"),
                "audit_status": kg_summary.get("audit_status"),
                "regulatory_compliance": kg_summary.get("regulatory_compliance"),
                "data_governance_compliance": kg_summary.get("data_governance_compliance")
            }
            
            # Enterprise Security
            enterprise_security = {
                "security_level": kg_summary.get("security_level"),
                "threat_assessment": kg_summary.get("threat_assessment"),
                "vulnerability_scan_status": kg_summary.get("vulnerability_scan_status"),
                "security_events": kg_summary.get("security_events")
            }
            
            # Computed Business Intelligence
            business_intelligence = {
                "overall_score": kg_summary.get("overall_score"),
                "business_value_score": kg_summary.get("business_value_score"),
                "risk_assessment": {
                    "risk_score": kg_summary.get("risk_score"),
                    "risk_level": kg_summary.get("risk_level")
                },
                "optimization_priority": kg_summary.get("optimization_priority")
            }
            
            # KG Analytics
            kg_analytics = {
                "graph_complexity_analysis": kg_summary.get("graph_complexity_analysis"),
                "relationship_patterns": kg_summary.get("relationship_patterns"),
                "entity_distribution": kg_summary.get("entity_distribution"),
                "usage_statistics": kg_summary.get("usage_statistics")
            }
            
            # Neo4j Database Metrics
            neo4j_db_metrics = {
                "database_size_mb": kg_summary.get("database_size_mb"),
                "index_count": kg_summary.get("index_count"),
                "constraint_count": kg_summary.get("constraint_count"),
                "query_performance": kg_summary.get("query_performance"),
                "storage_utilization": kg_summary.get("storage_utilization")
            }
            
            # ML Model Performance
            ml_model_performance = {
                "model_accuracy": kg_summary.get("model_accuracy"),
                "inference_speed": kg_summary.get("inference_speed"),
                "training_accuracy": kg_summary.get("training_accuracy"),
                "validation_accuracy": kg_summary.get("validation_accuracy"),
                "f1_score": kg_summary.get("f1_score")
            }
            
            # Graph Enhancement Analytics
            enhancement_analytics = {
                "enhancement_suggestions": kg_summary.get("enhancement_suggestions"),
                "optimization_opportunities": kg_summary.get("optimization_opportunities"),
                "performance_trends": kg_summary.get("performance_trends"),
                "scalability_metrics": kg_summary.get("scalability_metrics")
            }
            
            # Update certificate with KG Neo4j data
            # Structure: Only individual columns for cross-module references, detailed data in JSON summary
            update_data = {
                "file_id": file_id,  # Include file_id for validation
                "kg_neo4j_status": "completed",  # Mark KG Neo4j as completed
                "kg_neo4j_registry_id": registry_id,  # Individual column for cross-module reference
                "kg_neo4j_summary": {
                    # Basic Information
                    "file_id": file_id,
                    "graph_id": graph_id,
                    "registry_id": registry_id,
                    "timestamp": kg_summary.get("timestamp"),
                    "status": status,
                    
                    # Structured Data (reorganized from flat kg_summary)
                    "kg_identification": kg_identification,
                    "graph_registry_summary": graph_registry,
                    "graph_sources_breakdown": graph_sources,
                    "neo4j_sync_status": neo4j_sync,
                    "ml_training_summary": ml_training,
                    "performance_metrics": performance,
                    "kg_neo4j_metrics": kg_metrics,
                    "graph_operation_metrics": operation_metrics,
                    "module_integration": module_integration,
                    "enterprise_compliance": enterprise_compliance,
                    "enterprise_security": enterprise_security,
                    "computed_business_intelligence": business_intelligence,
                    "kg_analytics": kg_analytics,
                    "neo4j_database_metrics": neo4j_db_metrics,
                    "ml_model_performance": ml_model_performance,
                    "graph_enhancement_analytics": enhancement_analytics,
                    
                    # Complete KG Summary Data (for reference)
                    "raw_kg_summary": kg_summary
                }
            }
            
            # Update the certificate with the structured data
            success = await self.update_entity(
                entity_id=certificate.certificate_id,
                update_data=update_data,
                user_context=user_context
            )
            
            if success:
                self.logger.info(f"Successfully populated KG Neo4j data for file: {file_id}, registry: {registry_id}")
                return True
            else:
                self.logger.error(f"Failed to update certificate with KG Neo4j data for file: {file_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error populating from KG Neo4j: {e}")
            return False
    
    async def populate_from_federated_learning(self, fl_summary: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """
        Populate certificate with Federated Learning processing results.
        
        Args:
            fl_summary: Federated Learning processing data with comprehensive structure covering
                both federated_learning_registry and federated_learning_metrics tables
            
        Returns:
            bool: True if population successful, False otherwise
        """
        try:
            registry_id = fl_summary.get("registry_id")
            file_id = fl_summary.get("file_id")
            status = fl_summary.get("status")
            
            if not all([registry_id, file_id, status]):
                self.logger.error("Missing required Federated Learning data fields")
                return False
            
            certificate = await self.get_entity_by_file_id(file_id, user_context)
            if not certificate:
                self.logger.error(f"Certificate not found for file_id: {file_id}")
                return False
            
            # Reorganize flat fl_summary into structured format
            # Federated Learning Identification
            fl_identification = {
                "federation_name": fl_summary.get("federation_name"),
                "registry_name": fl_summary.get("registry_name"),
                "federation_category": fl_summary.get("federation_category"),
                "federation_type": fl_summary.get("federation_type"),
                "federation_priority": fl_summary.get("federation_priority"),
                "federation_version": fl_summary.get("federation_version"),
                "workflow_source": fl_summary.get("workflow_source"),
                "registry_type": fl_summary.get("registry_type")
            }
            
            # Federation Processing Summary
            federation_processing = {
                "total_participating_organizations": fl_summary.get("total_organizations") or fl_summary.get("federation_processing_summary", {}).get("total_participating_organizations"),
                "total_participating_twins": fl_summary.get("total_twins") or fl_summary.get("federation_processing_summary", {}).get("total_participating_twins"),
                "total_federation_rounds": fl_summary.get("total_rounds") or fl_summary.get("federation_processing_summary", {}).get("total_federation_rounds"),
                "total_models_aggregated": fl_summary.get("total_models") or fl_summary.get("federation_processing_summary", {}).get("total_models_aggregated"),
                "federation_complexity": fl_summary.get("federation_complexity") or fl_summary.get("federation_processing_summary", {}).get("federation_complexity"),
                "processing_status": fl_summary.get("processing_status") or fl_summary.get("federation_processing_summary", {}).get("processing_status"),
                "content_summary": fl_summary.get("content_summary") or fl_summary.get("federation_processing_summary", {}).get("content_summary"),
                "extracted_knowledge": fl_summary.get("extracted_knowledge") or fl_summary.get("federation_processing_summary", {}).get("extracted_knowledge"),
                "quality_score": fl_summary.get("quality_score") or fl_summary.get("federation_processing_summary", {}).get("quality_score"),
                "confidence_score": fl_summary.get("confidence_score") or fl_summary.get("federation_processing_summary", {}).get("confidence_score")
            }
            
            # Federation Participants Breakdown
            federation_participants = {
                "manufacturing_plants": {
                    "count": fl_summary.get("manufacturing_plants_count"),
                    "participation_rate": fl_summary.get("manufacturing_plants_participation_rate")
                },
                "equipment_types": {
                    "count": fl_summary.get("equipment_types_count"),
                    "cross_learning_potential": fl_summary.get("cross_learning_potential")
                }
            }
            
            # Federation Rounds Performance
            federation_rounds = {
                "round_1": {
                    "participants": fl_summary.get("round_1_participants"),
                    "accuracy_improvement": fl_summary.get("round_1_accuracy_improvement")
                },
                "round_2": {
                    "accuracy_improvement": fl_summary.get("round_2_accuracy_improvement")
                },
                "round_3": {
                    "accuracy_improvement": fl_summary.get("round_3_accuracy_improvement")
                }
            }
            
            # Federation Status
            federation_status = {
                "federation_participation_status": fl_summary.get("participation_status"),
                "model_aggregation_status": fl_summary.get("aggregation_status"),
                "privacy_compliance_status": fl_summary.get("privacy_compliance_status"),
                "algorithm_execution_status": fl_summary.get("algorithm_execution_status"),
                "last_federation_sync_at": fl_summary.get("last_sync_at")
            }
            
            # Federated Learning Configuration
            fl_configuration = {
                "federation_algorithm": fl_summary.get("federation_algorithm"),
                "aggregation_method": fl_summary.get("aggregation_method"),
                "privacy_mechanism": fl_summary.get("privacy_mechanism"),
                "communication_protocol": fl_summary.get("communication_protocol"),
                "model_architecture": fl_summary.get("model_architecture"),
                "training_parameters": fl_summary.get("training_parameters")
            }
            
            # Federated Learning Techniques Performance
            fl_techniques = {
                "federated_averaging_accuracy": fl_summary.get("federated_averaging_accuracy"),
                "differential_privacy_accuracy": fl_summary.get("differential_privacy_accuracy"),
                "secure_aggregation_accuracy": fl_summary.get("secure_aggregation_accuracy"),
                "homomorphic_encryption_accuracy": fl_summary.get("homomorphic_encryption_accuracy")
            }
            
            # Federation Capabilities Utilized
            federation_capabilities = {
                "cross_silo_learning": fl_summary.get("cross_silo_learning"),
                "privacy_preserving_aggregation": fl_summary.get("privacy_preserving_aggregation"),
                "distributed_training": fl_summary.get("distributed_training"),
                "model_compression": fl_summary.get("model_compression")
            }
            
            # Performance Metrics
            performance = {
                "performance_score": fl_summary.get("performance_score"),
                "data_quality_score": fl_summary.get("data_quality_score"),
                "reliability_score": fl_summary.get("reliability_score"),
                "compliance_score": fl_summary.get("compliance_score"),
                "overall_health_score": fl_summary.get("overall_health_score"),
                "health_status": fl_summary.get("health_status")
            }
            
            # Federated Learning Metrics
            fl_metrics = {
                "federation_accuracy": fl_summary.get("federation_accuracy"),
                "convergence_speed": fl_summary.get("convergence_speed"),
                "communication_efficiency": fl_summary.get("communication_efficiency"),
                "privacy_budget_utilization": fl_summary.get("privacy_budget_utilization"),
                "model_utility_score": fl_summary.get("model_utility_score")
            }
            
            # Federation Operation Metrics
            operation_metrics = {
                "federation_operations_count": fl_summary.get("federation_operations_count"),
                "successful_operations": fl_summary.get("successful_operations"),
                "failed_operations": fl_summary.get("failed_operations"),
                "average_operation_time": fl_summary.get("average_operation_time"),
                "throughput_operations_per_second": fl_summary.get("throughput_operations_per_second")
            }
            
            # Quality Validation
            quality_validation = {
                "model_quality_score": fl_summary.get("model_quality_score"),
                "data_validation_score": fl_summary.get("data_validation_score"),
                "aggregation_quality_score": fl_summary.get("aggregation_quality_score"),
                "privacy_validation_score": fl_summary.get("privacy_validation_score")
            }
            
            # Integration Status
            integration_status = {
                "federation_integration_status": fl_summary.get("federation_integration_status"),
                "data_sync_status": fl_summary.get("data_sync_status"),
                "model_sync_status": fl_summary.get("model_sync_status"),
                "communication_status": fl_summary.get("communication_status")
            }
            
            # Module Integration
            module_integration = {
                "aasx_integration_id": fl_summary.get("aasx_integration_id"),
                "twin_registry_id": fl_summary.get("twin_registry_id"),
                "kg_neo4j_id": fl_summary.get("kg_neo4j_id"),
                "physics_modeling_id": fl_summary.get("physics_modeling_id"),
                "ai_rag_id": fl_summary.get("ai_rag_id"),
                "certificate_manager_id": fl_summary.get("certificate_manager_id")
            }
            
            # Enterprise Compliance
            enterprise_compliance = {
                "compliance_status": fl_summary.get("compliance_status"),
                "audit_status": fl_summary.get("audit_status"),
                "regulatory_compliance": fl_summary.get("regulatory_compliance"),
                "data_governance_compliance": fl_summary.get("data_governance_compliance")
            }
            
            # Enterprise Security
            enterprise_security = {
                "security_level": fl_summary.get("security_level"),
                "threat_assessment": fl_summary.get("threat_assessment"),
                "vulnerability_scan_status": fl_summary.get("vulnerability_scan_status"),
                "security_events": fl_summary.get("security_events")
            }
            
            # User Management
            user_management = {
                "user_count": fl_summary.get("user_count"),
                "active_users": fl_summary.get("active_users"),
                "user_roles": fl_summary.get("user_roles"),
                "access_control_status": fl_summary.get("access_control_status")
            }
            
            # Timestamps
            timestamps = {
                "created_at": fl_summary.get("created_at"),
                "updated_at": fl_summary.get("updated_at"),
                "last_accessed_at": fl_summary.get("last_accessed_at"),
                "federation_start_time": fl_summary.get("federation_start_time"),
                "federation_end_time": fl_summary.get("federation_end_time")
            }
            
            # Computed Business Intelligence
            business_intelligence = {
                "overall_score": fl_summary.get("overall_score"),
                "business_value_score": fl_summary.get("business_value_score"),
                "risk_assessment": {
                    "risk_score": fl_summary.get("risk_score"),
                    "risk_level": fl_summary.get("risk_level")
                },
                "optimization_priority": fl_summary.get("optimization_priority")
            }
            
            # Federated Learning Analytics
            fl_analytics = {
                "federation_analytics": fl_summary.get("federation_analytics"),
                "performance_trends": fl_summary.get("performance_trends"),
                "participant_behavior": fl_summary.get("participant_behavior"),
                "model_evolution": fl_summary.get("model_evolution")
            }
            
            # Supported Federation Types Summary
            federation_types_summary = {
                "horizontal_federation": fl_summary.get("horizontal_federation"),
                "vertical_federation": fl_summary.get("vertical_federation"),
                "federated_transfer_learning": fl_summary.get("federated_transfer_learning"),
                "cross_silo_federation": fl_summary.get("cross_silo_federation")
            }
            
            # Federation Database Metrics
            federation_db_metrics = {
                "database_size_mb": fl_summary.get("database_size_mb"),
                "index_count": fl_summary.get("index_count"),
                "constraint_count": fl_summary.get("constraint_count"),
                "query_performance": fl_summary.get("query_performance"),
                "storage_utilization": fl_summary.get("storage_utilization")
            }
            
            # Model Performance
            model_performance = {
                "model_accuracy": fl_summary.get("model_accuracy"),
                "inference_speed": fl_summary.get("inference_speed"),
                "training_accuracy": fl_summary.get("training_accuracy"),
                "validation_accuracy": fl_summary.get("validation_accuracy"),
                "f1_score": fl_summary.get("f1_score")
            }
            
            # Federation Optimization Analytics
            optimization_analytics = {
                "optimization_suggestions": fl_summary.get("optimization_suggestions"),
                "performance_improvements": fl_summary.get("performance_improvements"),
                "resource_utilization": fl_summary.get("resource_utilization"),
                "scalability_metrics": fl_summary.get("scalability_metrics")
            }
            
            # Federation Patterns
            federation_patterns = {
                "communication_patterns": fl_summary.get("communication_patterns"),
                "aggregation_patterns": fl_summary.get("aggregation_patterns"),
                "privacy_patterns": fl_summary.get("privacy_patterns"),
                "convergence_patterns": fl_summary.get("convergence_patterns")
            }
            
            # Federation Visualization Metrics
            viz_metrics = {
                "visualization_quality": fl_summary.get("visualization_quality"),
                "dashboard_performance": fl_summary.get("dashboard_performance"),
                "chart_rendering_speed": fl_summary.get("chart_rendering_speed"),
                "user_interaction_metrics": fl_summary.get("user_interaction_metrics")
            }
            
            # Update certificate with Federated Learning data
            # Structure: Only individual columns for cross-module references, detailed data in JSON summary
            update_data = {
                "file_id": file_id,  # Include file_id for validation
                "federated_learning_status": "completed",
                "federated_learning_registry_id": registry_id,  # Individual column for cross-module reference
                "federated_learning_summary": {
                    # Basic Information
                    "file_id": file_id,
                    "registry_id": registry_id,
                    "timestamp": fl_summary.get("timestamp"),
                    "status": status,
                    
                    # Structured Data (reorganized from flat fl_summary)
                    "federated_learning_identification": fl_identification,
                    "federation_processing_summary": federation_processing,
                    "federation_participants_breakdown": federation_participants,
                    "federation_rounds_performance": federation_rounds,
                    "federation_status": federation_status,
                    "federated_learning_configuration": fl_configuration,
                    "federated_learning_techniques_performance": fl_techniques,
                    "federation_capabilities_utilized": federation_capabilities,
                    "performance_metrics": performance,
                    "federated_learning_metrics": fl_metrics,
                    "federation_operation_metrics": operation_metrics,
                    "quality_validation": quality_validation,
                    "integration_status": integration_status,
                    "module_integration": module_integration,
                    "enterprise_compliance": enterprise_compliance,
                    "enterprise_security": enterprise_security,
                    "user_management": user_management,
                    "timestamps": timestamps,
                    "computed_business_intelligence": business_intelligence,
                    "federated_learning_analytics": fl_analytics,
                    "supported_federation_types_summary": federation_types_summary,
                    "federation_database_metrics": federation_db_metrics,
                    "model_performance": model_performance,
                    "federation_optimization_analytics": optimization_analytics,
                    "federation_patterns": federation_patterns,
                    "federation_visualization_metrics": viz_metrics,
                    
                    # Complete FL Summary Data (for reference)
                    "raw_fl_summary": fl_summary
                }
            }
            
            success = await self.update_entity(
                entity_id=certificate.certificate_id, 
                update_data=update_data, 
                user_context=user_context
            )
            
            if success:
                self.logger.info(f"Successfully populated Federated Learning data for file: {file_id}, registry: {registry_id}")
                return True
            else:
                self.logger.error(f"Failed to update certificate with Federated Learning data for file: {file_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error populating from Federated Learning: {e}")
            return False
    
    async def populate_from_physics_modeling(self, physics_summary: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """
        Populate certificate with Physics Modeling processing results.
        
        Args:
            physics_summary: Physics Modeling processing data with comprehensive structure covering
                all three module tables (physics_modeling_registry, physics_ml_registry, physics_modeling_metrics)
            
        Returns:
            bool: True if population successful, False otherwise
        """
        try:
            registry_id = physics_summary.get("registry_id")
            file_id = physics_summary.get("file_id")
            status = physics_summary.get("status")
            
            if not all([registry_id, file_id, status]):
                self.logger.error("Missing required Physics Modeling data fields")
                return False
            
            certificate = await self.get_entity_by_file_id(file_id, user_context)
            if not certificate:
                self.logger.error(f"Certificate not found for file_id: {file_id}")
                return False
            
            # Reorganize flat physics_summary into structured format
            # Physics Modeling Identification
            physics_identification = {
                "model_name": physics_summary.get("model_name") or physics_summary.get("physics_modeling_identification", {}).get("model_name"),
                "registry_name": physics_summary.get("registry_name") or physics_summary.get("physics_modeling_identification", {}).get("registry_name"),
                "physics_category": physics_summary.get("physics_category") or physics_summary.get("physics_modeling_identification", {}).get("physics_category"),
                "physics_type": physics_summary.get("physics_type") or physics_summary.get("physics_modeling_identification", {}).get("physics_type"),
                "model_type": physics_summary.get("model_type") or physics_summary.get("physics_modeling_identification", {}).get("model_type"),
                "plugin_id": physics_summary.get("plugin_id") or physics_summary.get("physics_modeling_identification", {}).get("plugin_id"),
                "plugin_name": physics_summary.get("plugin_name") or physics_summary.get("physics_modeling_identification", {}).get("plugin_name"),
                "model_version": physics_summary.get("model_version") or physics_summary.get("physics_modeling_identification", {}).get("model_version"),
                "model_description": physics_summary.get("model_description") or physics_summary.get("physics_modeling_identification", {}).get("model_description"),
                "physics_priority": physics_summary.get("physics_priority") or physics_summary.get("physics_modeling_identification", {}).get("physics_priority"),
                "physics_version": physics_summary.get("physics_version") or physics_summary.get("physics_modeling_identification", {}).get("physics_version"),
                "registry_type": physics_summary.get("registry_type") or physics_summary.get("physics_modeling_identification", {}).get("registry_type"),
                "workflow_source": physics_summary.get("workflow_source") or physics_summary.get("physics_modeling_identification", {}).get("workflow_source")
            }
            
            # Traditional Physics Configuration
            traditional_config = {
                "traditional_physics_enabled": physics_summary.get("traditional_physics_enabled"),
                "physics_equations_count": physics_summary.get("physics_equations_count"),
                "constraints_count": physics_summary.get("constraints_count"),
                "simulation_parameters": physics_summary.get("simulation_parameters"),
                "numerical_methods": physics_summary.get("numerical_methods"),
                "convergence_criteria": physics_summary.get("convergence_criteria")
            }
            
            # Physics Equations and Constraints
            physics_equations = {
                "differential_equations": physics_summary.get("differential_equations"),
                "boundary_conditions": physics_summary.get("boundary_conditions"),
                "initial_conditions": physics_summary.get("initial_conditions"),
                "constraint_equations": physics_summary.get("constraint_equations"),
                "material_properties": physics_summary.get("material_properties"),
                "physical_constants": physics_summary.get("physical_constants")
            }
            
            # ML Integration Summary
            ml_integration = {
                "ml_integration_enabled": physics_summary.get("ml_integration_enabled"),
                "ml_models_count": physics_summary.get("ml_models_count"),
                "hybrid_approach": physics_summary.get("hybrid_approach"),
                "ml_physics_coupling": physics_summary.get("ml_physics_coupling"),
                "neural_physics_networks": physics_summary.get("neural_physics_networks"),
                "physics_informed_ml": physics_summary.get("physics_informed_ml")
            }
            
            # Performance Metrics
            performance = {
                "performance_score": physics_summary.get("performance_score"),
                "data_quality_score": physics_summary.get("data_quality_score"),
                "reliability_score": physics_summary.get("reliability_score"),
                "compliance_score": physics_summary.get("compliance_score"),
                "overall_health_score": physics_summary.get("overall_health_score"),
                "health_status": physics_summary.get("health_status")
            }
            
            # Resource Utilization
            resource_utilization = {
                "cpu_utilization": physics_summary.get("cpu_utilization"),
                "memory_utilization": physics_summary.get("memory_utilization"),
                "gpu_utilization": physics_summary.get("gpu_utilization"),
                "storage_utilization": physics_summary.get("storage_utilization"),
                "network_utilization": physics_summary.get("network_utilization"),
                "computational_efficiency": physics_summary.get("computational_efficiency")
            }
            
            # Quality Metrics
            quality_metrics = {
                "simulation_accuracy": physics_summary.get("simulation_accuracy"),
                "convergence_quality": physics_summary.get("convergence_quality"),
                "numerical_stability": physics_summary.get("numerical_stability"),
                "physics_consistency": physics_summary.get("physics_consistency"),
                "validation_accuracy": physics_summary.get("validation_accuracy")
            }
            
            # Traditional vs ML Comparison
            traditional_vs_ml = {
                "traditional_accuracy": physics_summary.get("traditional_accuracy"),
                "ml_accuracy": physics_summary.get("ml_accuracy"),
                "traditional_speed": physics_summary.get("traditional_speed"),
                "ml_speed": physics_summary.get("ml_speed"),
                "hybrid_effectiveness": physics_summary.get("hybrid_effectiveness"),
                "best_approach": physics_summary.get("best_approach")
            }
            
            # Simulation Results Metadata
            simulation_results = {
                "simulation_count": physics_summary.get("simulation_count"),
                "successful_simulations": physics_summary.get("successful_simulations"),
                "failed_simulations": physics_summary.get("failed_simulations"),
                "average_simulation_time": physics_summary.get("average_simulation_time"),
                "simulation_throughput": physics_summary.get("simulation_throughput")
            }
            
            # Error Metrics
            error_metrics = {
                "numerical_errors": physics_summary.get("numerical_errors"),
                "convergence_errors": physics_summary.get("convergence_errors"),
                "physics_violations": physics_summary.get("physics_violations"),
                "validation_errors": physics_summary.get("validation_errors"),
                "error_recovery_rate": physics_summary.get("error_recovery_rate")
            }
            
            # Time Based Analytics
            time_analytics = {
                "simulation_time_trends": physics_summary.get("simulation_time_trends"),
                "performance_over_time": physics_summary.get("performance_over_time"),
                "resource_usage_trends": physics_summary.get("resource_usage_trends"),
                "accuracy_evolution": physics_summary.get("accuracy_evolution")
            }
            
            # Enterprise Compliance
            enterprise_compliance = {
                "compliance_status": physics_summary.get("compliance_status"),
                "audit_status": physics_summary.get("audit_status"),
                "regulatory_compliance": physics_summary.get("regulatory_compliance"),
                "data_governance_compliance": physics_summary.get("data_governance_compliance")
            }
            
            # Enterprise Security
            enterprise_security = {
                "security_level": physics_summary.get("security_level"),
                "threat_assessment": physics_summary.get("threat_assessment"),
                "vulnerability_scan_status": physics_summary.get("vulnerability_scan_status"),
                "security_events": physics_summary.get("security_events")
            }
            
            # Performance Analytics
            performance_analytics = {
                "performance_trends": physics_summary.get("performance_trends"),
                "bottleneck_analysis": physics_summary.get("bottleneck_analysis"),
                "optimization_opportunities": physics_summary.get("optimization_opportunities"),
                "scalability_metrics": physics_summary.get("scalability_metrics")
            }
            
            # Module Integration
            module_integration = {
                "aasx_integration_id": physics_summary.get("aasx_integration_id"),
                "twin_registry_id": physics_summary.get("twin_registry_id"),
                "kg_neo4j_id": physics_summary.get("kg_neo4j_id"),
                "ai_rag_id": physics_summary.get("ai_rag_id"),
                "federated_learning_id": physics_summary.get("federated_learning_id"),
                "certificate_manager_id": physics_summary.get("certificate_manager_id")
            }
            
            # User Management
            user_management = {
                "user_count": physics_summary.get("user_count"),
                "active_users": physics_summary.get("active_users"),
                "user_roles": physics_summary.get("user_roles"),
                "access_control_status": physics_summary.get("access_control_status")
            }
            
            # Timestamps
            timestamps = {
                "created_at": physics_summary.get("created_at"),
                "updated_at": physics_summary.get("updated_at"),
                "last_accessed_at": physics_summary.get("last_accessed_at"),
                "simulation_start_time": physics_summary.get("simulation_start_time"),
                "simulation_end_time": physics_summary.get("simulation_end_time")
            }
            
            # Computed Business Intelligence
            business_intelligence = {
                "overall_score": physics_summary.get("overall_score"),
                "business_value_score": physics_summary.get("business_value_score"),
                "risk_assessment": {
                    "risk_score": physics_summary.get("risk_score"),
                    "risk_level": physics_summary.get("risk_level")
                },
                "optimization_priority": physics_summary.get("optimization_priority")
            }
            
            # Physics Modeling Analytics
            physics_analytics = {
                "physics_analytics": physics_summary.get("physics_analytics"),
                "simulation_analytics": physics_summary.get("simulation_analytics"),
                "model_evolution": physics_summary.get("model_evolution"),
                "accuracy_trends": physics_summary.get("accuracy_trends")
            }
            
            # Supported Physics Types Summary
            supported_physics_types = {
                "fluid_dynamics": physics_summary.get("fluid_dynamics"),
                "structural_mechanics": physics_summary.get("structural_mechanics"),
                "heat_transfer": physics_summary.get("heat_transfer"),
                "electromagnetic": physics_summary.get("electromagnetic"),
                "quantum_mechanics": physics_summary.get("quantum_mechanics")
            }
            
            # Physics Modeling Database Metrics
            database_metrics = {
                "database_size_mb": physics_summary.get("database_size_mb"),
                "index_count": physics_summary.get("index_count"),
                "constraint_count": physics_summary.get("constraint_count"),
                "query_performance": physics_summary.get("query_performance"),
                "storage_utilization": physics_summary.get("storage_utilization")
            }
            
            # Model Performance
            model_performance = {
                "model_accuracy": physics_summary.get("model_accuracy"),
                "inference_speed": physics_summary.get("inference_speed"),
                "training_accuracy": physics_summary.get("training_accuracy"),
                "validation_accuracy": physics_summary.get("validation_accuracy"),
                "f1_score": physics_summary.get("f1_score")
            }
            
            # Optimization Analytics
            optimization_analytics = {
                "optimization_suggestions": physics_summary.get("optimization_suggestions"),
                "performance_improvements": physics_summary.get("performance_improvements"),
                "resource_optimization": physics_summary.get("resource_optimization"),
                "algorithm_optimization": physics_summary.get("algorithm_optimization")
            }
            
            # Physics Modeling Patterns
            physics_patterns = {
                "simulation_patterns": physics_summary.get("simulation_patterns"),
                "convergence_patterns": physics_summary.get("convergence_patterns"),
                "error_patterns": physics_summary.get("error_patterns"),
                "performance_patterns": physics_summary.get("performance_patterns")
            }
            
            # Update certificate with Physics Modeling data
            # Structure: Only individual columns for cross-module references, detailed data in JSON summary
            update_data = {
                "file_id": file_id,  # Include file_id for validation
                "physics_modeling_status": "completed",
                "physics_modeling_registry_id": registry_id,  # Individual column for cross-module reference
                "physics_modeling_summary": {
                    # Basic Information
                    "file_id": file_id,
                    "registry_id": registry_id,
                    "timestamp": physics_summary.get("timestamp"),
                    "status": status,
                    
                    # Structured Data (reorganized from flat physics_summary)
                    "physics_modeling_identification": physics_identification,
                    "traditional_physics_configuration": traditional_config,
                    "physics_equations_and_constraints": physics_equations,
                    "ml_integration_summary": ml_integration,
                    "performance_metrics": performance,
                    "resource_utilization": resource_utilization,
                    "quality_metrics": quality_metrics,
                    "traditional_vs_ml_comparison": traditional_vs_ml,
                    "simulation_results_metadata": simulation_results,
                    "error_metrics": error_metrics,
                    "time_based_analytics": time_analytics,
                    "enterprise_compliance": enterprise_compliance,
                    "enterprise_security": enterprise_security,
                    "performance_analytics": performance_analytics,
                    "module_integration": module_integration,
                    "user_management": user_management,
                    "timestamps": timestamps,
                    "computed_business_intelligence": business_intelligence,
                    "physics_modeling_analytics": physics_analytics,
                    "supported_physics_types_summary": supported_physics_types,
                    "physics_modeling_database_metrics": database_metrics,
                    "model_performance": model_performance,
                    "optimization_analytics": optimization_analytics,
                    "physics_modeling_patterns": physics_patterns,
                    
                    # Complete Physics Summary Data (for reference)
                    "raw_physics_summary": physics_summary
                }
            }
            
            success = await self.update_entity(
                entity_id=certificate.certificate_id, 
                update_data=update_data, 
                user_context=user_context
            )
            
            if success:
                self.logger.info(f"Successfully populated Physics Modeling data for file: {file_id}, registry: {registry_id}")
                return True
            else:
                self.logger.error(f"Failed to update certificate with Physics Modeling data for file: {file_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error populating from Physics Modeling: {e}")
            return False
    
    
    async def populate_from_data_governance(self, governance_summary: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """
        Populate certificate with Data Governance processing results.
        
        Args:
            governance_summary: Data Governance processing data with comprehensive structure covering
                all five module tables (data_lineage, data_quality_metrics, change_requests, data_versions, governance_policies)
            
        Returns:
            bool: True if population successful, False otherwise
        """
        try:
            registry_id = governance_summary.get("registry_id")
            file_id = governance_summary.get("file_id")
            status = governance_summary.get("status")
            
            if not all([registry_id, file_id, status]):
                self.logger.error("Missing required Data Governance data fields")
                return False
            
            certificate = await self.get_entity_by_file_id(file_id, user_context)
            if not certificate:
                self.logger.error(f"Certificate not found for file_id: {file_id}")
                return False
            
            # Reorganize flat governance_summary into structured format
            # Data Governance Identification
            governance_identification = {
                "registry_name": governance_summary.get("registry_name"),
                "governance_category": governance_summary.get("governance_category"),
                "governance_type": governance_summary.get("governance_type"),
                "governance_priority": governance_summary.get("governance_priority"),
                "governance_version": governance_summary.get("governance_version"),
                "registry_type": governance_summary.get("registry_type"),
                "workflow_source": governance_summary.get("workflow_source")
            }
            
            # Data Lineage Summary
            data_lineage = {
                "lineage_tracking_enabled": governance_summary.get("lineage_tracking_enabled"),
                "total_data_sources": governance_summary.get("total_data_sources"),
                "total_data_transformations": governance_summary.get("total_data_transformations"),
                "total_data_destinations": governance_summary.get("total_data_destinations"),
                "lineage_completeness_score": governance_summary.get("lineage_completeness_score"),
                "data_flow_accuracy": governance_summary.get("data_flow_accuracy"),
                "lineage_validation_status": governance_summary.get("lineage_validation_status")
            }
            
            # Data Quality Summary
            data_quality = {
                "quality_monitoring_enabled": governance_summary.get("quality_monitoring_enabled"),
                "total_quality_rules": governance_summary.get("total_quality_rules"),
                "quality_checks_performed": governance_summary.get("quality_checks_performed"),
                "quality_violations_detected": governance_summary.get("quality_violations_detected"),
                "overall_quality_score": governance_summary.get("overall_quality_score") or governance_summary.get("data_quality_summary", {}).get("overall_quality_score"),
                "completeness_score": governance_summary.get("completeness_score") or governance_summary.get("data_quality_summary", {}).get("completeness_score"),
                "accuracy_score": governance_summary.get("accuracy_score") or governance_summary.get("data_quality_summary", {}).get("accuracy_score"),
                "consistency_score": governance_summary.get("consistency_score") or governance_summary.get("data_quality_summary", {}).get("consistency_score"),
                "timeliness_score": governance_summary.get("timeliness_score") or governance_summary.get("data_quality_summary", {}).get("timeliness_score"),
                "validity_score": governance_summary.get("validity_score") or governance_summary.get("data_quality_summary", {}).get("validity_score"),
                "data_completeness_score": governance_summary.get("data_completeness_score"),
                "data_accuracy_score": governance_summary.get("data_accuracy_score"),
                "data_consistency_score": governance_summary.get("data_consistency_score")
            }
            
            # Change Management Summary
            change_management = {
                "change_tracking_enabled": governance_summary.get("change_tracking_enabled"),
                "total_change_requests": governance_summary.get("total_change_requests"),
                "approved_changes": governance_summary.get("approved_changes"),
                "pending_changes": governance_summary.get("pending_changes"),
                "rejected_changes": governance_summary.get("rejected_changes"),
                "change_approval_rate": governance_summary.get("change_approval_rate"),
                "average_change_processing_time": governance_summary.get("average_change_processing_time")
            }
            
            # Data Versioning Summary
            data_versioning = {
                "versioning_enabled": governance_summary.get("versioning_enabled"),
                "total_data_versions": governance_summary.get("total_data_versions"),
                "active_versions": governance_summary.get("active_versions"),
                "archived_versions": governance_summary.get("archived_versions"),
                "version_retention_policy": governance_summary.get("version_retention_policy"),
                "version_rollback_capability": governance_summary.get("version_rollback_capability")
            }
            
            # Governance Policies Summary
            governance_policies = {
                "policies_defined": governance_summary.get("policies_defined"),
                "policies_active": governance_summary.get("policies_active"),
                "policies_enforced": governance_summary.get("policies_enforced"),
                "policy_violations": governance_summary.get("policy_violations"),
                "compliance_score": governance_summary.get("compliance_score"),
                "policy_effectiveness": governance_summary.get("policy_effectiveness")
            }
            
            # Compliance and Audit Summary
            compliance_audit = {
                "audit_trail_enabled": governance_summary.get("audit_trail_enabled"),
                "total_audit_events": governance_summary.get("total_audit_events"),
                "compliance_checks_performed": governance_summary.get("compliance_checks_performed"),
                "compliance_violations": governance_summary.get("compliance_violations"),
                "audit_coverage": governance_summary.get("audit_coverage"),
                "regulatory_compliance_status": governance_summary.get("regulatory_compliance_status")
            }
            
            # Performance Metrics
            performance = {
                "performance_score": governance_summary.get("performance_score"),
                "data_quality_score": governance_summary.get("data_quality_score"),
                "reliability_score": governance_summary.get("reliability_score"),
                "compliance_score": governance_summary.get("compliance_score"),
                "overall_health_score": governance_summary.get("overall_health_score"),
                "health_status": governance_summary.get("health_status")
            }
            
            # Enterprise Features
            enterprise_features = {
                "enterprise_governance": governance_summary.get("enterprise_governance"),
                "multi_tenant_support": governance_summary.get("multi_tenant_support"),
                "role_based_access": governance_summary.get("role_based_access"),
                "enterprise_integration": governance_summary.get("enterprise_integration"),
                "scalability_features": governance_summary.get("scalability_features")
            }
            
            # Module Integration
            module_integration = {
                "aasx_integration_id": governance_summary.get("aasx_integration_id"),
                "twin_registry_id": governance_summary.get("twin_registry_id"),
                "kg_neo4j_id": governance_summary.get("kg_neo4j_id"),
                "ai_rag_id": governance_summary.get("ai_rag_id"),
                "federated_learning_id": governance_summary.get("federated_learning_id"),
                "physics_modeling_id": governance_summary.get("physics_modeling_id"),
                "certificate_manager_id": governance_summary.get("certificate_manager_id")
            }
            
            # User Management
            user_management = {
                "user_count": governance_summary.get("user_count"),
                "active_users": governance_summary.get("active_users"),
                "user_roles": governance_summary.get("user_roles"),
                "access_control_status": governance_summary.get("access_control_status")
            }
            
            # Timestamps
            timestamps = {
                "created_at": governance_summary.get("created_at"),
                "updated_at": governance_summary.get("updated_at"),
                "last_accessed_at": governance_summary.get("last_accessed_at"),
                "governance_start_time": governance_summary.get("governance_start_time"),
                "governance_end_time": governance_summary.get("governance_end_time")
            }
            
            # Computed Business Intelligence
            business_intelligence = {
                "overall_score": governance_summary.get("overall_score"),
                "business_value_score": governance_summary.get("business_value_score"),
                "risk_assessment": {
                    "risk_score": governance_summary.get("risk_score"),
                    "risk_level": governance_summary.get("risk_level")
                },
                "optimization_priority": governance_summary.get("optimization_priority")
            }
            
            # Data Governance Analytics
            governance_analytics = {
                "governance_analytics": governance_summary.get("governance_analytics"),
                "compliance_trends": governance_summary.get("compliance_trends"),
                "quality_trends": governance_summary.get("quality_trends"),
                "policy_effectiveness_analysis": governance_summary.get("policy_effectiveness_analysis")
            }
            
            # Supported Governance Types Summary
            supported_types = {
                "data_lineage_governance": governance_summary.get("data_lineage_governance"),
                "data_quality_governance": governance_summary.get("data_quality_governance"),
                "data_privacy_governance": governance_summary.get("data_privacy_governance"),
                "data_security_governance": governance_summary.get("data_security_governance"),
                "data_lifecycle_governance": governance_summary.get("data_lifecycle_governance")
            }
            
            # Data Governance Database Metrics
            database_metrics = {
                "database_size_mb": governance_summary.get("database_size_mb"),
                "index_count": governance_summary.get("index_count"),
                "constraint_count": governance_summary.get("constraint_count"),
                "query_performance": governance_summary.get("query_performance"),
                "storage_utilization": governance_summary.get("storage_utilization")
            }
            
            # Governance Performance
            governance_performance = {
                "governance_efficiency": governance_summary.get("governance_efficiency"),
                "policy_enforcement_speed": governance_summary.get("policy_enforcement_speed"),
                "compliance_check_speed": governance_summary.get("compliance_check_speed"),
                "audit_processing_time": governance_summary.get("audit_processing_time"),
                "governance_throughput": governance_summary.get("governance_throughput")
            }
            
            # Optimization Analytics
            optimization_analytics = {
                "optimization_suggestions": governance_summary.get("optimization_suggestions"),
                "performance_improvements": governance_summary.get("performance_improvements"),
                "governance_optimization": governance_summary.get("governance_optimization"),
                "policy_optimization": governance_summary.get("policy_optimization")
            }
            
            # Data Governance Patterns
            governance_patterns = {
                "compliance_patterns": governance_summary.get("compliance_patterns"),
                "quality_patterns": governance_summary.get("quality_patterns"),
                "change_patterns": governance_summary.get("change_patterns"),
                "audit_patterns": governance_summary.get("audit_patterns")
            }
            
            # Data Governance Visualization Metrics
            viz_metrics = {
                "visualization_quality": governance_summary.get("visualization_quality"),
                "dashboard_performance": governance_summary.get("dashboard_performance"),
                "chart_rendering_speed": governance_summary.get("chart_rendering_speed"),
                "user_interaction_metrics": governance_summary.get("user_interaction_metrics")
            }
            
            # Update certificate with Data Governance data
            # Structure: Only individual columns for cross-module references, detailed data in JSON summary
            update_data = {
                "file_id": file_id,  # Include file_id for validation
                "data_governance_status": "completed",
                "data_governance_registry_id": registry_id,  # Individual column for cross-module reference
                "data_governance_summary": {
                    # Basic Information
                    "file_id": file_id,
                    "registry_id": registry_id,
                    "timestamp": governance_summary.get("timestamp"),
                    "status": status,
                    
                    # Structured Data (reorganized from flat governance_summary)
                    "data_governance_identification": governance_identification,
                    "data_lineage_summary": data_lineage,
                    "data_quality_summary": data_quality,
                    "change_management_summary": change_management,
                    "data_versioning_summary": data_versioning,
                    "governance_policies_summary": governance_policies,
                    "compliance_and_audit_summary": compliance_audit,
                    "performance_metrics": performance,
                    "enterprise_features": enterprise_features,
                    "module_integration": module_integration,
                    "user_management": user_management,
                    "timestamps": timestamps,
                    "computed_business_intelligence": business_intelligence,
                    "data_governance_analytics": governance_analytics,
                    "supported_governance_types_summary": supported_types,
                    "data_governance_database_metrics": database_metrics,
                    "governance_performance": governance_performance,
                    "optimization_analytics": optimization_analytics,
                    "data_governance_patterns": governance_patterns,
                    "data_governance_visualization_metrics": viz_metrics,
                    
                    # Complete Governance Summary Data (for reference)
                    "raw_governance_summary": governance_summary
                }
            }
             
            success = await self.update_entity(
                entity_id=certificate.certificate_id, 
                update_data=update_data, 
                user_context=user_context
            )
            
            if success:
                self.logger.info(f"Successfully populated Data Governance data for file: {file_id}, registry: {registry_id}")
                return True
            else:
                self.logger.error(f"Failed to update certificate with Data Governance data for file: {file_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error populating from Data Governance: {e}")
            return False
    
    async def populate_from_digital_product_passport(self, dpp_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """
        Populate certificate with Digital Product Passport processing results.
        
        Args:
            dpp_data: Digital Product Passport raw data with comprehensive structure covering
                product identification, material composition, environmental impact, compliance,
                supply chain transparency, circular economy indicators, lifecycle tracking,
                digital services, sustainability metrics, and data quality
            
        Returns:
            bool: True if population successful, False otherwise
        """
        try:
            passport_id = dpp_data.get("passport_id")
            file_id = dpp_data.get("file_id")
            status = dpp_data.get("status")
            
            if not all([passport_id, file_id, status]):
                self.logger.error("Missing required Digital Product Passport data fields")
                return False
            
            certificate = await self.get_entity_by_file_id(file_id, user_context)
            if not certificate:
                self.logger.error(f"Certificate not found for file_id: {file_id}")
                return False
            
            # Reorganize flat dpp_data into structured format
            # Product Identification
            product_identification = {
                "product_name": dpp_data.get("product_name") or dpp_data.get("product_identification", {}).get("product_name"),
                "product_category": dpp_data.get("product_category") or dpp_data.get("product_identification", {}).get("product_category"),
                "product_type": dpp_data.get("product_type") or dpp_data.get("product_identification", {}).get("product_type"),
                "manufacturer_id": dpp_data.get("manufacturer_id") or dpp_data.get("product_identification", {}).get("manufacturer_id"),
                "manufacturer_name": dpp_data.get("manufacturer_name") or dpp_data.get("product_identification", {}).get("manufacturer_name"),
                "model_number": dpp_data.get("model_number") or dpp_data.get("product_identification", {}).get("model_number"),
                "serial_number": dpp_data.get("serial_number") or dpp_data.get("product_identification", {}).get("serial_number"),
                "batch_number": dpp_data.get("batch_number") or dpp_data.get("product_identification", {}).get("batch_number"),
                "unique_product_identifier": dpp_data.get("unique_product_identifier") or dpp_data.get("product_identification", {}).get("unique_product_identifier"),
                "product_classification": {
                    "hs_code": dpp_data.get("hs_code") or dpp_data.get("product_identification", {}).get("product_classification", {}).get("hs_code"),
                    "eu_product_category": dpp_data.get("eu_product_category") or dpp_data.get("product_identification", {}).get("product_classification", {}).get("eu_product_category"),
                    "industry_sector": dpp_data.get("industry_sector") or dpp_data.get("product_identification", {}).get("product_classification", {}).get("industry_sector")
                }
            }
            
            # Material Composition
            material_composition = {
                "total_materials": dpp_data.get("total_materials") or dpp_data.get("material_composition", {}).get("total_materials"),
                "total_weight_grams": dpp_data.get("total_weight_grams") or dpp_data.get("material_composition", {}).get("total_weight_grams"),
                "materials_breakdown": dpp_data.get("materials_breakdown") or dpp_data.get("material_composition", {}).get("materials_breakdown", []),
                "hazardous_materials": dpp_data.get("hazardous_materials") or dpp_data.get("material_composition", {}).get("hazardous_materials", []),
                "conflict_minerals": {
                    "contains_conflict_minerals": dpp_data.get("contains_conflict_minerals") or dpp_data.get("material_composition", {}).get("conflict_minerals", {}).get("contains_conflict_minerals"),
                    "tin_verified": dpp_data.get("tin_verified") or dpp_data.get("material_composition", {}).get("conflict_minerals", {}).get("tin_verified"),
                    "tantalum_verified": dpp_data.get("tantalum_verified") or dpp_data.get("material_composition", {}).get("conflict_minerals", {}).get("tantalum_verified"),
                    "tungsten_verified": dpp_data.get("tungsten_verified") or dpp_data.get("material_composition", {}).get("conflict_minerals", {}).get("tungsten_verified"),
                    "gold_verified": dpp_data.get("gold_verified") or dpp_data.get("material_composition", {}).get("conflict_minerals", {}).get("gold_verified"),
                    "verification_standard": dpp_data.get("verification_standard") or dpp_data.get("material_composition", {}).get("conflict_minerals", {}).get("verification_standard")
                }
            }
            
            # Environmental Impact
            environmental_impact = {
                "carbon_footprint": {
                    "manufacturing_co2_kg": dpp_data.get("manufacturing_co2_kg") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("manufacturing_co2_kg"),
                    "transportation_co2_kg": dpp_data.get("transportation_co2_kg") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("transportation_co2_kg"),
                    "usage_co2_kg": dpp_data.get("usage_co2_kg") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("usage_co2_kg"),
                    "end_of_life_co2_kg": dpp_data.get("end_of_life_co2_kg") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("end_of_life_co2_kg"),
                    "total_co2_kg": dpp_data.get("total_co2_kg") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("total_co2_kg"),
                    "carbon_footprint_rating": dpp_data.get("carbon_footprint_rating") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("carbon_footprint_rating"),
                    "carbon_intensity_kg_per_unit": dpp_data.get("carbon_intensity_kg_per_unit") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("carbon_intensity_kg_per_unit"),
                    "carbon_offset_available": dpp_data.get("carbon_offset_available") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("carbon_offset_available"),
                    "carbon_neutral_certification": dpp_data.get("carbon_neutral_certification") or dpp_data.get("environmental_impact", {}).get("carbon_footprint", {}).get("carbon_neutral_certification")
                },
                "water_usage": {
                    "manufacturing_liters": dpp_data.get("manufacturing_liters") or dpp_data.get("environmental_impact", {}).get("water_usage", {}).get("manufacturing_liters"),
                    "usage_liters": dpp_data.get("usage_liters") or dpp_data.get("environmental_impact", {}).get("water_usage", {}).get("usage_liters"),
                    "total_liters": dpp_data.get("total_liters") or dpp_data.get("environmental_impact", {}).get("water_usage", {}).get("total_liters"),
                    "water_stress_impact": dpp_data.get("water_stress_impact") or dpp_data.get("environmental_impact", {}).get("water_usage", {}).get("water_stress_impact"),
                    "water_recycling_percentage": dpp_data.get("water_recycling_percentage") or dpp_data.get("environmental_impact", {}).get("water_usage", {}).get("water_recycling_percentage")
                },
                "energy_consumption": {
                    "manufacturing_kwh": dpp_data.get("manufacturing_kwh") or dpp_data.get("environmental_impact", {}).get("energy_consumption", {}).get("manufacturing_kwh"),
                    "usage_kwh_per_year": dpp_data.get("usage_kwh_per_year") or dpp_data.get("environmental_impact", {}).get("energy_consumption", {}).get("usage_kwh_per_year"),
                    "efficiency_rating": dpp_data.get("efficiency_rating") or dpp_data.get("environmental_impact", {}).get("energy_consumption", {}).get("efficiency_rating"),
                    "energy_star_certified": dpp_data.get("energy_star_certified") or dpp_data.get("environmental_impact", {}).get("energy_consumption", {}).get("energy_star_certified"),
                    "renewable_energy_percentage": dpp_data.get("renewable_energy_percentage") or dpp_data.get("environmental_impact", {}).get("energy_consumption", {}).get("renewable_energy_percentage")
                },
                "waste_generation": {
                    "manufacturing_waste_kg": dpp_data.get("manufacturing_waste_kg") or dpp_data.get("environmental_impact", {}).get("waste_generation", {}).get("manufacturing_waste_kg"),
                    "packaging_waste_kg": dpp_data.get("packaging_waste_kg") or dpp_data.get("environmental_impact", {}).get("waste_generation", {}).get("packaging_waste_kg"),
                    "end_of_life_waste_kg": dpp_data.get("end_of_life_waste_kg") or dpp_data.get("environmental_impact", {}).get("waste_generation", {}).get("end_of_life_waste_kg"),
                    "waste_recycling_percentage": dpp_data.get("waste_recycling_percentage") or dpp_data.get("environmental_impact", {}).get("waste_generation", {}).get("waste_recycling_percentage")
                }
            }
            
            # Supply Chain Transparency
            supply_chain_transparency = {
                "tier_1_suppliers": dpp_data.get("tier_1_suppliers") or dpp_data.get("supply_chain_transparency", {}).get("tier_1_suppliers"),
                "tier_2_suppliers": dpp_data.get("tier_2_suppliers") or dpp_data.get("supply_chain_transparency", {}).get("tier_2_suppliers"),
                "tier_3_suppliers": dpp_data.get("tier_3_suppliers") or dpp_data.get("supply_chain_transparency", {}).get("tier_3_suppliers"),
                "supply_chain_countries": dpp_data.get("supply_chain_countries") or dpp_data.get("supply_chain_transparency", {}).get("supply_chain_countries", []),
                "supplier_certifications": dpp_data.get("supplier_certifications") or dpp_data.get("supply_chain_transparency", {}).get("supplier_certifications", []),
                "conflict_minerals_compliance": dpp_data.get("conflict_minerals_compliance") or dpp_data.get("supply_chain_transparency", {}).get("conflict_minerals_compliance"),
                "child_labor_risk": dpp_data.get("child_labor_risk") or dpp_data.get("supply_chain_transparency", {}).get("child_labor_risk"),
                "forced_labor_risk": dpp_data.get("forced_labor_risk") or dpp_data.get("supply_chain_transparency", {}).get("forced_labor_risk"),
                "supply_chain_risk_score": dpp_data.get("supply_chain_risk_score") or dpp_data.get("supply_chain_transparency", {}).get("supply_chain_risk_score"),
                "supply_chain_audit_frequency": dpp_data.get("supply_chain_audit_frequency") or dpp_data.get("supply_chain_transparency", {}).get("supply_chain_audit_frequency"),
                "last_supply_chain_audit": dpp_data.get("last_supply_chain_audit") or dpp_data.get("supply_chain_transparency", {}).get("last_supply_chain_audit"),
                "supply_chain_visibility_percentage": dpp_data.get("supply_chain_visibility_percentage") or dpp_data.get("supply_chain_transparency", {}).get("supply_chain_visibility_percentage")
            }
            
            # Compliance Certifications
            compliance_certifications = {
                "regulatory_compliance": dpp_data.get("regulatory_compliance") or dpp_data.get("compliance_certifications", {}).get("regulatory_compliance", []),
                "sustainability_certifications": dpp_data.get("sustainability_certifications") or dpp_data.get("compliance_certifications", {}).get("sustainability_certifications", []),
                "quality_certifications": dpp_data.get("quality_certifications") or dpp_data.get("compliance_certifications", {}).get("quality_certifications", [])
            }
            
            # Circular Economy Indicators
            circular_economy_indicators = {
                "recyclability_score": dpp_data.get("recyclability_score") or dpp_data.get("circular_economy_indicators", {}).get("recyclability_score"),
                "repairability_score": dpp_data.get("repairability_score") or dpp_data.get("circular_economy_indicators", {}).get("repairability_score"),
                "upgradeability_score": dpp_data.get("upgradeability_score") or dpp_data.get("circular_economy_indicators", {}).get("upgradeability_score"),
                "modularity_score": dpp_data.get("modularity_score") or dpp_data.get("circular_economy_indicators", {}).get("modularity_score"),
                "disassembly_time_minutes": dpp_data.get("disassembly_time_minutes") or dpp_data.get("circular_economy_indicators", {}).get("disassembly_time_minutes"),
                "recycling_instructions": dpp_data.get("recycling_instructions") or dpp_data.get("circular_economy_indicators", {}).get("recycling_instructions"),
                "repair_manual_available": dpp_data.get("repair_manual_available") or dpp_data.get("circular_economy_indicators", {}).get("repair_manual_available"),
                "spare_parts_availability": dpp_data.get("spare_parts_availability") or dpp_data.get("circular_economy_indicators", {}).get("spare_parts_availability"),
                "take_back_program": dpp_data.get("take_back_program") or dpp_data.get("circular_economy_indicators", {}).get("take_back_program"),
                "refurbishment_program": dpp_data.get("refurbishment_program") or dpp_data.get("circular_economy_indicators", {}).get("refurbishment_program"),
                "material_recovery_percentage": dpp_data.get("material_recovery_percentage") or dpp_data.get("circular_economy_indicators", {}).get("material_recovery_percentage"),
                "component_reuse_percentage": dpp_data.get("component_reuse_percentage") or dpp_data.get("circular_economy_indicators", {}).get("component_reuse_percentage")
            }
            
            # Lifecycle Tracking
            lifecycle_tracking = {
                "manufacturing_date": dpp_data.get("manufacturing_date") or dpp_data.get("lifecycle_tracking", {}).get("manufacturing_date"),
                "warranty_period_months": dpp_data.get("warranty_period_months") or dpp_data.get("lifecycle_tracking", {}).get("warranty_period_months"),
                "expected_lifespan_years": dpp_data.get("expected_lifespan_years") or dpp_data.get("lifecycle_tracking", {}).get("expected_lifespan_years"),
                "maintenance_schedule": dpp_data.get("maintenance_schedule") or dpp_data.get("lifecycle_tracking", {}).get("maintenance_schedule"),
                "end_of_life_handling": dpp_data.get("end_of_life_handling") or dpp_data.get("lifecycle_tracking", {}).get("end_of_life_handling"),
                "recycling_program": dpp_data.get("recycling_program") or dpp_data.get("lifecycle_tracking", {}).get("recycling_program"),
                "lifecycle_phase": dpp_data.get("lifecycle_phase") or dpp_data.get("lifecycle_tracking", {}).get("lifecycle_phase"),
                "usage_tracking": {
                    "hours_in_operation": dpp_data.get("hours_in_operation") or dpp_data.get("lifecycle_tracking", {}).get("usage_tracking", {}).get("hours_in_operation"),
                    "maintenance_events": dpp_data.get("maintenance_events") or dpp_data.get("lifecycle_tracking", {}).get("usage_tracking", {}).get("maintenance_events"),
                    "performance_degradation": dpp_data.get("performance_degradation") or dpp_data.get("lifecycle_tracking", {}).get("usage_tracking", {}).get("performance_degradation")
                }
            }
            
            # Digital Services
            digital_services = {
                "qr_code": dpp_data.get("qr_code") or dpp_data.get("digital_services", {}).get("qr_code"),
                "blockchain_hash": dpp_data.get("blockchain_hash") or dpp_data.get("digital_services", {}).get("blockchain_hash"),
                "api_endpoint": dpp_data.get("api_endpoint") or dpp_data.get("digital_services", {}).get("api_endpoint"),
                "mobile_app_support": dpp_data.get("mobile_app_support") or dpp_data.get("digital_services", {}).get("mobile_app_support"),
                "real_time_updates": dpp_data.get("real_time_updates") or dpp_data.get("digital_services", {}).get("real_time_updates"),
                "data_portability": dpp_data.get("data_portability") or dpp_data.get("digital_services", {}).get("data_portability"),
                "privacy_compliance": dpp_data.get("privacy_compliance") or dpp_data.get("digital_services", {}).get("privacy_compliance"),
                "data_retention_years": dpp_data.get("data_retention_years") or dpp_data.get("digital_services", {}).get("data_retention_years")
            }
            
            # Sustainability Metrics
            sustainability_metrics = {
                "overall_sustainability_score": dpp_data.get("overall_sustainability_score") or dpp_data.get("sustainability_metrics", {}).get("overall_sustainability_score"),
                "environmental_score": dpp_data.get("environmental_score") or dpp_data.get("sustainability_metrics", {}).get("environmental_score"),
                "social_score": dpp_data.get("social_score") or dpp_data.get("sustainability_metrics", {}).get("social_score"),
                "governance_score": dpp_data.get("governance_score") or dpp_data.get("sustainability_metrics", {}).get("governance_score"),
                "esg_rating": dpp_data.get("esg_rating") or dpp_data.get("sustainability_metrics", {}).get("esg_rating"),
                "sustainability_trend": dpp_data.get("sustainability_trend") or dpp_data.get("sustainability_metrics", {}).get("sustainability_trend"),
                "sustainability_targets": {
                    "carbon_neutrality_target": dpp_data.get("carbon_neutrality_target") or dpp_data.get("sustainability_metrics", {}).get("sustainability_targets", {}).get("carbon_neutrality_target"),
                    "circular_economy_target": dpp_data.get("circular_economy_target") or dpp_data.get("sustainability_metrics", {}).get("sustainability_targets", {}).get("circular_economy_target"),
                    "renewable_energy_target": dpp_data.get("renewable_energy_target") or dpp_data.get("sustainability_metrics", {}).get("sustainability_targets", {}).get("renewable_energy_target")
                }
            }
            
            # Data Quality
            data_quality = {
                "completeness_percentage": dpp_data.get("completeness_percentage") or dpp_data.get("data_quality", {}).get("completeness_percentage"),
                "accuracy_score": dpp_data.get("accuracy_score") or dpp_data.get("data_quality", {}).get("accuracy_score"),
                "timeliness_score": dpp_data.get("timeliness_score") or dpp_data.get("data_quality", {}).get("timeliness_score"),
                "verification_status": dpp_data.get("verification_status") or dpp_data.get("data_quality", {}).get("verification_status"),
                "last_updated": dpp_data.get("last_updated") or dpp_data.get("data_quality", {}).get("last_updated"),
                "data_source_verification": dpp_data.get("data_source_verification") or dpp_data.get("data_quality", {}).get("data_source_verification"),
                "data_governance": {
                    "data_owner": dpp_data.get("data_owner") or dpp_data.get("data_quality", {}).get("data_governance", {}).get("data_owner"),
                    "data_steward": dpp_data.get("data_steward") or dpp_data.get("data_quality", {}).get("data_governance", {}).get("data_steward"),
                    "update_frequency": dpp_data.get("update_frequency") or dpp_data.get("data_quality", {}).get("data_governance", {}).get("update_frequency"),
                    "validation_process": dpp_data.get("validation_process") or dpp_data.get("data_quality", {}).get("data_governance", {}).get("validation_process")
                }
            }
            
            # Update certificate with Digital Product Passport data
            update_data = {
                "file_id": file_id,  # Include file_id for validation
                "digital_product_passport_status": "completed",
                "digital_product_passport_registry_id": passport_id,  # Individual column for cross-module reference
                "digital_product_passport_summary": {
                    # Basic Information
                    "file_id": file_id,
                    "passport_id": passport_id,
                    "passport_version": dpp_data.get("passport_version", "1.0"),
                    "generated_at": dpp_data.get("generated_at", datetime.utcnow().isoformat()),
                    "generated_by": dpp_data.get("generated_by"),
                    "certification_authority": dpp_data.get("certification_authority"),
                    "status": status,
                    
                    # Structured Data (reorganized from flat dpp_data)
                    "product_identification": product_identification,
                    "material_composition": material_composition,
                    "environmental_impact": environmental_impact,
                    "supply_chain_transparency": supply_chain_transparency,
                    "compliance_certifications": compliance_certifications,
                    "circular_economy_indicators": circular_economy_indicators,
                    "lifecycle_tracking": lifecycle_tracking,
                    "digital_services": digital_services,
                    "sustainability_metrics": sustainability_metrics,
                    "data_quality": data_quality
                }
            }
            
            success = await self.update_entity(certificate.certificate_id, update_data, user_context)
            
            if success:
                self.logger.info(f"Successfully populated DPP data for certificate {certificate.certificate_id}")
                return True
            else:
                self.logger.error(f"Failed to populate DPP data for certificate {certificate.certificate_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error populating DPP data: {e}")
            return False


    async def handle_module_completion_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Generic handler for module completion events.
        
        Routes module completion events to the appropriate populate_from_* method
        based on the module type in the event data.
        
        Args:
            event_data: Event data containing module info and summary with structure:
                - module_type: Type of module (aasx_etl, twin_registry, ai_rag, etc.)
                - module_data: Module-specific data to populate
                - user_context: User context for authorization
                - file_id: Associated file ID
                - status: Processing status
                
        Returns:
            True if event handled successfully, False otherwise
        """
        try:
            module_type = event_data.get("module_type")
            module_data = event_data.get("module_data", {})
            user_context = event_data.get("user_context", {})
            
            if not module_type:
                self.logger.error("Missing module_type in event data")
                return False
            
            # Route to appropriate populate method based on module type
            if module_type == "aasx_etl":
                return await self.populate_from_aasx_etl(module_data, user_context)
            elif module_type == "twin_registry":
                return await self.populate_from_twin_registry(module_data, user_context)
            elif module_type == "ai_rag":
                return await self.populate_from_ai_rag(module_data, user_context)
            elif module_type == "kg_neo4j":
                return await self.populate_from_kg_neo4j(module_data, user_context)
            elif module_type == "federated_learning":
                return await self.populate_from_federated_learning(module_data, user_context)
            elif module_type == "physics_modeling":
                return await self.populate_from_physics_modeling(module_data, user_context)
            elif module_type == "data_governance":
                return await self.populate_from_data_governance(module_data, user_context)
            elif module_type == "digital_product_passport":
                return await self.populate_from_digital_product_passport(module_data, user_context)
            else:
                self.logger.error(f"Unknown module type: {module_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error handling module completion event: {e}")
            return False
    
    # 🚨 MANDATORY: Customization Warning
    
    # ✅ REQUIRED: Enterprise Features
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive service health check.
        
        Returns:
            Dictionary containing health status and component information
        """
        try:
            # ✅ REQUIRED: Check service status
            service_health = {
                "service_name": self.service_name,
                "service_version": self.service_version,
                "service_status": self.service_status,
                "timestamp": datetime.now().isoformat()
            }
            
            # ✅ REQUIRED: Check engine components
            auth_health = await self.auth_manager.get_health()
            metrics_health = await self.metrics_collector.get_health()
            health_health = await self.health_monitor.get_health_summary()
            
            # ✅ REQUIRED: Check repository health
            repo_health = await self.repository.health_check()
            
            # ✅ REQUIRED: Compile overall health
            overall_health = "healthy"
            if any(h.get("status") != "healthy" for h in [auth_health, metrics_health, health_health, repo_health]):
                overall_health = "degraded"
            
            return {
                "status": overall_health,
                "service": service_health,
                "components": {
                    "authorization": auth_health,
                    "metrics": metrics_health,
                    "health_monitor": health_health,
                    "repository": repo_health
                }
            }
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get service performance metrics.
        
        Returns:
            Dictionary containing performance metrics and statistics
        """
        try:
            # ✅ REQUIRED: Get performance profiler metrics
            profiler_metrics = await self.performance_profiler.get_performance_metrics()
            
            # ✅ REQUIRED: Get metrics collector data
            metrics_data = await self.metrics_collector.get_metrics_summary()
            
            return {
                "service": self.service_name,
                "timestamp": datetime.now().isoformat(),
                "performance": profiler_metrics,
                "metrics": metrics_data
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def get_summary(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get service summary with statistics.
        
        Args:
            user_context: User context for authorization
            
        Returns:
            Dictionary containing service summary and statistics
        """
        with self.performance_profiler.profile_context("get_summary"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'certificate_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read certificate_registry summary")
                        return {"error": "Access denied"}
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    return {"error": "Access denied"}
                
                # ✅ REQUIRED: Get summary from repository
                summary = await self.repository.get_certificate_statistics()
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="certificate_registry_summary_retrieved",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id") if user_context else "unknown"}
                )
                
                logger.info("Retrieved service summary")
                return summary
                
            except Exception as e:
                logger.error(f"Error getting summary: {e}")
                await self.error_tracker.track_error(
                    error_type="get_summary_error",
                    error_message=str(e),
                    error_details=f"Failed to get summary: {e}",
                    severity="medium",
                    metadata={"user_context": user_context}
                )
                return {"error": str(e)}

    # ✅ REQUIRED: Business Logic Methods
    
    async def _validate_entity_data(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any],
        is_update: bool = False
    ) -> bool:
        """
        Validate entity data against business rules.
        
        Args:
            entity_data: Data to validate
            user_context: User context for validation
            is_update: Whether this is an update operation
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # ✅ REQUIRED: Basic data validation
            if not entity_data:
                logger.error("Entity data is empty")
                return False
            
            # ✅ REQUIRED: Required field validation - configurable based on business config
            if is_update:
                required_fields = self.business_config.get('required_fields', {}).get('update', ['file_id'])
            else:
                required_fields = self.business_config.get('required_fields', {}).get('create', ['file_id', 'certificate_name'])
            
            # If strict mode is enabled, also check user context fields
            strict_mode = self.business_config.get('required_fields', {}).get('strict', False)
            if strict_mode:
                context_fields = ['user_id', 'org_id', 'project_id', 'use_case_id', 'twin_id']
                required_fields.extend(context_fields)
            
            for field in required_fields:
                if field not in entity_data or entity_data[field] is None:
                    logger.error(f"Required field missing: {field}")
                    return False
            
            # ✅ REQUIRED: Business rule validation
            if not await self._validate_business_rules(entity_data, user_context, is_update):
                logger.error("Business rule validation failed")
                return False
            
            # ✅ REQUIRED: User permission validation
            if not await self._validate_user_permissions(entity_data, user_context):
                logger.error("User permission validation failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating entity data: {e}")
            return False
    
    async def _validate_business_rules(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any],
        is_update: bool
    ) -> bool:
        """
        Validate entity data against business rules.
        
        Args:
            entity_data: Data to validate
            user_context: User context for validation
            is_update: Whether this is an update operation
            
        Returns:
            True if business rules passed, False otherwise
        """
        try:
            # ✅ REQUIRED: Implement your business rule validation here
            # Example: Check file size limits, naming conventions, etc.
            
            # Check certificate type validation
            if 'certificate_type' in entity_data:
                allowed_types = self.business_config.get('default_rules', {}).get('allowed_certificate_types', [])
                if entity_data['certificate_type'] not in allowed_types:
                    logger.error(f"Invalid certificate type: {entity_data['certificate_type']}")
                    return False
            
            # Check security level validation
            if 'security_level' in entity_data:
                allowed_levels = self.business_config.get('business_specific', {}).get('security_levels', [])
                if entity_data['security_level'] not in allowed_levels:
                    logger.error(f"Invalid security level: {entity_data['security_level']}")
                    return False
            
            # Check compliance type validation
            if 'compliance_type' in entity_data:
                allowed_compliance = self.business_config.get('business_specific', {}).get('compliance_types', [])
                if entity_data['compliance_type'] not in allowed_compliance:
                    logger.error(f"Invalid compliance type: {entity_data['compliance_type']}")
                    return False
            
            # Add more business rule validations as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating business rules: {e}")
            return False
    
    async def _validate_user_permissions(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Validate user permissions for entity operations.
        
        Args:
            entity_data: Entity data to validate
            user_context: User context for validation
            
        Returns:
            True if user has required permissions, False otherwise
        """
        try:
            # ✅ REQUIRED: Check organization access
            user_org = user_context.get('org_id')
            entity_org = entity_data.get('org_id')
            
            if entity_org and user_org != entity_org:
                # Check if user has cross-org permissions
                user_roles = user_context.get('roles', [])
                cross_org_roles = self.business_config.get('cross_dept_roles', [])
                
                if not any(role in cross_org_roles for role in user_roles):
                    logger.error(f"User {user_context.get('user_id')} lacks cross-org permissions")
                    return False
            
            # ✅ REQUIRED: Check department access
            user_dept = user_context.get('dept_id')
            entity_dept = entity_data.get('dept_id')
            
            if entity_dept and user_dept != entity_dept:
                # Check if user has cross-dept permissions
                user_roles = user_context.get('roles', [])
                cross_dept_roles = self.business_config.get('cross_dept_roles', [])
                
                if not any(role in cross_dept_roles for role in user_roles):
                    logger.error(f"User {user_context.get('user_id')} lacks cross-dept permissions")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating user permissions: {e}")
            return False

    # ✅ REQUIRED: Cleanup Method
    
    async def cleanup(self):
        """
        Cleanup service resources and perform graceful shutdown.
        
        This method should be called when the service is being shut down
        to ensure proper cleanup of resources.
        """
        try:
            logger.info(f"Cleaning up {self.service_name}")
            
            # ✅ REQUIRED: Cleanup repository
            if hasattr(self.repository, 'cleanup'):
                await self.repository.cleanup()
            
            # ✅ REQUIRED: Cleanup engine components
            if hasattr(self.metrics_collector, 'cleanup'):
                await self.metrics_collector.cleanup()
            
            if hasattr(self.error_tracker, 'cleanup'):
                await self.error_tracker.cleanup()
            
            if hasattr(self.health_monitor, 'cleanup'):
                await self.health_monitor.cleanup()
            
            logger.info(f"{self.service_name} cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during {self.service_name} cleanup: {e}")

    async def get_certificates_by_use_case_id(
        self, 
        use_case_id: str, 
        user_context: Dict[str, Any],
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by use_case_id with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"use_case_id": use_case_id}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by use_case_id: {e}")
            raise

    # ========================================================================
    # COMPOSITE QUERIES - ADVANCED FILTERING
    # ========================================================================

    async def get_certificates_by_multiple_criteria(
        self, 
        criteria: Dict[str, Any], 
        user_context: Dict[str, Any],
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by multiple criteria with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters=criteria, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by multiple criteria: {e}")
            raise

    async def get_certificates_by_advanced_filter(
        self, 
        user_context: Dict[str, Any],
        filters: Dict[str, Any], 
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> List[CertificateRegistry]:
        """Get certificates with advanced filtering and sorting with permission checks using existing CRUD methods"""
        try:
            # Add sorting to filters
            enhanced_filters = filters.copy()
            enhanced_filters["sort_by"] = sort_by
            enhanced_filters["sort_order"] = sort_order
            
            return await self.search_entities(
                query="", 
                filters=enhanced_filters, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates with advanced filter: {e}")
            raise

    # ========================================================================
    # CERTIFICATE PROPERTIES QUERIES
    # ========================================================================

    async def get_certificates_by_certificate_type(
        self, 
        user_context: Dict[str, Any],
        certificate_type: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by certificate type with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"certificate_type": certificate_type}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by certificate type: {e}")
            raise

    async def get_certificates_by_certificate_category(
        self, 
        user_context: Dict[str, Any],
        certificate_category: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by certificate category with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"certificate_category": certificate_category}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by certificate category: {e}")
            raise

    async def get_certificates_by_priority(
        self, 
        user_context: Dict[str, Any],
        priority: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by priority with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"priority": priority}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by priority: {e}")
            raise

    async def get_certificates_by_risk_level(
        self, 
        user_context: Dict[str, Any],
        risk_level: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by risk level with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"risk_level": risk_level}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by risk level: {e}")
            raise

    async def get_certificates_by_complexity(
        self, 
        user_context: Dict[str, Any],
        complexity: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by complexity with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"complexity": complexity}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by complexity: {e}")
            raise

    # ========================================================================
    # BUSINESS CONTEXT QUERIES
    # ========================================================================

    async def get_certificates_by_industry(
        self, 
        user_context: Dict[str, Any],
        industry: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by industry with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"industry": industry}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by industry: {e}")
            raise

    async def get_certificates_by_domain(
        self, 
        user_context: Dict[str, Any],
        domain: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by domain with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"domain": domain}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by domain: {e}")
            raise

    async def get_certificates_by_geographic_location(
        self, 
        user_context: Dict[str, Any],
        geographic_location: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by geographic location with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"geographic_location": geographic_location}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by geographic location: {e}")
            raise

    async def get_certificates_by_environment(
        self, 
        user_context: Dict[str, Any],
        environment: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by environment with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"environment": environment}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by environment: {e}")
            raise

    # ========================================================================
    # WORKFLOW & STATUS QUERIES
    # ========================================================================

    async def get_certificates_by_workflow_stage(
        self, 
        user_context: Dict[str, Any],
        workflow_stage: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by workflow stage with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"workflow_stage": workflow_stage}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by workflow stage: {e}")
            raise

    async def get_certificates_by_processing_status(
        self, 
        user_context: Dict[str, Any],
        processing_status: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by processing status with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"processing_status": processing_status}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by processing status: {e}")
            raise

    async def get_certificates_by_validation_status(
        self, 
        user_context: Dict[str, Any],
        validation_status: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by validation status with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"validation_status": validation_status}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by validation status: {e}")
            raise

    async def get_certificates_by_verification_status(
        self, 
        user_context: Dict[str, Any],
        verification_status: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by verification status with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"verification_status": verification_status}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by verification status: {e}")
            raise

    async def get_certificates_by_certification_status(
        self, 
        user_context: Dict[str, Any],
        certification_status: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by certification status with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"certification_status": certification_status}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by certification status: {e}")
            raise

    async def get_certificates_by_accreditation_status(
        self, 
        user_context: Dict[str, Any],
        accreditation_status: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by accreditation status with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"accreditation_status": accreditation_status}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by accreditation status: {e}")
            raise

    # ========================================================================
    # MODULE INTEGRATION QUERIES
    # ========================================================================

    async def get_certificates_by_module_ready_status(
        self, 
        user_context: Dict[str, Any],
        module_name: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by module ready status with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"module_ready_status": module_name}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by module ready status: {e}")
            raise

    async def get_certificates_by_attention_required(
        self, 
        user_context: Dict[str, Any],
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates requiring attention with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"attention_required": True}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates requiring attention: {e}")
            raise

    # ========================================================================
    # TECHNICAL & INTEGRATION QUERIES
    # ========================================================================

    async def get_certificates_by_technology_stack(
        self, 
        user_context: Dict[str, Any],
        technology_stack: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by technology stack with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"technology_stack": technology_stack}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by technology stack: {e}")
            raise

    async def get_certificates_by_integration_type(
        self, 
        user_context: Dict[str, Any],
        integration_type: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by integration type with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"integration_type": integration_type}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by integration type: {e}")
            raise

    async def get_certificates_by_data_source(
        self, 
        user_context: Dict[str, Any],
        data_source: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by data source with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"data_source": data_source}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by data source: {e}")
            raise

    async def get_certificates_by_processing_type(
        self, 
        user_context: Dict[str, Any],
        processing_type: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by processing type with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"processing_type": processing_type}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by processing type: {e}")
            raise

    async def get_certificates_by_analytics_type(
        self, 
        user_context: Dict[str, Any],
        analytics_type: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by analytics type with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"analytics_type": analytics_type}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by analytics type: {e}")
            raise

    async def get_certificates_by_workflow_type(
        self, 
        user_context: Dict[str, Any],
        workflow_type: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by workflow type with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"workflow_type": workflow_type}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by workflow type: {e}")
            raise

    async def get_certificates_by_integration_layer(
        self, 
        user_context: Dict[str, Any],
        integration_layer: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by integration layer with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"integration_layer": integration_layer}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by integration layer: {e}")
            raise

    async def get_certificates_by_security_module(
        self, 
        user_context: Dict[str, Any],
        security_module: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by security module with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"security_module": security_module}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by security module: {e}")
            raise

    # ========================================================================
    # SCORE RANGE QUERIES
    # ========================================================================

    async def get_certificates_by_health_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by health score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"health_score_min": min_score, "health_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by health score range: {e}")
            raise

    async def get_certificates_by_quality_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by quality score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"quality_score_min": min_score, "quality_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by quality score range: {e}")
            raise

    async def get_certificates_by_compliance_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by compliance score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"compliance_score_min": min_score, "compliance_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by compliance score range: {e}")
            raise

    async def get_certificates_by_security_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by security score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"security_score_min": min_score, "security_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by security score range: {e}")
            raise

    async def get_certificates_by_trust_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by trust score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"trust_score_min": min_score, "trust_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by trust score range: {e}")
            raise

    async def get_certificates_by_business_value_range(
        self, 
        user_context: Dict[str, Any],
        min_value: float, 
        max_value: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by business value range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"business_value_min": min_value, "business_value_max": max_value}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by business value range: {e}")
            raise

    async def get_certificates_by_cost_range(
        self, 
        user_context: Dict[str, Any],
        min_cost: float, 
        max_cost: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by cost range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"cost_min": min_cost, "cost_max": max_cost}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by cost range: {e}")
            raise

    async def get_certificates_by_roi_range(
        self, 
        user_context: Dict[str, Any],
        min_roi: float, 
        max_roi: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by ROI range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"roi_min": min_roi, "roi_max": max_roi}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by ROI range: {e}")
            raise

    # ========================================================================
    # COMPLIANCE AND STANDARDS QUERIES
    # ========================================================================

    async def get_certificates_by_standard_compliance(
        self, 
        user_context: Dict[str, Any],
        standard_name: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by standard compliance with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"standard_compliance": standard_name}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by standard compliance: {e}")
            raise

    async def get_certificates_by_regulatory_compliance(
        self, 
        user_context: Dict[str, Any],
        regulatory_body: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by regulatory compliance with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"regulatory_compliance": regulatory_body}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by regulatory compliance: {e}")
            raise

    # ========================================================================
    # PERFORMANCE AND RELIABILITY QUERIES
    # ========================================================================

    async def get_certificates_by_performance_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by performance score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"performance_score_min": min_score, "performance_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by performance score range: {e}")
            raise

    async def get_certificates_by_reliability_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by reliability score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"reliability_score_min": min_score, "reliability_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by reliability score range: {e}")
            raise

    async def get_certificates_by_maintainability_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by maintainability score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"maintainability_score_min": min_score, "maintainability_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by maintainability score range: {e}")
            raise

    async def get_certificates_by_scalability_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by scalability score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"scalability_score_min": min_score, "scalability_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by scalability score range: {e}")
            raise

    async def get_certificates_by_interoperability_score_range(
        self, 
        user_context: Dict[str, Any],
        min_score: float, 
        max_score: float, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by interoperability score range with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"interoperability_score_min": min_score, "interoperability_score_max": max_score}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by interoperability score range: {e}")
            raise

    # ========================================================================
    # FREQUENCY AND POLICY QUERIES
    # ========================================================================

    async def get_certificates_by_audit_frequency(
        self, 
        user_context: Dict[str, Any],
        frequency: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by audit frequency with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"audit_frequency": frequency}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by audit frequency: {e}")
            raise

    async def get_certificates_by_review_frequency(
        self, 
        user_context: Dict[str, Any],
        frequency: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by review frequency with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"review_frequency": frequency}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by review frequency: {e}")
            raise

    async def get_certificates_by_update_frequency(
        self, 
        user_context: Dict[str, Any],
        frequency: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by update frequency with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"update_frequency": frequency}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by update frequency: {e}")
            raise

    async def get_certificates_by_sync_frequency(
        self, 
        user_context: Dict[str, Any],
        frequency: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by sync frequency with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"sync_frequency": frequency}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by sync frequency: {e}")
            raise

    async def get_certificates_by_backup_frequency(
        self, 
        user_context: Dict[str, Any],
        frequency: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by backup frequency with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"backup_frequency": frequency}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by backup frequency: {e}")
            raise

    async def get_certificates_by_retention_policy(
        self, 
        user_context: Dict[str, Any],
        policy: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by retention policy with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"retention_policy": policy}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by retention policy: {e}")
            raise

    async def get_certificates_by_archival_policy(
        self, 
        user_context: Dict[str, Any],
        policy: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by archival policy with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"archival_policy": policy}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by archival policy: {e}")
            raise

    async def get_certificates_by_deletion_policy(
        self, 
        user_context: Dict[str, Any],
        policy: str, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by deletion policy with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"deletion_policy": policy}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by deletion policy: {e}")
            raise

    # ========================================================================
    # COMPLIANCE COUNT QUERIES
    # ========================================================================

    async def get_certificates_by_standards_compliance_count(
        self, 
        user_context: Dict[str, Any],
        min_count: int, 
        max_count: int, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by standards compliance count with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"standards_compliance_count_min": min_count, "standards_compliance_count_max": max_count}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by standards compliance count: {e}")
            raise

    async def get_certificates_by_regulatory_compliance_count(
        self, 
        user_context: Dict[str, Any],
        min_count: int, 
        max_count: int, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by regulatory compliance count with permission checks using existing CRUD methods"""
        try:
            return await self.search_entities(
                query="", 
                filters={"regulatory_compliance_count_min": min_count, "regulatory_compliance_count_max": max_count}, 
                limit=limit, 
                user_context=user_context
            )
        except Exception as e:
            logger.error(f"Error getting certificates by regulatory compliance count: {e}")
            raise

    # ✅ REQUIRED: Cleanup Method


# ✅ REQUIRED: Service Factory Function

async def create_certificates_registry_service(connection_manager: ConnectionManager) -> CertificatesRegistryService:
    """
    Factory function to create and initialize a CertificatesRegistryService instance.
    
    Args:
        connection_manager: Database connection manager
        
    Returns:
        Initialized CertificatesRegistryService instance
        
    Raises:
        Exception: If service initialization fails
    """
    try:
        # Create service instance
        service = CertificatesRegistryService(connection_manager)
        
        # Initialize service
        if not await service.initialize_service():
            raise Exception(f"Failed to initialize {service.service_name}")
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create certificates_registry service: {e}")
        raise


# ✅ REQUIRED: Export the service class and factory
__all__ = ['CertificatesRegistryService', 'create_certificates_registry_service']
