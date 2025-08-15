/**
 * AASX Module Entry Point
 * Main entry point for AASX Digital Twin Analytics Framework
 * Imports and initializes all AASX components
 * 
 * Phase 5.2: Frontend Data Integration - Analytics modules added
 */

console.log('📦 AASX index.js: Module loading started...');

// Import shared utilities
console.log('📦 AASX index.js: Importing shared utilities...');
import { initAlertSystem } from '/static/js/shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '/static/js/shared/utils.js';
console.log('✅ AASX index.js: Shared utilities imported');

// Import AASX modules
console.log('📦 AASX index.js: Importing AASX modules...');
import { DataManager } from './data-manager/core.js';
import { AASXETLPipeline } from './etl-pipeline/core.js';
import { dropdownManager } from './shared/dropdown-manager.js';
import ProjectCreator from './data-manager/project-creator.js';
import AasxFileUploadManager from './file-upload/core.js';
console.log('✅ AASX index.js: AASX modules imported');

// Import Analytics modules for Phase 5.2
console.log('📦 AASX index.js: Importing Analytics modules for Phase 5.2...');
import './analytics/analytics-api.js';
import './analytics/dashboard-stats.js';
import './analytics/analytics-charts.js';
console.log('✅ AASX index.js: Analytics modules imported');

// Global instances
let dataManager = null;
let aasxETLPipeline = null;
let etlConfigManager = null;
let dashboardStats = null;
let analyticsCharts = null;
let isInitialized = false;

/**
 * Initialize AASX Module
 * Sets up all AASX components and functionality
 */
