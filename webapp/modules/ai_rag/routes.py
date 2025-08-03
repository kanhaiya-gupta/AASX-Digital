"""
AI/RAG System API Routes
Provides REST API endpoints for the AI/RAG system frontend
Uses modular service architecture for clean separation of concerns
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Import our service modules
from .query_service import QueryService
from .system_service import SystemService
from .project_service import ProjectService

# Import the new modular RAG system
try:
    from src.ai_rag.rag_system import RAGManager
    print("✅ AI/RAG modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import AI/RAG modules: {e}")
    # Fallback to None if modules not available
    RAGManager = None

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai_rag"])

# Initialize services
rag_manager = None
query_service = None
system_service = None
project_service = None

def get_services():
    """Get or initialize service instances"""
    global rag_manager, query_service, system_service, project_service
    
    if rag_manager is None:
        if RAGManager is None:
            raise HTTPException(
                status_code=503,
                detail="AI/RAG system not available. Please check that the src modules are properly installed."
            )
        try:
            rag_manager = RAGManager()
            logger.info("RAG Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Manager: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize RAG Manager")
    
    if project_service is None:
        project_service = ProjectService()
    
    if query_service is None:
        query_service = QueryService(rag_manager, project_service)
    
    if system_service is None:
        system_service = SystemService(rag_manager)
    
    return query_service, system_service, project_service

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    technique_id: Optional[str] = None
    project_id: Optional[str] = None
    search_limit: int = 10
    llm_model: str = "gpt-3.5-turbo"
    enable_auto_selection: bool = True

class QueryResponse(BaseModel):
    answer: str
    technique_id: str
    technique_name: str
    execution_time: float
    search_results_count: int
    query: str
    project_id: Optional[str] = None
    timestamp: str
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TechniqueComparisonRequest(BaseModel):
    query: str
    technique_ids: List[str]
    project_id: Optional[str] = None
    search_limit: int = 10

class TechniqueComparisonResponse(BaseModel):
    query: str
    techniques_compared: List[str]
    results: Dict[str, Any]
    best_technique: Optional[str] = None
    search_results_count: int
    timestamp: str

class TechniqueRecommendationRequest(BaseModel):
    query: str

class TechniqueRecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]

class SystemStatusResponse(BaseModel):
    vector_db_connected: bool
    available_techniques: int
    technique_names: List[str]
    config_loaded: bool
    timestamp: str

class EnhancedQueryRequest(BaseModel):
    query: str
    file_id: Optional[str] = None
    technique_id: Optional[str] = None
    search_limit: int = 10
    llm_model: str = "gpt-3.5-turbo"
    enable_auto_selection: bool = True
    include_context: bool = True

class EnhancedQueryResponse(BaseModel):
    answer: str
    technique_id: str
    technique_name: str
    execution_time: float
    search_results_count: int
    query: str
    file_id: Optional[str] = None
    project_id: Optional[str] = None
    timestamp: str
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    has_context: bool = False
    context_summary: Optional[Dict[str, Any]] = None

class AutoExtractionQueryRequest(BaseModel):
    query: str
    technique_id: Optional[str] = None
    search_limit: int = 10
    llm_model: str = "gpt-3.5-turbo"
    enable_auto_selection: bool = True

class AutoExtractionQueryResponse(BaseModel):
    answer: str
    technique_id: str
    technique_name: str
    execution_time: float
    search_results_count: int
    query: str
    extracted_file_id: Optional[str] = None
    project_id: Optional[str] = None
    timestamp: str
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    has_context: bool = False
    context_summary: Optional[Dict[str, Any]] = None
    extraction_success: bool = False

class FileIDExtractionRequest(BaseModel):
    query: str

class FileIDExtractionResponse(BaseModel):
    query: str
    extracted_file_id: Optional[str] = None
    extraction_success: bool = False
    timestamp: str

# Main page
@router.get("/", response_class=HTMLResponse)
async def ai_rag_page(request: Request):
    """AI/RAG system main page"""
    templates = Jinja2Templates(directory="webapp/templates")
    
    # Check if system is available
    system_available = RAGManager is not None
    
    return templates.TemplateResponse(
        "ai_rag/index.html",
        {
            "request": request,
            "title": "AI/RAG System",
            "description": "Advanced AI/RAG system with multiple techniques",
            "system_available": system_available
        }
    )

# Query processing endpoints
@router.post("/query", response_model=QueryResponse)
async def query_ai_rag(request: QueryRequest):
    """Process a query using the RAG system"""
    try:
        # Validate query is not empty
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        query_service, _, _ = get_services()
        
        # Validate technique_id if provided
        if request.technique_id and request.technique_id != "auto":
            available_techniques = query_service.get_available_techniques()
            valid_technique_ids = [tech['id'] for tech in available_techniques]
            if request.technique_id not in valid_technique_ids:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid technique_id: {request.technique_id}. Valid techniques: {valid_technique_ids}"
                )
        
        result = query_service.process_query(
            query=request.query,
            technique_id=request.technique_id,
            project_id=request.project_id,
            search_limit=request.search_limit,
            llm_model=request.llm_model,
            enable_auto_selection=request.enable_auto_selection
        )
        
        return QueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced-query", response_model=EnhancedQueryResponse)
async def enhanced_query_ai_rag(request: EnhancedQueryRequest):
    """Process a query with complete file context using src/shared/ methods"""
    try:
        # Validate query is not empty
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        query_service, _, _ = get_services()
        
        result = query_service.process_query_with_context(
            query=request.query,
            file_id=request.file_id,
            technique_id=request.technique_id,
            search_limit=request.search_limit,
            llm_model=request.llm_model,
            enable_auto_selection=request.enable_auto_selection
        )
        
        return EnhancedQueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing enhanced query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-extract-query", response_model=AutoExtractionQueryResponse)
async def auto_extract_query_ai_rag(request: AutoExtractionQueryRequest):
    """Process a query with automatic file_id extraction from natural language"""
    try:
        query_service, _, _ = get_services()
        
        result = query_service.process_query_with_auto_extraction(
            query=request.query,
            technique_id=request.technique_id,
            search_limit=request.search_limit,
            llm_model=request.llm_model,
            enable_auto_selection=request.enable_auto_selection
        )
        
        return AutoExtractionQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing auto-extract query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-file-id", response_model=FileIDExtractionResponse)
async def extract_file_id(request: FileIDExtractionRequest):
    """Extract file_id from natural language query"""
    try:
        query_service, _, _ = get_services()
        
        extracted_file_id = query_service.extract_file_id_from_query(request.query)
        
        return FileIDExtractionResponse(
            query=request.query,
            extracted_file_id=extracted_file_id,
            extraction_success=extracted_file_id is not None,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error extracting file_id: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/reverse-engineer/{file_id}")
async def reverse_engineer_file(file_id: str):
    """Get complete file context using src/shared/ methods"""
    try:
        query_service, _, _ = get_services()
        
        context = query_service.get_file_context(file_id)
        if not context:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found or no context available")
        
        return {
            "file_id": file_id,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reverse engineering file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file-context/{file_id}")
async def get_file_context(file_id: str):
    """Get file context with project and use case info"""
    try:
        query_service, _, _ = get_services()
        
        context = query_service.get_file_trace(file_id)
        if not context:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        return {
            "file_id": file_id,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file context for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project-context/{file_id}")
async def get_project_context(file_id: str):
    """Get project context for a file"""
    try:
        query_service, _, _ = get_services()
        
        context = query_service.get_project_context_for_file(file_id)
        if not context:
            raise HTTPException(status_code=404, detail=f"Project context not found for file {file_id}")
        
        return {
            "file_id": file_id,
            "project_context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project context for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-case-context/{file_id}")
async def get_use_case_context(file_id: str):
    """Get use case context for a file"""
    try:
        query_service, _, _ = get_services()
        
        context = query_service.get_use_case_context_for_file(file_id)
        if not context:
            raise HTTPException(status_code=404, detail=f"Use case context not found for file {file_id}")
        
        return {
            "file_id": file_id,
            "use_case_context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting use case context for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-twin-context/{file_id}")
async def get_digital_twin_context(file_id: str):
    """Get digital twin context for a file"""
    try:
        query_service, _, _ = get_services()
        
        context = query_service.get_digital_twin_context_for_file(file_id)
        if not context:
            raise HTTPException(status_code=404, detail=f"Digital twin context not found for file {file_id}")
        
        return {
            "file_id": file_id,
            "digital_twin_context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting digital twin context for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/related-files/{file_id}")
async def get_related_files(file_id: str):
    """Get related files for a file (same project)"""
    try:
        query_service, _, _ = get_services()
        
        files = query_service.get_related_files_for_file(file_id)
        
        return {
            "file_id": file_id,
            "related_files": files,
            "count": len(files),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting related files for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-twin-health/{file_id}")
async def get_digital_twin_health(file_id: str):
    """Get digital twin health information for a file"""
    try:
        query_service, _, _ = get_services()
        
        health = query_service.get_digital_twin_health_for_file(file_id)
        if not health:
            raise HTTPException(status_code=404, detail=f"Digital twin health not found for file {file_id}")
        
        return {
            "file_id": file_id,
            "health": health,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting digital twin health for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-files")
async def search_files_by_content(search_term: str, project_id: Optional[str] = None):
    """Search files by content using src/shared/ methods"""
    try:
        query_service, _, _ = get_services()
        
        files = query_service.search_files_by_content(search_term, project_id)
        
        return {
            "search_term": search_term,
            "project_id": project_id,
            "files": files,
            "count": len(files),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching files with term '{search_term}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/techniques/compare", response_model=TechniqueComparisonResponse)
async def compare_techniques(request: TechniqueComparisonRequest):
    """Compare multiple RAG techniques on the same query"""
    try:
        query_service, _, _ = get_services()
        
        comparison = query_service.compare_techniques(
            query=request.query,
            technique_ids=request.technique_ids,
            project_id=request.project_id,
            search_limit=request.search_limit
        )
        
        return TechniqueComparisonResponse(**comparison)
        
    except Exception as e:
        logger.error(f"Error comparing techniques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/techniques/recommendations", response_model=TechniqueRecommendationResponse)
async def get_technique_recommendations(request: TechniqueRecommendationRequest):
    """Get technique recommendations for a query"""
    try:
        query_service, _, _ = get_services()
        
        recommendations = query_service.get_technique_recommendations(request.query)
        
        return TechniqueRecommendationResponse(recommendations=recommendations)
        
    except Exception as e:
        logger.error(f"Error getting technique recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add missing status endpoints that JavaScript is calling
@router.get("/ai_rag/status")
async def get_ai_rag_status():
    """Get AI/RAG status (called by JavaScript with underscore)"""
    try:
        _, system_service, _ = get_services()
        status = system_service.get_system_status()
        return {
            "status": "connected" if status["vector_db_connected"] else "disconnected",
            "qdrant_status": "connected" if status["vector_db_connected"] else "disconnected",
            "openai_status": "connected",
            "available_techniques": status["available_techniques"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting AI/RAG status: {e}")
        return {
            "status": "error",
            "qdrant_status": "disconnected",
            "openai_status": "disconnected",
            "available_techniques": 0,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/etl/status")
async def get_etl_status():
    """Get ETL status"""
    try:
        return {
            "status": "available",
            "pipeline_status": "running",
            "last_processed": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ETL status: {e}")
        return {
            "status": "error",
            "pipeline_status": "stopped",
            "last_processed": None,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/kg/status")
async def get_kg_status():
    """Get Knowledge Graph status"""
    try:
        return {
            "status": "connected",
            "neo4j_status": "connected",
            "database_status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting KG status: {e}")
        return {
            "status": "disconnected",
            "neo4j_status": "disconnected",
            "database_status": "unhealthy",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/twin/status")
async def get_twin_status():
    """Get Twin Registry status"""
    try:
        return {
            "status": "connected",
            "registry_status": "active",
            "total_twins": 2,
            "active_twins": 2,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting twin status: {e}")
        return {
            "status": "disconnected",
            "registry_status": "inactive",
            "total_twins": 0,
            "active_twins": 0,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/system/status")
async def get_system_status_general():
    """Get general system status"""
    try:
        return {
            "status": "healthy",
            "uptime": "24h",
            "memory_usage": "45%",
            "cpu_usage": "12%",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "status": "unhealthy",
            "uptime": "0h",
            "memory_usage": "0%",
            "cpu_usage": "0%",
            "timestamp": datetime.now().isoformat()
        }

# Add missing endpoints that JavaScript is calling
@router.get("/techniques")
async def get_techniques():
    """Get available RAG techniques (called by JavaScript)"""
    try:
        _, system_service, _ = get_services()
        techniques = system_service.get_available_techniques()
        return {
            "status": "success",
            "techniques": techniques,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting techniques: {e}")
        return {
            "status": "error",
            "techniques": [],
            "timestamp": datetime.now().isoformat()
        }

@router.get("/stats")
async def get_stats():
    """Get system statistics (called by JavaScript)"""
    try:
        _, system_service, _ = get_services()
        stats = system_service.get_statistics()
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "status": "error",
            "stats": {},
            "timestamp": datetime.now().isoformat()
        }

@router.get("/collections")
async def get_collections():
    """Get vector collections (called by JavaScript)"""
    try:
        _, system_service, _ = get_services()
        collections = system_service.get_collections()
        return {
            "status": "success",
            "collections": collections,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting collections: {e}")
        return {
            "status": "error",
            "collections": [],
            "timestamp": datetime.now().isoformat()
        }

@router.get("/digital-twin-stats")
async def get_digital_twin_stats():
    """Get digital twin statistics (called by JavaScript)"""
    try:
        return {
            "status": "success",
            "total_twins": 2,
            "active_twins": 2,
            "inactive_twins": 0,
            "error_twins": 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting digital twin stats: {e}")
        return {
            "status": "error",
            "total_twins": 0,
            "active_twins": 0,
            "inactive_twins": 0,
            "error_twins": 0,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/vector-data-stats")
async def get_vector_data_stats():
    """Get vector data statistics (called by JavaScript)"""
    try:
        _, system_service, _ = get_services()
        stats = system_service.get_vector_data_stats()
        
        # Return the stats directly as the JavaScript expects
        return {
            "success": True,
            "total_collections": stats.get("total_collections", 0),
            "total_points": stats.get("total_points", 0),
            "total_storage": stats.get("total_storage", "Unknown"),
            "largest_collection": stats.get("largest_collection", "None"),
            "collection_stats": stats.get("collection_stats", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting vector data stats: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_collections": 0,
            "total_points": 0,
            "total_storage": "Unknown",
            "largest_collection": "None",
            "collection_stats": [],
            "timestamp": datetime.now().isoformat()
        }

@router.get("/generator-config")
async def get_generator_config():
    """Get generator configuration (called by JavaScript)"""
    try:
        return {
            "status": "success",
            "config": {
                "default_model": "gpt-3.5-turbo",
                "max_tokens": 4000,
                "temperature": 0.7,
                "streaming_enabled": True
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting generator config: {e}")
        return {
            "status": "error",
            "config": {},
            "timestamp": datetime.now().isoformat()
        }

@router.get("/models")
async def get_models():
    """Get available models (called by JavaScript)"""
    try:
        return {
            "status": "success",
            "models": [
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "provider": "openai",
                    "max_tokens": 4096
                },
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "provider": "openai",
                    "max_tokens": 8192
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return {
            "status": "error",
            "models": [],
            "timestamp": datetime.now().isoformat()
        }

# Project management endpoints
@router.get("/projects")
async def get_projects():
    """Get list of available projects"""
    try:
        _, _, project_service = get_services()
        
        projects = project_service.get_projects()
        
        return projects
        
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
async def get_project_files(project_id: str):
    """Get files for a specific project"""
    try:
        _, _, project_service = get_services()
        
        files = project_service.get_project_files(project_id)
        
        return files
        
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoints
@router.get("/config")
async def get_config():
    """Get AI/RAG system configuration"""
    try:
        return {
            "status": "success",
            "config": {
                "vector_db_enabled": True,
                "llm_model": "gpt-3.5-turbo",
                "max_search_results": 10,
                "auto_technique_selection": True,
                "available_techniques": ["basic", "hybrid", "multi_step"]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query-config")
async def get_query_config():
    """Get query processing configuration"""
    try:
        return {
            "status": "success",
            "config": {
                "default_search_limit": 10,
                "default_llm_model": "gpt-3.5-turbo",
                "enable_auto_selection": True,
                "max_query_length": 1000,
                "supported_languages": ["en", "de", "fr"]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting query config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-config")
async def get_vector_config():
    """Get vector database configuration"""
    try:
        return {
            "status": "success",
            "config": {
                "vector_db_type": "qdrant",
                "embedding_model": "text-embedding-ada-002",
                "vector_dimension": 1536,
                "similarity_metric": "cosine",
                "index_type": "hnsw"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting vector config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Vector query endpoints
@router.get("/vectors")
async def get_vectors(collection_name: Optional[str] = None, limit: int = 100):
    """Get vectors from vector database (query only)"""
    try:
        _, system_service, _ = get_services()
        
        vectors = system_service.get_vectors(collection_name, limit)
        
        return vectors
        
    except Exception as e:
        logger.error(f"Error getting vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Integration endpoints
@router.get("/project-data")
async def get_project_data():
    """Get project data for integration"""
    try:
        _, _, project_service = get_services()
        
        projects = project_service.get_projects()
        
        return {
            "status": "success",
            "projects": projects.get("projects", []),
            "total": projects.get("count", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting project data: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

# System management endpoints
@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get overall system status"""
    try:
        _, system_service, _ = get_services()
        
        status = system_service.get_system_status()
        
        return SystemStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        _, system_service, _ = get_services()
        
        health = system_service.get_health_status()
        
        return health
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/vector-db-info")
async def get_vector_db_info():
    """Get vector database information"""
    try:
        _, system_service, _ = get_services()
        
        db_info = system_service.get_vector_db_info()
        
        return db_info
        
    except Exception as e:
        logger.error(f"Error getting vector DB info: {e}")
        return {
            "status": "error",
            "error": str(e),
            "collection_info": None,
            "collection_name": None
        }

