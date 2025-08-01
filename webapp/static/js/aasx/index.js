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
import DataManager from './data-manager/core.js';
import { AASXETLPipeline } from './etl-pipeline/core.js';
import { dropdownManager } from './shared/dropdown-manager.js';
import ProjectCreator from './project-creator.js';
import FileUploadHandler from './file-upload-handler.js';
console.log('✅ AASX index.js: AASX modules imported');

// Global instances
let dataManager = null;
let aasxETLPipeline = null;
let etlConfigManager = null;
let isInitialized = false;

/**
 * Initialize AASX Module
 * Sets up all AASX components and functionality
 */
export async function initAASXModule() {
    if (isInitialized) {
        console.log('⚠️ AASX module already initialized, skipping...');
        return;
    }
    
    console.log('🚀 AASX Digital Twin Analytics Framework initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Data Manager
        dataManager = new DataManager();
        await dataManager.init();
        
        // Initialize ETL Pipeline
        aasxETLPipeline = new AASXETLPipeline();
        await aasxETLPipeline.init();
        
        // Make ETL pipeline globally accessible for HTML callbacks
        window.aasxETLPipeline = aasxETLPipeline;
        
        // Initialize Dropdown Manager
        await dropdownManager.init();
        
        // Make dropdown manager globally accessible
        window.dropdownManager = dropdownManager;
        
        // Initialize Project Creator
        const projectCreator = new ProjectCreator();
        window.projectCreator = projectCreator;
        
        // Initialize File Upload Handler
        const fileUploadHandler = new FileUploadHandler();
        window.fileUploadHandler = fileUploadHandler;
        
        // Initialize ETL Configuration Manager (lazy load when needed)
        // This will be initialized when the ETL configuration form is accessed
        console.log('ℹ️ ETL Configuration Manager will be initialized when needed');
        
        // Make data manager globally accessible for modal callbacks
        window.dataManager = dataManager;
        
        isInitialized = true;
        console.log('✅ AASX Digital Twin Analytics Framework initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('aasxModuleReady', {
            detail: {
                dataManager,
                aasxETLPipeline
            }
        }));
        
    } catch (error) {
        console.error('❌ AASX module initialization failed:', error);
        throw error;
    }
}

/**
 * Get Data Manager Instance
 */
export function getDataManager() {
    return dataManager;
}

/**
 * Get ETL Pipeline Instance
 */
export function getAASXETLPipeline() {
    return aasxETLPipeline;
}

/**
 * Get ETL Configuration Manager Instance
 */
export function getETLConfigurationManager() {
    return etlConfigManager;
}

/**
 * Initialize ETL Configuration Manager when needed
 */
export async function initETLConfigurationManager() {
    if (etlConfigManager) {
        return etlConfigManager;
    }
    
    try {
        // Check if ETL configuration form exists
        const etlConfigForm = document.getElementById('etlConfigForm');
        if (!etlConfigForm) {
            console.log('⚠️ ETL Configuration form not found');
            return null;
        }
        
        // Dynamically import ETL Configuration Manager
        const { default: ETLConfigurationManager } = await import('./etl-configuration.js');
        
        // Initialize ETL Configuration Manager
        etlConfigManager = new ETLConfigurationManager();
        const initialized = etlConfigManager.init(); // Call the init method
        if (initialized) {
            window.etlConfigManager = etlConfigManager;
            console.log('✅ ETL Configuration Manager initialized');
            return etlConfigManager;
        } else {
            return null;
        }
        
    } catch (error) {
        console.error('❌ Failed to initialize ETL Configuration Manager:', error);
        return null;
    }
}

/**
 * Cleanup AASX Module
 */
export function cleanupAASXModule() {
    if (dataManager) {
        dataManager.destroy();
        dataManager = null;
    }
    
    if (aasxETLPipeline) {
        aasxETLPipeline.destroy();
        aasxETLPipeline = null;
    }
    
    if (dropdownManager) {
        dropdownManager.destroy();
    }
    
    isInitialized = false;
    console.log('🧹 AASX module cleaned up');
}

/**
 * Check if AASX Module is Ready
 */
export function isAASXModuleReady() {
    return dataManager && aasxETLPipeline &&
           dataManager.isInitialized && aasxETLPipeline.isInitialized;
}

/**
 * Refresh AASX Data
 */
export async function refreshAASXData() {
    if (dataManager) {
        await dataManager.loadProjects();
    }
    
    if (aasxETLPipeline) {
        await aasxETLPipeline.refreshFiles();
    }
}

// Auto-initialize when DOM is ready
let autoInitCalled = false;
$(document).ready(() => {
    // Check if we're on an AASX page and not already initialized
    if (window.location.pathname.includes('/aasx') && !autoInitCalled) {
        autoInitCalled = true;
        initAASXModule().catch(error => {
            console.error('Failed to initialize AASX module:', error);
            autoInitCalled = false; // Reset flag on error
        });
    }
});

// Export for global access
window.AASXModule = {
    init: initAASXModule,
    cleanup: cleanupAASXModule,
    isReady: isAASXModuleReady,
    refresh: refreshAASXData,
    getDataManager,
    getAASXETLPipeline
};

// Export default
export default {
    init: initAASXModule,
    cleanup: cleanupAASXModule,
    isReady: isAASXModuleReady,
    refresh: refreshAASXData,
    getDataManager,
    getAASXETLPipeline
};