export async function initAASXModule() {
    if (isInitialized) {
        console.log('⚠️ AASX module already initialized, skipping...');
        return window.aasxModules;
    }
    
    // Prevent multiple simultaneous initializations
    if (window.aasxInitializationInProgress) {
        console.log('⚠️ AASX module initialization already in progress, waiting...');
        // Wait for initialization to complete
        while (window.aasxInitializationInProgress) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        return window.aasxModules;
    }
    
    window.aasxInitializationInProgress = true;
    console.log('🚀 AASX Digital Twin Analytics Framework initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Data Manager
        dataManager = new DataManager();
        await dataManager.init();
        
        // Initialize Dropdown Manager FIRST (before ETL Pipeline)
        await dropdownManager.init();
        
        // Make dropdown manager globally accessible
        window.dropdownManager = dropdownManager;
        
        // Initialize ETL Pipeline (now dropdown manager is ready)
        aasxETLPipeline = new AASXETLPipeline();
        await aasxETLPipeline.init();
        
        // Make ETL pipeline globally accessible for HTML callbacks
        window.aasxETLPipeline = aasxETLPipeline;
        
        // Initialize Project Creator
        const projectCreator = new ProjectCreator();
        window.projectCreator = projectCreator;
        
        // Initialize File Upload Manager and wait for it to be ready
        const fileUploadManager = new AasxFileUploadManager();
        await fileUploadManager.init();
        window.fileUploadManager = fileUploadManager;
        
        // Initialize Analytics modules for Phase 5.2
        console.log('📊 Initializing Analytics modules for Phase 5.2...');
        
        // Initialize Dashboard Stats
        dashboardStats = new window.DashboardStats();
        await dashboardStats.init();
        window.dashboardStats = dashboardStats;
        
        // Initialize Analytics Charts
        analyticsCharts = new window.AnalyticsCharts();
        await analyticsCharts.init();
        window.analyticsCharts = analyticsCharts;
        
        console.log('✅ Analytics modules initialized for Phase 5.2');
        
        // Initialize ETL Configuration Manager (lazy load when needed)
        // This will be initialized when the ETL configuration form is accessed
        console.log('ℹ️ ETL Configuration Manager will be initialized when needed');
        
        // Make data manager globally accessible for modal callbacks
        window.dataManager = dataManager;
        
        // 🚫 CRITICAL FIX: Create window.aasxModules object for PostLoginOrchestrator
        window.aasxModules = {
            dataManager: dataManager,
            etlPipeline: aasxETLPipeline,
            dropdownManager: dropdownManager,
            projectCreator: projectCreator,
            fileUploadManager: fileUploadManager,
            dashboardStats: dashboardStats,
            analyticsCharts: analyticsCharts
        };
        
        isInitialized = true;
        console.log('✅ AASX Digital Twin Analytics Framework initialized');
        console.log('📦 AASX index.js: window.aasxModules created:', window.aasxModules);
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('aasxModuleReady', {
            detail: {
                dataManager,
                aasxETLPipeline,
                aasxModules: window.aasxModules
            }
        }));
        
    } catch (error) {
        console.error('❌ AASX module initialization failed:', error);
        throw error;
    } finally {
        // Always clear the initialization in progress flag
        window.aasxInitializationInProgress = false;
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
 * Get Dashboard Stats Instance
 */
export function getDashboardStats() {
    return dashboardStats;
}

/**
 * Get Analytics Charts Instance
 */
export function getAnalyticsCharts() {
    return analyticsCharts;
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
        const { default: ETLConfigurationManager } = await import('./etl-pipeline/etl_configuration.js');
        
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
    
    if (dashboardStats) {
        dashboardStats.destroy();
        dashboardStats = null;
    }
    
    if (analyticsCharts) {
        analyticsCharts.destroy();
        analyticsCharts = null;
    }
    
    isInitialized = false;
    window.aasxInitializationInProgress = false;
    console.log('🧹 AASX module cleaned up');
}

/**
 * Check if AASX Module is Ready
 */
export function isAASXModuleReady() {
    return dataManager && aasxETLPipeline &&
           dataManager.isInitialized && aasxETLPipeline.isInitialized &&
           dashboardStats && analyticsCharts &&
           dashboardStats.isInitialized && analyticsCharts.isInitialized;
}

/**
 * Refresh AASX Data
 */
export async function refreshAASXData() {
    if (dataManager) {
        await dataManager.loadProjects();
    }
    
    if (dashboardStats) {
        await dashboardStats.refreshDashboard();
    }
    
    if (analyticsCharts) {
        await analyticsCharts.refreshAnalytics();
    }
}

// Auto-initialize when DOM is ready
let autoInitCalled = false;
let initializationInProgress = false;

function initializeWhenReady() {
    // 🚫 CRITICAL FIX: Initialize on any page, not just /aasx pages
    // This ensures PostLoginOrchestrator can access AASX modules from auth pages
    if (!autoInitCalled && !initializationInProgress) {
        autoInitCalled = true;
        initializationInProgress = true;
        console.log('🚀 AASX index.js: Auto-initializing AASX module...');
        initAASXModule().then(() => {
            initializationInProgress = false;
        }).catch(error => {
            console.error('❌ AASX index.js: Failed to initialize AASX module:', error);
            autoInitCalled = false; // Reset flag on error
            initializationInProgress = false;
        });
    }
}

// Try to initialize when DOM is ready
if (typeof $ !== 'undefined') {
    // jQuery is available, use it
    $(document).ready(initializeWhenReady);
} else {
    // jQuery not available, use native DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeWhenReady);
    } else {
        // DOM is already ready
        initializeWhenReady();
    }
}

// Export for global access
window.AASXModule = {
    init: initAASXModule,
    cleanup: cleanupAASXModule,
    isReady: isAASXModuleReady,
    refresh: refreshAASXData,
    getDataManager,
    getAASXETLPipeline
};

// 🚫 CRITICAL FIX: Make AASX modules globally accessible for PostLoginOrchestrator
window.initializeAASXIfNeeded = async () => {
    if (!isInitialized) {
        console.log('🚀 AASX index.js: Manual initialization requested...');
        await initAASXModule();
    }
    return window.aasxModules;
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