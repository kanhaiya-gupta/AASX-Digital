# AI/RAG Data Processors for Asset Administrative Shell (AAS)

## Overview

The AI/RAG Data Processors system is a comprehensive, modular solution designed to process and analyze diverse file types commonly found in Asset Administrative Shell (AAS) environments. This system enables intelligent content extraction, semantic analysis, and vector embedding generation for industrial asset management applications.

## 🎯 Key Features

- **Multi-Format Support**: Process 93+ different file types
- **Semantic Analysis**: Intelligent content understanding and pattern detection
- **Modular Architecture**: Easy to extend with new processors
- **Priority System**: Most specific processors take precedence
- **Rich Metadata**: Detailed information about processed files
- **Vector Embeddings**: Ready for AI-powered search and retrieval
- **Error Handling**: Graceful handling of missing dependencies

## 📁 Supported File Types

### 🏭 Industrial & Technical Documents
- **CAD Files**: `.dwg`, `.dxf`, `.step`, `.stp`, `.iges`, `.stl`, `.obj`, `.svg`
- **Spreadsheets**: `.xlsx`, `.xls`, `.csv`, `.tsv`, `.ods`, `.xlsm`, `.xlsb`
- **Documents**: `.pdf`, `.docx`, `.doc`, `.txt`, `.rtf`, `.odt`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`

### 💻 Code & Configuration
- **Programming**: `.py`, `.js`, `.java`, `.cpp`, `.cs`, `.php`, `.rb`, `.go`
- **Web**: `.html`, `.css`, `.jsx`, `.tsx`, `.vue`, `.svelte`
- **Data**: `.sql`, `.json`, `.xml`, `.yaml`, `.yml`, `.toml`
- **Configuration**: `.ini`, `.cfg`, `.conf`, `.env`, `.properties`

### 📊 Structured Data
- **Graph Data**: `.json` (with graph structure detection)
- **Structured Data**: `.json`, `.yaml`, `.yml`, `.xml`, `.csv`

## 🏗️ Architecture

### Core Components

```
src/ai_rag/processors/
├── __init__.py                 # Package initialization
├── base_processor.py          # Base processor class
├── processor_manager.py       # Main orchestrator
├── document_processor.py      # PDF, DOC, TXT processing
├── image_processor.py         # Image OCR and analysis
├── code_processor.py          # Code file processing
├── spreadsheet_processor.py   # Excel, CSV with semantic analysis
├── cad_processor.py           # CAD/technical drawing processing
├── structured_data_processor.py  # JSON, YAML processing
└── graph_data_processor.py    # Graph-structured data
```

### Processor Hierarchy

The system uses a priority-based approach where more specific processors take precedence:

1. **GraphDataProcessor** - For graph-structured JSON files
2. **StructuredDataProcessor** - For general structured data
3. **CADProcessor** - For technical drawings and CAD files
4. **SpreadsheetProcessor** - For Excel, CSV with semantic analysis
5. **DocumentProcessor** - For PDFs, documents, and text files
6. **ImageProcessor** - For image files with OCR
7. **CodeProcessor** - For programming language files

## 🚀 Quick Start

### Installation

1. **Install Python dependencies**:
```bash
pip install -r src/ai_rag/requirements_processors.txt
```

2. **Install system dependencies** (if needed):
```bash
# For OCR (Windows)
# Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki

# For PDF processing
pip install PyPDF2 pdfplumber pymupdf

# For CAD processing
pip install ezdxf trimesh
```

### Basic Usage

```python
from src.ai_rag.processors import ProcessorManager
from src.ai_rag.text_embeddings import TextEmbeddingManager
from src.ai_rag.vector_db import QdrantClient

# Initialize components
text_embedding_manager = TextEmbeddingManager()
vector_db = QdrantClient()

# Create processor manager
processor_manager = ProcessorManager(
    text_embedding_manager=text_embedding_manager,
    vector_db=vector_db
)

