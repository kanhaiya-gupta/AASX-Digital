"""
AI RAG Entity Extractor
=======================

Extracts entities from documents using NLP and AI techniques.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import uuid

from ..graph_models.graph_node import GraphNode

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Entity Extractor for AI RAG Graph Generation
    
    Extracts entities from documents using various NLP and AI techniques
    including named entity recognition, pattern matching, and semantic analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the entity extractor.
        
        Args:
            config: Configuration dictionary for extraction parameters
        """
        self.config = config or self._get_default_config()
        self.extraction_stats = {
            "total_entities_extracted": 0,
            "entities_by_type": {},
            "extraction_time_ms": 0,
            "confidence_scores": []
        }
        
        # Initialize extraction patterns
        self._initialize_patterns()
        
        logger.info("✅ EntityExtractor initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for entity extraction."""
        return {
            "min_confidence": 0.6,
            "max_entities_per_document": 100,
            "entity_types": [
                "person", "organization", "location", "technology", 
                "process", "system", "component", "interface"
            ],
            "use_nlp": True,
            "use_patterns": True,
            "use_semantic": True,
            "language": "en"
        }
    
    def _initialize_patterns(self) -> None:
        """Initialize extraction patterns for different entity types."""
        self.patterns = {
            "person": [
                r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # First Last
                r"\b[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+\b",  # First M. Last
                r"\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b",  # First Middle Last
            ],
            "organization": [
                r"\b[A-Z][a-z]+ (Corp|Inc|LLC|Ltd|Company|Organization|Institute|University)\b",
                r"\b[A-Z][a-z]+ [A-Z][a-z]+ (Systems|Solutions|Technologies|Services)\b",
            ],
            "technology": [
                r"\b[A-Z][a-z]+ [0-9]+\b",  # Product names with numbers
                r"\b[A-Z][a-z]+-[A-Z][a-z]+\b",  # Hyphenated tech terms
                r"\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b",  # Multi-word tech terms
            ],
            "process": [
                r"\b[A-Z][a-z]+ (Process|Workflow|Procedure|Method|Algorithm)\b",
                r"\b[A-Z][a-z]+ [A-Z][a-z]+ (Management|Development|Integration)\b",
            ],
            "system": [
                r"\b[A-Z][a-z]+ (System|Platform|Framework|Architecture|Infrastructure)\b",
                r"\b[A-Z][a-z]+ [A-Z][a-z]+ (Management|Monitoring|Control)\b",
            ]
        }
    
    async def extract_entities_from_document(
        self,
        document_id: str,
        document_text: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        graph_id: str = None,
        created_by: str = "system"
    ) -> List[GraphNode]:
        """
        Extract entities from a document.
        
        Args:
            document_id: ID of the source document
            document_text: Text content of the document
            document_metadata: Additional document metadata
            graph_id: ID of the graph these entities belong to
            created_by: User/system that initiated the extraction
            
        Returns:
            List[GraphNode]: List of extracted entity nodes
        """
        start_time = datetime.now()
        logger.info(f"🔍 Starting entity extraction from document: {document_id}")
        
        try:
            entities = []
            
            # Extract entities using different methods
            if self.config["use_patterns"]:
                pattern_entities = self._extract_using_patterns(document_text, document_id, graph_id, created_by)
                entities.extend(pattern_entities)
            
            if self.config["use_nlp"]:
                nlp_entities = await self._extract_using_nlp(document_text, document_id, graph_id, created_by)
                entities.extend(nlp_entities)
            
            if self.config["use_semantic"]:
                semantic_entities = await self._extract_using_semantic(document_text, document_id, graph_id, created_by)
                entities.extend(semantic_entities)
            
            # Deduplicate entities
            unique_entities = self._deduplicate_entities(entities)
            
            # Limit entities per document
            if len(unique_entities) > self.config["max_entities_per_document"]:
                unique_entities = unique_entities[:self.config["max_entities_per_document"]]
                logger.warning(f"⚠️ Limited entities to {self.config['max_entities_per_document']} for document {document_id}")
            
            # Update extraction statistics
            self._update_extraction_stats(unique_entities, start_time)
            
            logger.info(f"✅ Extracted {len(unique_entities)} entities from document {document_id}")
            return unique_entities
            
        except Exception as e:
            logger.error(f"❌ Entity extraction failed for document {document_id}: {e}")
            return []
    
    def _extract_using_patterns(
        self,
        text: str,
        document_id: str,
        graph_id: str,
        created_by: str
    ) -> List[GraphNode]:
        """Extract entities using pattern matching."""
        entities = []
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity_text = match.group()
                    confidence = self._calculate_pattern_confidence(entity_text, entity_type)
                    
                    if confidence >= self.config["min_confidence"]:
                        entity = self._create_entity_node(
                            entity_text, entity_type, document_id, graph_id, created_by, confidence
                        )
                        entities.append(entity)
        
        return entities
    
    async def _extract_using_nlp(
        self,
        text: str,
        document_id: str,
        graph_id: str,
        created_by: str
    ) -> List[GraphNode]:
        """Extract entities using NLP techniques (placeholder for actual NLP implementation)."""
        entities = []
        
        # This is a placeholder for actual NLP implementation
        # In a real implementation, you would use libraries like spaCy, NLTK, or cloud NLP services
        
        # Simple keyword-based extraction as fallback
        keywords = self._extract_keywords(text)
        for keyword, entity_type in keywords:
            confidence = 0.7  # Default confidence for keyword extraction
            entity = self._create_entity_node(
                keyword, entity_type, document_id, graph_id, created_by, confidence
            )
            entities.append(entity)
        
        return entities
    
    async def _extract_using_semantic(
        self,
        text: str,
        document_id: str,
        graph_id: str,
        created_by: str
    ) -> List[GraphNode]:
        """Extract entities using semantic analysis (placeholder for actual semantic implementation)."""
        entities = []
        
        # This is a placeholder for actual semantic analysis implementation
        # In a real implementation, you would use semantic similarity, embeddings, or knowledge bases
        
        # Extract domain-specific terms
        domain_terms = self._extract_domain_terms(text)
        for term, entity_type in domain_terms:
            confidence = 0.8  # Default confidence for domain terms
            entity = self._create_entity_node(
                term, entity_type, document_id, graph_id, created_by, confidence
            )
            entities.append(entity)
        
        return entities
    
    def _extract_keywords(self, text: str) -> List[tuple]:
        """Extract keywords from text."""
        keywords = []
        
        # Simple keyword extraction based on capitalization and frequency
        words = text.split()
        word_freq = {}
        
        for word in words:
            # Clean word
            clean_word = re.sub(r'[^\w\s]', '', word)
            if len(clean_word) > 3 and clean_word[0].isupper():
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Get most frequent capitalized words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        for word, freq in sorted_words[:20]:  # Top 20 keywords
            if freq >= 2:  # Appears at least twice
                entity_type = self._classify_keyword(word)
                keywords.append((word, entity_type))
        
        return keywords
    
    def _extract_domain_terms(self, text: str) -> List[tuple]:
        """Extract domain-specific terms from text."""
        domain_terms = []
        
        # Domain-specific patterns for technical documents
        technical_patterns = [
            (r'\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b', 'technology'),
            (r'\b[A-Z][a-z]+ [A-Z][a-z]+ System\b', 'system'),
            (r'\b[A-Z][a-z]+ [A-Z][a-z]+ Process\b', 'process'),
            (r'\b[A-Z][a-z]+ [A-Z][a-z]+ Interface\b', 'interface'),
        ]
        
        for pattern, entity_type in technical_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                term = match.group()
                domain_terms.append((term, entity_type))
        
        return domain_terms
    
    def _classify_keyword(self, word: str) -> str:
        """Classify a keyword into an entity type."""
        # Simple classification based on word patterns
        if word.endswith(('System', 'Platform', 'Framework')):
            return 'system'
        elif word.endswith(('Process', 'Workflow', 'Procedure')):
            return 'process'
        elif word.endswith(('Interface', 'API', 'Service')):
            return 'interface'
        elif word.endswith(('Component', 'Module', 'Library')):
            return 'component'
        else:
            return 'concept'
    
    def _calculate_pattern_confidence(self, entity_text: str, entity_type: str) -> float:
        """Calculate confidence score for pattern-matched entities."""
        base_confidence = 0.7
        
        # Adjust confidence based on entity text characteristics
        if len(entity_text.split()) >= 3:
            base_confidence += 0.1  # Multi-word entities are more reliable
        
        if entity_text.isupper():
            base_confidence += 0.1  # All caps often indicates proper nouns
        
        if re.search(r'\d', entity_text):
            base_confidence += 0.05  # Numbers often indicate specific entities
        
        return min(base_confidence, 1.0)
    
    def _create_entity_node(
        self,
        entity_text: str,
        entity_type: str,
        document_id: str,
        graph_id: str,
        created_by: str,
        confidence: float
    ) -> GraphNode:
        """Create a GraphNode for an extracted entity."""
        node_id = f"entity_{uuid.uuid4().hex[:8]}"
        
        # Create properties for the entity
        properties = {
            "extraction_method": "pattern" if confidence < 0.8 else "nlp",
            "source_text": entity_text,
            "entity_type": entity_type,
            "extraction_confidence": confidence,
            "extracted_at": datetime.now().isoformat()
        }
        
        # Create attributes for the entity
        attributes = [
            {
                "name": "extraction_quality",
                "value": "high" if confidence >= 0.8 else "medium" if confidence >= 0.6 else "low",
                "confidence": confidence
            }
        ]
        
        # Create the GraphNode
        node = GraphNode(
            node_id=node_id,
            node_type=entity_type,
            node_label=entity_text,
            properties=properties,
            attributes=attributes,
            confidence_score=confidence,
            source_text=entity_text,
            source_document_id=document_id,
            graph_id=graph_id,
            created_by=created_by
        )
        
        # Calculate quality score
        node.calculate_quality_score()
        
        return node
    
    def _deduplicate_entities(self, entities: List[GraphNode]) -> List[GraphNode]:
        """Remove duplicate entities based on text similarity."""
        unique_entities = []
        seen_texts = set()
        
        for entity in entities:
            # Normalize text for comparison
            normalized_text = entity.node_label.lower().strip()
            
            if normalized_text not in seen_texts:
                seen_texts.add(normalized_text)
                unique_entities.append(entity)
            else:
                # Merge properties if duplicate found
                existing_entity = next(e for e in unique_entities if e.node_label.lower().strip() == normalized_text)
                self._merge_entity_properties(existing_entity, entity)
        
        return unique_entities
    
    def _merge_entity_properties(self, target_entity: GraphNode, source_entity: GraphNode) -> None:
        """Merge properties from source entity into target entity."""
        # Merge properties
        target_props = target_entity.properties_dict
        source_props = source_entity.properties_dict
        
        for key, value in source_props.items():
            if key not in target_props:
                target_props[key] = value
            elif key == "extraction_confidence":
                # Take the higher confidence
                target_props[key] = max(target_props[key], value)
        
        target_entity.properties = target_entity.properties_dict
        
        # Update confidence score
        target_entity.confidence_score = max(target_entity.confidence_score, source_entity.confidence_score)
        
        # Recalculate quality score
        target_entity.calculate_quality_score()
    
    def _update_extraction_stats(self, entities: List[GraphNode], start_time: datetime) -> None:
        """Update extraction statistics."""
        end_time = datetime.now()
        extraction_time = (end_time - start_time).total_seconds() * 1000
        
        self.extraction_stats["total_entities_extracted"] += len(entities)
        self.extraction_stats["extraction_time_ms"] += extraction_time
        
        # Count entities by type
        for entity in entities:
            entity_type = entity.node_type
            self.extraction_stats["entities_by_type"][entity_type] = \
                self.extraction_stats["entities_by_type"].get(entity_type, 0) + 1
        
        # Track confidence scores
        confidence_scores = [entity.confidence_score for entity in entities]
        self.extraction_stats["confidence_scores"].extend(confidence_scores)
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        stats = self.extraction_stats.copy()
        
        # Calculate average confidence
        if stats["confidence_scores"]:
            stats["avg_confidence"] = sum(stats["confidence_scores"]) / len(stats["confidence_scores"])
        else:
            stats["avg_confidence"] = 0.0
        
        # Calculate extraction rate
        if stats["extraction_time_ms"] > 0:
            stats["entities_per_second"] = stats["total_entities_extracted"] / (stats["extraction_time_ms"] / 1000)
        else:
            stats["entities_per_second"] = 0.0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset extraction statistics."""
        self.extraction_stats = {
            "total_entities_extracted": 0,
            "entities_by_type": {},
            "extraction_time_ms": 0,
            "confidence_scores": []
        }
        logger.info("🔄 Entity extraction statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update extraction configuration."""
        self.config.update(new_config)
        logger.info("⚙️ Entity extraction configuration updated")
        
        # Reinitialize patterns if needed
        if "entity_types" in new_config:
            self._initialize_patterns()
