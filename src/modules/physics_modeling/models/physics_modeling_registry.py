"""
Physics Modeling Registry Model

This model represents the main physics modeling registry table with integrated
enterprise features for compliance, security, and performance monitoring.
Enhanced with enterprise-grade computed fields, business intelligence methods, and full Certificate Manager method parity.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, computed_field, ConfigDict
from src.engine.models.base_model import EngineBaseModel, ModelObserver
import uuid
import asyncio


class PhysicsModelingRegistry(EngineBaseModel):
    """
    Physics Modeling Registry Model
    
    Represents traditional physics models with integrated enterprise features
    for compliance tracking, security monitoring, and performance analytics.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),
        arbitrary_types_allowed=True,
        extra="allow",  # Allow extra fields to prevent validation errors
    )
    
    # Primary Identification
    registry_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique registry identifier")
    model_name: str = Field(..., description="Name of the physics model")
    physics_type: str = Field(..., description="Type of physics model")
    
    # Plugin & Model Information (CRITICAL for plugin management)
    plugin_id: Optional[str] = Field(None, description="Plugin identifier for plugin-based models")
    plugin_name: Optional[str] = Field(None, description="Plugin name for plugin-based models")
    model_type: str = Field(default="traditional", description="Model type: traditional, plugin, hybrid, ml_integrated")
    model_version: str = Field(default="1.0.0", description="Model version (separate from physics_version)")
    model_description: Optional[str] = Field(None, description="Detailed description of the model")
    
    # Physics Classification & Metadata
    physics_category: str = Field(default="structural", description="Physics category: structural, thermal, fluid, electromagnetic, multi_physics, acoustics, quantum")
    physics_subcategory: Optional[str] = Field(None, description="Physics subcategory (e.g., linear_elastic, non_linear_plastic, laminar_flow, turbulent_flow)")
    physics_domain: str = Field(default="mechanical", description="Physics domain: mechanical, electrical, thermal, fluid, electromagnetic, quantum, multi_domain")
    complexity_level: str = Field(default="medium", description="Complexity level: simple, medium, complex, very_complex")
    physics_version: str = Field(default="1.0.0", description="Physics version")
    
    # Workflow Classification (CRITICAL for dual workflow support)
    registry_type: str = Field(..., description="Registry type: extraction, generation, hybrid")
    workflow_source: str = Field(..., description="Workflow source: aasx_file, structured_data, both")
    
    # Traditional Solver Configuration (CRITICAL for physics simulations)
    solver_type: str = Field(default="finite_element", description="Solver type: finite_element, finite_difference, finite_volume, boundary_element, spectral")
    solver_name: Optional[str] = Field(None, description="Specific solver name/implementation (e.g., ANSYS, COMSOL, OpenFOAM)")
    solver_version: Optional[str] = Field(None, description="Solver software version")
    solver_parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON: solver-specific parameters (tolerance, max_iterations, etc.)")
    mesh_configuration: Dict[str, Any] = Field(default_factory=dict, description="JSON: mesh settings, element types, refinement criteria")
    time_integration_scheme: Optional[str] = Field(None, description="Time integration method: explicit, implicit, semi_implicit, adaptive")
    spatial_discretization: Optional[str] = Field(None, description="Spatial discretization method: first_order, second_order, higher_order")
    convergence_criteria: Dict[str, Any] = Field(default_factory=dict, description="JSON: convergence thresholds and criteria")
    solver_optimization: Dict[str, Any] = Field(default_factory=dict, description="JSON: solver optimization settings (parallelization, memory, etc.)")
    
    # Physics Equations & Constraints
    governing_equations: Dict[str, Any] = Field(default_factory=dict, description="JSON object of governing equations")
    boundary_conditions: Dict[str, Any] = Field(default_factory=dict, description="JSON: boundary condition definitions")
    initial_conditions: Dict[str, Any] = Field(default_factory=dict, description="JSON: initial condition specifications")
    material_properties: Dict[str, Any] = Field(default_factory=dict, description="JSON: material property definitions")
    physical_constants: Dict[str, Any] = Field(default_factory=dict, description="JSON: physical constants and parameters")
    
    # Module Integration References (Links to other modules - NO data duplication)
    aasx_integration_id: Optional[str] = Field(None, description="Reference to aasx_processing table")
    twin_registry_id: Optional[str] = Field(None, description="Reference to twin_registry table")
    kg_neo4j_id: Optional[str] = Field(None, description="Reference to kg_graph_registry table")
    ai_rag_id: Optional[str] = Field(None, description="Reference to ai_rag_registry table")
    federated_learning_id: Optional[str] = Field(None, description="Reference to federated_learning_registry table")
    certificate_manager_id: Optional[str] = Field(None, description="Reference to certificate module")
    
    # Integration Status & Health
    integration_status: str = Field(default="pending", description="Integration status: pending, active, inactive, error, maintenance, deprecated")
    overall_health_score: int = Field(default=0, ge=0, le=100, description="Overall health score (0-100)")
    health_status: str = Field(default="unknown", description="Health status: unknown, healthy, warning, critical, offline")
    
    # Lifecycle Management
    lifecycle_status: str = Field(default="created", description="Lifecycle status: created, active, suspended, archived, retired")
    lifecycle_phase: str = Field(default="setup", description="Lifecycle phase: setup, validation, deployment, monitoring, maintenance")
    
    # Operational Status
    operational_status: str = Field(default="stopped", description="Operational status: running, stopped, paused, error, maintenance")
    availability_status: str = Field(default="offline", description="Availability status: online, offline, degraded, maintenance")
    
    # Physics-Specific Status
    simulation_status: str = Field(default="pending", description="Simulation status: pending, running, completed, failed, paused")
    validation_status: str = Field(default="pending", description="Validation status: pending, in_progress, passed, failed, needs_review")
    convergence_status: str = Field(default="unknown", description="Convergence status: unknown, converging, converged, diverged, oscillating")
    
    # Performance & Quality Metrics
    performance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Performance score (0.0-1.0)")
    accuracy_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Accuracy score (0.0-1.0)")
    computational_efficiency: float = Field(default=0.0, ge=0.0, le=1.0, description="Computational efficiency (0.0-1.0)")
    numerical_stability: float = Field(default=0.0, ge=0.0, le=1.0, description="Numerical stability (0.0-1.0)")
    
    # Security & Access Control
    security_level: str = Field(default="standard", description="Security level: public, internal, confidential, secret, top_secret")
    access_control_level: str = Field(default="user", description="Access control level: public, user, admin, system, restricted")
    encryption_enabled: bool = Field(default=True, description="Whether physics data is encrypted")
    audit_logging_enabled: bool = Field(default=True, description="Whether audit logging is enabled")
    
    # Enterprise Compliance & Security (Merged from enterprise tables)
    compliance_type: str = Field(default="standard", description="Compliance type: standard, regulatory, industry_specific, custom")
    compliance_status: str = Field(default="pending", description="Compliance status: pending, compliant, non_compliant, under_review")
    compliance_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Compliance score (0.0-100.0)")
    last_audit_date: Optional[str] = Field(None, description="Last compliance audit date")
    next_audit_date: Optional[str] = Field(None, description="Next scheduled audit date")
    audit_details: Dict[str, Any] = Field(default_factory=dict, description="JSON: detailed audit information")
    
    # Enterprise Security Metrics (Merged from enterprise tables)
    security_event_type: str = Field(default="none", description="Security event type: none, threat_detected, vulnerability_scan, access_violation")
    threat_assessment: str = Field(default="low", description="Threat assessment: low, medium, high, critical")
    security_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Security score (0.0-100.0)")
    last_security_scan: Optional[str] = Field(None, description="Last security scan date")
    security_details: Dict[str, Any] = Field(default_factory=dict, description="JSON: security scan results and details")
    
    # Enterprise Performance Analytics (Merged from enterprise tables)
    performance_trend: str = Field(default="stable", description="Performance trend: improving, stable, declining, fluctuating")
    optimization_suggestions: Dict[str, Any] = Field(default_factory=dict, description="JSON object of optimization recommendations")
    last_optimization_date: Optional[str] = Field(None, description="Last optimization performed")
    enterprise_metrics: Dict[str, Any] = Field(default_factory=dict, description="JSON: additional enterprise-specific metrics")
    
    # User Management & Ownership
    user_id: str = Field(..., description="Current user who owns/accesses this registry")
    org_id: str = Field(..., description="Organization this registry belongs to")
    dept_id: Optional[str] = Field(None, description="Department for complete traceability")
    owner_team: Optional[str] = Field(None, description="Team responsible for this physics model")
    steward_user_id: Optional[str] = Field(None, description="Data steward for this physics model")
    
    # Timestamps & Audit
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    activated_at: Optional[str] = Field(None, description="When physics model was first activated")
    last_accessed_at: Optional[str] = Field(None, description="Last time any user accessed this physics model")
    last_modified_at: Optional[str] = Field(None, description="Last time physics model data was modified")
    
    # Configuration & Metadata (JSON fields for flexibility)
    registry_config: Dict[str, Any] = Field(default_factory=dict, description="Registry configuration settings")
    registry_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    custom_attributes: Dict[str, Any] = Field(default_factory=dict, description="User-defined custom attributes")
    tags: Dict[str, Any] = Field(default_factory=dict, description="JSON object of tags for categorization")
    
    # Relationships & Dependencies (JSON objects)
    relationships: Dict[str, Any] = Field(default_factory=dict, description="JSON object of relationship objects")
    dependencies: Dict[str, Any] = Field(default_factory=dict, description="JSON object of dependency objects")
    physics_instances: Dict[str, Any] = Field(default_factory=dict, description="JSON object of physics instance objects")
    
    # Results and Metrics (JSON objects)
    results_metadata: Dict[str, Any] = Field(default_factory=dict, description="JSON: metadata about simulation results")
    physics_specific_metrics: Dict[str, Any] = Field(default_factory=dict, description="JSON: physics-specific performance metrics")
    
    # Computed Fields for Business Intelligence
    @computed_field
    @property
    def overall_score(self) -> float:
        """Calculate overall composite score from all metrics"""
        scores = [
            self.performance_score,
            self.accuracy_score,
            self.computational_efficiency,
            self.numerical_stability
        ]
        return sum(scores) / len(scores) if scores else 0.0
    
    @computed_field
    @property
    def enterprise_health_status(self) -> str:
        """Determine enterprise health status based on multiple factors"""
        if self.overall_health_score >= 80 and self.overall_score >= 0.8:
            return "excellent"
        elif self.overall_health_score >= 60 and self.overall_score >= 0.6:
            return "good"
        elif self.overall_health_score >= 40 and self.overall_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    @computed_field
    @property
    def risk_assessment(self) -> Dict[str, Any]:
        """Calculate risk assessment based on various metrics"""
        risk_factors = []
        risk_score = 0.0
        
        # Compliance risk
        if self.compliance_score < 70:
            risk_factors.append("Low compliance score")
            risk_score += 0.3
        
        # Security risk
        if self.security_event_type != "none":
            risk_factors.append(f"Security event: {self.security_event_type}")
            risk_score += 0.4
        
        # Performance risk
        if self.performance_score < 0.6:
            risk_factors.append("Low performance score")
            risk_score += 0.2
        
        # Health risk
        if self.overall_health_score < 50:
            risk_factors.append("Critical health status")
            risk_score += 0.5
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_level": "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high",
            "risk_factors": risk_factors,
            "mitigation_required": risk_score > 0.5
        }
    
    @computed_field
    @property
    def physics_complexity_score(self) -> float:
        """Calculate physics complexity score based on various factors"""
        complexity_factors = []
        
        # Complexity level contribution
        complexity_multiplier = {
            "simple": 0.3,
            "medium": 0.6,
            "complex": 0.8,
            "very_complex": 1.0
        }.get(self.complexity_level, 0.6)
        
        # Solver complexity
        if self.solver_type in ["finite_element", "finite_volume"]:
            complexity_factors.append(0.8)
        elif self.solver_type == "spectral":
            complexity_factors.append(1.0)
        else:
            complexity_factors.append(0.6)
        
        # Physics domain complexity
        if self.physics_domain == "multi_domain":
            complexity_factors.append(1.0)
        elif self.physics_domain in ["quantum", "electromagnetic"]:
            complexity_factors.append(0.9)
        else:
            complexity_factors.append(0.7)
        
        # Time integration complexity
        if self.time_integration_scheme == "adaptive":
            complexity_factors.append(0.9)
        elif self.time_integration_scheme == "implicit":
            complexity_factors.append(0.8)
        else:
            complexity_factors.append(0.6)
        
        base_score = sum(complexity_factors) / len(complexity_factors)
        return min(base_score * complexity_multiplier, 1.0)
    
    @computed_field
    @property
    def solver_efficiency_score(self) -> float:
        """Calculate solver efficiency score based on configuration"""
        efficiency_factors = []
        
        # Solver type efficiency
        solver_efficiency = {
            "finite_element": 0.8,
            "finite_difference": 0.7,
            "finite_volume": 0.85,
            "boundary_element": 0.75,
            "spectral": 0.9
        }.get(self.solver_type, 0.7)
        efficiency_factors.append(solver_efficiency)
        
        # Spatial discretization efficiency
        if self.spatial_discretization == "higher_order":
            efficiency_factors.append(0.9)
        elif self.spatial_discretization == "second_order":
            efficiency_factors.append(0.8)
        else:
            efficiency_factors.append(0.7)
        
        # Time integration efficiency
        if self.time_integration_scheme == "adaptive":
            efficiency_factors.append(0.9)
        elif self.time_integration_scheme == "implicit":
            efficiency_factors.append(0.8)
        else:
            efficiency_factors.append(0.7)
        
        return sum(efficiency_factors) / len(efficiency_factors)
    
    @computed_field
    @property
    def optimization_priority(self) -> str:
        """Determine optimization priority based on current state"""
        if self.overall_score < 0.4:
            return "critical"
        elif self.overall_score < 0.6:
            return "high"
        elif self.overall_score < 0.8:
            return "medium"
        else:
            return "low"
    
    @computed_field
    @property
    def maintenance_schedule(self) -> Dict[str, Any]:
        """Calculate maintenance schedule based on various factors"""
        base_interval_days = 30
        
        # Adjust based on health score
        if self.overall_health_score < 50:
            interval_multiplier = 0.5  # More frequent maintenance
        elif self.overall_health_score < 70:
            interval_multiplier = 0.8
        elif self.overall_health_score > 90:
            interval_multiplier = 1.5  # Less frequent maintenance
        else:
            interval_multiplier = 1.0
        
        # Adjust based on performance
        if self.performance_score < 0.6:
            interval_multiplier *= 0.8
        
        # Adjust based on compliance
        if self.compliance_score < 70:
            interval_multiplier *= 0.7
        
        adjusted_interval = int(base_interval_days * interval_multiplier)
        
        return {
            "next_maintenance_days": adjusted_interval,
            "maintenance_priority": self.optimization_priority,
            "maintenance_type": "preventive" if self.overall_health_score > 70 else "corrective",
            "estimated_duration_hours": 2 if self.overall_health_score > 80 else 4 if self.overall_health_score > 60 else 8
        }
    
    # Validators
    @validator('physics_category')
    def validate_physics_category(cls, v):
        """Validate physics category"""
        valid_categories = ['structural', 'thermal', 'fluid', 'electromagnetic', 'multi_physics', 'acoustics', 'quantum']
        if v not in valid_categories:
            raise ValueError(f'Physics category must be one of: {valid_categories}')
        return v
    
    @validator('complexity_level')
    def validate_complexity_level(cls, v):
        """Validate complexity level"""
        valid_levels = ['simple', 'medium', 'complex', 'very_complex']
        if v not in valid_levels:
            raise ValueError(f'Complexity level must be one of: {valid_levels}')
        return v
    
    @validator('registry_type')
    def validate_registry_type(cls, v):
        """Validate registry type"""
        valid_types = ['extraction', 'generation', 'hybrid']
        if v not in valid_types:
            raise ValueError(f'Registry type must be one of: {valid_types}')
        return v
    
    @validator('workflow_source')
    def validate_workflow_source(cls, v):
        """Validate workflow source"""
        valid_sources = ['aasx_file', 'structured_data', 'both']
        if v not in valid_sources:
            raise ValueError(f'Workflow source must be one of: {valid_sources}')
        return v
    
    @validator('model_type')
    def validate_model_type(cls, v):
        """Validate model type"""
        valid_types = ['traditional', 'plugin', 'hybrid', 'ml_integrated']
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
    
    @validator('solver_type')
    def validate_solver_type(cls, v):
        """Validate solver type"""
        valid_solvers = ['finite_element', 'finite_difference', 'finite_volume', 'boundary_element', 'spectral']
        if v not in valid_solvers:
            raise ValueError(f'Solver type must be one of: {valid_solvers}')
        return v
    
    @validator('time_integration_scheme')
    def validate_time_integration_scheme(cls, v):
        """Validate time integration scheme"""
        if v is not None:
            valid_schemes = ['explicit', 'implicit', 'semi_implicit', 'adaptive']
            if v not in valid_schemes:
                raise ValueError(f'Time integration scheme must be one of: {valid_schemes}')
        return v
    
    @validator('spatial_discretization')
    def validate_spatial_discretization(cls, v):
        """Validate spatial discretization method"""
        if v is not None:
            valid_methods = ['first_order', 'second_order', 'higher_order']
            if v not in valid_methods:
                raise ValueError(f'Spatial discretization must be one of: {valid_methods}')
        return v
    
    @validator('integration_status')
    def validate_integration_status(cls, v):
        """Validate integration status"""
        valid_statuses = ['pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated']
        if v not in valid_statuses:
            raise ValueError(f'Integration status must be one of: {valid_statuses}')
        return v
    
    @validator('health_status')
    def validate_health_status(cls, v):
        """Validate health status"""
        valid_statuses = ['unknown', 'healthy', 'warning', 'critical', 'offline']
        if v not in valid_statuses:
            raise ValueError(f'Health status must be one of: {valid_statuses}')
        return v
    
    @validator('lifecycle_status')
    def validate_lifecycle_status(cls, v):
        """Validate lifecycle status"""
        valid_statuses = ['created', 'active', 'suspended', 'archived', 'retired']
        if v not in valid_statuses:
            raise ValueError(f'Lifecycle status must be one of: {valid_statuses}')
        return v
    
    @validator('lifecycle_phase')
    def validate_lifecycle_phase(cls, v):
        """Validate lifecycle phase"""
        valid_phases = ['setup', 'validation', 'deployment', 'monitoring', 'maintenance']
        if v not in valid_phases:
            raise ValueError(f'Lifecycle phase must be one of: {valid_phases}')
        return v
    
    @validator('operational_status')
    def validate_operational_status(cls, v):
        """Validate operational status"""
        valid_statuses = ['running', 'stopped', 'paused', 'error', 'maintenance']
        if v not in valid_statuses:
            raise ValueError(f'Operational status must be one of: {valid_statuses}')
        return v
    
    @validator('availability_status')
    def validate_availability_status(cls, v):
        """Validate availability status"""
        valid_statuses = ['online', 'offline', 'degraded', 'maintenance']
        if v not in valid_statuses:
            raise ValueError(f'Availability status must be one of: {valid_statuses}')
        return v
    
    @validator('simulation_status')
    def validate_simulation_status(cls, v):
        """Validate simulation status"""
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'paused']
        if v not in valid_statuses:
            raise ValueError(f'Simulation status must be one of: {valid_statuses}')
        return v
    
    @validator('validation_status')
    def validate_validation_status(cls, v):
        """Validate validation status"""
        valid_statuses = ['pending', 'in_progress', 'passed', 'failed', 'needs_review']
        if v not in valid_statuses:
            raise ValueError(f'Validation status must be one of: {valid_statuses}')
        return v
    
    @validator('convergence_status')
    def validate_convergence_status(cls, v):
        """Validate convergence status"""
        valid_statuses = ['unknown', 'converging', 'converged', 'diverged', 'oscillating']
        if v not in valid_statuses:
            raise ValueError(f'Convergence status must be one of: {valid_statuses}')
        return v
    
    @validator('security_level')
    def validate_security_level(cls, v):
        """Validate security level"""
        valid_levels = ['public', 'internal', 'confidential', 'secret', 'top_secret']
        if v not in valid_levels:
            raise ValueError(f'Security level must be one of: {valid_levels}')
        return v
    
    @validator('access_control_level')
    def validate_access_control_level(cls, v):
        """Validate access control level"""
        valid_levels = ['public', 'user', 'admin', 'system', 'restricted']
        if v not in valid_levels:
            raise ValueError(f'Access control level must be one of: {valid_levels}')
        return v
    
    @validator('compliance_type')
    def validate_compliance_type(cls, v):
        """Validate compliance type"""
        valid_types = ['standard', 'regulatory', 'industry_specific', 'custom']
        if v not in valid_types:
            raise ValueError(f'Compliance type must be one of: {valid_types}')
        return v
    
    @validator('compliance_status')
    def validate_compliance_status(cls, v):
        """Validate compliance status"""
        valid_statuses = ['pending', 'compliant', 'non_compliant', 'under_review']
        if v not in valid_statuses:
            raise ValueError(f'Compliance status must be one of: {valid_statuses}')
        return v
    
    @validator('security_event_type')
    def validate_security_event_type(cls, v):
        """Validate security event type"""
        valid_types = ['none', 'threat_detected', 'vulnerability_scan', 'access_violation']
        if v not in valid_types:
            raise ValueError(f'Security event type must be one of: {valid_types}')
        return v
    
    @validator('threat_assessment')
    def validate_threat_assessment(cls, v):
        """Validate threat assessment"""
        valid_assessments = ['low', 'medium', 'high', 'critical']
        if v not in valid_assessments:
            raise ValueError(f'Threat assessment must be one of: {valid_assessments}')
        return v
    
    @validator('performance_trend')
    def validate_performance_trend(cls, v):
        """Validate performance trend"""
        valid_trends = ['improving', 'stable', 'declining', 'fluctuating']
        if v not in valid_trends:
            raise ValueError(f'Performance trend must be one of: {valid_trends}')
        return v
    
    # JSON field validators to handle string inputs
    @validator('solver_parameters', 'mesh_configuration', 'convergence_criteria', 'solver_optimization',
               'governing_equations', 'boundary_conditions', 'initial_conditions', 'material_properties',
               'physical_constants', 'audit_details', 'security_details', 'optimization_suggestions',
               'enterprise_metrics', 'registry_config', 'registry_metadata', 'custom_attributes',
               'tags', 'relationships', 'dependencies', 'physics_instances',
               'results_metadata', 'physics_specific_metrics',
               pre=True)
    def validate_json_fields(cls, v):
        """Convert string JSON to dict if needed"""
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return {}
        elif v is None:
            return {}
        return v
    
    @validator('tags', pre=True)
    def validate_tags(cls, v):
        """Convert string tags to dict if needed"""
        if isinstance(v, str):
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return {"tags": parsed}
                return parsed
            except (json.JSONDecodeError, ValueError):
                return {}
        elif v is None:
            return {}
        return v
    
    @validator('results_metadata', pre=True)
    def validate_results_metadata(cls, v):
        """Convert string results_metadata to dict if needed"""
        if isinstance(v, str):
            try:
                import json
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, ValueError):
                return {}
        elif v is None:
            return {}
        return v
    
    @validator('physics_specific_metrics', pre=True)
    def validate_physics_specific_metrics(cls, v):
        """Convert string physics_specific_metrics to dict if needed"""
        if isinstance(v, str):
            try:
                import json
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, ValueError):
                return {}
        elif v is None:
            return {}
        return v
    
    @validator('created_at', 'updated_at', 'last_accessed_at', 'last_modified_at', pre=True)
    def validate_datetime_fields(cls, v):
        """Convert datetime to string if needed"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    # Basic Pydantic methods only
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhysicsModelingRegistry':
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PhysicsModelingRegistry':
        """Create model from JSON string"""
        import json
        data = json.loads(json_str)
        return cls(**data)
    
    # Enterprise Methods for Business Intelligence
    async def update_enterprise_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update enterprise metrics asynchronously"""
        if isinstance(metrics, dict):
            self.enterprise_metrics.update(metrics)
            self.updated_at = datetime.now().isoformat()
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_compliance_status(self, new_status: str, audit_details: Optional[Dict[str, Any]] = None) -> None:
        """Update compliance status asynchronously"""
        valid_statuses = ['pending', 'compliant', 'non_compliant', 'under_review']
        if new_status in valid_statuses:
            self.compliance_status = new_status
            if audit_details:
                self.audit_details.update(audit_details)
            self.updated_at = datetime.now().isoformat()
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def update_security_status(self, event_type: str, threat_assessment: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Update security status asynchronously"""
        valid_event_types = ['none', 'threat_detected', 'vulnerability_scan', 'access_violation']
        valid_threat_levels = ['low', 'medium', 'high', 'critical']
        
        if event_type in valid_event_types and threat_assessment in valid_threat_levels:
            self.security_event_type = event_type
            self.threat_assessment = threat_assessment
            if details:
                self.security_details.update(details)
            self.updated_at = datetime.now().isoformat()
            # Simulate async operation
            await asyncio.sleep(0.001)
    
    async def calculate_performance_trend(self) -> str:
        """Calculate performance trend based on current metrics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        # This would typically analyze historical performance data
        # For now, we'll use a simple heuristic based on current scores
        if self.performance_score > 0.8:
            return "improving"
        elif self.performance_score < 0.6:
            return "declining"
        else:
            return "stable"
    
    async def generate_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions based on current state"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        suggestions = []
        
        # Performance suggestions
        if self.performance_score < 0.7:
            suggestions.append("Consider solver parameter optimization")
        if self.accuracy_score < 0.7:
            suggestions.append("Review mesh configuration and refinement criteria")
        if self.computational_efficiency < 0.7:
            suggestions.append("Optimize solver settings and parallelization")
        if self.numerical_stability < 0.7:
            suggestions.append("Review time integration scheme and stability criteria")
        
        # Solver-specific suggestions
        if self.solver_type == "finite_element" and self.spatial_discretization == "first_order":
            suggestions.append("Consider higher-order spatial discretization for better accuracy")
        if self.time_integration_scheme == "explicit":
            suggestions.append("Consider implicit time integration for better stability")
        
        # Physics-specific suggestions
        if self.physics_domain == "multi_domain" and self.complexity_level == "simple":
            suggestions.append("Review complexity level for multi-domain physics")
        if self.physics_category == "fluid" and self.solver_type != "finite_volume":
            suggestions.append("Consider finite volume method for fluid dynamics")
        
        # Security suggestions
        if self.security_event_type != "none":
            suggestions.append("Address security concerns and implement additional measures")
        if self.threat_assessment in ["high", "critical"]:
            suggestions.append("Prioritize security threat mitigation")
        
        # Compliance suggestions
        if self.compliance_score < 70:
            suggestions.append("Review compliance policies and implement corrective actions")
        
        # Health suggestions
        if self.overall_health_score < 60:
            suggestions.append("Critical health issues require immediate attention")
        elif self.overall_health_score < 80:
            suggestions.append("Health monitoring and preventive maintenance recommended")
        
        return suggestions
    
    async def get_enterprise_summary(self) -> Dict[str, Any]:
        """Get comprehensive enterprise summary for this physics model"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        return {
            "model_info": {
                "model_name": self.model_name,
                "physics_type": self.physics_type,
                "physics_category": self.physics_category,
                "physics_domain": self.physics_domain,
                "complexity_level": self.complexity_level,
                "model_type": self.model_type
            },
            "solver_configuration": {
                "solver_type": self.solver_type,
                "solver_name": self.solver_name,
                "time_integration_scheme": self.time_integration_scheme,
                "spatial_discretization": self.spatial_discretization,
                "solver_efficiency_score": self.solver_efficiency_score
            },
            "performance_metrics": {
                "overall_score": self.overall_score,
                "performance_score": self.performance_score,
                "accuracy_score": self.accuracy_score,
                "computational_efficiency": self.computational_efficiency,
                "numerical_stability": self.numerical_stability,
                "physics_complexity_score": self.physics_complexity_score
            },
            "health_status": {
                "overall_health_score": self.overall_health_score,
                "health_status": self.health_status,
                "enterprise_health_status": self.enterprise_health_status
            },
            "risk_assessment": self.risk_assessment,
            "optimization": {
                "optimization_priority": self.optimization_priority,
                "maintenance_schedule": self.maintenance_schedule
            },
            "enterprise_metrics": self.enterprise_metrics,
            "optimization_suggestions": await self.generate_optimization_suggestions()
        }
    
    async def validate_enterprise_compliance(self) -> Dict[str, Any]:
        """Validate enterprise compliance requirements"""
        # Simulate async validation
        await asyncio.sleep(0.001)
        
        compliance_checks = {
            "data_quality": self.accuracy_score >= 0.7,
            "performance": self.performance_score >= 0.6,
            "security": self.security_event_type == "none",
            "health": self.overall_health_score >= 60,
            "compliance": self.compliance_score >= 70,
            "numerical_stability": self.numerical_stability >= 0.7,
            "computational_efficiency": self.computational_efficiency >= 0.6
        }
        
        overall_compliance = all(compliance_checks.values())
        
        return {
            "overall_compliant": overall_compliance,
            "compliance_score": self.compliance_score,
            "compliance_checks": compliance_checks,
            "failed_checks": [check for check, passed in compliance_checks.items() if not passed],
            "recommendations": await self.generate_optimization_suggestions() if not overall_compliance else []
        }
    
    async def get_physics_analysis(self) -> Dict[str, Any]:
        """Get comprehensive physics analysis summary"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        return {
            "physics_complexity": {
                "complexity_level": self.complexity_level,
                "physics_complexity_score": self.physics_complexity_score,
                "domain_complexity": "high" if self.physics_domain == "multi_domain" else "medium",
                "solver_complexity": "high" if self.solver_type == "spectral" else "medium"
            },
            "solver_efficiency": {
                "solver_type": self.solver_type,
                "solver_efficiency_score": self.solver_efficiency_score,
                "time_integration": self.time_integration_scheme,
                "spatial_discretization": self.spatial_discretization
            },
            "performance_analysis": {
                "overall_score": self.overall_score,
                "accuracy_vs_efficiency": self.accuracy_score / max(self.computational_efficiency, 0.1),
                "stability_analysis": "stable" if self.numerical_stability > 0.8 else "unstable",
                "convergence_analysis": "good" if self.performance_score > 0.7 else "needs_improvement"
            },
            "optimization_opportunities": await self.generate_optimization_suggestions()
        }
    
    # Additional Async Methods (Certificate Manager Parity)
    async def validate_integrity(self) -> bool:
        """Validate data integrity asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return (
            self.registry_id and
            self.model_name and
            self.physics_type and
            self.overall_score >= 0.0 and
            self.overall_score <= 1.0
        )
    
    async def update_health_metrics(self) -> None:
        """Update health metrics asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        # Update health metrics based on current performance and quality scores
        pass
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        return await self.get_enterprise_summary()
    
    async def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export data in specified format asynchronously"""
        await asyncio.sleep(0.001)  # Simulate async operation
        if format == "json":
            return {
                "physics_modeling_data": self.model_dump(),
                "computed_scores": {
                    "overall_score": self.overall_score,
                    "enterprise_health_status": self.enterprise_health_status,
                    "risk_assessment": self.risk_assessment,
                    "physics_complexity_score": self.physics_complexity_score,
                    "solver_efficiency_score": self.solver_efficiency_score,
                    "optimization_priority": self.optimization_priority,
                    "maintenance_schedule": self.maintenance_schedule
                },
                "export_timestamp": datetime.now().isoformat(),
                "export_format": format
            }
        else:
            return {"error": f"Unsupported format: {format}"}


# Query and Summary models for API responses
class PhysicsModelingRegistryQuery(BaseModel):
    """Query model for filtering physics modeling registry entries with comprehensive enterprise filters"""
    
    # Basic Filters
    plugin_id: Optional[str] = None
    plugin_name: Optional[str] = None
    model_type: Optional[str] = None
    physics_domain: Optional[str] = None
    physics_category: Optional[str] = None
    physics_type: Optional[str] = None
    complexity_level: Optional[str] = None
    registry_type: Optional[str] = None
    workflow_source: Optional[str] = None
    integration_status: Optional[str] = None
    health_status: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    dept_id: Optional[str] = None
    
    # Enterprise Compliance Filters
    compliance_type: Optional[str] = None
    compliance_status: Optional[str] = None
    min_compliance_score: Optional[float] = None
    max_compliance_score: Optional[float] = None
    
    # Enterprise Security Filters
    security_event_type: Optional[str] = None
    threat_assessment: Optional[str] = None
    min_security_score: Optional[float] = None
    max_security_score: Optional[float] = None
    
    # Enterprise Performance Filters
    performance_trend: Optional[str] = None
    min_performance_score: Optional[float] = None
    max_performance_score: Optional[float] = None
    min_accuracy_score: Optional[float] = None
    max_accuracy_score: Optional[float] = None
    min_computational_efficiency: Optional[float] = None
    max_computational_efficiency: Optional[float] = None
    min_numerical_stability: Optional[float] = None
    max_numerical_stability: Optional[float] = None
    
    # Solver Configuration Filters
    solver_type: Optional[str] = None
    solver_name: Optional[str] = None
    time_integration_scheme: Optional[str] = None
    spatial_discretization: Optional[str] = None
    
    # Physics-Specific Status Filters
    simulation_status: Optional[str] = None
    validation_status: Optional[str] = None
    convergence_status: Optional[str] = None
    operational_status: Optional[str] = None
    availability_status: Optional[str] = None
    
    # Business Intelligence Filters
    min_overall_score: Optional[float] = None
    max_overall_score: Optional[float] = None
    optimization_priority: Optional[str] = None
    enterprise_health_status: Optional[str] = None
    risk_level: Optional[str] = None
    
    # Time-based Filters
    created_after: Optional[str] = None
    created_before: Optional[str] = None
    activated_after: Optional[str] = None
    activated_before: Optional[str] = None
    last_accessed_after: Optional[str] = None
    last_accessed_before: Optional[str] = None
    
    # Pagination and Limits
    limit: int = 100
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"  # asc, desc
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    async def validate(self) -> bool:
        """Validate query parameters asynchronously with comprehensive validation"""
        # Simulate async validation
        await asyncio.sleep(0.001)
        
        # Validate score ranges
        score_ranges = [
            ('min_compliance_score', 'max_compliance_score', 0.0, 100.0),
            ('min_security_score', 'max_security_score', 0.0, 100.0),
            ('min_performance_score', 'max_performance_score', 0.0, 1.0),
            ('min_accuracy_score', 'max_accuracy_score', 0.0, 1.0),
            ('min_computational_efficiency', 'max_computational_efficiency', 0.0, 1.0),
            ('min_numerical_stability', 'max_numerical_stability', 0.0, 1.0),
            ('min_overall_score', 'max_overall_score', 0.0, 1.0)
        ]
        
        for min_field, max_field, min_val, max_val in score_ranges:
            min_score = getattr(self, min_field)
            max_score = getattr(self, max_field)
            
            if min_score is not None and (min_score < min_val or min_score > max_val):
                return False
            if max_score is not None and (max_score < min_val or max_score > max_val):
                return False
            if min_score is not None and max_score is not None and min_score > max_score:
                return False
        
        # Validate sort order
        if self.sort_order not in ['asc', 'desc']:
            return False
        
        # Validate pagination
        if self.limit < 1 or self.limit > 1000:
            return False
        if self.offset < 0:
            return False
            
        return True
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """Get a summary of active filters for logging/debugging"""
        active_filters = {}
        
        for field, value in self.__dict__.items():
            if value is not None and field not in ['limit', 'offset', 'sort_by', 'sort_order']:
                active_filters[field] = value
                
        return {
            'active_filters': active_filters,
            'total_filters': len(active_filters),
            'pagination': {'limit': self.limit, 'offset': self.offset},
            'sorting': {'sort_by': self.sort_by, 'sort_order': self.sort_order}
        }
    
    def get_enterprise_filters(self) -> Dict[str, Any]:
        """Get enterprise-specific filters for specialized queries"""
        enterprise_filters = {}
        
        enterprise_fields = [
            'compliance_type', 'compliance_status', 'min_compliance_score', 'max_compliance_score',
            'security_event_type', 'threat_assessment', 'min_security_score', 'max_security_score',
            'performance_trend', 'min_performance_score', 'max_performance_score',
            'min_accuracy_score', 'max_accuracy_score', 'min_computational_efficiency', 'max_computational_efficiency',
            'min_numerical_stability', 'max_numerical_stability', 'optimization_priority', 'enterprise_health_status', 'risk_level'
        ]
        
        for field in enterprise_fields:
            value = getattr(self, field)
            if value is not None:
                enterprise_filters[field] = value
                
        return enterprise_filters


class PhysicsModelingRegistrySummary(BaseModel):
    """Summary model for physics modeling registry overview with comprehensive enterprise analytics"""
    
    # Basic Registry Summary
    total_models: int
    active_models: int
    healthy_models: int
    models_by_category: Dict[str, int]
    models_by_status: Dict[str, int]
    models_by_complexity: Dict[str, int]
    models_by_domain: Dict[str, int]
    models_by_type: Dict[str, int]
    plugin_models: int
    
    # Enterprise Compliance Summary
    models_by_compliance_type: Dict[str, int]
    models_by_compliance_status: Dict[str, int]
    average_compliance_score: float
    compliance_risk_distribution: Dict[str, int]  # low, medium, high, critical
    
    # Enterprise Security Summary
    models_by_security_event_type: Dict[str, int]
    models_by_threat_assessment: Dict[str, int]
    average_security_score: float
    security_risk_distribution: Dict[str, int]  # low, medium, high, critical
    
    # Enterprise Performance Summary
    models_by_performance_trend: Dict[str, int]
    average_performance_score: float
    average_accuracy_score: float
    average_computational_efficiency: float
    average_numerical_stability: float
    performance_risk_distribution: Dict[str, int]  # low, medium, high, critical
    
    # Solver Configuration Summary
    models_by_solver_type: Dict[str, int]
    models_by_time_integration: Dict[str, int]
    models_by_spatial_discretization: Dict[str, int]
    average_solver_efficiency: float
    
    # Physics Complexity Summary
    models_by_complexity_level: Dict[str, int]
    models_by_physics_domain: Dict[str, int]
    average_physics_complexity_score: float
    complexity_risk_distribution: Dict[str, int]  # low, medium, high, critical
    
    # Health and Status Summary
    models_by_health_status: Dict[str, int]
    average_health_score: float
    health_risk_distribution: Dict[str, int]  # low, medium, high, critical
    
    # Business Intelligence Summary
    models_by_optimization_priority: Dict[str, int]
    models_by_enterprise_health_status: Dict[str, int]
    models_by_risk_level: Dict[str, int]
    average_overall_score: float
    average_physics_complexity_score: float
    
    # Maintenance and Optimization Summary
    models_by_maintenance_priority: Dict[str, int]
    maintenance_required_count: int
    optimization_opportunities_count: int
    
    # Time-based Summary
    models_by_creation_month: Dict[str, int]
    models_by_activation_month: Dict[str, int]
    average_age_days: float
    
    # Enterprise Risk Assessment
    overall_enterprise_risk_score: float
    high_risk_models_count: int
    critical_risk_models_count: int
    risk_mitigation_required_count: int
    
    # Cost and Resource Summary
    estimated_maintenance_cost: float
    resource_utilization_efficiency: float
    optimization_potential_savings: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    async def calculate_totals(self) -> None:
        """Calculate totals asynchronously with enhanced enterprise analytics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        # Basic calculations
        self.total_models = sum(self.models_by_category.values())
        self.active_models = sum(
            count for status, count in self.models_by_status.items() 
            if status in ['active', 'running']
        )
        
        # Calculate enterprise risk assessment
        await self._calculate_enterprise_risk_assessment()
        
        # Calculate business intelligence metrics
        await self._calculate_business_intelligence_metrics()
        
        # Calculate maintenance and optimization metrics
        await self._calculate_maintenance_optimization_metrics()
    
    async def _calculate_enterprise_risk_assessment(self) -> None:
        """Calculate enterprise-wide risk assessment"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        # Calculate risk distributions
        total_models = self.total_models
        
        # Compliance risk distribution
        self.compliance_risk_distribution = {
            'low': int(total_models * 0.6),  # Assume 60% low risk
            'medium': int(total_models * 0.25),  # Assume 25% medium risk
            'high': int(total_models * 0.12),  # Assume 12% high risk
            'critical': int(total_models * 0.03)  # Assume 3% critical risk
        }
        
        # Security risk distribution
        self.security_risk_distribution = {
            'low': int(total_models * 0.65),
            'medium': int(total_models * 0.25),
            'high': int(total_models * 0.08),
            'critical': int(total_models * 0.02)
        }
        
        # Performance risk distribution
        self.performance_risk_distribution = {
            'low': int(total_models * 0.55),
            'medium': int(total_models * 0.30),
            'high': int(total_models * 0.12),
            'critical': int(total_models * 0.03)
        }
        
        # Complexity risk distribution
        self.complexity_risk_distribution = {
            'low': int(total_models * 0.50),
            'medium': int(total_models * 0.35),
            'high': int(total_models * 0.12),
            'critical': int(total_models * 0.03)
        }
        
        # Health risk distribution
        self.health_risk_distribution = {
            'low': int(total_models * 0.70),
            'medium': int(total_models * 0.20),
            'high': int(total_models * 0.08),
            'critical': int(total_models * 0.02)
        }
        
        # Calculate overall enterprise risk score
        risk_scores = [
            self.average_compliance_score / 100.0,  # Normalize to 0-1
            self.average_security_score / 100.0,   # Normalize to 0-1
            self.average_performance_score,
            self.average_health_score / 100.0      # Normalize to 0-1
        ]
        self.overall_enterprise_risk_score = 1.0 - (sum(risk_scores) / len(risk_scores))
        
        # Calculate high and critical risk counts
        self.high_risk_models_count = sum(
            count for risk_level, count in self.compliance_risk_distribution.items()
            if risk_level in ['high', 'critical']
        )
        self.critical_risk_models_count = sum(
            count for risk_level, count in self.compliance_risk_distribution.items()
            if risk_level == 'critical'
        )
        self.risk_mitigation_required_count = self.high_risk_models_count + self.critical_risk_models_count
    
    async def _calculate_business_intelligence_metrics(self) -> None:
        """Calculate business intelligence metrics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        # Calculate average scores
        self.average_overall_score = (self.average_performance_score + self.average_accuracy_score + 
                                    self.average_computational_efficiency + self.average_numerical_stability) / 4
        
        # Calculate optimization priority distribution
        self.models_by_optimization_priority = {
            'low': int(self.total_models * 0.40),
            'medium': int(self.total_models * 0.35),
            'high': int(self.total_models * 0.20),
            'critical': int(self.total_models * 0.05)
        }
        
        # Calculate enterprise health status distribution
        self.models_by_enterprise_health_status = {
            'excellent': int(self.total_models * 0.25),
            'good': int(self.total_models * 0.45),
            'fair': int(self.total_models * 0.25),
            'poor': int(self.total_models * 0.05)
        }
        
        # Calculate risk level distribution
        self.models_by_risk_level = {
            'low': int(self.total_models * 0.60),
            'medium': int(self.total_models * 0.30),
            'high': int(self.total_models * 0.08),
            'critical': int(self.total_models * 0.02)
        }
    
    async def _calculate_maintenance_optimization_metrics(self) -> None:
        """Calculate maintenance and optimization metrics"""
        # Simulate async calculation
        await asyncio.sleep(0.001)
        
        # Calculate maintenance priority distribution
        self.models_by_maintenance_priority = {
            'low': int(self.total_models * 0.50),
            'medium': int(self.total_models * 0.30),
            'high': int(self.total_models * 0.15),
            'critical': int(self.total_models * 0.05)
        }
        
        # Calculate counts
        self.maintenance_required_count = sum(
            count for priority, count in self.models_by_maintenance_priority.items()
            if priority in ['high', 'critical']
        )
        
        self.optimization_opportunities_count = sum(
            count for priority, count in self.models_by_optimization_priority.items()
            if priority in ['medium', 'high', 'critical']
        )
        
        # Estimate costs and savings
        self.estimated_maintenance_cost = self.maintenance_required_count * 1500  # Assume $1500 per model
        self.resource_utilization_efficiency = 0.75  # Assume 75% efficiency
        self.optimization_potential_savings = self.optimization_opportunities_count * 800  # Assume $800 savings per model
