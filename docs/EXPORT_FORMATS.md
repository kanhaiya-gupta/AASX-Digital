# ETL Pipeline Export Formats

## Overview

The AASX Digital Twin Analytics Framework ETL pipeline generates **7 comprehensive export formats**, ensuring complete data accessibility for various use cases and applications. Each format is optimized for specific workflows and provides different levels of data structure and accessibility.

## Export Format Summary

| Format | File Extension | Use Case | Primary Features |
|--------|----------------|----------|------------------|
| **JSON** | `.json` | General purpose, APIs | Complete data with metadata |
| **YAML** | `.yaml` | Configuration, documentation | Human-readable structure |
| **CSV** | `.csv` | Analytics, spreadsheets | Flattened tabular data |
| **Graph** | `_graph.json` | Graph databases, Neo4j | Nodes and edges structure |
| **RAG** | `_rag.json` | AI systems, semantic search | AI-ready content format |
| **SQLite** | `.db` | Relational queries, SQL | Full database with indexes |
| **Vector DB** | `_vector_db.json` | Semantic search, embeddings | Vector metadata and collections |

## Detailed Format Specifications

### 1. JSON Format (General Purpose)

**File**: `aasx_data.json`

**Purpose**: Universal data exchange format for APIs, web services, and general processing.

**Structure**:
```json
{
  "format": "json",
  "version": "1.0",
  "data": {
    "assets": [
      {
        "id": "asset_001",
        "id_short": "Motor1",
        "description": "DC Servo Motor",
        "type": "Motor",
        "quality_level": "high",
        "compliance_status": "compliant",
        "properties": {
          "voltage": "24V",
          "power": "100W",
          "speed": "3000RPM"
        }
      }
    ],
    "submodels": [...],
    "documents": [...],
    "relationships": [...]
  },
  "quality_metrics": {
    "total_assets": 1,
    "total_submodels": 1,
    "quality_score": 1.0
  },
  "metadata": {
    "transformation_timestamp": "2025-07-11T12:03:34.314886",
    "transformer_version": "1.0.0"
  }
}
```

**Use Cases**:
- Web API responses
- Data exchange between systems
- General data processing
- Configuration storage

### 2. YAML Format (Human-Readable)

**File**: `aasx_data.yaml`

**Purpose**: Human-readable format for configuration files, documentation, and manual review.

**Structure**:
```yaml
format: yaml
version: "1.0"
data:
  assets:
    - id: "asset_001"
      id_short: "Motor1"
      description: "DC Servo Motor"
      type: "Motor"
      quality_level: "high"
      compliance_status: "compliant"
      properties:
        voltage: "24V"
        power: "100W"
        speed: "3000RPM"
  submodels: []
  documents: []
  relationships: []
quality_metrics:
  total_assets: 1
  total_submodels: 1
  quality_score: 1.0
metadata:
  transformation_timestamp: "2025-07-11T12:03:34.314886"
  transformer_version: "1.0.0"
```

**Use Cases**:
- Configuration files
- Documentation
- Human review and editing
- Version control friendly

### 3. CSV Format (Analytics-Ready)

**File**: `aasx_data.csv`

**Purpose**: Flattened tabular format for spreadsheet analysis, business intelligence, and data visualization.

**Structure**:
```csv
entity_type,id,id_short,description,type,quality_level,compliance_status
asset,asset_001,Motor1,DC Servo Motor,Motor,high,compliant
submodel,submodel_001,TechnicalData,Technical Data Submodel,TechnicalData,high,compliant
document,doc_001,Manual,User Manual,Manual,,,
```

**Use Cases**:
- Spreadsheet analysis (Excel, Google Sheets)
- Business intelligence tools
- Data visualization platforms
- Statistical analysis

### 4. Graph Format (Neo4j Compatible)

**File**: `aasx_data_graph.json`

**Purpose**: Graph database format optimized for Neo4j and other graph databases, enabling relationship analysis.

**Structure**:
```json
{
  "format": "graph",
  "version": "1.0",
  "nodes": [
    {
      "id": "asset_001",
      "type": "asset",
      "properties": {
        "id_short": "Motor1",
        "description": "DC Servo Motor",
        "type": "Motor",
        "quality_level": "high",
        "compliance_status": "compliant"
      }
    }
  ],
  "edges": [
    {
      "source": "asset_001",
      "target": "submodel_001",
      "type": "asset_has_submodel",
      "properties": {
        "extracted_at": "2025-07-11T12:03:34.314886"
      }
    }
  ],
  "metadata": {
    "created_at": "2025-07-11T12:03:34.314886",
    "total_nodes": 3,
    "total_edges": 1
  }
}
```

**Use Cases**:
- Neo4j graph database import
- Relationship analysis
- Network visualization
- Graph-based analytics

### 5. RAG Format (AI-Ready)

**File**: `aasx_data_rag.json`

**Purpose**: Optimized format for AI systems, retrieval-augmented generation, and semantic search applications.

