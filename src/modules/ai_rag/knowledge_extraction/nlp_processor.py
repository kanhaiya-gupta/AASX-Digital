"""
AI RAG NLP Processor
====================

Natural language processing for document analysis and knowledge extraction.
"""

import logging
import re
import string
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
import asyncio

logger = logging.getLogger(__name__)


class NLPProcessor:
    """
    NLP Processor for AI RAG Knowledge Extraction
    
    Handles text preprocessing, tokenization, part-of-speech tagging,
    named entity recognition, and semantic analysis for document processing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the NLP processor.
        
        Args:
            config: Configuration dictionary for NLP processing
        """
        self.config = config or self._get_default_config()
        self.processing_stats = {
            "documents_processed": 0,
            "total_tokens": 0,
            "total_sentences": 0,
            "entities_extracted": 0,
            "processing_time_ms": 0
        }
        
        # Initialize language-specific patterns
        self._init_language_patterns()
        
        logger.info("✅ NLPProcessor initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for NLP processing."""
        return {
            "language": "en",
            "min_token_length": 2,
            "max_token_length": 50,
            "remove_stopwords": True,
            "remove_punctuation": True,
            "remove_numbers": False,
            "case_sensitive": False,
            "normalize_whitespace": True,
            "preserve_sentences": True,
            "entity_types": ["PERSON", "ORGANIZATION", "LOCATION", "DATE", "TECHNOLOGY"],
            "confidence_threshold": 0.7,
            "max_entities_per_document": 1000,
            "batch_size": 100,
            "parallel_processing": True
        }
    
    def _init_language_patterns(self) -> None:
        """Initialize language-specific patterns and rules."""
        # English stopwords (common words to filter out)
        self.stopwords = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "will", "with", "the", "this", "but", "they", "have",
            "had", "what", "said", "each", "which", "she", "do", "how", "their",
            "if", "up", "out", "many", "then", "them", "these", "so", "some",
            "her", "would", "make", "like", "into", "him", "time", "two", "more",
            "go", "no", "way", "could", "my", "than", "first", "been", "call",
            "who", "its", "now", "find", "long", "down", "day", "did", "get",
            "come", "made", "may", "part"
        }
        
        # Punctuation patterns
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        
        # Number patterns
        self.number_pattern = re.compile(r'\b\d+(?:\.\d+)?\b')
        
        # Sentence boundary patterns
        self.sentence_pattern = re.compile(r'(?<=[.!?])\s+')
        
        # Entity patterns for basic extraction
        self.entity_patterns = {
            "PERSON": [
                r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
                r'\b[A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+\b',  # First M. Last
            ],
            "ORGANIZATION": [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Corporation|Organization)\b',
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:University|Institute|Laboratory|Center|Foundation)\b',
            ],
            "LOCATION": [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:City|State|Country|Province|Region)\b',
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|Avenue|Road|Boulevard|Lane)\b',
            ],
            "DATE": [
                r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY
                r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            ],
            "TECHNOLOGY": [
                r'\b[A-Z][A-Z0-9]+\b',  # Acronyms (likely technologies)
                r'\b(?:API|SDK|REST|GraphQL|Docker|Kubernetes|Python|Java|JavaScript|React|Angular|Vue)\b',
            ]
        }
        
        logger.info(f"🌐 Language patterns initialized for: {self.config['language']}")
    
    async def process_document(
        self,
        text: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a document through the NLP pipeline.
        
        Args:
            text: Document text to process
            document_id: Optional document identifier
            metadata: Optional document metadata
            
        Returns:
            Dict: Processing results including tokens, sentences, entities, and analysis
        """
        start_time = asyncio.get_event_loop().time()
        logger.info(f"📄 Starting NLP processing for document: {document_id or 'unknown'}")
        
        try:
            # Preprocess text
            processed_text = await self._preprocess_text(text)
            
            # Tokenize
            tokens = await self._tokenize_text(processed_text)
            
            # Extract sentences
            sentences = await self._extract_sentences(text)
            
            # Extract entities
            entities = await self._extract_entities(text, tokens)
            
            # Analyze text structure
            text_analysis = await self._analyze_text_structure(tokens, sentences, entities)
            
            # Calculate processing time
            end_time = asyncio.get_event_loop().time()
            processing_time = (end_time - start_time) * 1000
            
            # Update statistics
            self._update_processing_stats(len(tokens), len(sentences), len(entities), processing_time)
            
            results = {
                "document_id": document_id,
                "metadata": metadata or {},
                "processing_timestamp": asyncio.get_event_loop().time(),
                "processing_time_ms": processing_time,
                "text_length": len(text),
                "processed_text": processed_text,
                "tokens": tokens,
                "sentences": sentences,
                "entities": entities,
                "text_analysis": text_analysis,
                "nlp_metadata": {
                    "language": self.config["language"],
                    "config_used": self.config.copy(),
                    "processing_stats": self.processing_stats.copy()
                }
            }
            
            logger.info(f"✅ NLP processing completed: {document_id or 'unknown'} - {len(tokens)} tokens, {len(entities)} entities")
            return results
            
        except Exception as e:
            logger.error(f"❌ NLP processing failed: {e}")
            return {
                "document_id": document_id,
                "metadata": metadata or {},
                "processing_timestamp": asyncio.get_event_loop().time(),
                "processing_time_ms": 0,
                "error": str(e),
                "tokens": [],
                "sentences": [],
                "entities": [],
                "text_analysis": {}
            }
    
    async def _preprocess_text(self, text: str) -> str:
        """Preprocess text for NLP analysis."""
        if not text:
            return ""
        
        processed = text
        
        # Normalize whitespace
        if self.config["normalize_whitespace"]:
            processed = re.sub(r'\s+', ' ', processed).strip()
        
        # Remove punctuation
        if self.config["remove_punctuation"]:
            processed = self.punctuation_pattern.sub(' ', processed)
        
        # Remove numbers
        if self.config["remove_numbers"]:
            processed = self.number_pattern.sub('', processed)
        
        # Case normalization
        if not self.config["case_sensitive"]:
            processed = processed.lower()
        
        # Final whitespace normalization
        if self.config["normalize_whitespace"]:
            processed = re.sub(r'\s+', ' ', processed).strip()
        
        return processed
    
    async def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into individual words/tokens."""
        if not text:
            return []
        
        # Split on whitespace
        tokens = text.split()
        
        # Filter tokens by length
        filtered_tokens = []
        for token in tokens:
            if (len(token) >= self.config["min_token_length"] and 
                len(token) <= self.config["max_token_length"]):
                
                # Remove stopwords if configured
                if (self.config["remove_stopwords"] and 
                    token.lower() in self.stopwords):
                    continue
                
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    async def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        if not text or not self.config["preserve_sentences"]:
            return []
        
        # Split on sentence boundaries
        sentences = self.sentence_pattern.split(text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    async def _extract_entities(self, text: str, tokens: List[str]) -> List[Dict[str, Any]]:
        """Extract named entities from text using pattern matching."""
        entities = []
        
        try:
            # Extract entities using patterns
            for entity_type, patterns in self.entity_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        entity_text = match.group()
                        confidence = self._calculate_entity_confidence(entity_text, entity_type, text)
                        
                        if confidence >= self.config["confidence_threshold"]:
                            entity = {
                                "text": entity_text,
                                "type": entity_type,
                                "start_pos": match.start(),
                                "end_pos": match.end(),
                                "confidence": confidence,
                                "source": "pattern_matching"
                            }
                            entities.append(entity)
            
            # Limit entities per document
            if len(entities) > self.config["max_entities_per_document"]:
                # Sort by confidence and keep top entities
                entities.sort(key=lambda x: x["confidence"], reverse=True)
                entities = entities[:self.config["max_entities_per_document"]]
                logger.warning(f"⚠️ Limited entities to {self.config['max_entities_per_document']} (highest confidence)")
            
            # Remove duplicates (same text and type)
            seen = set()
            unique_entities = []
            for entity in entities:
                key = (entity["text"].lower(), entity["type"])
                if key not in seen:
                    seen.add(key)
                    unique_entities.append(entity)
            
            logger.info(f"🔍 Extracted {len(unique_entities)} entities from {len(tokens)} tokens")
            return unique_entities
            
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return []
    
    async def _analyze_text_structure(
        self,
        tokens: List[str],
        sentences: List[str],
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze text structure and characteristics."""
        analysis = {}
        
        try:
            # Token analysis
            if tokens:
                token_freq = Counter(tokens)
                analysis["token_analysis"] = {
                    "total_tokens": len(tokens),
                    "unique_tokens": len(token_freq),
                    "vocabulary_diversity": len(token_freq) / len(tokens) if tokens else 0,
                    "most_common_tokens": token_freq.most_common(10),
                    "average_token_length": sum(len(token) for token in tokens) / len(tokens) if tokens else 0
                }
            
            # Sentence analysis
            if sentences:
                sentence_lengths = [len(sentence.split()) for sentence in sentences]
                analysis["sentence_analysis"] = {
                    "total_sentences": len(sentences),
                    "average_sentence_length": sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
                    "min_sentence_length": min(sentence_lengths) if sentence_lengths else 0,
                    "max_sentence_length": max(sentence_lengths) if sentence_lengths else 0
                }
            
            # Entity analysis
            if entities:
                entity_types = Counter(entity["type"] for entity in entities)
                analysis["entity_analysis"] = {
                    "total_entities": len(entities),
                    "entity_types": dict(entity_types),
                    "average_confidence": sum(entity["confidence"] for entity in entities) / len(entities) if entities else 0,
                    "entities_by_source": Counter(entity["source"] for entity in entities)
                }
            
            # Text complexity metrics
            if tokens and sentences:
                analysis["complexity_metrics"] = {
                    "type_token_ratio": len(set(tokens)) / len(tokens) if tokens else 0,
                    "sentence_complexity": len(tokens) / len(sentences) if sentences else 0,
                    "entity_density": len(entities) / len(tokens) if tokens else 0
                }
            
        except Exception as e:
            logger.error(f"❌ Text structure analysis failed: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    def _calculate_entity_confidence(self, entity_text: str, entity_type: str, context: str) -> float:
        """Calculate confidence score for extracted entity."""
        confidence = 0.5  # Base confidence
        
        try:
            # Length-based confidence
            if len(entity_text) >= 3:
                confidence += 0.1
            
            # Case pattern confidence
            if entity_text[0].isupper():
                confidence += 0.1
            
            # Context frequency confidence
            context_lower = context.lower()
            entity_lower = entity_text.lower()
            frequency = context_lower.count(entity_lower)
            
            if frequency == 1:
                confidence += 0.1  # Unique mention
            elif frequency <= 3:
                confidence += 0.05  # Few mentions
            else:
                confidence -= 0.05  # Too many mentions might indicate noise
            
            # Entity type specific confidence
            if entity_type == "PERSON":
                if " " in entity_text:  # Has first and last name
                    confidence += 0.1
            elif entity_type == "ORGANIZATION":
                if any(word in entity_text.lower() for word in ["inc", "corp", "llc", "university", "institute"]):
                    confidence += 0.1
            elif entity_type == "TECHNOLOGY":
                if entity_text.isupper():  # Acronym
                    confidence += 0.1
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ Confidence calculation failed: {e}")
            confidence = 0.5
        
        return round(confidence, 3)
    
    async def process_batch(
        self,
        documents: List[Dict[str, Any]],
        batch_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple documents in batch.
        
        Args:
            documents: List of documents with 'text' and optional 'id' keys
            batch_size: Optional batch size override
            
        Returns:
            List: Processing results for all documents
        """
        batch_size = batch_size or self.config["batch_size"]
        results = []
        
        logger.info(f"📚 Starting batch processing of {len(documents)} documents")
        
        try:
            if self.config["parallel_processing"]:
                # Process documents in parallel
                tasks = []
                for doc in documents:
                    task = self.process_document(
                        doc.get("text", ""),
                        doc.get("id"),
                        doc.get("metadata")
                    )
                    tasks.append(task)
                
                # Execute all tasks concurrently
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle any exceptions
                for i, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ Document {i} processing failed: {result}")
                        results.append({
                            "document_id": documents[i].get("id"),
                            "error": str(result),
                            "tokens": [],
                            "sentences": [],
                            "entities": [],
                            "text_analysis": {}
                        })
                    else:
                        results.append(result)
            else:
                # Process documents sequentially
                for doc in documents:
                    result = await self.process_document(
                        doc.get("text", ""),
                        doc.get("id"),
                        doc.get("metadata")
                    )
                    results.append(result)
            
            logger.info(f"✅ Batch processing completed: {len(results)} documents processed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return []
    
    def _update_processing_stats(
        self,
        token_count: int,
        sentence_count: int,
        entity_count: int,
        processing_time: float
    ) -> None:
        """Update processing statistics."""
        self.processing_stats["documents_processed"] += 1
        self.processing_stats["total_tokens"] += token_count
        self.processing_stats["total_sentences"] += sentence_count
        self.processing_stats["entities_extracted"] += entity_count
        self.processing_stats["processing_time_ms"] += processing_time
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.processing_stats.copy()
        
        # Calculate averages
        if stats["documents_processed"] > 0:
            stats["avg_tokens_per_document"] = stats["total_tokens"] / stats["documents_processed"]
            stats["avg_sentences_per_document"] = stats["total_sentences"] / stats["documents_processed"]
            stats["avg_entities_per_document"] = stats["entities_extracted"] / stats["documents_processed"]
            stats["avg_processing_time_ms"] = stats["processing_time_ms"] / stats["documents_processed"]
        else:
            stats["avg_tokens_per_document"] = 0
            stats["avg_sentences_per_document"] = 0
            stats["avg_entities_per_document"] = 0
            stats["avg_processing_time_ms"] = 0
        
        # Calculate processing rate
        if stats["processing_time_ms"] > 0:
            stats["documents_per_second"] = stats["documents_processed"] / (stats["processing_time_ms"] / 1000)
        else:
            stats["documents_per_second"] = 0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.processing_stats = {
            "documents_processed": 0,
            "total_tokens": 0,
            "total_sentences": 0,
            "entities_extracted": 0,
            "processing_time_ms": 0
        }
        logger.info("🔄 NLP processing statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update processing configuration."""
        self.config.update(new_config)
        
        # Reinitialize patterns if language changed
        if "language" in new_config:
            self._init_language_patterns()
        
        logger.info("⚙️ NLP processing configuration updated")


