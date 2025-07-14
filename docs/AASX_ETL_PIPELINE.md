# AASX ETL Pipeline Documentation

## Overview

The AASX ETL (Extract, Transform, Load) Pipeline is a comprehensive data processing system designed for the Quality Infrastructure Digital Platform. It provides end-to-end processing of Asset Administration Shell (AAS) data from AASX packages, enabling advanced analytics, RAG (Retrieval-Augmented Generation) applications, and quality management workflows.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AASX Files    │───▶│  Extract Phase   │───▶│ Transform Phase │
│   (.aasx)       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Vector DB      │◀───│   Load Phase     │◀───│  Transformed    │
│  (ChromaDB)     │    │                  │    │     Data        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│  RAG System     │    │  SQLite DB       │
│  (Semantic      │    │  (Structured     │
│   Search)       │    │   Storage)       │
└─────────────────┘    └──────────────────┘
```

## Components

### 1. Extract Phase (`aasx_processor.py`)

**Purpose**: Extract data from AASX packages (ZIP-based AAS containers)

**Features**:
- ZIP archive extraction
- JSON and XML parsing
- Asset and submodel extraction
- Document extraction
- Metadata extraction
- Hybrid Python/.NET processing

**Key Classes**:
- `AASXProcessor`: Main processor with fallback mechanisms
- `DotNetBridge`: Bridge to .NET AAS Core libraries

### 2. Transform Phase (`aasx_transformer.py`)

**Purpose**: Transform extracted data into standardized formats

**Features**:
- Data cleaning and normalization
- Quality checks and validation
- Data enrichment with QI metadata
- Multiple output formats (JSON, XML, CSV, YAML)
- Graph database format (Neo4j compatible)
- Analytics format (flattened for BI tools)
- API-ready format (for web services)

**Key Classes**:
- `AASXTransformer`: Main transformation engine
- `TransformerConfig`: Configuration for transformation options

### 3. Load Phase (`aasx_loader.py`)

**Purpose**: Load transformed data into various storage systems

**Features**:
- File export (JSON, YAML, CSV)
- SQLite database storage
- Vector database integration (ChromaDB, FAISS)
- Embedding generation for RAG
- Semantic search capabilities
- RAG-ready dataset export

**Key Classes**:
- `AASXLoader`: Main loader with multiple storage backends
- `LoaderConfig`: Configuration for loading options

### 4. ETL Pipeline (`aasx_etl_pipeline.py`)

**Purpose**: Orchestrate the complete ETL process

**Features**:
- End-to-end pipeline orchestration
- Batch processing capabilities
- Parallel processing support
- Error handling and recovery
- Comprehensive logging and statistics
- Pipeline validation
- Performance monitoring

**Key Classes**:
- `AASXETLPipeline`: Main pipeline orchestrator
- `ETLPipelineConfig`: Complete pipeline configuration

## Installation

### Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt

# Vector database dependencies (optional)
pip install chromadb sentence-transformers

# FAISS for vector search (optional)
pip install faiss-cpu  # or faiss-gpu for GPU support

# .NET 6.0 SDK (for advanced AAS processing)
# Download from: https://dotnet.microsoft.com/download
```

### .NET AAS Processor Setup

```bash
# Navigate to .NET processor directory
cd aas-processor

# Restore NuGet packages
dotnet restore

# Build the project
dotnet build

# Test the processor
dotnet run --project AasProcessor
```

## Usage

### Basic Usage

```python
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline, ETLPipelineConfig

# Create pipeline configuration
config = ETLPipelineConfig(
    enable_validation=True,
    enable_logging=True,
    parallel_processing=False
)

# Create pipeline
pipeline = AASXETLPipeline(config)

# Process single file
result = pipeline.process_aasx_file("path/to/file.aasx")

# Process directory
batch_result = pipeline.process_aasx_directory("path/to/aasx/files")
```

### Advanced Configuration

