# Frontend-Backend Integration Guide

This document describes the complete integration between the frontend webapp and backend services for the QI Digital Platform.

## 🏗️ Architecture Overview

The integrated system consists of:

- **Frontend**: FastAPI webapp with Jinja2 templates and JavaScript
- **Backend Services**: AI/RAG system, Knowledge Graph, ETL pipeline
- **Databases**: Neo4j (graph), Qdrant (vector), SQLite (metadata)
- **APIs**: RESTful endpoints for all services

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Databases     │
│   (FastAPI)     │◄──►│   Services      │◄──►│   (Neo4j/Qdrant)│
│                 │    │                 │    │                 │
│ • Web Interface │    │ • AI/RAG System │    │ • Graph Data    │
│ • API Client    │    │ • Knowledge Graph│   │ • Vector Data   │
│ • Templates     │    │ • ETL Pipeline  │    │ • Metadata      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Integrated Webapp

```bash
# Start the complete system
python run_integrated_webapp.py

# Or with custom options
python run_integrated_webapp.py --port 8000 --host 0.0.0.0
```

### 2. Access the Application

- **Main Application**: http://localhost:8000/
- **AI/RAG System**: http://localhost:8000/ai-rag
- **Knowledge Graph**: http://localhost:8000/kg-neo4j
- **API Documentation**: http://localhost:8000/docs

## 📁 File Structure

```
webapp/
├── app.py                 # Main FastAPI application
├── routes.py              # Additional routes
├── static/
│   ├── css/              # Stylesheets
│   ├── js/
│   │   ├── api.js        # API client for frontend-backend communication
│   │   ├── main.js       # Main JavaScript functionality
│   │   └── twin.js       # Twin registry functionality
│   └── images/           # Static images
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── ai_rag/
│   │   └── index.html    # AI/RAG interface
│   └── kg_neo4j/
│       └── index.html    # Knowledge Graph interface
└── [module]/
    └── routes.py         # Module-specific API routes

backend/
├── ai_rag/
│   └── ai_rag.py         # AI/RAG system backend
├── kg_neo4j/
│   ├── neo4j_manager.py  # Neo4j connection manager
│   ├── cypher_queries.py # Cypher query utilities
│   └── graph_analyzer.py # Graph analysis tools
└── [other modules]/

test/
└── integration/
    └── test_frontend_backend_integration.py  # Integration tests
```

## 🔌 API Integration

### Frontend API Client (`webapp/static/js/api.js`)

The frontend uses a comprehensive API client that handles all communication with backend services:

```javascript
// Initialize API client
const apiClient = new APIClient();

// AI/RAG queries
const response = await apiClient.queryAIRAG("What are the quality issues?", "quality");

// Knowledge Graph queries
const results = await apiClient.queryKG("MATCH (n:Asset) RETURN n LIMIT 10");

// System status
const status = await apiClient.checkAllServices();
```

### Available API Endpoints

#### AI/RAG System (`/ai-rag`)
- `POST /ai-rag/query` - Submit AI analysis queries
- `POST /ai-rag/demo` - Run demo queries
- `GET /ai-rag/stats` - Get system statistics
- `GET /ai-rag/collections` - Get vector collections
- `POST /ai-rag/index-data` - Index ETL data

#### Knowledge Graph (`/kg-neo4j`)
- `POST /kg-neo4j/query` - Execute Cypher queries
- `GET /kg-neo4j/stats` - Get graph statistics
- `GET /kg-neo4j/status` - Get system status
- `POST /kg-neo4j/load-data` - Load graph data
- `GET /kg-neo4j/analysis` - Run graph analysis

#### System
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🎨 Frontend Components

### 1. AI/RAG Interface (`/ai-rag`)

Features:
- **Query Interface**: Natural language queries with analysis type selection
- **Demo Queries**: Pre-built examples for different analysis types
- **System Status**: Real-time status of AI/RAG components
- **Results Display**: Formatted AI responses with context and sources
- **Statistics**: Collection counts and system metrics

```html
<!-- Query Interface -->
<div class="query-section">
    <textarea id="query-input" placeholder="Ask about asset quality, risk assessment..."></textarea>
    <button id="submit-query">Get AI Analysis</button>
</div>

<!-- Demo Queries -->
<div class="demo-queries">
    <button data-query="What are the quality issues in our manufacturing assets?">
        Quality Issues
    </button>
    <button data-query="Assess the risk level of our critical equipment">
        Risk Assessment
    </button>
</div>
```

### 2. Knowledge Graph Interface (`/kg-neo4j`)

Features:
- **Cypher Query Editor**: Interactive query interface
- **Demo Queries**: Common graph queries
- **Results Table**: Formatted query results
- **Graph Statistics**: Node and relationship counts
- **System Status**: Neo4j connection and GDS availability
- **Data Loading**: Load ETL data into graph

```html
<!-- Cypher Query Interface -->
<div class="query-section">
    <textarea id="cypher-query" placeholder="MATCH (n) RETURN n LIMIT 10"></textarea>
    <button id="execute-query">Execute Query</button>
</div>

<!-- Demo Queries -->
<div class="demo-queries">
    <button data-query="MATCH (n:Asset) RETURN n LIMIT 10">Assets Only</button>
    <button data-query="MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10">Relationships</button>
</div>
```

