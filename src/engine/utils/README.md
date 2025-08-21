# Engine Utilities

Comprehensive utility modules for the AAS Data Modeling Engine, providing essential functionality for async operations, data transformation, file handling, time management, and validation.

## Overview

The Engine Utilities package provides a collection of robust, production-ready utility modules that handle common programming tasks and patterns. Each module is designed to be:

- **Modular**: Independent modules that can be used separately
- **Type-safe**: Full type hints and validation
- **Well-tested**: Comprehensive test coverage
- **Production-ready**: Error handling, logging, and configuration options
- **Extensible**: Easy to extend and customize

## Modules

### 1. Async Helpers (`async_helpers.py`)

Comprehensive async utility functions for handling asynchronous operations.

**Features:**
- **Timeout Handling**: Execute coroutines with configurable timeouts
- **Retry Logic**: Configurable retry strategies with exponential backoff
- **Batch Processing**: Process items in batches with controlled concurrency
- **Rate Limiting**: Control execution frequency
- **Circuit Breaker**: Basic circuit breaker pattern implementation
- **Parallel Processing**: Parallel execution with worker limits

**Key Classes:**
- `AsyncHelpers`: Main utility class with static methods
- `RetryConfig`: Configuration for retry behavior
- `RetryStrategy`: Enum for different retry strategies

**Example Usage:**
```python
from engine.utils.async_helpers import AsyncHelpers, RetryConfig

# Retry with exponential backoff
config = RetryConfig(max_attempts=3, base_delay=1.0)
result = await AsyncHelpers.retry_async(
    my_async_function, 
    config=config
)

# Batch processing
results = await AsyncHelpers.batch_process(
    items, 
    processor_func, 
    batch_size=10
)
```

### 2. Data Transformers (`data_transformers.py`)

Data format conversion, schema transformation, and data cleaning utilities.

**Features:**
- **Format Conversion**: Convert between JSON, CSV, XML, YAML, Parquet, Excel
- **Schema Transformation**: Map and transform data schemas
- **Data Cleaning**: Apply cleaning rules to data
- **Data Validation**: Validate data against schemas
- **Pandas Integration**: Native support for DataFrames and Series

**Key Classes:**
- `DataTransformers`: Main transformation utility class
- `DataFormat`: Enum for supported data formats
- `TransformationConfig`: Configuration for transformations

**Example Usage:**
```python
from engine.utils.data_transformers import DataTransformers, DataFormat

# Convert data to different formats
json_data = DataTransformers.convert_format(data, DataFormat.JSON)
csv_data = DataTransformers.convert_format(df, DataFormat.CSV)

# Transform schema
schema_mapping = {"old_name": "new_name"}
transformed = DataTransformers.transform_schema(data, schema_mapping)

# Clean data
cleaning_rules = {"name": lambda x: x.strip().lower()}
cleaned = DataTransformers.clean_data(data, cleaning_rules)
```

### 3. File Handlers (`file_handlers.py`)

Comprehensive file operations, compression, and management utilities.

**Features:**
- **File Information**: Get detailed file metadata and checksums
- **Compression**: Support for GZIP, BZIP2, LZMA, ZIP, and TAR
- **File Operations**: Copy, move, delete with safety features
- **Pattern Matching**: Find files using glob patterns
- **Temporary Files**: Context managers for temporary files/directories
- **File Reading/Writing**: Text and JSON file operations

**Key Classes:**
- `FileHandlers`: Main file handling utility class
- `CompressionType`: Enum for compression types
- `FileInfo`: Data structure for file information

**Example Usage:**
```python
from engine.utils.file_handlers import FileHandlers, CompressionType

# Get file information
file_info = FileHandlers.get_file_info("path/to/file.txt")
print(f"File size: {file_info.size} bytes")

# Compress file
compressed = FileHandlers.compress_file(
    "input.txt", 
    compression_type=CompressionType.GZIP
)

# Find files
txt_files = FileHandlers.find_files(".", "*.txt", recursive=True)
```

### 4. Time Utils (`time_utils.py`)

Time and date manipulation, timezone handling, and time calculations.

**Features:**
- **Timezone Support**: Convert between timezones using pytz
- **Date Parsing**: Parse various date formats automatically
- **Date Formatting**: Multiple output formats (ISO, RFC, human-readable)
- **Business Logic**: Business day calculations and holiday support
- **Time Ranges**: Create and manipulate time ranges
- **Duration Handling**: Format and parse time durations

