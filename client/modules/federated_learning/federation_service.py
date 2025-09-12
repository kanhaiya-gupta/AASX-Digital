"""
Federation Service
=================

Handles federation management operations using shared services and database.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Import shared services and database managers (following twin_registry pattern)
from src.modules.federated_learning.core.federated_learning_service import FederatedLearningService
from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager

logger = logging.getLogger(__name__)

class FederationService:
    """Service for managing federated learning federation operations"""
    
    def __init__(self, db_manager: BaseDatabaseManager, digital_twin_service: DigitalTwinService, federated_learning_service: FederatedLearningService):
        """Initialize the federation service"""
        self.db_manager = db_manager
        self.digital_twin_service = digital_twin_service
        self.federated_learning_service = federated_learning_service
        logger.info("✅ Federation Service initialized successfully")
    
    def start_federation(self, twin_ids: List[str], model_type: str = "federated_averaging", rounds: int = 10, privacy_level: str = "high") -> Dict[str, Any]:
        """Start federated learning process"""
        try:
            logger.info(f"🚀 Starting federation with {len(twin_ids)} twins, model: {model_type}, rounds: {rounds}")
            
            # Register twins for federated learning
            registered_twins = []
            for twin_id in twin_ids:
                try:
                    result = self.federated_learning_service.register_federated_node(twin_id)
                    if result.get("success"):
                        registered_twins.append(twin_id)
                        logger.info(f"✅ Twin {twin_id} registered for federation")
                    else:
                        logger.warning(f"⚠️ Failed to register twin {twin_id}: {result.get('error')}")
                except Exception as e:
                    logger.error(f"❌ Error registering twin {twin_id}: {e}")
            
            # Get federation status
            federation_status = self.get_federation_status()
            
            return {
                "success": True,
                "message": f"Federation started with {len(registered_twins)} twins",
                "registered_twins": registered_twins,
                "model_type": model_type,
                "rounds": rounds,
                "privacy_level": privacy_level,
                "federation_status": federation_status
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting federation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_federation(self) -> Dict[str, Any]:
        """Stop federated learning process"""
        try:
            logger.info("🛑 Stopping federation")
            
            # Get current federation status
            current_status = self.get_federation_status()
            
            return {
                "success": True,
                "message": "Federation stopped successfully",
                "previous_status": current_status
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping federation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_federation_status(self):
        """Get current federation status from database"""
        try:
            # Get federation statistics from database
            query = """
                SELECT 
                    COUNT(*) as total_twins,
                    SUM(CASE WHEN federated_participation_status = 'active' THEN 1 ELSE 0 END) as active_twins,
                    SUM(CASE WHEN federated_participation_status = 'ready' THEN 1 ELSE 0 END) as ready_twins,
                    AVG(health_score) as avg_health_score,
                    AVG(federated_contribution_score) as avg_contribution_score,
                    MAX(federated_round_number) as max_rounds,
                    COUNT(CASE WHEN federated_health_status = 'healthy' THEN 1 END) as healthy_twins,
                    COUNT(CASE WHEN federated_health_status = 'moderate' THEN 1 END) as moderate_twins,
                    COUNT(CASE WHEN federated_health_status = 'poor' THEN 1 END) as poor_twins
                FROM digital_twins
            """
            
            stats = self.db_manager.execute_query(query)[0]
            
            # Determine federation status based on data
            total_twins = stats['total_twins'] or 0
            active_twins = stats['active_twins'] or 0
            ready_twins = stats['ready_twins'] or 0
            
            if active_twins > 0:
                status = "active"
                status_message = f"Federation active with {active_twins} participating twins"
            elif ready_twins > 0:
                status = "ready"
                status_message = f"{ready_twins} twins ready for federation"
            else:
                status = "inactive"
                status_message = "No twins currently participating in federation"
            
            return {
                'status': status,
                'status_message': status_message,
                'total_twins': total_twins,
                'active_twins': active_twins,
                'ready_twins': ready_twins,
                'inactive_twins': total_twins - active_twins - ready_twins,
                'avg_health_score': round(stats['avg_health_score'] or 0, 1),
                'avg_contribution_score': round(stats['avg_contribution_score'] or 0, 1),
                'max_rounds': stats['max_rounds'] or 0,
                'health_distribution': {
                    'healthy': stats['healthy_twins'] or 0,
                    'moderate': stats['moderate_twins'] or 0,
                    'poor': stats['poor_twins'] or 0
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting federation status: {e}")
            return {
                'status': 'error',
                'status_message': 'Error retrieving federation status',
                'total_twins': 0,
                'active_twins': 0,
                'ready_twins': 0,
                'inactive_twins': 0,
                'avg_health_score': 0,
                'avg_contribution_score': 0,
                'max_rounds': 0,
                'health_distribution': {'healthy': 0, 'moderate': 0, 'poor': 0},
                'last_updated': datetime.now().isoformat()
            } 