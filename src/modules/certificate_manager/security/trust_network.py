"""
Trust Network for Certificate Manager

Handles trust relationships, reputation scoring, and trust validation for certificates.
Provides trust network analysis and reputation management capabilities.
"""

import asyncio
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels for entities and certificates"""
    UNTRUSTED = "untrusted"     # No trust
    LOW = "low"                 # Low trust
    MEDIUM = "medium"           # Medium trust
    HIGH = "high"               # High trust
    VERIFIED = "verified"       # Verified trust
    CERTIFIED = "certified"     # Certified trust


class TrustStatus(Enum):
    """Trust network status values"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"


class TrustNetwork:
    """
    Trust network and reputation management service
    
    Handles:
    - Trust relationship management
    - Reputation scoring and validation
    - Trust network analysis
    - Certificate trust validation
    - Trust chain verification
    - Reputation history tracking
    """
    
    def __init__(self):
        """Initialize the trust network service"""
        self.trust_levels = list(TrustLevel)
        self.trust_statuses = list(TrustStatus)
        
        # Trust network storage
        self.trust_entities: Dict[str, Dict[str, Any]] = {}
        self.trust_relationships: Dict[str, Dict[str, Any]] = {}
        self.trust_certificates: Dict[str, Dict[str, Any]] = {}
        self.reputation_scores: Dict[str, Dict[str, Any]] = {}
        self.trust_history: List[Dict[str, Any]] = []
        
        # Trust network locks
        self.trust_locks: Dict[str, asyncio.Lock] = {}
        
        # Trust network settings
        self.trust_settings = self._initialize_trust_settings()
        
        # Initialize default trust entities
        self._initialize_default_trust_entities()
        
        logger.info("Trust Network service initialized successfully")
    
    def _initialize_trust_settings(self) -> Dict[str, Any]:
        """Initialize trust network settings"""
        return {
            "default_trust_level": TrustLevel.MEDIUM,
            "min_trust_score": 50,
            "max_trust_score": 100,
            "trust_decay_rate": 0.1,  # Trust score decay per day
            "reputation_update_interval_hours": 24,
            "max_trust_chain_length": 5,
            "trust_validation_timeout_seconds": 30,
            "reputation_history_retention_days": 365
        }
    
    def _initialize_default_trust_entities(self) -> None:
        """Initialize default trust entities"""
        # Default trusted entities
        self.trust_entities = {
            "system_root": {
                "entity_id": "system_root",
                "name": "System Root Authority",
                "type": "authority",
                "trust_level": TrustLevel.CERTIFIED.value,
                "reputation_score": 100,
                "status": TrustStatus.ACTIVE.value,
                "created_at": asyncio.get_event_loop().time(),
                "metadata": {
                    "description": "Root authority for the certificate management system",
                    "jurisdiction": "system",
                    "certification_level": "root"
                }
            },
            "certificate_manager": {
                "entity_id": "certificate_manager",
                "name": "Certificate Manager System",
                "type": "system",
                "trust_level": TrustLevel.VERIFIED.value,
                "reputation_score": 95,
                "status": TrustStatus.ACTIVE.value,
                "created_at": asyncio.get_event_loop().time(),
                "metadata": {
                    "description": "Core certificate management system",
                    "version": "1.0",
                    "certification_level": "verified"
                }
            }
        }
        
        # Default trust relationships
        self.trust_relationships = {
            "root_to_system": {
                "relationship_id": "root_to_system",
                "from_entity": "system_root",
                "to_entity": "certificate_manager",
                "trust_level": TrustLevel.VERIFIED.value,
                "relationship_type": "authority",
                "created_at": asyncio.get_event_loop().time(),
                "status": TrustStatus.ACTIVE.value,
                "metadata": {
                    "description": "System root authority trusts certificate manager",
                    "trust_basis": "system_integration"
                }
            }
        }
    
    async def register_trust_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        initial_trust_level: TrustLevel = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new trust entity
        
        Args:
            entity_id: Unique entity identifier
            name: Human-readable entity name
            entity_type: Type of entity (e.g., 'authority', 'organization', 'system')
            initial_trust_level: Initial trust level (defaults to system default)
            metadata: Additional entity metadata
            
        Returns:
            Dictionary containing entity information
        """
        # Validate input parameters
        await self._validate_entity_registration(entity_id, name, entity_type)
        
        # Check if entity already exists
        if entity_id in self.trust_entities:
            raise ValueError(f"Entity '{entity_id}' already registered")
        
        # Use default trust level if none specified
        if initial_trust_level is None:
            initial_trust_level = self.trust_settings["default_trust_level"]
        
        # Calculate initial reputation score
        initial_reputation = self._calculate_reputation_from_trust_level(initial_trust_level)
        
        # Create entity record
        entity_record = {
            "entity_id": entity_id,
            "name": name,
            "type": entity_type,
            "trust_level": initial_trust_level.value,
            "reputation_score": initial_reputation,
            "status": TrustStatus.ACTIVE.value,
            "created_at": asyncio.get_event_loop().time(),
            "last_updated": asyncio.get_event_loop().time(),
            "metadata": metadata or {}
        }
        
        # Store entity
        self.trust_entities[entity_id] = entity_record
        
        # Initialize reputation tracking
        self.reputation_scores[entity_id] = {
            "current_score": initial_reputation,
            "history": [{
                "score": initial_reputation,
                "timestamp": asyncio.get_event_loop().time(),
                "reason": "Entity registration"
            }],
            "factors": {
                "base_score": initial_reputation,
                "activity_bonus": 0,
                "trust_relationships": 0,
                "certificate_quality": 0,
                "time_decay": 0
            }
        }
        
        # Record in history
        self.trust_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "action": "register_entity",
            "entity_id": entity_id,
            "entity_name": name,
            "trust_level": initial_trust_level.value,
            "status": "success"
        })
        
        logger.info(f"Trust entity '{entity_id}' registered with {initial_trust_level.value} trust level")
        
        return entity_record
    
    async def establish_trust_relationship(
        self,
        from_entity: str,
        to_entity: str,
        trust_level: TrustLevel,
        relationship_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Establish a trust relationship between two entities
        
        Args:
            from_entity: Source entity ID
            to_entity: Target entity ID
            trust_level: Trust level for the relationship
            relationship_type: Type of relationship
            metadata: Additional relationship metadata
            
        Returns:
            Dictionary containing relationship information
        """
        # Validate entities exist
        if from_entity not in self.trust_entities:
            raise ValueError(f"Source entity '{from_entity}' not found")
        if to_entity not in self.trust_entities:
            raise ValueError(f"Target entity '{to_entity}' not found")
        
        # Check if relationship already exists
        relationship_id = f"{from_entity}_to_{to_entity}"
        if relationship_id in self.trust_relationships:
            raise ValueError(f"Trust relationship already exists between '{from_entity}' and '{to_entity}'")
        
        # Create relationship record
        relationship_record = {
            "relationship_id": relationship_id,
            "from_entity": from_entity,
            "to_entity": to_entity,
            "trust_level": trust_level.value,
            "relationship_type": relationship_type,
            "created_at": asyncio.get_event_loop().time(),
            "status": TrustStatus.ACTIVE.value,
            "metadata": metadata or {}
        }
        
        # Store relationship
        self.trust_relationships[relationship_id] = relationship_record
        
        # Update reputation scores
        await self._update_reputation_from_relationship(relationship_record)
        
        # Record in history
        self.trust_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "action": "establish_relationship",
            "from_entity": from_entity,
            "to_entity": to_entity,
            "trust_level": trust_level.value,
            "relationship_type": relationship_type,
            "status": "success"
        })
        
        logger.info(f"Trust relationship established: {from_entity} -> {to_entity} ({trust_level.value})")
        
        return relationship_record
    
    async def validate_certificate_trust(
        self,
        certificate_id: str,
        certificate_data: Dict[str, Any],
        validation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate certificate trust based on trust network
        
        Args:
            certificate_id: Certificate identifier
            certificate_data: Certificate data for validation
            validation_context: Additional validation context
            
        Returns:
            Dictionary containing trust validation result
        """
        # Generate validation ID
        validation_id = f"trust_validation_{certificate_id}_{secrets.token_hex(8)}"
        
        try:
            # Extract trust-related information from certificate
            trust_info = await self._extract_certificate_trust_info(certificate_data)
            
            # Perform trust validation
            validation_result = await self._perform_trust_validation(trust_info, validation_context)
            
            # Store validation result
            self.trust_certificates[certificate_id] = {
                "certificate_id": certificate_id,
                "trust_info": trust_info,
                "validation_result": validation_result,
                "validated_at": asyncio.get_event_loop().time(),
                "status": "validated"
            }
            
            # Record validation in history
            self.trust_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "validate_certificate_trust",
                "certificate_id": certificate_id,
                "validation_id": validation_id,
                "trust_level": validation_result["overall_trust_level"],
                "status": "success"
            })
            
            logger.info(f"Certificate {certificate_id} trust validated: {validation_result['overall_trust_level']}")
            
            return validation_result
            
        except Exception as e:
            error_msg = f"Certificate trust validation failed: {str(e)}"
            logger.error(f"Failed to validate certificate {certificate_id}: {error_msg}")
            
            # Store error result
            self.trust_certificates[certificate_id] = {
                "certificate_id": certificate_id,
                "error": error_msg,
                "validated_at": asyncio.get_event_loop().time(),
                "status": "error"
            }
            
            raise
    
    async def calculate_trust_score(
        self,
        entity_id: str,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate trust score for an entity
        
        Args:
            entity_id: Entity identifier
            include_history: Whether to include score history
            
        Returns:
            Dictionary containing trust score and factors
        """
        if entity_id not in self.trust_entities:
            raise ValueError(f"Entity '{entity_id}' not found")
        
        if entity_id not in self.reputation_scores:
            raise ValueError(f"No reputation data for entity '{entity_id}'")
        
        # Get current reputation data
        reputation_data = self.reputation_scores[entity_id]
        
        # Calculate updated score
        updated_score = await self._calculate_updated_reputation_score(entity_id)
        
        # Update stored score
        reputation_data["current_score"] = updated_score
        reputation_data["last_updated"] = asyncio.get_event_loop().time()
        
        # Add to history
        reputation_data["history"].append({
            "score": updated_score,
            "timestamp": asyncio.get_event_loop().time(),
            "reason": "Score recalculation"
        })
        
        # Determine trust level from score
        trust_level = self._determine_trust_level_from_score(updated_score)
        
        # Update entity trust level
        self.trust_entities[entity_id]["trust_level"] = trust_level.value
        self.trust_entities[entity_id]["last_updated"] = asyncio.get_event_loop().time()
        
        result = {
            "entity_id": entity_id,
            "current_score": updated_score,
            "trust_level": trust_level.value,
            "factors": reputation_data["factors"],
            "last_updated": asyncio.get_event_loop().time()
        }
        
        if include_history:
            result["history"] = reputation_data["history"]
        
        return result
    
    async def analyze_trust_network(
        self,
        entity_id: str,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze trust network around an entity
        
        Args:
            entity_id: Entity identifier for analysis
            max_depth: Maximum depth for trust chain analysis
            
        Returns:
            Dictionary containing trust network analysis
        """
        if entity_id not in self.trust_entities:
            raise ValueError(f"Entity '{entity_id}' not found")
        
        # Build trust network graph
        trust_graph = await self._build_trust_graph(entity_id, max_depth)
        
        # Analyze trust patterns
        analysis_result = await self._analyze_trust_patterns(trust_graph)
        
        # Calculate network metrics
        network_metrics = await self._calculate_network_metrics(trust_graph)
        
        return {
            "entity_id": entity_id,
            "analysis_timestamp": asyncio.get_event_loop().time(),
            "max_depth": max_depth,
            "trust_graph": trust_graph,
            "analysis": analysis_result,
            "network_metrics": network_metrics
        }
    
    async def _validate_entity_registration(
        self,
        entity_id: str,
        name: str,
        entity_type: str
    ) -> None:
        """Validate entity registration parameters"""
        # Validate entity ID
        if not entity_id or len(entity_id) < 3:
            raise ValueError("Entity ID must be at least 3 characters long")
        
        if not entity_id.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Entity ID must contain only alphanumeric characters, underscores, and hyphens")
        
        # Validate name
        if not name or len(name.strip()) < 2:
            raise ValueError("Entity name must be at least 2 characters long")
        
        # Validate entity type
        valid_types = ["authority", "organization", "system", "individual", "service"]
        if entity_type not in valid_types:
            raise ValueError(f"Entity type must be one of: {', '.join(valid_types)}")
    
    def _calculate_reputation_from_trust_level(self, trust_level: TrustLevel) -> int:
        """Calculate reputation score from trust level"""
        trust_level_scores = {
            TrustLevel.UNTRUSTED: 0,
            TrustLevel.LOW: 25,
            TrustLevel.MEDIUM: 50,
            TrustLevel.HIGH: 75,
            TrustLevel.VERIFIED: 90,
            TrustLevel.CERTIFIED: 100
        }
        return trust_level_scores.get(trust_level, 50)
    
    async def _update_reputation_from_relationship(self, relationship: Dict[str, Any]) -> None:
        """Update reputation scores based on trust relationship"""
        from_entity = relationship["from_entity"]
        to_entity = relationship["to_entity"]
        trust_level = relationship["trust_level"]
        
        # Calculate reputation impact
        trust_level_scores = {
            "untrusted": -20,
            "low": -10,
            "medium": 0,
            "high": 10,
            "verified": 15,
            "certified": 20
        }
        
        impact = trust_level_scores.get(trust_level, 0)
        
        # Update target entity reputation
        if to_entity in self.reputation_scores:
            current_score = self.reputation_scores[to_entity]["current_score"]
            new_score = max(0, min(100, current_score + impact))
            
            self.reputation_scores[to_entity]["current_score"] = new_score
            self.reputation_scores[to_entity]["factors"]["trust_relationships"] += impact
            
            # Add to history
            self.reputation_scores[to_entity]["history"].append({
                "score": new_score,
                "timestamp": asyncio.get_event_loop().time(),
                "reason": f"Trust relationship from {from_entity}",
                "impact": impact
            })
    
    async def _extract_certificate_trust_info(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract trust-related information from certificate data"""
        trust_info = {
            "issuer": certificate_data.get("issuer"),
            "subject": certificate_data.get("subject"),
            "authority": certificate_data.get("authority"),
            "signature_algorithm": certificate_data.get("signature_algorithm"),
            "trust_chain": certificate_data.get("trust_chain", []),
            "certification_level": certificate_data.get("certification_level"),
            "validation_status": certificate_data.get("validation_status")
        }
        
        return trust_info
    
    async def _perform_trust_validation(
        self,
        trust_info: Dict[str, Any],
        validation_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform trust validation based on trust information"""
        validation_result = {
            "validation_timestamp": asyncio.get_event_loop().time(),
            "overall_trust_level": TrustLevel.UNTRUSTED.value,
            "overall_score": 0,
            "validation_factors": {},
            "trust_chain_validation": {},
            "recommendations": []
        }
        
        # Validate issuer trust
        issuer_trust = await self._validate_issuer_trust(trust_info.get("issuer"))
        validation_result["validation_factors"]["issuer_trust"] = issuer_trust
        
        # Validate authority trust
        authority_trust = await self._validate_authority_trust(trust_info.get("authority"))
        validation_result["validation_factors"]["authority_trust"] = authority_trust
        
        # Validate trust chain
        chain_validation = await self._validate_trust_chain(trust_info.get("trust_chain", []))
        validation_result["trust_chain_validation"] = chain_validation
        
        # Calculate overall score
        overall_score = await self._calculate_overall_trust_score(validation_result["validation_factors"])
        validation_result["overall_score"] = overall_score
        
        # Determine overall trust level
        overall_trust_level = self._determine_trust_level_from_score(overall_score)
        validation_result["overall_trust_level"] = overall_trust_level.value
        
        # Generate recommendations
        validation_result["recommendations"] = await self._generate_trust_recommendations(validation_result)
        
        return validation_result
    
    async def _validate_issuer_trust(self, issuer: Optional[str]) -> Dict[str, Any]:
        """Validate issuer trust level"""
        if not issuer:
            return {
                "valid": False,
                "score": 0,
                "reason": "No issuer specified",
                "trust_level": TrustLevel.UNTRUSTED.value
            }
        
        # Check if issuer is a known trust entity
        if issuer in self.trust_entities:
            entity = self.trust_entities[issuer]
            return {
                "valid": True,
                "score": entity["reputation_score"],
                "reason": "Known trust entity",
                "trust_level": entity["trust_level"]
            }
        else:
            return {
                "valid": False,
                "score": 25,
                "reason": "Unknown issuer",
                "trust_level": TrustLevel.LOW.value
            }
    
    async def _validate_authority_trust(self, authority: Optional[str]) -> Dict[str, Any]:
        """Validate authority trust level"""
        if not authority:
            return {
                "valid": False,
                "score": 0,
                "reason": "No authority specified",
                "trust_level": TrustLevel.UNTRUSTED.value
            }
        
        # Check if authority is a known trust entity
        if authority in self.trust_entities:
            entity = self.trust_entities[authority]
            return {
                "valid": True,
                "score": entity["reputation_score"],
                "reason": "Known trust authority",
                "trust_level": entity["trust_level"]
            }
        else:
            return {
                "valid": False,
                "score": 30,
                "reason": "Unknown authority",
                "trust_level": TrustLevel.LOW.value
            }
    
    async def _validate_trust_chain(self, trust_chain: List[str]) -> Dict[str, Any]:
        """Validate trust chain"""
        if not trust_chain:
            return {
                "valid": False,
                "score": 0,
                "reason": "No trust chain specified",
                "chain_length": 0,
                "valid_links": 0
            }
        
        valid_links = 0
        total_score = 0
        
        for entity_id in trust_chain:
            if entity_id in self.trust_entities:
                entity = self.trust_entities[entity_id]
                valid_links += 1
                total_score += entity["reputation_score"]
        
        chain_length = len(trust_chain)
        average_score = total_score / chain_length if chain_length > 0 else 0
        
        return {
            "valid": valid_links == chain_length,
            "score": average_score,
            "reason": f"{valid_links}/{chain_length} valid chain links",
            "chain_length": chain_length,
            "valid_links": valid_links
        }
    
    async def _calculate_overall_trust_score(self, validation_factors: Dict[str, Any]) -> int:
        """Calculate overall trust score from validation factors"""
        # Weight factors
        weights = {
            "issuer_trust": 0.4,
            "authority_trust": 0.3,
            "trust_chain": 0.3
        }
        
        total_score = 0
        total_weight = 0
        
        for factor, weight in weights.items():
            if factor in validation_factors:
                factor_data = validation_factors[factor]
                if isinstance(factor_data, dict) and "score" in factor_data:
                    total_score += factor_data["score"] * weight
                    total_weight += weight
        
        if total_weight == 0:
            return 0
        
        return int(total_score / total_weight)
    
    def _determine_trust_level_from_score(self, score: int) -> TrustLevel:
        """Determine trust level from reputation score"""
        if score >= 90:
            return TrustLevel.CERTIFIED
        elif score >= 80:
            return TrustLevel.VERIFIED
        elif score >= 60:
            return TrustLevel.HIGH
        elif score >= 40:
            return TrustLevel.MEDIUM
        elif score >= 20:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNTRUSTED
    
    async def _generate_trust_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate trust recommendations based on validation result"""
        recommendations = []
        
        overall_score = validation_result["overall_score"]
        
        if overall_score < 50:
            recommendations.append("Consider additional verification before accepting this certificate")
            recommendations.append("Review trust chain for potential issues")
        
        if overall_score < 70:
            recommendations.append("Certificate meets basic trust requirements but consider enhanced validation")
        
        if overall_score >= 80:
            recommendations.append("Certificate has high trust level and is recommended for use")
        
        return recommendations
    
    async def _calculate_updated_reputation_score(self, entity_id: str) -> int:
        """Calculate updated reputation score considering all factors"""
        if entity_id not in self.reputation_scores:
            return 0
        
        reputation_data = self.reputation_scores[entity_id]
        factors = reputation_data["factors"]
        
        # Calculate base score
        base_score = factors["base_score"]
        
        # Apply activity bonus
        activity_bonus = factors["activity_bonus"]
        
        # Apply trust relationship bonus
        relationship_bonus = factors["trust_relationships"]
        
        # Apply certificate quality bonus
        quality_bonus = factors["certificate_quality"]
        
        # Apply time decay
        time_decay = factors["time_decay"]
        
        # Calculate total score
        total_score = base_score + activity_bonus + relationship_bonus + quality_bonus + time_decay
        
        # Ensure score is within bounds
        return max(0, min(100, int(total_score)))
    
    async def _build_trust_graph(self, entity_id: str, max_depth: int) -> Dict[str, Any]:
        """Build trust graph around an entity"""
        graph = {
            "root_entity": entity_id,
            "max_depth": max_depth,
            "nodes": {},
            "edges": {},
            "depth_levels": {}
        }
        
        # Add root entity
        if entity_id in self.trust_entities:
            graph["nodes"][entity_id] = self.trust_entities[entity_id]
            graph["depth_levels"][0] = [entity_id]
        
        # Build graph by depth levels
        for depth in range(1, max_depth + 1):
            current_level = []
            
            # Find entities at this depth
            for edge_id, edge in self.trust_relationships.items():
                if edge["status"] != TrustStatus.ACTIVE.value:
                    continue
                
                # Check if this edge connects to entities at previous depth
                prev_level = graph["depth_levels"].get(depth - 1, [])
                
                if edge["from_entity"] in prev_level and edge["to_entity"] not in graph["nodes"]:
                    # Add new entity
                    if edge["to_entity"] in self.trust_entities:
                        graph["nodes"][edge["to_entity"]] = self.trust_entities[edge["to_entity"]]
                        current_level.append(edge["to_entity"])
                        graph["edges"][edge_id] = edge
                
                elif edge["to_entity"] in prev_level and edge["from_entity"] not in graph["nodes"]:
                    # Add new entity
                    if edge["from_entity"] in self.trust_entities:
                        graph["nodes"][edge["from_entity"]] = self.trust_entities[edge["from_entity"]]
                        current_level.append(edge["from_entity"])
                        graph["edges"][edge_id] = edge
            
            if current_level:
                graph["depth_levels"][depth] = current_level
        
        return graph
    
    async def _analyze_trust_patterns(self, trust_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trust patterns in the graph"""
        nodes = trust_graph["nodes"]
        edges = trust_graph["edges"]
        
        # Calculate basic metrics
        total_entities = len(nodes)
        total_relationships = len(edges)
        
        # Analyze trust level distribution
        trust_levels = {}
        for entity in nodes.values():
            level = entity.get("trust_level", "unknown")
            trust_levels[level] = trust_levels.get(level, 0) + 1
        
        # Calculate average reputation score
        total_score = sum(entity.get("reputation_score", 0) for entity in nodes.values())
        avg_score = total_score / total_entities if total_entities > 0 else 0
        
        return {
            "total_entities": total_entities,
            "total_relationships": total_relationships,
            "trust_level_distribution": trust_levels,
            "average_reputation_score": avg_score,
            "network_density": total_relationships / (total_entities * (total_entities - 1)) if total_entities > 1 else 0
        }
    
    async def _calculate_network_metrics(self, trust_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate network-level metrics"""
        nodes = trust_graph["nodes"]
        edges = trust_graph["edges"]
        
        # Calculate connectivity metrics
        in_degrees = {}
        out_degrees = {}
        
        for edge in edges.values():
            from_entity = edge["from_entity"]
            to_entity = edge["to_entity"]
            
            out_degrees[from_entity] = out_degrees.get(from_entity, 0) + 1
            in_degrees[to_entity] = in_degrees.get(to_entity, 0) + 1
        
        # Find hub entities (high out-degree)
        hub_entities = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Find authority entities (high in-degree)
        authority_entities = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "connectivity_metrics": {
                "in_degrees": in_degrees,
                "out_degrees": out_degrees
            },
            "hub_entities": hub_entities,
            "authority_entities": authority_entities,
            "network_centralization": max(out_degrees.values()) / total_entities if total_entities > 0 else 0
        }
    
    async def get_trust_entity_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get trust entity information by ID"""
        return self.trust_entities.get(entity_id)
    
    async def get_trust_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get trust relationships for an entity"""
        relationships = []
        
        for relationship in self.trust_relationships.values():
            if (relationship["from_entity"] == entity_id or 
                relationship["to_entity"] == entity_id):
                relationships.append(relationship)
        
        return relationships
    
    async def get_trust_statistics(self) -> Dict[str, Any]:
        """Get trust network statistics"""
        total_entities = len(self.trust_entities)
        active_entities = len([e for e in self.trust_entities.values() if e.get("status") == TrustStatus.ACTIVE.value])
        
        total_relationships = len(self.trust_relationships)
        active_relationships = len([r for r in self.trust_relationships.values() if r.get("status") == TrustStatus.ACTIVE.value])
        
        total_certificates = len(self.trust_certificates)
        validated_certificates = len([c for c in self.trust_certificates.values() if c.get("status") == "validated"])
        
        # Count by trust level
        entities_by_trust_level = {}
        for entity in self.trust_entities.values():
            level = entity.get("trust_level", "unknown")
            entities_by_trust_level[level] = entities_by_trust_level.get(level, 0) + 1
        
        return {
            "total_entities": total_entities,
            "active_entities": active_entities,
            "total_relationships": total_relationships,
            "active_relationships": active_relationships,
            "total_certificates": total_certificates,
            "validated_certificates": validated_certificates,
            "entities_by_trust_level": entities_by_trust_level,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def get_trust_history(
        self,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get trust network history with optional filtering"""
        history = self.trust_history.copy()
        
        # Filter by entity ID
        if entity_id:
            history = [h for h in history if h.get("entity_id") == entity_id]
        
        # Filter by action
        if action:
            history = [h for h in history if h.get("action") == action]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the trust network service"""
        return {
            "status": "healthy",
            "trust_levels": [level.value for level in self.trust_levels],
            "trust_statuses": [status.value for status in self.trust_statuses],
            "trust_entities_count": len(self.trust_entities),
            "trust_relationships_count": len(self.trust_relationships),
            "trust_certificates_count": len(self.trust_certificates),
            "reputation_scores_count": len(self.reputation_scores),
            "trust_history_size": len(self.trust_history),
            "trust_settings": {
                "default_trust_level": self.trust_settings["default_trust_level"].value,
                "min_trust_score": self.trust_settings["min_trust_score"],
                "max_trust_score": self.trust_settings["max_trust_score"],
                "trust_decay_rate": self.trust_settings["trust_decay_rate"]
            },
            "timestamp": asyncio.get_event_loop().time()
        }
