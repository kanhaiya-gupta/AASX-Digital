/**
 * Knowledge Graph Neo4j Module Entry Point
 * Main entry point for Knowledge Graph functionality
 */

// Import shared utilities
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';

// Import Knowledge Graph modules
import KGNeo4jCore from './graph-management/core.js';
import KGQueryEngine from './graph-management/query-engine.js';
import KGVisualization from './graph-management/visualization.js';
import KGDataProcessor from './graph-management/data-processor.js';

// Global instances
let kgNeo4jCore = null;
let kgQueryEngine = null;
let kgVisualization = null;
let kgDataProcessor = null;

/**
 * Initialize Knowledge Graph Module
 * Sets up all Knowledge Graph components and functionality
 */
export async function initKGNeo4jModule() {
    console.log('🚀 Knowledge Graph Neo4j Module initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Knowledge Graph
        kgNeo4jCore = new KGNeo4jCore();
        await kgNeo4jCore.init();
        
        // Initialize Query Engine
        kgQueryEngine = new KGQueryEngine();
        await kgQueryEngine.init();
        
        // Initialize Visualization
        kgVisualization = new KGVisualization();
        await kgVisualization.init();
        
        // Initialize Data Processor
        kgDataProcessor = new KGDataProcessor();
        await kgDataProcessor.init();
        
        console.log('✅ Knowledge Graph Neo4j Module initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('kgNeo4jModuleReady', {
            detail: {
                kgNeo4jCore,
                kgQueryEngine,
                kgVisualization,
                kgDataProcessor
            }
        }));
        
    } catch (error) {
        console.error('❌ Knowledge Graph module initialization failed:', error);
        throw error;
    }
}

/**
 * Get Knowledge Graph Core Instance
 */
export function getKGNeo4jCore() {
    return kgNeo4jCore;
}

/**
 * Get Query Engine Instance
 */
export function getKGQueryEngine() {
    return kgQueryEngine;
}

/**
 * Get Visualization Instance
 */
export function getKGVisualization() {
    return kgVisualization;
}

/**
 * Get Data Processor Instance
 */
export function getKGDataProcessor() {
    return kgDataProcessor;
}

/**
 * Cleanup Knowledge Graph Module
 */
export function cleanupKGNeo4jModule() {
    if (kgNeo4jCore) {
        kgNeo4jCore.destroy();
        kgNeo4jCore = null;
    }
    
    if (kgQueryEngine) {
        kgQueryEngine.destroy();
        kgQueryEngine = null;
    }
    
    if (kgVisualization) {
        kgVisualization.destroy();
        kgVisualization = null;
    }
    
    if (kgDataProcessor) {
        kgDataProcessor.destroy();
        kgDataProcessor = null;
    }
    
    console.log('🧹 Knowledge Graph module cleaned up');
}

/**
 * Check if Knowledge Graph Module is Ready
 */
export function isKGNeo4jModuleReady() {
    return kgNeo4jCore && kgQueryEngine && kgVisualization && kgDataProcessor &&
           kgNeo4jCore.isInitialized && kgQueryEngine.isInitialized && 
           kgVisualization.isInitialized && kgDataProcessor.isInitialized;
}

/**
 * Refresh Knowledge Graph Data
 */
export async function refreshKGNeo4jData() {
    if (kgNeo4jCore) {
        await kgNeo4jCore.refreshData();
    }
    
    if (kgQueryEngine) {
        await kgQueryEngine.refreshQueries();
    }
    
    if (kgVisualization) {
        await kgVisualization.refreshGraph();
    }
    
    if (kgDataProcessor) {
        await kgDataProcessor.refreshData();
    }
}

// Auto-initialize when DOM is ready
$(document).ready(() => {
    // Check if we're on a Knowledge Graph page
    if (window.location.pathname.includes('/kg-neo4j') || 
        window.location.pathname.includes('/knowledge-graph')) {
        initKGNeo4jModule().catch(error => {
            console.error('Failed to initialize Knowledge Graph module:', error);
        });
    }
});

// Export for global access
window.KGNeo4jModule = {
    init: initKGNeo4jModule,
    cleanup: cleanupKGNeo4jModule,
    isReady: isKGNeo4jModuleReady,
    refresh: refreshKGNeo4jData,
    getCore: getKGNeo4jCore,
    getQueryEngine: getKGQueryEngine,
    getVisualization: getKGVisualization,
    getDataProcessor: getKGDataProcessor
};

// Export default
export default {
    init: initKGNeo4jModule,
    cleanup: cleanupKGNeo4jModule,
    isReady: isKGNeo4jModuleReady,
    refresh: refreshKGNeo4jData,
    getCore: getKGNeo4jCore,
    getQueryEngine: getKGQueryEngine,
    getVisualization: getKGVisualization,
    getDataProcessor: getKGDataProcessor
}; 