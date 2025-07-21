import os
import shutil

MODULES = [
    'aasx',
    'twin_registry', 
    'ai_rag',
    'kg_neo4j',
    'certificate_manager',
    'qi_analytics',
    'shared',
    'federated_learning',
]

# Define the file structure for each module
MODULE_FILES = {
    'aasx': {
        '__init__.py': '',
        'routes.py': '# AASX ETL Pipeline Routes\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n',
        'templates/index.html': '<!-- AASX ETL Pipeline Template -->\n{% extends "base.html" %}\n{% block content %}\n<div class="aasx-container">\n    <h1>AASX ETL Pipeline</h1>\n    <!-- Content will be migrated from webapp_old -->\n</div>\n{% endblock %}',
        'static/js/aasx_etl.js': '// AASX ETL JavaScript\nconsole.log("AASX ETL module loaded");\n// Content will be migrated from webapp_old/static/js/aasx_etl.js',
        'static/css/aasx_styles.css': '/* AASX ETL Styles */\n.aasx-container {\n    padding: 20px;\n}\n/* Content will be migrated from webapp_old */'
    },
    'twin_registry': {
        '__init__.py': '',
        'routes.py': '# Twin Registry Routes\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n',
        'templates/index.html': '<!-- Twin Registry Template -->\n{% extends "base.html" %}\n{% block content %}\n<div class="twin-registry-container">\n    <h1>Digital Twin Registry</h1>\n    <!-- Content will be migrated from webapp_old -->\n</div>\n{% endblock %}',
        'templates/analytics/index.html': '<!-- Twin Registry Analytics -->\n{% extends "base.html" %}\n{% block content %}\n<div class="twin-analytics-container">\n    <h1>Twin Analytics</h1>\n    <!-- Analytics content -->\n</div>\n{% endblock %}',
        'static/js/twin_registry.js': '// Twin Registry JavaScript\nconsole.log("Twin Registry module loaded");\n// Content will be migrated from webapp_old/static/js/twin_registry.js',
        'static/js/twin_registry_performance.js': '// Twin Registry Performance JavaScript\nconsole.log("Twin Registry Performance module loaded");\n// Content will be migrated from webapp_old/static/js/twin_registry_performance.js',
        'static/js/analytics_integration.js': '// Analytics Integration JavaScript\nconsole.log("Analytics Integration module loaded");\n// Content will be migrated from webapp_old/static/js/analytics_integration.js',
        'static/css/twin_registry.css': '/* Twin Registry Styles */\n.twin-registry-container {\n    padding: 20px;\n}\n/* Content will be migrated from webapp_old */'
    },
    'ai_rag': {
        '__init__.py': '',
        'routes.py': '# AI/RAG Routes\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n',
        'templates/index.html': '<!-- AI/RAG Template -->\n{% extends "base.html" %}\n{% block content %}\n<div class="ai-rag-container">\n    <h1>AI/RAG System</h1>\n    <!-- Content will be migrated from webapp_old -->\n</div>\n{% endblock %}',
        'static/js/ai_rag.js': '// AI/RAG JavaScript\nconsole.log("AI/RAG module loaded");\n// Content will be migrated from webapp_old/static/js/ai_rag.js',
        'static/css/ai_rag.css': '/* AI/RAG Styles */\n.ai-rag-container {\n    padding: 20px;\n}\n/* Content will be migrated from webapp_old */'
    },
    'kg_neo4j': {
        '__init__.py': '',
        'routes.py': '# Knowledge Graph Routes\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n',
        'templates/index.html': '<!-- Knowledge Graph Template -->\n{% extends "base.html" %}\n{% block content %}\n<div class="kg-neo4j-container">\n    <h1>Knowledge Graph</h1>\n    <!-- Content will be migrated from webapp_old -->\n</div>\n{% endblock %}',
        'templates/visualize.html': '<!-- Knowledge Graph Visualization -->\n{% extends "base.html" %}\n{% block content %}\n<div class="kg-visualize-container">\n    <h1>Graph Visualization</h1>\n    <!-- Content will be migrated from webapp_old -->\n</div>\n{% endblock %}',
        'static/js/kg_neo4j.js': '// Knowledge Graph JavaScript\nconsole.log("Knowledge Graph module loaded");\n// Content will be migrated from webapp_old/static/js/kg_neo4j.js',
        'static/css/kg_neo4j.css': '/* Knowledge Graph Styles */\n.kg-neo4j-container {\n    padding: 20px;\n}\n/* Content will be migrated from webapp_old */'
    },
    'certificate_manager': {
        '__init__.py': '',
        'routes.py': '# Certificate Manager Routes\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n',
        'templates/index.html': '<!-- Certificate Manager Template -->\n{% extends "base.html" %}\n{% block content %}\n<div class="certificate-manager-container">\n    <h1>Certificate Manager</h1>\n    <!-- Content will be migrated from webapp_old -->\n</div>\n{% endblock %}',
        'static/js/certificate_manager.js': '// Certificate Manager JavaScript\nconsole.log("Certificate Manager module loaded");\n// Content will be migrated from webapp_old/static/js/certificate_manager.js',
        'static/css/certificate_manager.css': '/* Certificate Manager Styles */\n.certificate-manager-container {\n    padding: 20px;\n}\n/* Content will be migrated from webapp_old */'
    },
    'qi_analytics': {
        '__init__.py': '',
        'routes.py': '# QI Analytics Routes\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n',
        'templates/index.html': '<!-- QI Analytics Template -->\n{% extends "base.html" %}\n{% block content %}\n<div class="qi-analytics-container">\n    <h1>QI Analytics</h1>\n    <!-- Content will be migrated from webapp_old -->\n</div>\n{% endblock %}',
        'static/js/qi_analytics.js': '// QI Analytics JavaScript\nconsole.log("QI Analytics module loaded");\n// Content will be migrated from webapp_old/static/js/qi_analytics.js',
        'static/css/qi_analytics.css': '/* QI Analytics Styles */\n.qi-analytics-container {\n    padding: 20px;\n}\n/* Content will be migrated from webapp_old */'
    },
    'shared': {
        '__init__.py': '',
        'templates/base.html': '<!-- Base Template -->\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>{% block title %}AASX Digital Twin Analytics{% endblock %}</title>\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/base.css\') }}">\n    {% block extra_css %}{% endblock %}\n</head>\n<body>\n    {% include "components/header.html" %}\n    {% include "components/navigation.html" %}\n    <main>\n        {% block content %}{% endblock %}\n    </main>\n    {% include "components/footer.html" %}\n    <script src="{{ url_for(\'static\', filename=\'js/utils.js\') }}"></script>\n    {% block extra_js %}{% endblock %}\n</body>\n</html>',
        'templates/components/header.html': '<!-- Header Component -->\n<header class="main-header">\n    <div class="header-content">\n        <h1>AASX Digital Twin Analytics Framework</h1>\n    </div>\n</header>',
        'templates/components/navigation.html': '<!-- Navigation Component -->\n<nav class="main-nav">\n    <ul>\n        <li><a href="/aasx">AASX ETL</a></li>\n        <li><a href="/twin-registry">Twin Registry</a></li>\n        <li><a href="/ai-rag">AI/RAG</a></li>\n        <li><a href="/kg-neo4j">Knowledge Graph</a></li>\n        <li><a href="/certificates">Certificates</a></li>\n        <li><a href="/analytics">Analytics</a></li>\n    </ul>\n</nav>',
        'templates/components/footer.html': '<!-- Footer Component -->\n<footer class="main-footer">\n    <p>&copy; 2024 AASX Digital Twin Analytics Framework</p>\n</footer>',
        'static/js/api.js': '// API Utilities\nconst API_BASE = "/api";\n\nasync function apiCall(endpoint, options = {}) {\n    const url = `${API_BASE}${endpoint}`;\n    const response = await fetch(url, {\n        headers: {\n            "Content-Type": "application/json",\n            ...options.headers\n        },\n        ...options\n    });\n    return response.json();\n}\n\n// Content will be migrated from webapp_old/static/js/api.js',
        'static/js/utils.js': '// Utility Functions\nconsole.log("Utils module loaded");\n\n// Common utility functions\nfunction showLoading(element) {\n    element.innerHTML = "<div class=\'loading\'>Loading...</div>";\n}\n\nfunction hideLoading(element) {\n    const loading = element.querySelector(".loading");\n    if (loading) loading.remove();\n}\n\n// Content will be migrated from webapp_old/static/js/utils.js',
        'static/css/base.css': '/* Base Styles */\nbody {\n    margin: 0;\n    padding: 0;\n    font-family: Arial, sans-serif;\n}\n\n.main-header {\n    background: #2c3e50;\n    color: white;\n    padding: 1rem;\n}\n\n.main-nav {\n    background: #34495e;\n    padding: 0.5rem;\n}\n\n.main-nav ul {\n    list-style: none;\n    display: flex;\n    gap: 1rem;\n}\n\n.main-nav a {\n    color: white;\n    text-decoration: none;\n}\n\n/* Content will be migrated from webapp_old/static/css/style.css */',
        'static/css/components.css': '/* Component Styles */\n.loading {\n    text-align: center;\n    padding: 20px;\n}\n\n/* Additional component styles will be migrated from webapp_old */'
    },
    'federated_learning': {
        '__init__.py': '',
        'routes.py': '# Federated Learning Routes\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get("/")\ndef federation_dashboard():\n    return {"message": "Federated Learning Dashboard"}\n',
        'templates/federation_dashboard.html': '<!-- Federated Learning Dashboard -->\n{% extends "base.html" %}\n{% block title %}Federated Learning Dashboard{% endblock %}\n{% block content %}\n<div class="federation-dashboard">\n    <h1>Federated Learning Dashboard</h1>\n    <div class="twin-overview">\n        <h2>Digital Twin Overview</h2>\n        <div class="twin-grid">\n            <!-- Twin 1: Additive Manufacturing (77% Health) -->\n            <div class="twin-card">\n                <h3>Additive Manufacturing</h3>\n                <div class="health-score">77%</div>\n                <div class="optimization-target">Target: 85%</div>\n            </div>\n            <!-- Twin 2: Smart Grid (80.9% Health) -->\n            <div class="twin-card">\n                <h3>Smart Grid Substation</h3>\n                <div class="health-score">80.9%</div>\n                <div class="optimization-target">Target: 85%</div>\n            </div>\n            <!-- Twin 3: Hydrogen Station (80.4% Health) -->\n            <div class="twin-card">\n                <h3>Hydrogen Filling Station</h3>\n                <div class="health-score">80.4%</div>\n                <div class="optimization-target">Target: 85%</div>\n            </div>\n        </div>\n    </div>\n</div>\n{% endblock %}',
        'templates/twin_performance.html': '<!-- Twin Performance Monitoring -->\n{% extends "base.html" %}\n{% block title %}Twin Performance{% endblock %}\n{% block content %}\n<div class="twin-performance">\n    <h1>Twin Performance Monitoring</h1>\n    <div class="performance-metrics">\n        <!-- Real-time performance metrics will be displayed here -->\n    </div>\n</div>\n{% endblock %}',
        'templates/cross_twin_insights.html': '<!-- Cross-Twin Insights -->\n{% extends "base.html" %}\n{% block title %}Cross-Twin Insights{% endblock %}\n{% block content %}\n<div class="cross-twin-insights">\n    <h1>Cross-Twin Learning Insights</h1>\n    <div class="insights-grid">\n        <div class="insight-card">\n            <h3>Manufacturing-Energy Chain</h3>\n            <p>Optimization insights between Additive Manufacturing and Smart Grid</p>\n        </div>\n        <div class="insight-card">\n            <h3>Safety Standards</h3>\n            <p>Cross-domain safety enhancement across all three twins</p>\n        </div>\n        <div class="insight-card">\n            <h3>Efficiency Optimization</h3>\n            <p>15% overall efficiency improvement potential</p>\n        </div>\n    </div>\n</div>\n{% endblock %}',
        'templates/health_optimization.html': '<!-- Health Score Optimization -->\n{% extends "base.html" %}\n{% block title %}Health Optimization{% endblock %}\n{% block content %}\n<div class="health-optimization">\n    <h1>Health Score Optimization</h1>\n    <div class="optimization-targets">\n        <div class="target-card">\n            <h3>Additive Manufacturing</h3>\n            <div class="current">Current: 77%</div>\n            <div class="target">Target: 85%</div>\n            <div class="strategy">Strategy: Quality Control & Efficiency</div>\n        </div>\n        <div class="target-card">\n            <h3>Smart Grid Substation</h3>\n            <div class="current">Current: 80.9%</div>\n            <div class="target">Target: 85%</div>\n            <div class="strategy">Strategy: Resource Efficiency & Stability</div>\n        </div>\n        <div class="target-card">\n            <h3>Hydrogen Filling Station</h3>\n            <div class="current">Current: 80.4%</div>\n            <div class="target">Target: 85%</div>\n            <div class="strategy">Strategy: Safety & Efficiency</div>\n        </div>\n    </div>\n</div>\n{% endblock %}',
        'static/js/federation_dashboard.js': '// Federated Learning Dashboard JavaScript\nconsole.log("Federation Dashboard loaded");\n\nclass FederationDashboard {\n    constructor() {\n        this.twins = [\n            { id: "twin_1", name: "Additive Manufacturing", health: 77.0, target: 85.0 },\n            { id: "twin_2", name: "Smart Grid Substation", health: 80.9, target: 85.0 },\n            { id: "twin_3", name: "Hydrogen Filling Station", health: 80.4, target: 85.0 }\n        ];\n        this.init();\n    }\n\n    init() {\n        this.updateDashboard();\n        this.startRealTimeUpdates();\n    }\n\n    updateDashboard() {\n        // Update dashboard with current twin data\n        console.log("Updating federation dashboard...");\n    }\n\n    startRealTimeUpdates() {\n        // Start real-time updates\n        setInterval(() => {\n            this.updateDashboard();\n        }, 5000);\n    }\n}\n\n// Initialize dashboard\nnew FederationDashboard();',
        'static/js/twin_performance.js': '// Twin Performance Monitoring JavaScript\nconsole.log("Twin Performance module loaded");\n\nclass TwinPerformanceMonitor {\n    constructor() {\n        this.init();\n    }\n\n    init() {\n        this.setupWebSocket();\n        this.startPerformanceTracking();\n    }\n\n    setupWebSocket() {\n        // Setup WebSocket for real-time performance updates\n        console.log("Setting up WebSocket connection...");\n    }\n\n    startPerformanceTracking() {\n        // Start tracking performance metrics\n        console.log("Starting performance tracking...");\n    }\n}\n\n// Initialize performance monitor\nnew TwinPerformanceMonitor();',
        'static/js/real_time_monitoring.js': '// Real-Time Monitoring JavaScript\nconsole.log("Real-time monitoring module loaded");\n\nclass RealTimeMonitor {\n    constructor() {\n        this.connections = new Map();\n        this.init();\n    }\n\n    init() {\n        this.setupConnections();\n        this.startMonitoring();\n    }\n\n    setupConnections() {\n        // Setup connections to all twins\n        console.log("Setting up twin connections...");\n    }\n\n    startMonitoring() {\n        // Start real-time monitoring\n        console.log("Starting real-time monitoring...");\n    }\n}\n\n// Initialize real-time monitor\nnew RealTimeMonitor();',
        'static/css/federation_styles.css': '/* Federated Learning Styles */\n.federation-dashboard {\n    padding: 20px;\n}\n\n.twin-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));\n    gap: 20px;\n    margin-top: 20px;\n}\n\n.twin-card {\n    border: 1px solid #ddd;\n    border-radius: 8px;\n    padding: 20px;\n    background: white;\n    box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n}\n\n.health-score {\n    font-size: 2em;\n    font-weight: bold;\n    color: #2c3e50;\n    margin: 10px 0;\n}\n\n.optimization-target {\n    color: #7f8c8d;\n    font-size: 0.9em;\n}\n\n.insights-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n    gap: 15px;\n    margin-top: 20px;\n}\n\n.insight-card {\n    border: 1px solid #3498db;\n    border-radius: 8px;\n    padding: 15px;\n    background: #ecf0f1;\n}\n\n.optimization-targets {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));\n    gap: 20px;\n    margin-top: 20px;\n}\n\n.target-card {\n    border: 1px solid #e74c3c;\n    border-radius: 8px;\n    padding: 20px;\n    background: #fdf2f2;\n}\n\n.current {\n    color: #e74c3c;\n    font-weight: bold;\n}\n\n.target {\n    color: #27ae60;\n    font-weight: bold;\n}\n\n.strategy {\n    color: #7f8c8d;\n    font-style: italic;\n    margin-top: 10px;\n}'
    }
}

def create_dir(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Created directory: {path}")
    else:
        print(f"📁 Directory exists: {path}")

def create_file(path, content):
    """Create file with content if it doesn't exist"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created file: {path}")
    else:
        print(f"📄 File exists: {path}")

def main():
    """Create the complete webapp structure with files"""
    base = os.path.join(os.path.dirname(__file__), '..', 'webapp')
    
    print("🚀 Creating webapp module structure...")
    print("=" * 50)
    
    # Create module structure and files
    for module, files in MODULE_FILES.items():
        print(f"\n📦 Creating {module} module...")
        module_path = os.path.join(base, module)
        
        # Create module directory
        create_dir(module_path)
        
        # Create files for this module
        for file_path, content in files.items():
            full_path = os.path.join(module_path, file_path)
            create_file(full_path, content)
    
    print("\n" + "=" * 50)
    print("✅ Webapp structure created successfully!")
    print("\n📋 Next steps:")
    print("1. Run the migration script to copy content from webapp_old")
    print("2. Update template references to use new module structure")
    print("3. Test all modules work correctly")
    print("4. Remove webapp_old after successful migration")

if __name__ == "__main__":
    main() 