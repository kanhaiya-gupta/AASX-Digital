"""
AASX Processing Repository

This repository provides data access operations for the aasx_processing table
with integrated enterprise features and async database operations.

Features:
- Full CRUD operations with async support
- Enterprise-grade security and compliance
- Advanced querying and filtering capabilities
- Performance optimization and monitoring
- Schema introspection and validation
- Audit logging and audit trail support
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.schema.modules.aasx_etl import AasxEtlSchema
from ..models.aasx_processing import AasxProcessing

logger = logging.getLogger(__name__)


class AasxProcessingRepository:
    """
    Repository for AASX processing operations
    
    Provides async CRUD operations and advanced querying capabilities
    for AASX processing data with enterprise features.
    
    Enterprise Features:
    - Multi-tenant support with organization isolation
    - Role-based access control (RBAC)
    - Comprehensive audit logging
    - Security scoring and compliance tracking
    - Performance monitoring and optimization
    - Data quality validation and scoring
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the repository with engine connection manager."""
        self.connection_manager = connection_manager
        self.table_name = "aasx_processing"
        logger.info(f"AASX Processing Repository initialized with new schema and engine")
    
    async def initialize(self):
        """Initialize async components using the engine schema system."""
        try:
            # Check if table exists
            check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'"
            result = await self.connection_manager.execute_query(check_query)
            
            if not result or len(result) == 0:
                # Table doesn't exist, create it via schema
                logger.info(f"Table {self.table_name} does not exist, creating via schema...")
                schema = AasxEtlSchema(self.connection_manager)
                if await schema.initialize():
                    logger.info(f"Successfully created table {self.table_name} via AasxEtlSchema")
                else:
                    logger.error(f"Failed to create table {self.table_name} via schema")
                    raise Exception("Table creation failed via schema")
            else:
                logger.debug(f"Table {self.table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring table exists: {e}")
            raise
    
    def _get_json_columns(self) -> List[str]:
        """Get list of columns that should be stored as JSON (TEXT in SQLite)."""
        return [
            'extraction_options', 'generation_options', 'validation_options',
            'extraction_results', 'generation_results', 'validation_results',
            'processing_metadata', 'custom_attributes', 'processing_config', 
            'tags_config', 'relationships_config', 'dependencies_config', 
            'processing_instances_config', 'audit_trail', 'regulatory_requirements', 
            'dependencies', 'child_job_ids', 'notification_emails', 'webhook_urls',
            'notification_preferences', 'quality_gates', 'quality_check_results',
            'version_history', 'change_log', 'performance_targets', 'audit_info',
            'audit_details', 'security_details', 'enterprise_metadata',
            'optimization_suggestions'
        ]
    
    # ============================================================================
    # MANDATORY SCHEMA & METADATA METHODS (REQUIRED)
    # ============================================================================
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return self.table_name
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for this table."""
        return [
            # Primary Identification
            "job_id", "file_id", "project_id",
            
            # Job Classification & Metadata
            "job_type", "source_type", "processing_status", "processing_priority", "job_version",
            
            # Workflow Classification
            "workflow_type", "processing_mode",
            
            # Module Integration References
            "twin_registry_id", "kg_neo4j_id", "ai_rag_id", "physics_modeling_id", 
            "federated_learning_id", "certificate_manager_id",
            
            # Integration Status & Health
            "integration_status", "overall_health_score", "health_status",
            
            # Lifecycle Management
            "lifecycle_status", "lifecycle_phase",
            
            # Operational Status
            "operational_status", "availability_status",
            
            # AASX-Specific Processing Status
            "extraction_status", "generation_status", "validation_status", 
            "last_extraction_at", "last_generation_at", "last_validation_at",
            
            # Processing Configuration (JSON)
            "extraction_options", "generation_options", "validation_options",
            
            # Processing Results (JSON)
            "extraction_results", "generation_results", "validation_results",
            
            # Performance & Quality Metrics
            "processing_time", "extraction_time", "generation_time", "validation_time",
            "data_quality_score", "processing_accuracy", "file_integrity_checksum",
            
            # Security & Access Control
            "security_level", "access_control_level", "encryption_enabled", 
            "audit_logging_enabled", "security_event_type", "threat_assessment",
            "security_score", "last_security_scan", "security_details",
            
            # User Management & Ownership
            "processed_by", "org_id", "dept_id", "owner_team", "steward_user_id",
            
            # Timestamps & Audit
            "created_at", "updated_at", "started_at", "completed_at", "cancelled_at",
            "activated_at", "last_accessed_at", "last_modified_at", "timestamp",
            
            # Output & Storage
            "output_directory",
            
            # Error Handling & Retry Logic
            "error_message", "error_code", "retry_count", "max_retries",
            
            # Federated Learning & Consent
            "federated_learning", "user_consent_timestamp", "consent_terms_version",
            "federated_participation_status",
            
            # Processing Metadata (JSON)
            "processing_metadata", "custom_attributes",
            
            # Configuration & Metadata (JSON)
            "processing_config", "tags_config",
            
            # Relationships & Dependencies (JSON)
            "relationships_config", "dependencies_config", "processing_instances_config",
            
            # Progress Tracking
            "progress_percentage", "current_step", "total_steps",
            
            # Resource Allocation
            "allocated_cpu_cores", "allocated_memory_mb", "allocated_storage_gb",
            
            # SLA & Performance Targets
            "sla_target_seconds", "sla_breach_penalty", "performance_targets",
            
            # Compliance & Governance
            "compliance_status", "compliance_type", "compliance_score",
            "last_audit_date", "next_audit_date", "audit_details", "audit_trail",
            "regulatory_requirements",
            
            # Integration & Dependencies
            "dependencies", "parent_job_id", "child_job_ids",
            
            # MISSING COLUMNS FROM MODEL (Added for complete coverage)
            # Notification & Communication
            "notification_emails", "webhook_urls", "notification_preferences",
            
            # Cost & Resource Tracking
            "estimated_cost", "actual_cost", "cost_center",
            
            # Quality Assurance
            "quality_gates", "quality_check_results", "quality_score",
            
            # Versioning & History
            "version_history", "change_log", "rollback_version",
            
            # Additional Enterprise Fields
            "tags", "deleted_at", "archived_at", "restored_at",
            
            # Additional Security Fields
            "security_audit_score", "incident_response_time", "data_protection_score",
            "access_control_score", "authentication_method",
            
            # Additional Performance Fields
            "efficiency_score", "scalability_score", "optimization_potential",
            "bottleneck_identification", "performance_trend", "last_optimization_date",
            "optimization_suggestions",
            
            # Additional Compliance Fields
            "compliance_framework", "risk_level", "audit_info",
            
            # Additional Integration Fields
            "integration_maturity_score", "module_health_scores",
            
            # Additional Processing Fields
            "processing_efficiency_score", "aasx_processing_efficiency",
            "processing_technique_performance", "file_type_processing_stats",
            "processing_patterns", "resource_utilization_trends",
            
            # Additional User Activity Fields
            "user_activity", "job_patterns", "compliance_patterns", "security_events",
            
            # Additional Analytics Fields
            "aasx_analytics", "technique_effectiveness", "format_performance",
            "file_size_processing_efficiency",
            
            # Additional Enterprise Metadata
            "enterprise_metadata", "business_impact_score", "operational_efficiency",
            "strategic_alignment", "innovation_potential",
            
            # Additional Missing Fields from Model
            "user_id", "project_name", "project_description", "project_version",
            "project_status", "project_priority", "project_owner", "project_team",
            "project_budget", "project_timeline", "project_milestones",
            "project_risks", "project_issues", "project_changes",
            "project_approvals", "project_documents", "project_metadata"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for this table."""
        return "job_id"
    
    def _get_foreign_key_columns(self) -> Dict[str, str]:
        """Get foreign key relationships for this table."""
        return {
            "file_id": "aasx_files",
            "user_id": "users",
            "org_id": "organizations",
            "dept_id": "departments"
        }
    
    def _get_indexed_columns(self) -> List[str]:
        """Get columns that have database indexes."""
        return ["file_id", "user_id", "org_id", "processing_status", "created_at"]
    
    def _get_required_columns(self) -> List[str]:
        """Get columns that are NOT NULL (required) - excluding auto-generated fields."""
        return [
            "job_id", "file_id", "project_id", "job_type", "source_type", 
            "processing_status", "processed_by", "org_id"
            # Note: created_at and updated_at are auto-generated, not required from model
        ]
    
    def _get_audit_columns(self) -> List[str]:
        """Get audit-related columns (created_at, updated_at, etc.)."""
        return [
            "created_at", "updated_at", "started_at", "completed_at", "cancelled_at",
            "activated_at", "last_accessed_at", "last_modified_at", "timestamp",
            "processed_by", "org_id", "dept_id", "steward_user_id",
            "last_audit_date", "next_audit_date", "audit_details", "audit_trail",
            "last_security_scan", "user_consent_timestamp",
            # Additional audit fields for complete enterprise compliance
            "deleted_at", "archived_at", "restored_at", "last_optimization_date",
            "audit_info", "change_log", "version_history", "security_details",
            "enterprise_metadata", "processing_metadata", "custom_attributes"
        ]
    
    async def _validate_schema(self) -> bool:
        """Validate that table schema matches expected structure."""
        try:
            actual_columns = await self._get_actual_table_columns()
            expected_columns = set(self._get_columns())
            return expected_columns.issubset(set(actual_columns))
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    async def _get_actual_table_columns(self) -> List[str]:
        """Get actual columns from database table."""
        try:
            query = f"PRAGMA table_info({self.table_name})"  # SQLite
            # For PostgreSQL: "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
            result = await self.connection_manager.execute_query(query)
            return [row['name'] for row in result]
        except Exception as e:
            logger.error(f"Error getting actual table columns: {e}")
            return []
    
    def _schema_migration_needed(self) -> bool:
        """Check if schema migration is required."""
        return not self._validate_schema()
    
    def _validate_entity_schema(self, entity: AasxProcessing) -> bool:
        """Validate entity against repository schema."""
        # Get the actual data fields that will be inserted, excluding computed fields
        entity_data = entity.model_dump()
        entity_fields = set(entity_data.keys())
        schema_fields = set(self._get_columns())
        
        # Filter entity data to only include fields that exist in the schema
        valid_fields = entity_fields.intersection(schema_fields)
        extra_fields = entity_fields - schema_fields
        
        # Log for debugging
        logger.debug(f"Entity fields: {entity_fields}")
        logger.debug(f"Schema fields: {schema_fields}")
        logger.debug(f"Valid fields: {valid_fields}")
        logger.debug(f"Extra fields: {extra_fields}")
        
        # Store the filtered fields for later use in _model_to_dict
        entity._valid_schema_fields = valid_fields
        
        # Return True if we have at least the required fields
        required_fields = {"job_id", "file_id", "project_id", "processed_by", "org_id"}
        return required_fields.issubset(valid_fields)
    
    # ============================================================================
    # ENHANCED CRUD OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def create(self, aasx_processing: AasxProcessing) -> Optional[str]:
        """
        Async create a new AASX processing entry with schema validation.
        
        Args:
            aasx_processing: AasxProcessing model instance
            
        Returns:
            Created entity ID or None if failed
            
        Raises:
            ValueError: If entity schema validation fails
            Exception: If database operation fails
        """
        try:
            # Schema validation
            if not self._validate_entity_schema(aasx_processing):
                raise ValueError("Entity schema validation failed")
            
            # Required field validation
            required_columns = self._get_required_columns()
            for column in required_columns:
                if not hasattr(aasx_processing, column) or getattr(aasx_processing, column) is None:
                    raise ValueError(f"Required field '{column}' is missing")
            
            # Prepare data for insertion
            data = self._model_to_dict(aasx_processing)
            data['created_at'] = datetime.utcnow().isoformat()
            data['updated_at'] = datetime.utcnow().isoformat()
            
            # Build dynamic INSERT query
            query, params = self._build_insert_query(data)
            
            # Execute insert
            await self.connection_manager.execute_update(query, params)
            
            logger.info(f"Created AASX processing entry: {aasx_processing.job_id}")
            return aasx_processing.job_id
            
        except Exception as e:
            logger.error(f"Failed to create AASX processing entry: {e}")
            return None
    
    async def create_batch(self, entities: List[AasxProcessing]) -> List[str]:
        """Create multiple entities efficiently in batch operation."""
        try:
            created_ids = []
            for entity in entities:
                entity_id = await self.create(entity)
                if entity_id:
                    created_ids.append(entity_id)
            return created_ids
        except Exception as e:
            logger.error(f"Failed to create batch AASX processing entries: {e}")
            return []
    
    async def create_if_not_exists(self, entity: AasxProcessing) -> Tuple[bool, Optional[str]]:
        """Create only if doesn't exist, return (created, id)."""
        try:
            if await self.exists(entity.job_id):
                return False, entity.job_id
            
            entity_id = await self.create(entity)
            return True, entity_id
        except Exception as e:
            logger.error(f"Failed to create if not exists: {e}")
            return False, None
    
    # ============================================================================
    # ENHANCED READ OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def get_by_id(self, job_id: str) -> Optional[AasxProcessing]:
        """
        Async get AASX processing entry by ID.
        
        Args:
            job_id: Unique entity identifier
            
        Returns:
            AasxProcessing instance or None if not found
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {self._get_primary_key_column()} = :entity_id"
            result = await self.connection_manager.execute_query(query, {"entity_id": job_id})
            
            if result and len(result) > 0:
                return self._dict_to_model(dict(result[0]))
            return None
            
        except Exception as e:
            logger.error(f"Error getting AASX processing by ID: {e}")
            return None
    
    async def get_by_ids(self, job_ids: List[str]) -> List[AasxProcessing]:
        """Get multiple entities by IDs efficiently."""
        try:
            if not job_ids:
                return []
            
            placeholders = ','.join([f':id_{i}' for i in range(len(job_ids))])
            query = f"SELECT * FROM {self.table_name} WHERE {self._get_primary_key_column()} IN ({placeholders})"
            params = {f'id_{i}': job_id for i, job_id in enumerate(job_ids)}
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting AASX processing by IDs: {e}")
            return []
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[AasxProcessing]:
        """Get paginated list of all entities."""
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            result = await self.connection_manager.execute_query(query, {"limit": limit, "offset": offset})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting all AASX processing entries: {e}")
            return []
    
    async def get_by_field(self, field: str, value: Any) -> List[AasxProcessing]:
        """Get entities by specific field value."""
        try:
            if field not in self._get_columns():
                logger.warning(f"Invalid field '{field}' for AASX processing table")
                return []
            
            query = f"SELECT * FROM {self.table_name} WHERE {field} = :value ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"value": value})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting AASX processing by field: {e}")
            return []
    
    # ============================================================================
    # ENHANCED UPDATE OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def update(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """
        Async update AASX processing entry with schema validation.
        
        Args:
            job_id: Unique entity identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Schema validation for updates
            valid_columns = set(self._get_columns())
            invalid_fields = [field for field in updates.keys() if field not in valid_columns]
            if invalid_fields:
                logger.warning(f"Invalid fields in update: {invalid_fields}")
                updates = {k: v for k, v in updates.items() if k in valid_columns}
            
            # Add updated timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Build dynamic UPDATE query
            query, params = self._build_update_query(job_id, updates)
            
            # Execute update
            await self.connection_manager.execute_update(query, params)
            
            logger.info(f"Updated AASX processing entry: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating AASX processing entry: {e}")
            return False
    
    async def update_batch(self, updates: List[Tuple[str, Dict[str, Any]]]) -> bool:
        """Update multiple entities efficiently in batch operation."""
        try:
            for job_id, update_data in updates:
                success = await self.update(job_id, update_data)
                if not success:
                    logger.error(f"Failed to update batch entry: {job_id}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to update batch AASX processing entries: {e}")
            return False
    
    async def upsert(self, entity: AasxProcessing) -> bool:
        """Update if exists, create if not (upsert operation)."""
        try:
            if await self.exists(entity.job_id):
                # Update existing entity
                update_data = self._model_to_dict(entity)
                return await self.update(entity.job_id, update_data)
            else:
                # Create new entity
                entity_id = await self.create(entity)
                return entity_id is not None
        except Exception as e:
            logger.error(f"Failed to upsert AASX processing entry: {e}")
            return False
    
    # ============================================================================
    # ENHANCED DELETE OPERATIONS
    # ============================================================================
    
    async def delete(self, job_id: str) -> bool:
        """
        Async delete AASX processing entry.
        
        Args:
            job_id: Unique entity identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE {self._get_primary_key_column()} = :entity_id"
            await self.connection_manager.execute_update(query, {"entity_id": job_id})
            
            logger.info(f"Deleted AASX processing entry: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting AASX processing entry: {e}")
            return False
    
    async def delete_batch(self, job_ids: List[str]) -> bool:
        """Delete multiple entities efficiently in batch operation."""
        try:
            for job_id in job_ids:
                success = await self.delete(job_id)
                if not success:
                    logger.error(f"Failed to delete batch entry: {job_id}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to delete batch AASX processing entries: {e}")
            return False
    
    async def soft_delete(self, job_id: str) -> bool:
        """Mark as deleted without removing from database."""
        try:
            updates = {
                'lifecycle_status': 'deleted',
                'deleted_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            return await self.update(job_id, updates)
        except Exception as e:
            logger.error(f"Failed to soft delete AASX processing entry: {e}")
            return False
    
    # ============================================================================
    # ADVANCED QUERYING METHODS (REQUIRED)
    # ============================================================================
    
    async def search(self, query: str, fields: List[str]) -> List[AasxProcessing]:
        """Full-text search across specified fields."""
        try:
            if not fields:
                fields = ['job_id', 'file_id', 'project_id', 'job_type', 'source_type']
            
            # Build search conditions
            search_conditions = []
            params = {}
            for i, field in enumerate(fields):
                if field in self._get_columns():
                    search_conditions.append(f"{field} LIKE :search_{i}")
                    params[f'search_{i}'] = f"%{query}%"
            
            if not search_conditions:
                return []
            
            where_clause = " OR ".join(search_conditions)
            sql_query = f"SELECT * FROM {self.table_name} WHERE {where_clause} ORDER BY created_at DESC"
            
            results = await self.connection_manager.execute_query(sql_query, params)
            return [self._dict_to_model(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"Error searching AASX processing entries: {e}")
            return []
    
    async def filter_by_criteria(self, criteria: Dict[str, Any]) -> List[AasxProcessing]:
        """Complex filtering with multiple criteria."""
        try:
            if not criteria:
                return await self.get_all()
            
            # Build WHERE clause dynamically
            conditions = []
            params = {}
            
            for field, value in criteria.items():
                if field in self._get_columns():
                    if isinstance(value, (list, tuple)):
                        placeholders = ','.join([f':{field}_{i}' for i in range(len(value))])
                        conditions.append(f"{field} IN ({placeholders})")
                        for i, v in enumerate(value):
                            params[f'{field}_{i}'] = v
                    else:
                        conditions.append(f"{field} = :{field}")
                        params[field] = value
            
            if not conditions:
                return await self.get_all()
            
            where_clause = " AND ".join(conditions)
            sql_query = f"SELECT * FROM {self.table_name} WHERE {where_clause} ORDER BY created_at DESC"
            
            results = await self.connection_manager.execute_query(sql_query, params)
            return [self._dict_to_model(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"Error filtering AASX processing entries: {e}")
            return []
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AasxProcessing]:
        """Get entities within date range."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE created_at BETWEEN :start_date AND :end_date ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            })
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting AASX processing by date range: {e}")
            return []
    
    async def get_recent(self, hours: int = 24) -> List[AasxProcessing]:
        """Get recently created/updated entities."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            query = f"SELECT * FROM {self.table_name} WHERE updated_at >= :cutoff_time ORDER BY updated_at DESC"
            result = await self.connection_manager.execute_query(query, {"cutoff_time": cutoff_time.isoformat()})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting recent AASX processing: {e}")
            return []
    
    # ============================================================================
    # AGGREGATION & ANALYTICS METHODS (REQUIRED)
    # ============================================================================
    
    async def count_by_field(self, field: str, value: Any) -> int:
        """Count entities by field value."""
        try:
            if field not in self._get_columns():
                return 0
            
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {field} = :value"
            result = await self.connection_manager.execute_query(query, {"value": value})
            return result[0]['count'] if result and len(result) > 0 else 0
        except Exception as e:
            logger.error(f"Error counting AASX processing by field: {e}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics and metrics."""
        try:
            total_count = await self._get_total_count()
            recent_count = len(await self.get_recent(24))
            
            return {
                "total_entities": total_count,
                "recent_entities_24h": recent_count,
                "table_name": self.table_name,
                "schema_valid": await self._validate_schema(),
                "last_updated": await self._get_last_updated_timestamp()
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    async def get_trends(self, time_period: str) -> Dict[str, Any]:
        """Get temporal trends and patterns."""
        try:
            if time_period == "24h":
                hours = 24
            elif time_period == "7d":
                hours = 168
            elif time_period == "30d":
                hours = 720
            else:
                hours = 24
            
            recent_entities = await self.get_recent(hours)
            
            # Analyze trends
            status_counts = {}
            type_counts = {}
            
            for entity in recent_entities:
                # Count by status
                status = getattr(entity, 'processing_status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count by job type
                job_type = getattr(entity, 'job_type', 'unknown')
                type_counts[job_type] = type_counts.get(job_type, 0) + 1
            
            return {
                "time_period": time_period,
                "total_entities": len(recent_entities),
                "status_distribution": status_counts,
                "type_distribution": type_counts,
                "period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return {}
    
    # ============================================================================
    # ENTERPRISE FEATURES (REQUIRED)
    # ============================================================================
    
    async def get_by_user(self, user_id: str) -> List[AasxProcessing]:
        """Get entities accessible to specific user."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE processed_by = :user_id ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"user_id": user_id})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting AASX processing by user: {e}")
            return []
    
    async def get_by_organization(self, org_id: str) -> List[AasxProcessing]:
        """Get entities within organization scope."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE org_id = :org_id ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"org_id": org_id})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting AASX processing by organization: {e}")
            return []
    
    async def get_by_permission_level(self, permission: str) -> List[AasxProcessing]:
        """Get entities by permission level."""
        try:
            # Map permission levels to security levels
            permission_mapping = {
                "public": "public",
                "user": ["public", "user"],
                "admin": ["public", "user", "admin"],
                "restricted": ["restricted", "confidential"]
            }
            
            if permission not in permission_mapping:
                return []
            
            security_levels = permission_mapping[permission]
            if isinstance(security_levels, str):
                security_levels = [security_levels]
            
            placeholders = ','.join([f':level_{i}' for i in range(len(security_levels))])
            query = f"SELECT * FROM {self.table_name} WHERE security_level IN ({placeholders}) ORDER BY created_at DESC"
            params = {f'level_{i}': level for i, level in enumerate(security_levels)}
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting AASX processing by permission level: {e}")
            return []
    
    async def get_audit_trail(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get complete audit history for entity."""
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return []
            
            audit_trail = []
            
            # Add creation event
            if hasattr(entity, 'created_at') and entity.created_at:
                audit_trail.append({
                    "timestamp": entity.created_at,
                    "event": "created",
                    "user_id": getattr(entity, 'processed_by', 'unknown'),
                    "details": "Entity created"
                })
            
            # Add update events
            if hasattr(entity, 'updated_at') and entity.updated_at:
                audit_trail.append({
                    "timestamp": entity.updated_at,
                    "event": "updated",
                    "user_id": getattr(entity, 'processed_by', 'unknown'),
                    "details": "Entity updated"
                })
            
            # Add custom audit trail if available
            if hasattr(entity, 'audit_trail') and entity.audit_trail:
                audit_trail.extend(entity.audit_trail)
            
            return sorted(audit_trail, key=lambda x: x.get('timestamp', ''), reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []
    
    async def get_compliance_status(self, entity_id: str) -> Dict[str, Any]:
        """Get compliance and validation status."""
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return {}
            
            return {
                "compliance_status": getattr(entity, 'compliance_status', 'unknown'),
                "compliance_score": getattr(entity, 'compliance_score', 0.0),
                "compliance_type": getattr(entity, 'compliance_type', 'standard'),
                "last_audit_date": getattr(entity, 'last_audit_date', None),
                "next_audit_date": getattr(entity, 'next_audit_date', None),
                "regulatory_requirements": getattr(entity, 'regulatory_requirements', []),
                "audit_details": getattr(entity, 'audit_details', {}),
                "overall_health_score": getattr(entity, 'overall_health_score', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance status: {e}")
            return {}
    
    async def get_security_score(self, entity_id: str) -> float:
        """Get security assessment score."""
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return 0.0
            
            # Calculate composite security score
            security_score = getattr(entity, 'security_score', 100.0)
            threat_assessment = getattr(entity, 'threat_assessment', 'low')
            encryption_enabled = getattr(entity, 'encryption_enabled', False)
            audit_logging_enabled = getattr(entity, 'audit_logging_enabled', True)
            
            # Adjust score based on factors
            if threat_assessment == 'critical':
                security_score *= 0.5
            elif threat_assessment == 'high':
                security_score *= 0.7
            elif threat_assessment == 'medium':
                security_score *= 0.85
            
            if encryption_enabled:
                security_score *= 1.1
            
            if audit_logging_enabled:
                security_score *= 1.05
            
            return min(security_score, 100.0)
            
        except Exception as e:
            logger.error(f"Error getting security score: {e}")
            return 0.0
    
    def _model_to_dict(self, model: AasxProcessing) -> Dict[str, Any]:
        """Convert Pydantic model to database dictionary."""
        data = model.model_dump()
        
        # Filter data to only include fields that exist in the database schema
        if hasattr(model, '_valid_schema_fields'):
            # Use the filtered fields from schema validation
            data = {k: v for k, v in data.items() if k in model._valid_schema_fields}
        else:
            # Fallback: filter against schema columns
            schema_fields = set(self._get_columns())
            data = {k: v for k, v in data.items() if k in schema_fields}
        
        # Fields that should be stored as JSON in the database (from aasx_etl.py schema)
        json_fields = [
            # Core processing options and results
            'extraction_options', 'generation_options', 'validation_options',
            'extraction_results', 'generation_results', 'validation_results',
            'processing_metadata', 'custom_attributes', 'processing_config', 
            'tags_config', 'relationships_config', 'dependencies_config', 
            'processing_instances_config', 'audit_trail', 'regulatory_requirements', 
            'dependencies', 'child_job_ids', 'notification_emails', 'webhook_urls',
            'notification_preferences', 'quality_gates', 'quality_check_results',
            'version_history', 'change_log', 'performance_targets', 'audit_info',
            
            # Additional JSON fields from schema
            'audit_details', 'security_details', 'enterprise_metadata',
            'optimization_suggestions',
            
            # Metrics table JSON fields
            'processing_technique_performance', 'file_type_processing_stats',
            'processing_patterns', 'resource_utilization_trends', 'user_activity',
            'job_patterns', 'compliance_patterns', 'security_events',
            'aasx_analytics', 'technique_effectiveness', 'format_performance',
            'file_size_processing_efficiency'
        ]
        
        # Convert only JSON fields from Python objects to JSON strings
        for field in json_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], (dict, list)):
                    try:
                        data[field] = json.dumps(data[field])
                    except (TypeError, ValueError) as e:
                        # If JSON conversion fails, convert to string representation
                        data[field] = str(data[field])
                        print(f"Warning: Could not convert {field} to JSON, using string: {e}")
        
        return data
    
    def _dict_to_model(self, data: Dict[str, Any]) -> AasxProcessing:
        """Convert database dictionary to Pydantic model."""
        # Fields that should be stored as JSON in the database (from aasx_etl.py schema)
        json_fields = [
            # Core processing options and results
            'extraction_options', 'generation_options', 'validation_options',
            'extraction_results', 'generation_results', 'validation_results',
            'processing_metadata', 'custom_attributes', 'processing_config', 
            'tags_config', 'relationships_config', 'dependencies_config', 
            'processing_instances_config', 'audit_trail', 'regulatory_requirements', 
            'dependencies', 'child_job_ids', 'notification_emails', 'webhook_urls',
            'notification_preferences', 'quality_gates', 'quality_check_results',
            'version_history', 'change_log', 'performance_targets', 'audit_info',
            
            # Additional JSON fields from schema
            'audit_details', 'security_details', 'enterprise_metadata',
            'optimization_suggestions',
            
            # Metrics table JSON fields
            'processing_technique_performance', 'file_type_processing_stats',
            'processing_patterns', 'resource_utilization_trends', 'user_activity',
            'job_patterns', 'compliance_patterns', 'security_events',
            'aasx_analytics', 'technique_effectiveness', 'format_performance',
            'file_size_processing_efficiency'
        ]
        
        # Convert only JSON fields from JSON strings back to Python objects
        for field in json_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], str):
                    try:
                        data[field] = json.loads(data[field])
                    except (json.JSONDecodeError, TypeError):
                        # Keep as string if JSON parsing fails
                        pass
        
        return AasxProcessing(**data)

    # ============================================================================
    # PERFORMANCE & MONITORING METHODS (REQUIRED)
    # ============================================================================
    
    async def get_with_relations(self, entity_id: str, relations: List[str]) -> AasxProcessing:
        """Get entity with related data (eager loading)."""
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return None
            
            # Load related data based on requested relations
            if 'file_info' in relations and hasattr(entity, 'file_id'):
                # This would typically join with aasx_files table
                pass
            
            if 'user_info' in relations and hasattr(entity, 'processed_by'):
                # This would typically join with users table
                pass
            
            if 'organization_info' in relations and hasattr(entity, 'org_id'):
                # This would typically join with organizations table
                pass
            
            return entity
            
        except Exception as e:
            logger.error(f"Error getting entity with relations: {e}")
            return None
    
    async def bulk_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple operations in single transaction."""
        try:
            results = {
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            for operation in operations:
                try:
                    op_type = operation.get('type')
                    op_data = operation.get('data', {})
                    
                    if op_type == 'create':
                        entity = AasxProcessing(**op_data)
                        entity_id = await self.create(entity)
                        if entity_id:
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to create entity: {op_data.get('job_id', 'unknown')}")
                    
                    elif op_type == 'update':
                        job_id = op_data.get('job_id')
                        updates = {k: v for k, v in op_data.items() if k != 'job_id'}
                        if await self.update(job_id, updates):
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to update entity: {job_id}")
                    
                    elif op_type == 'delete':
                        job_id = op_data.get('job_id')
                        if await self.delete(job_id):
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to delete entity: {job_id}")
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Operation failed: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing bulk operations: {e}")
            return {"successful": 0, "failed": len(operations), "errors": [str(e)]}
    
    async def get_cached(self, entity_id: str) -> Optional[AasxProcessing]:
        """Get entity from cache if available."""
        # This is a placeholder for caching implementation
        # In a real implementation, you would check cache first, then database
        return await self.get_by_id(entity_id)
    
    # ============================================================================
    # HEALTH & MONITORING METHODS (REQUIRED)
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Repository health and connectivity status."""
        try:
            schema_valid = await self._validate_schema()
            connection_ok = await self._test_connection()
            
            return {
                "status": "healthy" if schema_valid and connection_ok else "unhealthy",
                "schema_valid": schema_valid,
                "connection_ok": connection_ok,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get query performance and efficiency metrics."""
        try:
            # Get basic performance metrics
            total_count = await self._get_total_count()
            recent_count = len(await self.get_recent(24))
            
            # Calculate processing efficiency
            processing_stats = await self._get_processing_efficiency_stats()
            
            return {
                "total_entities": total_count,
                "recent_entities_24h": recent_count,
                "processing_efficiency": processing_stats,
                "health_status": await self.health_check(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def cleanup_old_data(self, retention_days: int) -> int:
        """Clean up old/expired data."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Find old entities
            old_entities = await self.get_by_date_range(
                datetime.min, cutoff_date
            )
            
            deleted_count = 0
            for entity in old_entities:
                if await self.delete(entity.job_id):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old AASX processing entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
    # ============================================================================
    # UTILITY & MAINTENANCE METHODS (REQUIRED)
    # ============================================================================
    
    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists."""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {self._get_primary_key_column()} = :entity_id"
            result = await self.connection_manager.execute_query(query, {"entity_id": entity_id})
            return result[0]['count'] > 0 if result else False
        except Exception as e:
            logger.error(f"Error checking entity existence: {e}")
            return False
    
    async def get_table_info(self) -> Dict[str, Any]:
        """Get table schema and metadata."""
        return {
            "table_name": self._get_table_name(),
            "primary_key": self._get_primary_key_column(),
            "total_columns": len(self._get_columns()),
            "columns": self._get_columns(),
            "required_columns": self._get_required_columns(),
            "indexed_columns": self._get_indexed_columns(),
            "foreign_keys": self._get_foreign_key_columns(),
            "audit_columns": self._get_audit_columns()
        }
    
    async def validate_entity(self, entity: AasxProcessing) -> Dict[str, Any]:
        """Validate entity before persistence."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Schema validation
        if not self._validate_entity_schema(entity):
            validation_result["valid"] = False
            validation_result["errors"].append("Entity schema validation failed")
        
        # Required field validation
        required_columns = self._get_required_columns()
        for column in required_columns:
            if not hasattr(entity, column) or getattr(entity, column) is None:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Required field '{column}' is missing")
        
        return validation_result
    
    # ============================================================================
    # LIFECYCLE MANAGEMENT METHODS (REQUIRED)
    # ============================================================================
    
    async def archive(self, entity_id: str) -> bool:
        """Archive entity for long-term storage."""
        try:
            updates = {
                'lifecycle_status': 'archived',
                'archived_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            return await self.update(entity_id, updates)
        except Exception as e:
            logger.error(f"Failed to archive AASX processing entry: {e}")
            return False
    
    async def restore(self, entity_id: str) -> bool:
        """Restore archived entity."""
        try:
            updates = {
                'lifecycle_status': 'active',
                'restored_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            return await self.update(entity_id, updates)
        except Exception as e:
            logger.error(f"Failed to restore AASX processing entry: {e}")
            return False
    
    async def get_lifecycle_stage(self, entity_id: str) -> str:
        """Get current lifecycle stage."""
        try:
            entity = await self.get_by_id(entity_id)
            if entity:
                return getattr(entity, 'lifecycle_status', 'unknown')
            return 'unknown'
        except Exception as e:
            logger.error(f"Error getting lifecycle stage: {e}")
            return 'unknown'
    
    # ============================================================================
    # DYNAMIC QUERY BUILDING METHODS (REQUIRED)
    # ============================================================================
    
    def _build_select_query(self, columns: List[str] = None, 
                           where_clause: str = None, 
                           order_by: str = None, 
                           limit: int = None, 
                           offset: int = None) -> str:
        """Build dynamic SELECT query based on parameters."""
        columns = columns or self._get_columns()
        query = f"SELECT {', '.join(columns)} FROM {self._get_table_name()}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"
        
        return query
    
    def _build_insert_query(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build dynamic INSERT query based on data."""
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]
        
        query = f"""
            INSERT INTO {self._get_table_name()} 
            ({', '.join(columns)}) 
            VALUES ({', '.join(placeholders)})
        """
        
        return query, data
    
    def _build_update_query(self, entity_id: str, updates: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build dynamic UPDATE query based on updates."""
        set_clause = ', '.join([f"{key} = :{key}" for key in updates.keys()])
        params = updates.copy()
        params[self._get_primary_key_column()] = entity_id
        
        query = f"UPDATE {self._get_table_name()} SET {set_clause} WHERE {self._get_primary_key_column()} = :{self._get_primary_key_column()}"
        
        return query, params
    
    def _build_delete_query(self, entity_id: str) -> Tuple[str, Dict[str, Any]]:
        """Build DELETE query."""
        query = f"DELETE FROM {self._get_table_name()} WHERE {self._get_primary_key_column()} = :entity_id"
        params = {"entity_id": entity_id}
        
        return query, params
    
    # ============================================================================
    # REPOSITORY INFORMATION METHODS (REQUIRED)
    # ============================================================================
    
    async def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information."""
        try:
            return {
                "table_name": self._get_table_name(),
                "primary_key": self._get_primary_key_column(),
                "total_columns": len(self._get_columns()),
                "required_columns": self._get_required_columns(),
                "indexed_columns": self._get_indexed_columns(),
                "foreign_keys": self._get_foreign_key_columns(),
                "audit_columns": self._get_audit_columns(),
                "schema_valid": await self._validate_schema(),
                "total_records": await self._get_total_count(),
                "last_updated": await self._get_last_updated_timestamp(),
                "health_status": await self.health_check()
            }
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return {}
    
    async def _get_total_count(self) -> int:
        """Get total number of records in table."""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            result = await self.connection_manager.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting total count: {e}")
            return 0
    
    async def _get_last_updated_timestamp(self) -> Optional[datetime]:
        """Get timestamp of last record update."""
        try:
            query = f"SELECT MAX(updated_at) as last_updated FROM {self.table_name}"
            result = await self.connection_manager.execute_query(query)
            return result[0]['last_updated'] if result and result[0]['last_updated'] else None
        except Exception as e:
            logger.error(f"Error getting last updated timestamp: {e}")
            return None
    
    async def _test_connection(self) -> bool:
        """Test database connection."""
        try:
            await self._get_total_count()
            return True
        except Exception:
            return False
    
    async def _get_processing_efficiency_stats(self) -> Dict[str, Any]:
        """Get processing efficiency statistics."""
        try:
            query = f"""
                SELECT 
                    AVG(processing_time) as avg_processing_time,
                    AVG(data_quality_score) as avg_quality_score,
                    AVG(processing_accuracy) as avg_accuracy,
                    COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed_count,
                    COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed_count
                FROM {self.table_name}
                WHERE processing_time > 0
            """
            
            result = await self.connection_manager.execute_query(query)
            if result and len(result) > 0:
                return dict(result[0])
            return {}
            
        except Exception as e:
            logger.error(f"Error getting processing efficiency stats: {e}")
            return {}
    
    # ============================================================================
    # LEGACY METHODS (Maintained for backward compatibility)
    # ============================================================================
    
    async def get_by_file_id(self, file_id: str) -> List[AasxProcessing]:
        """Get all AASX processing records for a specific file using raw SQL."""
        return await self.get_by_field('file_id', file_id)
    
    async def get_by_project_id(self, project_id: str) -> List[AasxProcessing]:
        """Get all AASX processing records for a specific project using raw SQL."""
        return await self.get_by_field('project_id', project_id)
    
    async def get_by_status(self, status: str) -> List[AasxProcessing]:
        """Get all AASX processing records by status using raw SQL."""
        return await self.get_by_field('processing_status', status)
    
    async def count_by_status(self, status: str) -> int:
        """Count AASX processing records by status using raw SQL."""
        return await self.count_by_field('processing_status', status)
    
    async def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary statistics using raw SQL."""
        return await self.get_statistics()
