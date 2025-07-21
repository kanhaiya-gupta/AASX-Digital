# RAG Techniques Module

This document describes the modular RAG (Retrieval-Augmented Generation) techniques implemented in the AASX Digital Twin Analytics Framework.

## Overview

The RAG techniques module provides a flexible, extensible framework for different approaches to retrieval-augmented generation. Each technique is implemented as a separate module with a common interface, allowing for easy comparison, testing, and extension.

## Architecture

### Base Class: `BaseRAGTechnique`

All RAG techniques inherit from the `BaseRAGTechnique` abstract base class, which defines the common interface:

- `retrieve_context()`: Retrieve relevant context for a query
- `combine_contexts()`: Combine different types of context
- `generate_response()`: Generate AI response using combined context
- `validate_parameters()`: Validate technique-specific parameters
- `preprocess_query()`: Preprocess query if needed
- `postprocess_response()`: Postprocess response if needed

### Technique Manager: `RAGTechniqueManager`

The `RAGTechniqueManager` coordinates all available techniques and provides:

- Technique initialization and management
- Technique execution with parameter validation
- Technique comparison and evaluation
- Technique recommendations based on query characteristics
- Statistics and information about available techniques

## Available Techniques

### 1. Basic RAG (`BasicRAGTechnique`)

**Description**: Simple retrieval + generation approach using vector search and LLM

**Features**:
- Standard vector similarity search
- Simple context combination
- Basic prompt engineering
- Minimal configuration required

**Best For**:
- Simple queries
- Quick responses
- Baseline performance comparison

### 2. Hybrid RAG (`HybridRAGTechnique`)

**Description**: Dense + sparse retrieval approach using vector search and keyword matching

**Features**:
- Combines dense vector search with sparse keyword search
- Weighted scoring of results
- Deduplication of results
- Enhanced relevance through multiple retrieval methods

**Best For**:
- Queries with specific keywords
- Mixed semantic and exact matching needs
- Improved recall over basic RAG

### 3. Multi-Step RAG (`MultiStepRAGTechnique`)

**Description**: Iterative refinement approach with multiple retrieval and generation steps

**Features**:
- Multi-step query refinement
- Iterative context retrieval
- Query evolution based on intermediate results
- Step-by-step analysis

**Best For**:
- Complex queries requiring deep analysis
- Queries that benefit from iterative refinement
- Research-style questions

### 4. Graph RAG (`GraphRAGTechnique`)

**Description**: Knowledge graph integration approach using graph queries and relationships

**Features**:
- Graph-based context retrieval
- Relationship-aware search
- Structural insights from knowledge graph
- Enhanced understanding of entity connections

**Best For**:
- Queries about relationships and connections
- Structural analysis questions
- Entity relationship exploration

### 5. Advanced RAG (`AdvancedRAGTechnique`)

**Description**: Multi-modal + reasoning approach with advanced context processing

**Features**:
- Multi-modal context combination
- Advanced filtering and reranking
- Sophisticated reasoning capabilities
- Metadata analysis and insights

**Best For**:
- Complex, multi-faceted queries
- Comprehensive analysis requirements
- Advanced reasoning tasks

## Usage

### Basic Usage

```python
from src.ai_rag.ai_rag import get_rag_system

# Get RAG system
rag_system = get_rag_system()

# Execute a specific technique
result = await rag_system.execute_rag_technique(
    query="What are the quality issues in our manufacturing assets?",
    technique_id="hybrid",
    llm_model="gpt-3.5-turbo",
    top_k=5
)
```

### Technique Comparison

```python
# Compare multiple techniques
comparison = await rag_system.compare_rag_techniques(
    query="Analyze the risk factors in our production system",
    technique_ids=["basic", "hybrid", "graph"],
    llm_model="gpt-4"
)

print(f"Best technique: {comparison['summary']['best_technique']}")
```

### Technique Recommendations

