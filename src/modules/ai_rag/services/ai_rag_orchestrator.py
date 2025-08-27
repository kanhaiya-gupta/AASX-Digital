"""
AI RAG Orchestrator Service
Main service that coordinates all AI RAG operations and workflows
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

from ..core.ai_rag_registry_service import AIRAGRegistryService
from ..core.document_service import DocumentService
from ..core.embedding_service import EmbeddingService
from ..core.retrieval_service import RetrievalService
from ..core.generation_service import GenerationService
from ..core.ai_rag_graph_metadata_service import AIRAGGraphMetadataService
from ..events.event_bus import EventBus
from ..events.event_types import (
    DocumentProcessingEvent,
    GraphGenerationEvent,
    ProcessingCompletedEvent
)
from ..utils.performance_utils import measure_async_execution_time, track_memory_usage
from ..utils.validation_utils import validate_project_id, validate_file_info, validate_processing_config

logger = logging.getLogger(__name__)


class AIRAGOrchestrator:
    """
    Main orchestrator service that coordinates all AI RAG operations.
    
    This service provides a unified interface for document processing, graph generation,
    and knowledge extraction workflows.
    """
    
    def __init__(self):
        """Initialize the AI RAG orchestrator."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize core services
        self.registry_service = AIRAGRegistryService()
        self.document_service = DocumentService()
        self.embedding_service = EmbeddingService()
        self.retrieval_service = RetrievalService()
        self.generation_service = GenerationService()
        self.graph_metadata_service = AIRAGGraphMetadataService()
        
        # Initialize event bus
        self.event_bus = EventBus()
        
        # Processing configuration
        self.default_config = {
            'extract_entities': True,
            'build_graph': True,
            'chunk_size': 1000,
            'overlap': 100,
            'max_entities': 100,
            'quality_threshold': 0.8
        }
        
        self.logger.info("AI RAG Orchestrator initialized successfully")
    
    @measure_async_execution_time
    async def process_document(
        self,
        project_id: str,
        file_path: Union[str, Path],
        processing_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a single document through the complete AI RAG pipeline.
        
        Args:
            project_id: Project identifier
            file_path: Path to the document file
            processing_config: Processing configuration options
            metadata: Additional metadata for the document
            
        Returns:
            Dictionary containing processing results and metadata
        """
        # Validate inputs
        if not validate_project_id(project_id):
            raise ValueError(f"Invalid project ID: {project_id}")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")
        
        # Merge with default configuration
        config = {**self.default_config, **(processing_config or {})}
        if not validate_processing_config(config):
            raise ValueError("Invalid processing configuration")
        
        # Initialize result tracking
        result = {
            'project_id': project_id,
            'file_path': str(file_path),
            'processing_start': datetime.now().isoformat(),
            'status': 'processing',
            'steps_completed': [],
            'errors': [],
            'metadata': metadata or {}
        }
        
        try:
            self.logger.info(f"Starting document processing for {file_path}")
            
            # Step 1: Document processing and text extraction
            with track_memory_usage("document_processing"):
                doc_result = await self.document_service.process_document(
                    project_id=project_id,
                    file_path=file_path,
                    config=config
                )
                result['document_processing'] = doc_result
                result['steps_completed'].append('document_processing')
                
                # Publish document processing event
                await self.event_bus.publish(DocumentProcessingEvent(
                    project_id=project_id,
                    file_path=str(file_path),
                    status='completed',
                    metadata=doc_result
                ))
            
            # Step 2: Entity extraction (if enabled)
            if config.get('extract_entities', False):
                with track_memory_usage("entity_extraction"):
                    entities_result = await self._extract_entities(
                        project_id=project_id,
                        document_data=doc_result,
                        config=config
                    )
                    result['entity_extraction'] = entities_result
                    result['steps_completed'].append('entity_extraction')
            
            # Step 3: Graph generation (if enabled)
            if config.get('build_graph', False):
                with track_memory_usage("graph_generation"):
                    graph_result = await self._generate_knowledge_graph(
                        project_id=project_id,
                        document_data=doc_result,
                        entities_data=result.get('entity_extraction'),
                        config=config
                    )
                    result['graph_generation'] = graph_result
                    result['steps_completed'].append('graph_generation')
                    
                    # Publish graph generation event
                    await self.event_bus.publish(GraphGenerationEvent(
                        project_id=project_id,
                        graph_id=graph_result.get('graph_id'),
                        status='completed',
                        metadata=graph_result
                    ))
            
            # Step 4: Update registry and metadata
            await self._update_registry_and_metadata(
                project_id=project_id,
                file_path=file_path,
                result=result
            )
            
            # Mark as completed
            result['status'] = 'completed'
            result['processing_end'] = datetime.now().isoformat()
            
            # Publish completion event
            await self.event_bus.publish(ProcessingCompletedEvent(
                project_id=project_id,
                file_path=str(file_path),
                status='completed',
                metadata=result
            ))
            
            self.logger.info(f"Document processing completed successfully for {file_path}")
            
        except Exception as e:
            self.logger.error(f"Document processing failed for {file_path}: {e}")
            result['status'] = 'failed'
            result['processing_end'] = datetime.now().isoformat()
            result['errors'].append(str(e))
            
            # Publish error event
            await self.event_bus.publish(ProcessingCompletedEvent(
                project_id=project_id,
                file_path=str(file_path),
                status='failed',
                metadata={'error': str(e)}
            ))
        
        return result
    
    async def _extract_entities(
        self,
        project_id: str,
        document_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract entities from processed document data."""
        try:
            # This would integrate with the entity extraction service
            # For now, return a placeholder
            return {
                'entities_found': 0,
                'entity_types': [],
                'extraction_method': 'placeholder',
                'confidence_score': 0.0
            }
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}")
            raise
    
    async def _generate_knowledge_graph(
        self,
        project_id: str,
        document_data: Dict[str, Any],
        entities_data: Optional[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate knowledge graph from document and entity data."""
        try:
            # This would integrate with the graph generation service
            # For now, return a placeholder
            graph_id = f"graph_{project_id}_{int(datetime.now().timestamp())}"
            
            return {
                'graph_id': graph_id,
                'nodes_count': 0,
                'edges_count': 0,
                'graph_type': 'document',
                'generation_method': 'placeholder',
                'quality_score': 0.0
            }
        except Exception as e:
            self.logger.error(f"Graph generation failed: {e}")
            raise
    
    async def _update_registry_and_metadata(
        self,
        project_id: str,
        file_path: Path,
        result: Dict[str, Any]
    ) -> None:
        """Update registry and metadata with processing results."""
        try:
            # Update processing registry
            await self.registry_service.update_processing_status(
                project_id=project_id,
                file_path=str(file_path),
                status=result['status'],
                metadata=result
            )
            
            # Update graph metadata if graph was generated
            if 'graph_generation' in result:
                graph_data = result['graph_generation']
                await self.graph_metadata_service.create_graph_metadata(
                    graph_id=graph_data['graph_id'],
                    project_id=project_id,
                    graph_type=graph_data['graph_type'],
                    metadata=graph_data
                )
                
        except Exception as e:
            self.logger.error(f"Failed to update registry and metadata: {e}")
            # Don't raise - this is not critical for the main processing flow
    
    @measure_async_execution_time
    async def process_project(
        self,
        project_id: str,
        project_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process all documents in a project.
        
        Args:
            project_id: Project identifier
            project_config: Project-specific configuration
            
        Returns:
            Dictionary containing project processing results
        """
        if not validate_project_id(project_id):
            raise ValueError(f"Invalid project ID: {project_id}")
        
        self.logger.info(f"Starting project processing for {project_id}")
        
        # Get project files
        project_files = await self.registry_service.get_project_files(project_id)
        
        if not project_files:
            self.logger.warning(f"No files found for project {project_id}")
            return {
                'project_id': project_id,
                'status': 'no_files',
                'files_processed': 0,
                'total_files': 0
            }
        
        # Process each file
        results = []
        successful_files = 0
        failed_files = 0
        
        for file_info in project_files:
            try:
                file_result = await self.process_document(
                    project_id=project_id,
                    file_path=file_info['file_path'],
                    processing_config=project_config,
                    metadata=file_info
                )
                results.append(file_result)
                
                if file_result['status'] == 'completed':
                    successful_files += 1
                else:
                    failed_files += 1
                    
            except Exception as e:
                self.logger.error(f"Failed to process file {file_info['file_path']}: {e}")
                failed_files += 1
                results.append({
                    'project_id': project_id,
                    'file_path': file_info['file_path'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        project_result = {
            'project_id': project_id,
            'status': 'completed' if failed_files == 0 else 'completed_with_errors',
            'total_files': len(project_files),
            'successful_files': successful_files,
            'failed_files': failed_files,
            'file_results': results,
            'processing_start': datetime.now().isoformat(),
            'processing_end': datetime.now().isoformat()
        }
        
        self.logger.info(f"Project processing completed for {project_id}: {successful_files}/{len(project_files)} files successful")
        
        return project_result
    
    async def get_processing_status(
        self,
        project_id: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Get processing status for projects or specific files.
        
        Args:
            project_id: Optional project identifier
            file_path: Optional specific file path
            
        Returns:
            Dictionary containing processing status information
        """
        try:
            if file_path:
                # Get status for specific file
                return await self.registry_service.get_file_processing_status(str(file_path))
            elif project_id:
                # Get status for project
                return await self.registry_service.get_project_processing_status(project_id)
            else:
                # Get overall system status
                return await self.registry_service.get_system_status()
                
        except Exception as e:
            self.logger.error(f"Failed to get processing status: {e}")
            raise
    
    async def get_performance_metrics(
        self,
        project_id: Optional[str] = None,
        time_range: Optional[Dict[str, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for processing operations.
        
        Args:
            project_id: Optional project identifier
            time_range: Optional time range for metrics
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            return await self.registry_service.get_performance_metrics(
                project_id=project_id,
                time_range=time_range
            )
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            raise
    
    async def cleanup_project_data(
        self,
        project_id: str,
        cleanup_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Clean up project data and temporary files.
        
        Args:
            project_id: Project identifier
            cleanup_config: Cleanup configuration options
            
        Returns:
            Dictionary containing cleanup results
        """
        if not validate_project_id(project_id):
            raise ValueError(f"Invalid project ID: {project_id}")
        
        self.logger.info(f"Starting cleanup for project {project_id}")
        
        try:
            # This would integrate with cleanup services
            # For now, return a placeholder
            return {
                'project_id': project_id,
                'status': 'completed',
                'files_cleaned': 0,
                'storage_freed_mb': 0,
                'cleanup_method': 'placeholder'
            }
            
        except Exception as e:
            self.logger.error(f"Project cleanup failed: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the orchestrator and cleanup resources."""
        self.logger.info("Shutting down AI RAG Orchestrator")
        
        try:
            # Stop event bus
            await self.event_bus.shutdown()
            
            # Cleanup other resources as needed
            self.logger.info("AI RAG Orchestrator shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


