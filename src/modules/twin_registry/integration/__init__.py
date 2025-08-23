"""
Twin Registry Integration Layer

Provides integration capabilities for external systems and workflows.
Phase 3: Event System & Automation with pure async support.

Integrations:
- File upload processing
- ETL pipeline integration
- AI RAG system integration
- External API integrations
- Integration coordination
"""

__version__ = "3.3.0"
__description__ = "Integration layer for Twin Registry operations"

# File Upload Integration
from .file_upload_integration import (
    FileUploadIntegration,
    FileUploadProcessor,
    FileUploadValidator,
    FileUploadInfo,
    FileUploadIntegrationConfig
)

# ETL Integration
from .etl_integration import (
    ETLIntegration,
    ETLProcessor,
    ETLValidator,
    ETLMetricsCollector,
    ETLJobInfo,
    ETLIntegrationConfig
)

# AI RAG Integration
from .ai_rag_integration import (
    AIRAGIntegration,
    RAGProcessor,
    RAGValidator,
    RAGMetricsCollector,
    AIRAGRequest,
    AIRAGResponse,
    AIRAGIntegrationConfig
)

# Integration Coordinator
from .integration_coordinator import IntegrationCoordinator

__all__ = [
    # File Upload
    "FileUploadIntegration",
    "FileUploadProcessor", 
    "FileUploadValidator",
    "FileUploadInfo",
    "FileUploadIntegrationConfig",
    
    # ETL
    "ETLIntegration",
    "ETLProcessor",
    "ETLValidator",
    "ETLMetricsCollector",
    "ETLJobInfo",
    "ETLIntegrationConfig",
    
    # AI RAG
    "AIRAGIntegration",
    "RAGProcessor",
    "RAGValidator",
    "RAGMetricsCollector",
    "AIRAGRequest",
    "AIRAGResponse",
    "AIRAGIntegrationConfig",
    
    # Integration Coordinator
    "IntegrationCoordinator"
]
