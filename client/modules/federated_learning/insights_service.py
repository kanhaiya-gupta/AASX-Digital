"""
Insights Service
===============

Handles cross-twin insights and analytics using shared services and database.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Import shared services and database managers (following twin_registry pattern)
from src.federated_learning.core.federated_learning_service import FederatedLearningService
from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager

logger = logging.getLogger(__name__)

class InsightsService:
    """Service for managing cross-twin insights and analytics"""
    
    def __init__(self, db_manager: BaseDatabaseManager, digital_twin_service: DigitalTwinService, federated_learning_service: FederatedLearningService):
        """Initialize the insights service"""
        self.db_manager = db_manager
        self.digital_twin_service = digital_twin_service
        self.federated_learning_service = federated_learning_service
        logger.info("✅ Insights Service initialized successfully")
    
    def get_cross_twin_insights(self):
        """Get cross-twin insights from database"""
        try:
            # Get federated learning statistics from database
            query = """
                SELECT 
                    COUNT(*) as total_federated_twins,
                    SUM(CASE WHEN federated_participation_status = 'active' THEN 1 ELSE 0 END) as active_twins,
                    SUM(CASE WHEN federated_participation_status = 'ready' THEN 1 ELSE 0 END) as ready_twins,
                    AVG(health_score) as avg_health_score,
                    AVG(federated_contribution_score) as avg_contribution_score,
                    AVG(differential_privacy_epsilon) as avg_data_quality,
                    COUNT(CASE WHEN federated_health_status = 'healthy' THEN 1 END) as healthy_twins,
                    COUNT(CASE WHEN federated_health_status = 'moderate' THEN 1 END) as moderate_twins,
                    COUNT(CASE WHEN federated_health_status = 'poor' THEN 1 END) as poor_twins
                FROM digital_twins
            """
            
            stats = self.db_manager.execute_query(query)[0]
            
            # Get top contributors (twins with highest contribution scores)
            top_contributors_query = """
                SELECT 
                    twin_id,
                    twin_name,
                    health_score,
                    federated_contribution_score,
                    federated_round_number,
                    federated_health_status
                FROM digital_twins
                WHERE federated_contribution_score > 0
                ORDER BY federated_contribution_score DESC, health_score DESC
                LIMIT 5
            """
            
            top_contributors = self.db_manager.execute_query(top_contributors_query)
            
            # Convert to expected format
            contributors_list = []
            for contributor in top_contributors:
                contributors_list.append({
                    'twin_id': contributor['twin_id'],
                    'twin_name': contributor['twin_name'],
                    'health_score': contributor['health_score'] or 0,
                    'contribution_score': contributor['federated_contribution_score'] or 0,
                    'rounds': contributor['federated_round_number'] or 0,
                    'health_status': contributor['federated_health_status'] or 'unknown'
                })
            
            # Generate insights based on available data
            insights = []
            total_twins = stats['total_federated_twins'] or 0
            active_twins = stats['active_twins'] or 0
            
            if total_twins > 0:
                if active_twins > 0:
                    insights.append({
                        'type': 'federation_status',
                        'title': 'Active Federation Detected',
                        'description': f'Currently {active_twins} twins are actively participating in federated learning.',
                        'confidence': 0.95,
                        'twins': ['active_twins'],
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    insights.append({
                        'type': 'federation_status',
                        'title': 'Federation Ready',
                        'description': f'{total_twins} twins available for federated learning. Start federation to begin collaborative training.',
                        'confidence': 0.90,
                        'twins': ['all_twins'],
                        'timestamp': datetime.now().isoformat()
                    })
            
            return {
                'total_federated_twins': total_twins,
                'active_twins': active_twins,
                'ready_twins': stats['ready_twins'] or 0,
                'avg_contribution_score': round(stats['avg_contribution_score'] or 0, 2),
                'avg_health_score': round(stats['avg_health_score'] or 0, 1),
                'avg_data_quality': round(stats['avg_data_quality'] or 1.0, 2),
                'twin_types': {'industrial_process': total_twins},  # All twins are industrial process
                'performance_distribution': {
                    'high_performers': stats['healthy_twins'] or 0,
                    'medium_performers': stats['moderate_twins'] or 0,
                    'low_performers': stats['poor_twins'] or 0
                },
                'health_distribution': {
                    'healthy': stats['healthy_twins'] or 0,
                    'moderate': stats['moderate_twins'] or 0,
                    'poor': stats['poor_twins'] or 0
                },
                'top_contributors': contributors_list,
                'insights': insights,
                'relationships': []  # No relationships yet
            }
            
        except Exception as e:
            logger.error(f"Error getting cross-twin insights: {e}")
            return {
                'total_federated_twins': 0,
                'active_twins': 0,
                'ready_twins': 0,
                'avg_contribution_score': 0,
                'avg_health_score': 0,
                'avg_data_quality': 0,
                'twin_types': {},
                'performance_distribution': {'high_performers': 0, 'medium_performers': 0, 'low_performers': 0},
                'health_distribution': {'healthy': 0, 'moderate': 0, 'poor': 0},
                'top_contributors': [],
                'insights': [],
                'relationships': []
            }
    
    def get_insights_history(self) -> List[Dict[str, Any]]:
        """Get historical insights from database."""
        try:
            # Query database for insights history
            query = """
                SELECT 
                    twin_id,
                    federated_round_number,
                    federated_contribution_score,
                    health_score,
                    federated_last_sync
                FROM digital_twins 
                WHERE federated_participation_status = 'active'
                ORDER BY federated_round_number DESC, federated_contribution_score DESC
                LIMIT 100
            """
            
            results = self.db_manager.connection_manager.execute_query(query)
            
            history = []
            for row in results:
                history.append({
                    "twin_id": row["twin_id"],
                    "round_number": row["federated_round_number"],
                    "contribution_score": row["federated_contribution_score"],
                    "health_score": row["health_score"],
                    "last_sync": row["federated_last_sync"]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting insights history: {e}")
            return []
    
    def get_knowledge_graph(self) -> Dict[str, Any]:
        """Generate knowledge graph from twin relationships."""
        try:
            # Get all twins
            all_twins = self.digital_twin_service.get_all()
            
            nodes = []
            edges = []
            
            # Create nodes for each twin
            for twin in all_twins:
                nodes.append({
                    "id": twin.twin_id,
                    "label": twin.twin_name,
                    "type": "twin",
                    "health_score": twin.health_score,
                    "federated_status": twin.federated_participation_status,
                    "contribution_score": twin.federated_contribution_score
                })
            
            # Create edges for federated relationships
            federated_twins = self.federated_learning_service.get_federated_ready_twins()
            for i, twin1 in enumerate(federated_twins):
                for j, twin2 in enumerate(federated_twins[i+1:], i+1):
                    edge_strength = self._calculate_relationship_strength(twin1, twin2)
                    if edge_strength > 0:
                        edges.append({
                            "source": twin1.twin_id,
                            "target": twin2.twin_id,
                            "type": "federated_collaboration",
                            "strength": edge_strength,
                            "label": f"Collaboration ({edge_strength:.2f})"
                        })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "total_twins": len(all_twins),
                    "federated_twins": len(federated_twins),
                    "relationships": len(edges),
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating knowledge graph: {e}")
            return {"nodes": [], "edges": [], "metadata": {}}
    
    def get_twin_relationships(self) -> List[Dict[str, Any]]:
        """Get relationships between twins."""
        try:
            # Get federated twins
            federated_twins = self.federated_learning_service.get_federated_ready_twins()
            
            relationships = []
            
            # Generate relationships
            for i, twin1 in enumerate(federated_twins):
                for j, twin2 in enumerate(federated_twins[i+1:], i+1):
                    relationship = self._analyze_twin_relationship(twin1, twin2)
                    if relationship:
                        relationships.append(relationship)
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error getting twin relationships: {e}")
            return []
    
    def get_cross_twin_predictions(self) -> List[Dict[str, Any]]:
        """Get predictions based on cross-twin analysis."""
        try:
            # Get federated twins
            federated_twins = self.federated_learning_service.get_federated_ready_twins()
            
            predictions = []
            
            # Generate predictions
            for twin in federated_twins:
                prediction = self._generate_twin_prediction(twin)
                if prediction:
                    predictions.append(prediction)
            
            # Add collaborative predictions
            collaborative_predictions = self._generate_collaborative_predictions(federated_twins)
            predictions.extend(collaborative_predictions)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting cross-twin predictions: {e}")
            return []
    
    def _generate_twin_insight(self, twin1, twin2) -> Optional[Dict[str, Any]]:
        """Generate insight between two twins."""
        try:
            # Calculate similarity score
            similarity = self._calculate_twin_similarity(twin1, twin2)
            
            if similarity < 0.3:  # Only generate insights for similar twins
                return None
            
            # Determine insight type
            if twin1.health_score > 80 and twin2.health_score > 80:
                insight_type = "high_performance_pair"
                confidence = 0.9
            elif twin1.federated_contribution_score > 70 and twin2.federated_contribution_score > 70:
                insight_type = "high_contribution_pair"
                confidence = 0.8
            else:
                insight_type = "collaboration_opportunity"
                confidence = 0.6
            
            return {
                "insight_id": f"insight_{twin1.twin_id}_{twin2.twin_id}",
                "insight_type": insight_type,
                "twin_ids": [twin1.twin_id, twin2.twin_id],
                "twin_names": [twin1.twin_name, twin2.twin_name],
                "similarity_score": similarity,
                "confidence_score": confidence,
                "description": self._get_insight_description(insight_type, twin1, twin2),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating twin insight: {e}")
            return None
    
    def _generate_performance_insights(self, twins: List) -> List[Dict[str, Any]]:
        """Generate performance-based insights."""
        try:
            insights = []
            
            # Find top performers
            top_performers = sorted(twins, key=lambda x: x.health_score, reverse=True)[:3]
            
            if len(top_performers) >= 2:
                insights.append({
                    "insight_id": "top_performers_insight",
                    "insight_type": "top_performers",
                    "twin_ids": [t.twin_id for t in top_performers],
                    "twin_names": [t.twin_name for t in top_performers],
                    "confidence_score": 0.9,
                    "description": f"Top performing twins: {', '.join([t.twin_name for t in top_performers])}",
                    "created_at": datetime.now().isoformat()
                })
            
            # Find improvement opportunities
            low_performers = [t for t in twins if t.health_score < 60]
            if low_performers:
                insights.append({
                    "insight_id": "improvement_opportunity",
                    "insight_type": "improvement_opportunity",
                    "twin_ids": [t.twin_id for t in low_performers],
                    "twin_names": [t.twin_name for t in low_performers],
                    "confidence_score": 0.7,
                    "description": f"Twins needing improvement: {', '.join([t.twin_name for t in low_performers])}",
                    "created_at": datetime.now().isoformat()
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating performance insights: {e}")
            return []
    
    def _generate_collaboration_insights(self, twins: List) -> List[Dict[str, Any]]:
        """Generate collaboration-based insights."""
        try:
            insights = []
            
            # Find high contributors
            high_contributors = [t for t in twins if t.federated_contribution_score > 70]
            
            if len(high_contributors) >= 2:
                insights.append({
                    "insight_id": "high_contributors_insight",
                    "insight_type": "high_contributors",
                    "twin_ids": [t.twin_id for t in high_contributors],
                    "twin_names": [t.twin_name for t in high_contributors],
                    "confidence_score": 0.8,
                    "description": f"High contributing twins: {', '.join([t.twin_name for t in high_contributors])}",
                    "created_at": datetime.now().isoformat()
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating collaboration insights: {e}")
            return []
    
    def _calculate_twin_similarity(self, twin1, twin2) -> float:
        """Calculate similarity between two twins."""
        try:
            # Health score similarity
            health_diff = abs(twin1.health_score - twin2.health_score) / 100.0
            health_similarity = 1.0 - health_diff
            
            # Contribution score similarity
            contrib_diff = abs(twin1.federated_contribution_score - twin2.federated_contribution_score) / 100.0
            contrib_similarity = 1.0 - contrib_diff
            
            # Round number similarity
            round_diff = abs(twin1.federated_round_number - twin2.federated_round_number) / max(1, max(twin1.federated_round_number, twin2.federated_round_number))
            round_similarity = 1.0 - round_diff
            
            # Weighted average
            return (health_similarity * 0.4 + contrib_similarity * 0.4 + round_similarity * 0.2)
            
        except Exception as e:
            logger.error(f"Error calculating twin similarity: {e}")
            return 0.0
    
    def _calculate_relationship_strength(self, twin1, twin2) -> float:
        """Calculate relationship strength between twins."""
        try:
            similarity = self._calculate_twin_similarity(twin1, twin2)
            
            # Both twins must be active
            if twin1.federated_participation_status != "active" or twin2.federated_participation_status != "active":
                return 0.0
            
            # Both twins must have good health
            if twin1.health_score < 50 or twin2.health_score < 50:
                return 0.0
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating relationship strength: {e}")
            return 0.0
    
    def _analyze_twin_relationship(self, twin1, twin2) -> Optional[Dict[str, Any]]:
        """Analyze relationship between two twins."""
        try:
            strength = self._calculate_relationship_strength(twin1, twin2)
            
            if strength < 0.3:
                return None
            
            return {
                "relationship_id": f"rel_{twin1.twin_id}_{twin2.twin_id}",
                "twin_ids": [twin1.twin_id, twin2.twin_id],
                "twin_names": [twin1.twin_name, twin2.twin_name],
                "strength": strength,
                "type": "federated_collaboration",
                "health_scores": [twin1.health_score, twin2.health_score],
                "contribution_scores": [twin1.federated_contribution_score, twin2.federated_contribution_score],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing twin relationship: {e}")
            return None
    
    def _generate_twin_prediction(self, twin) -> Optional[Dict[str, Any]]:
        """Generate prediction for a single twin."""
        try:
            # Predict future health score
            current_health = twin.health_score
            predicted_health = min(100, current_health + (twin.federated_contribution_score * 0.1))
            
            # Predict future contribution
            current_contrib = twin.federated_contribution_score
            predicted_contrib = min(100, current_contrib + (current_health * 0.05))
            
            return {
                "prediction_id": f"pred_{twin.twin_id}",
                "twin_id": twin.twin_id,
                "twin_name": twin.twin_name,
                "prediction_type": "performance_forecast",
                "current_health": current_health,
                "predicted_health": predicted_health,
                "current_contribution": current_contrib,
                "predicted_contribution": predicted_contrib,
                "confidence": 0.7,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating twin prediction: {e}")
            return None
    
    def _generate_collaborative_predictions(self, twins: List) -> List[Dict[str, Any]]:
        """Generate collaborative predictions."""
        try:
            predictions = []
            
            if len(twins) >= 3:
                # Predict overall federation performance
                avg_health = sum(t.health_score for t in twins) / len(twins)
                avg_contrib = sum(t.federated_contribution_score for t in twins) / len(twins)
                
                predicted_health = min(100, avg_health + (avg_contrib * 0.1))
                
                predictions.append({
                    "prediction_id": "federation_performance",
                    "prediction_type": "federation_forecast",
                    "current_avg_health": avg_health,
                    "predicted_avg_health": predicted_health,
                    "participating_twins": len(twins),
                    "confidence": 0.8,
                    "created_at": datetime.now().isoformat()
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating collaborative predictions: {e}")
            return []
    
    def _get_insight_description(self, insight_type: str, twin1, twin2) -> str:
        """Get description for insight type."""
        descriptions = {
            "high_performance_pair": f"{twin1.twin_name} and {twin2.twin_name} are both high-performing twins with excellent health scores.",
            "high_contribution_pair": f"{twin1.twin_name} and {twin2.twin_name} are both high contributors to federated learning.",
            "collaboration_opportunity": f"{twin1.twin_name} and {twin2.twin_name} show potential for collaboration based on their similar characteristics."
        }
        return descriptions.get(insight_type, "Insight generated based on twin analysis.") 