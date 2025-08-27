"""
AI/RAG Schema Module
====================

Manages AI/RAG database tables for the AASX Digital Twin Framework.
Provides intelligent analysis, vector embeddings, and AI-powered insights
while maintaining world-class traceability and framework integration.
"""

import logging
from typing import List, Dict, Any
from ..base_schema import BaseSchemaModule

logger = logging.getLogger(__name__)


class AIRagSchema(BaseSchemaModule):
    """
    AI/RAG Schema Module
    
    Manages the following tables:
    - ai_rag_registry: Main AI/RAG registry and metadata
    - ai_rag_metrics: Performance metrics and analytics
    """
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.module_name = "ai_rag"
    
    def get_module_description(self) -> str:
        """Get human-readable description of this module."""
        return "Artificial Intelligence and Retrieval-Augmented Generation (AI/RAG) module for intelligent analysis and vector embeddings"
    
    def get_table_names(self) -> List[str]:
        """Get list of table names managed by this module."""
        return ["ai_rag_registry", "ai_rag_metrics"]
    
    def create_tables(self) -> bool:
        """
        Create all AI/RAG tables.
        
        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        logger.info("🤖 Creating AI/RAG Module Tables...")
        
        # Create tables in dependency order
        tables_created = []
        
        # 1. Create AI/RAG Registry Table
        if self._create_ai_rag_registry_table():
            tables_created.append("ai_rag_registry")
        else:
            logger.error("Failed to create ai_rag_registry table")
            return False
        
        # 2. Create AI/RAG Metrics Table
        if self._create_ai_rag_metrics_table():
            tables_created.append("ai_rag_metrics")
        else:
            logger.error("Failed to create ai_rag_metrics table")
            return False
        
        logger.info(f"✅ AI/RAG Module: Created {len(tables_created)} tables successfully")
        return True
    
    def _create_ai_rag_registry_table(self) -> bool:
        """Create the AI/RAG registry table with comprehensive AI/RAG management capabilities."""
        query = """
            CREATE TABLE IF NOT EXISTS ai_rag_registry (
                -- Primary Identification
                registry_id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                registry_name TEXT NOT NULL,
                
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
                
                -- Foreign Key Constraints
                FOREIGN KEY (file_id) REFERENCES files (file_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organizations (org_id) ON DELETE CASCADE,
                FOREIGN KEY (aasx_integration_id) REFERENCES aasx_processing (job_id) ON DELETE SET NULL,
                FOREIGN KEY (twin_registry_id) REFERENCES twin_registry (registry_id) ON DELETE SET NULL,
                FOREIGN KEY (kg_neo4j_id) REFERENCES kg_graph_registry (graph_id) ON DELETE SET NULL
            )
        """
        
        # Create the table
        if not self.create_table("ai_rag_registry", query):
            return False
        
        # Create indexes
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_file_id ON ai_rag_registry (file_id)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_user_id ON ai_rag_registry (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_org_id ON ai_rag_registry (org_id)",
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
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_registry_performance ON ai_rag_registry (performance_score, data_quality_score, reliability_score)"
        ]
        
        return self.create_indexes("ai_rag_registry", index_queries)
    
    def _create_ai_rag_metrics_table(self) -> bool:
        """Create the AI/RAG metrics table with comprehensive performance monitoring."""
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
                
                -- Foreign Key Constraints
                FOREIGN KEY (registry_id) REFERENCES ai_rag_registry (registry_id) ON DELETE CASCADE
            )
        """
        
        # Create the table
        if not self.create_table("ai_rag_metrics", query):
            return False
        
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
            "CREATE INDEX IF NOT EXISTS idx_ai_rag_metrics_document_processing ON ai_rag_metrics (document_processing_stats)"
        ]
        
        return self.create_indexes("ai_rag_metrics", index_queries)



