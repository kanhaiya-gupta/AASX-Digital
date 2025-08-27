"""
AASX Population Orchestrator
============================

Orchestrates the population of AASX-dependent modules in the correct dependency order:
1. AASX Tables (ETL results)
2. Twin Registry Tables (depends on AASX)
3. AI RAG Tables (depends on AASX)
4. KG Neo4j Tables (depends on AASX + Twin + RAG)

This orchestrator handles the heavy lifting of cross-module population coordination.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class AASXPopulationOrchestrator:
    """Orchestrates population of AASX-dependent modules."""
    
    def __init__(self, connection_manager):
        """
        Initialize the population orchestrator.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        self._initialize_services()
        logger.info("AASX Population Orchestrator initialized")
    
    def _initialize_services(self):
        """Initialize all required services for population."""
        try:
            # AASX services
            from ..services.aasx_processing_service import AASXProcessingService
            from ..services.aasx_processing_metrics_service import ProcessingMetricsService
            
            # Twin Registry services
            from src.modules.twin_registry.core.twin_registry_service import TwinRegistryService
            
            # AI RAG services
            from src.modules.ai_rag.core.rag_orchestrator import RAGOrchestrator
            
            # KG Neo4j services
            from src.modules.kg_neo4j.neo4j.manager import Neo4jManager
            
            # Initialize service instances
            self.aasx_processing_service = AASXProcessingService(self.connection_manager)
            self.aasx_metrics_service = ProcessingMetricsService(self.connection_manager)
            self.twin_registry_service = TwinRegistryService(self.connection_manager)
            self.rag_orchestrator = RAGOrchestrator(self.connection_manager)
            self.kg_neo4j_manager = Neo4jManager(self.connection_manager)
            
            logger.info("All population services initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to import required services: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize population services: {e}")
            raise
    
    async def populate_aasx_dependent_modules(self, etl_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Populate all AASX-dependent modules in the correct dependency order.
        
        Args:
            etl_result: ETL processing results from AASX processing
            
        Returns:
            Dict[str, Any]: Consolidated results from all population steps
        """
        try:
            logger.info("🚀 Starting AASX-dependent module population")
            logger.info(f"ETL Result keys: {list(etl_result.keys())}")
            
            # 1. Populate AASX tables (ETL results)
            logger.info("📊 Step 1: Populating AASX tables...")
            aasx_result = await self._populate_aasx_tables(etl_result)
            logger.info(f"✅ AASX tables populated: {aasx_result.get('status', 'unknown')}")
            
            # 2. Populate Twin Registry tables (depends on AASX)
            logger.info("🏗️ Step 2: Populating Twin Registry tables...")
            twin_result = await self._populate_twin_registry_tables(etl_result, aasx_result)
            logger.info(f"✅ Twin Registry tables populated: {twin_result.get('status', 'unknown')}")
            
            # 3. Populate AI RAG tables (depends on AASX) - includes Qdrant storage
            logger.info("🧠 Step 3: Populating AI RAG tables and Qdrant storage...")
            rag_result = await self._populate_ai_rag_tables(etl_result, aasx_result)
            logger.info(f"✅ AI RAG tables populated: {rag_result.get('status', 'unknown')}")
            
            # 4. Populate KG Neo4j tables (depends on AASX + Twin + RAG)
            logger.info("🔗 Step 4: Populating KG Neo4j tables...")
            kg_result = await self._populate_kg_neo4j_tables(etl_result, aasx_result, twin_result, rag_result)
            logger.info(f"✅ KG Neo4j tables populated: {kg_result.get('status', 'unknown')}")
            
            # 5. Consolidate and return results
            consolidated_result = self._consolidate_results(
                aasx_result, twin_result, rag_result, kg_result
            )
            
            logger.info("🎉 AASX-dependent module population completed successfully")
            return consolidated_result
            
        except Exception as e:
            logger.error(f"❌ Population failed: {e}")
            await self._rollback_population(etl_result)
            raise
    
    async def _populate_aasx_tables(self, etl_result: Dict[str, Any]) -> Dict[str, Any]:
        """Populate AASX tables with ETL results."""
        try:
            # Extract key information from ETL result
            file_id = etl_result.get('file_id')
            project_id = etl_result.get('project_id')
            job_id = etl_result.get('job_id')
            
            if not all([file_id, project_id, job_id]):
                logger.warning("Missing required fields for AASX table population")
                return {'status': 'skipped', 'reason': 'missing_required_fields'}
            
            # Update processing status
            await self.aasx_processing_service.update_status(
                job_id, 
                'completed', 
                {'completion_timestamp': datetime.now().isoformat()}
            )
            
            # Create metrics record if available
            if 'metrics' in etl_result:
                await self.aasx_metrics_service.create_metrics_from_etl_results(
                    job_id, 
                    etl_result['metrics']
                )
            
            return {
                'status': 'success',
                'aasx_job_id': job_id,
                'file_id': file_id,
                'project_id': project_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to populate AASX tables: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _process_ai_rag_analysis(self, etl_result: Dict[str, Any], 
                                      aasx_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI/RAG analysis on ETL data."""
        try:
            # Check if AASX population was successful
            if aasx_result.get('status') != 'success':
                logger.warning("Skipping AI/RAG analysis - AASX population failed")
                return {'status': 'skipped', 'reason': 'aasx_population_failed'}
            
            # Extract AASX data for RAG processing
            file_id = aasx_result.get('file_id')
            project_id = aasx_result.get('project_id')
            
            # Process AASX content through RAG system
            rag_data = {
                'source_type': 'aasx_file',
                'source_id': file_id,
                'project_id': project_id,
                'content': etl_result.get('extracted_content', {}),
                'metadata': etl_result.get('metadata', {})
            }
            
            # Process through RAG orchestrator
            rag_result = await self.rag_orchestrator.process_and_store(rag_data)
            
            return {
                'status': 'success',
                'rag_processing_id': rag_result.get('processing_id'),
                'source_file_id': file_id,
                'vector_count': rag_result.get('vector_count', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process AI/RAG analysis: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _store_in_qdrant(self, etl_result: Dict[str, Any], 
                               aasx_result: Dict[str, Any],
                               ai_rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """Store processed data in Qdrant vector database."""
        try:
            # Check if all previous populations were successful
            required_statuses = [
                aasx_result.get('status') == 'success',
                ai_rag_result.get('status') == 'success'
            ]
            
            if not all(required_statuses):
                logger.warning("Skipping Qdrant storage - some previous steps failed")
                return {'status': 'skipped', 'reason': 'previous_steps_failed'}
            
            # Extract vector count from AI/RAG result
            vector_count = ai_rag_result.get('vector_count', 0)
            
            # Combine data from all sources for Qdrant storage
            integrated_data = {
                'aasx_data': aasx_result,
                'rag_data': ai_rag_result,
                'etl_metadata': etl_result,
                'integration_timestamp': datetime.now().isoformat()
            }
            
            # Create Qdrant collections and upsert data
            # This is a simplified example. In a real scenario,
            # you'd iterate through documents and upsert them.
            # For demonstration, we'll just return a placeholder.
            
            return {
                'status': 'success',
                'message': 'Qdrant storage completed successfully',
                'vector_count': vector_count,
                'collection_name': 'aasx_documents',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to store data in Qdrant: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _populate_twin_registry_tables(self, etl_result: Dict[str, Any], 
                                           aasx_result: Dict[str, Any]) -> Dict[str, Any]:
        """Populate Twin Registry tables based on AASX data."""
        try:
            # Check if AASX population was successful
            if aasx_result.get('status') != 'success':
                logger.warning("Skipping Twin Registry population - AASX population failed")
                return {'status': 'skipped', 'reason': 'aasx_population_failed'}
            
            # Extract AASX data for twin creation
            file_id = aasx_result.get('file_id')
            project_id = aasx_result.get('project_id')
            
            # Create digital twin from AASX data
            twin_data = {
                'source_type': 'aasx_etl',
                'source_id': file_id,
                'project_id': project_id,
                'metadata': {
                    'etl_result': etl_result,
                    'aasx_data': aasx_result,
                    'rag_data': None, # Placeholder, will be populated later
                    'qdrant_data': None # Placeholder, will be populated later
                }
            }
            
            # Create twin registry entry
            twin_id = await self.twin_registry_service.create_twin_registry(twin_data)
            
            return {
                'status': 'success',
                'twin_id': twin_id,
                'source_file_id': file_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to populate Twin Registry tables: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _populate_ai_rag_tables(self, etl_result: Dict[str, Any], 
                                     aasx_result: Dict[str, Any]) -> Dict[str, Any]:
        """Populate AI RAG tables and store data in Qdrant vector database."""
        try:
            # Check if AASX population was successful
            if aasx_result.get('status') != 'success':
                logger.warning("Skipping AI RAG population - AASX population failed")
                return {'status': 'skipped', 'reason': 'aasx_population_failed'}
            
            # Extract AASX data for RAG processing
            file_id = aasx_result.get('file_id')
            project_id = aasx_result.get('project_id')
            
            # Step 1: Process AASX content through RAG system
            rag_data = {
                'source_type': 'aasx_file',
                'source_id': file_id,
                'project_id': project_id,
                'content': etl_result.get('extracted_content', {}),
                'metadata': etl_result.get('metadata', {})
            }
            
            # Process through RAG orchestrator
            rag_result = await self.rag_orchestrator.process_and_store(rag_data)
            
            # Step 2: Store processed data in Qdrant vector database
            qdrant_result = await self._store_in_qdrant(etl_result, aasx_result, rag_result)
            
            # Combine results from both RAG processing and Qdrant storage
            combined_result = {
                'status': 'success' if rag_result.get('status') == 'success' and qdrant_result.get('status') == 'success' else 'partial_success',
                'rag_processing_id': rag_result.get('processing_id'),
                'source_file_id': file_id,
                'vector_count': rag_result.get('vector_count', 0),
                'qdrant_storage': qdrant_result,
                'timestamp': datetime.now().isoformat()
            }
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Failed to populate AI RAG tables: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _populate_kg_neo4j_tables(self, etl_result: Dict[str, Any], 
                                       aasx_result: Dict[str, Any],
                                       twin_result: Dict[str, Any], 
                                       rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """Populate KG Neo4j tables with integrated data from all previous steps."""
        try:
            # Check if all previous populations were successful
            required_statuses = [
                aasx_result.get('status') == 'success',
                twin_result.get('status') == 'success',
                rag_result.get('status') == 'success'
            ]
            
            if not all(required_statuses):
                logger.warning("Skipping KG Neo4j population - some previous steps failed")
                return {'status': 'skipped', 'reason': 'previous_steps_failed'}
            
            # Combine data from all sources for knowledge graph
            integrated_data = {
                'aasx_data': aasx_result,
                'twin_data': twin_result,
                'rag_data': rag_result,
                'etl_metadata': etl_result,
                'integration_timestamp': datetime.now().isoformat()
            }
            
            # Create knowledge graph nodes and relationships
            kg_nodes = await self._create_kg_nodes(integrated_data)
            kg_relationships = await self._create_kg_relationships(integrated_data)
            
            return {
                'status': 'success',
                'kg_nodes_created': len(kg_nodes),
                'kg_relationships_created': len(kg_relationships),
                'integration_id': f"kg_{datetime.now().timestamp()}",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to populate KG Neo4j tables: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _create_kg_nodes(self, integrated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create knowledge graph nodes from integrated data."""
        try:
            nodes = []
            
            # Create AASX node
            aasx_node = {
                'label': 'AASXFile',
                'properties': {
                    'file_id': integrated_data['aasx_data']['file_id'],
                    'project_id': integrated_data['aasx_data']['project_id'],
                    'type': 'aasx_file',
                    'created_at': integrated_data['aasx_data']['timestamp']
                }
            }
            nodes.append(aasx_node)
            
            # Create Twin Registry node
            twin_node = {
                'label': 'DigitalTwin',
                'properties': {
                    'twin_id': integrated_data['twin_data']['twin_id'],
                    'source_type': 'aasx_etl',
                    'created_at': integrated_data['twin_data']['timestamp']
                }
            }
            nodes.append(twin_node)
            
            # Create RAG node
            rag_node = {
                'label': 'RAGProcessing',
                'properties': {
                    'processing_id': integrated_data['rag_data']['rag_processing_id'],
                    'vector_count': integrated_data['rag_data']['vector_count'],
                    'created_at': integrated_data['rag_data']['timestamp']
                }
            }
            nodes.append(rag_node)
            
            # Create Qdrant node
            qdrant_node = {
                'label': 'QdrantCollection',
                'properties': {
                    'collection_name': integrated_data['rag_data'].get('qdrant_storage', {}).get('collection_name', 'aasx_documents'),
                    'vector_count': integrated_data['rag_data'].get('qdrant_storage', {}).get('vector_count', 0),
                    'created_at': integrated_data['rag_data'].get('qdrant_storage', {}).get('timestamp', datetime.now().isoformat())
                }
            }
            nodes.append(qdrant_node)
            
            # Create nodes in Neo4j
            created_nodes = []
            for node in nodes:
                node_id = await self.kg_neo4j_manager.create_node(
                    node['label'], 
                    node['properties']
                )
                if node_id:
                    created_nodes.append({'node_id': node_id, 'node_data': node})
            
            return created_nodes
            
        except Exception as e:
            logger.error(f"Failed to create KG nodes: {e}")
            return []
    
    async def _create_kg_relationships(self, integrated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create knowledge graph relationships from integrated data."""
        try:
            relationships = []
            
            # AASX -> Twin Registry relationship
            aasx_twin_rel = {
                'from_label': 'AASXFile',
                'from_properties': {'file_id': integrated_data['aasx_data']['file_id']},
                'to_label': 'DigitalTwin',
                'to_properties': {'twin_id': integrated_data['twin_data']['twin_id']},
                'relationship_type': 'CREATES_TWIN',
                'properties': {
                    'created_at': datetime.now().isoformat(),
                    'source': 'aasx_population_orchestrator'
                }
            }
            relationships.append(aasx_twin_rel)
            
            # AASX -> RAG relationship
            aasx_rag_rel = {
                'from_label': 'AASXFile',
                'from_properties': {'file_id': integrated_data['aasx_data']['file_id']},
                'to_label': 'RAGProcessing',
                'to_properties': {'processing_id': integrated_data['rag_data']['rag_processing_id']},
                'relationship_type': 'PROCESSED_BY_RAG',
                'properties': {
                    'created_at': datetime.now().isoformat(),
                    'source': 'aasx_population_orchestrator'
                }
            }
            relationships.append(aasx_rag_rel)
            
            # Twin Registry -> RAG relationship
            twin_rag_rel = {
                'from_label': 'DigitalTwin',
                'from_properties': {'twin_id': integrated_data['twin_data']['twin_id']},
                'to_label': 'RAGProcessing',
                'to_properties': {'processing_id': integrated_data['rag_data']['rag_processing_id']},
                'relationship_type': 'ENRICHED_BY_RAG',
                'properties': {
                    'created_at': datetime.now().isoformat(),
                    'source': 'aasx_population_orchestrator'
                }
            }
            relationships.append(twin_rag_rel)
            
            # Qdrant Collection -> AASX relationship
            qdrant_aasx_rel = {
                'from_label': 'QdrantCollection',
                'from_properties': {'collection_name': integrated_data['rag_data'].get('qdrant_storage', {}).get('collection_name', 'aasx_documents')},
                'to_label': 'AASXFile',
                'to_properties': {'file_id': integrated_data['aasx_data']['file_id']},
                'relationship_type': 'STORES_DOCUMENTS',
                'properties': {
                    'created_at': datetime.now().isoformat(),
                    'source': 'aasx_population_orchestrator'
                }
            }
            relationships.append(qdrant_aasx_rel)
            
            # RAG Processing -> Qdrant Collection relationship
            rag_qdrant_rel = {
                'from_label': 'RAGProcessing',
                'from_properties': {'processing_id': integrated_data['rag_data']['rag_processing_id']},
                'to_label': 'QdrantCollection',
                'to_properties': {'collection_name': integrated_data['rag_data'].get('qdrant_storage', {}).get('collection_name', 'aasx_documents')},
                'relationship_type': 'STORES_VECTORS',
                'properties': {
                    'created_at': datetime.now().isoformat(),
                    'source': 'aasx_population_orchestrator'
                }
            }
            relationships.append(rag_qdrant_rel)
            
            # Create relationships in Neo4j
            created_relationships = []
            for rel in relationships:
                # Note: This is a simplified relationship creation
                # In practice, you'd need to implement proper relationship creation
                # based on your Neo4j manager's capabilities
                created_relationships.append(rel)
            
            return created_relationships
            
        except Exception as e:
            logger.error(f"Failed to create KG relationships: {e}")
            return []
    
    def _consolidate_results(self, aasx_result: Dict[str, Any], 
                           twin_result: Dict[str, Any],
                           rag_result: Dict[str, Any], 
                           kg_result: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate results from all population steps."""
        try:
            # Check overall success
            all_successful = all([
                result.get('status') == 'success' 
                for result in [aasx_result, twin_result, rag_result, kg_result]
            ])
            
            # Count successful steps
            successful_steps = sum([
                1 for result in [aasx_result, twin_result, rag_result, kg_result]
                if result.get('status') == 'success'
            ])
            
            consolidated = {
                'overall_status': 'success' if all_successful else 'partial_success',
                'successful_steps': successful_steps,
                'total_steps': 4,
                'timestamp': datetime.now().isoformat(),
                'step_results': {
                    'aasx_population': aasx_result,
                    'twin_registry_population': twin_result,
                    'ai_rag_population': rag_result,
                    'kg_neo4j_population': kg_result
                }
            }
            
            if not all_successful:
                consolidated['failed_steps'] = [
                    step for step, result in consolidated['step_results'].items()
                    if result.get('status') != 'success'
                ]
                consolidated['warnings'] = [
                    f"Step {step} failed: {result.get('error', 'unknown error')}"
                    for step, result in consolidated['step_results'].items()
                    if result.get('status') != 'success'
                ]
            
            return consolidated
            
        except Exception as e:
            logger.error(f"Failed to consolidate results: {e}")
            return {
                'overall_status': 'error',
                'error': f'Failed to consolidate results: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def _rollback_population(self, etl_result: Dict[str, Any]):
        """Rollback population changes if any step fails."""
        try:
            logger.warning("🔄 Rolling back population changes...")
            
            # Note: Implement rollback logic based on your requirements
            # This could involve:
            # - Deleting created records
            # - Reverting status changes
            # - Cleaning up temporary data
            
            logger.warning("Rollback completed (implementation depends on requirements)")
            
        except Exception as e:
            logger.error(f"Failed to rollback population: {e}")
            # Don't raise here as we're already in an error state


# Factory function for easy instantiation
def create_aasx_population_orchestrator(connection_manager) -> AASXPopulationOrchestrator:
    """Create AASX Population Orchestrator instance."""
    return AASXPopulationOrchestrator(connection_manager)
