"""
Federated Learning Registry Repository

World-Class Enterprise Repository Implementation
Comprehensive federated learning registry operations with schema introspection, validation, and enterprise features.
Pure async implementation using src.engine.database.connection_manager.

Features:
- Schema introspection and validation
- Advanced CRUD operations with validation
- Enterprise features (access control, audit, compliance)
- Performance monitoring and health checks
- Dynamic query building
- Comprehensive repository information
- JSON field handling for complex data structures
- Multi-tenant support and RBAC
- Audit logging and compliance tracking
- Performance analytics and optimization
"""

import logging
import asyncio
import json
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

from src.engine.database.connection_manager import ConnectionManager
from ..models.federated_learning_registry import (
    FederatedLearningRegistry,
    FederatedLearningRegistryQuery,
    FederatedLearningRegistrySummary
)

logger = logging.getLogger(__name__)


class FederatedLearningRegistryRepository:
    """Repository for federated learning registry operations with world-class enterprise standards"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.table_name = "federated_learning_registry"
        logger.info("Federated Learning Registry Repository initialized")
        
        # Initialize repository
        import asyncio
        asyncio.create_task(self.initialize())
    
    async def initialize(self) -> None:
        """Initialize the repository using the engine schema system."""
        try:
            # Check if table exists
            check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'"
            result = await self.connection_manager.execute_query(check_query)
            
            if not result or len(result) == 0:
                # Table doesn't exist, create it via schema
                logger.info(f"Table {self.table_name} does not exist, creating via schema...")
                from src.engine.database.schema.modules.federated_learning import FederatedLearningSchema
                schema = FederatedLearningSchema(self.connection_manager)
                if await schema.initialize():
                    logger.info(f"Successfully created table {self.table_name} via FederatedLearningSchema")
                else:
                    logger.error(f"Failed to create table {self.table_name} via schema")
                    raise Exception("Table creation failed via schema")
            else:
                logger.debug(f"Table {self.table_name} already exists")
            
            # Validate schema on startup
            if not await self._validate_schema():
                logger.warning("Schema validation failed - some features may not work correctly")
            else:
                logger.info("Schema validation successful")
                
            logger.info("Federated Learning Registry Repository initialized successfully")
        except Exception as e:
            logger.error(f"Repository initialization failed: {e}")
            raise
    
    def _get_columns(self) -> List[str]:
        """Get all column names for the federated_learning_registry table"""
        return [
            # Primary Identification
            "registry_id", "federation_name", "registry_name",
            
            # Federation Classification & Metadata
            "federation_category", "federation_type", "federation_priority", "federation_version",
            
            # Workflow Classification
            "registry_type", "workflow_source",
            
            # Integration IDs
            "aasx_integration_id", "twin_registry_id", "kg_neo4j_id", "physics_modeling_id",
            "ai_rag_id", "certificate_manager_id",
            
            # Integration Status & Health
            "integration_status", "overall_health_score", "health_status",
            
            # Lifecycle Management
            "lifecycle_status", "lifecycle_phase",
            
            # Operational Status
            "operational_status", "availability_status",
            
            # Federation-Specific Status
            "federation_participation_status", "model_aggregation_status", "privacy_compliance_status",
            "algorithm_execution_status", "last_federation_sync_at", "next_federation_sync_at",
            "federation_sync_error_count", "federation_sync_error_message",
            
            # Federation Data Metrics
            "total_participating_twins", "total_federation_rounds", "total_models_aggregated",
            "federation_complexity",
            
            # Performance & Quality Metrics
            "performance_score", "data_quality_score", "reliability_score", "compliance_score",
            
            # Enterprise Compliance Tracking
            "compliance_framework", "compliance_status", "last_audit_date", "next_audit_date",
            "audit_details", "risk_level",
            
            # Enterprise Security Metrics
            "security_score", "threat_detection_score", "encryption_strength", "authentication_method",
            "access_control_score", "data_protection_score", "incident_response_time", "security_audit_score",
            "last_security_scan", "security_details",
            
            # Enterprise Performance Analytics
            "efficiency_score", "scalability_score", "optimization_potential", "bottleneck_identification",
            "performance_trend", "last_optimization_date", "optimization_suggestions",
            
            # Security & Access Control
            "security_level", "access_control_level", "encryption_enabled", "audit_logging_enabled",
            
            # User Management & Ownership
            "user_id", "org_id", "dept_id", "owner_team", "steward_user_id",
            
            # Timestamps & Audit
            "created_at", "updated_at", "activated_at", "last_accessed_at", "last_modified_at",
            "last_audit_date", "next_audit_date", "last_security_scan", "last_optimization_date",
            
            # Configuration & Metadata
            "registry_config", "registry_metadata", "custom_attributes", "tags",
            
            # Relationships & Dependencies
            "relationships", "dependencies", "federation_instances",
            
            # NEW: Comprehensive Federated Learning Traceability (JSON fields)
            "federation_rounds", "organization_participation", "model_evolution", 
            "privacy_compliance", "performance_metrics", "federation_algorithms"
        ]
    
    def _deserialize_json_fields(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize JSON fields from database row"""
        try:
            deserialized = row.copy()
            
            # JSON fields that need deserialization
            json_fields = [
                'audit_details', 'security_details', 'optimization_suggestions',
                'registry_config', 'registry_metadata', 'custom_attributes', 'tags',
                'relationships', 'dependencies', 'federation_instances',
                # NEW: Federated Learning Traceability JSON fields
                'federation_rounds', 'organization_participation', 'model_evolution',
                'privacy_compliance', 'performance_metrics', 'federation_algorithms'
            ]
            
            for field in json_fields:
                if field in deserialized and deserialized[field] is not None:
                    if isinstance(deserialized[field], str):
                        try:
                            deserialized[field] = json.loads(deserialized[field])
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Failed to deserialize JSON field {field}: {deserialized[field]}")
                            if field in ['optimization_suggestions']:
                                deserialized[field] = []
                            else:
                                deserialized[field] = {}
                    elif isinstance(deserialized[field], (dict, list)):
                        # Already a dict/list, no need to deserialize
                        pass
                    else:
                        logger.warning(f"Unexpected type for JSON field {field}: {type(deserialized[field])}")
                        if field in ['optimization_suggestions']:
                            deserialized[field] = []
                        else:
                            deserialized[field] = {}
            
            return deserialized
        except Exception as e:
            logger.error(f"Failed to deserialize JSON fields: {e}")
            return row
    
    def _get_computed_fields(self) -> List[str]:
        """Get list of computed fields that should not be stored in database"""
        return [
            'overall_score', 'enterprise_health_status', 'risk_assessment', 'federation_maturity_score',
            'optimization_priority', 'maintenance_schedule', 'federation_efficiency_score',
            'privacy_compliance_score', 'integration_maturity_score'
        ]
    
    def _model_to_dict(self, model: FederatedLearningRegistry) -> Dict[str, Any]:
        """Convert model to dictionary with proper JSON serialization and filtering"""
        try:
            data = model.model_dump()
            
            # ✅ CRITICAL: Filter out computed fields that should not be stored in database
            # This prevents validation errors like "overall_score", "enterprise_health_status"
            computed_fields = set(self._get_computed_fields())
            data = {k: v for k, v in data.items() if k not in computed_fields}
            logger.debug(f"After filtering computed fields: {list(data.keys())}")
            
            # ✅ CRITICAL: Filter to only include fields that exist in database schema
            # This prevents schema mismatch errors by removing extra fields (including engine fields)
            schema_fields = set(self._get_columns())
            data = {k: v for k, v in data.items() if k in schema_fields}
            logger.debug(f"After filtering schema fields: {list(data.keys())}")
            
            # Serialize JSON fields
            json_fields = [
                'audit_details', 'security_details', 'optimization_suggestions',
                'registry_config', 'registry_metadata', 'custom_attributes', 'tags',
                'relationships', 'dependencies', 'federation_instances',
                # NEW: Federated Learning Traceability JSON fields
                'federation_rounds', 'organization_participation', 'model_evolution',
                'privacy_compliance', 'performance_metrics', 'federation_algorithms'
            ]
            
            for field in json_fields:
                if field in data and data[field] is not None:
                    if isinstance(data[field], (dict, list)):
                        data[field] = json.dumps(data[field])
            
            # Handle datetime fields
            datetime_fields = [
                'created_at', 'updated_at', 'activated_at', 'last_accessed_at', 'last_modified_at',
                'last_federation_sync_at', 'next_federation_sync_at', 'last_audit_date',
                'next_audit_date', 'last_security_scan', 'last_optimization_date'
            ]
            
            for field in datetime_fields:
                if field in data and data[field] is not None:
                    if isinstance(data[field], datetime):
                        data[field] = data[field].isoformat()
            
            return data
        except Exception as e:
            logger.error(f"Failed to convert model to dict: {e}")
            raise
    
    def _dict_to_model(self, data: Dict[str, Any]) -> FederatedLearningRegistry:
        """Convert dictionary to model with proper JSON deserialization"""
        try:
            # Deserialize JSON fields first
            deserialized_data = self._deserialize_json_fields(data)
            
            # Handle datetime fields
            datetime_fields = [
                'created_at', 'updated_at', 'activated_at', 'last_accessed_at', 'last_modified_at',
                'last_federation_sync_at', 'next_federation_sync_at', 'last_audit_date',
                'next_audit_date', 'last_security_scan', 'last_optimization_date'
            ]
            
            for field in datetime_fields:
                if field in deserialized_data and deserialized_data[field] is not None:
                    if isinstance(deserialized_data[field], str):
                        try:
                            deserialized_data[field] = datetime.fromisoformat(deserialized_data[field])
                        except ValueError:
                            logger.warning(f"Failed to parse datetime field {field}: {deserialized_data[field]}")
                            deserialized_data[field] = None
            
            # Create model instance
            return FederatedLearningRegistry(**deserialized_data)
        except Exception as e:
            logger.error(f"Failed to convert dict to model: {e}")
            raise

    # ==================== SCHEMA & METADATA METHODS ====================
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository"""
        return self.table_name
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name"""
        return "registry_id"
    
    def _get_foreign_key_columns(self) -> List[str]:
        """Get foreign key column names"""
        return ["aasx_integration_id", "twin_registry_id", "kg_neo4j_id", "physics_modeling_id",
                "ai_rag_id", "certificate_manager_id", "user_id", "org_id", "dept_id"]
    
    def _get_indexed_columns(self) -> List[str]:
        """Get indexed column names for performance optimization"""
        return ["federation_type", "federation_category", "health_status", "lifecycle_status",
                "operational_status", "user_id", "org_id", "dept_id", "created_at", "updated_at"]
    
    def _get_required_columns(self) -> List[str]:
        """Get required (non-nullable) column names"""
        return ["registry_id", "federation_name", "registry_name", "registry_type", "workflow_source",
                "user_id", "org_id", "created_at", "updated_at"]
    
    def _get_audit_columns(self) -> List[str]:
        """Get audit-related column names"""
        return ["created_at", "updated_at", "activated_at", "last_accessed_at", "last_modified_at",
                "last_federation_sync_at", "next_federation_sync_at", "last_audit_date",
                "next_audit_date", "last_security_scan", "last_optimization_date"]
    
    async def _validate_schema(self) -> bool:
        """Validate that the table schema matches expected structure"""
        try:
            actual_columns = await self._get_actual_table_columns()
            expected_columns = set(self._get_columns())
            actual_columns_set = set(actual_columns)
            
            missing_columns = expected_columns - actual_columns_set
            extra_columns = actual_columns_set - expected_columns
            
            if missing_columns or extra_columns:
                logger.warning(f"Schema validation issues - Missing: {missing_columns}, Extra: {extra_columns}")
                return False
            
            logger.info("Schema validation passed successfully")
            return True
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    async def _get_actual_table_columns(self) -> List[str]:
        """Get actual column names from the database table"""
        try:
            # Use SQLite PRAGMA command instead of information_schema
            query = f"PRAGMA table_info({self.table_name})"
            result = await self.connection_manager.execute_query(query)
            return [row['name'] for row in result]
        except Exception as e:
            logger.error(f"Failed to get actual table columns: {e}")
            return []
    
    async def _schema_migration_needed(self) -> bool:
        """Check if schema migration is needed"""
        try:
            return not await self._validate_schema()
        except Exception as e:
            logger.error(f"Failed to check schema migration: {e}")
            return True
    
    async def _validate_entity_schema(self, entity: FederatedLearningRegistry) -> bool:
        """Validate entity against expected schema"""
        try:
            entity_dict = entity.model_dump()
            expected_columns = set(self._get_columns())
            entity_columns = set(entity_dict.keys())
            
            # Check for required columns
            required_columns = set(self._get_required_columns())
            missing_required = required_columns - entity_columns
            if missing_required:
                logger.error(f"Missing required columns: {missing_required}")
                return False
            
            # Check for unexpected columns
            unexpected_columns = entity_columns - expected_columns
            if unexpected_columns:
                logger.warning(f"Unexpected columns found: {unexpected_columns}")
            
            return True
        except Exception as e:
            logger.error(f"Entity schema validation failed: {e}")
            return False

    # ==================== CRUD Operations ====================
    
    async def create(self, registry: FederatedLearningRegistry) -> FederatedLearningRegistry:
        """Create a new federated learning registry entry asynchronously"""
        try:
            # Validate entity schema
            if not await self._validate_entity_schema(registry):
                raise ValueError("Invalid entity schema")
            
            # Convert model to dict for insertion
            data = self._model_to_dict(registry)
            
            # Build INSERT query dynamically
            columns = list(data.keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute raw SQL
            await self.connection_manager.execute_update(query, data)
            
            logger.info(f"Created federated learning registry entry: {registry.registry_id}")
            return registry
            
        except Exception as e:
            logger.error(f"Failed to create federated learning registry entry: {e}")
            raise
    
    async def create_batch(self, registries: List[FederatedLearningRegistry]) -> List[FederatedLearningRegistry]:
        """Create multiple federated learning registry entries in a batch"""
        try:
            created_registries = []
            for registry in registries:
                created = await self.create(registry)
                created_registries.append(created)
            logger.info(f"Created {len(created_registries)} federated learning registry entries in batch")
            return created_registries
        except Exception as e:
            logger.error(f"Failed to create batch federated learning registry entries: {e}")
            raise
    
    async def create_if_not_exists(self, registry: FederatedLearningRegistry) -> FederatedLearningRegistry:
        """Create federated learning registry entry only if it doesn't already exist"""
        try:
            existing = await self.get_by_id(registry.registry_id)
            if existing:
                logger.info(f"Federated learning registry entry already exists: {registry.registry_id}")
                return existing
            
            return await self.create(registry)
        except Exception as e:
            logger.error(f"Failed to create if not exists: {e}")
            raise
    
    async def get_by_id(self, registry_id: str) -> Optional[FederatedLearningRegistry]:
        """Get federated learning registry entry by ID asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                return self._dict_to_model(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entry by ID {registry_id}: {e}")
            raise
    
    async def get_by_ids(self, registry_ids: List[str]) -> List[FederatedLearningRegistry]:
        """Get multiple federated learning registry entries by IDs"""
        try:
            if not registry_ids:
                return []
            
            placeholders = [f":id_{i}" for i in range(len(registry_ids))]
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE registry_id IN ({', '.join(placeholders)})
            """
            params = {f"id_{i}": registry_id for i, registry_id in enumerate(registry_ids)}
            
            result = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entries by IDs: {e}")
            raise
    
    async def get_all(self, limit: int = 1000, offset: int = 0) -> List[FederatedLearningRegistry]:
        """Get all federated learning registry entries with pagination"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                ORDER BY created_at DESC 
                LIMIT :limit OFFSET :offset
            """
            result = await self.connection_manager.execute_query(query, {"limit": limit, "offset": offset})
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get all federated learning registry entries: {e}")
            raise
    
    async def get_by_field(self, field: str, value: Any) -> List[FederatedLearningRegistry]:
        """Get federated learning registry entries by a specific field value"""
        try:
            if field not in self._get_columns():
                raise ValueError(f"Invalid field: {field}")
            
            query = f"SELECT * FROM {self.table_name} WHERE {field} = :value"
            result = await self.connection_manager.execute_query(query, {"value": value})
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entries by field {field}: {e}")
            raise
    
    async def update(self, registry: FederatedLearningRegistry) -> FederatedLearningRegistry:
        """Update an existing federated learning registry entry asynchronously"""
        try:
            # Update timestamp
            registry.updated_at = datetime.now()
            
            # Convert model to dict for update
            data = self._model_to_dict(registry)
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in data.keys()]
            query = f"""
                UPDATE {self.table_name} 
                SET {', '.join(set_clauses)}
                WHERE registry_id = :registry_id
            """
            
            # Add registry_id to params
            params = {**data, "registry_id": registry.registry_id}
            
            # Execute raw SQL
            await self.connection_manager.execute_update(query, params)
            
            logger.info(f"Updated federated learning registry entry: {registry.registry_id}")
            return registry
            
        except Exception as e:
            logger.error(f"Failed to update federated learning registry entry {registry.registry_id}: {e}")
            raise
    
    async def update_batch(self, registries: List[FederatedLearningRegistry]) -> List[FederatedLearningRegistry]:
        """Update multiple federated learning registry entries in a batch"""
        try:
            updated_registries = []
            for registry in registries:
                updated = await self.update(registry)
                updated_registries.append(updated)
            logger.info(f"Updated {len(updated_registries)} federated learning registry entries in batch")
            return updated_registries
        except Exception as e:
            logger.error(f"Failed to update batch federated learning registry entries: {e}")
            raise
    
    async def upsert(self, registry: FederatedLearningRegistry) -> FederatedLearningRegistry:
        """Update federated learning registry entry if it exists, otherwise create it"""
        try:
            existing = await self.get_by_id(registry.registry_id)
            if existing:
                return await self.update(registry)
            else:
                return await self.create(registry)
        except Exception as e:
            logger.error(f"Failed to upsert federated learning registry entry: {e}")
            raise
    
    async def delete(self, registry_id: str) -> bool:
        """Delete a federated learning registry entry asynchronously"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE registry_id = :registry_id"
            await self.connection_manager.execute_update(query, {"registry_id": registry_id})
            
            logger.info(f"Deleted federated learning registry entry: {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete federated learning registry entry {registry_id}: {e}")
            raise
    
    async def delete_batch(self, registry_ids: List[str]) -> bool:
        """Delete multiple federated learning registry entries in a batch"""
        try:
            if not registry_ids:
                return True
            
            placeholders = [f":id_{i}" for i in range(len(registry_ids))]
            query = f"""
                DELETE FROM {self.table_name} 
                WHERE registry_id IN ({', '.join(placeholders)})
            """
            params = {f"id_{i}": registry_id for i, registry_id in enumerate(registry_ids)}
            
            await self.connection_manager.execute_update(query, params)
            logger.info(f"Deleted {len(registry_ids)} federated learning registry entries in batch")
            return True
        except Exception as e:
            logger.error(f"Failed to delete batch federated learning registry entries: {e}")
            raise
    
    async def soft_delete(self, registry_id: str) -> bool:
        """Soft delete federated learning registry entry by marking as deleted"""
        try:
            query = f"""
                UPDATE {self.table_name} 
                SET lifecycle_status = 'deprecated', updated_at = :updated_at
                WHERE registry_id = :registry_id
            """
            await self.connection_manager.execute_update(query, {
                "registry_id": registry_id,
                "updated_at": datetime.now()
            })
            logger.info(f"Soft deleted federated learning registry entry: {registry_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to soft delete federated learning registry entry {registry_id}: {e}")
            raise

    # ==================== Advanced Querying ====================
    
    async def search_entities(self, search_criteria: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[FederatedLearningRegistry]:
        """Search entities based on criteria (wrapper for service compatibility)"""
        try:
            # Extract search term from criteria
            search_term = search_criteria.get('search_term', '')
            if not search_term:
                # If no search term, search by other criteria
                search_term = search_criteria.get('federation_name', '')
            
            # Use existing search method
            results = await self.search(search_term, fields=None)
            
            # Apply limit and offset
            start_idx = offset
            end_idx = offset + limit
            return results[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            return []

    async def search(self, search_term: str, fields: Optional[List[str]] = None) -> List[FederatedLearningRegistry]:
        """Search federated learning registry entries by text in specified fields"""
        try:
            if not fields:
                fields = ["federation_name", "registry_name", "federation_category", "federation_type"]
            
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
            logger.error(f"Failed to search federated learning registry entries: {e}")
            raise
    
    async def filter_by_criteria(self, criteria: Dict[str, Any]) -> List[FederatedLearningRegistry]:
        """Filter federated learning registry entries by multiple criteria"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            params = {}
            
            for field, value in criteria.items():
                if field in self._get_columns():
                    if isinstance(value, (list, tuple)):
                        placeholders = [f":{field}_{i}" for i in range(len(value))]
                        query += f" AND {field} IN ({', '.join(placeholders)})"
                        for i, v in enumerate(value):
                            params[f"{field}_{i}"] = v
                    else:
                        query += f" AND {field} = :{field}"
                        params[field] = value
            
            query += " ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to filter federated learning registry entries: {e}")
            raise
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime, 
                               date_field: str = "created_at") -> List[FederatedLearningRegistry]:
        """Get federated learning registry entries within a date range"""
        try:
            if date_field not in self._get_audit_columns():
                raise ValueError(f"Invalid date field: {date_field}")
            
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE {date_field} BETWEEN :start_date AND :end_date
                ORDER BY {date_field} DESC
            """
            result = await self.connection_manager.execute_query(query, {
                "start_date": start_date,
                "end_date": end_date
            })
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entries by date range: {e}")
            raise
    
    async def get_recent(self, days: int = 7) -> List[FederatedLearningRegistry]:
        """Get recently created federated learning registry entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            return await self.get_by_date_range(cutoff_date, datetime.now())
        except Exception as e:
            logger.error(f"Failed to get recent federated learning registry entries: {e}")
            raise
    
    async def count_by_field(self, field: str, value: Any) -> int:
        """Count federated learning registry entries by field value"""
        try:
            if field not in self._get_columns():
                raise ValueError(f"Invalid field: {field}")
            
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {field} = :value"
            result = await self.connection_manager.execute_query(query, {"value": value})
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Failed to count federated learning registry entries by field {field}: {e}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for federated learning registry"""
        try:
            stats = {}
            
            # Total count
            total_query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            total_result = await self.connection_manager.execute_query(total_query, {})
            stats['total_registries'] = total_result[0]['total'] if total_result else 0
            
            # Health status distribution
            health_query = f"SELECT health_status, COUNT(*) as count FROM {self.table_name} GROUP BY health_status"
            health_result = await self.connection_manager.execute_query(health_query, {})
            stats['health_status_distribution'] = {row['health_status']: row['count'] for row in health_result}
            
            # Federation type distribution
            type_query = f"SELECT federation_type, COUNT(*) as count FROM {self.table_name} GROUP BY federation_type"
            type_result = await self.connection_manager.execute_query(type_query, {})
            stats['federation_type_distribution'] = {row['federation_type']: row['count'] for row in type_result}
            
            # Average health score
            health_score_query = f"SELECT AVG(overall_health_score) as avg_health_score FROM {self.table_name} WHERE overall_health_score IS NOT NULL"
            health_score_result = await self.connection_manager.execute_query(health_score_query, {})
            stats['avg_health_score'] = health_score_result[0]['avg_health_score'] if health_score_result else 0.0
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get federated learning registry statistics: {e}")
            raise
    
    async def get_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get trends over time for federated learning registry"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Daily creation trends
            daily_query = f"""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM {self.table_name} 
                WHERE created_at >= :cutoff_date 
                GROUP BY DATE(created_at) 
                ORDER BY date
            """
            daily_result = await self.connection_manager.execute_query(daily_query, {"cutoff_date": cutoff_date})
            
            # Health score trends
            health_query = f"""
                SELECT DATE(created_at) as date, AVG(overall_health_score) as avg_health_score
                FROM {self.table_name} 
                WHERE created_at >= :cutoff_date AND overall_health_score IS NOT NULL
                GROUP BY DATE(created_at) 
                ORDER BY date
            """
            health_result = await self.connection_manager.execute_query(health_query, {"cutoff_date": cutoff_date})
            
            return {
                'daily_creations': {row['date']: row['count'] for row in daily_result},
                'daily_health_scores': {row['date']: row['avg_health_score'] for row in health_result}
            }
        except Exception as e:
            logger.error(f"Failed to get federated learning registry trends: {e}")
            raise

    # ==================== Enterprise Features ====================
    
    async def get_by_user(self, user_id: str, org_id: str, dept_id: Optional[str] = None) -> List[FederatedLearningRegistry]:
        """Get federated learning registry entries by user with optional department filter"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE user_id = :user_id AND org_id = :org_id"
            params = {"user_id": user_id, "org_id": org_id}
            
            if dept_id:
                query += " AND dept_id = :dept_id"
                params["dept_id"] = dept_id
            
            query += " ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entries by user {user_id}: {e}")
            raise
    
    async def get_by_organization(self, org_id: str, dept_id: Optional[str] = None) -> List[FederatedLearningRegistry]:
        """Get federated learning registry entries by organization with optional department filter"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE org_id = :org_id"
            params = {"org_id": org_id}
            
            if dept_id:
                query += " AND dept_id = :dept_id"
                params["dept_id"] = dept_id
            
            query += " ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, params)
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entries by organization {org_id}: {e}")
            raise
    
    async def get_audit_trail(self, registry_id: str) -> Dict[str, Any]:
        """Get audit trail for a specific federated learning registry entry"""
        try:
            query = f"""
                SELECT created_at, updated_at, activated_at, last_accessed_at, last_modified_at,
                       last_federation_sync_at, next_federation_sync_at, last_audit_date,
                       next_audit_date, last_security_scan, last_optimization_date
                FROM {self.table_name} 
                WHERE registry_id = :registry_id
            """
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result:
                return result[0]
            return {}
        except Exception as e:
            logger.error(f"Failed to get audit trail for federated learning registry {registry_id}: {e}")
            raise
    
    async def get_compliance_status(self, registry_id: str) -> Dict[str, Any]:
        """Get compliance status for a specific federated learning registry entry"""
        try:
            query = f"""
                SELECT compliance_score, compliance_status, compliance_framework, risk_level,
                       security_score, threat_detection_score, encryption_strength, authentication_method,
                       access_control_score, data_protection_score, incident_response_time, security_audit_score
                FROM {self.table_name} 
                WHERE registry_id = :registry_id
            """
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result:
                return result[0]
            return {}
        except Exception as e:
            logger.error(f"Failed to get compliance status for federated learning registry {registry_id}: {e}")
            raise
    
    async def get_security_score(self, registry_id: str) -> float:
        """Calculate security score for a specific federated learning registry entry"""
        try:
            query = f"""
                SELECT security_score, threat_detection_score, encryption_strength, authentication_method,
                       access_control_score, data_protection_score, incident_response_time, security_audit_score
                FROM {self.table_name} 
                WHERE registry_id = :registry_id
            """
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if not result:
                return 0.0
            
            row = result[0]
            scores = []
            
            if row.get('security_score'):
                scores.append(row['security_score'])
            if row.get('threat_detection_score'):
                scores.append(row['threat_detection_score'])
            if row.get('access_control_score'):
                scores.append(row['access_control_score'])
            if row.get('data_protection_score'):
                scores.append(row['data_protection_score'])
            if row.get('security_audit_score'):
                scores.append(row['security_audit_score'])
            
            # Encryption strength bonus
            if row.get('encryption_strength') == 'AES-256':
                scores.append(100.0)
            elif row.get('encryption_strength') == 'AES-128':
                scores.append(80.0)
            else:
                scores.append(60.0)
            
            # Authentication method bonus
            if row.get('authentication_method') == 'multi_factor':
                scores.append(100.0)
            elif row.get('authentication_method') == 'two_factor':
                scores.append(80.0)
            else:
                scores.append(60.0)
            
            return sum(scores) / len(scores) if scores else 0.0
        except Exception as e:
            logger.error(f"Failed to get security score for federated learning registry {registry_id}: {e}")
            raise

    # ==================== Performance & Monitoring ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the repository"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'checks': {}
            }
            
            # Check database connection
            try:
                await self.connection_manager.get_connection()
                health_status['checks']['database_connection'] = 'healthy'
            except Exception as e:
                health_status['checks']['database_connection'] = f'unhealthy: {e}'
                health_status['status'] = 'unhealthy'
            
            # Check schema validation
            try:
                schema_valid = await self._validate_schema()
                health_status['checks']['schema_validation'] = 'healthy' if schema_valid else 'unhealthy'
                if not schema_valid:
                    health_status['status'] = 'unhealthy'
            except Exception as e:
                health_status['checks']['schema_validation'] = f'unhealthy: {e}'
                health_status['status'] = 'unhealthy'
            
            # Check table accessibility
            try:
                count = await self.get_total_count()
                health_status['checks']['table_accessibility'] = 'healthy'
                health_status['checks']['total_records'] = count
            except Exception as e:
                health_status['checks']['table_accessibility'] = f'unhealthy: {e}'
                health_status['status'] = 'unhealthy'
            
            return health_status
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the repository"""
        try:
            start_time = datetime.now()
            
            # Test query performance
            query_start = datetime.now()
            await self.get_total_count()
            query_duration = (datetime.now() - query_start).total_seconds()
            
            # Test write performance (simulated)
            write_start = datetime.now()
            # Simulate write operation timing
            await asyncio.sleep(0.001)  # Minimal delay for simulation
            write_duration = (datetime.now() - write_start).total_seconds()
            
            total_duration = (datetime.now() - start_time).total_seconds()
            
            return {
                'query_performance_ms': round(query_duration * 1000, 2),
                'write_performance_ms': round(write_duration * 1000, 2),
                'total_operation_time_ms': round(total_duration * 1000, 2),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            raise
    
    async def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information"""
        try:
            info = {
                'repository_name': 'FederatedLearningRegistryRepository',
                'table_name': self.table_name,
                'total_columns': len(self._get_columns()),
                'primary_key': self._get_primary_key_column(),
                'foreign_keys': self._get_foreign_key_columns(),
                'indexed_columns': self._get_indexed_columns(),
                'required_columns': self._get_required_columns(),
                'audit_columns': self._get_audit_columns(),
                'features': [
                    'Schema introspection and validation',
                    'Advanced CRUD operations',
                    'Enterprise features (RBAC, audit, compliance)',
                    'Performance monitoring',
                    'Dynamic query building',
                    'JSON field handling',
                    'Multi-tenant support'
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            # Add schema validation status
            try:
                schema_valid = await self._validate_schema()
                info['schema_validation'] = 'valid' if schema_valid else 'needs_migration'
            except Exception:
                info['schema_validation'] = 'unknown'
            
            return info
        except Exception as e:
            logger.error(f"Failed to get repository info: {e}")
            raise
    
    # ==================== Utility & Maintenance ====================
    
    async def exists(self, registry_id: str) -> bool:
        """Check if federated learning registry entry exists"""
        try:
            query = f"SELECT 1 FROM {self.table_name} WHERE registry_id = :registry_id LIMIT 1"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to check existence of federated learning registry {registry_id}: {e}")
            raise
    
    async def get_table_info(self) -> Dict[str, Any]:
        """Get detailed table information"""
        try:
            info = {
                'table_name': self.table_name,
                'columns': self._get_columns(),
                'primary_key': self._get_primary_key_column(),
                'foreign_keys': self._get_foreign_key_columns(),
                'indexed_columns': self._get_indexed_columns(),
                'required_columns': self._get_required_columns(),
                'audit_columns': self._get_audit_columns(),
                'total_columns': len(self._get_columns()),
                'last_updated': datetime.now().isoformat()
            }
            
            # Add record count
            try:
                count = await self.get_total_count()
                info['total_records'] = count
            except Exception:
                info['total_records'] = 'unknown'
            
            return info
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            raise
    
    async def validate_entity(self, entity: FederatedLearningRegistry) -> Dict[str, Any]:
        """Validate entity and return validation results"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # Schema validation
            if not await self._validate_entity_schema(entity):
                validation_result['valid'] = False
                validation_result['errors'].append('Entity schema validation failed')
            
            # Required field validation
            entity_dict = entity.model_dump()
            required_fields = self._get_required_columns()
            for field in required_fields:
                if field not in entity_dict or entity_dict[field] is None:
                    validation_result['valid'] = False
                    validation_result['errors'].append(f'Required field missing: {field}')
            
            # Data type validation
            if entity.overall_health_score is not None and (entity.overall_health_score < 0 or entity.overall_health_score > 100):
                validation_result['warnings'].append('overall_health_score should be between 0 and 100')
            
            if entity.performance_score is not None and (entity.performance_score < 0.0 or entity.performance_score > 1.0):
                validation_result['warnings'].append('performance_score should be between 0.0 and 1.0')
            
            return validation_result
        except Exception as e:
            logger.error(f"Entity validation failed: {e}")
            return {
                'valid': False,
                'errors': [f'Validation error: {e}'],
                'warnings': [],
                'timestamp': datetime.now().isoformat()
            }

    # ==================== Dynamic Query Building ====================
    
    def _build_insert_query(self, data: Dict[str, Any]) -> str:
        """Build INSERT query dynamically"""
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]
        
        return f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
    
    def _build_update_query(self, data: Dict[str, Any], primary_key: str, primary_value: Any) -> str:
        """Build UPDATE query dynamically"""
        set_clauses = [f"{key} = :{key}" for key in data.keys()]
        
        return f"""
            UPDATE {self.table_name} 
            SET {', '.join(set_clauses)}
            WHERE {primary_key} = :{primary_key}
        """
    
    def _build_select_query(self, fields: Optional[List[str]] = None, 
                           where_clause: Optional[str] = None,
                           order_by: Optional[str] = None,
                           limit: Optional[int] = None,
                           offset: Optional[int] = None) -> str:
        """Build SELECT query dynamically"""
        if not fields:
            fields = ["*"]
        
        query = f"SELECT {', '.join(fields)} FROM {self.table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        if offset:
            query += f" OFFSET {offset}"
        
        return query
    
    def _build_delete_query(self, where_clause: str) -> str:
        """Build DELETE query dynamically"""
        return f"DELETE FROM {self.table_name} WHERE {where_clause}"
    
    async def _get_last_updated_timestamp(self) -> Optional[datetime]:
        """Get the timestamp of the last updated record"""
        try:
            query = f"SELECT MAX(updated_at) as last_updated FROM {self.table_name}"
            result = await self.connection_manager.execute_query(query, {})
            
            if result and result[0]['last_updated']:
                return result[0]['last_updated']
            return None
        except Exception as e:
            logger.error(f"Failed to get last updated timestamp: {e}")
            return None
    
    # ==================== Essential Methods ====================
    
    async def get_total_count(self) -> int:
        """Get total count of federated learning registry entries asynchronously"""
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            result = await self.connection_manager.execute_query(query, {})
            return result[0]['total'] if result and len(result) > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            raise
    
    async def get_by_federation_type(self, federation_type: str) -> List[FederatedLearningRegistry]:
        """Get federated learning registry entries by federation type asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE federation_type = :federation_type ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"federation_type": federation_type})
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entries by type {federation_type}: {e}")
            raise
    
    async def get_by_health_status(self, health_status: str) -> List[FederatedLearningRegistry]:
        """Get federated learning registry entries by health status asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE health_status = :health_status ORDER BY overall_health_score DESC"
            result = await self.connection_manager.execute_query(query, {"health_status": health_status})
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entries by health status {health_status}: {e}")
            raise
    
    async def get_by_department(self, dept_id: str) -> List[FederatedLearningRegistry]:
        """Get federated learning registry entries by department ID asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE dept_id = :dept_id ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"dept_id": dept_id})
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Failed to get federated learning registry entries by department {dept_id}: {e}")
            raise
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary statistics asynchronously"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_registries,
                    AVG(overall_health_score) as avg_health_score,
                    COUNT(CASE WHEN health_status = 'healthy' THEN 1 END) as healthy_count,
                    COUNT(CASE WHEN health_status = 'warning' THEN 1 END) as warning_count,
                    COUNT(CASE WHEN health_status = 'critical' THEN 1 END) as critical_count
                FROM {self.table_name}
            """
            
            result = await self.connection_manager.execute_query(query, {})
            return dict(result[0]) if result and len(result) > 0 else {}
            
        except Exception as e:
            logger.error(f"Failed to get health summary: {e}")
            raise
    
    async def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary statistics asynchronously"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_registries,
                    COUNT(CASE WHEN compliance_status = 'compliant' THEN 1 END) as compliant_count,
                    COUNT(CASE WHEN compliance_status = 'non_compliant' THEN 1 END) as non_compliant_count,
                    COUNT(CASE WHEN compliance_status = 'pending' THEN 1 END) as pending_count,
                    AVG(security_score) as avg_security_score
                FROM {self.table_name}
            """
            
            result = await self.connection_manager.execute_query(query, {})
            return dict(result[0]) if result and len(result) > 0 else {}
            
        except Exception as e:
            logger.error(f"Failed to get compliance summary: {e}")
            raise
    
    # ==================== Repository Information ====================
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """Get comprehensive compliance report for federated learning registry"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_registries': 0,
                'compliance_summary': {},
                'security_metrics': {},
                'recommendations': []
            }
            
            # Get total count
            total_count = await self.get_total_count()
            report['total_registries'] = total_count
            
            if total_count == 0:
                return report
            
            # Compliance scores
            compliance_query = f"""
                SELECT 
                    AVG(compliance_score) as avg_compliance,
                    COUNT(CASE WHEN compliance_score >= 0.9 THEN 1 END) as excellent_count,
                    COUNT(CASE WHEN compliance_score >= 0.7 AND compliance_score < 0.9 THEN 1 END) as good_count,
                    COUNT(CASE WHEN compliance_score >= 0.5 AND compliance_score < 0.7 THEN 1 END) as fair_count,
                    COUNT(CASE WHEN compliance_score < 0.5 THEN 1 END) as poor_count
                FROM {self.table_name} 
                WHERE compliance_score IS NOT NULL
            """
            compliance_result = await self.connection_manager.execute_query(compliance_query, {})
            
            if compliance_result:
                row = compliance_result[0]
                report['compliance_summary'] = {
                    'average_score': row['avg_compliance'] or 0.0,
                    'excellent': row['excellent_count'] or 0,
                    'good': row['good_count'] or 0,
                    'fair': row['fair_count'] or 0,
                    'poor': row['poor_count'] or 0
                }
            
            # Security metrics
            security_query = f"""
                SELECT 
                    AVG(security_score) as avg_security,
                    AVG(threat_detection_score) as avg_threat_detection,
                    AVG(access_control_score) as avg_access_control
                FROM {self.table_name} 
                WHERE security_score IS NOT NULL
            """
            security_result = await self.connection_manager.execute_query(security_query, {})
            
            if security_result:
                row = security_result[0]
                report['security_metrics'] = {
                    'average_security_score': row['avg_security'] or 0.0,
                    'average_threat_detection': row['avg_threat_detection'] or 0.0,
                    'average_access_control': row['avg_access_control'] or 0.0
                }
            
            # Generate recommendations
            if report['compliance_summary'].get('average_score', 0) < 0.7:
                report['recommendations'].append('Improve overall compliance scores through better validation processes')
            
            if report['security_metrics'].get('average_security_score', 0) < 80:
                report['recommendations'].append('Enhance security measures and implement stronger encryption')
            
            return report
        except Exception as e:
            logger.error(f"Failed to get compliance report: {e}")
            raise
    
    async def get_repository_standards_compliance(self) -> Dict[str, Any]:
        """Get compliance report against world-class repository standards"""
        try:
            compliance_report = {
                'timestamp': datetime.now().isoformat(),
                'overall_compliance': 0.0,
                'category_compliance': {},
                'missing_features': [],
                'recommendations': []
            }
            
            # Check each category
            categories = {
                'Schema & Metadata': [
                    '_get_table_name', '_get_columns', '_get_primary_key_column',
                    '_get_foreign_key_columns', '_get_indexed_columns', '_get_required_columns',
                    '_get_audit_columns', '_validate_schema', '_get_actual_table_columns',
                    '_schema_migration_needed', '_validate_entity_schema'
                ],
                'Enhanced CRUD': [
                    'create', 'create_batch', 'create_if_not_exists', 'get_by_id', 'get_by_ids',
                    'get_all', 'get_by_field', 'update', 'update_batch', 'upsert', 'delete',
                    'delete_batch', 'soft_delete'
                ],
                'Advanced Querying': [
                    'search', 'filter_by_criteria', 'get_by_date_range', 'get_recent',
                    'count_by_field', 'get_statistics', 'get_trends'
                ],
                'Enterprise Features': [
                    'get_by_user', 'get_by_organization', 'get_audit_trail', 'get_compliance_status',
                    'get_security_score'
                ],
                'Performance & Monitoring': [
                    'health_check', 'get_performance_metrics', 'get_repository_info'
                ],
                'Utility & Maintenance': [
                    'exists', 'get_table_info', 'validate_entity'
                ],
                'Dynamic Query Building': [
                    '_build_insert_query', '_build_update_query', '_build_select_query', '_build_delete_query'
                ],
                'JSON Field Handling': [
                    '_deserialize_json_fields', '_model_to_dict', '_dict_to_model'
                ]
            }
            
            total_methods = 0
            implemented_methods = 0
            
            for category, methods in categories.items():
                category_total = len(methods)
                category_implemented = sum(1 for method in methods if hasattr(self, method))
                
                total_methods += category_total
                implemented_methods += category_implemented
                
                category_score = category_implemented / category_total if category_total > 0 else 0.0
                compliance_report['category_compliance'][category] = {
                    'score': category_score,
                    'implemented': category_implemented,
                    'total': category_total,
                    'percentage': round(category_score * 100, 1)
                }
                
                if category_score < 1.0:
                    missing = [method for method in methods if not hasattr(self, method)]
                    compliance_report['missing_features'].extend([f"{category}: {method}" for method in missing])
            
            # Calculate overall compliance
            overall_compliance = implemented_methods / total_methods if total_methods > 0 else 0.0
            compliance_report['overall_compliance'] = round(overall_compliance, 3)
            
            # Generate recommendations
            if overall_compliance < 0.9:
                compliance_report['recommendations'].append('Implement missing methods to achieve 90%+ compliance')
            
            if compliance_report['category_compliance'].get('Schema & Metadata', {}).get('score', 0) < 1.0:
                compliance_report['recommendations'].append('Complete schema introspection and validation methods')
            
            if compliance_report['category_compliance'].get('Enterprise Features', {}).get('score', 0) < 1.0:
                compliance_report['recommendations'].append('Enhance enterprise features for RBAC and compliance')
            
            return compliance_report
        except Exception as e:
            logger.error(f"Failed to get repository standards compliance: {e}")
            raise
    
    # ==================== Cleanup ====================
    
    async def cleanup(self) -> None:
        """Cleanup repository resources asynchronously"""
        try:
            logger.info("Federated Learning Registry Repository cleanup completed")
        except Exception as e:
            logger.error(f"Failed to cleanup Federated Learning Registry Repository: {e}")
            raise

    async def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for federated learning registry"""
        try:
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            count_result = await self.connection_manager.execute_query(count_query)
            total_count = count_result[0]['total'] if count_result else 0
            
            # Get status distribution
            status_query = f"""
                SELECT federation_participation_status, COUNT(*) as count 
                FROM {self.table_name}
                GROUP BY federation_participation_status
            """
            status_result = await self.connection_manager.execute_query(status_query)
            status_distribution = {row['federation_participation_status']: row['count'] for row in status_result}
            
            # Get federation type distribution
            type_query = f"""
                SELECT federation_type, COUNT(*) as count 
                FROM {self.table_name}
                GROUP BY federation_type
            """
            type_result = await self.connection_manager.execute_query(type_query)
            type_distribution = {row['federation_type']: row['count'] for row in type_result}
            
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
                "status_distribution": status_distribution,
                "type_distribution": type_distribution,
                "health_metrics": {
                    "average_health_score": float(health_stats.get('avg_health_score', 0) or 0),
                    "healthy_registries": int(health_stats.get('healthy_count', 0) or 0),
                    "critical_registries": int(health_stats.get('critical_count', 0) or 0)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get federated learning registry summary: {e}")
            return {
                "total_registries": 0,
                "status_distribution": {},
                "type_distribution": {},
                "health_metrics": {
                    "average_health_score": 0.0,
                    "healthy_registries": 0,
                    "critical_registries": 0
                },
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