**Structure**:
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
    },
    {
      "type": "submodel",
      "id": "submodel_001",
      "id_short": "TechnicalData",
      "description": "Technical Data Submodel",
      "content": "Submodel: TechnicalData - Technical Data Submodel",
      "metadata": {}
    }
  ]
}
```

**Use Cases**:
- AI model training
- Retrieval-augmented generation
- Semantic search systems
- Natural language processing

### 6. SQLite Database Format (Relational)

**File**: `aasx_data.db`

**Purpose**: Full relational database with SQL query capabilities, indexes, and structured data access.

**Structure**:
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

-- Documents table
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    filename TEXT,
    size INTEGER,
    type TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relationships table
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    source_id TEXT,
    target_id TEXT,
    type TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Use Cases**:
- SQL-based queries
- Relational analytics
- Structured data access
- Database applications

### 7. Vector Database Format (Semantic Search)

**File**: `aasx_data_vector_db.json`

**Purpose**: Metadata and configuration for vector databases, enabling semantic search and similarity analysis.

**Structure**:
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
    },
    {
      "name": "test_aasx_test_submodels",
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

**Use Cases**:
- Semantic search
- Similarity analysis
- AI embeddings
- Vector database management

## Configuration

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

### Selective Export

```python
# Export only specific formats
config = LoaderConfig(
    export_formats=['json', 'csv']  # Only JSON and CSV
)

# Or use individual flags
config = LoaderConfig(
    export_json=True,
    export_csv=True,
    export_yaml=False,
    export_graph=False,
    export_rag=False,
    export_vector_db=False,
    export_sqlite=False
)
```

## Output Structure

### Expected Directory Layout
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

### File Size Comparison
Typical file sizes for a small AASX file (1 asset, 1 submodel, 1 document):
- **CSV**: ~200 bytes (flattened, minimal)
- **YAML**: ~700 bytes (human-readable)
- **JSON**: ~1KB (complete data)
- **Graph**: ~750 bytes (nodes/edges)
- **RAG**: ~800 bytes (AI-ready content)
- **Vector DB**: ~300 bytes (metadata only)
- **SQLite**: ~53KB (full database with indexes)

## Integration Examples

### JSON for Web APIs
```python
import json

with open('aasx_data.json', 'r') as f:
    data = json.load(f)
    
# Use in FastAPI response
@app.get("/api/assets")
async def get_assets():
    return data['data']['assets']
```

### CSV for Analytics
```python
import pandas as pd

df = pd.read_csv('aasx_data.csv')
print(f"Total entities: {len(df)}")
print(f"Asset types: {df[df['entity_type'] == 'asset']['type'].unique()}")
```

### SQLite for Queries
```python
import sqlite3

conn = sqlite3.connect('aasx_data.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM assets")
asset_count = cursor.fetchone()[0]
print(f"Total assets: {asset_count}")
```

### RAG for AI Systems
```python
import json

with open('aasx_data_rag.json', 'r') as f:
    rag_data = json.load(f)
    
# Use with AI models
for entity in rag_data['entities']:
    content = entity['content']
    # Process with AI model
```

## Best Practices

### Format Selection
- **Use JSON** for general data exchange and APIs
- **Use YAML** for configuration and documentation
- **Use CSV** for analytics and spreadsheet work
- **Use Graph** for relationship analysis and Neo4j
- **Use RAG** for AI systems and semantic search
- **Use SQLite** for relational queries and structured access
- **Use Vector DB** for semantic search and similarity analysis

### Performance Considerations
- **Large datasets**: Use CSV or SQLite for efficient processing
- **Real-time APIs**: Use JSON for fast serialization
- **AI applications**: Use RAG format for optimized content
- **Analytics**: Use CSV or SQLite for query performance

### Data Consistency
All formats contain the same core data but optimized for different use cases:
- **Consistent entity IDs** across all formats
- **Preserved relationships** in graph format
- **Quality metrics** included in structured formats
- **Metadata** maintained across all exports

## Troubleshooting

### Common Issues

1. **Missing Export Files**
   - Check `export_formats` configuration
   - Verify output directory permissions
   - Review error logs for specific format failures

2. **Large File Sizes**
   - SQLite databases can be large due to indexes
   - Consider selective export for specific use cases
   - Use compression for storage optimization

3. **Format Compatibility**
   - JSON/YAML: Universal compatibility
   - CSV: Check encoding for special characters
   - SQLite: Ensure SQLite client compatibility
   - Graph: Verify Neo4j version compatibility

### Validation

```python
# Validate export completeness
import os

expected_files = [
    'aasx_data.csv',
    'aasx_data.db', 
    'aasx_data.json',
    'aasx_data.yaml',
    'aasx_data_graph.json',
    'aasx_data_rag.json',
    'aasx_data_vector_db.json'
]

for file in expected_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - Missing")
```

---

**Last Updated**: July 2025  
**Framework Version**: 1.0.0  
**Export Formats**: 7 comprehensive formats 