```python
# Get recommendations for a query
recommendations = rag_system.get_technique_recommendations(
    "What are the relationships between our assets and submodels?"
)

for rec in recommendations:
    print(f"{rec['technique_id']}: {rec['reason']} (confidence: {rec['confidence']})")
```

## Configuration

Each technique can be configured through the main configuration file (`src/config/config_enhanced_rag.yaml`):

```yaml
# RAG technique configuration
rag_techniques:
  basic:
    temperature: 0.7
    max_tokens: 1000
    system_prompt: "You are an AI assistant analyzing digital twin data..."
  
  hybrid:
    dense_weight: 0.7
    sparse_weight: 0.3
    temperature: 0.7
  
  multi_step:
    max_steps: 3
    temperature: 0.7
  
  graph:
    enable_relationships: true
    max_graph_results: 10
  
  advanced:
    enable_metadata_analysis: true
    enable_reranking: true
    temperature: 0.7
```

## API Endpoints

The web interface provides several endpoints for RAG technique management:

- `GET /api/ai-rag/techniques` - Get available techniques
- `POST /api/ai-rag/techniques/recommendations` - Get technique recommendations
- `POST /api/ai-rag/techniques/execute` - Execute specific technique
- `POST /api/ai-rag/techniques/compare` - Compare multiple techniques

## Extending the Framework

### Adding a New Technique

1. Create a new technique class inheriting from `BaseRAGTechnique`:

```python
from .base_technique import BaseRAGTechnique

class CustomRAGTechnique(BaseRAGTechnique):
    def __init__(self, config):
        super().__init__(
            name="Custom RAG",
            description="Custom RAG technique description",
            config=config
        )
    
    def retrieve_context(self, query, **kwargs):
        # Implement custom retrieval logic
        pass
    
    def combine_contexts(self, vector_docs, graph_context, **kwargs):
        # Implement custom context combination
        pass
    
    def generate_response(self, query, context, llm_model, **kwargs):
        # Implement custom response generation
        pass
```

2. Add the technique to the technique manager:

```python
# In rag_technique_manager.py
from .custom_rag import CustomRAGTechnique

def _initialize_techniques(self):
    # ... existing techniques ...
    self.techniques['custom'] = CustomRAGTechnique(self.config)
```

3. Update the `__init__.py` file:

```python
# In rag_techniques/__init__.py
from .custom_rag import CustomRAGTechnique

__all__ = [
    # ... existing techniques ...
    'CustomRAGTechnique'
]
```

## Testing

Run the test script to verify all techniques are working:

```bash
python test_rag_techniques.py
```

This will test each technique with a sample query and report the results.

## Performance Considerations

- **Basic RAG**: Fastest, lowest resource usage
- **Hybrid RAG**: Moderate performance, better results
- **Multi-Step RAG**: Slower, more thorough analysis
- **Graph RAG**: Depends on graph size and complexity
- **Advanced RAG**: Most resource-intensive, most comprehensive

## Best Practices

1. **Start with Basic RAG** for simple queries
2. **Use Hybrid RAG** when you need better recall
3. **Apply Multi-Step RAG** for complex analysis
4. **Leverage Graph RAG** for relationship queries
5. **Reserve Advanced RAG** for comprehensive analysis

6. **Compare techniques** to find the best approach for your use case
7. **Monitor performance** and adjust parameters accordingly
8. **Use technique recommendations** to guide technique selection

## Troubleshooting

### Common Issues

1. **Technique not found**: Ensure the technique is properly registered in the technique manager
2. **Parameter validation errors**: Check that all required parameters are provided
3. **Graph context failures**: Verify Neo4j connection and data availability
4. **Vector search errors**: Check Qdrant connection and collection existence

### Debug Mode

Enable debug logging to see detailed information about technique execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Planned improvements to the RAG techniques framework:

1. **Automatic technique selection** based on query analysis
2. **Performance benchmarking** and optimization
3. **Custom technique composition** from existing techniques
4. **Real-time technique adaptation** based on user feedback
5. **Integration with external RAG frameworks** (LangChain, LlamaIndex) 