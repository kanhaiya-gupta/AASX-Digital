"""
AI RAG Operations Repository
============================

Repository for AI RAG operations using engine ConnectionManager.
Implements world-class enterprise-grade repository standards with comprehensive
schema introspection, validation, and enterprise features.
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.schema.modules.ai_rag import AIRagSchema
from ..models.ai_rag_operations import AIRagOperations


class AIRagOperationsRepository:
    """
    World-Class Repository for AI RAG operations
    
    Implements enterprise-grade repository standards with comprehensive
    schema introspection, validation, and enterprise features.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the repository with database connection"""
        self.connection_manager = connection_manager
        self.table_name = "ai_rag_operations"
        self.logger = logging.getLogger(__name__)
        
        # Initialize repository
        asyncio.create_task(self.initialize())
    
    async def initialize(self) -> None:
        """Initialize the repository using the engine schema system."""
        try:
            # Check if table exists
            check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'"
            result = await self.connection_manager.execute_query(check_query)
            
            if not result or len(result) == 0:
                # Table doesn't exist, create it via schema
                self.logger.info(f"Table {self.table_name} does not exist, creating via schema...")
                schema = AIRagSchema(self.connection_manager)
                if await schema.initialize():
                    self.logger.info(f"Successfully created table {self.table_name} via AIRagSchema")
                else:
                    self.logger.error(f"Failed to create table {self.table_name} via schema")
                    raise Exception("Table creation failed via schema")
            else:
                self.logger.debug(f"Table {self.table_name} already exists")
            
            # Validate schema on startup
            if not await self._validate_schema():
                self.logger.warning("Schema validation failed - some features may not work correctly")
            else:
                self.logger.info("Schema validation successful")
                
            self.logger.info("AI RAG Operations Repository initialized successfully")
        except Exception as e:
            self.logger.error(f"Repository initialization failed: {e}")
            raise
    
    # ==================== SCHEMA INTROSPECTION METHODS ====================
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository"""
        return self.table_name
    
    def _get_columns(self) -> List[str]:
        """Get all column names for the ai_rag_operations table"""
        return [
            # Primary Identification
            "operation_id", "registry_id", "operation_type", "timestamp",
            
            # Session Information
            "session_id", "user_id", "query_text", "response_text",
            "session_start", "session_end", "session_duration_ms",
            
            # Generation Logs
            "generation_type", "input_data", "output_data", "generation_time_ms",
            "generation_quality_score",
            
            # Embeddings
            "embedding_id", "vector_data", "embedding_model", "embedding_dimensions",
            "embedding_quality_score", "vector_type", "model_provider", "model_parameters",
            "generation_timestamp", "generation_duration_ms", "generation_cost",
            "similarity_threshold", "confidence_score", "context", "storage_location",
            "storage_format", "compression_ratio",
            
            # Graph Metadata
            "graphs_json", "graph_count", "graph_types",
            
            # Source Information
            "source_documents", "source_entities", "source_relationships",
            
            # Processing Information
            "processing_status", "processing_start_time", "processing_end_time",
            "processing_duration_ms",
            
            # Quality Metrics
            "quality_score", "validation_status", "validation_errors",
            
            # File Storage References
            "output_directory", "output_files", "file_formats",
            
            # Integration References
            "kg_neo4j_graph_id", "aasx_integration_id", "twin_registry_id",
            
            # Tracing & Audit
            "created_by", "updated_by",
            
            # Organizational Hierarchy
            "org_id", "dept_id",
            
            # Performance Metrics
            "memory_usage_mb", "cpu_usage_percent",
            
            # Metadata
            "operation_metadata", "tags",
            
            # Timestamps
            "created_at", "updated_at"
        ]
    
    def _get_required_columns(self) -> List[str]:
        """Get required columns for the ai_rag_operations table"""
        return [
            "operation_id", "registry_id", "operation_type", "timestamp",
            "user_id", "org_id", "dept_id", "created_by"
        ]
    
    def _get_computed_fields(self) -> List[str]:
        """Get computed fields that should not be stored in database"""
        return [
            "overall_operation_score", "operation_efficiency_score", "resource_utilization_score",
            "operation_complexity_score", "optimization_priority", "maintenance_schedule",
            "session_efficiency_score", "cost_efficiency_score"
        ]
    
    # ==================== CORE CRUD OPERATIONS ====================
    
    async def create(self, entity: AIRagOperations) -> bool:
        """Create a new AI RAG operation"""
        try:
            # Convert model to dictionary
            entity_dict = self._model_to_dict(entity)
            
            # Build INSERT query
            columns = list(entity_dict.keys())
            placeholders = ", ".join([f":{col}" for col in columns])
            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Debug logging
            self.logger.debug(f"Creating AI RAG operation with query: {query}")
            self.logger.debug(f"Parameters: {entity_dict}")
            
            # Execute query
            result = await self.connection_manager.execute_query(query, entity_dict)
            
            # Debug logging
            self.logger.debug(f"Query result: {result} (type: {type(result)})")
            
                                    # Check if query was successful (SQLite INSERT returns None on success, raises exception on failure)
            # Since no exception was raised, the query was successful
            self.logger.info(f"Successfully created AI RAG operation: {entity.operation_id}")
            return True
                
        except Exception as e:
            self.logger.error(f"Error creating AI RAG operation: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def get_by_id(self, operation_id: str) -> Optional[AIRagOperations]:
        """Get AI RAG operation by ID"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE operation_id = :operation_id"
            result = await self.connection_manager.execute_query(query, {"operation_id": operation_id})
            
            if result and len(result) > 0:
                return self._dict_to_model(result[0])
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving AI RAG operation {operation_id}: {e}")
            return None
    
    async def update(self, operation_id: str, update_data: Dict[str, Any]) -> bool:
        """Update AI RAG operation"""
        try:
            # Check if entity exists
            existing = await self.get_by_id(operation_id)
            if not existing:
                self.logger.warning(f"AI RAG operation not found for update: {operation_id}")
                return False
            
            # Filter out computed fields
            filtered_data = {k: v for k, v in update_data.items() if k not in self._get_computed_fields()}
            
            if not filtered_data:
                self.logger.warning("No valid fields to update")
                return False
            
            # Build UPDATE query
            set_clause = ", ".join([f"{col} = :{col}" for col in filtered_data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause}, updated_at = datetime('now') WHERE operation_id = :operation_id"
            
            # Add operation_id to parameters
            filtered_data["operation_id"] = operation_id
            
            # Execute query
            result = await self.connection_manager.execute_query(query, filtered_data)
            
            # SQLite UPDATE returns None on success, raises exception on failure
            # Since no exception was raised, the query was successful
            self.logger.info(f"Successfully updated AI RAG operation: {operation_id}")
            return True
                
        except Exception as e:
            self.logger.error(f"Error updating AI RAG operation {operation_id}: {e}")
            return False
    
    async def delete(self, operation_id: str) -> bool:
        """Delete AI RAG operation"""
        try:
            # Check if entity exists
            existing = await self.get_by_id(operation_id)
            if not existing:
                self.logger.warning(f"AI RAG operation not found for deletion: {operation_id}")
                return False
            
            query = f"DELETE FROM {self.table_name} WHERE operation_id = :operation_id"
            result = await self.connection_manager.execute_query(query, {"operation_id": operation_id})
            
            # SQLite DELETE returns None on success, raises exception on failure
            # Since no exception was raised, the query was successful
            self.logger.info(f"Successfully deleted AI RAG operation: {operation_id}")
            return True
                
        except Exception as e:
            self.logger.error(f"Error deleting AI RAG operation {operation_id}: {e}")
            return False
    
    # ==================== SEARCH AND QUERY METHODS ====================
    
    async def search(self, search_criteria: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[AIRagOperations]:
        """Search AI RAG operations by criteria"""
        try:
            # Build WHERE clause
            where_conditions = []
            params = {}
            
            for key, value in search_criteria.items():
                if key in self._get_columns():
                    if isinstance(value, str):
                        where_conditions.append(f"{key} LIKE :{key}")
                        params[key] = f"%{value}%"
                    else:
                        where_conditions.append(f"{key} = :{key}")
                        params[key] = value
            
            # Build query
            query = f"SELECT * FROM {self.table_name}"
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            query += f" ORDER BY timestamp DESC LIMIT {limit} OFFSET {offset}"
            
            # Execute query
            result = await self.connection_manager.execute_query(query, params)
            
            # Convert to models
            operations = []
            for row in result:
                operations.append(self._dict_to_model(row))
            
            self.logger.info(f"Search returned {len(operations)} results")
            return operations
            
        except Exception as e:
            self.logger.error(f"Error searching AI RAG operations: {e}")
            return []
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[AIRagOperations]:
        """Get all AI RAG operations with pagination"""
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY timestamp DESC LIMIT {limit} OFFSET {offset}"
            result = await self.connection_manager.execute_query(query)
            
            operations = []
            for row in result:
                operations.append(self._dict_to_model(row))
            
            self.logger.info(f"Retrieved {len(operations)} operations (limit: {limit}, offset: {offset})")
            return operations
            
        except Exception as e:
            self.logger.error(f"Error getting all operations: {e}")
            return []
    
    async def get_by_registry_id(self, registry_id: str, limit: int = 100) -> List[AIRagOperations]:
        """Get operations by registry ID"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id ORDER BY timestamp DESC LIMIT {limit}"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            operations = []
            for row in result:
                operations.append(self._dict_to_model(row))
            
            return operations
            
        except Exception as e:
            self.logger.error(f"Error getting operations by registry ID {registry_id}: {e}")
            return []
    
    async def get_by_user_id(self, user_id: str, limit: int = 100) -> List[AIRagOperations]:
        """Get operations by user ID"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE user_id = :user_id ORDER BY timestamp DESC LIMIT {limit}"
            result = await self.connection_manager.execute_query(query, {"user_id": user_id})
            
            operations = []
            for row in result:
                operations.append(self._dict_to_model(row))
            
            return operations
            
        except Exception as e:
            self.logger.error(f"Error getting operations by user ID {user_id}: {e}")
            return []
    
    async def get_by_operation_type(self, operation_type: str, limit: int = 100) -> List[AIRagOperations]:
        """Get operations by operation type"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE operation_type = :operation_type ORDER BY timestamp DESC LIMIT {limit}"
            result = await self.connection_manager.execute_query(query, {"operation_type": operation_type})
            
            operations = []
            for row in result:
                operations.append(self._dict_to_model(row))
            
            return operations
            
        except Exception as e:
            self.logger.error(f"Error getting operations by type {operation_type}: {e}")
            return []
    
    # ==================== UTILITY METHODS ====================
    
    async def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for AI RAG operations"""
        try:
            # Total operations
            total_query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            total_result = await self.connection_manager.execute_query(total_query)
            total_operations = total_result[0]["total"] if total_result else 0
            
            # Operations by type
            type_query = f"SELECT operation_type, COUNT(*) as count FROM {self.table_name} GROUP BY operation_type"
            type_result = await self.connection_manager.execute_query(type_query)
            operations_by_type = {row["operation_type"]: row["count"] for row in type_result}
            
            # Recent operations
            recent_query = f"SELECT COUNT(*) as recent FROM {self.table_name} WHERE timestamp >= datetime('now', '-24 hours')"
            recent_result = await self.connection_manager.execute_query(recent_query)
            recent_operations = recent_result[0]["recent"] if recent_result else 0
            
            return {
                "total_operations": total_operations,
                "operations_by_type": operations_by_type,
                "recent_operations_24h": recent_operations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting summary: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check repository health"""
        try:
            # Check table exists
            check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'"
            result = await self.connection_manager.execute_query(check_query)
            table_exists = len(result) > 0 if result else False
            
            # Check connection
            connection_healthy = await self.connection_manager.is_connected()
            
            # Check basic query
            basic_query = f"SELECT COUNT(*) as count FROM {self.table_name} LIMIT 1"
            basic_result = await self.connection_manager.execute_query(basic_query)
            basic_query_works = basic_result is not None
            
            return {
                "status": "healthy" if all([table_exists, connection_healthy, basic_query_works]) else "degraded",
                "table_exists": table_exists,
                "connection_healthy": connection_healthy,
                "basic_query_works": basic_query_works,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ==================== DATA CONVERSION METHODS ====================
    
    def _model_to_dict(self, entity: AIRagOperations) -> Dict[str, Any]:
        """Convert AIRagOperations model to dictionary for database operations"""
        try:
            # Get model data
            entity_dict = entity.model_dump()
            
            # Filter out computed fields
            computed_fields = self._get_computed_fields()
            entity_dict = {k: v for k, v in entity_dict.items() if k not in computed_fields}
            
            # ✅ CRITICAL: Filter to only include fields that exist in database schema
            # This prevents schema mismatch errors by removing extra fields from EngineBaseModel
            schema_fields = set(self._get_columns())
            entity_dict = {k: v for k, v in entity_dict.items() if k in schema_fields}
            self.logger.debug(f"After filtering schema fields: {list(entity_dict.keys())}")
            
            # Handle JSON fields
            json_fields = ["graphs_json", "graph_types", "source_documents", "source_entities", 
                          "source_relationships", "validation_errors", "output_files", "file_formats", 
                          "model_parameters", "operation_metadata", "tags"]
            
            for field in json_fields:
                if field in entity_dict and entity_dict[field] is not None:
                    if isinstance(entity_dict[field], dict):
                        entity_dict[field] = json.dumps(entity_dict[field])
                    elif isinstance(entity_dict[field], str):
                        # Already a string, validate it's valid JSON
                        try:
                            json.loads(entity_dict[field])
                        except json.JSONDecodeError:
                            # Invalid JSON, convert to empty dict
                            entity_dict[field] = "{}"
            
            return entity_dict
            
        except Exception as e:
            self.logger.error(f"Error converting model to dict: {e}")
            return {}
    
    def _dict_to_model(self, data: Dict[str, Any]) -> AIRagOperations:
        """Convert database dictionary to AIRagOperations model"""
        try:
            # Handle JSON fields
            json_fields = ["graphs_json", "graph_types", "source_documents", "source_entities", 
                          "source_relationships", "validation_errors", "output_files", "file_formats", 
                          "model_parameters", "operation_metadata", "tags"]
            
            for field in json_fields:
                if field in data and data[field] is not None:
                    if isinstance(data[field], str):
                        try:
                            data[field] = json.loads(data[field])
                        except json.JSONDecodeError:
                            data[field] = {}
                    elif isinstance(data[field], dict):
                        # Already a dict, keep as is
                        pass
                    else:
                        data[field] = {}
            
            # Handle datetime fields
            datetime_fields = ["timestamp", "session_start", "session_end", "generation_timestamp", 
                             "processing_start_time", "processing_end_time", "created_at", "updated_at"]
            
            for field in datetime_fields:
                if field in data and data[field] is not None:
                    if isinstance(data[field], datetime):
                        data[field] = data[field].isoformat()
                    elif isinstance(data[field], str):
                        # Already a string, keep as is
                        pass
                    else:
                        data[field] = None
            
            # Create model instance
            return AIRagOperations(**data)
            
        except Exception as e:
            self.logger.error(f"Error converting dict to model: {e}")
            raise
    
    # ==================== SCHEMA VALIDATION ====================
    
    async def _validate_schema(self) -> bool:
        """Validate that the table schema matches expected columns"""
        try:
            # Get actual table schema
            schema_query = f"PRAGMA table_info({self.table_name})"
            schema_result = await self.connection_manager.execute_query(schema_query)
            
            if not schema_result:
                self.logger.error("Could not retrieve table schema")
                return False
            
            # Extract column names
            actual_columns = [row["name"] for row in schema_result]
            expected_columns = set(self._get_columns())
            
            # Check for missing columns
            missing_columns = expected_columns - set(actual_columns)
            if missing_columns:
                self.logger.warning(f"Missing columns in {self.table_name}: {missing_columns}")
            
            # Check for extra columns
            extra_columns = set(actual_columns) - expected_columns
            if extra_columns:
                self.logger.warning(f"Extra columns in {self.table_name}: {extra_columns}")
            
            # Schema is valid if all required columns exist
            required_columns = set(self._get_required_columns())
            schema_valid = required_columns.issubset(set(actual_columns))
            
            if schema_valid:
                self.logger.info(f"Schema validation successful for {self.table_name}")
            else:
                self.logger.error(f"Schema validation failed for {self.table_name}")
            
            return schema_valid
            
        except Exception as e:
            self.logger.error(f"Error validating schema: {e}")
            return False
    
    async def _validate_entity_schema(self, entity: AIRagOperations) -> bool:
        """Validate entity against database schema"""
        try:
            # Get entity data
            entity_dict = self._model_to_dict(entity)
            
            # Check required fields
            required_fields = self._get_required_columns()
            for field in required_fields:
                if field not in entity_dict or entity_dict[field] is None:
                    self.logger.error(f"Required field missing: {field}")
                    return False
            
            # Check field types and constraints
            # This is a basic validation - more sophisticated validation can be added
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating entity schema: {e}")
            return False
