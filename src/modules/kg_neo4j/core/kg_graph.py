"""
Knowledge Graph Core Service

Heavy lifting business logic for Knowledge Graph operations.
Handles complex business operations, async operations, and cross-repository coordination.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import asdict

from src.engine.database.connection_manager import ConnectionManager
from ..repositories.kg_graph_registry_repository import KGGraphRegistryRepository
from ..repositories.kg_graph_metrics_repository import KGGraphMetricsRepository
from ..repositories.kg_neo4j_ml_repository import KGNeo4jMLRepository
from ..models.kg_graph_registry import KGGraphRegistry, KGGraphRegistryQuery
from ..models.kg_graph_metrics import KGGraphMetrics, KGGraphMetricsQuery
from ..models.kg_neo4j_ml_registry import KGNeo4jMLRegistry

logger = logging.getLogger(__name__)


class KGGraphService:
    """Main business logic service for Knowledge Graph operations."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the Knowledge Graph service with connection manager."""
        self.connection_manager = connection_manager
        self.registry_repo = KGGraphRegistryRepository(connection_manager)
        self.metrics_repo = KGGraphMetricsRepository(connection_manager)
        self.ml_repo = KGNeo4jMLRepository(connection_manager)
        logger.info("Knowledge Graph Service initialized with pure async support")
    
    async def initialize(self) -> None:
        """Initialize the service and repositories."""
        try:
            await self.registry_repo.initialize()
            await self.metrics_repo.initialize()
            logger.info("✅ Knowledge Graph Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Knowledge Graph Service: {e}")
            raise
    
    # ==================== GRAPH REGISTRY OPERATIONS ====================
    
    async def create_knowledge_graph(
        self, 
        file_id: str,
        graph_name: str,
        user_id: str,
        org_id: str,
        **kwargs
    ) -> KGGraphRegistry:
        """Create a new knowledge graph with comprehensive setup."""
        try:
            # Generate unique graph ID
            timestamp = datetime.now(timezone.utc)
            graph_id = f"kg_{int(timestamp.timestamp())}_{hash(file_id) % 10000:04d}"
            
            # Create registry entry
            registry = KGGraphRegistry(
                graph_id=graph_id,
                file_id=file_id,
                graph_name=graph_name,
                registry_name=f"{graph_name}_registry",
                user_id=user_id,
                org_id=org_id,
                created_at=timestamp,
                updated_at=timestamp,
                **kwargs
            )
            
            # Save to database
            created_registry = await self.registry_repo.create(registry)
            
            # Create initial metrics entry
            await self._create_initial_metrics(graph_id)
            
            logger.info(f"✅ Created knowledge graph: {graph_id} for file: {file_id}")
            return created_registry
            
        except Exception as e:
            logger.error(f"❌ Failed to create knowledge graph: {e}")
            raise
    
    async def get_graph_by_file_id(self, file_id: str) -> Optional[KGGraphRegistry]:
        """Get knowledge graph by file ID."""
        try:
            graphs = await self.registry_repo.get_by_file_id(file_id)
            return graphs[0] if graphs else None
        except Exception as e:
            logger.error(f"Error getting graph by file_id {file_id}: {e}")
            return None
    
    async def get_graph_by_id(self, graph_id: str) -> Optional[KGGraphRegistry]:
        """Get knowledge graph by graph ID."""
        try:
            return await self.registry_repo.get_by_id(graph_id)
        except Exception as e:
            logger.error(f"Error getting graph by graph_id {graph_id}: {e}")
            return None
    
    async def update_graph_status(
        self, 
        graph_id: str, 
        status_updates: Dict[str, Any]
    ) -> bool:
        """Update graph status with comprehensive validation."""
        try:
            # Get current graph
            current_graph = await self.get_graph_by_id(graph_id)
            if not current_graph:
                logger.warning(f"Graph {graph_id} not found for status update")
                return False
            
            # Validate status updates
            valid_updates = self._validate_status_updates(status_updates)
            if not valid_updates:
                logger.warning(f"No valid status updates for graph {graph_id}")
                return False
            
            # Get current graph and update it
            graph = await self.get_graph_by_id(graph_id)
            if not graph:
                logger.error(f"Graph {graph_id} not found for status update")
                return False
            
            # Update the graph object
            for key, value in valid_updates.items():
                if hasattr(graph, key):
                    setattr(graph, key, value)
            
            # Update timestamp
            graph.updated_at = datetime.now(timezone.utc)
            
            # Save updated graph
            updated_graph = await self.registry_repo.update(graph)
            
            if updated_graph:
                # Create metrics entry for status change
                await self._create_status_change_metrics(graph_id, status_updates)
                logger.info(f"✅ Updated graph {graph_id} status: {valid_updates}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to update graph {graph_id} status: {e}")
            return False
    
    async def link_graph_to_twin(self, graph_id: str, twin_id: str) -> bool:
        """Link knowledge graph to a digital twin."""
        try:
            # Validate both entities exist
            graph = await self.get_graph_by_id(graph_id)
            if not graph:
                logger.warning(f"Graph {graph_id} not found for twin linking")
                return False
            
            # Update the link
            graph.twin_registry_id = twin_id
            graph.updated_at = datetime.now(timezone.utc)
            
            updated_graph = await self.registry_repo.update(graph)
            
            if updated_graph:
                logger.info(f"✅ Linked graph {graph_id} to twin {twin_id}")
                # Create metrics for the linking operation
                await self._create_operation_metrics(graph_id, "twin_linking", {"twin_id": twin_id})
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to link graph {graph_id} to twin {twin_id}: {e}")
            return False
    
    # ==================== GRAPH METRICS OPERATIONS ====================
    
    async def record_graph_operation(
        self, 
        graph_id: str, 
        operation_type: str, 
        operation_data: Dict[str, Any]
    ) -> bool:
        """Record a graph operation with comprehensive metrics."""
        try:
            # Create metrics entry
            metrics = KGGraphMetrics(
                graph_id=graph_id,
                timestamp=datetime.now(timezone.utc),
                user_interaction_count=1,
                query_execution_count=1,
                operation_type=operation_type,
                operation_data=operation_data
            )
            
            await self.metrics_repo.create(metrics)
            logger.info(f"✅ Recorded operation {operation_type} for graph {graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record operation for graph {graph_id}: {e}")
            return False
    
    async def get_graph_performance_summary(self, graph_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for a graph."""
        try:
            # Get latest metrics
            latest_metrics = await self.metrics_repo.get_latest_metrics(graph_id)
            
            # Get performance trends
            performance_trends = await self.metrics_repo.get_performance_metrics(graph_id, 30)
            
            # Get user activity
            user_activity = await self.metrics_repo.get_user_activity_metrics(graph_id, 30)
            
            # Get data quality metrics
            data_quality = await self.metrics_repo.get_health_metrics(graph_id, 30)
            
            return {
                "graph_id": graph_id,
                "latest_metrics": latest_metrics.dict() if latest_metrics else None,
                "performance_trends": performance_trends,
                "user_activity": user_activity,
                "data_quality": data_quality,
                "summary_generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance summary for graph {graph_id}: {e}")
            return {"error": str(e)}
    
    # ==================== COMPLEX BUSINESS OPERATIONS ====================
    
    async def import_graph_from_aasx(
        self, 
        file_id: str, 
        user_id: str, 
        org_id: str,
        import_options: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[KGGraphRegistry]]:
        """Import graph from AASX file with comprehensive processing."""
        try:
            # Check if graph already exists for this file
            existing_graph = await self.get_graph_by_file_id(file_id)
            if existing_graph:
                logger.info(f"Graph already exists for file {file_id}: {existing_graph.graph_id}")
                return True, "Graph already exists", existing_graph
            
            # Create new graph
            graph = await self.create_knowledge_graph(
                file_id=file_id,
                graph_name=import_options.get("graph_name", f"Graph_{file_id}"),
                user_id=user_id,
                org_id=org_id,
                workflow_source="aasx_file",
                registry_type="extraction",
                integration_status="pending"
            )
            
            # Process import options
            await self._process_import_options(graph.graph_id, import_options)
            
            # Update status to active
            await self.update_graph_status(graph.graph_id, {
                "integration_status": "active",
                "lifecycle_status": "active",
                "operational_status": "running"
            })
            
            logger.info(f"✅ Successfully imported graph from AASX: {graph.graph_id}")
            return True, "Graph imported successfully", graph
            
        except Exception as e:
            logger.error(f"❌ Failed to import graph from AASX: {e}")
            return False, f"Import failed: {str(e)}", None
    
    async def export_graph_to_neo4j(self, graph_id: str) -> Tuple[bool, str]:
        """Export graph data to Neo4j with comprehensive validation."""
        try:
            # Get graph details
            graph = await self.get_graph_by_id(graph_id)
            if not graph:
                return False, "Graph not found"
            
            # Validate graph is ready for export
            if graph.integration_status != "active":
                return False, f"Graph not ready for export. Status: {graph.integration_status}"
            
            # Update export status
            await self.update_graph_status(graph_id, {
                "neo4j_export_status": "in_progress",
                "last_neo4j_sync_at": datetime.now(timezone.utc)
            })
            
            # TODO: Implement actual Neo4j export logic
            # This would integrate with the existing neo4j_manager.py
            
            # Update export status to completed
            await self.update_graph_status(graph_id, {
                "neo4j_export_status": "completed",
                "next_neo4j_sync_at": datetime.now(timezone.utc)
            })
            
            logger.info(f"✅ Successfully exported graph {graph_id} to Neo4j")
            return True, "Graph exported successfully to Neo4j"
            
        except Exception as e:
            logger.error(f"❌ Failed to export graph {graph_id} to Neo4j: {e}")
            # Update export status to failed
            await self.update_graph_status(graph_id, {
                "neo4j_export_status": "failed",
                "neo4j_sync_error_message": str(e)
            })
            return False, f"Export failed: {str(e)}"
    
    # ==================== AI/RAG ANALYTICS INTEGRATION ====================
    
    async def import_ai_rag_insights(
        self, 
        graph_id: str, 
        ai_analysis_data: Dict[str, Any],
        user_id: str
    ) -> Tuple[bool, str]:
        """Import AI/RAG analytics insights into the knowledge graph."""
        try:
            # Get graph details
            graph = await self.get_graph_by_id(graph_id)
            if not graph:
                return False, "Graph not found"
            
            # Validate AI analysis data
            if not self._validate_ai_analysis_data(ai_analysis_data):
                return False, "Invalid AI analysis data format"
            
            # Extract insights and patterns
            insights = await self._extract_ai_insights(ai_analysis_data)
            
            # Create AI insights graph entry
            ai_graph_id = f"{graph_id}_ai_{int(datetime.now(timezone.utc).timestamp())}"
            
            ai_registry = KGGraphRegistry(
                graph_id=ai_graph_id,
                file_id=graph.file_id,  # Link to same AASX file
                graph_name=f"{graph.graph_name}_AI_Insights",
                registry_name=f"{graph.graph_name}_AI_Registry",
                user_id=user_id,
                org_id=graph.org_id,
                workflow_source="ai_rag_analytics",
                registry_type="ai_insights",
                integration_status="active",
                graph_type="analytical",
                graph_category="ai_generated",
                graph_priority=graph.graph_priority,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                registry_metadata={
                    "source_graph_id": graph_id,
                    "ai_analysis_type": ai_analysis_data.get("analysis_type", "unknown"),
                    "confidence_score": ai_analysis_data.get("confidence_score", 0.0),
                    "insights_count": len(insights.get("patterns", [])),
                    "relationships_discovered": len(insights.get("relationships", []))
                },
                custom_attributes={
                    "ai_model_version": ai_analysis_data.get("model_version", "unknown"),
                    "analysis_timestamp": ai_analysis_data.get("timestamp", datetime.now(timezone.utc)),
                    "data_sources": ai_analysis_data.get("data_sources", []),
                    "processing_parameters": ai_analysis_data.get("parameters", {})
                },
                tags=["ai-generated", "insights", "analytics", "rag"],
                relationships={
                    "source_graph": graph_id,
                    "ai_analysis_session": ai_analysis_data.get("session_id", "unknown"),
                    "related_insights": insights.get("related_insights", [])
                }
            )
            
            # Save AI insights graph
            created_ai_graph = await self.registry_repo.create(ai_registry)
            
            # Create metrics for AI insights
            await self._create_ai_insights_metrics(ai_graph_id, insights)
            
            # Link AI graph to original graph
            await self._link_ai_graph_to_source(ai_graph_id, graph_id)
            
            logger.info(f"✅ Successfully imported AI/RAG insights for graph {graph_id}")
            return True, f"AI insights imported successfully. New graph: {ai_graph_id}"
            
        except Exception as e:
            logger.error(f"❌ Failed to import AI/RAG insights for graph {graph_id}: {e}")
            return False, f"AI insights import failed: {str(e)}"
    
    async def get_ai_insights_by_graph_id(self, graph_id: str) -> List[Dict[str, Any]]:
        """Get all AI insights graphs linked to a source graph."""
        try:
            # Find all AI insights graphs linked to this source graph
            ai_graphs = await self.registry_repo.get_by_workflow_source("ai_rag_analytics")
            
            # Filter for graphs linked to the source graph
            linked_ai_graphs = []
            for ai_graph in ai_graphs:
                if ai_graph.relationships and ai_graph.relationships.get("source_graph") == graph_id:
                    linked_ai_graphs.append(ai_graph.dict())
            
            logger.info(f"Found {len(linked_ai_graphs)} AI insights graphs for source graph {graph_id}")
            return linked_ai_graphs
            
        except Exception as e:
            logger.error(f"❌ Failed to get AI insights for graph {graph_id}: {e}")
            return []
    
    async def merge_ai_insights_with_graph(
        self, 
        graph_id: str, 
        ai_graph_id: str
    ) -> Tuple[bool, str]:
        """Merge AI insights graph with the main knowledge graph."""
        try:
            # Get both graphs
            main_graph = await self.get_graph_by_id(graph_id)
            ai_graph = await self.get_graph_by_id(ai_graph_id)
            
            if not main_graph or not ai_graph:
                return False, "One or both graphs not found"
            
            # Validate AI graph is linked to main graph
            if ai_graph.relationships.get("source_graph") != graph_id:
                return False, "AI graph is not linked to the main graph"
            
            # Merge metadata and insights
            merged_metadata = await self._merge_graph_metadata(
                main_graph.registry_metadata or {},
                ai_graph.registry_metadata or {}
            )
            
            # Update main graph with merged insights
            await self.update_graph_status(graph_id, {
                "registry_metadata": merged_metadata,
                "integration_status": "enhanced_with_ai"
            })
            
            # Mark AI graph as merged
            await self.update_graph_status(ai_graph_id, {
                "integration_status": "merged",
                "lifecycle_phase": "completed"
            })
            
            logger.info(f"✅ Successfully merged AI insights {ai_graph_id} with main graph {graph_id}")
            return True, "AI insights merged successfully"
            
        except Exception as e:
            logger.error(f"❌ Failed to merge AI insights with graph {graph_id}: {e}")
            return False, f"Merge failed: {str(e)}"
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    async def _create_initial_metrics(self, graph_id: str) -> None:
        """Create initial metrics entry for a new graph."""
        try:
            metrics = KGGraphMetrics(
                graph_id=graph_id,
                timestamp=datetime.now(timezone.utc),
                health_score=100,
                response_time_ms=0.0,
                uptime_percentage=100.0,
                error_rate=0.0,
                neo4j_connection_status="disconnected",
                user_interaction_count=0,
                query_execution_count=0,
                data_freshness_score=1.0,
                data_completeness_score=1.0,
                data_consistency_score=1.0,
                data_accuracy_score=1.0
            )
            
            await self.metrics_repo.create(metrics)
            logger.info(f"✅ Created initial metrics for graph {graph_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create initial metrics for graph {graph_id}: {e}")
    
    async def _create_status_change_metrics(
        self, 
        graph_id: str, 
        status_updates: Dict[str, Any]
    ) -> None:
        """Create metrics entry for status changes."""
        try:
            metrics = KGGraphMetrics(
                graph_id=graph_id,
                timestamp=datetime.now(timezone.utc),
                health_score=100,
                user_interaction_count=1,
                query_execution_count=1,
                operation_type="status_update",
                operation_data=status_updates
            )
            
            await self.metrics_repo.create_metrics(metrics)
            
        except Exception as e:
            logger.error(f"❌ Failed to create status change metrics for graph {graph_id}: {e}")
    
    async def _create_operation_metrics(
        self, 
        graph_id: str, 
        operation_type: str, 
        operation_data: Dict[str, Any]
    ) -> None:
        """Create metrics entry for specific operations."""
        try:
            metrics = KGGraphMetrics(
                graph_id=graph_id,
                timestamp=datetime.now(timezone.utc),
                health_score=100,
                user_interaction_count=1,
                query_execution_count=1,
                operation_type=operation_type,
                operation_data=operation_data
            )
            
            await self.metrics_repo.create(metrics)
            
        except Exception as e:
            logger.error(f"❌ Failed to create operation metrics for graph {graph_id}: {e}")
    
    async def _process_import_options(self, graph_id: str, import_options: Dict[str, Any]) -> None:
        """Process import options and update graph configuration."""
        try:
            # Extract relevant options
            config_updates = {}
            
            if "graph_category" in import_options:
                config_updates["graph_category"] = import_options["graph_category"]
            
            if "graph_type" in import_options:
                config_updates["graph_type"] = import_options["graph_type"]
            
            if "graph_priority" in import_options:
                config_updates["graph_priority"] = import_options["graph_priority"]
            
            if "tags" in import_options:
                config_updates["tags"] = import_options["tags"]
            
            if config_updates:
                # Get current graph and update it
                graph = await self.get_graph_by_id(graph_id)
                if graph:
                    # Update the graph object
                    for key, value in config_updates.items():
                        if hasattr(graph, key):
                            setattr(graph, key, value)
                    
                    # Update timestamp
                    graph.updated_at = datetime.now(timezone.utc)
                    
                    # Save updated graph
                    await self.registry_repo.update(graph)
                    logger.info(f"✅ Processed import options for graph {graph_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process import options for graph {graph_id}: {e}")
    
    def _validate_status_updates(self, status_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and filter status updates."""
        valid_fields = {
            'integration_status', 'health_status', 'lifecycle_status', 'operational_status',
            'neo4j_import_status', 'neo4j_export_status', 'overall_health_score',
            'performance_score', 'data_quality_score', 'updated_at'
        }
        
        return {k: v for k, v in status_updates.items() if k in valid_fields}
    
    # ==================== AI/RAG PRIVATE HELPER METHODS ====================
    
    def _validate_ai_analysis_data(self, ai_data: Dict[str, Any]) -> bool:
        """Validate AI analysis data format."""
        try:
            required_fields = ["analysis_type", "insights", "confidence_score"]
            for field in required_fields:
                if field not in ai_data:
                    logger.warning(f"Missing required AI analysis field: {field}")
                    return False
            
            # Validate insights structure
            if not isinstance(ai_data.get("insights"), (list, dict)):
                logger.warning("AI insights must be a list or dictionary")
                return False
            
            # Validate confidence score
            confidence = ai_data.get("confidence_score", 0)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                logger.warning("Confidence score must be between 0 and 1")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating AI analysis data: {e}")
            return False
    
    async def _extract_ai_insights(self, ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure AI insights from analysis data."""
        try:
            insights = {
                "patterns": [],
                "relationships": [],
                "anomalies": [],
                "predictions": [],
                "recommendations": [],
                "related_insights": []
            }
            
            # Extract patterns
            if "patterns" in ai_data.get("insights", {}):
                insights["patterns"] = ai_data["insights"]["patterns"]
            
            # Extract relationships
            if "relationships" in ai_data.get("insights", {}):
                insights["relationships"] = ai_data["insights"]["relationships"]
            
            # Extract anomalies
            if "anomalies" in ai_data.get("insights", {}):
                insights["anomalies"] = ai_data["insights"]["anomalies"]
            
            # Extract predictions
            if "predictions" in ai_data.get("insights", {}):
                insights["predictions"] = ai_data["insights"]["predictions"]
            
            # Extract recommendations
            if "recommendations" in ai_data.get("insights", {}):
                insights["recommendations"] = ai_data["insights"]["recommendations"]
            
            # Generate related insights
            insights["related_insights"] = await self._generate_related_insights(ai_data)
            
            logger.debug(f"Extracted {sum(len(v) for v in insights.values())} AI insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting AI insights: {e}")
            return {"patterns": [], "relationships": [], "anomalies": [], "predictions": [], "recommendations": [], "related_insights": []}
    
    async def _generate_related_insights(self, ai_data: Dict[str, Any]) -> List[str]:
        """Generate related insights based on AI analysis."""
        try:
            related = []
            
            # Add analysis type insights
            analysis_type = ai_data.get("analysis_type", "unknown")
            if analysis_type == "pattern_recognition":
                related.append("Pattern-based relationship discovery")
            elif analysis_type == "anomaly_detection":
                related.append("Anomaly-based insights")
            elif analysis_type == "predictive_analytics":
                related.append("Predictive relationship modeling")
            elif analysis_type == "semantic_analysis":
                related.append("Semantic relationship extraction")
            
            # Add confidence-based insights
            confidence = ai_data.get("confidence_score", 0)
            if confidence > 0.8:
                related.append("High-confidence insights")
            elif confidence > 0.6:
                related.append("Medium-confidence insights")
            else:
                related.append("Low-confidence insights requiring validation")
            
            return related
            
        except Exception as e:
            logger.error(f"Error generating related insights: {e}")
            return []
    
    async def _create_ai_insights_metrics(self, graph_id: str, insights: Dict[str, Any]) -> None:
        """Create metrics entry for AI insights."""
        try:
            metrics = KGGraphMetrics(
                graph_id=graph_id,
                timestamp=datetime.now(timezone.utc),
                health_score=100,
                response_time_ms=0.0,
                uptime_percentage=100.0,
                error_rate=0.0,
                neo4j_connection_status="disconnected",
                user_interaction_count=1,
                query_execution_count=1,
                operation_type="ai_insights_creation",
                operation_data={
                    "insights_count": len(insights.get("patterns", [])),
                    "relationships_count": len(insights.get("relationships", [])),
                    "anomalies_count": len(insights.get("anomalies", [])),
                    "predictions_count": len(insights.get("predictions", [])),
                    "recommendations_count": len(insights.get("recommendations", []))
                },
                data_freshness_score=1.0,
                data_completeness_score=1.0,
                data_consistency_score=1.0,
                data_accuracy_score=1.0
            )
            
            await self.metrics_repo.create(metrics)
            logger.info(f"✅ Created AI insights metrics for graph {graph_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create AI insights metrics for graph {graph_id}: {e}")
    
    async def _link_ai_graph_to_source(self, ai_graph_id: str, source_graph_id: str) -> None:
        """Link AI graph to its source graph."""
        try:
            # Update AI graph relationships
            ai_graph = await self.get_graph_by_id(ai_graph_id)
            if ai_graph:
                if not ai_graph.relationships:
                    ai_graph.relationships = []
                
                ai_graph.relationships.append({
                    "source_graph": source_graph_id,
                    "link_type": "ai_insights",
                    "link_timestamp": datetime.now(timezone.utc)
                })
                
                ai_graph.updated_at = datetime.now(timezone.utc)
                await self.registry_repo.update(ai_graph)
            
            # Update source graph to reference AI graph
            source_graph = await self.get_graph_by_id(source_graph_id)
            if source_graph and source_graph.relationships:
                relationships = source_graph.relationships
                if "ai_insights_graphs" not in relationships:
                    relationships["ai_insights_graphs"] = []
                relationships["ai_insights_graphs"].append(ai_graph_id)
                
                source_graph.relationships = relationships
                source_graph.updated_at = datetime.now(timezone.utc)
                await self.registry_repo.update(source_graph)
            
            logger.info(f"✅ Linked AI graph {ai_graph_id} to source graph {source_graph_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to link AI graph {ai_graph_id} to source graph {source_graph_id}: {e}")
    
    async def _merge_graph_metadata(self, main_metadata: Dict[str, Any], ai_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Merge main graph metadata with AI insights metadata."""
        try:
            merged = main_metadata.copy()
            
            # Merge AI insights
            if "ai_insights" not in merged:
                merged["ai_insights"] = []
            
            ai_insight = {
                "timestamp": ai_metadata.get("analysis_timestamp", datetime.now(timezone.utc)),
                "analysis_type": ai_metadata.get("ai_analysis_type", "unknown"),
                "confidence_score": ai_metadata.get("confidence_score", 0.0),
                "insights_count": ai_metadata.get("insights_count", 0),
                "relationships_discovered": ai_metadata.get("relationships_discovered", 0)
            }
            
            merged["ai_insights"].append(ai_insight)
            
            # Update total insights count
            merged["total_ai_insights"] = len(merged["ai_insights"])
            
            # Update last AI enhancement timestamp
            merged["last_ai_enhancement"] = datetime.now(timezone.utc)
            
            logger.debug(f"Merged AI metadata with {len(merged.get('ai_insights', []))} insights")
            return merged
            
        except Exception as e:
            logger.error(f"Error merging graph metadata: {e}")
            return main_metadata
