/**
 * Knowledge Graph Module Entry Point
 * Main entry point for Knowledge Graph functionality
 * Now with modular UI components
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
console.log('✅ Knowledge Graph index.js: KG core modules imported');

// Import UI component modules
console.log('📦 Knowledge Graph index.js: Importing UI component modules...');
import { initSystemStatus } from './ui-components/system_status.js?v=2025-01-27-2';
import { initGraphVisualization, loadGraphData } from './ui-components/graph_visualization.js?v=2025-01-27-2';
import { initQueryInterface } from './ui-components/query_interface.js?v=2025-01-27-2';
import DataManagementComponent from './ui-components/data_management.js?v=2025-01-27-2';
import DockerManagementComponent from './ui-components/docker_management.js?v=2025-01-27-2';
import { initAnalyticsDashboard } from './ui-components/analytics_dashboard.js?v=2025-01-27-2';
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
 */
export async function initKGModule() {
    if (isInitialized) {
        console.log('⚠️ Knowledge Graph module already initialized, skipping...');
        return;
    }
    
    console.log('🚀 Knowledge Graph Module initializing with modular UI components...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Knowledge Graph modules
        kgNeo4jCore = new KGNeo4jCore();
        await kgNeo4jCore.init();
        
        // Note: Using UI component visualization instead of D3-based visualization
        // kgNeo4jVisualization = new KGNeo4jVisualization();
        // await kgNeo4jVisualization.init();
        
        kgNeo4jQueryEngine = new KGNeo4jQueryEngine();
        await kgNeo4jQueryEngine.init();
        
        kgNeo4jDataProcessor = new KGNeo4jDataProcessor();
        await kgNeo4jDataProcessor.init();
        
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
        
        // Load initial graph data
        await loadGraphData();
        
        isInitialized = true;
        console.log('✅ Knowledge Graph Module initialized with all UI components');
        
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
                    analyticsDashboard: true
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

// Initialize module when script loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('📦 Knowledge Graph index.js: DOM ready, initializing module...');
    initKGModule();
}); 