"""
Federated Learning Service
==========================

Core federated learning service - moved from shared.
Standard federated learning service using FedAvg pattern for digital twins.
Implements privacy-preserving collaborative learning across organizations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

from src.engine.services.core_system import RegistryService, MetricsService
from pydantic import BaseModel
from src.engine.models.base_model import EngineBaseModel

logger = logging.getLogger(__name__)

class FederatedLearningService:
    """Core federated learning service - moved from shared"""
    
    def __init__(self, connection_manager, registry_service: RegistryService, metrics_service: MetricsService):
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.logger = logger
    
    # Standard Federated Learning Methods
    
    async def register_federated_node(self, twin_id: str, node_id: str) -> bool:
        """Register a twin as a federated learning node."""
        try:
            # Get twin from database using ConnectionManager
            twin_query = "SELECT * FROM twin_registry WHERE twin_id = ?"
            twin = await self.connection_manager.fetch_one(twin_query, (twin_id,))
            
            if not twin:
                self._raise_business_error(f"Digital twin {twin_id} not found")
            
            # Validate twin is ready for federated learning
            if twin.get('status') != "active":
                self._raise_business_error(f"Twin {twin_id} must be active to participate in federated learning")
            
            if twin.get('health_score', 0) < 70:
                self._raise_business_error(f"Twin {twin_id} health score too low for federated learning")
            
            # Update federated node information in twin_registry
            update_data = {
                "federated_node_id": node_id,
                "federated_participation_status": "active",
                "federated_health_status": "healthy",
                "federated_contribution_score": 0,
                "federated_round_number": 0
            }
            
            # Build update query
            set_clauses = ", ".join([f"{key} = ?" for key in update_data.keys()])
            update_query = f"UPDATE twin_registry SET {set_clauses} WHERE twin_id = ?"
            update_values = list(update_data.values()) + [twin_id]
            
            success = await self.connection_manager.execute_query(update_query, tuple(update_values))
            if success:
                self.logger.info(f"Registered twin {twin_id} as federated node {node_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error registering federated node: {str(e)}")
            return False
    
    def update_federated_participation(self, twin_id: str, status: str) -> bool:
        """Update federated participation status."""
        try:
            valid_statuses = ["active", "inactive", "excluded"]
            if status not in valid_statuses:
                self._raise_business_error(f"Invalid federated status. Must be one of: {valid_statuses}")
            
            twin = self.registry_service.get_by_id(twin_id)
            if not twin:
                self._raise_business_error(f"Digital twin {twin_id} not found")
            
            update_data = {
                "federated_participation_status": status,
                "federated_last_sync": self._get_current_timestamp()
            }
            
            success = self.registry_service.update(twin_id, update_data)
            if success:
                self.logger.info(f"Updated twin {twin_id} federated participation to {status}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating federated participation: {str(e)}")
            return False
    
    async def get_federated_ready_twins(self, privacy_level: str = "public") -> List[Dict[str, Any]]:
        """Get twins ready for federated learning."""
        try:
            # Query twins from database using ConnectionManager
            query = """
                SELECT * FROM twin_registry 
                WHERE status = 'active' 
                AND federated_participation_status = 'active'
                AND health_score >= 70
                AND data_privacy_level = ?
                AND extracted_data_path IS NOT NULL
                AND physics_context IS NOT NULL
            """
            
            all_twins = await self.connection_manager.fetch_all(query, (privacy_level,))
            
            ready_twins = []
            for twin in all_twins:
                if twin.get('extracted_data_path') and twin.get('physics_context'):
                    ready_twins.append(twin)
            
            self.logger.info(f"Found {len(ready_twins)} twins ready for federated learning (privacy: {privacy_level})")
            return ready_twins
            
        except Exception as e:
            self.logger.error(f"Error getting federated ready twins: {str(e)}")
            return []
    
    def calculate_federated_contribution(self, twin_id: str) -> int:
        """Calculate twin's contribution score for federated learning."""
        try:
            twin = self.registry_service.get_by_id(twin_id)
            if not twin:
                self._raise_business_error(f"Digital twin {twin_id} not found")
            
            contribution_score = 0
            
            # Data quality contribution (0-40 points)
            if twin.extracted_data_path:
                contribution_score += 20
            if twin.physics_context:
                contribution_score += 20
            
            # Health contribution (0-30 points)
            health_contribution = min(twin.health_score // 3, 30)
            contribution_score += health_contribution
            
            # Participation contribution (0-20 points)
            if twin.federated_participation_status == "active":
                contribution_score += 20
            
            # Privacy compliance contribution (0-10 points)
            if twin.secure_aggregation_enabled:
                contribution_score += 10
            
            # Update the contribution score
            update_data = {"federated_contribution_score": contribution_score}
            self.registry_service.update(twin_id, update_data)
            
            self.logger.info(f"Calculated federated contribution score for twin {twin_id}: {contribution_score}")
            return contribution_score
            
        except Exception as e:
            self.logger.error(f"Error calculating federated contribution: {str(e)}")
            return 0
    
    def perform_federated_health_check(self, twin_id: str) -> Dict[str, Any]:
        """Perform federated-specific health checks."""
        try:
            twin = self.registry_service.get_by_id(twin_id)
            if not twin:
                return {"status": "error", "message": "Twin not found"}
            
            # Perform federated-specific health checks
            federated_checks = {
                "federated_participation": self._check_federated_participation(twin),
                "data_quality_for_federated": self._check_data_quality_for_federated(twin),
                "privacy_compliance": self._check_privacy_compliance(twin),
                "model_synchronization": self._check_model_synchronization(twin)
            }
            
            # Calculate federated health score
            federated_health_score = self._calculate_federated_health_score(federated_checks)
            federated_health_status = self._determine_federated_health_status(federated_health_score)
            
            # Update twin federated health
            update_data = {
                "federated_health_status": federated_health_status,
                "federated_last_sync": self._get_current_timestamp()
            }
            self.registry_service.update(twin_id, update_data)
            
            return {
                "twin_id": twin_id,
                "federated_health_status": federated_health_status,
                "federated_health_score": federated_health_score,
                "checks": federated_checks,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error performing federated health check: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # Standard FedAvg Implementation
    
    def federated_averaging_step(self, twin_ids: List[str]) -> Dict[str, Any]:
        """Perform one step of federated averaging."""
        try:
            if not twin_ids:
                self._raise_business_error("No twin IDs provided for federated averaging")
            
            # Get participating twins
            participating_twins = []
            for twin_id in twin_ids:
                twin = self.registry_service.get_by_id(twin_id)
                if twin and twin.federated_participation_status == "active":
                    participating_twins.append(twin)
            
            if not participating_twins:
                self._raise_business_error("No active twins found for federated averaging")
            
            # Simulate local training on each twin
            local_models = []
            for twin in participating_twins:
                local_model = self._train_local_model(twin)
                local_models.append(local_model)
            
            # Perform federated averaging
            global_model = self._aggregate_models(local_models)
            
            # Update federated round number for all participating twins
            for twin in participating_twins:
                update_data = {
                    "federated_round_number": twin.federated_round_number + 1,
                    "federated_last_sync": self._get_current_timestamp()
                }
                self.registry_service.update(twin.twin_id, update_data)
            
            self.logger.info(f"Completed federated averaging step with {len(participating_twins)} twins")
            
            return {
                "status": "success",
                "participating_twins": len(participating_twins),
                "global_model": global_model,
                "round_number": participating_twins[0].federated_round_number + 1 if participating_twins else 0,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error in federated averaging step: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def update_federated_model_version(self, twin_id: str, version: str) -> bool:
        """Update federated model version."""
        try:
            twin = self.registry_service.get_by_id(twin_id)
            if not twin:
                self._raise_business_error(f"Digital twin {twin_id} not found")
            
            update_data = {
                "federated_model_version": version,
                "federated_last_sync": self._get_current_timestamp()
            }
            
            success = self.registry_service.update(twin_id, update_data)
            if success:
                self.logger.info(f"Updated federated model version for twin {twin_id}: {version}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating federated model version: {str(e)}")
            return False
    
    # Helper Methods
    
    def _check_federated_participation(self, twin: BaseModel) -> Dict[str, Any]:
        """Check federated participation status."""
        return {
            "status": "pass" if twin.federated_participation_status == "active" else "fail",
            "message": f"Federated participation: {twin.federated_participation_status}",
            "score": 100 if twin.federated_participation_status == "active" else 0
        }
    
    def _check_data_quality_for_federated(self, twin: BaseModel) -> Dict[str, Any]:
        """Check data quality for federated learning."""
        score = 0
        message = "Data quality check"
        
        if twin.extracted_data_path:
            score += 50
            message += ": extracted data available"
        
        if twin.physics_context:
            score += 50
            message += ": physics context available"
        
        return {
            "status": "pass" if score >= 80 else "fail",
            "message": message,
            "score": score
        }
    
    def _check_privacy_compliance(self, twin: BaseModel) -> Dict[str, Any]:
        """Check privacy compliance for federated learning."""
        score = 0
        message = "Privacy compliance check"
        
        if twin.secure_aggregation_enabled:
            score += 50
            message += ": secure aggregation enabled"
        
        if twin.differential_privacy_epsilon > 0:
            score += 50
            message += ": differential privacy configured"
        
        return {
            "status": "pass" if score >= 80 else "fail",
            "message": message,
            "score": score
        }
    
    def _check_model_synchronization(self, twin: BaseModel) -> Dict[str, Any]:
        """Check model synchronization status."""
        if not twin.federated_model_version:
            return {
                "status": "fail",
                "message": "No federated model version set",
                "score": 0
            }
        
        return {
            "status": "pass",
            "message": f"Model version: {twin.federated_model_version}",
            "score": 100
        }
    
    def _calculate_federated_health_score(self, federated_checks: Dict[str, Any]) -> int:
        """Calculate federated health score from individual checks."""
        total_score = 0
        check_count = 0
        
        for check_name, check_result in federated_checks.items():
            if isinstance(check_result, dict) and "score" in check_result:
                total_score += check_result["score"]
                check_count += 1
        
        return total_score // check_count if check_count > 0 else 0
    
    def _determine_federated_health_status(self, federated_health_score: int) -> str:
        """Determine federated health status based on score."""
        if federated_health_score >= 80:
            return "healthy"
        elif federated_health_score >= 50:
            return "warning"
        else:
            return "critical"
    
    def _train_local_model(self, twin: BaseModel) -> Dict[str, Any]:
        """Simulate local model training on twin data."""
        # This is a simplified simulation - in real implementation, this would train actual models
        return {
            "twin_id": twin.twin_id,
            "model_parameters": {
                "weights": [0.1, 0.2, 0.3],  # Simplified model weights
                "bias": 0.05
            },
            "training_metrics": {
                "loss": 0.1,
                "accuracy": 0.85
            },
            "data_size": 1000  # Simulated data size
        }
    
    def _aggregate_models(self, local_models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate local models using weighted averaging (FedAvg)."""
        if not local_models:
            return {}
        
        # Simple weighted averaging of model parameters
        aggregated_weights = [0.0, 0.0, 0.0]
        aggregated_bias = 0.0
        total_weight = 0
        
        for model in local_models:
            weight = model.get("data_size", 1)
            total_weight += weight
            
            # Aggregate weights
            for i, w in enumerate(model["model_parameters"]["weights"]):
                aggregated_weights[i] += w * weight
            
            # Aggregate bias
            aggregated_bias += model["model_parameters"]["bias"] * weight
        
        # Normalize by total weight
        if total_weight > 0:
            aggregated_weights = [w / total_weight for w in aggregated_weights]
            aggregated_bias /= total_weight
        
        return {
            "model_parameters": {
                "weights": aggregated_weights,
                "bias": aggregated_bias
            },
            "aggregation_metadata": {
                "num_models": len(local_models),
                "total_data_size": total_weight,
                "aggregation_method": "weighted_average"
            }
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def _raise_business_error(self, message: str) -> None:
        """Raise a business logic error."""
        self.logger.error(f"Business Logic Error: {message}")
        raise ValueError(f"Business Logic Error: {message}") 