/**
 * Knowledge Graph Module Entry Point
 * Main entry point for Knowledge Graph functionality
 * Now with modular UI components and full authentication integration
 */

console.log('📦 Knowledge Graph index.js: Module loading started...');

// Import shared utilities
console.log('📦 Knowledge Graph index.js: Importing shared utilities...');
import { initAlertSystem, showAlert } from '/static/js/shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '/static/js/shared/utils.js';
console.log('✅ Knowledge Graph index.js: Shared utilities imported');

// Import Knowledge Graph core modules
console.log('📦 Knowledge Graph index.js: Importing KG core modules...');
import KGNeo4jCore from './graph-management/core.js?v=2025-01-27-2';
// Note: Using UI component visualization instead of D3-based visualization
// import KGNeo4jVisualization from './graph-management/visualization.js?v=2025-01-27-2';
import KGNeo4jQueryEngine from './graph-management/query-engine.js?v=2025-01-27-2';
import KGNeo4jDataProcessor from './graph-management/data-processor.js?v=2025-01-27-2';
import { graphManagement } from './graph-management/graph-management.js?v=2025-01-27-2';
import { kgAnalytics } from './analytics.js?v=2025-01-27-1';
console.log('✅ Knowledge Graph index.js: KG core modules imported');

// Import UI component modules
console.log('📦 Knowledge Graph index.js: Importing UI component modules...');
import { initSystemStatus } from './ui-components/system_status.js?v=2025-01-27-2';
import { initGraphVisualization, loadGraphData } from './ui-components/graph_visualization.js?v=2025-01-27-2';
import { initQueryInterface } from './ui-components/query_interface.js?v=2025-01-27-2';
import DataManagementComponent from './ui-components/data_management.js?v=2025-01-27-2';
import DockerManagementComponent from './ui-components/docker_management.js?v=2025-01-27-2';
import { initAnalyticsDashboard } from './ui-components/analytics_dashboard.js?v=2025-01-27-2';
import { KGAIInsightsComponent } from './ui-components/ai_insights.js?v=2025-01-27-1';
import { KGIntegrationComponent } from './ui-components/integration.js?v=2025-01-27-1';

// Import Neo4j OPS module
console.log('📦 Knowledge Graph index.js: Importing Neo4j OPS module...');
import { Neo4jOpsManager } from './neo4j_ops.js?v=2025-01-27-1';
console.log('✅ Knowledge Graph index.js: Neo4j OPS module imported');

// Import Advanced Operations module
console.log('📦 Knowledge Graph index.js: Importing Advanced Operations module...');
import { AdvancedOperationsManager } from './advanced.js?v=2025-01-27-1';
console.log('✅ Knowledge Graph index.js: Advanced Operations module imported');

console.log('✅ Knowledge Graph index.js: UI component modules imported');

// Global instances
let kgNeo4jCore = null;
let kgNeo4jVisualization = null;
let kgNeo4jQueryEngine = null;
let kgNeo4jDataProcessor = null;
let isInitialized = false;

/**
 * Initialize Knowledge Graph Module
 * Sets up all Knowledge Graph components and functionality including modular UI components
 * Now with full authentication integration
 */
