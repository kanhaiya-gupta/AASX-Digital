"""
AI RAG Graph Validator
======================

Validates graph structures for integrity, quality, and consistency.
"""

import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime

from ..graph_models.graph_node import GraphNode
from ..graph_models.graph_edge import GraphEdge
from ..graph_models.graph_structure import GraphStructure

logger = logging.getLogger(__name__)


class GraphValidator:
    """
    Graph Validator for AI RAG Graph Generation
    
    Validates graph structures for integrity, quality, and consistency,
    including structural validation, semantic validation, and quality assessment.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the graph validator.
        
        Args:
            config: Configuration dictionary for validation parameters
        """
        self.config = config or self._get_default_config()
        self.validation_stats = {
            "total_graphs_validated": 0,
            "validation_time_ms": 0,
            "validation_results": {
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "common_issues": {}
        }
        
        logger.info("✅ GraphValidator initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for graph validation."""
        return {
            "enable_structural_validation": True,
            "enable_semantic_validation": True,
            "enable_quality_validation": True,
            "enable_performance_validation": True,
            "min_quality_score": 0.6,
            "max_validation_time_ms": 30000,  # 30 seconds
            "strict_mode": False,  # If True, warnings are treated as errors
            "validation_levels": ["basic", "intermediate", "advanced"],
            "quality_weights": {
                "structural": 0.3,
                "semantic": 0.3,
                "quality": 0.2,
                "performance": 0.2
            }
        }
    
    async def validate_graph(
        self,
        graph: GraphStructure,
        validation_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Validate a graph structure.
        
        Args:
            graph: Graph structure to validate
            validation_level: Level of validation (basic, intermediate, advanced)
            
        Returns:
            Dict: Validation results including status, issues, and recommendations
        """
        start_time = datetime.now()
        logger.info(f"🔍 Starting graph validation: {graph.graph_name} at {validation_level} level")
        
        try:
            validation_results = {
                "graph_id": graph.graph_id,
                "graph_name": graph.graph_name,
                "validation_level": validation_level,
                "validation_timestamp": datetime.now().isoformat(),
                "overall_status": "unknown",
                "score": 0.0,
                "issues": [],
                "warnings": [],
                "recommendations": [],
                "validation_details": {}
            }
            
            # Perform different types of validation
            if self.config["enable_structural_validation"]:
                structural_result = await self._validate_structure(graph, validation_level)
                validation_results["validation_details"]["structural"] = structural_result
            
            if self.config["enable_semantic_validation"]:
                semantic_result = await self._validate_semantics(graph, validation_level)
                validation_results["validation_details"]["semantic"] = semantic_result
            
            if self.config["enable_quality_validation"]:
                quality_result = await self._validate_quality(graph, validation_level)
                validation_results["validation_details"]["quality"] = quality_result
            
            if self.config["enable_performance_validation"]:
                performance_result = await self._validate_performance(graph, validation_level)
                validation_results["validation_details"]["performance"] = performance_result
            
            # Calculate overall validation score
            overall_score = self._calculate_overall_score(validation_results["validation_details"])
            validation_results["score"] = overall_score
            
            # Determine overall status
            validation_results["overall_status"] = self._determine_overall_status(
                overall_score, validation_results["issues"], validation_results["warnings"]
            )
            
            # Generate recommendations
            validation_results["recommendations"] = self._generate_recommendations(
                validation_results["validation_details"], overall_score
            )
            
            # Update validation statistics
            self._update_validation_stats(validation_results, start_time)
            
            logger.info(f"✅ Graph validation completed: {graph.graph_name} - Status: {validation_results['overall_status']}, Score: {overall_score:.2f}")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Graph validation failed: {e}")
            return {
                "graph_id": graph.graph_id,
                "graph_name": graph.graph_name,
                "validation_level": validation_level,
                "validation_timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "score": 0.0,
                "issues": [f"Validation error: {str(e)}"],
                "warnings": [],
                "recommendations": ["Fix validation error and retry"],
                "validation_details": {}
            }
    
    async def _validate_structure(
        self,
        graph: GraphStructure,
        validation_level: str
    ) -> Dict[str, Any]:
        """Validate graph structure integrity."""
        result = {
            "status": "unknown",
            "score": 0.0,
            "issues": [],
            "warnings": [],
            "details": {}
        }
        
        try:
            # Basic structural validation
            basic_issues = self._validate_basic_structure(graph)
            result["issues"].extend(basic_issues)
            
            # Intermediate structural validation
            if validation_level in ["intermediate", "advanced"]:
                intermediate_issues = self._validate_intermediate_structure(graph)
                result["issues"].extend(intermediate_issues)
            
            # Advanced structural validation
            if validation_level == "advanced":
                advanced_issues = self._validate_advanced_structure(graph)
                result["issues"].extend(advanced_issues)
            
            # Calculate structural score
            result["score"] = self._calculate_structural_score(graph, result["issues"], result["warnings"])
            result["status"] = "passed" if result["score"] >= 0.7 else "failed"
            
            return result
            
        except Exception as e:
            result["issues"].append(f"Structural validation error: {str(e)}")
            result["status"] = "error"
            result["score"] = 0.0
            return result
    
    def _validate_basic_structure(self, graph: GraphStructure) -> List[str]:
        """Perform basic structural validation."""
        issues = []
        
        # Check for empty graph
        if not graph.nodes:
            issues.append("Graph has no nodes")
        
        if not graph.edges:
            issues.append("Graph has no edges")
        
        # Check for orphaned nodes
        connected_nodes = set()
        for edge in graph.edges:
            connected_nodes.add(edge.source_node_id)
            connected_nodes.add(edge.target_node_id)
        
        orphaned_nodes = [node.node_id for node in graph.nodes if node.node_id not in connected_nodes]
        if orphaned_nodes:
            issues.append(f"Found {len(orphaned_nodes)} orphaned nodes")
        
        # Check for self-loops
        self_loops = [edge.edge_id for edge in graph.edges if edge.source_node_id == edge.target_node_id]
        if self_loops:
            issues.append(f"Found {len(self_loops)} self-loop edges")
        
        return issues
    
    def _validate_intermediate_structure(self, graph: GraphStructure) -> List[str]:
        """Perform intermediate structural validation."""
        issues = []
        
        # Check for duplicate edges
        edge_pairs = set()
        duplicate_edges = []
        for edge in graph.edges:
            pair = (edge.source_node_id, edge.target_node_id, edge.relationship_type)
            if pair in edge_pairs:
                duplicate_edges.append(edge.edge_id)
            edge_pairs.add(pair)
        
        if duplicate_edges:
            issues.append(f"Found {len(duplicate_edges)} duplicate edges")
        
        # Check for disconnected components
        if graph.connected_components > 1:
            issues.append(f"Graph has {graph.connected_components} disconnected components")
        
        # Check graph density
        if graph.graph_density < 0.01:
            issues.append("Graph density is very low (sparse graph)")
        elif graph.graph_density > 0.9:
            issues.append("Graph density is very high (dense graph)")
        
        return issues
    
    def _validate_advanced_structure(self, graph: GraphStructure) -> List[str]:
        """Perform advanced structural validation."""
        issues = []
        
        # Check for cycles in directed graphs
        cycles = self._detect_cycles(graph)
        if cycles:
            issues.append(f"Found {len(cycles)} cycles in directed graph")
        
        # Check for balanced relationships
        unbalanced_relationships = self._check_relationship_balance(graph)
        if unbalanced_relationships:
            issues.append(f"Found {len(unbalanced_relationships)} unbalanced relationships")
        
        # Check for clustering quality
        cluster_quality = self._assess_clustering_quality(graph)
        if cluster_quality < 0.5:
            issues.append("Graph clustering quality is low")
        
        return issues
    
    def _detect_cycles(self, graph: GraphStructure) -> List[List[str]]:
        """Detect cycles in the directed graph."""
        # Simple cycle detection using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node_id, path):
            if node_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(node_id)
                cycles.append(path[cycle_start:])
                return
            
            if node_id in visited:
                return
            
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            # Find outgoing edges
            for edge in graph.edges:
                if edge.source_node_id == node_id and edge.is_directed:
                    dfs(edge.target_node_id, path.copy())
            
            rec_stack.remove(node_id)
        
        # Start DFS from each node
        for node in graph.nodes:
            if node.node_id not in visited:
                dfs(node.node_id, [])
        
        return cycles
    
    def _check_relationship_balance(self, graph: GraphStructure) -> List[str]:
        """Check for balanced relationships."""
        unbalanced = []
        
        # Check for nodes with very high in-degree or out-degree
        in_degree = {}
        out_degree = {}
        
        for edge in graph.edges:
            source = edge.source_node_id
            target = edge.target_node_id
            
            out_degree[source] = out_degree.get(source, 0) + 1
            in_degree[target] = in_degree.get(target, 0) + 1
        
        # Find nodes with extreme degrees
        for node in graph.nodes:
            node_id = node.node_id
            out_deg = out_degree.get(node_id, 0)
            in_deg = in_degree.get(node_id, 0)
            
            if out_deg > 20 or in_deg > 20:
                unbalanced.append(node_id)
        
        return unbalanced
    
    def _assess_clustering_quality(self, graph: GraphStructure) -> float:
        """Assess the quality of graph clustering."""
        if not graph.nodes:
            return 0.0
        
        # Simple clustering quality based on node type distribution
        node_types = {}
        for node in graph.nodes:
            node_type = node.node_type
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Calculate entropy (lower is better for clustering)
        total_nodes = len(graph.nodes)
        entropy = 0.0
        
        for count in node_types.values():
            p = count / total_nodes
            if p > 0:
                entropy -= p * (p.bit_length() - 1)  # Simplified entropy calculation
        
        # Normalize to 0-1 scale (1 is best clustering)
        max_entropy = (len(node_types).bit_length() - 1) if node_types else 1
        quality = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 0.0
        
        return max(0.0, min(1.0, quality))
    
    async def _validate_semantics(
        self,
        graph: GraphStructure,
        validation_level: str
    ) -> Dict[str, Any]:
        """Validate graph semantic consistency."""
        result = {
            "status": "unknown",
            "score": 0.0,
            "issues": [],
            "warnings": [],
            "details": {}
        }
        
        try:
            # Check entity type consistency
            type_issues = self._validate_entity_types(graph)
            result["issues"].extend(type_issues)
            
            # Check relationship type consistency
            rel_issues = self._validate_relationship_types(graph)
            result["issues"].extend(rel_issues)
            
            # Check semantic coherence
            coherence_issues = self._validate_semantic_coherence(graph)
            result["issues"].extend(coherence_issues)
            
            # Calculate semantic score
            result["score"] = self._calculate_semantic_score(graph, result["issues"], result["warnings"])
            result["status"] = "passed" if result["score"] >= 0.7 else "failed"
            
            return result
            
        except Exception as e:
            result["issues"].append(f"Semantic validation error: {str(e)}")
            result["status"] = "error"
            result["score"] = 0.0
            return result
    
    def _validate_entity_types(self, graph: GraphStructure) -> List[str]:
        """Validate entity type consistency."""
        issues = []
        
        # Check for invalid entity types
        valid_types = {"entity", "concept", "document", "process", "system", "component", "interface", "technology"}
        
        for node in graph.nodes:
            if node.node_type not in valid_types:
                issues.append(f"Invalid entity type '{node.node_type}' for node '{node.node_label}'")
        
        # Check for type distribution
        type_counts = {}
        for node in graph.nodes:
            node_type = node.node_type
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        # Warn about skewed type distribution
        total_nodes = len(graph.nodes)
        for node_type, count in type_counts.items():
            if count / total_nodes > 0.8:
                issues.append(f"Entity type '{node_type}' dominates the graph ({count}/{total_nodes} nodes)")
        
        return issues
    
    def _validate_relationship_types(self, graph: GraphStructure) -> List[str]:
        """Validate relationship type consistency."""
        issues = []
        
        # Check for invalid relationship types
        valid_rel_types = {
            "contains", "depends_on", "relates_to", "implements", "extends",
            "uses", "creates", "modifies", "triggers", "follows", "precedes"
        }
        
        for edge in graph.edges:
            if edge.relationship_type not in valid_rel_types:
                issues.append(f"Invalid relationship type '{edge.relationship_type}' for edge '{edge.edge_id}'")
        
        # Check for relationship type distribution
        rel_type_counts = {}
        for edge in graph.edges:
            rel_type = edge.relationship_type
            rel_type_counts[rel_type] = rel_type_counts.get(rel_type, 0) + 1
        
        # Warn about overused relationship types
        total_edges = len(graph.edges)
        for rel_type, count in rel_type_counts.items():
            if count / total_edges > 0.6:
                issues.append(f"Relationship type '{rel_type}' is overused ({count}/{total_edges} edges)")
        
        return issues
    
    def _validate_semantic_coherence(self, graph: GraphStructure) -> List[str]:
        """Validate semantic coherence of the graph."""
        issues = []
        
        # Check for semantically inconsistent relationships
        for edge in graph.edges:
            source_node = graph.get_node(edge.source_node_id)
            target_node = graph.get_node(edge.target_node_id)
            
            if source_node and target_node:
                # Check for impossible relationships
                if edge.relationship_type == "contains":
                    if source_node.node_type == "component" and target_node.node_type == "system":
                        issues.append(f"Semantic inconsistency: component '{source_node.node_label}' cannot contain system '{target_node.node_label}'")
                
                elif edge.relationship_type == "implements":
                    if source_node.node_type not in ["interface", "component"]:
                        issues.append(f"Semantic inconsistency: '{source_node.node_type}' cannot implement relationships")
        
        return issues
    
    async def _validate_quality(
        self,
        graph: GraphStructure,
        validation_level: str
    ) -> Dict[str, Any]:
        """Validate graph quality metrics."""
        result = {
            "status": "unknown",
            "score": 0.0,
            "issues": [],
            "warnings": [],
            "details": {}
        }
        
        try:
            # Check node quality
            node_quality_issues = self._validate_node_quality(graph)
            result["issues"].extend(node_quality_issues)
            
            # Check edge quality
            edge_quality_issues = self._validate_edge_quality(graph)
            result["issues"].extend(edge_quality_issues)
            
            # Check overall graph quality
            graph_quality_issues = self._validate_graph_quality(graph)
            result["issues"].extend(graph_quality_issues)
            
            # Calculate quality score
            result["score"] = self._calculate_quality_score(graph, result["issues"], result["warnings"])
            result["status"] = "passed" if result["score"] >= 0.7 else "failed"
            
            return result
            
        except Exception as e:
            result["issues"].append(f"Quality validation error: {str(e)}")
            result["status"] = "error"
            result["score"] = 0.0
            return result
    
    def _validate_node_quality(self, graph: GraphStructure) -> List[str]:
        """Validate node quality metrics."""
        issues = []
        
        # Check for low-confidence nodes
        low_confidence_nodes = [node.node_id for node in graph.nodes if node.confidence_score < 0.5]
        if low_confidence_nodes:
            issues.append(f"Found {len(low_confidence_nodes)} nodes with low confidence (< 0.5)")
        
        # Check for nodes without properties
        empty_property_nodes = [node.node_id for node in graph.nodes if not node.properties_dict]
        if empty_property_nodes:
            issues.append(f"Found {len(empty_property_nodes)} nodes without properties")
        
        # Check for nodes without source text
        no_source_nodes = [node.node_id for node in graph.nodes if not node.source_text]
        if no_source_nodes:
            issues.append(f"Found {len(no_source_nodes)} nodes without source text")
        
        return issues
    
    def _validate_edge_quality(self, graph: GraphStructure) -> List[str]:
        """Validate edge quality metrics."""
        issues = []
        
        # Check for low-confidence edges
        low_confidence_edges = [edge.edge_id for edge in graph.edges if edge.confidence_score < 0.5]
        if low_confidence_edges:
            issues.append(f"Found {len(low_confidence_edges)} edges with low confidence (< 0.5)")
        
        # Check for edges without properties
        empty_property_edges = [edge.edge_id for edge in graph.edges if not edge.properties_dict]
        if empty_property_edges:
            issues.append(f"Found {len(empty_property_edges)} edges without properties")
        
        # Check for edges with extreme weights
        extreme_weight_edges = [edge.edge_id for edge in graph.edges if edge.weight < 0.1 or edge.weight > 9.9]
        if extreme_weight_edges:
            issues.append(f"Found {len(extreme_weight_edges)} edges with extreme weights")
        
        return issues
    
    def _validate_graph_quality(self, graph: GraphStructure) -> List[str]:
        """Validate overall graph quality."""
        issues = []
        
        # Check overall quality score
        if graph.overall_quality_score < self.config["min_quality_score"]:
            issues.append(f"Graph quality score {graph.overall_quality_score:.2f} is below threshold {self.config['min_quality_score']}")
        
        # Check for validation errors
        if graph.has_validation_errors:
            issues.append(f"Graph has {len(graph.validation_errors_list)} validation errors")
        
        # Check for processing status
        if graph.is_processing:
            issues.append("Graph is still processing")
        
        return issues
    
    async def _validate_performance(
        self,
        graph: GraphStructure,
        validation_level: str
    ) -> Dict[str, Any]:
        """Validate graph performance characteristics."""
        result = {
            "status": "unknown",
            "score": 0.0,
            "issues": [],
            "warnings": [],
            "details": {}
        }
        
        try:
            # Check graph size
            size_issues = self._validate_graph_size(graph)
            result["issues"].extend(size_issues)
            
            # Check graph complexity
            complexity_issues = self._validate_graph_complexity(graph)
            result["issues"].extend(complexity_issues)
            
            # Check performance metrics
            performance_issues = self._validate_performance_metrics(graph)
            result["issues"].extend(performance_issues)
            
            # Calculate performance score
            result["score"] = self._calculate_performance_score(graph, result["issues"], result["warnings"])
            result["status"] = "passed" if result["score"] >= 0.7 else "failed"
            
            return result
            
        except Exception as e:
            result["issues"].append(f"Performance validation error: {str(e)}")
            result["status"] = "error"
            result["score"] = 0.0
            return result
    
    def _validate_graph_size(self, graph: GraphStructure) -> List[str]:
        """Validate graph size characteristics."""
        issues = []
        
        # Check for very large graphs
        if graph.node_count > 10000:
            issues.append(f"Graph is very large with {graph.node_count} nodes (may impact performance)")
        
        if graph.edge_count > 50000:
            issues.append(f"Graph is very dense with {graph.edge_count} edges (may impact performance)")
        
        # Check for very small graphs
        if graph.node_count < 3:
            issues.append("Graph is very small (may not be meaningful)")
        
        return issues
    
    def _validate_graph_complexity(self, graph: GraphStructure) -> List[str]:
        """Validate graph complexity characteristics."""
        issues = []
        
        # Check graph density
        if graph.graph_density > 0.8:
            issues.append(f"Graph density {graph.graph_density:.2f} is very high (may be over-connected)")
        
        # Check for long paths
        if graph.graph_diameter > 20:
            issues.append(f"Graph diameter {graph.graph_diameter} is very long (may be inefficient)")
        
        return issues
    
    def _validate_performance_metrics(self, graph: GraphStructure) -> List[str]:
        """Validate performance-related metrics."""
        issues = []
        
        # Check for performance metrics in graph metadata
        # This would typically come from the graph metadata model
        # For now, we'll check basic structural performance indicators
        
        # Check for highly connected nodes (hubs)
        in_degree = {}
        out_degree = {}
        
        for edge in graph.edges:
            source = edge.source_node_id
            target = edge.target_node_id
            
            out_degree[source] = out_degree.get(source, 0) + 1
            in_degree[target] = in_degree.get(target, 0) + 1
        
        # Find hub nodes
        hub_threshold = min(50, len(graph.nodes) // 10)  # Adaptive threshold
        hub_nodes = []
        
        for node in graph.nodes:
            node_id = node.node_id
            total_degree = (out_degree.get(node_id, 0) + in_degree.get(node_id, 0))
            if total_degree > hub_threshold:
                hub_nodes.append(node_id)
        
        if hub_nodes:
            issues.append(f"Found {len(hub_nodes)} hub nodes with high connectivity (may cause performance bottlenecks)")
        
        return issues
    
    def _calculate_structural_score(
        self,
        graph: GraphStructure,
        issues: List[str],
        warnings: List[str]
    ) -> float:
        """Calculate structural validation score."""
        base_score = 1.0
        
        # Deduct points for issues
        issue_penalty = len(issues) * 0.1
        warning_penalty = len(warnings) * 0.05
        
        score = max(0.0, base_score - issue_penalty - warning_penalty)
        
        # Bonus for good structure
        if graph.is_connected:
            score += 0.1
        
        if 0.1 <= graph.graph_density <= 0.8:
            score += 0.05
        
        return min(1.0, score)
    
    def _calculate_semantic_score(
        self,
        graph: GraphStructure,
        issues: List[str],
        warnings: List[str]
    ) -> float:
        """Calculate semantic validation score."""
        base_score = 1.0
        
        # Deduct points for issues
        issue_penalty = len(issues) * 0.1
        warning_penalty = len(warnings) * 0.05
        
        score = max(0.0, base_score - issue_penalty - warning_penalty)
        
        # Bonus for semantic consistency
        valid_entity_types = {"entity", "concept", "document", "process", "system", "component", "interface", "technology"}
        valid_rel_types = {"contains", "depends_on", "relates_to", "implements", "extends", "uses", "creates", "modifies", "triggers", "follows", "precedes"}
        
        entity_type_score = sum(1 for node in graph.nodes if node.node_type in valid_entity_types) / len(graph.nodes) if graph.nodes else 0
        rel_type_score = sum(1 for edge in graph.edges if edge.relationship_type in valid_rel_types) / len(graph.edges) if graph.edges else 0
        
        score += (entity_type_score + rel_type_score) * 0.1
        
        return min(1.0, score)
    
    def _calculate_quality_score(
        self,
        graph: GraphStructure,
        issues: List[str],
        warnings: List[str]
    ) -> float:
        """Calculate quality validation score."""
        base_score = graph.overall_quality_score
        
        # Deduct points for issues
        issue_penalty = len(issues) * 0.05
        warning_penalty = len(warnings) * 0.02
        
        score = max(0.0, base_score - issue_penalty - warning_penalty)
        
        return min(1.0, score)
    
    def _calculate_performance_score(
        self,
        graph: GraphStructure,
        issues: List[str],
        warnings: List[str]
    ) -> float:
        """Calculate performance validation score."""
        base_score = 1.0
        
        # Deduct points for issues
        issue_penalty = len(issues) * 0.1
        warning_penalty = len(warnings) * 0.05
        
        score = max(0.0, base_score - issue_penalty - warning_penalty)
        
        # Bonus for good performance characteristics
        if graph.node_count <= 1000:
            score += 0.1
        
        if graph.edge_count <= 5000:
            score += 0.1
        
        if graph.graph_density <= 0.5:
            score += 0.05
        
        return min(1.0, score)
    
    def _calculate_overall_score(self, validation_details: Dict[str, Any]) -> float:
        """Calculate overall validation score."""
        if not validation_details:
            return 0.0
        
        weights = self.config["quality_weights"]
        total_score = 0.0
        total_weight = 0.0
        
        for validation_type, details in validation_details.items():
            if validation_type in weights and "score" in details:
                weight = weights[validation_type]
                score = details["score"]
                total_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def _determine_overall_status(
        self,
        score: float,
        issues: List[str],
        warnings: List[str]
    ) -> str:
        """Determine overall validation status."""
        if score >= 0.8 and not issues:
            return "excellent"
        elif score >= 0.7 and not issues:
            return "good"
        elif score >= 0.6 and len(issues) <= 2:
            return "acceptable"
        elif score >= 0.5:
            return "needs_improvement"
        else:
            return "failed"
    
    def _generate_recommendations(
        self,
        validation_details: Dict[str, Any],
        overall_score: float
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if overall_score < 0.8:
            recommendations.append("Consider improving graph quality by addressing validation issues")
        
        if "structural" in validation_details:
            structural_details = validation_details["structural"]
            if structural_details.get("issues"):
                recommendations.append("Fix structural issues to improve graph integrity")
        
        if "semantic" in validation_details:
            semantic_details = validation_details["semantic"]
            if semantic_details.get("issues"):
                recommendations.append("Improve semantic consistency of entities and relationships")
        
        if "quality" in validation_details:
            quality_details = validation_details["quality"]
            if quality_details.get("score", 0) < 0.7:
                recommendations.append("Enhance entity and relationship quality metrics")
        
        if "performance" in validation_details:
            performance_details = validation_details["performance"]
            if performance_details.get("issues"):
                recommendations.append("Optimize graph structure for better performance")
        
        if not recommendations:
            recommendations.append("Graph validation passed successfully")
        
        return recommendations
    
    def _update_validation_stats(self, validation_results: Dict[str, Any], start_time: datetime) -> None:
        """Update validation statistics."""
        end_time = datetime.now()
        validation_time = (end_time - start_time).total_seconds() * 1000
        
        self.validation_stats["total_graphs_validated"] += 1
        self.validation_stats["validation_time_ms"] += validation_time
        
        # Update validation results
        status = validation_results["overall_status"]
        if status in ["excellent", "good", "acceptable"]:
            self.validation_stats["validation_results"]["passed"] += 1
        elif status == "failed":
            self.validation_stats["validation_results"]["failed"] += 1
        else:
            self.validation_stats["validation_results"]["warnings"] += 1
        
        # Track common issues
        for issue in validation_results["issues"]:
            issue_type = issue.split(":")[0] if ":" in issue else "general"
            self.validation_stats["common_issues"][issue_type] = \
                self.validation_stats["common_issues"].get(issue_type, 0) + 1
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        stats = self.validation_stats.copy()
        
        # Calculate average validation time
        if stats["total_graphs_validated"] > 0:
            stats["avg_validation_time_ms"] = stats["validation_time_ms"] / stats["total_graphs_validated"]
        else:
            stats["avg_validation_time_ms"] = 0.0
        
        # Calculate success rate
        total_validations = stats["validation_results"]["passed"] + stats["validation_results"]["failed"] + stats["validation_results"]["warnings"]
        if total_validations > 0:
            stats["success_rate"] = stats["validation_results"]["passed"] / total_validations
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset validation statistics."""
        self.validation_stats = {
            "total_graphs_validated": 0,
            "validation_time_ms": 0,
            "validation_results": {
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "common_issues": {}
        }
        logger.info("🔄 Graph validation statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update validation configuration."""
        self.config.update(new_config)
        logger.info("⚙️ Graph validation configuration updated")
