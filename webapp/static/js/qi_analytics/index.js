/**
 * Quality Intelligence Analytics Module Entry Point
 * Main entry point for QI Analytics functionality
 */

// Import shared utilities
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';

// Import QI Analytics modules
import QIAnalyticsCore from './analytics-management/core.js';
import QIDataProcessor from './analytics-management/data-processor.js';
import QIVisualization from './analytics-management/visualization.js';
import QIReporting from './analytics-management/reporting.js';

// Global instances
let qiAnalyticsCore = null;
let qiDataProcessor = null;
let qiVisualization = null;
let qiReporting = null;

/**
 * Initialize QI Analytics Module
 * Sets up all QI Analytics components and functionality
 */
export async function initQIAnalyticsModule() {
    console.log('🚀 Quality Intelligence Analytics Module initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Analytics
        qiAnalyticsCore = new QIAnalyticsCore();
        await qiAnalyticsCore.init();
        
        // Initialize Data Processor
        qiDataProcessor = new QIDataProcessor();
        await qiDataProcessor.init();
        
        // Initialize Visualization
        qiVisualization = new QIVisualization();
        await qiVisualization.init();
        
        // Initialize Reporting
        qiReporting = new QIReporting();
        await qiReporting.init();
        
        console.log('✅ Quality Intelligence Analytics Module initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('qiAnalyticsModuleReady', {
            detail: {
                qiAnalyticsCore,
                qiDataProcessor,
                qiVisualization,
                qiReporting
            }
        }));
        
    } catch (error) {
        console.error('❌ QI Analytics module initialization failed:', error);
        throw error;
    }
}

/**
 * Get QI Analytics Core Instance
 */
export function getQIAnalyticsCore() {
    return qiAnalyticsCore;
}

/**
 * Get Data Processor Instance
 */
export function getQIDataProcessor() {
    return qiDataProcessor;
}

/**
 * Get Visualization Instance
 */
export function getQIVisualization() {
    return qiVisualization;
}

/**
 * Get Reporting Instance
 */
export function getQIReporting() {
    return qiReporting;
}

/**
 * Cleanup QI Analytics Module
 */
export function cleanupQIAnalyticsModule() {
    if (qiAnalyticsCore) {
        qiAnalyticsCore.destroy();
        qiAnalyticsCore = null;
    }
    
    if (qiDataProcessor) {
        qiDataProcessor.destroy();
        qiDataProcessor = null;
    }
    
    if (qiVisualization) {
        qiVisualization.destroy();
        qiVisualization = null;
    }
    
    if (qiReporting) {
        qiReporting.destroy();
        qiReporting = null;
    }
    
    console.log('🧹 QI Analytics module cleaned up');
}

/**
 * Check if QI Analytics Module is Ready
 */
export function isQIAnalyticsModuleReady() {
    return qiAnalyticsCore && qiDataProcessor && qiVisualization && qiReporting &&
           qiAnalyticsCore.isInitialized && qiDataProcessor.isInitialized && 
           qiVisualization.isInitialized && qiReporting.isInitialized;
}

/**
 * Refresh QI Analytics Data
 */
export async function refreshQIAnalyticsData() {
    if (qiAnalyticsCore) {
        await qiAnalyticsCore.refreshData();
    }
    
    if (qiDataProcessor) {
        await qiDataProcessor.refreshData();
    }
    
    if (qiVisualization) {
        await qiVisualization.refreshCharts();
    }
    
    if (qiReporting) {
        await qiReporting.refreshReports();
    }
}

// Auto-initialize when DOM is ready
$(document).ready(() => {
    // Check if we're on a QI Analytics page
    if (window.location.pathname.includes('/qi-analytics') || 
        window.location.pathname.includes('/analytics')) {
        initQIAnalyticsModule().catch(error => {
            console.error('Failed to initialize QI Analytics module:', error);
        });
    }
});

// Export for global access
window.QIAnalyticsModule = {
    init: initQIAnalyticsModule,
    cleanup: cleanupQIAnalyticsModule,
    isReady: isQIAnalyticsModuleReady,
    refresh: refreshQIAnalyticsData,
    getCore: getQIAnalyticsCore,
    getDataProcessor: getQIDataProcessor,
    getVisualization: getQIVisualization,
    getReporting: getQIReporting
};

// Export default
export default {
    init: initQIAnalyticsModule,
    cleanup: cleanupQIAnalyticsModule,
    isReady: isQIAnalyticsModuleReady,
    refresh: refreshQIAnalyticsData,
    getCore: getQIAnalyticsCore,
    getDataProcessor: getQIDataProcessor,
    getVisualization: getQIVisualization,
    getReporting: getQIReporting
}; 