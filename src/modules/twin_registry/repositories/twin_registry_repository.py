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
            ) VALUES (:registry_id, :twin_id, :twin_name, :registry_name, :twin_category, :twin_type,
                :twin_priority, :twin_version, :registry_type, :workflow_source, :aasx_integration_id,
                :physics_modeling_id, :federated_learning_id, :data_pipeline_id, :kg_neo4j_id,
                :certificate_manager_id, :integration_status, :overall_health_score, :health_status,
                :lifecycle_status, :lifecycle_phase, :operational_status, :availability_status,
                :sync_status, :sync_frequency, :last_sync_at, :next_sync_at, :sync_error_count,
                :sync_error_message, :performance_score, :data_quality_score, :reliability_score,
                :compliance_score, :security_level, :access_control_level, :encryption_enabled,
                :audit_logging_enabled, :user_id, :org_id, :dept_id, :owner_team, :steward_user_id,
                :created_at, :updated_at, :activated_at, :last_accessed_at, :last_modified_at,
                :registry_config, :registry_metadata, :custom_attributes, :tags, :relationships,
                :dependencies, :instances)
            """
            
            params = {
                'registry_id': registry.registry_id,
                'twin_id': registry.twin_id,
                'twin_name': registry.twin_name,
                'registry_name': registry.registry_name,
                'twin_category': registry.twin_category,
                'twin_type': registry.twin_type,
                'twin_priority': registry.twin_priority,
                'twin_version': registry.twin_version,
                'registry_type': registry.registry_type,
                'workflow_source': registry.workflow_source,
                'aasx_integration_id': registry.aasx_integration_id,
                'physics_modeling_id': registry.physics_modeling_id,
                'federated_learning_id': registry.federated_learning_id,
                'data_pipeline_id': registry.data_pipeline_id,
                'kg_neo4j_id': registry.kg_neo4j_id,
                'certificate_manager_id': registry.certificate_manager_id,
                'integration_status': registry.integration_status,
                'overall_health_score': registry.overall_health_score,
                'health_status': registry.health_status,
                'lifecycle_status': registry.lifecycle_status,
                'lifecycle_phase': registry.lifecycle_phase,
                'operational_status': registry.operational_status,
                'availability_status': registry.availability_status,
                'sync_status': registry.sync_status,
                'sync_frequency': registry.sync_frequency,
                'last_sync_at': registry.last_sync_at,
                'next_sync_at': registry.next_sync_at,
                'sync_error_count': registry.sync_error_count,
                'sync_error_message': registry.sync_error_message,
                'performance_score': registry.performance_score,
                'data_quality_score': registry.data_quality_score,
                'reliability_score': registry.reliability_score,
                'compliance_score': registry.compliance_score,
                'security_level': registry.security_level,
                'access_control_level': registry.access_control_level,
                'encryption_enabled': registry.encryption_enabled,
                'audit_logging_enabled': registry.audit_logging_enabled,
                'user_id': registry.user_id,
                'org_id': registry.org_id,
                'dept_id': registry.dept_id,
                'owner_team': registry.owner_team,
                'steward_user_id': registry.steward_user_id,
                'created_at': registry.created_at,
                'updated_at': registry.updated_at,
                'activated_at': registry.activated_at,
                'last_accessed_at': registry.last_accessed_at,
                'last_modified_at': registry.last_modified_at,
                'registry_config': registry.registry_config,
                'registry_metadata': registry.registry_metadata,
                'custom_attributes': registry.custom_attributes,
                'tags': registry.tags,
                'relationships': registry.relationships,
                'dependencies': registry.dependencies,
                'instances': registry.instances
            }
            
            await self.connection_manager.execute_update(sql, params)
            
            logger.info(f"Created twin registry entry for twin {registry.twin_id}")
            return registry
            
        except Exception as e:
            logger.error(f"Failed to create twin registry entry: {e}")
            raise
    
    async def get_by_id(self, registry_id: str) -> Optional[TwinRegistry]:
        """Get twin registry by ID."""
        try:
            sql = "SELECT * FROM twin_registry WHERE registry_id = :registry_id"
            
            result = await self.connection_manager.execute_query(sql, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                return self._row_to_registry(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get registry by ID {registry_id}: {e}")
            raise
    
    async def get_by_twin_id(self, twin_id: str) -> Optional[TwinRegistry]:
        """Get twin registry by twin ID."""
        try:
            sql = "SELECT * FROM twin_registry WHERE twin_id = :twin_id"
            
            result = await self.connection_manager.execute_query(sql, {"twin_id": twin_id})
            
            if result and len(result) > 0:
                return self._row_to_registry(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get registry by twin ID {twin_id}: {e}")
            raise
    
    async def get_all(self, query: Optional[TwinRegistryQuery] = None) -> List[TwinRegistry]:
        """Get all twin registries with optional filtering."""
        try:
            sql = "SELECT * FROM twin_registry"
            params = {}
            
            if query:
                conditions = []
                if query.twin_id:
                    conditions.append("twin_id = :twin_id")
                    params['twin_id'] = query.twin_id
                if query.twin_name:
                    conditions.append("twin_name LIKE :twin_name")
                    params['twin_name'] = f"%{query.twin_name}%"
                if query.registry_type:
                    conditions.append("registry_type = :registry_type")
                    params['registry_type'] = query.registry_type
                if query.workflow_source:
                    conditions.append("workflow_source = :workflow_source")
                    params['workflow_source'] = query.workflow_source
                if query.twin_category:
                    conditions.append("twin_category = :twin_category")
                    params['twin_category'] = query.twin_category
                if query.integration_status:
                    conditions.append("integration_status = :integration_status")
                    params['integration_status'] = query.integration_status
                if query.health_status:
                    conditions.append("health_status = :health_status")
                    params['health_status'] = query.health_status
                if query.lifecycle_status:
                    conditions.append("lifecycle_status = :lifecycle_status")
                    params['lifecycle_status'] = query.lifecycle_status
                if query.user_id:
                    conditions.append("user_id = :user_id")
                    params['user_id'] = query.user_id
                if query.org_id:
                    conditions.append("org_id = :org_id")
                    params['org_id'] = query.org_id
                if query.created_after:
                    conditions.append("created_at >= :created_after")
                    params['created_after'] = query.created_after.isoformat()
                if query.created_before:
                    conditions.append("created_at <= :created_before")
                    params['created_before'] = query.created_before.isoformat()
                
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)
            
            sql += " ORDER BY created_at DESC"
            
            result = await self.connection_manager.execute_query(sql, params)
            
            return [self._row_to_registry(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get registries: {e}")
            raise
    
    async def query_registries(self, query: TwinRegistryQuery) -> List[TwinRegistry]:
        """Query registries with filters - alias for get_all with query."""
        return await self.get_all(query)
    
    async def get_total_count(self) -> int:
        """Get total count of registries."""
        try:
            sql = "SELECT COUNT(*) as count FROM twin_registry"
            
            result = await self.connection_manager.execute_query(sql, {})
            
            return result[0]['count'] if result and len(result) > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            return 0
    
    async def get_count_by_type(self, registry_type: str) -> int:
        """Get count of registries by type."""
        try:
            sql = "SELECT COUNT(*) as count FROM twin_registry WHERE registry_type = :registry_type"
            
            result = await self.connection_manager.execute_query(sql, {"registry_type": registry_type})
            
            return result[0]['count'] if result and len(result) > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to get count by type: {e}")
            return 0
    
    async def get_count_by_status(self, status: str) -> int:
        """Get count of registries by integration status."""
        try:
            sql = "SELECT COUNT(*) as count FROM twin_registry WHERE integration_status = :status"
            
            result = await self.connection_manager.execute_query(sql, {"status": status})
            
            return result[0]['count'] if result and len(result) > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to get count by status: {e}")
            return 0
    
    async def update_registry(self, registry: TwinRegistry) -> TwinRegistry:
        """Update existing twin registry."""
        try:
            sql = """
            UPDATE twin_registry SET
                twin_name = :twin_name, registry_name = :registry_name, twin_category = :twin_category, twin_type = :twin_type,
                twin_priority = :twin_priority, twin_version = :twin_version, registry_type = :registry_type, workflow_source = :workflow_source,
                aasx_integration_id = :aasx_integration_id, physics_modeling_id = :physics_modeling_id, federated_learning_id = :federated_learning_id,
                data_pipeline_id = :data_pipeline_id, kg_neo4j_id = :kg_neo4j_id, certificate_manager_id = :certificate_manager_id,
                integration_status = :integration_status, overall_health_score = :overall_health_score, health_status = :health_status,
                lifecycle_status = :lifecycle_status, lifecycle_phase = :lifecycle_phase, operational_status = :operational_status,
                availability_status = :availability_status, sync_status = :sync_status, sync_frequency = :sync_frequency, last_sync_at = :last_sync_at,
                next_sync_at = :next_sync_at, sync_error_count = :sync_error_count, sync_error_message = :sync_error_message,
                performance_score = :performance_score, data_quality_score = :data_quality_score, reliability_score = :reliability_score,
                compliance_score = :compliance_score, security_level = :security_level, access_control_level = :access_control_level,
                encryption_enabled = :encryption_enabled, audit_logging_enabled = :audit_logging_enabled, owner_team = :owner_team,
                steward_user_id = :steward_user_id, updated_at = :updated_at, activated_at = :activated_at, last_accessed_at = :last_accessed_at,
                last_modified_at = :last_modified_at, registry_config = :registry_config, registry_metadata = :registry_metadata,
                custom_attributes = :custom_attributes, tags = :tags, relationships = :relationships, dependencies = :dependencies, instances = :instances
            WHERE registry_id = :registry_id
            """
            
            params = {
                'twin_name': registry.twin_name,
                'registry_name': registry.registry_name,
                'twin_category': registry.twin_category,
                'twin_type': registry.twin_type,
                'twin_priority': registry.twin_priority,
                'twin_version': registry.twin_version,
                'registry_type': registry.registry_type,
                'workflow_source': registry.workflow_source,
                'aasx_integration_id': registry.aasx_integration_id,
                'physics_modeling_id': registry.physics_modeling_id,
                'federated_learning_id': registry.federated_learning_id,
                'data_pipeline_id': registry.data_pipeline_id,
                'kg_neo4j_id': registry.kg_neo4j_id,
                'certificate_manager_id': registry.certificate_manager_id,
                'integration_status': registry.integration_status,
                'overall_health_score': registry.overall_health_score,
                'health_status': registry.health_status,
                'lifecycle_status': registry.lifecycle_status,
                'lifecycle_phase': registry.lifecycle_phase,
                'operational_status': registry.operational_status,
                'availability_status': registry.availability_status,
                'sync_status': registry.sync_status,
                'sync_frequency': registry.sync_frequency,
                'last_sync_at': registry.last_sync_at,
                'next_sync_at': registry.next_sync_at,
                'sync_error_count': registry.sync_error_count,
                'sync_error_message': registry.sync_error_message,
                'performance_score': registry.performance_score,
                'data_quality_score': registry.data_quality_score,
                'reliability_score': registry.reliability_score,
                'compliance_score': registry.compliance_score,
                'security_level': registry.security_level,
                'access_control_level': registry.access_control_level,
                'encryption_enabled': registry.encryption_enabled,
                'audit_logging_enabled': registry.audit_logging_enabled,
                'owner_team': registry.owner_team,
                'steward_user_id': registry.steward_user_id,
                'updated_at': registry.updated_at,
                'activated_at': registry.activated_at,
                'last_accessed_at': registry.last_accessed_at,
                'last_modified_at': registry.last_modified_at,
                'registry_config': registry.registry_config,
                'registry_metadata': registry.registry_metadata,
                'custom_attributes': registry.custom_attributes,
                'tags': registry.tags,
                'relationships': registry.relationships,
                'dependencies': registry.dependencies,
                'instances': registry.instances,
                'registry_id': registry.registry_id
            }
            
            await self.connection_manager.execute_update(sql, params)
            
            logger.info(f"Updated twin registry: {registry.registry_id}")
            return registry
            
        except Exception as e:
            logger.error(f"Failed to update twin registry: {e}")
            raise
    
    async def delete_registry(self, registry_id: str) -> bool:
        """Delete twin registry by ID."""
        try:
            sql = "DELETE FROM twin_registry WHERE registry_id = :registry_id"
            
            await self.connection_manager.execute_update(sql, {"registry_id": registry_id})
            
            logger.info(f"Deleted twin registry: {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete twin registry {registry_id}: {e}")
            raise
    
    async def get_summary(self) -> TwinRegistrySummary:
        """Get registry summary statistics."""
        try:
            # Total registries
            total_result = await self.connection_manager.execute_query("SELECT COUNT(*) as count FROM twin_registry", {})
            total = total_result[0]['count'] if total_result and len(total_result) > 0 else 0
            
            # Active registries (integration_status = 'active')
            active_result = await self.connection_manager.execute_query("SELECT COUNT(*) as count FROM twin_registry WHERE integration_status = 'active'", {})
            active = active_result[0]['count'] if active_result and len(active_result) > 0 else 0
            
            # By type
            by_type_result = await self.connection_manager.execute_query("SELECT registry_type, COUNT(*) as count FROM twin_registry GROUP BY registry_type", {})
            by_type = {row['registry_type']: row['count'] for row in by_type_result}
            
            # By workflow
            by_workflow_result = await self.connection_manager.execute_query("SELECT workflow_source, COUNT(*) as count FROM twin_registry GROUP BY workflow_source", {})
            by_workflow = {row['workflow_source']: row['count'] for row in by_workflow_result}
            
            # By category
            by_category_result = await self.connection_manager.execute_query("SELECT twin_category, COUNT(*) as count FROM twin_registry GROUP BY twin_category", {})
            by_category = {row['twin_category']: row['count'] for row in by_category_result}
            
            # By status
            by_status_result = await self.connection_manager.execute_query("SELECT integration_status, COUNT(*) as count FROM twin_registry GROUP BY integration_status", {})
            by_status = {row['integration_status']: row['count'] for row in by_status_result}
            
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