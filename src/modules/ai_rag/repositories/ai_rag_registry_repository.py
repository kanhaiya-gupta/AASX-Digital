"""
AI RAG Registry Repository
==========================

Data access layer for AI RAG registry operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.engine.database.connection_manager import ConnectionManager
from src.modules.ai_rag.models.ai_rag_registry import AIRagRegistry

logger = logging.getLogger(__name__)


class AIRagRegistryRepository:
    """
    AI RAG Registry Repository - Pure Async Implementation
    
    Handles all database operations for AI RAG registry.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "ai_rag_registry"
    
    async def create(self, registry: AIRagRegistry) -> bool:
        """Create a new AI RAG registry"""
        try:
            async with self.connection_manager.get_session() as session:
                # Convert model to dict for database insertion
                registry_data = registry.to_dict()
                
                # Execute insert query
                query = f"""
                INSERT INTO {self.table_name} (
                    registry_id, file_id, registry_name, rag_category, rag_type,
                    rag_priority, rag_version, registry_type, workflow_source,
                    aasx_integration_id, twin_registry_id, kg_neo4j_id,
                    integration_status, overall_health_score, health_status,
                    lifecycle_status, lifecycle_phase, operational_status,
                    availability_status, embedding_generation_status,
                    vector_db_sync_status, embedding_model, vector_db_type,
                    vector_collection_id, rag_techniques_config,
                    supported_file_types_config, processor_capabilities_config,
                    performance_score, data_quality_score, reliability_score,
                    compliance_score, security_level, access_control_level,
                    encryption_enabled, audit_logging_enabled, user_id,
                    org_id, dept_id, owner_team, steward_user_id,
                    created_at, updated_at, activated_at, last_accessed_at,
                    last_modified_at, registry_config, registry_metadata,
                    custom_attributes, tags_config, relationships_config,
                    dependencies_config, rag_instances_config, description,
                    notes, version, model_version
                ) VALUES (
                    :registry_id, :file_id, :registry_name, :rag_category,
                    :rag_type, :rag_priority, :rag_version, :registry_type,
                    :workflow_source, :aasx_integration_id, :twin_registry_id,
                    :kg_neo4j_id, :integration_status, :overall_health_score,
                    :health_status, :lifecycle_status, :lifecycle_phase,
                    :operational_status, :availability_status,
                    :embedding_generation_status, :vector_db_sync_status,
                    :embedding_model, :vector_db_type, :vector_collection_id,
                    :rag_techniques_config, :supported_file_types_config,
                    :processor_capabilities_config, :performance_score,
                    :data_quality_score, :reliability_score, :compliance_score,
                    :security_level, :access_control_level, :encryption_enabled,
                    :audit_logging_enabled, :user_id, :org_id, :dept_id,
                    :owner_team, :steward_user_id, :created_at, :updated_at,
                    :activated_at, :last_accessed_at, :last_modified_at,
                    :registry_config, :registry_metadata, :custom_attributes,
                    :tags_config, :relationships_config, :dependencies_config,
                    :rag_instances_config, :description, :notes, :version,
                    :model_version
                )
                """
                
                await session.execute(query, registry_data)
                await session.commit()
                
                logger.info(f"Created AI RAG registry: {registry.registry_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating AI RAG registry: {e}")
            return False
    
    async def get_by_id(self, registry_id: str) -> Optional[AIRagRegistry]:
        """Get AI RAG registry by ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id"
                result = await session.execute(query, {"registry_id": registry_id})
                row = result.fetchone()
                
                if row:
                    return AIRagRegistry.from_dict(dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Error getting AI RAG registry by ID: {e}")
            return None
    
    async def get_by_file_id(self, file_id: str) -> Optional[AIRagRegistry]:
        """Get AI RAG registry by file ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE file_id = :file_id"
                result = await session.execute(query, {"file_id": file_id})
                row = result.fetchone()
                
                if row:
                    return AIRagRegistry.from_dict(dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Error getting AI RAG registry by file ID: {e}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[AIRagRegistry]:
        """Get all AI RAG registries with pagination"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} LIMIT :limit OFFSET :offset"
                result = await session.execute(query, {"limit": limit, "offset": offset})
                rows = result.fetchall()
                
                return [AIRagRegistry.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting all AI RAG registries: {e}")
            return []
    
    async def update(self, registry: AIRagRegistry) -> bool:
        """Update an existing AI RAG registry"""
        try:
            async with self.connection_manager.get_session() as session:
                registry.update_timestamp()
                registry_data = registry.to_dict()
                
                query = f"""
                UPDATE {self.table_name} SET
                    registry_name = :registry_name, rag_category = :rag_category,
                    rag_type = :rag_type, rag_priority = :rag_priority,
                    rag_version = :rag_version, registry_type = :registry_type,
                    workflow_source = :workflow_source, integration_status = :integration_status,
                    overall_health_score = :overall_health_score, health_status = :health_status,
                    lifecycle_status = :lifecycle_status, lifecycle_phase = :lifecycle_phase,
                    operational_status = :operational_status, availability_status = :availability_status,
                    embedding_generation_status = :embedding_generation_status,
                    vector_db_sync_status = :vector_db_sync_status,
                    performance_score = :performance_score, data_quality_score = :data_quality_score,
                    reliability_score = :reliability_score, compliance_score = :compliance_score,
                    updated_at = :updated_at, registry_config = :registry_config,
                    registry_metadata = :registry_metadata, custom_attributes = :custom_attributes
                WHERE registry_id = :registry_id
                """
                
                await session.execute(query, registry_data)
                await session.commit()
                
                logger.info(f"Updated AI RAG registry: {registry.registry_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating AI RAG registry: {e}")
            return False
    
    async def delete(self, registry_id: str) -> bool:
        """Delete an AI RAG registry"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"DELETE FROM {self.table_name} WHERE registry_id = :registry_id"
                await session.execute(query, {"registry_id": registry_id})
                await session.commit()
                
                logger.info(f"Deleted AI RAG registry: {registry_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting AI RAG registry: {e}")
            return False
    
    async def get_by_user_id(self, user_id: str) -> List[AIRagRegistry]:
        """Get AI RAG registries by user ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE user_id = :user_id"
                result = await session.execute(query, {"user_id": user_id})
                rows = result.fetchall()
                
                return [AIRagRegistry.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting AI RAG registries by user ID: {e}")
            return []
    
    async def get_by_org_id(self, org_id: str) -> List[AIRagRegistry]:
        """Get AI RAG registries by organization ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE org_id = :org_id"
                result = await session.execute(query, {"org_id": org_id})
                rows = result.fetchall()
                
                return [AIRagRegistry.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting AI RAG registries by org ID: {e}")
            return []
    
    async def get_by_status(self, status: str) -> List[AIRagRegistry]:
        """Get AI RAG registries by status"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE integration_status = :status"
                result = await session.execute(query, {"status": status})
                rows = result.fetchall()
                
                return [AIRagRegistry.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting AI RAG registries by status: {e}")
            return []
    
    async def count_total(self) -> int:
        """Get total count of AI RAG registries"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT COUNT(*) as count FROM {self.table_name}"
                result = await session.execute(query)
                row = result.fetchone()
                
                return row['count'] if row else 0
                
        except Exception as e:
            logger.error(f"Error counting AI RAG registries: {e}")
            return 0
    
    async def search(self, search_term: str, limit: int = 50) -> List[AIRagRegistry]:
        """Search AI RAG registries by name or description"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"""
                SELECT * FROM {self.table_name} 
                WHERE registry_name LIKE :search_term 
                OR description LIKE :search_term
                LIMIT :limit
                """
                
                search_pattern = f"%{search_term}%"
                result = await session.execute(query, {
                    "search_term": search_pattern,
                    "limit": limit
                })
                rows = result.fetchall()
                
                return [AIRagRegistry.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error searching AI RAG registries: {e}")
            return []
