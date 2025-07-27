"""
AI/RAG System API Routes
Provides REST API endpoints for the AI/RAG system frontend
Integrated with the new modular RAG system
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging
from pathlib import Path
import sys
from datetime import datetime

# Import the new modular RAG system
try:
    from src.ai_rag.rag_system import RAGManager
    from src.ai_rag.vector_embedding_upload import VectorEmbeddingUploader
    from src.shared.management import ProjectManager, FileManagementError
    print("✅ AI/RAG modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import AI/RAG modules: {e}")
    # Fallback to None if modules not available
    RAGManager = None
    VectorEmbeddingUploader = None
    ProjectManager = None
    FileManagementError = None

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize RAG manager
rag_manager = None

def get_rag_manager():
    """Get or initialize RAG manager instance"""
    global rag_manager
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
    return rag_manager

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

class ProjectEmbeddingRequest(BaseModel):
    project_id: str

class ProjectEmbeddingResponse(BaseModel):
    project_id: str
    status: str
    files_processed: int
    embeddings_created: int
    errors: List[str]
    execution_time: float

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

@router.post("/query", response_model=QueryResponse)
async def query_ai_rag(request: QueryRequest):
    """Process a query using the RAG system"""
    try:
        rag_manager = get_rag_manager()
        
        # Use new RAG system
        logger.info(f"🔍 Processing query: {request.query[:50]}...")
        
        result = rag_manager.process_query(
            query=request.query,
            technique_id=request.technique_id if not request.enable_auto_selection else None,
            project_id=request.project_id,
            search_limit=request.search_limit,
            llm_model=request.llm_model
        )
        
        # Check for errors
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/techniques/compare", response_model=TechniqueComparisonResponse)
async def compare_techniques(request: TechniqueComparisonRequest):
    """Compare multiple RAG techniques on the same query"""
    try:
        rag_manager = get_rag_manager()
        
        # Compare techniques
        comparison = rag_manager.compare_techniques(
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
        rag_manager = get_rag_manager()
        
        # Get recommendations
        recommendations = rag_manager.get_technique_recommendations(request.query)
        
        return TechniqueRecommendationResponse(recommendations=recommendations)
        
    except Exception as e:
        logger.error(f"Error getting technique recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/techniques", response_model=List[Dict[str, Any]])
async def get_available_techniques():
    """Get list of available RAG techniques"""
    try:
        rag_manager = get_rag_manager()
        
        # Get available techniques
        techniques = rag_manager.get_available_techniques()
        
        return techniques
        
    except Exception as e:
        logger.error(f"Error getting available techniques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get overall system status"""
    try:
        if RAGManager is None:
            return SystemStatusResponse(
                vector_db_connected=False,
                available_techniques=0,
                technique_names=[],
                config_loaded=False,
                timestamp=datetime.now().isoformat()
            )
        
        rag_manager = get_rag_manager()
        
        # Get system status
        status = rag_manager.get_system_status()
        
        return SystemStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/embeddings", response_model=ProjectEmbeddingResponse)
async def process_project_embeddings(project_id: str, background_tasks: BackgroundTasks):
    """Process vector embeddings for a specific project"""
    try:
        rag_manager = get_rag_manager()
        
        # Process embeddings
        result = rag_manager.process_project_embeddings(project_id)
        
        # Add execution time if not present
        if 'execution_time' not in result:
            result['execution_time'] = 0.0
        
        return ProjectEmbeddingResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing project embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_similar_documents(
    query: str, 
    project_id: Optional[str] = None, 
    limit: int = 10
):
    """Search for similar documents using vector similarity"""
    try:
        rag_manager = get_rag_manager()
        
        # Search for similar documents
        results = rag_manager.search_similar_documents(
            query=query,
            limit=limit,
            project_id=project_id
        )
        
        return {
            "query": query,
            "project_id": project_id,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects")
async def get_projects():
    """Get list of available projects"""
    try:
        # Get projects from project manager
        if ProjectManager:
            project_manager = ProjectManager()
            projects = project_manager.list_projects()
        else:
            projects = []
        
        return {
            "projects": projects,
            "count": len(projects),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
async def get_project_files(project_id: str):
    """Get files for a specific project"""
    try:
        # Get project files
        if ProjectManager:
            project_manager = ProjectManager()
            files = project_manager.list_project_files(project_id)
        else:
            files = []
        
        return {
            "project_id": project_id,
            "files": files,
            "count": len(files),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-db-info")
async def get_vector_db_info():
    """Get vector database information"""
    try:
        rag_manager = get_rag_manager()
        
        # Get vector database info
        if rag_manager.vector_uploader and rag_manager.vector_uploader.vector_db:
            db_info = rag_manager.vector_uploader.vector_db.get_collection_info()
            return {
                "status": "connected",
                "collection_info": db_info,
                "collection_name": rag_manager.vector_uploader.vector_db.collection_name
            }
        else:
            return {
                "status": "not_connected",
                "collection_info": None,
                "collection_name": None
            }
        
    except Exception as e:
        logger.error(f"Error getting vector DB info: {e}")
        return {
            "status": "error",
            "error": str(e),
            "collection_info": None,
            "collection_name": None
        }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if RAGManager is None:
            return {
                "status": "unavailable",
                "message": "AI/RAG system not available",
                "timestamp": datetime.now().isoformat()
            }
        
        rag_manager = get_rag_manager()
        
        # Get health status
        health = rag_manager.get_system_status()
        
        return {
            "status": "healthy" if health.get('vector_db_connected') else "degraded",
            "message": "AI/RAG system is operational",
            "details": health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.post("/demo")
async def run_demo_queries():
    """Run demo queries to showcase the system"""
    try:
        rag_manager = get_rag_manager()
        
        # Demo queries
        demo_queries = [
            "What are the motor specifications?",
            "Explain the system architecture",
            "What are the key components?",
            "How does the control system work?"
        ]
        
        results = []
        successful_queries = 0
        
        for query in demo_queries:
            try:
                result = rag_manager.process_query(
                    query=query,
                    search_limit=5
                )
                
                if 'error' not in result:
                    successful_queries += 1
                
                results.append({
                    "query": query,
                    "result": result,
                    "success": 'error' not in result
                })
                
            except Exception as e:
                results.append({
                    "query": query,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "queries": results,
            "total_queries": len(demo_queries),
            "successful_queries": successful_queries
        }
        
    except Exception as e:
        logger.error(f"Error running demo queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-vector-data")
async def clear_vector_data(request: Request):
    """Clear vector database data"""
    try:
        rag_manager = get_rag_manager()
        
        # Clear vector database
        if rag_manager.vector_uploader and rag_manager.vector_uploader.vector_db:
            # Delete collection and recreate
            collection_name = rag_manager.vector_uploader.vector_db.collection_name
            rag_manager.vector_uploader.vector_db.delete_collection(collection_name)
            rag_manager.vector_uploader.vector_db.create_collection(collection_name)
            
            return {
                "status": "success",
                "message": f"Vector data cleared for collection: {collection_name}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Vector database not available")
        
    except Exception as e:
        logger.error(f"Error clearing vector data: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 