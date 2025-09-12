#!/usr/bin/env python3
"""
KG Neo4j ML Registry Repository

This repository provides data access operations for KG Neo4j ML registry
by leveraging the comprehensive engine infrastructure for enterprise features.

Features:
- Complete CRUD operations for ML registry entries
- Enterprise-grade field filtering and validation
- JSON field handling with proper serialization/deserialization
- Engine field filtering to exclude non-database fields
- Computed field exclusion from database operations
- Comprehensive search and summary capabilities
- Health monitoring and error handling
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

# ✅ REQUIRED: Import engine components
from src.engine.repositories.base_repository import BaseRepository
from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.schema.modules.kg_neo4j import KgNeo4jSchema

# ✅ REQUIRED: Import your module components
from ..models.kg_neo4j_ml_registry import KGNeo4jMLRegistry

logger = logging.getLogger(__name__)


class KGNeo4jMLRepository(BaseRepository):
    """
    Repository for KG Neo4j ML registry data operations.
    
    Provides comprehensive data access operations for ML registry entries
    by leveraging the engine infrastructure for enterprise features.
    
    Enterprise Features (via Engine):
    - Complete CRUD operations with proper field filtering
    - JSON field handling with smart serialization/deserialization
    - Engine field filtering to exclude non-database fields
    - Computed field exclusion from database operations
    - Comprehensive search and summary capabilities
    - Health monitoring and error handling
    - Schema validation and field mapping
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize the repository with connection manager.
        
        Args:
            connection_manager: Database connection manager for data access
        """
        super().__init__()  # Don't pass db_manager to base class
        self.connection_manager = connection_manager  # Store it ourselves
        self.table_name = "kg_neo4j_ml_registry"
        self.model_class = KGNeo4jMLRegistry
        
        # ✅ REQUIRED: Use engine schema system instead of manual table creation
        # Note: _ensure_table_exists() will be called in initialize() method
    
    def get_table_name(self) -> str:
        """Get the database table name for this repository."""
        return self.table_name
    
    def get_model_class(self) -> type:
        """Get the Pydantic model class for this repository."""
        return self.model_class
    
    async def _ensure_table_exists(self):
        """Ensure table exists using engine schema system."""
        try:
            # Check if table exists
            check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'"
            result = await self.connection_manager.execute_query(check_query)
            
            if not result or len(result) == 0:
                # Table doesn't exist, create it via schema
                logger.info(f"Table {self.table_name} does not exist, creating via schema...")
                schema = KgNeo4jSchema(self.connection_manager)
                if await schema.initialize():
                    logger.info(f"Successfully created table {self.table_name} via schema")
                else:
                    logger.error(f"Failed to create table {self.table_name} via schema")
                    raise Exception("Table creation failed via schema")
            else:
                logger.debug(f"Table {self.table_name} already exists")
            
        except Exception as e:
            logger.error(f"Error ensuring table exists: {e}")
            raise
    
    async def initialize(self):
        """
        Initialize the repository asynchronously.
        
        This method should be called after creating the repository instance
        to ensure proper async initialization of all components.
        """
        try:
            # Ensure table exists using engine schema system
            await self._ensure_table_exists()
            logger.info(f"{self.__class__.__name__} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")
            raise
    
    # ✅ REQUIRED: Column management methods
    
    def _get_columns(self) -> List[str]:
        """
        Get list of database columns (must match actual schema).
        
        Returns:
            List of column names that exist in the database
        """
        return [
            # #### Primary Identification ####
            'ml_registry_id', 'graph_id', 'model_id', 'session_id',
            
            # #### Model Metadata ####
            'model_name', 'model_type', 'model_version', 'model_description', 'model_architecture', 
            'model_framework', 'training_parameters',
            
            # #### Training Session Metadata ####
            'training_status', 'training_type', 'training_algorithm',
            
            # #### External Storage References ####
            'model_file_path', 'config_file_path', 'dataset_path', 'logs_path',
            'performance_logs_path', 'deployment_config_path',
            
            # #### Training Performance Summary ####
            'final_accuracy', 'training_duration_seconds', 'resource_consumption',
            'training_efficiency_score', 'training_metrics',
            
            # #### Model Performance Metrics ####
            'precision_score', 'recall_score', 'f1_score', 'auc_score',
            
            # #### Training Data Metadata ####
            'dataset_size', 'feature_count', 'data_quality_score', 'data_split_ratio',
            
            # #### Model Deployment & Usage ####
            'deployment_status', 'deployment_date', 'usage_count', 'last_used_at',
            
            # #### Enterprise Performance Analytics ####
            'performance_trend', 'performance_metric', 'performance_value',
            'optimization_suggestions', 'last_optimization_date',
            'optimization_effectiveness_score', 'performance_benchmarks',
            'resource_efficiency_score', 'scalability_score',
            
            # #### Integration References ####
            'aasx_integration_id', 'twin_registry_id', 'physics_modeling_id',
            'federated_learning_id', 'ai_rag_id', 'certificate_manager_id',
            
            # #### Quality & Governance ####
            'model_quality_score', 'validation_status', 'compliance_score',
            'bias_detection_score',
            
            # #### Lifecycle Management ####
            'lifecycle_status', 'lifecycle_phase',
            
            # #### User Management & Ownership ####
            'user_id', 'org_id', 'dept_id', 'owner_team', 'steward_user_id',
            
            # #### Timestamps & Audit ####
            'created_at', 'updated_at', 'training_started_at', 'training_completed_at',
            'last_accessed_at',
            
            # #### Configuration & Metadata ####
            'ml_config', 'model_metadata', 'custom_attributes', 'tags',
            
            # #### System Fields ####
            'is_deleted'
        ]
    
    def _get_computed_fields(self) -> List[str]:
        """
        Get list of computed fields that should NOT be stored in database.
        
        Returns:
            List of computed field names
        """
        return [
            'overall_score', 'health_status', 'compliance_rating',
            'training_efficiency', 'model_quality_score'
        ]
    
    def _get_engine_fields(self) -> List[str]:
        """
        Get list of EngineBaseModel fields that should NOT be stored in database.
        
        Returns:
            List of engine-specific field names
        """
        return [
            'audit_info', 'validation_context', 'business_rule_violations',
            'engine_metadata', 'framework_context'
        ]
    
    def _get_json_columns(self) -> List[str]:
        """
        Get columns that should be stored as JSON in database.
        
        Returns:
            List of JSON field names
        """
        return [
            'training_parameters', 'model_parameters', 'resource_consumption', 'optimization_suggestions',
            'performance_benchmarks', 'ml_config', 'model_metadata', 
            'custom_attributes', 'tags', 'training_metrics'
        ]
    
    # ✅ REQUIRED: Field filtering methods
    
    def _filter_engine_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out EngineBaseModel fields from data before database operations.
        
        Args:
            data: Data dictionary to filter
            
        Returns:
            Filtered data without engine fields
        """
        engine_fields = set(self._get_engine_fields())
        return {k: v for k, v in data.items() if k not in engine_fields}
    
    def _filter_computed_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out computed fields from data before database operations.
        
        Args:
            data: Data dictionary to filter
            
        Returns:
            Filtered data without computed fields
        """
        computed_fields = set(self._get_computed_fields())
        return {k: v for k, v in data.items() if k not in computed_fields}
    
    def _filter_schema_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter data to only include fields that exist in database schema.
        
        Args:
            data: Data dictionary to filter
            
        Returns:
            Filtered data with only schema fields
        """
        schema_fields = set(self._get_columns())
        return {k: v for k, v in data.items() if k in schema_fields}
    
    # ✅ REQUIRED: Model conversion methods
    
    def _model_to_dict(self, model: KGNeo4jMLRegistry) -> Dict[str, Any]:
        """
        Convert KGNeo4jMLRegistry model to dictionary with proper field filtering and JSON serialization.
        
        Args:
            model: Model instance to convert
            
        Returns:
            Dictionary representation ready for database operations
        """
        try:
            # Filter out EngineBaseModel fields first
            data = self._filter_engine_fields(model.model_dump())
            
            # Filter out computed fields that should not be stored in database
            data = self._filter_computed_fields(data)
            
            # Filter to only include fields that exist in database schema
            data = self._filter_schema_fields(data)
            
            # Handle JSON fields - use the dynamic list from _get_json_columns()
            json_fields = self._get_json_columns()
            for field in json_fields:
                if field in data and data[field] is not None:
                    if isinstance(data[field], (dict, list)):
                        data[field] = json.dumps(data[field])
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert model to dictionary: {e}")
            return {}
    
    def _dict_to_model(self, row: Dict[str, Any]) -> KGNeo4jMLRegistry:
        """
        Convert database row to KGNeo4jMLRegistry model with proper JSON deserialization.
        
        Args:
            row: Database row dictionary
            
        Returns:
            KGNeo4jMLRegistry model instance
        """
        try:
            # Handle JSON fields - deserialize if they are strings
            json_fields = self._get_json_columns()
            for field in json_fields:
                if field in row and row[field] is not None:
                    if isinstance(row[field], str):
                        try:
                            row[field] = json.loads(row[field])
                        except json.JSONDecodeError:
                            row[field] = {}
            
            return KGNeo4jMLRegistry(**row)
            
        except Exception as e:
            logger.error(f"Failed to convert row to model: {e}")
            raise
    
    # ✅ REQUIRED: Core CRUD operations
    
    async def create(self, ml_registry: KGNeo4jMLRegistry) -> bool:
        """
        Create a new ML registry entry.
        
        Args:
            ml_registry: ML registry instance to create
            
        Returns:
            True if creation successful, False otherwise
        """
        try:
            # Convert model to dictionary with proper field filtering
            data = self._model_to_dict(ml_registry)
            
            # Build INSERT query
            columns = list(data.keys())
            placeholders = [f":{col}" for col in columns]
            
            sql = f"""
                INSERT INTO {self.table_name} 
                ({', '.join(columns)}) 
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute query
            result = await self.connection_manager.execute_update(sql, data)
            
            if result:
                logger.info(f"Successfully created ML registry entry: {ml_registry.ml_registry_id}")
                return True
            else:
                logger.error(f"Failed to create ML registry entry: {ml_registry.ml_registry_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error creating ML registry entry: {e}")
            return False
    
    async def get_by_id(self, ml_registry_id: str) -> Optional[KGNeo4jMLRegistry]:
        """
        Retrieve ML registry entry by ID.
        
        Args:
            ml_registry_id: ID of the ML registry entry to retrieve
            
        Returns:
            ML registry instance or None if not found
        """
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE ml_registry_id = :ml_registry_id"
            result = await self.connection_manager.execute_query(sql, {"ml_registry_id": ml_registry_id})
            
            if not result or len(result) == 0:
                logger.warning(f"ML registry entry not found: {ml_registry_id}")
                return None
            
            # Convert row to model with proper JSON deserialization
            row = result[0]
            return self._dict_to_model(row)
            
        except Exception as e:
            logger.error(f"Error retrieving ML registry entry: {e}")
            return None
    
    async def update(self, ml_registry_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update ML registry entry.
        
        Args:
            ml_registry_id: ID of the ML registry entry to update
            update_data: Data to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Filter update data to only include schema fields
            filtered_data = self._filter_schema_fields(update_data)
            
            # Handle JSON fields
            json_fields = self._get_json_columns()
            for field in json_fields:
                if field in filtered_data and filtered_data[field] is not None:
                    if isinstance(filtered_data[field], (dict, list)):
                        filtered_data[field] = json.dumps(filtered_data[field])
            
            # Build UPDATE query
            set_clauses = []
            params = {"ml_registry_id": ml_registry_id}
            
            for field, value in filtered_data.items():
                if field != "ml_registry_id" and value is not None:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = value
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return False
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = :updated_at")
            params["updated_at"] = datetime.now().isoformat()
            
            sql = f"""
                UPDATE {self.table_name} 
                SET {', '.join(set_clauses)}
                WHERE ml_registry_id = :ml_registry_id
            """
            
            # Execute query
            result = await self.connection_manager.execute_update(sql, params)
            
            if result:
                logger.info(f"Successfully updated ML registry entry: {ml_registry_id}")
                return True
            else:
                logger.error(f"Failed to update ML registry entry: {ml_registry_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating ML registry entry: {e}")
            return False
    
    async def delete(self, ml_registry_id: str) -> bool:
        """
        Soft delete ML registry entry.
        
        Args:
            ml_registry_id: ID of the ML registry entry to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            sql = f"""
                UPDATE {self.table_name} 
                SET is_deleted = 1, updated_at = :updated_at
                WHERE ml_registry_id = :ml_registry_id
            """
            
            params = {
                "ml_registry_id": ml_registry_id,
                "updated_at": datetime.now().isoformat()
            }
            
            result = await self.connection_manager.execute_update(sql, params)
            
            if result:
                logger.info(f"Successfully soft deleted ML registry entry: {ml_registry_id}")
                return True
            else:
                logger.error(f"Failed to soft delete ML registry entry: {ml_registry_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting ML registry entry: {e}")
            return False
    
    # ✅ REQUIRED: Search and query methods
    
    async def search_entities(
        self, 
        search_criteria: Dict[str, Any], 
        limit: int = 100, 
        offset: int = 0
    ) -> List[KGNeo4jMLRegistry]:
        """
        Search for ML registry entries based on criteria.
        
        Args:
            search_criteria: Search criteria dictionary
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching ML registry entries
        """
        try:
            # Build dynamic search query
            sql, params = self._build_search_query(search_criteria, limit, offset)
            
            # Execute query
            result = await self.connection_manager.execute_query(sql, params)
            
            if not result:
                return []
            
            # Convert results to models
            ml_registries = []
            for row in result:
                try:
                    # Convert row to model with proper JSON deserialization
                    ml_registry = self._dict_to_model(row)
                    ml_registries.append(ml_registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return ml_registries
            
        except Exception as e:
            logger.error(f"Failed to search ML registry entries: {e}")
            return []
    
    def _build_search_query(
        self, 
        search_criteria: Dict[str, Any], 
        limit: int = 100, 
        offset: int = 0
    ) -> tuple[str, Dict[str, Any]]:
        """
        Build dynamic search query based on criteria.
        
        Args:
            search_criteria: Search criteria dictionary
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Tuple of (SQL query, parameters)
        """
        try:
            # Base query
            sql = f"SELECT * FROM {self.table_name} WHERE is_deleted = 0"
            params = {}
            
            # Add search conditions
            conditions = []
            
            for field, value in search_criteria.items():
                if field in self._get_columns() and value is not None:
                    if isinstance(value, (list, tuple)):
                        # Handle list values (IN clause)
                        placeholders = [f":{field}_{i}" for i in range(len(value))]
                        conditions.append(f"{field} IN ({', '.join(placeholders)})")
                        for i, val in enumerate(value):
                            params[f"{field}_{i}"] = val
                    elif isinstance(value, str) and "%" in value:
                        # Handle LIKE patterns
                        conditions.append(f"{field} LIKE :{field}")
                        params[field] = value
                    else:
                        # Handle exact matches
                        conditions.append(f"{field} = :{field}")
                        params[field] = value
            
            # Add conditions to query
            if conditions:
                sql += " AND " + " AND ".join(conditions)
            
            # Add ordering and pagination
            sql += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = offset
            
            return sql, params
            
        except Exception as e:
            logger.error(f"Error building search query: {e}")
            # Return safe fallback query
            fallback_sql = f"SELECT * FROM {self.table_name} WHERE is_deleted = 0 ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            fallback_params = {"limit": limit, "offset": offset}
            return fallback_sql, fallback_params
    
    # ✅ REQUIRED: Summary and statistics methods
    
    async def get_summary(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a summary of all ML registry entries with statistics.
        
        Args:
            user_context: Optional user context for authorization (not used in this implementation)
            
        Returns:
            Dictionary containing summary statistics
        """
        try:
            # Get basic counts
            count_sql = f"SELECT COUNT(*) as total FROM {self.table_name} WHERE is_deleted = 0"
            count_result = await self.connection_manager.execute_query(count_sql, {})
            total_count = count_result[0]["total"] if count_result else 0
            
            # Get counts by model type
            type_sql = f"""
                SELECT model_type, COUNT(*) as count 
                FROM {self.table_name} 
                WHERE is_deleted = 0 
                GROUP BY model_type
            """
            type_result = await self.connection_manager.execute_query(type_sql, {})
            type_counts = {row["model_type"]: row["count"] for row in type_result}
            
            # Get counts by training status
            status_sql = f"""
                SELECT training_status, COUNT(*) as count 
                FROM {self.table_name} 
                WHERE is_deleted = 0 
                GROUP BY training_status
            """
            status_result = await self.connection_manager.execute_query(status_sql, {})
            status_counts = {row["training_status"]: row["count"] for row in status_result}
            
            # Get counts by deployment status
            deploy_sql = f"""
                SELECT deployment_status, COUNT(*) as count 
                FROM {self.table_name} 
                WHERE is_deleted = 0 
                GROUP BY deployment_status
            """
            deploy_result = await self.connection_manager.execute_query(deploy_sql, {})
            deploy_counts = {row["deployment_status"]: row["count"] for row in deploy_result}
            
            # Get performance statistics
            perf_sql = f"""
                SELECT 
                    AVG(performance_value) as avg_performance,
                    AVG(final_accuracy) as avg_accuracy,
                    AVG(training_duration_seconds) as avg_training_duration
                FROM {self.table_name} 
                WHERE is_deleted = 0 
                AND performance_value IS NOT NULL
            """
            perf_result = await self.connection_manager.execute_query(perf_sql, {})
            perf_stats = perf_result[0] if perf_result else {}
            
            # Compile summary
            summary = {
                "total_ml_registries": total_count,
                "model_type_distribution": type_counts,
                "training_status_distribution": status_counts,
                "deployment_status_distribution": deploy_counts,
                "performance_statistics": {
                    "average_performance_score": perf_stats.get("avg_performance", 0),
                    "average_accuracy": perf_stats.get("avg_accuracy", 0),
                    "average_training_duration_minutes": perf_stats.get("avg_training_duration", 0)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get ML registry summary: {e}")
            return {
                "total_ml_registries": 0,
                "model_type_distribution": {},
                "training_status_distribution": {},
                "deployment_status_distribution": {},
                "performance_statistics": {},
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ✅ REQUIRED: Health monitoring methods
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check repository health status.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            # Check table existence
            table_check_sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'"
            table_result = await self.connection_manager.execute_query(table_check_sql, {})
            table_exists = len(table_result) > 0
            
            # Check basic connectivity
            basic_sql = f"SELECT COUNT(*) as count FROM {self.table_name} LIMIT 1"
            basic_result = await self.connection_manager.execute_query(basic_sql, {})
            basic_connectivity = basic_result is not None
            
            # Check column structure
            column_check_sql = f"PRAGMA table_info({self.table_name})"
            column_result = await self.connection_manager.execute_query(column_check_sql, {})
            expected_columns = set(self._get_columns())
            actual_columns = {row["name"] for row in column_result}
            column_match = expected_columns.issubset(actual_columns)
            
            # Determine overall health
            overall_status = "healthy"
            if not table_exists or not basic_connectivity or not column_match:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "table_exists": table_exists,
                "basic_connectivity": basic_connectivity,
                "column_structure_match": column_match,
                "expected_columns_count": len(expected_columns),
                "actual_columns_count": len(actual_columns),
                "missing_columns": list(expected_columns - actual_columns),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ✅ REQUIRED: Additional business methods
    
    async def get_by_graph_id(self, graph_id: str) -> List[KGNeo4jMLRegistry]:
        """
        Get all ML registry entries for a specific graph.
        
        Args:
            graph_id: ID of the graph
            
        Returns:
            List of ML registry entries for the graph
        """
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE graph_id = :graph_id AND is_deleted = 0 ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(sql, {"graph_id": graph_id})
            
            if not result:
                return []
            
            # Convert results to models
            ml_registries = []
            for row in result:
                try:
                    ml_registry = self._dict_to_model(row)
                    ml_registries.append(ml_registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return ml_registries
            
        except Exception as e:
            logger.error(f"Error retrieving ML registries by graph ID: {e}")
            return []
    
    async def get_by_model_type(self, model_type: str) -> List[KGNeo4jMLRegistry]:
        """
        Get all ML registry entries for a specific model type.
        
        Args:
            model_type: Type of ML model
            
        Returns:
            List of ML registry entries for the model type
        """
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE model_type = :model_type AND is_deleted = 0 ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(sql, {"model_type": model_type})
            
            if not result:
                return []
            
            # Convert results to models
            ml_registries = []
            for row in result:
                try:
                    ml_registry = self._dict_to_model(row)
                    ml_registries.append(ml_registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return ml_registries
            
        except Exception as e:
            logger.error(f"Error retrieving ML registries by model type: {e}")
            return []
    
    async def get_by_training_status(self, training_status: str) -> List[KGNeo4jMLRegistry]:
        """
        Get all ML registry entries with a specific training status.
        
        Args:
            training_status: Training status to filter by
            
        Returns:
            List of ML registry entries with the specified training status
        """
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE training_status = :training_status AND is_deleted = 0 ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(sql, {"training_status": training_status})
            
            if not result:
                return []
            
            # Convert results to models
            ml_registries = []
            for row in result:
                try:
                    ml_registry = self._dict_to_model(row)
                    ml_registries.append(ml_registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return ml_registries
            
        except Exception as e:
            logger.error(f"Error retrieving ML registry entries by training status: {e}")
            return []
    
    async def get_by_deployment_status(self, deployment_status: str) -> List[KGNeo4jMLRegistry]:
        """
        Get all ML registry entries with a specific deployment status.
        
        Args:
            deployment_status: Deployment status to filter by
            
        Returns:
            List of ML registry entries with the specified deployment status
        """
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE deployment_status = :deployment_status AND is_deleted = 0 ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(sql, {"deployment_status": deployment_status})
            
            if not result:
                return []
            
            # Convert results to models
            ml_registries = []
            for row in result:
                try:
                    ml_registry = self._dict_to_model(row)
                    ml_registries.append(ml_registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return ml_registries
            
        except Exception as e:
            logger.error(f"Error retrieving ML registries by deployment status: {e}")
            return []
    
    async def get_high_performance_models(self, min_performance_score: float = 0.8) -> List[KGNeo4jMLRegistry]:
        """
        Get ML registry entries with high performance scores.
        
        Args:
            min_performance_score: Minimum performance score threshold
            
        Returns:
            List of high-performance ML registry entries
        """
        try:
            sql = f"""
                SELECT * FROM {self.table_name} 
                            WHERE performance_value >= :min_score
            AND is_deleted = 0
            ORDER BY performance_value DESC
            """
            result = await self.connection_manager.execute_query(sql, {"min_score": min_performance_score})
            
            if not result:
                return []
            
            # Convert results to models
            ml_registries = []
            for row in result:
                try:
                    ml_registry = self._dict_to_model(row)
                    ml_registries.append(ml_registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return ml_registries
            
        except Exception as e:
            logger.error(f"Error retrieving high performance models: {e}")
            return []
    
    async def get_recent_models(self, days: int = 30) -> List[KGNeo4jMLRegistry]:
        """
        Get ML registry entries created within the specified number of days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent ML registry entries
        """
        try:
            from datetime import timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            sql = f"""
                SELECT * FROM {self.table_name} 
                WHERE created_at >= :cutoff_date 
                AND is_deleted = 0 
                ORDER BY created_at DESC
            """
            result = await self.connection_manager.execute_query(sql, {"cutoff_date": cutoff_date})
            
            if not result:
                return []
            
            # Convert results to models
            ml_registries = []
            for row in result:
                try:
                    ml_registry = self._dict_to_model(row)
                    ml_registries.append(ml_registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return ml_registries
            
        except Exception as e:
            logger.error(f"Error retrieving recent models: {e}")
            return []
    
    # ✅ REQUIRED: Advanced CRUD Operations (Missing from Template)
    
    async def create_batch(self, ml_registries: List[KGNeo4jMLRegistry]) -> List[str]:
        """Create multiple ML registry entries efficiently in batch operation."""
        try:
            created_ids = []
            for ml_registry in ml_registries:
                success = await self.create(ml_registry)
                if success:
                    created_ids.append(ml_registry.ml_registry_id)
            
            logger.info(f"Created {len(created_ids)} ML registry entries in batch")
            return created_ids
            
        except Exception as e:
            logger.error(f"Failed to create ML registry entries in batch: {e}")
            return []
    
    async def create_if_not_exists(self, ml_registry: KGNeo4jMLRegistry) -> Tuple[bool, Optional[str]]:
        """Create only if doesn't exist, return (created, id)."""
        try:
            # Check if registry already exists
            existing = await self.get_by_id(ml_registry.ml_registry_id)
            if existing:
                return False, existing.ml_registry_id
            
            # Create new registry
            success = await self.create(ml_registry)
            if success:
                return True, ml_registry.ml_registry_id
            return False, None
            
        except Exception as e:
            logger.error(f"Failed to create ML registry if not exists: {e}")
            return False, None
    
    async def get_by_ids(self, ml_registry_ids: List[str]) -> List[KGNeo4jMLRegistry]:
        """Get multiple ML registry entries by their IDs."""
        try:
            registries = []
            for ml_registry_id in ml_registry_ids:
                registry = await self.get_by_id(ml_registry_id)
                if registry:
                    registries.append(registry)
            
            return registries
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by IDs: {e}")
            return []
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[KGNeo4jMLRegistry]:
        """Get all ML registry entries with pagination."""
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            result = await self.connection_manager.execute_query(query, {"limit": limit, "offset": offset})
            
            registries = []
            for row in result:
                try:
                    registry = self._dict_to_model(row)
                    registries.append(registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return registries
            
        except Exception as e:
            logger.error(f"Failed to get all ML registry entries: {e}")
            return []
    
    async def update_batch(self, updates: List[Dict[str, Any]]) -> int:
        """Update multiple ML registry entries efficiently."""
        try:
            updated_count = 0
            for update_data in updates:
                ml_registry_id = update_data.get('ml_registry_id')
                if ml_registry_id:
                    success = await self.update(ml_registry_id, update_data)
                    if success:
                        updated_count += 1
            
            logger.info(f"Updated {updated_count} ML registry entries in batch")
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to update ML registry entries in batch: {e}")
            return 0
    
    async def upsert(self, ml_registry: KGNeo4jMLRegistry) -> bool:
        """Update if exists, otherwise create."""
        try:
            existing = await self.get_by_id(ml_registry.ml_registry_id)
            if existing:
                # Update existing registry
                update_data = {
                    'model_name': ml_registry.model_name,
                    'model_type': ml_registry.model_type,
                    'model_version': ml_registry.model_version,
                    'training_status': ml_registry.training_status,
                    'deployment_status': ml_registry.deployment_status,
                    'updated_at': datetime.now().isoformat()
                }
                return await self.update(ml_registry.ml_registry_id, update_data)
            else:
                # Create new registry
                return await self.create(ml_registry)
                
        except Exception as e:
            logger.error(f"Failed to upsert ML registry: {e}")
            return False
    
    async def delete_batch(self, ml_registry_ids: List[str]) -> int:
        """Delete multiple ML registry entries efficiently."""
        try:
            deleted_count = 0
            for ml_registry_id in ml_registry_ids:
                success = await self.delete(ml_registry_id)
                if success:
                    deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} ML registry entries in batch")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete ML registry entries in batch: {e}")
            return 0
    
    async def soft_delete(self, ml_registry_id: str) -> bool:
        """Soft delete an ML registry entry by marking as inactive."""
        try:
            update_data = {"is_deleted": 1, "updated_at": datetime.now().isoformat()}
            return await self.update(ml_registry_id, update_data)
            
        except Exception as e:
            logger.error(f"Failed to soft delete ML registry {ml_registry_id}: {e}")
            return False
    
    # ✅ REQUIRED: Advanced Querying Methods (Missing from Template)
    
    async def search(self, query: str, fields: List[str] = None) -> List[KGNeo4jMLRegistry]:
        """Search ML registry entries by text query across specified fields."""
        try:
            search_fields = fields or ['model_name', 'model_type', 'model_description']
            
            # Build dynamic search query
            where_conditions = []
            params = {"query": f"%{query}%"}
            
            for field in search_fields:
                where_conditions.append(f"{field} LIKE :query")
            
            where_clause = " OR ".join(where_conditions)
            sql = f"SELECT * FROM {self.table_name} WHERE {where_clause} ORDER BY created_at DESC"
            
            result = await self.connection_manager.execute_query(sql, params)
            
            registries = []
            for row in result:
                try:
                    registry = self._dict_to_model(row)
                    registries.append(registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return registries
            
        except Exception as e:
            logger.error(f"Failed to search ML registry entries: {e}")
            return []
    
    async def filter_by_criteria(self, criteria: Dict[str, Any]) -> List[KGNeo4jMLRegistry]:
        """Filter ML registry entries by multiple criteria."""
        try:
            where_conditions = []
            params = {}
            
            for field, value in criteria.items():
                if value is not None:
                    where_conditions.append(f"{field} = :{field}")
                    params[field] = value
            
            if not where_conditions:
                return await self.get_all()
            
            where_clause = " AND ".join(where_conditions)
            sql = f"SELECT * FROM {self.table_name} WHERE {where_clause} ORDER BY created_at DESC"
            
            result = await self.connection_manager.execute_query(sql, params)
            
            registries = []
            for row in result:
                try:
                    registry = self._dict_to_model(row)
                    registries.append(registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
    
            return registries
    
        except Exception as e:
            logger.error(f"Failed to filter ML registry entries by criteria: {e}")
            return []
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries within a date range."""
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE created_at BETWEEN :start_date AND :end_date ORDER BY created_at DESC"
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            result = await self.connection_manager.execute_query(sql, params)
            
            registries = []
            for row in result:
                try:
                    registry = self._dict_to_model(row)
                    registries.append(registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return registries
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by date range: {e}")
            return []
    
    async def get_recent(self, hours: int = 24) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries from the last N hours."""
        try:
            from datetime import timedelta
            
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours)
            return await self.get_by_date_range(start_date, end_date)
            
        except Exception as e:
            logger.error(f"Failed to get recent ML registry entries: {e}")
            return []
    
    # ✅ REQUIRED: Aggregation & Analytics Methods (Missing from Template)
    
    async def count_by_field(self, field: str, value: Any) -> int:
        """Count ML registry entries by a specific field value."""
        try:
            sql = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {field} = :value"
            result = await self.connection_manager.execute_query(sql, {"value": value})
            
            return result[0]["count"] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to count ML registry entries by field {field}: {e}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics and metrics."""
        try:
            # Get total count
            total_query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            total_result = await self.connection_manager.execute_query(total_query, {})
            total_count = total_result[0]["count"] if total_result else 0
            
            # Get active count
            active_query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE is_deleted = 0"
            active_result = await self.connection_manager.execute_query(active_query, {})
            active_count = active_result[0]["count"] if active_result else 0
            
            # Get by model type
            type_query = f"SELECT model_type, COUNT(*) as count FROM {self.table_name} GROUP BY model_type"
            type_result = await self.connection_manager.execute_query(type_query, {})
            type_stats = {row["model_type"]: row["count"] for row in type_result}
            
            return {
                "total_registries": total_count,
                "active_registries": active_count,
                "inactive_registries": total_count - active_count,
                "by_model_type": type_stats,
                "table_name": self.table_name,
                "last_updated": await self._get_last_updated_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    async def get_trends(self, time_period: str) -> Dict[str, Any]:
        """Get temporal trends and patterns."""
        try:
            # Get creation trends by date
            if time_period == "daily":
                group_by = "DATE(created_at)"
            elif time_period == "weekly":
                group_by = "strftime('%Y-%W', created_at)"
            elif time_period == "monthly":
                group_by = "strftime('%Y-%m', created_at)"
            else:
                group_by = "DATE(created_at)"
            
            sql = f"SELECT {group_by} as period, COUNT(*) as count FROM {self.table_name} GROUP BY {group_by} ORDER BY period DESC LIMIT 30"
            result = await self.connection_manager.execute_query(sql, {})
            
            trends = {row["period"]: row["count"] for row in result}
            
            return {
                "time_period": time_period,
                "trends": trends,
                "total_registries": sum(trends.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return {}
    
    # ✅ REQUIRED: Enterprise Features (Missing from Template)
    
    async def get_by_user(self, user_id: str) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries by user ID."""
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE created_by = :user_id ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(sql, {"user_id": user_id})
            
            registries = []
            for row in result:
                try:
                    registry = self._dict_to_model(row)
                    registries.append(registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return registries
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by user {user_id}: {e}")
            return []
    
    async def get_by_organization(self, org_id: str) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries by organization ID."""
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE org_id = :org_id ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(sql, {"org_id": org_id})
            
            registries = []
            for row in result:
                try:
                    registry = self._dict_to_model(row)
                    registries.append(registry)
                except Exception as e:
                    logger.warning(f"Failed to create model from row: {e}")
                    continue
            
            return registries
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by organization {org_id}: {e}")
            return []
    
    async def get_audit_trail(self, ml_registry_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for an ML registry entry."""
        try:
            # This would typically query an audit log table
            # For now, return basic audit info from the main table
            registry = await self.get_by_id(ml_registry_id)
            if not registry:
                return []
            
            audit_trail = [
                {
                    "action": "created",
                    "timestamp": registry.created_at,
                    "user_id": registry.created_by,
                    "details": f"ML registry entry {ml_registry_id} created"
                }
            ]
            
            if registry.updated_at and registry.updated_at != registry.created_at:
                audit_trail.append({
                    "action": "updated",
                    "timestamp": registry.updated_at,
                    "user_id": registry.updated_by,
                    "details": f"ML registry entry {ml_registry_id} updated"
                })
            
            return audit_trail
            
        except Exception as e:
            logger.error(f"Failed to get audit trail for ML registry {ml_registry_id}: {e}")
            return []
    
    # ✅ REQUIRED: Utility & Maintenance Methods (Missing from Template)
    
    async def exists(self, ml_registry_id: str) -> bool:
        """Check if ML registry entry exists."""
        try:
            registry = await self.get_by_id(ml_registry_id)
            return registry is not None
        except Exception as e:
            logger.error(f"Failed to check existence of ML registry {ml_registry_id}: {e}")
            return False
    
    async def get_table_info(self) -> Dict[str, Any]:
        """Get comprehensive table information."""
        try:
            info = {
                "table_name": self.table_name,
                "primary_key": "ml_registry_id",
                "columns": self._get_columns(),
                "required_columns": ["ml_registry_id", "graph_id", "model_id", "session_id", "model_name", "model_type"],
                "audit_columns": ["created_at", "updated_at", "created_by", "updated_by"],
                "indexed_columns": ["ml_registry_id", "graph_id", "model_id", "model_type", "training_status", "deployment_status"],
                "schema_valid": True,  # We're using engine schema system
                "migration_needed": False
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {"error": str(e)}
    
    async def validate_entity(self, entity: Any) -> Dict[str, Any]:
        """Validate entity against repository schema."""
        try:
            validation_result = {
                "valid": False,
                "errors": [],
                "warnings": [],
                "schema_compliance": 0.0
            }
            
            # Check if entity has required fields
            required_fields = ["ml_registry_id", "graph_id", "model_id", "session_id", "model_name", "model_type"]
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(entity, field) or getattr(entity, field) is None:
                    missing_fields.append(field)
            
            if missing_fields:
                validation_result["errors"].append(f"Missing required fields: {missing_fields}")
            
            # Check schema compliance
            entity_fields = set(entity.__dict__.keys())
            schema_fields = set(self._get_columns())
            if entity_fields.issubset(schema_fields):
                validation_result["schema_compliance"] = 100.0
            else:
                validation_result["warnings"].append("Entity schema doesn't match repository schema")
                validation_result["schema_compliance"] = 50.0
            
            # Calculate overall validity
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Entity validation failed: {e}")
            return {"valid": False, "error": str(e)}
    
    async def _get_last_updated_timestamp(self) -> Optional[str]:
        """Get the timestamp of the last update in the repository."""
        try:
            sql = f"SELECT MAX(updated_at) as last_updated FROM {self.table_name}"
            result = await self.connection_manager.execute_query(sql, {})
            
            if result and result[0]["last_updated"]:
                return result[0]["last_updated"]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last updated timestamp: {e}")
            return None
    
    # ✅ REQUIRED: Cleanup method
    
    async def cleanup(self):
        """
        Cleanup repository resources.
    
        This method should be called when the repository is being shut down
        to ensure proper cleanup of resources.
        """
        try:
            logger.info(f"Cleaning up {self.__class__.__name__}")
            # No specific cleanup needed for this repository
            logger.info(f"{self.__class__.__name__} cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during {self.__class__.__name__} cleanup: {e}")


# ✅ REQUIRED: Export the repository class
__all__ = ['KGNeo4jMLRepository']


