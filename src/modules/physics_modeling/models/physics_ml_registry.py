"""
Physics ML Registry Model

This model represents the machine learning models (PINNs, etc.) registry table with integrated
enterprise features for ML compliance, security, and performance monitoring.
Enhanced with enterprise-grade computed fields, business intelligence methods, and full Certificate Manager method parity.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, computed_field, ConfigDict
from src.engine.models.base_model import EngineBaseModel, ModelObserver
import uuid
import asyncio


class PhysicsMLRegistry(EngineBaseModel):
    """
    Physics ML Registry Model
    
    Represents machine learning models (PINNs, hybrid physics-ML) with integrated enterprise features
    for ML compliance tracking, security monitoring, and performance analytics.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),
        arbitrary_types_allowed=True,
        extra="allow",  # Allow extra fields to prevent validation errors
    )
    
    # Primary Identification
    ml_registry_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ML registry identifier")
    model_name: str = Field(..., description="Name of the ML model")
    ml_model_type: str = Field(default="pinn", description="Type of ML model: pinn, neural_ode, graph_neural_network, transformer, hybrid")
    
    # Model Information
    model_type: str = Field(default="ml", description="Model type: ml, hybrid_ml, traditional_enhanced")
    model_version: str = Field(default="1.0.0", description="Model version (separate from ml_model_type)")
    model_description: Optional[str] = Field(None, description="Detailed description of the ML model")
    
    # Physics Domain Classification
    physics_domain: str = Field(default="mechanical", description="Physics domain: mechanical, electrical, thermal, fluid, electromagnetic, quantum, multi_domain")
    
    # Neural Network Architecture
    nn_architecture: Dict[str, Any] = Field(default_factory=dict, description="JSON: layer sizes, activation functions, regularization")
    activation_functions: Dict[str, Any] = Field(default_factory=dict, description="JSON object of activation functions")
    regularization_methods: Dict[str, Any] = Field(default_factory=dict, description="JSON object of regularization methods")
    dropout_rates: Dict[str, Any] = Field(default_factory=dict, description="JSON object of dropout rates per layer")
    
    # Training Configuration
    training_parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON: learning rate, batch size, epochs, optimizer")
    loss_function_config: Dict[str, Any] = Field(default_factory=dict, description="JSON: loss function configuration and weights")
    optimization_settings: Dict[str, Any] = Field(default_factory=dict, description="JSON: optimizer settings, learning rate schedules")
    training_data_config: Dict[str, Any] = Field(default_factory=dict, description="JSON: training data configuration and augmentation")
    
    # Physics Integration
    physics_constraints: Dict[str, Any] = Field(default_factory=dict, description="JSON: physics constraints and enforcement methods")
    conservation_laws: Dict[str, Any] = Field(default_factory=dict, description="JSON object of conservation laws to enforce")
    differential_equations: Dict[str, Any] = Field(default_factory=dict, description="JSON object of differential equations")
    boundary_condition_handling: Dict[str, Any] = Field(default_factory=dict, description="JSON: boundary condition enforcement")
    initial_condition_learning: Dict[str, Any] = Field(default_factory=dict, description="JSON: initial condition learning configuration")
    
    # Model Performance & Quality
    training_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Training accuracy (0.0-1.0)")
    validation_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Validation accuracy (0.0-1.0)")
    physics_compliance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Physics compliance (0.0-1.0)")
    generalization_error: float = Field(default=0.0, ge=0.0, le=1.0, description="Generalization error (0.0-1.0)")
    overfitting_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overfitting assessment (0.0-1.0)")
    
    # Enterprise ML Metrics (Merged from enterprise tables)
    ml_compliance_type: str = Field(default="standard", description="Type of ML compliance requirement: standard, regulatory, industry_specific, custom")
    ml_compliance_status: str = Field(default="pending", description="ML compliance status: pending, compliant, non_compliant, under_review")
    ml_compliance_score: float = Field(default=0.0, ge=0.0, le=100.0, description="ML compliance score (0.0-100.0)")
    ml_security_score: float = Field(default=0.0, ge=0.0, le=100.0, description="ML security score (0.0-100.0)")
    ml_performance_trend: str = Field(default="stable", description="ML performance trend: improving, stable, declining, fluctuating")
    ml_optimization_suggestions: Dict[str, Any] = Field(default_factory=dict, description="JSON object of ML optimization recommendations")
    last_ml_optimization_date: Optional[str] = Field(None, description="Last ML optimization performed")
    enterprise_ml_metrics: Dict[str, Any] = Field(default_factory=dict, description="JSON: additional enterprise-specific ML metrics")
    
    # Integration References
    physics_modeling_id: Optional[str] = Field(None, description="Reference to physics_modeling_registry table")
    aasx_integration_id: Optional[str] = Field(None, description="Reference to aasx_processing table")
    twin_registry_id: Optional[str] = Field(None, description="Reference to twin_registry table")
    kg_neo4j_id: Optional[str] = Field(None, description="Reference to kg_graph_registry table")
    ai_rag_id: Optional[str] = Field(None, description="Reference to ai_rag_registry table")
    federated_learning_id: Optional[str] = Field(None, description="Reference to federated_learning_registry table")
    certificate_manager_id: Optional[str] = Field(None, description="Reference to certificate module")
    
    # Status & Lifecycle
    training_status: str = Field(default="pending", description="Training status: pending, training, completed, failed, paused")
    deployment_status: str = Field(default="not_deployed", description="Deployment status: not_deployed, deployed, serving, error, maintenance")
    model_version: str = Field(default="1.0.0", description="Semantic versioning")
    lifecycle_phase: str = Field(default="development", description="Lifecycle phase: development, training, validation, deployment, monitoring")
    
    # Training History & Metadata
    training_started_at: Optional[str] = Field(None, description="When training started")
    training_completed_at: Optional[str] = Field(None, description="When training completed")
    training_duration_sec: Optional[float] = Field(None, description="Total training duration")
    training_iterations: int = Field(default=0, description="Number of training iterations")
    model_checkpoints: Dict[str, Any] = Field(default_factory=dict, description="JSON object of model checkpoint information")
    
    # User Management & Ownership
    user_id: str = Field(..., description="Current user who owns/accesses this ML model")
    org_id: str = Field(..., description="Organization this ML model belongs to")
    dept_id: Optional[str] = Field(None, description="Department for complete traceability")
    ml_engineer_id: Optional[str] = Field(None, description="ML engineer responsible for this model")
    data_scientist_id: Optional[str] = Field(None, description="Data scientist who developed this model")
    owner_team: Optional[str] = Field(None, description="Team responsible for this ML model")
    steward_user_id: Optional[str] = Field(None, description="Data steward for this ML model")
    
    # Timestamps & Audit
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    activated_at: Optional[str] = Field(None, description="When ML model was first activated")
    last_accessed_at: Optional[str] = Field(None, description="Last time any user accessed this ML model")
    last_modified_at: Optional[str] = Field(None, description="Last time ML model data was modified")
    
    # Configuration & Metadata (JSON fields for flexibility)
    registry_config: Dict[str, Any] = Field(default_factory=dict, description="Registry configuration settings")
    registry_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    custom_attributes: Dict[str, Any] = Field(default_factory=dict, description="User-defined custom attributes")
    tags: Dict[str, Any] = Field(default_factory=dict, description="JSON object of tags for categorization")
    
    # Relationships & Dependencies (JSON objects)
    relationships: Dict[str, Any] = Field(default_factory=dict, description="JSON object of relationship objects")
    dependencies: Dict[str, Any] = Field(default_factory=dict, description="JSON object of dependency objects")
    ml_instances: Dict[str, Any] = Field(default_factory=dict, description="JSON object of ML instance objects")
    
    # Computed Fields for Business Intelligence
    @computed_field
    @property
    def overall_ml_score(self) -> float:
        """Calculate overall composite score from all ML metrics"""
        scores = [
            self.training_accuracy,
            self.validation_accuracy,
            self.physics_compliance_score,
            1.0 - self.generalization_error,  # Convert error to score
            1.0 - self.overfitting_score      # Convert overfitting to score
        ]
        return sum(scores) / len(scores) if scores else 0.0
    
    @computed_field
    @property
    def ml_enterprise_health_status(self) -> str:
        """Determine ML enterprise health status based on multiple factors"""
        if self.ml_compliance_score >= 80 and self.overall_ml_score >= 0.8:
            return "excellent"
        elif self.ml_compliance_score >= 60 and self.overall_ml_score >= 0.6:
            return "good"
        elif self.ml_compliance_score >= 40 and self.overall_ml_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    @computed_field
    @property
    def ml_risk_assessment(self) -> Dict[str, Any]:
        """Calculate ML risk assessment based on various metrics"""
        risk_factors = []
        risk_score = 0.0
        
        # Compliance risk
        if self.ml_compliance_score < 70:
            risk_factors.append("Low ML compliance score")
            risk_score += 0.3
        
        # Security risk
        if self.ml_security_score < 70:
            risk_factors.append("Low ML security score")
            risk_score += 0.4
        
        # Performance risk
        if self.overall_ml_score < 0.6:
            risk_factors.append("Low ML performance score")
            risk_score += 0.2
        
        # Overfitting risk
        if self.overfitting_score > 0.3:
            risk_factors.append("High overfitting risk")
            risk_score += 0.3
        
        # Generalization risk
        if self.generalization_error > 0.3:
            risk_factors.append("High generalization error")
            risk_score += 0.3
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_level": "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high",
            "risk_factors": risk_factors,
            "mitigation_required": risk_score > 0.5
        }
    
    @computed_field
    @property
    def ml_complexity_score(self) -> float:
        """Calculate ML complexity score based on various factors"""
        complexity_factors = []
        
        # Architecture complexity
        if len(self.nn_architecture) > 10:
            complexity_factors.append(0.9)
        elif len(self.nn_architecture) > 5:
            complexity_factors.append(0.7)
        else:
            complexity_factors.append(0.5)
        
        # Physics integration complexity
        if len(self.physics_constraints) > 5:
            complexity_factors.append(0.9)
        elif len(self.physics_constraints) > 2:
            complexity_factors.append(0.7)
        else:
            complexity_factors.append(0.5)
        
        # Training complexity
        if self.training_iterations > 10000:
            complexity_factors.append(0.9)
        elif self.training_iterations > 5000:
            complexity_factors.append(0.7)
        else:
            complexity_factors.append(0.5)
        
        # Physics domain complexity
        if self.physics_domain == "multi_domain":
            complexity_factors.append(1.0)
        elif self.physics_domain in ["quantum", "electromagnetic"]:
            complexity_factors.append(0.9)
        else:
            complexity_factors.append(0.7)
        
        return sum(complexity_factors) / len(complexity_factors)
    
    @computed_field
    @property
    def ml_optimization_priority(self) -> str:
        """Determine ML optimization priority based on current state"""
        if self.overall_ml_score < 0.4:
            return "critical"
        elif self.overall_ml_score < 0.6:
            return "high"
        elif self.overall_ml_score < 0.8:
            return "medium"
        else:
            return "low"
    
    @computed_field
    @property
    def ml_maintenance_schedule(self) -> Dict[str, Any]:
        """Calculate ML maintenance schedule based on various factors"""
        base_interval_days = 30
        
        # Adjust based on compliance score
        if self.ml_compliance_score < 50:
            interval_multiplier = 0.5  # More frequent maintenance
        elif self.ml_compliance_score < 70:
            interval_multiplier = 0.8
        elif self.ml_compliance_score > 90:
            interval_multiplier = 1.5  # Less frequent maintenance
        else:
            interval_multiplier = 1.0
        
        adjusted_interval = base_interval_days * interval_multiplier
        
        return {
            "base_interval_days": base_interval_days,
            "adjusted_interval_days": adjusted_interval,
            "next_maintenance": f"in_{int(adjusted_interval)}_days",
            "priority": "high" if self.ml_compliance_score < 60 else "medium" if self.ml_compliance_score < 80 else "low"
        }
    
    @computed_field
    @property
    def ml_training_efficiency_score(self) -> float:
        """Calculate ML training efficiency based on time and iterations"""
        if self.training_duration_sec and self.training_iterations > 0:
            # Higher iterations and lower duration = better efficiency
            efficiency = (self.training_iterations / self.training_duration_sec) * 100
            return min(efficiency / 100.0, 1.0)  # Normalize to 0-1
        return 0.0
    
    @computed_field
    @property
    def ml_physics_integration_score(self) -> float:
        """Calculate ML physics integration effectiveness"""
        integration_factors = []
        if len(self.physics_constraints) > 0:
            integration_factors.append(0.8)
        if len(self.conservation_laws) > 0:
            integration_factors.append(0.9)
        if len(self.differential_equations) > 0:
            integration_factors.append(0.8)
        if self.physics_compliance_score > 0.7:
            integration_factors.append(0.9)
        return sum(integration_factors) / len(integration_factors) if integration_factors else 0.0
    
    # Validators
    @validator('ml_model_type')
    def validate_ml_model_type(cls, v):
        """Validate ML model type"""
        valid_types = ['pinn', 'neural_ode', 'graph_neural_network', 'transformer', 'hybrid']
        if v not in valid_types:
            raise ValueError(f'ML model type must be one of: {valid_types}')
        return v
    
    @validator('training_status')
    def validate_training_status(cls, v):
        """Validate training status"""
        valid_statuses = ['pending', 'training', 'completed', 'failed', 'paused']
        if v not in valid_statuses:
            raise ValueError(f'Training status must be one of: {valid_statuses}')
        return v
    
    @validator('deployment_status')
    def validate_deployment_status(cls, v):
        """Validate deployment status"""
        valid_statuses = ['not_deployed', 'deployed', 'serving', 'error', 'maintenance']
        if v not in valid_statuses:
            raise ValueError(f'Deployment status must be one of: {valid_statuses}')
        return v
    
    @validator('lifecycle_phase')
    def validate_lifecycle_phase(cls, v):
        """Validate lifecycle phase"""
        valid_phases = ['development', 'training', 'validation', 'deployment', 'monitoring']
        if v not in valid_phases:
            raise ValueError(f'Lifecycle phase must be one of: {valid_phases}')
        return v
    
    @validator('ml_compliance_type')
    def validate_ml_compliance_type(cls, v):
        """Validate ML compliance type"""
        valid_types = ['standard', 'regulatory', 'industry_specific', 'custom']
        if v not in valid_types:
            raise ValueError(f'ML compliance type must be one of: {valid_types}')
        return v
    
    @validator('ml_compliance_status')
    def validate_ml_compliance_status(cls, v):
        """Validate ML compliance status"""
        valid_statuses = ['pending', 'compliant', 'non_compliant', 'under_review']
        if v not in valid_statuses:
            raise ValueError(f'ML compliance status must be one of: {valid_statuses}')
        return v
    
    @validator('ml_performance_trend')
    def validate_ml_performance_trend(cls, v):
        """Validate ML performance trend"""
        valid_trends = ['improving', 'stable', 'declining', 'fluctuating']
        if v not in valid_trends:
            raise ValueError(f'ML performance trend must be one of: {valid_trends}')
        return v
    
    @validator('model_type')
    def validate_model_type(cls, v):
        """Validate model type"""
        valid_types = ['ml', 'hybrid_ml', 'traditional_enhanced']
        if v not in valid_types:
            raise ValueError(f'Model type must be one of: {valid_types}')
        return v
    
    @validator('physics_domain')
    def validate_physics_domain(cls, v):
        """Validate physics domain"""
        valid_domains = ['mechanical', 'electrical', 'thermal', 'fluid', 'electromagnetic', 'quantum', 'multi_domain']
        if v not in valid_domains:
            raise ValueError(f'Physics domain must be one of: {valid_domains}')
        return v
    
    # Basic Pydantic methods only
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhysicsMLRegistry':
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PhysicsMLRegistry':
        """Create model from JSON string"""
        import json
        data = json.loads(json_str)
        return cls(**data)
    
    # Enterprise Methods for Business Intelligence
    async def update_enterprise_ml_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update enterprise ML metrics asynchronously"""
        if isinstance(metrics, dict):
            self.enterprise_ml_metrics.update(metrics)
            self.updated_at = datetime.now().isoformat()
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_ml_compliance_status(self, new_status: str, audit_details: Optional[Dict[str, Any]] = None) -> None:
        """Update ML compliance status asynchronously"""
        valid_statuses = ['pending', 'compliant', 'non_compliant', 'under_review']
        if new_status in valid_statuses:
            self.ml_compliance_status = new_status
            self.updated_at = datetime.now().isoformat()
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_ml_security_score(self, new_score: float, details: Optional[Dict[str, Any]] = None) -> None:
        """Update ML security score asynchronously"""
        if 0.0 <= new_score <= 100.0:
            self.ml_security_score = new_score
            self.updated_at = datetime.now().isoformat()
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def calculate_ml_performance_trend(self) -> str:
        """Calculate ML performance trend based on current metrics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        # This would typically analyze historical ML performance data
        # For now, we'll use a simple heuristic based on current scores
        if self.overall_ml_score > 0.8:
            return "improving"
        elif self.overall_ml_score < 0.6:
            return "declining"
        else:
            return "stable"
    
    async def generate_ml_optimization_suggestions(self) -> List[str]:
        """Generate ML optimization suggestions based on current state"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        suggestions = []
        
        # Performance suggestions
        if self.training_accuracy < 0.7:
            suggestions.append("Consider hyperparameter tuning and architecture optimization")
        if self.validation_accuracy < 0.7:
            suggestions.append("Review training data quality and validation split")
        if self.physics_compliance_score < 0.7:
            suggestions.append("Enhance physics constraints and conservation law enforcement")
        if self.generalization_error > 0.3:
            suggestions.append("Implement regularization techniques and data augmentation")
        if self.overfitting_score > 0.3:
            suggestions.append("Add dropout layers and early stopping")
        
        # Architecture suggestions
        if len(self.nn_architecture) < 3:
            suggestions.append("Consider deeper network architecture for complex physics")
        if not self.regularization_methods:
            suggestions.append("Implement regularization methods (L1, L2, dropout)")
        
        # Training suggestions
        if self.training_iterations < 1000:
            suggestions.append("Increase training iterations for better convergence")
        if not self.optimization_settings:
            suggestions.append("Optimize learning rate schedules and optimizer settings")
        
        # Physics integration suggestions
        if len(self.physics_constraints) < 2:
            suggestions.append("Add more physics constraints for better physical consistency")
        if not self.conservation_laws:
            suggestions.append("Implement conservation law enforcement")
        
        # Security suggestions
        if self.ml_security_score < 70:
            suggestions.append("Implement ML security measures and model protection")
        
        # Compliance suggestions
        if self.ml_compliance_score < 70:
            suggestions.append("Review ML compliance policies and implement corrective actions")
        
        return suggestions
    
    async def get_ml_enterprise_summary(self) -> Dict[str, Any]:
        """Get comprehensive ML enterprise summary for this physics ML model"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        return {
            "ml_model_info": {
                "model_name": self.model_name,
                "ml_model_type": self.ml_model_type,
                "model_type": self.model_type,
                "physics_domain": self.physics_domain,
                "model_version": self.model_version
            },
            "neural_network_architecture": {
                "nn_architecture": self.nn_architecture,
                "activation_functions": self.activation_functions,
                "regularization_methods": self.regularization_methods,
                "dropout_rates": self.dropout_rates,
                "ml_complexity_score": self.ml_complexity_score
            },
            "training_configuration": {
                "training_parameters": self.training_parameters,
                "loss_function_config": self.loss_function_config,
                "optimization_settings": self.optimization_settings,
                "training_data_config": self.training_data_config
            },
            "physics_integration": {
                "physics_constraints": self.physics_constraints,
                "conservation_laws": self.conservation_laws,
                "differential_equations": self.differential_equations,
                "boundary_condition_handling": self.boundary_condition_handling
            },
            "ml_performance_metrics": {
                "overall_ml_score": self.overall_ml_score,
                "training_accuracy": self.training_accuracy,
                "validation_accuracy": self.validation_accuracy,
                "physics_compliance_score": self.physics_compliance_score,
                "generalization_error": self.generalization_error,
                "overfitting_score": self.overfitting_score
            },
            "ml_enterprise_metrics": {
                "ml_compliance_score": self.ml_compliance_score,
                "ml_security_score": self.ml_security_score,
                "ml_performance_trend": self.ml_performance_trend
            },
            "ml_health_status": {
                "ml_enterprise_health_status": self.ml_enterprise_health_status
            },
            "ml_risk_assessment": self.ml_risk_assessment,
            "ml_optimization": {
                "ml_optimization_priority": self.ml_optimization_priority,
                "ml_maintenance_schedule": self.ml_maintenance_schedule
            },
            "enterprise_ml_metrics": self.enterprise_ml_metrics,
            "ml_optimization_suggestions": await self.generate_ml_optimization_suggestions()
        }
    
    async def validate_ml_enterprise_compliance(self) -> Dict[str, Any]:
        """Validate ML enterprise compliance requirements"""
        # Simulate async validation
        await asyncio.sleep(0.001)
        
        compliance_checks = {
            "training_accuracy": self.training_accuracy >= 0.7,
            "validation_accuracy": self.validation_accuracy >= 0.7,
            "physics_compliance": self.physics_compliance_score >= 0.7,
            "generalization": self.generalization_error <= 0.3,
            "overfitting": self.overfitting_score <= 0.3,
            "ml_compliance": self.ml_compliance_score >= 70,
            "ml_security": self.ml_security_score >= 70
        }
        
        overall_compliance = all(compliance_checks.values())
        
        return {
            "overall_compliant": overall_compliance,
            "ml_compliance_score": self.ml_compliance_score,
            "compliance_checks": compliance_checks,
            "failed_checks": [check for check, passed in compliance_checks.items() if not passed],
            "recommendations": await self.generate_ml_optimization_suggestions() if not overall_compliance else []
        }
    
    async def get_ml_physics_analysis(self) -> Dict[str, Any]:
        """Get comprehensive ML physics analysis summary"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        return {
            "ml_complexity_analysis": {
                "architecture_complexity": "high" if len(self.nn_architecture) > 10 else "medium" if len(self.nn_architecture) > 5 else "low",
                "physics_integration_complexity": "high" if len(self.physics_constraints) > 5 else "medium" if len(self.physics_constraints) > 2 else "low",
                "training_complexity": "high" if self.training_iterations > 10000 else "medium" if self.training_iterations > 5000 else "low",
                "ml_complexity_score": self.ml_complexity_score
            },
            "physics_integration_analysis": {
                "physics_constraints_count": len(self.physics_constraints),
                "conservation_laws_count": len(self.conservation_laws),
                "differential_equations_count": len(self.differential_equations),
                "physics_compliance_score": self.physics_compliance_score
            },
            "ml_performance_analysis": {
                "overall_ml_score": self.overall_ml_score,
                "accuracy_gap": self.training_accuracy - self.validation_accuracy,
                "generalization_quality": "good" if self.generalization_error < 0.2 else "fair" if self.generalization_error < 0.3 else "poor",
                "overfitting_assessment": "low" if self.overfitting_score < 0.2 else "medium" if self.overfitting_score < 0.3 else "high"
            },
            "ml_optimization_opportunities": await self.generate_ml_optimization_suggestions()
        }
    
    # Additional Async Methods (Certificate Manager Parity)
    async def validate_integrity(self) -> bool:
        """Validate data integrity asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return (
            self.ml_registry_id and
            self.model_name and
            self.ml_model_type and
            self.overall_ml_score >= 0.0 and
            self.overall_ml_score <= 1.0
        )
    
    async def update_health_metrics(self) -> None:
        """Update health metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        # Update health metrics based on current performance and quality scores
        pass
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return await self.get_ml_enterprise_summary()
    
    async def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export data in specified format asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        if format == "json":
            return {
                "ml_physics_data": self.model_dump(),
                "computed_scores": {
                    "overall_ml_score": self.overall_ml_score,
                    "ml_enterprise_health_status": self.ml_enterprise_health_status,
                    "ml_risk_assessment": self.ml_risk_assessment,
                    "ml_complexity_score": self.ml_complexity_score,
                    "ml_optimization_priority": self.ml_optimization_priority,
                    "ml_maintenance_schedule": self.ml_maintenance_schedule,
                    "ml_training_efficiency_score": self.ml_training_efficiency_score,
                    "ml_physics_integration_score": self.ml_physics_integration_score
                },
                "export_timestamp": datetime.now().isoformat(),
                "export_format": format
            }
        else:
            return {"error": f"Unsupported format: {format}"}


# Query and Summary models for API responses
class PhysicsMLRegistryQuery(BaseModel):
    """Query model for filtering physics ML registry entries"""
    model_type: Optional[str] = None
    physics_domain: Optional[str] = None
    ml_model_type: Optional[str] = None
    training_status: Optional[str] = None
    deployment_status: Optional[str] = None
    lifecycle_phase: Optional[str] = None
    ml_compliance_status: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    limit: int = 100
    offset: int = 0


class PhysicsMLRegistrySummary(BaseModel):
    """Summary model for physics ML registry overview"""
    total_ml_models: int
    active_models: int
    training_models: int
    deployed_models: int
    models_by_type: Dict[str, int]
    models_by_status: Dict[str, int]
    models_by_compliance: Dict[str, int]
    models_by_domain: Dict[str, int]