# Process a file
file_path = Path("path/to/your/file.pdf")
file_info = {"file_id": "unique_id", "project_id": "project_123"}

result = processor_manager.process_file("project_123", file_info, file_path)
print(f"Processing result: {result['status']}")
```

### Testing the System

Run the comprehensive test suite:

```bash
python test_new_processors.py
```

This will test all processors with sample files and verify the priority system.

## 📋 Processor Details

### 1. Document Processor
**Handles**: PDF, DOCX, DOC, TXT, RTF, ODT

**Features**:
- Multi-library PDF extraction (PyPDF2, pdfplumber, PyMuPDF)
- Word document processing
- Text extraction with metadata
- Fallback mechanisms for different formats

**Example Output**:
```json
{
  "content_type": "document",
  "text_length": 1542,
  "document_type": "pdf",
  "pages": 3,
  "content_preview": "Asset specification document..."
}
```

### 2. Image Processor
**Handles**: JPG, PNG, GIF, BMP, TIFF, WEBP

**Features**:
- Multi-engine OCR (Tesseract, EasyOCR, PaddleOCR)
- Image metadata extraction
- Text content extraction from images
- Fallback OCR engines

**Example Output**:
```json
{
  "content_type": "image",
  "image_type": "png",
  "dimensions": "1920x1080",
  "ocr_text": "Technical drawing of motor housing...",
  "ocr_confidence": 0.85
}
```

### 3. Spreadsheet Processor
**Handles**: XLSX, XLS, CSV, TSV, ODS

**Features**:
- Multi-sheet Excel processing
- Semantic analysis of data patterns
- Technical specification detection
- Asset information identification
- Statistical analysis

**Example Output**:
```json
{
  "content_type": "spreadsheet",
  "spreadsheet_type": "csv",
  "total_rows": 150,
  "total_columns": 8,
  "semantic_analysis": "Technical specifications detected in columns: Power, Voltage, Current...",
  "content_patterns": "Asset information detected in columns: Asset_ID, Name, Type..."
}
```

### 4. CAD Processor
**Handles**: DWG, DXF, STEP, STP, IGES, STL, OBJ, SVG

**Features**:
- Technical drawing analysis
- Geometric information extraction
- Material and dimension detection
- Layer and entity analysis
- Engineering metadata extraction

**Example Output**:
```json
{
  "content_type": "cad",
  "cad_type": "dxf",
  "technical_analysis": "Motor housing design with steel material...",
  "dimensions": "200mm x 150mm",
  "layers": ["DIMENSIONS", "MATERIALS", "ANNOTATIONS"],
  "total_entities": 45
}
```

### 5. Code Processor
**Handles**: Python, JavaScript, Java, C++, C#, and 20+ other languages

**Features**:
- Meaningful code extraction (skips comments/boilerplate)
- Function and class detection
- Language-specific analysis
- Code metadata extraction

**Example Output**:
```json
{
  "content_type": "code",
  "language": "python",
  "functions": ["process_data", "validate_input"],
  "classes": ["DataProcessor", "Validator"],
  "code_preview": "def process_data(input_data):..."
}
```

### 6. Structured Data Processor
**Handles**: JSON, YAML, YML, XML

**Features**:
- Hierarchical data extraction
- Asset and submodel detection
- Metadata preservation
- Structured content analysis

### 7. Graph Data Processor
**Handles**: Graph-structured JSON files

**Features**:
- Node and relationship extraction
- Graph topology analysis
- Asset relationship mapping
- Network structure understanding

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# Vector Database
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=6333

# OpenAI (for embeddings)
OPENAI_API_KEY=your_openai_api_key

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Processor Configuration

Each processor can be configured independently:

```python
# Custom processor configuration
processor_config = {
    "document_processor": {
        "max_file_size": "10MB",
        "ocr_enabled": True
    },
    "spreadsheet_processor": {
        "max_rows": 10000,
        "semantic_analysis": True
    }
}
```

## 📊 Performance & Scalability

### Processing Statistics
- **Average processing time**: 2-5 seconds per file
- **Memory usage**: 50-200MB per processor
- **Concurrent processing**: Supports multiple files simultaneously
- **Error recovery**: Graceful handling of corrupted files

### Optimization Tips
1. **Batch processing**: Process multiple files together
2. **Caching**: Enable embedding caching for repeated content
3. **Parallel processing**: Use multiple worker processes
4. **Resource limits**: Set appropriate memory and CPU limits

## 🏭 AAS Integration Use Cases

### 1. Asset Documentation Processing
```python
# Process asset specification documents
asset_docs = [
    "motor_specs.pdf",
    "pump_drawings.dwg", 
    "sensor_data.csv",
    "control_logic.py"
]