```python
from webapp.aasx.aasx_etl_pipeline import ETLPipelineConfig
from webapp.aasx.aasx_transformer import TransformerConfig
from webapp.aasx.aasx_loader import LoaderConfig

# Configure transformation
transform_config = TransformerConfig(
    enable_quality_checks=True,
    enable_enrichment=True,
    output_formats=['json', 'csv', 'graph'],
    include_metadata=True
)

# Configure loading
load_config = LoaderConfig(
    output_directory="output",
    database_path="aasx_data.db",
    vector_db_path="vector_db",
    vector_db_type="chromadb",
    embedding_model="all-MiniLM-L6-v2"
)

# Create complete pipeline configuration
config = ETLPipelineConfig(
    transform_config=transform_config,
    load_config=load_config,
    parallel_processing=True,
    max_workers=4
)
```

### Batch Processing

```python
# Process multiple files in parallel
config = ETLPipelineConfig(parallel_processing=True, max_workers=4)
pipeline = AASXETLPipeline(config)

# Process entire directory
result = pipeline.process_aasx_directory("aasx_files/")

print(f"Processed: {result['files_processed']}")
print(f"Failed: {result['files_failed']}")
print(f"Total time: {result['total_time']:.2f}s")
```

### Global Vector Database Integration

The ETL pipeline integrates with a **global vector database** that accumulates embeddings from all processed files, enabling cross-file semantic search and AI-powered analysis.

#### 🎯 **Global Vector Database Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Global Vector Database                       │
│                        (Qdrant Server)                         │
│                    http://localhost:6333                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    File-Specific Collections                    │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ aasx_file1_     │  │ aasx_file2_     │  │ aasx_file3_     │  │
│  │ assets          │  │ assets          │  │ assets          │  │
│  │ submodels       │  │ submodels       │  │ submodels       │  │
│  │ documents       │  │ documents       │  │ documents       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### ✅ **Key Features**

1. **Global Accumulation**: All ETL runs add to the same global vector database
2. **File-Specific Collections**: Each file gets its own collections (e.g., `aasx_additive-manufacturing-3d-printer_converted_assets`)
3. **Duplicate Prevention**: Uses `upsert` operations to prevent data accumulation
4. **Cross-File Search**: Search across all processed files simultaneously
5. **Persistent Storage**: Vector database persists across server restarts

#### 🔧 **Configuration**

```python
# Initialize pipeline with global vector database
config = ETLPipelineConfig()
pipeline = AASXETLPipeline(config)

# Process files (automatically adds to global vector database)
pipeline.process_aasx_file("file.aasx")

# Search across ALL processed files
results = pipeline.loader.search_similar(
    query="motor quality control",
    entity_type="asset",
    top_k=5
)

for result in results:
    print(f"ID: {result['id']}")
    print(f"File: {result['metadata']['source_file']}")
    print(f"Similarity: {result['similarity']}")
    print(f"Content: {result['document']}")
```

#### 📊 **Vector Database Status**

```bash
# Check global vector database status
curl http://localhost:6333/collections

# Example response showing accumulated collections:
{
  "collections": [
    {"name": "aasx_additive-manufacturing-3d-printer_converted_assets"},
    {"name": "aasx_additive-manufacturing-3d-printer_converted_submodels"},
    {"name": "aasx_hydrogen-filling-station_converted_assets"},
    {"name": "aasx_hydrogen-filling-station_converted_submodels"},
    {"name": "aasx_smart-grid-substation_converted_assets"},
    {"name": "aasx_smart-grid-substation_converted_submodels"},
    # ... hundreds more collections from previous ETL runs
  ]
}
```

#### 🔄 **Duplicate Handling**

The system prevents data accumulation when re-running ETL on the same files:

- **SQLite Database**: Uses `INSERT OR REPLACE` to update existing records
- **Vector Database**: Uses `upsert` operations to update existing embeddings
- **File Exports**: Overwrites existing files in the same location
- **Collections**: Updates existing file-specific collections

