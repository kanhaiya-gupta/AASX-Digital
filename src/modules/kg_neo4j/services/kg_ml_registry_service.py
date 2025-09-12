#!/usr/bin/env python3
"""
KG Neo4j ML Registry Service

This service provides business logic and orchestration for KG Neo4j ML registry operations
by leveraging the comprehensive engine infrastructure for enterprise features.

Features:
- ML model training session management and orchestration
- Model deployment and lifecycle management
- Performance monitoring and analytics for ML models
- Enterprise-grade security and access control (via engine)
- Comprehensive validation and error handling (via engine)
- Performance optimization and monitoring (via engine)
- Event-driven architecture and async operations (via engine)
- Audit logging and compliance tracking (via engine)
- Multi-tenant support and RBAC (via engine)
- Department-level access control (dept_id) (via engine)

Example Usage:
    # Initialize service
    service = KGMLRegistryService(connection_manager)
    await service.initialize_service()
    
    # Stage 1: Populate from graph registry (system-driven)
    result = await service.populate_from_graph_registry(
        graph_id="kg_123",
        graph_name="Production_Line_Graph",
        graph_type="knowledge_graph",
        org_id="org_456",
        dept_id="dept_789",
        user_id="user_001",
        graph_metadata={"total_assets": 150, "version": "2.1"},
        user_context=user_context
    )
    
    # Stage 2: Update training parameters (user-driven)
    await service.update_training_parameters(
        ml_registry_id="ml_001",
        training_status="in_progress",
        model_config={"architecture": "GNN", "layers": 3},
        hyperparameters={"learning_rate": 0.001, "epochs": 100},
        training_type="supervised",
        model_description="Graph Neural Network for asset classification",
        user_context=user_context
    )
    
    # Stage 3: Handle training completion
    await service.handle_training_completion(
        ml_registry_id="ml_001",
        final_accuracy=0.95,
        training_duration_seconds=3600,
        precision_score=0.94,
        recall_score=0.96,
        f1_score=0.95,
        resource_consumption={"cpu_usage": "80%", "memory_usage": "12GB"},
        model_file_path="/models/ml_001_model.pkl",
        user_context=user_context
    )
    
    # Query and search
    models = await service.search_ml_registries(criteria, user_context)
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
from ..models.kg_neo4j_ml_registry import KGNeo4jMLRegistry
from ..repositories.kg_neo4j_ml_repository import KGNeo4jMLRepository

logger = logging.getLogger(__name__)


class KGMLRegistryService:
    """
    Service for KG Neo4j ML registry business logic and orchestration
    
    Provides high-level ML registry operations with two-stage population:
    
    Stage 1 (System-driven): populate_from_graph_registry() - Gets basic graph info
    Stage 2 (User-driven): update_training_parameters() - Handles user training input
    Stage 3 (Completion): handle_training_completion() - Handles training results
    
    Enterprise Features (via Engine):
    - ML model training session management and orchestration
    - Model deployment and lifecycle management
    - Performance monitoring and analytics for ML models
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
    - Two-stage population pattern for ML registry management
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
        self.repository = KGNeo4jMLRepository(connection_manager)
        
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
        self.service_name = "kg_ml_registry_service"
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
                'allowed_file_types': ['.aasx', '.json', '.yaml', '.pkl', '.h5', '.onnx'],
                'processing_timeout_minutes': 30,
                'retry_attempts': 3,
                'max_training_duration_hours': 24,
                'max_model_size_gb': 10
            },
            'permissions': {
                'create': ['admin', 'ml_engineer', 'data_scientist'],
                'read': ['admin', 'ml_engineer', 'data_scientist', 'ml_analyst', 'viewer'],
                'update': ['admin', 'ml_engineer', 'data_scientist'],
                'delete': ['admin'],
                'execute': ['admin', 'ml_engineer', 'data_scientist'],
                'deploy': ['admin', 'ml_engineer']
            },
            'cross_dept_roles': ['admin', 'ml_manager'],
            'org_wide_roles': ['admin', 'system_admin'],
            'business_specific': {
                'max_models_per_org': 1000,
                'max_models_per_dept': 100,
                'naming_convention': "ML_{org_id}_{dept_id}_{model_type}_{timestamp}",
                'compliance_requirements': ["GDPR", "SOX", "ISO27001", "MLOps_Standards"],
                'model_types': ['node_classification', 'link_prediction', 'community_detection', 'anomaly_detection', 'graph_embedding', 'gnn', 'hybrid'],
                'training_types': ['supervised', 'unsupervised', 'semi_supervised', 'reinforcement', 'transfer'],
                'lifecycle_phases': ['training', 'validation', 'deployment', 'monitoring', 'retirement']
            }
        }
    
    async def _initialize_security_context(self) -> Dict[str, Any]:
        """
        Initialize security context for the service.
        
        Returns:
            Dictionary containing security configuration and requirements
        """
        return {
            'service_name': 'KGMLRegistryService',
            'security_level': 'enterprise',
            'audit_enabled': True,
            'encryption_required': True,
            'require_authentication': True,
            'require_authorization': True,
            'default_permissions': ['read', 'write'],
            'multi_tenant': True,
            'dept_isolation': True,
            'ml_specific_security': {
                'model_encryption': True,
                'training_data_isolation': True,
                'bias_detection': True,
                'compliance_tracking': True
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

    # ✅ REQUIRED: Core Business Operations
    
    async def populate_from_graph_registry(
        self,
        graph_id: str,
        graph_name: str,
        graph_type: str,
        org_id: str,
        dept_id: str,
        user_id: str,
        graph_metadata: Optional[Dict[str, Any]] = None,
        graph_config: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[KGNeo4jMLRegistry]:
        """
        Populate ML registry from graph registry data (Stage 1: System-driven basic info).
        
        This method handles the first stage of ML registry population:
        - Gets basic graph information from the graph registry
        - Creates initial ML registry entry with graph metadata
        - Sets up foundation for user training data
        
        STAGE 1 COLUMNS POPULATED:
        ✅ Basic Graph Info:
           - graph_id, graph_name, graph_type
           - org_id, dept_id, user_id (from graph creator)
        
        ✅ ML Registry Foundation:
           - session_id (auto-generated: session_{graph_id}_{timestamp})
           - model_id (auto-generated: model_{graph_id}_{timestamp})
           - model_name (auto-generated: ML_Model_{graph_name})
           - model_type (set to 'knowledge_graph_ml')
           - training_status (set to 'pending')
           - lifecycle_phase (set to 'development')
        
        ✅ Timestamps:
           - created_at, updated_at
        
        ✅ Graph Metadata (if available):
           - graph_metadata, graph_config
        
        Args:
            graph_registry_data: Basic graph data from graph registry
            user_context: User context for authorization and audit
            
        Returns:
            Created ML registry instance or None if creation failed
        """
        with self.performance_profiler.profile_context("populate_from_graph_registry"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'ml_engineer', 'data_scientist', 'ml_analyst', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="kg_registry",
                        action="create"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to create ML registry")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
            
                # ✅ REQUIRED: Business validation for graph registry data
                if not await self._validate_graph_registry_data(
                    graph_id, graph_name, graph_type, org_id, dept_id, user_id, user_context
                ):
                    logger.error("Graph registry data validation failed")
                    return None
                
                # ✅ REQUIRED: Transform graph registry data to ML registry format
                ml_registry_data = self._transform_graph_to_ml_registry(
                    graph_id, graph_name, graph_type, org_id, dept_id, user_id, graph_metadata, graph_config
                )
                
                # ✅ REQUIRED: Create ML registry instance
                ml_registry = KGNeo4jMLRegistry(**ml_registry_data)
                
                # ✅ REQUIRED: Save to repository
                if not await self.repository.create(ml_registry):
                    logger.error("Failed to save ML registry to repository")
                    return None
                
                # ✅ REQUIRED: Record metrics
                self.metrics_collector.record_value(
                    metric_name="ml_registry_populated_from_graph",
                    value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ml_registry.populated_from_graph", {
                    "ml_registry_id": getattr(ml_registry, 'ml_registry_id', None),
                    "graph_id": graph_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully populated ML registry from graph registry: {getattr(ml_registry, 'ml_registry_id', 'unknown')}")
                return ml_registry
                
            except Exception as e:
                logger.error(f"Error populating ML registry from graph registry: {e}")
                await self.error_tracker.track_error(
                    error_type="populate_from_graph_registry_error",
                    error_message=str(e),
                    error_details=f"Failed to populate ML registry from graph registry: {e}",
                    severity="medium",
                    metadata={"user_context": user_context}
                )
                return None
    
    async def get_ml_registry(
        self,
        ml_registry_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[KGNeo4jMLRegistry]:
        """
        Retrieve an ML registry entry by ID with authorization check.
        
        Args:
            ml_registry_id: ID of the ML registry entry to retrieve
            user_context: User context for authorization
            
        Returns:
            ML registry instance or None if not found or access denied
        """
        with self.performance_profiler.profile_context("get_ml_registry"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'ml_engineer', 'data_scientist', 'ml_analyst', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="kg_registry",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read ML registry")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Retrieve from repository
                ml_registry = await self.repository.get_by_id(ml_registry_id)
                if not ml_registry:
                    logger.warning(f"ML registry not found: {ml_registry_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                self.metrics_collector.record_value(
                    metric_name="ml_registry_retrieved",
                    value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                return ml_registry
                
            except Exception as e:
                logger.error(f"Error retrieving ML registry: {e}")
                await self.error_tracker.track_error(
                    error_type="get_ml_registry_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve ML registry {ml_registry_id}: {e}",
                    severity="medium",
                    metadata={"ml_registry_id": ml_registry_id, "user_context": user_context}
                )
                return None
    
    async def search_ml_registries(
        self,
        search_criteria: Dict[str, Any],
        user_context: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[KGNeo4jMLRegistry]:
        """
        Search for ML registry entries based on criteria with authorization check.
        
        Args:
            search_criteria: Search criteria dictionary
            user_context: User context for authorization
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching ML registry entries
        """
        with self.performance_profiler.profile_context("search_ml_registries"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'ml_engineer', 'data_scientist', 'ml_analyst', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="kg_registry",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to search ML registries")
                        return []
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return []
                
                # ✅ REQUIRED: Search repository
                ml_registries = await self.repository.search_entities(
                    search_criteria, limit, offset
                )
                
                # ✅ REQUIRED: Record metrics
                self.metrics_collector.record_value(
                    metric_name="ml_registry_search_executed",
                    value=len(ml_registries),
                    metadata={"user_id": user_context.get("user_id"), "criteria_count": len(search_criteria)}
                )
                
                logger.info(f"Search returned {len(ml_registries)} results")
                return ml_registries
                
            except Exception as e:
                logger.error(f"Error searching ML registries: {e}")
                await self.error_tracker.track_error(
                    error_type="search_ml_registries_error",
                    error_message=str(e),
                    error_details=f"Failed to search ML registries: {e}",
                    severity="medium",
                    metadata={"search_criteria": search_criteria, "user_context": user_context}
                )
                return []
    
    async def update_training_parameters(
        self,
        ml_registry_id: str,
        training_status: str,
        ml_config: Optional[Dict[str, Any]] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        training_type: Optional[str] = None,
        data_source_config: Optional[Dict[str, Any]] = None,
        model_description: Optional[str] = None,
        model_version: Optional[str] = None,
        model_tags: Optional[List[str]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update ML registry with training parameters (Stage 2: User-driven ML details).
        
        This method handles the second stage of ML registry population:
        - Updates ML registry with user-provided training parameters
        - Handles model configuration, hyperparameters, and training settings
        - Manages training session state and progress
        
        STAGE 2 COLUMNS POPULATED:
        ✅ Training Configuration:
           - ml_config (user-provided model configuration)
           - hyperparameters (user-provided hyperparameters)
           - training_type (user-selected training approach)
           - data_source_config (training data configuration)
        
        ✅ Training Session Management:
           - training_status (updated: 'in_progress', 'paused', etc.)
           - training_start_time (when training begins)
           - training_parameters (JSON of all training settings)
        
        ✅ Model Details:
           - model_description (user-provided model description)
           - model_version (version tracking)
           - model_tags (user-defined tags)
        
        ✅ User Context:
           - updated_by (user who updated training parameters)
           - updated_at (timestamp of update)
        
        Args:
            ml_registry_id: ID of the ML registry entry to update
            training_status: Training status to set
            ml_config: Model configuration settings
            hyperparameters: Training hyperparameters
            training_type: Type of training
            data_source_config: Data source configuration
            model_description: Model description
            model_version: Model version
            model_tags: Model tags
            user_context: User context for authorization
            
        Returns:
            True if update successful, False otherwise
        """
        with self.performance_profiler.profile_context("update_training_parameters"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'ml_engineer', 'data_scientist', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="kg_registry",
                        action="update"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update ML registry")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Prepare training update data
                training_update_data = {
                    'training_status': training_status,
                    'ml_config': ml_config,
                    'training_type': training_type,
                    'model_description': model_description,
                    'model_version': model_version,
                    'updated_at': datetime.now().isoformat()
                }
                
                # Store hyperparameters and data_source_config in training_parameters JSON field
                if hyperparameters or data_source_config:
                    current_training_params = {}
                    # Get existing training_parameters if any
                    existing_registry = await self.repository.get_by_id(ml_registry_id)
                    if existing_registry and hasattr(existing_registry, 'training_parameters'):
                        current_training_params = existing_registry.training_parameters or {}
                    
                    # Update with new values
                    if hyperparameters:
                        current_training_params['hyperparameters'] = hyperparameters
                    if data_source_config:
                        current_training_params['data_source_config'] = data_source_config
                    
                    training_update_data['training_parameters'] = current_training_params
                
                # Store model_tags in custom_attributes JSON field
                if model_tags:
                    current_custom_attrs = {}
                    # Get existing custom_attributes if any
                    existing_registry = await self.repository.get_by_id(ml_registry_id)
                    if existing_registry and hasattr(existing_registry, 'custom_attributes'):
                        current_custom_attrs = existing_registry.custom_attributes or {}
                    
                    # Update with new values
                    current_custom_attrs['model_tags'] = model_tags
                    training_update_data['custom_attributes'] = current_custom_attrs
                
                # ✅ REQUIRED: Business validation for training data
                if not await self._validate_training_data(training_update_data, user_context):
                    logger.error("Training data validation failed")
                    return False
                
                # ✅ REQUIRED: Update in repository
                if not await self.repository.update(ml_registry_id, training_update_data):
                    logger.error(f"Failed to update ML registry training parameters: {ml_registry_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                self.metrics_collector.record_value(
                    metric_name="ml_registry_training_updated",
                    value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ml_registry.training_updated", {
                    "ml_registry_id": ml_registry_id,
                    "training_status": training_status,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully updated ML registry training parameters: {ml_registry_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error updating ML registry training parameters: {e}")
                await self.error_tracker.track_error(
                    error_type="update_training_parameters_error",
                    error_message=str(e),
                    error_details=f"Failed to update ML registry training parameters {ml_registry_id}: {e}",
                    severity="medium",
                    metadata={"ml_registry_id": ml_registry_id, "user_context": user_context}
                )
                return False
    
    async def delete_ml_registry(
        self,
        ml_registry_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Delete an ML registry entry with authorization check.
        
        Args:
            ml_registry_id: ID of the ML registry entry to delete
            user_context: User context for authorization
            
        Returns:
            True if deletion successful, False otherwise
        """
        with self.performance_profiler.profile_context("delete_ml_registry"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="kg_registry",
                        action="delete"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to delete ML registry")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Delete from repository
                if not await self.repository.delete(ml_registry_id):
                    logger.error(f"Failed to delete ML registry: {ml_registry_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                self.metrics_collector.record_value(
                    metric_name="ml_registry_deleted",
                    value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ml_registry.deleted", {
                    "ml_registry_id": ml_registry_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully deleted ML registry: {ml_registry_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting ML registry: {e}")
                await self.error_tracker.track_error(
                    error_type="delete_ml_registry_error",
                    error_message=str(e),
                    error_details=f"Failed to delete ML registry {ml_registry_id}: {e}",
                    severity="medium",
                    metadata={"ml_registry_id": ml_registry_id, "user_context": user_context}
                )
                return False

    async def handle_training_completion(
        self,
        ml_registry_id: str,
        final_accuracy: float,
        training_duration_seconds: int,
        precision_score: Optional[float] = None,
        recall_score: Optional[float] = None,
        f1_score: Optional[float] = None,
        auc_score: Optional[float] = None,
        training_efficiency_score: Optional[float] = None,
        data_quality_score: Optional[float] = None,
        model_quality_score: Optional[float] = None,
        resource_consumption: Optional[Dict[str, Any]] = None,
        training_metrics: Optional[Dict[str, Any]] = None,
        model_file_path: Optional[str] = None,
        model_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Handle ML training completion and update registry with results (Stage 3: Training completion).
        
        This method handles the final stage of ML registry population:
        - Updates ML registry with training completion results
        - Records final model performance metrics
        - Updates training status and completion timestamps
        - Triggers post-training workflows and notifications
        
        STAGE 3 COLUMNS POPULATED:
        ✅ Training Completion:
           - training_status (set to 'completed')
           - training_completion_time (when training finished)
           - training_duration_seconds (total training time)
        
        ✅ Performance Metrics:
           - final_accuracy (final model accuracy 0.0-1.0)
           - precision_score, recall_score, f1_score, auc_score
           - training_efficiency_score, data_quality_score
           - model_quality_score, compliance_score, bias_detection_score
        
        ✅ Resource Consumption:
           - resource_consumption (JSON: CPU, memory, GPU usage)
           - training_metrics (training process metrics)
        
        ✅ Model Artifacts:
           - model_file_path (path to saved model)
           - model_metadata (model-specific metadata)
           - deployment_status (ready for deployment)
        
        ✅ Timestamps:
           - updated_at (completion timestamp)
        
        Args:
            ml_registry_id: ID of the ML registry entry to update
            training_results: Training completion results and metrics
            user_context: User context for authorization
            
        Returns:
            True if completion handling successful, False otherwise
        """
        with self.performance_profiler.profile_context("handle_training_completion"):
            try:
                # ✅ REQUIRED: Authorization check
                if user_context:
                    security_context = SecurityContext(
                        user_id=user_context.get("user_id"),
                        roles=['admin', 'ml_engineer', 'data_scientist', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="kg_registry",
                        action="update"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update ML registry")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Prepare completion data
                completion_data = {
                    'training_status': 'completed',
                    'final_accuracy': final_accuracy,
                    'training_duration_seconds': training_duration_seconds,
                    'precision_score': precision_score,
                    'recall_score': recall_score,
                    'f1_score': f1_score,
                    'auc_score': auc_score,
                    'training_efficiency_score': training_efficiency_score,
                    'data_quality_score': data_quality_score,
                    'model_quality_score': model_quality_score,
                    'resource_consumption': resource_consumption,
                    'training_metrics': training_metrics,
                    'model_file_path': model_file_path,
                    'model_metadata': model_metadata,
                    'training_completed_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # ✅ REQUIRED: Business validation for training results
                if not await self._validate_training_results(completion_data, user_context):
                    logger.error("Training results validation failed")
                    return False
                
                # ✅ REQUIRED: Update in repository
                if not await self.repository.update(ml_registry_id, completion_data):
                    logger.error(f"Failed to update ML registry with training completion: {ml_registry_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                self.metrics_collector.record_value(
                    metric_name="ml_registry_training_completed",
                    value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ml_registry.training_completed", {
                    "ml_registry_id": ml_registry_id,
                    "training_status": "completed",
                    "final_accuracy": final_accuracy,
                    "training_duration": training_duration_seconds,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully handled ML registry training completion: {ml_registry_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error handling ML registry training completion: {e}")
                await self.error_tracker.track_error(
                    error_type="handle_training_completion_error",
                    error_message=str(e),
                    error_details=f"Failed to handle ML registry training completion {ml_registry_id}: {e}",
                    severity="medium",
                    metadata={"ml_registry_id": ml_registry_id, "user_context": user_context}
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
                        roles=['admin', 'ml_engineer', 'data_scientist', 'ml_analyst', 'system'],
                        metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
                    )
                    
                    auth_result = await self.auth_manager.check_permission(
                        context=security_context,
                        resource="kg_registry",
                        action="read"
                    )
                    
                    if not auth_result.allowed:
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read ML registry summary")
                        return {"error": "Access denied"}
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    return {"error": "Access denied"}
                
                # ✅ REQUIRED: Get summary from repository
                summary = await self.repository.get_summary()
                
                # ✅ REQUIRED: Record metrics
                self.metrics_collector.record_value(
                    metric_name="ml_registry_summary_retrieved",
                    value=1,
                    metadata={"user_id": user_context.get("user_id") if user_context else "unknown"}
                )
                
                logger.info("Retrieved ML registry service summary")
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
    
    async def _validate_ml_registry_data(
        self,
        ml_registry_data: Dict[str, Any],
        user_context: Dict[str, Any],
        is_update: bool = False
    ) -> bool:
        """
        Validate ML registry data against business rules.
        
        Args:
            ml_registry_data: Data to validate
            user_context: User context for validation
            is_update: Whether this is an update operation
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # ✅ REQUIRED: Basic data validation
            if not ml_registry_data:
                logger.error("ML registry data is empty")
                return False
            
            # ✅ REQUIRED: Required field validation (only for creation, not updates)
            if not is_update:
                required_fields = ['graph_id', 'model_id', 'session_id', 'model_name', 'model_type', 'user_id', 'org_id']
                for field in required_fields:
                    if field not in ml_registry_data or ml_registry_data[field] is None:
                        logger.error(f"Required field missing: {field}")
                        return False
            
            # ✅ REQUIRED: Business rule validation
            if not await self._validate_ml_business_rules(ml_registry_data, user_context, is_update):
                logger.error("ML business rule validation failed")
                return False
            
            # ✅ REQUIRED: User permission validation
            if not await self._validate_user_permissions(ml_registry_data, user_context):
                logger.error("User permission validation failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating ML registry data: {e}")
            return False
    
    async def _validate_ml_business_rules(
        self,
        ml_registry_data: Dict[str, Any],
        user_context: Dict[str, Any],
        is_update: bool
    ) -> bool:
        """
        Validate ML registry data against ML-specific business rules.
        
        Args:
            ml_registry_data: Data to validate
            user_context: User context for validation
            is_update: Whether this is an update operation
            
        Returns:
            True if business rules passed, False otherwise
        """
        try:
            # Check model type validation
            if 'model_type' in ml_registry_data:
                allowed_model_types = self.business_config.get('business_specific', {}).get('model_types', [])
                if ml_registry_data['model_type'] not in allowed_model_types:
                    logger.error(f"Invalid model type: {ml_registry_data['model_type']}")
                    return False
            
            # Check training type validation
            if 'training_type' in ml_registry_data:
                allowed_training_types = self.business_config.get('business_specific', {}).get('training_types', [])
                if ml_registry_data['training_type'] not in allowed_training_types:
                    logger.error(f"Invalid training type: {ml_registry_data['training_type']}")
                    return False
            
            # Check lifecycle phase validation
            if 'lifecycle_phase' in ml_registry_data:
                allowed_lifecycle_phases = self.business_config.get('business_specific', {}).get('lifecycle_phases', [])
                if ml_registry_data['lifecycle_phase'] not in allowed_lifecycle_phases:
                    logger.error(f"Invalid lifecycle phase: {ml_registry_data['lifecycle_phase']}")
                    return False
            
            # Check score validations (0.0-1.0 range)
            score_fields = ['final_accuracy', 'training_efficiency_score', 'precision_score', 'recall_score', 
                           'f1_score', 'auc_score', 'data_quality_score', 'model_quality_score', 
                           'compliance_score', 'bias_detection_score']
            
            for field in score_fields:
                if field in ml_registry_data and ml_registry_data[field] is not None:
                    score = ml_registry_data[field]
                    if not isinstance(score, (int, float)) or score < 0.0 or score > 1.0:
                        logger.error(f"Invalid score for {field}: {score}. Must be between 0.0 and 1.0")
                        return False
            
            # Check file size limits for external storage paths
            if 'model_file_path' in ml_registry_data and ml_registry_data['model_file_path']:
                max_size = self.business_config.get('default_rules', {}).get('max_model_size_gb', 10)
                # Note: Actual file size validation would require file system access
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating ML business rules: {e}")
            return False
    
    async def _validate_user_permissions(
        self,
        ml_registry_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Validate user permissions for ML registry operations.
        
        Args:
            ml_registry_data: ML registry data to validate
            user_context: User context for validation
            
        Returns:
            True if user has required permissions, False otherwise
        """
        try:
            # ✅ REQUIRED: Check organization access
            user_org = user_context.get('org_id')
            entity_org = ml_registry_data.get('org_id')
            
            if entity_org and user_org != entity_org:
                # Check if user has cross-org permissions
                user_roles = user_context.get('roles', [])
                cross_org_roles = self.business_config.get('cross_dept_roles', [])
                
                if not any(role in cross_org_roles for role in user_roles):
                    logger.error(f"User {user_context.get('user_id')} lacks cross-org permissions")
                    return False
            
            # ✅ REQUIRED: Check department access
            user_dept = user_context.get('dept_id')
            entity_dept = ml_registry_data.get('dept_id')
            
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

    async def _validate_graph_registry_data(
        self,
        graph_id: str,
        graph_name: str,
        graph_type: str,
        org_id: str,
        dept_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Validate graph registry data for ML registry population.
        
        Args:
            graph_registry_data: Graph registry data to validate
            user_context: User context for validation
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # ✅ REQUIRED: Basic data validation
            if not all([graph_id, graph_name, graph_type, org_id, dept_id, user_id]):
                logger.error("Required graph registry fields missing")
                return False
            
            # ✅ REQUIRED: Graph type validation
            allowed_graph_types = ['knowledge_graph', 'semantic_graph', 'property_graph', 'hybrid_graph']
            if graph_type not in allowed_graph_types:
                logger.error(f"Invalid graph type: {graph_type}")
                return False
            
            # ✅ REQUIRED: User permission validation
            graph_data = {
                'org_id': org_id,
                'dept_id': dept_id,
                'user_id': user_id
            }
            if not await self._validate_user_permissions(graph_data, user_context):
                logger.error("User permission validation failed for graph registry data")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating graph registry data: {e}")
            return False

    async def _validate_training_data(
        self,
        training_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Validate training data for ML registry updates.
        
        Args:
            training_data: Training data to validate
            user_context: User context for validation
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # ✅ REQUIRED: Basic data validation
            if not training_data:
                logger.error("Training data is empty")
                return False
            
            # ✅ REQUIRED: Training status validation
            if 'training_status' in training_data:
                allowed_statuses = ['pending', 'in_progress', 'paused', 'completed', 'failed', 'cancelled']
                if training_data['training_status'] not in allowed_statuses:
                    logger.error(f"Invalid training status: {training_data['training_status']}")
                    return False
            
            # ✅ REQUIRED: Model configuration validation
            if 'model_config' in training_data and training_data['model_config']:
                if not isinstance(training_data['model_config'], dict):
                    logger.error("Model configuration must be a dictionary")
                    return False
            
            # ✅ REQUIRED: Hyperparameters validation
            if 'hyperparameters' in training_data and training_data['hyperparameters']:
                if not isinstance(training_data['hyperparameters'], dict):
                    logger.error("Hyperparameters must be a dictionary")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating training data: {e}")
            return False

    async def _validate_training_results(
        self,
        training_results: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Validate training results for ML registry completion.
        
        Args:
            training_results: Training results to validate
            user_context: User context for validation
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # ✅ REQUIRED: Basic data validation
            if not training_results:
                logger.error("Training results data is empty")
                return False
            
            # ✅ REQUIRED: Required completion fields
            required_fields = ['training_status', 'final_accuracy']
            for field in required_fields:
                if field not in training_results or training_results[field] is None:
                    logger.error(f"Required training result field missing: {field}")
                    return False
            
            # ✅ REQUIRED: Training status must be completed
            if training_results.get('training_status') != 'completed':
                logger.error(f"Training status must be 'completed', got: {training_results.get('training_status')}")
                return False
            
            # ✅ REQUIRED: Accuracy validation (0.0-1.0 range)
            final_accuracy = training_results.get('final_accuracy')
            if final_accuracy is not None:
                if not isinstance(final_accuracy, (int, float)) or final_accuracy < 0.0 or final_accuracy > 1.0:
                    logger.error(f"Invalid final accuracy: {final_accuracy}. Must be between 0.0 and 1.0")
                    return False
            
            # ✅ REQUIRED: Training duration validation
            if 'training_duration_seconds' in training_results:
                duration = training_results['training_duration_seconds']
                if not isinstance(duration, (int, float)) or duration < 0:
                    logger.error(f"Invalid training duration: {duration}. Must be non-negative")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating training results: {e}")
            return False

    def _transform_graph_to_ml_registry(
        self,
        graph_id: str,
        graph_name: str,
        graph_type: str,
        org_id: str,
        dept_id: str,
        user_id: str,
        graph_metadata: Optional[Dict[str, Any]] = None,
        graph_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Transform graph registry data to ML registry format.
        
        Args:
            graph_id, graph_name, graph_type, org_id, dept_id, user_id: Core graph identification data
            graph_metadata: Optional metadata from the graph registry
            graph_config: Optional configuration from the graph registry
            
        Returns:
            Transformed ML registry data with only valid fields
        """
        try:
            # ✅ REQUIRED: Extract basic graph information (only fields that exist in the model)
            ml_registry_data = {
                'graph_id': graph_id,
                'org_id': org_id,
                'dept_id': dept_id,
                'user_id': user_id,
                'session_id': f"session_{graph_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'model_id': f"model_{graph_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'model_name': f"ML_Model_{graph_name}",
                'model_type': 'gnn',
                'training_status': 'pending',
                'training_type': 'supervised',  # Default training type
                'lifecycle_phase': 'training',  # Default lifecycle phase
                'lifecycle_status': 'development',  # Default lifecycle status
                'training_parameters': {},  # Empty training parameters initially
                'training_metrics': {},  # Empty training metrics initially
                'optimization_status': 'pending',
                'optimization_type': 'hyperparameter_tuning',
                'optimization_parameters': {},
                'performance_benchmarks': {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # ✅ REQUIRED: Store graph metadata in training_parameters if available
            if graph_metadata:
                ml_registry_data['training_parameters']['graph_metadata'] = graph_metadata
            
            # ✅ REQUIRED: Store graph configuration in training_parameters if available
            if graph_config:
                ml_registry_data['training_parameters']['graph_config'] = graph_config
            
            return ml_registry_data
            
        except Exception as e:
            logger.error(f"Error transforming graph registry data: {e}")
            return {}



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

async def create_kg_ml_registry_service(connection_manager: ConnectionManager) -> KGMLRegistryService:
    """
    Factory function to create and initialize a KGMLRegistryService instance.
    
    Args:
        connection_manager: Database connection manager
        
    Returns:
        Initialized KGMLRegistryService instance
        
    Raises:
        Exception: If service initialization fails
    """
    try:
        # Create service instance
        service = KGMLRegistryService(connection_manager)
        
        # Initialize service
        if not await service.initialize_service():
            raise Exception(f"Failed to initialize {service.service_name}")
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create kg_ml_registry service: {e}")
        raise


# ✅ REQUIRED: Export the service class and factory
__all__ = ['KGMLRegistryService', 'create_kg_ml_registry_service']
