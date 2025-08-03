/**
 * AI RAG Module Entry Point
 * Main entry point for AI Retrieval-Augmented Generation functionality
 * Now with modular UI components
 */

console.log('📦 AI RAG index.js: Module loading started...');

// Import shared utilities
console.log('📦 AI RAG index.js: Importing shared utilities...');
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';
console.log('✅ AI RAG index.js: Shared utilities imported');

// Import AI RAG core modules
console.log('📦 AI RAG index.js: Importing AI RAG core modules...');
import AIRAGCore from './rag-management/core.js';
import AIRAGQueryProcessor from './rag-management/query-processor.js';
import AIRAGVectorStore from './rag-management/vector-store.js';
import AIRAGGenerator from './rag-management/generator.js';
console.log('✅ AI RAG index.js: AI RAG core modules imported');

// Import UI component modules
console.log('📦 AI RAG index.js: Importing UI component modules...');
import { initSystemStatus } from './ui-components/system_status.js?v=2025-08-03-09-26';
import { initQueryInterface } from './ui-components/query_interface.js?v=2025-08-03-09-29';
import { initQuickActions } from './ui-components/quick_actions.js?v=2025-08-03-09-26';
import { initStatistics } from './ui-components/statistics.js?v=2025-08-03-09-26';
import { initVectorManagement } from './ui-components/vector_management.js?v=2025-08-03-09-26';
import { initIntegration } from './ui-components/integration.js?v=2025-08-03-09-30';
console.log('✅ AI RAG index.js: UI component modules imported');

// Global instances
let aiRAGCore = null;
let aiRAGQueryProcessor = null;
let aiRAGVectorStore = null;
let aiRAGGenerator = null;
let isInitialized = false;

/**
 * Initialize AI RAG Module
 * Sets up all AI RAG components and functionality including modular UI components
 */
export async function initAIRAGModule() {
    if (isInitialized) {
        console.log('⚠️ AI RAG module already initialized, skipping...');
        return;
    }
    
    console.log('🚀 AI RAG Module initializing with modular UI components...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core AI RAG modules
        aiRAGCore = new AIRAGCore();
        await aiRAGCore.init();
        
        aiRAGQueryProcessor = new AIRAGQueryProcessor();
        await aiRAGQueryProcessor.init();
        
        aiRAGVectorStore = new AIRAGVectorStore();
        await aiRAGVectorStore.init();
        
        aiRAGGenerator = new AIRAGGenerator();
        await aiRAGGenerator.init();
        
        // Make core modules globally accessible for HTML callbacks
        window.aiRAGCore = aiRAGCore;
        window.aiRAGQueryProcessor = aiRAGQueryProcessor;
        window.aiRAGVectorStore = aiRAGVectorStore;
        window.aiRAGGenerator = aiRAGGenerator;
        
        // Initialize UI component modules
        console.log('🔧 Initializing UI component modules...');
        
        await initSystemStatus();
        await initQueryInterface();
        await initQuickActions();
        await initStatistics();
        await initVectorManagement();
        await initIntegration();
        
        isInitialized = true;
        console.log('✅ AI RAG Module initialized with all UI components');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('aiRAGModuleReady', {
            detail: {
                aiRAGCore,
                aiRAGQueryProcessor,
                aiRAGVectorStore,
                aiRAGGenerator,
                uiComponents: {
                    systemStatus: true,
                    queryInterface: true,
                    quickActions: true,
                    statistics: true,
                    vectorManagement: true,
                    integration: true
                }
            }
        }));
        
    } catch (error) {
        console.error('❌ AI RAG module initialization failed:', error);
        throw error;
    }
}

/**
 * Get AI RAG Core Instance
 */
export function getAIRAGCore() {
    return aiRAGCore;
}

/**
 * Get Query Processor Instance
 */
export function getAIRAGQueryProcessor() {
    return aiRAGQueryProcessor;
}

/**
 * Get Vector Store Instance
 */
export function getAIRAGVectorStore() {
    return aiRAGVectorStore;
}

/**
 * Get Generator Instance
 */
export function getAIRAGGenerator() {
    return aiRAGGenerator;
}

/**
 * Cleanup AI RAG Module
 */
export function cleanupAIRAGModule() {
    if (aiRAGCore) {
        aiRAGCore.destroy();
        aiRAGCore = null;
    }
    
    if (aiRAGQueryProcessor) {
        aiRAGQueryProcessor.destroy();
        aiRAGQueryProcessor = null;
    }
    
    if (aiRAGVectorStore) {
        aiRAGVectorStore.destroy();
        aiRAGVectorStore = null;
    }
    
    if (aiRAGGenerator) {
        aiRAGGenerator.destroy();
        aiRAGGenerator = null;
    }
    
    console.log('🧹 AI RAG module cleaned up');
}

/**
 * Check if AI RAG Module is Ready
 */
export function isAIRAGModuleReady() {
    return isInitialized && aiRAGCore && aiRAGQueryProcessor && aiRAGVectorStore && aiRAGGenerator &&
           aiRAGCore.isInitialized && aiRAGQueryProcessor.isInitialized && 
           aiRAGVectorStore.isInitialized && aiRAGGenerator.isInitialized;
}

/**
 * Refresh AI RAG Data
 */
export async function refreshAIRAGData() {
    if (aiRAGCore) {
        await aiRAGCore.refreshData();
    }
    
    if (aiRAGQueryProcessor) {
        await aiRAGQueryProcessor.refreshQueries();
    }
    
    if (aiRAGVectorStore) {
        await aiRAGVectorStore.refreshVectors();
    }
    
    if (aiRAGGenerator) {
        await aiRAGGenerator.refreshModels();
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on an AI RAG page
    if (window.location.pathname.includes('/ai-rag') || 
        window.location.pathname.includes('/rag')) {
        initAIRAGModule().catch(error => {
            console.error('Failed to initialize AI RAG module:', error);
        });
    }
});

// Export for global access
window.AIRAGModule = {
    init: initAIRAGModule,
    cleanup: cleanupAIRAGModule,
    isReady: isAIRAGModuleReady,
    refresh: refreshAIRAGData,
    getCore: getAIRAGCore,
    getQueryProcessor: getAIRAGQueryProcessor,
    getVectorStore: getAIRAGVectorStore,
    getGenerator: getAIRAGGenerator
};

// Export default
export default {
    init: initAIRAGModule,
    cleanup: cleanupAIRAGModule,
    isReady: isAIRAGModuleReady,
    refresh: refreshAIRAGData,
    getCore: getAIRAGCore,
    getQueryProcessor: getAIRAGQueryProcessor,
    getVectorStore: getAIRAGVectorStore,
    getGenerator: getAIRAGGenerator
}; 