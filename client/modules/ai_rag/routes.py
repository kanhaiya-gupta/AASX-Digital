"""
AI/RAG System API Routes
Provides REST API endpoints for the AI/RAG system frontend
Uses modular service architecture for clean separation of concerns
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Import authentication components
from src.engine.models.request_context import UserContext
from src.integration.api.dependencies import require_auth, get_current_user

# Import our service modules
from .query_service import QueryService
from .system_service import SystemService
from .project_service import ProjectService
from .services.user_specific_service import AIRAGUserSpecificService
from .services.organization_service import AIRAGOrganizationService

# Import the new modular RAG system
try:
    from src.modules.ai_rag.rag_system import RAGManager
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
@require_auth("read", allow_independent=True)
async def ai_rag_page(
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """AI/RAG system main page"""
    try:
        templates = Jinja2Templates(directory="client/templates")
        
        # Initialize user-specific and organization services
        user_specific_service = AIRAGUserSpecificService(user_context)
        organization_service = AIRAGOrganizationService(user_context)
        
        # Check if system is available
        system_available = RAGManager is not None
        
        # Get user-specific data
        user_projects = user_specific_service.get_user_projects()
        user_files = user_specific_service.get_user_files()
        user_stats = user_specific_service.get_user_statistics()
        organization_stats = organization_service.get_organization_statistics()
        
        # Get user permissions and capabilities
        can_create_project = user_specific_service.can_create_project()
        can_create_file = user_specific_service.can_create_file()
        can_manage_org = organization_service.can_manage_organization()
        
        return templates.TemplateResponse(
            "ai_rag/index.html",
            {
                "request": request,
                "title": "AI/RAG System",
                "description": "Advanced AI/RAG system with multiple techniques",
                "system_available": system_available,
                "user_context": user_context,
                "can_create_project": can_create_project,
                "can_create_file": can_create_file,
                "can_manage_org": can_manage_org,
                "is_independent": getattr(user_context, 'is_independent', None),
                "user_type": getattr(user_context, 'get_user_type', lambda: 'independent')(),
                "user_projects": user_projects,
                "user_files": user_files,
                "user_stats": user_stats,
                "organization_stats": organization_stats
            }
        )
    except Exception as e:
        logger.error(f"Error rendering AI/RAG page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Query processing endpoints
@router.post("/query", response_model=QueryResponse)
@require_auth("read", allow_independent=True)
async def query_ai_rag(
    request: QueryRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Process a query using the RAG system"""
    try:
        # Validate query is not empty
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Initialize user-specific service for access control
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Validate project access if project_id is provided
        if request.project_id and not user_specific_service.can_access_project(request.project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
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
@require_auth("read", allow_independent=True)
async def enhanced_query_ai_rag(
    request: EnhancedQueryRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Enhanced query with context and file-specific information"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access enhanced queries
        if not user_specific_service.can_access_enhanced_queries():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access enhanced queries")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Add user context to request
        if hasattr(request, 'user_id'):
            request.user_id = user_context.user_id
        if hasattr(request, 'organization_id') and user_context.organization_id:
            request.organization_id = user_context.organization_id
        
        # Execute enhanced query
        result = query_service.enhanced_query(request)
        return result
    except Exception as e:
        logger.error(f"Enhanced query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-extract-query", response_model=AutoExtractionQueryResponse)
@require_auth("read", allow_independent=True)
async def auto_extract_query_ai_rag(
    request: AutoExtractionQueryRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Auto-extract file ID and process query"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access auto-extraction queries
        if not user_specific_service.can_access_auto_extraction():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access auto-extraction queries")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Add user context to request
        if hasattr(request, 'user_id'):
            request.user_id = user_context.user_id
        if hasattr(request, 'organization_id') and user_context.organization_id:
            request.organization_id = user_context.organization_id
        
        # Execute auto-extraction query
        result = query_service.auto_extract_query(request)
        return result
    except Exception as e:
        logger.error(f"Auto-extraction query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-file-id", response_model=FileIDExtractionResponse)
@require_auth("read", allow_independent=True)
async def extract_file_id(
    request: FileIDExtractionRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Extract file ID from natural language query"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access file ID extraction
        if not user_specific_service.can_access_file_extraction():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access file ID extraction")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Add user context to request
        if hasattr(request, 'user_id'):
            request.user_id = user_context.user_id
        if hasattr(request, 'organization_id') and user_context.organization_id:
            request.organization_id = user_context.organization_id
        
        # Execute file ID extraction
        result = query_service.extract_file_id(request)
        return result
    except Exception as e:
        logger.error(f"File ID extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/reverse-engineer/{file_id}")
@require_auth("read", allow_independent=True)
async def reverse_engineer_file(
    file_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Reverse engineer AASX file structure"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access reverse engineering
        if not user_specific_service.can_access_reverse_engineering():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access reverse engineering")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Check if user can access this specific file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this file")
        
        # Execute reverse engineering
        result = query_service.reverse_engineer_file(file_id)
        return result
    except Exception as e:
        logger.error(f"Reverse engineering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file-context/{file_id}")
@require_auth("read", allow_independent=True)
async def get_file_context(
    file_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get file context using src/shared/ methods"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access file context
        if not user_specific_service.can_access_file_context():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access file context")
        
        # Check if user can access this specific file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this file")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
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
        logger.error(f"Error getting file context for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project-context/{file_id}")
@require_auth("read", allow_independent=True)
async def get_project_context(
    file_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get project context for a file"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access project context
        if not user_specific_service.can_access_project_context():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access project context")
        
        # Check if user can access this specific file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this file")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        context = query_service.get_project_context(file_id)
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
        logger.error(f"Error getting project context for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-case-context/{file_id}")
@require_auth("read", allow_independent=True)
async def get_use_case_context(
    file_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get use case context for a file"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access use case context
        if not user_specific_service.can_access_use_case_context():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access use case context")
        
        # Check if user can access this specific file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this file")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        context = query_service.get_use_case_context(file_id)
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
        logger.error(f"Error getting use case context for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-twin-context/{file_id}")
@require_auth("read", allow_independent=True)
async def get_digital_twin_context(
    file_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get digital twin context for a file"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access digital twin context
        if not user_specific_service.can_access_digital_twin_context():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access digital twin context")
        
        # Check if user can access this specific file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this file")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        context = query_service.get_digital_twin_context(file_id)
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
        logger.error(f"Error getting digital twin context for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/related-files/{file_id}")
@require_auth("read", allow_independent=True)
async def get_related_files(
    file_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get related files for a given file"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access related files
        if not user_specific_service.can_access_related_files():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access related files")
        
        # Check if user can access this specific file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this file")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        related_files = query_service.get_related_files(file_id)
        return {
            "file_id": file_id,
            "related_files": related_files,
            "count": len(related_files),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting related files for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-twin-health/{file_id}")
@require_auth("read", allow_independent=True)
async def get_digital_twin_health(
    file_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get digital twin health metrics for a file"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access digital twin health
        if not user_specific_service.can_access_digital_twin_health():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access digital twin health")
        
        # Check if user can access this specific file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this file")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        health_metrics = query_service.get_digital_twin_health(file_id)
        return {
            "file_id": file_id,
            "health_metrics": health_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting digital twin health for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-files")
@require_auth("read", allow_independent=True)
async def search_files_by_content(
    search_term: str, 
    project_id: Optional[str] = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Search files by content using src/shared/ methods"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        if project_id:
            # Check if user can access this project
            if not user_specific_service.can_access_project(project_id):
                raise HTTPException(status_code=403, detail="Access denied to this project")
            # Search within specific project
            files = user_specific_service.get_user_files(project_id)
        else:
            # Search across all accessible files
            files = user_specific_service.get_user_files()
        
        # Filter files by search term (mock implementation - replace with actual search)
        filtered_files = [f for f in files if search_term.lower() in f.get('name', '').lower()]
        
        return {
            "search_term": search_term,
            "project_id": project_id,
            "files": filtered_files,
            "count": len(filtered_files),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching files with term '{search_term}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/techniques/compare", response_model=TechniqueComparisonResponse)
@require_auth("read", allow_independent=True)
async def compare_techniques(
    request: TechniqueComparisonRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Compare different RAG techniques"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access technique comparison
        if not user_specific_service.can_access_technique_comparison():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access technique comparison")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Add user context to request
        if hasattr(request, 'user_id'):
            request.user_id = user_context.user_id
        if hasattr(request, 'organization_id') and user_context.organization_id:
            request.organization_id = user_context.organization_id
        
        # Execute technique comparison
        result = query_service.compare_techniques(request)
        return result
    except Exception as e:
        logger.error(f"Technique comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/techniques/recommendations", response_model=TechniqueRecommendationResponse)
@require_auth("read", allow_independent=True)
async def get_technique_recommendations(
    request: TechniqueRecommendationRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Get technique recommendations for a query"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access technique recommendations
        if not user_specific_service.can_access_technique_recommendations():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access technique recommendations")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Add user context to request
        if hasattr(request, 'user_id'):
            request.user_id = user_context.user_id
        if hasattr(request, 'organization_id') and user_context.organization_id:
            request.organization_id = user_context.organization_id
        
        # Execute technique recommendations
        result = query_service.get_technique_recommendations(request)
        return result
    except Exception as e:
        logger.error(f"Technique recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add missing status endpoints that JavaScript is calling
@router.get("/ai_rag/status")
@require_auth("read", allow_independent=True)
async def get_ai_rag_status(user_context: UserContext = Depends(get_current_user)):
    """Get AI/RAG system status"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access system status")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        status = system_service.get_ai_rag_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get AI/RAG status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/etl/status")
@require_auth("read", allow_independent=True)
async def get_etl_status(user_context: UserContext = Depends(get_current_user)):
    """Get ETL system status"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access ETL status
        if not user_specific_service.can_access_etl_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access ETL status")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        status = system_service.get_etl_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get ETL status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kg/status")
@require_auth("read", allow_independent=True)
async def get_kg_status(user_context: UserContext = Depends(get_current_user)):
    """Get Knowledge Graph system status"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access KG status
        if not user_specific_service.can_access_kg_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access Knowledge Graph status")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        status = system_service.get_kg_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get KG status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twin/status")
@require_auth("read", allow_independent=True)
async def get_twin_status(user_context: UserContext = Depends(get_current_user)):
    """Get Digital Twin system status"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access Digital Twin status
        if not user_specific_service.can_access_digital_twin_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access Digital Twin status")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        status = system_service.get_digital_twin_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get Digital Twin status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/status")
@require_auth("read", allow_independent=True)
async def get_system_status_general(user_context: UserContext = Depends(get_current_user)):
    """Get general system status"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access system status")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        status = system_service.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add missing endpoints that JavaScript is calling
@router.get("/techniques", response_model=List[Dict[str, Any]])
@require_auth("read", allow_independent=True)
async def get_techniques(user_context: UserContext = Depends(get_current_user)):
    """Get available RAG techniques"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access techniques
        if not user_specific_service.can_access_techniques():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access techniques")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        techniques = query_service.get_available_techniques()
        return techniques
    except Exception as e:
        logger.error(f"Failed to get techniques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
@require_auth("read", allow_independent=True)
async def get_stats(user_context: UserContext = Depends(get_current_user)):
    """Get system statistics for the current user"""
    try:
        # Initialize user-specific and organization services
        user_specific_service = AIRAGUserSpecificService(user_context)
        organization_service = AIRAGOrganizationService(user_context)
        
        # Get user-specific statistics
        user_stats = user_specific_service.get_user_statistics()
        organization_stats = organization_service.get_organization_statistics()
        
        # Combine statistics
        combined_stats = {
            "user_stats": user_stats,
            "organization_stats": organization_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "stats": combined_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        return {
            "status": "error",
            "stats": {},
            "timestamp": datetime.now().isoformat()
        }

@router.get("/collections")
@require_auth("read", allow_independent=True)
async def get_collections(user_context: UserContext = Depends(get_current_user)):
    """Get vector database collections"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access collections
        if not user_specific_service.can_access_collections():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access collections")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        collections = system_service.get_collections()
        return {
            "success": True,
            "collections": collections,
            "count": len(collections),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-twin-stats")
@require_auth("read", allow_independent=True)
async def get_digital_twin_stats(user_context: UserContext = Depends(get_current_user)):
    """Get digital twin statistics"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access digital twin stats
        if not user_specific_service.can_access_digital_twin_stats():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access digital twin statistics")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        stats = system_service.get_digital_twin_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get digital twin stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-data-stats")
@require_auth("read", allow_independent=True)
async def get_vector_data_stats(user_context: UserContext = Depends(get_current_user)):
    """Get vector data statistics"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access vector data stats
        if not user_specific_service.can_access_vector_data_stats():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access vector data statistics")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        stats = system_service.get_vector_data_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get vector data stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generator-config")
@require_auth("read", allow_independent=True)
async def get_generator_config(user_context: UserContext = Depends(get_current_user)):
    """Get generator configuration"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access generator config
        if not user_specific_service.can_access_generator_config():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access generator configuration")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        config = system_service.get_generator_config()
        return {
            "success": True,
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get generator config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
@require_auth("read", allow_independent=True)
async def get_models(user_context: UserContext = Depends(get_current_user)):
    """Get available AI models"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access models
        if not user_specific_service.can_access_models():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access models")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        models = system_service.get_available_models()
        return {
            "success": True,
            "models": models,
            "count": len(models),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Project management endpoints
@router.get("/projects")
@require_auth("read", allow_independent=True)
async def get_projects(user_context: UserContext = Depends(get_current_user)):
    """Get list of available projects for the current user"""
    try:
        # Initialize user-specific service
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Get user-specific projects
        user_projects = user_specific_service.get_user_projects()
        
        return {
            "projects": user_projects,
            "count": len(user_projects),
            "timestamp": datetime.now().isoformat(),
            "user_id": getattr(user_context, 'user_id', None),
            "organization_id": getattr(user_context, 'organization_id', None)
        }
    except Exception as e:
        logger.error(f"Error getting user projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
@require_auth("read", allow_independent=True)
async def get_project_files(
    project_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get files for a specific project"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access this project
        if not user_specific_service.can_access_project(project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        # Get user-specific files for this project
        user_files = user_specific_service.get_user_files(project_id)
        
        return {
            "files": user_files,
            "count": len(user_files),
            "project_id": project_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoints
@router.get("/config")
@require_auth("read", allow_independent=True)
async def get_config(user_context: UserContext = Depends(get_current_user)):
    """Get system configuration"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access system config
        if not user_specific_service.can_access_system_config():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access system configuration")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        config = system_service.get_system_config()
        return {
            "success": True,
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query-config")
@require_auth("read", allow_independent=True)
async def get_query_config(user_context: UserContext = Depends(get_current_user)):
    """Get query configuration"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access query config
        if not user_specific_service.can_access_query_config():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access query configuration")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        config = query_service.get_query_config()
        return {
            "success": True,
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get query config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-config")
@require_auth("read", allow_independent=True)
async def get_vector_config(user_context: UserContext = Depends(get_current_user)):
    """Get vector database configuration"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access vector config
        if not user_specific_service.can_access_vector_config():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access vector database configuration")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        config = system_service.get_vector_config()
        return {
            "success": True,
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get vector config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Vector query endpoints
@router.get("/vectors")
@require_auth("read", allow_independent=True)
async def get_vectors(
    collection_name: Optional[str] = None, 
    limit: int = 100,
    user_context: UserContext = Depends(get_current_user)
):
    """Get vector data"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access vectors
        if not user_specific_service.can_access_vectors():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access vector data")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        vectors = system_service.get_vectors(collection_name, limit)
        return {
            "success": True,
            "vectors": vectors,
            "count": len(vectors),
            "collection": collection_name,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Integration endpoints
@router.get("/project-data")
@require_auth("read", allow_independent=True)
async def get_project_data(user_context: UserContext = Depends(get_current_user)):
    """Get project data"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access project data
        if not user_specific_service.can_access_project_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access project data")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Get user-specific project data
        project_data = user_specific_service.get_user_project_data()
        
        return {
            "success": True,
            "project_data": project_data,
            "count": len(project_data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get project data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System management endpoints
@router.get("/status", response_model=SystemStatusResponse)
@require_auth("read", allow_independent=True)
async def get_system_status(user_context: UserContext = Depends(get_current_user)):
    """Get system status"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access system status")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        status = system_service.get_system_status()
        return SystemStatusResponse(**status)
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
@require_auth("read", allow_independent=True)
async def health_check(user_context: UserContext = Depends(get_current_user)):
    """Health check endpoint"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access health check
        if not user_specific_service.can_access_health_check():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access health check")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        health = system_service.get_health_status()
        return {
            "success": True,
            "status": "healthy",
            "health": health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-db-info")
@require_auth("read", allow_independent=True)
async def get_vector_db_info(user_context: UserContext = Depends(get_current_user)):
    """Get vector database information"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access vector database info
        if not user_specific_service.can_access_vector_db_info():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access vector database information")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        info = system_service.get_vector_db_info()
        return {
            "success": True,
            "info": info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get vector database info: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/demo")
@require_auth("read", allow_independent=True)
async def run_demo_queries(user_context: UserContext = Depends(get_current_user)):
    """Run demo queries for testing purposes"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access demo functionality
        if not user_specific_service.can_access_demo():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access demo functionality")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Run demo queries
        demo_results = query_service.run_demo_queries()
        return {
            "success": True,
            "demo_results": demo_results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to run demo queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
@require_auth("read", allow_independent=True)
async def search_similar_documents(
    query: str, 
    project_id: Optional[str] = None, 
    limit: int = 10,
    user_context: UserContext = Depends(get_current_user)
):
    """Search for similar documents using vector similarity"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access search functionality
        if not user_specific_service.can_access_search():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access search functionality")
        
        # If project_id is provided, check if user can access this project
        if project_id and not user_specific_service.can_access_project(project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Perform search
        search_results = query_service.search_similar_documents(query, project_id, limit)
        return {
            "success": True,
            "query": query,
            "results": search_results,
            "count": len(search_results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to search documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup-vector-data")
@require_auth("admin", allow_independent=False)
async def backup_vector_data(user_context: UserContext = Depends(get_current_user)):
    """Backup vector database data"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can manage vector data
        if not user_specific_service.can_manage_vector_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to backup vector data")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Perform backup
        backup_result = system_service.backup_vector_data()
        return {
            "success": True,
            "backup_result": backup_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to backup vector data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-vector-data")
@require_auth("admin", allow_independent=False)
async def clear_vector_data(user_context: UserContext = Depends(get_current_user)):
    """Clear all vector database data"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can manage vector data
        if not user_specific_service.can_manage_vector_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to clear vector data")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Clear vector data
        clear_result = system_service.clear_vector_data()
        return {
            "success": True,
            "clear_result": clear_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to clear vector data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/aasx-analysis")
@require_auth("read", allow_independent=True)
async def aasx_analysis(user_context: UserContext = Depends(get_current_user)):
    """Perform AASX file analysis"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access AASX analysis
        if not user_specific_service.can_access_aasx_analysis():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access AASX analysis")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Perform AASX analysis
        analysis_result = system_service.analyze_aasx_files()
        return {
            "success": True,
            "analysis_result": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to perform AASX analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-aasx")
@require_auth("read", allow_independent=True)
async def export_aasx(user_context: UserContext = Depends(get_current_user)):
    """Export AASX data"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access AASX export
        if not user_specific_service.can_access_aasx_export():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access AASX export")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Export AASX data
        export_result = system_service.export_aasx_data()
        return {
            "success": True,
            "export_result": export_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to export AASX data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
@require_auth("read", allow_independent=True)
async def get_stored_documents(
    limit: int = 50,
    user_context: UserContext = Depends(get_current_user)
):
    """Get stored documents from the system"""
    try:
        # Initialize authentication services
        user_specific_service = AIRAGUserSpecificService(user_context)
        
        # Check if user can access documents
        if not user_specific_service.can_access_documents():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access documents")
        
        # Get services
        query_service, system_service, project_service = get_services()
        
        # Get documents (filtered by user access)
        documents = user_specific_service.get_user_documents(limit)
        return {
            "success": True,
            "documents": documents,
            "count": len(documents),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get stored documents: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 