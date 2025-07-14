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

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from src.ai_rag.ai_rag import get_rag_system, EnhancedRAGSystem
from src.kg_neo4j.neo4j_manager import Neo4jManager
from src.kg_neo4j.cypher_queries import CypherQueries

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    analysis_type: str = "general"
    collection: str = "aasx_assets"

class QueryResponse(BaseModel):
    analysis: str
    context: List[str] = []
    sources: List[str] = []
    confidence: Optional[float] = None
    query: str
    analysis_type: str

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
        
        # Generate RAG response
        response = await rag.generate_rag_response(
            query=request.query,
            analysis_type=request.analysis_type
        )
        
        # Format response
        return QueryResponse(
            analysis=response.get('analysis', 'No analysis available'),
            context=response.get('context', []),
            sources=response.get('sources', []),
            confidence=response.get('confidence'),
            query=request.query,
            analysis_type=request.analysis_type
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
        rag_stats = await rag.get_system_stats()
        
        # Check service status
        neo4j_status = "connected" if rag.neo4j_manager else "disconnected"
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
        
        if not rag.neo4j_manager:
            return {
                "message": "Knowledge graph not available",
                "context": []
            }
        
        context = await rag.get_graph_context(query)
        
        return {
            "query": query,
            "context": context
        }
        
    except Exception as e:
        logger.error(f"Failed to get graph context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get graph context: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check for AI/RAG system
    
    Returns:
        System health status
    """
    try:
        rag = get_rag_system_instance()
        
        health_status = {
            "status": "healthy",
            "qdrant": "connected" if rag.qdrant_client else "disconnected",
            "neo4j": "connected" if rag.neo4j_manager else "disconnected",
            "openai": "connected" if rag.openai_client else "disconnected",
            "embedding_model": "loaded" if rag.embedding_model else "not_loaded"
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 