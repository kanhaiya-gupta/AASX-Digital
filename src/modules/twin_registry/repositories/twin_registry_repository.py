"""
Twin Registry Repository

Updated to use our new comprehensive database schema.
Handles twin registry operations with the new twin_registry table.
Phase 2: Service Layer Modernization with pure async support.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.engine.database.connection_manager import ConnectionManager
from ..models.twin_registry import (
    TwinRegistry,
    TwinRegistryQuery,
    TwinRegistrySummary
)

logger = logging.getLogger(__name__)


class TwinRegistryRepository:
    """Repository for managing twin registry data with new comprehensive schema."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the twin registry repository with engine connection manager."""
        self.connection_manager = connection_manager
        logger.info("Twin Registry Repository initialized with new schema and engine")
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return "twin_registry"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for this table."""
        return [
            "registry_id", "twin_id", "twin_name", "registry_name", "twin_category", "twin_type",
            "twin_priority", "twin_version", "registry_type", "workflow_source", "aasx_integration_id",
            "physics_modeling_id", "federated_learning_id", "data_pipeline_id", "kg_neo4j_id",
            "certificate_manager_id", "integration_status", "overall_health_score", "health_status",
            "lifecycle_status", "lifecycle_phase", "operational_status", "availability_status",
            "sync_status", "sync_frequency", "last_sync_at", "next_sync_at", "sync_error_count",
            "sync_error_message", "performance_score", "data_quality_score", "reliability_score",
            "compliance_score", "security_level", "access_control_level", "encryption_enabled",
            "audit_logging_enabled", "user_id", "org_id", "dept_id", "owner_team", "steward_user_id",
            "created_at", "updated_at", "activated_at", "last_accessed_at", "last_modified_at",
            "registry_config", "registry_metadata", "custom_attributes", "tags", "relationships",
            "dependencies", "instances"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for twin registry table."""
        return "registry_id"
    
    async def initialize(self) -> None:
        """Initialize the repository - tables already exist from Phase 1."""
        try:
            # Tables are already created by our migration script
            logger.info("Twin Registry Repository ready - tables already exist")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Registry Repository: {e}")
            raise
    
    async def create_registry(self, registry: TwinRegistry) -> TwinRegistry:
        """Create new twin registry entry."""
        try:
            sql = """
            INSERT INTO twin_registry (
                registry_id, twin_id, twin_name, registry_name, twin_category, twin_type,
                twin_priority, twin_version, registry_type, workflow_source, aasx_integration_id,
                physics_modeling_id, federated_learning_id, data_pipeline_id, kg_neo4j_id,
                certificate_manager_id, integration_status, overall_health_score, health_status,
                lifecycle_status, lifecycle_phase, operational_status, availability_status,
                sync_status, sync_frequency, last_sync_at, next_sync_at, sync_error_count,
                sync_error_message, performance_score, data_quality_score, reliability_score,
                compliance_score, security_level, access_control_level, encryption_enabled,
                audit_logging_enabled, user_id, org_id, dept_id, owner_team, steward_user_id,
                created_at, updated_at, activated_at, last_accessed_at, last_modified_at,
                registry_config, registry_metadata, custom_attributes, tags, relationships,
                dependencies, instances
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                registry.registry_id,
                registry.twin_id,
                registry.twin_name,
                registry.registry_name,
                registry.twin_category,
                registry.twin_type,
                registry.twin_priority,
                registry.twin_version,
                registry.registry_type,
                registry.workflow_source,
                registry.aasx_integration_id,
                registry.physics_modeling_id,
                registry.federated_learning_id,
                registry.data_pipeline_id,
                registry.kg_neo4j_id,
                registry.certificate_manager_id,
                registry.integration_status,
                registry.overall_health_score,
                registry.health_status,
                registry.lifecycle_status,
                registry.lifecycle_phase,
                registry.operational_status,
                registry.availability_status,
                registry.sync_status,
                registry.sync_frequency,
                registry.last_sync_at,
                registry.next_sync_at,
                registry.sync_error_count,
                registry.sync_error_message,
                registry.performance_score,
                registry.data_quality_score,
                registry.reliability_score,
                registry.compliance_score,
                registry.security_level,
                registry.access_control_level,
                registry.encryption_enabled,
                registry.audit_logging_enabled,
                registry.user_id,
                registry.org_id,
                registry.dept_id,  # Added dept_id
                registry.owner_team,
                registry.steward_user_id,
                registry.created_at,
                registry.updated_at,
                registry.activated_at,
                registry.last_accessed_at,
                registry.last_modified_at,
                registry.registry_config,
                registry.registry_metadata,
                registry.custom_attributes,
                registry.tags,
                registry.relationships,
                registry.dependencies,
                registry.instances
            )
            
            async with self.connection_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Created twin registry entry for twin {registry.twin_id}")
            return registry
            
        except Exception as e:
            logger.error(f"Failed to create twin registry entry: {e}")
            raise
    
    async def get_by_id(self, registry_id: str) -> Optional[TwinRegistry]:
        """Get twin registry by ID."""
        try:
            sql = "SELECT * FROM twin_registry WHERE registry_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(sql, (registry_id,))
                row = await cursor.fetchone()
            
            if row:
                return self._row_to_registry(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get registry by ID {registry_id}: {e}")
            raise
    
    async def get_by_twin_id(self, twin_id: str) -> Optional[TwinRegistry]:
        """Get twin registry by twin ID."""
        try:
            sql = "SELECT * FROM twin_registry WHERE twin_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(sql, (twin_id,))
                row = await cursor.fetchone()
            
            if row:
                return self._row_to_registry(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get registry by twin ID {twin_id}: {e}")
            raise
    
    async def get_all(self, query: Optional[TwinRegistryQuery] = None) -> List[TwinRegistry]:
        """Get all twin registries with optional filtering."""
        try:
            sql = "SELECT * FROM twin_registry"
            params = []
            
            if query:
                conditions = []
                if query.twin_id:
                    conditions.append("twin_id = ?")
                    params.append(query.twin_id)
                if query.twin_name:
                    conditions.append("twin_name LIKE ?")
                    params.append(f"%{query.twin_name}%")
                if query.registry_type:
                    conditions.append("registry_type = ?")
                    params.append(query.registry_type)
                if query.workflow_source:
                    conditions.append("workflow_source = ?")
                    params.append(query.workflow_source)
                if query.twin_category:
                    conditions.append("twin_category = ?")
                    params.append(query.twin_category)
                if query.integration_status:
                    conditions.append("integration_status = ?")
                    params.append(query.integration_status)
                if query.health_status:
                    conditions.append("health_status = ?")
                    params.append(query.health_status)
                if query.lifecycle_status:
                    conditions.append("lifecycle_status = ?")
                    params.append(query.lifecycle_status)
                if query.user_id:
                    conditions.append("user_id = ?")
                    params.append(query.user_id)
                if query.org_id:
                    conditions.append("org_id = ?")
                    params.append(query.org_id)
                if query.created_after:
                    conditions.append("created_at >= ?")
                    params.append(query.created_after.isoformat())
                if query.created_before:
                    conditions.append("created_at <= ?")
                    params.append(query.created_before.isoformat())
                
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)
            
            sql += " ORDER BY created_at DESC"
            
            # Use the database manager's connection method
            conn = self.connection_manager.get_connection()
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._row_to_registry(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get registries: {e}")
            raise
    
    async def query_registries(self, query: TwinRegistryQuery) -> List[TwinRegistry]:
        """Query registries with filters - alias for get_all with query."""
        return await self.get_all(query)
    
    async def get_total_count(self) -> int:
        """Get total count of registries."""
        try:
            sql = "SELECT COUNT(*) FROM twin_registry"
            
            conn = self.connection_manager.get_connection()
            cursor = conn.execute(sql)
            result = cursor.fetchone()
            
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            return 0
    
    async def get_count_by_type(self, registry_type: str) -> int:
        """Get count of registries by type."""
        try:
            sql = "SELECT COUNT(*) FROM twin_registry WHERE registry_type = ?"
            
            conn = self.connection_manager.get_connection()
            cursor = conn.execute(sql, (registry_type,))
            result = cursor.fetchone()
            
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get count by type {registry_type}: {e}")
            return 0
    
    async def get_count_by_status(self, status: str) -> int:
        """Get count of registries by integration status."""
        try:
            sql = "SELECT COUNT(*) FROM twin_registry WHERE integration_status = ?"
            
            conn = self.connection_manager.get_connection()
            cursor = conn.execute(sql, (status,))
            result = cursor.fetchone()
            
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get count by status {status}: {e}")
            return 0
    
    async def update_registry(self, registry: TwinRegistry) -> TwinRegistry:
        """Update existing twin registry."""
        try:
            sql = """
            UPDATE twin_registry SET
                twin_name = ?, registry_name = ?, twin_category = ?, twin_type = ?,
                twin_priority = ?, twin_version = ?, registry_type = ?, workflow_source = ?,
                aasx_integration_id = ?, physics_modeling_id = ?, federated_learning_id = ?,
                data_pipeline_id = ?, kg_neo4j_id = ?, certificate_manager_id = ?,
                integration_status = ?, overall_health_score = ?, health_status = ?,
                lifecycle_status = ?, lifecycle_phase = ?, operational_status = ?,
                availability_status = ?, sync_status = ?, sync_frequency = ?, last_sync_at = ?,
                next_sync_at = ?, sync_error_count = ?, sync_error_message = ?,
                performance_score = ?, data_quality_score = ?, reliability_score = ?,
                compliance_score = ?, security_level = ?, access_control_level = ?,
                encryption_enabled = ?, audit_logging_enabled = ?, owner_team = ?,
                steward_user_id = ?, updated_at = ?, activated_at = ?, last_accessed_at = ?,
                last_modified_at = ?, registry_config = ?, registry_metadata = ?,
                custom_attributes = ?, tags = ?, relationships = ?, dependencies = ?, instances = ?
            WHERE registry_id = ?
            """
            
            params = (
                registry.twin_name,
                registry.registry_name,
                registry.twin_category,
                registry.twin_type,
                registry.twin_priority,
                registry.twin_version,
                registry.registry_type,
                registry.workflow_source,
                registry.aasx_integration_id,
                registry.physics_modeling_id,
                registry.federated_learning_id,
                registry.data_pipeline_id,
                registry.kg_neo4j_id,
                registry.certificate_manager_id,
                registry.integration_status,
                registry.overall_health_score,
                registry.health_status,
                registry.lifecycle_status,
                registry.lifecycle_phase,
                registry.operational_status,
                registry.availability_status,
                registry.sync_status,
                registry.sync_frequency,
                registry.last_sync_at,
                registry.next_sync_at,
                registry.sync_error_count,
                registry.sync_error_message,
                registry.performance_score,
                registry.data_quality_score,
                registry.reliability_score,
                registry.compliance_score,
                registry.security_level,
                registry.access_control_level,
                registry.encryption_enabled,
                registry.audit_logging_enabled,
                registry.owner_team,
                registry.steward_user_id,
                registry.updated_at,
                registry.activated_at,
                registry.last_accessed_at,
                registry.last_modified_at,
                registry.registry_config,
                registry.registry_metadata,
                registry.custom_attributes,
                registry.tags,
                registry.relationships,
                registry.dependencies,
                registry.instances,
                registry.registry_id
            )
            
            async with self.connection_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Updated twin registry: {registry.registry_id}")
            return registry
            
        except Exception as e:
            logger.error(f"Failed to update twin registry: {e}")
            raise
    
    async def delete_registry(self, registry_id: str) -> bool:
        """Delete twin registry by ID."""
        try:
            sql = "DELETE FROM twin_registry WHERE registry_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(sql, (registry_id,))
                await conn.commit()
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted twin registry: {registry_id}")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete twin registry {registry_id}: {e}")
            raise
    
    async def get_summary(self) -> TwinRegistrySummary:
        """Get registry summary statistics."""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Total registries
                cursor = await conn.execute("SELECT COUNT(*) FROM twin_registry")
                total = (await cursor.fetchone())[0]
                
                # Active registries (integration_status = 'active')
                cursor = await conn.execute("SELECT COUNT(*) FROM twin_registry WHERE integration_status = 'active'")
                active = (await cursor.fetchone())[0]
                
                # By type
                cursor = await conn.execute("SELECT registry_type, COUNT(*) FROM twin_registry GROUP BY registry_type")
                by_type = {row[0]: row[1] for row in await cursor.fetchall()}
                
                # By workflow
                cursor = await conn.execute("SELECT workflow_source, COUNT(*) FROM twin_registry GROUP BY workflow_source")
                by_workflow = {row[0]: row[1] for row in await cursor.fetchall()}
                
                # By category
                cursor = await conn.execute("SELECT twin_category, COUNT(*) FROM twin_registry GROUP BY twin_category")
                by_category = {row[0]: row[1] for row in await cursor.fetchall()}
                
                # By status
                cursor = await conn.execute("SELECT integration_status, COUNT(*) FROM twin_registry GROUP BY integration_status")
                by_status = {row[0]: row[1] for row in await cursor.fetchall()}
            
            return TwinRegistrySummary(
                total_registries=total,
                active_registries=active,
                registries_by_type=by_type,
                registries_by_workflow=by_workflow,
                registries_by_category=by_category,
                registries_by_status=by_status
            )
            
        except Exception as e:
            logger.error(f"Failed to get registry summary: {e}")
            raise
    
    def _row_to_registry(self, row) -> TwinRegistry:
        """Convert database row to TwinRegistry model."""
        try:
            # Handle different row types
            if hasattr(row, 'keys') and hasattr(row, '__getitem__'):
                # Row is a dictionary-like object (sqlite3.Row or dict)
                def safe_get(key, default=None):
                    try:
                        return row[key] if key in row else default
                    except (KeyError, IndexError):
                        return default
            else:
                # Row is a tuple, convert to dictionary using column names
                columns = self._get_columns()
                row_dict = dict(zip(columns, row))
                def safe_get(key, default=None):
                    return row_dict.get(key, default)
            
            return TwinRegistry(
                registry_id=safe_get('registry_id'),
                twin_id=safe_get('twin_id'),
                twin_name=safe_get('twin_name'),
                registry_name=safe_get('registry_name'),
                twin_category=safe_get('twin_category') or 'generic',
                twin_type=safe_get('twin_type') or 'physical',
                twin_priority=safe_get('twin_priority') or 'normal',
                twin_version=safe_get('twin_version') or '1.0.0',
                registry_type=safe_get('registry_type') or 'extraction',
                workflow_source=safe_get('workflow_source') or 'aasx_file',
                aasx_integration_id=safe_get('aasx_integration_id'),
                physics_modeling_id=safe_get('physics_modeling_id'),
                federated_learning_id=safe_get('federated_learning_id'),
                data_pipeline_id=safe_get('data_pipeline_id'),
                kg_neo4j_id=safe_get('kg_neo4j_id'),
                certificate_manager_id=safe_get('certificate_manager_id'),
                integration_status=safe_get('integration_status') or 'pending',
                overall_health_score=safe_get('overall_health_score') or 0,
                health_status=safe_get('health_status') or 'unknown',
                lifecycle_status=safe_get('lifecycle_status') or 'created',
                lifecycle_phase=safe_get('lifecycle_phase') or 'development',
                operational_status=safe_get('operational_status') or 'stopped',
                availability_status=safe_get('availability_status') or 'offline',
                sync_status=safe_get('sync_status') or 'pending',
                sync_frequency=safe_get('sync_frequency') or 'daily',
                last_sync_at=self._parse_datetime(safe_get('last_sync_at')),
                next_sync_at=self._parse_datetime(safe_get('next_sync_at')),
                sync_error_count=safe_get('sync_error_count') or 0,
                sync_error_message=safe_get('sync_error_message'),
                performance_score=safe_get('performance_score') or 0.0,
                data_quality_score=safe_get('data_quality_score') or 0.0,
                reliability_score=safe_get('reliability_score') or 0.0,
                compliance_score=safe_get('compliance_score') or 0.0,
                security_level=safe_get('security_level') or 'standard',
                access_control_level=safe_get('access_control_level') or 'user',
                encryption_enabled=bool(safe_get('encryption_enabled')),
                audit_logging_enabled=bool(safe_get('audit_logging_enabled')),
                user_id=safe_get('user_id'),
                org_id=safe_get('org_id'),
                dept_id=safe_get('dept_id'),
                owner_team=safe_get('owner_team'),
                steward_user_id=safe_get('steward_user_id'),
                created_at=self._parse_datetime(safe_get('created_at')) or datetime.now(),
                updated_at=self._parse_datetime(safe_get('updated_at')) or datetime.now(),
                activated_at=self._parse_datetime(safe_get('activated_at')),
                last_accessed_at=self._parse_datetime(safe_get('last_accessed_at')),
                last_modified_at=self._parse_datetime(safe_get('last_modified_at')),
                registry_config=self._deserialize_json(safe_get('registry_config')),
                registry_metadata=self._deserialize_json(safe_get('registry_metadata')),
                custom_attributes=self._deserialize_json(safe_get('custom_attributes')),
                tags=self._deserialize_json(safe_get('tags')) or [],
                relationships=self._deserialize_json(safe_get('relationships')) or [],
                dependencies=self._deserialize_json(safe_get('dependencies')) or [],
                instances=self._deserialize_json(safe_get('instances')) or []
            )
        except Exception as e:
            logger.error(f"Failed to convert row to TwinRegistry: {e}")
            raise
    
    def _parse_datetime(self, value) -> Optional[datetime]:
        """Parse datetime from string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except:
            return None
    
    def _serialize_json(self, data) -> str:
        """Serialize data to JSON string."""
        if data is None:
            return "{}"
        try:
            import json
            return json.dumps(data)
        except:
            return "{}"
    
    def _deserialize_json(self, data) -> Any:
        """Deserialize JSON string to data."""
        if not data:
            return {}
        try:
            import json
            return json.loads(data)
        except:
            return {} 