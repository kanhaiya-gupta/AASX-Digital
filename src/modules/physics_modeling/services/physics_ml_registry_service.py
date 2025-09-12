#!/usr/bin/env python3
"""
Physics Modeling ML Registry Service

This service provides business logic and orchestration for physics ML registry operations
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
    service = PhysicsMLRegistryService(connection_manager)
    await service.initialize_service()
    
    # Use service methods
    result = await service.create_entity(data, user_context)
    entities = await service.search_entities(criteria, user_context)
"""

import json
import logging
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
from ..models.physics_ml_registry import PhysicsMLRegistry
from ..repositories.physics_ml_registry_repository import PhysicsMLRegistryRepository

logger = logging.getLogger(__name__)


class PhysicsMLRegistryService:
    """
    Service for physics ML registry business logic and orchestration
    
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
        self.repository = PhysicsMLRegistryRepository(connection_manager)
        
        # ✅ REQUIRED: Engine components for enterprise features
        monitoring_config = MonitoringConfig()
        self.performance_profiler = PerformanceProfiler(monitoring_config)
        self.auth_manager = RoleBasedAccessControl(create_defaults=True)
        self.health_monitor = HealthMonitor(monitoring_config)
        self.metrics_collector = MetricsCollector(monitoring_config)
        self.error_tracker = ErrorTracker(monitoring_config)
        self.event_bus = EventBus()
        
        # ✅ REQUIRED: Business configuration and security context (loaded in initialize)
        self.business_config = {}
        self.security_context = {}
        
        # ✅ REQUIRED: Service metadata
        self.service_name = "physics_ml_registry"
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
                'max_file_size_mb': 100,
                'allowed_file_types': ['.aasx', '.json', '.yaml'],
                'processing_timeout_minutes': 30,
                'retry_attempts': 3
            },
            'permissions': {
                'create': ['admin', 'user', 'processor', 'system'],
                'read': ['admin', 'user', 'processor', 'viewer', 'system'],
                'update': ['admin', 'user', 'processor', 'system'],
                'delete': ['admin', 'system'],
                'execute': ['admin', 'processor', 'system']
            },
            'cross_dept_roles': ['admin', 'manager'],
            'org_wide_roles': ['admin', 'system_admin'],
            'business_specific': {
                # Add your module-specific business rules here
                'max_entities_per_org': 1000,
                'max_entities_per_dept': 100,
                'naming_convention': "MLModel_{org_id}_{dept_id}_{timestamp}",
                'compliance_requirements': ["GDPR", "SOX", "ISO27001"]
            }
        }
    
    async def _initialize_security_context(self) -> Dict[str, Any]:
        """
        Initialize security context for the service.
        
        Returns:
            Dictionary containing security configuration and requirements
        """
        return {
            'service_name': 'PhysicsMLRegistryService',
            'security_level': 'enterprise',
            'audit_enabled': True,
            'encryption_required': True,
            'require_authentication': True,
            'require_authorization': True,
            'default_permissions': ['read', 'write'],
            'multi_tenant': True,
            'dept_isolation': True
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

    # ✅ REQUIRED: Core Business Operations
    
    async def create_entity(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[PhysicsMLRegistry]:
        """
        Create a new ML registry entity with comprehensive business logic validation.
        
        Args:
            entity_data: Data for the new ML registry entity
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
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="physics_modeling",
                        action="create"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to create physics_ml_registry")
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
                entity = PhysicsMLRegistry(**entity_data)
                
                # ✅ REQUIRED: Save to repository
                if not await self.repository.create(entity):
                    logger.error("Failed to save entity to repository")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_ml_registry_created",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("physics_ml_registry.created", {
                    "entity_id": getattr(entity, 'ml_registry_id', None),
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully created physics_ml_registry: {getattr(entity, 'ml_registry_id', 'unknown')}")
                return entity
                
            except Exception as e:
                logger.error(f"Error creating physics_ml_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="create_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to create physics_ml_registry: {e}",
                    severity="medium",
                    metadata={"user_context": user_context}
                )
                return None
    
    async def get_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[PhysicsMLRegistry]:
        """
        Retrieve an ML registry entity by ID with authorization check.
        
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
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="physics_modeling",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read physics_ml_registry")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Retrieve from repository
                entity = await self.repository.get_by_id(entity_id)
                if not entity:
                    logger.warning(f"PhysicsMLRegistry not found: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_ml_registry_retrieved",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                return entity
                
            except Exception as e:
                logger.error(f"Error retrieving physics_ml_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="get_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve physics_ml_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return None
    
    async def search_entities(
        self,
        search_criteria: Dict[str, Any],
        user_context: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[PhysicsMLRegistry]:
        """
        Search for ML registry entities based on criteria with authorization check.
        
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
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="physics_modeling",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to search physics_ml_registry")
                        return []
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return []
                
                # ✅ REQUIRED: Search repository
                entities = await self.repository.search_entities(
                    search_criteria, limit, offset
                )
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_ml_registry_search_executed",
                    metric_value=len(entities),
                    metadata={"user_id": user_context.get("user_id"), "criteria_count": len(search_criteria)}
                )
                
                logger.info(f"Search returned {len(entities)} results")
                return entities
                
            except Exception as e:
                logger.error(f"Error searching physics_ml_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="search_entities_error",
                    error_message=str(e),
                    error_details=f"Failed to search physics_ml_registry: {e}",
                    severity="medium",
                    metadata={"search_criteria": search_criteria, "user_context": user_context}
                )
                return []
    
    async def update_entity(
        self,
        entity_id: str,
        update_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Update an ML registry entity with authorization check and validation.
        
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
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="physics_modeling",
                        action="update"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update physics_ml_registry")
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
                    logger.error(f"Failed to update physics_ml_registry: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_ml_registry_updated",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("physics_ml_registry.updated", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully updated physics_ml_registry: {entity_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error updating physics_ml_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="update_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to update physics_ml_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False
    
    async def delete_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Delete an ML registry entity with authorization check.
        
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
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="physics_modeling",
                        action="delete"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to delete physics_ml_registry")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Delete from repository
                if not await self.repository.delete(entity_id):
                    logger.error(f"Failed to delete physics_ml_registry: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_ml_registry_deleted",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("physics_ml_registry.deleted", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully deleted physics_ml_registry: {entity_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting physics_ml_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="delete_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to delete physics_ml_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False

    # ✅ REQUIRED: Single Population Method for ML Registry
    
    async def populate_from_ml_training_job(self, training_job_data: Dict[str, Any]) -> bool:
        """
        Populate ML registry from completed training job.
        
        This method transforms training job results into ML registry entities
        and stores them in the database using the existing create_entity method.
        
        Args:
            training_job_data: Training job results and metadata
            
        Returns:
            True if population successful, False otherwise
        """
        with self.performance_profiler.profile_context("populate_from_ml_training_job"):
            try:
                logger.info(f"Starting ML registry population from training job: {training_job_data.get('training_job_id', 'unknown')}")
                
                # ✅ REQUIRED: Validate training job data
                if not await self._validate_training_job_data(training_job_data):
                    logger.error("Training job data validation failed")
                    return False
                
                # ✅ REQUIRED: Transform training job data to entity format
                entity_data = await self._transform_training_job_to_entity(training_job_data)
                if not entity_data:
                    logger.error("Failed to transform training job data to entity format")
                    return False
                
                # ✅ REQUIRED: Create user context for the training job
                user_context = await self._create_training_job_user_context(training_job_data)
                if not user_context:
                    logger.error("Failed to create user context for training job")
                    return False
                
                # ✅ REQUIRED: Create entity using existing create_entity method
                entity = await self.create_entity(entity_data, user_context)
                if not entity:
                    logger.error("Failed to create ML registry entity from training job")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_ml_registry_populated_from_training_job",
                    metric_value=1,
                    metadata={
                        "training_job_id": training_job_data.get("training_job_id"),
                        "ml_model_type": entity_data.get("ml_model_type"),  # Use correct field name
                        "model_name": entity_data.get("model_name")
                    }
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("physics_ml_registry.populated_from_training_job", {
                    "training_job_id": training_job_data.get("training_job_id"),
                    "entity_id": getattr(entity, 'ml_registry_id', None),
                    "ml_model_type": entity_data.get("ml_model_type"),  # Use correct field name
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully populated ML registry from training job: {training_job_data.get('training_job_id')}")
                return True
                
            except Exception as e:
                logger.error(f"Error populating ML registry from training job: {e}")
                await self.error_tracker.track_error(
                    error_type="populate_from_training_job_error",
                    error_message=str(e),
                    error_details=f"Failed to populate ML registry from training job: {e}",
                    severity="high",
                    metadata={"training_job_data": training_job_data}
                )
                return False
    
    async def _validate_training_job_data(self, training_job_data: Dict[str, Any]) -> bool:
        """
        Validate training job data before processing.
        
        Args:
            training_job_data: Training job data to validate
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # ✅ REQUIRED: Basic data validation
            if not training_job_data:
                logger.error("Training job data is empty")
                return False
            
            # ✅ REQUIRED: Required fields validation
            required_fields = [
                "training_job_id",
                "ml_model_type",  # Use correct field name
                "model_name",
                "model_version",
                "training_status",
                "training_started_at",  # Use correct field name
                "training_completed_at",  # Use correct field name
                "created_by"  # Required for user_id
            ]
            
            for field in required_fields:
                if field not in training_job_data or training_job_data[field] is None:
                    logger.error(f"Required field missing in training job data: {field}")
                    return False
            
            # ✅ REQUIRED: Model type specific validation
            ml_model_type = training_job_data.get("ml_model_type")
            if not await self._validate_model_type_specific_data(training_job_data, ml_model_type):
                logger.error(f"Model type specific validation failed for: {ml_model_type}")
                return False
            
            # ✅ REQUIRED: Training status validation
            training_status = training_job_data.get("training_status")
            if training_status not in ["completed", "successful", "finished"]:
                logger.warning(f"Training job status is not completed: {training_status}")
                # Still allow processing for non-completed jobs if needed
            
            # ✅ REQUIRED: Validate user context fields
            created_by = training_job_data.get("created_by")
            if not created_by:
                logger.error("Training job data missing required 'created_by' field")
                return False
            
            # ✅ REQUIRED: Validate physics domain (should have default if not provided)
            physics_domain = training_job_data.get("physics_domain", "mechanical")
            valid_physics_domains = ["mechanical", "electrical", "thermal", "fluid", "electromagnetic", "quantum", "multi_domain"]
            if physics_domain not in valid_physics_domains:
                logger.warning(f"Invalid physics domain: {physics_domain}, using default 'mechanical'")
                training_job_data["physics_domain"] = "mechanical"
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating training job data: {e}")
            return False
    
    async def _validate_model_type_specific_data(self, training_job_data: Dict[str, Any], ml_model_type: str) -> bool:
        """
        Validate model type specific data based on the comprehensive reference.
        
        Args:
            training_job_data: Training job data to validate
            ml_model_type: Type of ML model (pinn, neural_ode, graph_neural_network, etc.)
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            if ml_model_type == "pinn":
                return await self._validate_pinn_data(training_job_data)
            elif ml_model_type == "neural_ode":
                return await self._validate_nn_data(training_job_data)
            elif ml_model_type == "graph_neural_network":
                return await self._validate_gnn_data(training_job_data)
            elif ml_model_type == "transformer":
                return await self._validate_transformer_data(training_job_data)
            elif ml_model_type == "reinforcement_learning":
                return await self._validate_rl_data(training_job_data)
            elif ml_model_type == "hybrid":
                return await self._validate_hybrid_data(training_job_data)
            else:
                logger.warning(f"Unknown ML model type: {ml_model_type}, skipping specific validation")
                return True
                
        except Exception as e:
            logger.error(f"Error in model type specific validation: {e}")
            return False
    
    async def _validate_pinn_data(self, training_job_data: Dict[str, Any]) -> bool:
        """Validate PINN specific data."""
        try:
            required_fields = ["physics_constraints", "physics_equations", "collocation_points"]
            for field in required_fields:
                if field not in training_job_data:
                    logger.error(f"PINN required field missing: {field}")
                    return False
            
            # Check physics constraints
            physics_constraints = training_job_data.get("physics_constraints", {})
            if not physics_constraints.get("conservation_laws") or not physics_constraints.get("boundary_conditions"):
                logger.error("PINN physics constraints incomplete")
                return False
            
            # Check collocation points
            collocation_points = training_job_data.get("collocation_points", {})
            if not collocation_points.get("total_points") or not collocation_points.get("sampling_strategy"):
                logger.error("PINN collocation points incomplete")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating PINN data: {e}")
            return False
    
    async def _validate_nn_data(self, training_job_data: Dict[str, Any]) -> bool:
        """Validate traditional neural network data."""
        try:
            required_fields = ["model_structure", "training_parameters"]
            for field in required_fields:
                if field not in training_job_data:
                    logger.error(f"NN required field missing: {field}")
                    return False
            
            # Check model structure
            model_structure = training_job_data.get("model_structure", {})
            if not model_structure.get("hidden_layers"):
                logger.error("NN model structure incomplete")
                return False
            
            # Check training parameters
            training_params = training_job_data.get("training_parameters", {})
            if not training_params.get("learning_rate") or not training_params.get("epochs"):
                logger.error("NN training parameters incomplete")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating NN data: {e}")
            return False
    
    async def _validate_gnn_data(self, training_job_data: Dict[str, Any]) -> bool:
        """Validate GNN specific data."""
        try:
            required_fields = ["graph_structure", "gnn_architecture"]
            for field in required_fields:
                if field not in training_job_data:
                    logger.error(f"GNN required field missing: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating GNN data: {e}")
            return False
    
    async def _validate_transformer_data(self, training_job_data: Dict[str, Any]) -> bool:
        """Validate Transformer specific data."""
        try:
            required_fields = ["transformer_architecture", "attention_mechanism"]
            for field in required_fields:
                if field not in training_job_data:
                    logger.error(f"Transformer required field missing: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating Transformer data: {e}")
            return False
    
    async def _validate_rl_data(self, training_job_data: Dict[str, Any]) -> bool:
        """Validate Reinforcement Learning specific data."""
        try:
            required_fields = ["rl_architecture", "environment_config"]
            for field in required_fields:
                if field not in training_job_data:
                    logger.error(f"RL required field missing: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating RL data: {e}")
            return False
    
    async def _validate_hybrid_data(self, training_job_data: Dict[str, Any]) -> bool:
        """Validate Hybrid model specific data."""
        try:
            required_fields = ["hybrid_components", "integration_strategy"]
            for field in required_fields:
                if field not in training_job_data:
                    logger.error(f"Hybrid model required field missing: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating Hybrid model data: {e}")
            return False
    
    async def _transform_training_job_to_entity(self, training_job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform training job data to ML registry entity format.
        
        Args:
            training_job_data: Training job data to transform
            
        Returns:
            Transformed entity data or None if transformation failed
        """
        try:
            # ✅ REQUIRED: Generate unique ML registry ID
            ml_registry_id = await self._generate_ml_registry_id(training_job_data)
            
            # ✅ REQUIRED: Extract basic information
            entity_data = {
                "ml_registry_id": ml_registry_id,
                "org_id": training_job_data.get("org_id", "ORG_DEFAULT"),
                "dept_id": training_job_data.get("dept_id", "DEPT_DEFAULT"),
                "model_name": training_job_data.get("model_name"),
                "model_version": training_job_data.get("model_version"),
                "model_type": training_job_data.get("model_type", "ml"),  # Default to "ml"
                "ml_model_type": training_job_data.get("ml_model_type", "pinn"),  # Use correct field
                "model_framework": training_job_data.get("model_framework", "Unknown"),
                "model_architecture": training_job_data.get("model_architecture", "Unknown"),
                "training_data_source": training_job_data.get("training_data_source", "Unknown"),
                "training_job_id": training_job_data.get("training_job_id"),
                "training_started_at": training_job_data.get("training_started_at"),  # Use correct field name
                "training_completed_at": training_job_data.get("training_completed_at"),  # Use correct field name
                "training_status": training_job_data.get("training_status"),
                "deployment_status": "not_deployed",  # Use correct enum value
                "user_id": training_job_data.get("created_by", "system"),  # Required field
                "created_by": training_job_data.get("created_by", "system"),  # Required field
                "updated_by": training_job_data.get("created_by", "system"),  # Required field
                "physics_domain": training_job_data.get("physics_domain", "mechanical"),  # Required field with default
                "lifecycle_phase": training_job_data.get("lifecycle_phase", "development"),  # Required field with default
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "custom_attributes": {}  # Initialize as empty dict, not string
            }
            
            # ✅ REQUIRED: Extract model-specific data
            ml_model_type = training_job_data.get("ml_model_type")
            if ml_model_type == "pinn":
                entity_data.update(await self._extract_pinn_data(training_job_data))
            elif ml_model_type == "neural_ode":
                entity_data.update(await self._extract_nn_data(training_job_data))
            elif ml_model_type == "graph_neural_network":
                entity_data.update(await self._extract_gnn_data(training_job_data))
            elif ml_model_type == "transformer":
                entity_data.update(await self._extract_transformer_data(training_job_data))
            elif ml_model_type == "reinforcement_learning":
                entity_data.update(await self._extract_rl_data(training_job_data))
            elif ml_model_type == "hybrid":
                entity_data.update(await self._extract_hybrid_data(training_job_data))
            
            # ✅ REQUIRED: Extract common metrics and metadata
            entity_data.update(await self._extract_common_data(training_job_data))
            
            logger.info(f"Successfully transformed training job data to entity format for: {ml_registry_id}")
            return entity_data
            
        except Exception as e:
            logger.error(f"Error transforming training job data to entity: {e}")
            return None
    
    async def _generate_ml_registry_id(self, training_job_data: Dict[str, Any]) -> str:
        """Generate unique ML registry ID."""
        try:
            model_type = training_job_data.get("model_type", "UNKNOWN")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_suffix = str(hash(training_job_data.get("training_job_id", "")) % 10000).zfill(4)
            
            return f"{model_type.upper()}_{timestamp}_{random_suffix}"
            
        except Exception as e:
            logger.error(f"Error generating ML registry ID: {e}")
            return f"ML_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(training_job_data)) % 10000}"
    
    async def _extract_pinn_data(self, training_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract PINN specific data."""
        return {
            "physics_constraints": training_job_data.get("physics_constraints", {}),
            "physics_equations": training_job_data.get("physics_equations", {}),
            "collocation_points": training_job_data.get("collocation_points", {}),
            "physics_validation": training_job_data.get("physics_validation", {}),
            "description": training_job_data.get("description", "Physics-Informed Neural Network"),
            "tags": {"type": "pinn", "category": "physics_informed"},  # Use dict format
            "metadata": {
                "physics_domain": training_job_data.get("metadata", {}).get("physics_domain", "unknown"),
                "simulation_type": training_job_data.get("metadata", {}).get("simulation_type", "unknown"),
                "pinn_specific": training_job_data.get("metadata", {}).get("pinn_specific", {})
            }
        }
    
    async def _extract_nn_data(self, training_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract traditional neural network data."""
        return {
            "model_structure": training_job_data.get("model_structure", {}),
            "data_preprocessing": training_job_data.get("data_preprocessing", {}),
            "description": training_job_data.get("description", "Traditional Neural Network"),
            "tags": {"type": "neural_network", "category": "ml"},  # Use dict format
            "metadata": {
                "physics_domain": training_job_data.get("metadata", {}).get("physics_domain", "unknown"),
                "simulation_type": training_job_data.get("metadata", {}).get("simulation_type", "unknown")
            }
        }
    
    async def _extract_gnn_data(self, training_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GNN specific data."""
        return {
            "graph_structure": training_job_data.get("graph_structure", {}),
            "gnn_architecture": training_job_data.get("gnn_architecture", {}),
            "description": training_job_data.get("description", "Graph Neural Network"),
            "tags": {"type": "gnn", "category": "graph_neural_network"},  # Use dict format
            "metadata": {
                "physics_domain": training_job_data.get("metadata", {}).get("physics_domain", "unknown"),
                "simulation_type": training_job_data.get("metadata", {}).get("simulation_type", "unknown")
            }
        }
    
    async def _extract_transformer_data(self, training_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Transformer specific data."""
        return {
            "transformer_architecture": training_job_data.get("transformer_architecture", {}),
            "attention_mechanism": training_job_data.get("attention_mechanism", {}),
            "description": training_job_data.get("description", "Transformer Model"),
            "tags": {"type": "transformer", "category": "attention"},  # Use dict format
            "metadata": {
                "physics_domain": training_job_data.get("metadata", {}).get("physics_domain", "unknown"),
                "simulation_type": training_job_data.get("metadata", {}).get("simulation_type", "unknown")
            }
        }
    
    async def _extract_rl_data(self, training_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Reinforcement Learning specific data."""
        return {
            "rl_architecture": training_job_data.get("rl_architecture", {}),
            "environment_config": training_job_data.get("environment_config", {}),
            "reward_structure": training_job_data.get("reward_structure", {}),
            "description": training_job_data.get("description", "Reinforcement Learning Model"),
            "tags": {"type": "reinforcement_learning", "category": "rl"},  # Use dict format
            "metadata": {
                "physics_domain": training_job_data.get("metadata", {}).get("physics_domain", "unknown"),
                "simulation_type": training_job_data.get("metadata", {}).get("simulation_type", "unknown")
            }
        }
    
    async def _extract_hybrid_data(self, training_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Hybrid model specific data."""
        return {
            "hybrid_components": training_job_data.get("hybrid_components", {}),
            "integration_strategy": training_job_data.get("integration_strategy", {}),
            "description": training_job_data.get("description", "Hybrid ML Model"),
            "tags": {"type": "hybrid", "category": "multi_model"},  # Use dict format
            "metadata": {
                "physics_domain": training_job_data.get("metadata", {}).get("physics_domain", "unknown"),
                "simulation_type": training_job_data.get("metadata", {}).get("simulation_type", "unknown")
            }
        }
    
    async def _extract_common_data(self, training_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract common data fields."""
        return {
            "training_parameters": training_job_data.get("training_parameters", {}),
            "model_metrics": training_job_data.get("model_metrics", {}),
            "model_file_path": training_job_data.get("model_file_path", ""),
            "model_file_size": training_job_data.get("model_file_size", 0),
            "model_hash": training_job_data.get("model_hash", ""),
            "training_duration_minutes": training_job_data.get("training_duration_minutes", 0)
        }
    
    async def _create_training_job_user_context(self, training_job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create user context for the training job.
        
        Args:
            training_job_data: Training job data
            
        Returns:
            User context dictionary or None if creation failed
        """
        try:
            # ✅ REQUIRED: Extract user information from training job
            user_id = training_job_data.get("created_by")
            if not user_id:
                logger.error("Training job data missing required 'created_by' field for user_id")
                return None
                
            org_id = training_job_data.get("org_id", "ORG_DEFAULT")
            dept_id = training_job_data.get("dept_id", "DEPT_DEFAULT")
            
            # ✅ REQUIRED: Create user context with appropriate permissions
            user_context = {
                "user_id": user_id,  # This is critical - never missing
                "org_id": org_id,
                "dept_id": dept_id,
                "roles": ["processor", "system"],  # Training jobs typically run with processor permissions
                "permissions": ["create", "read", "write"],
                "session_id": f"training_job_{training_job_data.get('training_job_id', 'unknown')}",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Created user context for training job: {user_id} in {org_id}/{dept_id}")
            return user_context
            
        except Exception as e:
            logger.error(f"Error creating user context for training job: {e}")
            return None

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
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="physics_modeling",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read physics_ml_registry summary")
                        return {"error": "Access denied"}
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    return {"error": "Access denied"}
                
                # ✅ REQUIRED: Get summary from repository
                summary = await self.repository.get_statistics()
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_ml_registry_summary_retrieved",
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
            
            # ✅ REQUIRED: Required field validation
            required_fields = self.business_config.get('required_fields', [])
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
            
            # Check file size limits
            if 'file_size' in entity_data:
                max_size = self.business_config.get('default_rules', {}).get('max_file_size_mb', 100)
                if entity_data['file_size'] > max_size * 1024 * 1024:  # Convert MB to bytes
                    logger.error(f"File size exceeds limit: {entity_data['file_size']} bytes")
                    return False
            
            # Check naming conventions
            if 'name' in entity_data:
                naming_pattern = self.business_config.get('business_specific', {}).get('naming_convention', '')
                # Implement naming pattern validation here
                pass
            
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


# ✅ REQUIRED: Service Factory Function

async def create_physics_ml_registry_service(connection_manager: ConnectionManager) -> PhysicsMLRegistryService:
    """
    Factory function to create and initialize a PhysicsMLRegistryService instance.
    
    Args:
        connection_manager: Database connection manager
        
    Returns:
        Initialized PhysicsMLRegistryService instance
        
    Raises:
        Exception: If service initialization fails
    """
    try:
        # Create service instance
        service = PhysicsMLRegistryService(connection_manager)
        
        # Initialize service
        if not await service.initialize_service():
            raise Exception(f"Failed to initialize {service.service_name}")
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create physics_ml_registry service: {e}")
        raise


# ✅ REQUIRED: Export the service class and factory
__all__ = ['PhysicsMLRegistryService', 'create_physics_ml_registry_service']
