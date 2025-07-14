# 📁 Systematic Output Structure

This document describes the systematic folder structure for ETL pipeline results, designed to organize processed AASX data in a logical and maintainable way.

## 🎯 Overview

The ETL pipeline now supports a systematic folder structure that organizes results by:
- **Timestamp**: Each ETL run gets a timestamped folder
- **File**: Each processed AASX file gets its own subfolder
- **Format**: Each file contains multiple output formats (JSON, YAML, CSV, Graph)

## 🏗️ Folder Structure

### Default Structure: `timestamped_by_file`

```
output/etl_results/
├── etl_run_20250109_143022/           # Timestamped run folder
│   ├── Example_AAS_ServoDCMotor_21/   # Individual file folder
│   │   ├── aasx_data.json            # JSON format
│   │   ├── aasx_data.yaml            # YAML format
│   │   ├── aasx_data.csv             # CSV format
│   │   └── aasx_data_graph.json      # Graph format
│   ├── additive-manufacturing-3d-printer_converted/
│   │   ├── aasx_data.json
│   │   ├── aasx_data.yaml
│   │   ├── aasx_data.csv
│   │   └── aasx_data_graph.json
│   └── hydrogen-filling-station_converted/
│       ├── aasx_data.json
│       ├── aasx_data.yaml
│       ├── aasx_data.csv
│       └── aasx_data_graph.json
├── etl_run_20250109_150145/           # Another run
│   └── ...
└── ...
```

### Alternative Structures

#### 1. `by_type` Structure
```
output/etl_results/
├── by_file/
│   ├── Example_AAS_ServoDCMotor_21/
│   │   ├── aasx_data.json
│   │   ├── aasx_data.yaml
│   │   ├── aasx_data.csv
│   │   └── aasx_data_graph.json
│   └── ...
└── ...
```

#### 2. `flat` Structure
```
output/etl_results/
├── Example_AAS_ServoDCMotor_21/
│   ├── aasx_data.json
│   ├── aasx_data.yaml
│   ├── aasx_data.csv
│   └── aasx_data_graph.json
└── ...
```

## ⚙️ Configuration

The folder structure is configured in `webapp/config/config_etl.yaml`:

```yaml
# Output Configuration
output:
  # Base output directory
  base_directory: "output/etl_results"
  # Create timestamped subdirectories
  timestamped_output: true
  # Create separate outputs for each file
  separate_file_outputs: true
  # Include file name in output directory
  include_filename_in_output: true
  # Create systematic folder structure
  systematic_structure: true
  # Folder structure: timestamped_by_file, by_type, flat
  folder_structure: "timestamped_by_file"
```

### Configuration Management

The ETL configuration is managed through the webapp's configuration system:

```python
from webapp.config.etl_config import get_etl_config, ETLConfig

# Load configuration
etl_config = get_etl_config()

# Check systematic structure settings
if etl_config.is_systematic_structure_enabled():
    folder_type = etl_config.get_folder_structure_type()
    output_dir = etl_config.get_base_output_directory()
```

## 📄 Output Files

Each file folder contains the following output formats:

### 1. `aasx_data.json`
- **Format**: JSON
- **Content**: Complete transformed data with metadata
- **Use case**: Web APIs, data exchange, general processing

### 2. `aasx_data.yaml`
- **Format**: YAML
- **Content**: Human-readable version of the data
- **Use case**: Configuration, documentation, manual review

### 3. `aasx_data.csv`
- **Format**: CSV
- **Content**: Flattened data for spreadsheet analysis
- **Use case**: Business intelligence, Excel analysis, reporting

### 4. `aasx_data_graph.json`
- **Format**: JSON (Graph format)
- **Content**: Nodes and edges for graph databases
- **Use case**: Neo4j import, graph analysis, relationship visualization

## 🔧 Usage Examples

### Running ETL with Systematic Structure

