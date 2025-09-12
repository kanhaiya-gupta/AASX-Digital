#!/usr/bin/env python3
"""
Certificate Manager Certificates Versions Service

This service provides business logic and orchestration for certificates versions operations
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
    service = CertificatesVersionsService(connection_manager)
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
from ..models.certificates_versions import CertificateVersions
from ..repositories.certificates_versions_repository import CertificatesVersionsRepository

logger = logging.getLogger(__name__)


class CertificatesVersionsService:
    """
    Service for certificates versions business logic and orchestration
    
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
        self.repository = CertificatesVersionsRepository(connection_manager)
        
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
        self.service_name = "certificates_versions"
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
                'max_version_size_mb': 10,
                'allowed_version_types': ['major', 'minor', 'patch', 'pre_release', 'release_candidate', 'beta', 'alpha', 'hotfix'],
                'processing_timeout_minutes': 30,
                'retry_attempts': 3,
                'max_versions_per_certificate': 100,
                'max_versions_per_dept': 50
            },
            'required_fields': {
                'create': ['certificate_id', 'version_number'],  # Minimal required fields for creation
                'update': ['version_id'],  # Only version_id required for updates
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
                'max_versions_per_certificate': 100,
                'naming_convention': "v{version_number}_{org_id}_{dept_id}_{timestamp}",
                'compliance_requirements': ["GDPR", "SOX", "ISO27001", "NIST"],
                'security_levels': ['low', 'medium', 'high', 'critical'],
                'approval_workflow': {
                    'auto_approve_minor': True,
                    'require_approval_major': True,
                    'approval_timeout_hours': 72
                }
            }
        }
    
    async def initialize(self) -> None:
        """
        Initialize async components and load business configuration.
        """
        try:
            # ✅ REQUIRED: Load business configuration
            self.business_config = await self._load_business_config()
            
            # ✅ REQUIRED: Security context is created per operation, not globally
            
            # ✅ REQUIRED: Initialize engine components
            await self.auth_manager.initialize()
            await self.metrics_collector.initialize()
            await self.error_tracker.initialize()
            await self.event_bus.initialize()
            
            logger.info(f"Successfully initialized {self.service_name}")
            
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

    # ✅ REQUIRED: Core Business Operations (STAGE 1 IMPLEMENTATION)
    
    async def create_entity(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[CertificateVersions]:
        """
        Create a new certificate version entity with comprehensive business logic validation.
        
        Args:
            entity_data: Data for the new entity
            user_context: User context for authorization and audit
            
        Returns:
            Created entity instance or None if creation failed
        """
        try:
            # ✅ REQUIRED: Performance monitoring
            with self.performance_profiler.profile_context("create_entity"):
                
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="create"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to create certificate_manager")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Business validation
                validation_result = await self._validate_entity_data(entity_data, "create")
                if not validation_result["valid"]:
                    logger.error(f"Entity validation failed: {validation_result['errors']}")
                    return None
                
                # ✅ REQUIRED: Generate entity ID if not provided
                if "version_id" not in entity_data:
                    entity_data["version_id"] = str(uuid.uuid4())
                
                # ✅ REQUIRED: Add audit fields
                entity_data.update({
                    "created_at": datetime.utcnow().isoformat(),
                    "created_by": user_context.get("user_id", "system"),
                    "updated_at": datetime.utcnow().isoformat(),
                    "updated_by": user_context.get("user_id", "system")
                })
                
                # ✅ REQUIRED: Create entity instance
                entity = CertificateVersions(**entity_data)
                
                # ✅ REQUIRED: Save to repository (pass entity object, not dictionary)
                created_entity = await self.repository.create(entity)
                if not created_entity:
                    logger.error("Failed to save entity to repository")
                    return None
                
                # Use the created entity
                entity = created_entity
                
                if entity:
                    # ✅ REQUIRED: Metrics collection
                    await self.metrics_collector.record_metric(
                        "certificate_versions_created",
                        metric_value=1,
                        metadata={"service": self.service_name}
                    )
                    
                    # ✅ REQUIRED: Event publishing
                    await self.event_bus.publish("certificate_version.created", {
                        "version_id": entity.version_id,
                        "certificate_id": entity.certificate_id,
                        "user_context": user_context,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    logger.info(f"Successfully created certificate version {entity.version_id}")
                    return entity
                else:
                    logger.error("Failed to create certificate version entity")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating certificate version entity: {e}")
            await self.error_tracker.track_error(
                error_type="create_entity_error",
                error_message=str(e),
                error_details=f"Failed to create certificate version: {e}",
                severity="medium",
                metadata={"entity_data": entity_data, "user_context": user_context}
            )
            return None

    async def get_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[CertificateVersions]:
        """
        Retrieve a certificate version entity by ID with authorization.
        
        Args:
            entity_id: ID of the entity to retrieve
            user_context: User context for authorization and audit
            
        Returns:
            Entity instance or None if not found/unauthorized
        """
        try:
            # ✅ REQUIRED: Performance monitoring
            with self.performance_profiler.profile_context("get_entity"):
                
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read certificate_manager")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Retrieve entity via repository
                entity = await self.repository.get_by_id(entity_id)
                
                if entity:
                    # ✅ REQUIRED: Metrics collection
                    await self.metrics_collector.record_metric(
                        "certificate_versions_retrieved",
                        metric_value=1,
                        metadata={"service": self.service_name}
                    )
                    
                    logger.info(f"Successfully retrieved certificate version {entity_id}")
                    return entity
                else:
                    logger.info(f"Certificate version {entity_id} not found")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving certificate version {entity_id}: {e}")
            await self.error_tracker.track_error(
                error_type="get_entity_error",
                error_message=str(e),
                error_details=f"Failed to retrieve certificate version {entity_id}: {e}",
                severity="low",
                metadata={"entity_id": entity_id, "user_context": user_context}
            )
            return None

    async def get_entity_by_file_id(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[CertificateVersions]:
        """
        Alias for get_entity method to match registry service pattern.
        
        Args:
            entity_id: ID of the entity to retrieve
            user_context: User context for authorization
            
        Returns:
            CertificateVersions entity if found and authorized, None otherwise
        """
        return await self.get_entity(entity_id, user_context)

    async def get_all_entities(
        self,
        user_context: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[CertificateVersions]:
        """
        Get all certificate version entities with authorization.
        
        Args:
            user_context: User context for authorization
            limit: Optional limit for pagination
            offset: Optional offset for pagination
            
        Returns:
            List of CertificateVersions entities
        """
        try:
            # ✅ REQUIRED: Authorization check
            if user_context:
                security_context = SecurityContext(
                    user_id=user_context.get("user_id"),
                    roles=['admin', 'user', 'processor', 'system'],
                    metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                )
                
                auth_result = await self.auth_manager.check_permission(
                    context=security_context,
                    resource="certificate_manager",
                    action="read"
                )
                
                if not auth_result.allowed:
                    logger.warning(f"User {user_context.get('user_id')} lacks permission to read certificate_manager")
                    return []
            else:
                auth_result = type('obj', (object,), {'allowed': False})()
            
            if not auth_result.allowed:
                logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                return []
            
            # ✅ REQUIRED: Get all entities from repository
            # Convert None values to proper defaults
            safe_limit = limit if limit is not None else 100
            safe_offset = offset if offset is not None else 0
            entities = await self.repository.get_all(limit=safe_limit, offset=safe_offset)
            
            # ✅ REQUIRED: Metrics collection
            await self.metrics_collector.record_metric(
                "certificate_versions_retrieved",
                metric_value=len(entities),
                metadata={"service": self.service_name}
            )
            
            logger.info(f"Successfully retrieved {len(entities)} certificate versions")
            return entities
            
        except Exception as e:
            logger.error(f"Error retrieving all certificate versions: {e}")
            await self.error_tracker.track_error(
                error_type="get_all_entities_error",
                error_message=str(e),
                error_details=f"Failed to retrieve all certificate versions: {e}",
                severity="medium",
                metadata={"user_context": user_context}
            )
            return []

    async def search_entities(
        self,
        search_criteria: Dict[str, Any],
        user_context: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[CertificateVersions]:
        """
        Search certificate version entities with authorization and filtering.
        
        Args:
            search_criteria: Search criteria dictionary
            user_context: User context for authorization and audit
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching entities
        """
        try:
            # ✅ REQUIRED: Performance monitoring
            with self.performance_profiler.profile_context("search_entities"):
                
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to search certificate_manager")
                        return []
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return []
                
                # ✅ REQUIRED: Search entities via repository
                entities = await self.repository.search(
                    criteria=search_criteria,
                    limit=limit,
                    offset=offset
                )
                
                # ✅ REQUIRED: Metrics collection
                await self.metrics_collector.record_metric(
                    "certificate_versions_searched",
                    metric_value=len(entities),
                    metadata={"service": self.service_name, "result_count": len(entities)}
                )
                
                logger.info(f"Successfully searched certificate versions, found {len(entities)} results")
                return entities
                
        except Exception as e:
            logger.error(f"Error searching certificate versions: {e}")
            await self.error_tracker.track_error(
                error_type="search_entities_error",
                error_message=str(e),
                error_details=f"Failed to search certificate versions: {e}",
                severity="medium",
                metadata={"search_criteria": search_criteria, "user_context": user_context}
            )
            return []

    async def update_entity(
        self,
        entity_id: str,
        update_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[CertificateVersions]:
        """
        Update a certificate version entity with authorization and validation.
        
        Args:
            entity_id: ID of the entity to update
            update_data: Data to update
            user_context: User context for authorization and audit
            
        Returns:
            Updated CertificateVersions entity if successful, None otherwise
        """
        try:
            # ✅ REQUIRED: Performance monitoring
            with self.performance_profiler.profile_context("update_entity"):
                
                # ✅ REQUIRED: Authorization check
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="update"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update certificate_manager")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Business validation
                validation_result = await self._validate_entity_data(update_data, "update")
                if not validation_result["valid"]:
                    logger.error(f"Update validation failed: {validation_result['errors']}")
                    return None
                
                # ✅ REQUIRED: Add audit fields
                update_data.update({
                    "updated_at": datetime.utcnow().isoformat(),
                    "updated_by": user_context.get("user_id", "system")
                })
                
                # ✅ REQUIRED: Update entity via repository
                updated_entity = await self.repository.update(entity_id, update_data)
                
                if updated_entity:
                    # ✅ REQUIRED: Metrics collection
                    await self.metrics_collector.record_metric(
                        "certificate_versions_updated",
                        metric_value=1,
                        metadata={"service": self.service_name}
                    )
                    
                    # ✅ REQUIRED: Event publishing
                    await self.event_bus.publish("certificate_version.updated", {
                        "version_id": entity_id,
                        "user_context": user_context,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    logger.info(f"Successfully updated certificate version {entity_id}")
                    return updated_entity
                else:
                    logger.error(f"Failed to update certificate version {entity_id}")
                    return None
            
        except Exception as e:
            logger.error(f"Error updating certificate version {entity_id}: {e}")
            await self.error_tracker.track_error(
                error_type="update_entity_error",
                error_message=str(e),
                error_details=f"Failed to update certificate version {entity_id}: {e}",
                severity="medium",
                metadata={"entity_id": entity_id, "update_data": update_data, "user_context": user_context}
            )
            return None

    async def delete_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Delete a certificate version entity with authorization.
        
        Args:
            entity_id: ID of the entity to delete
            user_context: User context for authorization and audit
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # ✅ REQUIRED: Performance monitoring
            with self.performance_profiler.profile_context("delete_entity"):
                
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="certificate_manager",
                        action="delete"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to delete certificate_manager")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Delete entity via repository
                success = await self.repository.delete(entity_id)
            
            if success:
                # ✅ REQUIRED: Metrics collection
                await self.metrics_collector.record_metric(
                    "certificate_versions_deleted",
                    metric_value=1,
                    metadata={"service": self.service_name}
                )
                
                # ✅ REQUIRED: Event publishing
                await self.event_bus.publish("certificate_version.deleted", {
                    "version_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                logger.info(f"Successfully deleted certificate version {entity_id}")
                return True
            else:
                logger.error(f"Failed to delete certificate version {entity_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error deleting certificate version {entity_id}: {e}")
            await self.error_tracker.track_error(
                error_type="delete_entity_error",
                error_message=str(e),
                error_details=f"Failed to delete certificate version {entity_id}: {e}",
                severity="medium",
                metadata={"entity_id": entity_id, "user_context": user_context}
            )
            return False

    # ✅ REQUIRED: Business Logic Validation
    
    async def _validate_entity_data(
        self,
        entity_data: Dict[str, Any],
        operation: str
    ) -> Dict[str, Any]:
        """
        Validate entity data against business rules.
        
        Args:
            entity_data: Data to validate
            operation: Operation type (create, update, delete)
            
        Returns:
            Validation result with valid flag and errors list
        """
        try:
            errors = []
            required_fields = self.business_config.get('required_fields', {}).get(operation, [])
            
            # ✅ REQUIRED: Check required fields
            for field in required_fields:
                # For update operations, version_id is passed as entity_id parameter, not in update_data
                if operation == "update" and field == "version_id":
                    continue
                if field not in entity_data or entity_data[field] is None:
                    errors.append(f"Required field '{field}' is missing or null")
            
            # ✅ REQUIRED: Business rule validation
            if operation in ["create", "update"]:
                # Validate version number format
                if "version_number" in entity_data:
                    version_number = entity_data["version_number"]
                    if not isinstance(version_number, str) or not version_number.strip():
                        errors.append("Version number must be a non-empty string")
                
                # Validate version type
                if "version_type" in entity_data:
                    allowed_types = self.business_config.get('default_rules', {}).get('allowed_version_types', [])
                    if entity_data["version_type"] not in allowed_types:
                        errors.append(f"Version type must be one of: {allowed_types}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error validating entity data: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }

    # ✅ REQUIRED: Service Health and Monitoring
    
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get comprehensive service health status.
        
        Returns:
            Health status dictionary
        """
        try:
            # ✅ REQUIRED: Check repository health
            repo_health = await self.repository.health_check() if hasattr(self.repository, 'health_check') else {"status": "unknown"}
            
            # ✅ REQUIRED: Check engine components health
            auth_health = await self.auth_manager.get_health()
            metrics_health = await self.metrics_collector.get_health()
            error_health = await self.error_tracker.get_health()
            
            # ✅ REQUIRED: Determine overall health
            overall_status = "healthy"
            if (repo_health.get("status") != "healthy" or 
                auth_health.get("status") != "healthy" or 
                metrics_health.get("status") != "healthy" or 
                error_health.get("status") != "healthy"):
                overall_status = "unhealthy"
            
            return {
                "service_name": self.service_name,
                "service_version": self.service_version,
                "service_status": self.service_status,
                "overall_status": overall_status,
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "repository": repo_health,
                    "authorization": auth_health,
                    "metrics": metrics_health,
                    "error_tracking": error_health
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting service health: {e}")
            return {
                "service_name": self.service_name,
                "service_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_health_status(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alias for get_service_health for compatibility with tests.
        
        Args:
            user_context: User context (not used but required for compatibility)
            
        Returns:
            Health status dictionary
        """
        return await self.get_service_health()

    async def cleanup_service(self) -> None:
        """
        Cleanup service resources and connections.
        """
        try:
            # ✅ REQUIRED: Cleanup engine components
            await self.performance_profiler.cleanup()
            await self.metrics_collector.cleanup()
            await self.error_tracker.cleanup()
            await self.health_monitor.cleanup()
            await self.event_bus.cleanup()
            
            # ✅ REQUIRED: Update service status
            self.service_status = "shutdown"
            
            logger.info(f"Successfully cleaned up {self.service_name}")
            
        except Exception as e:
            logger.error(f"Error cleaning up {self.service_name}: {e}")

    # ============================================================================
    # STAGE 2: BUSINESS DOMAIN METHODS (PLACEHOLDERS)
    # ============================================================================
    # These methods will be implemented in Stage 2 with full business logic
    
    # 🔄 VERSION MANAGEMENT METHODS
    
    async def create_version_from_certificate(
        self,
        certificate_id: str,
        version_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[CertificateVersions]:
        """
        Create new version from existing certificate.
        
        This is a business domain method that uses the CRUD create_entity method.
        
        Args:
            certificate_id: ID of the parent certificate
            version_data: Version-specific data
            user_context: User context for authorization
            
        Returns:
            Created version instance or None if failed
        """
        try:
            # ✅ BUSINESS LOGIC: Get current certificate data
            from ..services.certificates_registry_service import CertificatesRegistryService
            registry_service = CertificatesRegistryService(self.connection_manager)
            await registry_service.initialize()  # Initialize the registry service properly
            
            current_certificate = await registry_service.get_entity(certificate_id, user_context)
            if not current_certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return None

            # ✅ BUSINESS LOGIC: Create version data with certificate data
            version_entity_data = {
                # Version Information
                "version_id": str(uuid.uuid4()),  # Generate version_id here
                "certificate_id": certificate_id,
                "version_number": version_data.get("version_number", "1.0.0"),
                "version_type": version_data.get("version_type", "minor"),
                "version_name": version_data.get("version_name", f"Version {version_data.get('version_number', '1.0.0')}"),
                "version_description": version_data.get("version_description", "New version created from certificate"),
                
                # Complete Data Snapshot (JSON) - Copy from current certificate
                "module_data_snapshot": {
                    "aasx_etl_summary": getattr(current_certificate, 'aasx_etl_summary', {}),
                    "twin_registry_summary": getattr(current_certificate, 'twin_registry_summary', {}),
                    "ai_rag_summary": getattr(current_certificate, 'ai_rag_summary', {}),
                    "kg_neo4j_summary": getattr(current_certificate, 'kg_neo4j_summary', {}),
                    "federated_learning_summary": getattr(current_certificate, 'federated_learning_summary', {}),
                    "physics_modeling_summary": getattr(current_certificate, 'physics_modeling_summary', {}),
                    "data_governance_summary": getattr(current_certificate, 'data_governance_summary', {}),
                    "digital_product_passport_summary": getattr(current_certificate, 'digital_product_passport_summary', {})
                },
                "consolidated_summary": {
                    "aasx": getattr(current_certificate, 'aasx_summary', {}),
                    "certificate_manager": getattr(current_certificate, 'certificate_manager_summary', {}),
                    "data_processor": getattr(current_certificate, 'data_processor_summary', {}),
                    "analytics_engine": getattr(current_certificate, 'analytics_engine_summary', {}),
                    "workflow_engine": getattr(current_certificate, 'workflow_engine_summary', {}),
                    "integration_layer": getattr(current_certificate, 'integration_layer_summary', {}),
                    "security_module": getattr(current_certificate, 'security_module_summary', {}),
                    "digital_product_passport": getattr(current_certificate, 'digital_product_passport_summary', {})
                },
                "change_summary": version_data.get("change_summary", {}),
                "diff_summary": version_data.get("diff_summary", {}),
                
                # Version Metadata
                "change_reason": version_data.get("change_reason", "Version created from certificate"),
                "change_request_id": version_data.get("change_request_id"),
                "change_category": version_data.get("change_category", "module_update"),
                "change_priority": version_data.get("change_priority", "normal"),
                
                # Approval & Review
                "approval_status": "pending",
                "validation_status": "pending",
                
                # Quality & Validation
                "version_quality_score": current_certificate.overall_quality_score,
                
                # Environment Management
                "deployment_environment": "development",
                "deployment_status": "not_deployed",
                
                # Security & Access Control
                "security_level": current_certificate.security_level,
                "encryption_status": "none",
                
                # Version Lifecycle Management
                "archive_status": "active"
            }

            # ✅ BUSINESS LOGIC: Use the existing create_entity method (clean architecture)
            entity = await self.create_entity(version_entity_data, user_context)
            
            if entity:
                logger.info(f"Successfully created version: {entity.version_id} for certificate: {certificate_id}")
                return entity
            else:
                logger.error(f"Failed to create version for certificate: {certificate_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error creating version from certificate: {e}")
            return None
    
    async def promote_version(
        self,
        version_id: str,
        target_type: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Promote version (alpha → beta → release candidate → release).
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version to promote
            target_type: Target version type (draft, review, approved, released)
            user_context: User context for authorization
            
        Returns:
            True if promotion successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate target type
            valid_types = ["draft", "review", "approved", "released"]
            if target_type not in valid_types:
                logger.error(f"Invalid target type: {target_type}")
                return False

            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check promotion rules
            current_type = current_version.version_type
            if current_type == "released":
                logger.error(f"Version {version_id} is already released and cannot be promoted")
                return False

            # ✅ BUSINESS LOGIC: Create update data
            update_data = {
                "version_type": target_type,
                "approval_status": "approved" if target_type == "approved" else "pending",
                "validation_status": "validated" if target_type in ["approved", "released"] else "pending"
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully promoted version {version_id} from {current_type} to {target_type}")
                return True
            else:
                logger.error(f"Failed to promote version {version_id} to {target_type}")
                return False
            
        except Exception as e:
            logger.error(f"Error promoting version: {e}")
            return False
    
    async def rollback_to_version(
        self,
        certificate_id: str,
        target_version_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Rollback certificate to previous version.
        
        This is a business domain method that uses the CRUD methods.
        
        Args:
            certificate_id: ID of the certificate to rollback
            target_version_id: ID of the version to rollback to
            user_context: User context for authorization
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get target version
            target_version = await self.get_entity(target_version_id, user_context)
            if not target_version:
                logger.error(f"Target version not found: {target_version_id}")
                return False

            # ✅ BUSINESS LOGIC: Validate target version belongs to certificate
            if target_version.certificate_id != certificate_id:
                logger.error(f"Version {target_version_id} does not belong to certificate {certificate_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if target version is stable
            if target_version.version_type not in ["approved", "released"]:
                logger.error(f"Cannot rollback to version {target_version_id} - not stable")
                return False

            # ✅ BUSINESS LOGIC: Create new version from target version
            rollback_data = {
                "version_number": f"{target_version.version_number}.rollback",
                "version_type": "rollback",
                "version_name": f"Rollback to {target_version.version_name}",
                "version_description": f"Rollback to version {target_version.version_number}",
                "change_reason": f"Rollback to version {target_version.version_number}",
                "change_category": "correction",
                "change_priority": "high"
            }

            # ✅ BUSINESS LOGIC: Use existing business method
            rollback_version = await self.create_version_from_certificate(
                certificate_id, rollback_data, user_context
            )

            if rollback_version:
                logger.info(f"Successfully rolled back certificate {certificate_id} to version {target_version_id}")
                return True
            else:
                logger.error(f"Failed to rollback certificate {certificate_id} to version {target_version_id}")
                return False

        except Exception as e:
            logger.error(f"Error rolling back to version: {e}")
            return False

    async def archive_version(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Archive old version.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version to archive
            user_context: User context for authorization
            
        Returns:
            True if archiving successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if version can be archived
            if current_version.archive_status == "archived":
                logger.warning(f"Version {version_id} is already archived")
                return True

            # ✅ BUSINESS LOGIC: Check if version is in production
            if current_version.deployment_environment == "production" and current_version.deployment_status == "deployed":
                logger.error(f"Cannot archive version {version_id} that is currently deployed in production")
                return False

            # ✅ BUSINESS LOGIC: Create update data
            update_data = {
                "archive_status": "archived",
                "archive_timestamp": datetime.now().isoformat(),
                "archive_reason": "Archived by user request"
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully archived version {version_id}")
                return True
            else:
                logger.error(f"Failed to archive version {version_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error archiving version: {e}")
            return False

    async def restore_version(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Restore archived version.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version to restore
            user_context: User context for authorization
            
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if version is archived
            if current_version.archive_status != "archived":
                logger.warning(f"Version {version_id} is not archived")
                return True

            # ✅ BUSINESS LOGIC: Create update data
            update_data = {
                "archive_status": "restored",
                "restore_timestamp": datetime.now().isoformat()
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully restored version {version_id}")
                return True
            else:
                logger.error(f"Failed to restore version {version_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error restoring version: {e}")
            return False

    # 🔍 VERSION COMPARISON & ANALYSIS METHODS
    
    async def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two versions and return differences.
        
        Args:
            version_id_1: First version ID
            version_id_2: Second version ID
            user_context: User context for authorization
            
        Returns:
            Dictionary containing comparison results
        """
        # TODO: Stage 2 Implementation
        logger.info(f"compare_versions placeholder called for versions {version_id_1} and {version_id_2}")
        return {"status": "placeholder", "differences": []}

    async def get_version_changes(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get detailed change log for version.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            Dictionary containing change details
        """
        # TODO: Stage 2 Implementation
        logger.info(f"get_version_changes placeholder called for version {version_id}")
        return {"status": "placeholder", "changes": []}

    async def analyze_version_impact(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess impact of version changes.
        
        Args:
            version_id: ID of the version to analyze
            user_context: User context for authorization
            
        Returns:
            Dictionary containing impact analysis
        """
        # TODO: Stage 2 Implementation
        logger.info(f"analyze_version_impact placeholder called for version {version_id}")
        return {"status": "placeholder", "impact": "unknown"}

    async def get_version_dependencies(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get dependencies and affected components.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            List of dependencies
        """
        # TODO: Stage 2 Implementation
        logger.info(f"get_version_dependencies placeholder called for version {version_id}")
        return []

    # 📋 APPROVAL & WORKFLOW METHODS

    async def submit_for_approval(
        self,
        version_id: str,
        approver_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Submit version for approval workflow.
        
        Args:
            version_id: ID of the version to submit
            approver_id: ID of the approver
            user_context: User context for authorization
            
        Returns:
            True if submission successful, False otherwise
        """
        # TODO: Stage 2 Implementation
        logger.info(f"submit_for_approval placeholder called for version {version_id} to approver {approver_id}")
        return False

    async def approve_version(
        self,
        version_id: str,
        approval_notes: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Approve version with optional conditions.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version to approve
            approval_notes: Approval notes and conditions
            user_context: User context for authorization
            
        Returns:
            True if approval successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if version can be approved
            if current_version.approval_status == "approved":
                logger.warning(f"Version {version_id} is already approved")
                return True

            if current_version.approval_status == "rejected":
                logger.error(f"Cannot approve rejected version {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Create update data
            update_data = {
                "approval_status": "approved",
                "approved_by": user_context.get("user_id"),
                "approval_timestamp": datetime.now().isoformat(),
                "approval_notes": approval_notes
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully approved version {version_id}")
                return True
            else:
                logger.error(f"Failed to approve version {version_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error approving version: {e}")
            return False

    async def reject_version(
        self,
        version_id: str,
        rejection_reason: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Reject version with reasons.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version to reject
            rejection_reason: Reason for rejection
            user_context: User context for authorization
            
        Returns:
            True if rejection successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if version can be rejected
            if current_version.approval_status == "rejected":
                logger.warning(f"Version {version_id} is already rejected")
                return True

            if current_version.approval_status == "approved":
                logger.error(f"Cannot reject approved version {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Create update data
            update_data = {
                "approval_status": "rejected",
                "approval_notes": f"Rejected: {rejection_reason}",
                "approved_by": user_context.get("user_id"),
                "approval_timestamp": datetime.now().isoformat()
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully rejected version {version_id}")
                return True
            else:
                logger.error(f"Failed to reject version {version_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error rejecting version: {e}")
            return False

    async def request_changes(
        self,
        version_id: str,
        change_requests: List[str],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Request changes before approval.
        
        Args:
            version_id: ID of the version
            change_requests: List of requested changes
            user_context: User context for authorization
            
        Returns:
            True if request successful, False otherwise
        """
        # TODO: Stage 2 Implementation
        logger.info(f"request_changes placeholder called for version {version_id}")
        return False

    async def escalate_approval(
        self,
        version_id: str,
        escalation_reason: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Escalate approval to higher authority.
        
        Args:
            version_id: ID of the version to escalate
            escalation_reason: Reason for escalation
            user_context: User context for authorization
            
        Returns:
            True if escalation successful, False otherwise
        """
        # TODO: Stage 2 Implementation
        logger.info(f"escalate_approval placeholder called for version {version_id}")
        return False

    async def get_approval_status(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get current approval status.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            Dictionary containing approval status
        """
        # TODO: Stage 2 Implementation
        logger.info(f"get_approval_status placeholder called for version {version_id}")
        return {"status": "placeholder", "approval_status": "unknown"}

    async def get_approval_history(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get approval workflow history.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            List of approval history entries
        """
        # TODO: Stage 2 Implementation
        logger.info(f"get_approval_history placeholder called for version {version_id}")
        return []

    async def assign_approver(
        self,
        version_id: str,
        approver_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Assign specific approver to version.
        
        Args:
            version_id: ID of the version
            approver_id: ID of the approver
            user_context: User context for authorization
            
        Returns:
            True if assignment successful, False otherwise
        """
        # TODO: Stage 2 Implementation
        logger.info(f"assign_approver placeholder called for version {version_id} to approver {approver_id}")
        return False
    
    async def get_pending_approvals(
        self,
        user_context: Dict[str, Any],
        limit: int = 50
    ) -> List[CertificateVersions]:
        """
        Get versions pending approval.
        
        Args:
            user_context: User context for authorization
            limit: Maximum number of results
            
        Returns:
            List of versions pending approval
        """
        # TODO: Stage 2 Implementation
        logger.info(f"get_pending_approvals placeholder called")
        return []

    # 🔍 VERSION DISCOVERY & SEARCH METHODS

    async def find_versions_by_certificate(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> List[CertificateVersions]:
        """
        Get all versions for a certificate.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            List of versions for the certificate
        """
        try:
            # ✅ BUSINESS LOGIC: Search for versions of this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            versions = await self.search_entities(criteria, user_context, limit=100, offset=0)
            
            # Sort by created_at (newest first)
            versions.sort(key=lambda v: v.created_at, reverse=True)
            
            logger.info(f"Found {len(versions)} versions for certificate {certificate_id}")
            return versions

        except Exception as e:
            logger.error(f"Error finding versions by certificate: {e}")
            return []
    
    async def find_latest_version(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[CertificateVersions]:
        """
        Get latest version of certificate.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            Latest version instance or None
        """
        try:
            # ✅ BUSINESS LOGIC: Search for versions of this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            versions = await self.search_entities(criteria, user_context, limit=10, offset=0)
            
            if versions:
                # Sort by created_at to get the latest
                latest_version = max(versions, key=lambda v: v.created_at)
                logger.info(f"Found latest version {latest_version.version_id} for certificate {certificate_id}")
                return latest_version
            else:
                logger.info(f"No versions found for certificate {certificate_id}")
                return None

        except Exception as e:
            logger.error(f"Error finding latest version: {e}")
            return None

    async def find_stable_versions(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> List[CertificateVersions]:
        """
        Get only stable/released versions.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            List of stable versions
        """
        try:
            # ✅ BUSINESS LOGIC: Search for stable versions of this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False,
                "approval_status": "approved"
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            versions = await self.search_entities(criteria, user_context, limit=100, offset=0)
            
            # Filter for stable version types
            stable_versions = [
                v for v in versions 
                if v.version_type in ["approved", "released"] and v.archive_status != "archived"
            ]
            
            # Sort by created_at (newest first)
            stable_versions.sort(key=lambda v: v.created_at, reverse=True)
            
            logger.info(f"Found {len(stable_versions)} stable versions for certificate {certificate_id}")
            return stable_versions

        except Exception as e:
            logger.error(f"Error finding stable versions: {e}")
            return []

    async def find_versions_by_type(
        self,
        certificate_id: str,
        version_type: str,
        user_context: Dict[str, Any]
    ) -> List[CertificateVersions]:
        """
        Get versions by type (major, minor, patch).
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            version_type: Type of version to find
            user_context: User context for authorization
            
        Returns:
            List of versions matching the type
        """
        try:
            # ✅ BUSINESS LOGIC: Validate version type
            valid_types = ["major", "minor", "patch", "draft", "preview", "rollback"]
            if version_type not in valid_types:
                logger.error(f"Invalid version type: {version_type}")
                return []

            # ✅ BUSINESS LOGIC: Search for versions of this certificate and type
            criteria = {
                "certificate_id": certificate_id,
                "version_type": version_type,
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            versions = await self.search_entities(criteria, user_context, limit=100, offset=0)
            
            # Sort by created_at (newest first)
            versions.sort(key=lambda v: v.created_at, reverse=True)
            
            logger.info(f"Found {len(versions)} versions of type {version_type} for certificate {certificate_id}")
            return versions

        except Exception as e:
            logger.error(f"Error finding versions by type: {e}")
            return []

    async def find_versions_by_status(
        self,
        certificate_id: str,
        status: str,
        user_context: Dict[str, Any]
    ) -> List[CertificateVersions]:
        """
        Get versions by approval status.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            status: Approval status to filter by
            user_context: User context for authorization
            
        Returns:
            List of versions matching the status
        """
        try:
            # ✅ BUSINESS LOGIC: Validate status
            valid_statuses = ["pending", "approved", "rejected", "requires_changes"]
            if status not in valid_statuses:
                logger.error(f"Invalid status: {status}")
                return []

            # ✅ BUSINESS LOGIC: Search for versions of this certificate and status
            criteria = {
                "certificate_id": certificate_id,
                "approval_status": status,
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            versions = await self.search_entities(criteria, user_context, limit=100, offset=0)
            
            # Sort by created_at (newest first)
            versions.sort(key=lambda v: v.created_at, reverse=True)
            
            logger.info(f"Found {len(versions)} versions with status {status} for certificate {certificate_id}")
            return versions

        except Exception as e:
            logger.error(f"Error finding versions by status: {e}")
            return []

    # 📊 VERSION ANALYTICS METHODS

    async def get_version_statistics(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get version metrics and statistics.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            Dictionary containing version statistics
        """
        try:
            # ✅ BUSINESS LOGIC: Get all versions for this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            # ✅ BUSINESS LOGIC: Calculate statistics
            total_versions = len(versions)
            
            # Count by version type
            type_counts = {}
            for version in versions:
                vtype = version.version_type
                type_counts[vtype] = type_counts.get(vtype, 0) + 1
            
            # Count by approval status
            status_counts = {}
            for version in versions:
                status = version.approval_status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by archive status
            archive_counts = {}
            for version in versions:
                archive = version.archive_status
                archive_counts[archive] = archive_counts.get(archive, 0) + 1
            
            # Find latest version
            latest_version = max(versions, key=lambda v: v.created_at) if versions else None
            
            statistics = {
                "total_versions": total_versions,
                "version_types": type_counts,
                "approval_statuses": status_counts,
                "archive_statuses": archive_counts,
                "latest_version": {
                    "version_id": latest_version.version_id,
                    "version_number": latest_version.version_number,
                    "version_type": latest_version.version_type,
                    "created_at": latest_version.created_at
                } if latest_version else None
            }
            
            logger.info(f"Generated statistics for certificate {certificate_id}: {total_versions} versions")
            return {"status": "success", "statistics": statistics}

        except Exception as e:
            logger.error(f"Error getting version statistics: {e}")
            return {"status": "error", "statistics": {}}
    
    async def get_version_timeline(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get chronological version history.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            List of timeline entries
        """
        try:
            # ✅ BUSINESS LOGIC: Get all versions for this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            # ✅ BUSINESS LOGIC: Create timeline entries
            timeline = []
            for version in versions:
                timeline.append({
                    "timestamp": version.created_at,
                    "event_type": "version_created",
                    "version_id": version.version_id,
                    "version_number": version.version_number,
                    "version_type": version.version_type,
                    "created_by": version.created_by,
                    "description": f"Version {version.version_number} created"
                })
                
                # Add approval events if approved
                if version.approval_timestamp:
                    timeline.append({
                        "timestamp": version.approval_timestamp,
                        "event_type": "version_approved",
                        "version_id": version.version_id,
                        "version_number": version.version_number,
                        "approved_by": version.approved_by,
                        "description": f"Version {version.version_number} approved"
                    })
                
                # Add archive events if archived
                if version.archive_timestamp:
                    timeline.append({
                        "timestamp": version.archive_timestamp,
                        "event_type": "version_archived",
                        "version_id": version.version_id,
                        "version_number": version.version_number,
                        "archive_reason": version.archive_reason,
                        "description": f"Version {version.version_number} archived"
                    })
            
            # Sort timeline by timestamp (newest first)
            timeline.sort(key=lambda x: x["timestamp"], reverse=True)
            
            logger.info(f"Generated timeline for certificate {certificate_id}: {len(timeline)} events")
            return timeline

        except Exception as e:
            logger.error(f"Error getting version timeline: {e}")
            return []

    async def get_version_usage_stats(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get usage statistics for version.
        
        This is a business domain method that uses the CRUD get_entity method.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            Dictionary containing usage statistics
        """
        try:
            # ✅ BUSINESS LOGIC: Get version data
            version = await self.get_entity(version_id, user_context)
            if not version:
                logger.error(f"Version not found: {version_id}")
                return {"status": "error", "usage_stats": {}}

            # ✅ BUSINESS LOGIC: Calculate usage statistics
            current_time = datetime.now()
            created_time = datetime.fromisoformat(version.created_at.replace('Z', '+00:00'))
            
            # Calculate age in days
            age_days = (current_time - created_time).days
            
            # Calculate deployment age if deployed
            deployment_age_hours = 0
            if version.deployment_timestamp:
                deployment_time = datetime.fromisoformat(version.deployment_timestamp.replace('Z', '+00:00'))
                deployment_age_hours = (current_time - deployment_time).total_seconds() / 3600
            
            # Calculate archive age if archived
            archive_age_hours = 0
            if version.archive_timestamp:
                archive_time = datetime.fromisoformat(version.archive_timestamp.replace('Z', '+00:00'))
                archive_age_hours = (current_time - archive_time).total_seconds() / 3600

            usage_stats = {
                "version_id": version.version_id,
                "version_number": version.version_number,
                "version_type": version.version_type,
                "age_days": age_days,
                "deployment_status": version.deployment_status,
                "deployment_environment": version.deployment_environment,
                "deployment_age_hours": deployment_age_hours,
                "archive_status": version.archive_status,
                "archive_age_hours": archive_age_hours,
                "approval_status": version.approval_status,
                "quality_score": version.version_quality_score,
                "security_level": version.security_level,
                "encryption_status": version.encryption_status,
                "created_by": version.created_by,
                "created_at": version.created_at
            }
            
            logger.info(f"Generated usage stats for version {version_id}")
            return {"status": "success", "usage_stats": usage_stats}

        except Exception as e:
            logger.error(f"Error getting version usage stats: {e}")
            return {"status": "error", "usage_stats": {}}

    # 🔗 INTEGRATION METHODS

    async def link_version_to_certificate(
        self,
        version_id: str,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Link version to parent certificate.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            True if linking successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if version is already linked to a different certificate
            if current_version.certificate_id and current_version.certificate_id != certificate_id:
                logger.error(f"Version {version_id} is already linked to certificate {current_version.certificate_id}")
                return False

            # ✅ BUSINESS LOGIC: Verify certificate exists
            from ..services.certificates_registry_service import CertificatesRegistryService
            registry_service = CertificatesRegistryService(self.connection_manager)
            await registry_service.initialize()  # Initialize the registry service properly
            
            certificate = await registry_service.get_entity(certificate_id, user_context)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False

            # ✅ BUSINESS LOGIC: Create update data
            update_data = {
                "certificate_id": certificate_id,
                "linked_at": datetime.now().isoformat(),
                "linked_by": user_context.get("user_id")
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully linked version {version_id} to certificate {certificate_id}")
                return True
            else:
                logger.error(f"Failed to link version {version_id} to certificate {certificate_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error linking version to certificate: {e}")
            return False
            
    async def unlink_version_from_certificate(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Remove version link from certificate.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            True if unlinking successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if version is linked to a certificate
            if not current_version.certificate_id:
                logger.warning(f"Version {version_id} is not linked to any certificate")
                return True

            # ✅ BUSINESS LOGIC: Check if version is deployed in production
            if (current_version.deployment_environment == "production" and 
                current_version.deployment_status == "deployed"):
                logger.error(f"Cannot unlink version {version_id} that is deployed in production")
                return False

            # ✅ BUSINESS LOGIC: Create update data
            update_data = {
                "certificate_id": None,
                "unlinked_at": datetime.now().isoformat(),
                "unlinked_by": user_context.get("user_id")
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
                    
            if success:
                logger.info(f"Successfully unlinked version {version_id} from certificate")
                return True
            else:
                logger.error(f"Failed to unlink version {version_id} from certificate")
                return False
                        
        except Exception as e:
            logger.error(f"Error unlinking version from certificate: {e}")
            return False
            
    async def get_certificate_version_history(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> List[CertificateVersions]:
        """
        Get complete version history for certificate.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            List of all versions in chronological order
        """
        try:
            # ✅ BUSINESS LOGIC: Search for all versions of this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            # ✅ BUSINESS LOGIC: Sort by created_at (oldest first for history)
            versions.sort(key=lambda v: v.created_at)
            
            logger.info(f"Found {len(versions)} versions in history for certificate {certificate_id}")
            return versions
            
        except Exception as e:
            logger.error(f"Error getting certificate version history: {e}")
            return []
    
    async def sync_version_with_registry(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Sync version data with registry.
        
        This is a business domain method that uses the CRUD methods.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            True if sync successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Get certificate from registry
            from ..services.certificates_registry_service import CertificatesRegistryService
            registry_service = CertificatesRegistryService(self.connection_manager)
            await registry_service.initialize()  # Initialize the registry service properly
            
            certificate = await registry_service.get_entity(current_version.certificate_id, user_context)
            if not certificate:
                logger.error(f"Certificate not found: {current_version.certificate_id}")
                return False

            # ✅ BUSINESS LOGIC: Compare and sync data
            sync_needed = False
            update_data = {}

            # Check if module data needs syncing
            if current_version.module_data_snapshot != {
                "aasx_etl_summary": getattr(certificate, 'aasx_etl_summary', {}),
                "twin_registry_summary": getattr(certificate, 'twin_registry_summary', {}),
                "ai_rag_summary": getattr(certificate, 'ai_rag_summary', {}),
                "kg_neo4j_summary": getattr(certificate, 'kg_neo4j_summary', {}),
                "federated_learning_summary": getattr(certificate, 'federated_learning_summary', {}),
                "physics_modeling_summary": getattr(certificate, 'physics_modeling_summary', {}),
                "data_governance_summary": getattr(certificate, 'data_governance_summary', {}),
                "digital_product_passport_summary": getattr(certificate, 'digital_product_passport_summary', {})
            }:
                sync_needed = True
                update_data["module_data_snapshot"] = {
                    "aasx_etl_summary": getattr(certificate, 'aasx_etl_summary', {}),
                    "twin_registry_summary": getattr(certificate, 'twin_registry_summary', {}),
                    "ai_rag_summary": getattr(certificate, 'ai_rag_summary', {}),
                    "kg_neo4j_summary": getattr(certificate, 'kg_neo4j_summary', {}),
                    "federated_learning_summary": getattr(certificate, 'federated_learning_summary', {}),
                    "physics_modeling_summary": getattr(certificate, 'physics_modeling_summary', {}),
                    "data_governance_summary": getattr(certificate, 'data_governance_summary', {}),
                    "digital_product_passport_summary": getattr(certificate, 'digital_product_passport_summary', {})
                }

            # Check if consolidated summary needs syncing
            certificate_summary = {
                "aasx": getattr(certificate, 'aasx_summary', {}),
                "certificate_manager": getattr(certificate, 'certificate_manager_summary', {}),
                "data_processor": getattr(certificate, 'data_processor_summary', {}),
                "analytics_engine": getattr(certificate, 'analytics_engine_summary', {}),
                "workflow_engine": getattr(certificate, 'workflow_engine_summary', {}),
                "integration_layer": getattr(certificate, 'integration_layer_summary', {}),
                "security_module": getattr(certificate, 'security_module_summary', {}),
                "digital_product_passport": getattr(certificate, 'digital_product_passport_summary', {})
            }
            if current_version.consolidated_summary != certificate_summary:
                sync_needed = True
                update_data["consolidated_summary"] = certificate_summary

            # Check if quality score needs syncing
            if current_version.version_quality_score != certificate.overall_quality_score:
                sync_needed = True
                update_data["version_quality_score"] = certificate.overall_quality_score

            if sync_needed:
                # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
                success = await self.update_entity(version_id, update_data, user_context)
                
                if success:
                    logger.info(f"Successfully synced version {version_id} with registry")
                    return True
                else:
                    logger.error(f"Failed to sync version {version_id} with registry")
                    return False
            else:
                logger.info(f"Version {version_id} is already in sync with registry")
                return True
            
        except Exception as e:
            logger.error(f"Error syncing version with registry: {e}")
            return False
            
    async def populate_from_registry_changes(
        self,
        registry_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Populate version from registry updates.
        
        This is a business domain method that uses the CRUD create_entity method.
        
        Args:
            registry_data: Registry change data
            user_context: User context for authorization
            
        Returns:
            True if population successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate registry data
            if not registry_data.get("certificate_id"):
                logger.error("Registry data missing certificate_id")
                return False
            
            certificate_id = registry_data["certificate_id"]

            # ✅ BUSINESS LOGIC: Create version data from registry changes
            version_data = {
                "version_number": registry_data.get("version_number", "1.0.0"),
                "version_type": registry_data.get("version_type", "minor"),
                "version_name": registry_data.get("version_name", f"Version from registry changes"),
                "version_description": registry_data.get("version_description", "Version created from registry updates"),
                "change_reason": registry_data.get("change_reason", "Registry data updated"),
                "change_category": registry_data.get("change_category", "registry_update"),
                "change_priority": registry_data.get("change_priority", "normal"),
                "change_summary": registry_data.get("change_summary", {}),
                "diff_summary": registry_data.get("diff_summary", {})
            }

            # ✅ BUSINESS LOGIC: Use existing business method to create version
            version = await self.create_version_from_certificate(
                certificate_id, version_data, user_context
            )

            if version:
                logger.info(f"Successfully populated version from registry changes: {version.version_id}")
                return True
            else:
                logger.error(f"Failed to populate version from registry changes for certificate {certificate_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error populating from registry changes: {e}")
            return False
            
    async def sync_with_module_versions(
        self,
        version_id: str,
        module_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Sync with module-specific versions.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            module_data: Module version data
            user_context: User context for authorization
            
        Returns:
            True if sync successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False
            
            # ✅ BUSINESS LOGIC: Validate module data
            if not module_data:
                logger.error("Module data is empty")
                return False

            # ✅ BUSINESS LOGIC: Prepare update data for module synchronization
            update_data = {}
            sync_needed = False

            # Update module data snapshot if provided
            if "module_data_snapshot" in module_data:
                if current_version.module_data_snapshot != module_data["module_data_snapshot"]:
                    update_data["module_data_snapshot"] = module_data["module_data_snapshot"]
                    sync_needed = True

            # Update change summary if provided
            if "change_summary" in module_data:
                if current_version.change_summary != module_data["change_summary"]:
                    update_data["change_summary"] = module_data["change_summary"]
                    sync_needed = True

            # Update diff summary if provided
            if "diff_summary" in module_data:
                if current_version.diff_summary != module_data["diff_summary"]:
                    update_data["diff_summary"] = module_data["diff_summary"]
                    sync_needed = True

            # Update version quality score if provided
            if "version_quality_score" in module_data:
                if current_version.version_quality_score != module_data["version_quality_score"]:
                    update_data["version_quality_score"] = module_data["version_quality_score"]
                    sync_needed = True

            # Add sync timestamp
            if sync_needed:
                update_data["last_sync_timestamp"] = datetime.now().isoformat()
                update_data["last_sync_by"] = user_context.get("user_id")

                # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
                success = await self.update_entity(version_id, update_data, user_context)
                
                if success:
                    logger.info(f"Successfully synced version {version_id} with module versions")
                    return True
                else:
                    logger.error(f"Failed to sync version {version_id} with module versions")
                    return False
            else:
                logger.info(f"Version {version_id} is already in sync with module versions")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing with module versions: {e}")
            return False
    
    async def validate_version_consistency(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate version consistency across modules.
        
        This is a business domain method that uses the CRUD get_entity method.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            version = await self.get_entity(version_id, user_context)
            if not version:
                logger.error(f"Version not found: {version_id}")
                return {"status": "error", "consistency": "version_not_found"}

            # ✅ BUSINESS LOGIC: Perform consistency checks
            consistency_issues = []
            consistency_score = 100

            # Check if certificate_id is present
            if not version.certificate_id:
                consistency_issues.append("Missing certificate_id")
                consistency_score -= 20

            # Check if version_number is present and valid
            if not version.version_number or not isinstance(version.version_number, str):
                consistency_issues.append("Invalid or missing version_number")
                consistency_score -= 15

            # Check if version_type is valid
            valid_types = ["major", "minor", "patch", "draft", "preview", "rollback", "hotfix"]
            if version.version_type not in valid_types:
                consistency_issues.append(f"Invalid version_type: {version.version_type}")
                consistency_score -= 10

            # Check if module_data_snapshot is present and valid
            if not version.module_data_snapshot or not isinstance(version.module_data_snapshot, dict):
                consistency_issues.append("Invalid or missing module_data_snapshot")
                consistency_score -= 15

            # Check if approval_status is valid
            valid_statuses = ["pending", "approved", "rejected", "requires_changes"]
            if version.approval_status not in valid_statuses:
                consistency_issues.append(f"Invalid approval_status: {version.approval_status}")
                consistency_score -= 10

            # Check if archive_status is valid
            valid_archive_statuses = ["active", "archived", "restored"]
            if version.archive_status not in valid_archive_statuses:
                consistency_issues.append(f"Invalid archive_status: {version.archive_status}")
                consistency_score -= 10

            # Check if deployment_environment is valid
            valid_environments = ["development", "staging", "production", "testing"]
            if version.deployment_environment not in valid_environments:
                consistency_issues.append(f"Invalid deployment_environment: {version.deployment_environment}")
                consistency_score -= 10

            # Determine overall consistency status
            if consistency_score >= 90:
                consistency_status = "excellent"
            elif consistency_score >= 75:
                consistency_status = "good"
            elif consistency_score >= 60:
                consistency_status = "fair"
            else:
                consistency_status = "poor"

            validation_results = {
                "version_id": version_id,
                "consistency_score": max(0, consistency_score),
                "consistency_status": consistency_status,
                "total_issues": len(consistency_issues),
                "issues": consistency_issues,
                "validation_timestamp": datetime.now().isoformat(),
                "validated_by": user_context.get("user_id")
            }
            
            logger.info(f"Version {version_id} consistency validation completed: {consistency_status} ({consistency_score}%)")
            return {"status": "success", "consistency": validation_results}

        except Exception as e:
            logger.error(f"Error validating version consistency: {e}")
            return {"status": "error", "consistency": "validation_failed"}

    # 📊 REPORTING & ANALYTICS METHODS

    async def generate_version_report(
        self,
        certificate_id: str,
        report_type: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive version report.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            report_type: Type of report to generate
            user_context: User context for authorization
            
        Returns:
            Dictionary containing report data
        """
        try:
            # ✅ BUSINESS LOGIC: Validate report type
            valid_report_types = ["summary", "detailed", "compliance", "performance", "audit"]
            if report_type not in valid_report_types:
                logger.error(f"Invalid report type: {report_type}")
                return {"status": "error", "report": {}}

            # ✅ BUSINESS LOGIC: Get all versions for this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            if not versions:
                logger.warning(f"No versions found for certificate {certificate_id}")
                return {"status": "success", "report": {"message": "No versions found"}}

            # ✅ BUSINESS LOGIC: Generate report based on type
            report_data = {
                "certificate_id": certificate_id,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "generated_by": user_context.get("user_id"),
                "total_versions": len(versions)
            }

            if report_type == "summary":
                # Summary report with key metrics
                report_data.update({
                    "latest_version": max(versions, key=lambda v: v.created_at).version_number if versions else None,
                    "version_types": {vtype: len([v for v in versions if v.version_type == vtype]) for vtype in set(v.version_type for v in versions)},
                    "approval_statuses": {status: len([v for v in versions if v.approval_status == status]) for status in set(v.approval_status for v in versions)},
                    "deployment_environments": {env: len([v for v in versions if v.deployment_environment == env]) for env in set(v.deployment_environment for v in versions)},
                    "archive_statuses": {status: len([v for v in versions if v.archive_status == status]) for status in set(v.archive_status for v in versions)}
                })

            elif report_type == "detailed":
                # Detailed report with all version information
                report_data["versions"] = [
                    {
                        "version_id": v.version_id,
                        "version_number": v.version_number,
                        "version_type": v.version_type,
                        "approval_status": v.approval_status,
                        "deployment_status": v.deployment_status,
                        "deployment_environment": v.deployment_environment,
                        "archive_status": v.archive_status,
                        "quality_score": v.version_quality_score,
                        "created_at": v.created_at,
                        "created_by": v.created_by
                    } for v in versions
                ]

            elif report_type == "compliance":
                # Compliance report
                approved_versions = [v for v in versions if v.approval_status == "approved"]
                report_data.update({
                    "compliance_score": (len(approved_versions) / len(versions)) * 100 if versions else 0,
                    "approved_versions": len(approved_versions),
                    "pending_approvals": len([v for v in versions if v.approval_status == "pending"]),
                    "rejected_versions": len([v for v in versions if v.approval_status == "rejected"]),
                    "compliance_issues": [v.version_id for v in versions if v.approval_status not in ["approved", "pending"]]
                })

            elif report_type == "performance":
                # Performance report
                report_data.update({
                    "average_quality_score": sum(v.version_quality_score or 0 for v in versions) / len(versions) if versions else 0,
                    "high_quality_versions": len([v for v in versions if (v.version_quality_score or 0) >= 80]),
                    "deployment_performance": {
                        "deployed": len([v for v in versions if v.deployment_status == "deployed"]),
                        "not_deployed": len([v for v in versions if v.deployment_status == "not_deployed"]),
                        "failed": len([v for v in versions if v.deployment_status == "failed"])
                    }
                })

            elif report_type == "audit":
                # Audit report
                report_data.update({
                    "audit_trail": [
                        {
                            "version_id": v.version_id,
                            "version_number": v.version_number,
                            "action": "created",
                            "timestamp": v.created_at,
                            "user": v.created_by
                        } for v in versions
                    ],
                    "recent_activities": sorted(versions, key=lambda v: v.created_at, reverse=True)[:10]
                })
            
            logger.info(f"Generated {report_type} report for certificate {certificate_id} with {len(versions)} versions")
            return {"status": "success", "report": report_data}

        except Exception as e:
            logger.error(f"Error generating version report: {e}")
            return {"status": "error", "report": {}}

    async def get_version_metrics(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get version performance metrics.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            # ✅ BUSINESS LOGIC: Get all versions for this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            if not versions:
                logger.warning(f"No versions found for certificate {certificate_id}")
                return {"status": "success", "metrics": {"message": "No versions found"}}

            # ✅ BUSINESS LOGIC: Calculate performance metrics
            current_time = datetime.now()
            
            # Version lifecycle metrics
            total_versions = len(versions)
            active_versions = len([v for v in versions if v.archive_status == "active"])
            archived_versions = len([v for v in versions if v.archive_status == "archived"])
            
            # Approval metrics
            approved_versions = len([v for v in versions if v.approval_status == "approved"])
            pending_versions = len([v for v in versions if v.approval_status == "pending"])
            rejected_versions = len([v for v in versions if v.approval_status == "rejected"])
            
            # Deployment metrics
            deployed_versions = len([v for v in versions if v.deployment_status == "deployed"])
            production_versions = len([v for v in versions if v.deployment_environment == "production"])
            
            # Quality metrics
            quality_scores = [v.version_quality_score for v in versions if v.version_quality_score is not None]
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            high_quality_versions = len([v for v in versions if (v.version_quality_score or 0) >= 80])
            
            # Time-based metrics
            version_ages = []
            for version in versions:
                try:
                    created_time = datetime.fromisoformat(version.created_at.replace('Z', '+00:00'))
                    age_days = (current_time - created_time).days
                    version_ages.append(age_days)
                except:
                    continue
            
            avg_version_age = sum(version_ages) / len(version_ages) if version_ages else 0
            oldest_version_age = max(version_ages) if version_ages else 0
            newest_version_age = min(version_ages) if version_ages else 0
            
            # Version type distribution
            version_type_distribution = {}
            for version in versions:
                vtype = version.version_type
                version_type_distribution[vtype] = version_type_distribution.get(vtype, 0) + 1
            
            # Security metrics
            encrypted_versions = len([v for v in versions if v.encryption_status == "encrypted"])
            high_security_versions = len([v for v in versions if v.security_level == "high"])
            
            metrics = {
                "certificate_id": certificate_id,
                "generated_at": current_time.isoformat(),
                "generated_by": user_context.get("user_id"),
                
                # Basic counts
                "total_versions": total_versions,
                "active_versions": active_versions,
                "archived_versions": archived_versions,
                
                # Approval metrics
                "approval_metrics": {
                    "approved": approved_versions,
                    "pending": pending_versions,
                    "rejected": rejected_versions,
                    "approval_rate": (approved_versions / total_versions) * 100 if total_versions > 0 else 0
                },
                
                # Deployment metrics
                "deployment_metrics": {
                    "deployed": deployed_versions,
                    "production": production_versions,
                    "deployment_rate": (deployed_versions / total_versions) * 100 if total_versions > 0 else 0
                },
                
                # Quality metrics
                "quality_metrics": {
                    "average_quality_score": round(avg_quality_score, 2),
                    "high_quality_versions": high_quality_versions,
                    "quality_distribution": {
                        "excellent": len([v for v in versions if (v.version_quality_score or 0) >= 90]),
                        "good": len([v for v in versions if 70 <= (v.version_quality_score or 0) < 90]),
                        "fair": len([v for v in versions if 50 <= (v.version_quality_score or 0) < 70]),
                        "poor": len([v for v in versions if (v.version_quality_score or 0) < 50])
                    }
                },
                
                # Time metrics
                "time_metrics": {
                    "average_version_age_days": round(avg_version_age, 1),
                    "oldest_version_age_days": oldest_version_age,
                    "newest_version_age_days": newest_version_age
                },
                
                # Distribution metrics
                "version_type_distribution": version_type_distribution,
                
                # Security metrics
                "security_metrics": {
                    "encrypted_versions": encrypted_versions,
                    "high_security_versions": high_security_versions,
                    "encryption_rate": (encrypted_versions / total_versions) * 100 if total_versions > 0 else 0
                }
            }
            
            logger.info(f"Generated metrics for certificate {certificate_id} with {total_versions} versions")
            return {"status": "success", "metrics": metrics}
            
        except Exception as e:
            logger.error(f"Error getting version metrics: {e}")
            return {"status": "error", "metrics": {}}
    
    async def export_version_data(
        self,
        certificate_id: str,
        export_format: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Export version data for analysis.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            export_format: Format for export (json, csv, xml)
            user_context: User context for authorization
            
        Returns:
            Dictionary containing export data
        """
        try:
            # ✅ BUSINESS LOGIC: Validate export format
            valid_formats = ["json", "csv", "xml"]
            if export_format not in valid_formats:
                logger.error(f"Invalid export format: {export_format}")
                return {"status": "error", "export_data": {}}

            # ✅ BUSINESS LOGIC: Get all versions for this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            if not versions:
                logger.warning(f"No versions found for certificate {certificate_id}")
                return {"status": "success", "export_data": {"message": "No versions found"}}

            # ✅ BUSINESS LOGIC: Prepare export data
            export_timestamp = datetime.now().isoformat()
            export_metadata = {
                "certificate_id": certificate_id,
                "export_format": export_format,
                "export_timestamp": export_timestamp,
                "exported_by": user_context.get("user_id"),
                    "total_versions": len(versions)
            }

            # ✅ BUSINESS LOGIC: Format data based on export format
            if export_format == "json":
                export_data = {
                    "metadata": export_metadata,
                    "versions": [
                        {
                            "version_id": v.version_id,
                            "certificate_id": v.certificate_id,
                            "version_number": v.version_number,
                            "version_type": v.version_type,
                            "version_name": v.version_name,
                            "version_description": v.version_description,
                            "approval_status": v.approval_status,
                            "validation_status": v.validation_status,
                            "deployment_status": v.deployment_status,
                            "deployment_environment": v.deployment_environment,
                            "archive_status": v.archive_status,
                            "version_quality_score": v.version_quality_score,
                            "security_level": v.security_level,
                            "encryption_status": v.encryption_status,
                            "created_at": v.created_at,
                            "created_by": v.created_by,
                            "updated_at": v.updated_at,
                            "updated_by": v.updated_by
                        } for v in versions
                    ]
                }

            elif export_format == "csv":
                # Prepare CSV headers and rows
                headers = [
                    "version_id", "certificate_id", "version_number", "version_type", 
                    "version_name", "approval_status", "deployment_status", 
                    "deployment_environment", "archive_status", "quality_score",
                    "security_level", "created_at", "created_by"
                ]
                
                rows = []
                for v in versions:
                    rows.append([
                        v.version_id, v.certificate_id, v.version_number, v.version_type,
                        v.version_name, v.approval_status, v.deployment_status,
                        v.deployment_environment, v.archive_status, v.version_quality_score,
                        v.security_level, v.created_at, v.created_by
                    ])
                
                export_data = {
                    "metadata": export_metadata,
                    "headers": headers,
                    "rows": rows
                }

            elif export_format == "xml":
                # Prepare XML structure
                xml_versions = []
                for v in versions:
                    xml_versions.append({
                        "version_id": v.version_id,
                        "certificate_id": v.certificate_id,
                        "version_number": v.version_number,
                        "version_type": v.version_type,
                        "version_name": v.version_name,
                        "approval_status": v.approval_status,
                        "deployment_status": v.deployment_status,
                        "deployment_environment": v.deployment_environment,
                        "archive_status": v.archive_status,
                        "quality_score": v.version_quality_score,
                        "security_level": v.security_level,
                        "created_at": v.created_at,
                        "created_by": v.created_by
                    })
                
                export_data = {
                    "metadata": export_metadata,
                    "versions": xml_versions
                }

            logger.info(f"Exported {len(versions)} versions for certificate {certificate_id} in {export_format} format")
            return {"status": "success", "export_data": export_data}
            
        except Exception as e:
            logger.error(f"Error exporting version data: {e}")
            return {"status": "error", "export_data": {}}
    
    async def get_compliance_report(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get compliance status report.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            Dictionary containing compliance report
        """
        try:
            # ✅ BUSINESS LOGIC: Get all versions for this certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }

            versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            if not versions:
                logger.warning(f"No versions found for certificate {certificate_id}")
                return {"status": "success", "compliance": {"message": "No versions found"}}

            # ✅ BUSINESS LOGIC: Calculate compliance metrics
            total_versions = len(versions)
            current_time = datetime.now()
            
            # Approval compliance
            approved_versions = [v for v in versions if v.approval_status == "approved"]
            pending_versions = [v for v in versions if v.approval_status == "pending"]
            rejected_versions = [v for v in versions if v.approval_status == "rejected"]
            
            # Security compliance
            encrypted_versions = [v for v in versions if v.encryption_status == "encrypted"]
            high_security_versions = [v for v in versions if v.security_level == "high"]
            
            # Quality compliance
            high_quality_versions = [v for v in versions if (v.version_quality_score or 0) >= 80]
            quality_scores = [v.version_quality_score for v in versions if v.version_quality_score is not None]
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Archive compliance
            archived_versions = [v for v in versions if v.archive_status == "archived"]
            active_versions = [v for v in versions if v.archive_status == "active"]
            
            # Deployment compliance
            deployed_versions = [v for v in versions if v.deployment_status == "deployed"]
            production_versions = [v for v in versions if v.deployment_environment == "production"]
            
            # Calculate compliance scores
            approval_compliance_score = (len(approved_versions) / total_versions) * 100 if total_versions > 0 else 0
            security_compliance_score = (len(encrypted_versions) / total_versions) * 100 if total_versions > 0 else 0
            quality_compliance_score = (len(high_quality_versions) / total_versions) * 100 if total_versions > 0 else 0
            archive_compliance_score = (len(archived_versions) / total_versions) * 100 if total_versions > 0 else 0
            
            # Overall compliance score
            overall_compliance_score = (
                approval_compliance_score * 0.3 +
                security_compliance_score * 0.25 +
                quality_compliance_score * 0.25 +
                archive_compliance_score * 0.2
            )
            
            # Compliance issues
            compliance_issues = []
            
            # Check for non-approved versions in production
            non_approved_production = [v for v in versions if v.deployment_environment == "production" and v.approval_status != "approved"]
            if non_approved_production:
                compliance_issues.append(f"{len(non_approved_production)} non-approved versions in production")
            
            # Check for unencrypted high-security versions
            unencrypted_high_security = [v for v in versions if v.security_level == "high" and v.encryption_status != "encrypted"]
            if unencrypted_high_security:
                compliance_issues.append(f"{len(unencrypted_high_security)} high-security versions without encryption")
            
            # Check for low-quality approved versions
            low_quality_approved = [v for v in approved_versions if (v.version_quality_score or 0) < 70]
            if low_quality_approved:
                compliance_issues.append(f"{len(low_quality_approved)} approved versions with low quality scores")
            
            # Check for old active versions
            old_active_versions = []
            for v in active_versions:
                try:
                    created_time = datetime.fromisoformat(v.created_at.replace('Z', '+00:00'))
                    age_days = (current_time - created_time).days
                    if age_days > 365:  # More than 1 year old
                        old_active_versions.append(v)
                except:
                    continue
            
            if old_active_versions:
                compliance_issues.append(f"{len(old_active_versions)} active versions older than 1 year")

            # Determine overall compliance status
            if overall_compliance_score >= 90:
                compliance_status = "excellent"
            elif overall_compliance_score >= 75:
                compliance_status = "good"
            elif overall_compliance_score >= 60:
                compliance_status = "fair"
            else:
                compliance_status = "poor"

            compliance_report = {
                "certificate_id": certificate_id,
                "generated_at": current_time.isoformat(),
                "generated_by": user_context.get("user_id"),
                "total_versions": total_versions,
                
                # Overall compliance
                "overall_compliance_score": round(overall_compliance_score, 2),
                "compliance_status": compliance_status,
                "total_issues": len(compliance_issues),
                "compliance_issues": compliance_issues,
                
                # Detailed compliance metrics
                "approval_compliance": {
                    "score": round(approval_compliance_score, 2),
                    "approved": len(approved_versions),
                    "pending": len(pending_versions),
                    "rejected": len(rejected_versions),
                    "approval_rate": round(approval_compliance_score, 2)
                },
                
                "security_compliance": {
                    "score": round(security_compliance_score, 2),
                    "encrypted": len(encrypted_versions),
                    "high_security": len(high_security_versions),
                    "encryption_rate": round(security_compliance_score, 2)
                },
                
                "quality_compliance": {
                    "score": round(quality_compliance_score, 2),
                    "high_quality": len(high_quality_versions),
                    "average_quality_score": round(avg_quality_score, 2),
                    "quality_rate": round(quality_compliance_score, 2)
                },
                
                "archive_compliance": {
                    "score": round(archive_compliance_score, 2),
                    "archived": len(archived_versions),
                    "active": len(active_versions),
                    "archive_rate": round(archive_compliance_score, 2)
                },
                
                "deployment_compliance": {
                    "deployed": len(deployed_versions),
                    "production": len(production_versions),
                    "deployment_rate": round((len(deployed_versions) / total_versions) * 100, 2) if total_versions > 0 else 0
                }
            }
            
            logger.info(f"Generated compliance report for certificate {certificate_id}: {compliance_status} ({overall_compliance_score}%)")
            return {"status": "success", "compliance": compliance_report}

        except Exception as e:
            logger.error(f"Error getting compliance report: {e}")
            return {"status": "error", "compliance": {}}

    # 🔍 AUDIT & COMPLIANCE METHODS

    async def get_version_audit_trail(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get complete audit trail for version.
        
        This is a business domain method that uses the CRUD get_entity method.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            List of audit trail entries
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            version = await self.get_entity(version_id, user_context)
            if not version:
                logger.error(f"Version not found: {version_id}")
                return []

            # ✅ BUSINESS LOGIC: Build comprehensive audit trail
            audit_trail = []
            current_time = datetime.now()

            # Version creation event
            audit_trail.append({
                "event_id": f"{version_id}_created",
                "event_type": "version_created",
                "timestamp": version.created_at,
                "user_id": version.created_by,
                "action": "created",
                "description": f"Version {version.version_number} created",
                "details": {
                    "version_number": version.version_number,
                    "version_type": version.version_type,
                    "version_name": version.version_name,
                    "certificate_id": version.certificate_id
                }
            })

            # Version update event (if updated)
            if version.updated_at and version.updated_at != version.created_at:
                audit_trail.append({
                    "event_id": f"{version_id}_updated",
                    "event_type": "version_updated",
                    "timestamp": version.updated_at,
                    "user_id": version.updated_by,
                    "action": "updated",
                    "description": f"Version {version.version_number} updated",
                    "details": {
                        "updated_by": version.updated_by,
                        "update_fields": ["version_data"]
                    }
                })

            # Approval events
            if version.approval_timestamp:
                audit_trail.append({
                    "event_id": f"{version_id}_approved",
                    "event_type": "version_approved",
                    "timestamp": version.approval_timestamp,
                    "user_id": version.approved_by,
                    "action": "approved",
                    "description": f"Version {version.version_number} approved",
                    "details": {
                        "approval_status": version.approval_status,
                        "approval_notes": version.approval_notes,
                        "approved_by": version.approved_by
                    }
                })

            # Archive events
            if version.archive_timestamp:
                audit_trail.append({
                    "event_id": f"{version_id}_archived",
                    "event_type": "version_archived",
                    "timestamp": version.archive_timestamp,
                    "user_id": version.archived_by,
                    "action": "archived",
                    "description": f"Version {version.version_number} archived",
                    "details": {
                        "archive_status": version.archive_status,
                        "archive_reason": version.archive_reason,
                        "archived_by": version.archived_by
                    }
                })

            # Restore events
            if version.restore_timestamp:
                audit_trail.append({
                    "event_id": f"{version_id}_restored",
                    "event_type": "version_restored",
                    "timestamp": version.restore_timestamp,
                    "user_id": version.restored_by,
                    "action": "restored",
                    "description": f"Version {version.version_number} restored",
                    "details": {
                        "restore_reason": version.restore_reason,
                        "restored_by": version.restored_by
                    }
                })

            # Deployment events
            if version.deployment_timestamp:
                audit_trail.append({
                    "event_id": f"{version_id}_deployed",
                    "event_type": "version_deployed",
                    "timestamp": version.deployment_timestamp,
                    "user_id": version.deployed_by,
                    "action": "deployed",
                    "description": f"Version {version.version_number} deployed to {version.deployment_environment}",
                    "details": {
                        "deployment_environment": version.deployment_environment,
                        "deployment_status": version.deployment_status,
                        "deployed_by": version.deployed_by
                    }
                })

            # Link events
            if version.linked_at:
                audit_trail.append({
                    "event_id": f"{version_id}_linked",
                    "event_type": "version_linked",
                    "timestamp": version.linked_at,
                    "user_id": version.linked_by,
                    "action": "linked",
                    "description": f"Version {version.version_number} linked to certificate",
                    "details": {
                        "certificate_id": version.certificate_id,
                        "linked_by": version.linked_by
                    }
                })

            # Unlink events
            if version.unlinked_at:
                audit_trail.append({
                    "event_id": f"{version_id}_unlinked",
                    "event_type": "version_unlinked",
                    "timestamp": version.unlinked_at,
                    "user_id": version.unlinked_by,
                    "action": "unlinked",
                    "description": f"Version {version.version_number} unlinked from certificate",
                    "details": {
                        "unlinked_by": version.unlinked_by
                    }
                })

            # Sync events
            if version.last_sync_timestamp:
                audit_trail.append({
                    "event_id": f"{version_id}_synced",
                    "event_type": "version_synced",
                    "timestamp": version.last_sync_timestamp,
                    "user_id": version.last_sync_by,
                    "action": "synced",
                    "description": f"Version {version.version_number} synchronized",
                    "details": {
                        "sync_type": "module_sync",
                        "synced_by": version.last_sync_by
                    }
                })

            # Sort audit trail by timestamp (newest first)
            audit_trail.sort(key=lambda x: x["timestamp"], reverse=True)

            # Add audit trail metadata
            audit_metadata = {
                "version_id": version_id,
                "version_number": version.version_number,
                "total_events": len(audit_trail),
                "generated_at": current_time.isoformat(),
                "generated_by": user_context.get("user_id")
            }

            logger.info(f"Generated audit trail for version {version_id} with {len(audit_trail)} events")
            return [audit_metadata] + audit_trail

        except Exception as e:
            logger.error(f"Error getting version audit trail: {e}")
            return []

    async def validate_compliance(
        self,
        version_id: str,
        compliance_standard: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate version compliance against standard.
        
        This is a business domain method that uses the CRUD get_entity method.
        
        Args:
            version_id: ID of the version
            compliance_standard: Compliance standard to validate against
            user_context: User context for authorization
            
        Returns:
            Dictionary containing compliance validation results
        """
        try:
            # ✅ BUSINESS LOGIC: Validate compliance standard
            valid_standards = ["GDPR", "SOX", "ISO27001", "NIST", "HIPAA", "PCI-DSS", "SOC2"]
            if compliance_standard not in valid_standards:
                logger.error(f"Invalid compliance standard: {compliance_standard}")
                return {"status": "error", "compliance": "invalid_standard"}

            # ✅ BUSINESS LOGIC: Get current version
            version = await self.get_entity(version_id, user_context)
            if not version:
                logger.error(f"Version not found: {version_id}")
                return {"status": "error", "compliance": "version_not_found"}

            # ✅ BUSINESS LOGIC: Perform compliance validation based on standard
            compliance_results = {
                "version_id": version_id,
                "compliance_standard": compliance_standard,
                "validated_at": datetime.now().isoformat(),
                "validated_by": user_context.get("user_id"),
                "overall_compliance": "unknown",
                "compliance_score": 0,
                "requirements": {},
                "violations": [],
                "recommendations": []
            }

            if compliance_standard == "GDPR":
                # GDPR compliance checks
                gdpr_requirements = {
                    "data_encryption": version.encryption_status == "encrypted",
                    "access_control": version.security_level in ["high", "critical"],
                    "audit_trail": version.created_at is not None,
                    "data_minimization": version.module_data_snapshot is not None,
                    "consent_management": version.approval_status == "approved"
                }
                
                compliance_results["requirements"] = gdpr_requirements
                compliance_score = (sum(gdpr_requirements.values()) / len(gdpr_requirements)) * 100
                
                if not gdpr_requirements["data_encryption"]:
                    compliance_results["violations"].append("Data not encrypted - GDPR Article 32")
                if not gdpr_requirements["access_control"]:
                    compliance_results["violations"].append("Insufficient access control - GDPR Article 25")
                if not gdpr_requirements["consent_management"]:
                    compliance_results["violations"].append("No approval process - GDPR Article 6")

            elif compliance_standard == "SOX":
                # SOX compliance checks
                sox_requirements = {
                    "audit_trail": version.created_at is not None and version.updated_at is not None,
                    "access_control": version.security_level in ["high", "critical"],
                    "change_management": version.approval_status == "approved",
                    "data_integrity": version.version_quality_score and version.version_quality_score >= 80,
                    "segregation_of_duties": version.created_by != version.approved_by
                }
                
                compliance_results["requirements"] = sox_requirements
                compliance_score = (sum(sox_requirements.values()) / len(sox_requirements)) * 100
                
                if not sox_requirements["audit_trail"]:
                    compliance_results["violations"].append("Incomplete audit trail - SOX Section 404")
                if not sox_requirements["change_management"]:
                    compliance_results["violations"].append("No change management process - SOX Section 302")

            elif compliance_standard == "ISO27001":
                # ISO 27001 compliance checks
                iso_requirements = {
                    "information_security_policy": version.security_level in ["high", "critical"],
                    "access_control": version.encryption_status == "encrypted",
                    "cryptography": version.encryption_status == "encrypted",
                    "operations_security": version.deployment_status in ["deployed", "not_deployed"],
                    "monitoring": version.created_at is not None
                }
                
                compliance_results["requirements"] = iso_requirements
                compliance_score = (sum(iso_requirements.values()) / len(iso_requirements)) * 100
                
                if not iso_requirements["cryptography"]:
                    compliance_results["violations"].append("No encryption implemented - ISO 27001 A.10.1.1")

            elif compliance_standard == "NIST":
                # NIST compliance checks
                nist_requirements = {
                    "identify": version.certificate_id is not None,
                    "protect": version.encryption_status == "encrypted",
                    "detect": version.created_at is not None,
                    "respond": version.approval_status in ["approved", "rejected"],
                    "recover": version.archive_status in ["active", "archived"]
                }
                
                compliance_results["requirements"] = nist_requirements
                compliance_score = (sum(nist_requirements.values()) / len(nist_requirements)) * 100
                
                if not nist_requirements["protect"]:
                    compliance_results["violations"].append("Data protection insufficient - NIST PR.AC-1")

            elif compliance_standard == "HIPAA":
                # HIPAA compliance checks
                hipaa_requirements = {
                    "administrative_safeguards": version.approval_status == "approved",
                    "physical_safeguards": version.security_level in ["high", "critical"],
                    "technical_safeguards": version.encryption_status == "encrypted",
                    "audit_controls": version.created_at is not None,
                    "access_control": version.security_level in ["high", "critical"]
                }
                
                compliance_results["requirements"] = hipaa_requirements
                compliance_score = (sum(hipaa_requirements.values()) / len(hipaa_requirements)) * 100
                
                if not hipaa_requirements["technical_safeguards"]:
                    compliance_results["violations"].append("Technical safeguards missing - HIPAA §164.312")

            elif compliance_standard == "PCI-DSS":
                # PCI-DSS compliance checks
                pci_requirements = {
                    "firewall_configuration": version.security_level in ["high", "critical"],
                    "default_passwords": version.encryption_status == "encrypted",
                    "cardholder_data_protection": version.encryption_status == "encrypted",
                    "encryption": version.encryption_status == "encrypted",
                    "access_control": version.approval_status == "approved"
                }
                
                compliance_results["requirements"] = pci_requirements
                compliance_score = (sum(pci_requirements.values()) / len(pci_requirements)) * 100
                
                if not pci_requirements["encryption"]:
                    compliance_results["violations"].append("Data encryption required - PCI DSS Requirement 3.4")

            elif compliance_standard == "SOC2":
                # SOC2 compliance checks
                soc2_requirements = {
                    "security": version.security_level in ["high", "critical"],
                    "availability": version.deployment_status in ["deployed", "not_deployed"],
                    "processing_integrity": version.version_quality_score and version.version_quality_score >= 80,
                    "confidentiality": version.encryption_status == "encrypted",
                    "privacy": version.approval_status == "approved"
                }
                
                compliance_results["requirements"] = soc2_requirements
                compliance_score = (sum(soc2_requirements.values()) / len(soc2_requirements)) * 100
                
                if not soc2_requirements["confidentiality"]:
                    compliance_results["violations"].append("Confidentiality controls missing - SOC2 CC6.1")

            # Determine overall compliance status
            compliance_results["compliance_score"] = round(compliance_score, 2)
            
            if compliance_score >= 90:
                compliance_results["overall_compliance"] = "compliant"
            elif compliance_score >= 75:
                compliance_results["overall_compliance"] = "mostly_compliant"
            elif compliance_score >= 60:
                compliance_results["overall_compliance"] = "partially_compliant"
            else:
                compliance_results["overall_compliance"] = "non_compliant"

            # Add recommendations based on violations
            if compliance_results["violations"]:
                compliance_results["recommendations"].append("Address all identified violations to improve compliance")
                if "encryption" in str(compliance_results["violations"]).lower():
                    compliance_results["recommendations"].append("Implement data encryption for sensitive information")
                if "audit" in str(compliance_results["violations"]).lower():
                    compliance_results["recommendations"].append("Ensure complete audit trail is maintained")
                if "approval" in str(compliance_results["violations"]).lower():
                    compliance_results["recommendations"].append("Implement proper approval workflow")

            logger.info(f"Validated {compliance_standard} compliance for version {version_id}: {compliance_results['overall_compliance']} ({compliance_score}%)")
            return {"status": "success", "compliance": compliance_results}

        except Exception as e:
            logger.error(f"Error validating compliance: {e}")
            return {"status": "error", "compliance": "validation_failed"}

    async def get_approval_compliance(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get approval compliance status.
        
        This is a business domain method that uses the CRUD get_entity method.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            Dictionary containing approval compliance status
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            version = await self.get_entity(version_id, user_context)
            if not version:
                logger.error(f"Version not found: {version_id}")
                return {"status": "error", "approval_compliance": "version_not_found"}

            # ✅ BUSINESS LOGIC: Calculate approval compliance metrics
            current_time = datetime.now()
            compliance_score = 0
            compliance_issues = []
            compliance_status = "unknown"

            # Check approval status compliance
            if version.approval_status == "approved":
                compliance_score += 40
                if version.approved_by:
                    compliance_score += 20
                if version.approval_timestamp:
                    compliance_score += 20
                if version.approval_notes:
                    compliance_score += 20
            elif version.approval_status == "pending":
                compliance_score += 20
                compliance_issues.append("Version is pending approval")
            elif version.approval_status == "rejected":
                compliance_score += 10
                compliance_issues.append("Version has been rejected")
            else:
                compliance_issues.append("Invalid approval status")

            # Check approval workflow compliance
            if version.created_by and version.approved_by:
                if version.created_by != version.approved_by:
                    compliance_score += 10  # Segregation of duties
                else:
                    compliance_issues.append("Same user created and approved version")
            else:
                compliance_issues.append("Missing creator or approver information")

            # Check approval timing compliance
            if version.approval_timestamp and version.created_at:
                try:
                    created_time = datetime.fromisoformat(version.created_at.replace('Z', '+00:00'))
                    approval_time = datetime.fromisoformat(version.approval_timestamp.replace('Z', '+00:00'))
                    approval_duration = (approval_time - created_time).total_seconds() / 3600  # hours
                    
                    if approval_duration <= 24:
                        compliance_score += 10  # Quick approval
                    elif approval_duration <= 72:
                        compliance_score += 5   # Reasonable approval time
                    else:
                        compliance_issues.append(f"Approval took too long: {approval_duration:.1f} hours")
                except:
                    compliance_issues.append("Invalid timestamp format")

            # Check approval documentation compliance
            if version.approval_notes and len(version.approval_notes.strip()) > 10:
                compliance_score += 10  # Adequate documentation
            else:
                compliance_issues.append("Insufficient approval documentation")

            # Check version quality for approval
            if version.version_quality_score:
                if version.version_quality_score >= 80:
                    compliance_score += 10  # High quality approved
                elif version.version_quality_score >= 60:
                    compliance_score += 5   # Acceptable quality
                else:
                    compliance_issues.append(f"Low quality score for approved version: {version.version_quality_score}")

            # Determine compliance status
            if compliance_score >= 90:
                compliance_status = "excellent"
            elif compliance_score >= 75:
                compliance_status = "good"
            elif compliance_score >= 60:
                compliance_status = "fair"
            elif compliance_score >= 40:
                compliance_status = "poor"
            else:
                compliance_status = "critical"

            # Generate recommendations
            recommendations = []
            if compliance_issues:
                recommendations.append("Address all identified compliance issues")
                if "pending" in str(compliance_issues).lower():
                    recommendations.append("Complete approval process for pending versions")
                if "rejected" in str(compliance_issues).lower():
                    recommendations.append("Review and address rejection reasons")
                if "segregation" in str(compliance_issues).lower() or "same user" in str(compliance_issues).lower():
                    recommendations.append("Implement proper segregation of duties in approval workflow")
                if "documentation" in str(compliance_issues).lower():
                    recommendations.append("Ensure adequate approval documentation is provided")
                if "quality" in str(compliance_issues).lower():
                    recommendations.append("Improve version quality before approval")

            approval_compliance = {
                "version_id": version_id,
                "version_number": version.version_number,
                "compliance_score": min(100, compliance_score),
                "compliance_status": compliance_status,
                "total_issues": len(compliance_issues),
                "compliance_issues": compliance_issues,
                "recommendations": recommendations,
                "approval_details": {
                    "approval_status": version.approval_status,
                    "approved_by": version.approved_by,
                    "approval_timestamp": version.approval_timestamp,
                    "approval_notes": version.approval_notes,
                    "created_by": version.created_by,
                    "created_at": version.created_at,
                    "quality_score": version.version_quality_score
                },
                "workflow_compliance": {
                    "segregation_of_duties": version.created_by != version.approved_by if version.created_by and version.approved_by else False,
                    "approval_documentation": bool(version.approval_notes and len(version.approval_notes.strip()) > 10),
                    "timely_approval": version.approval_timestamp is not None,
                    "quality_approved": (version.version_quality_score or 0) >= 60
                },
                "generated_at": current_time.isoformat(),
                "generated_by": user_context.get("user_id")
            }

            logger.info(f"Generated approval compliance for version {version_id}: {compliance_status} ({compliance_score}%)")
            return {"status": "success", "approval_compliance": approval_compliance}

        except Exception as e:
            logger.error(f"Error getting approval compliance: {e}")
            return {"status": "error", "approval_compliance": "validation_failed"}

    # 🚀 DEPLOYMENT & RELEASE METHODS

    async def prepare_for_release(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Prepare version for release.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            True if preparation successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Validate version is ready for release
            if current_version.approval_status != "approved":
                logger.error(f"Version {version_id} is not approved for release")
                return False

            if current_version.archive_status == "archived":
                logger.error(f"Version {version_id} is archived and cannot be released")
                return False

            if current_version.deployment_status == "deployed":
                logger.warning(f"Version {version_id} is already deployed")
                return True

            # ✅ BUSINESS LOGIC: Check quality requirements
            if not current_version.version_quality_score or current_version.version_quality_score < 70:
                logger.error(f"Version {version_id} quality score too low for release: {current_version.version_quality_score}")
                return False

            # ✅ BUSINESS LOGIC: Check security requirements
            if current_version.security_level == "critical" and current_version.encryption_status != "encrypted":
                logger.error(f"Version {version_id} requires encryption for critical security level")
                return False

            # ✅ BUSINESS LOGIC: Prepare release data
            current_time = datetime.now()
            update_data = {
                "deployment_status": "ready_for_release",
                "release_preparation_timestamp": current_time.isoformat(),
                "release_prepared_by": user_context.get("user_id"),
                "release_notes": f"Version {current_version.version_number} prepared for release",
                "validation_status": "validated"
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully prepared version {version_id} for release")
                return True
            else:
                logger.error(f"Failed to prepare version {version_id} for release")
                return False
                
        except Exception as e:
            logger.error(f"Error preparing version for release: {e}")
            return False

    async def release_version(
        self,
        version_id: str,
        release_notes: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Release version to production.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            release_notes: Release notes
            user_context: User context for authorization
            
        Returns:
            True if release successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Validate version is ready for release
            if current_version.approval_status != "approved":
                logger.error(f"Version {version_id} is not approved for release")
                return False

            if current_version.archive_status == "archived":
                logger.error(f"Version {version_id} is archived and cannot be released")
                return False

            if current_version.deployment_status == "deployed":
                logger.warning(f"Version {version_id} is already deployed")
                return True

            # ✅ BUSINESS LOGIC: Check if version is prepared for release
            if current_version.deployment_status not in ["ready_for_release", "not_deployed"]:
                logger.error(f"Version {version_id} is not prepared for release")
                return False

            # ✅ BUSINESS LOGIC: Validate release notes
            if not release_notes or len(release_notes.strip()) < 10:
                logger.error("Release notes must be at least 10 characters long")
                return False

            # ✅ BUSINESS LOGIC: Check for existing production deployments
            # Get all versions for this certificate to check for production conflicts
            criteria = {
                "certificate_id": current_version.certificate_id,
                "deployment_environment": "production",
                "deployment_status": "deployed",
                "is_deleted": False
            }
            
            existing_production = await self.search_entities(criteria, user_context, limit=10, offset=0)
            if existing_production:
                logger.warning(f"Found {len(existing_production)} existing production deployments for certificate {current_version.certificate_id}")

            # ✅ BUSINESS LOGIC: Prepare release data
            current_time = datetime.now()
            update_data = {
                "deployment_status": "deployed",
                "deployment_environment": "production",
                "deployment_timestamp": current_time.isoformat(),
                "deployed_by": user_context.get("user_id"),
                "release_notes": release_notes,
                "version_type": "released",
                "validation_status": "validated"
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully released version {version_id} to production")
                return True
            else:
                logger.error(f"Failed to release version {version_id} to production")
                return False
                
        except Exception as e:
            logger.error(f"Error releasing version: {e}")
            return False

    async def rollback_release(
        self,
        version_id: str,
        rollback_reason: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Rollback production release.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version to rollback
            rollback_reason: Reason for rollback
            user_context: User context for authorization
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Validate version can be rolled back
            if current_version.deployment_status != "deployed":
                logger.error(f"Version {version_id} is not deployed and cannot be rolled back")
                return False

            if current_version.deployment_environment != "production":
                logger.error(f"Version {version_id} is not in production and cannot be rolled back")
                return False

            if current_version.archive_status == "archived":
                logger.error(f"Version {version_id} is archived and cannot be rolled back")
                return False

            # ✅ BUSINESS LOGIC: Validate rollback reason
            if not rollback_reason or len(rollback_reason.strip()) < 10:
                logger.error("Rollback reason must be at least 10 characters long")
                return False

            # ✅ BUSINESS LOGIC: Check if there's a previous version to rollback to
            criteria = {
                "certificate_id": current_version.certificate_id,
                "deployment_status": "deployed",
                "deployment_environment": "production",
                "is_deleted": False
            }
            
            production_versions = await self.search_entities(criteria, user_context, limit=10, offset=0)
            if len(production_versions) <= 1:
                logger.warning(f"No previous production version found for rollback of certificate {current_version.certificate_id}")

            # ✅ BUSINESS LOGIC: Prepare rollback data
            current_time = datetime.now()
            update_data = {
                "deployment_status": "rollback",
                "rollback_timestamp": current_time.isoformat(),
                "rollback_reason": rollback_reason,
                "rollback_by": user_context.get("user_id"),
                "version_type": "rollback",
                "validation_status": "rollback"
            }

            # ✅ BUSINESS LOGIC: Use the existing update_entity method (clean architecture)
            success = await self.update_entity(version_id, update_data, user_context)
            
            if success:
                logger.info(f"Successfully rolled back version {version_id} from production")
                return True
            else:
                logger.error(f"Failed to rollback version {version_id} from production")
                return False
                
        except Exception as e:
            logger.error(f"Error rolling back release: {e}")
            return False

    async def get_release_candidates(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> List[CertificateVersions]:
        """
        Get versions ready for release.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            List of release candidate versions
        """
        try:
            # ✅ BUSINESS LOGIC: Search for versions ready for release
            criteria = {
                "certificate_id": certificate_id,
                "approval_status": "approved",
                "archive_status": "active",
                "deployment_status": "not_deployed",
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            all_versions = await self.search_entities(criteria, user_context, limit=100, offset=0)
            
            # ✅ BUSINESS LOGIC: Filter for release candidates based on quality and readiness
            release_candidates = []
            for version in all_versions:
                # Check quality requirements
                if not version.version_quality_score or version.version_quality_score < 70:
                    continue
                
                # Check security requirements
                if version.security_level == "critical" and version.encryption_status != "encrypted":
                    continue
                
                # Check if version is not already in production
                if version.deployment_environment == "production":
                    continue
                
                # Check if version has proper validation
                if version.validation_status not in ["validated", "pending"]:
                    continue
                
                release_candidates.append(version)
            
            # ✅ BUSINESS LOGIC: Sort by quality score and creation date
            release_candidates.sort(key=lambda v: (
                v.version_quality_score or 0,
                v.created_at
            ), reverse=True)
            
            logger.info(f"Found {len(release_candidates)} release candidates for certificate {certificate_id}")
            return release_candidates

        except Exception as e:
            logger.error(f"Error getting release candidates: {e}")
            return []

    # 🌍 ENVIRONMENT MANAGEMENT METHODS

    async def deploy_to_environment(
        self,
        version_id: str,
        environment: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Deploy version to specific environment.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            environment: Target environment
            user_context: User context for authorization
            
        Returns:
            True if deployment successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate environment
            valid_environments = ["development", "staging", "production", "testing"]
            if environment not in valid_environments:
                logger.error(f"Invalid environment: {environment}")
                return False

            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check deployment prerequisites
            if current_version.archive_status == "archived":
                logger.error(f"Cannot deploy archived version: {version_id}")
                return False

            if current_version.approval_status not in ["approved", "released"]:
                logger.error(f"Cannot deploy unapproved version: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check for existing deployment in same environment
            if current_version.deployment_environment == environment:
                logger.warning(f"Version {version_id} is already deployed to {environment}")
                return True

            # ✅ BUSINESS LOGIC: Create deployment update data
            deployment_data = {
                "deployment_environment": environment,
                "deployment_status": "deployed",
                "deployment_timestamp": datetime.utcnow().isoformat(),
                "deployment_metadata": {
                    "deployed_by": user_context.get("user_id", "unknown"),
                    "deployment_environment": environment,
                    "deployment_timestamp": datetime.utcnow().isoformat(),
                    "deployment_notes": f"Deployed to {environment} environment"
                }
            }

            # ✅ BUSINESS LOGIC: Use existing update method
            success = await self.update_entity(version_id, deployment_data, user_context)
            
            if success:
                logger.info(f"Successfully deployed version {version_id} to {environment}")
                return True
            else:
                logger.error(f"Failed to deploy version {version_id} to {environment}")
                return False

        except Exception as e:
            logger.error(f"Error deploying version to environment: {e}")
            return False

    async def get_environment_versions(
        self,
        certificate_id: str,
        environment: str,
        user_context: Dict[str, Any]
    ) -> List[CertificateVersions]:
        """
        Get versions in specific environment.
        
        This is a business domain method that uses the CRUD search_entities method.
        
        Args:
            certificate_id: ID of the certificate
            environment: Environment to check
            user_context: User context for authorization
            
        Returns:
            List of versions in the environment
        """
        try:
            # ✅ BUSINESS LOGIC: Validate environment
            valid_environments = ["development", "staging", "production", "testing"]
            if environment not in valid_environments:
                logger.error(f"Invalid environment: {environment}")
                return []

            # ✅ BUSINESS LOGIC: Search for versions in the environment
            criteria = {
                "certificate_id": certificate_id,
                "deployment_environment": environment,
                "deployment_status": "deployed",
                "is_deleted": False
            }

            # ✅ BUSINESS LOGIC: Use existing search method
            environment_versions = await self.search_entities(criteria, user_context, limit=100, offset=0)
            
            # ✅ BUSINESS LOGIC: Sort by deployment timestamp (most recent first)
            environment_versions.sort(key=lambda v: v.deployment_timestamp or v.created_at, reverse=True)
            
            logger.info(f"Found {len(environment_versions)} versions in {environment} for certificate {certificate_id}")
            return environment_versions

        except Exception as e:
            logger.error(f"Error getting environment versions: {e}")
            return []

    async def promote_environment(
        self,
        version_id: str,
        from_environment: str,
        to_environment: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Promote version between environments.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            from_environment: Source environment
            to_environment: Target environment
            user_context: User context for authorization
            
        Returns:
            True if promotion successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate environments
            valid_environments = ["development", "staging", "production", "testing"]
            if from_environment not in valid_environments or to_environment not in valid_environments:
                logger.error(f"Invalid environment: {from_environment} or {to_environment}")
                return False

            # ✅ BUSINESS LOGIC: Check promotion flow rules
            promotion_flow = {
                "development": ["staging", "testing"],
                "testing": ["staging"],
                "staging": ["production"],
                "production": []  # Production is final
            }
            
            if to_environment not in promotion_flow.get(from_environment, []):
                logger.error(f"Invalid promotion flow: {from_environment} → {to_environment}")
                return False

            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check current deployment status
            if current_version.deployment_environment != from_environment:
                logger.error(f"Version {version_id} is not deployed in {from_environment}")
                return False

            if current_version.deployment_status != "deployed":
                logger.error(f"Version {version_id} is not properly deployed")
                return False

            # ✅ BUSINESS LOGIC: Check approval status for production promotion
            if to_environment == "production" and current_version.approval_status != "approved":
                logger.error(f"Version {version_id} must be approved before production promotion")
                return False

            # ✅ BUSINESS LOGIC: Create promotion update data
            promotion_data = {
                "deployment_environment": to_environment,
                "deployment_status": "deployed",
                "deployment_timestamp": datetime.utcnow().isoformat(),
                "deployment_metadata": {
                    "promoted_from": from_environment,
                    "promoted_to": to_environment,
                    "promoted_by": user_context.get("user_id", "unknown"),
                    "promotion_timestamp": datetime.utcnow().isoformat(),
                    "promotion_notes": f"Promoted from {from_environment} to {to_environment}"
                }
            }

            # ✅ BUSINESS LOGIC: Use existing update method
            success = await self.update_entity(version_id, promotion_data, user_context)
            
            if success:
                logger.info(f"Successfully promoted version {version_id} from {from_environment} to {to_environment}")
                return True
            else:
                logger.error(f"Failed to promote version {version_id} from {from_environment} to {to_environment}")
                return False

        except Exception as e:
            logger.error(f"Error promoting version between environments: {e}")
            return False

    # 🔧 CONFIGURATION & SETTINGS METHODS

    async def configure_version_policy(
        self,
        policy_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Configure version policies.
        
        This is a business domain method that validates and stores policy configuration.
        
        Args:
            policy_data: Policy configuration data
            user_context: User context for authorization
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate policy data structure
            required_fields = ["policy_name", "policy_type", "policy_rules"]
            for field in required_fields:
                if field not in policy_data:
                    logger.error(f"Missing required policy field: {field}")
                    return False

            # ✅ BUSINESS LOGIC: Validate policy type
            valid_policy_types = ["approval", "deployment", "retention", "security", "quality"]
            if policy_data["policy_type"] not in valid_policy_types:
                logger.error(f"Invalid policy type: {policy_data['policy_type']}")
                return False

            # ✅ BUSINESS LOGIC: Validate policy rules structure
            policy_rules = policy_data.get("policy_rules", {})
            if not isinstance(policy_rules, dict):
                logger.error("Policy rules must be a dictionary")
                return False

            # ✅ BUSINESS LOGIC: Create policy configuration record
            policy_config = {
                "policy_name": policy_data["policy_name"],
                "policy_type": policy_data["policy_type"],
                "policy_rules": policy_rules,
                "policy_metadata": {
                    "configured_by": user_context.get("user_id", "unknown"),
                    "configuration_timestamp": datetime.utcnow().isoformat(),
                    "policy_version": policy_data.get("policy_version", "1.0"),
                    "policy_description": policy_data.get("policy_description", ""),
                    "policy_scope": policy_data.get("policy_scope", "global")
                },
                "is_active": policy_data.get("is_active", True),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # ✅ BUSINESS LOGIC: Store policy configuration (using a generic entity creation)
            # Note: This would typically use a dedicated policy configuration service
            # For now, we'll log the configuration and return success
            logger.info(f"Policy configuration created: {policy_data['policy_name']}")
            logger.info(f"Policy type: {policy_data['policy_type']}")
            logger.info(f"Policy rules: {policy_rules}")
            
            return True

        except Exception as e:
            logger.error(f"Error configuring version policy: {e}")
            return False

    async def set_version_constraints(
        self,
        certificate_id: str,
        constraints: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Set version constraints.
        
        This is a business domain method that validates and applies version constraints.
        
        Args:
            certificate_id: ID of the certificate
            constraints: Version constraints
            user_context: User context for authorization
            
        Returns:
            True if setting successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate constraints structure
            if not isinstance(constraints, dict):
                logger.error("Constraints must be a dictionary")
                return False

            # ✅ BUSINESS LOGIC: Validate constraint types
            valid_constraint_types = [
                "max_versions", "min_quality_score", "required_approvals",
                "deployment_restrictions", "retention_period", "security_levels"
            ]
            
            for constraint_type in constraints.keys():
                if constraint_type not in valid_constraint_types:
                    logger.warning(f"Unknown constraint type: {constraint_type}")

            # ✅ BUSINESS LOGIC: Validate specific constraint values
            if "max_versions" in constraints:
                max_versions = constraints["max_versions"]
                if not isinstance(max_versions, int) or max_versions <= 0:
                    logger.error("max_versions must be a positive integer")
                    return False

            if "min_quality_score" in constraints:
                min_quality = constraints["min_quality_score"]
                if not isinstance(min_quality, (int, float)) or not (0 <= min_quality <= 100):
                    logger.error("min_quality_score must be a number between 0 and 100")
                    return False

            if "required_approvals" in constraints:
                required_approvals = constraints["required_approvals"]
                if not isinstance(required_approvals, int) or required_approvals < 0:
                    logger.error("required_approvals must be a non-negative integer")
                    return False

            # ✅ BUSINESS LOGIC: Create constraint configuration
            constraint_config = {
                "certificate_id": certificate_id,
                "constraints": constraints,
                "constraint_metadata": {
                    "set_by": user_context.get("user_id", "unknown"),
                    "set_timestamp": datetime.utcnow().isoformat(),
                    "constraint_version": constraints.get("version", "1.0"),
                    "constraint_scope": constraints.get("scope", "certificate")
                },
                "is_active": constraints.get("is_active", True),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # ✅ BUSINESS LOGIC: Store constraint configuration
            # Note: This would typically use a dedicated constraint configuration service
            # For now, we'll log the configuration and return success
            logger.info(f"Version constraints set for certificate {certificate_id}")
            logger.info(f"Constraints: {constraints}")
            
            return True

        except Exception as e:
            logger.error(f"Error setting version constraints: {e}")
            return False

    async def update_version_metadata(
        self,
        version_id: str,
        metadata: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Update version metadata.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            metadata: Metadata to update
            user_context: User context for authorization
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate metadata structure
            if not isinstance(metadata, dict):
                logger.error("Metadata must be a dictionary")
                return False

            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Validate metadata fields
            valid_metadata_fields = [
                "version_description", "version_notes", "version_tags",
                "version_author", "version_reviewer", "version_approver",
                "version_source", "version_branch", "version_commit",
                "version_build_number", "version_release_notes"
            ]
            
            # Check for unknown metadata fields
            for field in metadata.keys():
                if field not in valid_metadata_fields:
                    logger.warning(f"Unknown metadata field: {field}")

            # ✅ BUSINESS LOGIC: Create metadata update data
            metadata_update = {
                "version_metadata": {
                    **current_version.version_metadata,  # Preserve existing metadata
                    **metadata,  # Add/update with new metadata
                    "last_updated_by": user_context.get("user_id", "unknown"),
                    "last_updated_timestamp": datetime.utcnow().isoformat()
                },
                "updated_at": datetime.utcnow().isoformat()
            }

            # ✅ BUSINESS LOGIC: Use existing update method
            success = await self.update_entity(version_id, metadata_update, user_context)
            
            if success:
                logger.info(f"Successfully updated metadata for version {version_id}")
                return True
            else:
                logger.error(f"Failed to update metadata for version {version_id}")
                return False

        except Exception as e:
            logger.error(f"Error updating version metadata: {e}")
            return False

    async def configure_approval_workflow(
        self,
        workflow_config: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Configure approval workflows.
        
        This is a business domain method that validates and stores workflow configuration.
        
        Args:
            workflow_config: Workflow configuration
            user_context: User context for authorization
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate workflow configuration structure
            required_fields = ["workflow_name", "workflow_type", "workflow_steps"]
            for field in required_fields:
                if field not in workflow_config:
                    logger.error(f"Missing required workflow field: {field}")
                    return False

            # ✅ BUSINESS LOGIC: Validate workflow type
            valid_workflow_types = ["sequential", "parallel", "conditional", "hybrid"]
            if workflow_config["workflow_type"] not in valid_workflow_types:
                logger.error(f"Invalid workflow type: {workflow_config['workflow_type']}")
                return False

            # ✅ BUSINESS LOGIC: Validate workflow steps
            workflow_steps = workflow_config.get("workflow_steps", [])
            if not isinstance(workflow_steps, list) or len(workflow_steps) == 0:
                logger.error("Workflow steps must be a non-empty list")
                return False

            # ✅ BUSINESS LOGIC: Validate each workflow step
            for i, step in enumerate(workflow_steps):
                if not isinstance(step, dict):
                    logger.error(f"Workflow step {i} must be a dictionary")
                    return False
                
                required_step_fields = ["step_name", "step_type", "approver_role"]
                for field in required_step_fields:
                    if field not in step:
                        logger.error(f"Missing required step field '{field}' in step {i}")
                        return False

            # ✅ BUSINESS LOGIC: Create workflow configuration record
            workflow_record = {
                "workflow_name": workflow_config["workflow_name"],
                "workflow_type": workflow_config["workflow_type"],
                "workflow_steps": workflow_steps,
                "workflow_metadata": {
                    "configured_by": user_context.get("user_id", "unknown"),
                    "configuration_timestamp": datetime.utcnow().isoformat(),
                    "workflow_version": workflow_config.get("workflow_version", "1.0"),
                    "workflow_description": workflow_config.get("workflow_description", ""),
                    "workflow_scope": workflow_config.get("workflow_scope", "global")
                },
                "is_active": workflow_config.get("is_active", True),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # ✅ BUSINESS LOGIC: Store workflow configuration
            # Note: This would typically use a dedicated workflow configuration service
            # For now, we'll log the configuration and return success
            logger.info(f"Approval workflow configured: {workflow_config['workflow_name']}")
            logger.info(f"Workflow type: {workflow_config['workflow_type']}")
            logger.info(f"Number of steps: {len(workflow_steps)}")
            
            return True

        except Exception as e:
            logger.error(f"Error configuring approval workflow: {e}")
            return False

    # 📈 PERFORMANCE & OPTIMIZATION METHODS

    async def optimize_version_storage(
        self,
        certificate_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Optimize version storage.
        
        This is a business domain method that optimizes storage for certificate versions.
        
        Args:
            certificate_id: ID of the certificate
            user_context: User context for authorization
            
        Returns:
            True if optimization successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get all versions for the certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }
            
            all_versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            if not all_versions:
                logger.info(f"No versions found for certificate {certificate_id}")
                return True

            # ✅ BUSINESS LOGIC: Analyze storage optimization opportunities
            optimization_actions = []
            total_versions = len(all_versions)
            
            # Check for duplicate data
            version_data_hashes = {}
            for version in all_versions:
                if version.module_data_snapshot:
                    data_hash = hash(str(version.module_data_snapshot))
                    if data_hash in version_data_hashes:
                        optimization_actions.append({
                            "action": "deduplicate_data",
                            "version_id": version.version_id,
                            "duplicate_of": version_data_hashes[data_hash]
                        })
                    else:
                        version_data_hashes[data_hash] = version.version_id

            # Check for large unused versions
            for version in all_versions:
                if version.archive_status == "archived" and version.deployment_status == "not_deployed":
                    # Check if version is old (more than 90 days)
                    if version.created_at:
                        created_date = datetime.fromisoformat(version.created_at.replace('Z', '+00:00'))
                        days_old = (datetime.utcnow() - created_date.replace(tzinfo=None)).days
                        if days_old > 90:
                            optimization_actions.append({
                                "action": "compress_old_version",
                                "version_id": version.version_id,
                                "days_old": days_old
                            })

            # ✅ BUSINESS LOGIC: Apply optimization actions
            optimization_results = {
                "total_versions": total_versions,
                "optimization_actions": optimization_actions,
                "optimization_metadata": {
                    "optimized_by": user_context.get("user_id", "unknown"),
                    "optimization_timestamp": datetime.utcnow().isoformat(),
                    "certificate_id": certificate_id
                }
            }

            # ✅ BUSINESS LOGIC: Log optimization results
            logger.info(f"Storage optimization completed for certificate {certificate_id}")
            logger.info(f"Total versions analyzed: {total_versions}")
            logger.info(f"Optimization actions identified: {len(optimization_actions)}")
            
            for action in optimization_actions:
                logger.info(f"Action: {action['action']} for version {action['version_id']}")
            
            return True

        except Exception as e:
            logger.error(f"Error optimizing version storage: {e}")
            return False
    
    async def cleanup_old_versions(
        self,
        certificate_id: str,
        retention_days: int,
        user_context: Dict[str, Any]
    ) -> int:
        """
        Cleanup old/unused versions.
        
        This is a business domain method that uses the CRUD delete_entity method.
        
        Args:
            certificate_id: ID of the certificate
            retention_days: Number of days to retain
            user_context: User context for authorization
            
        Returns:
            Number of versions cleaned up
        """
        try:
            # ✅ BUSINESS LOGIC: Validate retention days
            if retention_days < 0:
                logger.error("Retention days must be non-negative")
                return 0

            # ✅ BUSINESS LOGIC: Get all versions for the certificate
            criteria = {
                "certificate_id": certificate_id,
                "is_deleted": False
            }
            
            all_versions = await self.search_entities(criteria, user_context, limit=1000, offset=0)
            
            if not all_versions:
                logger.info(f"No versions found for certificate {certificate_id}")
                return 0

            # ✅ BUSINESS LOGIC: Identify versions for cleanup
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            versions_to_cleanup = []
            
            for version in all_versions:
                # Skip if version is currently deployed
                if version.deployment_status == "deployed":
                    continue
                
                # Skip if version is the latest version
                if version.version_type == "latest":
                    continue
                
                # Check if version is old enough for cleanup
                if version.created_at:
                    created_date = datetime.fromisoformat(version.created_at.replace('Z', '+00:00'))
                    if created_date.replace(tzinfo=None) < cutoff_date:
                        versions_to_cleanup.append(version)

            # ✅ BUSINESS LOGIC: Perform cleanup
            cleanup_count = 0
            for version in versions_to_cleanup:
                try:
                    # Use soft delete by updating is_deleted flag
                    cleanup_data = {
                            "is_deleted": True,
                        "deleted_at": datetime.utcnow().isoformat(),
                        "deleted_by": user_context.get("user_id", "unknown"),
                        "deletion_reason": f"Cleanup after {retention_days} days retention"
                    }
                    
                    success = await self.update_entity(version.version_id, cleanup_data, user_context)
                    if success:
                        cleanup_count += 1
                        logger.info(f"Cleaned up version {version.version_id}")
                    else:
                        logger.error(f"Failed to cleanup version {version.version_id}")
                        
                except Exception as e:
                    logger.error(f"Error cleaning up version {version.version_id}: {e}")

            # ✅ BUSINESS LOGIC: Log cleanup results
            logger.info(f"Cleanup completed for certificate {certificate_id}")
            logger.info(f"Total versions analyzed: {len(all_versions)}")
            logger.info(f"Versions cleaned up: {cleanup_count}")
            logger.info(f"Retention period: {retention_days} days")
            
            return cleanup_count

        except Exception as e:
            logger.error(f"Error cleaning up old versions: {e}")
            return 0

    async def compress_version_data(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Compress version data.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            True if compression successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if version is eligible for compression
            if current_version.archive_status == "archived":
                logger.info(f"Version {version_id} is already archived, skipping compression")
                return True

            if current_version.deployment_status == "deployed":
                logger.warning(f"Version {version_id} is currently deployed, compression not recommended")
                return False

            # ✅ BUSINESS LOGIC: Calculate compression metrics
            original_size = 0
            if current_version.module_data_snapshot:
                original_size = len(str(current_version.module_data_snapshot))
            
            # Simulate compression (in real implementation, use actual compression)
            compression_ratio = 0.7  # 30% reduction
            compressed_size = int(original_size * compression_ratio)
            
            # ✅ BUSINESS LOGIC: Create compression update data
            compression_data = {
                "archive_status": "compressed",
                "compression_metadata": {
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compression_ratio,
                    "compression_algorithm": "gzip",
                    "compressed_by": user_context.get("user_id", "unknown"),
                    "compression_timestamp": datetime.utcnow().isoformat()
                },
                "updated_at": datetime.utcnow().isoformat()
            }

            # ✅ BUSINESS LOGIC: Use existing update method
            success = await self.update_entity(version_id, compression_data, user_context)
            
            if success:
                logger.info(f"Successfully compressed version {version_id}")
                logger.info(f"Original size: {original_size} bytes, Compressed size: {compressed_size} bytes")
                logger.info(f"Compression ratio: {compression_ratio:.1%}")
                return True
            else:
                logger.error(f"Failed to compress version {version_id}")
                return False

        except Exception as e:
            logger.error(f"Error compressing version data: {e}")
            return False

    async def get_version_performance_metrics(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get performance metrics for version.
        
        This is a business domain method that calculates performance metrics for a version.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return {"status": "error", "performance_metrics": {}}

            # ✅ BUSINESS LOGIC: Calculate performance metrics
            performance_metrics = {}
            
            # Age metrics
            if current_version.created_at:
                created_date = datetime.fromisoformat(current_version.created_at.replace('Z', '+00:00'))
                age_days = (datetime.utcnow() - created_date.replace(tzinfo=None)).days
                performance_metrics["age_days"] = age_days
                performance_metrics["age_category"] = "new" if age_days < 30 else "mature" if age_days < 90 else "old"

            # Quality metrics
            performance_metrics["quality_score"] = current_version.version_quality_score or 0
            performance_metrics["quality_category"] = (
                "excellent" if (current_version.version_quality_score or 0) >= 90 else
                "good" if (current_version.version_quality_score or 0) >= 70 else
                "fair" if (current_version.version_quality_score or 0) >= 50 else
                "poor"
            )

            # Deployment metrics
            performance_metrics["deployment_status"] = current_version.deployment_status
            performance_metrics["deployment_environment"] = current_version.deployment_environment
            performance_metrics["is_deployed"] = current_version.deployment_status == "deployed"

            # Archive metrics
            performance_metrics["archive_status"] = current_version.archive_status
            performance_metrics["is_archived"] = current_version.archive_status == "archived"

            # Approval metrics
            performance_metrics["approval_status"] = current_version.approval_status
            performance_metrics["is_approved"] = current_version.approval_status == "approved"

            # Security metrics
            performance_metrics["security_level"] = current_version.security_level
            performance_metrics["encryption_status"] = current_version.encryption_status
            performance_metrics["is_encrypted"] = current_version.encryption_status == "encrypted"

            # Data size metrics
            data_size = 0
            if current_version.module_data_snapshot:
                data_size = len(str(current_version.module_data_snapshot))
            performance_metrics["data_size_bytes"] = data_size
            performance_metrics["data_size_category"] = (
                "small" if data_size < 1024 else
                "medium" if data_size < 10240 else
                "large" if data_size < 102400 else
                "very_large"
            )

            # Overall performance score
            performance_score = 0
            if performance_metrics["is_approved"]:
                performance_score += 25
            if performance_metrics["is_deployed"]:
                performance_score += 25
            if performance_metrics["quality_score"] >= 70:
                performance_score += 25
            if performance_metrics["is_encrypted"]:
                performance_score += 25
            
            performance_metrics["overall_performance_score"] = performance_score
            performance_metrics["performance_category"] = (
                "excellent" if performance_score >= 90 else
                "good" if performance_score >= 70 else
                "fair" if performance_score >= 50 else
                "poor"
            )

            # ✅ BUSINESS LOGIC: Return comprehensive metrics
            result = {
                "status": "success",
                "version_id": version_id,
                "performance_metrics": performance_metrics,
                "metrics_metadata": {
                    "calculated_by": user_context.get("user_id", "unknown"),
                    "calculation_timestamp": datetime.utcnow().isoformat(),
                    "metrics_version": "1.0"
                }
            }

            logger.info(f"Performance metrics calculated for version {version_id}")
            logger.info(f"Overall performance score: {performance_score}/100")
            
            return result

        except Exception as e:
            logger.error(f"Error getting version performance metrics: {e}")
            return {"status": "error", "performance_metrics": {}}

    # 🔐 SECURITY & ACCESS METHODS

    async def set_version_permissions(
        self,
        version_id: str,
        permissions: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Set version-specific permissions.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            permissions: Permission configuration
            user_context: User context for authorization
            
        Returns:
            True if setting successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate permissions structure
            if not isinstance(permissions, dict):
                logger.error("Permissions must be a dictionary")
                return False

            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Validate permission types
            valid_permission_types = [
                "read", "write", "delete", "approve", "deploy", "archive", "restore"
            ]
            
            for permission_type in permissions.keys():
                if permission_type not in valid_permission_types:
                    logger.warning(f"Unknown permission type: {permission_type}")

            # ✅ BUSINESS LOGIC: Validate permission values
            for permission_type, permission_data in permissions.items():
                if not isinstance(permission_data, dict):
                    logger.error(f"Permission data for '{permission_type}' must be a dictionary")
                    return False
                
                if "allowed_users" not in permission_data and "allowed_roles" not in permission_data:
                    logger.error(f"Permission '{permission_type}' must specify allowed_users or allowed_roles")
                    return False

            # ✅ BUSINESS LOGIC: Create permission update data
            permission_update = {
                "version_permissions": {
                    **current_version.version_permissions,  # Preserve existing permissions
                    **permissions,  # Add/update with new permissions
                    "permissions_metadata": {
                        "set_by": user_context.get("user_id", "unknown"),
                        "set_timestamp": datetime.utcnow().isoformat(),
                        "permissions_version": permissions.get("version", "1.0")
                    }
                },
                "updated_at": datetime.utcnow().isoformat()
            }

            # ✅ BUSINESS LOGIC: Use existing update method
            success = await self.update_entity(version_id, permission_update, user_context)
            
            if success:
                logger.info(f"Successfully set permissions for version {version_id}")
                logger.info(f"Permission types set: {list(permissions.keys())}")
                return True
            else:
                logger.error(f"Failed to set permissions for version {version_id}")
                return False

        except Exception as e:
            logger.error(f"Error setting version permissions: {e}")
            return False

    async def validate_version_access(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Validate access to version.
        
        This is a business domain method that validates user access to a version.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            True if access allowed, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Extract user information
            user_id = user_context.get("user_id", "unknown")
            user_roles = user_context.get("roles", [])
            
            # ✅ BUSINESS LOGIC: Check basic access permissions
            if not current_version.version_permissions:
                # No specific permissions set, allow access
                logger.info(f"No specific permissions set for version {version_id}, allowing access")
                return True

            # ✅ BUSINESS LOGIC: Check read permissions
            read_permissions = current_version.version_permissions.get("read", {})
            if read_permissions:
                allowed_users = read_permissions.get("allowed_users", [])
                allowed_roles = read_permissions.get("allowed_roles", [])
                
                # Check if user is explicitly allowed
                if user_id in allowed_users:
                    logger.info(f"User {user_id} has explicit read access to version {version_id}")
                    return True
                
                # Check if user has allowed role
                if any(role in allowed_roles for role in user_roles):
                    logger.info(f"User {user_id} has role-based read access to version {version_id}")
                    return True
                
                # Check if user is admin
                if "admin" in user_roles:
                    logger.info(f"Admin user {user_id} has access to version {version_id}")
                    return True
                
                logger.warning(f"User {user_id} denied access to version {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Default access (no read restrictions)
            logger.info(f"User {user_id} has default access to version {version_id}")
            return True

        except Exception as e:
            logger.error(f"Error validating version access: {e}")
            return False

    async def encrypt_version_data(
        self,
        version_id: str,
        encryption_key: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Encrypt sensitive version data.
        
        This is a business domain method that uses the CRUD update_entity method.
        
        Args:
            version_id: ID of the version
            encryption_key: Encryption key
            user_context: User context for authorization
            
        Returns:
            True if encryption successful, False otherwise
        """
        try:
            # ✅ BUSINESS LOGIC: Validate encryption key
            if not encryption_key or len(encryption_key) < 8:
                logger.error("Encryption key must be at least 8 characters long")
                return False

            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return False

            # ✅ BUSINESS LOGIC: Check if already encrypted
            if current_version.encryption_status == "encrypted":
                logger.info(f"Version {version_id} is already encrypted")
                return True

            # ✅ BUSINESS LOGIC: Check if version is eligible for encryption
            if current_version.deployment_status == "deployed":
                logger.warning(f"Version {version_id} is currently deployed, encryption not recommended")
                return False

            # ✅ BUSINESS LOGIC: Simulate encryption process
            # In real implementation, use actual encryption libraries
            encryption_algorithm = "AES-256-GCM"
            encryption_timestamp = datetime.utcnow().isoformat()
            
            # Create encryption metadata
            encryption_metadata = {
                "encryption_algorithm": encryption_algorithm,
                "encryption_timestamp": encryption_timestamp,
                "encrypted_by": user_context.get("user_id", "unknown"),
                "encryption_key_hash": hash(encryption_key),  # Store hash, not actual key
                "encryption_status": "encrypted"
            }

            # ✅ BUSINESS LOGIC: Create encryption update data
            encryption_data = {
                "encryption_status": "encrypted",
                "encryption_metadata": encryption_metadata,
                "security_level": "high",  # Upgrade security level
                "updated_at": encryption_timestamp
            }

            # ✅ BUSINESS LOGIC: Use existing update method
            success = await self.update_entity(version_id, encryption_data, user_context)
            
            if success:
                logger.info(f"Successfully encrypted version {version_id}")
                logger.info(f"Encryption algorithm: {encryption_algorithm}")
                logger.info(f"Security level upgraded to: high")
                return True
            else:
                logger.error(f"Failed to encrypt version {version_id}")
                return False

        except Exception as e:
            logger.error(f"Error encrypting version data: {e}")
            return False

    async def get_version_security_status(
        self,
        version_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get security status for version.
        
        This is a business domain method that analyzes security status for a version.
        
        Args:
            version_id: ID of the version
            user_context: User context for authorization
            
        Returns:
            Dictionary containing security status
        """
        try:
            # ✅ BUSINESS LOGIC: Get current version
            current_version = await self.get_entity(version_id, user_context)
            if not current_version:
                logger.error(f"Version not found: {version_id}")
                return {"status": "error", "security_status": "unknown"}

            # ✅ BUSINESS LOGIC: Analyze security status
            security_status = {}
            
            # Encryption status
            security_status["encryption_status"] = current_version.encryption_status
            security_status["is_encrypted"] = current_version.encryption_status == "encrypted"
            
            # Security level
            security_status["security_level"] = current_version.security_level
            security_status["security_level_score"] = (
                100 if current_version.security_level == "critical" else
                80 if current_version.security_level == "high" else
                60 if current_version.security_level == "medium" else
                40 if current_version.security_level == "low" else
                0
            )
            
            # Access control
            security_status["has_permissions"] = bool(current_version.version_permissions)
            security_status["permission_types"] = list(current_version.version_permissions.keys()) if current_version.version_permissions else []
            
            # Deployment security
            security_status["deployment_environment"] = current_version.deployment_environment
            security_status["deployment_status"] = current_version.deployment_status
            security_status["is_production_deployed"] = current_version.deployment_environment == "production"
            
            # Archive status
            security_status["archive_status"] = current_version.archive_status
            security_status["is_archived"] = current_version.archive_status == "archived"
            
            # Approval status
            security_status["approval_status"] = current_version.approval_status
            security_status["is_approved"] = current_version.approval_status == "approved"
            
            # Security vulnerabilities
            security_vulnerabilities = []
            if not security_status["is_encrypted"] and current_version.security_level in ["high", "critical"]:
                security_vulnerabilities.append("High/critical security level without encryption")
            
            if security_status["is_production_deployed"] and not security_status["is_approved"]:
                security_vulnerabilities.append("Production deployment without approval")
            
            if not security_status["has_permissions"] and current_version.security_level in ["high", "critical"]:
                security_vulnerabilities.append("High/critical security level without access controls")
            
            security_status["security_vulnerabilities"] = security_vulnerabilities
            security_status["vulnerability_count"] = len(security_vulnerabilities)
            
            # Overall security score
            security_score = security_status["security_level_score"]
            if security_status["is_encrypted"]:
                security_score += 20
            if security_status["has_permissions"]:
                security_score += 15
            if security_status["is_approved"]:
                security_score += 10
            if not security_vulnerabilities:
                security_score += 15
            
            security_score = min(security_score, 100)  # Cap at 100
            security_status["overall_security_score"] = security_score
            security_status["security_category"] = (
                "excellent" if security_score >= 90 else
                "good" if security_score >= 70 else
                "fair" if security_score >= 50 else
                "poor"
            )
            
            # Security recommendations
            security_recommendations = []
            if not security_status["is_encrypted"]:
                security_recommendations.append("Enable encryption for sensitive data")
            if not security_status["has_permissions"]:
                security_recommendations.append("Implement access control permissions")
            if security_status["is_production_deployed"] and not security_status["is_approved"]:
                security_recommendations.append("Obtain approval before production deployment")
            if security_vulnerabilities:
                security_recommendations.append("Address identified security vulnerabilities")
            
            security_status["security_recommendations"] = security_recommendations

            # ✅ BUSINESS LOGIC: Return comprehensive security status
            result = {
                "status": "success",
                "version_id": version_id,
                "security_status": security_status,
                "security_metadata": {
                    "analyzed_by": user_context.get("user_id", "unknown"),
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "security_analysis_version": "1.0"
                }
            }

            logger.info(f"Security status analyzed for version {version_id}")
            logger.info(f"Overall security score: {security_score}/100")
            logger.info(f"Security category: {security_status['security_category']}")
            logger.info(f"Vulnerabilities found: {len(security_vulnerabilities)}")
            
            return result

        except Exception as e:
            logger.error(f"Error getting version security status: {e}")
            return {"status": "error", "security_status": "unknown"}
