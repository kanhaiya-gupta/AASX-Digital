/**
 * Dashboard Builder Module Entry Point
 * Main entry point for Dashboard Builder functionality
 */

// Import shared utilities
import { initAlertSystem } from '../shared/alerts.js';
import { formatFileSize, getFileStatusInfo } from '../shared/utils.js';

// Import Dashboard Builder modules
import DashboardBuilderCore from './builder-management/core.js';
import DashboardWidgets from './builder-management/widgets.js';
import DashboardLayouts from './builder-management/layouts.js';
import DashboardThemes from './builder-management/themes.js';

// Global instances
let dashboardBuilderCore = null;
let dashboardWidgets = null;
let dashboardLayouts = null;
let dashboardThemes = null;

/**
 * Initialize Dashboard Builder Module
 * Sets up all Dashboard Builder components and functionality
 */
export async function initDashboardBuilderModule() {
    console.log('🚀 Dashboard Builder Module initializing...');
    
    try {
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Dashboard Builder
        dashboardBuilderCore = new DashboardBuilderCore();
        await dashboardBuilderCore.init();
        
        // Initialize Widgets Management
        dashboardWidgets = new DashboardWidgets();
        await dashboardWidgets.init();
        
        // Initialize Layouts Management
        dashboardLayouts = new DashboardLayouts();
        await dashboardLayouts.init();
        
        // Initialize Themes Management
        dashboardThemes = new DashboardThemes();
        await dashboardThemes.init();
        
        console.log('✅ Dashboard Builder Module initialized');
        
        // Dispatch custom event for other modules
        window.dispatchEvent(new CustomEvent('dashboardBuilderModuleReady', {
            detail: {
                dashboardBuilderCore,
                dashboardWidgets,
                dashboardLayouts,
                dashboardThemes
            }
        }));
        
    } catch (error) {
        console.error('❌ Dashboard Builder module initialization failed:', error);
        throw error;
    }
}

/**
 * Get Dashboard Builder Core Instance
 */
export function getDashboardBuilderCore() {
    return dashboardBuilderCore;
}

/**
 * Get Widgets Management Instance
 */
export function getDashboardWidgets() {
    return dashboardWidgets;
}

/**
 * Get Layouts Management Instance
 */
export function getDashboardLayouts() {
    return dashboardLayouts;
}

/**
 * Get Themes Management Instance
 */
export function getDashboardThemes() {
    return dashboardThemes;
}

/**
 * Cleanup Dashboard Builder Module
 */
export function cleanupDashboardBuilderModule() {
    if (dashboardBuilderCore) {
        dashboardBuilderCore.destroy();
        dashboardBuilderCore = null;
    }
    
    if (dashboardWidgets) {
        dashboardWidgets.destroy();
        dashboardWidgets = null;
    }
    
    if (dashboardLayouts) {
        dashboardLayouts.destroy();
        dashboardLayouts = null;
    }
    
    if (dashboardThemes) {
        dashboardThemes.destroy();
        dashboardThemes = null;
    }
    
    console.log('🧹 Dashboard Builder module cleaned up');
}

/**
 * Check if Dashboard Builder Module is Ready
 */
export function isDashboardBuilderModuleReady() {
    return dashboardBuilderCore && dashboardWidgets && dashboardLayouts && dashboardThemes &&
           dashboardBuilderCore.isInitialized && dashboardWidgets.isInitialized && 
           dashboardLayouts.isInitialized && dashboardThemes.isInitialized;
}

/**
 * Refresh Dashboard Builder Data
 */
export async function refreshDashboardBuilderData() {
    if (dashboardBuilderCore) {
        await dashboardBuilderCore.refreshData();
    }
    
    if (dashboardWidgets) {
        await dashboardWidgets.refreshWidgets();
    }
    
    if (dashboardLayouts) {
        await dashboardLayouts.refreshLayouts();
    }
    
    if (dashboardThemes) {
        await dashboardThemes.refreshThemes();
    }
}

// Auto-initialize when DOM is ready
$(document).ready(() => {
    // Check if we're on a Dashboard Builder page
    if (window.location.pathname.includes('/dashboard-builder') || 
        window.location.pathname.includes('/builder')) {
        initDashboardBuilderModule().catch(error => {
            console.error('Failed to initialize Dashboard Builder module:', error);
        });
    }
});

// Export for global access
window.DashboardBuilderModule = {
    init: initDashboardBuilderModule,
    cleanup: cleanupDashboardBuilderModule,
    isReady: isDashboardBuilderModuleReady,
    refresh: refreshDashboardBuilderData,
    getCore: getDashboardBuilderCore,
    getWidgets: getDashboardWidgets,
    getLayouts: getDashboardLayouts,
    getThemes: getDashboardThemes
};

// Export default
export default {
    init: initDashboardBuilderModule,
    cleanup: cleanupDashboardBuilderModule,
    isReady: isDashboardBuilderModuleReady,
    refresh: refreshDashboardBuilderData,
    getCore: getDashboardBuilderCore,
    getWidgets: getDashboardWidgets,
    getLayouts: getDashboardLayouts,
    getThemes: getDashboardThemes
}; 