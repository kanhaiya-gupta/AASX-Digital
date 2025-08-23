"""
AI RAG Graph Builder
====================

Builds complete graph structures from entities and relationships.
"""

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import uuid

from ..graph_models.graph_node import GraphNode
from ..graph_models.graph_edge import GraphEdge
from ..graph_models.graph_structure import GraphStructure

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Graph Builder for AI RAG Graph Generation
    
    Builds complete graph structures from extracted entities and discovered relationships,
    including graph optimization, clustering, and structure validation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the graph builder.
        
        Args:
            config: Configuration dictionary for building parameters
        """
        self.config = config or self._get_default_config()
        self.building_stats = {
            "total_graphs_built": 0,
            "total_nodes_processed": 0,
            "total_edges_processed": 0,
            "building_time_ms": 0,
            "graph_quality_scores": []
        }
        
        logger.info("✅ GraphBuilder initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for graph building."""
        return {
            "min_nodes_per_graph": 3,
            "max_nodes_per_graph": 1000,
            "min_edges_per_graph": 2,
            "max_edges_per_graph": 5000,
            "enable_clustering": True,
            "enable_optimization": True,
            "enable_validation": True,
            "cluster_threshold": 0.7,
            "quality_threshold": 0.6,
            "remove_isolated_nodes": True,
            "merge_similar_entities": True,
            "similarity_threshold": 0.8
        }
    
    async def build_graph(
        self,
        entities: List[GraphNode],
        relationships: List[GraphEdge],
        graph_name: str,
        graph_type: str,
        graph_category: str,
        graph_id: Optional[str] = None,
        created_by: str = "system",
        source_documents: Optional[List[str]] = None,
        source_entities: Optional[List[Dict[str, Any]]] = None,
        source_relationships: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[GraphStructure]:
        """
        Build a complete graph structure from entities and relationships.
        
        Args:
            entities: List of entities to include in the graph
            relationships: List of relationships to include in the graph
            graph_name: Name for the graph
            graph_type: Type of graph (entity_relationship, knowledge_graph, dependency_graph)
            graph_category: Category of graph (technical, business, operational)
            graph_id: Optional custom graph ID
            created_by: User/system that created the graph
            source_documents: List of source document IDs
            source_entities: List of source entity information
            source_relationships: List of source relationship information
            
        Returns:
            GraphStructure: Built graph structure, None if building failed
        """
        start_time = datetime.now()
        logger.info(f"🏗️ Starting graph building: {graph_name} with {len(entities)} entities and {len(relationships)} relationships")
        
        try:
            # Generate graph ID if not provided
            if not graph_id:
                graph_id = f"graph_{uuid.uuid4().hex[:8]}"
            
            # Validate input
            if not self._validate_input(entities, relationships):
                logger.error("❌ Input validation failed")
                return None
            
            # Preprocess entities and relationships
            processed_entities = await self._preprocess_entities(entities, graph_id, created_by)
            processed_relationships = await self._preprocess_relationships(relationships, graph_id, created_by)
            
            # Build initial graph structure
            graph = GraphStructure(
                graph_id=graph_id,
                graph_name=graph_name,
                graph_type=graph_type,
                graph_category=graph_category,
                nodes=processed_entities,
                edges=processed_relationships,
                created_by=created_by
            )
            
            # Add source information
            if source_documents:
                for doc_id in source_documents:
                    graph.add_source_document(doc_id)
            
            if source_entities:
                for entity_info in source_entities:
                    graph.add_source_entity(entity_info)
            
            if source_relationships:
                for rel_info in source_relationships:
                    graph.add_source_relationship(rel_info)
            
            # Optimize graph structure
            if self.config["enable_optimization"]:
                graph = await self._optimize_graph(graph)
            
            # Cluster graph nodes
            if self.config["enable_clustering"]:
                graph = await self._cluster_graph(graph)
            
            # Validate graph structure
            if self.config["enable_validation"]:
                validation_result = graph.validate_structure()
                if not validation_result["valid"]:
                    logger.warning(f"⚠️ Graph validation warnings: {validation_result['warnings']}")
                    # Add validation errors to graph
                    for error in validation_result["errors"]:
                        graph.add_validation_error(error)
            
            # Calculate final quality score
            graph.calculate_quality_score()
            
            # Update building statistics
            self._update_building_stats(graph, start_time)
            
            logger.info(f"✅ Successfully built graph: {graph_name} with {graph.node_count} nodes and {graph.edge_count} edges")
            return graph
            
        except Exception as e:
            logger.error(f"❌ Graph building failed: {e}")
            return None
    
    def _validate_input(self, entities: List[GraphNode], relationships: List[GraphEdge]) -> bool:
        """Validate input entities and relationships."""
        if not entities:
            logger.error("❌ No entities provided for graph building")
            return False
        
        if len(entities) < self.config["min_nodes_per_graph"]:
            logger.error(f"❌ Too few entities: {len(entities)} < {self.config['min_nodes_per_graph']}")
            return False
        
        if len(entities) > self.config["max_nodes_per_graph"]:
            logger.error(f"❌ Too many entities: {len(entities)} > {self.config['max_nodes_per_graph']}")
            return False
        
        if relationships and len(relationships) < self.config["min_edges_per_graph"]:
            logger.error(f"❌ Too few relationships: {len(relationships)} < {self.config['min_edges_per_graph']}")
            return False
        
        if relationships and len(relationships) > self.config["max_edges_per_graph"]:
            logger.error(f"❌ Too many relationships: {len(relationships)} > {self.config['max_edges_per_graph']}")
            return False
        
        return True
    
    async def _preprocess_entities(
        self,
        entities: List[GraphNode],
        graph_id: str,
        created_by: str
    ) -> List[GraphNode]:
        """Preprocess entities for graph building."""
        processed_entities = []
        
        for entity in entities:
            # Create a copy of the entity for the graph
            processed_entity = GraphNode(
                node_id=entity.node_id,
                node_type=entity.node_type,
                node_label=entity.node_label,
                properties=entity.properties,
                attributes=entity.attributes,
                confidence_score=entity.confidence_score,
                content_hash=entity.content_hash,
                source_text=entity.source_text,
                source_document_id=entity.source_document_id,
                graph_id=graph_id,
                created_by=created_by
            )
            
            # Recalculate quality score
            processed_entity.calculate_quality_score()
            processed_entities.append(processed_entity)
        
        # Merge similar entities if enabled
        if self.config["merge_similar_entities"]:
            processed_entities = self._merge_similar_entities(processed_entities)
        
        # Remove isolated nodes if enabled
        if self.config["remove_isolated_nodes"]:
            processed_entities = self._remove_isolated_nodes(processed_entities)
        
        return processed_entities
    
    async def _preprocess_relationships(
        self,
        relationships: List[GraphEdge],
        graph_id: str,
        created_by: str
    ) -> List[GraphEdge]:
        """Preprocess relationships for graph building."""
        processed_relationships = []
        
        for relationship in relationships:
            # Create a copy of the relationship for the graph
            processed_relationship = GraphEdge(
                edge_id=relationship.edge_id,
                source_node_id=relationship.source_node_id,
                target_node_id=relationship.target_node_id,
                relationship_type=relationship.relationship_type,
                relationship_label=relationship.relationship_label,
                properties=relationship.properties,
                attributes=relationship.attributes,
                weight=relationship.weight,
                confidence_score=relationship.confidence_score,
                is_directed=relationship.is_directed,
                is_bidirectional=relationship.is_bidirectional,
                source_text=relationship.source_text,
                source_document_id=relationship.source_document_id,
                graph_id=graph_id,
                created_by=created_by
            )
            
            # Recalculate quality score
            processed_relationship.calculate_quality_score()
            processed_relationships.append(processed_relationship)
        
        return processed_relationships
    
    def _merge_similar_entities(self, entities: List[GraphNode]) -> List[GraphNode]:
        """Merge similar entities based on similarity threshold."""
        if not entities:
            return entities
        
        merged_entities = []
        processed_indices = set()
        
        for i, entity1 in enumerate(entities):
            if i in processed_indices:
                continue
            
            similar_entities = [entity1]
            processed_indices.add(i)
            
            # Find similar entities
            for j, entity2 in enumerate(entities[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                if self._calculate_entity_similarity(entity1, entity2) >= self.config["similarity_threshold"]:
                    similar_entities.append(entity2)
                    processed_indices.add(j)
            
            # Merge similar entities
            if len(similar_entities) > 1:
                merged_entity = self._merge_entity_group(similar_entities)
                merged_entities.append(merged_entity)
                logger.info(f"🔄 Merged {len(similar_entities)} similar entities into: {merged_entity.node_label}")
            else:
                merged_entities.append(entity1)
        
        return merged_entities
    
    def _calculate_entity_similarity(self, entity1: GraphNode, entity2: GraphNode) -> float:
        """Calculate similarity between two entities."""
        # Simple text similarity based on label
        label1 = entity1.node_label.lower()
        label2 = entity2.node_label.lower()
        
        # Exact match
        if label1 == label2:
            return 1.0
        
        # Partial match
        if label1 in label2 or label2 in label1:
            return 0.8
        
        # Word overlap
        words1 = set(label1.split())
        words2 = set(label2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _merge_entity_group(self, entities: List[GraphNode]) -> GraphNode:
        """Merge a group of similar entities into one."""
        if not entities:
            raise ValueError("Cannot merge empty entity group")
        
        if len(entities) == 1:
            return entities[0]
        
        # Use the first entity as the base
        base_entity = entities[0]
        
        # Merge properties
        merged_properties = base_entity.properties_dict.copy()
        for entity in entities[1:]:
            entity_props = entity.properties_dict
            for key, value in entity_props.items():
                if key not in merged_properties:
                    merged_properties[key] = value
                elif key == "extraction_confidence":
                    # Take the highest confidence
                    merged_properties[key] = max(merged_properties[key], value)
        
        base_entity.properties = merged_properties
        
        # Update confidence score to the highest
        max_confidence = max(entity.confidence_score for entity in entities)
        base_entity.confidence_score = max_confidence
        
        # Recalculate quality score
        base_entity.calculate_quality_score()
        
        return base_entity
    
    def _remove_isolated_nodes(self, entities: List[GraphNode]) -> List[GraphNode]:
        """Remove entities that have no relationships."""
        # This is a placeholder - in a real implementation, you would check
        # if entities have incoming or outgoing relationships
        # For now, we'll keep all entities
        return entities
    
    async def _optimize_graph(self, graph: GraphStructure) -> GraphStructure:
        """Optimize the graph structure."""
        logger.info("🔧 Optimizing graph structure...")
        
        # Remove duplicate relationships
        graph = self._remove_duplicate_relationships(graph)
        
        # Optimize node positions for visualization
        graph = self._optimize_node_positions(graph)
        
        # Balance relationship weights
        graph = self._balance_relationship_weights(graph)
        
        logger.info("✅ Graph optimization completed")
        return graph
    
    def _remove_duplicate_relationships(self, graph: GraphStructure) -> GraphStructure:
        """Remove duplicate relationships from the graph."""
        seen_pairs = set()
        unique_edges = []
        
        for edge in graph.edges:
            pair_key = (edge.source_node_id, edge.target_node_id, edge.relationship_type)
            
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                unique_edges.append(edge)
            else:
                # Find existing edge and merge properties
                existing_edge = next(e for e in unique_edges if 
                                   (e.source_node_id, e.target_node_id, e.relationship_type) == pair_key)
                self._merge_edge_properties(existing_edge, edge)
        
        graph.edges = unique_edges
        graph.edge_count = len(unique_edges)
        
        return graph
    
    def _merge_edge_properties(self, target_edge: GraphEdge, source_edge: GraphEdge) -> None:
        """Merge properties from source edge into target edge."""
        target_props = target_edge.properties_dict
        source_props = source_edge.properties_dict
        
        for key, value in source_props.items():
            if key not in target_props:
                target_props[key] = value
            elif key == "discovery_confidence":
                target_props[key] = max(target_props[key], value)
        
        target_edge.properties = target_props
        target_edge.confidence_score = max(target_edge.confidence_score, source_edge.confidence_score)
        target_edge.calculate_quality_score()
    
    def _optimize_node_positions(self, graph: GraphStructure) -> GraphStructure:
        """Optimize node positions for better visualization."""
        # Simple grid layout optimization
        import math
        
        node_count = len(graph.nodes)
        if node_count == 0:
            return graph
        
        # Calculate grid dimensions
        cols = math.ceil(math.sqrt(node_count))
        rows = math.ceil(node_count / cols)
        
        for i, node in enumerate(graph.nodes):
            row = i // cols
            col = i % cols
            
            # Position nodes in a grid with some spacing
            x = col * 200 + 100
            y = row * 150 + 100
            
            node.update_position(x, y)
            node.update_layer(row)  # Use row as layer
        
        return graph
    
    def _balance_relationship_weights(self, graph: GraphStructure) -> GraphStructure:
        """Balance relationship weights for better graph structure."""
        if not graph.edges:
            return graph
        
        # Calculate average weight
        weights = [edge.weight for edge in graph.edges]
        avg_weight = sum(weights) / len(weights)
        
        # Normalize weights to be around the average
        for edge in graph.edges:
            if edge.weight > avg_weight * 2:
                edge.update_weight(avg_weight * 1.5)
            elif edge.weight < avg_weight * 0.5:
                edge.update_weight(avg_weight * 0.8)
        
        return graph
    
    async def _cluster_graph(self, graph: GraphStructure) -> GraphStructure:
        """Cluster graph nodes into communities."""
        logger.info("🔗 Clustering graph nodes...")
        
        # Simple clustering based on node types
        clusters = {}
        
        for node in graph.nodes:
            node_type = node.node_type
            if node_type not in clusters:
                clusters[node_type] = []
            clusters[node_type].append(node)
        
        # Assign cluster IDs
        for cluster_id, cluster_nodes in clusters.items():
            for node in cluster_nodes:
                node.cluster_id = f"cluster_{cluster_id}"
        
        logger.info(f"✅ Created {len(clusters)} clusters based on node types")
        return graph
    
    def _update_building_stats(self, graph: GraphStructure, start_time: datetime) -> None:
        """Update building statistics."""
        end_time = datetime.now()
        building_time = (end_time - start_time).total_seconds() * 1000
        
        self.building_stats["total_graphs_built"] += 1
        self.building_stats["total_nodes_processed"] += graph.node_count
        self.building_stats["total_edges_processed"] += graph.edge_count
        self.building_stats["building_time_ms"] += building_time
        self.building_stats["graph_quality_scores"].append(graph.overall_quality_score)
    
    def get_building_stats(self) -> Dict[str, Any]:
        """Get building statistics."""
        stats = self.building_stats.copy()
        
        # Calculate average quality
        if stats["graph_quality_scores"]:
            stats["avg_graph_quality"] = sum(stats["graph_quality_scores"]) / len(stats["graph_quality_scores"])
        else:
            stats["avg_graph_quality"] = 0.0
        
        # Calculate building rate
        if stats["building_time_ms"] > 0:
            stats["graphs_per_second"] = stats["total_graphs_built"] / (stats["building_time_ms"] / 1000)
        else:
            stats["graphs_per_second"] = 0.0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset building statistics."""
        self.building_stats = {
            "total_graphs_built": 0,
            "total_nodes_processed": 0,
            "total_edges_processed": 0,
            "building_time_ms": 0,
            "graph_quality_scores": []
        }
        logger.info("🔄 Graph building statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update building configuration."""
        self.config.update(new_config)
        logger.info("⚙️ Graph building configuration updated")
