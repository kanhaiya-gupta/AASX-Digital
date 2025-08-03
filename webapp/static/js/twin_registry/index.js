/**
 * Twin Registry Module Entry Point
 * Main entry point for Twin Registry functionality
 */

// Import shared utilities
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';

// Import Twin Registry modules
import TwinRegistryCore from './registry-management/core.js';
import TwinRegistryHealth from './registry-management/health.js';
import TwinRegistryPerformance from './registry-management/performance.js';
import TwinRegistryRealtime from './registry-management/realtime.js';
import TwinRegistryUIUpdater from './registry-management/ui-updater.js';
import TwinRegistryChartUpdater from './registry-management/chart-updater.js';

// Global instances
let twinRegistryCore = null;
let twinRegistryHealth = null;
let twinRegistryPerformance = null;
let twinRegistryRealtime = null;
let twinRegistryUIUpdater = null;
let twinRegistryChartUpdater = null;

/**
 * Initialize Twin Registry Module
 * Sets up all Twin Registry components and functionality
 */
export async function initTwinRegistryModule() {
    console.log('🚀 Twin Registry Module initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Registry
        twinRegistryCore = new TwinRegistryCore();
        await twinRegistryCore.init();
        
        // Initialize Health Monitoring
        twinRegistryHealth = new TwinRegistryHealth();
        await twinRegistryHealth.init();
        
        // Initialize Performance Monitoring
        twinRegistryPerformance = new TwinRegistryPerformance();
        await twinRegistryPerformance.init();
        
        // Initialize Real-time Monitoring
        twinRegistryRealtime = new TwinRegistryRealtime();
        await twinRegistryRealtime.init();
        
        // Initialize UI Updater
        twinRegistryUIUpdater = new TwinRegistryUIUpdater();
        await twinRegistryUIUpdater.init();
        
        // Initialize Chart Updater
        twinRegistryChartUpdater = new TwinRegistryChartUpdater();
        await twinRegistryChartUpdater.init();
        
        console.log('✅ Twin Registry Module initialized');
        
        // Make instances available globally
        window.twinRegistryCore = twinRegistryCore;
        window.twinRegistryHealth = twinRegistryHealth;
        window.twinRegistryPerformance = twinRegistryPerformance;
        window.twinRegistryRealtime = twinRegistryRealtime;
        window.twinRegistryUIUpdater = twinRegistryUIUpdater;
        window.twinRegistryChartUpdater = twinRegistryChartUpdater;
        
        // Add window resize listener for chart resizing
        window.addEventListener('resize', () => {
            if (twinRegistryChartUpdater && twinRegistryChartUpdater.isInitialized) {
                setTimeout(() => {
                    twinRegistryChartUpdater.resizeCharts();
                }, 100);
            }
        });
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('twinRegistryModuleReady', {
            detail: {
                twinRegistryCore,
                twinRegistryHealth,
                twinRegistryPerformance,
                twinRegistryRealtime,
                twinRegistryUIUpdater,
                twinRegistryChartUpdater
            }
        }));
        
    } catch (error) {
        console.error('❌ Twin Registry module initialization failed:', error);
        throw error;
    }
}

/**
 * Get Twin Registry Core Instance
 */
export function getTwinRegistryCore() {
    return twinRegistryCore;
}

/**
 * Get Health Monitoring Instance
 */
export function getTwinRegistryHealth() {
    return twinRegistryHealth;
}

/**
 * Get Performance Monitoring Instance
 */
export function getTwinRegistryPerformance() {
    return twinRegistryPerformance;
}

/**
 * Get Real-time Monitoring Instance
 */
export function getTwinRegistryRealtime() {
    return twinRegistryRealtime;
}

/**
 * Get UI Updater Instance
 */
export function getTwinRegistryUIUpdater() {
    return twinRegistryUIUpdater;
}

/**
 * Get Chart Updater Instance
 */
export function getTwinRegistryChartUpdater() {
    return twinRegistryChartUpdater;
}

/**
 * Cleanup Twin Registry Module
 */
export function cleanupTwinRegistryModule() {
    if (twinRegistryCore) {
        twinRegistryCore.destroy();
        twinRegistryCore = null;
    }
    
    if (twinRegistryHealth) {
        twinRegistryHealth.destroy();
        twinRegistryHealth = null;
    }
    
    if (twinRegistryPerformance) {
        twinRegistryPerformance.destroy();
        twinRegistryPerformance = null;
    }
    
    if (twinRegistryRealtime) {
        twinRegistryRealtime.destroy();
        twinRegistryRealtime = null;
    }
    
    if (twinRegistryUIUpdater) {
        twinRegistryUIUpdater.destroy();
        twinRegistryUIUpdater = null;
    }
    
    if (twinRegistryChartUpdater) {
        twinRegistryChartUpdater.destroy();
        twinRegistryChartUpdater = null;
    }
    
    console.log('🧹 Twin Registry module cleaned up');
}

/**
 * Check if Twin Registry Module is Ready
 */
export function isTwinRegistryModuleReady() {
    return twinRegistryCore && twinRegistryHealth && twinRegistryPerformance && twinRegistryRealtime && twinRegistryUIUpdater && twinRegistryChartUpdater &&
           twinRegistryCore.isInitialized && twinRegistryHealth.isInitialized && 
           twinRegistryPerformance.isInitialized && twinRegistryRealtime.isInitialized && twinRegistryUIUpdater.isInitialized && twinRegistryChartUpdater.isInitialized;
}

/**
 * Refresh Twin Registry Data
 */
export async function refreshTwinRegistryData() {
    if (twinRegistryCore) {
        await twinRegistryCore.refreshData();
    }
    
    if (twinRegistryHealth) {
        await twinRegistryHealth.refreshHealthData();
    }
    
    if (twinRegistryPerformance) {
        await twinRegistryPerformance.refreshPerformanceData();
    }
    
    if (twinRegistryRealtime) {
        await twinRegistryRealtime.refreshRealtimeData();
    }
    
    if (twinRegistryUIUpdater) {
        await twinRegistryUIUpdater.refreshData();
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on a Twin Registry page
    if (window.location.pathname.includes('/twin-registry') || 
        window.location.pathname.includes('/twins')) {
        initTwinRegistryModule().catch(error => {
            console.error('Failed to initialize Twin Registry module:', error);
        });
    }
});

// Export for global access
window.TwinRegistryModule = {
    init: initTwinRegistryModule,
    cleanup: cleanupTwinRegistryModule,
    isReady: isTwinRegistryModuleReady,
    refresh: refreshTwinRegistryData,
    getCore: getTwinRegistryCore,
    getHealth: getTwinRegistryHealth,
    getPerformance: getTwinRegistryPerformance,
    getRealtime: getTwinRegistryRealtime,
    getUIUpdater: getTwinRegistryUIUpdater
};

// Export default
export default {
    init: initTwinRegistryModule,
    cleanup: cleanupTwinRegistryModule,
    isReady: isTwinRegistryModuleReady,
    refresh: refreshTwinRegistryData,
    getCore: getTwinRegistryCore,
    getHealth: getTwinRegistryHealth,
    getPerformance: getTwinRegistryPerformance,
    getRealtime: getTwinRegistryRealtime,
    getUIUpdater: getTwinRegistryUIUpdater
}; 