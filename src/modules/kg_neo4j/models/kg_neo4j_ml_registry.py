"""
Knowledge Graph Neo4j ML Registry Model

Comprehensive ML registry model for knowledge graph ML training and model management.
Supports ML model training, deployment, and performance tracking with enterprise-grade features.
Enhanced with computed fields and business intelligence methods.
"""

from src.engine.models.engine_base_model import EngineBaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import Field, ConfigDict, computed_field
import uuid
import asyncio


class KGNeo4jMLRegistry(EngineBaseModel):
    """
    ML registry model for knowledge graph ML training and model management.
    
    This model represents the kg_neo4j_ml_registry table with all fields from the database schema.
    Supports ML model training, deployment, performance tracking, and enterprise-grade features.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Primary Identification
    ml_registry_id: str = Field(..., description="Unique ML registry identifier")
    graph_id: str = Field(..., description="Reference to kg_graph_registry")
    model_id: str = Field(..., description="Unique model identifier")
    session_id: str = Field(..., description="Training session identifier")
    
    # Model Metadata (NO raw data - only metadata)
    model_name: str = Field(..., description="Human-readable model name")
    model_type: str = Field(..., description="Model type: node_classification, link_prediction, community_detection, anomaly_detection, graph_embedding, gnn, hybrid")
    model_version: str = Field(default="1.0.0", description="Model version")
    model_architecture: Optional[str] = Field(default=None, description="Model architecture description")
    model_framework: Optional[str] = Field(default=None, description="ML framework used (PyTorch, TensorFlow, etc.)")
    
    # Training Session Metadata (NO raw data - only metadata)
    training_status: str = Field(default="pending", description="Training status: pending, in_progress, completed, failed, cancelled, paused")
    training_type: str = Field(default="supervised", description="Training type: supervised, unsupervised, semi_supervised, reinforcement, transfer")
    training_algorithm: Optional[str] = Field(default=None, description="Training algorithm used")
    training_parameters: Dict[str, Any] = Field(default={}, description="JSON: hyperparameters, learning rate, etc.")
    
    # External Storage References (NO data storage - only file paths)
    model_file_path: Optional[str] = Field(default=None, description="Path to trained model file (external storage)")
    config_file_path: Optional[str] = Field(default=None, description="Path to training configuration (external storage)")
    dataset_path: Optional[str] = Field(default=None, description="Path to training dataset (external storage)")
    logs_path: Optional[str] = Field(default=None, description="Path to training logs (external storage)")
    performance_logs_path: Optional[str] = Field(default=None, description="Path to performance logs (external storage)")
    deployment_config_path: Optional[str] = Field(default=None, description="Path to deployment configuration (external storage)")
    
    # Training Performance Summary (NO raw data - only summary metrics)
    final_accuracy: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Final training accuracy (0.0-1.0)")
    training_duration_seconds: Optional[int] = Field(default=None, description="Total training time in seconds")
    resource_consumption: Dict[str, Any] = Field(default={}, description="JSON: CPU, memory, GPU usage summary")
    training_efficiency_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Training efficiency score (0.0-1.0)")
    
    # Model Performance Metrics (NO raw data - only summary metrics)
    precision_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Precision score (0.0-1.0)")
    recall_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Recall score (0.0-1.0)")
    f1_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="F1 score (0.0-1.0)")
    roc_auc_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="ROC AUC score (0.0-1.0)")
    auc_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="AUC score (0.0-1.0) - legacy field")
    confusion_matrix: Optional[Dict[str, Any]] = Field(default=None, description="JSON: confusion matrix data")
    
    # Model Optimization & Deployment (NO raw data - only metadata)
    optimization_status: str = Field(default="pending", description="Optimization status: pending, in_progress, completed, failed")
    optimization_type: str = Field(default="hyperparameter_tuning", description="Type of optimization performed")
    optimization_parameters: Dict[str, Any] = Field(default={}, description="JSON: optimization parameters and results")
    last_optimization_date: Optional[datetime] = Field(default=None, description="Last optimization performed")
    optimization_effectiveness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Optimization effectiveness score (0.0-1.0)")
    performance_benchmarks: Dict[str, Any] = Field(default={}, description="JSON: performance benchmarks and comparisons")
    resource_efficiency_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Resource efficiency score (0.0-1.0)")
    scalability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Scalability score (0.0-1.0)")
    
    # Training Data Metadata (NO raw data - only metadata)
    dataset_size: Optional[int] = Field(
        default=None, 
        description="Number of training samples"
    )
    feature_count: Optional[int] = Field(
        default=None, 
        description="Number of features used"
    )
    data_quality_score: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Data quality score (0.0-1.0)"
    )
    data_split_ratio: str = Field(
        default="0.7:0.2:0.1", 
        description="Train:Validation:Test split"
    )
    
    # Model Deployment & Usage (NO raw data - only metadata)
    deployment_status: str = Field(
        default="not_deployed", 
        description="Deployment status: not_deployed, deployed, active, inactive, deprecated"
    )
    deployment_date: Optional[datetime] = Field(
        default=None, 
        description="When model was deployed"
    )
    usage_count: int = Field(
        default=0, 
        description="Number of times model was used"
    )
    last_used_at: Optional[datetime] = Field(
        default=None, 
        description="Last time model was used"
    )
    
    # Enterprise Performance Analytics (Merged from enterprise table)
    performance_trend: str = Field(
        default="stable", 
        description="Performance trend: improving, stable, declining, fluctuating"
    )
    performance_metric: str = Field(
        default="standard", 
        description="Specific performance metric identifier"
    )
    performance_value: Optional[float] = Field(
        default=None, 
        description="Actual performance value"
    )
    optimization_suggestions: Dict[str, Any] = Field(
        default={}, 
        description="JSON: AI-generated optimization recommendations"
    )
    
    # Integration References (Links to other modules - NO data duplication)
    aasx_integration_id: Optional[str] = Field(default=None, description="Reference to aasx_processing table")
    twin_registry_id: Optional[str] = Field(default=None, description="Reference to twin_registry table")
    physics_modeling_id: Optional[str] = Field(default=None, description="Reference to physics_modeling table")
    federated_learning_id: Optional[str] = Field(default=None, description="Reference to federated_learning table")
    ai_rag_id: Optional[str] = Field(default=None, description="Reference to ai_rag_registry table")
    certificate_manager_id: Optional[str] = Field(default=None, description="Reference to certificate module")
    
    # Quality & Governance (NO raw data - only metadata)
    model_quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Model quality score (0.0-1.0)")
    validation_status: str = Field(default="pending", description="Validation status: pending, validated, failed, requires_review")
    compliance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Compliance score (0.0-1.0)")
    bias_detection_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Bias detection score (0.0-1.0)")
    
    # Lifecycle Management (NO raw data - only metadata)
    lifecycle_status: str = Field(default="development", description="Lifecycle status: development, testing, production, maintenance, deprecated")
    lifecycle_phase: str = Field(default="training", description="Lifecycle phase: training, validation, deployment, monitoring, retirement")
    
    # User Management & Ownership (NO raw data - only metadata)
    user_id: str = Field(..., description="User who created/trained this model")
    org_id: str = Field(..., description="Organization this model belongs to")
    owner_team: Optional[str] = Field(default=None, description="Team responsible for this model")
    steward_user_id: Optional[str] = Field(default=None, description="Data steward for this model")
    
    # Timestamps & Audit (NO raw data - only metadata)
    created_at: datetime = Field(..., description="When the ML registry entry was created")
    updated_at: datetime = Field(..., description="When the ML registry entry was last updated")
    training_started_at: Optional[datetime] = Field(
        default=None, 
        description="When training started"
    )
    training_completed_at: Optional[datetime] = Field(
        default=None, 
        description="When training completed"
    )
    last_accessed_at: Optional[datetime] = Field(
        default=None, 
        description="Last time model was accessed"
    )
    
    # Configuration & Metadata (JSON fields for flexibility - NO raw data)
    ml_config: Dict[str, Any] = Field(
        default={}, 
        description="ML configuration settings"
    )
    model_metadata: Dict[str, Any] = Field(
        default={}, 
        description="Additional model metadata"
    )
    custom_attributes: Dict[str, Any] = Field(
        default={}, 
        description="User-defined custom attributes"
    )
    tags: List[str] = Field(default=[], description="List of tags for categorization")
    
    # Additional Enterprise Fields (Missing from schema)
    compliance_type: str = Field(default="standard", description="Type of compliance being tracked")
    security_event_type: str = Field(default="none", description="Type of security event")
    performance_metric: str = Field(default="standard", description="Specific performance metric identifier")
    
    # Time-based Analytics (Framework Time Analysis)
    hour_of_day: Optional[int] = Field(default=None, ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(default=None, ge=1, le=7, description="Day of week (1-7)")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="Month (1-12)")
    
    # Performance Trends (Framework Performance Analysis)
    graph_management_trend: Optional[float] = Field(default=None, description="Compared to historical average")
    resource_efficiency_trend: Optional[float] = Field(default=None, description="Performance over time")
    quality_trend: Optional[float] = Field(default=None, description="Quality metrics over time")

    # Computed Fields for Business Intelligence
    @computed_field
    def overall_model_score(self) -> float:
        """Calculate overall model performance score"""
        scores = []
        if self.final_accuracy is not None:
            scores.append(self.final_accuracy)
        if self.precision_score is not None:
            scores.append(self.precision_score)
        if self.recall_score is not None:
            scores.append(self.recall_score)
        if self.f1_score is not None:
            scores.append(self.f1_score)
        if self.roc_auc_score is not None:
            scores.append(self.roc_auc_score)
        if self.auc_score is not None:
            scores.append(self.auc_score)
        
        return sum(scores) / len(scores) if scores else 0.0

    @computed_field
    def training_efficiency_rating(self) -> str:
        """Rate training efficiency based on multiple factors"""
        if not self.training_efficiency_score:
            return "unknown"
        
        if self.training_efficiency_score >= 0.9:
            return "excellent"
        elif self.training_efficiency_score >= 0.7:
            return "good"
        elif self.training_efficiency_score >= 0.5:
            return "fair"
        else:
            return "poor"

    @computed_field
    def model_maturity_level(self) -> str:
        """Determine model maturity level based on lifecycle and performance"""
        if self.lifecycle_phase == "retirement":
            return "deprecated"
        elif self.lifecycle_phase == "monitoring" and self.usage_count > 100:
            return "mature"
        elif self.lifecycle_phase == "deployment" and self.deployment_status == "active":
            return "production"
        elif self.lifecycle_phase == "validation" and self.validation_status == "validated":
            return "validated"
        elif self.lifecycle_phase == "training" and self.training_status == "completed":
            return "trained"
        else:
            return "development"

    @computed_field
    def performance_health_status(self) -> str:
        """Assess overall performance health status"""
        if self.overall_model_score >= 0.9 and self.training_efficiency_score and self.training_efficiency_score >= 0.8:
            return "excellent"
        elif self.overall_model_score >= 0.7 and self.training_efficiency_score and self.training_efficiency_score >= 0.6:
            return "good"
        elif self.overall_model_score >= 0.5 and self.training_efficiency_score and self.training_efficiency_score >= 0.4:
            return "fair"
        else:
            return "poor"

    @computed_field
    def resource_utilization_score(self) -> float:
        """Calculate resource utilization efficiency score"""
        if not self.resource_consumption:
            return 0.0
        
        # Simple scoring based on resource consumption patterns
        cpu_usage = self.resource_consumption.get("cpu_usage", 0)
        memory_usage = self.resource_consumption.get("memory_usage", 0)
        gpu_usage = self.resource_consumption.get("gpu_usage", 0)
        
        # Lower usage is better for efficiency
        cpu_score = max(0, 1.0 - (cpu_usage / 100))
        memory_score = max(0, 1.0 - (memory_usage / 100))
        gpu_score = max(0, 1.0 - (gpu_usage / 100)) if gpu_usage > 0 else 1.0
        
        scores = [cpu_score, memory_score]
        if gpu_score > 0:
            scores.append(gpu_score)
        
        return sum(scores) / len(scores)

    @computed_field
    def deployment_readiness_score(self) -> float:
        """Calculate deployment readiness score"""
        readiness_factors = []
        
        if self.training_status == "completed":
            readiness_factors.append(0.3)
        if self.validation_status == "validated":
            readiness_factors.append(0.3)
        if self.overall_model_score and self.overall_model_score >= 0.7:
            readiness_factors.append(0.2)
        if self.model_quality_score and self.model_quality_score >= 0.7:
            readiness_factors.append(0.2)
        
        return sum(readiness_factors) if readiness_factors else 0.0

    @computed_field
    def bias_risk_assessment(self) -> str:
        """Assess bias risk based on bias detection and data quality"""
        if self.bias_detection_score is None:
            return "unknown"
        
        if self.bias_detection_score >= 0.9:
            return "low"
        elif self.bias_detection_score >= 0.7:
            return "medium"
        elif self.bias_detection_score >= 0.5:
            return "high"
        else:
            return "critical"

    @computed_field
    def optimization_priority(self) -> str:
        """Determine optimization priority based on performance and efficiency"""
        if self.overall_model_score and self.overall_model_score < 0.5:
            return "critical"
        elif self.training_efficiency_score and self.training_efficiency_score < 0.5:
            return "high"
        elif self.model_quality_score and self.model_quality_score < 0.7:
            return "medium"
        else:
            return "low"

    @computed_field
    def maintenance_schedule(self) -> str:
        """Determine maintenance schedule based on model health and usage"""
        if self.performance_health_status == "poor" or self.bias_risk_assessment == "critical":
            return "immediate"
        elif self.performance_health_status == "fair" or self.bias_risk_assessment == "high":
            return "scheduled"
        else:
            return "routine"

    @computed_field
    def enterprise_compliance_score(self) -> float:
        """Calculate enterprise compliance score"""
        compliance_factors = []
        
        if self.compliance_score:
            compliance_factors.append(self.compliance_score * 0.4)
        if self.model_quality_score:
            compliance_factors.append(self.model_quality_score * 0.3)
        if self.bias_detection_score:
            compliance_factors.append(self.bias_detection_score * 0.3)
        
        return sum(compliance_factors) if compliance_factors else 0.0

    def __init__(self, **data):
        # Generate ml_registry_id if not provided
        if 'ml_registry_id' not in data:
            data['ml_registry_id'] = f"ml_{uuid.uuid4().hex[:8]}"
        
        # Set timestamps if not provided
        if 'created_at' not in data:
            data['created_at'] = datetime.now(timezone.utc)
        if 'updated_at' not in data:
            data['updated_at'] = datetime.now(timezone.utc)
        
        super().__init__(**data)
    
    # Asynchronous Enterprise Methods for Business Intelligence
    async def update_training_status(self, new_status: str) -> None:
        """Update training status asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        self.training_status = new_status
        self.updated_at = datetime.now(timezone.utc)
        
        if new_status == "completed":
            self.training_completed_at = datetime.now(timezone.utc)

    async def update_performance_metrics(self, accuracy: float, precision: float, recall: float, f1: float, auc: float) -> None:
        """Update model performance metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        self.final_accuracy = accuracy
        self.precision_score = precision
        self.recall_score = recall
        self.f1_score = f1
        self.roc_auc_score = auc
        self.auc_score = auc  # Set both for compatibility
        self.updated_at = datetime.now(timezone.utc)

    async def update_deployment_status(self, status: str) -> None:
        """Update deployment status asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        self.deployment_status = status
        if status == "deployed":
            self.deployment_date = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    async def increment_usage_count(self) -> None:
        """Increment model usage count asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        self.usage_count += 1
        self.last_used_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    async def update_resource_consumption(self, cpu: float, memory: float, gpu: float = None) -> None:
        """Update resource consumption metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        self.resource_consumption = {
            "cpu_usage": cpu,
            "memory_usage": memory,
            "gpu_usage": gpu
        }
        self.updated_at = datetime.now(timezone.utc)

    async def calculate_training_efficiency(self) -> float:
        """Calculate training efficiency score asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        
        if not self.training_duration_seconds or not self.dataset_size:
            return 0.0
        
        # Simple efficiency calculation based on time and dataset size
        base_efficiency = min(1.0, 1000 / self.training_duration_seconds)
        data_efficiency = min(1.0, self.dataset_size / 10000)
        
        efficiency_score = (base_efficiency + data_efficiency) / 2
        self.training_efficiency_score = efficiency_score
        self.updated_at = datetime.now(timezone.utc)
        
        return efficiency_score

    async def generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        recommendations = []
        
        if self.overall_model_score and self.overall_model_score < 0.7:
            recommendations.append("Consider hyperparameter tuning to improve model performance")
        if self.training_efficiency_score and self.training_efficiency_score < 0.6:
            recommendations.append("Optimize training process and resource allocation")
        if self.bias_detection_score and self.bias_detection_score < 0.8:
            recommendations.append("Review training data for potential bias and implement bias mitigation")
        if self.model_quality_score and self.model_quality_score < 0.7:
            recommendations.append("Enhance model validation and quality assurance processes")
        
        return recommendations

    async def get_model_analytics(self) -> Dict[str, Any]:
        """Get comprehensive model analytics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "overall_score": self.overall_model_score,
            "performance_health": self.performance_health_status,
            "model_maturity": self.model_maturity_level,
            "training_efficiency": self.training_efficiency_rating,
            "deployment_readiness": self.deployment_readiness_score,
            "bias_risk": self.bias_risk_assessment,
            "optimization_priority": self.optimization_priority,
            "maintenance_schedule": self.maintenance_schedule,
            "enterprise_compliance": self.enterprise_compliance_score,
            "performance_metrics": {
                "accuracy": self.final_accuracy,
                "precision": self.precision_score,
                "recall": self.recall_score,
                "f1_score": self.f1_score,
                "auc_score": self.roc_auc_score,
                "roc_auc_score": self.roc_auc_score
            },
            "training_metrics": {
                "status": self.training_status,
                "type": self.training_type,
                "duration": self.training_duration_seconds,
                "efficiency": self.training_efficiency_score,
                "dataset_size": self.dataset_size
            },
            "deployment_metrics": {
                "status": self.deployment_status,
                "usage_count": self.usage_count,
                "last_used": self.last_used_at.isoformat() if self.last_used_at else None
            },
            "quality_metrics": {
                "model_quality": self.model_quality_score,
                "data_quality": self.data_quality_score,
                "validation_status": self.validation_status,
                "compliance_score": self.compliance_score
            }
        }

    # ========================================================================
    # ADDITIONAL ASYNC METHODS (Matching Certificate Manager)
    # ========================================================================
    
    async def validate_integrity(self) -> bool:
        """Validate ML registry data integrity"""
        try:
            # Validate required fields
            if not all([self.ml_registry_id, self.graph_id, self.model_id, self.session_id, self.user_id, self.org_id]):
                return False
            
            # Validate business rules
            if self.final_accuracy is not None and (self.final_accuracy < 0.0 or self.final_accuracy > 1.0):
                return False
            
            if self.precision_score is not None and (self.precision_score < 0.0 or self.precision_score > 1.0):
                return False
            
            if self.recall_score is not None and (self.recall_score < 0.0 or self.recall_score > 1.0):
                return False
            
            if self.f1_score is not None and (self.f1_score < 0.0 or self.f1_score > 1.0):
                return False
            
            if self.roc_auc_score is not None and (self.roc_auc_score < 0.0 or self.roc_auc_score > 1.0):
                return False
            
            if self.auc_score is not None and (self.auc_score < 0.0 or self.auc_score > 1.0):
                return False
            
            if self.training_efficiency_score is not None and (self.training_efficiency_score < 0.0 or self.training_efficiency_score > 1.0):
                return False
            
            return True
            
        except Exception as e:
            return False
    
    async def update_health_metrics(self) -> None:
        """Update health metrics based on current state"""
        try:
            # Update performance health status
            if self.overall_model_score and self.overall_model_score >= 0.9:
                self.performance_trend = "improving"
            elif self.overall_model_score and self.overall_model_score >= 0.7:
                self.performance_trend = "stable"
            else:
                self.performance_trend = "declining"
            
            # Update lifecycle status based on training and deployment
            if self.training_status == "completed" and self.deployment_status == "active":
                self.lifecycle_status = "production"
            elif self.training_status == "completed" and self.validation_status == "validated":
                self.lifecycle_status = "testing"
            elif self.training_status == "in_progress":
                self.lifecycle_status = "development"
            
            self.updated_at = datetime.now(timezone.utc)
            
        except Exception as e:
            pass
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive ML model summary"""
        try:
            await self.update_health_metrics()
            
            summary = {
                "ml_registry_id": self.ml_registry_id,
                "model_id": self.model_id,
                "model_name": self.model_name,
                "model_type": self.model_type,
                "overall_score": self.overall_model_score,
                "performance_health": self.performance_health_status,
                "model_maturity": self.model_maturity_level,
                "training_efficiency": self.training_efficiency_rating,
                "deployment_readiness": self.deployment_readiness_score,
                "bias_risk": self.bias_risk_assessment,
                "optimization_priority": self.optimization_priority,
                "maintenance_schedule": self.maintenance_schedule,
                "training_status": {
                    "status": self.training_status,
                    "type": self.training_type,
                    "duration": self.training_duration_seconds,
                    "efficiency": self.training_efficiency_score
                },
                "performance_metrics": {
                    "accuracy": self.final_accuracy,
                    "precision": self.precision_score,
                    "recall": self.recall_score,
                    "f1_score": self.f1_score,
                    "auc_score": self.roc_auc_score,
                    "roc_auc_score": self.roc_auc_score
                },
                "deployment_status": {
                    "status": self.deployment_status,
                    "usage_count": self.usage_count,
                    "last_used": self.last_used_at
                },
                "quality_metrics": {
                    "model_quality": self.model_quality_score,
                    "data_quality": self.data_quality_score,
                    "validation_status": self.validation_status,
                    "compliance_score": self.compliance_score
                },
                "enterprise_metrics": {
                    "performance_trend": self.performance_trend,
                    "resource_efficiency": self.resource_efficiency_score,
                    "scalability": self.scalability_score,
                    "enterprise_compliance": self.enterprise_compliance_score
                }
            }
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to generate summary: {str(e)}"}
    
    async def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export ML registry data in specified format"""
        try:
            if format.lower() == "json":
                return {
                    "ml_registry_id": self.ml_registry_id,
                    "graph_id": self.graph_id,
                    "model_id": self.model_id,
                    "model_name": self.model_name,
                    "model_type": self.model_type,
                    "model_version": self.model_version,
                    "training_status": self.training_status,
                    "training_type": self.training_type,
                    "deployment_status": self.deployment_status,
                    "lifecycle_status": self.lifecycle_status,
                    "lifecycle_phase": self.lifecycle_phase,
                    "performance_metrics": {
                        "final_accuracy": self.final_accuracy,
                        "precision_score": self.precision_score,
                        "recall_score": self.recall_score,
                        "f1_score": self.f1_score,
                        "auc_score": self.roc_auc_score,
                        "roc_auc_score": self.roc_auc_score,
                        "overall_score": self.overall_model_score
                    },
                    "training_metrics": {
                        "training_duration": self.training_duration_seconds,
                        "training_efficiency": self.training_efficiency_score,
                        "dataset_size": self.dataset_size,
                        "feature_count": self.feature_count,
                        "data_quality": self.data_quality_score
                    },
                    "deployment_metrics": {
                        "deployment_date": self.deployment_date.isoformat() if self.deployment_date else None,
                        "usage_count": self.usage_count,
                        "last_used": self.last_used_at.isoformat() if self.last_used_at else None
                    },
                    "quality_metrics": {
                        "model_quality": self.model_quality_score,
                        "validation_status": self.validation_status,
                        "compliance_score": self.compliance_score,
                        "bias_detection": self.bias_detection_score
                    },
                    "enterprise_metrics": {
                        "performance_trend": self.performance_trend,
                        "resource_efficiency": self.resource_efficiency_score,
                        "scalability": self.scalability_score,
                        "enterprise_compliance": self.enterprise_compliance_score
                    },
                    "computed_fields": {
                        "training_efficiency_rating": self.training_efficiency_rating,
                        "model_maturity_level": self.model_maturity_level,
                        "performance_health_status": self.performance_health_status,
                        "resource_utilization_score": self.resource_utilization_score,
                        "deployment_readiness_score": self.deployment_readiness_score,
                        "bias_risk_assessment": self.bias_risk_assessment,
                        "optimization_priority": self.optimization_priority,
                        "maintenance_schedule": self.maintenance_schedule,
                        "enterprise_compliance_score": self.enterprise_compliance_score
                    },
                    "timestamps": {
                        "created_at": self.created_at.isoformat() if self.created_at else None,
                        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                        "training_started": self.training_started_at.isoformat() if self.training_started_at else None,
                        "training_completed": self.training_completed_at.isoformat() if self.training_completed_at else None
                    }
                }
            else:
                return {"error": f"Unsupported format: {format}"}
                
        except Exception as e:
            return {"error": f"Failed to export data: {str(e)}"}


