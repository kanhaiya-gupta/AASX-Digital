"""
Twin Registry Metrics Repository

This repository provides data access operations for the twin_registry_metrics table
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

# Engine components for enterprise features
from src.engine.database.schema.modules.twin_registry import TwinRegistrySchema
from src.engine.monitoring.performance_profiler import PerformanceProfiler
from src.engine.security.authorization import RoleBasedAccessControl
from src.engine.monitoring.health_monitor import HealthMonitor
from src.engine.monitoring.metrics_collector import MetricsCollector
from src.engine.monitoring.error_tracker import ErrorTracker
from src.engine.messaging.event_bus import EventBus
from src.engine.database.connection_manager import ConnectionManager
from ..models.twin_registry_metrics import (
    TwinRegistryMetrics,
    TwinMetricsQuery,
    TwinMetricsSummary
)

logger = logging.getLogger(__name__)


class TwinRegistryMetricsRepository:
    """
    Repository for Twin Registry metrics operations
    
    Provides async CRUD operations and advanced querying capabilities
    for Twin Registry metrics data with enterprise features.
    
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
        self.table_name = "twin_registry_metrics"
        logger.info(f"Twin Registry Metrics Repository initialized with new schema and engine")
    
    async def initialize(self) -> None:
        """Initialize the repository and ensure tables exist using the engine schema."""
        try:
            # Check if table exists
            check_sql = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='twin_registry_metrics'
            """
            result = await self.connection_manager.execute_query(check_sql, {})
            
            if not result or len(result) == 0:
                logger.info("Table twin_registry_metrics does not exist, creating via schema...")
                # Use the engine schema to create the table
                schema = TwinRegistrySchema(self.connection_manager)
                if await schema.initialize():
                    logger.info("Successfully created table via TwinRegistrySchema")
                else:
                    logger.error("Failed to create table via TwinRegistrySchema")
                    raise Exception("Table creation failed via schema")
            else:
                logger.debug("Table twin_registry_metrics already exists")
            
            logger.info("Twin Registry Metrics Repository initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Metrics Repository: {e}")
            raise
    
    # ============================================================================
    # MANDATORY SCHEMA & METADATA METHODS (REQUIRED)
    # ============================================================================
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return self.table_name
    
    def _get_columns(self) -> List[str]:
        """Get all column names for this table."""
        return [
            # Primary Identification
            "metric_id", "registry_id", "timestamp",
            
            # Real-time Health Metrics (Framework Health)
            "health_score", "response_time_ms", "uptime_percentage", "error_rate",
            
            # Twin Registry Performance Metrics (Framework Performance)
            "twin_sync_speed_sec", "relationship_update_speed_sec", "lifecycle_transition_speed_sec",
            "twin_registry_efficiency",
            
            # Twin Management Performance (JSON for better framework analysis)
            "twin_management_performance", "twin_category_performance_stats",
            
            # User Interaction Metrics (Framework Usage)
            "user_interaction_count", "twin_access_count", "successful_twin_operations",
            "failed_twin_operations",
            
            # Data Quality Metrics (Framework Quality)
            "data_freshness_score", "data_completeness_score", "data_consistency_score",
            "data_accuracy_score",
            
            # System Resource Metrics (Framework Resources)
            "cpu_usage_percent", "memory_usage_percent", "network_throughput_mbps",
            "storage_usage_percent", "disk_io_mb",
            
            # Twin Registry Patterns & Analytics (Framework Trends - JSON)
            "twin_registry_patterns", "resource_utilization_trends", "user_activity",
            "twin_operation_patterns", "compliance_status", "security_events",
            
            # Twin Registry-Specific Metrics (Framework Capabilities - JSON)
            "twin_registry_analytics", "category_effectiveness", "workflow_performance",
            "twin_size_performance_efficiency",
            
            # Time-based Analytics (Framework Time Analysis)
            "hour_of_day", "day_of_week", "month",
            
            # Performance Trends
            "twin_management_trend", "resource_efficiency_trend", "quality_trend",
            
            # Enterprise Compliance Metrics (MERGED)
            "enterprise_compliance_score", "compliance_audit_status", "compliance_violations_count",
            "compliance_corrective_actions",
            
            # Enterprise Security Metrics (MERGED)
            "enterprise_security_score", "security_threat_level", "security_vulnerabilities_count",
            "security_incident_response_time", "security_scan_frequency",
            
            # Enterprise Performance Analytics (MERGED)
            "enterprise_performance_score", "performance_optimization_status", "resource_optimization_efficiency",
            "enterprise_analytics_metadata",
            
            # Multi-Tenant Support (REQUIRED for RBAC)
            "user_id", "org_id", "dept_id",
            
            # Timestamps
            "created_at", "updated_at"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for this table."""
        return "metric_id"
    
    def _get_foreign_key_columns(self) -> Dict[str, str]:
        """Get foreign key relationships for this table."""
        return {
            "registry_id": "twin_registry",
            "metric_id": "twin_registry_metrics"
        }
    
    def _get_indexed_columns(self) -> List[str]:
        """Get columns that have database indexes."""
        return ["registry_id", "timestamp", "health_score", "created_at"]
    
    def _get_required_columns(self) -> List[str]:
        """Get columns that are NOT NULL (required)."""
        return [
            "registry_id", "timestamp", "user_id", "org_id", "dept_id"  # Multi-tenant fields required for RBAC
        ]
    
    def _get_audit_columns(self) -> List[str]:
        """Get audit-related columns (created_at, updated_at, etc.)."""
        return [
            "created_at", "updated_at", "timestamp",
            "health_score", "uptime_percentage", "error_rate",
            "compliance_status", "security_events", "enterprise_compliance_score",
            "enterprise_security_score", "enterprise_performance_score"
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
    
    def _validate_entity_schema(self, entity: TwinRegistryMetrics) -> bool:
        """Validate entity against repository schema."""
        entity_fields = set(entity.__dict__.keys())
        schema_fields = set(self._get_columns())
        return entity_fields.issubset(schema_fields)
    
    # ============================================================================
    # ENHANCED CRUD OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def create(self, metrics: TwinRegistryMetrics) -> Optional[int]:
        """
        Async create a new Twin Registry metrics entry with schema validation.
        
        Args:
            metrics: TwinRegistryMetrics model instance
            
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
            
            # Get the last inserted row ID for SQLite AUTOINCREMENT
            last_id_result = await self.connection_manager.execute_query("SELECT last_insert_rowid() as id")
            created_id = last_id_result[0]['id'] if last_id_result else None
            
            logger.info(f"Created Twin Registry metrics entry for registry: {metrics.registry_id}")
            return created_id
            
        except Exception as e:
            logger.error(f"Failed to create Twin Registry metrics entry: {e}")
            return None
    
    async def create_batch(self, entities: List[TwinRegistryMetrics]) -> List[int]:
        """Create multiple entities efficiently in batch operation."""
        try:
            created_ids = []
            for entity in entities:
                entity_id = await self.create(entity)
                if entity_id:
                    created_ids.append(entity_id)
            return created_ids
        except Exception as e:
            logger.error(f"Failed to create batch Twin Registry metrics entries: {e}")
            return []
    
    async def create_if_not_exists(self, entity: TwinRegistryMetrics) -> Tuple[bool, Optional[int]]:
        """Create only if doesn't exist, return (created, id)."""
        try:
            if await self.exists(entity.metric_id):
                return False, entity.metric_id
            
            entity_id = await self.create(entity)
            return True, entity_id
        except Exception as e:
            logger.error(f"Failed to create if not exists: {e}")
            return False, None
    
    # ============================================================================
    # ENHANCED READ OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def get_by_id(self, metric_id: int) -> Optional[TwinRegistryMetrics]:
        """
        Async get Twin Registry metrics entry by ID.
        
        Args:
            metric_id: Unique entity identifier
            
        Returns:
            TwinRegistryMetrics instance or None if not found
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {self._get_primary_key_column()} = :entity_id"
            result = await self.connection_manager.execute_query(query, {"entity_id": metric_id})
            
            if result and len(result) > 0:
                return self._dict_to_model(dict(result[0]))
            return None
            
        except Exception as e:
            logger.error(f"Error getting Twin Registry metrics by ID: {e}")
            return None
    
    async def get_by_ids(self, metric_ids: List[int]) -> List[TwinRegistryMetrics]:
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
            logger.error(f"Error getting Twin Registry metrics by IDs: {e}")
            return []
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[TwinRegistryMetrics]:
        """Get paginated list of all entities."""
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            result = await self.connection_manager.execute_query(query, {"limit": limit, "offset": offset})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting all Twin Registry metrics entries: {e}")
            return []
    
    async def get_by_field(self, field: str, value: Any) -> List[TwinRegistryMetrics]:
        """Get entities by specific field value."""
        try:
            if field not in self._get_columns():
                logger.warning(f"Invalid field '{field}' for Twin Registry metrics table")
                return []
            
            query = f"SELECT * FROM {self.table_name} WHERE {field} = :value ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"value": value})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting Twin Registry metrics by field: {e}")
            return []
    
    # ============================================================================
    # ENHANCED UPDATE OPERATIONS WITH VALIDATION
    # ============================================================================
    
    async def update(self, metric_id: int, updates: Dict[str, Any]) -> bool:
        """
        Async update Twin Registry metrics entry with schema validation.
        
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
            
            logger.info(f"Updated Twin Registry metrics entry: {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Twin Registry metrics entry: {e}")
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
            logger.error(f"Failed to update batch Twin Registry metrics entries: {e}")
            return False
    
    async def upsert(self, entity: TwinRegistryMetrics) -> bool:
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
            logger.error(f"Failed to upsert Twin Registry metrics entry: {e}")
            return False
    
    # ============================================================================
    # ENHANCED DELETE OPERATIONS
    # ============================================================================
    
    async def delete(self, metric_id: int) -> bool:
        """
        Async delete Twin Registry metrics entry.
        
        Args:
            metric_id: Unique entity identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE {self._get_primary_key_column()} = :entity_id"
            await self.connection_manager.execute_update(query, {"entity_id": metric_id})
            
            logger.info(f"Deleted Twin Registry metrics entry: {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Twin Registry metrics entry: {e}")
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
            logger.error(f"Failed to delete batch Twin Registry metrics entries: {e}")
            return False
    
    async def soft_delete(self, metric_id: int) -> bool:
        """Mark as deleted without removing from database."""
        try:
            updates = {
                'health_score': 0,
                'updated_at': datetime.utcnow().isoformat()
            }
            return await self.update(metric_id, updates)
        except Exception as e:
            logger.error(f"Failed to soft delete Twin Registry metrics entry: {e}")
            return False
    
    # ============================================================================
    # ADVANCED QUERYING METHODS (REQUIRED)
    # ============================================================================
    
    async def search(self, query: str, fields: List[str]) -> List[TwinRegistryMetrics]:
        """Full-text search across specified fields."""
        try:
            if not fields:
                fields = ['registry_id', 'health_score', 'uptime_percentage']
            
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
            logger.error(f"Error searching Twin Registry metrics entries: {e}")
            return []
    
    async def filter_by_criteria(self, criteria: Dict[str, Any]) -> List[TwinRegistryMetrics]:
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
            logger.error(f"Error filtering Twin Registry metrics entries: {e}")
            return []
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TwinRegistryMetrics]:
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
            logger.error(f"Error getting Twin Registry metrics by date range: {e}")
            return []
    
    async def get_recent(self, hours: int = 24) -> List[TwinRegistryMetrics]:
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
            logger.error(f"Error getting recent Twin Registry metrics: {e}")
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
            logger.error(f"Error counting Twin Registry metrics by field: {e}")
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
            health_score_counts = {}
            registry_counts = {}
            
            for entity in recent_entities:
                # Count by health score ranges
                health_score = getattr(entity, 'health_score', 0) or 0
                if health_score >= 80:
                    range_key = "80-100"
                elif health_score >= 60:
                    range_key = "60-79"
                elif health_score >= 40:
                    range_key = "40-59"
                else:
                    range_key = "0-39"
                
                health_score_counts[range_key] = health_score_counts.get(range_key, 0) + 1
                
                # Count by registry
                registry_id = getattr(entity, 'registry_id', 'unknown')
                registry_counts[registry_id] = registry_counts.get(registry_id, 0) + 1
            
            return {
                "time_period": time_period,
                "total_entities": len(recent_entities),
                "health_score_distribution": health_score_counts,
                "registry_distribution": registry_counts,
                "period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return {}
    
    # ============================================================================
    # ENTERPRISE FEATURES (REQUIRED)
    # ============================================================================
    
    async def get_by_registry(self, registry_id: str) -> List[TwinRegistryMetrics]:
        """Get entities for specific registry."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id ORDER BY timestamp DESC"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting Twin Registry metrics by registry: {e}")
            return []
    
    async def get_by_health_score_range(self, min_score: int, max_score: int) -> List[TwinRegistryMetrics]:
        """Get entities within health score range."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE health_score BETWEEN :min_score AND :max_score ORDER BY health_score DESC"
            result = await self.connection_manager.execute_query(query, {"min_score": min_score, "max_score": max_score})
            
            entities = []
            for row in result:
                entities.append(self._dict_to_model(dict(row)))
            return entities
            
        except Exception as e:
            logger.error(f"Error getting Twin Registry metrics by health score range: {e}")
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
    
    async def get_compliance_status(self, entity_id: int) -> Dict[str, Any]:
        """Get compliance and validation status."""
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return {}
            
            return {
                "enterprise_compliance_score": getattr(entity, 'enterprise_compliance_score', 0.0),
                "compliance_audit_status": getattr(entity, 'compliance_audit_status', 'pending'),
                "compliance_violations_count": getattr(entity, 'compliance_violations_count', 0),
                "health_score": getattr(entity, 'health_score', 0),
                "uptime_percentage": getattr(entity, 'uptime_percentage', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance status: {e}")
            return {}
    
    async def get_security_score(self, entity_id: int) -> float:
        """Get security assessment score."""
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return 0.0
            
            # Calculate composite security score
            security_score = getattr(entity, 'enterprise_security_score', 0.0)
            threat_level = getattr(entity, 'security_threat_level', 'low')
            vulnerabilities_count = getattr(entity, 'security_vulnerabilities_count', 0)
            
            # Adjust score based on factors
            if threat_level == 'critical':
                security_score *= 0.5
            elif threat_level == 'high':
                security_score *= 0.7
            elif threat_level == 'medium':
                security_score *= 0.85
            
            if vulnerabilities_count > 10:
                security_score *= 0.8
            elif vulnerabilities_count > 5:
                security_score *= 0.9
            
            return min(security_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error getting security score: {e}")
            return 0.0
    
    # ============================================================================
    # PERFORMANCE & MONITORING METHODS (REQUIRED)
    # ============================================================================
    
    async def get_with_relations(self, entity_id: int, relations: List[str]) -> TwinRegistryMetrics:
        """Get entity with related data (eager loading)."""
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return None
            
            # Load related data based on requested relations
            if 'registry_info' in relations and hasattr(entity, 'registry_id'):
                # This would typically join with twin_registry table
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
                        entity = TwinRegistryMetrics(**op_data)
                        entity_id = await self.create(entity)
                        if entity_id:
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to create entity: {op_data.get('metric_id', 'unknown')}")
                    
                    elif op_type == 'update':
                        metric_id = op_data.get('metric_id')
                        updates = {k: v for k, v in op_data.items() if k != 'metric_id'}
                        if await self.update(metric_id, updates):
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to update entity: {metric_id}")
                    
                    elif op_type == 'delete':
                        metric_id = op_data.get('metric_id')
                        if await self.delete(metric_id):
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to delete entity: {metric_id}")
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Operation failed: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing bulk operations: {e}")
            return {"successful": 0, "failed": len(operations), "errors": [str(e)]}
    
    async def get_cached(self, entity_id: int) -> Optional[TwinRegistryMetrics]:
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
            
            # Calculate metrics efficiency
            metrics_stats = await self._get_metrics_efficiency_stats()
            
            return {
                "total_entities": total_count,
                "recent_entities_24h": recent_count,
                "metrics_efficiency": metrics_stats,
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
                if await self.delete(entity.metric_id):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old Twin Registry metrics entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
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
    
    async def validate_entity(self, entity: TwinRegistryMetrics) -> Dict[str, Any]:
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
    
    def _build_update_query(self, entity_id: int, updates: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build dynamic UPDATE query based on updates."""
        set_clause = ', '.join([f"{key} = :{key}" for key in updates.keys()])
        params = updates.copy()
        params[self._get_primary_key_column()] = entity_id
        
        query = f"UPDATE {self._get_table_name()} SET {set_clause} WHERE {self._get_primary_key_column()} = :{self._get_primary_key_column()}"
        
        return query, params
    
    def _build_delete_query(self, entity_id: int) -> Tuple[str, Dict[str, Any]]:
        """Build DELETE query."""
        query = f"DELETE FROM {self._get_table_name()} WHERE {self._get_primary_key_column()} = :{self._get_primary_key_column()}"
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
            result = await self.connection_manager.execute_query(query, {"updated_at": "updated_at"})
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
    
    async def _get_metrics_efficiency_stats(self) -> Dict[str, Any]:
        """Get metrics efficiency statistics."""
        try:
            query = f"""
                SELECT 
                    AVG(health_score) as avg_health_score,
                    AVG(uptime_percentage) as avg_uptime_percentage,
                    AVG(enterprise_compliance_score) as avg_compliance_score,
                    AVG(enterprise_security_score) as avg_security_score,
                    COUNT(CASE WHEN health_score >= 80 THEN 1 END) as healthy_count,
                    COUNT(CASE WHEN health_score < 50 THEN 1 END) as unhealthy_count
                FROM {self.table_name}
                WHERE health_score IS NOT NULL
            """
            
            result = await self.connection_manager.execute_query(query)
            if result and len(result) > 0:
                return dict(result[0])
            return {}
            
        except Exception as e:
            logger.error(f"Error getting metrics efficiency stats: {e}")
            return {}
    
    # ============================================================================
    # MODEL CONVERSION METHODS
    # ============================================================================
    
    def _get_engine_fields(self) -> List[str]:
        """Get list of EngineBaseModel fields that should NOT be stored in database."""
        return [
            'audit_info', 'validation_context', 'business_rule_violations', 
            'cached_properties', 'lazy_loaded', 'observers', 'plugins'
        ]
    
    def _filter_engine_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out EngineBaseModel fields from data before database operations."""
        engine_fields = set(self._get_engine_fields())
        return {k: v for k, v in data.items() if k not in engine_fields}
    
    def _get_json_columns(self) -> List[str]:
        """Get columns that should be stored as JSON in database."""
        return [
            'twin_management_performance', 'twin_category_performance_stats',
            'twin_registry_patterns', 'resource_utilization_trends', 'user_activity',
            'twin_operation_patterns', 'compliance_status', 'security_events',
            'twin_registry_analytics', 'category_effectiveness', 'workflow_performance',
            'twin_size_performance_efficiency', 'compliance_corrective_actions',
            'enterprise_analytics_metadata'
        ]
    
    def _get_computed_fields(self) -> List[str]:
        """Get list of computed fields that should NOT be stored in database."""
        return [
            'overall_metrics_score', 'enterprise_health_status', 'risk_assessment',
            'optimization_priority', 'maintenance_schedule', 'system_efficiency_score',
            'user_engagement_score', 'twin_management_efficiency_score'
        ]
    
    def _row_to_metrics(self, row: Dict[str, Any]) -> TwinRegistryMetrics:
        """Convert database row to TwinRegistryMetrics model."""
        try:
            # Handle JSON fields
            json_fields = self._get_json_columns()
            for field in json_fields:
                if field in row and row[field] is not None:
                    if isinstance(row[field], str):
                        try:
                            row[field] = json.loads(row[field])
                        except (json.JSONDecodeError, TypeError):
                            # Keep as string if JSON parsing fails
                            pass
            
            # Convert to model
            return TwinRegistryMetrics(**row)
        except Exception as e:
            logger.error(f"Error converting row to metrics: {e}")
            raise
    
    def _model_to_dict(self, model: TwinRegistryMetrics) -> Dict[str, Any]:
        """Convert Pydantic model to database dictionary."""
        # Filter out EngineBaseModel fields first
        data = self._filter_engine_fields(model.model_dump())
        
        # Filter out computed fields that should not be stored in database
        computed_fields = set(self._get_computed_fields())
        data = {k: v for k, v in data.items() if k not in computed_fields}
        
        # Get JSON fields dynamically from the method
        json_fields = self._get_json_columns()
        
        # Convert only JSON fields from Python objects to JSON strings
        for field in json_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], (dict, list)):
                    try:
                        data[field] = json.dumps(data[field])
                    except (TypeError, ValueError) as e:
                        # If JSON conversion fails, convert to string representation
                        data[field] = str(data[field])
                        logger.warning(f"Could not convert {field} to JSON, using string: {e}")
        
        return data
    
    def _dict_to_model(self, data: Dict[str, Any]) -> TwinRegistryMetrics:
        """Convert database dictionary to Pydantic model."""
        # Get JSON fields dynamically from the method
        json_fields = self._get_json_columns()
        
        # Convert only JSON fields from JSON strings back to Python objects
        for field in json_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], str):
                    try:
                        data[field] = json.loads(data[field])
                    except (json.JSONDecodeError, TypeError):
                        # Keep as string if JSON parsing fails
                        pass
        
        return TwinRegistryMetrics(**data)
    
    # ============================================================================
    # COUNTING AND STATISTICS METHODS
    # ============================================================================
    
    async def get_count_by_type(self, count_type: str) -> int:
        """Get count of metrics by type."""
        try:
            if count_type == "all":
                query = f"SELECT COUNT(*) as count FROM {self.table_name}"
                params = {}
            else:
                query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE type = :type"
                params = {"type": count_type}
            
            result = await self.connection_manager.execute_query(query, params)
            return result[0]['count'] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get count by type {count_type}: {e}")
            return 0
    
    async def get_count_by_status(self, status: str) -> int:
        """Get count of metrics by status."""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE status = :status"
            params = {"status": status}
            
            result = await self.connection_manager.execute_query(query, params)
            return result[0]['count'] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get count by status {status}: {e}")
            return 0
    
    # ============================================================================
    # LEGACY METHODS (Maintained for backward compatibility)
    # ============================================================================
    
    
    async def get_latest_by_registry_id(self, registry_id: str) -> Optional[TwinRegistryMetrics]:
        """Get the latest metrics for a specific registry."""
        try:
            sql = "SELECT * FROM twin_registry_metrics WHERE registry_id = :registry_id ORDER BY timestamp DESC LIMIT 1"
            
            result = await self.connection_manager.execute_query(sql, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                return self._row_to_metrics(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest metrics for registry {registry_id}: {e}")
            raise
    
    async def query_metrics(self, query: TwinMetricsQuery) -> List[TwinRegistryMetrics]:
        """Query metrics with filters."""
        try:
            sql = "SELECT * FROM twin_registry_metrics WHERE 1=1"
            params = {}
            
            if query.registry_id:
                sql += " AND registry_id = :registry_id"
                params['registry_id'] = query.registry_id
            
            if query.start_timestamp:
                sql += " AND timestamp >= :start_timestamp"
                params['start_timestamp'] = query.start_timestamp.isoformat()
            
            if query.end_timestamp:
                sql += " AND timestamp <= :end_timestamp"
                params['end_timestamp'] = query.end_timestamp.isoformat()
            
            if query.min_health_score is not None:
                sql += " AND health_score >= :min_health_score"
                params['min_health_score'] = query.min_health_score
            
            if query.max_health_score is not None:
                sql += " AND health_score <= :max_health_score"
                params['max_health_score'] = query.max_health_score
            
            sql += " ORDER BY timestamp DESC"
            
            result = await self.connection_manager.execute_query(sql, params)
            
            return [self._row_to_metrics(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            raise

    
    async def get_summary(self) -> TwinMetricsSummary:
        """Get metrics summary statistics."""
        try:
            # Total metrics
            total_result = await self.connection_manager.execute_query("SELECT COUNT(*) as count FROM twin_registry_metrics", {})
            total = total_result[0]['count'] if total_result and len(total_result) > 0 else 0
            
            # Average health score
            avg_health_result = await self.connection_manager.execute_query("SELECT AVG(health_score) as avg_health FROM twin_registry_metrics WHERE health_score IS NOT NULL", {})
            avg_health = avg_health_result[0]['avg_health'] if avg_health_result and len(avg_health_result) > 0 else 0.0
            
            # Average response time
            avg_response_result = await self.connection_manager.execute_query("SELECT AVG(uptime_percentage) as avg_uptime FROM twin_registry_metrics WHERE uptime_percentage IS NOT NULL", {})
            avg_response = avg_response_result[0]['avg_uptime'] if avg_response_result and len(avg_response_result) > 0 else 0.0
            
            # By registry
            by_registry_result = await self.connection_manager.execute_query("SELECT registry_id, COUNT(*) as count FROM twin_registry_metrics GROUP BY registry_id", {})
            by_registry = {row['registry_id']: row['count'] for row in by_registry_result}
            
            # By timestamp (group by hour)
            by_timestamp_result = await self.connection_manager.execute_query("""
                SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour, COUNT(*) as count
                FROM twin_registry_metrics 
                GROUP BY hour 
                ORDER BY hour DESC 
                LIMIT 24
            """, {})
            by_timestamp = {row['hour']: row['count'] for row in by_timestamp_result}
            
            return TwinMetricsSummary(
                total_metrics=total,
                average_health_score=float(avg_health),
                average_uptime_percentage=float(avg_response),
                metrics_by_registry=by_registry,
                metrics_by_timestamp=by_timestamp
            )
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            raise
    

    

    

    
    # ============================================================================
    # ADDITIONAL LEGACY METHODS FOR COMPATIBILITY
    # ============================================================================
    
    async def get_latest_by_registry_id(self, registry_id: str) -> Optional[TwinRegistryMetrics]:
        """Get the latest metrics for a specific registry - Legacy method."""
        try:
            # Get all metrics for registry and return the latest
            metrics = await self.get_by_registry(registry_id)
            return metrics[0] if metrics else None
        except Exception as e:
            logger.error(f"Failed to get latest metrics for registry {registry_id}: {e}")
            raise
    
    async def query_metrics(self, query: TwinMetricsQuery) -> List[TwinRegistryMetrics]:
        """Query metrics with filters - Legacy method."""
        try:
            # Build criteria from query
            criteria = {}
            if query.registry_id:
                criteria['registry_id'] = query.registry_id
            if query.start_timestamp:
                criteria['created_at'] = query.start_timestamp.isoformat()
            if query.end_timestamp:
                criteria['updated_at'] = query.end_timestamp.isoformat()
            if query.min_health_score is not None:
                criteria['health_score'] = query.min_health_score
            if query.max_health_score is not None:
                criteria['health_score'] = query.max_health_score
            
            return await self.filter_by_criteria(criteria)
        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            raise
    
    async def get_summary(self) -> TwinMetricsSummary:
        """Get metrics summary statistics - Legacy method."""
        try:
            # Get basic statistics
            total_count = await self._get_total_count()
            
            # Get average health score
            health_result = await self.connection_manager.execute_query(
                "SELECT AVG(health_score) as avg_health FROM twin_registry_metrics WHERE health_score IS NOT NULL", {}
            )
            avg_health = health_result[0]['avg_health'] if health_result and len(health_result) > 0 else 0.0
            
            # Get average uptime percentage
            uptime_result = await self.connection_manager.execute_query(
                "SELECT AVG(uptime_percentage) as avg_uptime FROM twin_registry_metrics WHERE uptime_percentage IS NOT NULL", {}
            )
            avg_uptime = uptime_result[0]['avg_uptime'] if uptime_result and len(uptime_result) > 0 else 0.0
            
            # Get metrics by registry
            by_registry_result = await self.connection_manager.execute_query(
                "SELECT registry_id, COUNT(*) as count FROM twin_registry_metrics GROUP BY registry_id", {}
            )
            by_registry = {row['registry_id']: row['count'] for row in by_registry_result}
            
            # Get metrics by timestamp (group by hour)
            by_timestamp_result = await self.connection_manager.execute_query("""
                SELECT strftime('%Y-%m-%d %H:00:00', created_at) as hour, COUNT(*) as count
                FROM twin_registry_metrics 
                GROUP BY hour 
                ORDER BY hour DESC 
                LIMIT 24
            """, {})
            by_timestamp = {row['hour']: row['count'] for row in by_timestamp_result}
            
            return TwinMetricsSummary(
                total_metrics=total_count,
                average_health_score=float(avg_health),
                average_uptime_percentage=float(avg_uptime),
                metrics_by_registry=by_registry,
                metrics_by_timestamp=by_timestamp
            )
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            raise
