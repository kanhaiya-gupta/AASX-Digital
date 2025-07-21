# AASX Processing Architecture & ETL Pipeline

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Overview](#architecture-overview)
3. [Detailed Chain Process](#detailed-chain-process)
4. [ETL Pipeline Stages](#etl-pipeline-stages)
5. [Component Details](#component-details)
6. [Auto-Setup Process](#auto-setup-process)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Usage Examples](#usage-examples)
9. [Troubleshooting](#troubleshooting)

## 🎯 Overview

The AASX Processing Architecture provides a robust solution for processing Asset Administration Shell Exchange (AASX) files using proper AAS Core 3.0 libraries. Since Python lacks official AAS libraries, we use a .NET-based processor with Python orchestration.

### Key Features
- ✅ **Proper AAS Processing**: Uses official AAS Core 3.0 libraries
- ✅ **Auto-Setup**: Automatically builds and configures .NET processor
- ✅ **Data Validation**: Ensures AAS specification compliance
- ✅ **ETL Pipeline**: Complete extraction, transformation, and loading
- ✅ **Multiple Output Formats**: JSON, YAML, and structured data

## 🏗️ Architecture Overview

```mermaid
graph TB
    A[AASX File] --> B[.NET AAS Processor]
    B --> C[JSON Output]
    C --> D[Python ETL Pipeline]
    D --> E[Validated Data]
    E --> F[Multiple Formats]
    
    B --> G[AasCore.Aas3.Package]
    B --> H[AasCore.Aas3_0]
    
    D --> I[Data Validation]
    D --> J[Data Cleaning]
    D --> K[Format Conversion]
    
    F --> L[JSON Files]
    F --> M[YAML Files]
    F --> N[Structured Data]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#fce4ec
```

## 🔄 Detailed Chain Process

### Phase 1: .NET Processor Setup
```mermaid
sequenceDiagram
    participant U as User
    participant P as Python Script
    participant B as .NET Bridge
    participant N as .NET Processor
    participant C as AAS Core 3.0
    
    U->>P: Import aasx_processor
    P->>B: Initialize DotNetAasBridge
    B->>N: Check if processor exists
    alt Processor not found
        B->>N: Build processor
        N->>C: Restore NuGet packages
        N->>C: Build with AAS Core 3.0
        B->>P: Return success
    else Processor exists
        B->>P: Return ready status
    end
```

### Phase 2: AASX Processing
```mermaid
sequenceDiagram
    participant P as Python ETL
    participant B as .NET Bridge
    participant N as .NET Processor
    participant A as AASX File
    participant J as JSON Output
    
    P->>B: process_aasx_file(aasx_path)
    B->>N: Call processor with file
    N->>A: Read AASX file
    N->>N: Parse with AAS Core 3.0
    N->>J: Generate JSON output
    B->>P: Return processed data
    P->>P: Validate and clean data
    P->>P: Return final result
```

## 🔧 ETL Pipeline Stages

### 1. Extraction Stage
```mermaid
graph LR
    A[AASX File] --> B[.NET Processor]
    B --> C[Raw JSON Data]
    C --> D[Asset Data]
    C --> E[Submodel Data]
    C --> F[Document Data]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
```

**Process:**
- AASX file is read by .NET processor
- AAS Core 3.0 libraries parse the file structure
- Raw JSON data is extracted with proper AAS semantics
- Data includes assets, submodels, and documents

### 2. Transformation Stage
```mermaid
graph LR
    A[Raw JSON Data] --> B[Data Validation]
    B --> C[Data Cleaning]
    C --> D[Structure Normalization]
    D --> E[Quality Checks]
    E --> F[Transformed Data]
    
    style A fill:#fff3e0
    style B fill:#e8f5e8
    style C fill:#f3e5f5
    style F fill:#fce4ec
```

**Process:**
- **Validation**: Check AAS specification compliance
- **Cleaning**: Remove null/invalid entries
- **Normalization**: Standardize data structure
- **Quality Checks**: Ensure data integrity

### 3. Loading Stage
```mermaid
graph LR
    A[Transformed Data] --> B[JSON Output]
    A --> C[YAML Output]
    A --> D[Structured Data]
    A --> E[Database Storage]
    
    B --> F[File System]
    C --> F
    D --> G[Data Warehouse]
    E --> H[Neo4j Graph DB]
    
    style A fill:#fce4ec
    style F fill:#e1f5fe
    style G fill:#e8f5e8
    style H fill:#f3e5f5
```

**Process:**
- **JSON Output**: Human-readable structured data
- **YAML Output**: Configuration-friendly format
- **Structured Data**: Database-ready format
- **Graph Storage**: Neo4j for relationship analysis

## 🧩 Component Details

### 1. .NET AAS Processor (`aas-processor/`)

**Purpose**: Core AASX processing engine
**Language**: C# (.NET 6.0)
**Dependencies**:
```xml
<PackageReference Include="AasCore.Aas3.Package" Version="1.0.2" />
<PackageReference Include="AasCore.Aas3_0" Version="1.0.4" />
```

**Key Features**:
- Proper AASX file parsing
- XML and JSON content extraction
- AAS Core 3.0 specification compliance
- Error handling and validation

### 2. Python Bridge (`src/aasx/dotnet_bridge.py`)

**Purpose**: Python interface to .NET processor
**Key Functions**:
```python
class DotNetAasBridge:
    def __init__(self, dotnet_project_path: str = "aas-processor")
    def _build_processor(self) -> bool
    def process_aasx_file(self, aasx_file_path: str) -> Optional[Dict[str, Any]]
    def is_available(self) -> bool
```

### 3. Python ETL Pipeline (`src/aasx/aasx_processor.py`)

**Purpose**: Complete ETL orchestration
**Key Classes**:
```python
class AASXProcessor:
    def __init__(self, aasx_file_path: str)
    def ensure_processor_ready(self) -> bool
    def process(self) -> Dict[str, Any]
    def _validate_and_clean_result(self, result: Dict[str, Any]) -> Dict[str, Any]

class AASXBatchProcessor:
    def process_all(self) -> Dict[str, Any]
```

## 🤖 Auto-Setup Process

```mermaid
flowchart TD
    A[Import aasx_processor] --> B{Check .NET Bridge}
    B -->|Available| C{Check .NET Processor}
    B -->|Not Available| D[Raise ImportError]
    
    C -->|Available| E[Ready for Processing]
    C -->|Not Available| F[Auto-Build Processor]
    
    F --> G{Restore Packages}
    G -->|Success| H{Build Project}
    G -->|Failure| I[Log Error]
    
    H -->|Success| J{Check Executable}
    H -->|Failure| I
    
    J -->|Exists| E
    J -->|Missing| I
    
    E --> K[Process AASX Files]
    
    style A fill:#e1f5fe
    style E fill:#e8f5e8
    style I fill:#ffebee
    style K fill:#fce4ec
```

**Auto-Setup Features**:
- ✅ Automatic .NET processor building
- ✅ NuGet package restoration
- ✅ Executable verification
- ✅ Error handling and logging
- ✅ Idempotent operations

## 📊 Data Flow Diagrams

### Complete Data Flow
```mermaid
graph TB
    subgraph "Input Layer"
        A1[AASX File 1]
        A2[AASX File 2]
        A3[AASX File N]
    end
    
    subgraph "Processing Layer"
        B1[.NET Processor 1]
        B2[.NET Processor 2]
        B3[.NET Processor N]
    end
    
    subgraph "ETL Layer"
        C1[Python ETL 1]
        C2[Python ETL 2]
        C3[Python ETL N]
    end
    
    subgraph "Validation Layer"
        D1[Data Validation]
        D2[Quality Checks]
        D3[Structure Normalization]
    end
    
    subgraph "Output Layer"
        E1[JSON Files]
        E2[YAML Files]
        E3[Structured Data]
        E4[Graph Database]
    end
    
    A1 --> B1 --> C1 --> D1 --> E1
    A2 --> B2 --> C2 --> D2 --> E2
    A3 --> B3 --> C3 --> D3 --> E3
    
    D1 --> E4
    D2 --> E4
    D3 --> E4
    
    style A1 fill:#e1f5fe
    style B1 fill:#f3e5f5
    style C1 fill:#e8f5e8
    style D1 fill:#fff3e0
    style E1 fill:#fce4ec
```

### Batch Processing Flow
```mermaid
graph LR
    A[Directory Scan] --> B[File Discovery]
    B --> C[Parallel Processing]
    C --> D[Data Aggregation]
    D --> E[Validation Summary]
    E --> F[Output Generation]
    
    C --> G[Processor 1]
    C --> H[Processor 2]
    C --> I[Processor N]
    
    G --> D
    H --> D
    I --> D
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fce4ec
```

## 💻 Usage Examples

### Basic Usage
```python
from aasx.aasx_processor import AASXProcessor

# Auto-setup happens automatically
processor = AASXProcessor("path/to/file.aasx")
result = processor.process()

print(f"Assets: {len(result['assets'])}")
print(f"Submodels: {len(result['submodels'])}")
```

### Batch Processing
```python
from aasx.aasx_processor import AASXBatchProcessor

batch_processor = AASXBatchProcessor("path/to/aasx/directory")
results = batch_processor.process_all()

print(f"Processed: {results['successful_processing']} files")
print(f"Failed: {results['failed_processing']} files")
```

### Manual Setup
```python
from aasx.aasx_processor import auto_setup_dotnet_processor

# Manual setup if needed
if auto_setup_dotnet_processor():
    print("✅ .NET processor ready")
else:
    print("❌ Setup failed")
```

## 🔧 Troubleshooting

### Common Issues

#### 1. .NET Processor Build Failure
**Symptoms**: `Failed to build .NET project`
**Solutions**:
- Ensure .NET 6.0 SDK is installed
- Check NuGet package availability
- Verify project structure

#### 2. AASX Processing Errors
**Symptoms**: `Invalid result from .NET processor`
**Solutions**:
- Verify AASX file integrity
- Check file permissions
- Validate AASX format

#### 3. Import Errors
**Symptoms**: `DotNet bridge not available`
**Solutions**:
- Check Python path configuration
- Verify module structure
- Ensure auto-setup is working

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed setup and processing logs
from aasx.aasx_processor import AASXProcessor
```

## 📈 Performance Considerations

### Optimization Strategies
1. **Parallel Processing**: Batch processor uses multiple threads
2. **Caching**: Built processor is reused
3. **Memory Management**: Efficient data structures
4. **Error Recovery**: Graceful failure handling

### Scalability
- ✅ **Horizontal**: Multiple processors
- ✅ **Vertical**: Optimized single processor
- ✅ **Batch**: Efficient bulk processing
- ✅ **Streaming**: Large file handling

## 🔮 Future Enhancements

### Planned Features
- [ ] **Web API**: RESTful interface
- [ ] **Real-time Processing**: Streaming capabilities
- [ ] **Advanced Validation**: Custom validation rules
- [ ] **Plugin System**: Extensible processing
- [ ] **Cloud Integration**: AWS/Azure support

### Architecture Evolution
- [ ] **Microservices**: Distributed processing
- [ ] **Event-Driven**: Message-based architecture
- [ ] **Containerization**: Docker deployment
- [ ] **Monitoring**: Performance metrics

---

## 📚 Additional Resources

- [AAS Core 3.0 Specification](https://www.plattform-i40.de/PI40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part1_V3.html)
- [.NET AAS Libraries](https://www.nuget.org/packages/AasCore.Aas3.Package/)
- [AASX Package Format](https://www.plattform-i40.de/PI40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part2_V3.html)

---

*This architecture ensures proper AASX processing using official AAS Core 3.0 libraries while providing a user-friendly Python interface with automatic setup capabilities.* 