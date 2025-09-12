#!/usr/bin/env python3
"""
AI RAG Operations Service

This service provides business logic and orchestration for AI RAG operations
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
    service = AIRagOperationsService(connection_manager)
    await service.initialize_service()
    
    # Use service methods
    result = await service.create_entity(data, user_context)
    entities = await service.search_entities(criteria, user_context)
    
    # Populate operations table from multiple sources
    success = await service.populate_operations_table(
        frontend_data=user_interaction_data,
        registry_data=registry_information,
        system_data=processing_results
    )
"""

import json
import logging
import hashlib
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
from ..models.ai_rag_operations import AIRagOperations
from ..repositories.ai_rag_operations_repository import AIRagOperationsRepository

logger = logging.getLogger(__name__)


class AIRagOperationsService:
    """
    Service for AI RAG operations business logic and orchestration
    
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
        self.repository = AIRagOperationsRepository(connection_manager)
        
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
        self.service_name = "ai_rag_operations"
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
                'create': ['admin', 'user', 'processor'],
                'read': ['admin', 'user', 'processor', 'viewer'],
                'update': ['admin', 'user', 'processor'],
                'delete': ['admin'],
                'execute': ['admin', 'processor']
            },
            'cross_dept_roles': ['admin', 'manager'],
            'org_wide_roles': ['admin', 'system_admin'],
            'business_specific': {
                # Add your module-specific business rules here
                'max_entities_per_org': 1000,
                'max_entities_per_dept': 100,
                'naming_convention': "Operation_{org_id}_{dept_id}_{timestamp}",
                'compliance_requirements': ["GDPR", "SOX", "ISO27001"]
            },
            'required_fields': ['operation_id', 'registry_id', 'operation_type', 'timestamp', 'user_id', 'org_id', 'dept_id']
        }
    
    async def _initialize_security_context(self) -> Dict[str, Any]:
        """
        Initialize security context for the service.
        
        Returns:
            Dictionary containing security configuration and requirements
        """
        return {
            'service_name': 'AIRagOperationsService',
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
    ) -> Optional[AIRagOperations]:
        """
        Create a new AI RAG operations entity with comprehensive business logic validation.
        
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
                        resource="ai_rag",
                        action="create"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to create ai_rag_operations")
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
                entity = AIRagOperations(**entity_data)
                
                # ✅ REQUIRED: Save to repository
                if not await self.repository.create(entity):
                    logger.error("Failed to save entity to repository")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_operations_created",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ai_rag_operations.created", {
                    "entity_id": getattr(entity, 'operation_id', None),
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully created ai_rag_operations: {getattr(entity, 'operation_id', 'unknown')}")
                return entity
                
            except Exception as e:
                logger.error(f"Error creating ai_rag_operations: {e}")
                await self.error_tracker.track_error(
                    error_type="create_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to create ai_rag_operations: {e}",
                    severity="medium",
                    metadata={"user_context": user_context}
                )
                return None

    async def get_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[AIRagOperations]:
        """
        Retrieve an AI RAG operations entity by ID with authorization check.
        
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
                        resource="ai_rag",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read ai_rag_operations")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Retrieve from repository
                entity = await self.repository.get_by_id(entity_id)
                if not entity:
                    logger.warning(f"AI RAG Operations not found: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_operations_retrieved",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                return entity
                
            except Exception as e:
                logger.error(f"Error retrieving ai_rag_operations: {e}")
                await self.error_tracker.track_error(
                    error_type="get_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve ai_rag_operations {entity_id}: {e}",
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
    ) -> List[AIRagOperations]:
        """
        Search for AI RAG operations entities based on criteria with authorization check.
        
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
                        resource="ai_rag",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to search ai_rag_operations")
                        return []
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return []
                
                # ✅ REQUIRED: Search repository
                entities = await self.repository.search(
                    search_criteria, limit, offset
                )
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_operations_search_executed",
                    metric_value=len(entities),
                    metadata={"user_id": user_context.get("user_id"), "criteria_count": len(search_criteria)}
                )
                
                logger.info(f"Search returned {len(entities)} results")
                return entities
                
            except Exception as e:
                logger.error(f"Error searching ai_rag_operations: {e}")
                await self.error_tracker.track_error(
                    error_type="search_entities_error",
                    error_message=str(e),
                    error_details=f"Failed to search ai_rag_operations: {e}",
                    severity="medium",
                    metadata={"search_criteria": search_criteria, "user_context": user_context}
                )
                return []

    async def get_all(
        self,
        user_context: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[AIRagOperations]:
        """
        Get all AI RAG operations with pagination and authorization.
        
        Args:
            user_context: User context for authorization and audit
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of AI RAG operations or empty list if none found
        """
        with self.performance_profiler.profile_context("get_all"):
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
                        resource="ai_rag",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read ai_rag_operations")
                        return []
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return []
                
                # ✅ REQUIRED: Get all entities from repository
                operations = await self.repository.get_all(limit=limit, offset=offset)
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_operations_retrieved_all",
                    metric_value=len(operations),
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ai_rag_operations.retrieved_all", {
                    "count": len(operations),
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully retrieved {len(operations)} ai_rag_operations")
                return operations
                
            except Exception as e:
                logger.error(f"Error retrieving all ai_rag_operations: {e}")
                await self.error_tracker.track_error(
                    error_type="get_all_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve all ai_rag_operations: {e}",
                    severity="medium",
                    metadata={"user_context": user_context}
                )
                return []
    
    async def update_entity(
        self,
        entity_id: str,
        update_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[AIRagOperations]:
        """
        Update an AI RAG operations entity with authorization check and validation.
        
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
                        resource="ai_rag",
                        action="update"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update ai_rag_operations")
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
                    logger.error(f"Failed to update ai_rag_operations: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Get updated entity
                updated_entity = await self.repository.get_by_id(entity_id)
                if not updated_entity:
                    logger.error(f"Failed to retrieve updated ai_rag_operations: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_operations_updated",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ai_rag_operations.updated", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully updated ai_rag_operations: {entity_id}")
                return updated_entity
                
            except Exception as e:
                logger.error(f"Error updating ai_rag_operations: {e}")
                await self.error_tracker.track_error(
                    error_type="update_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to update ai_rag_operations {entity_id}: {e}",
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
        Delete an AI RAG operations entity with authorization check.
        
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
                        resource="ai_rag",
                        action="delete"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to delete ai_rag_operations")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Delete from repository
                if not await self.repository.delete(entity_id):
                    logger.error(f"Failed to delete ai_rag_operations: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_operations_deleted",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ai_rag_operations.deleted", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully deleted ai_rag_operations: {entity_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting ai_rag_operations: {e}")
                await self.error_tracker.track_error(
                    error_type="delete_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to delete ai_rag_operations {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False

    # 🚀 STAGE 2: Domain-Specific Business Logic Methods
    
    async def populate_operations_table(
        self,
        frontend_data: Optional[Dict[str, Any]] = None,
        registry_data: Optional[Dict[str, Any]] = None,
        system_data: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Populate AI RAG operations table from multiple data sources.
        
        This method intelligently combines data from:
        1. Frontend user interactions (queries, responses, sessions)
        2. Registry table data (metadata, configurations, status)
        3. System processing results (AASX processing, embeddings, graphs)
        
        Args:
            frontend_data: User interaction data from frontend
                - user_id: User identifier
                - query_text: User query text
                - response_text: System response text
                - session_data: Session information
                - user_preferences: User settings and preferences
                
            registry_data: Data from ai_rag_registry table
                - registry_id: Registry identifier
                - registry_metadata: Registry metadata and status
                - integration_info: Integration information
                - workflow_config: Workflow configurations
                
            system_data: System processing results
                - aasx_processing: AASX processing outcomes
                - document_extraction: Document extraction results
                - embedding_generation: Embedding generation results
                - graph_metadata: Graph metadata updates
                
            user_context: User context for authorization and audit
                
        Returns:
            True if population successful, False otherwise
        """
        try:
            logger.info("🚀 Starting AI RAG operations table population from multiple sources")
            
            # ✅ REQUIRED: Validate organizational hierarchy
            org_id, dept_id = await self._extract_org_hierarchy(frontend_data, registry_data, system_data)
            if not org_id or not dept_id:
                logger.error("Missing org_id or dept_id - cannot proceed with operations population")
                return False
            
            # ✅ REQUIRED: Extract and validate registry data
            registry_id = await self._extract_registry_id(registry_data, system_data)
            if not registry_id:
                logger.error("Missing registry_id - cannot proceed with operations population")
                return False
            
            # ✅ REQUIRED: Generate operation ID
            operation_id = await self._generate_operation_id(org_id, dept_id)
            
            # ✅ REQUIRED: Build comprehensive operation data
            operation_data = await self._build_operation_data(
                operation_id=operation_id,
                registry_id=registry_id,
                frontend_data=frontend_data,
                registry_data=registry_data,
                system_data=system_data,
                org_id=org_id,
                dept_id=dept_id
            )
            
            # ✅ REQUIRED: Create operation entity
            operation_entity = AIRagOperations(**operation_data)
            
            # ✅ REQUIRED: Save to repository
            if not await self.repository.create(operation_entity):
                logger.error(f"Failed to save operation to repository: {operation_id}")
                return False
            
            # ✅ REQUIRED: Record metrics
            await self.metrics_collector.record_metric(
                metric_name="ai_rag_operations_populated",
                metric_value=1,
                metadata={
                    "operation_id": operation_id,
                    "registry_id": registry_id,
                    "org_id": org_id,
                    "dept_id": dept_id
                }
            )
            
            # ✅ REQUIRED: Publish event
            await self.event_bus.publish("ai_rag_operations.populated", {
                "operation_id": operation_id,
                "registry_id": registry_id,
                "user_context": user_context,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ Successfully populated AI RAG operations table: {operation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error populating AI RAG operations table: {e}")
            await self.error_tracker.track_error(
                error_type="populate_operations_error",
                error_message=str(e),
                error_details=f"Failed to populate operations table: {e}",
                severity="high",
                metadata={
                    "frontend_data": frontend_data,
                    "registry_data": registry_data,
                    "system_data": system_data
                }
            )
            return False

    async def populate_query_operation(
        self,
        user_query: str,
        ai_response: str,
        session_data: Dict[str, Any],
        user_context: Dict[str, Any],
        registry_id: str
    ) -> bool:
        """
        Populate operations table for user query interactions.
        
        Args:
            user_query: User's query text
            ai_response: AI-generated response
            session_data: Session information (start, end, duration)
            user_context: User context and permissions
            registry_id: Associated registry ID
            
        Returns:
            True if operation created successfully
        """
        try:
            logger.info(f"🔍 Creating query operation for user {user_context.get('user_id')}")
            
            # Build frontend data structure
            frontend_data = {
                "user_id": user_context.get("user_id"),
                "query_text": user_query,
                "response_text": ai_response,
                "session_data": {
                    "session_id": session_data.get("session_id"),
                    "start_time": session_data.get("start_time"),
                    "end_time": session_data.get("end_time"),
                    "duration_ms": session_data.get("duration_ms")
                },
                "user_preferences": {
                    "similarity_threshold": user_context.get("similarity_threshold", 0.85),
                    "confidence_score": user_context.get("confidence_score", 0.9)
                },
                "org_id": user_context.get("org_id"),
                "dept_id": user_context.get("dept_id")
            }
            
            # Ensure org_id and dept_id are available
            if not frontend_data.get("org_id") or not frontend_data.get("dept_id"):
                logger.error("Missing org_id or dept_id in user_context")
                return False
            
            # Build system data for query processing
            system_data = {
                "processing_info": {
                    "start_time": session_data.get("start_time"),
                    "end_time": session_data.get("end_time"),
                    "duration_ms": session_data.get("duration_ms")
                },
                "quality_metrics": {
                    "response_relevance": user_context.get("response_relevance", 0.9),
                    "query_complexity": self._calculate_query_complexity(user_query),
                    "response_length": len(ai_response)
                }
            }
            
            # Populate operations table
            success = await self.populate_operations_table(
                frontend_data=frontend_data,
                registry_data={"registry_id": registry_id},
                system_data=system_data,
                user_context=user_context
            )
            
            if success:
                logger.info(f"✅ Query operation created successfully for user {user_context.get('user_id')}")
                return True
            else:
                logger.error(f"❌ Failed to create query operation for user {user_context.get('user_id')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating query operation: {e}")
            await self.error_tracker.track_error(
                error_type="query_operation_error",
                error_message=str(e),
                error_details=f"Failed to create query operation: {e}",
                severity="medium",
                metadata={"user_context": user_context, "registry_id": registry_id}
            )
            return False

    async def populate_embedding_operation(
        self,
        embedding_data: Dict[str, Any],
        source_documents: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        registry_id: str
    ) -> bool:
        """
        Populate operations table for embedding generation operations.
        
        Args:
            embedding_data: Embedding generation results
            source_documents: Source documents used for embedding
            user_context: User context and permissions
            registry_id: Associated registry ID
            
        Returns:
            True if operation created successfully
        """
        try:
            logger.info(f"🧠 Creating embedding operation for registry {registry_id}")
            
            # Build system data for embedding generation
            system_data = {
                "embedding_generation": {
                    "embedding_id": embedding_data.get("embedding_id"),
                    "vector_data": embedding_data.get("vector_data"),
                    "model": embedding_data.get("model", "text-embedding-ada-002"),
                    "dimensions": embedding_data.get("dimensions", 1536),
                    "quality_score": embedding_data.get("quality_score", 0.9),
                    "provider": embedding_data.get("provider", "OpenAI"),
                    "parameters": embedding_data.get("parameters", {}),
                    "timestamp": datetime.now().isoformat(),
                    "duration_ms": embedding_data.get("duration_ms", 0),
                    "cost": embedding_data.get("cost", 0.0)
                },
                "document_extraction": {
                    "documents": {f"doc_{i}": doc for i, doc in enumerate(source_documents)},
                    "entities": embedding_data.get("extracted_entities", {}),
                    "relationships": embedding_data.get("extracted_relationships", {})
                },
                "processing_info": {
                    "start_time": embedding_data.get("start_time"),
                    "end_time": datetime.now().isoformat(),
                    "duration_ms": embedding_data.get("duration_ms", 0)
                },
                "org_id": user_context.get("org_id"),
                "dept_id": user_context.get("dept_id")
            }
            
            # Ensure org_id and dept_id are available
            if not system_data.get("org_id") or not system_data.get("dept_id"):
                logger.error("Missing org_id or dept_id in user_context")
                return False
            
            # Populate operations table
            success = await self.populate_operations_table(
                registry_data={"registry_id": registry_id},
                system_data=system_data,
                user_context=user_context
            )
            
            if success:
                logger.info(f"✅ Embedding operation created successfully for registry {registry_id}")
                return True
            else:
                logger.error(f"❌ Failed to create embedding operation for registry {registry_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating embedding operation: {e}")
            await self.error_tracker.track_error(
                error_type="embedding_operation_error",
                error_message=str(e),
                error_details=f"Failed to create embedding operation: {e}",
                severity="medium",
                metadata={"user_context": user_context, "registry_id": registry_id}
            )
            return False

    async def populate_graph_operation(
        self,
        graph_data: Dict[str, Any],
        graph_type: str,
        user_context: Dict[str, Any],
        registry_id: str
    ) -> bool:
        """
        Populate operations table for graph metadata operations.
        
        Args:
            graph_data: Graph metadata and structure
            graph_type: Type of graph (component_relationship, impact_analysis, etc.)
            user_context: User context and permissions
            registry_id: Associated registry ID
            
        Returns:
            True if operation created successfully
        """
        try:
            logger.info(f"🕸️ Creating graph operation for registry {registry_id}, type: {graph_type}")
            
            # Build system data for graph operations
            system_data = {
                "graph_metadata": {
                    "graphs": {
                        f"graph_{graph_data.get('graph_id', 'unknown')}": {
                            "graph_id": graph_data.get("graph_id"),
                            "graph_type": graph_type,
                            "nodes": graph_data.get("node_count", 0),
                            "edges": graph_data.get("edge_count", 0),
                            "centrality_score": graph_data.get("centrality_score", 0.0),
                            "clustering_coefficient": graph_data.get("clustering_coefficient", 0.0)
                        }
                    },
                    "count": 1,
                    "types": {
                        graph_type: {
                            "count": 1,
                            "graph_ids": [graph_data.get("graph_id")],
                            "description": self._get_graph_type_description(graph_type)
                        }
                    }
                },
                "processing_info": {
                    "start_time": graph_data.get("start_time"),
                    "end_time": datetime.now().isoformat(),
                    "duration_ms": graph_data.get("duration_ms", 0)
                },
                "org_id": user_context.get("org_id"),
                "dept_id": user_context.get("dept_id")
            }
            
            # Ensure org_id and dept_id are available
            if not system_data.get("org_id") or not system_data.get("dept_id"):
                logger.error("Missing org_id or dept_id in user_context")
                return False
            
            # Populate operations table
            success = await self.populate_operations_table(
                registry_data={"registry_id": registry_id},
                system_data=system_data,
                user_context=user_context
            )
            
            if success:
                logger.info(f"✅ Graph operation created successfully for registry {registry_id}")
                return True
            else:
                logger.error(f"❌ Failed to create graph operation for registry {registry_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating graph operation: {e}")
            await self.error_tracker.track_error(
                error_type="graph_operation_error",
                error_message=str(e),
                error_details=f"Failed to create graph operation: {e}",
                severity="medium",
                metadata={"user_context": user_context, "registry_id": registry_id}
            )
            return False

    async def populate_aasx_processing_operation(
        self,
        aasx_results: Dict[str, Any],
        user_context: Dict[str, Any],
        registry_id: str
    ) -> bool:
        """
        Populate operations table for AASX processing operations.
        
        Args:
            aasx_results: AASX processing results and metadata
            user_context: User context and permissions
            registry_id: Associated registry ID
            
        Returns:
            True if operation created successfully
        """
        try:
            logger.info(f"📄 Creating AASX processing operation for registry {registry_id}")
            
            # Build system data for AASX processing
            system_data = {
                "aasx_processing": {
                    "generation_type": aasx_results.get("generation_type", "document_extraction"),
                    "input_data": aasx_results.get("input_files", []),
                    "output_data": aasx_results.get("extracted_content", {}),
                    "generation_time_ms": aasx_results.get("processing_time_ms", 0),
                    "quality_score": aasx_results.get("extraction_quality", 0.9)
                },
                "document_extraction": {
                    "documents": aasx_results.get("extracted_documents", {}),
                    "entities": aasx_results.get("extracted_entities", {}),
                    "relationships": aasx_results.get("extracted_relationships", {})
                },
                "file_storage": {
                    "directory": aasx_results.get("output_directory"),
                    "files": aasx_results.get("output_files", {}),
                    "formats": aasx_results.get("supported_formats", {})
                },
                "processing_info": {
                    "start_time": aasx_results.get("start_time"),
                    "end_time": aasx_results.get("end_time"),
                    "duration_ms": aasx_results.get("processing_time_ms", 0)
                },
                "org_id": user_context.get("org_id"),
                "dept_id": user_context.get("dept_id")
            }
            
            # Ensure org_id and dept_id are available
            if not system_data.get("org_id") or not system_data.get("dept_id"):
                logger.error("Missing org_id or dept_id in user_context")
                return False
            
            # Populate operations table
            success = await self.populate_operations_table(
                registry_data={"registry_id": registry_id},
i                system_data=system_data,
                user_context=user_context
            )
            
            if success:
                logger.info(f"✅ AASX processing operation created successfully for registry {registry_id}")
                return True
            else:
                logger.error(f"❌ Failed to create AASX processing operation for registry {registry_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating AASX processing operation: {e}")
            await self.error_tracker.track_error(
                error_type="aasx_processing_operation_error",
                error_message=str(e),
                error_details=f"Failed to create AASX processing operation: {e}",
                severity="medium",
                metadata={"user_context": user_context, "registry_id": registry_id}
            )
            return False

    # 🔧 Enhanced Business Logic Helper Methods
    
    def _calculate_query_complexity(self, query_text: str) -> float:
        """
        Calculate query complexity score based on various factors.
        
        Args:
            query_text: User query text
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        try:
            if not query_text:
                return 0.0
            
            # Simple complexity factors
            word_count = len(query_text.split())
            has_technical_terms = any(term in query_text.lower() for term in [
                'specification', 'parameter', 'efficiency', 'carbon', 'footprint',
                'analysis', 'calculation', 'relationship', 'dependency'
            ])
            has_numbers = any(char.isdigit() for char in query_text)
            has_special_chars = any(char in query_text for char in ['%', '>', '<', '=', '+', '-'])
            
            # Calculate complexity score
            complexity = 0.0
            complexity += min(word_count / 20.0, 0.3)  # Word count factor
            complexity += 0.2 if has_technical_terms else 0.0
            complexity += 0.2 if has_numbers else 0.0
            complexity += 0.1 if has_special_chars else 0.0
            complexity += 0.2 if len(query_text) > 100 else 0.0
            
            return min(complexity, 1.0)
            
        except Exception as e:
            logger.warning(f"Error calculating query complexity: {e}")
            return 0.5  # Default medium complexity

    def _get_graph_type_description(self, graph_type: str) -> str:
        """
        Get human-readable description for graph types.
        
        Args:
            graph_type: Graph type identifier
            
        Returns:
            Human-readable description
        """
        descriptions = {
            "component_relationship": "Technical component relationships and dependencies",
            "impact_analysis": "Environmental impact and sustainability analysis",
            "workflow_process": "Business workflow and process flows",
            "data_flow": "Data flow and information architecture",
            "system_architecture": "System architecture and component mapping",
            "dependency_graph": "Component dependency and requirement mapping",
            "quality_metrics": "Quality metrics and performance indicators",
            "compliance_mapping": "Compliance and regulatory requirement mapping"
        }
        
        return descriptions.get(graph_type, f"Graph type: {graph_type}")

    async def get_operations_by_type(
        self,
        operation_type: str,
        user_context: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[AIRagOperations]:
        """
        Get operations filtered by operation type.
        
        Args:
            operation_type: Type of operations to retrieve
            user_context: User context for authorization
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of operations matching the type
        """
        try:
            # Build search criteria
            search_criteria = {"operation_type": operation_type}
            
            # Get operations from repository
            operations = await self.repository.get_by_operation_type(operation_type, limit)
            
            # Filter by user permissions
            filtered_operations = []
            for operation in operations:
                if await self._validate_user_permissions(
                    {"org_id": operation.org_id, "dept_id": operation.dept_id},
                    user_context
                ):
                    filtered_operations.append(operation)
            
            logger.info(f"Retrieved {len(filtered_operations)} operations of type: {operation_type}")
            return filtered_operations
            
        except Exception as e:
            logger.error(f"Error retrieving operations by type {operation_type}: {e}")
            return []

    async def get_operations_summary_by_type(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary statistics for operations grouped by type.
        
        Args:
            user_context: User context for authorization
            
        Returns:
            Summary statistics by operation type
        """
        try:
            # Get all operations for the user's organization
            org_id = user_context.get("org_id")
            dept_id = user_context.get("dept_id")
            
            if not org_id or not dept_id:
                return {"error": "Missing organization information"}
            
            # Build search criteria
            search_criteria = {"org_id": org_id, "dept_id": dept_id}
            operations = await self.repository.search(search_criteria, limit=1000)
            
            # Group by operation type
            summary_by_type = {}
            for operation in operations:
                op_type = operation.operation_type
                if op_type not in summary_by_type:
                    summary_by_type[op_type] = {
                        "count": 0,
                        "total_duration_ms": 0,
                        "avg_quality_score": 0.0,
                        "recent_operations": []
                    }
                
                summary = summary_by_type[op_type]
                summary["count"] += 1
                summary["total_duration_ms"] += getattr(operation, 'processing_duration_ms', 0) or 0
                summary["avg_quality_score"] += getattr(operation, 'quality_score', 0.0) or 0.0
                
                # Keep track of recent operations
                if len(summary["recent_operations"]) < 5:
                    summary["recent_operations"].append({
                        "operation_id": operation.operation_id,
                        "timestamp": operation.timestamp,
                        "quality_score": getattr(operation, 'quality_score', 0.0)
                    })
            
            # Calculate averages
            for op_type, summary in summary_by_type.items():
                if summary["count"] > 0:
                    summary["avg_duration_ms"] = summary["total_duration_ms"] / summary["count"]
                    summary["avg_quality_score"] = summary["avg_quality_score"] / summary["count"]
            
            return {
                "organization_id": org_id,
                "department_id": dept_id,
                "total_operations": sum(s["count"] for s in summary_by_type.values()),
                "operations_by_type": summary_by_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting operations summary by type: {e}")
            return {"error": str(e)}

    # 🔄 Legacy Method Support (for backward compatibility)
    
    async def populate_table_from_source(self, source_data: Dict[str, Any]) -> bool:
        """
        Legacy method for backward compatibility.
        Delegates to the new populate_operations_table method.
        """
        logger.info("🔄 Using legacy populate_table_from_source - delegating to populate_operations_table")
        return await self.populate_operations_table(system_data=source_data)

    async def integrate_with_external_systems(self, external_data: Dict[str, Any]) -> bool:
        """
        Legacy method for backward compatibility.
        Delegates to appropriate domain-specific methods based on data type.
        """
        logger.info("🔄 Using legacy integrate_with_external_systems - delegating to appropriate method")
        
        # Determine the type of external data and delegate accordingly
        if external_data.get("embedding_generation"):
            return await self.populate_embedding_operation(
                embedding_data=external_data["embedding_generation"],
                source_documents=external_data.get("source_documents", []),
                user_context=external_data.get("user_context", {}),
                registry_id=external_data.get("registry_id", "unknown")
            )
        elif external_data.get("graph_metadata"):
            return await self.populate_graph_operation(
                graph_data=external_data["graph_metadata"],
                graph_type=external_data.get("graph_type", "unknown"),
                user_context=external_data.get("user_context", {}),
                registry_id=external_data.get("registry_id", "unknown")
            )
        elif external_data.get("aasx_processing"):
            return await self.populate_aasx_processing_operation(
                aasx_results=external_data["aasx_processing"],
                user_context=external_data.get("user_context", {}),
                registry_id=external_data.get("registry_id", "unknown")
            )
        else:
            # Fallback to generic population
            return await self.populate_operations_table(system_data=external_data)

    async def handle_data_population_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Legacy method for backward compatibility.
        Handles events and delegates to appropriate population methods.
        """
        logger.info("🔄 Using legacy handle_data_population_event - processing event data")
        
        event_type = event_data.get("event_type", "unknown")
        
        if event_type == "user_query":
            return await self.populate_query_operation(
                user_query=event_data.get("query_text", ""),
                ai_response=event_data.get("response_text", ""),
                session_data=event_data.get("session_data", {}),
                user_context=event_data.get("user_context", {}),
                registry_id=event_data.get("registry_id", "unknown")
            )
        elif event_type == "embedding_generated":
            return await self.populate_embedding_operation(
                embedding_data=event_data.get("embedding_data", {}),
                source_documents=event_data.get("source_documents", []),
                user_context=event_data.get("user_context", {}),
                registry_id=event_data.get("registry_id", "unknown")
            )
        elif event_type == "graph_updated":
            return await self.populate_graph_operation(
                graph_data=event_data.get("graph_data", {}),
                graph_type=event_data.get("graph_type", "unknown"),
                user_context=event_data.get("user_context", {}),
                registry_id=event_data.get("registry_id", "unknown")
            )
        elif event_type == "aasx_processed":
            return await self.populate_aasx_processing_operation(
                aasx_results=event_data.get("aasx_results", {}),
                user_context=event_data.get("user_context", {}),
                registry_id=event_data.get("registry_id", "unknown")
            )
        else:
            # Generic event handling
            return await self.populate_operations_table(system_data=event_data)
    
    async def _extract_org_hierarchy(
        self,
        frontend_data: Optional[Dict[str, Any]],
        registry_data: Optional[Dict[str, Any]],
        system_data: Optional[Dict[str, Any]]
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Extract organizational hierarchy from multiple data sources.
        
        Returns:
            Tuple of (org_id, dept_id) or (None, None) if not found
        """
        # Priority order: frontend_data > registry_data > system_data
        
        # Check frontend data first
        if frontend_data:
            org_id = frontend_data.get('org_id')
            dept_id = frontend_data.get('dept_id')
            if org_id and dept_id:
                return org_id, dept_id
        
        # Check registry data
        if registry_data:
            org_id = registry_data.get('org_id')
            dept_id = registry_data.get('dept_id')
            if org_id and dept_id:
                return org_id, dept_id
        
        # Check system data
        if system_data:
            org_id = system_data.get('org_id')
            dept_id = system_data.get('dept_id')
            if org_id and dept_id:
                return org_id, dept_id
        
        return None, None
    
    async def _extract_registry_id(
        self,
        registry_data: Optional[Dict[str, Any]],
        system_data: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Extract registry ID from data sources.
        
        Returns:
            Registry ID or None if not found
        """
        # Check registry data first
        if registry_data and registry_data.get('registry_id'):
            return registry_data['registry_id']
        
        # Check system data
        if system_data and system_data.get('registry_id'):
            return system_data['registry_id']
        
        return None
    
    async def _generate_operation_id(self, org_id: str, dept_id: str) -> str:
        """
        Generate unique operation ID.
        
        Args:
            org_id: Organization identifier
            dept_id: Department identifier
            
        Returns:
            Unique operation ID
        """
        # Use microseconds to ensure uniqueness even for rapid operations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        hash_suffix = hashlib.md5(f"{org_id}_{dept_id}_{timestamp}".encode()).hexdigest()[:8]
        return f"op_{timestamp}_{hash_suffix}"
    
    async def _build_operation_data(
        self,
        operation_id: str,
        registry_id: str,
        frontend_data: Optional[Dict[str, Any]],
        registry_data: Optional[Dict[str, Any]],
        system_data: Optional[Dict[str, Any]],
        org_id: str,
        dept_id: str
    ) -> Dict[str, Any]:
        """
        Build comprehensive operation data from multiple sources.
        
        Args:
            operation_id: Generated operation ID
            registry_id: Registry identifier
            frontend_data: Frontend user interaction data
            registry_data: Registry table data
            system_data: System processing results
            org_id: Organization identifier
            dept_id: Department identifier
            
        Returns:
            Complete operation data dictionary
        """
        timestamp = datetime.now().isoformat()
        
        # Base operation data
        operation_data = {
            "operation_id": operation_id,
            "registry_id": registry_id,
            "timestamp": timestamp,
            "org_id": org_id,
            "dept_id": dept_id,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Extract frontend data
        if frontend_data:
            operation_data.update(await self._extract_frontend_data(frontend_data))
        
        # Extract registry data
        if registry_data:
            operation_data.update(await self._extract_registry_data(registry_data))
        
        # Extract system data
        if system_data:
            operation_data.update(await self._extract_system_data(system_data))
        
        # Set default values for required fields
        operation_data.setdefault("operation_type", "session")  # Use valid operation type
        operation_data.setdefault("user_id", frontend_data.get("user_id") if frontend_data else "system")
        operation_data.setdefault("created_by", frontend_data.get("user_id") if frontend_data else "system")  # Add missing created_by
        operation_data.setdefault("processing_status", "completed")
        operation_data.setdefault("quality_score", 0.9)
        operation_data.setdefault("validation_status", "validated")
        
        return operation_data
    
    async def _extract_frontend_data(self, frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and process frontend data for operations.
        
        Args:
            frontend_data: Frontend user interaction data
            
        Returns:
            Processed frontend data for operations
        """
        extracted_data = {}
        
        # Session information
        if frontend_data.get("session_data"):
            session = frontend_data["session_data"]
            extracted_data.update({
                "session_id": session.get("session_id"),
                "user_id": frontend_data.get("user_id"),
                "query_text": frontend_data.get("query_text"),
                "response_text": frontend_data.get("response_text"),
                "session_start": session.get("start_time"),
                "session_end": session.get("end_time"),
                "session_duration_ms": session.get("duration_ms")
            })
        
        # User preferences and settings
        if frontend_data.get("user_preferences"):
            prefs = frontend_data["user_preferences"]
            extracted_data.update({
                "similarity_threshold": prefs.get("similarity_threshold", 0.85),
                "confidence_score": prefs.get("confidence_score", 0.9)
            })
        
        return extracted_data
    
    async def _extract_registry_data(self, registry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and process registry data for operations.
        
        Args:
            registry_data: Registry table data
            
        Returns:
            Processed registry data for operations
        """
        extracted_data = {}
        
        # Integration references
        extracted_data.update({
            "kg_neo4j_graph_id": registry_data.get("kg_neo4j_id"),
            "aasx_integration_id": registry_data.get("aasx_integration_id"),
            "twin_registry_id": registry_data.get("twin_registry_id")
        })
        
        # Registry metadata
        if registry_data.get("registry_metadata"):
            metadata = registry_data["registry_metadata"]
            extracted_data.update({
                "registry_type": metadata.get("registry_type"),
                "workflow_source": metadata.get("workflow_source")
            })
        
        return extracted_data
    
    async def _extract_system_data(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and process system data for operations.
        
        Args:
            system_data: System processing results
            
        Returns:
            Processed system data for operations
        """
        extracted_data = {}
        
        # AASX processing results
        if system_data.get("aasx_processing"):
            aasx = system_data["aasx_processing"]
            extracted_data.update({
                "generation_type": aasx.get("generation_type"),
                "input_data": json.dumps(aasx.get("input_data", [])) if aasx.get("input_data") is not None else "[]",
                "output_data": json.dumps(aasx.get("output_data", {})) if aasx.get("output_data") is not None else "{}",
                "generation_time_ms": aasx.get("generation_time_ms"),
                "generation_quality_score": aasx.get("quality_score")
            })
        
        # Document extraction results
        if system_data.get("document_extraction"):
            docs = system_data["document_extraction"]
            extracted_data.update({
                "source_documents": docs.get("documents", {}),
                "source_entities": docs.get("entities", {}),
                "source_relationships": docs.get("relationships", {})
            })
        
        # Embedding generation results
        if system_data.get("embedding_generation"):
            emb = system_data["embedding_generation"]
            extracted_data.update({
                "embedding_id": emb.get("embedding_id"),
                "vector_data": emb.get("vector_data"),
                "embedding_model": emb.get("model"),
                "embedding_dimensions": emb.get("dimensions"),
                "embedding_quality_score": emb.get("quality_score"),
                "model_provider": emb.get("provider"),
                "model_parameters": emb.get("parameters", {}),
                "generation_timestamp": emb.get("timestamp"),
                "generation_duration_ms": emb.get("duration_ms"),
                "generation_cost": emb.get("cost")
            })
        
        # Graph metadata
        if system_data.get("graph_metadata"):
            graphs = system_data["graph_metadata"]
            extracted_data.update({
                "graphs_json": graphs.get("graphs", {}),
                "graph_count": graphs.get("count", 0),
                "graph_types": graphs.get("types", {})
            })
        
        # Processing information
        if system_data.get("processing_info"):
            proc = system_data["processing_info"]
            extracted_data.update({
                "processing_start_time": proc.get("start_time"),
                "processing_end_time": proc.get("end_time"),
                "processing_duration_ms": proc.get("duration_ms")
            })
        
        # File storage references
        if system_data.get("file_storage"):
            files = system_data["file_storage"]
            extracted_data.update({
                "output_directory": files.get("directory"),
                "output_files": files.get("files", {}),
                "file_formats": files.get("formats", {})
            })
        
        return extracted_data

    # 🚨 MANDATORY: Customization Warning
    # These are TEMPLATE methods that MUST be customized!
    # ❌ DON'T: Leave them as generic pass-through methods
    # ❌ DON'T: Just call repository.create() without business logic
    # ❌ DON'T: Copy-paste without understanding your module's needs
    # ✅ DO: Customize each method for your specific module
    # ✅ DO: Add actual population logic, not just CRUD operations
    # ✅ DO: Understand how your table gets populated
    
    # 📋 CUSTOMIZATION CHECKLIST:
    # Before implementing, answer:
    # 1. What populates this table? (Users, systems, files, events?)
    # 2. What external integrations are needed?
    # 3. What business logic is required?
    # 4. How is this different from a basic repository?
    # Then customize the template methods accordingly.

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
                        resource="ai_rag",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read ai_rag_operations summary")
                        return {"error": "Access denied"}
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    return {"error": "Access denied"}
                
                # ✅ REQUIRED: Get summary from repository
                summary = await self.repository.get_summary()
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_operations_summary_retrieved",
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
            if not is_update:
                # For create operations, check all required fields
                required_fields = self.business_config.get('required_fields', [])
                for field in required_fields:
                    if field not in entity_data or entity_data[field] is None:
                        logger.error(f"Required field missing: {field}")
                        return False
            else:
                # For update operations, only check that at least one field is provided
                if not entity_data:
                    logger.error("No update data provided")
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
            
            # Check organizational hierarchy (both org_id and dept_id are now required)
            if 'org_id' in entity_data and entity_data['org_id']:
                if 'dept_id' not in entity_data or not entity_data['dept_id']:
                    logger.error("dept_id is required (both org_id and dept_id are mandatory)")
                    return False
            elif 'dept_id' in entity_data and entity_data['dept_id']:
                if 'org_id' not in entity_data or not entity_data['org_id']:
                    logger.error("org_id is required (both org_id and dept_id are mandatory)")
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
                cross_org_roles = self.business_config.get('cross_org_roles', [])
                
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

async def create_ai_rag_operations_service(connection_manager: ConnectionManager) -> AIRagOperationsService:
    """
    Factory function to create and initialize a AIRagOperationsService instance.
    
    Args:
        connection_manager: Database connection manager
        
    Returns:
        Initialized AIRagOperationsService instance
        
    Raises:
        Exception: If service initialization fails
    """
    try:
        # Create service instance
        service = AIRagOperationsService(connection_manager)
        
        # Initialize service
        if not await service.initialize_service():
            raise Exception(f"Failed to initialize {service.service_name}")
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create ai_rag_operations service: {e}")
        raise


# ✅ REQUIRED: Export the service class and factory
__all__ = ['AIRagOperationsService', 'create_ai_rag_operations_service']