## 🔧 Backend Integration

### 1. AI/RAG System Integration

The AI/RAG system integrates:
- **Vector Database**: Qdrant for semantic search
- **Knowledge Graph**: Neo4j for graph context
- **AI Models**: OpenAI GPT for analysis
- **ETL Data**: Processed AASX data

```python
# Backend AI/RAG routes
@router.post("/query", response_model=QueryResponse)
async def query_ai_rag(request: QueryRequest):
    rag = get_rag_system_instance()
    response = await rag.generate_rag_response(
        query=request.query,
        analysis_type=request.analysis_type
    )
    return QueryResponse(**response)
```

### 2. Knowledge Graph Integration

The Knowledge Graph integrates:
- **Neo4j Database**: Graph storage and queries
- **Graph Analysis**: Community detection, centrality
- **ETL Integration**: Load processed data
- **Cypher Queries**: Interactive query execution

```python
# Backend Knowledge Graph routes
@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    neo4j_mgr, cypher, analyzer = get_neo4j_manager()
    results = neo4j_mgr.execute_query(request.query)
    return QueryResponse(query=request.query, results=results)
```

## 🧪 Testing Integration

### Run Integration Tests

```bash
# Run comprehensive integration tests
python test/integration/test_frontend_backend_integration.py

# Test with custom URL
python test/integration/test_frontend_backend_integration.py --url http://localhost:8000

# Save test results
python test/integration/test_frontend_backend_integration.py --output test_results.json
```

### Test Coverage

The integration tests cover:
- ✅ Webapp health and accessibility
- ✅ Backend service connectivity
- ✅ AI/RAG API functionality
- ✅ Knowledge Graph API functionality
- ✅ Frontend page accessibility
- ✅ API documentation
- ✅ Complete data flow

## 🔄 Data Flow

### 1. AI/RAG Query Flow

```
User Query → Frontend → API Client → AI/RAG Backend → Vector Search → Graph Context → AI Analysis → Response
```

1. User submits query through frontend
2. API client sends request to AI/RAG backend
3. Backend searches vector database for relevant content
4. Backend retrieves graph context from Neo4j
5. AI model generates analysis using retrieved context
6. Response returned to frontend for display

### 2. Knowledge Graph Query Flow

```
Cypher Query → Frontend → API Client → Knowledge Graph Backend → Neo4j → Results → Formatted Display
```

1. User enters Cypher query in frontend
2. API client sends query to Knowledge Graph backend
3. Backend executes query against Neo4j
4. Results formatted and returned to frontend
5. Frontend displays results in table format

## 🛠️ Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional (with defaults)
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
QDRANT_URL=http://localhost:6333
```

### Webapp Configuration

The webapp can be configured via:
- Environment variables
- Configuration files
- Command-line arguments

```python
# Example configuration
app = FastAPI(
    title="QI Digital Platform",
    description="Integrated frontend-backend platform",
    version="1.0.0"
)
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f manifests/framework/docker-compose.framework.yml up -d

# Or run individual components
docker-compose -f manifests/independent/docker-compose.ai-rag.yml up -d
docker-compose -f manifests/independent/docker-compose.knowledge-graph.yml up -d
```

### Local Development

```bash
# Start backend services
python run_etl_docker.sh
python run_ai_rag_docker.sh
python run_knowledge_graph_docker.sh

# Start integrated webapp
python run_integrated_webapp.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Frontend can't connect to backend**
   - Check if backend services are running
   - Verify API endpoints are accessible
   - Check CORS configuration

2. **AI/RAG queries failing**
   - Verify OpenAI API key is set
   - Check Qdrant connection
   - Ensure ETL data is indexed

3. **Knowledge Graph queries failing**
   - Check Neo4j connection
   - Verify graph data is loaded
   - Check Cypher query syntax

4. **Integration tests failing**
   - Ensure all services are running
   - Check environment variables
   - Verify network connectivity

### Debug Mode

```bash
# Enable verbose logging
python run_integrated_webapp.py --verbose

# Check dependencies only
python run_integrated_webapp.py --check-only
```

## 📈 Performance Optimization

### Frontend Optimization

- **API Caching**: Cache frequently accessed data
- **Lazy Loading**: Load components on demand
- **Minification**: Compress JavaScript and CSS
- **CDN**: Use CDN for external libraries

### Backend Optimization

- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Optimize Cypher queries
- **Caching**: Cache AI responses and graph data
- **Async Processing**: Use background tasks for heavy operations

## 🔐 Security Considerations

- **API Authentication**: Implement proper authentication
- **Input Validation**: Validate all user inputs
- **CORS Configuration**: Configure CORS properly
- **Environment Variables**: Secure sensitive configuration
- **HTTPS**: Use HTTPS in production

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Qdrant Python Client](https://qdrant.tech/documentation/guides/python/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## 🤝 Contributing

To contribute to the frontend-backend integration:

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure backward compatibility
5. Follow security best practices

---

For more information, see the main project documentation and API reference. 