"""
AI RAG Graph Metadata Repository
================================

Data access layer for ai_rag_graph_metadata table.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class AIRagGraphMetadataRepository:
    """
    Repository for AI RAG Graph Metadata operations.
    
    Handles all database operations for the ai_rag_graph_metadata table
    including CRUD operations and complex queries.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize the repository.
        
        Args:
            connection_manager: Database connection manager instance
        """
        self.connection_manager = connection_manager
        self.table_name = "ai_rag_graph_metadata"
    
    async def create(self, graph_metadata: Dict[str, Any]) -> Optional[str]:
        """
        Create a new graph metadata record.
        
        Args:
            graph_metadata: Dictionary containing graph metadata fields
            
        Returns:
            str: Created graph_id if successful, None otherwise
        """
        try:
            # Prepare the INSERT query
            columns = list(graph_metadata.keys())
            placeholders = ', '.join(['?' for _ in columns])
            values = list(graph_metadata.values())
            
            query = f"""
                INSERT INTO {self.table_name} 
                ({', '.join(columns)}) 
                VALUES ({placeholders})
            """
            
            await self.connection_manager.execute_update(query, dict(zip(columns, values)))
            
            graph_id = graph_metadata.get('graph_id')
            logger.info(f"✅ Created graph metadata record: {graph_id}")
            return graph_id
                
        except Exception as e:
            logger.error(f"❌ Failed to create graph metadata record: {e}")
            return None
    
    async def get_by_id(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """
        Get graph metadata by ID.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            Dict: Graph metadata record if found, None otherwise
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE graph_id = ?"
            result = await self.connection_manager.execute_query(query, {"graph_id": graph_id})
            
            if result and len(result) > 0:
                return result[0]
            return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by ID {graph_id}: {e}")
            return None
    
    async def get_by_registry_id(self, registry_id: str) -> List[Dict[str, Any]]:
        """
        Get all graph metadata records for a specific registry.
        
        Args:
            registry_id: AI RAG registry ID
            
        Returns:
            List: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ?"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by registry ID {registry_id}: {e}")
            return []
    
    async def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by processing status.
        
        Args:
            status: Processing status (processing, completed, failed)
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE processing_status = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"status": status})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by status {status}: {e}")
            return []
    
    async def get_by_validation_status(self, validation_status: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by validation status.
        
        Args:
            validation_status: Validation status (pending, validated, failed)
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE validation_status = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"validation_status": validation_status})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by validation status {validation_status}: {e}")
            return []
    
    async def get_by_graph_type(self, graph_type: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by graph type.
        
        Args:
            graph_type: Graph type (entity_relationship, knowledge_graph, dependency_graph)
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE graph_type = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"graph_type": graph_type})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by graph type {graph_type}: {e}")
            return []
    
    async def get_by_category(self, graph_category: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by graph category.
        
        Args:
            graph_category: Graph category (technical, business, operational)
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE graph_category = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"graph_category": graph_category})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by category {graph_category}: {e}")
            return []
    
    async def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records created by a specific user.
        
        Args:
            user_id: User ID who created the graphs
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE created_by = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"user_id": user_id})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by user {user_id}: {e}")
            return []
    
    async def get_by_department(self, dept_id: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by department.
        
        Args:
            dept_id: Department ID
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE dept_id = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"dept_id": dept_id})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by department {dept_id}: {e}")
            return []
    
    async def get_by_organization(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE org_id = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"org_id": org_id})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by organization {org_id}: {e}")
            return []
    
    async def get_high_quality_graphs(self, min_quality_score: float = 0.8) -> List[Dict[str, Any]]:
        """
        Get high-quality graph metadata records.
        
        Args:
            min_quality_score: Minimum quality score threshold (default: 0.8)
            
        Returns:
            List[Dict]: List of high-quality graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE quality_score >= ? ORDER BY quality_score DESC"
            result = await self.connection_manager.execute_query(query, {"min_quality_score": min_quality_score})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get high-quality graph metadata: {e}")
            return []
    
    async def get_failed_graphs(self) -> List[Dict[str, Any]]:
        """
        Get failed graph metadata records.
        
        Returns:
            List[Dict]: List of failed graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE processing_status = 'failed' ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get failed graph metadata: {e}")
            return []
    
    async def get_processing_graphs(self) -> List[Dict[str, Any]]:
        """
        Get currently processing graph metadata records.
        
        Returns:
            List[Dict]: List of processing graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE processing_status = 'processing' ORDER BY created_at ASC"
            result = await self.connection_manager.execute_query(query, {})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get processing graph metadata: {e}")
            return []
    
    async def get_recent_graphs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent graph metadata records.
        
        Args:
            limit: Maximum number of records to return (default: 10)
            
        Returns:
            List[Dict]: List of recent graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT ?"
            result = await self.connection_manager.execute_query(query, {"limit": limit})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get recent graph metadata: {e}")
            return []
    
    async def get_graphs_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records within a date range.
        
        Args:
            start_date: Start date (ISO format string)
            end_date: End date (ISO format string)
            
        Returns:
            List[Dict]: List of graph metadata records within the date range
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE created_at BETWEEN ? AND ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"start_date": start_date, "end_date": end_date})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by date range: {e}")
            return []
    
    async def update(self, graph_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a graph metadata record.
        
        Args:
            graph_id: Unique identifier for the graph
            updates: Dictionary containing fields to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            # Prepare the UPDATE query
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [graph_id]
            
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE graph_id = ?"
            
            await self.connection_manager.execute_update(query, dict(zip(updates.keys(), values)))
            
            logger.info(f"✅ Updated graph metadata record: {graph_id}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Failed to update graph metadata record {graph_id}: {e}")
            return False
    
    async def delete(self, graph_id: str) -> bool:
        """
        Delete a graph metadata record.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE graph_id = ?"
            await self.connection_manager.execute_update(query, {"graph_id": graph_id})
            
            logger.info(f"✅ Deleted graph metadata record: {graph_id}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Failed to delete graph metadata record {graph_id}: {e}")
            return False
    
    async def count_total(self) -> int:
        """
        Get total count of graph metadata records.
        
        Returns:
            int: Total count of records
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            result = await self.connection_manager.execute_query(query, {})
            
            return result[0]['count'] if result and len(result) > 0 else 0
                
        except Exception as e:
            logger.error(f"❌ Failed to count total graph metadata records: {e}")
            return 0
    
    async def count_by_status(self, status: str) -> int:
        """
        Get count of graph metadata records by status.
        
        Args:
            status: Processing status
            
        Returns:
            int: Count of records with the specified status
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE processing_status = ?"
            result = await self.connection_manager.execute_query(query, {"status": status})
            
            return result[0]['count'] if result and len(result) > 0 else 0
                
        except Exception as e:
            logger.error(f"❌ Failed to count graph metadata by status {status}: {e}")
            return 0
    
    async def count_by_validation_status(self, validation_status: str) -> int:
        """
        Get count of graph metadata records by validation status.
        
        Args:
            validation_status: Validation status
            
        Returns:
            int: Count of records with the specified validation status
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE validation_status = ?"
            result = await self.connection_manager.execute_query(query, {"validation_status": validation_status})
            
            return result[0]['count'] if result and len(result) > 0 else 0
                
        except Exception as e:
            logger.error(f"❌ Failed to count graph metadata by validation status {validation_status}: {e}")
            return 0
    
    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search graph metadata records by name or description.
        
        Args:
            search_term: Search term to look for
            limit: Maximum number of results to return
            
        Returns:
            List[Dict]: List of matching graph metadata records
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE graph_name LIKE ? OR graph_type LIKE ? OR graph_category LIKE ?
                ORDER BY created_at DESC 
                LIMIT ?
            """
            search_pattern = f"%{search_term}%"
            result = await self.connection_manager.execute_query(query, {
                "search_pattern": search_pattern,
                "limit": limit
            })
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to search graph metadata: {e}")
            return []
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for graph metadata.
        
        Returns:
            Dict: Performance statistics
        """
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_graphs,
                    AVG(quality_score) as avg_quality_score,
                    AVG(generation_time_ms) as avg_generation_time,
                    AVG(memory_usage_mb) as avg_memory_usage,
                    AVG(cpu_usage_percent) as avg_cpu_usage,
                    SUM(CASE WHEN processing_status = 'completed' THEN 1 ELSE 0 END) as completed_graphs,
                    SUM(CASE WHEN processing_status = 'failed' THEN 1 ELSE 0 END) as failed_graphs,
                    SUM(CASE WHEN validation_status = 'validated' THEN 1 ELSE 0 END) as validated_graphs
                FROM {self.table_name}
            """
            result = await self.connection_manager.execute_query(query, {})
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    "total_graphs": row['total_graphs'],
                    "avg_quality_score": round(row['avg_quality_score'], 3) if row['avg_quality_score'] else 0.0,
                    "avg_generation_time_ms": round(row['avg_generation_time'], 2) if row['avg_generation_time'] else 0.0,
                    "avg_memory_usage_mb": round(row['avg_memory_usage'], 2) if row['avg_memory_usage'] else 0.0,
                    "avg_cpu_usage_percent": round(row['avg_cpu_usage'], 2) if row['avg_cpu_usage'] else 0.0,
                    "completed_graphs": row['completed_graphs'],
                    "failed_graphs": row['failed_graphs'],
                    "validated_graphs": row['validated_graphs'],
                    "success_rate": round(row['completed_graphs'] / row['total_graphs'] * 100, 2) if row['total_graphs'] > 0 else 0.0
                }
            return {}
                
        except Exception as e:
            logger.error(f"❌ Failed to get performance stats: {e}")
            return {}
    
    async def get_graphs_by_kg_neo4j_integration(self, kg_neo4j_graph_id: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by KG Neo4j integration ID.
        
        Args:
            kg_neo4j_graph_id: KG Neo4j graph ID
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE kg_neo4j_graph_id = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"kg_neo4j_graph_id": kg_neo4j_graph_id})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by KG Neo4j ID {kg_neo4j_graph_id}: {e}")
            return []
    
    async def get_graphs_by_aasx_integration(self, aasx_integration_id: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by AASX integration ID.
        
        Args:
            aasx_integration_id: AASX integration ID
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE aasx_integration_id = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"aasx_integration_id": aasx_integration_id})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by AASX integration ID {aasx_integration_id}: {e}")
            return []
    
    async def get_graphs_by_twin_registry_integration(self, twin_registry_id: str) -> List[Dict[str, Any]]:
        """
        Get graph metadata records by Twin Registry integration ID.
        
        Args:
            twin_registry_id: Twin Registry ID
            
        Returns:
            List[Dict]: List of graph metadata records
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE twin_registry_id = ? ORDER BY created_at DESC"
            result = await self.connection_manager.execute_query(query, {"twin_registry_id": twin_registry_id})
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by Twin Registry ID {twin_registry_id}: {e}")
            return []
    
    async def exists(self, graph_id: str) -> bool:
        """
        Check if a graph metadata record exists.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            bool: True if record exists, False otherwise
        """
        try:
            query = f"SELECT 1 FROM {self.table_name} WHERE graph_id = ? LIMIT 1"
            result = await self.connection_manager.execute_query(query, {"graph_id": graph_id})
            
            return len(result) > 0
                
        except Exception as e:
            logger.error(f"❌ Failed to check existence of graph metadata {graph_id}: {e}")
            return False
