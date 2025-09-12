"""
AI RAG Entity Recognizer
========================

Named entity recognition and entity classification for knowledge extraction.
"""

import logging
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
import asyncio

logger = logging.getLogger(__name__)


class EntityRecognizer:
    """
    Entity Recognizer for AI RAG Knowledge Extraction
    
    Specializes in named entity recognition, entity classification,
    entity linking, and entity disambiguation for document processing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the entity recognizer.
        
        Args:
            config: Configuration dictionary for entity recognition
        """
        self.config = config or self._get_default_config()
        self.recognition_stats = {
            "entities_recognized": 0,
            "entities_classified": 0,
            "entities_linked": 0,
            "entities_disambiguated": 0,
            "processing_time_ms": 0
        }
        
        # Initialize entity patterns and rules
        self._init_entity_patterns()
        self._init_entity_classifiers()
        
        logger.info("✅ EntityRecognizer initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for entity recognition."""
        return {
            "entity_types": [
                "PERSON", "ORGANIZATION", "LOCATION", "DATE", "TIME",
                "MONEY", "PERCENT", "QUANTITY", "TECHNOLOGY", "PRODUCT",
                "EVENT", "CONCEPT", "SKILL", "CERTIFICATION", "PROJECT"
            ],
            "confidence_threshold": 0.6,
            "max_entities_per_type": 100,
            "enable_entity_linking": True,
            "enable_disambiguation": True,
            "enable_hierarchical_classification": True,
            "enable_cross_reference": True,
            "batch_size": 50,
            "parallel_processing": True,
            "use_external_apis": False,
            "external_api_keys": {},
            "entity_database_path": None
        }
    
    def _init_entity_patterns(self) -> None:
        """Initialize entity recognition patterns."""
        self.entity_patterns = {
            "PERSON": [
                # Full names
                r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                r'\b[A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+\b',
                r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                # Titles with names
                r'\b(?:Dr|Prof|Professor|Mr|Mrs|Ms|Sir|Lady)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                # Initials
                r'\b[A-Z]\.[A-Z]\.\s+[A-Z][a-z]+\b'
            ],
            "ORGANIZATION": [
                # Companies
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Corporation|Organization|Group|Systems|Technologies|Solutions)\b',
                # Educational institutions
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:University|College|Institute|School|Academy|Laboratory|Center|Foundation)\b',
                # Government agencies
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Department|Agency|Bureau|Office|Ministry|Commission)\b',
                # Non-profits
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Foundation|Charity|Association|Society|Council|Alliance)\b'
            ],
            "LOCATION": [
                # Cities, States, Countries
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:City|State|Country|Province|Region|District|County)\b',
                # Addresses
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|Avenue|Road|Boulevard|Lane|Drive|Way|Place)\b',
                # Geographic features
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Mountain|River|Lake|Ocean|Sea|Forest|Desert|Valley)\b',
                # Coordinates
                r'\b\d+°\s*\d+\'\s*\d+"\s*[NS]\s*,\s*\d+°\s*\d+\'\s*\d+"\s*[EW]\b'
            ],
            "DATE": [
                # Various date formats
                r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',
                # Written dates
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
                # Relative dates
                r'\b(?:today|yesterday|tomorrow|next\s+week|last\s+month|this\s+year)\b'
            ],
            "TIME": [
                # Time formats
                r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b',
                r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:UTC|GMT|EST|PST|CST|MST)\b',
                # Relative times
                r'\b(?:morning|afternoon|evening|night|noon|midnight)\b'
            ],
            "MONEY": [
                # Currency amounts
                r'\b\$\s*\d+(?:,\d{3})*(?:\.\d{2})?\b',
                r'\b(?:USD|EUR|GBP|JPY|CAD|AUD)\s*\d+(?:,\d{3})*(?:\.\d{2})?\b',
                r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|euros|pounds|yen)\b'
            ],
            "PERCENT": [
                # Percentage values
                r'\b\d+(?:\.\d+)?%\b',
                r'\b\d+(?:\.\d+)?\s*percent\b',
                r'\b\d+(?:\.\d+)?\s*per\s*cent\b'
            ],
            "QUANTITY": [
                # Measurements
                r'\b\d+(?:\.\d+)?\s*(?:kg|lb|g|oz|km|mi|m|ft|cm|in|L|gal|ml|fl\s*oz)\b',
                r'\b\d+(?:\.\d+)?\s*(?:kilograms|pounds|grams|ounces|kilometers|miles|meters|feet|centimeters|inches|liters|gallons|milliliters)\b'
            ],
            "TECHNOLOGY": [
                # Programming languages
                r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin|PHP|Ruby|Scala|R|MATLAB)\b',
                # Frameworks and libraries
                r'\b(?:React|Angular|Vue|Django|Flask|Spring|Express|Node\.js|TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy)\b',
                # Tools and platforms
                r'\b(?:Docker|Kubernetes|AWS|Azure|GCP|Git|Jenkins|Jira|Confluence|Slack|Zoom|Teams)\b',
                # Protocols and standards
                r'\b(?:HTTP|HTTPS|REST|GraphQL|SOAP|gRPC|WebSocket|OAuth|JWT|OpenAPI|GraphQL|RDF|OWL)\b'
            ],
            "PRODUCT": [
                # Software products
                r'\b(?:Microsoft\s+Office|Adobe\s+Creative\s+Suite|Google\s+Workspace|Slack|Zoom|Teams|Chrome|Firefox|Safari)\b',
                # Hardware products
                r'\b(?:iPhone|iPad|MacBook|Dell\s+XPS|HP\s+Spectre|Lenovo\s+ThinkPad|Samsung\s+Galaxy|Google\s+Pixel)\b'
            ],
            "EVENT": [
                # Conferences and meetings
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Conference|Summit|Workshop|Symposium|Meeting|Webinar|Hackathon)\b',
                # Dates with events
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\s+(?:Conference|Summit|Workshop)\b'
            ],
            "CONCEPT": [
                # Abstract concepts
                r'\b(?:Artificial\s+Intelligence|Machine\s+Learning|Deep\s+Learning|Data\s+Science|Big\s+Data|Cloud\s+Computing|Blockchain|Internet\s+of\s+Things)\b',
                r'\b(?:Digital\s+Transformation|Industry\s+4\.0|Smart\s+Cities|Sustainable\s+Development|Circular\s+Economy|Green\s+Technology)\b'
            ],
            "SKILL": [
                # Technical skills
                r'\b(?:Programming|Coding|Software\s+Development|Data\s+Analysis|Project\s+Management|Leadership|Communication|Problem\s+Solving)\b',
                r'\b(?:Agile|Scrum|DevOps|CI/CD|Testing|Debugging|Architecture|Design\s+Patterns|Algorithms|Data\s+Structures)\b'
            ],
            "CERTIFICATION": [
                # Professional certifications
                r'\b(?:PMP|PMP®|AWS\s+Certified|Microsoft\s+Certified|Google\s+Certified|CISSP|CompTIA|ITIL|PRINCE2)\b',
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Certification|Certificate|Diploma|Degree|License)\b'
            ],
            "PROJECT": [
                # Project names
                r'\b(?:Project\s+[A-Z][a-z]+|Initiative\s+[A-Z][a-z]+|Program\s+[A-Z][a-z]+|Campaign\s+[A-Z][a-z]+)\b',
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Project|Initiative|Program|Campaign|Study|Research)\b'
            ]
        }
        
        logger.info(f"🔍 Entity patterns initialized for {len(self.entity_patterns)} entity types")
    
    def _init_entity_classifiers(self) -> None:
        """Initialize entity classification rules and heuristics."""
        self.entity_classifiers = {
            "PERSON": {
                "indicators": ["title", "name", "person", "individual", "user", "employee", "student"],
                "context_words": ["said", "reported", "announced", "stated", "commented", "explained"],
                "exclude_patterns": [r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:Inc|Corp|LLC|Company)\b']
            },
            "ORGANIZATION": {
                "indicators": ["company", "organization", "institution", "agency", "corporation", "foundation"],
                "context_words": ["announced", "released", "published", "developed", "launched", "acquired"],
                "exclude_patterns": []
            },
            "LOCATION": {
                "indicators": ["city", "country", "state", "region", "area", "location", "place"],
                "context_words": ["located", "situated", "based", "headquartered", "established", "founded"],
                "exclude_patterns": []
            },
            "TECHNOLOGY": {
                "indicators": ["technology", "platform", "framework", "library", "tool", "software", "system"],
                "context_words": ["developed", "built", "created", "implemented", "deployed", "integrated"],
                "exclude_patterns": []
            }
        }
        
        logger.info(f"🏷️ Entity classifiers initialized for {len(self.entity_classifiers)} entity types")
    
    async def recognize_entities(
        self,
        text: str,
        document_id: Optional[str] = None,
        entity_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recognize entities in text using pattern matching and classification.
        
        Args:
            text: Text to analyze for entities
            document_id: Optional document identifier
            entity_types: Specific entity types to look for
            
        Returns:
            List: Recognized entities with metadata
        """
        start_time = asyncio.get_event_loop().time()
        logger.info(f"🔍 Starting entity recognition for document: {document_id or 'unknown'}")
        
        try:
            # Use specified entity types or all available
            types_to_check = entity_types or self.config["entity_types"]
            
            # Extract entities using patterns
            entities = await self._extract_entities_with_patterns(text, types_to_check)
            
            # Classify entities
            classified_entities = await self._classify_entities(entities, text)
            
            # Link entities if enabled
            if self.config["enable_entity_linking"]:
                linked_entities = await self._link_entities(classified_entities, text)
            else:
                linked_entities = classified_entities
            
            # Disambiguate entities if enabled
            if self.config["enable_disambiguation"]:
                disambiguated_entities = await self._disambiguate_entities(linked_entities, text)
            else:
                disambiguated_entities = linked_entities
            
            # Calculate processing time
            end_time = asyncio.get_event_loop().time()
            processing_time = (end_time - start_time) * 1000
            
            # Update statistics
            self._update_recognition_stats(len(entities), len(classified_entities), 
                                         len(linked_entities), len(disambiguated_entities), processing_time)
            
            logger.info(f"✅ Entity recognition completed: {len(disambiguated_entities)} entities recognized")
            return disambiguated_entities
            
        except Exception as e:
            logger.error(f"❌ Entity recognition failed: {e}")
            return []
    
    async def _extract_entities_with_patterns(
        self,
        text: str,
        entity_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Extract entities using predefined patterns."""
        entities = []
        
        try:
            for entity_type in entity_types:
                if entity_type in self.entity_patterns:
                    patterns = self.entity_patterns[entity_type]
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, text, re.IGNORECASE)
                        
                        for match in matches:
                            entity_text = match.group()
                            confidence = self._calculate_pattern_confidence(entity_text, entity_type, text)
                            
                            if confidence >= self.config["confidence_threshold"]:
                                entity = {
                                    "text": entity_text,
                                    "type": entity_type,
                                    "start_pos": match.start(),
                                    "end_pos": match.end(),
                                    "confidence": confidence,
                                    "source": "pattern_matching",
                                    "raw_match": match.group(0),
                                    "context": self._extract_context(text, match.start(), match.end())
                                }
                                entities.append(entity)
            
            # Remove duplicates and limit per type
            entities = self._deduplicate_entities(entities)
            entities = self._limit_entities_per_type(entities)
            
            return entities
            
        except Exception as e:
            logger.error(f"❌ Pattern-based entity extraction failed: {e}")
            return []
    
    async def _classify_entities(
        self,
        entities: List[Dict[str, Any]],
        text: str
    ) -> List[Dict[str, Any]]:
        """Classify entities using contextual analysis and heuristics."""
        classified_entities = []
        
        try:
            for entity in entities:
                # Apply classification rules
                classification = await self._apply_classification_rules(entity, text)
                
                # Update entity with classification results
                entity.update(classification)
                
                # Add hierarchical classification if enabled
                if self.config["enable_hierarchical_classification"]:
                    hierarchy = await self._determine_entity_hierarchy(entity, text)
                    entity["hierarchy"] = hierarchy
                
                classified_entities.append(entity)
            
            return classified_entities
            
        except Exception as e:
            logger.error(f"❌ Entity classification failed: {e}")
            return entities
    
    async def _link_entities(
        self,
        entities: List[Dict[str, Any]],
        text: str
    ) -> List[Dict[str, Any]]:
        """Link entities to external knowledge bases or databases."""
        linked_entities = []
        
        try:
            for entity in entities:
                # Basic entity linking (placeholder for external API integration)
                linking_result = await self._perform_entity_linking(entity, text)
                
                # Update entity with linking information
                entity.update(linking_result)
                
                linked_entities.append(entity)
            
            return linked_entities
            
        except Exception as e:
            logger.error(f"❌ Entity linking failed: {e}")
            return entities
    
    async def _disambiguate_entities(
        self,
        entities: List[Dict[str, Any]],
        text: str
    ) -> List[Dict[str, Any]]:
        """Disambiguate entities using context and cross-references."""
        disambiguated_entities = []
        
        try:
            # Group entities by text for disambiguation
            entity_groups = defaultdict(list)
            for entity in entities:
                entity_groups[entity["text"].lower()].append(entity)
            
            # Disambiguate each group
            for text_key, group in entity_groups.items():
                if len(group) == 1:
                    # Single entity, no disambiguation needed
                    disambiguated_entities.append(group[0])
                else:
                    # Multiple entities with same text, disambiguate
                    disambiguated = await self._disambiguate_entity_group(group, text)
                    disambiguated_entities.extend(disambiguated)
            
            return disambiguated_entities
            
        except Exception as e:
            logger.error(f"❌ Entity disambiguation failed: {e}")
            return entities
    
    async def _apply_classification_rules(
        self,
        entity: Dict[str, Any],
        text: str
    ) -> Dict[str, Any]:
        """Apply classification rules to an entity."""
        classification = {
            "classification_confidence": entity["confidence"],
            "classification_method": "rule_based",
            "subtype": None,
            "attributes": {}
        }
        
        try:
            entity_type = entity["type"]
            entity_text = entity["text"]
            context = entity["context"]
            
            # Apply type-specific classification rules
            if entity_type in self.entity_classifiers:
                classifier = self.entity_classifiers[entity_type]
                
                # Check context indicators
                context_score = 0
                for indicator in classifier["indicators"]:
                    if indicator.lower() in context.lower():
                        context_score += 0.1
                
                # Check context words
                for word in classifier["context_words"]:
                    if word.lower() in context.lower():
                        context_score += 0.05
                
                # Apply context score
                classification["classification_confidence"] = min(
                    entity["confidence"] + context_score, 1.0
                )
                
                # Determine subtype
                subtype = await self._determine_entity_subtype(entity, text)
                classification["subtype"] = subtype
                
                # Extract attributes
                attributes = await self._extract_entity_attributes(entity, text)
                classification["attributes"] = attributes
            
            return classification
            
        except Exception as e:
            logger.warning(f"⚠️ Classification rule application failed: {e}")
            return classification
    
    async def _determine_entity_hierarchy(
        self,
        entity: Dict[str, Any],
        text: str
    ) -> Dict[str, Any]:
        """Determine hierarchical classification for an entity."""
        hierarchy = {
            "level": "primary",
            "parent_entities": [],
            "child_entities": [],
            "related_entities": []
        }
        
        try:
            entity_type = entity["type"]
            entity_text = entity["text"]
            
            # Simple hierarchy rules
            if entity_type == "ORGANIZATION":
                if any(word in entity_text.lower() for word in ["department", "division", "unit"]):
                    hierarchy["level"] = "subordinate"
                elif any(word in entity_text.lower() for word in ["group", "holding", "parent"]):
                    hierarchy["level"] = "parent"
            
            elif entity_type == "LOCATION":
                if any(word in entity_text.lower() for word in ["city", "town", "village"]):
                    hierarchy["level"] = "municipality"
                elif any(word in entity_text.lower() for word in ["state", "province", "region"]):
                    hierarchy["level"] = "administrative"
                elif any(word in entity_text.lower() for word in ["country", "nation"]):
                    hierarchy["level"] = "national"
            
            return hierarchy
            
        except Exception as e:
            logger.warning(f"⚠️ Hierarchy determination failed: {e}")
            return hierarchy
    
    async def _perform_entity_linking(
        self,
        entity: Dict[str, Any],
        text: str
    ) -> Dict[str, Any]:
        """Perform entity linking to external knowledge bases."""
        linking_result = {
            "linked_entities": [],
            "external_ids": [],
            "knowledge_base": None,
            "linking_confidence": 0.0
        }
        
        try:
            # Placeholder for external API integration
            # In a real implementation, this would call external APIs
            
            if self.config["use_external_apis"]:
                # Example: Wikipedia API, Wikidata, etc.
                pass
            
            # Basic internal linking
            internal_links = await self._find_internal_entity_links(entity, text)
            linking_result["linked_entities"] = internal_links
            
            return linking_result
            
        except Exception as e:
            logger.warning(f"⚠️ Entity linking failed: {e}")
            return linking_result
    
    async def _disambiguate_entity_group(
        self,
        entities: List[Dict[str, Any]],
        text: str
    ) -> List[Dict[str, Any]]:
        """Disambiguate a group of entities with the same text."""
        disambiguated = []
        
        try:
            for entity in entities:
                # Apply disambiguation rules
                disambiguation = await self._apply_disambiguation_rules(entity, text)
                
                # Update entity with disambiguation results
                entity.update(disambiguation)
                
                disambiguated.append(entity)
            
            return disambiguated
            
        except Exception as e:
            logger.warning(f"⚠️ Entity group disambiguation failed: {e}")
            return entities
    
    async def _determine_entity_subtype(
        self,
        entity: Dict[str, Any],
        text: str
    ) -> Optional[str]:
        """Determine the subtype of an entity."""
        try:
            entity_type = entity["type"]
            entity_text = entity["text"]
            
            if entity_type == "PERSON":
                if "Dr" in entity_text or "Professor" in entity_text:
                    return "academic"
                elif "Mr" in entity_text or "Mrs" in entity_text or "Ms" in entity_text:
                    return "professional"
                else:
                    return "individual"
            
            elif entity_type == "ORGANIZATION":
                if any(word in entity_text.lower() for word in ["university", "college", "institute"]):
                    return "educational"
                elif any(word in entity_text.lower() for word in ["inc", "corp", "llc"]):
                    return "commercial"
                elif any(word in entity_text.lower() for word in ["government", "agency", "bureau"]):
                    return "governmental"
                else:
                    return "organization"
            
            elif entity_type == "TECHNOLOGY":
                if any(word in entity_text.lower() for word in ["python", "java", "javascript"]):
                    return "programming_language"
                elif any(word in entity_text.lower() for word in ["react", "angular", "vue"]):
                    return "framework"
                elif any(word in entity_text.lower() for word in ["docker", "kubernetes"]):
                    return "platform"
                else:
                    return "technology"
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Subtype determination failed: {e}")
            return None
    
    async def _extract_entity_attributes(
        self,
        entity: Dict[str, Any],
        text: str
    ) -> Dict[str, Any]:
        """Extract attributes for an entity."""
        attributes = {}
        
        try:
            entity_type = entity["type"]
            entity_text = entity["text"]
            context = entity["context"]
            
            if entity_type == "PERSON":
                # Extract potential titles
                title_patterns = [r'\b(?:Dr|Prof|Professor|Mr|Mrs|Ms|Sir|Lady)\b']
                for pattern in title_patterns:
                    if re.search(pattern, context, re.IGNORECASE):
                        attributes["title"] = re.search(pattern, context, re.IGNORECASE).group()
                        break
            
            elif entity_type == "ORGANIZATION":
                # Extract organization type
                org_patterns = [
                    (r'\b(?:Inc|Corp|LLC|Ltd)\b', 'company_type'),
                    (r'\b(?:University|College|Institute)\b', 'institution_type'),
                    (r'\b(?:Department|Agency|Bureau)\b', 'government_type')
                ]
                
                for pattern, attr_name in org_patterns:
                    if re.search(pattern, context, re.IGNORECASE):
                        attributes[attr_name] = re.search(pattern, context, re.IGNORECASE).group()
                        break
            
            elif entity_type == "LOCATION":
                # Extract location type
                loc_patterns = [
                    (r'\b(?:City|Town|Village)\b', 'settlement_type'),
                    (r'\b(?:State|Province|Region)\b', 'administrative_type'),
                    (r'\b(?:Country|Nation)\b', 'national_type')
                ]
                
                for pattern, attr_name in loc_patterns:
                    if re.search(pattern, context, re.IGNORECASE):
                        attributes[attr_name] = re.search(pattern, context, re.IGNORECASE).group()
                        break
            
            return attributes
            
        except Exception as e:
            logger.warning(f"⚠️ Attribute extraction failed: {e}")
            return attributes
    
    async def _find_internal_entity_links(
        self,
        entity: Dict[str, Any],
        text: str
    ) -> List[Dict[str, Any]]:
        """Find internal entity links within the same document."""
        links = []
        
        try:
            entity_text = entity["text"]
            entity_type = entity["type"]
            
            # Find related entities of the same type
            for match in re.finditer(re.escape(entity_text), text, re.IGNORECASE):
                if match.start() != entity["start_pos"]:  # Different occurrence
                    link = {
                        "linked_entity": entity_text,
                        "link_type": "same_entity",
                        "position": match.start(),
                        "context": self._extract_context(text, match.start(), match.end())
                    }
                    links.append(link)
            
            return links
            
        except Exception as e:
            logger.warning(f"⚠️ Internal linking failed: {e}")
            return links
    
    async def _apply_disambiguation_rules(
        self,
        entity: Dict[str, Any],
        text: str
    ) -> Dict[str, Any]:
        """Apply disambiguation rules to an entity."""
        disambiguation = {
            "disambiguated": False,
            "disambiguation_method": None,
            "disambiguation_confidence": 0.0,
            "alternative_meanings": []
        }
        
        try:
            entity_text = entity["text"]
            entity_type = entity["type"]
            context = entity["context"]
            
            # Simple disambiguation based on context
            if entity_type == "PERSON":
                # Check if it's a person or organization
                if any(word in context.lower() for word in ["said", "reported", "announced"]):
                    disambiguation["disambiguated"] = True
                    disambiguation["disambiguation_method"] = "context_analysis"
                    disambiguation["disambiguation_confidence"] = 0.8
            
            elif entity_type == "ORGANIZATION":
                # Check if it's an organization or location
                if any(word in context.lower() for word in ["announced", "released", "developed"]):
                    disambiguation["disambiguated"] = True
                    disambiguation["disambiguation_method"] = "context_analysis"
                    disambiguation["disambiguation_confidence"] = 0.8
            
            return disambiguation
            
        except Exception as e:
            logger.warning(f"⚠️ Disambiguation rule application failed: {e}")
            return disambiguation
    
    def _calculate_pattern_confidence(
        self,
        entity_text: str,
        entity_type: str,
        text: str
    ) -> float:
        """Calculate confidence score for pattern-matched entity."""
        confidence = 0.5  # Base confidence
        
        try:
            # Length-based confidence
            if len(entity_text) >= 3:
                confidence += 0.1
            
            # Case pattern confidence
            if entity_text[0].isupper():
                confidence += 0.1
            
            # Context frequency confidence
            context_lower = text.lower()
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
    
    def _extract_context(
        self,
        text: str,
        start_pos: int,
        end_pos: int,
        context_window: int = 100
    ) -> str:
        """Extract context around an entity."""
        try:
            context_start = max(0, start_pos - context_window)
            context_end = min(len(text), end_pos + context_window)
            
            return text[context_start:context_end].strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Context extraction failed: {e}")
            return ""
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities based on text and type."""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity["text"].lower(), entity["type"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _limit_entities_per_type(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Limit the number of entities per type."""
        type_counts = defaultdict(int)
        limited_entities = []
        
        for entity in entities:
            entity_type = entity["type"]
            if type_counts[entity_type] < self.config["max_entities_per_type"]:
                type_counts[entity_type] += 1
                limited_entities.append(entity)
        
        return limited_entities
    
    def _update_recognition_stats(
        self,
        entities_recognized: int,
        entities_classified: int,
        entities_linked: int,
        entities_disambiguated: int,
        processing_time: float
    ) -> None:
        """Update recognition statistics."""
        self.recognition_stats["entities_recognized"] += entities_recognized
        self.recognition_stats["entities_classified"] += entities_classified
        self.recognition_stats["entities_linked"] += entities_linked
        self.recognition_stats["entities_disambiguated"] += entities_disambiguated
        self.recognition_stats["processing_time_ms"] += processing_time
    
    def get_recognition_stats(self) -> Dict[str, Any]:
        """Get recognition statistics."""
        stats = self.recognition_stats.copy()
        
        # Calculate averages
        if stats["entities_recognized"] > 0:
            stats["avg_entities_per_recognition"] = stats["entities_recognized"] / stats["entities_recognized"]
            stats["classification_rate"] = stats["entities_classified"] / stats["entities_recognized"]
            stats["linking_rate"] = stats["entities_linked"] / stats["entities_recognized"]
            stats["disambiguation_rate"] = stats["entities_disambiguated"] / stats["entities_recognized"]
        else:
            stats["avg_entities_per_recognition"] = 0
            stats["classification_rate"] = 0
            stats["linking_rate"] = 0
            stats["disambiguation_rate"] = 0
        
        # Calculate processing rate
        if stats["processing_time_ms"] > 0:
            stats["entities_per_second"] = stats["entities_recognized"] / (stats["processing_time_ms"] / 1000)
        else:
            stats["entities_per_second"] = 0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset recognition statistics."""
        self.recognition_stats = {
            "entities_recognized": 0,
            "entities_classified": 0,
            "entities_linked": 0,
            "entities_disambiguated": 0,
            "processing_time_ms": 0
        }
        logger.info("🔄 Entity recognition statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update recognition configuration."""
        self.config.update(new_config)
        
        # Reinitialize patterns and classifiers if needed
        if any(key in new_config for key in ["entity_types", "language"]):
            self._init_entity_patterns()
            self._init_entity_classifiers()
        
        logger.info("⚙️ Entity recognition configuration updated")