```bash
# Run ETL pipeline (uses webapp config by default)
python scripts/run_etl.py

# Run with specific configuration
python scripts/run_etl.py --config webapp/config/config_etl.yaml

# Run with verbose output to see folder creation
python scripts/run_etl.py --verbose
```

### Testing the Structure

```bash
# Test the systematic folder structure
python scripts/test_systematic_structure.py

# Test webapp ETL configuration integration
python scripts/test_webapp_etl_config.py
```

### Programmatic Usage

```python
from backend.aasx.aasx_loader import LoaderConfig, AASXLoader

# Create loader with systematic structure
config = LoaderConfig(
    output_directory="output/etl_results",
    systematic_structure=True,
    folder_structure="timestamped_by_file",
    separate_file_outputs=True,
    include_filename_in_output=True
)

loader = AASXLoader(config=config, source_file="data/aasx-examples/example.aasx")
```

### Webapp Integration

The ETL pipeline is fully integrated with the webapp:

```python
from webapp.aasx.routes import get_etl_pipeline

# Get ETL pipeline with webapp configuration
pipeline = get_etl_pipeline()

# Process files using systematic structure
result = pipeline.process_aasx_file("data/aasx-examples/example.aasx")
```

## 🎨 Benefits

### 1. **Organization**
- Clear separation between different ETL runs
- Easy to identify which files were processed when
- Logical grouping of related data

### 2. **Traceability**
- Timestamped folders provide audit trail
- Easy to track processing history
- Version control friendly

### 3. **Scalability**
- Supports multiple file formats
- Easy to add new output formats
- Maintains structure as data grows

### 4. **Usability**
- Intuitive folder navigation
- Consistent naming conventions
- Easy to find specific data

## 🔄 Migration from Legacy Structure

If you have existing ETL results in the old flat structure, you can:

1. **Keep existing data**: Old structure still works with `systematic_structure: false`
2. **Migrate data**: Use the migration script to reorganize existing results
3. **Fresh start**: New runs will use the systematic structure

### Legacy Structure (for reference)
```
output/etl_results/
├── aasx_data_20250109_143022.json
├── aasx_data_20250109_143022.yaml
├── aasx_data_20250109_143022.csv
└── aasx_data_20250109_143022_graph.json
```

## 🛠️ Customization

### Adding New Output Formats

To add new output formats, modify the `_export_to_files` method in `backend/aasx/aasx_loader.py`:

```python
def _export_to_files(self, data: Dict[str, Any]) -> List[str]:
    exported_files = []
    
    # Existing formats...
    
    # Add new format
    xml_path = self.output_dir / "aasx_data.xml"
    self._export_to_xml(data, xml_path)
    exported_files.append(str(xml_path))
    
    return exported_files
```

### Custom Folder Naming

You can customize folder naming by modifying the `_create_output_directory` method:

```python
def _create_output_directory(self) -> Path:
    # Custom timestamp format
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Custom file naming
    if self.source_file:
        file_name = Path(self.source_file).stem.replace('_', '-')
        return base_dir / f"run_{timestamp}" / file_name
```

## 📊 Monitoring and Maintenance

### Cleanup Old Runs

```bash
# Remove runs older than 30 days
find output/etl_results -name "etl_run_*" -type d -mtime +30 -exec rm -rf {} \;
```

### Disk Space Monitoring

```bash
# Check disk usage
du -sh output/etl_results/*

# Find largest runs
du -sh output/etl_results/etl_run_* | sort -hr
```

## 🚀 Future Enhancements

Planned improvements for the systematic structure:

1. **Compression**: Automatic compression of old runs
2. **Indexing**: Searchable index of all processed files
3. **Metadata**: Enhanced metadata tracking
4. **Backup**: Automated backup of important runs
5. **Cleanup**: Intelligent cleanup policies

---

This systematic structure ensures that your ETL results are well-organized, easily accessible, and maintainable as your data processing needs grow. 