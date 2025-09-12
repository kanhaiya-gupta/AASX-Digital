"""
AI RAG Domain Knowledge Extractor
=================================

Domain-specific knowledge extraction and ontology management.
"""

import logging
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
import asyncio

logger = logging.getLogger(__name__)


class DomainKnowledgeExtractor:
    """
    Domain Knowledge Extractor for AI RAG Knowledge Extraction
    
    Specializes in domain-specific knowledge extraction, ontology management,
    and domain-specific pattern recognition for various knowledge domains.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the domain knowledge extractor.
        
        Args:
            config: Configuration dictionary for domain knowledge extraction
        """
        self.config = config or self._get_default_config()
        self.extraction_stats = {
            "domains_processed": 0,
            "concepts_extracted": 0,
            "relationships_discovered": 0,
            "ontologies_built": 0,
            "processing_time_ms": 0
        }
        
        # Initialize domain-specific patterns and ontologies
        self._init_domain_patterns()
        self._init_domain_ontologies()
        
        logger.info("✅ DomainKnowledgeExtractor initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for domain knowledge extraction."""
        return {
            "supported_domains": [
                "technology", "healthcare", "finance", "education", "legal",
                "manufacturing", "research", "business", "science", "engineering"
            ],
            "default_domain": "technology",
            "enable_ontology_building": True,
            "enable_domain_patterns": True,
            "enable_concept_extraction": True,
            "enable_relationship_discovery": True,
            "confidence_threshold": 0.6,
            "max_concepts_per_domain": 500,
            "max_relationships_per_domain": 1000,
            "ontology_depth_limit": 5,
            "batch_size": 50,
            "parallel_processing": True,
            "use_external_ontologies": False,
            "external_ontology_sources": [],
            "domain_specific_rules": True
        }
    
    def _init_domain_patterns(self) -> None:
        """Initialize domain-specific extraction patterns."""
        self.domain_patterns = {
            "technology": {
                "concepts": [
                    r'\b(?:API|SDK|REST|GraphQL|HTTP|JSON|XML|SQL|NoSQL|ORM|MVC|MVP|CI/CD)\b',
                    r'\b(?:algorithm|function|method|procedure|process|system|framework|architecture)\b',
                    r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin)\b',
                    r'\b(?:React|Angular|Vue|Django|Flask|Spring|Express|Node\.js|TensorFlow|PyTorch)\b',
                    r'\b(?:Docker|Kubernetes|AWS|Azure|GCP|Git|Jenkins|Jira|Confluence|Slack)\b'
                ],
                "relationships": [
                    r'\b(?:implements|extends|inherits|from|uses|depends\s+on|integrates\s+with)\b',
                    r'\b(?:built\s+with|developed\s+using|created\s+by|maintained\s+by)\b',
                    r'\b(?:version|release|update|upgrade|migration|deployment|rollback)\b'
                ],
                "attributes": [
                    r'\b(?:performance|scalability|security|reliability|maintainability|usability)\b',
                    r'\b(?:efficiency|optimization|benchmark|testing|debugging|monitoring)\b'
                ]
            },
            "healthcare": {
                "concepts": [
                    r'\b(?:diagnosis|treatment|medication|therapy|surgery|rehabilitation|prevention)\b',
                    r'\b(?:patient|doctor|nurse|specialist|clinic|hospital|pharmacy|laboratory)\b',
                    r'\b(?:symptoms|disease|condition|syndrome|infection|inflammation|tumor)\b',
                    r'\b(?:blood|urine|tissue|organ|bone|muscle|nerve|brain|heart|lung)\b',
                    r'\b(?:antibiotic|vaccine|painkiller|antidepressant|antihistamine|steroid)\b'
                ],
                "relationships": [
                    r'\b(?:causes|treats|prevents|diagnoses|monitors|manages|relieves)\b',
                    r'\b(?:prescribed\s+for|administered\s+to|applied\s+to|injected\s+into)\b',
                    r'\b(?:side\s+effect|interaction|contraindication|dosage|frequency)\b'
                ],
                "attributes": [
                    r'\b(?:efficacy|safety|tolerance|absorption|metabolism|excretion)\b',
                    r'\b(?:clinical|trial|study|research|evidence|guideline|protocol)\b'
                ]
            },
            "finance": {
                "concepts": [
                    r'\b(?:investment|portfolio|asset|liability|equity|debt|bond|stock|fund|derivative)\b',
                    r'\b(?:bank|credit|loan|mortgage|insurance|pension|retirement|savings|checking)\b',
                    r'\b(?:interest|rate|yield|return|dividend|capital\s+gain|loss|profit|revenue)\b',
                    r'\b(?:market|exchange|trading|broker|trader|analyst|advisor|manager|officer)\b',
                    r'\b(?:risk|volatility|liquidity|diversification|hedging|arbitrage|speculation)\b'
                ],
                "relationships": [
                    r'\b(?:invests\s+in|borrows\s+from|lends\s+to|insures\s+against|hedges\s+with)\b',
                    r'\b(?:manages|advises|trades|analyzes|evaluates|assesses|monitors)\b',
                    r'\b(?:increases|decreases|fluctuates|stabilizes|recovers|declines|peaks)\b'
                ],
                "attributes": [
                    r'\b(?:volatile|stable|liquid|illiquid|risky|safe|profitable|unprofitable)\b',
                    r'\b(?:regulated|unregulated|taxable|tax\s+free|insured|uninsured)\b'
                ]
            },
            "education": {
                "concepts": [
                    r'\b(?:course|lesson|lecture|tutorial|workshop|seminar|conference|symposium)\b',
                    r'\b(?:student|teacher|professor|instructor|tutor|mentor|advisor|counselor)\b',
                    r'\b(?:curriculum|syllabus|textbook|reference|assignment|project|exam|quiz|test)\b',
                    r'\b(?:university|college|school|institute|academy|department|faculty|library)\b',
                    r'\b(?:degree|certificate|diploma|major|minor|concentration|specialization)\b'
                ],
                "relationships": [
                    r'\b(?:teaches|learns|studies|enrolls\s+in|graduates\s+from|attends)\b',
                    r'\b(?:requires|prerequisite|corequisite|elective|mandatory|optional)\b',
                    r'\b(?:evaluates|assesses|grades|reviews|provides\s+feedback|mentors)\b'
                ],
                "attributes": [
                    r'\b(?:academic|practical|theoretical|interactive|collaborative|individual)\b',
                    r'\b(?:beginner|intermediate|advanced|introductory|specialized|comprehensive)\b'
                ]
            },
            "legal": {
                "concepts": [
                    r'\b(?:law|statute|regulation|ordinance|code|act|bill|amendment|clause|section)\b',
                    r'\b(?:court|judge|lawyer|attorney|prosecutor|defendant|plaintiff|witness|jury)\b',
                    r'\b(?:contract|agreement|treaty|constitution|charter|license|permit|certificate)\b',
                    r'\b(?:right|obligation|duty|liability|responsibility|authority|jurisdiction)\b',
                    r'\b(?:case|precedent|ruling|decision|verdict|appeal|settlement|mediation)\b'
                ],
                "relationships": [
                    r'\b(?:enforces|violates|complies\s+with|governs|regulates|authorizes)\b',
                    r'\b(?:represents|defends|prosecutes|advises|counsels|mediates|arbitrates)\b',
                    r'\b(?:establishes|amends|repeals|interprets|applies|enforces|upholds)\b'
                ],
                "attributes": [
                    r'\b(?:binding|enforceable|valid|void|legal|illegal|constitutional|unconstitutional)\b',
                    r'\b(?:federal|state|local|international|domestic|civil|criminal|administrative)\b'
                ]
            }
        }
        
        logger.info(f"🔍 Domain patterns initialized for {len(self.domain_patterns)} domains")
    
    def _init_domain_ontologies(self) -> None:
        """Initialize domain-specific ontologies."""
        self.domain_ontologies = {
            "technology": {
                "concept_hierarchy": {
                    "Programming": {
                        "Languages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#"],
                        "Paradigms": ["Object-Oriented", "Functional", "Procedural", "Declarative"],
                        "Tools": ["IDE", "Debugger", "Profiler", "Linter", "Formatter"]
                    },
                    "Frameworks": {
                        "Web": ["React", "Angular", "Vue", "Django", "Flask", "Express"],
                        "Mobile": ["React Native", "Flutter", "Xamarin", "Ionic"],
                        "Data": ["TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy"]
                    },
                    "Infrastructure": {
                        "Cloud": ["AWS", "Azure", "GCP", "Digital Ocean", "Heroku"],
                        "Containerization": ["Docker", "Kubernetes", "Podman", "LXC"],
                        "CI/CD": ["Jenkins", "GitHub Actions", "GitLab CI", "CircleCI"]
                    }
                },
                "relationship_types": [
                    "implements", "extends", "depends_on", "integrates_with",
                    "replaces", "complements", "competes_with", "evolves_from"
                ]
            },
            "healthcare": {
                "concept_hierarchy": {
                    "Medical_Professionals": {
                        "Doctors": ["General Practitioner", "Specialist", "Surgeon", "Resident"],
                        "Nurses": ["Registered Nurse", "Nurse Practitioner", "Specialist Nurse"],
                        "Allied_Health": ["Pharmacist", "Technologist", "Therapist", "Technician"]
                    },
                    "Medical_Procedures": {
                        "Diagnostic": ["Examination", "Test", "Scan", "Biopsy", "Endoscopy"],
                        "Therapeutic": ["Surgery", "Medication", "Therapy", "Radiation"],
                        "Preventive": ["Vaccination", "Screening", "Counseling", "Education"]
                    },
                    "Body_Systems": {
                        "Cardiovascular": ["Heart", "Blood Vessels", "Blood"],
                        "Respiratory": ["Lungs", "Airways", "Chest"],
                        "Nervous": ["Brain", "Spinal Cord", "Nerves"]
                    }
                },
                "relationship_types": [
                    "treats", "diagnoses", "prevents", "causes", "symptoms_of",
                    "prescribed_for", "administered_to", "interacts_with", "contraindicated_for"
                ]
            },
            "finance": {
                "concept_hierarchy": {
                    "Financial_Products": {
                        "Investments": ["Stocks", "Bonds", "Mutual Funds", "ETFs", "Real Estate"],
                        "Banking": ["Savings", "Checking", "CDs", "Money Market", "Credit Cards"],
                        "Insurance": ["Life", "Health", "Auto", "Home", "Liability"]
                    },
                    "Financial_Institutions": {
                        "Banks": ["Commercial", "Investment", "Credit Union", "Online"],
                        "Investment_Firms": ["Brokerage", "Asset Management", "Hedge Fund", "Private Equity"],
                        "Insurance_Companies": ["Life", "Property", "Casualty", "Health"]
                    },
                    "Market_Concepts": {
                        "Risk": ["Volatility", "Liquidity", "Credit", "Market", "Operational"],
                        "Returns": ["Capital Gains", "Dividends", "Interest", "Rental Income"],
                        "Analysis": ["Fundamental", "Technical", "Quantitative", "Behavioral"]
                    }
                },
                "relationship_types": [
                    "invests_in", "borrows_from", "lends_to", "insures_against",
                    "manages", "advises", "trades", "analyzes", "evaluates"
                ]
            }
        }
        
        logger.info(f"🏗️ Domain ontologies initialized for {len(self.domain_ontologies)} domains")
    
    async def extract_domain_knowledge(
        self,
        text: str,
        domain: Optional[str] = None,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract domain-specific knowledge from text.
        
        Args:
            text: Document text to analyze
            domain: Specific domain to focus on (default: auto-detect)
            document_id: Optional document identifier
            metadata: Optional document metadata
            
        Returns:
            Dict: Domain knowledge extraction results
        """
        start_time = asyncio.get_event_loop().time()
        logger.info(f"🔍 Starting domain knowledge extraction for document: {document_id or 'unknown'}")
        
        try:
            # Auto-detect domain if not specified
            if not domain:
                domain = await self._auto_detect_domain(text)
            
            # Validate domain
            if domain not in self.config["supported_domains"]:
                logger.warning(f"⚠️ Unsupported domain: {domain}, using default: {self.config['default_domain']}")
                domain = self.config["default_domain"]
            
            # Extract domain-specific concepts
            concepts = await self._extract_domain_concepts(text, domain)
            
            # Discover domain relationships
            relationships = await self._discover_domain_relationships(text, domain, concepts)
            
            # Build domain ontology
            ontology = await self._build_domain_ontology(domain, concepts, relationships)
            
            # Extract domain-specific attributes
            attributes = await self._extract_domain_attributes(text, domain, concepts)
            
            # Calculate processing time
            end_time = asyncio.get_event_loop().time()
            processing_time = (end_time - start_time) * 1000
            
            # Update statistics
            self._update_extraction_stats(domain, len(concepts), len(relationships), 
                                        len(ontology), processing_time)
            
            results = {
                "document_id": document_id,
                "metadata": metadata or {},
                "extraction_timestamp": asyncio.get_event_loop().time(),
                "processing_time_ms": processing_time,
                "domain": domain,
                "concepts": concepts,
                "relationships": relationships,
                "ontology": ontology,
                "attributes": attributes,
                "extraction_metadata": {
                    "config_used": self.config.copy(),
                    "extraction_stats": self.extraction_stats.copy()
                }
            }
            
            logger.info(f"✅ Domain knowledge extraction completed: {domain} - {len(concepts)} concepts, {len(relationships)} relationships")
            return results
            
        except Exception as e:
            logger.error(f"❌ Domain knowledge extraction failed: {e}")
            return {
                "document_id": document_id,
                "metadata": metadata or {},
                "extraction_timestamp": asyncio.get_event_loop().time(),
                "processing_time_ms": 0,
                "error": str(e),
                "domain": domain or "unknown",
                "concepts": [],
                "relationships": [],
                "ontology": {},
                "attributes": {}
            }
    
    async def _auto_detect_domain(self, text: str) -> str:
        """Auto-detect the domain of the document."""
        try:
            domain_scores = defaultdict(float)
            
            for domain, patterns in self.domain_patterns.items():
                score = 0.0
                
                # Score based on concept patterns
                for pattern in patterns["concepts"]:
                    matches = len(re.findall(pattern, text, re.IGNORECASE))
                    score += matches * 0.1
                
                # Score based on relationship patterns
                for pattern in patterns["relationships"]:
                    matches = len(re.findall(pattern, text, re.IGNORECASE))
                    score += matches * 0.05
                
                # Score based on attribute patterns
                for pattern in patterns["attributes"]:
                    matches = len(re.findall(pattern, text, re.IGNORECASE))
                    score += matches * 0.03
                
                domain_scores[domain] = score
            
            # Return domain with highest score
            if domain_scores:
                best_domain = max(domain_scores, key=domain_scores.get)
                if domain_scores[best_domain] > 0.1:  # Minimum threshold
                    return best_domain
            
            # Default to technology if no clear domain detected
            return self.config["default_domain"]
            
        except Exception as e:
            logger.warning(f"⚠️ Domain auto-detection failed: {e}")
            return self.config["default_domain"]
    
    async def _extract_domain_concepts(
        self,
        text: str,
        domain: str
    ) -> List[Dict[str, Any]]:
        """Extract domain-specific concepts from text."""
        concepts = []
        
        try:
            if not self.config["enable_concept_extraction"]:
                return concepts
            
            if domain not in self.domain_patterns:
                logger.warning(f"⚠️ No patterns available for domain: {domain}")
                return concepts
            
            domain_patterns = self.domain_patterns[domain]
            
            # Extract concepts using domain patterns
            for pattern in domain_patterns["concepts"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    concept_text = match.group()
                    confidence = self._calculate_concept_confidence(concept_text, domain, text)
                    
                    if confidence >= self.config["confidence_threshold"]:
                        concept = {
                            "text": concept_text,
                            "domain": domain,
                            "type": "concept",
                            "start_pos": match.start(),
                            "end_pos": match.end(),
                            "confidence": confidence,
                            "source": "domain_pattern",
                            "raw_match": match.group(0),
                            "context": self._extract_concept_context(text, match.start(), match.end()),
                            "category": self._categorize_concept(concept_text, domain)
                        }
                        concepts.append(concept)
            
            # Limit concepts per domain
            if len(concepts) > self.config["max_concepts_per_domain"]:
                # Sort by confidence and keep top concepts
                concepts.sort(key=lambda x: x["confidence"], reverse=True)
                concepts = concepts[:self.config["max_concepts_per_domain"]]
                logger.warning(f"⚠️ Limited concepts to {self.config['max_concepts_per_domain']} (highest confidence)")
            
            # Remove duplicates
            concepts = self._deduplicate_concepts(concepts)
            
            return concepts
            
        except Exception as e:
            logger.error(f"❌ Domain concept extraction failed: {e}")
            return []
    
    async def _discover_domain_relationships(
        self,
        text: str,
        domain: str,
        concepts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Discover domain-specific relationships."""
        relationships = []
        
        try:
            if not self.config["enable_relationship_discovery"]:
                return relationships
            
            if domain not in self.domain_patterns:
                return relationships
            
            domain_patterns = self.domain_patterns[domain]
            
            # Extract relationships using domain patterns
            for pattern in domain_patterns["relationships"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    rel_text = match.group()
                    confidence = self._calculate_relationship_confidence(rel_text, domain, text)
                    
                    if confidence >= self.config["confidence_threshold"]:
                        # Find related concepts
                        related_concepts = self._find_related_concepts(rel_text, concepts)
                        
                        if len(related_concepts) >= 2:  # Need at least 2 concepts for a relationship
                            relationship = {
                                "text": rel_text,
                                "domain": domain,
                                "type": "relationship",
                                "start_pos": match.start(),
                                "end_pos": match.end(),
                                "confidence": confidence,
                                "source": "domain_pattern",
                                "raw_match": match.group(0),
                                "context": self._extract_concept_context(text, match.start(), match.end()),
                                "relationship_type": self._determine_relationship_type(rel_text, domain),
                                "concepts_involved": related_concepts
                            }
                            relationships.append(relationship)
            
            # Limit relationships per domain
            if len(relationships) > self.config["max_relationships_per_domain"]:
                # Sort by confidence and keep top relationships
                relationships.sort(key=lambda x: x["confidence"], reverse=True)
                relationships = relationships[:self.config["max_relationships_per_domain"]]
                logger.warning(f"⚠️ Limited relationships to {self.config['max_relationships_per_domain']} (highest confidence)")
            
            return relationships
            
        except Exception as e:
            logger.error(f"❌ Domain relationship discovery failed: {e}")
            return []
    
    async def _build_domain_ontology(
        self,
        domain: str,
        concepts: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build domain-specific ontology."""
        ontology = {
            "domain": domain,
            "concepts": [],
            "relationships": [],
            "hierarchy": {},
            "metadata": {
                "concept_count": len(concepts),
                "relationship_count": len(relationships),
                "depth": 0,
                "coverage_score": 0.0
            }
        }
        
        try:
            if not self.config["enable_ontology_building"]:
                return ontology
            
            # Build concept hierarchy
            concept_hierarchy = await self._build_concept_hierarchy(domain, concepts)
            ontology["hierarchy"] = concept_hierarchy
            
            # Build relationship network
            relationship_network = await self._build_relationship_network(domain, relationships)
            ontology["relationships"] = relationship_network
            
            # Calculate ontology metrics
            ontology["metadata"]["depth"] = self._calculate_ontology_depth(concept_hierarchy)
            ontology["metadata"]["coverage_score"] = self._calculate_ontology_coverage(concepts, relationships)
            
            return ontology
            
        except Exception as e:
            logger.error(f"❌ Domain ontology building failed: {e}")
            return ontology
    
    async def _extract_domain_attributes(
        self,
        text: str,
        domain: str,
        concepts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract domain-specific attributes."""
        attributes = []
        
        try:
            if domain not in self.domain_patterns:
                return attributes
            
            domain_patterns = self.domain_patterns[domain]
            
            # Extract attributes using domain patterns
            for pattern in domain_patterns["attributes"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    attr_text = match.group()
                    confidence = self._calculate_attribute_confidence(attr_text, domain, text)
                    
                    if confidence >= self.config["confidence_threshold"]:
                        # Find related concepts
                        related_concepts = self._find_related_concepts(attr_text, concepts)
                        
                        attribute = {
                            "text": attr_text,
                            "domain": domain,
                            "type": "attribute",
                            "start_pos": match.start(),
                            "end_pos": match.end(),
                            "confidence": confidence,
                            "source": "domain_pattern",
                            "raw_match": match.group(0),
                            "context": self._extract_concept_context(text, match.start(), match.end()),
                            "attribute_type": self._determine_attribute_type(attr_text, domain),
                            "concepts_affected": related_concepts
                        }
                        attributes.append(attribute)
            
            return attributes
            
        except Exception as e:
            logger.error(f"❌ Domain attribute extraction failed: {e}")
            return []
    
    async def _build_concept_hierarchy(
        self,
        domain: str,
        concepts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build hierarchical structure of concepts."""
        hierarchy = {}
        
        try:
            if domain not in self.domain_ontologies:
                return hierarchy
            
            base_ontology = self.domain_ontologies[domain]["concept_hierarchy"]
            
            # Build hierarchy based on base ontology and extracted concepts
            for category, subcategories in base_ontology.items():
                if isinstance(subcategories, dict):
                    hierarchy[category] = {
                        "subcategories": subcategories,
                        "concepts": [],
                        "extracted_count": 0
                    }
                    
                    # Add extracted concepts to appropriate categories
                    for concept in concepts:
                        if self._concept_belongs_to_category(concept, category, subcategories):
                            hierarchy[category]["concepts"].append(concept)
                            hierarchy[category]["extracted_count"] += 1
                else:
                    # Direct list of concepts
                    hierarchy[category] = {
                        "concepts": subcategories,
                        "extracted_concepts": [],
                        "extracted_count": 0
                    }
                    
                    # Add extracted concepts
                    for concept in concepts:
                        if concept["text"] in subcategories:
                            hierarchy[category]["extracted_concepts"].append(concept)
                            hierarchy[category]["extracted_count"] += 1
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"❌ Concept hierarchy building failed: {e}")
            return hierarchy
    
    async def _build_relationship_network(
        self,
        domain: str,
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build network of relationships."""
        network = []
        
        try:
            for relationship in relationships:
                network_item = {
                    "id": f"rel_{len(network)}",
                    "type": relationship["relationship_type"],
                    "source_concept": relationship["concepts_involved"][0] if relationship["concepts_involved"] else None,
                    "target_concept": relationship["concepts_involved"][1] if len(relationship["concepts_involved"]) > 1 else None,
                    "confidence": relationship["confidence"],
                    "context": relationship["context"],
                    "domain": domain
                }
                network.append(network_item)
            
            return network
            
        except Exception as e:
            logger.error(f"❌ Relationship network building failed: {e}")
            return network
    
    def _calculate_concept_confidence(
        self,
        concept_text: str,
        domain: str,
        text: str
    ) -> float:
        """Calculate confidence score for extracted concept."""
        confidence = 0.5  # Base confidence
        
        try:
            # Length-based confidence
            if len(concept_text) >= 2:
                confidence += 0.1
            
            # Domain-specific confidence
            if domain in self.domain_ontologies:
                # Check if concept exists in base ontology
                if self._concept_in_base_ontology(concept_text, domain):
                    confidence += 0.2
            
            # Frequency-based confidence
            concept_lower = concept_text.lower()
            text_lower = text.lower()
            frequency = text_lower.count(concept_lower)
            
            if frequency == 1:
                confidence += 0.1  # Unique concept
            elif frequency <= 3:
                confidence += 0.05  # Few occurrences
            else:
                confidence -= 0.05  # Too many might indicate noise
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ Concept confidence calculation failed: {e}")
            confidence = 0.5
        
        return round(confidence, 3)
    
    def _calculate_relationship_confidence(
        self,
        rel_text: str,
        domain: str,
        text: str
    ) -> float:
        """Calculate confidence score for discovered relationship."""
        confidence = 0.5  # Base confidence
        
        try:
            # Length-based confidence
            if len(rel_text) >= 5:
                confidence += 0.1
            
            # Domain-specific confidence
            if domain in self.domain_ontologies:
                # Check if relationship type exists in base ontology
                if self._relationship_type_in_base_ontology(rel_text, domain):
                    confidence += 0.2
            
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
    
    def _calculate_attribute_confidence(
        self,
        attr_text: str,
        domain: str,
        text: str
    ) -> float:
        """Calculate confidence score for extracted attribute."""
        confidence = 0.5  # Base confidence
        
        try:
            # Length-based confidence
            if len(attr_text) >= 3:
                confidence += 0.1
            
            # Frequency-based confidence
            attr_lower = attr_text.lower()
            text_lower = text.lower()
            frequency = text_lower.count(attr_lower)
            
            if frequency == 1:
                confidence += 0.1  # Unique attribute
            elif frequency <= 2:
                confidence += 0.05  # Few occurrences
            else:
                confidence -= 0.05  # Too many might indicate noise
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ Attribute confidence calculation failed: {e}")
            confidence = 0.5
        
        return round(confidence, 3)
    
    def _extract_concept_context(
        self,
        text: str,
        start_pos: int,
        end_pos: int,
        context_window: int = 100
    ) -> str:
        """Extract context around a concept."""
        try:
            context_start = max(0, start_pos - context_window)
            context_end = min(len(text), end_pos + context_window)
            
            return text[context_start:context_end].strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Concept context extraction failed: {e}")
            return ""
    
    def _categorize_concept(self, concept_text: str, domain: str) -> str:
        """Categorize a concept within its domain."""
        try:
            if domain in self.domain_ontologies:
                base_ontology = self.domain_ontologies[domain]["concept_hierarchy"]
                
                for category, subcategories in base_ontology.items():
                    if isinstance(subcategories, dict):
                        for subcategory, concepts in subcategories.items():
                            if concept_text in concepts:
                                return f"{category}.{subcategory}"
                    else:
                        if concept_text in subcategories:
                            return category
            
            return "general"
            
        except Exception as e:
            logger.warning(f"⚠️ Concept categorization failed: {e}")
            return "general"
    
    def _determine_relationship_type(self, rel_text: str, domain: str) -> str:
        """Determine the type of relationship."""
        try:
            if domain in self.domain_ontologies:
                base_ontology = self.domain_ontologies[domain]
                
                for rel_type in base_ontology["relationship_types"]:
                    if rel_type.lower() in rel_text.lower():
                        return rel_type
            
            # Default relationship types
            if any(word in rel_text.lower() for word in ["uses", "implements", "extends"]):
                return "implements"
            elif any(word in rel_text.lower() for word in ["depends", "requires", "needs"]):
                return "depends_on"
            elif any(word in rel_text.lower() for word in ["integrates", "connects", "links"]):
                return "integrates_with"
            else:
                return "related_to"
                
        except Exception as e:
            logger.warning(f"⚠️ Relationship type determination failed: {e}")
            return "related_to"
    
    def _determine_attribute_type(self, attr_text: str, domain: str) -> str:
        """Determine the type of attribute."""
        try:
            # Default attribute types based on common patterns
            if any(word in attr_text.lower() for word in ["performance", "speed", "efficiency"]):
                return "performance"
            elif any(word in attr_text.lower() for word in ["security", "safety", "protection"]):
                return "security"
            elif any(word in attr_text.lower() for word in ["quality", "reliability", "durability"]):
                return "quality"
            elif any(word in attr_text.lower() for word in ["cost", "price", "expense"]):
                return "cost"
            else:
                return "general"
                
        except Exception as e:
            logger.warning(f"⚠️ Attribute type determination failed: {e}")
            return "general"
    
    def _find_related_concepts(
        self,
        text: str,
        concepts: List[Dict[str, Any]]
    ) -> List[str]:
        """Find concepts mentioned in relationship or attribute text."""
        related = []
        
        try:
            for concept in concepts:
                if concept["text"] in text:
                    related.append(concept["text"])
            
            return related
            
        except Exception as e:
            logger.warning(f"⚠️ Related concept finding failed: {e}")
            return related
    
    def _concept_belongs_to_category(
        self,
        concept: Dict[str, Any],
        category: str,
        subcategories: Dict[str, Any]
    ) -> bool:
        """Check if a concept belongs to a specific category."""
        try:
            concept_text = concept["text"]
            
            for subcategory, concepts_list in subcategories.items():
                if concept_text in concepts_list:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _concept_in_base_ontology(self, concept_text: str, domain: str) -> bool:
        """Check if a concept exists in the base ontology."""
        try:
            if domain not in self.domain_ontologies:
                return False
            
            base_ontology = self.domain_ontologies[domain]["concept_hierarchy"]
            
            for category, subcategories in base_ontology.items():
                if isinstance(subcategories, dict):
                    for subcategory, concepts in subcategories.items():
                        if concept_text in concepts:
                            return True
                else:
                    if concept_text in subcategories:
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _relationship_type_in_base_ontology(self, rel_text: str, domain: str) -> bool:
        """Check if a relationship type exists in the base ontology."""
        try:
            if domain not in self.domain_ontologies:
                return False
            
            base_ontology = self.domain_ontologies[domain]
            
            for rel_type in base_ontology["relationship_types"]:
                if rel_type.lower() in rel_text.lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_ontology_depth(self, hierarchy: Dict[str, Any]) -> int:
        """Calculate the depth of the ontology hierarchy."""
        try:
            max_depth = 0
            
            def calculate_depth(node, current_depth):
                nonlocal max_depth
                max_depth = max(max_depth, current_depth)
                
                if isinstance(node, dict):
                    for key, value in node.items():
                        if key in ["subcategories", "concepts"]:
                            calculate_depth(value, current_depth + 1)
            
            calculate_depth(hierarchy, 0)
            return min(max_depth, self.config["ontology_depth_limit"])
            
        except Exception:
            return 0
    
    def _calculate_ontology_coverage(
        self,
        concepts: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> float:
        """Calculate the coverage score of the ontology."""
        try:
            if not concepts:
                return 0.0
            
            # Simple coverage based on concept and relationship counts
            concept_score = min(len(concepts) / 100, 1.0)  # Normalize to 100 concepts
            relationship_score = min(len(relationships) / 200, 1.0)  # Normalize to 200 relationships
            
            # Weighted average
            coverage = (concept_score * 0.6) + (relationship_score * 0.4)
            
            return round(coverage, 3)
            
        except Exception:
            return 0.0
    
    def _deduplicate_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate concepts."""
        seen = set()
        unique_concepts = []
        
        for concept in concepts:
            key = (concept["text"].lower(), concept["domain"])
            if key not in seen:
                seen.add(key)
                unique_concepts.append(concept)
        
        return unique_concepts
    
    def _update_extraction_stats(
        self,
        domain: str,
        concepts_extracted: int,
        relationships_discovered: int,
        ontologies_built: int,
        processing_time: float
    ) -> None:
        """Update extraction statistics."""
        self.extraction_stats["domains_processed"] += 1
        self.extraction_stats["concepts_extracted"] += concepts_extracted
        self.extraction_stats["relationships_discovered"] += relationships_discovered
        self.extraction_stats["ontologies_built"] += ontologies_built
        self.extraction_stats["processing_time_ms"] += processing_time
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        stats = self.extraction_stats.copy()
        
        # Calculate averages
        if stats["domains_processed"] > 0:
            stats["avg_concepts_per_domain"] = stats["concepts_extracted"] / stats["domains_processed"]
            stats["avg_relationships_per_domain"] = stats["relationships_discovered"] / stats["domains_processed"]
            stats["avg_processing_time_ms"] = stats["processing_time_ms"] / stats["domains_processed"]
        else:
            stats["avg_concepts_per_domain"] = 0
            stats["avg_relationships_per_domain"] = 0
            stats["avg_processing_time_ms"] = 0
        
        # Calculate processing rate
        if stats["processing_time_ms"] > 0:
            stats["domains_per_second"] = stats["domains_processed"] / (stats["processing_time_ms"] / 1000)
        else:
            stats["domains_per_second"] = 0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset extraction statistics."""
        self.extraction_stats = {
            "domains_processed": 0,
            "concepts_extracted": 0,
            "relationships_discovered": 0,
            "ontologies_built": 0,
            "processing_time_ms": 0
        }
        logger.info("🔄 Domain knowledge extraction statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update extraction configuration."""
        self.config.update(new_config)
        
        # Reinitialize patterns and ontologies if needed
        if any(key in new_config for key in ["supported_domains", "domain_patterns"]):
            self._init_domain_patterns()
            self._init_domain_ontologies()
        
        logger.info("⚙️ Domain knowledge extraction configuration updated")





