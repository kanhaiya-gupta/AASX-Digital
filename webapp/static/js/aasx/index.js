/**
 * AASX Module Entry Point
 * Main entry point for AASX Digital Twin Analytics Framework
 * Imports and initializes all AASX components
 */

console.log('📦 AASX index.js: Module loading started...');

// Import shared utilities
console.log('📦 AASX index.js: Importing shared utilities...');
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';
console.log('✅ AASX index.js: Shared utilities imported');

// Import AASX modules
console.log('📦 AASX index.js: Importing AASX modules...');
import ProjectManager from './project-manager/core.js';
import { AASXETLPipeline } from './etl-pipeline/core.js';
console.log('✅ AASX index.js: AASX modules imported');

// Global instances
let projectManager = null;
let aasxETLPipeline = null;

/**
 * Initialize AASX Module
 * Sets up all AASX components and functionality
 */
export async function initAASXModule() {
    console.log('🚀 AASX Digital Twin Analytics Framework initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Project Manager
        projectManager = new ProjectManager();
        await projectManager.init();
        
        // Initialize ETL Pipeline
        aasxETLPipeline = new AASXETLPipeline();
        await aasxETLPipeline.init();
        
        console.log('✅ AASX Digital Twin Analytics Framework initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('aasxModuleReady', {
            detail: {
                projectManager,
                aasxETLPipeline
            }
        }));
        
    } catch (error) {
        console.error('❌ AASX module initialization failed:', error);
        throw error;
    }
}

/**
 * Get Project Manager Instance
 */
export function getProjectManager() {
    return projectManager;
}

/**
 * Get ETL Pipeline Instance
 */
export function getAASXETLPipeline() {
    return aasxETLPipeline;
}

/**
 * Cleanup AASX Module
 */
export function cleanupAASXModule() {
    if (projectManager) {
        projectManager.destroy();
        projectManager = null;
    }
    
    if (aasxETLPipeline) {
        aasxETLPipeline.destroy();
        aasxETLPipeline = null;
    }
    
    console.log('🧹 AASX module cleaned up');
}

/**
 * Check if AASX Module is Ready
 */
export function isAASXModuleReady() {
    return projectManager && aasxETLPipeline && 
           projectManager.isInitialized && aasxETLPipeline.isInitialized;
}

/**
 * Refresh AASX Data
 */
export async function refreshAASXData() {
    if (projectManager) {
        await projectManager.loadProjects();
    }
    
    if (aasxETLPipeline) {
        await aasxETLPipeline.refreshFiles();
    }
}

// Auto-initialize when DOM is ready
$(document).ready(() => {
    // Check if we're on an AASX page
    if (window.location.pathname.includes('/aasx')) {
        initAASXModule().catch(error => {
            console.error('Failed to initialize AASX module:', error);
        });
    }
});

// Export for global access
window.AASXModule = {
    init: initAASXModule,
    cleanup: cleanupAASXModule,
    isReady: isAASXModuleReady,
    refresh: refreshAASXData,
    getProjectManager,
    getAASXETLPipeline
};

// Export default
export default {
    init: initAASXModule,
    cleanup: cleanupAASXModule,
    isReady: isAASXModuleReady,
    refresh: refreshAASXData,
    getProjectManager,
    getAASXETLPipeline
};