#### 💾 **Local Backup Strategy**

While the global vector database is stored in Qdrant, you can create local backups:

```bash
# 1. Export vector database metadata
curl http://localhost:6333/collections > vector_db_backup.json

# 2. Create backup script
cat > backup_vector_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/vector_db_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Export collections metadata
curl -s http://localhost:6333/collections > $BACKUP_DIR/collections.json

# Export each collection's points (optional - can be large)
for collection in $(curl -s http://localhost:6333/collections | jq -r '.collections[].name'); do
    echo "Backing up collection: $collection"
    curl -s "http://localhost:6333/collections/$collection/points" > $BACKUP_DIR/${collection}_points.json
done

echo "Vector database backup completed: $BACKUP_DIR"
EOF

chmod +x backup_vector_db.sh
./backup_vector_db.sh
```

#### 🚨 **Important Notes**

1. **No Local Vector Database Directory**: The vector database is stored in Qdrant server, not in local files
2. **Global Persistence**: Data persists across ETL runs and server restarts
3. **Collection Growth**: Each file creates new collections, but existing collections are updated
4. **Memory Usage**: Large numbers of collections may impact Qdrant performance
5. **Backup Recommended**: Regular backups of the Qdrant data directory are recommended

### RAG Dataset Creation

```python
# Create RAG-ready dataset
pipeline = AASXETLPipeline()

# Process some files first
pipeline.process_aasx_directory("aasx_files/")

# Export RAG dataset
rag_path = pipeline.create_rag_ready_dataset("rag_dataset.json")
print(f"RAG dataset created: {rag_path}")
```

## Configuration Options

### ETLPipelineConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `extract_config` | dict | `{}` | Extraction phase configuration |
| `transform_config` | TransformerConfig | Default | Transformation configuration |
| `load_config` | LoaderConfig | Default | Loading configuration |
| `enable_validation` | bool | `True` | Enable data validation |
| `enable_logging` | bool | `True` | Enable detailed logging |
| `enable_backup` | bool | `True` | Enable backup of processed files |
| `parallel_processing` | bool | `False` | Enable parallel processing |
| `max_workers` | int | `4` | Maximum parallel workers |

### TransformerConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_quality_checks` | bool | `True` | Enable data quality validation |
| `enable_enrichment` | bool | `True` | Enable data enrichment |
| `output_formats` | list | `['json']` | Output formats to generate |
| `include_metadata` | bool | `True` | Include metadata in output |
| `quality_threshold` | float | `0.8` | Minimum quality score |
| `enrichment_sources` | list | `[]` | External enrichment sources |

### LoaderConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_directory` | str | `"output"` | Output directory for files |
| `database_path` | str | `"aasx_data.db"` | SQLite database path |
| `vector_db_path` | str | `"vector_db"` | Vector database path |
| `vector_db_type` | str | `"chromadb"` | Vector database type |
| `embedding_model` | str | `"all-MiniLM-L6-v2"` | Embedding model name |
| `chunk_size` | int | `512` | Text chunk size for embeddings |
| `overlap_size` | int | `50` | Chunk overlap size |
| `include_metadata` | bool | `True` | Include metadata in vector DB |
| `create_indexes` | bool | `True` | Create database indexes |
| `backup_existing` | bool | `True` | Backup existing databases |

## Output Formats

The ETL pipeline generates **7 comprehensive export formats**, each optimized for specific use cases and ensuring complete data accessibility:

### 1. JSON Format (General Purpose)
```json
{
  "format": "json",
  "version": "1.0",
  "data": {
    "assets": [...],
    "submodels": [...],
    "documents": [...],
    "relationships": [...]
  },
  "quality_metrics": {
    "total_assets": 2,
    "total_submodels": 5,
    "quality_score": 1.0
  },
  "metadata": {
    "transformation_timestamp": "2025-07-09T12:36:45.011634",
    "transformer_version": "1.0.0"
  }
}
```
**Use case**: Web APIs, data exchange, general processing  
**Features**: Complete data with metadata, quality metrics, configuration info

