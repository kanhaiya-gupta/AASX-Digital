"""
AI RAG Schema Module
====================

Defines tables for AI RAG (Retrieval-Augmented Generation) operations,
including document processing, vector storage, and retrieval operations.

CONSOLIDATED ENTERPRISE FEATURES:
- Advanced AI RAG lifecycle management with ML-powered insights
- Automated performance monitoring and optimization for RAG operations
- Comprehensive health assessment and alerting for AI pipelines
- Enterprise-grade metrics and analytics for RAG operations (consolidated into main tables)
- Advanced security and compliance capabilities for AI processing (consolidated into main tables)
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import asyncio
from ..base_schema import BaseSchema

logger = logging.getLogger(__name__)


class AIRagSchema(BaseSchema):
    """
    Enterprise-Grade AI RAG Schema Module

    Manages the following tables with consolidated enterprise features:
    - ai_rag_registry: Main AI RAG registry and document metadata (includes enterprise compliance & security)
    - ai_rag_metrics: Performance metrics and all analytics (includes enterprise metrics & performance analytics)
    - ai_rag_operations: Sessions, logs, embeddings, and graph metadata (consolidated operations table)
    """

    def __init__(self, connection_manager, schema_name: str = "ai_rag"):
        super().__init__(connection_manager, schema_name)
        self._ai_rag_metrics = {}
        self._performance_analytics = {}
        self._compliance_status = {}
        self._security_metrics = {}

    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "AI RAG schema with 3 consolidated tables: registry (with documents), metrics (with analytics), and operations (sessions, logs, embeddings, graphs)"

    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["ai_rag_registry", "ai_rag_metrics", "ai_rag_operations"]

    async def initialize(self) -> bool:
        """Initialize the AI RAG schema with consolidated enterprise features."""
        try:
            # Call parent initialization
            if not await super().initialize():
                return False
            
            # Create consolidated tables with enterprise features
            await self._create_consolidated_tables()
            
            logger.info("✅ AI RAG Schema initialized with 3 consolidated tables")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI RAG Schema: {e}")
            return False

    # create_table method is inherited from BaseSchema - no need to override

    async def create_tables(self) -> bool:
        """Create all AI RAG tables with consolidated enterprise features"""
        try:
            return await self._create_consolidated_tables()
        except Exception as e:
            logger.error(f"Failed to create AI RAG tables: {e}")
            return False

    async def _create_ai_rag_registry_table(self) -> bool:
        """Create the AI/RAG registry table with document metadata and comprehensive AI/RAG management capabilities."""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS ai_rag_registry (
                    -- Primary Identification
                    registry_id TEXT PRIMARY KEY,
                    file_id TEXT NOT NULL,
                    registry_name TEXT NOT NULL,
                    
                    -- Document Metadata (CONSOLIDATED from documents table)
                    documents_json TEXT DEFAULT '{}',  -- JSON object of all documents from this AASX file
                    document_count INTEGER DEFAULT 0,  -- Total number of documents
                    document_types TEXT DEFAULT '{}',  -- JSON object of file types with counts
                    total_document_size INTEGER DEFAULT 0,  -- Combined size of all documents
                    
                    -- Document Processing Details (CONSOLIDATED from documents table)
                    processing_status TEXT DEFAULT 'pending',  -- Overall processing status for the AASX file
                    file_type TEXT DEFAULT 'aasx',  -- Primary file type of the AASX file
                    processing_start_time TEXT,
                    processing_end_time TEXT,
                    processing_duration_ms REAL,
                    content_summary TEXT,
                    extracted_text TEXT,
                    quality_score REAL DEFAULT 0.0 CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
                    confidence_score REAL DEFAULT 0.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
                    validation_errors TEXT DEFAULT '{}', -- JSON object of validation errors
                    processor_config TEXT DEFAULT '{}', -- JSON: Processor configuration
                    extraction_config TEXT DEFAULT '{}', -- JSON: Extraction configuration
                    
                    -- RAG Classification & Metadata
                    rag_category TEXT DEFAULT 'generic' CHECK (rag_category IN ('text', 'image', 'multimodal', 'hybrid', 'graph_enhanced')),
                    rag_type TEXT DEFAULT 'basic' CHECK (rag_type IN ('basic', 'advanced', 'graph', 'hybrid', 'multi_step')),
                    rag_priority TEXT DEFAULT 'normal' CHECK (rag_priority IN ('low', 'normal', 'high', 'critical')),
                    rag_version TEXT DEFAULT '1.0.0',
                    
                    -- Workflow Classification
                    registry_type TEXT NOT NULL CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
                    workflow_source TEXT NOT NULL CHECK (workflow_source IN ('aasx_file', 'structured_data', 'both')),
                    
                    -- Module Integration References (Framework Integration)
                    aasx_integration_id TEXT,
                    twin_registry_id TEXT,
                    kg_neo4j_id TEXT,
                    physics_modeling_id TEXT,
                    federated_learning_id TEXT,
                    certificate_manager_id TEXT,
                    
                    -- Integration Status & Health (Framework Health)
                    integration_status TEXT DEFAULT 'pending' CHECK (integration_status IN ('pending', 'active', 'inactive', 'error', 'maintenance', 'deprecated')),
                    overall_health_score INTEGER DEFAULT 0 CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
                    health_status TEXT DEFAULT 'unknown' CHECK (health_status IN ('unknown', 'healthy', 'warning', 'critical', 'offline')),
                    
                    -- Lifecycle Management (Framework Lifecycle)
                    lifecycle_status TEXT DEFAULT 'created' CHECK (lifecycle_status IN ('created', 'active', 'suspended', 'archived', 'retired')),
                    lifecycle_phase TEXT DEFAULT 'development' CHECK (lifecycle_phase IN ('development', 'testing', 'production', 'maintenance', 'sunset')),
                    
                    -- Operational Status (Framework Operations)
                    operational_status TEXT DEFAULT 'stopped' CHECK (operational_status IN ('running', 'stopped', 'paused', 'error', 'maintenance')),
                    availability_status TEXT DEFAULT 'offline' CHECK (availability_status IN ('online', 'offline', 'degraded', 'maintenance')),
                    
                    -- RAG-Specific Integration Status (Framework Integration Points)
                    embedding_generation_status TEXT DEFAULT 'pending' CHECK (embedding_generation_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                    vector_db_sync_status TEXT DEFAULT 'pending' CHECK (vector_db_sync_status IN ('pending', 'in_progress', 'completed', 'failed', 'scheduled')),
                    last_embedding_generated_at TEXT,
                    last_vector_db_sync_at TEXT,
                    
                    -- RAG Configuration (Framework Configuration - NOT Raw Data)
                    embedding_model TEXT,                    -- Model name/version, not the model itself
                    vector_db_type TEXT,                     -- 'qdrant', 'pinecone', etc.
                    vector_collection_id TEXT,               -- Collection identifier, not the collection
                    
                    -- RAG Techniques Configuration (JSON for better framework flexibility)
                    rag_techniques_config TEXT DEFAULT '{}', -- JSON: {
                                                             --   "basic": {"enabled": true, "priority": 1, "config": {...}},
                                                             --   "advanced": {"enabled": false, "priority": 2, "config": {...}},
                                                             --   "graph": {"enabled": true, "priority": 3, "config": {...}},
                                                             --   "hybrid": {"enabled": false, "priority": 4, "config": {...}},
                                                             --   "multi_step": {"enabled": true, "priority": 5, "config": {...}}
                                                             -- }
                    
                    -- Document Type Support (JSON for better framework capabilities)
                    supported_file_types_config TEXT DEFAULT '{}', -- JSON: {
                                                                  --   "documents": {"extensions": [".pdf", ".docx", ".txt"], "enabled": true, "processor": "DocumentProcessor"},
                                                                  --   "images": {"extensions": [".jpg", ".png", ".gif"], "enabled": true, "processor": "ImageProcessor"},
                                                                  --   "code": {"extensions": [".py", ".js", ".java"], "enabled": true, "processor": "CodeProcessor"},
                                                                  --   "spreadsheets": {"extensions": [".xlsx", ".csv"], "enabled": true, "processor": "SpreadsheetProcessor"},
                                                                  --   "cad": {"extensions": [".dwg", ".step", ".stl"], "enabled": true, "processor": "CADProcessor"},
                                                                  --   "graph_data": {"extensions": [".graphml", ".gml"], "enabled": true, "processor": "GraphDataProcessor"},
                                                                  --   "structured_data": {"extensions": [".json", ".yaml", ".xml"], "enabled": true, "processor": "StructuredDataProcessor"}
                                                                  -- }
                    
                    -- Document Processor Capabilities (JSON for framework capabilities)
                    processor_capabilities_config TEXT DEFAULT '{}', -- JSON: {
                                                                     --   "DocumentProcessor": {"ocr_enabled": true, "image_extraction": true, "text_processing": true},
                                                                     --   "ImageProcessor": {"tesseract": true, "easyocr": true, "paddleocr": true},
                                                                     --   "CodeProcessor": {"syntax_highlighting": true, "semantic_analysis": true, "dependency_analysis": true},
                                                                     --   "SpreadsheetProcessor": {"semantic_analysis": true, "pattern_detection": true, "data_quality": true},
                                                                     --   "CADProcessor": {"technical_analysis": true, "metadata_extraction": true, "3d_analysis": true}
                                                                     -- }
                    
                    -- Performance & Quality Metrics (Framework Performance)
                    performance_score REAL DEFAULT 0.0 CHECK (performance_score >= 0.0 AND performance_score <= 1.0),
                    data_quality_score REAL DEFAULT 0.0 CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
                    reliability_score REAL DEFAULT 0.0 CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0),
                    compliance_score REAL DEFAULT 0.0 CHECK (compliance_score >= 0.0 AND compliance_score <= 1.0),
                    
                    -- Security & Access Control (Framework Security)
                    security_level TEXT DEFAULT 'standard' CHECK (security_level IN ('public', 'internal', 'confidential', 'secret', 'top_secret')),
                    access_control_level TEXT DEFAULT 'user' CHECK (access_control_level IN ('public', 'user', 'admin', 'system', 'restricted')),
                    encryption_enabled BOOLEAN DEFAULT FALSE,
                    audit_logging_enabled BOOLEAN DEFAULT TRUE,
                    
                    -- User Management & Ownership (Framework Access Control)
                    user_id TEXT NOT NULL,
                    org_id TEXT NOT NULL,
                    dept_id TEXT, -- Department for complete traceability
                    owner_team TEXT,
                    steward_user_id TEXT,
                    
                    -- Timestamps & Audit (Framework Audit Trail)
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    activated_at TEXT,
                    last_accessed_at TEXT,
                    last_modified_at TEXT,
                    
                    -- Configuration & Metadata (Framework Configuration - JSON)
                    registry_config TEXT DEFAULT '{}',      -- JSON: Framework settings, not data
                    registry_metadata TEXT DEFAULT '{}',    -- JSON: Framework metadata, not content
                    custom_attributes TEXT DEFAULT '{}',    -- JSON: Custom framework attributes
                    tags_config TEXT DEFAULT '{}',          -- JSON: {"tags": ["ai", "rag", "nlp"], "categories": ["ml", "ai"], "keywords": ["vector", "embedding"]}
                    
                    -- Relationships & Dependencies (Framework Dependencies - JSON)
                    relationships_config TEXT DEFAULT '{}', -- JSON: {"depends_on": ["twin_registry", "kg_neo4j"], "provides_to": ["certificate_manager"], "integrates_with": ["aasx_processing"]}
                    dependencies_config TEXT DEFAULT '{}',  -- JSON: {"required_modules": ["vector_db", "embedding_models"], "optional_modules": ["neo4j", "physics_modeling"]}
                    rag_instances_config TEXT DEFAULT '{}', -- JSON: {"active_instances": ["instance_1", "instance_2"], "instance_configs": {...}}
                    
                    -- ENTERPRISE COMPLIANCE COLUMNS (Merged from enterprise_ai_rag_compliance_tracking)
                    enterprise_compliance_type TEXT DEFAULT 'standard',           -- Compliance type (standard, regulatory, industry)
                    enterprise_compliance_status TEXT DEFAULT 'pending',          -- Compliance status (pending, compliant, non_compliant)
                    enterprise_compliance_score REAL DEFAULT 0.0,                 -- Compliance score (0.0 to 1.0)
                    enterprise_last_audit_date TEXT,                             -- Last audit date
                    enterprise_next_audit_date TEXT,                             -- Next audit date
                    enterprise_audit_details TEXT DEFAULT '{}',                  -- Audit details in JSON format
                    
                    -- ENTERPRISE SECURITY COLUMNS (Merged from enterprise_ai_rag_security_metrics)
                    enterprise_security_event_type TEXT DEFAULT 'none',           -- Security event type (none, threat, breach, alert)
                    enterprise_threat_assessment TEXT DEFAULT 'low',              -- Threat assessment level (low, medium, high, critical)
                    enterprise_security_score REAL DEFAULT 0.0,                   -- Security score (0.0 to 1.0)
                    enterprise_last_security_scan TEXT,                          -- Last security scan timestamp
                    enterprise_security_details TEXT DEFAULT '{}',                -- Security details in JSON format
                    
                    -- Foreign Key Constraints
                    FOREIGN KEY (file_id) REFERENCES files (file_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                    FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE CASCADE,
                    FOREIGN KEY (dept_id) REFERENCES departments (dept_id) ON DELETE SET NULL,
                    FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing (job_id) ON DELETE SET NULL,
                    FOREIGN KEY (twin_registry_id) REFERENCES twin_registry (registry_id) ON DELETE SET NULL,
                    FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry (graph_id) ON DELETE SET NULL
                )
            """
            
            # Create the table using connection manager
            await self.connection_manager.execute_query(query)
            logger.info("✅ Created ai_rag_registry table with consolidated document metadata")
            
            # Create indexes
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_file_id ON ai_rag_registry (file_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_document_count ON ai_rag_registry (document_count)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_total_document_size ON ai_rag_registry (total_document_size)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_user_id ON ai_rag_registry (user_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_org_id ON ai_rag_registry (org_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_dept_id ON ai_rag_registry (dept_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_category ON ai_rag_registry (rag_category)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_type ON ai_rag_registry (rag_type)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_status ON ai_rag_registry (integration_status)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_health ON ai_rag_registry (health_status)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_lifecycle ON ai_rag_registry (lifecycle_status)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_embedding ON ai_rag_registry (embedding_generation_status, vector_db_sync_status)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_created ON ai_rag_registry (created_at)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_updated ON ai_rag_registry (updated_at)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_workflow ON ai_rag_registry (workflow_source, registry_type)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_integration ON ai_rag_registry (aasx_integration_id, twin_registry_id, kg_neo4j_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_performance ON ai_rag_registry (performance_score, data_quality_score, reliability_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_enterprise_compliance ON ai_rag_registry (enterprise_compliance_type, enterprise_compliance_status, enterprise_compliance_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_enterprise_security ON ai_rag_registry (enterprise_security_event_type, enterprise_threat_assessment, enterprise_security_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_processing_status ON ai_rag_registry (processing_status)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_file_type ON ai_rag_registry (file_type)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_processing_time ON ai_rag_registry (processing_start_time, processing_end_time)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_quality ON ai_rag_registry (quality_score, confidence_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_validation ON ai_rag_registry (validation_errors)"
            ]
            
            return await self.create_indexes("ai_rag_registry", index_queries)
            
        except Exception as e:
            logger.error(f"Failed to create ai_rag_registry table: {e}")
            return False

    async def _create_ai_rag_metrics_table(self) -> bool:
        """Create the AI/RAG metrics table with comprehensive performance monitoring and all analytics."""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS ai_rag_metrics (
                    -- Primary Identification
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registry_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    
                    -- Real-time Health Metrics (Framework Health)
                    health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
                    response_time_ms REAL,
                    uptime_percentage REAL CHECK (uptime_percentage >= 0.0 AND uptime_percentage <= 100.0),
                    error_rate REAL CHECK (error_rate >= 0.0 AND error_rate <= 1.0),
                    
                    -- AI/RAG Performance Metrics (Framework Performance - NOT Data)
                    embedding_generation_speed_sec REAL,           -- Time to generate embeddings
                    vector_db_query_response_time_ms REAL,         -- Vector DB query performance
                    rag_response_generation_time_ms REAL,          -- RAG response generation time
                    context_retrieval_accuracy REAL CHECK (context_retrieval_accuracy >= 0.0 AND context_retrieval_accuracy <= 1.0),
                    
                    -- RAG Technique Performance (JSON for better framework analysis)
                    rag_technique_performance TEXT DEFAULT '{}',   -- JSON: {
                                                                   --   "basic": {"usage_count": 150, "avg_response_time": 2.3, "success_rate": 0.98, "last_used": "2024-01-15T10:30:00Z"},
                                                                   --   "advanced": {"usage_count": 75, "avg_response_time": 5.7, "success_rate": 0.95, "last_used": "2024-01-15T09:15:00Z"},
                                                                   --   "graph": {"usage_count": 45, "avg_response_time": 3.2, "success_rate": 0.92, "last_used": "2024-01-15T08:45:00Z"},
                                                                   --   "hybrid": {"usage_count": 60, "avg_response_time": 4.1, "success_rate": 0.96, "last_used": "2024-01-15T10:00:00Z"},
                                                                   --   "multi_step": {"usage_count": 30, "avg_response_time": 8.9, "success_rate": 0.88, "last_used": "2024-01-15T07:30:00Z"}
                                                                   -- }
                    
                    -- Document Processing Metrics (JSON for better framework analysis)
                    document_processing_stats TEXT DEFAULT '{}',   -- JSON: {
                                                                   --   "documents": {"processed": 250, "successful": 245, "failed": 5, "avg_processing_time": 1.2, "file_types": {".pdf": 120, ".docx": 80, ".txt": 50}},
                                                                   --   "images": {"processed": 180, "successful": 175, "failed": 5, "avg_processing_time": 2.8, "file_types": {".jpg": 100, ".png": 60, ".gif": 20}},
                                                                   --   "code": {"processed": 320, "successful": 315, "failed": 5, "avg_processing_time": 0.8, "file_types": {".py": 150, ".js": 80, ".java": 50, ".cpp": 40}},
                                                                   --   "spreadsheets": {"processed": 95, "successful": 92, "failed": 3, "avg_processing_time": 1.5, "file_types": {".xlsx": 60, ".csv": 25, ".ods": 10}},
                                                                   --   "cad": {"processed": 45, "successful": 42, "failed": 3, "avg_processing_time": 4.2, "file_types": {".dwg": 20, ".step": 15, ".stl": 10}},
                                                                   --   "graph_data": {"processed": 30, "successful": 28, "failed": 2, "avg_processing_time": 2.1, "file_types": {".graphml": 20, ".gml": 10}},
                                                                   --   "structured_data": {"processed": 110, "successful": 108, "failed": 2, "avg_processing_time": 0.6, "file_types": {".json": 70, ".yaml": 25, ".xml": 15}}
                                                                   -- }
                    
                    -- User Interaction Metrics (Framework Usage - NOT Content)
                    user_interaction_count INTEGER DEFAULT 0,      -- Number of user interactions
                    query_execution_count INTEGER DEFAULT 0,       -- Number of queries executed
                    successful_rag_operations INTEGER DEFAULT 0,   -- Successful operations
                    failed_rag_operations INTEGER DEFAULT 0,       -- Failed operations
                    
                    -- Data Quality Metrics (Framework Quality - NOT Data Content)
                    data_freshness_score REAL CHECK (data_freshness_score >= 0.0 AND data_freshness_score <= 1.0),
                    data_completeness_score REAL CHECK (data_completeness_score >= 0.0 AND data_completeness_score <= 1.0),
                    data_consistency_score REAL CHECK (data_consistency_score >= 0.0 AND data_consistency_score <= 1.0),
                    data_accuracy_score REAL CHECK (data_accuracy_score >= 0.0 AND data_accuracy_score <= 1.0),
                    
                    -- System Resource Metrics (Framework Resources - NOT Data)
                    cpu_usage_percent REAL CHECK (cpu_usage_percent >= 0.0 AND cpu_usage_percent <= 100.0),
                    memory_usage_percent REAL CHECK (memory_usage_percent >= 0.0 AND memory_usage_percent <= 100.0),
                    network_throughput_mbps REAL,
                    storage_usage_percent REAL CHECK (storage_usage_percent >= 0.0 AND storage_usage_percent <= 100.0),
                    
                    -- Performance Trends (Framework Trends - JSON)
                    performance_trends TEXT DEFAULT '{}',           -- JSON: {"hourly": {...}, "daily": {...}, "weekly": {...}, "monthly": {...}}
                    resource_utilization_trends TEXT DEFAULT '{}', -- JSON: {"cpu_trend": [...], "memory_trend": [...], "network_trend": [...]}
                    user_activity TEXT DEFAULT '{}',               -- JSON: {"peak_hours": [...], "user_patterns": {...}, "session_durations": [...]}
                    query_patterns TEXT DEFAULT '{}',              -- JSON: {"query_types": {...}, "complexity_distribution": {...}, "response_times": [...]}
                    compliance_status TEXT DEFAULT '{}',           -- JSON: {"compliance_score": 0.95, "audit_status": "passed", "last_audit": "2024-01-15T00:00:00Z"}
                    security_events TEXT DEFAULT '{}',             -- JSON: {"events": [...], "threat_level": "low", "last_security_scan": "2024-01-15T00:00:00Z"}
                    
                    -- AI/RAG-Specific Metrics (Framework Capabilities - JSON)
                    rag_analytics TEXT DEFAULT '{}',               -- JSON: {"embedding_quality": 0.92, "retrieval_accuracy": 0.89, "generation_quality": 0.94}
                    technique_effectiveness TEXT DEFAULT '{}',     -- JSON: {"technique_comparison": {...}, "best_performing": "hybrid", "optimization_suggestions": [...]}
                    model_performance TEXT DEFAULT '{}',           -- JSON: {"embedding_model": {...}, "llm_model": {...}, "model_versions": [...]}
                    file_type_processing_efficiency TEXT DEFAULT '{}', -- JSON: {"processing_speed_by_type": {...}, "quality_by_type": {...}, "optimization_opportunities": [...]}
                    
                    -- ENTERPRISE METRICS COLUMNS (Merged from enterprise_ai_rag_metrics)
                    enterprise_metric_type TEXT DEFAULT 'performance',           -- Metric type (performance, quality, security, compliance)
                    enterprise_metric_value REAL DEFAULT 0.0,                    -- Enterprise metric value
                    enterprise_metric_metadata TEXT DEFAULT '{}',                -- Enterprise metric metadata in JSON format
                    enterprise_metric_last_updated TEXT,                         -- Last update timestamp for enterprise metric
                    
                    -- ENTERPRISE PERFORMANCE ANALYTICS COLUMNS (Merged from enterprise_ai_rag_performance_analytics)
                    enterprise_performance_metric TEXT DEFAULT 'overall',         -- Performance metric identifier
                    enterprise_performance_trend TEXT DEFAULT 'stable',          -- Performance trend (improving, stable, declining)
                    enterprise_optimization_suggestions TEXT DEFAULT '{}',       -- Optimization suggestions in JSON format
                    enterprise_last_optimization_date TEXT,                      -- Last optimization date
                    
                    -- Foreign Key Constraints
                    FOREIGN KEY (registry_id) REFERENCES ai_rag_registry (registry_id) ON DELETE CASCADE
                )
            """
            
            # Create the table using connection manager
            await self.connection_manager.execute_query(query)
            logger.info("✅ Created ai_rag_metrics table with consolidated analytics")
            
            # Create indexes
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_registry_id ON ai_rag_metrics (registry_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_timestamp ON ai_rag_metrics (timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_health ON ai_rag_metrics (health_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_performance ON ai_rag_metrics (embedding_generation_speed_sec, vector_db_query_response_time_ms)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_quality ON ai_rag_metrics (data_freshness_score, data_completeness_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_resources ON ai_rag_metrics (cpu_usage_percent, memory_usage_percent)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_user_activity ON ai_rag_metrics (user_interaction_count, query_execution_count)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_technique ON ai_rag_metrics (rag_technique_performance)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_document_processing ON ai_rag_metrics (document_processing_stats)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_enterprise_metrics ON ai_rag_metrics (enterprise_metric_type, enterprise_metric_value)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_enterprise_performance ON ai_rag_metrics (enterprise_performance_metric, enterprise_performance_trend)"
            ]
            
            return await self.create_indexes("ai_rag_metrics", index_queries)
            
        except Exception as e:
            logger.error(f"Failed to create ai_rag_metrics table: {e}")
            return False

    async def _create_ai_rag_operations_table(self) -> bool:
        """Create the AI/RAG operations table with consolidated sessions, logs, embeddings, and graph metadata."""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS ai_rag_operations (
                    -- Primary Identification
                    operation_id TEXT PRIMARY KEY,
                    registry_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL CHECK (operation_type IN ('session', 'generation', 'embedding', 'graph', 'retrieval')),
                    timestamp TEXT NOT NULL,
                    
                    -- Session Information (CONSOLIDATED from retrieval_sessions)
                    session_id TEXT,
                    user_id TEXT NOT NULL,
                    query_text TEXT,
                    response_text TEXT,
                    session_start TEXT,
                    session_end TEXT,
                    session_duration_ms INTEGER,
                    
                    -- Generation Logs (CONSOLIDATED from generation_logs)
                    generation_type TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    generation_time_ms INTEGER,
                    generation_quality_score REAL CHECK (generation_quality_score >= 0.0 AND generation_quality_score <= 1.0),
                    
                    -- Embeddings (CONSOLIDATED from embeddings table)
                    embedding_id TEXT,
                    vector_data TEXT,
                    embedding_model TEXT,
                    embedding_dimensions INTEGER,
                    embedding_quality_score REAL CHECK (embedding_quality_score >= 0.0 AND embedding_quality_score <= 1.0),
                    
                    -- Additional Embedding Fields (CONSOLIDATED from embeddings table)
                    vector_type TEXT DEFAULT 'float32' CHECK (vector_type IN ('float32', 'float64', 'int32', 'int64', 'uint8')),
                    model_provider TEXT, -- Model provider (e.g., OpenAI, HuggingFace)
                    model_parameters TEXT DEFAULT '{}', -- JSON: Model parameters
                    generation_timestamp TEXT, -- Generation timestamp
                    generation_duration_ms REAL, -- Generation duration in milliseconds
                    generation_cost REAL, -- Generation cost in credits/tokens
                    similarity_threshold REAL, -- Similarity threshold for retrieval
                    confidence_score REAL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0), -- Confidence score
                    context TEXT, -- Context information
                    storage_location TEXT, -- Storage location identifier
                    storage_format TEXT DEFAULT 'base64' CHECK (storage_format IN ('base64', 'json', 'binary', 'hex')),
                    compression_ratio REAL, -- Compression ratio
                    
                    -- Graph Metadata (CONSOLIDATED from ai_rag_graph_metadata)
                    graphs_json TEXT DEFAULT '{}', -- JSON object with graph_id as keys for unique identification
                    graph_count INTEGER DEFAULT 0, -- Total number of graphs
                    graph_types TEXT DEFAULT '{}', -- JSON object of graph types with counts and graph_ids
                    
                    -- Source Information
                    source_documents TEXT DEFAULT '{}', -- JSON object of document IDs with metadata
                    source_entities TEXT DEFAULT '{}',  -- JSON object of extracted entities with details
                    source_relationships TEXT DEFAULT '{}', -- JSON object of discovered relationships with metadata
                    
                    -- Processing Information
                    processing_status TEXT DEFAULT 'processing' CHECK (processing_status IN ('processing', 'completed', 'failed')),
                    processing_start_time TEXT,
                    processing_end_time TEXT,
                    processing_duration_ms INTEGER,
                    
                    -- Quality Metrics
                    quality_score REAL DEFAULT 0.0 CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
                    validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'failed')),
                    validation_errors TEXT DEFAULT '{}', -- JSON object of validation errors with details
                    
                    -- File Storage References
                    output_directory TEXT,
                    output_files TEXT DEFAULT '{}', -- JSON object of generated files with paths and metadata
                    file_formats TEXT DEFAULT '{}', -- JSON object of available export formats with options
                    
                    -- Integration References
                    kg_neo4j_graph_id TEXT,
                    aasx_integration_id TEXT,
                    twin_registry_id TEXT,
                    
                    -- Tracing & Audit
                    created_by TEXT NOT NULL,
                    updated_by TEXT,
                    dept_id TEXT,
                    org_id TEXT,
                    
                    -- Performance Metrics
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL,
                    
                    -- Metadata (JSON for flexibility)
                    operation_metadata TEXT DEFAULT '{}', -- JSON: Additional operation-specific metadata
                    tags TEXT DEFAULT '{}', -- JSON object of tags with categories and metadata
                    
                    -- Foreign Key Constraints
                    FOREIGN KEY (registry_id) REFERENCES ai_rag_registry (registry_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users (user_id) ON DELETE CASCADE
                )
            """
            
            # Create the table using connection manager
            await self.connection_manager.execute_query(query)
            logger.info("✅ Created ai_rag_operations table with consolidated operations data")
            
            # Create indexes
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_registry_id ON ai_rag_operations (registry_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_operation_type ON ai_rag_operations (operation_type)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_timestamp ON ai_rag_operations (timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_session_id ON ai_rag_operations (session_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_user_id ON ai_rag_operations (user_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_generation_type ON ai_rag_operations (generation_type)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_embedding_id ON ai_rag_operations (embedding_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_embedding_model ON ai_rag_operations (embedding_model)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_vector_type ON ai_rag_operations (vector_type)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_model_provider ON ai_rag_operations (model_provider)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_embedding_quality ON ai_rag_operations (embedding_quality_score, confidence_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_storage ON ai_rag_operations (storage_location, storage_format)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_graph_count ON ai_rag_operations (graph_count)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_processing_status ON ai_rag_operations (processing_status)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_quality_score ON ai_rag_operations (quality_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_validation_status ON ai_rag_operations (validation_status)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_created_by ON ai_rag_operations (created_by)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_dept_id ON ai_rag_operations (dept_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_org_id ON ai_rag_operations (org_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_integration ON ai_rag_operations (kg_neo4j_graph_id, aasx_integration_id, twin_registry_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_rag_operations_performance ON ai_rag_operations (generation_time_ms, memory_usage_mb, cpu_usage_percent)"
            ]
            
            return await self.create_indexes("ai_rag_operations", index_queries)
            
        except Exception as e:
            logger.error(f"Failed to create ai_rag_operations table: {e}")
            return False

    async def _create_consolidated_tables(self) -> bool:
        """Create all consolidated AI RAG tables with enterprise features."""
        try:
            # Create the 3 consolidated tables
            if not await self._create_ai_rag_registry_table():
                return False
            
            if not await self._create_ai_rag_metrics_table():
                return False
            
            if not await self._create_ai_rag_operations_table():
                return False
            
            logger.info("✅ Created all 3 consolidated AI RAG tables")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create consolidated tables: {e}")
            return False
