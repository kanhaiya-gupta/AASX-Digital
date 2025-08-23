"""
Knowledge Graph Neo4j ML Registry Model

Updated to match our comprehensive database schema with all fields.
Supports ML training status and model management for knowledge graphs.
"""

from src.engine.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid


class KGNeo4jMLRegistry(BaseModel):
    """ML training registry model for knowledge graphs with Neo4j integration"""
    
    # Primary Identification
    ml_registry_id: str
    graph_id: str
    model_id: str
    session_id: str
    
    # Model Metadata (NO raw data - only metadata)
    model_name: str
    model_type: str  # node_classification, link_prediction, community_detection, anomaly_detection, graph_embedding, gnn, hybrid
    model_version: str = "1.0.0"
    model_architecture: Optional[str] = None
    model_framework: Optional[str] = None  # PyTorch, TensorFlow, etc.
    
    # Training Session Metadata (NO raw data - only metadata)
    training_status: str = "pending"  # pending, in_progress, completed, failed, cancelled, paused
    training_type: str = "supervised"  # supervised, unsupervised, semi_supervised, reinforcement, transfer
    training_algorithm: Optional[str] = None
    training_parameters: Dict[str, Any] = {}  # JSON: hyperparameters, learning rate, etc.
    
    # External Storage References (NO data storage - only file paths)
    model_file_path: Optional[str] = None
    config_file_path: Optional[str] = None
    dataset_path: Optional[str] = None
    logs_path: Optional[str] = None
    performance_logs_path: Optional[str] = None
    deployment_config_path: Optional[str] = None
    
    # Training Performance Summary (NO raw data - only summary metrics)
    final_accuracy: Optional[float] = None
    training_duration_seconds: Optional[int] = None
    resource_consumption: Dict[str, Any] = {}  # JSON: CPU, memory, GPU usage summary
    training_efficiency_score: Optional[float] = None
    
    # Model Performance Metrics (NO raw data - only summary metrics)
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    f1_score: Optional[float] = None
    auc_score: Optional[float] = None
    
    # Training Data Metadata (NO raw data - only metadata)
    dataset_size: Optional[int] = None
    feature_count: Optional[int] = None
    data_quality_score: Optional[float] = None
    data_split_ratio: str = "0.7:0.2:0.1"  # Train:Validation:Test split
    
    # Model Deployment & Usage (NO raw data - only metadata)
    deployment_status: str = "not_deployed"  # not_deployed, deployed, active, inactive, deprecated
    deployment_date: Optional[datetime] = None
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    
    # Integration References (Links to other modules - NO data duplication)
    aasx_integration_id: Optional[str] = None
    twin_registry_id: Optional[str] = None
    physics_modeling_id: Optional[str] = None
    federated_learning_id: Optional[str] = None
    ai_rag_id: Optional[str] = None
    certificate_manager_id: Optional[str] = None
    
    # Quality & Governance (NO raw data - only metadata)
    model_quality_score: Optional[float] = None
    validation_status: str = "pending"  # pending, validated, failed, requires_review
    compliance_score: Optional[float] = None
    bias_detection_score: Optional[float] = None
    
    # Lifecycle Management (NO raw data - only metadata)
    lifecycle_status: str = "development"  # development, testing, production, maintenance, deprecated
    lifecycle_phase: str = "training"  # training, validation, deployment, monitoring, retirement
    
    # User Management & Ownership (NO raw data - only metadata)
    user_id: str
    org_id: str
    dept_id: Optional[str] = None
    owner_team: Optional[str] = None
    steward_user_id: Optional[str] = None
    
    # Timestamps & Audit (NO raw data - only metadata)
    created_at: datetime
    updated_at: datetime
    training_started_at: Optional[datetime] = None
    training_completed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    
    # Configuration & Metadata (JSON fields for flexibility - NO raw data)
    ml_config: Dict[str, Any] = {}
    model_metadata: Dict[str, Any] = {}
    custom_attributes: Dict[str, Any] = {}
    tags: List[str] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
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
    
    async def update_training_status(self, status: str, **kwargs) -> None:
        """Update training status asynchronously"""
        self.training_status = status
        self.updated_at = datetime.now(timezone.utc)
        
        # Update related timestamps
        if status == "in_progress" and not self.training_started_at:
            self.training_started_at = datetime.now(timezone.utc)
        elif status == "completed" and not self.training_completed_at:
            self.training_completed_at = datetime.now(timezone.utc)
        
        # Update any additional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    async def update_performance_metrics(
        self,
        accuracy: float,
        precision: float,
        recall: float,
        f1: float,
        auc: Optional[float] = None
    ) -> None:
        """Update model performance metrics asynchronously"""
        self.final_accuracy = max(0.0, min(1.0, accuracy))
        self.precision_score = max(0.0, min(1.0, precision))
        self.recall_score = max(0.0, min(1.0, recall))
        self.f1_score = max(0.0, min(1.0, f1))
        if auc is not None:
            self.auc_score = max(0.0, min(1.0, auc))
        
        self.updated_at = datetime.now(timezone.utc)
    
    async def update_deployment_status(self, status: str, deployment_date: Optional[datetime] = None) -> None:
        """Update deployment status asynchronously"""
        self.deployment_status = status
        if deployment_date:
            self.deployment_date = deployment_date
        elif status == "deployed" and not self.deployment_date:
            self.deployment_date = datetime.now(timezone.utc)
        
        self.updated_at = datetime.now(timezone.utc)
    
    async def increment_usage(self) -> None:
        """Increment usage count asynchronously"""
        self.usage_count += 1
        self.last_used_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    async def update_quality_scores(
        self,
        model_quality: float,
        compliance: float,
        bias_detection: float
    ) -> None:
        """Update quality and governance scores asynchronously"""
        self.model_quality_score = max(0.0, min(1.0, model_quality))
        self.compliance_score = max(0.0, min(1.0, compliance))
        self.bias_detection_score = max(0.0, min(1.0, bias_detection))
        
        self.updated_at = datetime.now(timezone.utc)
    
    async def add_tag(self, tag: str) -> None:
        """Add a tag asynchronously"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(timezone.utc)
    
    async def remove_tag(self, tag: str) -> None:
        """Remove a tag asynchronously"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now(timezone.utc)
    
    async def update_custom_attribute(self, key: str, value: Any) -> None:
        """Update custom attribute asynchronously"""
        self.custom_attributes[key] = value
        self.updated_at = datetime.now(timezone.utc)
    
    @classmethod
    async def create_for_node_classification(
        cls,
        graph_id: str,
        model_name: str,
        user_id: str,
        org_id: str,
        dept_id: Optional[str] = None,
        **kwargs
    ) -> "KGNeo4jMLRegistry":
        """Create ML registry entry for node classification asynchronously"""
        return cls(
            graph_id=graph_id,
            model_name=model_name,
            model_id=f"node_clf_{uuid.uuid4().hex[:8]}",
            session_id=f"session_{uuid.uuid4().hex[:8]}",
            model_type="node_classification",
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            **kwargs
        )
    
    @classmethod
    async def create_for_link_prediction(
        cls,
        graph_id: str,
        model_name: str,
        user_id: str,
        org_id: str,
        dept_id: Optional[str] = None,
        **kwargs
    ) -> "KGNeo4jMLRegistry":
        """Create ML registry entry for link prediction asynchronously"""
        return cls(
            graph_id=graph_id,
            model_name=model_name,
            model_id=f"link_pred_{uuid.uuid4().hex[:8]}",
            session_id=f"session_{uuid.uuid4().hex[:8]}",
            model_type="link_prediction",
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            **kwargs
        )
    
    @classmethod
    async def create_for_graph_embedding(
        cls,
        graph_id: str,
        model_name: str,
        user_id: str,
        org_id: str,
        dept_id: Optional[str] = None,
        **kwargs
    ) -> "KGNeo4jMLRegistry":
        """Create ML registry entry for graph embedding asynchronously"""
        return cls(
            graph_id=graph_id,
            model_name=model_name,
            model_id=f"embed_{uuid.uuid4().hex[:8]}",
            session_id=f"session_{uuid.uuid4().hex[:8]}",
            model_type="graph_embedding",
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            **kwargs
        )


# Query and Summary models for API responses
class KGNeo4jMLRegistryQuery(BaseModel):
    """Query model for filtering ML registry entries"""
    graph_id: Optional[str] = None
    model_type: Optional[str] = None
    training_status: Optional[str] = None
    deployment_status: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    dept_id: Optional[str] = None
    limit: int = 100
    offset: int = 0


class KGNeo4jMLRegistrySummary(BaseModel):
    """Summary model for ML registry overview"""
    total_models: int
    active_training_sessions: int
    completed_models: int
    deployed_models: int
    avg_model_accuracy: float
    avg_training_duration: float
    model_type_distribution: Dict[str, int]
    training_success_rate: float
