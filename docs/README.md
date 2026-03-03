# 🏗️ AAS Data Modeling Engine

> **Enterprise-grade Asset Administration Shell (AAS) data modeling and management platform with comprehensive business logic, authentication, and data governance capabilities**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-Modular-orange.svg)](https://github.com/your-repo)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 **What This Engine Provides**

The **AAS Data Modeling Engine** is a comprehensive platform designed for enterprise-scale Asset Administration Shell (AAS) operations, providing:

- **🔧 Core Business Services** - Organizations, projects, files, and workflow management
- **🔐 Authentication & Authorization** - User management, role-based access control, and security
- **📊 Data Governance** - Lineage tracking, quality assessment, change management, versioning, and policy enforcement
- **🤖 AI/ML Integration Ready** - Built-in support for AI, RAG, and specialized processing modules
- **🌐 Scalable Architecture** - Modular design with clean separation of concerns
- **🔒 Enterprise Security** - Comprehensive audit trails, compliance monitoring, and data protection
- **📈 Real-time Monitoring** - Health monitoring, analytics, and performance tracking
- **🧪 Comprehensive Testing** - Unit tests, integration tests, and validation frameworks

## 🏛️ **Architecture Overview**

### **Two-Tier Integration Architecture**

The engine follows a **two-tier integration approach** that separates core business logic from specialized processing modules:

```
src/
├── engine/                          # Core Business Platform
│   ├── services/
│   │   ├── business_domain/        # ✅ COMPLETED
│   │   │   ├── organization_service.py
│   │   │   ├── project_service.py
│   │   │   ├── file_service.py
│   │   │   └── workflow_service.py
│   │   ├── auth/                   # ✅ COMPLETED  
│   │   │   ├── user_service.py
│   │   │   ├── role_service.py
│   │   │   ├── auth_service.py
│   │   │   └── metrics_service.py
│   │   ├── data_governance/        # ✅ COMPLETED
│   │   │   ├── lineage_service.py
│   │   │   ├── quality_service.py
│   │   │   ├── change_service.py
│   │   │   ├── version_service.py
│   │   │   └── policy_service.py
│   │   └── integration/            # Internal Engine Integration
│   │       ├── audit_service.py
│   │       ├── compliance_service.py
│   │       └── workflow_orchestration.py
│   ├── models/                     # Data models and validation
│   ├── repositories/               # Data access layer
│   └── database/                   # Database management
├── modules/                         # Task modules
│   ├── aasx/                       # AASX processing
│   │   ├── models/
│   │   ├── repositories/
│   │   └── services/
│   ├── ai_rag/                     # AI/RAG processing
│   │   ├── models/
│   │   ├── repositories/
│   │   └── services/
│   ├── kg_neo4j/                   # Knowledge graph (Neo4j)
│   │   ├── models/
│   │   ├── repositories/
│   │   └── services/
│   ├── twin_registry/              # Digital twin registry
│   │   ├── models/
│   │   ├── repositories/
│   │   └── services/
│   ├── certificate_manager/        # Certificate management
│   ├── physics_modeling/           # Physics modeling
│   └── federated_learning/         # Federated learning
└── integration/                    # Cross-Module Integration Layer
    ├── module_orchestrator.py      # Coordinates between engine and task modules
    ├── cross_module_workflow.py    # Workflows spanning multiple modules
    ├── unified_api_gateway.py      # Single entry point for all modules
    └── global_monitoring.py        # System-wide monitoring and metrics
```

### **Integration Strategy**

#### **Tier 1: Internal Engine Integration** (`src/engine/services/integration/`)
- **Scope**: Integrate services within the `src/engine/` directory
- **Purpose**: Create a cohesive core business platform
- **Services**: Business domain, authentication, data governance
- **Status**: 🆕 **TO BE IMPLEMENTED**

#### **Tier 2: Cross-Module Integration** (`src/integration/`)
- **Scope**: Integrate `src/engine/` with external task modules
- **Purpose**: Connect core business logic with specialized processing
- **Modules**: aasx, ai_rag, kg_neo4j, twin_registry, etc.
- **Status**: 🆕 **TO BE IMPLEMENTED**

## 📦 **Task Modules**

Specialized processing lives in `src/modules/`. Each module has its own models, repositories, services, and (where needed) core logic and integrations.

| Module | Path | What it does |
|--------|------|--------------|
| **AASX** | `src/modules/aasx/` | AASX file ingestion and ETL. Validates and processes AASX packages, runs extraction/generation workflows, and orchestrates population of AASX-dependent modules (e.g. Twin Registry, AI RAG, KG). |
| **Twin Registry** | `src/modules/twin_registry/` | Digital twin lifecycle, sync, and relationships. Manages twin instances, configuration, and events; provides lifecycle status, sync operations, and real-time monitoring. |
| **KG Neo4j** | `src/modules/kg_neo4j/` | Knowledge graph over AAS/twin data. Neo4j-backed graph management, analytics, and lifecycle; supports extraction/generation workflows and integration with the rest of the platform. |
| **AI RAG** | `src/modules/ai_rag/` | Retrieval-augmented generation and document intelligence. Handles embedding, vector search, LLM-backed generation, document processing (including CAD/code), and graph metadata for knowledge extraction. |
| **Federated Learning** | `src/modules/federated_learning/` | Privacy-preserving distributed ML across twins and organizations. Trains models from data that stays at the source; aggregates only model updates. See [Federated Learning](#-federated-learning) below for details. |
| **Physics Modeling** | `src/modules/physics_modeling/` | Physics and simulation. Plugin-based framework for custom physics types and solvers (e.g. thermal, structural), model creation from twins, and integration with the shared database. |
| **Certificate Manager** | `src/modules/certificate_manager/` | Digital certificate lifecycle and trust. Creates and manages certificates for AAS/digital twin use cases, supports multi-format export (PDF, HTML, JSON, etc.), signing, QR codes, and audit trails. |

## 🚀 **Key Features**

The engine is built for enterprise AAS operations with clear separation between core platform and task modules. Below is what each area provides.

### **🏗️ Modular Architecture**
The codebase is organized so that business logic, data access, and configuration are clearly separated. Components are loosely coupled and easier to test and extend.
- **Clean Architecture** - Separation of concerns with distinct layers
- **Dependency Injection** - Loose coupling between components
- **Repository Pattern** - Abstracted data access layer
- **Service Layer** - Business logic encapsulation
- **Configuration Management** - Environment-specific settings

### **📊 Data Management**
Data is organized in a hierarchy (use cases → projects → files), validated on input, and tracked for lineage and changes. Multiple formats are supported with consistent IDs and audit trails.
- **Multi-Format Support** - Process data into various formats
- **Hierarchical Organization** - Use Cases → Projects → Files structure
- **Unique ID Management** - UUID-based identification with context awareness
- **Data Validation** - Comprehensive input validation and sanitization
- **Audit Trails** - Complete change tracking and history

### **🔐 Enterprise Security**
Access is controlled by roles and permissions; authentication uses JWT. Data is protected in transit and at rest, with sanitization and audit logging for compliance.
- **Role-Based Access Control** - Granular permissions system
- **Authentication & Authorization** - JWT-based security
- **Data Encryption** - At-rest and in-transit encryption
- **Input Sanitization** - Protection against injection attacks
- **Audit Logging** - Security event tracking

### **🤖 AI/ML Ready**
The platform supports RAG, vector search, and federated learning so you can run semantic search and train models across sites without centralizing raw data. Model lifecycle and analytics pipelines are supported.
- **RAG Integration** - Retrieval-Augmented Generation support
- **Vector Databases** - Semantic search capabilities
- **Federated Learning** - Privacy-preserving distributed ML (see [Federated Learning](#-federated-learning) below)
- **Model Management** - AI model versioning and deployment
- **Analytics Pipeline** - Data science workflow support

### **📈 Monitoring & Analytics**
Health, performance, and errors are monitored across the system. Usage and custom dashboards support operations and tuning.
- **Health Monitoring** - System and component health tracking
- **Performance Metrics** - Real-time performance monitoring
- **Error Tracking** - Comprehensive error handling and reporting
- **Usage Analytics** - User behavior and system usage insights
- **Custom Dashboards** - Configurable analytics views

## 🔀 **Federated Learning**

The engine includes a **Federated Learning** task module for **privacy-preserving, distributed machine learning** across digital twins and organizations. Training data stays at each site; only model updates (e.g. gradients or weights) are sent to an aggregator, so multiple parties can improve a shared model without sharing raw data.

### **Role in the framework**
- **Input**: Fed by the **Population Orchestrator** (twin tables and AASX-derived data) after governance and module sync.
- **Output**: Feeds into **Cross-Module Fusion** with other modules (AI RAG, KG Neo4j, Physics Modeling, etc.) for orchestrated workflows and quality assessment.

See the [framework flowchart](docs/framework-flowchart.md) for the full data and control flow.

### **What the module provides**
- **Federation engine & orchestration** – `FederationEngine`, `FederatedLearningService`, and advanced federation orchestration.
- **Local training & aggregation** – `LocalTrainer` for on-site training and `AggregationServer` for secure model aggregation (e.g. FedAvg).
- **Privacy & compliance** – Differential privacy, secure aggregation, privacy preservation and compliance monitoring services.
- **Registry & metrics** – Federated learning registry (45-column schema) and metrics for participation, rounds, and performance.
- **Integrations** – AASX, Twin Registry, AI RAG, KG Neo4j, and Physics Modeling for federation discovery and data preparation.

### **Data sources for federations**
Federations can be created or enriched from:
- **AASX module** – federation opportunities from file/asset analysis  
- **Twin Registry** – federation opportunities from twin analysis  
- **AI RAG** – discovery from knowledge graphs and semantic search  
- **External ML platforms** – federation data from external systems  
- **Manual creation** – user-initiated federation setup  

### **Where it lives**
- **Module**: `src/modules/federated_learning/`
- **Registry & roadmap**: `src/modules/federated_learning/services/README_ROADMAP.md`

## 🛠️ **Technology Stack**

### **Backend Framework**
- **Python 3.8+** - Modern Python with async support
- **SQLite** - Lightweight relational database for development
- **Pydantic** - Data validation using Python type annotations

### **Architecture Patterns**
- **Repository Pattern** - Abstracted data access
- **Service Layer** - Business logic encapsulation
- **Observer Pattern** - Event-driven communication
- **Strategy Pattern** - Configurable business logic
- **Factory Pattern** - Service instantiation management

### **Development & Testing**
- **pytest** - Testing framework
- **asyncio** - Asynchronous programming support
- **logging** - Comprehensive logging system

## 📁 **Project Structure**

```
aas-data-modeling/
├── src/
│   ├── engine/                     # Core Business Platform
│   │   ├── models/                 # Data models
│   │   ├── repositories/           # Data access layer
│   │   ├── services/               # Business logic services
│   │   ├── database/               # Database management
│   │   └── CORE_BUSINESS_LOGIC_PLAN.md
│   ├── modules/                    # Task modules
│   │   ├── aasx/                   # AASX processing
│   │   ├── ai_rag/                 # AI/RAG processing
│   │   ├── kg_neo4j/               # Knowledge graph (Neo4j)
│   │   ├── twin_registry/          # Digital twin registry
│   │   ├── certificate_manager/    # Certificate management
│   │   ├── physics_modeling/       # Physics modeling
│   │   └── federated_learning/     # Federated learning
│   └── integration/                # Cross-module integration
├── scripts/                         # Test and utility scripts
├── tests/                          # Test suites
├── docs/                           # Documentation
└── README.md                       # This file
```

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.8 or higher
- SQLite (for development)
- Git

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd aas-data-modeling

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Running Tests**
```bash
# Run all tests
python scripts/test_data_governance_services.py

# Run specific test suites
python -m pytest tests/
```

## 📋 **Development Roadmap**

### **Immediate Next Steps**
1. **Complete Phase 6A** - Internal engine integration
2. **Implement Task Modules** - Each module with complete architecture
3. **Complete Phase 6B** - Cross-module integration
4. **End-to-End Testing** - Validate complete system integration

### **Long-term Goals**
- **Production Deployment** - Enterprise-grade deployment
- **Performance Optimization** - Scalability and performance tuning
- **Additional Modules** - Expand specialized processing capabilities
- **API Documentation** - Comprehensive API documentation
- **User Interface** - Web-based user interface

## 🤝 **Contributing**

We welcome contributions! Please see our contributing guidelines for details on:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📄 **License**

## 📞 **Support**

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test examples

---

**Note**: This README documents the current state of the AAS Data Modeling Engine. The two-tier integration architecture ensures clean separation between core business logic and specialized processing modules, enabling scalable and maintainable development.
