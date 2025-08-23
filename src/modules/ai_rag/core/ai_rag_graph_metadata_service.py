"""
AI RAG Graph Metadata Service
=============================

Business logic layer for AI RAG Graph Metadata operations.
Orchestrates operations across repositories and models.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import uuid

from src.engine.database.connection_manager import ConnectionManager
from ..repositories.ai_rag_graph_metadata_repository import AIRagGraphMetadataRepository
from ..repositories.ai_rag_registry_repository import AIRagRegistryRepository
from ..models.ai_rag_graph_metadata import AIRagGraphMetadata

logger = logging.getLogger(__name__)


class AIRagGraphMetadataService:
    """
    Service for AI RAG Graph Metadata operations.
    
    Handles business logic for graph metadata management including:
    - Graph metadata lifecycle management
    - Graph file management and validation
    - Integration coordination with other modules
    - Performance monitoring and quality assessment
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize the service.
        
        Args:
            connection_manager: Database connection manager instance
        """
        self.connection_manager = connection_manager
        self.graph_metadata_repo = AIRagGraphMetadataRepository(connection_manager)
        self.registry_repo = AIRagRegistryRepository(connection_manager)
    
    async def create_graph_metadata(
        self,
        registry_id: str,
        graph_name: str,
        graph_type: str,
        graph_category: str,
        created_by: str,
        dept_id: Optional[str] = None,
        org_id: Optional[str] = None,
        output_directory: Optional[str] = None
    ) -> Optional[AIRagGraphMetadata]:
        """
        Create new graph metadata record.
        
        Args:
            registry_id: AI RAG registry ID
            graph_name: Human-readable name for the graph
            graph_type: Type of graph (entity_relationship, knowledge_graph, dependency_graph)
            graph_category: Category of graph (technical, business, operational)
            created_by: User ID creating the graph
            dept_id: Department ID for traceability
            org_id: Organization ID for traceability
            output_directory: Path to output directory (auto-generated if not provided)
            
        Returns:
            AIRagGraphMetadata: Created graph metadata instance, None if failed
        """
        try:
            # Validate registry exists
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                logger.error(f"❌ Registry not found: {registry_id}")
                return None
            
            # Generate graph ID
            graph_id = f"graph_{uuid.uuid4().hex[:8]}"
            
            # Generate output directory if not provided
            if not output_directory:
                output_directory = f"output/graphs/ai_rag/{graph_id}"
            
            # Create graph metadata instance
            graph_metadata = AIRagGraphMetadata(
                graph_id=graph_id,
                registry_id=registry_id,
                graph_name=graph_name,
                graph_type=graph_type,
                graph_category=graph_category,
                created_by=created_by,
                dept_id=dept_id,
                org_id=org_id,
                output_directory=output_directory,
                processing_start_time=datetime.now().isoformat()
            )
            
            # Save to database
            success = await self.graph_metadata_repo.create(graph_metadata.to_dict())
            if success:
                logger.info(f"✅ Created graph metadata: {graph_id}")
                return graph_metadata
            else:
                logger.error(f"❌ Failed to save graph metadata to database: {graph_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to create graph metadata: {e}")
            return None
    
    async def get_graph_metadata_by_id(self, graph_id: str) -> Optional[AIRagGraphMetadata]:
        """
        Get graph metadata by ID.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            AIRagGraphMetadata: Graph metadata instance if found, None otherwise
        """
        try:
            data = await self.graph_metadata_repo.get_by_id(graph_id)
            if data:
                return AIRagGraphMetadata(**data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get graph metadata by ID {graph_id}: {e}")
            return None
    
    async def get_graphs_by_registry(self, registry_id: str) -> List[AIRagGraphMetadata]:
        """
        Get all graphs for a specific registry.
        
        Args:
            registry_id: AI RAG registry ID
            
        Returns:
            List[AIRagGraphMetadata]: List of graph metadata instances
        """
        try:
            data_list = await self.graph_metadata_repo.get_by_registry_id(registry_id)
            return [AIRagGraphMetadata(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to get graphs by registry {registry_id}: {e}")
            return []
    
    async def get_graphs_by_status(self, status: str) -> List[AIRagGraphMetadata]:
        """
        Get graphs by processing status.
        
        Args:
            status: Processing status (processing, completed, failed)
            
        Returns:
            List[AIRagGraphMetadata]: List of graph metadata instances
        """
        try:
            data_list = await self.graph_metadata_repo.get_by_status(status)
            return [AIRagGraphMetadata(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to get graphs by status {status}: {e}")
            return []
    
    async def get_processing_graphs(self) -> List[AIRagGraphMetadata]:
        """
        Get currently processing graphs.
        
        Returns:
            List[AIRagGraphMetadata]: List of processing graph metadata instances
        """
        try:
            data_list = await self.graph_metadata_repo.get_processing_graphs()
            return [AIRagGraphMetadata(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to get processing graphs: {e}")
            return []
    
    async def get_failed_graphs(self) -> List[AIRagGraphMetadata]:
        """
        Get failed graphs.
        
        Returns:
            List[AIRagGraphMetadata]: List of failed graph metadata instances
        """
        try:
            data_list = await self.graph_metadata_repo.get_failed_graphs()
            return [AIRagGraphMetadata(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to get failed graphs: {e}")
            return []
    
    async def get_high_quality_graphs(self, min_quality_score: float = 0.8) -> List[AIRagGraphMetadata]:
        """
        Get high-quality graphs.
        
        Args:
            min_quality_score: Minimum quality score threshold
            
        Returns:
            List[AIRagGraphMetadata]: List of high-quality graph metadata instances
        """
        try:
            data_list = await self.graph_metadata_repo.get_high_quality_graphs(min_quality_score)
            return [AIRagGraphMetadata(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to get high-quality graphs: {e}")
            return []
    
    async def update_graph_metadata(self, graph_id: str, updates: Dict[str, Any], updated_by: str) -> bool:
        """
        Update graph metadata.
        
        Args:
            graph_id: Unique identifier for the graph
            updates: Dictionary containing fields to update
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Add updated_by and updated_at
            updates['updated_by'] = updated_by
            updates['updated_at'] = datetime.now().isoformat()
            
            # Update in database
            success = await self.graph_metadata_repo.update(graph_id, updates)
            if success:
                logger.info(f"✅ Updated graph metadata: {graph_id}")
                return True
            else:
                logger.error(f"❌ Failed to update graph metadata: {graph_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to update graph metadata {graph_id}: {e}")
            return False
    
    async def mark_processing_complete(
        self, 
        graph_id: str, 
        duration_ms: Optional[int] = None,
        updated_by: Optional[str] = None
    ) -> bool:
        """
        Mark graph processing as complete.
        
        Args:
            graph_id: Unique identifier for the graph
            duration_ms: Processing duration in milliseconds
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            updates = {
                'processing_status': 'completed',
                'processing_end_time': datetime.now().isoformat()
            }
            
            if duration_ms is not None:
                updates['processing_duration_ms'] = duration_ms
            
            if updated_by:
                updates['updated_by'] = updated_by
            
            return await self.update_graph_metadata(graph_id, updates, updated_by or 'system')
            
        except Exception as e:
            logger.error(f"❌ Failed to mark processing complete for {graph_id}: {e}")
            return False
    
    async def mark_processing_failed(
        self, 
        graph_id: str, 
        error_message: str,
        updated_by: Optional[str] = None
    ) -> bool:
        """
        Mark graph processing as failed.
        
        Args:
            graph_id: Unique identifier for the graph
            error_message: Error message describing the failure
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get current graph metadata
            graph_metadata = await self.get_graph_metadata_by_id(graph_id)
            if not graph_metadata:
                logger.error(f"❌ Graph metadata not found: {graph_id}")
                return False
            
            # Add validation error and mark as failed
            graph_metadata.add_validation_error(error_message)
            graph_metadata.mark_processing_failed(error_message)
            
            # Update in database
            updates = {
                'processing_status': 'failed',
                'processing_end_time': graph_metadata.processing_end_time,
                'validation_errors': graph_metadata.validation_errors,
                'validation_status': 'failed'
            }
            
            return await self.update_graph_metadata(graph_id, updates, updated_by or 'system')
            
        except Exception as e:
            logger.error(f"❌ Failed to mark processing failed for {graph_id}: {e}")
            return False
    
    async def mark_validated(self, graph_id: str, updated_by: str) -> bool:
        """
        Mark graph as validated.
        
        Args:
            graph_id: Unique identifier for the graph
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            updates = {
                'validation_status': 'validated'
            }
            
            return await self.update_graph_metadata(graph_id, updates, updated_by)
            
        except Exception as e:
            logger.error(f"❌ Failed to mark validated for {graph_id}: {e}")
            return False
    
    async def update_graph_structure(
        self, 
        graph_id: str, 
        node_count: int, 
        edge_count: int, 
        density: float, 
        diameter: int,
        updated_by: str
    ) -> bool:
        """
        Update graph structure metrics.
        
        Args:
            graph_id: Unique identifier for the graph
            node_count: Number of nodes in the graph
            edge_count: Number of edges in the graph
            density: Graph density (0-1)
            diameter: Graph diameter
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            updates = {
                'node_count': node_count,
                'edge_count': edge_count,
                'graph_density': density,
                'graph_diameter': diameter
            }
            
            return await self.update_graph_metadata(graph_id, updates, updated_by)
            
        except Exception as e:
            logger.error(f"❌ Failed to update graph structure for {graph_id}: {e}")
            return False
    
    async def update_performance_metrics(
        self, 
        graph_id: str, 
        generation_time_ms: int, 
        memory_mb: float, 
        cpu_percent: float,
        updated_by: str
    ) -> bool:
        """
        Update performance metrics.
        
        Args:
            graph_id: Unique identifier for the graph
            generation_time_ms: Generation time in milliseconds
            memory_mb: Memory usage in MB
            cpu_percent: CPU usage percentage
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            updates = {
                'generation_time_ms': generation_time_ms,
                'memory_usage_mb': memory_mb,
                'cpu_usage_percent': cpu_percent
            }
            
            return await self.update_graph_metadata(graph_id, updates, updated_by)
            
        except Exception as e:
            logger.error(f"❌ Failed to update performance metrics for {graph_id}: {e}")
            return False
    
    async def add_source_document(self, graph_id: str, document_id: str, updated_by: str) -> bool:
        """
        Add a source document to the graph.
        
        Args:
            graph_id: Unique identifier for the graph
            document_id: Document ID to add
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get current graph metadata
            graph_metadata = await self.get_graph_metadata_by_id(graph_id)
            if not graph_metadata:
                logger.error(f"❌ Graph metadata not found: {graph_id}")
                return False
            
            # Add source document
            graph_metadata.add_source_document(document_id)
            
            # Update in database
            updates = {
                'source_documents': graph_metadata.source_documents
            }
            
            return await self.update_graph_metadata(graph_id, updates, updated_by)
            
        except Exception as e:
            logger.error(f"❌ Failed to add source document for {graph_id}: {e}")
            return False
    
    async def add_source_entity(self, graph_id: str, entity: Dict[str, Any], updated_by: str) -> bool:
        """
        Add a source entity to the graph.
        
        Args:
            graph_id: Unique identifier for the graph
            entity: Entity data to add
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get current graph metadata
            graph_metadata = await self.get_graph_metadata_by_id(graph_id)
            if not graph_metadata:
                logger.error(f"❌ Graph metadata not found: {graph_id}")
                return False
            
            # Add source entity
            graph_metadata.add_source_entity(entity)
            
            # Update in database
            updates = {
                'source_entities': graph_metadata.source_entities
            }
            
            return await self.update_graph_metadata(graph_id, updates, updated_by)
            
        except Exception as e:
            logger.error(f"❌ Failed to add source entity for {graph_id}: {e}")
            return False
    
    async def add_source_relationship(self, graph_id: str, relationship: Dict[str, Any], updated_by: str) -> bool:
        """
        Add a source relationship to the graph.
        
        Args:
            graph_id: Unique identifier for the graph
            relationship: Relationship data to add
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get current graph metadata
            graph_metadata = await self.get_graph_metadata_by_id(graph_id)
            if not graph_metadata:
                logger.error(f"❌ Graph metadata not found: {graph_id}")
                return False
            
            # Add source relationship
            graph_metadata.add_source_relationship(relationship)
            
            # Update in database
            updates = {
                'source_relationships': graph_metadata.source_relationships
            }
            
            return await self.update_graph_metadata(graph_id, updates, updated_by)
            
        except Exception as e:
            logger.error(f"❌ Failed to add source relationship for {graph_id}: {e}")
            return False
    
    async def add_graph_file(
        self, 
        graph_id: str, 
        file_path: str, 
        file_format: str, 
        file_size: Optional[int] = None,
        updated_by: str = 'system'
    ) -> bool:
        """
        Add a generated graph file.
        
        Args:
            graph_id: Unique identifier for the graph
            file_path: Path to the graph file
            file_format: Format of the file (cypher, graphml, jsonld, png, svg, html)
            file_size: Size of the file in bytes
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get current graph metadata
            graph_metadata = await self.get_graph_metadata_by_id(graph_id)
            if not graph_metadata:
                logger.error(f"❌ Graph metadata not found: {graph_id}")
                return False
            
            # Add graph file
            graph_metadata.add_graph_file(file_path, file_format, file_size)
            
            # Update in database
            updates = {
                'graph_files': graph_metadata.graph_files,
                'file_formats': graph_metadata.file_formats
            }
            
            return await self.update_graph_metadata(graph_id, updates, updated_by)
            
        except Exception as e:
            logger.error(f"❌ Failed to add graph file for {graph_id}: {e}")
            return False
    
    async def calculate_and_update_quality_score(self, graph_id: str, updated_by: str = 'system') -> bool:
        """
        Calculate and update quality score for the graph.
        
        Args:
            graph_id: Unique identifier for the graph
            updated_by: User ID making the update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get current graph metadata
            graph_metadata = await self.get_graph_metadata_by_id(graph_id)
            if not graph_metadata:
                logger.error(f"❌ Graph metadata not found: {graph_id}")
                return False
            
            # Calculate quality score
            quality_score = graph_metadata.calculate_quality_score()
            
            # Update in database
            updates = {
                'quality_score': quality_score
            }
            
            success = await self.update_graph_metadata(graph_id, updates, updated_by)
            if success:
                logger.info(f"✅ Updated quality score for {graph_id}: {quality_score}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate quality score for {graph_id}: {e}")
            return False
    
    async def delete_graph_metadata(self, graph_id: str) -> bool:
        """
        Delete graph metadata record.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            # Check if graph exists
            if not await self.graph_metadata_repo.exists(graph_id):
                logger.warning(f"⚠️ Graph metadata not found for deletion: {graph_id}")
                return True
            
            # Delete from database
            success = await self.graph_metadata_repo.delete(graph_id)
            if success:
                logger.info(f"✅ Deleted graph metadata: {graph_id}")
                return True
            else:
                logger.error(f"❌ Failed to delete graph metadata: {graph_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to delete graph metadata {graph_id}: {e}")
            return False
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for all graphs.
        
        Returns:
            Dict: Graph statistics
        """
        try:
            # Get performance stats from repository
            performance_stats = await self.graph_metadata_repo.get_performance_stats()
            
            # Get counts by status
            total_count = await self.graph_metadata_repo.count_total()
            processing_count = await self.graph_metadata_repo.count_by_status('processing')
            completed_count = await self.graph_metadata_repo.count_by_status('completed')
            failed_count = await self.graph_metadata_repo.count_by_status('failed')
            
            # Get counts by validation status
            pending_count = await self.graph_metadata_repo.count_by_validation_status('pending')
            validated_count = await self.graph_metadata_repo.count_by_validation_status('validated')
            validation_failed_count = await self.graph_metadata_repo.count_by_validation_status('failed')
            
            # Get counts by graph type
            entity_relationship_count = len(await self.graph_metadata_repo.get_by_graph_type('entity_relationship'))
            knowledge_graph_count = len(await self.graph_metadata_repo.get_by_graph_type('knowledge_graph'))
            dependency_graph_count = len(await self.graph_metadata_repo.get_by_graph_type('dependency_graph'))
            
            # Get counts by category
            technical_count = len(await self.graph_metadata_repo.get_by_category('technical'))
            business_count = len(await self.graph_metadata_repo.get_by_category('business'))
            operational_count = len(await self.graph_metadata_repo.get_by_category('operational'))
            
            return {
                "total_graphs": total_count,
                "by_status": {
                    "processing": processing_count,
                    "completed": completed_count,
                    "failed": failed_count
                },
                "by_validation": {
                    "pending": pending_count,
                    "validated": validated_count,
                    "failed": validation_failed_count
                },
                "by_type": {
                    "entity_relationship": entity_relationship_count,
                    "knowledge_graph": knowledge_graph_count,
                    "dependency_graph": dependency_graph_count
                },
                "by_category": {
                    "technical": technical_count,
                    "business": business_count,
                    "operational": operational_count
                },
                "performance": performance_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get graph statistics: {e}")
            return {}
    
    async def search_graphs(self, search_term: str, limit: int = 50) -> List[AIRagGraphMetadata]:
        """
        Search graphs by name, type, or category.
        
        Args:
            search_term: Search term to look for
            limit: Maximum number of results to return
            
        Returns:
            List[AIRagGraphMetadata]: List of matching graph metadata instances
        """
        try:
            data_list = await self.graph_metadata_repo.search(search_term, limit)
            return [AIRagGraphMetadata(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to search graphs: {e}")
            return []
    
    async def get_graphs_by_date_range(self, start_date: str, end_date: str) -> List[AIRagGraphMetadata]:
        """
        Get graphs within a date range.
        
        Args:
            start_date: Start date (ISO format string)
            end_date: End date (ISO format string)
            
        Returns:
            List[AIRagGraphMetadata]: List of graph metadata instances within the date range
        """
        try:
            data_list = await self.graph_metadata_repo.get_graphs_by_date_range(start_date, end_date)
            return [AIRagGraphMetadata(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to get graphs by date range: {e}")
            return []
    
    async def get_graphs_by_integration(self, integration_type: str, integration_id: str) -> List[AIRagGraphMetadata]:
        """
        Get graphs by integration type and ID.
        
        Args:
            integration_type: Type of integration (kg_neo4j, aasx, twin_registry)
            integration_id: Integration ID
            
        Returns:
            List[AIRagGraphMetadata]: List of graph metadata instances
        """
        try:
            if integration_type == 'kg_neo4j':
                data_list = await self.graph_metadata_repo.get_graphs_by_kg_neo4j_integration(integration_id)
            elif integration_type == 'aasx':
                data_list = await self.graph_metadata_repo.get_graphs_by_aasx_integration(integration_id)
            elif integration_type == 'twin_registry':
                data_list = await self.graph_metadata_repo.get_graphs_by_twin_registry_integration(integration_id)
            else:
                logger.error(f"❌ Unknown integration type: {integration_type}")
                return []
            
            return [AIRagGraphMetadata(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to get graphs by integration {integration_type}: {e}")
            return []
    
    async def cleanup_failed_graphs(self, older_than_days: int = 30) -> int:
        """
        Clean up failed graphs older than specified days.
        
        Args:
            older_than_days: Number of days to consider for cleanup
            
        Returns:
            int: Number of graphs cleaned up
        """
        try:
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
            
            # Get failed graphs older than cutoff
            failed_graphs = await self.get_failed_graphs()
            old_failed_graphs = [
                graph for graph in failed_graphs 
                if graph.created_at < cutoff_date
            ]
            
            # Delete old failed graphs
            cleaned_count = 0
            for graph in old_failed_graphs:
                if await self.delete_graph_metadata(graph.graph_id):
                    cleaned_count += 1
            
            logger.info(f"✅ Cleaned up {cleaned_count} old failed graphs")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup failed graphs: {e}")
            return 0
    
    async def validate_graph_metadata(self, graph_id: str) -> Dict[str, Any]:
        """
        Validate graph metadata for completeness and consistency.
        
        Args:
            graph_id: Unique identifier for the graph
            
        Returns:
            Dict: Validation results
        """
        try:
            # Get graph metadata
            graph_metadata = await self.get_graph_metadata_by_id(graph_id)
            if not graph_metadata:
                return {
                    "valid": False,
                    "errors": ["Graph metadata not found"],
                    "warnings": []
                }
            
            errors = []
            warnings = []
            
            # Validate required fields
            if not graph_metadata.graph_name:
                errors.append("Graph name is required")
            
            if not graph_metadata.output_directory:
                errors.append("Output directory is required")
            
            # Validate processing status consistency
            if graph_metadata.is_completed and not graph_metadata.processing_end_time:
                errors.append("Completed graphs must have processing end time")
            
            if graph_metadata.is_failed and not graph_metadata.validation_errors_list:
                warnings.append("Failed graphs should have validation errors")
            
            # Validate file references
            if graph_metadata.is_completed and not graph_metadata.graph_files_list:
                warnings.append("Completed graphs should have generated files")
            
            # Validate quality score
            if graph_metadata.quality_score < 0.0 or graph_metadata.quality_score > 1.0:
                errors.append("Quality score must be between 0.0 and 1.0")
            
            # Validate graph structure
            if graph_metadata.node_count < 0:
                errors.append("Node count cannot be negative")
            
            if graph_metadata.edge_count < 0:
                errors.append("Edge count cannot be negative")
            
            if graph_metadata.graph_density < 0.0 or graph_metadata.graph_density > 1.0:
                errors.append("Graph density must be between 0.0 and 1.0")
            
            # Check for orphaned graphs (no registry reference)
            if not await self.registry_repo.exists(graph_metadata.registry_id):
                errors.append("Referenced registry does not exist")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "quality_score": graph_metadata.quality_score,
                "processing_status": graph_metadata.processing_status,
                "validation_status": graph_metadata.validation_status
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to validate graph metadata {graph_id}: {e}")
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": []
            }
