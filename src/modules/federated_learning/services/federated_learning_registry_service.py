#!/usr/bin/env python3
"""
Federated Learning Registry Service

This service provides business logic and orchestration for federated learning registry operations
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
    service = FederatedLearningRegistryService(connection_manager)
    await service.initialize_service()
    
    # Use service methods
    result = await service.create_entity(data, user_context)
    entities = await service.search_entities(criteria, user_context)
"""

import json
import logging
import re
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
from ..models.federated_learning_registry import FederatedLearningRegistry
from ..repositories.federated_learning_registry_repository import FederatedLearningRegistryRepository

logger = logging.getLogger(__name__)


class FederatedLearningRegistryService:
    """
    Service for federated learning registry business logic and orchestration
    
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
        self.repository = FederatedLearningRegistryRepository(connection_manager)
        
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
        self.service_name = "federated_learning_registry_service"
        self.service_version = "1.0.0"
        self.service_status = "initialized"
        
        # ✅ REQUIRED: Logger
        self.logger = logger
        
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
                'allowed_file_types': ['.aasx', '.json', '.yaml', '.pkl', '.h5'],
                'processing_timeout_minutes': 30,
                'retry_attempts': 3,
                'max_federation_rounds': 1000,
                'max_participating_twins': 100,
                'min_health_score': 50
            },
            'permissions': {
                'create': ['admin', 'user', 'processor', 'federation_manager'],
                'read': ['admin', 'user', 'processor', 'federation_manager', 'viewer'],
                'update': ['admin', 'user', 'processor', 'federation_manager'],
                'delete': ['admin', 'federation_manager'],
                'execute': ['admin', 'federation_manager', 'processor']
            },
            'cross_dept_roles': ['admin', 'federation_manager'],
            'org_wide_roles': ['admin', 'system_admin'],
            'business_specific': {
                'max_federations_per_org': 50,
                'max_federations_per_dept': 10,
                'naming_convention': "Fed_{org_id}_{dept_id}_{timestamp}",
                'compliance_requirements': ["GDPR", "HIPAA", "SOX", "ISO27001"],
                'federation_categories': ['collaborative_learning', 'privacy_preserving', 'secure_aggregation', 'hybrid'],
                'federation_types': ['fedavg', 'secure_aggregation', 'differential_privacy', 'performance_weighting', 'hybrid'],
                'lifecycle_phases': ['setup', 'recruitment', 'training', 'aggregation', 'evaluation', 'deployment', 'maintenance']
            }
        }
    
    async def _initialize_security_context(self) -> Dict[str, Any]:
        """
        Initialize security context for the service.
        
        Returns:
            Dictionary containing security configuration and requirements
        """
        return {
            'service_name': 'FederatedLearningRegistryService',
            'security_level': 'enterprise',
            'audit_enabled': True,
            'encryption_required': True,
            'require_authentication': True,
            'require_authorization': True,
            'default_permissions': ['read', 'write'],
            'multi_tenant': True,
            'dept_isolation': True,
            'federation_isolation': True,
            'privacy_preservation': True
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
    
    # ⚠️ IMPORTANT: This is a POPULATION SERVICE that integrates with external data sources!
    # 
    # This service needs to populate tables from:
    # - AASX file processing (extraction workflows)
    # - Twin Registry integration (generation workflows)
    # - AI RAG integration (hybrid workflows)
    # - External federation systems
    #
    # Therefore, we use DOMAIN-SPECIFIC methods, not generic CRUD methods!
    
    # ✅ REQUIRED: Standard Entity Operations (STAGE 1 IMPLEMENTATION)
    
    async def create_entity(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[FederatedLearningRegistry]:
        """
        Create a new federated learning registry entity with comprehensive business logic validation.
        
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
                        roles=['admin', 'user', 'processor', 'federation_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="federated_learning",
                        action="create"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to create federated_learning")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
            
                # ✅ REQUIRED: Business validation
                if not await self._validate_federation_data(entity_data, user_context):
                    logger.error("Entity data validation failed")
                    return None
                
                # ✅ REQUIRED: Create entity instance
                entity = FederatedLearningRegistry(**entity_data)
                
                # ✅ REQUIRED: Save to repository
                if not await self.repository.create(entity):
                    logger.error("Failed to save entity to repository")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="federated_learning_created",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("federated_learning.created", {
                    "entity_id": getattr(entity, 'registry_id', None),
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully created federated_learning: {getattr(entity, 'registry_id', 'unknown')}")
                return entity
                
            except Exception as e:
                logger.error(f"Error creating federated_learning: {e}")
                await self.error_tracker.track_error(
                    error_type="create_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to create federated_learning: {e}",
                    severity="medium",
                    metadata={"user_context": user_context}
                )
                return None
    
    async def update_entity(
        self,
        entity_id: str,
        update_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Update a federated learning registry entity with authorization check and validation.
        
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
                        roles=['admin', 'user', 'processor', 'federation_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="federated_learning",
                        action="update"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update federated_learning")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Business validation
                if not await self._validate_federation_data(update_data, user_context, is_update=True):
                    logger.error("Update data validation failed")
                    return False
                
                # ✅ REQUIRED: Get existing entity and update it
                existing_entity = await self.repository.get_by_id(entity_id)
                if not existing_entity:
                    logger.error(f"Entity not found for update: {entity_id}")
                    return False
                
                # Update the entity with new data
                for key, value in update_data.items():
                    if hasattr(existing_entity, key):
                        setattr(existing_entity, key, value)
                
                # Update timestamp
                existing_entity.updated_at = datetime.now()
                
                # ✅ REQUIRED: Update in repository
                updated_entity = await self.repository.update(existing_entity)
                if not updated_entity:
                    logger.error(f"Failed to update federated_learning: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="federated_learning_updated",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("federated_learning.updated", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully updated federated_learning: {entity_id}")
                return True
            
            except Exception as e:
                logger.error(f"Error updating federated_learning: {e}")
                await self.error_tracker.track_error(
                    error_type="update_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to update federated_learning {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False
    
    async def get_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[FederatedLearningRegistry]:
        """
        Retrieve a federated learning registry entity by ID with authorization check.
        
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
                        roles=['admin', 'user', 'processor', 'federation_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="federated_learning",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read federated_learning")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Retrieve from repository
                entity = await self.repository.get_by_id(entity_id)
                if not entity:
                    logger.warning(f"FederatedLearningRegistry not found: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="federated_learning_retrieved",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                return entity
                
            except Exception as e:
                logger.error(f"Error retrieving federated_learning: {e}")
                await self.error_tracker.track_error(
                    error_type="get_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve federated_learning {entity_id}: {e}",
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
    ) -> List[FederatedLearningRegistry]:
        """
        Search for federated learning registry entities based on criteria with authorization check.
        
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
                        roles=['admin', 'user', 'processor', 'federation_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="federated_learning",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to search federated_learning")
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
                    metric_name="federated_learning_search_executed",
                    metric_value=len(entities),
                    metadata={"user_id": user_context.get("user_id"), "criteria_count": len(search_criteria)}
                )
                
                logger.info(f"Search returned {len(entities)} results")
                return entities
                
            except Exception as e:
                logger.error(f"Error searching federated_learning: {e}")
                await self.error_tracker.track_error(
                    error_type="search_entities_error",
                    error_message=str(e),
                    error_details=f"Failed to search federated_learning: {e}",
                    severity="medium",
                    metadata={"search_criteria": search_criteria, "user_context": user_context}
                )
                return []
    
    async def delete_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Delete a federated learning registry entity with authorization check.
        
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
                        roles=['admin', 'user', 'processor', 'federation_manager'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="federated_learning",
                        action="delete"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to delete federated_learning")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Delete from repository
                if not await self.repository.delete(entity_id):
                    logger.error(f"Failed to delete federated_learning: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="federated_learning_deleted",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("federated_learning.deleted", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully deleted federated_learning: {entity_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting federated_learning: {e}")
                await self.error_tracker.track_error(
                    error_type="delete_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to delete federated_learning {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False
    
    # ✅ REQUIRED: Domain-Specific Population Methods (STAGE 2 IMPLEMENTATION)
    
    async def create_federation_from_aasx(
        self,
        aasx_integration_id: str,
        federation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[FederatedLearningRegistry]:
        """
        Create a federated learning registry entry from AASX processing.
        
        Args:
            aasx_integration_id: ID of the AASX processing job
            federation_data: Federation configuration and metadata
            user_context: User context for authorization and audit
            
        Returns:
            Created federation registry or None if creation failed
        """
        try:
            # Extract AASX-specific data for federation creation
            import uuid
            entity_data = {
                "registry_id": str(uuid.uuid4()),
                "federation_name": f"Fed_AASX_{federation_data.get('asset_type', 'Unknown')}_{federation_data.get('timestamp', 'Unknown')}",
                "registry_name": f"{federation_data.get('asset_type', 'Asset')} Efficiency Federation",
                "federation_category": "collaborative_learning",
                "federation_type": "fedavg",
                "federation_priority": federation_data.get('priority', 'normal'),
                "federation_version": "1.0.0",
                "registry_type": "extraction",
                "workflow_source": "aasx_file",
                "user_id": user_context.get("user_id"),
                "org_id": user_context.get("org_id"),
                "dept_id": user_context.get("dept_id"),
                "integration_references": {
                    "aasx_integration_id": aasx_integration_id,
                    "twin_registry_id": federation_data.get('twin_registry_id'),
                    "kg_neo4j_id": None,
                    "physics_modeling_id": None,
                    "ai_rag_id": None,
                    "certificate_manager_id": None
                },
                "integration_status": "active",
                "overall_health_score": 75,
                "health_status": "healthy",
                "lifecycle_status": "active",
                "lifecycle_phase": "recruitment",
                "operational_status": "running",
                "availability_status": "online",
                "federation_specific_status": {
                    "federation_participation_status": "recruiting",
                    "model_aggregation_status": "not_started",
                    "privacy_compliance_status": "compliant",
                    "algorithm_execution_status": "ready",
                    "last_federation_sync_at": federation_data.get('timestamp'),
                    "next_federation_sync_at": None,
                    "federation_sync_error_count": 0,
                    "federation_sync_error_message": None
                },
                "federation_data_metrics": {
                    "total_participating_twins": federation_data.get('participating_twins', 0),
                    "total_federation_rounds": 0,
                    "total_models_aggregated": 0,
                    "federation_complexity": "moderate"
                },
                "performance_quality_metrics": {
                    "performance_score": 0.75,
                    "data_quality_score": 0.85,
                    "reliability_score": 0.80,
                    "compliance_score": 0.90
                },
                "enterprise_compliance_tracking": {
                    "compliance_framework": "GDPR",
                    "compliance_status": "compliant",
                    "last_audit_date": None,
                    "next_audit_date": None,
                    "audit_details": None,
                    "risk_level": "low"
                },
                "enterprise_security_metrics": {
                    "security_score": 85.0,
                    "threat_detection_score": 80.0,
                    "encryption_strength": "AES-256",
                    "authentication_method": "multi_factor",
                    "access_control_score": 85.0,
                    "data_protection_score": 90.0,
                    "incident_response_time": 30,
                    "security_audit_score": 85.0,
                    "last_security_scan": None,
                    "security_details": {
                        "encryption_enabled": True,
                        "key_rotation": "daily",
                        "last_key_update": None,
                        "threat_level": "low"
                    }
                },
                "enterprise_performance_analytics": {
                    "efficiency_score": 80.0,
                    "scalability_score": 75.0,
                    "optimization_potential": 85.0,
                    "bottleneck_identification": "network_latency",
                    "performance_trend": "improving",
                    "last_optimization_date": None,
                    "optimization_suggestions": []
                },
                "security_access_control": {
                    "security_level": "confidential",
                    "access_control_level": "restricted",
                    "encryption_enabled": True,
                    "audit_logging_enabled": True
                },
                "user_management_ownership": {
                    "user_id": user_context.get('user_id'),
                    "org_id": user_context.get('org_id'),
                    "dept_id": user_context.get('dept_id'),
                    "owner_team": "AASX_Processing_Team",
                    "steward_user_id": user_context.get('steward_user_id')
                },
                "timestamps_audit": {
                    "created_at": federation_data.get('timestamp'),
                    "updated_at": federation_data.get('timestamp'),
                    "activated_at": federation_data.get('timestamp'),
                    "last_accessed_at": federation_data.get('timestamp'),
                    "last_modified_at": federation_data.get('timestamp')
                },
                "configuration_metadata": {
                    "registry_config": {
                        "federation_settings": {
                            "max_rounds": 50,
                            "convergence_threshold": 0.001,
                            "participation_timeout": 3600,
                            "model_validation_enabled": True
                        },
                        "privacy_settings": {
                            "differential_privacy": True,
                            "epsilon": 1.0,
                            "delta": 0.0001,
                            "secure_aggregation": True
                        },
                        "performance_settings": {
                            "parallel_processing": True,
                            "max_concurrent_orgs": 5,
                            "resource_monitoring": True
                        }
                    },
                    "registry_metadata": {
                        "federation_purpose": f"{federation_data.get('asset_type', 'Asset')} efficiency optimization across manufacturing plants",
                        "business_value": f"Expected {federation_data.get('expected_improvement', 15)}% improvement in efficiency",
                        "success_criteria": f"Achieve {federation_data.get('target_accuracy', 90)}% accuracy in efficiency prediction",
                        "expected_completion": None
                    },
                    "custom_attributes": {
                        "industry_sector": federation_data.get('industry_sector', 'manufacturing'),
                        "equipment_type": federation_data.get('asset_type', 'unknown'),
                        "optimization_target": "efficiency",
                        "collaboration_model": "horizontal"
                    },
                    "tags": {
                        "technical": [federation_data.get('asset_type', 'asset'), "efficiency", "optimization", "federated_learning", "aasx_driven"],
                        "business": ["manufacturing", "cost_reduction", "quality_improvement"],
                        "compliance": ["GDPR", "manufacturing_standards"],
                        "priority": [federation_data.get('priority', 'normal')]
                    }
                },
                "relationships_dependencies": {
                    "relationships": {
                        "depends_on": {
                            "aasx_processing": aasx_integration_id,
                            "twin_registry": federation_data.get('twin_registry_id')
                        },
                        "enables": {}
                    },
                    "dependencies": {
                        "required_modules": ["aasx_processing", "twin_registry"],
                        "optional_modules": [],
                        "external_systems": []
                    },
                    "federation_instances": {}
                },
                "traceability_fields": {
                    "federation_rounds": {},
                    "organization_participation": {},
                    "model_evolution": {},
                    "privacy_compliance": {},
                    "performance_metrics": {},
                    "federation_algorithms": {}
                }
            }
            
            # Create federation using standard entity operation
            return await self.create_entity(entity_data, user_context)
            
        except Exception as e:
            self.logger.error(f"Failed to create federation from AASX: {str(e)}")
            await self._audit_logger.log_activity(
                user_context.get('user_id'),
                "create_federation_from_aasx",
                "error",
                f"Failed to create federation from AASX: {str(e)}"
            )
            return None
    
    async def create_federation_from_twin_registry(
        self,
        twin_registry_id: str,
        federation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[FederatedLearningRegistry]:
        """
        Create a federated learning registry entry from Twin Registry integration.
        
        Args:
            twin_registry_id: ID of the twin registry entry
            federation_data: Federation configuration and metadata
            user_context: User context for authorization and audit
            
        Returns:
            Created federation registry or None if creation failed
        """
        try:
            # Extract Twin Registry-specific data for federation creation
            import uuid
            entity_data = {
                "registry_id": str(uuid.uuid4()),
                "federation_name": f"Fed_Twin_{federation_data.get('equipment_type', 'Unknown')}_{federation_data.get('timestamp', 'Unknown')}",
                "registry_name": f"{federation_data.get('equipment_type', 'Equipment')} Performance Optimization Federation",
                "federation_category": "privacy_preserving",
                "federation_type": "secure_aggregation",
                "federation_priority": federation_data.get('priority', 'high'),
                "federation_version": "1.0.0",
                "registry_type": "generation",
                "workflow_source": "structured_data",
                "user_id": user_context.get("user_id"),
                "org_id": user_context.get("org_id"),
                "dept_id": user_context.get("dept_id"),
                "integration_references": {
                    "aasx_integration_id": None,
                    "twin_registry_id": twin_registry_id,
                    "kg_neo4j_id": None,
                    "physics_modeling_id": None,
                    "ai_rag_id": None,
                    "certificate_manager_id": None
                },
                "integration_status": "active",
                "overall_health_score": 80,
                "health_status": "healthy",
                "lifecycle_status": "active",
                "lifecycle_phase": "recruitment",
                "operational_status": "running",
                "availability_status": "online",
                "federation_specific_status": {
                    "federation_participation_status": "recruiting",
                    "model_aggregation_status": "not_started",
                    "privacy_compliance_status": "compliant",
                    "algorithm_execution_status": "ready",
                    "last_federation_sync_at": federation_data.get('timestamp'),
                    "next_federation_sync_at": None,
                    "federation_sync_error_count": 0,
                    "federation_sync_error_message": None
                },
                "federation_data_metrics": {
                    "total_participating_twins": federation_data.get('participating_twins', 0),
                    "total_federation_rounds": 0,
                    "total_models_aggregated": 0,
                    "federation_complexity": "moderate"
                },
                "performance_quality_metrics": {
                    "performance_score": 0.80,
                    "data_quality_score": 0.90,
                    "reliability_score": 0.85,
                    "compliance_score": 0.95
                },
                "enterprise_compliance_tracking": {
                    "compliance_framework": "GDPR",
                    "compliance_status": "compliant",
                    "last_audit_date": None,
                    "next_audit_date": None,
                    "audit_details": None,
                    "risk_level": "low"
                },
                "enterprise_security_metrics": {
                    "security_score": 90.0,
                    "threat_detection_score": 85.0,
                    "encryption_strength": "AES-256",
                    "authentication_method": "multi_factor",
                    "access_control_score": 90.0,
                    "data_protection_score": 95.0,
                    "incident_response_time": 20,
                    "security_audit_score": 90.0,
                    "last_security_scan": None,
                    "security_details": {
                        "encryption_enabled": True,
                        "key_rotation": "daily",
                        "last_key_update": None,
                        "threat_level": "low"
                    }
                },
                "enterprise_performance_analytics": {
                    "efficiency_score": 85.0,
                    "scalability_score": 80.0,
                    "optimization_potential": 90.0,
                    "bottleneck_identification": "data_validation",
                    "performance_trend": "improving",
                    "last_optimization_date": None,
                    "optimization_suggestions": []
                },
                "security_access_control": {
                    "security_level": "confidential",
                    "access_control_level": "restricted",
                    "encryption_enabled": True,
                    "audit_logging_enabled": True
                },
                "user_management_ownership": {
                    "user_id": user_context.get('user_id'),
                    "org_id": user_context.get('org_id'),
                    "dept_id": user_context.get('dept_id'),
                    "owner_team": "Twin_Analytics_Team",
                    "steward_user_id": user_context.get('steward_user_id')
                },
                "timestamps_audit": {
                    "created_at": federation_data.get('timestamp'),
                    "updated_at": federation_data.get('timestamp'),
                    "activated_at": federation_data.get('timestamp'),
                    "last_accessed_at": federation_data.get('timestamp'),
                    "last_modified_at": federation_data.get('timestamp')
                },
                "configuration_metadata": {
                    "registry_config": {
                        "federation_settings": {
                            "max_rounds": 100,
                            "convergence_threshold": 0.0005,
                            "participation_timeout": 7200,
                            "model_validation_enabled": True
                        },
                        "privacy_settings": {
                            "differential_privacy": True,
                            "epsilon": 0.5,
                            "delta": 0.00001,
                            "secure_aggregation": True
                        },
                        "performance_settings": {
                            "parallel_processing": True,
                            "max_concurrent_orgs": 8,
                            "resource_monitoring": True
                        }
                    },
                    "registry_metadata": {
                        "federation_purpose": f"{federation_data.get('equipment_type', 'Equipment')} performance optimization across facilities",
                        "business_value": f"Expected {federation_data.get('expected_improvement', 20)}% improvement in efficiency",
                        "success_criteria": f"Achieve {federation_data.get('target_accuracy', 95)}% accuracy in performance prediction",
                        "expected_completion": None
                    },
                    "custom_attributes": {
                        "industry_sector": federation_data.get('industry_sector', 'water_management'),
                        "equipment_type": federation_data.get('equipment_type', 'unknown'),
                        "optimization_target": "performance_and_efficiency",
                        "collaboration_model": "vertical"
                    },
                    "tags": {
                        "technical": [federation_data.get('equipment_type', 'equipment'), "performance", "efficiency", "federated_learning", "twin_driven", "privacy_preserving"],
                        "business": ["optimization", "cost_savings", "sustainability"],
                        "compliance": ["GDPR", "industry_standards"],
                        "priority": [federation_data.get('priority', 'high')]
                    }
                },
                "relationships_dependencies": {
                    "relationships": {
                        "depends_on": {
                            "twin_registry": twin_registry_id
                        },
                        "enables": {}
                    },
                    "dependencies": {
                        "required_modules": ["twin_registry"],
                        "optional_modules": [],
                        "external_systems": []
                    },
                    "federation_instances": {}
                },
                "traceability_fields": {
                    "federation_rounds": {},
                    "organization_participation": {},
                    "model_evolution": {},
                    "privacy_compliance": {},
                    "performance_metrics": {},
                    "federation_algorithms": {}
                }
            }
            
            # Create federation using standard entity operation
            return await self.create_entity(entity_data, user_context)
            
        except Exception as e:
            self.logger.error(f"Failed to create federation from Twin Registry: {str(e)}")
            await self._audit_logger.log_activity(
                user_context.get('user_id'),
                "create_federation_from_twin_registry",
                "error",
                f"Failed to create federation from Twin Registry: {str(e)}"
            )
            return None
    
    async def create_hybrid_federation(
        self,
        integration_data: Dict[str, str],
        federation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[FederatedLearningRegistry]:
        """
        Create a hybrid federated learning registry entry with multiple integrations.
        
        Args:
            integration_data: Dictionary of integration IDs (aasx_integration_id, twin_registry_id, etc.)
            federation_data: Federation configuration and metadata
            user_context: User context for authorization and audit
            
        Returns:
            Created federation registry or None if creation failed
        """
        try:
            # Extract hybrid federation data with multiple integrations
            import uuid
            entity_data = {
                "registry_id": str(uuid.uuid4()),
                "federation_name": f"Fed_Hybrid_{federation_data.get('optimization_target', 'Unknown')}_{federation_data.get('timestamp', 'Unknown')}",
                "registry_name": f"{federation_data.get('optimization_target', 'System')} Optimization Federation",
                "federation_category": "hybrid",
                "federation_type": "hybrid",
                "federation_priority": federation_data.get('priority', 'critical'),
                "federation_version": "1.0.0",
                "registry_type": "hybrid",
                "workflow_source": "both",
                "user_id": user_context.get("user_id"),
                "org_id": user_context.get("org_id"),
                "dept_id": user_context.get("dept_id"),
                "integration_references": {
                    "aasx_integration_id": integration_data.get('aasx_integration_id'),
                    "twin_registry_id": integration_data.get('twin_registry_id'),
                    "kg_neo4j_id": integration_data.get('kg_neo4j_id'),
                    "physics_modeling_id": integration_data.get('physics_modeling_id'),
                    "ai_rag_id": integration_data.get('ai_rag_id'),
                    "certificate_manager_id": integration_data.get('certificate_manager_id')
                },
                "integration_status": "active",
                "overall_health_score": 95,
                "health_status": "healthy",
                "lifecycle_status": "active",
                "lifecycle_phase": "training",
                "operational_status": "running",
                "availability_status": "online",
                "federation_specific_status": {
                    "federation_participation_status": "in_progress",
                    "model_aggregation_status": "in_progress",
                    "privacy_compliance_status": "compliant",
                    "algorithm_execution_status": "running",
                    "last_federation_sync_at": federation_data.get('timestamp'),
                    "next_federation_sync_at": None,
                    "federation_sync_error_count": 0,
                    "federation_sync_error_message": None
                },
                "federation_data_metrics": {
                    "total_participating_twins": federation_data.get('participating_twins', 0),
                    "total_federation_rounds": federation_data.get('federation_rounds', 0),
                    "total_models_aggregated": federation_data.get('models_aggregated', 0),
                    "federation_complexity": "complex"
                },
                "performance_quality_metrics": {
                    "performance_score": 0.95,
                    "data_quality_score": 0.92,
                    "reliability_score": 0.90,
                    "compliance_score": 0.95
                },
                "enterprise_compliance_tracking": {
                    "compliance_framework": "GDPR",
                    "compliance_status": "compliant",
                    "last_audit_date": None,
                    "next_audit_date": None,
                    "audit_details": None,
                    "risk_level": "low"
                },
                "enterprise_security_metrics": {
                    "security_score": 95.0,
                    "threat_detection_score": 92.0,
                    "encryption_strength": "AES-256",
                    "authentication_method": "multi_factor",
                    "access_control_score": 95.0,
                    "data_protection_score": 95.0,
                    "incident_response_time": 10,
                    "security_audit_score": 95.0,
                    "last_security_scan": None,
                    "security_details": {
                        "encryption_enabled": True,
                        "key_rotation": "daily",
                        "last_key_update": None,
                        "threat_level": "low"
                    }
                },
                "enterprise_performance_analytics": {
                    "efficiency_score": 92.0,
                    "scalability_score": 90.0,
                    "optimization_potential": 95.0,
                    "bottleneck_identification": "model_convergence",
                    "performance_trend": "improving",
                    "last_optimization_date": None,
                    "optimization_suggestions": []
                },
                "security_access_control": {
                    "security_level": "confidential",
                    "access_control_level": "restricted",
                    "encryption_enabled": True,
                    "audit_logging_enabled": True
                },
                "user_management_ownership": {
                    "user_id": user_context.get('user_id'),
                    "org_id": user_context.get('org_id'),
                    "dept_id": user_context.get('dept_id'),
                    "owner_team": "AI_RAG_Research_Team",
                    "steward_user_id": user_context.get('steward_user_id')
                },
                "timestamps_audit": {
                    "created_at": federation_data.get('timestamp'),
                    "updated_at": federation_data.get('timestamp'),
                    "activated_at": federation_data.get('timestamp'),
                    "last_accessed_at": federation_data.get('timestamp'),
                    "last_modified_at": federation_data.get('timestamp')
                },
                "configuration_metadata": {
                    "registry_config": {
                        "federation_settings": {
                            "max_rounds": 200,
                            "convergence_threshold": 0.0001,
                            "participation_timeout": 10800,
                            "model_validation_enabled": True
                        },
                        "privacy_settings": {
                            "differential_privacy": True,
                            "epsilon": 0.3,
                            "delta": 0.000001,
                            "secure_aggregation": True
                        },
                        "performance_settings": {
                            "parallel_processing": True,
                            "max_concurrent_orgs": 15,
                            "resource_monitoring": True
                        }
                    },
                    "registry_metadata": {
                        "federation_purpose": f"{federation_data.get('optimization_target', 'System')} optimization across multiple industries using AI RAG analysis",
                        "business_value": f"Expected {federation_data.get('expected_improvement', 25)}% improvement in efficiency",
                        "success_criteria": f"Achieve {federation_data.get('target_accuracy', 98)}% accuracy in optimization prediction",
                        "expected_completion": None
                    },
                    "custom_attributes": {
                        "industry_sector": federation_data.get('industry_sector', 'multi_industry'),
                        "equipment_type": federation_data.get('equipment_type', 'energy_systems'),
                        "optimization_target": federation_data.get('optimization_target', 'energy_efficiency_and_cost_reduction'),
                        "collaboration_model": "hybrid"
                    },
                    "tags": {
                        "technical": [federation_data.get('optimization_target', 'optimization'), "ai_rag_driven", "multi_source_learning", "federated_learning", "hybrid_federation"],
                        "business": ["efficiency", "cost_reduction", "sustainability", "cross_industry_collaboration"],
                        "compliance": ["GDPR", "industry_standards"],
                        "priority": [federation_data.get('priority', 'critical')]
                    }
                },
                "relationships_dependencies": {
                    "relationships": {
                        "depends_on": {
                            "aasx_processing": integration_data.get('aasx_integration_id'),
                            "twin_registry": integration_data.get('twin_registry_id'),
                            "knowledge_graph": integration_data.get('kg_neo4j_id'),
                            "physics_modeling": integration_data.get('physics_modeling_id'),
                            "ai_rag": integration_data.get('ai_rag_id')
                        },
                        "enables": {}
                    },
                    "dependencies": {
                        "required_modules": ["aasx_processing", "twin_registry", "knowledge_graph", "physics_modeling", "ai_rag"],
                        "optional_modules": ["certificate_manager"],
                        "external_systems": []
                    },
                    "federation_instances": {}
                },
                "traceability_fields": {
                    "federation_rounds": federation_data.get('federation_rounds', {}),
                    "organization_participation": federation_data.get('organization_participation', {}),
                    "model_evolution": federation_data.get('model_evolution', {}),
                    "privacy_compliance": federation_data.get('privacy_compliance', {}),
                    "performance_metrics": federation_data.get('performance_metrics', {}),
                    "federation_algorithms": federation_data.get('federation_algorithms', {})
                }
            }
            
            # Create federation using standard entity operation
            return await self.create_entity(entity_data, user_context)
            
        except Exception as e:
            self.logger.error(f"Failed to create hybrid federation: {str(e)}")
            await self._audit_logger.log_activity(
                user_context.get('user_id'),
                "create_hybrid_federation",
                "error",
                f"Failed to create hybrid federation: {str(e)}"
            )
            return None
    
    async def update_federation_status(
        self,
        registry_id: str,
        status_updates: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Update federation status and lifecycle information.
        
        Args:
            registry_id: ID of the federation to update
            status_updates: Status updates to apply
            user_context: User context for authorization
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Prepare update data with current timestamp
            current_time = datetime.now().isoformat()
            update_data = {
                "updated_at": current_time,
                "last_modified_at": current_time,
                "last_accessed_at": current_time
            }
            
            # Update federation-specific status if provided
            if "federation_specific_status" in status_updates:
                update_data["federation_specific_status"] = status_updates["federation_specific_status"]
            
            # Update federation data metrics if provided
            if "federation_data_metrics" in status_updates:
                update_data["federation_data_metrics"] = status_updates["federation_data_metrics"]
            
            # Update performance metrics if provided
            if "performance_quality_metrics" in status_updates:
                update_data["performance_quality_metrics"] = status_updates["performance_quality_metrics"]
            
            # Update enterprise metrics if provided
            if "enterprise_performance_analytics" in status_updates:
                update_data["enterprise_performance_analytics"] = status_updates["enterprise_performance_analytics"]
            
            # Update traceability fields if provided
            if "traceability_fields" in status_updates:
                update_data["traceability_fields"] = status_updates["traceability_fields"]
            
            # Update configuration if provided
            if "configuration_metadata" in status_updates:
                update_data["configuration_metadata"] = status_updates["configuration_metadata"]
            
            # Update federation version if provided
            if "federation_version" in status_updates:
                update_data["federation_version"] = status_updates["federation_version"]
            
            # Update overall health score if provided
            if "overall_health_score" in status_updates:
                update_data["overall_health_score"] = status_updates["overall_health_score"]
                # Update health status based on score
                health_score = status_updates["overall_health_score"]
                if health_score >= 95:
                    update_data["health_status"] = "excellent"
                elif health_score >= 80:
                    update_data["health_status"] = "healthy"
                elif health_score >= 60:
                    update_data["health_status"] = "warning"
                else:
                    update_data["health_status"] = "critical"
            
            # Update lifecycle phase if provided
            if "lifecycle_phase" in status_updates:
                update_data["lifecycle_phase"] = status_updates["lifecycle_phase"]
            
            # Update operational status if provided
            if "operational_status" in status_updates:
                update_data["operational_status"] = status_updates["operational_status"]
            
            # Update availability status if provided
            if "availability_status" in status_updates:
                update_data["availability_status"] = status_updates["availability_status"]
            
            # Use standard entity update operation
            return await self.update_entity(registry_id, update_data, user_context)
            
        except Exception as e:
            self.logger.error(f"Failed to update federation status: {str(e)}")
            await self._audit_logger.log_activity(
                user_context.get('user_id'),
                "update_federation_status",
                "error",
                f"Failed to update federation status: {str(e)}"
            )
            return False
    
    async def get_federation_by_id(
        self,
        registry_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[FederatedLearningRegistry]:
        """
        Retrieve a federation by ID with authorization check.
        
        Args:
            registry_id: ID of the federation to retrieve
            user_context: User context for authorization
            
        Returns:
            Federation instance or None if not found or access denied
        """
        try:
            # Use standard entity retrieval operation
            federation = await self.get_entity(registry_id, user_context)
            
            if federation:
                # Log successful retrieval
                await self._audit_logger.log_activity(
                    user_context.get('user_id'),
                    "get_federation_by_id",
                    "success",
                    f"Successfully retrieved federation: {registry_id}"
                )
                
                # Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="federation_retrieved",
                    metric_value=1,
                    metadata={"registry_id": registry_id, "user_id": user_context.get('user_id')}
                )
                
                return federation
            else:
                # Log failed retrieval
                await self._audit_logger.log_activity(
                    user_context.get('user_id'),
                    "get_federation_by_id",
                    "not_found",
                    f"Federation not found: {registry_id}"
                )
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve federation: {str(e)}")
            await self._audit_logger.log_activity(
                user_context.get('user_id'),
                "get_federation_by_id",
                "error",
                f"Failed to retrieve federation: {str(e)}"
            )
            return None
    
    async def search_federations(
        self,
        search_criteria: Dict[str, Any],
        user_context: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[FederatedLearningRegistry]:
        """
        Search for federations based on criteria with authorization check.
        
        Args:
            search_criteria: Search criteria dictionary
            user_context: User context for authorization
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching federations
        """
        try:
            # Use standard entity search operation
            federations = await self.search_entities(search_criteria, user_context, limit, offset)
            
            if federations:
                # Log successful search
                await self._audit_logger.log_activity(
                    user_context.get('user_id'),
                    "search_federations",
                    "success",
                    f"Successfully searched federations, found {len(federations)} results"
                )
                
                # Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="federations_searched",
                    metric_value=len(federations),
                    metadata={"search_criteria": str(search_criteria), "user_id": user_context.get('user_id')}
                )
                
                return federations
            else:
                # Log search with no results
                await self._audit_logger.log_activity(
                    user_context.get('user_id'),
                    "search_federations",
                    "no_results",
                    f"Search completed with no results for criteria: {search_criteria}"
                )
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to search federations: {str(e)}")
            await self._audit_logger.log_activity(
                user_context.get('user_id'),
                "search_federations",
                "error",
                f"Failed to search federations: {str(e)}"
            )
            return []
    
    async def delete_federation(
        self,
        registry_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Delete a federation with authorization check.
        
        Args:
            registry_id: ID of the federation to delete
            user_context: User context for authorization
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Use standard entity deletion operation
            deletion_success = await self.delete_entity(registry_id, user_context)
            
            if deletion_success:
                # Log successful deletion
                await self._audit_logger.log_activity(
                    user_context.get('user_id'),
                    "delete_federation",
                    "success",
                    f"Successfully deleted federation: {registry_id}"
                )
                
                # Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="federation_deleted",
                    metric_value=1,
                    metadata={"registry_id": registry_id, "user_id": user_context.get('user_id')}
                )
                
                # Publish deletion event
                await self.event_bus.publish("federated_learning.deleted", {
                    "entity_id": registry_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                return True
            else:
                # Log failed deletion
                await self._audit_logger.log_activity(
                    user_context.get('user_id'),
                    "delete_federation",
                    "failed",
                    f"Failed to delete federation: {registry_id}"
                )
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete federation: {str(e)}")
            await self._audit_logger.log_activity(
                user_context.get('user_id'),
                "delete_federation",
                "error",
                f"Failed to delete federation: {str(e)}"
            )
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
                        roles=['admin', 'user', 'processor', 'federation_manager', 'viewer'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="federated_learning",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read federation summary")
                        return {"error": "Access denied"}
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    return {"error": "Access denied"}
                
                # ✅ REQUIRED: Get summary from repository
                summary = await self.repository.get_summary()
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="federation_summary_retrieved",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id") if user_context else "unknown"}
                )
                
                logger.info("Retrieved federation summary")
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

    # ✅ REQUIRED: Business Logic Methods (STAGE 2 IMPLEMENTATION)
    
    async def _validate_federation_data(
        self,
        federation_data: Dict[str, Any],
        user_context: Dict[str, Any],
        is_update: bool = False
    ) -> bool:
        """
        Validate federation data against business rules.
        
        Args:
            federation_data: Data to validate
            user_context: User context for validation
            is_update: Whether this is an update operation
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # Basic data structure validation
            if not federation_data or not isinstance(federation_data, dict):
                self.logger.warning("Federation data is empty or invalid")
                return False
            
            # Required field validation for creation
            if not is_update:
                required_fields = [
                    "federation_name", "registry_name", "federation_category", 
                    "federation_type", "federation_priority", "federation_version"
                ]
                
                for field in required_fields:
                    if field not in federation_data or not federation_data[field]:
                        self.logger.warning(f"Required field missing: {field}")
                        return False
            
            # Validate federation name format
            if "federation_name" in federation_data:
                federation_name = federation_data["federation_name"]
                if not isinstance(federation_name, str) or len(federation_name) < 3:
                    self.logger.warning("Federation name must be a string with at least 3 characters")
                    return False
            
            # Validate federation type
            valid_types = ["fedavg", "secure_aggregation", "hybrid", "federated_sgd"]
            if "federation_type" in federation_data:
                fed_type = federation_data["federation_type"]
                if fed_type not in valid_types:
                    self.logger.warning(f"Invalid federation type: {fed_type}. Must be one of {valid_types}")
                    return False
            
            # Validate federation category
            valid_categories = ["collaborative_learning", "privacy_preserving", "hybrid", "cross_industry"]
            if "federation_category" in federation_data:
                category = federation_data["federation_category"]
                if category not in valid_categories:
                    self.logger.warning(f"Invalid federation category: {category}. Must be one of {valid_categories}")
                    return False
            
            # Validate priority
            valid_priorities = ["low", "normal", "high", "critical"]
            if "federation_priority" in federation_data:
                priority = federation_data["federation_priority"]
                if priority not in valid_priorities:
                    self.logger.warning(f"Invalid federation priority: {priority}. Must be one of {valid_priorities}")
                    return False
            
            # Validate version format
            if "federation_version" in federation_data:
                version = federation_data["federation_version"]
                if not isinstance(version, str) or not re.match(r'^\d+\.\d+\.\d+$', version):
                    self.logger.warning("Federation version must be in format X.Y.Z")
                    return False
            
            # Validate numeric fields
            numeric_fields = ["overall_health_score", "performance_score", "data_quality_score"]
            for field in numeric_fields:
                if field in federation_data:
                    value = federation_data[field]
                    if not isinstance(value, (int, float)) or value < 0 or value > 100:
                        self.logger.warning(f"{field} must be a number between 0 and 100")
                        return False
            
            # Validate timestamp fields
            timestamp_fields = ["created_at", "updated_at", "activated_at"]
            for field in timestamp_fields:
                if field in federation_data:
                    timestamp = federation_data[field]
                    if timestamp and not self._is_valid_timestamp(timestamp):
                        self.logger.warning(f"Invalid timestamp format for {field}: {timestamp}")
                        return False
            
            # Validate integration references
            if "integration_references" in federation_data:
                refs = federation_data["integration_references"]
                if not isinstance(refs, dict):
                    self.logger.warning("Integration references must be a dictionary")
                    return False
            
            # Validate traceability fields
            if "traceability_fields" in federation_data:
                trace = federation_data["traceability_fields"]
                if not isinstance(trace, dict):
                    self.logger.warning("Traceability fields must be a dictionary")
                    return False
            
            # Business rule validation
            if not await self._validate_business_rules(federation_data, user_context, is_update):
                return False
            
            # User permission validation
            if not await self._validate_user_permissions(federation_data, user_context):
                return False
            
            self.logger.info("Federation data validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during federation data validation: {str(e)}")
            return False
    
    async def _validate_business_rules(
        self,
        federation_data: Dict[str, Any],
        user_context: Dict[str, Any],
        is_update: bool
    ) -> bool:
        """
        Validate federation data against business rules.
        
        Args:
            federation_data: Data to validate
            user_context: User context for validation
            is_update: Whether this is an update operation
            
        Returns:
            True if business rules passed, False otherwise
        """
        try:
            # Business rule 1: Federation name uniqueness (for creation only)
            if not is_update and "federation_name" in federation_data:
                federation_name = federation_data["federation_name"]
                # Check if federation name already exists (this would require a repository call)
                # For now, we'll validate the format and business rules
                if len(federation_name) > 100:
                    self.logger.warning("Federation name too long (max 100 characters)")
                    return False
            
            # Business rule 2: Priority-based validation
            if "federation_priority" in federation_data:
                priority = federation_data["federation_priority"]
                if priority == "critical":
                    # Critical federations require specific security settings
                    if "enterprise_security_metrics" in federation_data:
                        security = federation_data["enterprise_security_metrics"]
                        if security.get("encryption_strength") != "AES-256":
                            self.logger.warning("Critical federations must use AES-256 encryption")
                            return False
                        if security.get("authentication_method") != "multi_factor":
                            self.logger.warning("Critical federations must use multi-factor authentication")
                            return False
            
            # Business rule 3: Privacy-preserving federations validation
            if federation_data.get("federation_category") == "privacy_preserving":
                if "configuration_metadata" in federation_data:
                    config = federation_data["configuration_metadata"]
                    if "registry_config" in config:
                        registry_config = config["registry_config"]
                        if "privacy_settings" in registry_config:
                            privacy = registry_config["privacy_settings"]
                            if not privacy.get("differential_privacy", False):
                                self.logger.warning("Privacy-preserving federations must enable differential privacy")
                                return False
                            if not privacy.get("secure_aggregation", False):
                                self.logger.warning("Privacy-preserving federations must enable secure aggregation")
                                return False
            
            # Business rule 4: Hybrid federation validation
            if federation_data.get("federation_type") == "hybrid":
                if "integration_references" in federation_data:
                    refs = federation_data["integration_references"]
                    # Hybrid federations should have at least 2 integration sources
                    active_integrations = sum(1 for v in refs.values() if v is not None)
                    if active_integrations < 2:
                        self.logger.warning("Hybrid federations must have at least 2 active integration sources")
                        return False
            
            # Business rule 5: Performance threshold validation
            if "performance_quality_metrics" in federation_data:
                metrics = federation_data["performance_quality_metrics"]
                if "performance_score" in metrics:
                    score = metrics["performance_score"]
                    if score < 0.5:
                        self.logger.warning("Performance score below acceptable threshold (0.5)")
                        return False
            
            # Business rule 6: Compliance framework validation
            if "enterprise_compliance_tracking" in federation_data:
                compliance = federation_data["enterprise_compliance_tracking"]
                if "compliance_framework" in compliance:
                    framework = compliance["compliance_framework"]
                    if framework not in ["GDPR", "SOX", "HIPAA", "ISO27001"]:
                        self.logger.warning(f"Unsupported compliance framework: {framework}")
                        return False
            
            # Business rule 7: User organization validation
            if "user_management_ownership" in federation_data:
                ownership = federation_data["user_management_ownership"]
                if "org_id" in ownership and "dept_id" in ownership:
                    if not ownership["org_id"] or not ownership["dept_id"]:
                        self.logger.warning("Organization and department IDs are required")
                        return False
            
            # Business rule 8: Timestamp validation for updates
            if is_update:
                if "updated_at" in federation_data:
                    updated_at = federation_data["updated_at"]
                    if not self._is_valid_timestamp(updated_at):
                        self.logger.warning("Invalid updated_at timestamp format")
                        return False
            
            self.logger.info("Business rules validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during business rules validation: {str(e)}")
            return False
    
    async def _validate_user_permissions(
        self,
        federation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Validate user permissions for federation operations.
        
        Args:
            federation_data: Federation data to validate
            user_context: Federation data to validate
            
        Returns:
            True if user has required permissions, False otherwise
        """
        try:
            # Basic user context validation
            if not user_context:
                self.logger.warning("User context is required for permission validation")
                return False
            
            user_id = user_context.get('user_id')
            org_id = user_context.get('org_id')
            dept_id = user_context.get('dept_id')
            roles = user_context.get('roles', [])
            
            if not user_id:
                self.logger.warning("User ID is required for permission validation")
                return False
            
            # Permission 1: User can only create federations for their own organization
            if "user_management_ownership" in federation_data:
                ownership = federation_data["user_management_ownership"]
                fed_org_id = ownership.get('org_id')
                fed_dept_id = ownership.get('dept_id')
                
                if fed_org_id and fed_org_id != org_id:
                    self.logger.warning(f"User {user_id} cannot create federation for organization {fed_org_id}")
                    return False
                
                if fed_dept_id and fed_dept_id != dept_id:
                    # Check if user has cross-department permissions
                    if 'admin' not in roles and 'federation_manager' not in roles:
                        self.logger.warning(f"User {user_id} cannot create federation for department {fed_dept_id}")
                        return False
            
            # Permission 2: Critical federations require admin or federation_manager role
            if federation_data.get('federation_priority') == 'critical':
                if not any(role in ['admin', 'federation_manager'] for role in roles):
                    self.logger.warning(f"User {user_id} lacks permission to create critical federations")
                    return False
            
            # Permission 3: Privacy-preserving federations require data_steward role
            if federation_data.get('federation_category') == 'privacy_preserving':
                if 'data_steward' not in roles and 'admin' not in roles:
                    self.logger.warning(f"User {user_id} lacks permission to create privacy-preserving federations")
                    return False
            
            # Permission 4: Hybrid federations require advanced permissions
            if federation_data.get('federation_type') == 'hybrid':
                if not any(role in ['admin', 'federation_manager', 'ai_researcher'] for role in roles):
                    self.logger.warning(f"User {user_id} lacks permission to create hybrid federations")
                    return False
            
            # Permission 5: Check if user is the designated steward
            if "user_management_ownership" in federation_data:
                ownership = federation_data["user_management_ownership"]
                steward_id = ownership.get('steward_user_id')
                
                if steward_id and steward_id != user_id:
                    # Only admins can assign other users as stewards
                    if 'admin' not in roles:
                        self.logger.warning(f"User {user_id} cannot assign {steward_id} as steward")
                        return False
            
            # Permission 6: Organization-level restrictions
            if org_id:
                # Check if organization has federation capabilities enabled
                # This would typically require a call to organization service
                # For now, we'll assume all organizations can create federations
                pass
            
            # Permission 7: Department-level restrictions
            if dept_id:
                # Check if department has federation permissions
                # This would typically require a call to department service
                # For now, we'll assume all departments can create federations
                pass
            
            # Permission 8: Rate limiting check
            # Check if user has exceeded federation creation limits
            # This would require tracking user activity
            # For now, we'll assume no rate limiting
            
            self.logger.info(f"User permission validation passed for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during user permission validation: {str(e)}")
            return False
    
    def _is_valid_timestamp(self, timestamp: str) -> bool:
        """
        Validate if a string is a valid ISO timestamp format.
        
        Args:
            timestamp: Timestamp string to validate
            
        Returns:
            True if valid ISO timestamp, False otherwise
        """
        try:
            if not isinstance(timestamp, str):
                return False
            
            # Try to parse the timestamp
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
            
        except (ValueError, TypeError):
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

async def create_federated_learning_registry_service(connection_manager: ConnectionManager) -> FederatedLearningRegistryService:
    """
    Factory function to create and initialize a FederatedLearningRegistryService instance.
    
    Args:
        connection_manager: Database connection manager
        
    Returns:
        Initialized FederatedLearningRegistryService instance
        
    Raises:
        Exception: If service initialization fails
    """
    try:
        # Create service instance
        service = FederatedLearningRegistryService(connection_manager)
        
        # Initialize service
        if not await service.initialize_service():
            raise Exception(f"Failed to initialize {service.service_name}")
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create federated_learning_registry service: {e}")
        raise


# ✅ REQUIRED: Export the service class and factory
__all__ = ['FederatedLearningRegistryService', 'create_federated_learning_registry_service']
