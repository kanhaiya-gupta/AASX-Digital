"""
Physics Modeling Schema Module
==============================

Manages Physics Modeling database tables for the AASX Digital Twin Framework.
Provides comprehensive physics modeling, machine learning integration (PINNs), and performance monitoring
with metadata and references only - no raw data storage to prevent database explosion.

ENTERPRISE-GRADE FEATURES:
- Advanced physics modeling lifecycle management with ML integration insights
- Automated performance monitoring and optimization for physics simulations
- Comprehensive health assessment and alerting for physics modeling pipelines
- Enterprise-grade metrics and analytics for physics operations
- Advanced security and compliance capabilities for physics modeling management
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import asyncio
from ..base_schema import BaseSchema

logger = logging.getLogger(__name__)


class PhysicsModelingSchema(BaseSchema):
    """
    Enterprise-Grade Physics Modeling Schema Module

    Manages the following tables with integrated enterprise features:
    - physics_modeling_registry: Traditional physics models, equations, and solver configurations + enterprise compliance, security, and performance analytics
    - physics_ml_registry: Machine learning models (PINNs, neural networks) for physics + enterprise ML metrics and compliance
    - physics_modeling_metrics: Unified performance metrics for both traditional and ML models + enterprise tracking and analytics
    
    SCHEMA OPTIMIZATION COMPLETED: 4 enterprise tables merged into 3 main tables for cleaner architecture!
    """

    def __init__(self, connection_manager, schema_name: str = "physics_modeling"):
        super().__init__(connection_manager, schema_name)
        self._physics_modeling_metrics = {}
        self._performance_analytics = {}
        self._compliance_status = {}
        self._security_metrics = {}

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Physics Modeling module for traditional physics simulations and machine learning integration (PINNs) with comprehensive performance tracking and integrated enterprise features"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["physics_modeling_registry", "physics_ml_registry", "physics_modeling_metrics"]

    async def initialize(self) -> bool:
        """Initialize the Physics Modeling schema with enterprise-grade features."""
        try:
            # Call parent initialization
            if not await super().initialize():
                return False
            
            # Create core tables
            if not await self._create_enterprise_tables():
                return False
            
            logger.info("✅ Physics Modeling Schema initialized with enterprise-grade features and optimized schema (3 tables instead of 7)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Physics Modeling Schema: {e}")
            return False



    async def create_tables(self) -> bool:
        """
        Create all Physics Modeling tables.

        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        try:
            logger.info("🔬 Creating Physics Modeling Module Tables...")

            # Create tables in dependency order
            tables_created = []

            # 1. Create Physics Modeling Registry Table (no dependencies)
            if await self._create_physics_modeling_registry_table():
                tables_created.append("physics_modeling_registry")
            else:
                logger.error("Failed to create physics_modeling_registry table")
                return False

            # 2. Create Physics ML Registry Table (depends on physics modeling registry)
            if await self._create_physics_ml_registry_table():
                tables_created.append("physics_ml_registry")
            else:
                logger.error("Failed to create physics_ml_registry table")
                return False

            # 3. Create Physics Modeling Metrics Table (depends on both registries)
            if await self._create_physics_modeling_metrics_table():
                tables_created.append("physics_modeling_metrics")
            else:
                logger.error("Failed to create physics_modeling_metrics table")
                return False

            logger.info(f"✅ Physics Modeling Module: Created {len(tables_created)} tables successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Physics Modeling tables: {e}")
            return False

    async def _create_physics_modeling_registry_table(self) -> bool:
        """Create the physics_modeling_registry table for traditional physics models."""
        query = """
            CREATE TABLE IF NOT EXISTS physics_modeling_registry (
                -- Primary Identification
                registry_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                physics_type TEXT NOT NULL,
                
                -- Plugin & Model Information (CRITICAL for plugin management)
                plugin_id TEXT, -- Plugin identifier for plugin-based models
                plugin_name TEXT, -- Plugin name for plugin-based models
                model_type TEXT NOT NULL DEFAULT 'traditional' CHECK (model_type IN ('traditional', 'plugin', 'hybrid', 'ml_integrated')), -- traditional, plugin, hybrid, ml_integrated
                model_version TEXT NOT NULL DEFAULT '1.0.0', -- Model version (separate from physics_version)
                model_description TEXT, -- Detailed description of the model
                
                -- Physics Classification & Metadata
                physics_category TEXT NOT NULL DEFAULT 'structural' CHECK (physics_category IN ('structural', 'thermal', 'fluid', 'electromagnetic', 'multi_physics', 'acoustics', 'quantum')), -- structural, thermal, fluid, electromagnetic, multi_physics, acoustics, quantum
                physics_subcategory TEXT, -- e.g., linear_elastic, non_linear_plastic, laminar_flow, turbulent_flow
                physics_domain TEXT NOT NULL DEFAULT 'mechanical' CHECK (physics_domain IN ('mechanical', 'electrical', 'thermal', 'fluid', 'electromagnetic', 'quantum', 'multi_domain')), -- mechanical, electrical, thermal, fluid, electromagnetic, quantum, multi_domain
                complexity_level TEXT NOT NULL DEFAULT 'medium' CHECK (complexity_level IN ('simple', 'medium', 'complex', 'very_complex')), -- simple, medium, complex, very_complex
                physics_version TEXT NOT NULL DEFAULT '1.0.0', -- Semantic versioning
                
                -- Workflow Classification (CRITICAL for dual workflow support)
                registry_type TEXT NOT NULL CHECK (registry_type IN ('extraction', 'generation', 'hybrid')), -- extraction, generation, hybrid
                workflow_source TEXT NOT NULL CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')), -- aasx_file, structured_data, both
                
                -- Traditional Solver Configuration (CRITICAL for physics simulations)
                solver_type TEXT NOT NULL DEFAULT 'finite_element' CHECK (solver_type IN ('finite_element', 'finite_difference', 'finite_volume', 'boundary_element', 'spectral')), -- finite_element, finite_difference, finite_volume, boundary_element, spectral
                solver_name TEXT, -- Specific solver name/implementation (e.g., ANSYS, COMSOL, OpenFOAM)
                solver_version TEXT, -- Solver software version
                solver_parameters TEXT DEFAULT '{}', -- JSON: solver-specific parameters (tolerance, max_iterations, etc.)
                mesh_configuration TEXT DEFAULT '{}', -- JSON: mesh settings, element types, refinement criteria
                time_integration_scheme TEXT CHECK (time_integration_scheme IN ('explicit', 'implicit', 'semi_implicit', 'adaptive') OR time_integration_scheme IS NULL), -- Time integration method: explicit, implicit, semi_implicit, adaptive
                spatial_discretization TEXT CHECK (spatial_discretization IN ('first_order', 'second_order', 'higher_order') OR spatial_discretization IS NULL), -- Spatial discretization method: first_order, second_order, higher_order
                convergence_criteria TEXT DEFAULT '{}', -- JSON: convergence thresholds and criteria
                solver_optimization TEXT DEFAULT '{}', -- JSON: solver optimization settings (parallelization, memory, etc.)
                
                -- Physics Equations & Constraints
                governing_equations TEXT DEFAULT '{}', -- JSON object of governing equations
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
                integration_status TEXT NOT NULL DEFAULT 'pending' CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')), -- pending, active, inactive, error, maintenance, deprecated
                overall_health_score INTEGER DEFAULT 0 CHECK (overall_health_score >= 0 AND overall_health_score <= 100), -- 0-100 health score across all modules
                health_status TEXT NOT NULL DEFAULT 'unknown' CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')), -- unknown, healthy, warning, critical, offline
                
                -- Lifecycle Management
                lifecycle_status TEXT NOT NULL DEFAULT 'created' CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')), -- created, active, suspended, archived, retired
                lifecycle_phase TEXT NOT NULL DEFAULT 'setup' CHECK (lifecycle_phase IN ('setup', 'validation', 'deployment', 'monitoring', 'maintenance')), -- setup, validation, deployment, monitoring, maintenance
                
                -- Operational Status
                operational_status TEXT NOT NULL DEFAULT 'stopped' CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')), -- running, stopped, paused, error, maintenance
                availability_status TEXT NOT NULL DEFAULT 'offline' CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')), -- online, offline, degraded, maintenance
                
                -- Physics-Specific Status
                simulation_status TEXT DEFAULT 'pending' CHECK (simulation_status IN ('pending', 'running', 'completed', 'failed', 'paused')), -- pending, running, completed, failed, paused
                validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'in_progress', 'passed', 'failed', 'needs_review')), -- pending, in_progress, passed, failed, needs_review
                convergence_status TEXT DEFAULT 'unknown' CHECK (convergence_status IN ('unknown', 'converging', 'converged', 'diverged', 'oscillating')), -- unknown, converging, converged, diverged, oscillating
                
                -- Performance & Quality Metrics
                performance_score REAL DEFAULT 0.0, -- 0.0-1.0 performance rating
                accuracy_score REAL DEFAULT 0.0, -- 0.0-1.0 accuracy rating
                computational_efficiency REAL DEFAULT 0.0, -- 0.0-1.0 efficiency rating
                numerical_stability REAL DEFAULT 0.0, -- 0.0-1.0 stability rating
                
                -- Security & Access Control
                security_level TEXT NOT NULL DEFAULT 'standard' CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')), -- public, internal, confidential, secret, top_secret
                access_control_level TEXT NOT NULL DEFAULT 'user' CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')), -- public, user, admin, system, restricted
                encryption_enabled BOOLEAN DEFAULT TRUE, -- Whether physics data is encrypted
                audit_logging_enabled BOOLEAN DEFAULT TRUE, -- Whether audit logging is enabled
                
                -- Enterprise Compliance & Security (Merged from enterprise tables)
                compliance_type TEXT DEFAULT 'standard', -- standard, regulatory, industry_specific, custom
                compliance_status TEXT DEFAULT 'pending', -- pending, compliant, non_compliant, under_review
                compliance_score REAL DEFAULT 0.0 CHECK (compliance_score >= 0.0 AND compliance_score <= 100.0),
                last_audit_date TEXT, -- Last compliance audit date
                next_audit_date TEXT, -- Next scheduled audit date
                audit_details TEXT DEFAULT '{}', -- JSON: detailed audit information
                
                -- Enterprise Security Metrics (Merged from enterprise tables)
                security_event_type TEXT DEFAULT 'none', -- none, threat_detected, vulnerability_scan, access_violation
                threat_assessment TEXT DEFAULT 'low', -- low, medium, high, critical
                security_score REAL DEFAULT 0.0 CHECK (security_score >= 0.0 AND security_score <= 100.0),
                last_security_scan TEXT, -- Last security scan date
                security_details TEXT DEFAULT '{}', -- JSON: security scan results and details
                
                -- Enterprise Performance Analytics (Merged from enterprise tables)
                performance_trend TEXT DEFAULT 'stable', -- improving, stable, declining, fluctuating
                optimization_suggestions TEXT DEFAULT '{}', -- JSON object of optimization recommendations
                last_optimization_date TEXT, -- Last optimization performed
                enterprise_metrics TEXT DEFAULT '{}', -- JSON: additional enterprise-specific metrics
                
                -- User Management & Ownership
                user_id TEXT NOT NULL, -- Current user who owns/accesses this registry
                org_id TEXT NOT NULL, -- Organization this registry belongs to
                dept_id TEXT NOT NULL, -- Department for complete traceability
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
                tags TEXT DEFAULT '{}', -- JSON object of tags for categorization
                
                -- Results & Physics-Specific Data (CRITICAL for simulation tracking)
                results_metadata TEXT DEFAULT '{}', -- JSON: simulation results metadata and analysis data
                physics_specific_metrics TEXT DEFAULT '{}', -- JSON: mesh quality, solver performance, convergence data
                
                -- Relationships & Dependencies (JSON objects)
                relationships TEXT DEFAULT '{}', -- JSON object of relationship objects
                dependencies TEXT DEFAULT '{}', -- JSON object of dependency objects
                physics_instances TEXT DEFAULT '{}' -- JSON object of physics instance objects
                
                -- Constraints
                --FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                --FOREIGN KEY (twin_registry_id) REFERENCES twin_registry(registry_id) ON DELETE SET NULL,
                --FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry(graph_id) ON DELETE SET NULL,
                --FOREIGN KEY (dept_id) REFERENCES departments (dept_id) ON DELETE SET NULL
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)
        
        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_user_id ON physics_modeling_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_org_id ON physics_modeling_registry (org_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_registry_dept_id ON physics_modeling_registry (dept_id)",
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

        return await self.create_indexes("physics_modeling_registry", index_queries)

    async def _create_physics_ml_registry_table(self) -> bool:
        """Create the physics_ml_registry table for machine learning models (PINNs, etc.)."""
        query = """
            CREATE TABLE IF NOT EXISTS physics_ml_registry (
                -- Primary Identification
                ml_registry_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                ml_model_type TEXT NOT NULL DEFAULT 'pinn' CHECK (ml_model_type IN ('pinn', 'neural_ode', 'graph_neural_network', 'transformer', 'hybrid')), -- pinn, neural_ode, graph_neural_network, transformer, hybrid
                
                -- Model Information
                model_type TEXT NOT NULL DEFAULT 'ml' CHECK (model_type IN ('ml', 'hybrid_ml', 'traditional_enhanced')), -- ml, hybrid_ml, traditional_enhanced
                model_version TEXT NOT NULL DEFAULT '1.0.0', -- Model version (separate from ml_model_type)
                model_description TEXT, -- Detailed description of the ML model
                
                -- Physics Domain Classification
                physics_domain TEXT NOT NULL DEFAULT 'mechanical' CHECK (physics_domain IN ('mechanical', 'electrical', 'thermal', 'fluid', 'electromagnetic', 'quantum', 'multi_domain')), -- mechanical, electrical, thermal, fluid, electromagnetic, quantum, multi_domain
                
                -- Neural Network Architecture
                nn_architecture TEXT DEFAULT '{}', -- JSON: layer sizes, activation functions, regularization
                activation_functions TEXT DEFAULT '{}', -- JSON object of activation functions
                regularization_methods TEXT DEFAULT '{}', -- JSON object of regularization methods
                dropout_rates TEXT DEFAULT '{}', -- JSON object of dropout rates per layer
                
                -- Training Configuration
                training_parameters TEXT DEFAULT '{}', -- JSON: learning rate, batch size, epochs, optimizer
                loss_function_config TEXT DEFAULT '{}', -- JSON: loss function configuration and weights
                optimization_settings TEXT DEFAULT '{}', -- JSON: optimizer settings, learning rate schedules
                training_data_config TEXT DEFAULT '{}', -- JSON: training data configuration and augmentation
                
                -- Physics Integration
                physics_constraints TEXT DEFAULT '{}', -- JSON: physics constraints and enforcement methods
                conservation_laws TEXT DEFAULT '{}', -- JSON object of conservation laws to enforce
                differential_equations TEXT DEFAULT '{}', -- JSON object of differential equations
                boundary_condition_handling TEXT DEFAULT '{}', -- JSON: boundary condition enforcement
                initial_condition_learning TEXT DEFAULT '{}', -- JSON: initial condition learning configuration
                
                -- Model Performance & Quality
                training_accuracy REAL DEFAULT 0.0, -- 0.0-1.0 training accuracy
                validation_accuracy REAL DEFAULT 0.0, -- 0.0-1.0 validation accuracy
                physics_compliance_score REAL DEFAULT 0.0, -- 0.0-1.0 physics compliance
                generalization_error REAL DEFAULT 0.0, -- 0.0-1.0 generalization error
                overfitting_score REAL DEFAULT 0.0, -- 0.0-1.0 overfitting assessment
                
                -- Enterprise ML Metrics (Merged from enterprise tables)
                ml_compliance_type TEXT DEFAULT 'standard', -- standard, regulatory, industry_specific, custom
                ml_compliance_status TEXT DEFAULT 'pending', -- pending, compliant, non_compliant, under_review
                ml_compliance_score REAL DEFAULT 0.0 CHECK (ml_compliance_score >= 0.0 AND ml_compliance_score <= 100.0),
                ml_security_score REAL DEFAULT 0.0 CHECK (ml_security_score >= 0.0 AND ml_security_score <= 100.0),
                ml_performance_trend TEXT DEFAULT 'stable', -- improving, stable, declining, fluctuating
                ml_optimization_suggestions TEXT DEFAULT '{}', -- JSON object of ML optimization recommendations
                last_ml_optimization_date TEXT, -- Last ML optimization performed
                enterprise_ml_metrics TEXT DEFAULT '{}', -- JSON: additional enterprise-specific ML metrics
                
                -- Integration References
                physics_modeling_id TEXT, -- Reference to physics_modeling_registry table
                aasx_integration_id TEXT, -- Reference to aasx_processing table
                twin_registry_id TEXT, -- Reference to twin_registry table
                kg_neo4j_id TEXT, -- Reference to kg_graph_registry table
                ai_rag_id TEXT, -- Reference to ai_rag_registry table
                federated_learning_id TEXT, -- Reference to federated_learning_registry table
                certificate_manager_id TEXT, -- Reference to certificate module
                
                -- Status & Lifecycle
                training_status TEXT NOT NULL DEFAULT 'pending' CHECK (training_status IN ('pending', 'training', 'completed', 'failed', 'paused')), -- pending, training, completed, failed, paused
                deployment_status TEXT NOT NULL DEFAULT 'not_deployed' CHECK (deployment_status IN ('not_deployed', 'deployed', 'serving', 'error', 'maintenance')), -- not_deployed, deployed, serving, error, maintenance
                lifecycle_phase TEXT NOT NULL DEFAULT 'development' CHECK (lifecycle_phase IN ('development', 'training', 'validation', 'deployment', 'monitoring')), -- development, training, validation, deployment, monitoring
                
                -- Training History & Metadata
                training_started_at TEXT, -- When training started
                training_completed_at TEXT, -- When training completed
                training_duration_sec REAL, -- Total training duration
                training_iterations INTEGER DEFAULT 0, -- Number of training iterations
                model_checkpoints TEXT DEFAULT '{}', -- JSON object of model checkpoint information
                
                -- User Management & Ownership
                user_id TEXT NOT NULL, -- Current user who owns/accesses this ML model
                org_id TEXT NOT NULL, -- Organization this ML model belongs to
                dept_id TEXT, -- Department for complete traceability
                ml_engineer_id TEXT, -- ML engineer responsible for this model
                data_scientist_id TEXT, -- Data scientist who developed this model
                created_by TEXT, -- User who created this ML model
                updated_by TEXT, -- User who last updated this ML model
                
                -- Timestamps & Audit
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                last_trained_at TEXT, -- Last time model was trained
                last_deployed_at TEXT, -- Last time model was deployed
                
                -- Configuration & Metadata (JSON fields for flexibility)
                ml_config TEXT DEFAULT '{}', -- ML-specific configuration settings
                ml_metadata TEXT DEFAULT '{}', -- Additional ML metadata
                custom_attributes TEXT DEFAULT '{}', -- User-defined custom attributes
                tags TEXT DEFAULT '{}' -- JSON object of tags for categorization
                
                -- Constraints
                --FOREIGN KEY (physics_modeling_id) REFERENCES physics_modeling_registry (registry_id) ON DELETE SET NULL,
                --FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing(job_id) ON DELETE SET NULL,
                --FOREIGN KEY (twin_registry_id) REFERENCES twin_registry(registry_id) ON DELETE SET NULL,
                --FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry(graph_id) ON DELETE SET NULL
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

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

        return await self.create_indexes("physics_ml_registry", index_queries)

    async def _create_physics_modeling_metrics_table(self) -> bool:
        """Create the physics_modeling_metrics table for unified performance tracking."""
        query = """
            CREATE TABLE IF NOT EXISTS physics_modeling_metrics (
                -- Primary Identification
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                
                -- Organizational Hierarchy (REQUIRED for proper access control)
                org_id TEXT NOT NULL DEFAULT 'default', -- Organization this metric belongs to
                dept_id TEXT DEFAULT 'default', -- Department for complete traceability
                user_id TEXT NOT NULL DEFAULT 'system', -- User who owns/accesses this metric
                
                -- Model Reference (Links to either traditional or ML registry)
                registry_id TEXT, -- Reference to physics_modeling_registry (traditional)
                ml_registry_id TEXT, -- Reference to physics_ml_registry (ML)
                model_type TEXT NOT NULL CHECK (model_type IN ('traditional', 'ml', 'hybrid')), -- traditional, ml, hybrid
                
                -- Performance Metrics (Unified for both types)
                simulation_duration_sec REAL, -- Time to complete simulation/training
                accuracy_score REAL DEFAULT 0.0 CHECK (accuracy_score >= 0.0 AND accuracy_score <= 1.0),
                convergence_rate REAL, -- Rate of convergence for traditional models
                error_metrics TEXT DEFAULT '{}', -- JSON: various error metrics
                
                -- Resource Utilization
                cpu_usage_percent REAL DEFAULT 0.0 CHECK (cpu_usage_percent >= 0.0 AND cpu_usage_percent <= 100.0),
                memory_usage_mb REAL,
                gpu_usage_percent REAL DEFAULT 0.0 CHECK (gpu_usage_percent >= 0.0 AND gpu_usage_percent <= 100.0),
                storage_usage_mb REAL,
                network_throughput_mbps REAL,
                
                -- Quality Metrics
                numerical_stability REAL DEFAULT 0.0 CHECK (numerical_stability >= 0.0 AND numerical_stability <= 1.0),
                mesh_quality_score REAL DEFAULT 0.0 CHECK (mesh_quality_score >= 0.0 AND mesh_quality_score <= 1.0),
                physics_compliance REAL DEFAULT 0.0 CHECK (physics_compliance >= 0.0 AND physics_compliance <= 1.0),
                generalization_error REAL DEFAULT 0.0 CHECK (generalization_error >= 0.0 AND generalization_error <= 1.0),
                
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
                hour_of_day INTEGER DEFAULT 0 CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
                day_of_week INTEGER DEFAULT 1 CHECK (day_of_week >= 1 AND day_of_week <= 7),
                month INTEGER DEFAULT 1 CHECK (month >= 1 AND month <= 12),
                
                -- Performance Trends
                performance_trend REAL, -- Compared to historical average
                efficiency_trend REAL, -- Performance over time
                quality_trend REAL, -- Quality metrics over time
                
                -- Enterprise Metrics (Merged from enterprise tables)
                enterprise_metric_type TEXT DEFAULT 'standard', -- standard, compliance, security, performance
                enterprise_metric_value REAL, -- Enterprise-specific metric value
                enterprise_metric_timestamp TEXT, -- When enterprise metric was recorded
                enterprise_metadata TEXT DEFAULT '{}', -- JSON: additional enterprise metadata
                
                -- Enterprise Compliance Tracking (Merged from enterprise tables)
                compliance_tracking_status TEXT DEFAULT 'pending', -- pending, active, completed, failed
                compliance_tracking_score REAL DEFAULT 0.0 CHECK (compliance_tracking_score >= 0.0 AND compliance_tracking_score <= 100.0),
                compliance_tracking_details TEXT DEFAULT '{}', -- JSON: compliance tracking information
                
                -- Enterprise Security Metrics (Merged from enterprise tables)
                security_metrics_status TEXT DEFAULT 'pending', -- pending, active, completed, failed
                security_metrics_score REAL DEFAULT 0.0 CHECK (security_metrics_score >= 0.0 AND security_metrics_score <= 100.0),
                security_metrics_details TEXT DEFAULT '{}', -- JSON: security metrics information
                
                -- Enterprise Performance Analytics (Merged from enterprise tables)
                performance_analytics_status TEXT DEFAULT 'pending', -- pending, active, completed, failed
                performance_analytics_score REAL DEFAULT 0.0 CHECK (performance_analytics_score >= 0.0 AND performance_analytics_score <= 100.0),
                performance_analytics_details TEXT DEFAULT '{}', -- JSON: performance analytics information
                
                -- Alerting & Monitoring (NEW for enterprise monitoring)
                alert_status TEXT DEFAULT 'normal', -- normal, warning, critical, resolved
                warning_threshold REAL DEFAULT 0.7, -- Warning threshold value
                critical_threshold REAL DEFAULT 0.5, -- Critical threshold value
                alert_history TEXT DEFAULT '{}', -- JSON: alert history and details
                
                -- Categorization & Metadata (NEW for enterprise organization)
                tags TEXT DEFAULT '{}', -- JSON: tags for categorization
                metadata TEXT DEFAULT '{}', -- JSON: additional metadata
                
                -- Audit Timestamps (REQUIRED for audit trails)
                created_at TEXT NOT NULL DEFAULT (datetime('now')), -- When metric was created
                updated_at TEXT NOT NULL DEFAULT (datetime('now')), -- When metric was last updated
                
                -- Constraints (Ensure at least one registry reference exists)
                CHECK ((registry_id IS NOT NULL AND ml_registry_id IS NULL) OR 
                       (registry_id IS NULL AND ml_registry_id IS NOT NULL) OR
                       (registry_id IS NOT NULL AND ml_registry_id IS NOT NULL))
                
                -- Foreign Key Constraints
                --FOREIGN KEY (registry_id) REFERENCES physics_modeling_registry (registry_id) ON DELETE CASCADE,
                --FOREIGN KEY (ml_registry_id) REFERENCES physics_ml_registry (ml_registry_id) ON DELETE CASCADE
            )
        """

        # Create the table using connection manager
        await self.connection_manager.execute_query(query)

        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_timestamp ON physics_modeling_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_registry_id ON physics_modeling_metrics (registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_ml_registry_id ON physics_modeling_metrics (ml_registry_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_model_type ON physics_modeling_metrics (model_type)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_org_dept ON physics_modeling_metrics (org_id, dept_id, user_id)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_performance ON physics_modeling_metrics (simulation_duration_sec, accuracy_score, convergence_rate)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_resources ON physics_modeling_metrics (cpu_usage_percent, memory_usage_mb, gpu_usage_percent)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_quality ON physics_modeling_metrics (numerical_stability, mesh_quality_score, physics_compliance)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_comparative ON physics_modeling_metrics (computational_efficiency_gain, accuracy_improvement)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_time_analysis ON physics_modeling_metrics (hour_of_day, day_of_week, month)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_alerting ON physics_modeling_metrics (alert_status, warning_threshold, critical_threshold)",
            "CREATE INDEX IF NOT EXISTS idx_physics_modeling_metrics_audit ON physics_modeling_metrics (created_at, updated_at)"
        ]

        return await self.create_indexes("physics_modeling_metrics", index_queries)

    # Enterprise-Grade Helper Methods



    async def _create_enterprise_tables(self) -> bool:
        """Create all core Physics Modeling tables with integrated enterprise features."""
        try:
            # Create core tables
            if not await self._create_physics_modeling_registry_table():
                return False
            
            if not await self._create_physics_ml_registry_table():
                return False
            
            if not await self._create_physics_modeling_metrics_table():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create core tables: {e}")
            return False


