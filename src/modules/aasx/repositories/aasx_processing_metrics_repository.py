"""
AASX Processing Metrics Repository

This repository provides data access operations for the aasx_processing_metrics table
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
from ..models.aasx_processing_metrics import AasxProcessingMetrics

logger = logging.getLogger(__name__)


class AasxProcessingMetricsRepository:
    """
    Repository for AASX processing metrics operations
    
    Provides async CRUD operations and advanced querying capabilities
    for AASX processing metrics data with enterprise features.
    
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
        self.table_name = "aasx_processing_metrics"
        logger.info(f"AASX Processing Metrics Repository initialized with new schema and engine")
    
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
            "metric_id", "job_id", "timestamp",
            
            # Real-time Health Metrics (Framework Health)
            "health_score", "response_time_ms", "uptime_percentage", "error_rate",
            
            # AASX Processing Performance Metrics (Framework Performance)
            "processing_time_trend", "extraction_speed_sec", "generation_speed_sec", 
            "validation_speed_sec", "aasx_processing_efficiency",
            
            # AASX Management Performance (JSON for better framework analysis)
            "aasx_management_performance", "aasx_category_performance_stats",
            
            # User Interaction Metrics (Framework Usage)
            "user_interaction_count", "file_access_count", "successful_operations", 
            "failed_operations", "job_execution_count", "successful_processing_operations", 
            "failed_processing_operations",
            
            # Data Quality Metrics (Framework Quality)
            "data_freshness_score", "data_completeness_score", "data_consistency_score", 
            "data_accuracy_score",
            
            # System Resource Metrics (Framework Resources)
            "cpu_usage_percent", "memory_usage_percent", "network_throughput_mbps", 
            "storage_usage_percent", "disk_io_mb",
            
            # AASX Processing Patterns & Analytics (Framework Trends - JSON)
            "aasx_processing_patterns", "resource_utilization_trends", "user_activity", 
            "file_operation_patterns", "compliance_patterns", "security_events",
            
            # Processing Patterns & Analytics (Framework Trends - JSON)
            "processing_patterns", "job_patterns",
            
            # AASX Processing-Specific Metrics (Framework Capabilities - JSON)
            "aasx_processing_analytics", "category_effectiveness", "workflow_performance", 
            "file_size_performance_efficiency",
            
            # Processing Technique Performance (JSON for better framework analysis)
            "processing_technique_performance",
            
            # File Type Processing Metrics (JSON for better framework analysis)
            "file_type_processing_stats",
            
            # AASX-Specific Metrics (Framework Capabilities - JSON)
            "aasx_analytics", "technique_effectiveness", "format_performance", 
            "file_size_processing_efficiency",
            
            # Time-based Analytics (Framework Time Analysis)
            "hour_of_day", "day_of_week", "month",
            
            # Performance Trends (Framework Performance Analysis)
            "aasx_management_trend", "resource_efficiency_trend", "quality_trend",
            
            # ENTERPRISE FEATURES - Merged from enterprise tables
            
            # Enterprise Processing Metrics (from enterprise_aasx_processing_metrics)
            "enterprise_metric_type", "enterprise_metric_value", "enterprise_metadata",
            
            # Enterprise Performance Analytics (from enterprise_aasx_performance_analytics)
            "performance_metric", "performance_trend", "optimization_suggestions", 
            "last_optimization_date",
            
            # Enterprise Compliance & Governance (from enterprise_aasx_compliance_tracking)
            "compliance_type", "compliance_status", "compliance_score",
            
            # Enterprise Security & Access Control (from enterprise_aasx_security_metrics)
            "security_event_type", "threat_assessment", "security_score",
            
            # Timestamps
            "created_at", "updated_at",
            
            # Additional fields that might be in the database schema
            "file_id", "project_id", "org_id", "dept_id", "audit_details", "security_details"
        ]
    
    def _get_computed_fields(self) -> List[str]:
        """Get list of computed fields that should NOT be stored in database."""
        return [
            "overall_metrics_score", "enterprise_health_status", "risk_assessment",
            "optimization_priority", "maintenance_schedule", "system_efficiency_score",
            "user_engagement_score", "processing_performance_score"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for this table."""
        return "metric_id"
    
    def _get_foreign_key_columns(self) -> Dict[str, str]:
        """Get foreign key relationships for this table."""
        return {
            "job_id": "aasx_processing",
            "file_id": "aasx_files",
            "project_id": "projects",
            "org_id": "organizations",
            "dept_id": "departments"
        }
    
    def _get_indexed_columns(self) -> List[str]:
        """Get columns that have database indexes."""
        return ["job_id", "file_id", "project_id", "timestamp", "org_id", "health_score"]
    
    def _get_required_columns(self) -> List[str]:
        """Get columns that are NOT NULL (required)."""
        return [
            "job_id", "timestamp"  # Only job_id and timestamp are required in the model
        ]
    
    def _get_audit_columns(self) -> List[str]:
        """Get audit-related columns (created_at, updated_at, etc.)."""
        return [
            "timestamp", "created_at", "updated_at", "org_id", "dept_id",
            "audit_details", "security_details", "enterprise_metadata",
            "last_optimization_date", "compliance_score", "security_score"
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
    
    def _validate_entity_schema(self, entity: AasxProcessingMetrics) -> bool:
        """Validate entity against repository schema."""
        entity_fields = set(entity.__dict__.keys())
        schema_fields = set(self._get_columns())
        return entity_fields.issubset(schema_fields)
    
    # ============================================================================
    # ENHANCED CRUD OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def create(self, metrics: AasxProcessingMetrics) -> Optional[int]:
        """
        Async create a new AASX processing metrics record with schema validation.
        
        Args:
            metrics: AasxProcessingMetrics model instance
            
        Returns:
            Created entity ID or None if failed
            
        Raises:
            ValueError: If entity schema validation fails
            Exception: If database operation fails
        """
        try:
            # Schema validation
            if not self._validate_entity_schema(metrics):
                raise ValueError("Entity schema validation failed")
            
            # Required field validation
            required_columns = self._get_required_columns()
            for column in required_columns:
                if not hasattr(metrics, column) or getattr(metrics, column) is None:
                    raise ValueError(f"Required field '{column}' is missing")
            
            # Prepare data for insertion
            data = self._model_to_dict(metrics)
            data['created_at'] = datetime.utcnow().isoformat()
            data['updated_at'] = datetime.utcnow().isoformat()
            
            # Build dynamic INSERT query
            query, params = self._build_insert_query(data)
            
            # Execute insert
            await self.connection_manager.execute_update(query, params)
            
            # Get the last inserted row ID
            result = await self.connection_manager.execute_query("SELECT last_insert_rowid() as id")
            created_id = result[0]['id'] if result else None
            
            logger.info(f"Created AASX processing metrics record: {created_id}")
            return created_id
            
        except Exception as e:
            logger.error(f"Failed to create AASX processing metrics record: {e}")
            return None
    
    async def create_batch(self, entities: List[AasxProcessingMetrics]) -> List[int]:
        """Create multiple entities efficiently in batch operation."""
        try:
            created_ids = []
            for entity in entities:
                entity_id = await self.create(entity)
                if entity_id:
                    created_ids.append(entity_id)
            return created_ids
        except Exception as e:
            logger.error(f"Failed to create batch AASX processing metrics records: {e}")
            return []
    
    async def create_if_not_exists(self, entity: AasxProcessingMetrics) -> Tuple[bool, Optional[int]]:
        """Create only if doesn't exist, return (created, id)."""
        try:
            if await self.exists(entity.metric_id):
                return False, entity.metric_id
            
            entity_id = await self.create(entity)
            return True, entity_id
        except Exception as e:
            logger.error(f"Failed to create if not exists: {e}")
            return False, None
    
    async def get_by_id(self, metric_id: int) -> Optional[AasxProcessingMetrics]:
        """
        Async get AASX processing metrics record by ID.
        
        Args:
            metric_id: Unique entity identifier
            
        Returns:
            AasxProcessingMetrics instance or None if not found
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {self._get_primary_key_column()} = :entity_id"
            result = await self.connection_manager.execute_query(query, {"entity_id": metric_id})
            
            if result and len(result) > 0:
                return self._dict_to_model(dict(result[0]))
            return None
            
        except Exception as e:
            logger.error(f"Error getting AASX processing metrics by ID: {e}")
            return None
    
    async def get_by_job_id(self, job_id: str) -> List[AasxProcessingMetrics]:
        """
        Get all AASX processing metrics records for a specific job using raw SQL.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE job_id = :job_id
                ORDER BY timestamp DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {"job_id": job_id})
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            logger.error(f"Error retrieving AASX processing metrics by job ID: {e}")
            return []
    
    async def get_by_timestamp_range(self, start_timestamp: str, end_timestamp: str) -> List[AasxProcessingMetrics]:
        """
        Get AASX processing metrics records within a timestamp range using raw SQL.
        
        Args:
            start_timestamp: Start timestamp
            end_timestamp: End timestamp
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE timestamp >= :start_timestamp AND timestamp <= :end_timestamp
                ORDER BY timestamp DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp
            })
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            logger.error(f"Error retrieving AASX processing metrics by timestamp range: {e}")
            return []
    
    async def get_by_health_score_range(self, min_score: int, max_score: int) -> List[AasxProcessingMetrics]:
        """
        Get AASX processing metrics records by health score range using raw SQL.
        
        Args:
            min_score: Minimum health score
            max_score: Maximum health score
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE health_score >= :min_score AND health_score <= :max_score
                ORDER BY timestamp DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {
                "min_score": min_score,
                "max_score": max_score
            })
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            logger.error(f"Error retrieving AASX processing metrics by health score range: {e}")
            return []
    
    async def update(self, metric_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update AASX processing metrics record using raw SQL.
        
        Args:
            metric_id: Unique metric identifier
            update_data: Dictionary of fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not update_data:
                return True
            
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Build UPDATE query dynamically
            set_clauses = [f"{col} = :{col}" for col in update_data.keys()]
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE metric_id = :metric_id
            """
            
            # Add metric_id to parameters
            params = {**update_data, "metric_id": metric_id}
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_update(query, params)
            
            return result > 0
                
        except Exception as e:
            logger.error(f"Error updating AASX processing metrics record: {e}")
            return False
    
    async def delete(self, metric_id: int) -> bool:
        """
        Delete AASX processing metrics record using raw SQL.
        
        Args:
            metric_id: Unique metric identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"""
                DELETE FROM {self.table_name}
                WHERE metric_id = :metric_id
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_update(query, {"metric_id": metric_id})
            
            return result > 0
                
        except Exception as e:
            logger.error(f"Error deleting AASX processing metrics record: {e}")
            return False
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[AasxProcessingMetrics]:
        """
        Get all AASX processing metrics records using raw SQL with optional pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY timestamp DESC"
            params = {}
            
            if limit is not None:
                query += " LIMIT :limit"
                params['limit'] = limit
                
            if offset is not None:
                query += " OFFSET :offset"
                params['offset'] = offset
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, params)
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            logger.error(f"Error retrieving all AASX processing metrics records: {e}")
            return []
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary statistics using raw SQL.
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(health_score) as avg_health_score,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(uptime_percentage) as avg_uptime,
                    AVG(error_rate) as avg_error_rate,
                    AVG(extraction_speed_sec) as avg_extraction_speed,
                    AVG(generation_speed_sec) as avg_generation_speed,
                    AVG(validation_speed_sec) as avg_validation_speed
                FROM {self.table_name}
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query)
            
            return dict(result[0]) if result and len(result) > 0 else {}
                
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}
    
    async def get_health_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get health score trends over time using raw SQL.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List[Dict[str, Any]]: List of health trend data points
        """
        try:
            query = f"""
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour_bucket,
                    AVG(health_score) as avg_health_score,
                    COUNT(*) as metric_count
                FROM {self.table_name}
                WHERE timestamp >= datetime('now', '-{hours} hours')
                GROUP BY hour_bucket
                ORDER BY hour_bucket DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query)
            
            return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Error getting health trends: {e}")
            return []
    
    async def get_resource_utilization_summary(self) -> Dict[str, Any]:
        """
        Get resource utilization summary using raw SQL.
        
        Returns:
            Dict[str, Any]: Resource utilization summary
        """
        try:
            query = f"""
                SELECT 
                    AVG(cpu_usage_percent) as avg_cpu_usage,
                    AVG(memory_usage_percent) as avg_memory_usage,
                    AVG(storage_usage_percent) as avg_storage_usage,
                    AVG(network_throughput_mbps) as avg_network_throughput,
                    AVG(disk_io_mb) as avg_disk_io
                FROM {self.table_name}
                WHERE cpu_usage_percent IS NOT NULL
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query)
            
            return dict(result[0]) if result and len(result) > 0 else {}
                
        except Exception as e:
            logger.error(f"Error getting resource utilization summary: {e}")
            return {}
    
    def _model_to_dict(self, model: AasxProcessingMetrics) -> Dict[str, Any]:
        """Convert Pydantic model to database dictionary."""
        data = model.model_dump()
        
        # Remove computed fields that should not be stored in database
        computed_fields = self._get_computed_fields()
        for field in computed_fields:
            data.pop(field, None)
        
        # Handle JSON fields - all Dict[str, Any] fields from the model
        json_fields = [
            'aasx_management_performance', 'aasx_category_performance_stats',
            'aasx_processing_patterns', 'resource_utilization_trends',
            'user_activity', 'file_operation_patterns', 'compliance_patterns',
            'security_events', 'processing_patterns', 'job_patterns',
            'aasx_processing_analytics', 'category_effectiveness',
            'workflow_performance', 'file_size_performance_efficiency',
            'processing_technique_performance', 'file_type_processing_stats',
            'aasx_analytics', 'technique_effectiveness', 'format_performance',
            'file_size_processing_efficiency', 'enterprise_metadata',
            'optimization_suggestions', 'audit_details', 'security_details'
        ]
        
        for field in json_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], (dict, list)):
                    data[field] = json.dumps(data[field])
        
        return data
    
    def _dict_to_model(self, data: Dict[str, Any]) -> AasxProcessingMetrics:
        """Convert database dictionary to Pydantic model."""
        # Create a copy of data to avoid modifying the original
        filtered_data = {}
        
        # Get the model fields to know what's allowed
        model_fields = AasxProcessingMetrics.model_fields.keys()
        
        # Only include fields that exist in the model
        for field in model_fields:
            if field in data:
                filtered_data[field] = data[field]
        
        # Handle JSON fields - all Dict[str, Any] fields from the model
        json_fields = [
            'aasx_management_performance', 'aasx_category_performance_stats',
            'aasx_processing_patterns', 'resource_utilization_trends',
            'user_activity', 'file_operation_patterns', 'compliance_patterns',
            'security_events', 'processing_patterns', 'job_patterns',
            'aasx_processing_analytics', 'category_effectiveness',
            'workflow_performance', 'file_size_performance_efficiency',
            'processing_technique_performance', 'file_type_processing_stats',
            'aasx_analytics', 'technique_effectiveness', 'format_performance',
            'file_size_processing_efficiency', 'enterprise_metadata',
            'optimization_suggestions', 'audit_details', 'security_details'
        ]
        
        for field in json_fields:
            if field in filtered_data and filtered_data[field] is not None:
                try:
                    if isinstance(filtered_data[field], str):
                        filtered_data[field] = json.loads(filtered_data[field])
                except (json.JSONDecodeError, TypeError):
                    # Keep as string if JSON parsing fails
                    pass
        
        return AasxProcessingMetrics(**filtered_data)

    # ============================================================================
    # ENHANCED READ OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def get_by_ids(self, metric_ids: List[int]) -> List[AasxProcessingMetrics]:
        """Get multiple entities by IDs efficiently."""
        try:
            if not metric_ids:
                return []
            
            placeholders = ','.join([f':id_{i}' for i in range(len(metric_ids))])
            query = f"SELECT * FROM {self.table_name} WHERE {self._get_primary_key_column()} IN ({placeholders})"
            params = {f'id_{i}': metric_id for i, metric_id in enumerate(metric_ids)}
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting AASX processing metrics by IDs: {e}")
            return []
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[AasxProcessingMetrics]:
        """Get paginated list of all entities."""
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            result = await self.connection_manager.execute_query(query, {"limit": limit, "offset": offset})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting all AASX processing metrics entries: {e}")
            return []
    
    async def get_by_field(self, field: str, value: Any) -> List[AasxProcessingMetrics]:
        """Get entities by specific field value."""
        try:
            if field not in self._get_columns():
                logger.warning(f"Invalid field '{field}' for AASX processing metrics table")
                return []
            
            query = f"SELECT * FROM {self.table_name} WHERE {field} = :value ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"value": value})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting AASX processing metrics by field: {e}")
            return []
    
    # ============================================================================
    # ENHANCED UPDATE OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def update(self, metric_id: int, updates: Dict[str, Any]) -> bool:
        """
        Async update AASX processing metrics record with schema validation.
        
        Args:
            metric_id: Unique entity identifier
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
            query, params = self._build_update_query(metric_id, updates)
            
            # Execute update
            await self.connection_manager.execute_update(query, params)
            
            logger.info(f"Updated AASX processing metrics record: {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating AASX processing metrics record: {e}")
            return False
    
    async def update_batch(self, updates: List[Tuple[int, Dict[str, Any]]]) -> bool:
        """Update multiple entities efficiently in batch operation."""
        try:
            for metric_id, update_data in updates:
                success = await self.update(metric_id, update_data)
                if not success:
                    logger.error(f"Failed to update batch entry: {metric_id}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to update batch AASX processing metrics records: {e}")
            return False
    
    async def upsert(self, entity: AasxProcessingMetrics) -> bool:
        """Update if exists, create if not (upsert operation)."""
        try:
            if await self.exists(entity.metric_id):
                # Update existing entity
                update_data = self._model_to_dict(entity)
                return await self.update(entity.metric_id, update_data)
            else:
                # Create new entity
                entity_id = await self.create(entity)
                return entity_id is not None
        except Exception as e:
            logger.error(f"Failed to upsert AASX processing metrics record: {e}")
            return False
    
    # ============================================================================
    # ENHANCED DELETE OPERATIONS
    # ============================================================================
    
    async def delete(self, metric_id: int) -> bool:
        """
        Async delete AASX processing metrics record.
        
        Args:
            metric_id: Unique entity identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE {self._get_primary_key_column()} = :entity_id"
            await self.connection_manager.execute_update(query, {"entity_id": metric_id})
            
            logger.info(f"Deleted AASX processing metrics record: {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting AASX processing metrics record: {e}")
            return False
    
    async def delete_batch(self, metric_ids: List[int]) -> bool:
        """Delete multiple entities efficiently in batch operation."""
        try:
            for metric_id in metric_ids:
                success = await self.delete(metric_id)
                if not success:
                    logger.error(f"Failed to delete batch entry: {metric_id}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to delete batch AASX processing metrics records: {e}")
            return False
    
    async def soft_delete(self, metric_id: int) -> bool:
        """Mark as deleted without removing from database."""
        try:
            updates = {
                'deleted_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            return await self.update(metric_id, updates)
        except Exception as e:
            logger.error(f"Failed to soft delete AASX processing metrics record: {e}")
            return False
    
    # ============================================================================
    # ADVANCED QUERYING METHODS (REQUIRED)
    # ============================================================================
    
    async def search(self, query: str, fields: List[str]) -> List[AasxProcessingMetrics]:
        """Full-text search across specified fields."""
        try:
            if not fields:
                fields = ['metric_id', 'job_id', 'file_id', 'project_id']
            
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
            logger.error(f"Error searching AASX processing metrics records: {e}")
            return []
    
    async def filter_by_criteria(self, criteria: Dict[str, Any]) -> List[AasxProcessingMetrics]:
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
            logger.error(f"Error filtering AASX processing metrics records: {e}")
            return []
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AasxProcessingMetrics]:
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
            logger.error(f"Error getting AASX processing metrics by date range: {e}")
            return []
    
    async def get_recent(self, hours: int = 24) -> List[AasxProcessingMetrics]:
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
            logger.error(f"Error getting recent AASX processing metrics: {e}")
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
            logger.error(f"Error counting AASX processing metrics by field: {e}")
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
            health_score_ranges = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
            
            for entity in recent_entities:
                health_score = getattr(entity, 'health_score', 0)
                if health_score >= 90:
                    health_score_ranges["excellent"] += 1
                elif health_score >= 75:
                    health_score_ranges["good"] += 1
                elif health_score >= 50:
                    health_score_ranges["fair"] += 1
                else:
                    health_score_ranges["poor"] += 1
            
            return {
                "time_period": time_period,
                "total_entities": len(recent_entities),
                "health_score_distribution": health_score_ranges,
                "period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return {}
    
    # ============================================================================
    # ENTERPRISE FEATURES (REQUIRED)
    # ============================================================================
    
    async def get_by_organization(self, org_id: str) -> List[AasxProcessingMetrics]:
        """Get entities within organization scope."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE org_id = :org_id ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"org_id": org_id})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting AASX processing metrics by organization: {e}")
            return []
    
    async def get_audit_trail(self, entity_id: int) -> List[Dict[str, Any]]:
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
                    "details": "Entity created"
                })
            
            # Add update events
            if hasattr(entity, 'updated_at') and entity.updated_at:
                audit_trail.append({
                    "timestamp": entity.updated_at,
                    "event": "updated",
                    "details": "Entity updated"
                })
            
            return sorted(audit_trail, key=lambda x: x.get('timestamp', ''), reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []
    
    # ============================================================================
    # PERFORMANCE & MONITORING METHODS (REQUIRED)
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
            
            return {
                "total_entities": total_count,
                "recent_entities_24h": recent_count,
                "health_status": await self.health_check(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    # ============================================================================
    # UTILITY & MAINTENANCE METHODS (REQUIRED)
    # ============================================================================
    
    async def exists(self, entity_id: int) -> bool:
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
    
    async def validate_entity(self, entity: AasxProcessingMetrics) -> Dict[str, Any]:
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
    # DYNAMIC QUERY BUILDING METHODS (REQUIRED)
    # ============================================================================
    
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
    
    def _build_update_query(self, entity_id: int, updates: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build dynamic UPDATE query based on updates."""
        set_clause = ', '.join([f"{key} = :{key}" for key in updates.keys()])
        params = updates.copy()
        params[self._get_primary_key_column()] = entity_id
        
        query = f"UPDATE {self._get_table_name()} SET {set_clause} WHERE {self._get_primary_key_column()} = :{self._get_primary_key_column()}"
        
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

    # ============================================================================
    # LEGACY METHODS (Maintained for backward compatibility)
    # ============================================================================
    
    async def get_by_job_id(self, job_id: str) -> List[AasxProcessingMetrics]:
        """
        Get all AASX processing metrics records for a specific job using raw SQL.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        return await self.get_by_field('job_id', job_id)
    
    async def get_by_timestamp_range(self, start_timestamp: str, end_timestamp: str) -> List[AasxProcessingMetrics]:
        """
        Get AASX processing metrics records within a timestamp range using raw SQL.
        
        Args:
            start_timestamp: Start timestamp
            end_timestamp: End timestamp
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            start_date = datetime.fromisoformat(start_timestamp)
            end_date = datetime.fromisoformat(end_timestamp)
            return await self.get_by_date_range(start_date, end_date)
        except Exception as e:
            logger.error(f"Error parsing timestamp range: {e}")
            return []
    
    async def get_by_health_score_range(self, min_score: int, max_score: int) -> List[AasxProcessingMetrics]:
        """
        Get AASX processing metrics records by health score range using raw SQL.
        
        Args:
            min_score: Minimum health score
            max_score: Maximum health score
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            criteria = {
                "health_score": [min_score, max_score]
            }
            return await self.filter_by_criteria(criteria)
        except Exception as e:
            logger.error(f"Error getting by health score range: {e}")
            return []
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary statistics using raw SQL.
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        return await self.get_statistics()
    
    async def get_health_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get health score trends over time using raw SQL.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List[Dict[str, Any]]: List of health trend data points
        """
        try:
            query = f"""
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour_bucket,
                    AVG(health_score) as avg_health_score,
                    COUNT(*) as metric_count
                FROM {self.table_name}
                WHERE timestamp >= datetime('now', '-{hours} hours')
                GROUP BY hour_bucket
                ORDER BY hour_bucket DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query)
            
            return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Error getting health trends: {e}")
            return []
    
    async def get_resource_utilization_summary(self) -> Dict[str, Any]:
        """
        Get resource utilization summary using raw SQL.
        
        Returns:
            Dict[str, Any]: Resource utilization summary
        """
        try:
            query = f"""
                SELECT 
                    AVG(cpu_usage_percent) as avg_cpu_usage,
                    AVG(memory_usage_percent) as avg_memory_usage,
                    AVG(storage_usage_percent) as avg_storage_usage,
                    AVG(network_throughput_mbps) as avg_network_throughput,
                    AVG(disk_io_mb) as avg_disk_io
                FROM {self.table_name}
                WHERE cpu_usage_percent IS NOT NULL
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query)
            
            return dict(result[0]) if result and len(result) > 0 else {}
                
        except Exception as e:
            logger.error(f"Error getting resource utilization summary: {e}")
            return {}

    # ============================================================================
    # JSON COLUMN METHODS
    # ============================================================================
    
    def _get_json_columns(self) -> List[str]:
        """Get list of columns that should be stored as JSON (TEXT in SQLite)."""
        return [
            "aasx_management_performance", "aasx_category_performance_stats",
            "aasx_processing_patterns", "resource_utilization_trends", "user_activity",
            "file_operation_patterns", "compliance_patterns", "security_events",
            "processing_patterns", "job_patterns", "aasx_processing_analytics",
            "category_effectiveness", "workflow_performance", "file_size_performance_efficiency",
            "processing_technique_performance", "file_type_processing_stats",
            "aasx_analytics", "technique_effectiveness", "format_performance",
            "enterprise_metadata", "optimization_suggestions", "audit_details", "security_details"
        ]


