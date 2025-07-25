"""
AI/RAG System API Routes
Provides REST API endpoints for the AI/RAG system frontend
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

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from src.ai_rag.ai_rag import get_rag_system, EnhancedRAGSystem
from src.kg_neo4j.neo4j_manager import Neo4jManager
from src.kg_neo4j.cypher_queries import CypherQueries

# Import centralized file management system
from src.shared.management import ProjectManager, FileManagementError

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize centralized project manager
project_manager = ProjectManager()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    analysis_type: str = "general"
    collection: str = "aasx_assets"
    llm_model: str = "gpt-3.5-turbo"
    rag_technique: str = "basic"
    top_k: int = 5
    similarity_threshold: float = 0.7
    enable_reranking: bool = False
    enable_graph_context: bool = True
    enable_metadata_filtering: bool = False

class QueryResponse(BaseModel):
    analysis: str
    context: List[str] = []
    sources: List[str] = []
    confidence: Optional[float] = None
    query: str
    analysis_type: str
    rag_technique: str = "basic"
    technique_name: Optional[str] = None
    model: Optional[str] = None

class DemoResponse(BaseModel):
    queries: List[Dict[str, Any]]
    total_queries: int
    successful_queries: int

class SystemStats(BaseModel):
    collections_count: int
    total_points: int
    assets_count: int
    submodels_count: int
    last_indexed: Optional[str] = None
    neo4j_status: str
    qdrant_status: str
    openai_status: str

class CollectionInfo(BaseModel):
    name: str
    points_count: int
    description: str

# Initialize RAG system
rag_system = None

def get_rag_system_instance():
    """Get or initialize RAG system instance"""
    global rag_system
    if rag_system is None:
        try:
            rag_system = get_rag_system()
            logger.info("RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize RAG system")
    return rag_system

@router.get("/", response_class=HTMLResponse)
async def ai_rag_page(request: Request):
    """AI/RAG system main page"""
    templates = Jinja2Templates(directory="webapp/templates")
    return templates.TemplateResponse(
        "ai_rag/index.html",
        {
            "request": request,
            "title": "AI/RAG System - QI Digital Platform"
        }
    )

@router.post("/query", response_model=QueryResponse)
async def query_ai_rag(request: QueryRequest):
    """
    Submit a query to the AI/RAG system
    
    Args:
        request: Query request with question and analysis type
        
    Returns:
        AI-generated analysis with context and sources
    """
    try:
        rag = get_rag_system_instance()
        
        # Execute RAG technique with enhanced parameters
        logger.info(f"🔍 Executing RAG technique: {request.rag_technique} with query: {request.query}")
        
        response = await rag.execute_rag_technique(
            query=request.query,
            technique_id=request.rag_technique,
            llm_model=request.llm_model,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            enable_reranking=request.enable_reranking,
            enable_graph_context=request.enable_graph_context,
            enable_metadata_filtering=request.enable_metadata_filtering
        )
        
        logger.info(f"✅ RAG technique execution completed. Response keys: {list(response.keys())}")
        
        # Format response from technique execution
        return QueryResponse(
            analysis=response.get('answer', 'No analysis available'),
            context=response.get('context', []),
            sources=response.get('sources', []),
            confidence=response.get('confidence'),
            query=request.query,
            analysis_type=request.analysis_type,
            rag_technique=response.get('technique_name', request.rag_technique),
            technique_name=response.get('technique_name'),
            model=response.get('model')
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.post("/demo", response_model=DemoResponse)
async def run_demo_queries():
    """
    Run a set of predefined demo queries
    
    Returns:
        Results from all demo queries
    """
    demo_queries = [
        {
            "query": "What are the quality issues in our manufacturing assets?",
            "analysis_type": "quality"
        },
        {
            "query": "Assess the risk level of our critical equipment",
            "analysis_type": "risk"
        },
        {
            "query": "How can we optimize our production efficiency?",
            "analysis_type": "optimization"
        },
        {
            "query": "What are the main assets in our digital twin system?",
            "analysis_type": "general"
        }
    ]
    
    try:
        rag = get_rag_system_instance()
        results = []
        successful = 0
        
        for demo_query in demo_queries:
            try:
                response = await rag.generate_rag_response(
                    query=demo_query["query"],
                    analysis_type=demo_query["analysis_type"]
                )
                
                results.append({
                    "query": demo_query["query"],
                    "analysis_type": demo_query["analysis_type"],
                    "response": response,
                    "status": "success"
                })
                successful += 1
                
            except Exception as e:
                logger.error(f"Demo query failed: {e}")
                results.append({
                    "query": demo_query["query"],
                    "analysis_type": demo_query["analysis_type"],
                    "error": str(e),
                    "status": "error"
                })
        
        return DemoResponse(
            queries=results,
            total_queries=len(demo_queries),
            successful_queries=successful
        )
        
    except Exception as e:
        logger.error(f"Demo queries failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo queries failed: {str(e)}")

@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """
    Get system statistics and status
    
    Returns:
        System statistics including collection counts and service status
    """
    try:
        rag = get_rag_system_instance()
        
        # Get RAG system stats
        rag_stats = rag.get_system_stats()
        
        # Check service status
        neo4j_status = "connected" if rag.neo4j_driver else "disconnected"
        qdrant_status = "connected" if rag.qdrant_client else "disconnected"
        openai_status = "connected" if rag.openai_client else "disconnected"
        
        return SystemStats(
            collections_count=rag_stats.get('collections_count', 0),
            total_points=rag_stats.get('total_points', 0),
            assets_count=rag_stats.get('assets_count', 0),
            submodels_count=rag_stats.get('submodels_count', 0),
            last_indexed=rag_stats.get('last_indexed'),
            neo4j_status=neo4j_status,
            qdrant_status=qdrant_status,
            openai_status=openai_status
        )
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")

@router.get("/collections", response_model=List[CollectionInfo])
async def get_collections():
    """
    Get available vector collections
    
    Returns:
        List of available collections with metadata
    """
    try:
        rag = get_rag_system_instance()
        
        collections = []
        collection_names = [
            'aasx_assets',
            'aasx_submodels', 
            'quality_standards',
            'compliance_data',
            'analysis_results'
        ]
        
        for collection_name in collection_names:
            try:
                collection_info = rag.qdrant_client.get_collection(collection_name)
                collections.append(CollectionInfo(
                    name=collection_name,
                    points_count=collection_info.points_count,
                    description=f"{collection_name.replace('_', ' ').title()} collection"
                ))
            except Exception as e:
                logger.warning(f"Failed to get collection {collection_name}: {e}")
                collections.append(CollectionInfo(
                    name=collection_name,
                    points_count=0,
                    description=f"{collection_name.replace('_', ' ').title()} collection (unavailable)"
                ))
        
        return collections
        
    except Exception as e:
        logger.error(f"Failed to get collections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collections: {str(e)}")

@router.post("/index-data")
async def index_etl_data(background_tasks: BackgroundTasks):
    """
    Index ETL pipeline data into vector database
    
    Returns:
        Indexing status and statistics
    """
    try:
        rag = get_rag_system_instance()
        
        # Run indexing in background
        background_tasks.add_task(rag.index_etl_data)
        
        return {
            "message": "Data indexing started in background",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Failed to start indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start indexing: {str(e)}")

@router.get("/search")
async def search_data(query: str, collection: str = "aasx_assets", limit: int = 5):
    """
    Search vector database for similar content
    
    Args:
        query: Search query
        collection: Collection to search in
        limit: Maximum number of results
        
    Returns:
        Search results with similarity scores
    """
    try:
        rag = get_rag_system_instance()
        
        results = await rag.search_aasx_data(
            query=query,
            collection=collection,
            limit=limit
        )
        
        return {
            "query": query,
            "collection": collection,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/graph-context")
async def get_graph_context(query: str):
    """
    Get relevant context from knowledge graph
    
    Args:
        query: Query to find relevant graph context
        
    Returns:
        Relevant graph nodes and relationships
    """
    try:
        rag = get_rag_system_instance()
        
        if not rag.neo4j_driver:
            return {
                "message": "Knowledge graph not available",
                "context": []
            }
        
        context = await rag._get_graph_context(query)
        
        return {
            "query": query,
            "context": context
        }
        
    except Exception as e:
        logger.error(f"Failed to get graph context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get graph context: {str(e)}")

@router.get("/vector-db-info")
async def get_vector_db_info():
    """
    Get vector database information
    
    Returns:
        Vector database information and statistics
    """
    try:
        rag = get_rag_system_instance()
        
        # Get collections info
        collections = rag.get_collections_info()
        
        # Get system stats
        stats = rag.get_system_stats()
        
        return {
            "success": True,
            "collections": collections,
            "total_collections": len(collections),
            "total_points": stats.get('total_points', 0),
            "qdrant_status": stats.get('qdrant_status', 'unknown'),
            "db_type": "Qdrant Vector Database",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get vector DB info: {e}")
        return {
            "success": False,
            "collections": [],
            "total_collections": 0,
            "total_points": 0,
            "qdrant_status": "error",
            "db_type": "Qdrant Vector Database",
            "error": str(e)
        }

@router.get("/health")
async def health_check():
    """
    Health check for AI/RAG system
    
    Returns:
        System health status
    """
    try:
        rag = get_rag_system_instance()
        
        # Check centralized project manager
        try:
            projects = project_manager.list_projects()
            project_manager_status = "connected" if projects is not None else "disconnected"
        except:
            project_manager_status = "disconnected"
        
        health_status = {
            "status": "healthy",
            "qdrant": "connected" if rag.qdrant_client else "disconnected",
            "neo4j": "connected" if rag.neo4j_driver else "disconnected",
            "openai": "connected" if rag.openai_client else "disconnected",
            "embedding_model": "loaded" if hasattr(rag, '_local_model') else "not_loaded",
            "project_manager": project_manager_status
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/projects")
async def get_projects():
    """Get all projects using centralized project manager"""
    try:
        projects = project_manager.list_projects()
        return {
            "success": True,
            "projects": projects,
            "total_count": len(projects)
        }
    except FileManagementError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
async def get_project_files(project_id: str):
    """Get files for a specific project using centralized project manager"""
    try:
        if not project_manager.project_exists(project_id):
            raise HTTPException(status_code=404, detail="Project not found")
        
        files = project_manager.list_project_files(project_id)
        return {
            "success": True,
            "project_id": project_id,
            "files": files,
            "total_count": len(files)
        }
    except FileManagementError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-vector-data")
async def clear_vector_data(request: Request):
    """
    Clear all vector data from the global database
    
    Returns:
        Status of the clearing operation
    """
    try:
        data = await request.json()
        clear_all = data.get('clear_all', False)
        
        if not clear_all:
            raise HTTPException(status_code=400, detail="clear_all must be set to true")
        
        rag = get_rag_system_instance()
        
        # Get statistics before clearing
        collections = rag.qdrant_client.get_collections()
        total_points = 0
        collections_removed = 0
        
        for collection in collections.collections:
            # Get collection info to access points count
            try:
                collection_info = rag.qdrant_client.get_collection(collection.name)
                points_count = collection_info.points_count
                total_points += points_count
            except Exception as e:
                logger.warning(f"Could not get points count for collection {collection.name}: {e}")
                points_count = 0
            collections_removed += 1
        
        # Clear all collections
        for collection in collections.collections:
            try:
                rag.qdrant_client.delete_collection(collection.name)
                logger.info(f"Deleted collection: {collection.name}")
            except Exception as e:
                logger.warning(f"Failed to delete collection {collection.name}: {e}")
        
        # Recreate the main collection
        try:
            rag._setup_collection()
            logger.info("Recreated main collection")
        except Exception as e:
            logger.error(f"Failed to recreate main collection: {e}")
        
        result = {
            'success': True,
            'collections_removed': collections_removed,
            'points_deleted': total_points,
            'storage_freed': f"{total_points * 0.001:.2f} MB",  # Rough estimate
            'timestamp': datetime.now().isoformat(),
            'message': 'All vector data cleared successfully'
        }
        
        logger.info(f"✅ Cleared {collections_removed} collections with {total_points} total points")
        return result
        
    except Exception as e:
        logger.error(f"Failed to clear vector data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear vector data: {str(e)}")

@router.get("/vector-data-stats")
async def get_vector_data_stats():
    """
    Get detailed statistics about vector database data
    
    Returns:
        Statistics about collections and data
    """
    try:
        logger.info("🔍 Getting vector data statistics...")
        
        try:
            rag = get_rag_system_instance()
            logger.info("✅ Got RAG system instance")
        except Exception as e:
            logger.error(f"❌ Failed to get RAG system instance: {e}")
            return {
                'success': False,
                'error': f'Failed to initialize RAG system: {str(e)}'
            }
        
        if not rag.qdrant_client:
            logger.error("❌ Qdrant client not available")
            return {
                'success': False,
                'error': 'Qdrant client not available'
            }
        
        logger.info("✅ Got RAG system instance, fetching collections...")
        
        try:
            collections = rag.qdrant_client.get_collections()
            logger.info(f"✅ Found {len(collections.collections)} collections")
        except Exception as e:
            logger.error(f"❌ Failed to get collections from Qdrant: {e}")
            return {
                'success': False,
                'error': f'Failed to connect to Qdrant: {str(e)}'
            }
        
        total_points = 0
        collection_stats = []
        largest_collection = None
        max_points = 0
        
        for collection in collections.collections:
            logger.info(f"🔍 Processing collection: {collection.name}")
            
            # Get collection info to access points count
            try:
                collection_info = rag.qdrant_client.get_collection(collection.name)
                
                # Get points count from collection info
                points_count = collection_info.points_count
                
                logger.info(f"✅ Collection {collection.name} has {points_count} points")
                
                total_points += points_count
                collection_stats.append({
                    'name': collection.name,
                    'points': points_count,
                    'storage': f"{points_count * 0.001:.2f} MB"
                })
                
                # Track largest collection
                if points_count > max_points:
                    max_points = points_count
                    largest_collection = collection.name
                    
            except Exception as e:
                logger.warning(f"Could not get info for collection {collection.name}: {e}")
                collection_stats.append({
                    'name': collection.name,
                    'points': 0,
                    'storage': 'Unknown'
                })
        
        result = {
            'success': True,
            'total_collections': len(collections.collections),
            'total_points': total_points,
            'total_storage': f"{total_points * 0.001:.2f} MB",
            'largest_collection': largest_collection or 'None',
            'collection_stats': collection_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Successfully generated stats: {result['total_collections']} collections, {result['total_points']} points")
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get vector data stats: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        }

# RAG Technique Management Routes

@router.get("/techniques")
async def get_rag_techniques():
    """
    Get available RAG techniques
    
    Returns:
        List of available RAG techniques with their information
    """
    try:
        rag = get_rag_system_instance()
        techniques = rag.get_available_rag_techniques()
        return {"techniques": techniques}
        
    except Exception as e:
        logger.error(f"Failed to get RAG techniques: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get RAG techniques: {str(e)}")

@router.post("/techniques/recommendations")
async def get_technique_recommendations(request: Request):
    """
    Get RAG technique recommendations for a query
    
    Returns:
        List of technique recommendations with reasoning
    """
    try:
        data = await request.json()
        query = data.get('query', '')
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        rag = get_rag_system_instance()
        recommendations = rag.get_technique_recommendations(query)
        return {"recommendations": recommendations}
        
    except Exception as e:
        logger.error(f"Failed to get technique recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get technique recommendations: {str(e)}")

@router.post("/techniques/execute")
async def execute_rag_technique(request: Request):
    """
    Execute a specific RAG technique
    
    Returns:
        Response from the RAG technique
    """
    try:
        data = await request.json()
        query = data.get('query', '')
        technique_id = data.get('technique_id', 'basic')
        llm_model = data.get('llm_model', 'gpt-3.5-turbo')
        
        # Advanced parameters
        top_k = data.get('top_k', 5)
        similarity_threshold = data.get('similarity_threshold', 0.7)
        enable_reranking = data.get('enable_reranking', False)
        enable_graph_context = data.get('enable_graph_context', True)
        enable_metadata_filtering = data.get('enable_metadata_filtering', False)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        rag = get_rag_system_instance()
        
        # Execute technique
        response = await rag.execute_rag_technique(
            query=query,
            technique_id=technique_id,
            llm_model=llm_model,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            enable_reranking=enable_reranking,
            enable_graph_context=enable_graph_context,
            enable_metadata_filtering=enable_metadata_filtering
        )
        
        return response
        
    except Exception as e:
        logger.error(f"RAG technique execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG technique execution failed: {str(e)}")

@router.post("/techniques/compare")
async def compare_rag_techniques(request: Request):
    """
    Compare multiple RAG techniques
    
    Returns:
        Comparison results
    """
    try:
        data = await request.json()
        query = data.get('query', '')
        technique_ids = data.get('technique_ids', None)  # None means compare all
        llm_model = data.get('llm_model', 'gpt-3.5-turbo')
        
        # Advanced parameters
        top_k = data.get('top_k', 5)
        similarity_threshold = data.get('similarity_threshold', 0.7)
        enable_reranking = data.get('enable_reranking', False)
        enable_graph_context = data.get('enable_graph_context', True)
        enable_metadata_filtering = data.get('enable_metadata_filtering', False)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        rag = get_rag_system_instance()
        
        # Compare techniques
        comparison = await rag.compare_rag_techniques(
            query=query,
            technique_ids=technique_ids,
            llm_model=llm_model,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            enable_reranking=enable_reranking,
            enable_graph_context=enable_graph_context,
            enable_metadata_filtering=enable_metadata_filtering
        )
        
        return comparison
        
    except Exception as e:
        logger.error(f"RAG technique comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG technique comparison failed: {str(e)}") 