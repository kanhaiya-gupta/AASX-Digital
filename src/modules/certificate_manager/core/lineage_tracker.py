"""
Lineage Tracker - Data Lineage and Provenance Service

Handles data lineage tracking, provenance analysis, and data flow
visualization. Tracks how data flows through the system, maintains
provenance information, and provides lineage insights for
certificate validation and audit purposes.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple, Set
from enum import Enum
from collections import defaultdict

from ..models.certificates_registry import (
    CertificateRegistry,
    ModuleStatus,
    QualityLevel
)
from ..models.certificates_metrics import CertificateMetrics, MetricCategory
from ..services.certificates_registry_service import CertificatesRegistryService
from ..services.certificates_metrics_service import CertificatesMetricsService

logger = logging.getLogger(__name__)


class LineageType(str, Enum):
    """Types of data lineage"""
    DATA_FLOW = "data_flow"
    PROCESS_FLOW = "process_flow"
    TRANSFORMATION_FLOW = "transformation_flow"
    ACCESS_FLOW = "access_flow"
    DEPENDENCY_FLOW = "dependency_flow"


class ProvenanceLevel(str, Enum):
    """Levels of provenance detail"""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


class LineageNode:
    """Represents a node in the lineage graph"""
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        node_name: str,
        metadata: Dict[str, Any],
        timestamp: datetime
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.node_name = node_name
        self.metadata = metadata
        self.timestamp = timestamp
        self.incoming_edges: List[str] = []
        self.outgoing_edges: List[str] = []


class LineageEdge:
    """Represents an edge in the lineage graph"""
    
    def __init__(
        self,
        edge_id: str,
        source_node: str,
        target_node: str,
        edge_type: str,
        metadata: Dict[str, Any],
        timestamp: datetime
    ):
        self.edge_id = edge_id
        self.source_node = source_node
        self.target_node = target_node
        self.edge_type = edge_type
        self.metadata = metadata
        self.timestamp = timestamp


class LineageTracker:
    """
    Data lineage tracking and provenance service
    
    Handles:
    - Data flow tracking across modules
    - Provenance information management
    - Lineage graph construction and analysis
    - Data dependency mapping
    - Audit trail generation
    - Lineage visualization support
    """
    
    def __init__(
        self,
        registry_service: CertificatesRegistryService,
        metrics_service: CertificatesMetricsService
    ):
        """Initialize the lineage tracker"""
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Lineage graph storage
        self.lineage_graphs: Dict[str, Dict[str, LineageNode]] = {}
        self.lineage_edges: Dict[str, List[LineageEdge]] = {}
        
        # Provenance data
        self.provenance_data: Dict[str, Dict[str, Any]] = {}
        
        # Lineage tracking locks per certificate
        self.lineage_locks: Dict[str, asyncio.Lock] = {}
        
        # Lineage history
        self.lineage_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Module dependencies mapping
        self.module_dependencies = {
            "aasx_module": ["data_governance"],
            "twin_registry": ["aasx_module", "data_governance"],
            "ai_rag": ["aasx_module", "twin_registry", "data_governance"],
            "kg_neo4j": ["aasx_module", "twin_registry", "ai_rag", "data_governance"],
            "physics_modeling": ["aasx_module", "twin_registry", "kg_neo4j", "data_governance"],
            "federated_learning": ["aasx_module", "twin_registry", "kg_neo4j", "physics_modeling", "data_governance"],
            "data_governance": ["aasx_module", "twin_registry", "ai_rag", "kg_neo4j", "physics_modeling", "federated_learning"]
        }
        
        logger.info("Lineage Tracker initialized successfully")
    
    async def start_lineage_tracking(
        self,
        certificate_id: str,
        provenance_level: ProvenanceLevel = ProvenanceLevel.STANDARD
    ) -> bool:
        """
        Start lineage tracking for a certificate
        
        This is the main entry point for lineage tracking.
        Initializes tracking for all modules and begins
        collecting lineage information.
        """
        try:
            # Acquire lineage lock for this certificate
            if certificate_id not in self.lineage_locks:
                self.lineage_locks[certificate_id] = asyncio.Lock()
            
            async with self.lineage_locks[certificate_id]:
                logger.info(f"Starting lineage tracking for certificate: {certificate_id}")
                
                # Initialize lineage graph
                self.lineage_graphs[certificate_id] = {}
                self.lineage_edges[certificate_id] = []
                
                # Initialize provenance data
                self.provenance_data[certificate_id] = {
                    "provenance_level": provenance_level.value,
                    "tracking_started": datetime.utcnow().isoformat(),
                    "modules_tracked": [],
                    "data_sources": [],
                    "transformations": []
                }
                
                # Start tracking for all modules
                tracking_tasks = []
                for module_name in self.module_dependencies.keys():
                    task = asyncio.create_task(
                        self._track_module_lineage(certificate_id, module_name, provenance_level)
                    )
                    tracking_tasks.append(task)
                
                # Wait for all tracking tasks to complete
                results = await asyncio.gather(*tracking_tasks, return_exceptions=True)
                
                # Analyze tracking results
                successful_tracking = sum(1 for r in results if not isinstance(r, Exception))
                total_modules = len(self.module_dependencies)
                
                # Build lineage graph
                await self._build_lineage_graph(certificate_id)
                
                # Generate lineage summary
                summary = await self._generate_lineage_summary(certificate_id)
                
                # Record lineage history
                await self._record_lineage_history(certificate_id, results, summary)
                
                logger.info(f"Lineage tracking completed for certificate: {certificate_id} - {successful_tracking}/{total_modules} modules tracked")
                return True
                
        except Exception as e:
            logger.error(f"Error starting lineage tracking: {e}")
            return False
    
    async def _track_module_lineage(
        self,
        certificate_id: str,
        module_name: str,
        provenance_level: ProvenanceLevel
    ) -> Dict[str, Any]:
        """Track lineage for a specific module"""
        try:
            logger.info(f"Tracking lineage for module {module_name} in certificate: {certificate_id}")
            
            # Get module dependencies
            dependencies = self.module_dependencies.get(module_name, [])
            
            # Simulate lineage data collection
            lineage_data = await self._simulate_lineage_data_collection(
                module_name, dependencies, provenance_level
            )
            
            # Create lineage nodes
            await self._create_lineage_nodes(certificate_id, module_name, lineage_data)
            
            # Create lineage edges
            await self._create_lineage_edges(certificate_id, module_name, dependencies, lineage_data)
            
            # Update provenance data
            await self._update_provenance_data(certificate_id, module_name, lineage_data)
            
            # Update tracking metrics
            await self._update_lineage_metrics(certificate_id, module_name, lineage_data)
            
            logger.info(f"Successfully tracked lineage for module {module_name} in certificate: {certificate_id}")
            return lineage_data
            
        except Exception as e:
            logger.error(f"Error tracking lineage for module {module_name}: {e}")
            raise
    
    async def _simulate_lineage_data_collection(
        self,
        module_name: str,
        dependencies: List[str],
        provenance_level: ProvenanceLevel
    ) -> Dict[str, Any]:
        """Simulate lineage data collection from a module"""
        try:
            base_data = {
                "module_name": module_name,
                "tracking_started": datetime.utcnow().isoformat(),
                "dependencies": dependencies,
                "data_sources": [],
                "transformations": [],
                "outputs": [],
                "metadata": {}
            }
            
            # Add module-specific lineage data
            if module_name == "aasx_module":
                base_data.update({
                    "data_sources": [
                        {
                            "source_id": "aasx_file_001",
                            "source_type": "file",
                            "file_path": "/data/aasx/input/model.aasx",
                            "file_size_mb": 45.2,
                            "format": "aasx",
                            "validation_status": "validated"
                        }
                    ],
                    "transformations": [
                        {
                            "transformation_id": "parse_aasx",
                            "transformation_type": "parsing",
                            "input_format": "aasx",
                            "output_format": "json",
                            "processing_time_ms": 1250
                        }
                    ],
                    "outputs": [
                        {
                            "output_id": "parsed_data_001",
                            "output_type": "structured_data",
                            "data_size_mb": 12.8,
                            "format": "json",
                            "quality_score": 95.2
                        }
                    ]
                })
            elif module_name == "twin_registry":
                base_data.update({
                    "data_sources": [
                        {
                            "source_id": "parsed_data_001",
                            "source_type": "module_output",
                            "source_module": "aasx_module",
                            "data_format": "json",
                            "data_size_mb": 12.8
                        }
                    ],
                    "transformations": [
                        {
                            "transformation_id": "create_twin",
                            "transformation_type": "modeling",
                            "input_format": "json",
                            "output_format": "twin_model",
                            "processing_time_ms": 890
                        }
                    ],
                    "outputs": [
                        {
                            "output_id": "twin_model_001",
                            "output_type": "digital_twin",
                            "model_type": "asset_twin",
                            "complexity_score": 78.5,
                            "validation_status": "validated"
                        }
                    ]
                })
            elif module_name == "ai_rag":
                base_data.update({
                    "data_sources": [
                        {
                            "source_id": "parsed_data_001",
                            "source_type": "module_output",
                            "source_module": "aasx_module",
                            "data_format": "json",
                            "data_size_mb": 12.8
                        },
                        {
                            "source_id": "twin_model_001",
                            "source_type": "module_output",
                            "source_module": "twin_registry",
                            "data_format": "twin_model",
                            "model_type": "asset_twin"
                        }
                    ],
                    "transformations": [
                        {
                            "transformation_id": "embed_documents",
                            "transformation_type": "embedding",
                            "model": "text-embedding-ada-002",
                            "chunk_size": 512,
                            "processing_time_ms": 2100
                        }
                    ],
                    "outputs": [
                        {
                            "output_id": "knowledge_base_001",
                            "output_type": "vector_database",
                            "document_count": 1250,
                            "embedding_dimensions": 1536,
                            "index_status": "indexed"
                        }
                    ]
                })
            elif module_name == "kg_neo4j":
                base_data.update({
                    "data_sources": [
                        {
                            "source_id": "knowledge_base_001",
                            "source_type": "module_output",
                            "source_module": "ai_rag",
                            "data_format": "vector_database",
                            "document_count": 1250
                        }
                    ],
                    "transformations": [
                        {
                            "transformation_id": "extract_entities",
                            "transformation_type": "entity_extraction",
                            "algorithm": "named_entity_recognition",
                            "confidence_threshold": 0.85,
                            "processing_time_ms": 3400
                        }
                    ],
                    "outputs": [
                        {
                            "output_id": "knowledge_graph_001",
                            "output_type": "graph_database",
                            "node_count": 15420,
                            "relationship_count": 28750,
                            "graph_density": 0.67
                        }
                    ]
                })
            elif module_name == "physics_modeling":
                base_data.update({
                    "data_sources": [
                        {
                            "source_id": "twin_model_001",
                            "source_type": "module_output",
                            "source_module": "twin_registry",
                            "data_format": "twin_model",
                            "model_type": "asset_twin"
                        },
                        {
                            "source_id": "knowledge_graph_001",
                            "source_type": "module_output",
                            "source_module": "kg_neo4j",
                            "data_format": "graph_database",
                            "node_count": 15420
                        }
                    ],
                    "transformations": [
                        {
                            "transformation_id": "simulate_physics",
                            "transformation_type": "simulation",
                            "algorithm": "finite_element_analysis",
                            "mesh_resolution": "high",
                            "processing_time_ms": 15600
                        }
                    ],
                    "outputs": [
                        {
                            "output_id": "simulation_result_001",
                            "output_type": "simulation_output",
                            "result_type": "stress_analysis",
                            "accuracy_score": 87.5,
                            "validation_status": "validated"
                        }
                    ]
                })
            elif module_name == "federated_learning":
                base_data.update({
                    "data_sources": [
                        {
                            "source_id": "simulation_result_001",
                            "source_type": "module_output",
                            "source_module": "physics_modeling",
                            "data_format": "simulation_output",
                            "result_type": "stress_analysis"
                        }
                    ],
                    "transformations": [
                        {
                            "transformation_id": "train_federated_model",
                            "transformation_type": "machine_learning",
                            "algorithm": "federated_averaging",
                            "participant_count": 6,
                            "training_rounds": 15,
                            "processing_time_ms": 45000
                        }
                    ],
                    "outputs": [
                        {
                            "output_id": "ml_model_001",
                            "output_type": "trained_model",
                            "model_type": "neural_network",
                            "accuracy_score": 89.3,
                            "model_size_mb": 45.8
                        }
                    ]
                })
            elif module_name == "data_governance":
                base_data.update({
                    "data_sources": [
                        {
                            "source_id": "all_modules",
                            "source_type": "system_wide",
                            "scope": "entire_system",
                            "data_types": ["aasx", "json", "twin_model", "vector", "graph", "simulation", "ml_model"]
                        }
                    ],
                    "transformations": [
                        {
                            "transformation_id": "apply_governance",
                            "transformation_type": "policy_enforcement",
                            "policies": ["data_quality", "access_control", "retention"],
                            "enforcement_level": "strict",
                            "processing_time_ms": 1200
                        }
                    ],
                    "outputs": [
                        {
                            "output_id": "governance_report_001",
                            "output_type": "compliance_report",
                            "compliance_score": 93.1,
                            "audit_status": "audited",
                            "policy_violations": 0
                        }
                    ]
                })
            
            # Add provenance level specific data
            if provenance_level == ProvenanceLevel.DETAILED:
                base_data["metadata"]["detailed_tracking"] = True
                base_data["metadata"]["tracking_granularity"] = "high"
            elif provenance_level == ProvenanceLevel.COMPREHENSIVE:
                base_data["metadata"]["comprehensive_tracking"] = True
                base_data["metadata"]["tracking_granularity"] = "maximum"
                base_data["metadata"]["audit_trail"] = True
            
            return base_data
            
        except Exception as e:
            logger.error(f"Error simulating lineage data collection: {e}")
            return {}
    
    async def _create_lineage_nodes(
        self,
        certificate_id: str,
        module_name: str,
        lineage_data: Dict[str, Any]
    ) -> None:
        """Create lineage nodes for a module"""
        try:
            graph = self.lineage_graphs[certificate_id]
            
            # Create main module node
            module_node = LineageNode(
                node_id=f"{certificate_id}_{module_name}",
                node_type="module",
                node_name=module_name,
                metadata={
                    "module_name": module_name,
                    "tracking_started": lineage_data.get("tracking_started"),
                    "dependencies": lineage_data.get("dependencies", [])
                },
                timestamp=datetime.utcnow()
            )
            graph[module_node.node_id] = module_node
            
            # Create data source nodes
            for source in lineage_data.get("data_sources", []):
                source_node = LineageNode(
                    node_id=f"{certificate_id}_{module_name}_{source.get('source_id', 'unknown')}",
                    node_type="data_source",
                    node_name=source.get("source_id", "unknown"),
                    metadata=source,
                    timestamp=datetime.utcnow()
                )
                graph[source_node.node_id] = source_node
            
            # Create transformation nodes
            for transformation in lineage_data.get("transformations", []):
                transform_node = LineageNode(
                    node_id=f"{certificate_id}_{module_name}_{transformation.get('transformation_id', 'unknown')}",
                    node_type="transformation",
                    node_name=transformation.get("transformation_id", "unknown"),
                    metadata=transformation,
                    timestamp=datetime.utcnow()
                )
                graph[transform_node.node_id] = transform_node
            
            # Create output nodes
            for output in lineage_data.get("outputs", []):
                output_node = LineageNode(
                    node_id=f"{certificate_id}_{module_name}_{output.get('output_id', 'unknown')}",
                    node_type="output",
                    node_name=output.get("output_id", "unknown"),
                    metadata=output,
                    timestamp=datetime.utcnow()
                )
                graph[output_node.node_id] = output_node
            
        except Exception as e:
            logger.error(f"Error creating lineage nodes: {e}")
    
    async def _create_lineage_edges(
        self,
        certificate_id: str,
        module_name: str,
        dependencies: List[str],
        lineage_data: Dict[str, Any]
    ) -> None:
        """Create lineage edges for a module"""
        try:
            edges = self.lineage_edges[certificate_id]
            graph = self.lineage_graphs[certificate_id]
            
            # Create dependency edges
            for dependency in dependencies:
                dependency_edge = LineageEdge(
                    edge_id=f"{certificate_id}_{dependency}_to_{module_name}",
                    source_node=f"{certificate_id}_{dependency}",
                    target_node=f"{certificate_id}_{module_name}",
                    edge_type="depends_on",
                    metadata={
                        "dependency_type": "module_dependency",
                        "strength": "strong"
                    },
                    timestamp=datetime.utcnow()
                )
                edges.append(dependency_edge)
                
                # Update node edge lists
                if dependency_edge.source_node in graph:
                    graph[dependency_edge.source_node].outgoing_edges.append(dependency_edge.edge_id)
                if dependency_edge.target_node in graph:
                    graph[dependency_edge.target_node].incoming_edges.append(dependency_edge.edge_id)
            
            # Create data flow edges
            for source in lineage_data.get("data_sources", []):
                source_id = source.get("source_id")
                if source_id:
                    # Connect data source to module
                    data_edge = LineageEdge(
                        edge_id=f"{certificate_id}_{source_id}_to_{module_name}",
                        source_node=f"{certificate_id}_{module_name}_{source_id}",
                        target_node=f"{certificate_id}_{module_name}",
                        edge_type="feeds_into",
                        metadata={
                            "data_flow_type": "input",
                            "data_format": source.get("format", "unknown")
                        },
                        timestamp=datetime.utcnow()
                    )
                    edges.append(data_edge)
                    
                    # Update node edge lists
                    if data_edge.source_node in graph:
                        graph[data_edge.source_node].outgoing_edges.append(data_edge.edge_id)
                    if data_edge.target_node in graph:
                        graph[data_edge.target_node].incoming_edges.append(data_edge.edge_id)
            
            # Create transformation flow edges
            for transformation in lineage_data.get("transformations", []):
                transform_id = transformation.get("transformation_id")
                if transform_id:
                    # Connect module to transformation
                    transform_edge = LineageEdge(
                        edge_id=f"{certificate_id}_{module_name}_to_{transform_id}",
                        source_node=f"{certificate_id}_{module_name}",
                        target_node=f"{certificate_id}_{module_name}_{transform_id}",
                        edge_type="performs",
                        metadata={
                            "transformation_type": transformation.get("transformation_type", "unknown"),
                            "processing_time_ms": transformation.get("processing_time_ms", 0)
                        },
                        timestamp=datetime.utcnow()
                    )
                    edges.append(transform_edge)
                    
                    # Update node edge lists
                    if transform_edge.source_node in graph:
                        graph[transform_edge.source_node].outgoing_edges.append(transform_edge.edge_id)
                    if transform_edge.target_node in graph:
                        graph[transform_edge.target_node].incoming_edges.append(transform_edge.edge_id)
            
            # Create output flow edges
            for output in lineage_data.get("outputs", []):
                output_id = output.get("output_id")
                if output_id:
                    # Connect transformation to output
                    output_edge = LineageEdge(
                        edge_id=f"{certificate_id}_{module_name}_to_{output_id}",
                        source_node=f"{certificate_id}_{module_name}",
                        target_node=f"{certificate_id}_{module_name}_{output_id}",
                        edge_type="produces",
                        metadata={
                            "output_type": output.get("output_type", "unknown"),
                            "quality_score": output.get("quality_score", 0)
                        },
                        timestamp=datetime.utcnow()
                    )
                    edges.append(output_edge)
                    
                    # Update node edge lists
                    if output_edge.source_node in graph:
                        graph[output_edge.source_node].outgoing_edges.append(output_edge.edge_id)
                    if output_edge.target_node in graph:
                        graph[output_edge.target_node].incoming_edges.append(output_edge.edge_id)
            
        except Exception as e:
            logger.error(f"Error creating lineage edges: {e}")
    
    async def _update_provenance_data(
        self,
        certificate_id: str,
        module_name: str,
        lineage_data: Dict[str, Any]
    ) -> None:
        """Update provenance data for a module"""
        try:
            provenance = self.provenance_data[certificate_id]
            
            # Add module to tracked modules
            if module_name not in provenance["modules_tracked"]:
                provenance["modules_tracked"].append(module_name)
            
            # Add data sources
            for source in lineage_data.get("data_sources", []):
                provenance["data_sources"].append({
                    "module": module_name,
                    "source": source,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Add transformations
            for transformation in lineage_data.get("transformations", []):
                provenance["transformations"].append({
                    "module": module_name,
                    "transformation": transformation,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Error updating provenance data: {e}")
    
    async def _update_lineage_metrics(
        self,
        certificate_id: str,
        module_name: str,
        lineage_data: Dict[str, Any]
    ) -> None:
        """Update lineage tracking metrics"""
        try:
            # Track lineage coverage
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.QUALITY,
                metric_name=f"{module_name}_lineage_coverage",
                metric_value=100.0,
                metric_unit="percentage",
                additional_data={
                    "module_name": module_name,
                    "data_sources_count": len(lineage_data.get("data_sources", [])),
                    "transformations_count": len(lineage_data.get("transformations", [])),
                    "outputs_count": len(lineage_data.get("outputs", [])),
                    "tracking_timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating lineage metrics: {e}")
    
    async def _build_lineage_graph(self, certificate_id: str) -> None:
        """Build complete lineage graph for a certificate"""
        try:
            # This method would typically perform graph optimization,
            # cycle detection, and other graph analysis
            logger.info(f"Built lineage graph for certificate: {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error building lineage graph: {e}")
    
    async def _generate_lineage_summary(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Generate comprehensive lineage summary"""
        try:
            graph = self.lineage_graphs.get(certificate_id, {})
            edges = self.lineage_edges.get(certificate_id, [])
            
            # Count node types
            node_types = defaultdict(int)
            for node in graph.values():
                node_types[node.node_type] += 1
            
            # Count edge types
            edge_types = defaultdict(int)
            for edge in edges:
                edge_types[edge.edge_type] += 1
            
            # Calculate graph metrics
            total_nodes = len(graph)
            total_edges = len(edges)
            graph_density = total_edges / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0
            
            summary = {
                "certificate_id": certificate_id,
                "generated_at": datetime.utcnow().isoformat(),
                "graph_metrics": {
                    "total_nodes": total_nodes,
                    "total_edges": total_edges,
                    "graph_density": round(graph_density, 4),
                    "node_types": dict(node_types),
                    "edge_types": dict(edge_types)
                },
                "module_coverage": len([n for n in graph.values() if n.node_type == "module"]),
                "data_flow_complexity": len([e for e in edges if e.edge_type in ["feeds_into", "produces"]]),
                "dependency_depth": self._calculate_dependency_depth(certificate_id),
                "provenance_level": self.provenance_data.get(certificate_id, {}).get("provenance_level", "unknown")
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating lineage summary: {e}")
            return None
    
    def _calculate_dependency_depth(self, certificate_id: str) -> int:
        """Calculate maximum dependency depth in the lineage graph"""
        try:
            graph = self.lineage_graphs.get(certificate_id, {})
            edges = self.lineage_edges.get(certificate_id, [])
            
            # Find root nodes (no incoming edges)
            root_nodes = [node_id for node_id, node in graph.items() if not node.incoming_edges]
            
            if not root_nodes:
                return 0
            
            # Calculate depth using BFS
            max_depth = 0
            visited = set()
            
            for root in root_nodes:
                queue = [(root, 0)]
                while queue:
                    node_id, depth = queue.pop(0)
                    if node_id in visited:
                        continue
                    
                    visited.add(node_id)
                    max_depth = max(max_depth, depth)
                    
                    # Add outgoing edges
                    for edge in edges:
                        if edge.source_node == node_id:
                            queue.append((edge.target_node, depth + 1))
            
            return max_depth
            
        except Exception as e:
            logger.error(f"Error calculating dependency depth: {e}")
            return 0
    
    async def _record_lineage_history(
        self,
        certificate_id: str,
        results: List[Any],
        summary: Optional[Dict[str, Any]]
    ) -> None:
        """Record lineage tracking history"""
        try:
            if certificate_id not in self.lineage_history:
                self.lineage_history[certificate_id] = []
            
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "results_count": len(results),
                "successful_tracking": sum(1 for r in results if not isinstance(r, Exception)),
                "failed_tracking": sum(1 for r in results if isinstance(r, Exception)),
                "summary_generated": summary is not None,
                "graph_metrics": summary.get("graph_metrics", {}) if summary else {},
                "module_coverage": summary.get("module_coverage", 0) if summary else 0
            }
            
            self.lineage_history[certificate_id].append(history_entry)
            
            # Keep only last 10 entries
            if len(self.lineage_history[certificate_id]) > 10:
                self.lineage_history[certificate_id] = self.lineage_history[certificate_id][-10:]
                
        except Exception as e:
            logger.error(f"Error recording lineage history: {e}")
    
    async def get_lineage_graph(self, certificate_id: str) -> Dict[str, Any]:
        """Get complete lineage graph for a certificate"""
        try:
            graph = self.lineage_graphs.get(certificate_id, {})
            edges = self.lineage_edges.get(certificate_id, [])
            
            # Convert to serializable format
            serializable_graph = {}
            for node_id, node in graph.items():
                serializable_graph[node_id] = {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "node_name": node.node_name,
                    "metadata": node.metadata,
                    "timestamp": node.timestamp.isoformat(),
                    "incoming_edges": node.incoming_edges,
                    "outgoing_edges": node.outgoing_edges
                }
            
            serializable_edges = []
            for edge in edges:
                serializable_edges.append({
                    "edge_id": edge.edge_id,
                    "source_node": edge.source_node,
                    "target_node": edge.target_node,
                    "edge_type": edge.edge_type,
                    "metadata": edge.metadata,
                    "timestamp": edge.timestamp.isoformat()
                })
            
            return {
                "nodes": serializable_graph,
                "edges": serializable_edges,
                "metadata": {
                    "certificate_id": certificate_id,
                    "generated_at": datetime.utcnow().isoformat(),
                    "total_nodes": len(graph),
                    "total_edges": len(edges)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting lineage graph: {e}")
            return {}
    
    async def get_data_provenance(self, certificate_id: str, data_id: str) -> Optional[Dict[str, Any]]:
        """Get provenance information for specific data"""
        try:
            graph = self.lineage_graphs.get(certificate_id, {})
            edges = self.lineage_edges.get(certificate_id, [])
            
            # Find the data node
            data_node = None
            for node in graph.values():
                if (node.node_type in ["data_source", "output"] and 
                    data_id in node.node_name):
                    data_node = node
                    break
            
            if not data_node:
                return None
            
            # Build provenance chain
            provenance_chain = await self._build_provenance_chain(
                certificate_id, data_node.node_id, graph, edges
            )
            
            return {
                "data_id": data_id,
                "certificate_id": certificate_id,
                "provenance_chain": provenance_chain,
                "metadata": data_node.metadata,
                "timestamp": data_node.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting data provenance: {e}")
            return None
    
    async def _build_provenance_chain(
        self,
        certificate_id: str,
        node_id: str,
        graph: Dict[str, LineageNode],
        edges: List[LineageEdge]
    ) -> List[Dict[str, Any]]:
        """Build provenance chain for a node"""
        try:
            chain = []
            visited = set()
            
            def traverse_backwards(current_node_id: str, depth: int = 0):
                if current_node_id in visited or depth > 10:  # Prevent infinite loops
                    return
                
                visited.add(current_node_id)
                current_node = graph.get(current_node_id)
                if not current_node:
                    return
                
                chain.append({
                    "node_id": current_node.node_id,
                    "node_type": current_node.node_type,
                    "node_name": current_node.node_name,
                    "depth": depth,
                    "metadata": current_node.metadata,
                    "timestamp": current_node.timestamp.isoformat()
                })
                
                # Find incoming edges
                for edge in edges:
                    if edge.target_node == current_node_id:
                        traverse_backwards(edge.source_node, depth + 1)
            
            traverse_backwards(node_id)
            return chain
            
        except Exception as e:
            logger.error(f"Error building provenance chain: {e}")
            return []
    
    async def get_lineage_summary(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get lineage summary for a certificate"""
        try:
            return await self._generate_lineage_summary(certificate_id)
        except Exception as e:
            logger.error(f"Error getting lineage summary: {e}")
            return None
    
    async def get_lineage_history(self, certificate_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get lineage tracking history for a certificate"""
        try:
            return self.lineage_history.get(certificate_id, [])[-limit:]
        except Exception as e:
            logger.error(f"Error getting lineage history: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the lineage tracker"""
        try:
            health_status = {
                "status": "healthy",
                "active_graphs": len(self.lineage_graphs),
                "total_nodes": sum(len(graph) for graph in self.lineage_graphs.values()),
                "total_edges": sum(len(edges) for edges in self.lineage_edges.values()),
                "active_locks": len(self.lineage_locks),
                "lineage_history_size": sum(len(h) for h in self.lineage_history.values()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