# Query Models for API Operations
class KGNeo4jMLRegistryQuery(BaseModel):
    """Query model for filtering KG Neo4j ML registries"""
    
    # Basic filters
    model_name: Optional[str] = None
    model_type: Optional[str] = None
    training_status: Optional[str] = None
    deployment_status: Optional[str] = None
    lifecycle_status: Optional[str] = None
    
    # Performance filters
    min_overall_score: Optional[float] = None
    max_overall_score: Optional[float] = None
    min_accuracy: Optional[float] = None
    max_accuracy: Optional[float] = None
    
    # Training filters
    training_type: Optional[str] = None
    min_training_efficiency: Optional[float] = None
    max_training_efficiency: Optional[float] = None
    
    # Quality filters
    validation_status: Optional[str] = None
    min_model_quality: Optional[float] = None
    max_model_quality: Optional[float] = None
    
    # Enterprise filters
    performance_trend: Optional[str] = None
    bias_risk: Optional[str] = None
    compliance_score: Optional[float] = None
    
    # User filters
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    owner_team: Optional[str] = None
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    training_started_after: Optional[datetime] = None
    training_started_before: Optional[datetime] = None
    
    # Pagination
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"


# Summary Models for Analytics
class KGNeo4jMLRegistrySummary(BaseModel):
    """Summary model for KG Neo4j ML registry analytics"""
    
    # Counts
    total_models: int
    active_models: int
    deployed_models: int
    training_models: int
    completed_models: int
    
    # Performance averages
    avg_overall_score: float
    avg_accuracy: float
    avg_precision: float
    avg_recall: float
    avg_f1_score: float
    avg_auc_score: float
    
    # Status distribution
    training_status_distribution: Dict[str, int]
    deployment_status_distribution: Dict[str, int]
    lifecycle_status_distribution: Dict[str, int]
    
    # Model type distribution
    model_type_distribution: Dict[str, int]
    training_type_distribution: Dict[str, int]
    
    # Quality metrics
    avg_model_quality: float
    avg_data_quality: float
    avg_compliance_score: float
    avg_bias_detection: float
    
    # Training metrics
    avg_training_efficiency: float
    avg_training_duration: float
    total_training_time: int
    
    # Enterprise metrics
    avg_resource_efficiency: float
    avg_scalability_score: float
    performance_trend_distribution: Dict[str, int]
    
    # Risk assessment
    high_bias_risk_count: int
    medium_bias_risk_count: int
    low_bias_risk_count: int
    
    # Timestamps
    summary_generated_at: datetime
    data_from_date: Optional[datetime] = None
    data_to_date: Optional[datetime] = None
