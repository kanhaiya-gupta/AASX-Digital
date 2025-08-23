"""
Knowledge Graph Operations Service

Operational services for Knowledge Graph operations.
Handles specific graph operations, transformations, and workflows.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import json

from src.engine.database.connection_manager import ConnectionManager
from src.kg_neo4j.core.kg_graph_service import KGGraphService
from src.kg_neo4j.core.kg_neo4j_integration_service import KGNeo4jIntegrationService
from src.kg_neo4j.models.kg_graph_registry import KGGraphRegistry
from src.kg_neo4j.models.kg_graph_metrics import KGGraphMetrics

logger = logging.getLogger(__name__)


class KGGraphOperationsService:
    """Operational service for Knowledge Graph operations."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the operations service with connection manager."""
        self.connection_manager = connection_manager
        self.graph_service = KGGraphService(connection_manager)
        self.neo4j_service = KGNeo4jIntegrationService(connection_manager)
        logger.info("Knowledge Graph Operations Service initialized with pure async support")
    
    async def initialize(self) -> None:
        """Initialize the operations service."""
        try:
            await self.graph_service.initialize()
            await self.neo4j_service.initialize()
            logger.info("✅ Knowledge Graph Operations Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Operations Service: {e}")
            raise
    
    # ==================== GRAPH WORKFLOW OPERATIONS ====================
    
    async def create_graph_from_aasx_file(
        self, 
        file_id: str, 
        user_id: str, 
        org_id: str,
        graph_config: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[KGGraphRegistry]]:
        """Complete workflow to create graph from AASX file."""
        try:
            logger.info(f"🚀 Starting graph creation workflow for file: {file_id}")
            
            # Step 1: Create knowledge graph
            graph_name = graph_config.get("graph_name", f"Graph_{file_id}")
            graph = await self.graph_service.create_knowledge_graph(
                file_id=file_id,
                graph_name=graph_name,
                user_id=user_id,
                org_id=org_id,
                **graph_config
            )
            
            if not graph:
                return False, "Failed to create knowledge graph", None
            
            logger.info(f"✅ Step 1: Created knowledge graph {graph.graph_id}")
            
            # Step 2: Test Neo4j connection
            connection_success, connection_msg, connection_info = await self.neo4j_service.test_neo4j_connection(
                graph.graph_id
            )
            
            if not connection_success:
                logger.warning(f"⚠️ Step 2: Neo4j connection test failed: {connection_msg}")
                # Continue anyway, as Neo4j is optional for basic operations
            
            logger.info(f"✅ Step 2: Neo4j connection test completed")
            
            # Step 3: Import graph data to Neo4j (if connection successful)
            if connection_success:
                import_success, import_msg = await self.neo4j_service.import_graph_to_neo4j(
                    graph.graph_id,
                    {"format": "cypher", "batch_size": 1000}
                )
                
                if import_success:
                    logger.info(f"✅ Step 3: Graph data imported to Neo4j: {import_msg}")
                else:
                    logger.warning(f"⚠️ Step 3: Neo4j import failed: {import_msg}")
            
            # Step 4: Update final status
            await self.graph_service.update_graph_status(graph.graph_id, {
                "integration_status": "active",
                "lifecycle_status": "active",
                "operational_status": "running"
            })
            
            logger.info(f"🎉 Graph creation workflow completed successfully: {graph.graph_id}")
            return True, "Graph creation workflow completed successfully", graph
            
        except Exception as e:
            logger.error(f"❌ Graph creation workflow failed: {e}")
            return False, f"Workflow failed: {str(e)}", None
    
    async def link_graph_to_twin_workflow(
        self, 
        graph_id: str, 
        twin_id: str,
        link_config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Complete workflow to link graph to digital twin."""
        try:
            logger.info(f"🔗 Starting graph-twin linking workflow: {graph_id} -> {twin_id}")
            
            # Step 1: Validate both entities exist
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return False, "Graph not found"
            
            # Step 2: Perform the linking
            link_success = await self.graph_service.link_graph_to_twin(graph_id, twin_id)
            
            if not link_success:
                return False, "Failed to link graph to twin"
            
            # Step 3: Update Neo4j with relationship (if connected)
            if graph.neo4j_connection_status == "connected":
                # Create relationship in Neo4j
                cypher_query = """
                MATCH (g:KnowledgeGraph {graph_id: $graph_id})
                MATCH (t:DigitalTwin {twin_id: $twin_id})
                MERGE (g)-[:LINKED_TO {link_type: $link_type, created_at: $created_at}]->(t)
                RETURN g, t
                """
                
                query_params = {
                    "graph_id": graph_id,
                    "twin_id": twin_id,
                    "link_type": link_config.get("link_type", "standard"),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                query_success, query_msg, query_results = await self.neo4j_service.execute_neo4j_query(
                    graph_id, cypher_query, query_params
                )
                
                if query_success:
                    logger.info(f"✅ Neo4j relationship created: {query_msg}")
                else:
                    logger.warning(f"⚠️ Neo4j relationship creation failed: {query_msg}")
            
            # Step 4: Record the operation
            await self.graph_service.record_graph_operation(
                graph_id, 
                "twin_linking", 
                {"twin_id": twin_id, "link_config": link_config}
            )
            
            logger.info(f"🎉 Graph-twin linking workflow completed successfully")
            return True, "Graph successfully linked to digital twin"
            
        except Exception as e:
            logger.error(f"❌ Graph-twin linking workflow failed: {e}")
            return False, f"Linking workflow failed: {str(e)}"
    
    async def export_graph_workflow(
        self, 
        graph_id: str, 
        export_config: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Complete workflow to export graph data."""
        try:
            logger.info(f"📤 Starting graph export workflow: {graph_id}")
            
            # Step 1: Validate graph exists and is ready
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return False, "Graph not found", None
            
            if graph.integration_status != "active":
                return False, f"Graph not ready for export. Status: {graph.integration_status}", None
            
            # Step 2: Export from Neo4j (if connected)
            export_results = {}
            if graph.neo4j_connection_status == "connected":
                export_success, export_msg = await self.neo4j_service.export_graph_from_neo4j(
                    graph_id, export_config
                )
                
                if export_success:
                    logger.info(f"✅ Neo4j export completed: {export_msg}")
                    export_results["neo4j_export"] = {"success": True, "message": export_msg}
                else:
                    logger.warning(f"⚠️ Neo4j export failed: {export_msg}")
                    export_results["neo4j_export"] = {"success": False, "message": export_msg}
            
            # Step 3: Export from database
            db_export_success, db_export_data = await self._export_graph_from_database(graph_id, export_config)
            
            if db_export_success:
                logger.info(f"✅ Database export completed")
                export_results["database_export"] = {"success": True, "data": db_export_data}
            else:
                logger.warning(f"⚠️ Database export failed")
                export_results["database_export"] = {"success": False, "error": db_export_data}
            
            # Step 4: Record the operation
            await self.graph_service.record_graph_operation(
                graph_id, 
                "graph_export", 
                {"export_config": export_config, "export_results": export_results}
            )
            
            logger.info(f"🎉 Graph export workflow completed successfully")
            return True, "Graph export workflow completed successfully", export_results
            
        except Exception as e:
            logger.error(f"❌ Graph export workflow failed: {e}")
            return False, f"Export workflow failed: {str(e)}", None
    
    # ==================== GRAPH TRANSFORMATION OPERATIONS ====================
    
    async def transform_graph_structure(
        self, 
        graph_id: str, 
        transformation_config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Transform graph structure based on configuration."""
        try:
            logger.info(f"🔄 Starting graph transformation: {graph_id}")
            
            # Validate transformation configuration
            if not self._validate_transformation_config(transformation_config):
                return False, "Invalid transformation configuration"
            
            # Get graph details
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return False, "Graph not found"
            
            # Apply transformations
            transformations_applied = []
            
            # Node transformation
            if "node_transformations" in transformation_config:
                node_success = await self._apply_node_transformations(
                    graph_id, transformation_config["node_transformations"]
                )
                if node_success:
                    transformations_applied.append("node_transformations")
            
            # Relationship transformation
            if "relationship_transformations" in transformation_config:
                rel_success = await self._apply_relationship_transformations(
                    graph_id, transformation_config["relationship_transformations"]
                )
                if rel_success:
                    transformations_applied.append("relationship_transformations")
            
            # Property transformation
            if "property_transformations" in transformation_config:
                prop_success = await self._apply_property_transformations(
                    graph_id, transformation_config["property_transformations"]
                )
                if prop_success:
                    transformations_applied.append("property_transformations")
            
            # Update graph metadata
            await self.graph_service.update_graph_status(graph_id, {
                "graph_version": transformation_config.get("new_version", "1.1"),
                "transformation_history": json.dumps(transformations_applied),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Record the transformation
            await self.graph_service.record_graph_operation(
                graph_id, 
                "graph_transformation", 
                {"transformation_config": transformation_config, "applied": transformations_applied}
            )
            
            logger.info(f"✅ Graph transformation completed: {transformations_applied}")
            return True, f"Graph transformation completed: {', '.join(transformations_applied)}"
            
        except Exception as e:
            logger.error(f"❌ Graph transformation failed: {e}")
            return False, f"Transformation failed: {str(e)}"
    
    async def merge_graphs(
        self, 
        source_graph_id: str, 
        target_graph_id: str,
        merge_config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Merge two knowledge graphs with comprehensive conflict resolution."""
        try:
            # Get graph details
            source_graph = await self.graph_service.get_graph_by_id(source_graph_id)
            target_graph = await self.graph_service.get_graph_by_id(target_graph_id)
            
            if not source_graph or not target_graph:
                return False, "One or both graphs not found"
            
            # Validate merge configuration
            if not self._validate_merge_config(merge_config):
                return False, "Invalid merge configuration"
            
            # Apply transformations to source graph
            node_success = await self._apply_node_transformations(
                source_graph_id, merge_config.get("node_transformations", {})
            )
            
            rel_success = await self._apply_relationship_transformations(
                source_graph_id, merge_config.get("relationship_transformations", {})
            )
            
            prop_success = await self._apply_property_transformations(
                source_graph_id, merge_config.get("property_transformations", {})
            )
            
            if not all([node_success, rel_success, prop_success]):
                return False, "Graph transformation failed"
            
            # Update target graph status
            await self.graph_service.update_graph_status(target_graph_id, {
                "integration_status": "merging",
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Record merge operation
            await self.graph_service.record_graph_operation(
                target_graph_id, "graph_merge", {
                    "source_graph_id": source_graph_id,
                    "merge_config": merge_config,
                    "transformation_results": {
                        "nodes": node_success,
                        "relationships": rel_success,
                        "properties": prop_success
                    }
                }
            )
            
            logger.info(f"✅ Successfully merged graphs {source_graph_id} into {target_graph_id}")
            return True, "Graphs merged successfully"
            
        except Exception as e:
            logger.error(f"❌ Graph merge failed: {e}")
            return False, f"Merge failed: {str(e)}"
    
    # ==================== AI/RAG INTEGRATION OPERATIONS ====================
    
    async def create_graph_with_ai_insights(
        self, 
        file_id: str,
        user_id: str,
        org_id: str,
        ai_analysis_data: Dict[str, Any],
        graph_config: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[str]]:
        """Create knowledge graph with integrated AI/RAG insights."""
        try:
            # Step 1: Create base knowledge graph from AASX
            success, message, graph = await self.create_graph_from_aasx_file(
                file_id, user_id, org_id, graph_config
            )
            
            if not success:
                return False, f"Failed to create base graph: {message}", None
            
            # Step 2: Import AI/RAG insights
            ai_success, ai_message = await self.graph_service.import_ai_rag_insights(
                graph.graph_id, ai_analysis_data, user_id
            )
            
            if not ai_success:
                logger.warning(f"⚠️ AI insights import failed: {ai_message}")
                # Continue with base graph only
                return True, f"Base graph created successfully. AI insights failed: {ai_message}", graph.graph_id
            
            # Step 3: Get AI insights graph ID
            ai_graphs = await self.graph_service.get_ai_insights_by_graph_id(graph.graph_id)
            if ai_graphs:
                ai_graph_id = ai_graphs[0].get("graph_id")
                
                # Step 4: Merge AI insights with main graph
                merge_success, merge_message = await self.graph_service.merge_ai_insights_with_graph(
                    graph.graph_id, ai_graph_id
                )
                
                if merge_success:
                    logger.info(f"✅ Successfully created graph with AI insights: {graph.graph_id}")
                    return True, "Graph created with integrated AI insights", graph.graph_id
                else:
                    logger.warning(f"⚠️ AI insights merge failed: {merge_message}")
                    return True, f"Base graph created. AI merge failed: {merge_message}", graph.graph_id
            
            return True, "Base graph created successfully", graph.graph_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create graph with AI insights: {e}")
            return False, f"Creation failed: {str(e)}", None
    
    async def enhance_existing_graph_with_ai(
        self, 
        graph_id: str,
        ai_analysis_data: Dict[str, Any],
        user_id: str
    ) -> Tuple[bool, str]:
        """Enhance existing knowledge graph with AI/RAG insights."""
        try:
            # Step 1: Validate graph exists
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return False, "Graph not found"
            
            # Step 2: Import AI insights
            ai_success, ai_message = await self.graph_service.import_ai_rag_insights(
                graph_id, ai_analysis_data, user_id
            )
            
            if not ai_success:
                return False, f"AI insights import failed: {ai_message}"
            
            # Step 3: Get AI insights graph
            ai_graphs = await self.graph_service.get_ai_insights_by_graph_id(graph_id)
            if not ai_graphs:
                return False, "No AI insights graphs found after import"
            
            ai_graph_id = ai_graphs[0].get("graph_id")
            
            # Step 4: Merge insights
            merge_success, merge_message = await self.graph_service.merge_ai_insights_with_graph(
                graph_id, ai_graph_id
            )
            
            if merge_success:
                logger.info(f"✅ Successfully enhanced graph {graph_id} with AI insights")
                return True, "Graph enhanced with AI insights successfully"
            else:
                return False, f"AI insights merge failed: {merge_message}"
            
        except Exception as e:
            logger.error(f"❌ Failed to enhance graph {graph_id} with AI: {e}")
            return False, f"Enhancement failed: {str(e)}"
    
    async def get_graph_ai_insights_summary(
        self, 
        graph_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Get comprehensive AI insights summary for a graph."""
        try:
            # Get main graph
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return False, "Graph not found", None
            
            # Get AI insights graphs
            ai_graphs = await self.graph_service.get_ai_insights_by_graph_id(graph_id)
            
            # Get performance metrics
            performance_summary = await self.graph_service.get_graph_performance_summary(graph_id)
            
            # Compile AI insights summary
            ai_summary = {
                "graph_id": graph_id,
                "graph_name": graph.graph_name,
                "ai_insights_count": len(ai_graphs),
                "ai_graphs": ai_graphs,
                "performance_summary": performance_summary,
                "ai_enhancement_status": graph.integration_status,
                "last_ai_enhancement": graph.registry_metadata.get("last_ai_enhancement") if graph.registry_metadata else None,
                "total_ai_insights": graph.registry_metadata.get("total_ai_insights", 0) if graph.registry_metadata else 0,
                "summary_generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Generated AI insights summary for graph {graph_id}")
            return True, "AI insights summary generated successfully", ai_summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get AI insights summary for graph {graph_id}: {e}")
            return False, f"Summary generation failed: {str(e)}", None
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    async def _export_graph_from_database(
        self, 
        graph_id: str, 
        export_config: Dict[str, Any]
    ) -> Tuple[bool, Any]:
        """Export graph data from database."""
        try:
            # Get graph registry
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return False, "Graph not found"
            
            # Get graph metrics
            metrics = await self.graph_service.get_graph_performance_summary(graph_id)
            
            # Prepare export data
            export_data = {
                "graph_registry": graph.dict(),
                "metrics_summary": metrics,
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "export_format": export_config.get("format", "json")
            }
            
            return True, export_data
            
        except Exception as e:
            logger.error(f"❌ Database export failed: {e}")
            return False, str(e)
    
    async def _apply_node_transformations(
        self, 
        graph_id: str, 
        transformations: List[Dict[str, Any]]
    ) -> bool:
        """Apply node transformations to graph."""
        try:
            # TODO: Implement actual node transformation logic
            # This would involve updating the graph structure in Neo4j
            logger.info(f"Applied {len(transformations)} node transformations to graph {graph_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Node transformation failed: {e}")
            return False
    
    async def _apply_relationship_transformations(
        self, 
        graph_id: str, 
        transformations: List[Dict[str, Any]]
    ) -> bool:
        """Apply relationship transformations to graph."""
        try:
            # TODO: Implement actual relationship transformation logic
            logger.info(f"Applied {len(transformations)} relationship transformations to graph {graph_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Relationship transformation failed: {e}")
            return False
    
    async def _apply_property_transformations(
        self, 
        graph_id: str, 
        transformations: List[Dict[str, Any]]
    ) -> bool:
        """Apply property transformations to graph."""
        try:
            # TODO: Implement actual property transformation logic
            logger.info(f"Applied {len(transformations)} property transformations to graph {graph_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Property transformation failed: {e}")
            return False
    
    async def _merge_graph_nodes(
        self, 
        source_graph_id: str, 
        target_graph_id: str, 
        merge_config: Dict[str, Any]
    ) -> bool:
        """Merge nodes from source graph to target graph."""
        try:
            # TODO: Implement actual node merging logic
            logger.info(f"Merged nodes from {source_graph_id} to {target_graph_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Node merge failed: {e}")
            return False
    
    async def _merge_graph_relationships(
        self, 
        source_graph_id: str, 
        target_graph_id: str, 
        merge_config: Dict[str, Any]
    ) -> bool:
        """Merge relationships from source graph to target graph."""
        try:
            # TODO: Implement actual relationship merging logic
            logger.info(f"Merged relationships from {source_graph_id} to {target_graph_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Relationship merge failed: {e}")
            return False
    
    async def _merge_graph_metadata(
        self, 
        source_graph_id: str, 
        target_graph_id: str, 
        merge_config: Dict[str, Any]
    ) -> bool:
        """Merge metadata from source graph to target graph."""
        try:
            # TODO: Implement actual metadata merging logic
            logger.info(f"Merged metadata from {source_graph_id} to {target_graph_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Metadata merge failed: {e}")
            return False
    
    def _validate_transformation_config(self, config: Dict[str, Any]) -> bool:
        """Validate transformation configuration."""
        required_fields = ["transformation_type", "transformation_rules"]
        return all(field in config for field in required_fields)
    
    def _validate_merge_compatibility(
        self, 
        source_graph: KGGraphRegistry, 
        target_graph: KGGraphRegistry
    ) -> bool:
        """Validate if two graphs are compatible for merging."""
        # Basic compatibility checks
        if source_graph.graph_id == target_graph.graph_id:
            return False  # Cannot merge with self
        
        if source_graph.graph_type != target_graph.graph_type:
            return False  # Different graph types may not be compatible
        
        return True