export async function initKGModule() {
    if (isInitialized) {
        console.log('⚠️ Knowledge Graph module already initialized, skipping...');
        return;
    }
    
    console.log('🚀 Knowledge Graph Module initializing with modular UI components and authentication...');
    
    try {
        // 🔐 CRITICAL: Wait for authentication system to be ready
        console.log('🔐 Knowledge Graph Module: Waiting for authentication system...');
        await new Promise((resolve) => {
            if (window.authSystemReady && window.authManager) {
                console.log('🔐 Knowledge Graph Module: Auth system already ready');
                resolve();
                return;
            }
            
            const handleReady = () => {
                console.log('🚀 Knowledge Graph Module: Auth system ready event received');
                window.removeEventListener('authSystemReady', handleReady);
                resolve();
            };
            
            window.addEventListener('authSystemReady', handleReady);
            
            // Fallback: check periodically
            const checkInterval = setInterval(() => {
                if (window.authSystemReady && window.authManager) {
                    clearInterval(checkInterval);
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                window.removeEventListener('authSystemReady', handleReady);
                console.warn('⚠️ Knowledge Graph Module: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
        
        console.log('🔐 Knowledge Graph Module: Authentication system ready, proceeding with initialization...');
        
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Knowledge Graph modules
        try {
            kgNeo4jCore = new KGNeo4jCore();
            await kgNeo4jCore.init();
            console.log('✅ Knowledge Graph Core initialized successfully');
        } catch (error) {
            console.warn('⚠️ Knowledge Graph Core initialization failed, continuing with other modules:', error);
        }
        
        // Note: Using UI component visualization instead of D3-based visualization
        // kgNeo4jVisualization = new KGNeo4jVisualization();
        // await kgNeo4jVisualization.init();
        
        try {
            kgNeo4jQueryEngine = new KGNeo4jQueryEngine();
            await kgNeo4jQueryEngine.init();
            console.log('✅ Knowledge Graph Query Engine initialized successfully');
        } catch (error) {
            console.warn('⚠️ Knowledge Graph Query Engine initialization failed, continuing with other modules:', error);
        }
        
        try {
            kgNeo4jDataProcessor = new KGNeo4jDataProcessor();
            await kgNeo4jDataProcessor.init();
            console.log('✅ Knowledge Graph Data Processor initialized successfully');
        } catch (error) {
            console.warn('⚠️ Knowledge Graph Data Processor initialization failed, continuing with other modules:', error);
        }
        
        // Make core modules globally accessible for HTML callbacks
        window.kgNeo4jCore = kgNeo4jCore;
        // Note: Using UI component visualization instead of D3-based visualization
        // window.kgNeo4jVisualization = kgNeo4jVisualization;
        window.kgNeo4jQueryEngine = kgNeo4jQueryEngine;
        window.kgNeo4jDataProcessor = kgNeo4jDataProcessor;
        
        // Initialize UI component modules
        console.log('🔧 Initializing UI component modules...');
        
        await initSystemStatus();
        await initGraphVisualization();
        await initQueryInterface();
        // Initialize Data Management Component
        window.dataManagementComponent = new DataManagementComponent();
        
        // Initialize Docker Management Component
        window.dockerManagementComponent = new DockerManagementComponent();
        await initAnalyticsDashboard();
        
        // Initialize Neo4j OPS Manager
        console.log('🔧 Initializing Neo4j OPS Manager...');
        try {
            window.neo4jOpsManager = new Neo4jOpsManager();
            console.log('✅ Neo4j OPS Manager initialized successfully');
        } catch (error) {
            console.warn('⚠️ Neo4j OPS Manager initialization failed, continuing with other modules:', error);
        }
        
        // Initialize Advanced Operations Manager
        console.log('🔧 Initializing Advanced Operations Manager...');
        try {
            window.advancedOperationsManager = new AdvancedOperationsManager();
            console.log('✅ Advanced Operations Manager initialized successfully');
        } catch (error) {
            console.warn('⚠️ Advanced Operations Manager initialization failed, continuing with other modules:', error);
        }
        
        // Initialize graph management with authentication
        if (window.authManager) {
            await graphManagement.initialize(window.authManager);
            console.log('✅ Graph management initialized with authentication');
            
            await kgAnalytics.initialize(window.authManager);
            console.log('✅ Analytics initialized with authentication');
        } else {
            console.warn('⚠️ Auth manager not available, graph management and analytics will initialize later');
        }
        
        // Load initial graph data
        await loadGraphData();
        
        // 🔐 CRITICAL FIX: Populate global window.kgModules for post-login orchestrator
        if (window.kgModules) {
            window.kgModules.dataManagement = window.dataManagementComponent;
            window.kgModules.analyticsDashboard = window.analyticsDashboard;
            window.kgModules.graphVisualization = window.graphVisualization;
            window.kgModules.queryInterface = window.queryInterface;
                window.kgModules.systemStatus = window.systemStatus;
                window.kgModules.dockerManagement = window.dockerManagementComponent;
                window.kgModules.neo4jOps = window.neo4jOpsManager;
                window.kgModules.advancedOperations = window.advancedOperationsManager;
            console.log('✅ Knowledge Graph Module: Populated window.kgModules for post-login orchestrator');
        }
        
        // Mark as initialized if at least the core module is working
        isInitialized = true;
        console.log('✅ Knowledge Graph Module initialized with authentication (some backend services may be unavailable)');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('kgModuleReady', {
            detail: {
                kgNeo4jCore,
                // Note: Using UI component visualization instead of D3-based visualization
                // kgNeo4jVisualization,
                kgNeo4jQueryEngine,
                kgNeo4jDataProcessor,
                uiComponents: {
                    systemStatus: true,
                    graphVisualization: true,
                    queryInterface: true,
                        dataManagement: true,
                        dockerManagement: true,
                        analyticsDashboard: true,
                        neo4jOps: true,
                        advancedOperations: true
                },
                authentication: {
                    isAuthenticated: kgNeo4jCore.isAuthenticated,
                    currentUser: kgNeo4jCore.currentUser,
                    organizationId: kgNeo4jCore.organizationId
                }
            }
        }));
        
    } catch (error) {
        console.error('❌ Knowledge Graph Module initialization failed:', error);
        showAlert('Knowledge Graph Module failed to initialize', 'error');
    }
}

// Export getter functions for external access
export function getKGNeo4jCore() {
    return kgNeo4jCore;
}

// Note: Using UI component visualization instead of D3-based visualization
// export function getKGNeo4jVisualization() {
//     return kgNeo4jVisualization;
// }

export function getKGNeo4jQueryEngine() {
    return kgNeo4jQueryEngine;
}

export function getKGNeo4jDataProcessor() {
    return kgNeo4jDataProcessor;
}

export function cleanupKGModule() {
    console.log('🧹 Cleaning up Knowledge Graph Module...');
    
    try {
        // Cleanup core modules
        if (kgNeo4jCore) {
            kgNeo4jCore.cleanup();
        }
        // Note: Using UI component visualization instead of D3-based visualization
        // if (kgNeo4jVisualization) {
        //     kgNeo4jVisualization.cleanup();
        // }
        if (kgNeo4jQueryEngine) {
            kgNeo4jQueryEngine.cleanup();
        }
        if (kgNeo4jDataProcessor) {
            kgNeo4jDataProcessor.cleanup();
        }
        
        // Cleanup Neo4j OPS Manager
        if (window.neo4jOpsManager) {
            window.neo4jOpsManager.destroy();
            window.neo4jOpsManager = null;
        }
        
        // Cleanup Advanced Operations Manager
        if (window.advancedOperationsManager) {
            window.advancedOperationsManager.destroy();
            window.advancedOperationsManager = null;
        }
        
        // Reset global instances
        kgNeo4jCore = null;
        // Note: Using UI component visualization instead of D3-based visualization
        // kgNeo4jVisualization = null;
        kgNeo4jQueryEngine = null;
        kgNeo4jDataProcessor = null;
        isInitialized = false;
        
        console.log('✅ Knowledge Graph Module cleanup completed');
        
    } catch (error) {
        console.error('❌ Knowledge Graph Module cleanup failed:', error);
    }
}

export function isKGModuleReady() {
    return isInitialized;
}

export async function refreshKGData() {
    console.log('🔄 Refreshing Knowledge Graph data...');
    
    try {
        await loadGraphData();
        console.log('✅ Knowledge Graph data refreshed');
    } catch (error) {
        console.error('❌ Failed to refresh Knowledge Graph data:', error);
    }
}

// 🔐 CRITICAL FIX: Don't auto-initialize - wait for post-login orchestrator
// This prevents the 500 errors by ensuring services are initialized after auth is ready
console.log('📦 Knowledge Graph index.js: Module loaded, waiting for post-login orchestration...');

// Export global function for post-login orchestrator
window.initializeKGIfNeeded = async function() {
    console.log('🚀 Knowledge Graph Module: Post-login initialization triggered...');
    
    if (isInitialized) {
        console.log('⚠️ Knowledge Graph Module already initialized, skipping...');
        return;
    }
    
    try {
        await initKGModule();
        console.log('✅ Knowledge Graph Module: Post-login initialization completed');
    } catch (error) {
        console.error('❌ Knowledge Graph Module: Post-login initialization failed:', error);
        throw error;
    }
};

// Export graph management functions globally for HTML templates
window.refreshKnowledgeGraphData = () => graphManagement.refreshKnowledgeGraphData();
window.exportKnowledgeGraphData = () => graphManagement.exportKnowledgeGraphData();
window.kgShowRelationshipModal = (graphId) => graphManagement.kgShowRelationshipModal(graphId);
window.kgShowRelationships = (graphId) => graphManagement.kgShowRelationships(graphId);
window.kgViewGraphDetails = (graphId) => graphManagement.kgViewGraphDetails(graphId);
window.kgEditGraph = (graphId) => graphManagement.kgEditGraph(graphId);
window.kgSaveAllConfigurations = () => graphManagement.kgSaveAllConfigurations();
window.kgResetToDefaults = () => graphManagement.kgResetToDefaults();
window.handleKGConfigurationTabClick = (event) => graphManagement.handleKGConfigurationTabClick(event);

// Make graph management instance available globally
window.graphManagement = graphManagement;

// Analytics functions
window.kgGenerateAnalyticsReport = () => kgAnalytics.generateAnalyticsReport();
window.kgExportAnalyticsData = () => kgAnalytics.exportAnalyticsData();
window.kgRefreshChart = (chartType) => kgAnalytics.refreshChart(chartType);
window.kgGenerateBusinessReport = () => kgAnalytics.generateBusinessReport();
window.kgAnalytics = kgAnalytics; // Make instance globally available

// Also export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initializeKGIfNeeded };
} 