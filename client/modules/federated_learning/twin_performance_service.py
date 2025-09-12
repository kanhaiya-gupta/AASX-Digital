"""
Twin Performance Service
========================

Handles twin performance analysis and metrics using shared services and database.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Import shared services and database managers (following twin_registry pattern)
from src.modules.federated_learning.core.federated_learning_service import FederatedLearningService
# Migrated to new twin registry system
from src.modules.twin_registry.core.twin_registry_service import TwinRegistryService as CoreTwinRegistryService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager

logger = logging.getLogger(__name__)

class TwinPerformanceService:
    """Service for managing twin performance analysis and metrics"""
    
    def __init__(self, db_manager: BaseDatabaseManager, twin_registry_service: CoreTwinRegistryService, federated_learning_service: FederatedLearningService):
        """Initialize the twin performance service"""
        self.db_manager = db_manager
        # Migrated to new twin registry system
        self.twin_registry_service = twin_registry_service
        self.federated_learning_service = federated_learning_service
        logger.info("✅ Twin Performance Service initialized successfully")
    
    def get_twin_performance(self):
        """Get twin performance metrics from database"""
        try:
            # Get all digital twins from database
            query = """
                SELECT 
                    twin_id,
                    twin_name,
                    health_score,
                    federated_participation_status,
                    federated_contribution_score,
                    federated_round_number,
                    federated_health_status,
                    federated_last_sync,
                    data_privacy_level,
                    differential_privacy_epsilon,
                    secure_aggregation_enabled,
                    created_at,
                    updated_at
                FROM digital_twins
                ORDER BY twin_name
            """
            
            twins_data = self.db_manager.execute_query(query)
            
            # Convert to list format expected by frontend
            twins_list = []
            for twin in twins_data:
                twins_list.append({
                    'twin_id': twin['twin_id'],
                    'twin_name': twin['twin_name'],
                    'health_score': twin['health_score'] or 0,
                    'federated_status': twin['federated_participation_status'] or 'inactive',
                    'contribution_score': twin['federated_contribution_score'] or 0,
                    'round_number': twin['federated_round_number'] or 0,
                    'federated_health': twin['federated_health_status'] or 'unknown',
                    'last_sync': twin['federated_last_sync'],
                    'data_quality': 85.0,  # Default data quality
                    'twin_type': 'industrial_process',  # Extract from name or default
                    'data_privacy_level': twin['data_privacy_level'] or 'private',
                    'differential_privacy_epsilon': twin['differential_privacy_epsilon'] or 1.0,
                    'secure_aggregation_enabled': twin['secure_aggregation_enabled'] or True
                })
            
            return {
                'twins': twins_list,
                'total_twins': len(twins_list),
                'active_twins': len([t for t in twins_list if t['federated_status'] == 'active']),
                'ready_twins': len([t for t in twins_list if t['federated_status'] == 'ready']),
                'inactive_twins': len([t for t in twins_list if t['federated_status'] == 'inactive'])
            }
            
        except Exception as e:
            logger.error(f"Error getting twin performance: {e}")
            return {
                'twins': [],
                'total_twins': 0,
                'active_twins': 0,
                'ready_twins': 0,
                'inactive_twins': 0
            } 