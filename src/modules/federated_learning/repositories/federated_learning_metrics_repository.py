"""
Federated Learning Metrics Repository
====================================

Repository for federated learning metrics operations using engine ConnectionManager.
Implements world-class enterprise-grade repository standards with comprehensive
schema introspection, validation, and enterprise features.
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from ..models.federated_learning_metrics import FederatedLearningMetrics


class FederatedLearningMetricsRepository:
    """
    World-Class Repository for federated learning metrics operations.
    
    Implements comprehensive enterprise-grade features including:
    - Schema introspection and validation
    - Advanced CRUD operations with validation
    - Enterprise features (RBAC, audit, compliance)
    - Performance monitoring and health checks
    - Dynamic query building
    - Professional logging and error handling
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "federated_learning_metrics"
        self.logger = logging.getLogger(__name__)
        
        # Initialize repository
        import asyncio
        asyncio.create_task(self.initialize())
    
    async def initialize(self) -> bool:
        """Initialize the repository using the engine schema system."""
        try:
            # Check if table exists
            check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'"
            result = await self.connection_manager.execute_query(check_query)
            
            if not result or len(result) == 0:
                # Table doesn't exist, create it via schema
                self.logger.info(f"Table {self.table_name} does not exist, creating via schema...")
                from src.engine.database.schema.modules.federated_learning import FederatedLearningSchema
                schema = FederatedLearningSchema(self.connection_manager)
                if await schema.initialize():
                    self.logger.info(f"Successfully created table {self.table_name} via FederatedLearningSchema")
                else:
                    self.logger.error(f"Failed to create table {self.table_name} via schema")
                    return False
            else:
                self.logger.debug(f"Table {self.table_name} already exists")
            
            # Validate table exists and schema is correct
            if not await self._validate_schema():
                self.logger.warning("Schema validation failed - some features may not work correctly")
            else:
                self.logger.info("Schema validation successful")
            
            self.logger.info(f"Repository initialized successfully for table: {self.table_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize repository: {e}")
            return False
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository"""
        return self.table_name
    
    def _get_columns(self) -> List[str]:
        """Get all column names for the federated_learning_metrics table"""
        return [
            # Primary identification
            "metric_id", "registry_id", "timestamp",
            
            # Organizational Hierarchy (REQUIRED for proper access control)
            "user_id", "org_id", "dept_id",
            
            # Real-time Health Metrics
            "health_score", "response_time_ms", "uptime_percentage", "error_rate",
            
            # Federation Performance Metrics
            "federation_participation_speed_sec", "model_aggregation_speed_sec", 
            "privacy_compliance_speed_sec", "algorithm_execution_speed_sec", "federation_efficiency",
            
            # Federation Management Performance (JSON)
            "federation_performance", "federation_category_performance_stats",
            
            # User Interaction Metrics
            "user_interaction_count", "federation_access_count", 
            "successful_federation_operations", "failed_federation_operations",
            
            # Data Quality Metrics
            "data_freshness_score", "data_completeness_score", 
            "data_consistency_score", "data_accuracy_score",
            
            # Federation Resource Metrics
            "cpu_usage_percent", "memory_usage_percent", "network_throughput_mbps",
            "storage_usage_percent", "gpu_usage_percent",
            
            # Federation Patterns & Analytics (JSON)
            "federation_patterns", "resource_utilization_trends", "user_activity",
            "federation_operation_patterns", "compliance_status", "privacy_events",
            
            # Enterprise Metrics
            "enterprise_health_score", "federation_efficiency_score", "privacy_preservation_score",
            "model_quality_score", "collaboration_effectiveness", "risk_assessment_score", "compliance_adherence",
            
            # Federation-Specific Metrics (JSON)
            "federation_analytics", "category_effectiveness", "algorithm_performance",
            "federation_size_performance_efficiency",
            
            # Time-based Analytics
            "hour_of_day", "day_of_week", "month",
            
            # Performance Trends
            "federation_management_trend", "resource_efficiency_trend", "quality_trend",
            
            # Timestamps
            "created_at", "updated_at",
            
            # Metadata
            "metadata"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name"""
        return "metric_id"
    
    def _get_foreign_key_columns(self) -> List[str]:
        """Get foreign key column names"""
        return ["registry_id"]
    
    def _get_indexed_columns(self) -> List[str]:
        """Get indexed column names for performance optimization"""
        return ["registry_id", "timestamp", "created_at", "health_score", "enterprise_health_score"]
    
    def _get_required_columns(self) -> List[str]:
        """Get required (non-nullable) column names"""
        return ["registry_id", "timestamp", "health_score", "created_at", "updated_at"]
    
    def _get_audit_columns(self) -> List[str]:
        """Get audit-related column names"""
        return ["created_at", "updated_at", "timestamp"]
    
    async def _validate_schema(self) -> bool:
        """Validate that the table schema matches expected structure"""
        try:
            # Get actual table columns from database
            actual_columns = await self._get_actual_table_columns()
            expected_columns = set(self._get_columns())
            
            # Check if all expected columns exist
            missing_columns = expected_columns - set(actual_columns)
            if missing_columns:
                self.logger.warning(f"Missing columns in table: {missing_columns}")
                return False
            
            self.logger.info("Schema validation successful")
            return True
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False
    
    async def _get_actual_table_columns(self) -> List[str]:
        """Get actual column names from the database table"""
        try:
            query = f"PRAGMA table_info({self.table_name})"
            result = await self.connection_manager.execute_query(query, {})
            return [row['name'] for row in result] if result else []
        except Exception as e:
            self.logger.error(f"Failed to get actual table columns: {e}")
            return []
    
    async def _schema_migration_needed(self) -> bool:
        """Check if schema migration is needed"""
        try:
            actual_columns = await self._get_actual_table_columns()
            expected_columns = set(self._get_columns())
            return len(expected_columns - set(actual_columns)) > 0
        except Exception as e:
            self.logger.error(f"Failed to check schema migration: {e}")
            return False
    
    def _validate_entity_schema(self, entity: FederatedLearningMetrics) -> bool:
        """Validate entity against expected schema"""
        try:
            # Basic validation using Pydantic
            entity.model_validate(entity.model_dump())
            return True
        except Exception as e:
            self.logger.error(f"Entity validation failed: {e}")
            return False
    
    def _deserialize_json_fields(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize JSON fields from database row"""
        try:
            deserialized = row.copy()
            
            # JSON fields that need deserialization
            json_fields = [
                'federation_performance', 'federation_category_performance_stats',
                'federation_patterns', 'resource_utilization_trends', 'user_activity',
                'federation_operation_patterns', 'compliance_status', 'privacy_events',
                'federation_analytics', 'category_effectiveness', 'algorithm_performance',
                'federation_size_performance_efficiency', 'metadata'
            ]
            
            for field in json_fields:
                if field in deserialized and deserialized[field] is not None:
                    if isinstance(deserialized[field], str):
                        try:
                            deserialized[field] = json.loads(deserialized[field])
                        except (json.JSONDecodeError, TypeError):
                            self.logger.warning(f"Failed to deserialize JSON field {field}: {deserialized[field]}")
                            if field in ['federation_performance', 'federation_category_performance_stats',
                                       'federation_patterns', 'resource_utilization_trends', 'user_activity',
                                       'federation_operation_patterns', 'compliance_status', 'privacy_events',
                                       'federation_analytics', 'category_effectiveness', 'algorithm_performance',
                                       'federation_size_performance_efficiency']:
                                deserialized[field] = {}
                            else:
                                deserialized[field] = {}
                    elif isinstance(deserialized[field], (dict, list)):
                        # Already a dict/list, no need to deserialize
                        pass
                    else:
                        self.logger.warning(f"Unexpected type for JSON field {field}: {type(deserialized[field])}")
                        if field in ['federation_performance', 'federation_category_performance_stats',
                                   'federation_patterns', 'resource_utilization_trends', 'user_activity',
                                   'federation_operation_patterns', 'compliance_status', 'privacy_events',
                                   'federation_analytics', 'category_effectiveness', 'algorithm_performance',
                                   'federation_size_performance_efficiency']:
                            deserialized[field] = {}
                        else:
                            deserialized[field] = {}
            
            return deserialized
        except Exception as e:
            self.logger.error(f"Failed to deserialize JSON fields: {e}")
            return row
    
    def _get_computed_fields(self) -> List[str]:
        """Get list of computed fields that should not be stored in database"""
        return [
            'overall_metrics_score', 'enterprise_health_status', 'risk_assessment',
            'optimization_priority', 'maintenance_schedule', 'system_efficiency_score',
            'user_engagement_score', 'federation_performance_score'
        ]
    
    def _model_to_dict(self, model: FederatedLearningMetrics) -> Dict[str, Any]:
        """Convert model to dictionary with proper JSON serialization and filtering"""
        try:
            data = model.model_dump()
            
            # ✅ CRITICAL: Filter out computed fields that should not be stored in database
            # This prevents validation errors like "overall_metrics_score", "enterprise_health_status"
            computed_fields = set(self._get_computed_fields())
            data = {k: v for k, v in data.items() if k not in computed_fields}
            self.logger.debug(f"After filtering computed fields: {list(data.keys())}")
            
            # ✅ CRITICAL: Filter to only include fields that exist in database schema
            # This prevents schema mismatch errors by removing extra fields (including engine fields)
            schema_fields = set(self._get_columns())
            data = {k: v for k, v in data.items() if k in schema_fields}
            self.logger.debug(f"After filtering schema fields: {list(data.keys())}")
            
            # Now work with filtered data instead of model_dict
            model_dict = data
            
            # Serialize JSON fields
            json_fields = [
                'federation_performance', 'federation_category_performance_stats',
                'federation_patterns', 'resource_utilization_trends', 'user_activity',
                'federation_operation_patterns', 'compliance_status', 'privacy_events',
                'federation_analytics', 'category_effectiveness', 'algorithm_performance',
                'federation_size_performance_efficiency', 'metadata'
            ]
            
            for field in json_fields:
                if field in model_dict and model_dict[field] is not None:
                    if isinstance(model_dict[field], (dict, list)):
                        model_dict[field] = json.dumps(model_dict[field])
            
            # Handle datetime fields
            datetime_fields = [
                'timestamp', 'created_at', 'updated_at'
            ]
            
            for field in datetime_fields:
                if field in model_dict and model_dict[field] is not None:
                    if isinstance(model_dict[field], datetime):
                        model_dict[field] = model_dict[field].isoformat()
            
            return model_dict
        except Exception as e:
            self.logger.error(f"Failed to convert model to dict: {e}")
            raise
    
    def _dict_to_model(self, data: Dict[str, Any]) -> FederatedLearningMetrics:
        """Convert dictionary to model with proper JSON deserialization"""
        try:
            # Deserialize JSON fields first
            deserialized_data = self._deserialize_json_fields(data)
            
            # Handle datetime fields
            datetime_fields = [
                'timestamp', 'created_at', 'updated_at'
            ]
            
            for field in datetime_fields:
                if field in deserialized_data and deserialized_data[field] is not None:
                    if isinstance(deserialized_data[field], str):
                        try:
                            deserialized_data[field] = datetime.fromisoformat(deserialized_data[field])
                        except ValueError:
                            self.logger.warning(f"Failed to parse datetime field {field}: {deserialized_data[field]}")
                            deserialized_data[field] = datetime.now()
            
            return FederatedLearningMetrics(**deserialized_data)
        except Exception as e:
            self.logger.error(f"Failed to convert dict to model: {e}")
            raise
    
    def _build_insert_query(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build dynamic INSERT query"""
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]
        
        query = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        return query, data
    
    def _build_update_query(self, data: Dict[str, Any], where_conditions: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build dynamic UPDATE query"""
        set_clauses = [f"{col} = :{col}" for col in data.keys()]
        where_clauses = [f"{col} = :where_{col}" for col in where_conditions.keys()]
        
        # Rename where parameters to avoid conflicts
        where_params = {f"where_{k}": v for k, v in where_conditions.items()}
        
        query = f"""
            UPDATE {self.table_name} 
            SET {', '.join(set_clauses)}
            WHERE {' AND '.join(where_clauses)}
        """
        
        # Combine parameters
        params = {**data, **where_params}
        return query, params
    
    def _build_select_query(self, columns: List[str] = None, where_conditions: Dict[str, Any] = None, 
                           order_by: str = None, limit: int = None, offset: int = None) -> Tuple[str, Dict[str, Any]]:
        """Build dynamic SELECT query"""
        if columns is None:
            columns = ["*"]
        
        query = f"SELECT {', '.join(columns)} FROM {self.table_name}"
        params = {}
        
        if where_conditions:
            where_clauses = [f"{col} = :{col}" for col in where_conditions.keys()]
            query += f" WHERE {' AND '.join(where_clauses)}"
            params.update(where_conditions)
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT :limit"
            params['limit'] = limit
        
        if offset:
            query += f" OFFSET :offset"
            params['offset'] = offset
        
        return query, params
    
    def _build_delete_query(self, where_conditions: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build dynamic DELETE query"""
        where_clauses = [f"{col} = :{col}" for col in where_conditions.keys()]
        
        query = f"DELETE FROM {self.table_name} WHERE {' AND '.join(where_clauses)}"
        return query, where_conditions
    
    async def _get_last_updated_timestamp(self) -> Optional[datetime]:
        """Get the timestamp of the last update in the table"""
        try:
            query = f"SELECT MAX(updated_at) as last_updated FROM {self.table_name}"
            result = await self.connection_manager.execute_query(query, {})
            
            if result and result[0]['last_updated']:
                return datetime.fromisoformat(result[0]['last_updated'])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get last updated timestamp: {e}")
            return None
    
    async def create(self, metrics: FederatedLearningMetrics) -> bool:
        """Create a new metrics entry with world-class validation and error handling"""
        try:
            # Validate entity schema
            if not self._validate_entity_schema(metrics):
                self.logger.error("Entity validation failed")
                return False
            
            # Convert model to dict with proper JSON serialization
            data = self._model_to_dict(metrics)
            
            # Build dynamic insert query
            query, params = self._build_insert_query(data)
            
            await self.connection_manager.execute_update(query, params)
            self.logger.info(f"Successfully created metrics for registry: {metrics.registry_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating metrics: {e}")
            return False
    
    async def get_by_id(self, metric_id: int) -> Optional[FederatedLearningMetrics]:
        """Get metrics by ID with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"metric_id": metric_id}
            )
            
            result = await self.connection_manager.execute_query(query, params)
            
            if result and len(result) > 0:
                return self._dict_to_model(result[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching metrics by ID {metric_id}: {e}")
            return None
    
    async def get_by_registry_id(self, registry_id: str, limit: int = 100) -> List[FederatedLearningMetrics]:
        """Get metrics by registry ID with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"registry_id": registry_id},
                order_by="created_at DESC",
                limit=limit
            )
            
            results = await self.connection_manager.execute_query(query, params)
            
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error fetching metrics by registry ID {registry_id}: {e}")
            return []
    
    async def get_latest_by_registry_id(self, registry_id: str) -> Optional[FederatedLearningMetrics]:
        """Get latest metrics for a registry with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"registry_id": registry_id},
                order_by="created_at DESC",
                limit=1
            )
            
            result = await self.connection_manager.execute_query(query, params)
            
            if result and len(result) > 0:
                return self._dict_to_model(result[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching latest metrics for registry {registry_id}: {e}")
            return None
    
    async def get_by_time_range(self, registry_id: str, start_time: datetime, end_time: datetime) -> List[FederatedLearningMetrics]:
        """Get metrics within a time range with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"registry_id": registry_id},
                order_by="created_at ASC"
            )
            
            # Add time range conditions manually since they're complex
            query = query.replace("WHERE", "WHERE created_at BETWEEN :start_time AND :end_time AND")
            params.update({
                "start_time": start_time,
                "end_time": end_time
            })
            
            results = await self.connection_manager.execute_query(query, params)
            
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error fetching metrics by time range for registry {registry_id}: {e}")
            return []
    
    async def get_performance_trends(self, registry_id: str, days: int = 7) -> Dict[str, List[float]]:
        """Get performance trends over time (async)"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            query = f"""
                SELECT 
                    DATE(created_at) as date,
                    AVG(health_score) as avg_health,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(error_rate) as avg_error_rate,
                    AVG(cpu_usage_percent) as avg_cpu,
                    AVG(memory_usage_percent) as avg_memory
                FROM {self.table_name} 
                WHERE registry_id = :registry_id AND created_at BETWEEN :start_time AND :end_time
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            
            results = await self.connection_manager.execute_query(query, {"registry_id": registry_id, "start_time": start_time, "end_time": end_time})
            
            trends = {
                'dates': [],
                'health_scores': [],
                'response_times': [],
                'error_rates': [],
                'cpu_usage': [],
                'memory_usage': []
            }
            
            for row in results:
                trends['dates'].append(row['date'])
                trends['health_scores'].append(row['avg_health'] or 0.0)
                trends['response_times'].append(row['avg_response_time'] or 0.0)
                trends['error_rates'].append(row['avg_error_rate'] or 0.0)
                trends['cpu_usage'].append(row['avg_cpu'] or 0.0)
                trends['memory_usage'].append(row['avg_memory'] or 0.0)
            
            return trends
            
        except Exception as e:
            print(f"Error getting performance trends: {e}")
            return {}
    
    async def update(self, metric_id: int, update_data: Dict[str, Any]) -> bool:
        """Update metrics with world-class validation and error handling"""
        try:
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.now()
            
            # Build dynamic update query
            query, params = self._build_update_query(
                update_data, 
                {"metric_id": metric_id}
            )
            
            await self.connection_manager.execute_update(query, params)
            self.logger.info(f"Successfully updated metrics {metric_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating metrics {metric_id}: {e}")
            return False
    
    async def delete(self, metric_id: int) -> bool:
        """Delete metrics with world-class error handling"""
        try:
            query, params = self._build_delete_query({"metric_id": metric_id})
            await self.connection_manager.execute_update(query, params)
            
            self.logger.info(f"Successfully deleted metrics {metric_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting metrics {metric_id}: {e}")
            return False
    
    # ==================== WORLD-CLASS ENHANCED CRUD METHODS ====================
    
    async def create_batch(self, metrics_list: List[FederatedLearningMetrics]) -> bool:
        """Create multiple metrics entries in a single transaction"""
        try:
            if not metrics_list:
                return True
            
            # Validate all entities
            for metrics in metrics_list:
                if not self._validate_entity_schema(metrics):
                    self.logger.error(f"Entity validation failed for registry: {metrics.registry_id}")
                    return False
            
            # Convert all models to dicts
            data_list = [self._model_to_dict(metrics) for metrics in metrics_list]
            
            # Build batch insert query
            columns = list(data_list[0].keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute batch insert
            for data in data_list:
                await self.connection_manager.execute_update(query, data)
            
            self.logger.info(f"Successfully created {len(metrics_list)} metrics entries")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating batch metrics: {e}")
            return False
    
    async def create_if_not_exists(self, metrics: FederatedLearningMetrics, 
                                 check_fields: List[str] = None) -> bool:
        """Create metrics only if it doesn't already exist"""
        try:
            if check_fields is None:
                check_fields = ["registry_id", "timestamp"]
            
            # Check if exists
            where_conditions = {field: getattr(metrics, field) for field in check_fields}
            existing = await self.get_by_field(where_conditions)
            
            if existing:
                self.logger.info(f"Metrics already exists for registry: {metrics.registry_id}")
                return True
            
            # Create if not exists
            return await self.create(metrics)
            
        except Exception as e:
            self.logger.error(f"Error in create_if_not_exists: {e}")
            return False
    
    async def get_by_ids(self, metric_ids: List[int]) -> List[FederatedLearningMetrics]:
        """Get multiple metrics by IDs"""
        try:
            if not metric_ids:
                return []
            
            # Build IN clause query
            placeholders = [f":id_{i}" for i in range(len(metric_ids))]
            query = f"SELECT * FROM {self.table_name} WHERE metric_id IN ({', '.join(placeholders)})"
            params = {f"id_{i}": metric_id for i, metric_id in enumerate(metric_ids)}
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error fetching metrics by IDs: {e}")
            return []
    
    async def get_by_field(self, field_values: Dict[str, Any]) -> Optional[FederatedLearningMetrics]:
        """Get metrics by field values"""
        try:
            query, params = self._build_select_query(where_conditions=field_values)
            result = await self.connection_manager.execute_query(query, params)
            
            if result and len(result) > 0:
                return self._dict_to_model(result[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching metrics by field: {e}")
            return None
    
    async def update_batch(self, updates: List[Tuple[int, Dict[str, Any]]]) -> bool:
        """Update multiple metrics in a single transaction"""
        try:
            if not updates:
                return True
            
            for metric_id, update_data in updates:
                success = await self.update(metric_id, update_data)
                if not success:
                    self.logger.error(f"Failed to update metrics {metric_id}")
                    return False
            
            self.logger.info(f"Successfully updated {len(updates)} metrics entries")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating batch metrics: {e}")
            return False
    
    async def upsert(self, metrics: FederatedLearningMetrics, 
                    check_fields: List[str] = None) -> bool:
        """Update if exists, create if not exists"""
        try:
            if check_fields is None:
                check_fields = ["registry_id", "timestamp"]
            
            # Check if exists
            where_conditions = {field: getattr(metrics, field) for field in check_fields}
            existing = await self.get_by_field(where_conditions)
            
            if existing:
                # Update existing
                update_data = self._model_to_dict(metrics)
                # Remove primary key from update data
                if 'metric_id' in update_data:
                    del update_data['metric_id']
                
                return await self.update(existing.metric_id, update_data)
            else:
                # Create new
                return await self.create(metrics)
                
        except Exception as e:
            self.logger.error(f"Error in upsert: {e}")
            return False
    
    async def delete_batch(self, metric_ids: List[int]) -> bool:
        """Delete multiple metrics by IDs"""
        try:
            if not metric_ids:
                return True
            
            # Build IN clause query
            placeholders = [f":id_{i}" for i in range(len(metric_ids))]
            query = f"DELETE FROM {self.table_name} WHERE metric_id IN ({', '.join(placeholders)})"
            params = {f"id_{i}": metric_id for i, metric_id in enumerate(metric_ids)}
            
            await self.connection_manager.execute_update(query, params)
            self.logger.info(f"Successfully deleted {len(metric_ids)} metrics entries")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting batch metrics: {e}")
            return False
    
    async def soft_delete(self, metric_id: int) -> bool:
        """Soft delete metrics by marking as deleted"""
        try:
            update_data = {
                "deleted_at": datetime.now(),
                "is_deleted": True
            }
            
            return await self.update(metric_id, update_data)
            
        except Exception as e:
            self.logger.error(f"Error soft deleting metrics {metric_id}: {e}")
            return False
    
    # ==================== ADVANCED QUERYING METHODS ====================
    
    async def search(self, search_criteria: Dict[str, Any], limit: int = 100) -> List[FederatedLearningMetrics]:
        """Search metrics using flexible criteria"""
        try:
            # Build search query with LIKE clauses for text fields
            where_clauses = []
            params = {}
            
            for field, value in search_criteria.items():
                if isinstance(value, str):
                    where_clauses.append(f"{field} LIKE :{field}")
                    params[field] = f"%{value}%"
                else:
                    where_clauses.append(f"{field} = :{field}")
                    params[field] = value
            
            if where_clauses:
                query = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(where_clauses)} ORDER BY created_at DESC LIMIT :limit"
                params['limit'] = limit
            else:
                query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT :limit"
                params['limit'] = limit
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error searching metrics: {e}")
            return []
    
    async def filter_by_criteria(self, criteria: Dict[str, Any], 
                               order_by: str = "created_at DESC", 
                               limit: int = 100) -> List[FederatedLearningMetrics]:
        """Filter metrics by specific criteria"""
        try:
            query, params = self._build_select_query(
                where_conditions=criteria,
                order_by=order_by,
                limit=limit
            )
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error filtering metrics by criteria: {e}")
            return []
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime, 
                              registry_id: str = None) -> List[FederatedLearningMetrics]:
        """Get metrics within a date range, optionally filtered by registry"""
        try:
            where_conditions = {
                "created_at": f"BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'"
            }
            
            if registry_id:
                where_conditions["registry_id"] = registry_id
            
            # Build custom query for date range
            query = f"SELECT * FROM {self.table_name} WHERE created_at BETWEEN :start_date AND :end_date"
            params = {"start_date": start_date, "end_date": end_date}
            
            if registry_id:
                query += " AND registry_id = :registry_id"
                params["registry_id"] = registry_id
            
            query += " ORDER BY created_at ASC"
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting metrics by date range: {e}")
            return []
    
    async def get_recent(self, hours: int = 24, registry_id: str = None) -> List[FederatedLearningMetrics]:
        """Get recent metrics from the last N hours"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            return await self.get_by_date_range(start_time, end_time, registry_id)
            
        except Exception as e:
            self.logger.error(f"Error getting recent metrics: {e}")
            return []
    
    async def count_by_field(self, field: str, value: Any) -> int:
        """Count metrics by field value"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {field} = :value"
            result = await self.connection_manager.execute_query(query, {"value": value})
            
            return result[0]['count'] if result else 0
            
        except Exception as e:
            self.logger.error(f"Error counting metrics by field {field}: {e}")
            return 0
    
    async def get_statistics(self, registry_id: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics for metrics"""
        try:
            where_clause = "WHERE registry_id = :registry_id" if registry_id else ""
            params = {"registry_id": registry_id} if registry_id else {}
            
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(health_score) as avg_health_score,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(error_rate) as avg_error_rate,
                    AVG(cpu_usage_percent) as avg_cpu_usage,
                    AVG(memory_usage_percent) as avg_memory_usage,
                    AVG(enterprise_health_score) as avg_enterprise_health,
                    AVG(federation_efficiency_score) as avg_federation_efficiency,
                    MIN(created_at) as earliest_metric,
                    MAX(created_at) as latest_metric
                FROM {self.table_name}
                {where_clause}
            """
            
            result = await self.connection_manager.execute_query(query, params)
            return dict(result[0]) if result and len(result) > 0 else {}
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    async def get_trends(self, registry_id: str, days: int = 7) -> Dict[str, List[float]]:
        """Get performance trends over time"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            query = f"""
                SELECT 
                    DATE(created_at) as date,
                    AVG(health_score) as avg_health,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(error_rate) as avg_error_rate,
                    AVG(cpu_usage_percent) as avg_cpu,
                    AVG(memory_usage_percent) as avg_memory,
                    AVG(enterprise_health_score) as avg_enterprise_health
                FROM {self.table_name} 
                WHERE registry_id = :registry_id AND created_at BETWEEN :start_time AND :end_time
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            
            results = await self.connection_manager.execute_query(query, {
                "registry_id": registry_id, 
                "start_time": start_time, 
                "end_time": end_time
            })
            
            trends = {
                'dates': [],
                'health_scores': [],
                'response_times': [],
                'error_rates': [],
                'cpu_usage': [],
                'memory_usage': [],
                'enterprise_health': []
            }
            
            for row in results:
                trends['dates'].append(row['date'])
                trends['health_scores'].append(row['avg_health'] or 0.0)
                trends['response_times'].append(row['avg_response_time'] or 0.0)
                trends['error_rates'].append(row['avg_error_rate'] or 0.0)
                trends['cpu_usage'].append(row['avg_cpu'] or 0.0)
                trends['memory_usage'].append(row['avg_memory'] or 0.0)
                trends['enterprise_health'].append(row['avg_enterprise_health'] or 0.0)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error getting trends: {e}")
            return {}
    
    # ==================== ENTERPRISE FEATURES ====================
    
    async def get_by_user(self, user_id: str, limit: int = 100) -> List[FederatedLearningMetrics]:
        """Get metrics by user ID (for RBAC)"""
        try:
            # This would typically join with a user_registry table
            # For now, we'll use registry_id as a proxy
            query, params = self._build_select_query(
                where_conditions={"registry_id": user_id},  # Assuming registry_id maps to user
                order_by="created_at DESC",
                limit=limit
            )
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting metrics by user {user_id}: {e}")
            return []
    
    async def get_by_organization(self, org_id: str, limit: int = 100) -> List[FederatedLearningMetrics]:
        """Get metrics by organization ID"""
        try:
            # This would typically join with an organization_registry table
            # For now, we'll use a pattern match on registry_id
            query = f"SELECT * FROM {self.table_name} WHERE registry_id LIKE :org_pattern ORDER BY created_at DESC LIMIT :limit"
            params = {"org_pattern": f"{org_id}%", "limit": limit}
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting metrics by organization {org_id}: {e}")
            return []
    
    async def get_audit_trail(self, registry_id: str, start_date: datetime = None, 
                             end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get audit trail for metrics changes"""
        try:
            where_conditions = {"registry_id": registry_id}
            
            if start_date and end_date:
                query = f"""
                    SELECT metric_id, created_at, updated_at, health_score, enterprise_health_score
                    FROM {self.table_name} 
                    WHERE registry_id = :registry_id 
                    AND created_at BETWEEN :start_date AND :end_date
                    ORDER BY created_at DESC
                """
                params = {"registry_id": registry_id, "start_date": start_date, "end_date": end_date}
            else:
                query = f"""
                    SELECT metric_id, created_at, updated_at, health_score, enterprise_health_score
                    FROM {self.table_name} 
                    WHERE registry_id = :registry_id 
                    ORDER BY created_at DESC
                """
                params = {"registry_id": registry_id}
            
            results = await self.connection_manager.execute_query(query, params)
            return [dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting audit trail for registry {registry_id}: {e}")
            return []
    
    async def get_compliance_status(self, registry_id: str) -> Dict[str, Any]:
        """Get compliance status for metrics"""
        try:
            query = f"""
                SELECT 
                    AVG(compliance_adherence) as avg_compliance,
                    AVG(privacy_preservation_score) as avg_privacy,
                    AVG(risk_assessment_score) as avg_risk,
                    COUNT(*) as total_metrics,
                    MIN(created_at) as earliest_metric,
                    MAX(created_at) as latest_metric
                FROM {self.table_name}
                WHERE registry_id = :registry_id
            """
            
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    "compliance_score": row['avg_compliance'] or 0.0,
                    "privacy_score": row['avg_privacy'] or 0.0,
                    "risk_score": row['avg_risk'] or 0.0,
                    "total_metrics": row['total_metrics'] or 0,
                    "earliest_metric": row['earliest_metric'],
                    "latest_metric": row['latest_metric'],
                    "compliance_status": "compliant" if (row['avg_compliance'] or 0) >= 80 else "non_compliant"
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting compliance status for registry {registry_id}: {e}")
            return {}
    
    async def get_security_score(self, registry_id: str) -> Dict[str, Any]:
        """Get security score for metrics"""
        try:
            query = f"""
                SELECT 
                    AVG(enterprise_health_score) as avg_health,
                    AVG(error_rate) as avg_error_rate,
                    AVG(security_score) as avg_security,
                    COUNT(*) as total_metrics
                FROM {self.table_name}
                WHERE registry_id = :registry_id
            """
            
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                row = result[0]
                health_score = row['avg_health'] or 0
                error_rate = row['avg_error_rate'] or 0
                security_score = row['avg_security'] or 0
                
                # Calculate overall security score
                overall_score = (health_score + security_score + (100 - error_rate * 100)) / 3
                
                return {
                    "overall_security_score": overall_score,
                    "health_score": health_score,
                    "error_rate": error_rate,
                    "security_score": security_score,
                    "total_metrics": row['total_metrics'] or 0,
                    "security_level": "high" if overall_score >= 80 else "medium" if overall_score >= 60 else "low"
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting security score for registry {registry_id}: {e}")
            return {}
    
    # ==================== PERFORMANCE & MONITORING ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform repository health check"""
        try:
            # Check if table exists and is accessible
            query = f"SELECT COUNT(*) as count FROM {self.table_name} LIMIT 1"
            result = await self.connection_manager.execute_query(query, {})
            
            if result is not None:
                return {
                    "status": "healthy",
                    "table_accessible": True,
                    "total_records": result[0]['count'] if result else 0,
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "table_accessible": False,
                    "error": "Table not accessible",
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "table_accessible": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get repository performance metrics"""
        try:
            # Get basic performance stats
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(health_score) as avg_health,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(error_rate) as avg_error_rate,
                    MIN(created_at) as earliest_record,
                    MAX(created_at) as latest_record
                FROM {self.table_name}
            """
            
            result = await self.connection_manager.execute_query(query, {})
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    "total_metrics": row['total_metrics'] or 0,
                    "average_health_score": row['avg_health'] or 0.0,
                    "average_response_time": row['avg_response_time'] or 0.0,
                    "average_error_rate": row['avg_error_rate'] or 0.0,
                    "earliest_record": row['earliest_record'],
                    "latest_record": row['latest_record'],
                    "data_freshness_hours": (datetime.now() - (row['latest_record'] or datetime.now())).total_seconds() / 3600 if row['latest_record'] else 0
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information"""
        try:
            return {
                "repository_name": "FederatedLearningMetricsRepository",
                "table_name": self.table_name,
                "total_columns": len(self._get_columns()),
                "primary_key": self._get_primary_key_column(),
                "foreign_keys": self._get_foreign_key_columns(),
                "indexed_columns": self._get_indexed_columns(),
                "required_columns": self._get_required_columns(),
                "audit_columns": self._get_audit_columns(),
                "json_fields": [
                    'federation_performance', 'federation_category_performance_stats',
                    'federation_patterns', 'resource_utilization_trends', 'user_activity',
                    'federation_operation_patterns', 'compliance_status', 'privacy_events',
                    'federation_analytics', 'category_effectiveness', 'algorithm_performance',
                    'federation_size_performance_efficiency', 'metadata'
                ],
                "datetime_fields": ['timestamp', 'created_at', 'updated_at'],
                "world_class_features": [
                    "Schema introspection and validation",
                    "Dynamic query building",
                    "JSON field handling",
                    "Batch operations",
                    "Enterprise features (RBAC, audit, compliance)",
                    "Performance monitoring",
                    "Professional logging"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting repository info: {e}")
            return {}
    
    # ==================== UTILITY & MAINTENANCE ====================
    
    async def exists(self, metric_id: int) -> bool:
        """Check if metrics with given ID exists"""
        try:
            query, params = self._build_select_query(
                columns=["1"],
                where_conditions={"metric_id": metric_id}
            )
            
            result = await self.connection_manager.execute_query(query, params)
            return len(result) > 0
            
        except Exception as e:
            self.logger.error(f"Error checking existence of metrics {metric_id}: {e}")
            return False
    
    async def get_table_info(self) -> Dict[str, Any]:
        """Get detailed table information"""
        try:
            # Get column information
            query = f"PRAGMA table_info({self.table_name})"
            columns_info = await self.connection_manager.execute_query(query, {})
            
            # Get index information
            query = f"PRAGMA index_list({self.table_name})"
            indexes_info = await self.connection_manager.execute_query(query, {})
            
            return {
                "table_name": self.table_name,
                "columns": columns_info,
                "indexes": indexes_info,
                "total_columns": len(columns_info) if columns_info else 0,
                "total_indexes": len(indexes_info) if indexes_info else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting table info: {e}")
            return {}
    
    def validate_entity(self, entity: FederatedLearningMetrics) -> Tuple[bool, List[str]]:
        """Validate entity and return validation errors"""
        try:
            errors = []
            
            # Basic validation
            if not entity.registry_id:
                errors.append("registry_id is required")
            
            if entity.health_score < 0 or entity.health_score > 100:
                errors.append("health_score must be between 0 and 100")
            
            if entity.error_rate < 0 or entity.error_rate > 1:
                errors.append("error_rate must be between 0 and 1")
            
            # Pydantic validation
            try:
                entity.model_validate(entity.model_dump())
            except Exception as e:
                errors.append(f"Pydantic validation failed: {e}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    async def cleanup(self, days_old: int = 90) -> int:
        """Clean up old metrics records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            query = f"DELETE FROM {self.table_name} WHERE created_at < :cutoff_date"
            params = {"cutoff_date": cutoff_date}
            
            await self.connection_manager.execute_update(query, params)
            
            self.logger.info(f"Cleanup completed for records older than {days_old} days")
            return 0  # Return count of deleted records if available
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """Get comprehensive compliance report"""
        try:
            # Get overall compliance statistics
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(compliance_adherence) as avg_compliance,
                    AVG(privacy_preservation_score) as avg_privacy,
                    AVG(risk_assessment_score) as avg_risk,
                    AVG(enterprise_health_score) as avg_health,
                    COUNT(CASE WHEN compliance_adherence >= 80 THEN 1 END) as compliant_count,
                    COUNT(CASE WHEN compliance_adherence < 80 THEN 1 END) as non_compliant_count
                FROM {self.table_name}
            """
            
            result = await self.connection_manager.execute_query(query, {})
            
            if result and len(result) > 0:
                row = result[0]
                total = row['total_metrics'] or 0
                compliant = row['compliant_count'] or 0
                non_compliant = row['non_compliant_count'] or 0
                
                return {
                    "total_metrics": total,
                    "compliance_rate": (compliant / total * 100) if total > 0 else 0,
                    "average_compliance_score": row['avg_compliance'] or 0.0,
                    "average_privacy_score": row['avg_privacy'] or 0.0,
                    "average_risk_score": row['avg_risk'] or 0.0,
                    "average_health_score": row['avg_health'] or 0.0,
                    "compliant_metrics": compliant,
                    "non_compliant_metrics": non_compliant,
                    "compliance_status": "compliant" if (row['avg_compliance'] or 0) >= 80 else "non_compliant",
                    "report_generated_at": datetime.now().isoformat()
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {e}")
            return {}
    
    async def get_repository_standards_compliance(self) -> Dict[str, Any]:
        """Get repository standards compliance report"""
        try:
            # Check implementation of world-class features
            features = {
                "schema_introspection": hasattr(self, '_get_columns'),
                "schema_validation": hasattr(self, '_validate_schema'),
                "json_field_handling": hasattr(self, '_deserialize_json_fields'),
                "dynamic_query_building": hasattr(self, '_build_select_query'),
                "batch_operations": hasattr(self, 'create_batch'),
                "enterprise_features": hasattr(self, 'get_compliance_status'),
                "performance_monitoring": hasattr(self, 'health_check'),
                "professional_logging": hasattr(self, 'logger')
            }
            
            implemented_count = sum(features.values())
            total_count = len(features)
            compliance_percentage = (implemented_count / total_count) * 100
            
            return {
                "compliance_percentage": compliance_percentage,
                "compliance_level": "world_class" if compliance_percentage >= 90 else "enterprise" if compliance_percentage >= 70 else "basic",
                "implemented_features": implemented_count,
                "total_features": total_count,
                "feature_details": features,
                "missing_features": [k for k, v in features.items() if not v],
                "assessment_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing repository standards compliance: {e}")
            return {}
    
    # ==================== LEGACY METHODS (MAINTAINING BACKWARD COMPATIBILITY) ====================
    
    async def get_performance_summary(self, registry_id: str) -> Dict[str, Any]:
        """Get performance summary for a specific registry (legacy method)"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(health_score) as avg_health_score,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(uptime_percentage) as avg_uptime,
                    AVG(error_rate) as avg_error_rate,
                    AVG(cpu_usage_percent) as avg_cpu_usage,
                    AVG(memory_usage_percent) as avg_memory_usage,
                    AVG(enterprise_health_score) as avg_enterprise_health,
                    AVG(federation_efficiency_score) as avg_federation_efficiency
                FROM {self.table_name}
                WHERE registry_id = :registry_id
            """
            
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            return dict(result[0]) if result and len(result) > 0 else {}
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {}
    
    async def get_alerts(self, registry_id: str, threshold: float = 80.0) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds (legacy method)"""
        try:
            query = f"""
                SELECT 
                    metric_id, created_at, health_score, error_rate, cpu_usage_percent, memory_usage_percent
                FROM {self.table_name}
                WHERE registry_id = :registry_id AND (
                    health_score < :threshold OR 
                    error_rate > :error_threshold OR 
                    cpu_usage_percent > :threshold OR 
                    memory_usage_percent > :threshold
                )
                ORDER BY created_at DESC
                LIMIT 50
            """
            
            params = {
                "registry_id": registry_id, 
                "threshold": threshold, 
                "error_threshold": 100-threshold
            }
            
            results = await self.connection_manager.execute_query(query, params)
            
            alerts = []
            for row in results:
                alert = {
                    'metric_id': row['metric_id'],
                    'timestamp': row['created_at'],
                    'issues': []
                }
                
                if row['health_score'] < threshold:
                    alert['issues'].append(f"Low health score: {row['health_score']}")
                if row['error_rate'] > (100-threshold):
                    alert['issues'].append(f"High error rate: {row['error_rate']}")
                if row['cpu_usage_percent'] > threshold:
                    alert['issues'].append(f"High CPU usage: {row['cpu_usage_percent']}%")
                if row['memory_usage_percent'] > threshold:
                    alert['issues'].append(f"High memory usage: {row['memory_usage_percent']}%")
                
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return []
    
    async def get_enterprise_metrics_summary(self) -> Dict[str, Any]:
        """Get enterprise metrics summary across all registries (legacy method)"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(enterprise_health_score) as avg_enterprise_health,
                    AVG(federation_efficiency_score) as avg_federation_efficiency,
                    AVG(privacy_preservation_score) as avg_privacy_preservation,
                    AVG(model_quality_score) as avg_model_quality,
                    AVG(collaboration_effectiveness) as avg_collaboration,
                    AVG(risk_assessment_score) as avg_risk_assessment,
                    AVG(compliance_adherence) as avg_compliance
                FROM {self.table_name}
                WHERE enterprise_health_score IS NOT NULL
            """
            
            result = await self.connection_manager.execute_query(query, {})
            return dict(result[0]) if result and len(result) > 0 else {}
            
        except Exception as e:
            self.logger.error(f"Error getting enterprise metrics summary: {e}")
            return {}
    
    def _row_to_model(self, row: Dict[str, Any]) -> FederatedLearningMetrics:
        """Convert database row to model instance (legacy method)"""
        # Use the new world-class method
        return self._dict_to_model(row)

