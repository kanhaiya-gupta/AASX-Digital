# JavaScript File Organization

## 📁 **Complete Modular Structure (AASX-Style)**

```
webapp/static/js/
├── shared/                          # Shared utilities and components
│   ├── utils.js                     # Common utility functions
│   ├── alerts.js                    # Alert and notification system
│   ├── api.js                       # API communication helpers
│   └── validators.js                # Form validation helpers
├── aasx/                           # AASX module components
│   ├── project-manager/             # Project management functionality
│   │   ├── core.js                  # Main ProjectManager class
│   │   ├── categorization.js        # Project categorization logic
│   │   ├── rendering.js             # UI rendering methods
│   │   ├── file-upload.js           # File upload handlers
│   │   └── stats.js                 # Statistics and dashboard updates
│   ├── etl-pipeline/                # ETL pipeline functionality
│   │   ├── core.js                  # Main AASXETLPipeline class
│   │   ├── progress.js              # Progress tracking and UI updates
│   │   ├── processing.js            # File processing logic
│   │   └── configuration.js         # ETL configuration management
│   └── index.js                     # Main entry point for AASX module
├── auth/                            # Authentication module
│   ├── auth-management/             # Authentication management functionality
│   │   ├── core.js                  # Main AuthCore class
│   │   ├── login.js                 # Login and session management
│   │   ├── profile.js               # User profile management
│   │   └── permissions.js           # User permissions and roles
│   └── index.js                     # Main entry point for Auth module
├── qi_analytics/                    # Quality Intelligence Analytics module
│   ├── analytics-management/        # Analytics management functionality
│   │   ├── core.js                  # Main QIAnalyticsCore class
│   │   ├── data-processor.js        # Data processing and analysis
│   │   ├── visualization.js         # Charts and visualizations
│   │   └── reporting.js             # Report generation
│   └── index.js                     # Main entry point for QI Analytics
├── twin_registry/                   # Twin Registry module
│   ├── registry-management/         # Registry management functionality
│   │   ├── core.js                  # Main TwinRegistryCore class
│   │   ├── health.js                # Health monitoring functionality
│   │   ├── performance.js           # Performance monitoring
│   │   └── realtime.js              # Real-time monitoring
│   └── index.js                     # Main entry point for Twin Registry
├── kg_neo4j/                        # Knowledge Graph Neo4j module
│   ├── graph-management/            # Graph management functionality
│   │   ├── core.js                  # Main KGNeo4jCore class
│   │   ├── query-engine.js          # Query processing engine
│   │   ├── visualization.js         # Graph visualization
│   │   └── data-processor.js        # Data processing for KG
│   └── index.js                     # Main entry point for Knowledge Graph
├── ai_rag/                          # AI RAG module
│   ├── rag-management/              # RAG management functionality
│   │   ├── core.js                  # Main AIRAGCore class
│   │   ├── query-processor.js       # Query processing
│   │   ├── vector-store.js          # Vector storage management
│   │   └── generator.js             # Text generation
│   └── index.js                     # Main entry point for AI RAG
├── certificate_manager/             # Certificate Manager module
│   ├── certificate-management/      # Certificate management functionality
│   │   ├── core.js                  # Main CertificateManagerCore class
│   │   ├── validator.js             # Certificate validation
│   │   ├── storage.js               # Certificate storage
│   │   └── ui.js                    # Certificate UI management
│   └── index.js                     # Main entry point for Certificate Manager
├── physics_modeling/                # Physics modeling module
│   ├── use-cases/                   # Use case management
│   │   ├── core.js                  # Use case management core
│   │   ├── crud.js                  # CRUD operations
│   │   └── ui.js                    # UI interactions
│   └── index.js                     # Main entry point for physics modeling
├── federated_learning/              # Federated Learning module
│   ├── learning-management/         # Learning management functionality
│   │   ├── core.js                  # Main FederatedLearningCore class
│   │   ├── training.js              # Training coordination
│   │   ├── aggregation.js           # Model aggregation
│   │   └── communication.js         # Node communication
│   └── index.js                     # Main entry point for Federated Learning
├── dashboard_builder/               # Dashboard Builder module
│   ├── builder-management/          # Builder management functionality
│   │   ├── core.js                  # Main DashboardBuilderCore class
│   │   ├── widgets.js               # Widget management
│   │   ├── layouts.js               # Layout management
│   │   └── themes.js                # Theme management
│   └── index.js                     # Main entry point for Dashboard Builder
└── [legacy files]                   # Legacy monolithic files (backed up)
```