for doc in asset_docs:
    result = processor_manager.process_file("asset_123", doc_info, doc)
    # Store in AAS submodel
```

### 2. Technical Drawing Analysis
```python
# Extract technical information from CAD files
cad_files = ["assembly.dxf", "part_drawing.step"]

for cad_file in cad_files:
    result = processor_manager.process_file("project_456", cad_info, cad_file)
    # Extract dimensions, materials, tolerances
```

### 3. Spreadsheet Data Mining
```python
# Analyze equipment specifications
spec_sheets = ["equipment_list.xlsx", "maintenance_schedule.csv"]

for sheet in spec_sheets:
    result = processor_manager.process_file("facility_789", sheet_info, sheet)
    # Identify technical parameters and asset relationships
```

## 🧪 Testing & Quality Assurance

### Test Coverage
- **Unit tests**: Individual processor functionality
- **Integration tests**: End-to-end processing workflows
- **Performance tests**: Processing speed and memory usage
- **Error handling tests**: Graceful failure scenarios

### Running Tests
```bash
# Run all tests
python test_new_processors.py

# Run specific processor tests
python -m pytest tests/test_document_processor.py
python -m pytest tests/test_spreadsheet_processor.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```
   Error: name 'pd' is not defined
   Solution: pip install pandas openpyxl
   ```

2. **OCR Not Working**
   ```
   Error: Tesseract not found
   Solution: Install Tesseract OCR system package
   ```

3. **PDF Extraction Fails**
   ```
   Error: PDF extraction failed
   Solution: Try different PDF libraries (PyPDF2, pdfplumber, PyMuPDF)
   ```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging for troubleshooting
processor_manager = ProcessorManager(
    text_embedding_manager=text_embedding_manager,
    vector_db=vector_db,
    debug=True
)
```

## 📈 Future Enhancements

### Planned Features
- **Audio/Video Processing**: Support for multimedia files
- **3D Model Analysis**: Advanced CAD and 3D file processing
- **Machine Learning**: Automated content classification
- **Real-time Processing**: Stream processing capabilities
- **Cloud Integration**: AWS, Azure, GCP support

### Extension Points
- **Custom Processors**: Easy addition of new file types
- **Plugin System**: Third-party processor support
- **API Integration**: RESTful API for remote processing
- **Web Interface**: Browser-based file processing

## 🤝 Contributing

### Adding New Processors
1. Create a new processor class inheriting from `BaseDataProcessor`
2. Implement required methods: `can_process()`, `process()`
3. Add to `ProcessorManager` initialization
4. Update `requirements_processors.txt`
5. Add comprehensive tests

### Code Standards
- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Add type hints for all functions
- Write unit tests for new features

## 📄 License

This project is part of the AAS Data Modeling framework and follows the same licensing terms.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review test examples
3. Check the configuration documentation
4. Open an issue with detailed error information

---

**Last Updated**: July 2025  
**Version**: 1.0.0  
**Compatibility**: Python 3.8+, Windows/Linux/macOS 