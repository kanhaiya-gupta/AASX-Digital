"""
AI RAG Relationship Discoverer
==============================

Discovers relationships between entities using various techniques.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
import uuid

from ..graph_models.graph_node import GraphNode
from ..graph_models.graph_edge import GraphEdge

logger = logging.getLogger(__name__)


class RelationshipDiscoverer:
    """
    Relationship Discoverer for AI RAG Graph Generation
    
    Discovers relationships between entities using various techniques
    including co-occurrence analysis, pattern matching, and semantic analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the relationship discoverer.
        
        Args:
            config: Configuration dictionary for discovery parameters
        """
        self.config = config or self._get_default_config()
        self.discovery_stats = {
            "total_relationships_discovered": 0,
            "relationships_by_type": {},
            "discovery_time_ms": 0,
            "confidence_scores": []
        }
        
        # Initialize relationship patterns
        self._initialize_patterns()
        
        logger.info("✅ RelationshipDiscoverer initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for relationship discovery."""
        return {
            "min_confidence": 0.5,
            "max_relationships_per_document": 200,
            "relationship_types": [
                "contains", "depends_on", "relates_to", "implements", "extends",
                "uses", "creates", "modifies", "triggers", "follows", "precedes"
            ],
            "use_cooccurrence": True,
            "use_patterns": True,
            "use_semantic": True,
            "cooccurrence_window": 100,  # Words within this window are considered co-occurring
            "min_cooccurrence_count": 2,  # Minimum co-occurrence count to consider relationship
            "language": "en"
        }
    
    def _initialize_patterns(self) -> None:
        """Initialize relationship patterns for different types."""
        self.patterns = {
            "contains": [
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (contains|includes|has) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (consists of|comprises) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
            ],
            "depends_on": [
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (depends on|requires|needs) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (relies on|is based on) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
            ],
            "implements": [
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (implements|provides|offers) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (supports|enables) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
            ],
            "uses": [
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (uses|utilizes|employs) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (calls|invokes) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
            ],
            "creates": [
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (creates|generates|produces) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (builds|constructs) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
            ],
            "modifies": [
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (modifies|changes|updates) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
                r"\b([A-Z][a-z]+ [A-Z][a-z]+) (alters|transforms) ([A-Z][a-z]+ [A-Z][a-z]+)\b",
            ]
        }
    
    async def discover_relationships(
        self,
        entities: List[GraphNode],
        document_text: str,
        document_id: str,
        graph_id: str,
        created_by: str = "system"
    ) -> List[GraphEdge]:
        """
        Discover relationships between entities.
        
        Args:
            entities: List of entities to analyze for relationships
            document_text: Text content of the document
            document_id: ID of the source document
            graph_id: ID of the graph these relationships belong to
            created_by: User/system that initiated the discovery
            
        Returns:
            List[GraphEdge]: List of discovered relationship edges
        """
        start_time = datetime.now()
        logger.info(f"🔍 Starting relationship discovery for {len(entities)} entities in document: {document_id}")
        
        try:
            relationships = []
            
            # Discover relationships using different methods
            if self.config["use_cooccurrence"]:
                cooccurrence_rels = self._discover_cooccurrence_relationships(
                    entities, document_text, document_id, graph_id, created_by
                )
                relationships.extend(cooccurrence_rels)
            
            if self.config["use_patterns"]:
                pattern_rels = self._discover_pattern_relationships(
                    entities, document_text, document_id, graph_id, created_by
                )
                relationships.extend(pattern_rels)
            
            if self.config["use_semantic"]:
                semantic_rels = await self._discover_semantic_relationships(
                    entities, document_text, document_id, graph_id, created_by
                )
                relationships.extend(semantic_rels)
            
            # Deduplicate relationships
            unique_relationships = self._deduplicate_relationships(relationships)
            
            # Limit relationships per document
            if len(unique_relationships) > self.config["max_relationships_per_document"]:
                unique_relationships = unique_relationships[:self.config["max_relationships_per_document"]]
                logger.warning(f"⚠️ Limited relationships to {self.config['max_relationships_per_document']} for document {document_id}")
            
            # Update discovery statistics
            self._update_discovery_stats(unique_relationships, start_time)
            
            logger.info(f"✅ Discovered {len(unique_relationships)} relationships in document {document_id}")
            return unique_relationships
            
        except Exception as e:
            logger.error(f"❌ Relationship discovery failed for document {document_id}: {e}")
            return []
    
    def _discover_cooccurrence_relationships(
        self,
        entities: List[GraphNode],
        document_text: str,
        document_id: str,
        graph_id: str,
        created_by: str
    ) -> List[GraphEdge]:
        """Discover relationships based on entity co-occurrence in text."""
        relationships = []
        
        # Create entity position mapping
        entity_positions = self._map_entity_positions(entities, document_text)
        
        # Find co-occurring entities within the window
        window_size = self.config["cooccurrence_window"]
        
        for entity1 in entities:
            for entity2 in entities:
                if entity1.node_id == entity2.node_id:
                    continue
                
                # Check if entities co-occur within the window
                cooccurrence_count = self._count_cooccurrences(
                    entity1, entity2, entity_positions, window_size
                )
                
                if cooccurrence_count >= self.config["min_cooccurrence_count"]:
                    # Calculate confidence based on co-occurrence frequency
                    confidence = min(0.9, 0.5 + (cooccurrence_count * 0.1))
                    
                    # Determine relationship type based on entity types
                    relationship_type = self._infer_relationship_type(entity1, entity2)
                    
                    # Create relationship edge
                    relationship = self._create_relationship_edge(
                        entity1, entity2, relationship_type, confidence,
                        document_id, graph_id, created_by, "cooccurrence"
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _discover_pattern_relationships(
        self,
        entities: List[GraphNode],
        document_text: str,
        document_id: str,
        graph_id: str,
        created_by: str
    ) -> List[GraphEdge]:
        """Discover relationships using pattern matching."""
        relationships = []
        
        for rel_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, document_text, re.IGNORECASE)
                for match in matches:
                    # Extract source and target entities from pattern
                    source_text = match.group(1)
                    target_text = match.group(3)
                    
                    # Find matching entities
                    source_entity = self._find_matching_entity(source_text, entities)
                    target_entity = self._find_matching_entity(target_text, entities)
                    
                    if source_entity and target_entity and source_entity.node_id != target_entity.node_id:
                        # Calculate confidence based on pattern match
                        confidence = 0.8  # High confidence for pattern matches
                        
                        # Create relationship edge
                        relationship = self._create_relationship_edge(
                            source_entity, target_entity, rel_type, confidence,
                            document_id, graph_id, created_by, "pattern"
                        )
                        relationships.append(relationship)
        
        return relationships
    
    async def _discover_semantic_relationships(
        self,
        entities: List[GraphNode],
        document_text: str,
        document_id: str,
        graph_id: str,
        created_by: str
    ) -> List[GraphEdge]:
        """Discover relationships using semantic analysis (placeholder for actual semantic implementation)."""
        relationships = []
        
        # This is a placeholder for actual semantic analysis implementation
        # In a real implementation, you would use semantic similarity, embeddings, or knowledge bases
        
        # Simple domain-based relationship inference as fallback
        domain_rels = self._infer_domain_relationships(entities, document_text)
        for source_entity, target_entity, rel_type in domain_rels:
            confidence = 0.6  # Default confidence for domain inference
            relationship = self._create_relationship_edge(
                source_entity, target_entity, rel_type, confidence,
                document_id, graph_id, created_by, "semantic"
            )
            relationships.append(relationship)
        
        return relationships
    
    def _map_entity_positions(self, entities: List[GraphNode], text: str) -> Dict[str, List[int]]:
        """Map entities to their positions in the text."""
        entity_positions = {}
        
        for entity in entities:
            positions = []
            entity_text = entity.node_label
            
            # Find all occurrences of the entity text
            start = 0
            while True:
                pos = text.find(entity_text, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            entity_positions[entity.node_id] = positions
        
        return entity_positions
    
    def _count_cooccurrences(
        self,
        entity1: GraphNode,
        entity2: GraphNode,
        entity_positions: Dict[str, List[int]],
        window_size: int
    ) -> int:
        """Count how many times two entities co-occur within the window."""
        count = 0
        positions1 = entity_positions.get(entity1.node_id, [])
        positions2 = entity_positions.get(entity2.node_id, [])
        
        for pos1 in positions1:
            for pos2 in positions2:
                if abs(pos1 - pos2) <= window_size:
                    count += 1
        
        return count
    
    def _find_matching_entity(self, text: str, entities: List[GraphNode]) -> Optional[GraphNode]:
        """Find an entity that matches the given text."""
        normalized_text = text.lower().strip()
        
        for entity in entities:
            if entity.node_label.lower().strip() == normalized_text:
                return entity
        
        return None
    
    def _infer_relationship_type(self, entity1: GraphNode, entity2: GraphNode) -> str:
        """Infer relationship type based on entity types."""
        # Simple heuristics for relationship type inference
        if entity1.node_type == "system" and entity2.node_type == "component":
            return "contains"
        elif entity1.node_type == "process" and entity2.node_type == "process":
            return "relates_to"
        elif entity1.node_type == "interface" and entity2.node_type == "system":
            return "implements"
        elif entity1.node_type == "technology" and entity2.node_type == "technology":
            return "relates_to"
        else:
            return "relates_to"
    
    def _infer_domain_relationships(
        self,
        entities: List[GraphNode],
        document_text: str
    ) -> List[Tuple[GraphNode, GraphNode, str]]:
        """Infer relationships based on domain knowledge."""
        relationships = []
        
        # Group entities by type
        systems = [e for e in entities if e.node_type == "system"]
        components = [e for e in entities if e.node_type == "component"]
        processes = [e for e in entities if e.node_type == "process"]
        
        # System contains components
        for system in systems:
            for component in components:
                if self._entities_related_in_text(system, component, document_text):
                    relationships.append((system, component, "contains"))
        
        # Process relates to systems
        for process in processes:
            for system in systems:
                if self._entities_related_in_text(process, system, document_text):
                    relationships.append((process, system, "relates_to"))
        
        return relationships
    
    def _entities_related_in_text(self, entity1: GraphNode, entity2: GraphNode, text: str) -> bool:
        """Check if two entities are mentioned together in the text."""
        # Simple check: entities appear in the same sentence or paragraph
        sentences = text.split('.')
        
        for sentence in sentences:
            if entity1.node_label in sentence and entity2.node_label in sentence:
                return True
        
        return False
    
    def _create_relationship_edge(
        self,
        source_entity: GraphNode,
        target_entity: GraphNode,
        relationship_type: str,
        confidence: float,
        document_id: str,
        graph_id: str,
        created_by: str,
        discovery_method: str
    ) -> GraphEdge:
        """Create a GraphEdge for a discovered relationship."""
        edge_id = f"rel_{uuid.uuid4().hex[:8]}"
        
        # Create relationship label
        relationship_label = f"{source_entity.node_label} {relationship_type} {target_entity.node_label}"
        
        # Create properties for the relationship
        properties = {
            "discovery_method": discovery_method,
            "source_text": f"{source_entity.node_label} {relationship_type} {target_entity.node_label}",
            "discovery_confidence": confidence,
            "discovered_at": datetime.now().isoformat()
        }
        
        # Create attributes for the relationship
        attributes = [
            {
                "name": "discovery_quality",
                "value": "high" if confidence >= 0.8 else "medium" if confidence >= 0.6 else "low",
                "confidence": confidence
            }
        ]
        
        # Create the GraphEdge
        edge = GraphEdge(
            edge_id=edge_id,
            source_node_id=source_entity.node_id,
            target_node_id=target_entity.node_id,
            relationship_type=relationship_type,
            relationship_label=relationship_label,
            properties=properties,
            attributes=attributes,
            confidence_score=confidence,
            source_text=f"{source_entity.node_label} {relationship_type} {target_entity.node_label}",
            source_document_id=document_id,
            graph_id=graph_id,
            created_by=created_by
        )
        
        # Calculate quality score
        edge.calculate_quality_score()
        
        return edge
    
    def _deduplicate_relationships(self, relationships: List[GraphEdge]) -> List[GraphEdge]:
        """Remove duplicate relationships based on source-target pairs."""
        unique_relationships = []
        seen_pairs = set()
        
        for relationship in relationships:
            # Create a unique key for the relationship pair
            pair_key = (relationship.source_node_id, relationship.target_node_id, relationship.relationship_type)
            
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                unique_relationships.append(relationship)
            else:
                # Merge properties if duplicate found
                existing_relationship = next(
                    r for r in unique_relationships 
                    if (r.source_node_id, r.target_node_id, r.relationship_type) == pair_key
                )
                self._merge_relationship_properties(existing_relationship, relationship)
        
        return unique_relationships
    
    def _merge_relationship_properties(self, target_rel: GraphEdge, source_rel: GraphEdge) -> None:
        """Merge properties from source relationship into target relationship."""
        # Merge properties
        target_props = target_rel.properties_dict
        source_props = source_rel.properties_dict
        
        for key, value in source_props.items():
            if key not in target_props:
                target_props[key] = value
            elif key == "discovery_confidence":
                # Take the higher confidence
                target_props[key] = max(target_props[key], value)
        
        target_rel.properties = target_rel.properties_dict
        
        # Update confidence score
        target_rel.confidence_score = max(target_rel.confidence_score, source_rel.confidence_score)
        
        # Recalculate quality score
        target_rel.calculate_quality_score()
    
    def _update_discovery_stats(self, relationships: List[GraphEdge], start_time: datetime) -> None:
        """Update discovery statistics."""
        end_time = datetime.now()
        discovery_time = (end_time - start_time).total_seconds() * 1000
        
        self.discovery_stats["total_relationships_discovered"] += len(relationships)
        self.discovery_stats["discovery_time_ms"] += discovery_time
        
        # Count relationships by type
        for relationship in relationships:
            rel_type = relationship.relationship_type
            self.discovery_stats["relationships_by_type"][rel_type] = \
                self.discovery_stats["relationships_by_type"].get(rel_type, 0) + 1
        
        # Track confidence scores
        confidence_scores = [relationship.confidence_score for relationship in relationships]
        self.discovery_stats["confidence_scores"].extend(confidence_scores)
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery statistics."""
        stats = self.discovery_stats.copy()
        
        # Calculate average confidence
        if stats["confidence_scores"]:
            stats["avg_confidence"] = sum(stats["confidence_scores"]) / len(stats["confidence_scores"])
        else:
            stats["avg_confidence"] = 0.0
        
        # Calculate discovery rate
        if stats["discovery_time_ms"] > 0:
            stats["relationships_per_second"] = stats["total_relationships_discovered"] / (stats["discovery_time_ms"] / 1000)
        else:
            stats["relationships_per_second"] = 0.0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset discovery statistics."""
        self.discovery_stats = {
            "total_relationships_discovered": 0,
            "relationships_by_type": {},
            "discovery_time_ms": 0,
            "confidence_scores": []
        }
        logger.info("🔄 Relationship discovery statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update discovery configuration."""
        self.config.update(new_config)
        logger.info("⚙️ Relationship discovery configuration updated")
        
        # Reinitialize patterns if needed
        if "relationship_types" in new_config:
            self._initialize_patterns()
