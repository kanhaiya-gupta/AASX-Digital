# AI/RAG Routes Modularization

## Overview
The AI/RAG module has been successfully modularized following the AASX pattern, separating business logic from route definitions for better maintainability and testability. **The module now properly uses the central data management system from `src/shared/`** instead of creating its own data management layer.

## Modular Structure

### 1. **`routes.py`** (11KB, 363 lines)
**Purpose**: FastAPI route definitions only
- Contains only endpoint definitions and Pydantic models
- Imports and uses service classes for business logic
- Clean separation of concerns
- Easy to test and maintain

**Key Features**:
- Route grouping by functionality (Query, System, Project)
- Service initialization and management
- Error handling at route level
- Pydantic models for request/response validation

### 2. **`query_service.py`** (5.7KB, 158 lines)
**Purpose**: Query processing business logic
- `QueryService` class with RAG manager integration
- Query processing, technique comparison, recommendations
- Demo query execution
- Document similarity search

**Methods**:
- `process_query()` - Main query processing
- `compare_techniques()` - Technique comparison
- `get_technique_recommendations()` - AI recommendations
- `get_available_techniques()` - List available techniques
- `run_demo_queries()` - Demo functionality
- `search_similar_documents()` - Vector similarity search

### 3. **`system_service.py`** (5.2KB, 138 lines)
**Purpose**: System management and health monitoring
- `SystemService` class for system operations
- Health checks, status monitoring
- Vector database management
- Project embedding processing

**Methods**:
- `get_system_status()` - Overall system status
- `get_health_status()` - Health check endpoint
- `get_vector_db_info()` - Vector DB information
- `clear_vector_data()` - Clear vector database
- `process_project_embeddings()` - Process embeddings

### 4. **`project_service.py`** (5.7KB, 160 lines)
**Purpose**: Project and file management using central data system
- `ProjectService` class that integrates with `src/shared/services/project_service.py`
- Uses central database connection and repositories
- Project CRUD operations through shared service layer
- File management within projects
- Project validation and statistics

**Methods**:
- `get_projects()` - List all projects
- `get_project_files()` - Get project files
- `get_project_details()` - Detailed project info
- `create_project()` - Create new project
- `update_project()` - Update existing project
- `delete_project()` - Delete project
- `get_project_statistics()` - Project statistics
- `validate_project()` - Project validation

## Benefits of Modularization

### 1. **Separation of Concerns**
- Routes handle HTTP concerns only
- Services handle business logic
- Clear boundaries between layers

### 2. **Testability**
- Services can be unit tested independently
- Routes can be tested with mocked services
- Easier to write comprehensive tests

### 3. **Maintainability**
- Changes to business logic don't affect routes
- New endpoints can reuse existing services
- Easier to understand and modify

### 4. **Reusability**
- Services can be used by other modules
- Business logic is not tied to HTTP layer
- Consistent patterns across modules

### 5. **Error Handling**
- Centralized error handling in services
- Route-level error transformation
- Better error messages and logging

### 6. **Central Data Management Integration**
- Uses `src/shared/database/` for database connections
- Integrates with `src/shared/services/` for business logic
- Uses `src/shared/repositories/` for data access
- Consistent with AASX module pattern
- Single source of truth for all data operations

## Service Initialization Pattern

```python
def get_services():
    """Get or initialize service instances"""
    global rag_manager, query_service, system_service, project_service
    
    if rag_manager is None:
        # Initialize RAG manager
        rag_manager = RAGManager()
    
    if query_service is None:
        query_service = QueryService(rag_manager)
    
    if system_service is None:
        system_service = SystemService(rag_manager)
    
    if project_service is None:
        # Initialize project service with central data management system
        project_service = ProjectService()
    
    return query_service, system_service, project_service
```

## Route Usage Pattern

```python
@router.post("/query", response_model=QueryResponse)
async def query_ai_rag(request: QueryRequest):
    """Process a query using the RAG system"""
    try:
        query_service, _, _ = get_services()
        
        result = query_service.process_query(
            query=request.query,
            technique_id=request.technique_id,
            project_id=request.project_id,
            search_limit=request.search_limit,
            llm_model=request.llm_model,
            enable_auto_selection=request.enable_auto_selection
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## Comparison with AASX Pattern

| Aspect | AASX Module | AI/RAG Module |
|--------|-------------|---------------|
| **Routes** | `routes.py` | `routes.py` |
| **Business Logic** | `use_cases.py`, `projects.py`, `files.py`, `processor.py` | `query_service.py`, `system_service.py`, `project_service.py` |
| **Service Pattern** | Service classes with database integration | Service classes with RAG manager integration |
| **Error Handling** | Centralized in services | Centralized in services |
| **Initialization** | Service instances in routes | Service instances in routes |
| **Data Management** | Uses `src/shared/` central system | Uses `src/shared/` central system |

## Next Steps

1. **Testing**: Write unit tests for each service
2. **Documentation**: Add detailed API documentation
3. **Validation**: Add input validation in services
4. **Caching**: Implement caching for frequently accessed data
5. **Monitoring**: Add metrics and monitoring to services

## Files Summary

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| `routes.py` | 11KB | 363 | FastAPI route definitions |
| `query_service.py` | 5.7KB | 158 | Query processing logic |
| `system_service.py` | 5.2KB | 138 | System management logic |
| `project_service.py` | 5.7KB | 160 | Project management logic |
| **Total** | **27.6KB** | **819** | **Modular AI/RAG system** |

The modularization reduces the original monolithic `routes.py` (15KB, 459 lines) into a clean, maintainable structure that follows established patterns and best practices. 