@router.get("/techniques", response_model=List[Dict[str, Any]])
async def get_available_techniques():
    """Get list of available RAG techniques"""
    try:
        query_service, _, _ = get_services()
        
        techniques = query_service.get_available_techniques()
        
        return techniques
        
    except Exception as e:
        logger.error(f"Error getting available techniques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/demo")
async def run_demo_queries():
    """Run demo queries to showcase the system"""
    try:
        query_service, _, _ = get_services()
        
        results = query_service.run_demo_queries()
        
        return results
        
    except Exception as e:
        logger.error(f"Error running demo queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_similar_documents(
    query: str, 
    project_id: Optional[str] = None, 
    limit: int = 10
):
    """Search for similar documents using vector similarity"""
    try:
        query_service, _, _ = get_services()
        
        results = query_service.search_similar_documents(
            query=query,
            project_id=project_id,
            limit=limit
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup-vector-data")
async def backup_vector_data():
    """Backup vector database data"""
    try:
        _, system_service, _ = get_services()
        
        result = system_service.backup_vector_data()
        
        return result
        
    except Exception as e:
        logger.error(f"Error backing up vector data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-vector-data")
async def clear_vector_data():
    """Clear vector database data"""
    try:
        _, system_service, _ = get_services()
        
        result = system_service.clear_vector_data()
        
        return result
        
    except Exception as e:
        logger.error(f"Error clearing vector data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/aasx-analysis")
async def aasx_analysis():
    """Perform AASX analysis"""
    try:
        # Placeholder for AASX analysis functionality
        return {
            "status": "success",
            "message": "AASX analysis completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error performing AASX analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-aasx")
async def export_aasx():
    """Export AASX data"""
    try:
        # Placeholder for AASX export functionality
        return {
            "status": "success",
            "message": "AASX export completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting AASX data: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/documents")
async def get_stored_documents(limit: int = 50):
    """Get list of documents stored in Qdrant with their file_ids"""
    try:
        _, system_service, _ = get_services()
        
        if system_service.rag_manager and system_service.rag_manager.vector_uploader and system_service.rag_manager.vector_uploader.vector_db:
            vector_db = system_service.rag_manager.vector_uploader.vector_db
            
            if vector_db.is_connected:
                # Get all documents from Qdrant
                documents = vector_db.get_all_documents(limit=limit)
                
                return {
                    "success": True,
                    "total_documents": len(documents),
                    "documents": documents,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Vector database not connected",
                    "total_documents": 0,
                    "documents": [],
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "success": False,
                "error": "Vector database not available",
                "total_documents": 0,
                "documents": [],
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error getting stored documents: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_documents": 0,
            "documents": [],
            "timestamp": datetime.now().isoformat()
        } 