### 2. YAML Format (Human-Readable)
```yaml
format: yaml
version: "1.0"
data:
  assets:
    - id: "asset_001"
      id_short: "Motor_001"
      description: "DC Servo Motor"
      type: "Motor"
      quality_level: "HIGH"
      compliance_status: "COMPLIANT"
```
**Use case**: Configuration files, documentation, human review  
**Features**: Readable format with preserved structure

### 3. CSV Format (Analytics-Ready)
```csv
entity_type,id,id_short,description,type,quality_level,compliance_status
asset,asset_001,Motor_001,DC Servo Motor,Motor,HIGH,COMPLIANT
submodel,submodel_001,TechData_001,Technical Data,TechnicalData,MEDIUM,COMPLIANT
```
**Use case**: Spreadsheet analysis, data visualization, business intelligence  
**Features**: Flattened structure with one row per entity

### 4. Graph Format (Neo4j/Graph Databases)
```json
{
  "format": "graph",
  "version": "1.0",
  "nodes": [
    {
      "id": "asset_001",
      "type": "asset",
      "properties": {
        "id_short": "Motor_001",
        "description": "DC Servo Motor",
        "type": "Motor",
        "quality_level": "HIGH",
        "compliance_status": "COMPLIANT"
      }
    }
  ],
  "edges": [
    {
      "source": "asset_001",
      "target": "submodel_001",
      "type": "asset_has_submodel",
      "properties": {
        "extracted_at": "2025-07-09T12:36:45.020020"
      }
    }
  ],
  "metadata": {
    "created_at": "2025-07-09T12:36:45.020020",
    "total_nodes": 7,
    "total_edges": 1
  }
}
```
**Use case**: Graph databases (Neo4j, ArangoDB), relationship analysis, network visualization  
**Features**: Nodes and edges structure optimized for graph operations

### 5. RAG Format (AI/Retrieval-Augmented Generation)
```json
{
  "version": "1.0",
  "format": "rag_ready",
  "timestamp": "2025-07-11T12:03:34.314886",
  "source_file": "test.aasx",
  "entities": [
    {
      "type": "asset",
      "id": "asset_001",
      "id_short": "Motor1",
      "description": "DC Servo Motor",
      "content": "Asset: Motor1 - DC Servo Motor",
      "metadata": {}
    }
  ]
}
```
**Use case**: AI systems, semantic search, retrieval-augmented generation  
**Features**: Pre-formatted content optimized for AI model consumption

### 6. SQLite Database Format (Relational Storage)
```sql
-- Assets table
CREATE TABLE assets (
    id TEXT PRIMARY KEY,
    id_short TEXT,
    description TEXT,
    type TEXT,
    quality_level TEXT,
    compliance_status TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Submodels table
CREATE TABLE submodels (
    id TEXT PRIMARY KEY,
    id_short TEXT,
    description TEXT,
    type TEXT,
    quality_level TEXT,
    compliance_status TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Use case**: Relational queries, SQL-based analytics, structured data access  
**Features**: Full SQLite database with indexed tables and relationships

### 7. Vector Database Format (Semantic Search)
```json
{
  "format": "vector_database",
  "version": "1.0",
  "vector_db_type": "qdrant",
  "created_at": "2025-07-11T12:03:34.314886",
  "collections": [
    {
      "name": "test_aasx_test_assets",
      "points_count": 3,
      "vector_size": 384,
      "distance": "Cosine",
      "type": "qdrant_collection"
    }
  ],
  "metadata": {
    "embedding_model": "all-MiniLM-L6-v2",
    "chunk_size": 512,
    "overlap_size": 50,
    "collection_prefix": "test_aasx"
  }
}
```
**Use case**: Semantic search, similarity analysis, AI embeddings  
**Features**: Vector embeddings with metadata for advanced search capabilities

## Export Configuration

### Complete Export Setup
```python
from backend.aasx.aasx_loader import LoaderConfig