## 🎯 **Uniform Module Pattern (AASX-Style)**

Each module follows the same structure as AASX:

### **Module Entry Point (`index.js`)**
- Imports shared utilities and sub-modules from management directory
- Manages global instances
- Provides initialization, cleanup, and access functions
- Auto-initializes based on URL path
- Exports for global access

### **Management Directory (`[module]-management/`)**
- Contains all related functionality for the module
- Main class (`core.js`) for primary functionality
- Specialized files for specific features
- Follows same patterns as AASX subdirectories

### **Shared Module (`shared/`)**
Common utilities used across all modules:
- **`utils.js`**: File formatting, validation, DOM utilities
- **`alerts.js`**: Consistent notification system
- **`api.js`**: API communication helpers
- **`validators.js`**: Form validation helpers

## 📋 **Module Organization**

### **Feature Modules**
Each major feature has its own module following AASX pattern:
- **`aasx/`**: AASX ETL Pipeline and Project Management
- **`auth/`**: Authentication, Login, Profile, and Permissions
- **`qi_analytics/`**: Quality Intelligence Analytics
- **`twin_registry/`**: Digital Twin Registry Management
- **`kg_neo4j/`**: Knowledge Graph with Neo4j
- **`ai_rag/`**: AI Retrieval-Augmented Generation
- **`certificate_manager/`**: Certificate Management
- **`physics_modeling/`**: Physics-based Modeling
- **`federated_learning/`**: Federated Learning
- **`dashboard_builder/`**: Dashboard Builder

## 🚀 **Usage Examples**

### **Loading a Module**
```html
<!-- In HTML template -->
<script type="module" src="/static/js/aasx/index.js"></script>
<script type="module" src="/static/js/auth/index.js"></script>
<script type="module" src="/static/js/dashboard_builder/index.js"></script>
```

### **Accessing Module Functions**
```javascript
// Check if module is ready
if (window.AASXModule && window.AASXModule.isReady()) {
    const projectManager = window.AASXModule.getCore();
    // Use module functionality
}

// Or use ES6 imports
import { getProjectManager } from '/static/js/aasx/index.js';
const projectManager = getProjectManager();
```

### **Module Initialization**
```javascript
// Auto-initialization (handled by index.js)
// Modules automatically initialize when their pages are loaded

// Manual initialization
await window.AASXModule.init();
```

## 🔧 **Benefits of This Structure**

1. **✅ Uniformity**: All modules follow the exact same AASX pattern
2. **✅ Modularity**: Clear separation of concerns
3. **✅ Reusability**: Shared utilities across modules
4. **✅ Maintainability**: Smaller, focused files
5. **✅ Scalability**: Easy to add new modules
6. **✅ Performance**: Better caching and loading strategies
7. **✅ Consistency**: Same initialization, cleanup, and access patterns

## 📝 **Migration Guide**

### **From Legacy to Modular**
1. **Backup**: Legacy files are backed up in `backup_old_structure/`
2. **Update HTML**: Replace script tags with ES6 module imports
3. **Test**: Verify functionality with new structure
4. **Cleanup**: Remove old files after successful testing

### **Adding New Modules**
1. Create module directory structure following AASX pattern
2. Create `index.js` as main entry point
3. Create `[module]-management/` directory for all functionality
4. Import shared utilities
5. Add auto-initialization logic
6. Update this README

## 🎯 **Module Status**

- ✅ **AASX Module**: Complete with project management and ETL pipeline
- ✅ **Auth Module**: Structure created for authentication, login, profile, and permissions
- ✅ **QI Analytics Module**: Structure updated to match AASX pattern
- ✅ **Twin Registry Module**: Structure updated to match AASX pattern
- ✅ **Knowledge Graph Module**: Structure updated to match AASX pattern
- ✅ **AI RAG Module**: Structure updated to match AASX pattern
- ✅ **Certificate Manager Module**: Structure updated to match AASX pattern
- ✅ **Dashboard Builder Module**: Structure created for widget, layout, and theme management
- 🔄 **Physics Modeling Module**: Partially complete (use cases)
- 🔄 **Federated Learning Module**: Structure created

---

**Last Updated**: January 2025
**Status**: Uniform AASX-style modular structure established for all major modules including Auth and Dashboard Builder