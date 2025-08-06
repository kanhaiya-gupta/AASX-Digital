"""
Validation Service

Handles business logic for physics model validation and verification.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

# Import the physics modeling framework
try:
    from src.physics_modeling import DynamicPhysicsModelingFramework
    from src.physics_modeling.core.dynamic_types import PhysicsPlugin
    from src.physics_modeling.core.plugin_manager import PluginManager
    from src.physics_modeling.core.model_factory import ModelFactory
    from src.physics_modeling.simulation.simulation_engine import SimulationEngine
except ImportError as e:
    logging.warning(f"Physics Modeling modules not available: {e}")
    DynamicPhysicsModelingFramework = None
    PhysicsPlugin = None
    PluginManager = None
    ModelFactory = None
    SimulationEngine = None

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating physics models"""
    
    def __init__(self):
        self.physics_framework = None
        self.validation_history = {}  # In-memory storage for validation results
        self._initialize_framework()
    
    def _initialize_framework(self):
        """Initialize the physics modeling framework"""
        if DynamicPhysicsModelingFramework is None:
            logger.error("Physics Modeling Framework not available")
            return
            
        try:
            self.physics_framework = DynamicPhysicsModelingFramework()
            logger.info("Physics Modeling Framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Physics Modeling Framework: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize Physics Modeling Framework"
            )
    
    def validate_model(self, model_id: str, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a physics model against experimental or reference data
        
        Args:
            model_id: ID of the physics model to validate
            validation_data: Experimental or reference data for validation
            
        Returns:
            Validation results with accuracy metrics
        """
        if not self.physics_framework:
            # Return a mock validation result when framework is not available
            validation_id = str(uuid.uuid4())
            return {
                "validation_id": validation_id,
                "model_id": model_id,
                "accuracy_score": 0.0,
                "validation_metrics": {"error": "Physics framework not available"},
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # Generate unique validation ID
            validation_id = str(uuid.uuid4())
            
            # Validate model exists
            model = self.physics_framework.get_model(model_id)
            if not model:
                raise HTTPException(
                    status_code=404,
                    detail=f"Physics model {model_id} not found"
                )
            
            # Perform validation using the framework
            validation_results = self.physics_framework.validate_model(
                model_id=model_id,
                validation_data=validation_data
            )
            
            # Calculate accuracy score
            accuracy_score = self._calculate_accuracy_score(validation_results)
            
            # Store validation results
            validation_record = {
                "validation_id": validation_id,
                "model_id": model_id,
                "accuracy_score": accuracy_score,
                "validation_metrics": validation_results,
                "validation_data": validation_data,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.validation_history[validation_id] = validation_record
            
            # Update model validation status
            self._update_model_validation_status(model_id, accuracy_score)
            
            return {
                "validation_id": validation_id,
                "model_id": model_id,
                "accuracy_score": accuracy_score,
                "validation_metrics": validation_results,
                "status": "completed",
                "timestamp": validation_record["timestamp"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to validate model {model_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate model: {str(e)}"
            )
    
    def _calculate_accuracy_score(self, validation_results: Dict[str, Any]) -> float:
        """
        Calculate overall accuracy score from validation metrics
        
        Args:
            validation_results: Validation metrics from framework
            
        Returns:
            Overall accuracy score (0.0 to 1.0)
        """
        try:
            # Extract key metrics
            metrics = validation_results.get("metrics", {})
            
            # Calculate weighted average of different accuracy measures
            scores = []
            weights = []
            
            # R-squared score (if available)
            if "r_squared" in metrics:
                scores.append(metrics["r_squared"])
                weights.append(0.4)
            
            # Mean absolute error (normalized)
            if "mae" in metrics and "data_range" in metrics:
                normalized_mae = 1.0 - (metrics["mae"] / metrics["data_range"])
                scores.append(max(0.0, normalized_mae))
                weights.append(0.3)
            
            # Root mean square error (normalized)
            if "rmse" in metrics and "data_range" in metrics:
                normalized_rmse = 1.0 - (metrics["rmse"] / metrics["data_range"])
                scores.append(max(0.0, normalized_rmse))
                weights.append(0.3)
            
            # Calculate weighted average
            if scores and weights:
                total_weight = sum(weights)
                weighted_score = sum(score * weight for score, weight in zip(scores, weights))
                return weighted_score / total_weight
            else:
                # Fallback to simple average if no specific metrics
                all_scores = [v for v in metrics.values() if isinstance(v, (int, float)) and 0 <= v <= 1]
                return sum(all_scores) / len(all_scores) if all_scores else 0.5
                
        except Exception as e:
            logger.warning(f"Failed to calculate accuracy score: {e}")
            return 0.5  # Default score
    
    def _update_model_validation_status(self, model_id: str, accuracy_score: float):
        """Update model validation status in the framework"""
        try:
            if self.physics_framework:
                validation_status = "validated" if accuracy_score >= 0.8 else "needs_improvement"
                self.physics_framework.update_model_validation_status(
                    model_id, validation_status, accuracy_score
                )
        except Exception as e:
            logger.warning(f"Failed to update model validation status: {e}")
    
    def get_validation_results(self, validation_id: str) -> Dict[str, Any]:
        """
        Get detailed validation results
        
        Args:
            validation_id: ID of the validation run
            
        Returns:
            Detailed validation results
        """
        if validation_id not in self.validation_history:
            raise HTTPException(
                status_code=404,
                detail=f"Validation {validation_id} not found"
            )
        
        return self.validation_history[validation_id]
    
    def compare_models(self, model_ids: List[str], comparison_metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare multiple physics models
        
        Args:
            model_ids: List of model IDs to compare
            comparison_metrics: List of metrics to compare (optional)
            
        Returns:
            Model comparison results
        """
        if not self.physics_framework:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available"
            )
        
        if len(model_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 models required for comparison"
            )
        
        try:
            # Get models
            models = []
            for model_id in model_ids:
                model = self.physics_framework.get_model(model_id)
                if not model:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Physics model {model_id} not found"
                    )
                models.append(model)
            
            # Perform comparison using framework
            comparison_results = self.physics_framework.compare_models(
                model_ids=model_ids,
                metrics=comparison_metrics
            )
            
            # Add model metadata to results
            comparison_results["models"] = [
                {
                    "model_id": model.model_id,
                    "twin_id": model.twin_id,
                    "model_type": model.model_type,
                    "status": model.status,
                    "validation_status": getattr(model, 'validation_status', 'unknown')
                }
                for model in models
            ]
            
            return comparison_results
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to compare models: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to compare models: {str(e)}"
            )
    
    def generate_validation_report(self, model_id: str, validation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive validation report
        
        Args:
            model_id: ID of the physics model
            validation_id: Optional specific validation ID
            
        Returns:
            Comprehensive validation report
        """
        if not self.physics_framework:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available"
            )
        
        try:
            # Get model details
            model = self.physics_framework.get_model(model_id)
            if not model:
                raise HTTPException(
                    status_code=404,
                    detail=f"Physics model {model_id} not found"
                )
            
            # Get validation history for this model
            model_validations = [
                v for v in self.validation_history.values()
                if v["model_id"] == model_id
            ]
            
            if validation_id:
                # Get specific validation
                specific_validation = next(
                    (v for v in model_validations if v["validation_id"] == validation_id),
                    None
                )
                if not specific_validation:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Validation {validation_id} not found for model {model_id}"
                    )
                validations_to_include = [specific_validation]
            else:
                # Get all validations
                validations_to_include = model_validations
            
            # Generate report
            report = {
                "model_info": {
                    "model_id": model_id,
                    "twin_id": model.twin_id,
                    "model_type": model.model_type,
                    "status": model.status,
                    "validation_status": getattr(model, 'validation_status', 'unknown'),
                    "created_at": model.created_at.isoformat() if model.created_at else None
                },
                "validation_summary": {
                    "total_validations": len(model_validations),
                    "latest_accuracy": max([v["accuracy_score"] for v in model_validations]) if model_validations else 0.0,
                    "average_accuracy": sum([v["accuracy_score"] for v in model_validations]) / len(model_validations) if model_validations else 0.0,
                    "validation_trend": self._calculate_validation_trend(model_validations)
                },
                "validation_details": validations_to_include,
                "recommendations": self._generate_validation_recommendations(model_validations),
                "report_generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to generate validation report for model {model_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate validation report: {str(e)}"
            )
    
    def _calculate_validation_trend(self, validations: List[Dict[str, Any]]) -> str:
        """Calculate validation accuracy trend"""
        if len(validations) < 2:
            return "insufficient_data"
        
        # Sort by timestamp
        sorted_validations = sorted(validations, key=lambda x: x["timestamp"])
        scores = [v["accuracy_score"] for v in sorted_validations]
        
        # Calculate trend
        if len(scores) >= 2:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            if avg_second > avg_first + 0.05:
                return "improving"
            elif avg_second < avg_first - 0.05:
                return "declining"
            else:
                return "stable"
        
        return "insufficient_data"
    
    def _generate_validation_recommendations(self, validations: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on validation history"""
        recommendations = []
        
        if not validations:
            recommendations.append("No validation data available. Run initial validation to assess model accuracy.")
            return recommendations
        
        # Get latest validation
        latest_validation = max(validations, key=lambda x: x["timestamp"])
        accuracy_score = latest_validation["accuracy_score"]
        
        if accuracy_score < 0.6:
            recommendations.append("Model accuracy is low. Consider reviewing model parameters and assumptions.")
            recommendations.append("Check input data quality and boundary conditions.")
        elif accuracy_score < 0.8:
            recommendations.append("Model accuracy is acceptable but could be improved.")
            recommendations.append("Consider fine-tuning model parameters or adding more training data.")
        else:
            recommendations.append("Model accuracy is good. Continue monitoring for consistency.")
        
        # Check for consistency
        if len(validations) > 1:
            scores = [v["accuracy_score"] for v in validations]
            score_variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
            
            if score_variance > 0.1:
                recommendations.append("Validation results show high variance. Investigate model stability.")
        
        return recommendations
    
    def list_validations(self, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List validation runs with optional filtering
        
        Args:
            model_id: Optional model ID to filter by
            
        Returns:
            List of validation summaries
        """
        validations = []
        
        for validation_id, validation in self.validation_history.items():
            if model_id and validation["model_id"] != model_id:
                continue
            
            validations.append({
                "validation_id": validation_id,
                "model_id": validation["model_id"],
                "accuracy_score": validation["accuracy_score"],
                "status": validation["status"],
                "timestamp": validation["timestamp"]
            })
        
        # Sort by timestamp (newest first)
        validations.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return validations 