# Configure all 7 export formats
config = LoaderConfig(
    output_directory="output/test_etl",
    database_path="output/test_etl/test/aasx_data.db",
    vector_db_type="qdrant",
    qdrant_url="http://localhost:6333",
    qdrant_collection_prefix="test_aasx",
    backup_existing=False,  # Disable backup for cleaner output
    export_formats=['json', 'yaml', 'csv', 'graph', 'rag', 'vector_db', 'sqlite']
)
```

### Expected Output Structure
```
output/test_etl/test/
├── aasx_data.csv              # CSV export (analytics)
├── aasx_data.db               # SQLite database (relational)
├── aasx_data.json             # JSON export (general)
├── aasx_data.yaml             # YAML export (human-readable)
├── aasx_data_graph.json       # Graph export (Neo4j compatible)
├── aasx_data_rag.json         # RAG export (AI-ready)
└── aasx_data_vector_db.json   # Vector DB export (semantic search)
```

## Performance Optimization

### Parallel Processing
```python
# Enable parallel processing for large datasets
config = ETLPipelineConfig(
    parallel_processing=True,
    max_workers=8  # Adjust based on CPU cores
)
```

### Vector Database Optimization
```python
# Use GPU-accelerated FAISS for large vector databases
load_config = LoaderConfig(
    vector_db_type="faiss",
    embedding_model="all-mpnet-base-v2"  # Better quality embeddings
)
```

### Memory Management
```python
# Process files in batches for large datasets
files = list(Path("aasx_files/").glob("*.aasx"))
batch_size = 100

for i in range(0, len(files), batch_size):
    batch = files[i:i+batch_size]
    result = process_aasx_batch(batch, config)
    print(f"Processed batch {i//batch_size + 1}")
```

## Error Handling

### Common Errors and Solutions

1. **AASX File Format Error**
   ```python
   # Use hybrid processing with .NET fallback
   processor = AASXProcessor()
   result = processor.process_aasx_file("file.aasx")
   ```

2. **Vector Database Connection Error**
   ```python
   # Check ChromaDB installation
   pip install chromadb
   # Or use FAISS instead
   load_config = LoaderConfig(vector_db_type="faiss")
   ```

3. **Memory Issues with Large Files**
   ```python
   # Process in smaller chunks
   config = ETLPipelineConfig(
       transform_config=TransformerConfig(chunk_size=256)
   )
   ```

### Logging and Monitoring

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

# Get pipeline statistics
stats = pipeline.get_pipeline_stats()
print(f"Files processed: {stats['files_processed']}")
print(f"Processing time: {stats['total_processing_time']:.2f}s")
```

## Integration with QI Platform

### Web Application Integration
```python
# In FastAPI route
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline

@app.post("/api/aasx/process")
async def process_aasx_file(file: UploadFile):
    pipeline = AASXETLPipeline()
    result = pipeline.process_aasx_file(file.filename)
    return result
```

### AI/RAG System Integration
```python
# Create RAG dataset for AI system
pipeline = AASXETLPipeline()
pipeline.process_aasx_directory("aasx_files/")
rag_dataset = pipeline.create_rag_ready_dataset("ai_rag_dataset.json")

# Use in RAG system
from webapp.ai_rag.rag_system import RAGSystem
rag = RAGSystem(rag_dataset)
results = rag.query("quality control requirements")
```

### Analytics Dashboard Integration
```python
# Export analytics-ready data
config = ETLPipelineConfig(
    transform_config=TransformerConfig(
        output_formats=['csv', 'analytics']
    )
)
pipeline = AASXETLPipeline(config)
pipeline.process_aasx_file("file.aasx")
```

## Neo4j Graph Database Integration

