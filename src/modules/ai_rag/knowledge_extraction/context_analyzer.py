"""
AI RAG Context Analyzer
=======================

Document context analysis, semantic relationships, and document structure analysis.
"""

import logging
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
import asyncio

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """
    Context Analyzer for AI RAG Knowledge Extraction
    
    Analyzes document context, semantic relationships, document structure,
    and provides insights for better knowledge extraction and graph generation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the context analyzer.
        
        Args:
            config: Configuration dictionary for context analysis
        """
        self.config = config or self._get_default_config()
        self.analysis_stats = {
            "documents_analyzed": 0,
            "contexts_extracted": 0,
            "relationships_discovered": 0,
            "structures_identified": 0,
            "processing_time_ms": 0
        }
        
        # Initialize analysis patterns and rules
        self._init_context_patterns()
        self._init_semantic_rules()
        
        logger.info("✅ ContextAnalyzer initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for context analysis."""
        return {
            "context_window_size": 200,
            "max_contexts_per_document": 1000,
            "semantic_analysis_enabled": True,
            "structure_analysis_enabled": True,
            "relationship_discovery_enabled": True,
            "cross_reference_enabled": True,
            "confidence_threshold": 0.6,
            "batch_size": 50,
            "parallel_processing": True,
            "enable_semantic_clustering": True,
            "enable_topic_modeling": True,
            "enable_sentiment_analysis": False,
            "enable_document_classification": True,
            "context_types": [
                "definition", "example", "comparison", "cause_effect",
                "sequence", "hierarchy", "classification", "description"
            ]
        }
    
    def _init_context_patterns(self) -> None:
        """Initialize context analysis patterns."""
        self.context_patterns = {
            "definition": [
                r'\b(?:is|are|refers\s+to|means|defined\s+as|consists\s+of)\s+[^.!?]+[.!?]',
                r'\b(?:definition|meaning|description)\s+[^.!?]+[.!?]',
                r'\b(?:in\s+other\s+words|that\s+is|namely|specifically)\s+[^.!?]+[.!?]'
            ],
            "example": [
                r'\b(?:for\s+example|such\s+as|including|e\.g\.|i\.e\.)\s+[^.!?]+[.!?]',
                r'\b(?:example|instance|case|illustration)\s+[^.!?]+[.!?]',
                r'\b(?:consider|suppose|imagine)\s+[^.!?]+[.!?]'
            ],
            "comparison": [
                r'\b(?:similar\s+to|like|unlike|compared\s+to|in\s+contrast)\s+[^.!?]+[.!?]',
                r'\b(?:however|but|on\s+the\s+other\s+hand|nevertheless)\s+[^.!?]+[.!?]',
                r'\b(?:while|whereas|although|despite)\s+[^.!?]+[.!?]'
            ],
            "cause_effect": [
                r'\b(?:because|since|as|due\s+to|as\s+a\s+result)\s+[^.!?]+[.!?]',
                r'\b(?:therefore|thus|consequently|hence|so)\s+[^.!?]+[.!?]',
                r'\b(?:leads\s+to|results\s+in|causes|affects|impacts)\s+[^.!?]+[.!?]'
            ],
            "sequence": [
                r'\b(?:first|second|third|next|then|finally|lastly)\s+[^.!?]+[.!?]',
                r'\b(?:before|after|during|while|when|once)\s+[^.!?]+[.!?]',
                r'\b(?:step|phase|stage|iteration|cycle)\s+[^.!?]+[.!?]'
            ],
            "hierarchy": [
                r'\b(?:above|below|under|over|within|contains|includes)\s+[^.!?]+[.!?]',
                r'\b(?:parent|child|subordinate|superior|main|sub)\s+[^.!?]+[.!?]',
                r'\b(?:level|tier|layer|category|group|class)\s+[^.!?]+[.!?]'
            ],
            "classification": [
                r'\b(?:type|kind|sort|category|class|group|division)\s+[^.!?]+[.!?]',
                r'\b(?:classified\s+as|categorized\s+as|grouped\s+into)\s+[^.!?]+[.!?]',
                r'\b(?:belongs\s+to|is\s+part\s+of|falls\s+under)\s+[^.!?]+[.!?]'
            ],
            "description": [
                r'\b(?:has|contains|features|characterized\s+by)\s+[^.!?]+[.!?]',
                r'\b(?:appears|looks|seems|appears\s+to\s+be)\s+[^.!?]+[.!?]',
                r'\b(?:consists\s+of|made\s+up\s+of|composed\s+of)\s+[^.!?]+[.!?]'
            ]
        }
        
        logger.info(f"🔍 Context patterns initialized for {len(self.context_patterns)} context types")
    
    def _init_semantic_rules(self) -> None:
        """Initialize semantic analysis rules."""
        self.semantic_rules = {
            "synonym_patterns": [
                r'\b(?:also\s+known\s+as|aka|alternatively|or|same\s+as)\s+[^.!?]+[.!?]',
                r'\b(?:synonym|equivalent|similar|related)\s+[^.!?]+[.!?]'
            ],
            "antonym_patterns": [
                r'\b(?:opposite|contrary|unlike|different\s+from|not)\s+[^.!?]+[.!?]',
                r'\b(?:antonym|reverse|inverse|contrast)\s+[^.!?]+[.!?]'
            ],
            "hyponym_patterns": [
                r'\b(?:type\s+of|kind\s+of|example\s+of|instance\s+of)\s+[^.!?]+[.!?]',
                r'\b(?:subcategory|subclass|subtype|variant)\s+[^.!?]+[.!?]'
            ],
            "hypernym_patterns": [
                r'\b(?:category|class|group|family|genus)\s+[^.!?]+[.!?]',
                r'\b(?:general|broad|overall|umbrella)\s+[^.!?]+[.!?]'
            ],
            "meronym_patterns": [
                r'\b(?:part\s+of|component\s+of|element\s+of|piece\s+of)\s+[^.!?]+[.!?]',
                r'\b(?:contains|includes|consists\s+of|made\s+up\s+of)\s+[^.!?]+[.!?]'
            ],
            "holonym_patterns": [
                r'\b(?:whole|complete|entire|full|total)\s+[^.!?]+[.!?]',
                r'\b(?:assembly|system|structure|framework)\s+[^.!?]+[.!?]'
            ]
        }
        
        logger.info(f"🧠 Semantic rules initialized for {len(self.semantic_rules)} relationship types")
    
    async def analyze_document_context(
        self,
        text: str,
        document_id: Optional[str] = None,
        entities: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze document context comprehensively.
        
        Args:
            text: Document text to analyze
            document_id: Optional document identifier
            entities: Optional list of extracted entities
            metadata: Optional document metadata
            
        Returns:
            Dict: Comprehensive context analysis results
        """
        start_time = asyncio.get_event_loop().time()
        logger.info(f"📄 Starting context analysis for document: {document_id or 'unknown'}")
        
        try:
            # Extract contexts
            contexts = await self._extract_contexts(text)
            
            # Analyze document structure
            structure = await self._analyze_document_structure(text)
            
            # Discover semantic relationships
            relationships = await self._discover_semantic_relationships(text, entities)
            
            # Perform semantic clustering
            clusters = await self._perform_semantic_clustering(text, contexts, entities)
            
            # Identify topics
            topics = await self._identify_topics(text, contexts)
            
            # Analyze document classification
            classification = await self._classify_document(text, contexts, metadata)
            
            # Calculate processing time
            end_time = asyncio.get_event_loop().time()
            processing_time = (end_time - start_time) * 1000
            
            # Update statistics
            self._update_analysis_stats(len(contexts), len(relationships), 
                                      len(structure), processing_time)
            
            results = {
                "document_id": document_id,
                "metadata": metadata or {},
                "analysis_timestamp": asyncio.get_event_loop().time(),
                "processing_time_ms": processing_time,
                "text_length": len(text),
                "contexts": contexts,
                "structure": structure,
                "relationships": relationships,
                "clusters": clusters,
                "topics": topics,
                "classification": classification,
                "analysis_metadata": {
                    "config_used": self.config.copy(),
                    "analysis_stats": self.analysis_stats.copy()
                }
            }
            
            logger.info(f"✅ Context analysis completed: {document_id or 'unknown'} - {len(contexts)} contexts, {len(relationships)} relationships")
            return results
            
        except Exception as e:
            logger.error(f"❌ Context analysis failed: {e}")
            return {
                "document_id": document_id,
                "metadata": metadata or {},
                "analysis_timestamp": asyncio.get_event_loop().time(),
                "processing_time_ms": 0,
                "error": str(e),
                "contexts": [],
                "structure": {},
                "relationships": [],
                "clusters": [],
                "topics": [],
                "classification": {}
            }
    
    async def _extract_contexts(self, text: str) -> List[Dict[str, Any]]:
        """Extract different types of contexts from text."""
        contexts = []
        
        try:
            for context_type, patterns in self.context_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        context_text = match.group()
                        confidence = self._calculate_context_confidence(context_text, context_type, text)
                        
                        if confidence >= self.config["confidence_threshold"]:
                            context = {
                                "text": context_text,
                                "type": context_type,
                                "start_pos": match.start(),
                                "end_pos": match.end(),
                                "confidence": confidence,
                                "source": "pattern_matching",
                                "raw_match": match.group(0),
                                "surrounding_context": self._extract_surrounding_context(text, match.start(), match.end())
                            }
                            contexts.append(context)
            
            # Limit contexts per document
            if len(contexts) > self.config["max_contexts_per_document"]:
                # Sort by confidence and keep top contexts
                contexts.sort(key=lambda x: x["confidence"], reverse=True)
                contexts = contexts[:self.config["max_contexts_per_document"]]
                logger.warning(f"⚠️ Limited contexts to {self.config['max_contexts_per_document']} (highest confidence)")
            
            # Remove duplicates
            contexts = self._deduplicate_contexts(contexts)
            
            return contexts
            
        except Exception as e:
            logger.error(f"❌ Context extraction failed: {e}")
            return []
    
    async def _analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure and organization."""
        structure = {
            "sections": [],
            "paragraphs": [],
            "sentences": [],
            "headings": [],
            "lists": [],
            "tables": [],
            "references": [],
            "structure_type": "unknown",
            "organization_score": 0.0
        }
        
        try:
            # Split into paragraphs
            paragraphs = text.split('\n\n')
            structure["paragraphs"] = [p.strip() for p in paragraphs if p.strip()]
            
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            structure["sentences"] = [s.strip() for s in sentences if s.strip()]
            
            # Identify headings
            heading_patterns = [
                r'^[A-Z][^.!?]*$',  # All caps lines
                r'^\d+\.\s+[A-Z][^.!?]*$',  # Numbered headings
                r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title case lines
            ]
            
            for pattern in heading_patterns:
                for line in text.split('\n'):
                    if re.match(pattern, line.strip()):
                        structure["headings"].append({
                            "text": line.strip(),
                            "level": self._determine_heading_level(line.strip()),
                            "position": text.find(line)
                        })
            
            # Identify lists
            list_patterns = [
                r'^\s*[-*•]\s+',  # Bullet points
                r'^\s*\d+\.\s+',  # Numbered lists
                r'^\s*[a-z]\)\s+',  # Lettered lists
            ]
            
            for pattern in list_patterns:
                for line in text.split('\n'):
                    if re.match(pattern, line.strip()):
                        structure["lists"].append({
                            "text": line.strip(),
                            "type": "bullet" if "-*•" in pattern else "numbered",
                            "position": text.find(line)
                        })
            
            # Determine structure type
            structure["structure_type"] = self._determine_structure_type(structure)
            
            # Calculate organization score
            structure["organization_score"] = self._calculate_organization_score(structure)
            
            return structure
            
        except Exception as e:
            logger.error(f"❌ Document structure analysis failed: {e}")
            return structure
    
    async def _discover_semantic_relationships(
        self,
        text: str,
        entities: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Discover semantic relationships in the document."""
        relationships = []
        
        try:
            if not self.config["relationship_discovery_enabled"]:
                return relationships
            
            # Extract relationships using semantic rules
            for rel_type, patterns in self.semantic_rules.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        rel_text = match.group()
                        confidence = self._calculate_relationship_confidence(rel_text, rel_type, text)
                        
                        if confidence >= self.config["confidence_threshold"]:
                            relationship = {
                                "text": rel_text,
                                "type": rel_type,
                                "start_pos": match.start(),
                                "end_pos": match.end(),
                                "confidence": confidence,
                                "source": "semantic_analysis",
                                "entities_involved": self._extract_entities_from_relationship(rel_text, entities),
                                "context": self._extract_surrounding_context(text, match.start(), match.end())
                            }
                            relationships.append(relationship)
            
            # Cross-reference relationships if enabled
            if self.config["cross_reference_enabled"] and entities:
                cross_refs = await self._find_cross_references(text, entities)
                relationships.extend(cross_refs)
            
            return relationships
            
        except Exception as e:
            logger.error(f"❌ Semantic relationship discovery failed: {e}")
            return []
    
    async def _perform_semantic_clustering(
        self,
        text: str,
        contexts: List[Dict[str, Any]],
        entities: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic clustering of contexts and entities."""
        clusters = []
        
        try:
            if not self.config["enable_semantic_clustering"]:
                return clusters
            
            # Simple clustering based on context types
            context_clusters = defaultdict(list)
            for context in contexts:
                context_clusters[context["type"]].append(context)
            
            # Create clusters
            for cluster_type, cluster_contexts in context_clusters.items():
                if len(cluster_contexts) > 1:  # Only clusters with multiple items
                    cluster = {
                        "cluster_id": f"cluster_{cluster_type}_{len(clusters)}",
                        "type": cluster_type,
                        "contexts": cluster_contexts,
                        "size": len(cluster_contexts),
                        "center_text": self._find_cluster_center(cluster_contexts),
                        "coherence_score": self._calculate_cluster_coherence(cluster_contexts),
                        "entities": self._extract_entities_from_contexts(cluster_contexts, entities)
                    }
                    clusters.append(cluster)
            
            return clusters
            
        except Exception as e:
            logger.error(f"❌ Semantic clustering failed: {e}")
            return []
    
    async def _identify_topics(
        self,
        text: str,
        contexts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify main topics in the document."""
        topics = []
        
        try:
            if not self.config["enable_topic_modeling"]:
                return topics
            
            # Simple topic identification based on context frequency
            context_types = Counter(context["type"] for context in contexts)
            
            # Identify main topics based on context distribution
            for context_type, count in context_types.most_common(5):
                if count >= 2:  # At least 2 contexts of this type
                    topic = {
                        "topic_id": f"topic_{context_type}_{len(topics)}",
                        "name": context_type.replace('_', ' ').title(),
                        "type": context_type,
                        "frequency": count,
                        "contexts": [c for c in contexts if c["type"] == context_type],
                        "keywords": self._extract_topic_keywords([c for c in contexts if c["type"] == context_type]),
                        "confidence": min(count / len(contexts), 1.0) if contexts else 0.0
                    }
                    topics.append(topic)
            
            return topics
            
        except Exception as e:
            logger.error(f"❌ Topic identification failed: {e}")
            return []
    
    async def _classify_document(
        self,
        text: str,
        contexts: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Classify the document based on content and structure."""
        classification = {
            "document_type": "unknown",
            "domain": "unknown",
            "purpose": "unknown",
            "audience": "unknown",
            "complexity_level": "unknown",
            "confidence": 0.0,
            "tags": [],
            "categories": []
        }
        
        try:
            if not self.config["enable_document_classification"]:
                return classification
            
            # Analyze document characteristics
            characteristics = self._analyze_document_characteristics(text, contexts)
            
            # Determine document type
            doc_type = self._determine_document_type(characteristics)
            classification["document_type"] = doc_type
            
            # Determine domain
            domain = self._determine_document_domain(characteristics)
            classification["domain"] = domain
            
            # Determine purpose
            purpose = self._determine_document_purpose(characteristics)
            classification["purpose"] = purpose
            
            # Determine audience
            audience = self._determine_document_audience(characteristics)
            classification["audience"] = audience
            
            # Determine complexity level
            complexity = self._determine_complexity_level(characteristics)
            classification["complexity_level"] = complexity
            
            # Generate tags and categories
            tags = self._generate_document_tags(characteristics)
            classification["tags"] = tags
            
            categories = self._generate_document_categories(characteristics)
            classification["categories"] = categories
            
            # Calculate overall confidence
            classification["confidence"] = self._calculate_classification_confidence(classification)
            
            return classification
            
        except Exception as e:
            logger.error(f"❌ Document classification failed: {e}")
            return classification
    
    def _calculate_context_confidence(
        self,
        context_text: str,
        context_type: str,
        text: str
    ) -> float:
        """Calculate confidence score for extracted context."""
        confidence = 0.5  # Base confidence
        
        try:
            # Length-based confidence
            if len(context_text) >= 20:
                confidence += 0.1
            
            # Context type specific confidence
            if context_type in ["definition", "example"]:
                confidence += 0.1  # These are usually more reliable
            
            # Frequency-based confidence
            context_lower = context_text.lower()
            text_lower = text.lower()
            frequency = text_lower.count(context_lower)
            
            if frequency == 1:
                confidence += 0.1  # Unique context
            elif frequency <= 3:
                confidence += 0.05  # Few occurrences
            else:
                confidence -= 0.05  # Too many might indicate noise
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ Context confidence calculation failed: {e}")
            confidence = 0.5
        
        return round(confidence, 3)
    
    def _extract_surrounding_context(
        self,
        text: str,
        start_pos: int,
        end_pos: int,
        window_size: Optional[int] = None
    ) -> str:
        """Extract context surrounding a match."""
        window = window_size or self.config["context_window_size"]
        
        try:
            context_start = max(0, start_pos - window)
            context_end = min(len(text), end_pos + window)
            
            return text[context_start:context_end].strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Surrounding context extraction failed: {e}")
            return ""
    
    def _determine_heading_level(self, heading_text: str) -> int:
        """Determine the level of a heading."""
        try:
            # Simple heuristics for heading levels
            if re.match(r'^\d+\.\s+', heading_text):
                return 1
            elif re.match(r'^\d+\.\d+\.\s+', heading_text):
                return 2
            elif re.match(r'^\d+\.\d+\.\d+\.\s+', heading_text):
                return 3
            elif heading_text.isupper():
                return 1
            else:
                return 2
        except Exception:
            return 1
    
    def _determine_structure_type(self, structure: Dict[str, Any]) -> str:
        """Determine the overall structure type of the document."""
        try:
            if structure["headings"] and len(structure["headings"]) > 3:
                return "hierarchical"
            elif structure["lists"] and len(structure["lists"]) > 2:
                return "list_based"
            elif structure["paragraphs"] and len(structure["paragraphs"]) > 5:
                return "narrative"
            elif structure["tables"]:
                return "tabular"
            else:
                return "mixed"
        except Exception:
            return "unknown"
    
    def _calculate_organization_score(self, structure: Dict[str, Any]) -> float:
        """Calculate how well organized the document is."""
        try:
            score = 0.0
            
            # Score based on headings
            if structure["headings"]:
                score += min(len(structure["headings"]) * 0.1, 0.3)
            
            # Score based on lists
            if structure["lists"]:
                score += min(len(structure["lists"]) * 0.05, 0.2)
            
            # Score based on paragraph structure
            if structure["paragraphs"]:
                avg_para_length = sum(len(p) for p in structure["paragraphs"]) / len(structure["paragraphs"])
                if 50 <= avg_para_length <= 200:
                    score += 0.2  # Good paragraph length
                elif 20 <= avg_para_length <= 500:
                    score += 0.1  # Acceptable paragraph length
            
            # Score based on sentence structure
            if structure["sentences"]:
                avg_sent_length = sum(len(s) for s in structure["sentences"]) / len(structure["sentences"])
                if 10 <= avg_sent_length <= 50:
                    score += 0.2  # Good sentence length
                elif 5 <= avg_sent_length <= 100:
                    score += 0.1  # Acceptable sentence length
            
            return min(score, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_relationship_confidence(
        self,
        rel_text: str,
        rel_type: str,
        text: str
    ) -> float:
        """Calculate confidence score for discovered relationship."""
        confidence = 0.5  # Base confidence
        
        try:
            # Length-based confidence
            if len(rel_text) >= 15:
                confidence += 0.1
            
            # Relationship type specific confidence
            if rel_type in ["synonym", "antonym"]:
                confidence += 0.1  # These are usually more reliable
            
            # Frequency-based confidence
            rel_lower = rel_text.lower()
            text_lower = text.lower()
            frequency = text_lower.count(rel_lower)
            
            if frequency == 1:
                confidence += 0.1  # Unique relationship
            elif frequency <= 2:
                confidence += 0.05  # Few occurrences
            else:
                confidence -= 0.05  # Too many might indicate noise
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ Relationship confidence calculation failed: {e}")
            confidence = 0.5
        
        return round(confidence, 3)
    
    def _extract_entities_from_relationship(
        self,
        rel_text: str,
        entities: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Extract entity references from a relationship text."""
        entity_refs = []
        
        try:
            if not entities:
                return entity_refs
            
            for entity in entities:
                if entity["text"] in rel_text:
                    entity_refs.append(entity["text"])
            
            return entity_refs
            
        except Exception as e:
            logger.warning(f"⚠️ Entity extraction from relationship failed: {e}")
            return entity_refs
    
    async def _find_cross_references(
        self,
        text: str,
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find cross-references between entities."""
        cross_refs = []
        
        try:
            # Simple cross-reference detection
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities[i+1:], i+1):
                    # Check if entities appear near each other
                    if self._entities_are_nearby(entity1, entity2, text):
                        cross_ref = {
                            "text": f"{entity1['text']} - {entity2['text']}",
                            "type": "cross_reference",
                            "start_pos": min(entity1["start_pos"], entity2["start_pos"]),
                            "end_pos": max(entity1["end_pos"], entity2["end_pos"]),
                            "confidence": 0.7,
                            "source": "cross_reference_analysis",
                            "entity1": entity1["text"],
                            "entity2": entity2["text"],
                            "relationship_type": "co_occurrence"
                        }
                        cross_refs.append(cross_ref)
            
            return cross_refs
            
        except Exception as e:
            logger.warning(f"⚠️ Cross-reference discovery failed: {e}")
            return cross_refs
    
    def _entities_are_nearby(
        self,
        entity1: Dict[str, Any],
        entity2: Dict[str, Any],
        text: str,
        max_distance: int = 100
    ) -> bool:
        """Check if two entities are near each other in the text."""
        try:
            distance = abs(entity1["start_pos"] - entity2["start_pos"])
            return distance <= max_distance
        except Exception:
            return False
    
    def _find_cluster_center(self, contexts: List[Dict[str, Any]]) -> str:
        """Find the central context in a cluster."""
        try:
            if not contexts:
                return ""
            
            # Simple approach: return the context with highest confidence
            best_context = max(contexts, key=lambda x: x["confidence"])
            return best_context["text"]
            
        except Exception:
            return ""
    
    def _calculate_cluster_coherence(self, contexts: List[Dict[str, Any]]) -> float:
        """Calculate how coherent a cluster is."""
        try:
            if len(contexts) < 2:
                return 1.0
            
            # Simple coherence based on confidence scores
            avg_confidence = sum(c["confidence"] for c in contexts) / len(contexts)
            return min(avg_confidence, 1.0)
            
        except Exception:
            return 0.0
    
    def _extract_entities_from_contexts(
        self,
        contexts: List[Dict[str, Any]],
        entities: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Extract entities mentioned in contexts."""
        entity_refs = []
        
        try:
            if not entities:
                return entity_refs
            
            for context in contexts:
                for entity in entities:
                    if entity["text"] in context["text"]:
                        entity_refs.append(entity["text"])
            
            return list(set(entity_refs))  # Remove duplicates
            
        except Exception as e:
            logger.warning(f"⚠️ Entity extraction from contexts failed: {e}")
            return entity_refs
    
    def _extract_topic_keywords(self, contexts: List[Dict[str, Any]]) -> List[str]:
        """Extract keywords from contexts for topic identification."""
        keywords = []
        
        try:
            # Simple keyword extraction: words that appear frequently
            all_words = []
            for context in contexts:
                words = re.findall(r'\b\w+\b', context["text"].lower())
                all_words.extend(words)
            
            # Count word frequencies
            word_counts = Counter(all_words)
            
            # Return most common words (excluding common stopwords)
            stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            for word, count in word_counts.most_common(10):
                if word not in stopwords and len(word) > 2:
                    keywords.append(word)
            
            return keywords[:5]  # Return top 5 keywords
            
        except Exception as e:
            logger.warning(f"⚠️ Topic keyword extraction failed: {e}")
            return keywords
    
    def _analyze_document_characteristics(
        self,
        text: str,
        contexts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze document characteristics for classification."""
        characteristics = {
            "length": len(text),
            "context_types": Counter(context["type"] for context in contexts),
            "avg_context_length": 0,
            "technical_terms": 0,
            "formal_language": False,
            "has_definitions": False,
            "has_examples": False,
            "has_references": False
        }
        
        try:
            # Calculate average context length
            if contexts:
                characteristics["avg_context_length"] = sum(len(c["text"]) for c in contexts) / len(contexts)
            
            # Check for technical terms
            technical_patterns = [
                r'\b(?:algorithm|function|method|procedure|process|system|framework|architecture)\b',
                r'\b(?:API|SDK|REST|GraphQL|HTTP|JSON|XML|SQL|NoSQL)\b'
            ]
            
            for pattern in technical_patterns:
                characteristics["technical_terms"] += len(re.findall(pattern, text, re.IGNORECASE))
            
            # Check for formal language indicators
            formal_indicators = [
                r'\b(?:therefore|thus|consequently|hence|moreover|furthermore|additionally)\b',
                r'\b(?:in\s+conclusion|to\s+summarize|in\s+summary|as\s+a\s+result)\b'
            ]
            
            characteristics["formal_language"] = any(
                re.search(pattern, text, re.IGNORECASE) for pattern in formal_indicators
            )
            
            # Check for specific content types
            characteristics["has_definitions"] = any(c["type"] == "definition" for c in contexts)
            characteristics["has_examples"] = any(c["type"] == "example" for c in contexts)
            characteristics["has_references"] = any(c["type"] == "reference" for c in contexts)
            
            return characteristics
            
        except Exception as e:
            logger.warning(f"⚠️ Document characteristics analysis failed: {e}")
            return characteristics
    
    def _determine_document_type(self, characteristics: Dict[str, Any]) -> str:
        """Determine the type of document."""
        try:
            if characteristics["has_definitions"] and characteristics["has_examples"]:
                return "tutorial"
            elif characteristics["technical_terms"] > 10:
                return "technical_documentation"
            elif characteristics["formal_language"]:
                return "academic_paper"
            elif characteristics["has_references"]:
                return "research_paper"
            elif characteristics["length"] > 5000:
                return "long_form_content"
            else:
                return "general_content"
        except Exception:
            return "unknown"
    
    def _determine_document_domain(self, characteristics: Dict[str, Any]) -> str:
        """Determine the domain of the document."""
        try:
            if characteristics["technical_terms"] > 15:
                return "technology"
            elif characteristics["formal_language"]:
                return "academic"
            elif characteristics["has_definitions"]:
                return "educational"
            else:
                return "general"
        except Exception:
            return "unknown"
    
    def _determine_document_purpose(self, characteristics: Dict[str, Any]) -> str:
        """Determine the purpose of the document."""
        try:
            if characteristics["has_definitions"]:
                return "informative"
            elif characteristics["has_examples"]:
                return "instructional"
            elif characteristics["formal_language"]:
                return "academic"
            else:
                return "descriptive"
        except Exception:
            return "unknown"
    
    def _determine_document_audience(self, characteristics: Dict[str, Any]) -> str:
        """Determine the intended audience of the document."""
        try:
            if characteristics["technical_terms"] > 20:
                return "expert"
            elif characteristics["technical_terms"] > 10:
                return "intermediate"
            elif characteristics["formal_language"]:
                return "academic"
            else:
                return "general"
        except Exception:
            return "unknown"
    
    def _determine_complexity_level(self, characteristics: Dict[str, Any]) -> str:
        """Determine the complexity level of the document."""
        try:
            if characteristics["technical_terms"] > 25:
                return "advanced"
            elif characteristics["technical_terms"] > 15:
                return "intermediate"
            elif characteristics["technical_terms"] > 5:
                return "beginner"
            else:
                return "basic"
        except Exception:
            return "unknown"
    
    def _generate_document_tags(self, characteristics: Dict[str, Any]) -> List[str]:
        """Generate tags for the document."""
        tags = []
        
        try:
            # Add tags based on characteristics
            if characteristics["technical_terms"] > 10:
                tags.append("technical")
            
            if characteristics["formal_language"]:
                tags.append("formal")
            
            if characteristics["has_definitions"]:
                tags.append("educational")
            
            if characteristics["has_examples"]:
                tags.append("practical")
            
            if characteristics["length"] > 3000:
                tags.append("comprehensive")
            
            return tags
            
        except Exception:
            return tags
    
    def _generate_document_categories(self, characteristics: Dict[str, Any]) -> List[str]:
        """Generate categories for the document."""
        categories = []
        
        try:
            # Add categories based on characteristics
            if characteristics["technical_terms"] > 15:
                categories.append("Technical Documentation")
            
            if characteristics["formal_language"]:
                categories.append("Academic Content")
            
            if characteristics["has_definitions"]:
                categories.append("Educational Material")
            
            if characteristics["has_examples"]:
                categories.append("Tutorial Content")
            
            return categories
            
        except Exception:
            return categories
    
    def _calculate_classification_confidence(self, classification: Dict[str, Any]) -> float:
        """Calculate confidence in the document classification."""
        try:
            confidence = 0.0
            
            # Base confidence for each classification aspect
            if classification["document_type"] != "unknown":
                confidence += 0.2
            
            if classification["domain"] != "unknown":
                confidence += 0.2
            
            if classification["purpose"] != "unknown":
                confidence += 0.2
            
            if classification["audience"] != "unknown":
                confidence += 0.2
            
            if classification["complexity_level"] != "unknown":
                confidence += 0.2
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.0
    
    def _deduplicate_contexts(self, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate contexts."""
        seen = set()
        unique_contexts = []
        
        for context in contexts:
            key = (context["text"].lower(), context["type"])
            if key not in seen:
                seen.add(key)
                unique_contexts.append(context)
        
        return unique_contexts
    
    def _update_analysis_stats(
        self,
        contexts_extracted: int,
        relationships_discovered: int,
        structures_identified: int,
        processing_time: float
    ) -> None:
        """Update analysis statistics."""
        self.analysis_stats["documents_analyzed"] += 1
        self.analysis_stats["contexts_extracted"] += contexts_extracted
        self.analysis_stats["relationships_discovered"] += relationships_discovered
        self.analysis_stats["structures_identified"] += structures_identified
        self.analysis_stats["processing_time_ms"] += processing_time
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        stats = self.analysis_stats.copy()
        
        # Calculate averages
        if stats["documents_analyzed"] > 0:
            stats["avg_contexts_per_document"] = stats["contexts_extracted"] / stats["documents_analyzed"]
            stats["avg_relationships_per_document"] = stats["relationships_discovered"] / stats["documents_analyzed"]
            stats["avg_processing_time_ms"] = stats["processing_time_ms"] / stats["documents_analyzed"]
        else:
            stats["avg_contexts_per_document"] = 0
            stats["avg_relationships_per_document"] = 0
            stats["avg_processing_time_ms"] = 0
        
        # Calculate processing rate
        if stats["processing_time_ms"] > 0:
            stats["documents_per_second"] = stats["documents_analyzed"] / (stats["processing_time_ms"] / 1000)
        else:
            stats["documents_per_second"] = 0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset analysis statistics."""
        self.analysis_stats = {
            "documents_analyzed": 0,
            "contexts_extracted": 0,
            "relationships_discovered": 0,
            "structures_identified": 0,
            "processing_time_ms": 0
        }
        logger.info("🔄 Context analysis statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update analysis configuration."""
        self.config.update(new_config)
        
        # Reinitialize patterns and rules if needed
        if any(key in new_config for key in ["context_types", "semantic_rules"]):
            self._init_context_patterns()
            self._init_semantic_rules()
        
        logger.info("⚙️ Context analysis configuration updated")


