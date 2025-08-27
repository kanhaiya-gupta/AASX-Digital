"""
Processor Integration Service for AI RAG Graph Generation.

This service connects the existing AI RAG document processors to the new graph generation pipeline,
enabling automatic knowledge graph creation from processed documents.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from ..models.ai_rag_graph_metadata import AIRagGraphMetadata
from ..core.ai_rag_graph_metadata_service import AIRagGraphMetadataService
from .entity_extractor import EntityExtractor
from .relationship_discoverer import RelationshipDiscoverer
from .graph_builder import GraphBuilder
from .graph_validator import GraphValidator
from .graph_exporter import GraphExporter
from ..kg_integration.graph_transfer_service import GraphTransferService
from ..kg_integration.graph_sync_manager import GraphSyncManager
from ..kg_integration.graph_lifecycle import GraphLifecycleManager


class ProcessorIntegrationService:
    """
    Service that integrates existing AI RAG processors with the new graph generation pipeline.
    
    This service:
    1. Monitors processor outputs for document processing completion
    2. Triggers automatic graph generation when documents are processed
    3. Manages the complete pipeline from document → entities → relationships → graph → KG Neo4j
    4. Provides configuration options for different integration modes
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the processor integration service.
        
        Args:
            config: Configuration dictionary with integration settings
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize graph generation components
        self.entity_extractor = EntityExtractor(self.config.get("entity_extraction", {}))
        self.relationship_discoverer = RelationshipDiscoverer(self.config.get("relationship_discovery", {}))
        self.graph_builder = GraphBuilder(self.config.get("graph_building", {}))
        self.graph_validator = GraphValidator(self.config.get("graph_validation", {}))
        self.graph_exporter = GraphExporter(self.config.get("graph_export", {}))
        
        # Initialize KG integration components
        self.graph_transfer_service = GraphTransferService(self.config.get("transfer", {}))
        self.graph_sync_manager = GraphSyncManager(self.config.get("sync", {}))
        self.graph_lifecycle_manager = GraphLifecycleManager(self.config.get("lifecycle", {}))
        
        # Initialize metadata service for tracking
        self.metadata_service = AIRagGraphMetadataService()
        
        # Integration state
        self.integration_active = False
        self.processing_queue = asyncio.Queue()
        self.processing_stats = {
            "documents_processed": 0,
            "graphs_generated": 0,
            "graphs_transferred": 0,
            "errors": 0
        }
        
        # Event handlers for different processor types
        self.processor_handlers = {
            "document": self._handle_document_processing,
            "spreadsheet": self._handle_spreadsheet_processing,
            "code": self._handle_code_processing,
            "image": self._handle_image_processing,
            "cad": self._handle_cad_processing,
            "structured_data": self._handle_structured_data_processing,
            "graph_data": self._handle_graph_data_processing
        }
    
    async def start_integration_service(self) -> None:
        """Start the integration service and begin monitoring processor outputs."""
        try:
            self.logger.info("🚀 Starting AI RAG Processor Integration Service")
            
            # Start lifecycle manager
            await self.graph_lifecycle_manager.start_lifecycle_manager()
            
            # Start sync manager
            await self.graph_sync_manager.start_sync_manager()
            
            # Start processing loop
            self.integration_active = True
            asyncio.create_task(self._processing_loop())
            
            self.logger.info("✅ AI RAG Processor Integration Service started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start integration service: {e}")
            raise
    
    async def stop_integration_service(self) -> None:
        """Stop the integration service and cleanup resources."""
        try:
            self.logger.info("🛑 Stopping AI RAG Processor Integration Service")
            
            self.integration_active = False
            
            # Stop lifecycle manager
            if hasattr(self.graph_lifecycle_manager, 'stop_lifecycle_manager'):
                await self.graph_lifecycle_manager.stop_lifecycle_manager()
            
            # Stop sync manager
            if hasattr(self.graph_sync_manager, 'stop_sync_manager'):
                await self.graph_sync_manager.stop_sync_manager()
            
            self.logger.info("✅ AI RAG Processor Integration Service stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping integration service: {e}")
    
    async def integrate_processor_output(
        self,
        processor_type: str,
        project_id: str,
        file_info: Dict[str, Any],
        processing_result: Dict[str, Any],
        extracted_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Integrate processor output with graph generation pipeline.
        
        This is the main entry point for processors to trigger graph generation.
        
        Args:
            processor_type: Type of processor (document, spreadsheet, code, etc.)
            project_id: Project identifier
            file_info: File information from project manager
            processing_result: Result from processor execution
            extracted_content: Optional extracted text content for graph generation
            
        Returns:
            Integration result with graph generation status
        """
        try:
            self.logger.info(f"🔄 Integrating {processor_type} processor output for {file_info.get('filename', 'unknown')}")
            
            # Check if processing was successful
            if processing_result.get('status') != 'success':
                self.logger.info(f"⏭️ Skipping graph generation for failed processing: {processing_result.get('reason', 'unknown error')}")
                return {
                    'status': 'skipped',
                    'reason': 'Processing failed',
                    'processing_result': processing_result
                }
            
            # Get the appropriate handler for this processor type
            handler = self.processor_handlers.get(processor_type)
            if not handler:
                self.logger.warning(f"⚠️ No handler found for processor type: {processor_type}")
                return {
                    'status': 'error',
                    'reason': f'No handler for processor type: {processor_type}'
                }
            
            # Process with the appropriate handler
            result = await handler(project_id, file_info, processing_result, extracted_content)
            
            # Update statistics
            self.processing_stats["documents_processed"] += 1
            if result.get('status') == 'success':
                self.processing_stats["graphs_generated"] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error integrating processor output: {e}")
            self.processing_stats["errors"] += 1
            return {
                'status': 'error',
                'reason': str(e)
            }
    
    async def _handle_document_processing(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        processing_result: Dict[str, Any],
        extracted_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle document processor output and trigger graph generation."""
        try:
            # Extract content from processing result if not provided
            if not extracted_content:
                extracted_content = processing_result.get('content_preview', '')
            
            if not extracted_content or len(extracted_content.strip()) < 50:
                return {
                    'status': 'skipped',
                    'reason': 'Insufficient content for graph generation'
                }
            
            # Generate graph from document content
            return await self._generate_graph_from_content(
                project_id=project_id,
                file_info=file_info,
                content=extracted_content,
                content_type="document",
                source_processor="document_processor"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error handling document processing: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _handle_spreadsheet_processing(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        processing_result: Dict[str, Any],
        extracted_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle spreadsheet processor output and trigger graph generation."""
        try:
            # Extract structured data from spreadsheet
            structured_data = processing_result.get('structured_data', {})
            if not structured_data:
                return {
                    'status': 'skipped',
                    'reason': 'No structured data available for graph generation'
                }
            
            # Convert structured data to content for graph generation
            content = self._convert_structured_data_to_content(structured_data)
            
            return await self._generate_graph_from_content(
                project_id=project_id,
                file_info=file_info,
                content=content,
                content_type="spreadsheet",
                source_processor="spreadsheet_processor"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error handling spreadsheet processing: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _handle_code_processing(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        processing_result: Dict[str, Any],
        extracted_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle code processor output and trigger graph generation."""
        try:
            # Extract code structure and dependencies
            code_structure = processing_result.get('code_structure', {})
            if not code_structure:
                return {
                    'status': 'skipped',
                    'reason': 'No code structure available for graph generation'
                }
            
            # Convert code structure to content for graph generation
            content = self._convert_code_structure_to_content(code_structure)
            
            return await self._generate_graph_from_content(
                project_id=project_id,
                file_info=file_info,
                content=content,
                content_type="code",
                source_processor="code_processor"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error handling code processing: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _handle_image_processing(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        processing_result: Dict[str, Any],
        extracted_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle image processor output and trigger graph generation."""
        try:
            # Extract image analysis results
            image_analysis = processing_result.get('image_analysis', {})
            if not image_analysis:
                return {
                    'status': 'skipped',
                    'reason': 'No image analysis available for graph generation'
                }
            
            # Convert image analysis to content for graph generation
            content = self._convert_image_analysis_to_content(image_analysis)
            
            return await self._generate_graph_from_content(
                project_id=project_id,
                file_info=file_info,
                content=content,
                content_type="image",
                source_processor="image_processor"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error handling image processing: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _handle_cad_processing(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        processing_result: Dict[str, Any],
        extracted_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle CAD processor output and trigger graph generation."""
        try:
            # Extract CAD model information
            cad_model_info = processing_result.get('cad_model_info', {})
            if not cad_model_info:
                return {
                    'status': 'skipped',
                    'reason': 'No CAD model information available for graph generation'
                }
            
            # Convert CAD model info to content for graph generation
            content = self._convert_cad_model_to_content(cad_model_info)
            
            return await self._generate_graph_from_content(
                project_id=project_id,
                file_info=file_info,
                content=content,
                content_type="cad",
                source_processor="cad_processor"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error handling CAD processing: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _handle_structured_data_processing(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        processing_result: Dict[str, Any],
        extracted_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle structured data processor output and trigger graph generation."""
        try:
            # Extract structured data
            structured_data = processing_result.get('structured_data', {})
            if not structured_data:
                return {
                    'status': 'skipped',
                    'reason': 'No structured data available for graph generation'
                }
            
            # Convert structured data to content for graph generation
            content = self._convert_structured_data_to_content(structured_data)
            
            return await self._generate_graph_from_content(
                project_id=project_id,
                file_info=file_info,
                content=content,
                content_type="structured_data",
                source_processor="structured_data_processor"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error handling structured data processing: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _handle_graph_data_processing(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        processing_result: Dict[str, Any],
        extracted_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle graph data processor output and trigger graph generation."""
        try:
            # Extract existing graph data
            graph_data = processing_result.get('graph_data', {})
            if not graph_data:
                return {
                    'status': 'skipped',
                    'reason': 'No graph data available for processing'
                }
            
            # For graph data, we might want to enhance or merge with existing graphs
            return await self._enhance_existing_graph(
                project_id=project_id,
                file_info=file_info,
                existing_graph_data=graph_data
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error handling graph data processing: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _generate_graph_from_content(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        content: str,
        content_type: str,
        source_processor: str
    ) -> Dict[str, Any]:
        """
        Generate a complete knowledge graph from extracted content.
        
        This is the core method that orchestrates the entire graph generation pipeline.
        """
        try:
            self.logger.info(f"🎯 Starting graph generation for {file_info.get('filename', 'unknown')}")
            
            # Step 1: Extract entities from content
            entities = await self.entity_extractor.extract_entities(content)
            if not entities:
                return {
                    'status': 'skipped',
                    'reason': 'No entities extracted from content'
                }
            
            self.logger.info(f"📊 Extracted {len(entities)} entities from content")
            
            # Step 2: Discover relationships between entities
            relationships = await self.relationship_discoverer.discover_relationships(entities, content)
            if not relationships:
                return {
                    'status': 'skipped',
                    'reason': 'No relationships discovered between entities'
                }
            
            self.logger.info(f"🔗 Discovered {len(relationships)} relationships between entities")
            
            # Step 3: Build the complete graph structure
            graph_structure = await self.graph_builder.build_graph(
                entities=entities,
                relationships=relationships,
                metadata={
                    'project_id': project_id,
                    'file_id': file_info.get('file_id'),
                    'filename': file_info.get('filename'),
                    'content_type': content_type,
                    'source_processor': source_processor,
                    'generation_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            if not graph_structure:
                return {
                    'status': 'error',
                    'reason': 'Failed to build graph structure'
                }
            
            self.logger.info(f"🏗️ Built graph structure with {len(graph_structure.nodes)} nodes and {len(graph_structure.edges)} edges")
            
            # Step 4: Validate the graph
            validation_result = await self.graph_validator.validate_graph(graph_structure)
            if not validation_result.get('is_valid', False):
                self.logger.warning(f"⚠️ Graph validation issues: {validation_result.get('issues', [])}")
                # Continue with warnings rather than failing completely
            
            # Step 5: Export the graph to various formats
            export_formats = ['cypher', 'graphml', 'json_ld']
            exported_graphs = {}
            
            for format_type in export_formats:
                try:
                    exported_content = await self.graph_exporter.export_graph(graph_structure, format_type)
                    if exported_content:
                        exported_graphs[format_type] = exported_content
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to export to {format_type}: {e}")
            
            if not exported_graphs:
                return {
                    'status': 'error',
                    'reason': 'Failed to export graph to any format'
                }
            
            self.logger.info(f"📤 Exported graph to {len(exported_graphs)} formats: {list(exported_graphs.keys())}")
            
            # Step 6: Create graph metadata record
            graph_metadata = await self._create_graph_metadata(
                project_id=project_id,
                file_info=file_info,
                graph_structure=graph_structure,
                validation_result=validation_result,
                export_formats=list(exported_graphs.keys()),
                source_processor=source_processor
            )
            
            # Step 7: Transfer to KG Neo4j
            transfer_result = await self._transfer_graph_to_kg_neo4j(
                graph_structure=graph_structure,
                graph_metadata=graph_metadata,
                exported_graphs=exported_graphs
            )
            
            if transfer_result.get('status') == 'success':
                self.processing_stats["graphs_transferred"] += 1
            
            # Step 8: Start lifecycle management
            lifecycle_result = await self._start_graph_lifecycle(
                graph_structure=graph_structure,
                graph_metadata=graph_metadata
            )
            
            return {
                'status': 'success',
                'graph_id': graph_metadata.graph_id,
                'entities_extracted': len(entities),
                'relationships_discovered': len(relationships),
                'graph_nodes': len(graph_structure.nodes),
                'graph_edges': len(graph_structure.edges),
                'export_formats': list(exported_graphs.keys()),
                'transfer_status': transfer_result.get('status'),
                'lifecycle_status': lifecycle_result.get('status'),
                'metadata': {
                    'graph_id': graph_metadata.graph_id,
                    'quality_score': graph_metadata.quality_score,
                    'processing_status': graph_metadata.processing_status
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error generating graph from content: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _create_graph_metadata(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        graph_structure: Any,
        validation_result: Dict[str, Any],
        export_formats: List[str],
        source_processor: str
    ) -> AIRagGraphMetadata:
        """Create and store graph metadata record."""
        try:
            # Create graph metadata
            graph_metadata = AIRagGraphMetadata(
                project_id=project_id,
                org_id=file_info.get('org_id', 'default'),
                dept_id=file_info.get('dept_id', 'default'),
                graph_name=f"Graph_{file_info.get('filename', 'unknown')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                processing_status="completed",
                quality_score=validation_result.get('quality_score', 0.8),
                output_directory=f"output/graphs/ai_rag/{project_id}/",
                source_file=file_info.get('filename'),
                source_processor=source_processor,
                graph_type="knowledge_graph",
                node_count=len(graph_structure.nodes),
                edge_count=len(graph_structure.edges),
                entity_count=len([n for n in graph_structure.nodes if n.node_type == 'entity']),
                relationship_count=len([e for e in graph_structure.edges if e.edge_type == 'relationship']),
                export_formats=export_formats,
                validation_status=validation_result.get('is_valid', False),
                validation_issues=validation_result.get('issues', []),
                processing_notes=[
                    f"Generated from {source_processor}",
                    f"Content type: {file_info.get('content_type', 'unknown')}",
                    f"Validation score: {validation_result.get('quality_score', 0.8)}"
                ]
            )
            
            # Save to database
            saved_metadata = await self.metadata_service.create_graph_metadata(graph_metadata)
            
            self.logger.info(f"💾 Saved graph metadata with ID: {saved_metadata.graph_id}")
            return saved_metadata
            
        except Exception as e:
            self.logger.error(f"❌ Error creating graph metadata: {e}")
            raise
    
    async def _transfer_graph_to_kg_neo4j(
        self,
        graph_structure: Any,
        graph_metadata: AIRagGraphMetadata,
        exported_graphs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transfer the generated graph to KG Neo4j."""
        try:
            self.logger.info(f"🚀 Transferring graph {graph_metadata.graph_id} to KG Neo4j")
            
            # Use the graph transfer service
            transfer_result = await self.graph_transfer_service.transfer_graph(
                graph_structure=graph_structure,
                graph_metadata=graph_metadata,
                transfer_mode="automatic",
                priority="normal"
            )
            
            if transfer_result.get('status') == 'success':
                self.logger.info(f"✅ Successfully transferred graph {graph_metadata.graph_id} to KG Neo4j")
            else:
                self.logger.warning(f"⚠️ Graph transfer had issues: {transfer_result.get('message', 'unknown')}")
            
            return transfer_result
            
        except Exception as e:
            self.logger.error(f"❌ Error transferring graph to KG Neo4j: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _start_graph_lifecycle(
        self,
        graph_structure: Any,
        graph_metadata: AIRagGraphMetadata
    ) -> Dict[str, Any]:
        """Start lifecycle management for the generated graph."""
        try:
            self.logger.info(f"🔄 Starting lifecycle management for graph {graph_metadata.graph_id}")
            
            # Start lifecycle with standard workflow
            lifecycle_result = await self.graph_lifecycle_manager.create_graph_lifecycle(
                graph_id=graph_metadata.graph_id,
                graph_structure=graph_structure,
                graph_metadata=graph_metadata,
                workflow_name="standard"
            )
            
            if lifecycle_result.get('status') == 'success':
                self.logger.info(f"✅ Started lifecycle management for graph {graph_metadata.graph_id}")
            else:
                self.logger.warning(f"⚠️ Lifecycle start had issues: {lifecycle_result.get('message', 'unknown')}")
            
            return lifecycle_result
            
        except Exception as e:
            self.logger.error(f"❌ Error starting graph lifecycle: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _enhance_existing_graph(
        self,
        project_id: str,
        file_info: Dict[str, Any],
        existing_graph_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance an existing graph with new data."""
        try:
            self.logger.info(f"🔄 Enhancing existing graph for {file_info.get('filename', 'unknown')}")
            
            # This would involve merging new data with existing graph structures
            # For now, return a placeholder implementation
            return {
                'status': 'success',
                'message': 'Graph enhancement not yet implemented',
                'graph_id': existing_graph_data.get('graph_id', 'unknown')
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error enhancing existing graph: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def _convert_structured_data_to_content(self, structured_data: Dict[str, Any]) -> str:
        """Convert structured data to text content for graph generation."""
        try:
            content_parts = []
            
            # Extract key-value pairs
            for key, value in structured_data.items():
                if isinstance(value, (str, int, float)):
                    content_parts.append(f"{key}: {value}")
                elif isinstance(value, list):
                    content_parts.append(f"{key}: {', '.join(map(str, value[:10]))}")  # Limit to first 10 items
                elif isinstance(value, dict):
                    content_parts.append(f"{key}: {json.dumps(value, default=str)[:200]}...")
            
            return "\n".join(content_parts)
            
        except Exception as e:
            self.logger.error(f"❌ Error converting structured data to content: {e}")
            return str(structured_data)
    
    def _convert_code_structure_to_content(self, code_structure: Dict[str, Any]) -> str:
        """Convert code structure to text content for graph generation."""
        try:
            content_parts = []
            
            # Extract code components
            if 'classes' in code_structure:
                content_parts.append(f"Classes: {', '.join(code_structure['classes'])}")
            
            if 'functions' in code_structure:
                content_parts.append(f"Functions: {', '.join(code_structure['functions'])}")
            
            if 'dependencies' in code_structure:
                content_parts.append(f"Dependencies: {', '.join(code_structure['dependencies'])}")
            
            if 'imports' in code_structure:
                content_parts.append(f"Imports: {', '.join(code_structure['imports'])}")
            
            if 'language' in code_structure:
                content_parts.append(f"Programming Language: {code_structure['language']}")
            
            return "\n".join(content_parts)
            
        except Exception as e:
            self.logger.error(f"❌ Error converting code structure to content: {e}")
            return str(code_structure)
    
    def _convert_image_analysis_to_content(self, image_analysis: Dict[str, Any]) -> str:
        """Convert image analysis to text content for graph generation."""
        try:
            content_parts = []
            
            # Extract image properties
            if 'objects_detected' in image_analysis:
                content_parts.append(f"Objects detected: {', '.join(image_analysis['objects_detected'])}")
            
            if 'text_content' in image_analysis:
                content_parts.append(f"Text content: {image_analysis['text_content']}")
            
            if 'colors' in image_analysis:
                content_parts.append(f"Dominant colors: {', '.join(image_analysis['colors'])}")
            
            if 'image_type' in image_analysis:
                content_parts.append(f"Image type: {image_analysis['image_type']}")
            
            if 'dimensions' in image_analysis:
                dims = image_analysis['dimensions']
                content_parts.append(f"Dimensions: {dims.get('width', 'unknown')}x{dims.get('height', 'unknown')}")
            
            return "\n".join(content_parts)
            
        except Exception as e:
            self.logger.error(f"❌ Error converting image analysis to content: {e}")
            return str(image_analysis)
    
    def _convert_cad_model_to_content(self, cad_model_info: Dict[str, Any]) -> str:
        """Convert CAD model information to text content for graph generation."""
        try:
            content_parts = []
            
            # Extract CAD model properties
            if 'model_type' in cad_model_info:
                content_parts.append(f"Model type: {cad_model_info['model_type']}")
            
            if 'components' in cad_model_info:
                content_parts.append(f"Components: {', '.join(cad_model_info['components'])}")
            
            if 'materials' in cad_model_info:
                content_parts.append(f"Materials: {', '.join(cad_model_info['materials'])}")
            
            if 'dimensions' in cad_model_info:
                dims = cad_model_info['dimensions']
                content_parts.append(f"Dimensions: {dims.get('length', 'unknown')} x {dims.get('width', 'unknown')} x {dims.get('height', 'unknown')}")
            
            if 'file_format' in cad_model_info:
                content_parts.append(f"File format: {cad_model_info['file_format']}")
            
            return "\n".join(content_parts)
            
        except Exception as e:
            self.logger.error(f"❌ Error converting CAD model to content: {e}")
            return str(cad_model_info)
    
    async def _processing_loop(self) -> None:
        """Main processing loop for handling queued items."""
        while self.integration_active:
            try:
                # Process items from queue
                if not self.processing_queue.empty():
                    item = await self.processing_queue.get()
                    await self._process_queued_item(item)
                    self.processing_queue.task_done()
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"❌ Error in processing loop: {e}")
                await asyncio.sleep(1)  # Longer delay on error
    
    async def _process_queued_item(self, item: Dict[str, Any]) -> None:
        """Process a single queued item."""
        try:
            # Process the item based on its type
            processor_type = item.get('processor_type')
            project_id = item.get('project_id')
            file_info = item.get('file_info')
            processing_result = item.get('processing_result')
            
            await self.integrate_processor_output(
                processor_type=processor_type,
                project_id=project_id,
                file_info=file_info,
                processing_result=processing_result
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error processing queued item: {e}")
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get current integration statistics."""
        return {
            **self.processing_stats,
            'integration_active': self.integration_active,
            'queue_size': self.processing_queue.qsize() if hasattr(self.processing_queue, 'qsize') else 0
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the integration service."""
        return {
            "entity_extraction": {
                "min_confidence": 0.7,
                "max_entities": 100,
                "entity_types": ["person", "organization", "location", "concept", "technology"]
            },
            "relationship_discovery": {
                "min_confidence": 0.6,
                "max_relationships": 200,
                "relationship_types": ["is_a", "part_of", "located_in", "uses", "creates"]
            },
            "graph_building": {
                "max_nodes": 1000,
                "max_edges": 2000,
                "enable_cycles": True,
                "enable_loops": False
            },
            "graph_validation": {
                "min_quality_score": 0.5,
                "max_validation_time": 30,
                "enable_schema_validation": True
            },
            "graph_export": {
                "formats": ["cypher", "graphml", "json_ld"],
                "include_metadata": True,
                "enable_compression": False
            },
            "transfer": {
                "api_endpoint": "http://localhost:7474/api",
                "timeout": 30,
                "retry_attempts": 3
            },
            "sync": {
                "sync_interval": 300,
                "conflict_resolution": "ai_rag_wins",
                "enable_auto_sync": True
            },
            "lifecycle": {
                "stages": ["created", "processing", "validated", "published", "active"],
                "auto_transitions": True,
                "cleanup_interval": 3600
            }
        }