### Importing Graph Data to Neo4j

The ETL pipeline generates graph-optimized JSON files that can be directly imported into Neo4j:

#### 1. Using Neo4j Cypher Scripts
```cypher
// Load graph data from ETL output
LOAD JSON FROM 'file:///aasx_data_20250709_123645_graph.json' AS graph

// Create nodes
UNWIND graph.nodes AS node
CREATE (n:Node {
    id: node.id,
    type: node.type,
    id_short: node.properties.id_short,
    description: node.properties.description,
    quality_level: node.properties.quality_level,
    compliance_status: node.properties.compliance_status
})

// Create relationships
UNWIND graph.edges AS edge
MATCH (source:Node {id: edge.source})
MATCH (target:Node {id: edge.target})
CREATE (source)-[r:RELATES_TO {
    type: edge.type,
    extracted_at: edge.properties.extracted_at
}]->(target)
```

#### 2. Using Neo4j Import Tool
```bash
# Convert graph JSON to CSV for Neo4j import
python -c "
import json
import csv

# Load graph data
with open('aasx_data_20250709_123645_graph.json', 'r') as f:
    graph_data = json.load(f)

# Export nodes
with open('nodes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id:ID', 'type:LABEL', 'id_short', 'description', 'quality_level', 'compliance_status'])
    for node in graph_data['nodes']:
        writer.writerow([
            node['id'],
            node['type'],
            node['properties']['id_short'],
            node['properties']['description'],
            node['properties']['quality_level'],
            node['properties']['compliance_status']
        ])

# Export relationships
with open('relationships.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([':START_ID', ':END_ID', ':TYPE', 'extracted_at'])
    for edge in graph_data['edges']:
        writer.writerow([
            edge['source'],
            edge['target'],
            edge['type'],
            edge['properties']['extracted_at']
        ])
"

# Import to Neo4j
neo4j-admin import --database=aasx_data --nodes=nodes.csv --relationships=relationships.csv
```

#### 3. Graph Analytics Queries

Once imported, you can run powerful graph analytics:

```cypher
// Find all assets with high quality levels
MATCH (a:Node {type: 'asset', quality_level: 'HIGH'})
RETURN a.id, a.description, a.compliance_status

// Find submodels related to specific assets
MATCH (asset:Node {type: 'asset'})-[r:RELATES_TO]->(submodel:Node {type: 'submodel'})
WHERE asset.id CONTAINS 'motor'
RETURN asset.description, submodel.description, r.type

// Analyze compliance across the network
MATCH (n:Node)
RETURN n.type, n.quality_level, n.compliance_status, count(*) as count
ORDER BY count DESC

// Find connected components
CALL gds.alpha.scc.stream('aasx_graph')
YIELD nodeId, componentId
RETURN componentId, count(*) as size
ORDER BY size DESC
```

