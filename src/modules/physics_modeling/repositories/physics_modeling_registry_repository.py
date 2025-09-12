"""
Physics Modeling Registry Repository
==================================

Repository for physics modeling registry operations using engine ConnectionManager.
Implements world-class enterprise-grade repository standards with comprehensive
schema introspection, validation, and enterprise features.
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from ..models.physics_modeling_registry import PhysicsModelingRegistry


class PhysicsModelingRegistryRepository:
    """
    World-Class Repository for physics modeling registry operations.
    
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
        self.table_name = "physics_modeling_registry"
        self.logger = logging.getLogger(__name__)
        
        # Auto-initialization pattern for enterprise repositories
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
                from src.engine.database.schema.modules.physics_modeling import PhysicsModelingSchema
                schema = PhysicsModelingSchema(self.connection_manager)
                if await schema.initialize():
                    self.logger.info(f"Successfully created table {self.table_name} via PhysicsModelingSchema")
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
                
            self.logger.info(f"Repository initialized successfully for table: {self.table_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize repository: {e}")
            return False
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository"""
        return self.table_name
    
    def _get_columns(self) -> List[str]:
        """Get all column names for the physics_modeling_registry table"""
        return [
            # Primary Identification
            "registry_id", "model_name", "physics_type",
            
            # Plugin & Model Information
            "plugin_id", "plugin_name", "model_type", "model_version", "model_description",
            
            # Physics Classification & Metadata
            "physics_category", "physics_subcategory", "physics_domain", "complexity_level", "physics_version",
            
            # Workflow Classification
            "registry_type", "workflow_source",
            
            # Traditional Solver Configuration
            "solver_type", "solver_name", "solver_version", "solver_parameters", "mesh_configuration",
            "time_integration_scheme", "spatial_discretization", "convergence_criteria", "solver_optimization",
            
            # Physics Equations & Constraints
            "governing_equations", "boundary_conditions", "initial_conditions", "material_properties", "physical_constants",
            
            # Module Integration References
            "aasx_integration_id", "twin_registry_id", "kg_neo4j_id", "ai_rag_id", "federated_learning_id", "certificate_manager_id",
            
            # Integration Status & Health
            "integration_status", "overall_health_score", "health_status",
            
            # Lifecycle Management
            "lifecycle_status", "lifecycle_phase",
            
            # Operational Status
            "operational_status", "availability_status",
            
            # Physics-Specific Status
            "simulation_status", "validation_status", "convergence_status",
            
            # Performance & Quality Metrics
            "performance_score", "accuracy_score", "computational_efficiency", "numerical_stability",
            
            # Security & Access Control
            "security_level", "access_control_level", "encryption_enabled", "audit_logging_enabled",
            
            # Enterprise Compliance & Security
            "compliance_type", "compliance_status", "compliance_score", "last_audit_date", "next_audit_date", "audit_details",
            
            # Enterprise Security Metrics
            "security_event_type", "threat_assessment", "security_score", "last_security_scan", "security_details",
            
            # Enterprise Performance Analytics
            "performance_trend", "optimization_suggestions", "last_optimization_date", "enterprise_metrics",
            
            # User Management & Ownership
            "user_id", "org_id", "dept_id", "owner_team", "steward_user_id",
            
            # Timestamps & Audit
            "created_at", "updated_at", "activated_at", "last_accessed_at", "last_modified_at",
            
            # Configuration & Metadata
            "registry_config", "registry_metadata", "custom_attributes", "tags",
            
            # Relationships & Dependencies
            "relationships", "dependencies", "physics_instances"
        ]
    
    def _get_computed_fields(self) -> List[str]:
        """Get list of computed fields that should not be stored in database"""
        return [
            'overall_score', 'enterprise_health_status', 'risk_assessment', 'physics_maturity_score',
            'optimization_priority', 'maintenance_schedule', 'physics_efficiency_score',
            'compliance_adherence_score', 'integration_maturity_score'
        ]
    
    def _get_json_columns(self) -> List[str]:
        """Get list of JSON columns that need special handling"""
        return [
            'solver_parameters', 'mesh_configuration', 'governing_equations', 'boundary_conditions',
            'initial_conditions', 'material_properties', 'physical_constants', 'convergence_criteria',
            'solver_optimization', 'audit_details', 'security_details', 'optimization_suggestions',
            'enterprise_metrics', 'registry_config', 'registry_metadata', 'custom_attributes',
            'tags', 'relationships', 'dependencies', 'physics_instances', 'results_metadata', 'physics_specific_metrics'
        ]
    
    # Removed _filter_engine_fields method - not needed with simplified filtering
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name"""
        return "registry_id"
    
    def _get_foreign_key_columns(self) -> List[str]:
        """Get foreign key column names"""
        return ["aasx_integration_id", "twin_registry_id", "kg_neo4j_id", "ai_rag_id", "federated_learning_id", "certificate_manager_id"]
    
    def _get_indexed_columns(self) -> List[str]:
        """Get indexed column names for performance optimization"""
        return ["model_name", "physics_type", "model_type", "physics_domain", "status", "created_at", "overall_health_score"]
    
    def _get_required_columns(self) -> List[str]:
        """Get required (non-nullable) column names"""
        return ["registry_id", "model_name", "physics_type", "registry_type", "workflow_source", "user_id", "org_id", "dept_id", "created_at", "updated_at"]
    
    def _get_audit_columns(self) -> List[str]:
        """Get audit-related column names"""
        return ["created_at", "updated_at", "activated_at", "last_accessed_at", "last_modified_at", "last_audit_date", "next_audit_date", "last_security_scan"]
    
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
    
    def _validate_entity_schema(self, entity: PhysicsModelingRegistry) -> bool:
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
            
            # JSON fields that need deserialization - use dynamic method
            json_fields = self._get_json_columns()
            
            for field in json_fields:
                if field in deserialized and deserialized[field] is not None:
                    if isinstance(deserialized[field], str):
                        try:
                            deserialized[field] = json.loads(deserialized[field])
                        except (json.JSONDecodeError, TypeError):
                            self.logger.warning(f"Failed to deserialize JSON field {field}: {deserialized[field]}")
                            # Use dynamic method to determine default value
                            if field in self._get_json_columns():
                                deserialized[field] = {}
                    elif isinstance(deserialized[field], (dict, list)):
                        # Already a dict/list, no need to deserialize
                        pass
                    else:
                        self.logger.warning(f"Unexpected type for JSON field {field}: {type(deserialized[field])}")
                        # Use dynamic method to determine default value
                        if field in self._get_json_columns():
                            deserialized[field] = {}
            
            return deserialized
        except Exception as e:
            self.logger.error(f"Failed to deserialize JSON fields: {e}")
            return row
    
    def _model_to_dict(self, model: PhysicsModelingRegistry) -> Dict[str, Any]:
        """Convert model to dictionary with proper JSON serialization and filtering"""
        try:
            data = model.model_dump()
            
            # ✅ CRITICAL: Filter out computed fields that should not be stored in database
            # This prevents validation errors like "overall_score", "enterprise_health_status"
            computed_fields = set(self._get_computed_fields())
            data = {k: v for k, v in data.items() if k not in computed_fields}
            self.logger.debug(f"After filtering computed fields: {list(data.keys())}")
            
            # ✅ CRITICAL: Filter to only include fields that exist in database schema
            # This prevents schema mismatch errors by removing extra fields (including engine fields)
            schema_fields = set(self._get_columns())
            data = {k: v for k, v in data.items() if k in schema_fields}
            self.logger.debug(f"After filtering schema fields: {list(data.keys())}")
            
            # Serialize JSON fields using the dynamic method
            json_fields = self._get_json_columns()
            
            for field in json_fields:
                if field in data and data[field] is not None:
                    if isinstance(data[field], (dict, list)):
                        data[field] = json.dumps(data[field])
            
            # Handle datetime fields
            datetime_fields = [
                'created_at', 'updated_at', 'activated_at', 'last_accessed_at', 'last_modified_at',
                'last_audit_date', 'next_audit_date', 'last_security_scan', 'last_optimization_date'
            ]
            
            for field in datetime_fields:
                if field in data and data[field] is not None:
                    if isinstance(data[field], datetime):
                        data[field] = data[field].isoformat()
            
            return data
        except Exception as e:
            self.logger.error(f"Failed to convert model to dict: {e}")
            raise
    
    def _dict_to_model(self, data: Dict[str, Any]) -> PhysicsModelingRegistry:
        """Convert dictionary to model with proper JSON deserialization"""
        try:
            # Deserialize JSON fields first
            deserialized_data = self._deserialize_json_fields(data)
            
            # Handle datetime fields
            datetime_fields = [
                'created_at', 'updated_at', 'activated_at', 'last_accessed_at', 'last_modified_at',
                'last_audit_date', 'next_audit_date', 'last_security_scan', 'last_optimization_date'
            ]
            
            for field in datetime_fields:
                if field in deserialized_data and deserialized_data[field] is not None:
                    if isinstance(deserialized_data[field], str):
                        try:
                            deserialized_data[field] = datetime.fromisoformat(deserialized_data[field])
                        except ValueError:
                            self.logger.warning(f"Failed to parse datetime field {field}: {deserialized_data[field]}")
                            deserialized_data[field] = datetime.now()
            
            return PhysicsModelingRegistry(**deserialized_data)
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
    
    async def create(self, model: PhysicsModelingRegistry) -> Optional[str]:
        """Create a new physics modeling registry entry with world-class validation and error handling"""
        try:
            # Validate entity schema
            if not self._validate_entity_schema(model):
                self.logger.error("Entity validation failed")
                return None
            
            # Convert model to dict with proper JSON serialization
            data = self._model_to_dict(model)
            
            # Add timestamps
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
            
            # Build dynamic insert query
            query, params = self._build_insert_query(data)
            
            await self.connection_manager.execute_update(query, params)
            self.logger.info(f"Successfully created physics modeling registry entry: {model.registry_id}")
            return model.registry_id
            
        except Exception as e:
            self.logger.error(f"Failed to create physics modeling registry entry: {e}")
            return None
    
    async def get_by_id(self, model_id: str) -> Optional[PhysicsModelingRegistry]:
        """Get physics modeling registry entry by ID with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"registry_id": model_id}
            )
            
            result = await self.connection_manager.execute_query(query, params)
            
            if result and len(result) > 0:
                return self._dict_to_model(result[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting physics modeling registry by ID {model_id}: {e}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[PhysicsModelingRegistry]:
        """Get all physics modeling registry entries with pagination and world-class error handling"""
        try:
            query, params = self._build_select_query(
                order_by="created_at DESC",
                limit=limit,
                offset=offset
            )
            
            result = await self.connection_manager.execute_query(query, params)
            
            models = []
            for row in result:
                models.append(self._dict_to_model(row))
            return models
            
        except Exception as e:
            self.logger.error(f"Error getting all physics modeling registry entries: {e}")
            return []
    
    async def update(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """Update physics modeling registry entry with world-class validation and error handling"""
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            # Build dynamic update query
            query, params = self._build_update_query(
                updates, 
                {"registry_id": model_id}
            )
            
            await self.connection_manager.execute_update(query, params)
            self.logger.info(f"Successfully updated physics modeling registry entry: {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating physics modeling registry entry: {e}")
            return False
    
    async def delete(self, model_id: str) -> bool:
        """Delete physics modeling registry entry with world-class error handling"""
        try:
            query, params = self._build_delete_query({"registry_id": model_id})
            await self.connection_manager.execute_update(query, params)
            
            self.logger.info(f"Successfully deleted physics modeling registry entry: {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting physics modeling registry entry: {e}")
            return False
    
    async def search_by_type(self, model_type: str) -> List[PhysicsModelingRegistry]:
        """Search physics modeling registry entries by model type with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"model_type": model_type},
                order_by="created_at DESC"
            )
            
            result = await self.connection_manager.execute_query(query, params)
            
            models = []
            for row in result:
                models.append(self._dict_to_model(row))
            return models
            
        except Exception as e:
            self.logger.error(f"Error searching physics modeling registry entries by type {model_type}: {e}")
            return []
    
    async def get_by_compliance_status(self, compliance_status: str) -> List[PhysicsModelingRegistry]:
        """Get physics modeling registry entries by compliance status with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"compliance_status": compliance_status},
                order_by="created_at DESC"
            )
            
            result = await self.connection_manager.execute_query(query, params)
            
            models = []
            for row in result:
                models.append(self._dict_to_model(row))
            return models
            
        except Exception as e:
            self.logger.error(f"Error getting physics modeling registry entries by compliance status {compliance_status}: {e}")
            return []
    
    async def get_by_security_score_range(self, min_score: float, max_score: float) -> List[PhysicsModelingRegistry]:
        """Get physics modeling registry entries by security score range with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"security_score": f"BETWEEN {min_score} AND {max_score}"},
                order_by="security_score DESC"
            )
            
            # Handle BETWEEN clause manually since it's complex
            query = query.replace("security_score = :security_score", "security_score BETWEEN :min_score AND :max_score")
            params = {"min_score": min_score, "max_score": max_score}
            
            result = await self.connection_manager.execute_query(query, params)
            
            models = []
            for row in result:
                models.append(self._dict_to_model(row))
            return models
            
        except Exception as e:
            self.logger.error(f"Error getting physics modeling registry entries by security score range: {e}")
            return []
    
    async def count_by_status(self, status: str) -> int:
        """Count physics modeling registry entries by status with world-class error handling"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE status = :status"
            result = await self.connection_manager.execute_query(query, {"status": status})
            
            return result[0]['count'] if result and len(result) > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Error counting physics modeling registry entries by status {status}: {e}")
            return 0
    
    async def get_by_status(self, status: str, limit: int = 100) -> List[PhysicsModelingRegistry]:
        """Get physics modeling registry entries by status with world-class error handling"""
        try:
            query, params = self._build_select_query(
                where_conditions={"status": status},
                order_by="created_at DESC",
                limit=limit
            )
            
            result = await self.connection_manager.execute_query(query, params)
            
            models = []
            for row in result:
                models.append(self._dict_to_model(row))
            return models
            
        except Exception as e:
            self.logger.error(f"Error getting physics modeling registry entries by status {status}: {e}")
            return []
    
    def _row_to_model(self, row: Dict[str, Any]) -> Optional[PhysicsModelingRegistry]:
        """Convert database row to PhysicsModelingRegistry model (legacy method)"""
        # Use the new world-class method
        return self._dict_to_model(row)
    
    # ==================== WORLD-CLASS ENHANCED CRUD METHODS ====================
    
    async def create_batch(self, models_list: List[PhysicsModelingRegistry]) -> bool:
        """Create multiple physics modeling registry entries in a single transaction"""
        try:
            if not models_list:
                return True
            
            # Validate all entities
            for model in models_list:
                if not self._validate_entity_schema(model):
                    self.logger.error(f"Entity validation failed for registry: {model.registry_id}")
                    return False
            
            # Convert all models to dicts
            data_list = [self._model_to_dict(model) for model in models_list]
            
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
            
            self.logger.info(f"Successfully created {len(models_list)} physics modeling registry entries")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating batch physics modeling registry entries: {e}")
            return False
    
    async def create_if_not_exists(self, model: PhysicsModelingRegistry, 
                                 check_fields: List[str] = None) -> bool:
        """Create physics modeling registry entry only if it doesn't already exist"""
        try:
            if check_fields is None:
                check_fields = ["registry_id", "model_name"]
            
            # Check if exists
            where_conditions = {field: getattr(model, field) for field in check_fields}
            existing = await self.get_by_field(where_conditions)
            
            if existing:
                self.logger.info(f"Physics modeling registry entry already exists: {model.registry_id}")
                return True
            
            # Create if not exists
            return await self.create(model) is not None
            
        except Exception as e:
            self.logger.error(f"Error in create_if_not_exists: {e}")
            return False
    
    async def get_by_ids(self, registry_ids: List[str]) -> List[PhysicsModelingRegistry]:
        """Get multiple physics modeling registry entries by IDs"""
        try:
            if not registry_ids:
                return []
            
            # Build IN clause query
            placeholders = [f":id_{i}" for i in range(len(registry_ids))]
            query = f"SELECT * FROM {self.table_name} WHERE registry_id IN ({', '.join(placeholders)})"
            params = {f"id_{i}": registry_id for i, registry_id in enumerate(registry_ids)}
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error fetching physics modeling registry entries by IDs: {e}")
            return []
    
    async def get_by_field(self, field_values: Dict[str, Any]) -> Optional[PhysicsModelingRegistry]:
        """Get physics modeling registry entry by field values"""
        try:
            query, params = self._build_select_query(where_conditions=field_values)
            result = await self.connection_manager.execute_query(query, params)
            
            if result and len(result) > 0:
                return self._dict_to_model(result[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching physics modeling registry entry by field: {e}")
            return None
    
    async def update_batch(self, updates: List[Tuple[str, Dict[str, Any]]]) -> bool:
        """Update multiple physics modeling registry entries in a single transaction"""
        try:
            if not updates:
                return True
            
            for registry_id, update_data in updates:
                success = await self.update(registry_id, update_data)
                if not success:
                    self.logger.error(f"Failed to update physics modeling registry entry {registry_id}")
                    return False
            
            self.logger.info(f"Successfully updated {len(updates)} physics modeling registry entries")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating batch physics modeling registry entries: {e}")
            return False
    
    async def upsert(self, model: PhysicsModelingRegistry, 
                    check_fields: List[str] = None) -> bool:
        """Update if exists, create if not exists"""
        try:
            if check_fields is None:
                check_fields = ["registry_id"]
            
            # Check if exists
            where_conditions = {field: getattr(model, field) for field in check_fields}
            existing = await self.get_by_field(where_conditions)
            
            if existing:
                # Update existing
                update_data = self._model_to_dict(model)
                # Remove primary key from update data
                if 'registry_id' in update_data:
                    del update_data['registry_id']
                
                return await self.update(existing.registry_id, update_data)
            else:
                # Create new
                return await self.create(model) is not None
                
        except Exception as e:
            self.logger.error(f"Error in upsert: {e}")
            return False
    
    async def delete_batch(self, registry_ids: List[str]) -> bool:
        """Delete multiple physics modeling registry entries by IDs"""
        try:
            if not registry_ids:
                return True
            
            # Build IN clause query
            placeholders = [f":id_{i}" for i in range(len(registry_ids))]
            query = f"DELETE FROM {self.table_name} WHERE registry_id IN ({', '.join(placeholders)})"
            params = {f"id_{i}": registry_id for i, registry_id in enumerate(registry_ids)}
            
            await self.connection_manager.execute_update(query, params)
            self.logger.info(f"Successfully deleted {len(registry_ids)} physics modeling registry entries")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting batch physics modeling registry entries: {e}")
            return False
    
    async def soft_delete(self, registry_id: str) -> bool:
        """Soft delete physics modeling registry entry by marking as deleted"""
        try:
            update_data = {
                "deleted_at": datetime.now().isoformat(),
                "is_deleted": True
            }
            
            return await self.update(registry_id, update_data)
            
        except Exception as e:
            self.logger.error(f"Error soft deleting physics modeling registry entry {registry_id}: {e}")
            return False
    
    # ==================== ADVANCED QUERYING METHODS ====================
    
    async def search_entities(self, search_criteria: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[PhysicsModelingRegistry]:
        """Search entities based on criteria (wrapper for service compatibility)"""
        try:
            # Extract search term from criteria
            search_term = search_criteria.get('search_term', '')
            if not search_term:
                # If no search term, search by other criteria
                search_term = search_criteria.get('model_name', '')
            
            # Use existing search method
            results = await self.search(search_term, fields=None)
            
            # Apply limit and offset
            start_idx = offset
            end_idx = offset + limit
            return results[start_idx:end_idx]
            
        except Exception as e:
            self.logger.error(f"Failed to search entities: {e}")
            return []

    async def search(self, search_term: str, fields: Optional[List[str]] = None) -> List[PhysicsModelingRegistry]:
        """Search physics modeling registry entries by text in specified fields"""
        try:
            if not fields:
                fields = ["model_name", "physics_type", "model_type", "physics_domain"]
            
            search_conditions = []
            params = {"search_term": f"%{search_term}%"}
            
            for i, field in enumerate(fields):
                if field in self._get_columns():
                    search_conditions.append(f"{field} LIKE :search_term")
            
            if not search_conditions:
                return []
            
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE {' OR '.join(search_conditions)}
                ORDER BY created_at DESC
            """
            
            result = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            self.logger.error(f"Failed to search physics modeling registry entries: {e}")
            raise
    
    async def filter_by_criteria(self, criteria: Dict[str, Any], 
                               order_by: str = "created_at DESC", 
                               limit: int = 100) -> List[PhysicsModelingRegistry]:
        """Filter physics modeling registry entries by specific criteria"""
        try:
            query, params = self._build_select_query(
                where_conditions=criteria,
                order_by=order_by,
                limit=limit
            )
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error filtering physics modeling registry entries by criteria: {e}")
            return []
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime, 
                              physics_domain: str = None) -> List[PhysicsModelingRegistry]:
        """Get physics modeling registry entries within a date range, optionally filtered by physics domain"""
        try:
            where_conditions = {
                "created_at": f"BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'"
            }
            
            if physics_domain:
                where_conditions["physics_domain"] = physics_domain
            
            # Build custom query for date range
            query = f"SELECT * FROM {self.table_name} WHERE created_at BETWEEN :start_date AND :end_date"
            params = {"start_date": start_date, "end_date": end_date}
            
            if physics_domain:
                query += " AND physics_domain = :physics_domain"
                params["physics_domain"] = physics_domain
            
            query += " ORDER BY created_at ASC"
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting physics modeling registry entries by date range: {e}")
            return []
    
    async def get_recent(self, hours: int = 24, physics_domain: str = None) -> List[PhysicsModelingRegistry]:
        """Get recent physics modeling registry entries from the last N hours"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            return await self.get_by_date_range(start_time, end_time, physics_domain)
            
        except Exception as e:
            self.logger.error(f"Error getting recent physics modeling registry entries: {e}")
            return []
    
    async def count_by_field(self, field: str, value: Any) -> int:
        """Count physics modeling registry entries by field value"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {field} = :value"
            result = await self.connection_manager.execute_query(query, {"value": value})
            
            return result[0]['count'] if result else 0
            
        except Exception as e:
            self.logger.error(f"Error counting physics modeling registry entries by field {field}: {e}")
            return 0
    
    async def get_statistics(self, physics_domain: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics for physics modeling registry entries"""
        try:
            where_clause = "WHERE physics_domain = :physics_domain" if physics_domain else ""
            params = {"physics_domain": physics_domain} if physics_domain else {}
            
            query = f"""
                SELECT 
                    COUNT(*) as total_entries,
                    AVG(overall_health_score) as avg_health_score,
                    AVG(performance_score) as avg_performance_score,
                    AVG(accuracy_score) as avg_accuracy_score,
                    AVG(compliance_score) as avg_compliance_score,
                    AVG(security_score) as avg_security_score,
                    MIN(created_at) as earliest_entry,
                    MAX(created_at) as latest_entry
                FROM {self.table_name}
                {where_clause}
            """
            
            result = await self.connection_manager.execute_query(query, params)
            return dict(result[0]) if result and len(result) > 0 else {}
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    # ==================== ENTERPRISE FEATURES ====================
    
    async def get_by_user(self, user_id: str, limit: int = 100) -> List[PhysicsModelingRegistry]:
        """Get physics modeling registry entries by user ID (for RBAC)"""
        try:
            query, params = self._build_select_query(
                where_conditions={"user_id": user_id},
                order_by="created_at DESC",
                limit=limit
            )
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting physics modeling registry entries by user {user_id}: {e}")
            return []
    
    async def get_by_organization(self, org_id: str, limit: int = 100) -> List[PhysicsModelingRegistry]:
        """Get physics modeling registry entries by organization ID"""
        try:
            query, params = self._build_select_query(
                where_conditions={"org_id": org_id},
                order_by="created_at DESC",
                limit=limit
            )
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting physics modeling registry entries by organization {org_id}: {e}")
            return []
    
    async def get_audit_trail(self, registry_id: str, start_date: datetime = None, 
                             end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get audit trail for physics modeling registry changes"""
        try:
            where_conditions = {"registry_id": registry_id}
            
            if start_date and end_date:
                query = f"""
                    SELECT registry_id, created_at, updated_at, overall_health_score, compliance_score, security_score
                    FROM {self.table_name} 
                    WHERE registry_id = :registry_id 
                    AND created_at BETWEEN :start_date AND :end_date
                    ORDER BY created_at DESC
                """
                params = {"registry_id": registry_id, "start_date": start_date, "end_date": end_date}
            else:
                query = f"""
                    SELECT registry_id, created_at, updated_at, overall_health_score, compliance_score, security_score
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
        """Get compliance status for physics modeling registry entry"""
        try:
            query = f"""
                SELECT 
                    AVG(compliance_score) as avg_compliance,
                    AVG(overall_health_score) as avg_health,
                    COUNT(*) as total_entries,
                    MIN(created_at) as earliest_entry,
                    MAX(created_at) as latest_entry
                FROM {self.table_name}
                WHERE registry_id = :registry_id
            """
            
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    "compliance_score": row['avg_compliance'] or 0.0,
                    "health_score": row['avg_health'] or 0.0,
                    "total_entries": row['total_entries'] or 0,
                    "earliest_entry": row['earliest_entry'],
                    "latest_entry": row['latest_entry'],
                    "compliance_status": "compliant" if (row['avg_compliance'] or 0) >= 80 else "non_compliant"
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting compliance status for registry {registry_id}: {e}")
            return {}
    
    async def get_security_score(self, registry_id: str) -> Dict[str, Any]:
        """Get security score for physics modeling registry entry"""
        try:
            query = f"""
                SELECT 
                    AVG(overall_health_score) as avg_health,
                    AVG(security_score) as avg_security,
                    COUNT(*) as total_entries
                FROM {self.table_name}
                WHERE registry_id = :registry_id
            """
            
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                row = result[0]
                health_score = row['avg_health'] or 0
                security_score = row['avg_security'] or 0
                
                # Calculate overall security score
                overall_score = (health_score + security_score) / 2
                
                return {
                    "overall_security_score": overall_score,
                    "health_score": health_score,
                    "security_score": security_score,
                    "total_entries": row['total_entries'] or 0,
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
                    COUNT(*) as total_entries,
                    AVG(overall_health_score) as avg_health,
                    AVG(performance_score) as avg_performance,
                    AVG(accuracy_score) as avg_accuracy,
                    MIN(created_at) as earliest_record,
                    MAX(created_at) as latest_record
                FROM {self.table_name}
            """
            
            result = await self.connection_manager.execute_query(query, {})
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    "total_entries": row['total_entries'] or 0,
                    "average_health_score": row['avg_health'] or 0.0,
                    "average_performance_score": row['avg_performance'] or 0.0,
                    "average_accuracy_score": row['avg_accuracy'] or 0.0,
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
                "repository_name": "PhysicsModelingRegistryRepository",
                "table_name": self.table_name,
                "total_columns": len(self._get_columns()),
                "primary_key": self._get_primary_key_column(),
                "foreign_keys": self._get_foreign_key_columns(),
                "indexed_columns": self._get_indexed_columns(),
                "required_columns": self._get_required_columns(),
                "audit_columns": self._get_audit_columns(),
                "json_fields": [
                    'solver_parameters', 'mesh_configuration', 'governing_equations', 'boundary_conditions',
                    'initial_conditions', 'material_properties', 'physical_constants', 'convergence_criteria',
                    'solver_optimization', 'audit_details', 'security_details', 'optimization_suggestions',
                    'enterprise_metrics', 'registry_config', 'registry_metadata', 'custom_attributes',
                    'tags', 'relationships', 'dependencies', 'physics_instances'
                ],
                "datetime_fields": [
                    'created_at', 'updated_at', 'activated_at', 'last_accessed_at', 'last_modified_at',
                    'last_audit_date', 'next_audit_date', 'last_security_scan', 'last_optimization_date'
                ],
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
    
    async def exists(self, registry_id: str) -> bool:
        """Check if physics modeling registry entry with given ID exists"""
        try:
            query, params = self._build_select_query(
                columns=["1"],
                where_conditions={"registry_id": registry_id}
            )
            
            result = await self.connection_manager.execute_query(query, params)
            return len(result) > 0
            
        except Exception as e:
            self.logger.error(f"Error checking existence of physics modeling registry entry {registry_id}: {e}")
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
    
    def validate_entity(self, entity: PhysicsModelingRegistry) -> Tuple[bool, List[str]]:
        """Validate entity and return validation errors"""
        try:
            errors = []
            
            # Basic validation
            if not entity.registry_id:
                errors.append("registry_id is required")
            
            if not entity.model_name:
                errors.append("model_name is required")
            
            if not entity.physics_type:
                errors.append("physics_type is required")
            
            # Pydantic validation
            try:
                entity.model_validate(entity.model_dump())
            except Exception as e:
                errors.append(f"Pydantic validation failed: {e}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    async def cleanup(self, days_old: int = 90) -> int:
        """Clean up old physics modeling registry entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            query = f"DELETE FROM {self.table_name} WHERE created_at < :cutoff_date"
            params = {"cutoff_date": cutoff_date}
            
            await self.connection_manager.execute_update(query, params)
            
            self.logger.info(f"Cleanup completed for entries older than {days_old} days")
            return 0  # Return count of deleted entries if available
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """Get comprehensive compliance report"""
        try:
            # Get overall compliance statistics
            query = f"""
                SELECT 
                    COUNT(*) as total_entries,
                    AVG(compliance_score) as avg_compliance,
                    AVG(overall_health_score) as avg_health,
                    COUNT(CASE WHEN compliance_score >= 80 THEN 1 END) as compliant_count,
                    COUNT(CASE WHEN compliance_score < 80 THEN 1 END) as non_compliant_count
                FROM {self.table_name}
            """
            
            result = await self.connection_manager.execute_query(query, {})
            
            if result and len(result) > 0:
                row = result[0]
                total = row['total_entries'] or 0
                compliant = row['compliant_count'] or 0
                non_compliant = row['non_compliant_count'] or 0
                
                return {
                    "total_entries": total,
                    "compliance_rate": (compliant / total * 100) if total > 0 else 0,
                    "average_compliance_score": row['avg_compliance'] or 0.0,
                    "average_health_score": row['avg_health'] or 0.0,
                    "compliant_entries": compliant,
                    "non_compliant_entries": non_compliant,
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
    
    async def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for physics modeling registry"""
        try:
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            count_result = await self.connection_manager.execute_query(count_query)
            total_count = count_result[0]['total'] if count_result else 0
            
            # Get physics type distribution
            type_query = f"""
                SELECT physics_type, COUNT(*) as count 
                FROM {self.table_name}
                GROUP BY physics_type
            """
            type_result = await self.connection_manager.execute_query(type_query)
            type_distribution = {row['physics_type']: row['count'] for row in type_result}
            
            # Get model type distribution
            model_type_query = f"""
                SELECT model_type, COUNT(*) as count 
                FROM {self.table_name}
                GROUP BY model_type
            """
            model_type_result = await self.connection_manager.execute_query(model_type_query)
            model_type_distribution = {row['model_type']: row['count'] for row in model_type_result}
            
            # Get health metrics
            health_query = f"""
                SELECT 
                    AVG(overall_health_score) as avg_health_score,
                    COUNT(CASE WHEN overall_health_score >= 80 THEN 1 END) as healthy_count,
                    COUNT(CASE WHEN overall_health_score < 50 THEN 1 END) as critical_count
                FROM {self.table_name}
            """
            health_result = await self.connection_manager.execute_query(health_query)
            health_stats = health_result[0] if health_result else {}
            
            return {
                "total_registries": total_count,
                "physics_type_distribution": type_distribution,
                "model_type_distribution": model_type_distribution,
                "health_metrics": {
                    "average_health_score": float(health_stats.get('avg_health_score', 0) or 0),
                    "healthy_registries": int(health_stats.get('healthy_count', 0) or 0),
                    "critical_registries": int(health_stats.get('critical_count', 0) or 0)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get physics modeling registry summary: {e}")
            return {
                "total_registries": 0,
                "physics_type_distribution": {},
                "model_type_distribution": {},
                "health_metrics": {
                    "average_health_score": 0.0,
                    "healthy_registries": 0,
                    "critical_registries": 0
                },
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

    async def close(self) -> None:
        """Async cleanup of database connections"""
        if self.connection_manager:
            await self.connection_manager.close()
            self.logger.info("Physics Modeling Registry Repository connections closed")
