#!/usr/bin/env python3
"""
AI RAG Registry Service

This service provides business logic and orchestration for AI RAG registry operations
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
    service = AIRagRegistryService(connection_manager)
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
from ..models.ai_rag_registry import AIRagRegistry
from ..repositories.ai_rag_registry_repository import AIRagRegistryRepository

logger = logging.getLogger(__name__)


class AIRagRegistryService:
    """
    Service for AI RAG registry business logic and orchestration
    
    Provides high-level business operations, workflow management, and
    enterprise features by leveraging the engine infrastructure.
    
    Enterprise Features (via Engine):
    - Business logic orchestration and workflow management
    - Enterprise-grade security and access control
    - Comprehensive validation and business rule enforcement
    - Performance monitoring and optimization
    - Event-driven architecture and async operations
    - Multi-tenant support with RBAC
    - Department-level access control (dept_id) (via engine)
    - Audit logging and compliance tracking
    - Error handling and recovery mechanisms
    
    Architecture:
    - Thin business logic layer that orchestrates engine components
    - Repository pattern for data access
    - Event-driven architecture for inter-service communication
    - Comprehensive monitoring and metrics collection
    - Role-based access control with multi-tenant support
    
    IMPORTANT: Organizational Hierarchy Requirements
    - If org_id is provided, dept_id MUST also be provided
    - This ensures proper access control and organizational isolation
    - Both fields are required for all registry operations
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
        self.repository = AIRagRegistryRepository(connection_manager)
        
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
        self.service_name = "ai_rag_registry"
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
                'max_file_size_mb': 1000,
                'allowed_file_types': ['.aasx', '.pdf', '.docx', '.dwg', '.step', '.json', '.yaml'],
                'processing_timeout_minutes': 60,
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
            'required_fields': ['registry_id', 'file_id', 'registry_name', 'registry_type', 'workflow_source', 'user_id', 'org_id', 'dept_id'],
            'business_specific': {
                # Add your module-specific business rules here
                'max_registries_per_org': 10000,
                'max_registries_per_dept': 1000,
                'naming_convention': "ai_rag_{timestamp}_{hash}",
                'compliance_requirements': ["GDPR", "SOX", "ISO27001", "IEC62443"]
            }
        }
    
    async def _initialize_security_context(self) -> Dict[str, Any]:
        """
        Initialize security context for the service.
        
        Returns:
            Dictionary containing security configuration and requirements
        """
        return {
            'service_name': 'AIRagRegistryService',
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
    
    # ⚠️ IMPORTANT: This is a POPULATION SERVICE - data comes from external systems!
    # 
    # This service needs to populate the AI RAG registry table from:
    # - ETL pipeline outputs
    # - AASX file processing
    # - Document processing systems
    # - External integrations
    #
    # ❌ DON'T: Use generic CRUD methods for everything
    # ✅ DO: Use domain-specific population methods for data integration
    
    # ✅ REQUIRED: Core Business Operations
    
    async def create_entity(
        self,
        entity_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[AIRagRegistry]:
        """
        Create a new AI RAG registry entity with comprehensive business logic validation.
        
        Args:
            entity_data: Data for the new registry entity
            user_context: User context for authorization and audit
            
        Returns:
            Created registry entity instance or None if creation failed
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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to create ai_rag")
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
                entity = AIRagRegistry(**entity_data)
                
                # ✅ REQUIRED: Save to repository
                if not await self.repository.create(entity):
                    logger.error("Failed to save entity to repository")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_registry_created",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ai_rag_registry.created", {
                    "entity_id": getattr(entity, 'registry_id', None),
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully created ai_rag_registry: {getattr(entity, 'registry_id', 'unknown')}")
                return entity
                
            except Exception as e:
                logger.error(f"Error creating ai_rag_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="create_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to create ai_rag_registry: {e}",
                    severity="medium",
                    metadata={"user_context": user_context}
                )
                return None
    
    async def get_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[AIRagRegistry]:
        """
        Retrieve an AI RAG registry entity by ID with authorization check.
        
        Args:
            entity_id: ID of the registry entity to retrieve
            user_context: User context for authorization
            
        Returns:
            Registry entity instance or None if not found or access denied
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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read ai_rag")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Retrieve from repository
                entity = await self.repository.get_by_id(entity_id)
                
                if not entity:
                    logger.warning(f"AI RAG registry entity not found: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_registry_retrieved",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                logger.info(f"Successfully retrieved ai_rag_registry: {entity_id}")
                return entity
                
            except Exception as e:
                logger.error(f"Error retrieving ai_rag_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="get_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to retrieve ai_rag_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return None
    
    async def update_entity(
        self,
        entity_id: str,
        update_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[AIRagRegistry]:
        """
        Update an AI RAG registry entity with authorization check.
        
        Args:
            entity_id: ID of the registry entity to update
            update_data: Data to update
            user_context: User context for authorization
            
        Returns:
            Updated registry entity instance or None if update failed
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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to update ai_rag")
                        return None
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return None
                
                # ✅ REQUIRED: Business validation
                if not await self._validate_entity_data(update_data, user_context, is_update=True):
                    logger.error("Update data validation failed")
                    return None
                
                # ✅ REQUIRED: Get existing entity first
                existing_entity = await self.repository.get_by_id(entity_id)
                if not existing_entity:
                    logger.error(f"Entity not found for update: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Update entity with new data
                for key, value in update_data.items():
                    if hasattr(existing_entity, key):
                        setattr(existing_entity, key, value)
                
                # ✅ REQUIRED: Update in repository
                if not await self.repository.update(existing_entity):
                    logger.error(f"Failed to update ai_rag_registry: {entity_id}")
                    return None
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_registry_updated",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ai_rag_registry.updated", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully updated ai_rag_registry: {entity_id}")
                return existing_entity
                
            except Exception as e:
                logger.error(f"Error updating ai_rag_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="update_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to update ai_rag_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return None
    
    async def delete_entity(
        self,
        entity_id: str,
        user_context: Dict[str, Any]
    ) -> bool:
        """
        Delete an AI RAG registry entity with authorization check.
        
        Args:
            entity_id: ID of the registry entity to delete
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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to delete ai_rag")
                        return False
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    logger.warning(f"Access denied for user {user_context.get('user_id') if user_context else 'unknown'}")
                    return False
                
                # ✅ REQUIRED: Delete from repository
                if not await self.repository.delete(entity_id):
                    logger.error(f"Failed to delete ai_rag_registry: {entity_id}")
                    return False
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_registry_deleted",
                    metric_value=1,
                    metadata={"user_id": user_context.get("user_id")}
                )
                
                # ✅ REQUIRED: Publish event
                await self.event_bus.publish("ai_rag_registry.deleted", {
                    "entity_id": entity_id,
                    "user_context": user_context,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully deleted ai_rag_registry: {entity_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting ai_rag_registry: {e}")
                await self.error_tracker.track_error(
                    error_type="delete_entity_error",
                    error_message=str(e),
                    error_details=f"Failed to delete ai_rag_registry {entity_id}: {e}",
                    severity="medium",
                    metadata={"entity_id": entity_id, "user_context": user_context}
                )
                return False
    
    async def get_all(self, user_context: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[AIRagRegistry]:
        """Get all AI RAG registry entities with pagination"""
        try:
            # Check authorization using existing method
            security_context = SecurityContext(
                user_id=user_context.get("user_id"),
                roles=user_context.get("roles", []),
                metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
            )
            
            auth_result = await self.auth_manager.check_permission(security_context, "ai_rag", "read")
            if not auth_result.allowed:
                raise PermissionError("User lacks permission to read ai_rag")
            
            # Get entities from repository
            entities = await self.repository.get_all(limit=limit, offset=offset)
            
            # Record metrics
            await self.metrics_collector.record_metric("ai_rag_registry_read_all", 1)
            
            return entities
            
        except Exception as e:
            await self.error_tracker.track_error("get_all_failed", str(e), user_context)
            raise
    
    async def search(self, query: str, user_context: Dict[str, Any], limit: int = 100) -> List[AIRagRegistry]:
        """Search AI RAG registry entities by query string"""
        try:
            # Check authorization using existing method
            security_context = SecurityContext(
                user_id=user_context.get("user_id"),
                roles=user_context.get("roles", []),
                metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
            )
            
            auth_result = await self.auth_manager.check_permission(security_context, "ai_rag", "read")
            if not auth_result.allowed:
                raise PermissionError("User lacks permission to read ai_rag")
            
            # Search entities from repository
            entities = await self.repository.search(query, limit=limit)
            
            # Record metrics
            await self.metrics_collector.record_metric("ai_rag_registry_search", 1)
            
            return entities
            
        except Exception as e:
            await self.error_tracker.track_error("search_failed", str(e), user_context)
            raise
    
    async def filter_by_criteria(self, criteria: Dict[str, Any], user_context: Dict[str, Any], limit: int = 100) -> List[AIRagRegistry]:
        """Filter AI RAG registry entities by criteria"""
        try:
            # Check authorization using existing method
            security_context = SecurityContext(
                user_id=user_context.get("user_id"),
                roles=user_context.get("roles", []),
                metadata={'org_id': user_context.get("org_id"), 'dept_id': user_context.get("dept_id")}
            )
            
            auth_result = await self.auth_manager.check_permission(security_context, "ai_rag", "read")
            if not auth_result.allowed:
                raise PermissionError("User lacks permission to read ai_rag")
            
            # Filter entities from repository
            entities = await self.repository.filter_by_criteria(criteria, limit=limit)
            
            # Record metrics
            await self.metrics_collector.record_metric("ai_rag_registry_filter", 1)
            
            return entities
            
        except Exception as e:
            await self.error_tracker.track_error("filter_failed", str(e), user_context)
            raise

    # ✅ REQUIRED: Table Population Methods
    
    # 🚨 CRITICAL: This service MUST implement table population logic for AI RAG registry!
    # These methods will be filled in STEP 2 with actual implementation.
    
    async def populate_registry_after_aasx_processing(self, aasx_processing_data: Dict[str, Any]) -> bool:
        """
        Populate AI RAG registry table after successful AASX ETL processing.
        
        Called by AASX module after ETL completion - no pre-registration needed.
        This method transforms AASX processing results into comprehensive registry data
        with file paths, storage information, and detailed metadata.
        
        Args:
            aasx_processing_data: Complete AASX processing results from ETL
                - file_id: Source file identifier
                - project_id: Project identifier
                - job_id: Processing job identifier
                - extracted_content: Documents and content extracted
                - metadata: File and processing metadata
                - processing_stats: Processing statistics and quality metrics
                
        Returns:
            True if population successful, False otherwise
        """
        try:
            logger.info("🚀 Starting AI RAG registry population from AASX processing")
            
            # Extract key data from AASX processing results
            file_id = aasx_processing_data.get('file_id')
            project_id = aasx_processing_data.get('project_id')
            job_id = aasx_processing_data.get('job_id')
            extracted_content = aasx_processing_data.get('extracted_content', {})
            metadata = aasx_processing_data.get('metadata', {})
            processing_stats = aasx_processing_data.get('processing_stats', {})
            
            if not file_id:
                logger.error("Missing file_id in AASX processing data")
                return False
            
            # ✅ REQUIRED: Validate organizational hierarchy
            org_id = aasx_processing_data.get('org_id')
            dept_id = aasx_processing_data.get('dept_id')
            
            if not org_id:
                logger.error("Missing org_id in AASX processing data")
                return False
            
            if not dept_id:
                logger.error("Missing dept_id in AASX processing data - required when org_id is present")
                return False
                
            # Generate registry ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            import hashlib
            hash_suffix = hashlib.md5(f"{file_id}_{timestamp}".encode()).hexdigest()[:8]
            registry_id = f"ai_rag_{timestamp}_{hash_suffix}"
            
            # Extract documents from AASX content
            documents = extracted_content.get('documents', [])
            if not documents:
                logger.warning(f"No documents found in AASX content for file {file_id}")
                return False
                
            # Build comprehensive documents_json structure
            documents_json = {}
            total_document_size = 0
            document_types = {}
            
            for idx, doc in enumerate(documents, 1):
                doc_id = f"doc_{idx:03d}"
                
                # Extract document metadata
                doc_name = doc.get('name', f'Document_{idx}')
                doc_type = doc.get('type', 'unknown')
                doc_size = doc.get('size', 0)
                doc_content = doc.get('content', '')
                
                # Build file paths based on project structure
                project_path = f"servo_motor_{datetime.now().strftime('%Y%m%d')}"
                base_paths = {
                    "aasx_source": f"/data/aasx/{project_path}",
                    "extracted": f"/data/extracted/{project_path}",
                    "processed": f"/data/processed/{project_path}",
                    "backup": f"/data/backup/{project_path}",
                    "archive": f"/data/archive/{project_path}"
                }
                
                # Build comprehensive document entry
                documents_json[doc_id] = {
                    "name": doc_name,
                    "type": doc_type,
                    "size": doc_size,
                    "content_preview": doc_content[:200] + "..." if len(doc_content) > 200 else doc_content,
                    "extraction_status": "completed",
                    "quality_score": doc.get('quality_score', 0.9),
                    "ocr_confidence": doc.get('ocr_confidence', 0.95),
                    "language_detected": doc.get('language', 'en'),
                    "page_count": doc.get('page_count', 1),
                    
                    # File paths & storage information
                    "file_paths": {
                        "original_source": f"{base_paths['aasx_source']}/{doc_name}",
                        "extracted_location": f"{base_paths['extracted']}/{doc_id}/",
                        "processed_location": f"{base_paths['processed']}/{doc_id}/",
                        "backup_location": f"{base_paths['backup']}/{doc_id}/",
                        "archive_location": f"{base_paths['archive']}/{doc_id}/"
                    },
                    "storage_info": {
                        "storage_type": "local_filesystem",
                        "storage_tier": "performance",
                        "replication_factor": 3,
                        "compression_enabled": True,
                        "encryption_enabled": True,
                        "checksum": f"sha256:{hashlib.sha256(doc_name.encode()).hexdigest()[:16]}...",
                        "file_permissions": "644"
                    },
                    "access_paths": {
                        "web_access": f"/api/documents/{doc_id}/content",
                        "download_path": f"/downloads/{project_path}/{doc_id}.{doc_type}",
                        "preview_path": f"/preview/{project_path}/{doc_id}",
                        "thumbnail_path": f"/thumbnails/{project_path}/{doc_id}.jpg"
                    },
                    "metadata": {
                        "author": metadata.get('author', 'Unknown'),
                        "created_date": metadata.get('created_date', datetime.now().strftime('%Y-%m-%d')),
                        "keywords": doc.get('keywords', []),
                        "security_classification": metadata.get('security_level', 'internal')
                    }
                }
                
                # Update counters
                total_document_size += doc_size
                if doc_type not in document_types:
                    document_types[doc_type] = {"count": 0, "total_size": 0, "documents": []}
                document_types[doc_type]["count"] += 1
                document_types[doc_type]["total_size"] += doc_size
                document_types[doc_type]["documents"].append(doc_id)
            
            # Build complete registry data structure
            registry_data = {
                # Primary Identification
                "registry_id": registry_id,
                "file_id": file_id,
                "registry_name": f"{metadata.get('title', 'Technical Documentation')} - AI RAG Registry",
                
                # Document Tracking (Enhanced with paths)
                "documents_json": documents_json,
                "document_count": len(documents),
                "document_types": document_types,
                "total_document_size": total_document_size,
                
                # Processing Details
                "processing_status": "completed",
                "file_type": "aasx",
                "processing_start_time": aasx_processing_data.get('processing_start_time'),
                "processing_end_time": aasx_processing_data.get('processing_end_time'),
                "processing_duration_ms": aasx_processing_data.get('processing_duration_ms', 0),
                "content_summary": metadata.get('summary', 'Technical documentation extracted from AASX file'),
                "extracted_text": extracted_content.get('text_content', ''),
                "quality_score": processing_stats.get('quality_score', 0.9),
                "confidence_score": processing_stats.get('confidence_score', 0.85),
                
                # Integration References
                "aasx_integration_id": job_id,
                "user_id": aasx_processing_data.get('processed_by', 'system'),
                "org_id": aasx_processing_data.get('org_id', 'default'),
                "dept_id": aasx_processing_data.get('dept_id'),
                
                # RAG Configuration
                "rag_category": "multimodal",
                "rag_type": "advanced",
                "rag_priority": "normal",
                "rag_version": "1.0.0",
                
                # Workflow Classification
                "registry_type": "extraction",
                "workflow_source": "aasx_file",
                
                # Note: Removed storage_config to keep service focused on core AI RAG functionality
                
                # Note: Removed file_system_info to keep service focused on core AI RAG functionality
                
                # Note: Removed path_security to keep service focused on core AI RAG functionality
                
                # Note: Removed file_operations to keep service focused on core AI RAG functionality
                
                # Note: Removed cloud_storage to keep service focused on core AI RAG functionality
                
                # Note: Removed path_monitoring to keep service focused on core AI RAG functionality
                
                # Timestamps
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Create and save the registry entry
            logger.info(f"📊 Creating AI RAG registry entry: {registry_id}")
            
            # Use the existing create_entity method
            user_context = {
                "user_id": aasx_processing_data.get('processed_by', 'system'),
                "org_id": aasx_processing_data.get('org_id', 'default'),
                "dept_id": aasx_processing_data.get('dept_id'),
                "roles": ['processor', 'system']
            }
            
            created_entity = await self.create_entity(registry_data, user_context)
            
            if created_entity:
                logger.info(f"✅ Successfully populated AI RAG registry: {registry_id}")
                
                # Publish event for other modules
                await self.event_bus.publish("ai_rag_registry.populated", {
                    "registry_id": registry_id,
                    "file_id": file_id,
                    "document_count": len(documents),
                    "timestamp": datetime.now().isoformat()
                })
                
                return True
            else:
                logger.error(f"❌ Failed to create AI RAG registry entry: {registry_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error populating AI RAG registry: {e}")
            await self.error_tracker.track_error(
                error_type="registry_population_error",
                error_message=str(e),
                error_details=f"Failed to populate AI RAG registry from AASX processing: {e}",
                severity="high",
                metadata={"aasx_processing_data": aasx_processing_data}
            )
            return False
    
    async def integrate_with_external_systems(self, external_data: Dict[str, Any]) -> bool:
        """
        REQUIRED: Integrate with external systems that provide data.
        
        This method will be implemented in STEP 2 to handle:
        - AASX processing integration
        - Twin registry integration
        - Knowledge graph integration
        - Document processing integration
        
        Args:
            external_data: Data from external systems
            
        Returns:
            True if integration successful, False otherwise
        """
        # TODO: IMPLEMENT IN STEP 2
        logger.info("integrate_with_external_systems method - TO BE IMPLEMENTED IN STEP 2")
        raise NotImplementedError("This method will be implemented in STEP 2 for external system integration!")
    
    async def handle_data_population_event(self, event_data: Dict[str, Any]) -> bool:
        """
        REQUIRED: Handle events that trigger table population.
        
        This method will be implemented in STEP 2 to handle:
        - File processing completion events
        - ETL pipeline completion events
        - System integration events
        - User action events
        
        Args:
            event_data: Event data that triggers population
            
        Returns:
            True if event handling successful, False otherwise
        """
        # TODO: IMPLEMENT IN STEP 2
        logger.info("handle_data_population_event method - TO BE IMPLEMENTED IN STEP 2")
        raise NotImplementedError("This method will be implemented in STEP 2 for event-driven population!")

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
                        logger.warning(f"User {user_context.get('user_id')} lacks permission to read ai_rag summary")
                        return {"error": "Access denied"}
                else:
                    auth_result = type('obj', (object,), {'allowed': False})()
                
                if not auth_result.allowed:
                    return {"error": "Access denied"}
                
                # ✅ REQUIRED: Get summary from repository
                summary = await self.repository.get_summary()
                
                # ✅ REQUIRED: Record metrics
                await self.metrics_collector.record_metric(
                    metric_name="ai_rag_registry_summary_retrieved",
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
            
            # ✅ REQUIRED: Required field validation - different logic for updates vs creates
            if is_update:
                # For updates, only validate fields that are actually being updated
                # Don't require registry_id, file_id, etc. since those are identifiers
                updateable_required_fields = [
                    'registry_name', 'registry_type', 'workflow_source', 
                    'user_id', 'org_id', 'dept_id'
                ]
                for field in updateable_required_fields:
                    if field in entity_data and entity_data[field] is None:
                        logger.error(f"Required field cannot be null: {field}")
                        return False
            else:
                # For creates, validate all required fields
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
            if 'total_document_size' in entity_data:
                max_size = self.business_config.get('default_rules', {}).get('max_file_size_mb', 1000)
                if entity_data['total_document_size'] > max_size * 1024 * 1024:  # Convert MB to bytes
                    logger.error(f"File size exceeds limit: {entity_data['total_document_size']} bytes")
                    return False
            
            # ✅ REQUIRED: Check organizational hierarchy - if org_id exists, dept_id must exist
            if entity_data.get('org_id') and not entity_data.get('dept_id'):
                logger.error("If org_id is provided, dept_id must also be provided for proper organizational hierarchy")
                return False
            
            # Check naming conventions
            if 'registry_name' in entity_data:
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

async def create_ai_rag_registry_service(connection_manager: ConnectionManager) -> AIRagRegistryService:
    """
    Factory function to create and initialize a AIRagRegistryService instance.
    
    Args:
        connection_manager: Database connection manager
        
    Returns:
        Initialized AIRagRegistryService instance
        
    Raises:
        Exception: If service initialization fails
    """
    try:
        # Create service instance
        service = AIRagRegistryService(connection_manager)
        
        # Initialize service
        if not await service.initialize_service():
            raise Exception(f"Failed to initialize {service.service_name}")
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create ai_rag_registry service: {e}")
        raise


# ✅ REQUIRED: Export the service class and factory
__all__ = ['AIRagRegistryService', 'create_ai_rag_registry_service']
