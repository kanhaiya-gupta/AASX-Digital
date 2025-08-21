# 🏗️ Shared Modular Architecture Framework

> **A production-ready, enterprise-grade modular architecture template for mega projects**

[![Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-blue.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Pattern](https://img.shields.io/badge/Pattern-Repository%20Pattern-green.svg)](https://martinfowler.com/eaaCatalog/repository.html)
[![Layers](https://img.shields.io/badge/Layers-6%20Layer%20Architecture-orange.svg)](https://github.com/your-repo)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 **What This Architecture Provides**

This `src/shared` directory contains a **comprehensive modular architecture** that serves as the foundation for:

1. **🏗️ Current Project** - AASX Digital Twin Analytics Framework
2. **📋 Template for Mega Projects** - Reusable architecture for any large-scale data management system

### **🔧 Core Architectural Principles**

- **Clean Architecture** - Separation of concerns with distinct layers
- **Dependency Inversion** - High-level modules don't depend on low-level modules
- **Single Responsibility** - Each class has one reason to change
- **Open/Closed Principle** - Open for extension, closed for modification
- **Repository Pattern** - Abstracted data access layer
- **Service Layer** - Business logic encapsulation

## 🏛️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  🌐 Web Controllers  │  📱 API Routes  │  🔌 External APIs │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  🔧 Services  │  📊 Analytics  │  🎯 Business Logic       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  📋 Models  │  🗄️ Repositories  │  🔍 Query Handlers     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  💾 Database  │  🔐 Security  │  📝 Logging  │  ⚙️ Config  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 **Directory Structure**

```
src/shared/
├── 📁 database/                    # Database Infrastructure Layer
│   ├── __init__.py                 # Package exports
│   ├── base_manager.py             # Base database operations
│   ├── connection_manager.py       # Connection pooling & lifecycle
│   └── schema_manager.py           # Schema creation & management
├── 📁 models/                      # Domain Models Layer
│   ├── __init__.py                 # Package exports
│   ├── base_model.py               # Base model with common fields
│   ├── organization.py             # Organization model
│   ├── user.py                     # User model with roles
│   ├── use_case.py                 # Use case model
│   ├── project.py                  # Project model
│   ├── file.py                     # File model
│   └── digital_twin.py             # Digital twin model
├── 📁 repositories/                # Data Access Layer
│   ├── __init__.py                 # Package exports
│   ├── base_repository.py          # Generic CRUD operations
│   ├── organization_repository.py  # Organization data access
│   ├── user_repository.py          # User data access
│   ├── use_case_repository.py      # Use case data access
│   ├── project_repository.py       # Project data access
│   ├── file_repository.py          # File data access
│   └── digital_twin_repository.py  # Digital twin data access
├── 📁 services/                    # Business Logic Layer
│   ├── __init__.py                 # Package exports
│   ├── use_cases.py                # Use case business logic
│   ├── projects.py                 # Project business logic
│   ├── files.py                    # File business logic
│   └── processor.py                # ETL processing logic
├── 📁 utils/                       # Utility Functions Layer
│   ├── __init__.py                 # Package exports
│   ├── file_utils.py               # File operations
│   ├── validation_utils.py         # Data validation
│   ├── security_utils.py           # Security functions
│   └── logging_utils.py            # Logging utilities
├── 📁 config/                      # Configuration Layer
│   ├── __init__.py                 # Package exports
│   ├── database_config.py          # Database settings
│   ├── app_config.py               # Application settings
│   └── logging_config.py           # Logging configuration
├── database_manager.py             # Legacy monolithic manager (deprecated)
├── management.py                   # Legacy management utilities
├── config.py                       # Legacy configuration
├── utils.py                        # Legacy utilities
├── loggers.py                      # Legacy logging
└── __init__.py                     # Package initialization
```

## 🚀 **How to Use This Architecture**

### **1. In Current Project (AASX Framework)**

This architecture is actively used in the AASX Digital Twin Analytics Framework:

```python
# Example: Creating a use case with full architecture
from src.shared.services.use_cases import create_use_case
from src.shared.services.projects import create_project
from src.shared.services.files import upload_file

# 1. Create use case (Service Layer)
use_case = create_use_case(
    name="Manufacturing Analytics",
    description="Analytics for manufacturing processes",
    category="industrial"
)

# 2. Create project within use case (Service Layer)
project = create_project(
    name="Production Line A",
    description="Production line monitoring",
    use_case_id=use_case.id
)

# 3. Upload file to project (Service Layer)
file_info = upload_file(
    file_path="/path/to/data.csv",
    project_id=project.id,
    use_case_id=use_case.id
)
```

**Behind the scenes, this uses:**
- **Models Layer** - Data validation and structure
- **Repositories Layer** - Database operations
- **Database Layer** - Connection management and transactions
- **Utils Layer** - File validation and processing
- **Config Layer** - Environment-specific settings

### **2. As Template for Other Mega Projects**

This architecture can be adapted for any large-scale project:

#### **🏭 Manufacturing Project**
```python
# Adapt models for manufacturing
from src.shared.models.base_model import BaseModel

@dataclass
class ProductionLine(BaseModel):
    name: str
    capacity: int
    status: str
    location: str
    equipment: List[str]

@dataclass
class QualityControl(BaseModel):
    batch_id: str
    test_results: Dict[str, Any]
    inspector: str
    timestamp: datetime
```

#### **🏥 Healthcare Project**
```python
# Adapt models for healthcare
@dataclass
class Patient(BaseModel):
    patient_id: str
    name: str
    date_of_birth: datetime
    medical_history: List[str]
    current_medications: List[str]

@dataclass
class MedicalRecord(BaseModel):
    record_id: str
    patient_id: str
    diagnosis: str
    treatment_plan: str
    doctor: str
    date: datetime
```

#### **🏦 Financial Project**
```python
# Adapt models for financial services
@dataclass
class Account(BaseModel):
    account_number: str
    account_type: str
    balance: Decimal
    owner_id: str
    status: str

@dataclass
class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    amount: Decimal
    transaction_type: str
    description: str
    timestamp: datetime
```

## 🔧 **Architecture Components Deep Dive**

### **1. Database Layer (`database/`)**

**Purpose**: Database infrastructure and connection management

**Key Features**:
- **Connection Pooling** - Efficient database connection management
- **Transaction Support** - ACID compliance with rollback capabilities
- **Schema Management** - Automated table creation and migration
- **Error Handling** - Comprehensive error handling and logging

**Usage Example**:
```python
from src.shared.database.connection_manager import DatabaseConnectionManager

# Get database connection
with DatabaseConnectionManager() as db:
    # Execute queries
    result = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
    # Automatic connection cleanup
```

### **2. Models Layer (`models/`)**

**Purpose**: Data structures and validation

**Key Features**:
- **Base Model** - Common fields (id, created_at, updated_at)
- **Data Validation** - Pydantic-style validation
- **JSON Serialization** - Easy database storage and API responses
- **Type Safety** - Full type hints for IDE support

**Usage Example**:
```python
from src.shared.models.base_model import BaseModel
from dataclasses import dataclass

@dataclass
class CustomModel(BaseModel):
    name: str
    description: str
    
    def validate(self) -> bool:
        if not self.name.strip():
            raise ValueError("Name is required")
        return True
```

### **3. Repositories Layer (`repositories/`)**

**Purpose**: Data access abstraction

**Key Features**:
- **Generic CRUD** - Common operations (Create, Read, Update, Delete)
- **Specialized Queries** - Entity-specific operations
- **Relationship Management** - Handle complex relationships
- **Statistics** - Built-in analytics and reporting

**Usage Example**:
```python
from src.shared.repositories.base_repository import BaseRepository

class CustomRepository(BaseRepository[CustomModel]):
    def _get_table_name(self) -> str:
        return "custom_table"
    
    def _get_columns(self) -> List[str]:
        return ["id", "name", "description", "created_at", "updated_at"]
    
    def find_by_name(self, name: str) -> Optional[CustomModel]:
        sql = "SELECT * FROM custom_table WHERE name = ?"
        result = self.db_manager.execute_query(sql, (name,))
        return CustomModel.from_dict(result[0]) if result else None
```

### **4. Services Layer (`services/`)**

**Purpose**: Business logic and orchestration

**Key Features**:
- **Business Rules** - Complex business logic implementation
- **Transaction Management** - Multi-step operations
- **Validation** - Business rule validation
- **Orchestration** - Coordinate between multiple repositories

**Usage Example**:
```python
from src.shared.services.base_service import BaseService

class CustomService(BaseService):
    def create_with_validation(self, data: Dict[str, Any]) -> CustomModel:
        # Business logic validation
        if self._check_duplicate_name(data['name']):
            raise ValueError("Name already exists")
        
        # Create model
        model = CustomModel(**data)
        model.validate()
        
        # Save to database
        return self.repository.create(model)
    
    def _check_duplicate_name(self, name: str) -> bool:
        return self.repository.find_by_name(name) is not None
```

### **5. Utils Layer (`utils/`)**

**Purpose**: Common utility functions

**Key Features**:
- **File Operations** - File handling, validation, and processing
- **Data Validation** - Input validation and sanitization
- **Security** - Encryption, hashing, and security utilities
- **Logging** - Structured logging and monitoring

**Usage Example**:
```python
from src.shared.utils.file_utils import FileUtils
from src.shared.utils.validation_utils import ValidationUtils

# File operations
file_info = FileUtils.get_file_info("/path/to/file.csv")
is_valid = FileUtils.validate_file("/path/to/file.csv")

# Data validation
is_valid_email = ValidationUtils.is_valid_email("user@example.com")
is_valid_uuid = ValidationUtils.is_valid_uuid("123e4567-e89b-12d3-a456-426614174000")
```

### **6. Config Layer (`config/`)**

**Purpose**: Configuration management

**Key Features**:
- **Environment-Specific** - Development, testing, production configs
- **Type Safety** - Pydantic-based configuration
- **Validation** - Configuration validation
- **Flexibility** - Multiple configuration sources

**Usage Example**:
```python
from src.shared.config.app_config import get_app_config

# Get environment-specific configuration
config = get_app_config()

# Access configuration values
database_url = config.database_url
api_key = config.api_key
log_level = config.log_level
```

## 🎯 **Adaptation Guide for New Projects**

### **Step 1: Define Your Domain Models**

```python
# 1. Create your models extending BaseModel
from src.shared.models.base_model import BaseModel
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class YourEntity(BaseModel):
    name: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        if not self.name.strip():
            raise ValueError("Name is required")
        return True
```

### **Step 2: Create Repository**

```python
# 2. Create repository for your entity
from src.shared.repositories.base_repository import BaseRepository

class YourEntityRepository(BaseRepository[YourEntity]):
    def _get_table_name(self) -> str:
        return "your_entities"
    
    def _get_columns(self) -> List[str]:
        return ["id", "name", "description", "metadata", "created_at", "updated_at"]
    
    def find_by_name(self, name: str) -> Optional[YourEntity]:
        sql = "SELECT * FROM your_entities WHERE name = ?"
        result = self.db_manager.execute_query(sql, (name,))
        return YourEntity.from_dict(result[0]) if result else None
```

### **Step 3: Create Service**

```python
# 3. Create service with business logic
from src.shared.services.base_service import BaseService

class YourEntityService(BaseService):
    def __init__(self):
        super().__init__(YourEntityRepository())
    
    def create_entity(self, name: str, description: str) -> YourEntity:
        # Business logic
        if self.repository.find_by_name(name):
            raise ValueError("Entity with this name already exists")
        
        # Create and save
        entity = YourEntity(name=name, description=description)
        return self.repository.create(entity)
```

### **Step 4: Create API Endpoints**

```python
# 4. Create FastAPI endpoints
from fastapi import APIRouter, HTTPException
from src.shared.services.your_entity_service import YourEntityService

router = APIRouter()
service = YourEntityService()

@router.post("/entities/")
async def create_entity(name: str, description: str):
    try:
        entity = service.create_entity(name, description)
        return {"success": True, "entity": entity.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 📊 **Performance Benefits**

### **1. Scalability**
- **Connection Pooling** - Efficient database connection management
- **Caching Layers** - Built-in caching for frequently accessed data
- **Async Support** - Non-blocking operations for high concurrency

### **2. Maintainability**
- **Separation of Concerns** - Clear boundaries between layers
- **Single Responsibility** - Each class has one purpose
- **Dependency Injection** - Loose coupling between components

### **3. Testability**
- **Mockable Interfaces** - Easy to mock for unit testing
- **Isolated Components** - Test each layer independently
- **Comprehensive Testing** - Built-in test utilities and patterns

### **4. Extensibility**
- **Plugin Architecture** - Easy to add new features
- **Configuration Driven** - Environment-specific behavior
- **Modular Design** - Add/remove components without affecting others

## 🔒 **Security Features**

### **1. Data Protection**
- **Input Validation** - Comprehensive input sanitization
- **SQL Injection Prevention** - Parameterized queries
- **XSS Protection** - Output encoding and sanitization

### **2. Authentication & Authorization**
- **JWT Tokens** - Secure token-based authentication
- **Role-Based Access** - Granular permission system
- **API Key Management** - Secure API access

### **3. Encryption**
- **Data at Rest** - Database encryption
- **Data in Transit** - TLS/SSL encryption
- **Password Hashing** - Secure password storage

## 🧪 **Testing Strategy**

### **1. Unit Testing**
```python
import pytest
from src.shared.services.your_entity_service import YourEntityService

def test_create_entity_success():
    service = YourEntityService()
    entity = service.create_entity("Test Entity", "Test Description")
    assert entity.name == "Test Entity"
    assert entity.description == "Test Description"

def test_create_entity_duplicate_name():
    service = YourEntityService()
    service.create_entity("Test Entity", "Test Description")
    
    with pytest.raises(ValueError, match="already exists"):
        service.create_entity("Test Entity", "Another Description")
```

### **2. Integration Testing**
```python
def test_full_entity_lifecycle():
    # Test complete flow from API to database
    service = YourEntityService()
    
    # Create
    entity = service.create_entity("Test", "Description")
    
    # Read
    found = service.get_entity(entity.id)
    assert found.name == "Test"
    
    # Update
    updated = service.update_entity(entity.id, {"name": "Updated"})
    assert updated.name == "Updated"
    
    # Delete
    service.delete_entity(entity.id)
    assert service.get_entity(entity.id) is None
```

## 🚀 **Deployment Considerations**

### **1. Environment Configuration**
```python
# Development
export ENVIRONMENT=development
export DATABASE_URL=sqlite:///dev.db
export LOG_LEVEL=DEBUG

# Production
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@host:port/db
export LOG_LEVEL=INFO
```

### **2. Database Migration**
```python
# Run schema migrations
python scripts/migrate_database.py

# Verify schema
python scripts/verify_database_setup.py
```

### **3. Health Monitoring**
```python
# Health check endpoint
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }
```

## 📚 **Best Practices**

### **1. Code Organization**
- **Consistent Naming** - Use clear, descriptive names
- **Documentation** - Document all public methods
- **Type Hints** - Use type hints for better IDE support
- **Error Handling** - Comprehensive error handling

### **2. Performance**
- **Connection Pooling** - Reuse database connections
- **Caching** - Cache frequently accessed data
- **Pagination** - Implement pagination for large datasets
- **Indexing** - Proper database indexing

### **3. Security**
- **Input Validation** - Validate all inputs
- **Output Encoding** - Encode all outputs
- **Least Privilege** - Minimal required permissions
- **Audit Logging** - Log all security events

## 🤝 **Contributing to This Architecture**

### **1. Adding New Models**
1. Create model in `models/` directory
2. Extend `BaseModel` class
3. Add validation rules
4. Create corresponding repository
5. Add business logic in services
6. Create API endpoints
7. Add comprehensive tests

### **2. Adding New Utilities**
1. Create utility in `utils/` directory
2. Follow existing patterns
3. Add type hints
4. Add comprehensive tests
5. Update documentation

### **3. Configuration Changes**
1. Update configuration classes
2. Add environment variable support
3. Update documentation
4. Test in all environments

## 📄 **License**

This architecture is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Clean Architecture** - Robert C. Martin
- **Repository Pattern** - Martin Fowler
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **SQLAlchemy** - Database toolkit

---

**⭐ This architecture serves as a foundation for both the current AASX project and as a template for future mega projects!**

**🔄 For updates and improvements, check our [Changelog](../../CHANGELOG.md).** 