#### 4. Python Integration with Neo4j
```python
from neo4j import GraphDatabase
import json

class AASXGraphAnalyzer:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def import_graph_data(self, graph_file_path):
        """Import graph data from ETL output"""
        with open(graph_file_path, 'r') as f:
            graph_data = json.load(f)
        
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create nodes
            for node in graph_data['nodes']:
                session.run("""
                    CREATE (n:Node {
                        id: $id,
                        type: $type,
                        id_short: $id_short,
                        description: $description,
                        quality_level: $quality_level,
                        compliance_status: $compliance_status
                    })
                """, **node['properties'], id=node['id'], type=node['type'])
            
            # Create relationships
            for edge in graph_data['edges']:
                session.run("""
                    MATCH (source:Node {id: $source_id})
                    MATCH (target:Node {id: $target_id})
                    CREATE (source)-[r:RELATES_TO {
                        type: $rel_type,
                        extracted_at: $extracted_at
                    }]->(target)
                """, source_id=edge['source'], target_id=edge['target'],
                     rel_type=edge['type'], extracted_at=edge['properties']['extracted_at'])
    
    def analyze_quality_distribution(self):
        """Analyze quality distribution across assets"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Node {type: 'asset'})
                RETURN n.quality_level, count(*) as count
                ORDER BY count DESC
            """)
            return [record.data() for record in result]
    
    def find_related_submodels(self, asset_id):
        """Find all submodels related to a specific asset"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (asset:Node {id: $asset_id, type: 'asset'})-[r:RELATES_TO]->(submodel:Node {type: 'submodel'})
                RETURN submodel.id, submodel.description, r.type
            """, asset_id=asset_id)
            return [record.data() for record in result]

# Usage
analyzer = AASXGraphAnalyzer("bolt://localhost:7687", "neo4j", "password")
analyzer.import_graph_data("output/etl_results/additive-manufacturing-3d-printer_converted/aasx_data_20250709_123645_graph.json")

# Run analytics
quality_stats = analyzer.analyze_quality_distribution()
print("Quality distribution:", quality_stats)

related_submodels = analyzer.find_related_submodels("http://manufacturing.com/assets/3d_printer_am5000_001")
print("Related submodels:", related_submodels)
```

## Testing

### Run All Tests
```bash
# Run complete test suite
python -m pytest test/aasx/ -v

# Run specific test categories
python -m pytest test/aasx/test_aasx_processor.py -v
python -m pytest test/aasx/test_aasx_transformer.py -v
python -m pytest test/aasx/test_aasx_loader.py -v
python -m pytest test/aasx/test_aasx_etl_pipeline.py -v
```

### Test Individual Components
```python
# Test extraction
from test.aasx.test_aasx_processor import TestAASXProcessor
unittest.main(TestAASXProcessor)

# Test transformation
from test.aasx.test_aasx_transformer import TestAASXTransformer
unittest.main(TestAASXTransformer)

# Test loading
from test.aasx.test_aasx_loader import TestAASXLoader
unittest.main(TestAASXLoader)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure webapp directory is in Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/webapp"
   ```

2. **Vector Database Issues**
   ```bash
   # Reinstall vector database dependencies
   pip uninstall chromadb sentence-transformers
   pip install chromadb sentence-transformers
   ```

3. **.NET Processor Issues**
   ```bash
   # Rebuild .NET processor
   cd aas-processor
   dotnet clean
   dotnet build
   ```

### Performance Issues

1. **Slow Processing**
   - Enable parallel processing
   - Use SSD storage for databases
   - Increase chunk sizes for large files

2. **Memory Issues**
   - Process files in batches
   - Reduce chunk sizes
   - Use streaming processing for large files

3. **Vector Database Performance**
   - Use GPU-accelerated FAISS
   - Optimize embedding model selection
   - Implement vector database indexing

## Future Enhancements

### Planned Features

1. **Advanced Processing**
   - Real-time streaming processing
   - Incremental updates
   - Delta processing for changed files

2. **Enhanced Vector Search**
   - Multi-modal embeddings
   - Hierarchical search
   - Semantic similarity clustering

3. **Quality Management**
   - Automated quality scoring
   - Compliance checking
   - Quality trend analysis

4. **Integration Capabilities**
   - REST API endpoints
   - GraphQL interface
   - WebSocket real-time updates

### Contributing

1. **Code Standards**
   - Follow PEP 8 style guide
   - Add comprehensive tests
   - Update documentation

2. **Testing Requirements**
   - Unit tests for all functions
   - Integration tests for pipeline
   - Performance benchmarks

3. **Documentation**
   - Update README files
   - Add code examples
   - Create user guides

## Support

For issues and questions:

1. **Documentation**: Check this README and inline code documentation
2. **Tests**: Review test files for usage examples
3. **Issues**: Create GitHub issues with detailed error information
4. **Community**: Join the QI Digital Platform community discussions

## License

This ETL pipeline is part of the Quality Infrastructure Digital Platform and follows the same licensing terms as the main project. 