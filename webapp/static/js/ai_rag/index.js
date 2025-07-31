/**
 * AI RAG Module Entry Point
 * Main entry point for AI Retrieval-Augmented Generation functionality
 */

// Import shared utilities
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';

// Import AI RAG modules
import AIRAGCore from './rag-management/core.js';
import AIRAGQueryProcessor from './rag-management/query-processor.js';
import AIRAGVectorStore from './rag-management/vector-store.js';
import AIRAGGenerator from './rag-management/generator.js';

// Global instances
let aiRAGCore = null;
let aiRAGQueryProcessor = null;
let aiRAGVectorStore = null;
let aiRAGGenerator = null;

/**
 * Initialize AI RAG Module
 * Sets up all AI RAG components and functionality
 */
export async function initAIRAGModule() {
    console.log('🚀 AI RAG Module initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core AI RAG
        aiRAGCore = new AIRAGCore();
        await aiRAGCore.init();
        
        // Initialize Query Processor
        aiRAGQueryProcessor = new AIRAGQueryProcessor();
        await aiRAGQueryProcessor.init();
        
        // Initialize Vector Store
        aiRAGVectorStore = new AIRAGVectorStore();
        await aiRAGVectorStore.init();
        
        // Initialize Generator
        aiRAGGenerator = new AIRAGGenerator();
        await aiRAGGenerator.init();
        
        console.log('✅ AI RAG Module initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('aiRAGModuleReady', {
            detail: {
                aiRAGCore,
                aiRAGQueryProcessor,
                aiRAGVectorStore,
                aiRAGGenerator
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
    return aiRAGCore && aiRAGQueryProcessor && aiRAGVectorStore && aiRAGGenerator &&
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
$(document).ready(() => {
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