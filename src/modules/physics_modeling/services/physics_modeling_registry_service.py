#!/usr/bin/env python3
"""
Physics Modeling Registry Service

This service provides business logic and orchestration for physics modeling operations
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
    service = PhysicsModelingRegistryService(connection_manager)
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
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository

logger = logging.getLogger(__name__)


class PhysicsModelingRegistryService:
    """
    Service for physics modeling registry business logic and orchestration
    
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
        self.repository = PhysicsModelingRegistryRepository(connection_manager)
        
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
        self.service_name = "physics_modeling_registry"
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
                'allowed_file_types': ['.aasx', '.json', '.yaml', '.step', '.vtk', '.csv'],
                'processing_timeout_minutes': 30,
                'retry_attempts': 3
            },
            'permissions': {
                'create': ['admin', 'user', 'processor', 'engineer'],
                'read': ['admin', 'user', 'processor', 'engineer', 'viewer'],
                'update': ['admin', 'user', 'processor', 'engineer'],
                'delete': ['admin'],
                'execute': ['admin', 'processor', 'engineer']
            },
            'cross_dept_roles': ['admin', 'manager', 'senior_engineer'],
            'org_wide_roles': ['admin', 'system_admin'],
            'business_specific': {
                # Physics modeling specific business rules
                'max_models_per_org': 1000,
                'max_models_per_dept': 100,
                'naming_convention': "Physics_{org_id}_{dept_id}_{timestamp}",
                'compliance_requirements': ["ISO27001", "ASME", "FAA", "AS9100"],
                'physics_categories': ["structural", "thermal", "fluid", "electromagnetic", "acoustic"],
                'solver_types': ["finite_element", "finite_difference", "finite_volume", "boundary_element"],
                'complexity_levels': ["simple", "moderate", "complex", "very_complex"]
            }
        }
    
    async def _initialize_security_context(self) -> Dict[str, Any]:
        """
        Initialize security context for the service.
        
        Returns:
            Dictionary containing security configuration and requirements
        """
        return {
            'service_name': 'PhysicsModelingRegistryService',
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

    # 🚨 CRITICAL: Service Method Decision Framework
    
    # ⚠️ IMPORTANT: Choose the right approach for your service!
    # 
    # There are TWO types of services:
    # 1. BASIC SERVICES: Use generic CRUD methods below (create_entity, update_entity, etc.)
    # 2. POPULATION SERVICES: Use domain-specific population methods (see examples below)
    #
    # ❌ DON'T: Blindly copy-paste generic CRUD methods without understanding your use case
    # ✅ DO: Determine if your service needs to populate tables from data sources
    #
    # 🔍 DECISION FRAMEWORK:
    # Q: How does your table get populated?
    # A1: Users input data through frontend → Use generic CRUD methods below
    # A2: Data comes from external systems/APIs → Use domain-specific population methods
    # A3: Data comes from other services → Use domain-specific integration methods
    # A4: Data comes from file processing → Use domain-specific file handling methods
    #
    # 📋 EXAMPLES OF DOMAIN-SPECIFIC METHODS (replace generic CRUD if needed):
    #
    # For ML Registry Service:
    # - populate_from_graph_registry() - Gets basic graph data from registry
    # - update_training_parameters() - Handles user training input
    # - handle_training_completion() - Handles training results
    #
    # For Graph Registry Service:
    # - add_aasx_graph() - Integrates with AASX processing
    # - add_twin_registry_graph() - Integrates with Twin Registry
    # - add_ai_rag_graph() - Integrates with AI RAG
    #
    # For User Registry Service:
    # - create_user_from_auth() - Creates user from authentication system
    # - update_user_profile() - Updates user profile data
    # - sync_user_permissions() - Syncs with permission systems
    #
    # 🎯 REMEMBER: Generic CRUD methods are for simple user input services.
    #              Domain-specific methods are for services that integrate with data sources.
    
    # ✅ REQUIRED: Core Business Operations
    
    # ⚠️ WARNING: Use these generic CRUD methods ONLY for basic user input services!
    #              For services that integrate with data sources, use domain-specific methods above.
    #
    async def create_entity(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[PhysicsModelingRegistry]:
        """
        Create a new entity with comprehensive business logic validation.
        
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
                        roles=['admin', 'user', 'processor', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="physics_modeling",
                        action="create"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to create physics_modeling_registry")
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
                entity = PhysicsModelingRegistry(**entity_data)
                
                # ✅ REQUIRED: Save to repository
                if not await self.repository.create(entity):
                    logger.error("Failed to save entity to repository")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_modeling_registry_created",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("physics_modeling_registry.created", {
                    "entity_id": getattr(entity, 'id', None),
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully created physics_modeling_registry: {getattr(entity, 'id', 'unknown')}")
                return entity
                
            except Exception as e:
                logger.error(f"Error creating physics_modeling_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="create_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to create physics_modeling_registry: {e}",
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
    ) -> Optional[PhysicsModelingRegistry]:
        """
        Retrieve an entity by ID with authorization check.
        
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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read physics_modeling_registry")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Retrieve from repository
                entity = await self.repository.get_by_id(entity_id)
                if not entity:
                    logger.warning(f"PhysicsModelingRegistry not found: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_modeling_registry_retrieved",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                return entity
                
            except Exception as e:
                logger.error(f"Error retrieving physics_modeling_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="get_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve physics_modeling_registry {entity_id}: {e}",
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
    ) -> List[PhysicsModelingRegistry]:
        """
        Search for entities based on criteria with authorization check.
        
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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to search physics_modeling_registry")
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
                    metric_name="physics_modeling_registry_search_executed",
                    metric_value=len(entities),
                    metadata={"user_id": user_context.get("user_id"), "criteria_count": len(search_criteria)}
                )
                
                logger.info(f"Search returned {len(entities)} results")
                return entities
                
            except Exception as e:
                logger.error(f"Error searching physics_modeling_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="search_entities_error",
                    error_message=str(e),
                    error_details=f"Failed to search physics_modeling_registry: {e}",
                    severity="medium",
                    metadata={"search_criteria": search_criteria, "user_context": user_context}
                )
                return []
    
    # ⚠️ WARNING: Generic CRUD method - customize for your domain if needed!
    #
    async def update_entity(
        self,
        entity_id: str,
        update_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Update an entity with authorization check and validation.
        
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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update physics_modeling_registry")
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
                    logger.error(f"Failed to update physics_modeling_registry: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_modeling_registry_updated",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("physics_modeling_registry.updated", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully updated physics_modeling_registry: {entity_id}")
                return True
            
            except Exception as e:
                logger.error(f"Error updating physics_modeling_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="update_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to update physics_modeling_registry {entity_id}: {e}",
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
        Delete an entity with authorization check.
        
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
                        resource="physics_modeling_registry",
                        action="delete"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to delete physics_modeling_registry")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Delete from repository
                if not await self.repository.delete(entity_id):
                    logger.error(f"Failed to delete physics_modeling_registry: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_modeling_registry_deleted",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("physics_modeling_registry.deleted", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully deleted physics_modeling_registry: {entity_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting physics_modeling_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="delete_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to delete physics_modeling_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False

    # ✅ REQUIRED: Table Population Methods
    
    # 🚨 CRITICAL: Every service MUST implement table population logic, not just CRUD operations!
    # Customize these methods for your specific module's data source and population pattern.
    
    async def register_physics_model(self, user_model_data: Dict[str, Any]) -> Optional[PhysicsModelingRegistry]:
        """
        User registers a new physics model.
        
        Engineers register a new physics model with essential information:
        - Model name, physics type, solver information
        - Core parameters and configuration
        - User and organization details (user_id, org_id, dept_id)
        - Essential fields for model identification
        
        Args:
            user_model_data: Basic physics model data from user input
                - Must include: user_id, org_id, dept_id
                - Optional: owner_team, steward_user_id
                - Physics model details: name, physics_type, solver_type, etc.
            
        Returns:
            Created PhysicsModelingRegistry instance or None if failed
        """
        try:
            # ✅ REQUIRED: Construct user context from user_model_data
            user_context = {
                "user_id": user_model_data.get("user_id"),
                "org_id": user_model_data.get("org_id"), 
                "dept_id": user_model_data.get("dept_id"),
                "owner_team": user_model_data.get("owner_team", "Physics_Modeling_Team"),
                "steward_user_id": user_model_data.get("steward_user_id")
            }
            
            # ✅ REQUIRED: Validate required user context fields
            if not all([user_context["user_id"], user_context["org_id"], user_context["dept_id"]]):
                logger.error("Missing required user context fields: user_id, org_id, dept_id")
                await self.error_tracker.track_error(
                    error_type="missing_user_context",
                    error_message="Missing required user context fields",
                    error_details="user_id, org_id, and dept_id are required in user_model_data",
                    severity="high",
                    metadata={"user_model_data": user_model_data}
                )
                return None
            
            # Prepare comprehensive entity data for database storage
            import uuid
            from datetime import datetime
            
            entity_data = {
                "registry_id": f"physics_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}_{user_model_data.get('physics_type', 'unknown')}",
                "model_name": user_model_data.get('model_name'),
                "physics_type": user_model_data.get('physics_type'),
                "plugin_id": user_model_data.get('plugin_id'),
                "plugin_name": user_model_data.get('plugin_name'),
                "model_type": user_model_data.get('model_type', 'traditional'),
                "model_version": user_model_data.get('model_version', '1.0.0'),
                "model_description": user_model_data.get('model_description'),
                "physics_category": user_model_data.get('physics_category', 'structural'),
                "physics_subcategory": user_model_data.get('physics_subcategory', 'linear_elastic'),
                "physics_domain": user_model_data.get('physics_domain', 'mechanical'),
                "complexity_level": user_model_data.get('complexity_level', 'medium'),
                "physics_version": user_model_data.get('physics_version', '1.0.0'),
                "registry_type": user_model_data.get('registry_type', 'generation'),
                "workflow_source": user_model_data.get('workflow_source', 'structured_data'),
                "solver_type": user_model_data.get('solver_type'),
                "solver_name": user_model_data.get('solver_name'),
                "solver_version": user_model_data.get('solver_version'),
                "solver_parameters": user_model_data.get('solver_parameters', {}),
                "mesh_configuration": user_model_data.get('mesh_configuration', {}),
                "time_integration_scheme": user_model_data.get('time_integration_scheme', 'implicit'),
                "spatial_discretization": user_model_data.get('spatial_discretization', 'first_order'),
                "convergence_criteria": user_model_data.get('convergence_criteria', {}),
                "solver_optimization": user_model_data.get('solver_optimization', {}),
                "governing_equations": user_model_data.get('governing_equations', {}),
                "boundary_conditions": user_model_data.get('boundary_conditions', {}),
                "initial_conditions": user_model_data.get('initial_conditions', {}),
                "material_properties": user_model_data.get('material_properties', {}),
                "physical_constants": user_model_data.get('physical_constants', {}),
                "aasx_integration_id": None,
                "twin_registry_id": None,
                "kg_neo4j_id": None,
                "ai_rag_id": None,
                "federated_learning_id": None,
                "certificate_manager_id": None,
                "integration_status": "pending",
                "overall_health_score": 50,
                "health_status": "unknown",
                "lifecycle_status": "created",
                "lifecycle_phase": "setup",
                "operational_status": "stopped",
                "availability_status": "offline",
                "simulation_status": "pending",
                "validation_status": "pending",
                "convergence_status": "unknown",
                "performance_score": 0.0,
                "accuracy_score": 0.0,
                "computational_efficiency": 0.0,
                "numerical_stability": 0.0,
                "security_level": "internal",
                "access_control_level": "user",
                "encryption_enabled": True,
                "audit_logging_enabled": True,
                "compliance_type": "standard",
                "compliance_status": "pending",
                "compliance_score": 0.0,
                "last_audit_date": None,
                "next_audit_date": None,
                "audit_details": {},
                "security_event_type": "none",
                "threat_assessment": "low",  # Changed from "unknown" to valid enum value
                "security_score": 0.0,
                "last_security_scan": None,
                "security_details": {},
                "performance_trend": "stable",  # Changed from "unknown" to valid enum value
                "optimization_suggestions": {},
                "last_optimization_date": None,
                "enterprise_metrics": {},
                "user_id": user_context.get("user_id"),
                "org_id": user_context.get("org_id"),
                "dept_id": user_context.get("dept_id"),
                "owner_team": user_context.get("owner_team", "Physics_Modeling_Team"),
                "steward_user_id": user_context.get("steward_user_id"),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "activated_at": None,
                "last_accessed_at": datetime.now(),
                "last_modified_at": datetime.now(),
                "registry_config": {},
                "registry_metadata": {},
                "custom_attributes": {},
                "tags": {},
                "relationships": {},
                "dependencies": {},
                "physics_instances": {},
                "results_metadata": {},
                "physics_specific_metrics": {}
            }
            
            # Create physics model using standard entity operation
            return await self.create_entity(entity_data, user_context)
            
        except Exception as e:
            logger.error(f"Failed to register physics model: {str(e)}")
            await self.error_tracker.track_error(
                error_type="register_physics_model_error",
                error_message=str(e),
                error_details=f"Failed to register physics model: {str(e)}",
                severity="medium",
                metadata={"user_context": user_context}
            )
            return None
    
    
    async def populate_simulation_results(self, model_id: str, simulation_data: Dict[str, Any]) -> bool:
        """
        System populates physics model with simulation results.
        
        After simulation completion, populate the model with:
        - Simulation results and performance metrics
        - Raw data and results data paths
        - Enterprise features and compliance data
        - Complete model lifecycle information
        
        Args:
            model_id: ID of the existing physics model to update
            simulation_data: Simulation results and comprehensive data
                - Must include: user_id, org_id, dept_id
                - Simulation results: performance_score, accuracy_score, etc.
                - Physics metrics: mesh_element_count, solver_iteration_count, etc.
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # ✅ REQUIRED: Construct user context from simulation_data
            user_context = {
                "user_id": simulation_data.get("user_id"),
                "org_id": simulation_data.get("org_id"), 
                "dept_id": simulation_data.get("dept_id")
            }
            
            # ✅ REQUIRED: Validate required user context fields
            if not all([user_context["user_id"], user_context["org_id"], user_context["dept_id"]]):
                logger.error("Missing required user context fields: user_id, org_id, dept_id")
                await self.error_tracker.track_error(
                    error_type="missing_user_context",
                    error_message="Missing required user context fields",
                    error_details="user_id, org_id, and dept_id are required in simulation_data",
                    severity="high",
                    metadata={"model_id": model_id, "simulation_data": simulation_data}
                )
                return False
            
            # Prepare update data with simulation results matching schema fields
            update_data = {
                "simulation_status": simulation_data.get('simulation_status', 'completed'),
                "validation_status": simulation_data.get('validation_status', 'passed'),
                "convergence_status": simulation_data.get('convergence_status', 'converged'),
                "performance_score": simulation_data.get('performance_score', 0.0),
                "accuracy_score": simulation_data.get('accuracy_score', 0.0),
                "computational_efficiency": simulation_data.get('computational_efficiency', 0.0),
                "numerical_stability": simulation_data.get('numerical_stability', 0.0),
                "lifecycle_phase": "monitoring",
                "operational_status": "running",
                "availability_status": "online",
                "overall_health_score": simulation_data.get('overall_health_score', 75),
                "health_status": "healthy",
                "results_metadata": json.dumps(simulation_data.get('results_metadata', {})),
                "physics_specific_metrics": json.dumps({
                    "mesh_element_count": simulation_data.get('mesh_element_count', 0),
                    "mesh_quality_metrics": simulation_data.get('mesh_quality_metrics', {}),
                    "solver_iteration_count": simulation_data.get('solver_iteration_count', 0),
                    "convergence_history": simulation_data.get('convergence_history', {}),
                    "physical_constraints_count": simulation_data.get('physical_constraints_count', 0),
                    "boundary_conditions_count": simulation_data.get('boundary_conditions_count', 0),
                    "material_properties_count": simulation_data.get('material_properties_count', 0),
                    "load_cases_count": simulation_data.get('load_cases_count', 0),
                    "analysis_types": simulation_data.get('analysis_types', {})
                }),
                "updated_at": datetime.now(),
                "last_modified_at": datetime.now(),
                "last_accessed_at": datetime.now()
            }
            
            # Update physics model using standard entity operation
            return await self.update_entity(model_id, update_data, user_context)
            
        except Exception as e:
            logger.error(f"Failed to populate simulation results: {str(e)}")
            await self.error_tracker.track_error(
                error_type="populate_simulation_results_error",
                error_message=str(e),
                error_details=f"Failed to populate simulation results: {str(e)}",
                severity="medium",
                metadata={"model_id": model_id, "user_context": user_context}
            )
            return False
    
    # ✅ REQUIRED: Physics Modeling Validation Methods
    
    async def _validate_physics_model_data(self, model_data: Dict[str, Any], user_context: Dict[str, Any], is_update: bool = False) -> bool:
        """
        Validate physics model data for registration and updates.
        
        Args:
            model_data: Physics model data to validate
            user_context: User context for validation
            is_update: Whether this is an update operation
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # ✅ REQUIRED: Basic data validation
            if not model_data:
                logger.error("Model data is empty")
                return False
            
            # ✅ REQUIRED: Required fields for physics models
            required_fields = [
                'model_name', 'physics_type', 'solver_type', 'org_id', 'dept_id', 'user_id'
            ]
            
            for field in required_fields:
                if field not in model_data or model_data[field] is None:
                    logger.error(f"Required field missing: {field}")
                    return False
            
            # ✅ REQUIRED: Physics-specific validation
            physics_categories = self.business_config.get('business_specific', {}).get('physics_categories', [])
            if 'physics_type' in model_data and model_data['physics_type'] not in physics_categories:
                logger.error(f"Invalid physics type: {model_data['physics_type']}")
                return False
            
            solver_types = self.business_config.get('business_specific', {}).get('solver_types', [])
            if 'solver_type' in model_data and model_data['solver_type'] not in solver_types:
                logger.error(f"Invalid solver type: {model_data['solver_type']}")
                return False
            
            # ✅ REQUIRED: Business rule validation
            if not await self._validate_business_rules(model_data, user_context, is_update):
                logger.error("Business rule validation failed")
                return False
            
            # ✅ REQUIRED: User permission validation
            if not await self._validate_user_permissions(model_data, user_context):
                logger.error("User permission validation failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating physics model data: {e}")
            return False

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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read physics_modeling_registry summary")
                        return {"error": "Access denied"}
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    return {"error": "Access denied"}
                
                # ✅ REQUIRED: Get summary from repository
                summary = await self.repository.get_summary()
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="physics_modeling_registry_summary_retrieved",
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
            if 'model_name' in entity_data:
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

async def create_physics_modeling_registry_service(connection_manager: ConnectionManager) -> PhysicsModelingRegistryService:
    """
    Factory function to create and initialize a PhysicsModelingRegistryService instance.
    
    Args:
        connection_manager: Database connection manager
        
    Returns:
        Initialized PhysicsModelingRegistryService instance
        
    Raises:
        Exception: If service initialization fails
    """
    try:
        # Create service instance
        service = PhysicsModelingRegistryService(connection_manager)
        
        # Initialize service
        if not await service.initialize_service():
            raise Exception(f"Failed to initialize {service.service_name}")
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create physics_modeling_registry service: {e}")
        raise


# ✅ REQUIRED: Export the service class and factory
__all__ = ['PhysicsModelingRegistryService', 'create_physics_modeling_registry_service']
