"""
Knowledge Graph Registry Repository

Updated to use our new comprehensive database schema with async support.
Handles knowledge graph registry operations with the new kg_graph_registry table.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from src.engine.database.connection_manager import ConnectionManager
from ..models.kg_graph_registry import (
    KGGraphRegistry,
    KGGraphRegistryQuery,
    KGGraphRegistrySummary
)

logger = logging.getLogger(__name__)


class KGGraphRegistryRepository:
    """Repository for managing knowledge graph registry data with new comprehensive schema."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the knowledge graph registry repository."""
        self.connection_manager = connection_manager
        self.table_name = "kg_graph_registry"
        logger.info("Knowledge Graph Registry Repository initialized with async support")
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return "kg_graph_registry"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for this table."""
        return [
            "graph_id", "file_id", "graph_name", "registry_name", "graph_category", "graph_type",
            "graph_priority", "graph_version", "registry_type", "workflow_source", "aasx_integration_id",
            "twin_registry_id", "physics_modeling_id", "federated_learning_id", "certificate_manager_id",
            "integration_status", "overall_health_score", "health_status", "lifecycle_status", "lifecycle_phase",
            "operational_status", "availability_status", "neo4j_import_status", "neo4j_export_status",
            "last_neo4j_sync_at", "next_neo4j_sync_at", "neo4j_sync_error_count", "neo4j_sync_error_message",
            "total_nodes", "total_relationships", "graph_complexity", "performance_score", "data_quality_score",
            "reliability_score", "compliance_score", "security_level", "access_control_level", "encryption_enabled",
            "audit_logging_enabled", "user_id", "org_id", "owner_team", "steward_user_id", "created_at",
            "updated_at", "activated_at", "last_accessed_at", "last_modified_at", "registry_config",
            "registry_metadata", "custom_attributes", "tags", "relationships", "dependencies", "graph_instances"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for knowledge graph registry table."""
        return "graph_id"
    
    def _deserialize_json_fields(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize JSON fields from database row."""
        import json
        
        # Fields that are stored as JSON strings
        json_fields = [
            'registry_config', 'registry_metadata', 'custom_attributes', 
            'tags', 'relationships', 'dependencies', 'graph_instances'
        ]
        
        deserialized_row = dict(row)
        for field in json_fields:
            if field in deserialized_row and deserialized_row[field]:
                try:
                    if isinstance(deserialized_row[field], str):
                        deserialized_row[field] = json.loads(deserialized_row[field])
                except (json.JSONDecodeError, TypeError):
                    # If deserialization fails, keep the original value
                    logger.warning(f"Failed to deserialize JSON field {field}: {deserialized_row[field]}")
        
        return deserialized_row
    
    async def initialize(self) -> None:
        """Initialize the repository - tables already exist from Phase 1."""
        try:
            # Tables are already created by our migration script
            logger.info("Knowledge Graph Registry Repository ready - tables already exist")
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Graph Registry Repository: {e}")
            raise
    
    async def create_registry(self, registry: KGGraphRegistry) -> KGGraphRegistry:
        """Create new knowledge graph registry entry."""
        try:
            # Count the columns in the SQL statement
            columns_list = [
                "graph_id", "file_id", "graph_name", "registry_name", "graph_category", "graph_type",
                "graph_priority", "graph_version", "registry_type", "workflow_source", "aasx_integration_id",
                "twin_registry_id", "physics_modeling_id", "federated_learning_id", "certificate_manager_id",
                "integration_status", "overall_health_score", "health_status", "lifecycle_status", "lifecycle_phase",
                "operational_status", "availability_status", "neo4j_import_status", "neo4j_export_status",
                "last_neo4j_sync_at", "next_neo4j_sync_at", "neo4j_sync_error_count", "neo4j_sync_error_message",
                "total_nodes", "total_relationships", "graph_complexity", "performance_score", "data_quality_score",
                "reliability_score", "compliance_score", "security_level", "access_control_level", "encryption_enabled",
                "audit_logging_enabled", "user_id", "org_id", "owner_team", "steward_user_id", "created_at",
                "updated_at", "activated_at", "last_accessed_at", "last_modified_at", "registry_config",
                "registry_metadata", "custom_attributes", "tags", "relationships", "dependencies", "graph_instances"
            ]
            
            # Debug: Print column count
            logger.info(f"🔍 DEBUG: SQL columns count: {len(columns_list)}")
            
            sql = f"""
            INSERT INTO kg_graph_registry (
                {', '.join(columns_list)}
            ) VALUES ({', '.join([f':{col}' for col in columns_list])})
            """
            
            # Convert dictionary/list fields to JSON strings for SQLite compatibility
            registry_config_json = json.dumps(registry.registry_config) if registry.registry_config else '{}'
            registry_metadata_json = json.dumps(registry.registry_metadata) if registry.registry_metadata else '{}'
            custom_attributes_json = json.dumps(registry.custom_attributes) if registry.custom_attributes else '{}'
            tags_json = json.dumps(registry.tags) if registry.tags else '[]'
            relationships_json = json.dumps(registry.relationships) if registry.relationships else '[]'
            dependencies_json = json.dumps(registry.dependencies) if registry.dependencies else '[]'
            graph_instances_json = json.dumps(registry.graph_instances) if registry.graph_instances else '[]'
            
            params = {
                "graph_id": registry.graph_id,
                "file_id": registry.file_id,
                "graph_name": registry.graph_name,
                "registry_name": registry.registry_name,
                "graph_category": registry.graph_category,
                "graph_type": registry.graph_type,
                "graph_priority": registry.graph_priority,
                "graph_version": registry.graph_version,
                "registry_type": registry.registry_type,
                "workflow_source": registry.workflow_source,
                "aasx_integration_id": registry.aasx_integration_id,
                "twin_registry_id": registry.twin_registry_id,
                "physics_modeling_id": registry.physics_modeling_id,
                "federated_learning_id": registry.federated_learning_id,
                "certificate_manager_id": registry.certificate_manager_id,
                "integration_status": registry.integration_status,
                "overall_health_score": registry.overall_health_score,
                "health_status": registry.health_status,
                "lifecycle_status": registry.lifecycle_status,
                "lifecycle_phase": registry.lifecycle_phase,
                "operational_status": registry.operational_status,
                "availability_status": registry.availability_status,
                "neo4j_import_status": registry.neo4j_import_status,
                "neo4j_export_status": registry.neo4j_export_status,
                "last_neo4j_sync_at": registry.last_neo4j_sync_at,
                "next_neo4j_sync_at": registry.next_neo4j_sync_at,
                "neo4j_sync_error_count": registry.neo4j_sync_error_count,
                "neo4j_sync_error_message": registry.neo4j_sync_error_message,
                "total_nodes": registry.total_nodes,
                "total_relationships": registry.total_relationships,
                "graph_complexity": registry.graph_complexity,
                "performance_score": registry.performance_score,
                "data_quality_score": registry.data_quality_score,
                "reliability_score": registry.reliability_score,
                "compliance_score": registry.compliance_score,
                "security_level": registry.security_level,
                "access_control_level": registry.access_control_level,
                "encryption_enabled": registry.encryption_enabled,
                "audit_logging_enabled": registry.audit_logging_enabled,
                "user_id": registry.user_id,
                "org_id": registry.org_id,
                "owner_team": registry.owner_team,
                "steward_user_id": registry.steward_user_id,
                "created_at": registry.created_at,
                "updated_at": registry.updated_at,
                "activated_at": registry.activated_at,
                "last_accessed_at": registry.last_accessed_at,
                "last_modified_at": registry.last_modified_at,
                "registry_config": registry_config_json,
                "registry_metadata": registry_metadata_json,
                "custom_attributes": custom_attributes_json,
                "tags": tags_json,
                "relationships": relationships_json,
                "dependencies": dependencies_json,
                "graph_instances": graph_instances_json
            }
            
            # Debug: Print params count
            logger.info(f"🔍 DEBUG: Params count: {len(params)}")
            
            await self.connection_manager.execute_update(sql, params)
            
            logger.info(f"✅ Created knowledge graph registry entry: {registry.graph_id}")
            return registry
            
        except Exception as e:
            logger.error(f"❌ Failed to create knowledge graph registry: {e}")
            raise
    
    async def get_by_file_id(self, file_id: str) -> Optional[KGGraphRegistry]:
        """Get knowledge graph registry by file ID."""
        try:
            sql = "SELECT * FROM kg_graph_registry WHERE file_id = :file_id"
            result = await self.connection_manager.execute_query(sql, {"file_id": file_id})
            
            if result and len(result) > 0:
                # Deserialize JSON fields before creating the model
                row = self._deserialize_json_fields(result[0])
                return KGGraphRegistry(**row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting registry by file_id {file_id}: {e}")
            return None
    
    async def get_by_graph_id(self, graph_id: str) -> Optional[KGGraphRegistry]:
        """Get knowledge graph registry by graph ID."""
        try:
            sql = "SELECT * FROM kg_graph_registry WHERE graph_id = :graph_id"
            result = await self.connection_manager.execute_query(sql, {"graph_id": graph_id})
            
            if result and len(result) > 0:
                # Deserialize JSON fields before creating the model
                row = self._deserialize_json_fields(result[0])
                return KGGraphRegistry(**row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting registry by graph_id {graph_id}: {e}")
            return None
    
    async def get_by_user_id(self, user_id: str, org_id: Optional[str] = None) -> List[KGGraphRegistry]:
        """Get knowledge graph registries by user ID."""
        try:
            if org_id:
                return await self.get_by_user(user_id, org_id)
            else:
                query = f"SELECT * FROM {self.table_name} WHERE user_id = :user_id ORDER BY created_at DESC"
                result = await self.connection_manager.execute_query(query, {"user_id": user_id})
                
                registries = []
                for row in result:
                    registries.append(KGGraphRegistry(**row))
                
                return registries
                
        except Exception as e:
            logger.error(f"Error getting registries by user_id {user_id}: {e}")
            return []
    
    async def get_by_workflow_source(self, workflow_source: str) -> List[KGGraphRegistry]:
        """Get knowledge graph registries by workflow source."""
        try:
            sql = "SELECT * FROM kg_graph_registry WHERE workflow_source = :workflow_source ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(sql, {"workflow_source": workflow_source})
            
            registries = []
            for row in result:
                # Deserialize JSON fields before creating the model
                row = self._deserialize_json_fields(row)
                registries.append(KGGraphRegistry(**row))
            
            return registries
            
        except Exception as e:
            logger.error(f"Error getting registries by workflow_source {workflow_source}: {e}")
            return []
    
    async def get_by_integration_status(self, status: str) -> List[KGGraphRegistry]:
        """Get knowledge graph registries by integration status."""
        try:
            sql = "SELECT * FROM kg_graph_registry WHERE integration_status = :status ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(sql, {"status": status})
            
            registries = []
            for row in result:
                # Deserialize JSON fields before creating the model
                row = self._deserialize_json_fields(row)
                registries.append(KGGraphRegistry(**row))
            
            return registries
            
        except Exception as e:
            logger.error(f"Error getting registries by integration_status {status}: {e}")
            return []
    
    async def update_neo4j_status(self, graph_id: str, import_status: str, export_status: str = None) -> bool:
        """Update Neo4j synchronization status."""
        try:
            if export_status:
                query = f"""
                    UPDATE {self.table_name} 
                    SET neo4j_import_status = :import_status, neo4j_export_status = :export_status, updated_at = :updated_at
                    WHERE graph_id = :graph_id
                """
                params = {
                    "import_status": import_status, 
                    "export_status": export_status, 
                    "updated_at": datetime.now(timezone.utc).isoformat(), 
                    "graph_id": graph_id
                }
            else:
                query = f"""
                    UPDATE {self.table_name} 
                    SET neo4j_import_status = :import_status, updated_at = :updated_at
                    WHERE graph_id = :graph_id
                """
                params = {
                    "import_status": import_status, 
                    "updated_at": datetime.now(timezone.utc).isoformat(), 
                    "graph_id": graph_id
                }
            
            await self.connection_manager.execute_update(query, params)
            logger.info(f"Updated Neo4j status for graph {graph_id}: {import_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Neo4j status for graph {graph_id}: {e}")
            return False
    
    async def update_graph_metrics(self, graph_id: str, nodes: int, relationships: int) -> bool:
        """Update graph data metrics."""
        try:
            sql = """
            UPDATE kg_graph_registry 
            SET total_nodes = :nodes, total_relationships = :relationships, updated_at = :updated_at
            WHERE graph_id = :graph_id
            """
            params = {
                "nodes": nodes, 
                "relationships": relationships, 
                "updated_at": datetime.now().isoformat(), 
                "graph_id": graph_id
            }
            
            await self.connection_manager.execute_update(sql, params)
            logger.info(f"✅ Updated graph metrics for graph {graph_id}: {nodes} nodes, {relationships} relationships")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update graph metrics for graph {graph_id}: {e}")
            return False
    
    async def update_health_score(self, graph_id: str, health_score: int) -> bool:
        """Update overall health score."""
        try:
            sql = """
            UPDATE kg_graph_registry 
            SET overall_health_score = :health_score, updated_at = :updated_at
            WHERE graph_id = :graph_id
            """
            params = {
                "health_score": health_score, 
                "updated_at": datetime.now().isoformat(), 
                "graph_id": graph_id
            }
            
            await self.connection_manager.execute_update(sql, params)
            logger.info(f"✅ Updated health score for graph {graph_id}: {health_score}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update health score for graph {graph_id}: {e}")
            return False
    
    async def get_summary(self) -> KGGraphRegistrySummary:
        """Get summary statistics for knowledge graph registry."""
        try:
            # Get total counts
            total_sql = "SELECT COUNT(*) as total FROM kg_graph_registry"
            total_result = await self.connection_manager.execute_query(total_sql, {})
            total_graphs = total_result[0]['total'] if total_result and len(total_result) > 0 else 0
            
            # Get active graphs
            active_sql = "SELECT COUNT(*) as active FROM kg_graph_registry WHERE lifecycle_status = 'active'"
            active_result = await self.connection_manager.execute_query(active_sql, {})
            active_graphs = active_result[0]['active'] if active_result and len(active_result) > 0 else 0
            
            # Get healthy graphs
            healthy_sql = "SELECT COUNT(*) as healthy FROM kg_graph_registry WHERE health_status = 'healthy'"
            healthy_result = await self.connection_manager.execute_query(healthy_sql, {})
            healthy_graphs = healthy_result[0]['healthy'] if healthy_result and len(healthy_result) > 0 else 0
            
            # Get total nodes and relationships
            metrics_sql = "SELECT SUM(total_nodes) as total_nodes, SUM(total_relationships) as total_relationships FROM kg_graph_registry"
            metrics_result = await self.connection_manager.execute_query(metrics_sql, {})
            total_nodes = metrics_result[0]['total_nodes'] if metrics_result and len(metrics_result) > 0 and metrics_result[0]['total_nodes'] else 0
            total_relationships = metrics_result[0]['total_relationships'] if metrics_result and len(metrics_result) > 0 and metrics_result[0]['total_relationships'] else 0
            
            # Get graphs by category
            category_sql = "SELECT graph_category, COUNT(*) as count FROM kg_graph_registry GROUP BY graph_category"
            category_result = await self.connection_manager.execute_query(category_sql, {})
            graphs_by_category = {row['graph_category']: row['count'] for row in category_result if 'graph_category' in row and 'count' in row}
            
            # Get graphs by status
            status_sql = "SELECT integration_status, COUNT(*) as count FROM kg_graph_registry GROUP BY integration_status"
            status_result = await self.connection_manager.execute_query(status_sql, {})
            graphs_by_status = {row['integration_status']: row['count'] for row in status_result if 'integration_status' in row and 'count' in row}
            
            return KGGraphRegistrySummary(
                total_graphs=total_graphs,
                active_graphs=active_graphs,
                healthy_graphs=healthy_graphs,
                total_nodes=total_nodes,
                total_relationships=total_relationships,
                graphs_by_category=graphs_by_category,
                graphs_by_status=graphs_by_status
            )
            
        except Exception as e:
            logger.error(f"Error getting registry summary: {e}")
            return KGGraphRegistrySummary(
                total_graphs=0,
                active_graphs=0,
                healthy_graphs=0,
                total_nodes=0,
                total_relationships=0,
                graphs_by_category={},
                graphs_by_status={}
            )

    # ==================== Cleanup ====================
    
    async def cleanup(self) -> None:
        """Cleanup repository resources asynchronously"""
        try:
            logger.info("Knowledge Graph Registry Repository cleanup completed")
        except Exception as e:
            logger.error(f"Failed to cleanup Knowledge Graph Registry Repository: {e}")
            raise
    
    # ==================== ADDITIONAL METHODS FROM ORIGINAL ====================
    
    async def update_neo4j_status(self, graph_id: str, import_status: str, export_status: str = None) -> bool:
        """Update Neo4j synchronization status."""
        try:
            if export_status:
                query = f"""
                    UPDATE {self.table_name} 
                    SET neo4j_import_status = :import_status, neo4j_export_status = :export_status, updated_at = :updated_at
                    WHERE graph_id = :graph_id
                """
                params = {
                    "import_status": import_status, 
                    "export_status": export_status, 
                    "updated_at": datetime.now(timezone.utc).isoformat(), 
                    "graph_id": graph_id
                }
            else:
                query = f"""
                    UPDATE {self.table_name} 
                    SET neo4j_import_status = :import_status, updated_at = :updated_at
                    WHERE graph_id = :graph_id
                """
                params = {
                    "import_status": import_status, 
                    "updated_at": datetime.now(timezone.utc).isoformat(), 
                    "graph_id": graph_id
                }
            
            await self.connection_manager.execute_update(query, params)
            logger.info(f"Updated Neo4j status for graph {graph_id}: {import_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Neo4j status for graph {graph_id}: {e}")
            return False
    
    async def update_graph_metrics(self, graph_id: str, nodes: int, relationships: int) -> bool:
        """Update graph data metrics."""
        try:
            sql = """
            UPDATE kg_graph_registry 
            SET total_nodes = :nodes, total_relationships = :relationships, updated_at = :updated_at
            WHERE graph_id = :graph_id
            """
            params = {
                "nodes": nodes, 
                "relationships": relationships, 
                "updated_at": datetime.now().isoformat(), 
                "graph_id": graph_id
            }
            
            await self.connection_manager.execute_update(sql, params)
            logger.info(f"✅ Updated graph metrics for graph {graph_id}: {nodes} nodes, {relationships} relationships")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update graph metrics for graph {graph_id}: {e}")
            return False
    
    async def update_health_score(self, graph_id: str, health_score: int) -> bool:
        """Update overall health score."""
        try:
            sql = """
            UPDATE kg_graph_registry 
            SET overall_health_score = :health_score, updated_at = :updated_at
            WHERE graph_id = :graph_id
            """
            params = {
                "health_score": health_score, 
                "updated_at": datetime.now().isoformat(), 
                "graph_id": graph_id
            }
            
            await self.connection_manager.execute_update(sql, params)
            logger.info(f"✅ Updated health score for graph {graph_id}: {health_score}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update health score for graph {graph_id}: {e}")
            return False
    
    async def get_by_graph_id(self, graph_id: str) -> Optional[KGGraphRegistry]:
        """Get knowledge graph registry by graph ID."""
        try:
            return await self.get_by_id(graph_id)
        except Exception as e:
            logger.error(f"Error getting registry by graph_id {graph_id}: {e}")
            return None
    
    async def get_by_user_id(self, user_id: str, org_id: Optional[str] = None) -> List[KGGraphRegistry]:
        """Get knowledge graph registries by user ID."""
        try:
            if org_id:
                return await self.get_by_user(user_id, org_id)
            else:
                query = f"SELECT * FROM {self.table_name} WHERE user_id = :user_id ORDER BY created_at DESC"
                result = await self.connection_manager.execute_query(query, {"user_id": user_id})
                
                registries = []
                for row in result:
                    registries.append(KGGraphRegistry(**row))
                
                return registries
                
        except Exception as e:
            logger.error(f"Error getting registries by user_id {user_id}: {e}")
            return []
    
    async def get_by_integration_status_old(self, status: str) -> List[KGGraphRegistry]:
        """Get knowledge graph registries by integration status (legacy method)."""
        try:
            return await self.get_by_integration_status(status)
        except Exception as e:
            logger.error(f"Error getting registries by integration_status {status}: {e}")
            return []
    
    async def get_by_workflow_source_old(self, workflow_source: str) -> List[KGGraphRegistry]:
        """Get knowledge graph registries by workflow source (legacy method)."""
        try:
            return await self.get_by_workflow_source(workflow_source)
        except Exception as e:
            logger.error(f"Error getting registries by workflow_source {workflow_source}: {e}")
            return []
