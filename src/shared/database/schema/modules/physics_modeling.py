"""
Physics Modeling Schema Module
==============================

Manages Physics Modeling database tables for the AASX Digital Twin Framework.
Provides comprehensive physics modeling, machine learning integration (PINNs), and performance monitoring
with metadata and references only - no raw data storage to prevent database explosion.
"""

import logging
from typing import List, Dict, Any
from ..base_schema import BaseSchemaModule

logger = logging.getLogger(__name__)


class PhysicsModelingSchema(BaseSchemaModule):
    """
    Physics Modeling Schema Module

    Manages the following tables:
    - physics_modeling_registry: Traditional physics models, equations, and solver configurations
    - physics_ml_registry: Machine learning models (PINNs, neural networks) for physics
    - physics_modeling_metrics: Unified performance metrics for both traditional and ML models
    """

    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.module_name = "physics_modeling"

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Physics Modeling module for traditional physics simulations and machine learning integration (PINNs) with comprehensive performance tracking"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["physics_modeling_registry", "physics_ml_registry", "physics_modeling_metrics"]

    def create_tables(self) -> bool:
        """
        Create all Physics Modeling tables.

        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        logger.info("🔬 Creating Physics Modeling Module Tables...")

        # Create tables in dependency order
        tables_created = []

        # 1. Create Physics Modeling Registry Table (no dependencies)
        if self._create_physics_modeling_registry_table():
            tables_created.append("physics_modeling_registry")
        else:
            logger.error("Failed to create physics_modeling_registry table")
            return False

        # 2. Create Physics ML Registry Table (depends on physics modeling registry)
        if self._create_physics_ml_registry_table():
            tables_created.append("physics_ml_registry")
        else:
            logger.error("Failed to create physics_ml_registry table")
            return False

        # 3. Create Physics Modeling Metrics Table (depends on both registries)
        if self._create_physics_modeling_metrics_table():
            tables_created.append("physics_modeling_metrics")
        else:
            logger.error("Failed to create physics_modeling_metrics table")
            return False

        logger.info(f"✅ Physics Modeling Module: Created {len(tables_created)} tables successfully")
        return True

    def _create_physics_modeling_registry_table(self) -> bool:
        """Create the physics_modeling_registry table for traditional physics models."""
        query = """
            CREATE TABLE IF NOT EXISTS physics_modeling_registry (
                -- Primary Identification
                registry_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                physics_type TEXT NOT NULL,
                
                -- Physics Classification & Metadata
                physics_category TEXT NOT NULL DEFAULT 'structural' -- structural, thermal, fluid, electromagnetic, multi_physics, acoustics, quantum
                    CHECK (physics_category IN ('structural', 'thermal', 'fluid', 'electromagnetic', 'multi_physics', 'acoustics', 'quantum')),
                physics_subcategory TEXT, -- e.g., linear_elastic, non_linear_plastic, laminar_flow, turbulent_flow
                complexity_level TEXT NOT NULL DEFAULT 'medium' -- simple, medium, complex, very_complex
                    CHECK (complexity_level IN ('simple', 'medium', 'complex', 'very_complex')),
                physics_version TEXT NOT NULL DEFAULT '1.0.0', -- Semantic versioning
                
                -- Workflow Classification (CRITICAL for dual workflow support)
                registry_type TEXT NOT NULL -- extraction, generation, hybrid
                    CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                workflow_source TEXT NOT NULL -- aasx_file, structured_data, both
                    CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                
                -- Traditional Solver Configuration
                solver_type TEXT NOT NULL DEFAULT 'finite_element' -- finite_element, finite_difference, finite_volume, boundary_element, spectral
                    CHECK (solver_type IN ('finite_element', 'finite_difference', 'finite_volume', 'boundary_element', 'spectral')),
                solver_parameters TEXT DEFAULT '{}', -- JSON: solver-specific parameters
                mesh_configuration TEXT DEFAULT '{}', -- JSON: mesh settings, element types, refinement criteria
                
                -- Physics Equations & Constraints
                governing_equations TEXT DEFAULT '[]', -- JSON array of governing equations
                boundary_conditions TEXT DEFAULT '{}', -- JSON: boundary condition definitions
                initial_conditions TEXT DEFAULT '{}', -- JSON: initial condition specifications
                material_properties TEXT DEFAULT '{}', -- JSON: material property definitions
                physical_constants TEXT DEFAULT '{}', -- JSON: physical constants and parameters
                
                -- Module Integration References (Links to other modules - NO data duplication)
                aasx_integration_id TEXT, -- Reference to aasx_processing table
                twin_registry_id TEXT, -- Reference to twin_registry table
                kg_neo4j_id TEXT, -- Reference to kg_graph_registry table
                ai_rag_id TEXT, -- Reference to ai_rag_registry table
                federated_learning_id TEXT, -- Reference to federated_learning_registry table
                certificate_manager_id TEXT, -- Reference to certificate module
                
                -- Integration Status & Health
                integration_status TEXT NOT NULL DEFAULT 'pending' -- pending, active, inactive, error, maintenance, deprecated
                    CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')),
                overall_health_score INTEGER DEFAULT 0 -- 0-100 health score across all modules
                    CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
                health_status TEXT NOT NULL DEFAULT 'unknown' -- unknown, healthy, warning, critical, offline
                    CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')),
                
                -- Lifecycle Management
                lifecycle_status TEXT NOT NULL DEFAULT 'created' -- created, active, suspended, archived, retired
                    CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')),
                lifecycle_phase TEXT NOT NULL DEFAULT 'setup' -- setup, validation, deployment, monitoring, maintenance
                    CHECK (lifecycle_phase IN ('setup', 'validation', 'deployment', 'monitoring', 'maintenance')),
                
                -- Operational Status
                operational_status TEXT NOT NULL DEFAULT 'stopped' -- running, stopped, paused, error, maintenance
                    CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')),
                availability_status TEXT NOT NULL DEFAULT 'offline' -- online, offline, degraded, maintenance
                    CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')),
                
                -- Physics-Specific Status
                simulation_status TEXT DEFAULT 'pending' -- pending, running, completed, failed, paused
                    CHECK (simulation_status IN ('pending', 'running', 'completed', 'failed', 'paused')),
                validation_status TEXT DEFAULT 'pending' -- pending, in_progress, passed, failed, needs_review
                    CHECK (validation_status IN ('pending', 'in_progress', 'passed', 'failed', 'needs_review')),
                convergence_status TEXT DEFAULT 'unknown' -- unknown, converging, converged, diverged, oscillating
                    CHECK (convergence_status IN ('unknown', 'converging', 'converged', 'diverged', 'oscillating')),
                
                -- Performance & Quality Metrics
                performance_score REAL DEFAULT 0.0, -- 0.0-1.0 performance rating
                accuracy_score REAL DEFAULT 0.0, -- 0.0-1.0 accuracy rating
                computational_efficiency REAL DEFAULT 0.0, -- 0.0-1.0 efficiency rating
                numerical_stability REAL DEFAULT 0.0, -- 0.0-1.0 stability rating
                
                -- Security & Access Control
                security_level TEXT NOT NULL DEFAULT 'standard' -- public, internal, confidential, secret, top_secret
                    CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                access_control_level TEXT NOT NULL DEFAULT 'user' -- public, user, admin, system, restricted
                    CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                encryption_enabled BOOLEAN DEFAULT TRUE, -- Whether physics data is encrypted
                audit_logging_enabled BOOLEAN DEFAULT TRUE, -- Whether audit logging is enabled
                
                -- User Management & Ownership
                user_id TEXT NOT NULL, -- Current user who owns/accesses this registry
                org_id TEXT NOT NULL, -- Organization this registry belongs to
                owner_team TEXT, -- Team responsible for this physics model
                steward_user_id TEXT, -- Data steward for this physics model
                
                -- Timestamps & Audit
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                activated_at TEXT, -- When physics model was first activated
                last_accessed_at TEXT, -- Last time any user accessed this physics model
                last_modified_at TEXT, -- Last time physics model data was modified
                
                -- Configuration & Metadata (JSON fields for flexibility)
                registry_config TEXT DEFAULT '{}', -- Registry configuration settings
                registry_metadata TEXT DEFAULT '{}', -- Additional metadata
                custom_attributes TEXT DEFAULT '{}', -- User-defined custom attributes
                tags TEXT DEFAULT '[]', -- JSON array of tags for categorization
                
                -- Relationships & Dependencies (JSON arrays)
                relationships TEXT DEFAULT '[]', -- Array of relationship objects
                dependencies TEXT DEFAULT '[]', -- Array of dependency objects
                physics_instances TEXT DEFAULT '[]', -- Array of physics instance objects
                
                -- Constraints
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry(graph_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not self.create_table("physics_modeling_registry", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_user_id ON physics_modeling_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_org_id ON physics_modeling_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_category ON physics_modeling_registry (physics_category)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_type ON physics_modeling_registry (physics_type)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_solver ON physics_modeling_registry (solver_type)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_complexity ON physics_modeling_registry (complexity_level)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_status ON physics_modeling_registry (integration_status)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_health ON physics_modeling_registry (health_status)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_lifecycle ON physics_modeling_registry (lifecycle_status)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_operational ON physics_modeling_registry (operational_status)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_simulation ON physics_modeling_registry (simulation_status, validation_status, convergence_status)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_performance ON physics_modeling_registry (performance_score, accuracy_score, computational_efficiency)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_created ON physics_modeling_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_updated ON physics_modeling_registry (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_integration ON physics_modeling_registry (aasx_integration_id, twin_registry_id, kg_neo4j_id, ai_rag_id, federated_learning_id, certificate_manager_id)"
        ]

        return self.create_indexes("physics_modeling_registry", index_queries)

    def _create_physics_ml_registry_table(self) -> bool:
        """Create the physics_ml_registry table for machine learning models (PINNs, etc.)."""
        query = """
            CREATE TABLE IF NOT EXISTS physics_ml_registry (
                -- Primary Identification
                ml_registry_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                ml_model_type TEXT NOT NULL DEFAULT 'pinn' -- pinn, neural_ode, graph_neural_network, transformer, hybrid
                    CHECK (ml_model_type IN ('pinn', 'neural_ode', 'graph_neural_network', 'transformer', 'hybrid')),
                
                -- Neural Network Architecture
                nn_architecture TEXT DEFAULT '{}', -- JSON: layer sizes, activation functions, regularization
                activation_functions TEXT DEFAULT '[]', -- JSON array of activation functions
                regularization_methods TEXT DEFAULT '[]', -- JSON array of regularization methods
                dropout_rates TEXT DEFAULT '[]', -- JSON array of dropout rates per layer
                
                -- Training Configuration
                training_parameters TEXT DEFAULT '{}', -- JSON: learning rate, batch size, epochs, optimizer
                loss_function_config TEXT DEFAULT '{}', -- JSON: loss function configuration and weights
                optimization_settings TEXT DEFAULT '{}', -- JSON: optimizer settings, learning rate schedules
                training_data_config TEXT DEFAULT '{}', -- JSON: training data configuration and augmentation
                
                -- Physics Integration
                physics_constraints TEXT DEFAULT '{}', -- JSON: physics constraints and enforcement methods
                conservation_laws TEXT DEFAULT '[]', -- JSON array of conservation laws to enforce
                differential_equations TEXT DEFAULT '[]', -- JSON array of differential equations
                boundary_condition_handling TEXT DEFAULT '{}', -- JSON: boundary condition enforcement
                initial_condition_learning TEXT DEFAULT '{}', -- JSON: initial condition learning configuration
                
                -- Model Performance & Quality
                training_accuracy REAL DEFAULT 0.0, -- 0.0-1.0 training accuracy
                validation_accuracy REAL DEFAULT 0.0, -- 0.0-1.0 validation accuracy
                physics_compliance_score REAL DEFAULT 0.0, -- 0.0-1.0 physics compliance
                generalization_error REAL DEFAULT 0.0, -- 0.0-1.0 generalization error
                overfitting_score REAL DEFAULT 0.0, -- 0.0-1.0 overfitting assessment
                
                -- Integration References
                physics_modeling_id TEXT, -- Reference to physics_modeling_registry table
                aasx_integration_id TEXT, -- Reference to aasx_processing table
                twin_registry_id TEXT, -- Reference to twin_registry table
                kg_neo4j_id TEXT, -- Reference to kg_graph_registry table
                ai_rag_id TEXT, -- Reference to ai_rag_registry table
                federated_learning_id TEXT, -- Reference to federated_learning_registry table
                certificate_manager_id TEXT, -- Reference to certificate module
                
                -- Status & Lifecycle
                training_status TEXT NOT NULL DEFAULT 'pending' -- pending, training, completed, failed, paused
                    CHECK (training_status IN ('pending', 'training', 'completed', 'failed', 'paused')),
                deployment_status TEXT NOT NULL DEFAULT 'not_deployed' -- not_deployed, deployed, serving, error, maintenance
                    CHECK (deployment_status IN ('not_deployed', 'deployed', 'serving', 'error', 'maintenance')),
                model_version TEXT NOT NULL DEFAULT '1.0.0', -- Semantic versioning
                lifecycle_phase TEXT NOT NULL DEFAULT 'development' -- development, training, validation, deployment, monitoring
                    CHECK (lifecycle_phase IN ('development', 'training', 'validation', 'deployment', 'monitoring')),
                
                -- Training History & Metadata
                training_started_at TEXT, -- When training started
                training_completed_at TEXT, -- When training completed
                training_duration_sec REAL, -- Total training duration
                training_iterations INTEGER DEFAULT 0, -- Number of training iterations
                model_checkpoints TEXT DEFAULT '[]', -- JSON array of model checkpoint information
                
                -- User Management & Ownership
                user_id TEXT NOT NULL, -- Current user who owns/accesses this ML model
                org_id TEXT NOT NULL, -- Organization this ML model belongs to
                ml_engineer_id TEXT, -- ML engineer responsible for this model
                data_scientist_id TEXT, -- Data scientist who developed this model
                
                -- Timestamps & Audit
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                last_trained_at TEXT, -- Last time model was trained
                last_deployed_at TEXT, -- Last time model was deployed
                
                -- Configuration & Metadata (JSON fields for flexibility)
                ml_config TEXT DEFAULT '{}', -- ML-specific configuration settings
                ml_metadata TEXT DEFAULT '{}', -- Additional ML metadata
                custom_attributes TEXT DEFAULT '{}', -- User-defined custom attributes
                tags TEXT DEFAULT '[]', -- JSON array of tags for categorization
                
                -- Constraints
                FOREIGN KEY (physics_modeling_id) REFERENCES physics_modeling_registry (registry_id) ON DELETE SET NULL,
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry(registry_id) ON DELETE SET NULL,
                FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry(graph_id) ON DELETE SET NULL
            )
        """

        # Create the table
        if not self.create_table("physics_ml_registry", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_user_id ON physics_ml_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_org_id ON physics_ml_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_type ON physics_ml_registry (ml_model_type)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_physics ON physics_ml_registry (physics_modeling_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_training ON physics_ml_registry (training_status, training_accuracy, validation_accuracy)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_deployment ON physics_ml_registry (deployment_status, model_version)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_lifecycle ON physics_ml_registry (lifecycle_phase)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_performance ON physics_ml_registry (training_accuracy, validation_accuracy, physics_compliance_score)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_created ON physics_ml_registry (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_updated ON physics_ml_registry (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_physics_ml_registry_integration ON physics_ml_registry (physics_modeling_id, aasx_integration_id, twin_registry_id, kg_neo4j_id, ai_rag_id, federated_learning_id, certificate_manager_id)"
        ]

        return self.create_indexes("physics_ml_registry", index_queries)

    def _create_physics_modeling_metrics_table(self) -> bool:
        """Create the physics_modeling_metrics table for unified performance tracking."""
        query = """
            CREATE TABLE IF NOT EXISTS physics_modeling_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                
                -- Model Reference (Links to either traditional or ML registry)
                registry_id TEXT, -- Reference to physics_modeling_registry (traditional)
                ml_registry_id TEXT, -- Reference to physics_ml_registry (ML)
                model_type TEXT NOT NULL -- traditional, ml, hybrid
                    CHECK (model_type IN ('traditional', 'ml', 'hybrid')),
                
                -- Performance Metrics (Unified for both types)
                simulation_duration_sec REAL, -- Time to complete simulation/training
                accuracy_score REAL CHECK (accuracy_score >= 0.0 AND accuracy_score <= 1.0),
                convergence_rate REAL, -- Rate of convergence for traditional models
                error_metrics TEXT DEFAULT '{}', -- JSON: various error metrics
                
                -- Resource Utilization
                cpu_usage_percent REAL CHECK (cpu_usage_percent >= 0.0 AND cpu_usage_percent <= 100.0),
                memory_usage_mb REAL,
                gpu_usage_percent REAL CHECK (gpu_usage_percent >= 0.0 AND gpu_usage_percent <= 100.0),
                storage_usage_mb REAL,
                network_throughput_mbps REAL,
                
                -- Quality Metrics
                numerical_stability REAL CHECK (numerical_stability >= 0.0 AND numerical_stability <= 1.0),
                mesh_quality_score REAL CHECK (mesh_quality_score >= 0.0 AND mesh_quality_score <= 1.0),
                physics_compliance REAL CHECK (physics_compliance >= 0.0 AND physics_compliance <= 1.0),
                generalization_error REAL CHECK (generalization_error >= 0.0 AND generalization_error <= 1.0),
                
                -- Traditional Physics Specific Metrics (JSON for flexibility)
                traditional_metrics TEXT DEFAULT '{}', -- JSON: finite element metrics, solver performance, etc.
                
                -- ML Specific Metrics (JSON for flexibility)
                ml_metrics TEXT DEFAULT '{}', -- JSON: training loss, validation loss, physics loss, etc.
                
                -- Comparative Analysis (Traditional vs ML)
                traditional_vs_ml_performance TEXT DEFAULT '{}', -- JSON: performance comparison metrics
                computational_efficiency_gain REAL, -- Efficiency improvement over traditional methods
                accuracy_improvement REAL, -- Accuracy improvement over traditional methods
                data_requirement_reduction REAL, -- Reduction in training data requirements
                
                -- Time-based Analytics
                hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
                                 day_of_week INTEGER CHECK (day_of_week >= 1 AND day_of_week <= 7),
                month INTEGER CHECK (month >= 1 AND month <= 12),
                
                -- Performance Trends
                performance_trend REAL, -- Compared to historical average
                efficiency_trend REAL, -- Performance over time
                quality_trend REAL, -- Quality metrics over time
                
                -- Constraints (Ensure at least one registry reference exists)
                CHECK ((registry_id IS NOT NULL AND ml_registry_id IS NULL) OR 
                       (registry_id IS NULL AND ml_registry_id IS NOT NULL) OR
                       (registry_id IS NOT NULL AND ml_registry_id IS NOT NULL)),
                
                -- Foreign Key Constraints
                FOREIGN KEY (registry_id) REFERENCES physics_modeling_registry (registry_id) ON DELETE CASCADE,
                FOREIGN KEY (ml_registry_id) REFERENCES physics_ml_registry (ml_registry_id) ON DELETE CASCADE
            )
        """

        # Create the table
        if not self.create_table("physics_modeling_metrics", query):
            return False

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_timestamp ON physics_modeling_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_registry_id ON physics_modeling_metrics (registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_ml_registry_id ON physics_modeling_metrics (ml_registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_model_type ON physics_modeling_metrics (model_type)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_performance ON physics_modeling_metrics (simulation_duration_sec, accuracy_score, convergence_rate)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_resources ON physics_modeling_metrics (cpu_usage_percent, memory_usage_mb, gpu_usage_percent)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_quality ON physics_modeling_metrics (numerical_stability, mesh_quality_score, physics_compliance)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_comparative ON physics_modeling_metrics (computational_efficiency_gain, accuracy_improvement)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_time_analysis ON physics_modeling_metrics (hour_of_day, day_of_week, month)"
        ]

        return self.create_indexes("physics_modeling_metrics", index_queries)