**Key Classes:**
- `TimeUtils`: Main time utility class
- `TimeFormat`: Enum for time formats
- `TimeRange`: Data structure for time ranges

**Example Usage:**
```python
from engine.utils.time_utils import TimeUtils, TimeFormat

# Parse datetime string
dt = TimeUtils.parse_datetime("2023-12-25 10:30:00")

# Format datetime
formatted = TimeUtils.format_datetime(dt, TimeFormat.HUMAN)

# Business day calculations
is_business = TimeUtils.is_business_day(dt)
next_business_day = TimeUtils.add_business_days(dt, 5)
```

### 5. Validators (`validators.py`)

Comprehensive validation utilities for various data types and formats.

**Features:**
- **Email Validation**: RFC-compliant email validation
- **URL Validation**: URL format and scheme validation
- **IP Address Validation**: IPv4/IPv6 with range checking
- **Phone Number Validation**: International phone number formats
- **Credit Card Validation**: Luhn algorithm validation
- **Password Strength**: Comprehensive password validation
- **JSON Schema**: JSON schema validation
- **File Path Validation**: File existence and type checking

**Key Classes:**
- `Validators`: Main validation utility class
- `ValidationResult`: Result structure for validation operations
- `ValidationLevel`: Enum for validation levels

**Example Usage:**
```python
from engine.utils.validators import Validators

# Validate email
email_result = Validators.validate_email("user@example.com")
if email_result.is_valid:
    print("Valid email")

# Validate password strength
password_result = Validators.validate_password_strength(
    "MyPassword123!",
    min_length=8,
    require_special=True
)

# Validate JSON schema
schema = {"type": "object", "properties": {"name": {"type": "string"}}}
validation = Validators.validate_json_schema(data, schema)
```

## Installation and Dependencies

### Required Dependencies

```bash
pip install pandas numpy pytz email-validator
```

### Optional Dependencies

- **PyYAML**: For YAML format support in data transformers
- **openpyxl**: For Excel format support in data transformers

## Testing

Run the comprehensive test suite:

```bash
cd scripts
python test_engine_utils.py
```

The test suite covers:
- All utility modules
- Edge cases and error conditions
- Integration between modules
- Performance characteristics

## Configuration

Most utilities provide configuration options through dataclass configurations:

```python
from engine.utils.async_helpers import RetryConfig
from engine.utils.data_transformers import TransformationConfig

# Configure retry behavior
retry_config = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF
)

# Configure data transformation
transform_config = TransformationConfig(
    preserve_original=True,
    handle_missing="fill",
    missing_fill_value="N/A"
)
```

## Error Handling

All utilities include comprehensive error handling:

- **Graceful Degradation**: Fallback options when operations fail
- **Detailed Error Messages**: Clear error descriptions for debugging
- **Logging Integration**: Structured logging for monitoring
- **Exception Types**: Specific exception types for different error conditions

## Performance Considerations

- **Async Operations**: Non-blocking async operations for I/O-bound tasks
- **Batch Processing**: Efficient batch operations with configurable concurrency
- **Lazy Evaluation**: On-demand processing to minimize memory usage
- **Caching**: Built-in caching for expensive operations where appropriate

## Extending the Utilities

### Adding New Validation Rules

```python
from engine.utils.validators import Validators

class CustomValidators(Validators):
    @staticmethod
    def validate_custom_field(value: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        # Add custom validation logic
        return result
```

### Adding New Data Formats

```python
from engine.utils.data_transformers import DataTransformers, DataFormat

class CustomDataTransformers(DataTransformers):
    @staticmethod
    def _to_custom_format(data: Any, config: TransformationConfig) -> str:
        # Implement custom format conversion
        return custom_string
```

## Contributing

When adding new utilities:

1. **Follow the existing patterns** for class structure and method organization
2. **Include comprehensive docstrings** with examples
3. **Add type hints** for all functions and methods
4. **Write tests** for new functionality
5. **Update this README** with new features and examples

## License

This module is part of the AAS Data Modeling Engine and follows the same license terms.

## Support

For issues, questions, or contributions:

1. Check the test suite for usage examples
2. Review the docstrings for detailed API documentation
3. Submit issues with detailed error descriptions
4. Include test cases when reporting bugs

