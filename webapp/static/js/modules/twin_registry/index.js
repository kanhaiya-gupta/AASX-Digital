/**
 * Twin Registry Module Entry Point
 * Main entry point for Twin Registry functionality
 */

// Import shared utilities
import { initAlertSystem } from '/static/js/shared/alerts.js';

// Import Twin Registry modules
import TwinRegistryCore from './registry-management/core.js';
import TwinRegistryHealth from './registry-management/health.js';
import TwinRegistryPerformance from './registry-management/performance.js';
import TwinRegistryRealtime from './registry-management/realtime.js';
import TwinRegistryUIUpdater from './registry-management/ui-updater.js';
import TwinRegistryChartUpdater from './registry-management/chart-updater.js';
import TwinRegistryInstances from './registry-management/instances.js';
import TwinRegistryLifecycle from './registry-management/lifecycle.js';
import TwinRegistryRelationships from './registry-management/relationships.js';
import TwinRegistryAnalytics from './registry-management/analytics.js';
import TwinRegistryConfiguration from './registry-management/configuration.js';
import TwinRegistryTwinManagement from './registry-management/twin-management.js';

// Import new modular managers (BACKUP - not currently used)
// import LifecycleManager from './modules/lifecycle/index.js';
// import RelationshipManager from './modules/relationships/index.js';
// import InstanceManager from './modules/instances/index.js';
// import ConfigurationManager from './modules/configuration/index.js';

// Global instances
let twinRegistryCore = null;
let twinRegistryHealth = null;
let twinRegistryPerformance = null;
let twinRegistryRealtime = null;
let twinRegistryUIUpdater = null;
let twinRegistryChartUpdater = null;
let twinRegistryInstances = null;
let twinRegistryLifecycle = null;
let twinRegistryRelationships = null;
let twinRegistryAnalytics = null;
let twinRegistryConfiguration = null;
let twinRegistryTwinManagement = null;

// New modular manager instances (BACKUP - not currently used)
// let lifecycleManager = null;
// let relationshipManager = null;
// let instanceManager = null;
// let configurationManager = null;

// Module initialization state
let isInitialized = false;

/**
 * Initialize Twin Registry Module
 * Sets up all Twin Registry components and functionality
 */
export async function initTwinRegistryModule() {
    console.log('🚀 Twin Registry Module initializing...');
    
    try {
        // ✅ CORRECT: Wait for central auth system (like Knowledge Graph)
        console.log('🔐 Twin Registry Module: Waiting for authentication system...');
        await new Promise((resolve) => {
            if (window.authSystemReady && window.authManager) {
                console.log('🔐 Twin Registry Module: Auth system already ready');
                resolve();
                return;
            }
            
            const handleReady = () => {
                console.log('🚀 Twin Registry Module: Auth system ready event received');
                window.removeEventListener('authSystemReady', handleReady);
                resolve();
            };
            
            window.addEventListener('authSystemReady', handleReady);
            
            // Fallback: check periodically
            const checkInterval = setInterval(() => {
                if (window.authSystemReady && window.authManager) {
                    clearInterval(checkInterval);
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                window.removeEventListener('authSystemReady', handleReady);
                console.warn('⚠️ Twin Registry Module: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
        
        console.log('🔐 Twin Registry Module: Authentication system ready, proceeding with initialization...');
        
        // Initialize alert system first
        initAlertSystem();
        
        // Initialize Core Registry with auth integration
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
        
        // Initialize Instances Management
        twinRegistryInstances = new TwinRegistryInstances();
        await twinRegistryInstances.init();
        
        // Initialize Lifecycle Management
        twinRegistryLifecycle = new TwinRegistryLifecycle();
        await twinRegistryLifecycle.init();
        
        // Initialize Relationships Management
        twinRegistryRelationships = new TwinRegistryRelationships();
        await twinRegistryRelationships.init();
        
        // Initialize Analytics Dashboard
        twinRegistryAnalytics = new TwinRegistryAnalytics();
        await twinRegistryAnalytics.init();
        
        // Initialize Configuration Management
        twinRegistryConfiguration = new TwinRegistryConfiguration();
        await twinRegistryConfiguration.init();
        
        // Initialize Twin Management
        twinRegistryTwinManagement = new TwinRegistryTwinManagement();
        await twinRegistryTwinManagement.init();
        
        // Initialize new modular managers (BACKUP - not currently used)
        // console.log('🔄 Initializing modular twin registry managers...');
        
        // // Initialize Lifecycle Manager
        // lifecycleManager = new LifecycleManager('/api/twin-registry');
        // await lifecycleManager.init();
        
        // // Initialize Relationship Manager
        // relationshipManager = new RelationshipManager('/api/twin-registry');
        // await relationshipManager.init();
        
        // // Initialize Instance Manager
        // instanceManager = new InstanceManager('/api/twin-registry');
        // await instanceManager.init();
        
        // // Initialize Configuration Manager
        // configurationManager = new ConfigurationManager('/api/twin-registry');
        // await configurationManager.init();
        
        console.log('✅ Twin Registry Module initialized with working registry-management modules');
        
        // Make instances available globally
        window.twinRegistryCore = twinRegistryCore;
        window.twinRegistryHealth = twinRegistryHealth;
        window.twinRegistryPerformance = twinRegistryPerformance;
        window.twinRegistryRealtime = twinRegistryRealtime;
        window.twinRegistryUIUpdater = twinRegistryUIUpdater;
        window.twinRegistryChartUpdater = twinRegistryChartUpdater;
        window.twinRegistryInstances = twinRegistryInstances;
        window.twinRegistryLifecycle = twinRegistryLifecycle;
        window.twinRegistryRelationships = twinRegistryRelationships;
        window.twinRegistryAnalytics = twinRegistryAnalytics;
        
        // Setup tab switching to load data for each tab
        setupTabSwitching();
        
        // Make remaining instances available globally
        window.twinRegistryConfiguration = twinRegistryConfiguration;
        window.twinRegistryTwinManagement = twinRegistryTwinManagement;
        
        // Make modular managers available globally (BACKUP - not currently used)
        // window.lifecycleManager = lifecycleManager;
        // window.relationshipManager = relationshipManager;
        // window.instanceManager = instanceManager;
        // window.configurationManager = configurationManager;
        
        // Make initialization function available globally for post-login orchestrator
        window.initializeTwinRegistryIfNeeded = async () => {
            if (!isInitialized) {
                console.log('🔄 Post-Login Orchestrator: Initializing Twin Registry modules...');
                await initTwinRegistryModule();
                console.log('✅ Post-Login Orchestrator: Twin Registry modules initialized successfully');
            }
        };
        
        isInitialized = true;
        
        // Set up global functions for HTML onclick handlers using working modules
        window.startTwin = (twinId, user = 'system') => twinRegistryLifecycle?.startTwin?.(twinId, user);
        window.stopTwin = (twinId, user = 'system') => twinRegistryLifecycle?.stopTwin?.(twinId, user);
        window.syncTwin = (twinId, syncData = {}, user = 'system') => twinRegistryLifecycle?.syncTwin?.(twinId, syncData, user);
        window.restartTwin = (twinId, user = 'system') => twinRegistryLifecycle?.restartTwin?.(twinId, user);
        
        window.createRelationship = (sourceTwinId, targetTwinId, relationshipType, relationshipData = {}) => 
            twinRegistryRelationships?.createRelationship?.(sourceTwinId, targetTwinId, relationshipType, relationshipData);
        window.deleteRelationship = (relationshipId) => twinRegistryRelationships?.deleteRelationship?.(relationshipId);
        
        // Instance management functions
        window.createInstance = () => twinRegistryInstances?.createInstance?.();
        window.createSnapshot = () => twinRegistryInstances?.createSnapshot?.();
        window.createBackup = () => twinRegistryInstances?.createBackup?.();
        window.compareInstances = () => twinRegistryInstances?.compareInstances?.();
        window.activateInstance = (instanceId) => twinRegistryInstances?.activateInstance?.(instanceId);
        window.restoreInstance = (instanceId) => twinRegistryInstances?.restoreInstance?.(instanceId);
        window.deleteInstance = (instanceId) => twinRegistryInstances?.deleteInstance?.(instanceId);
        window.viewInstanceDetails = (instanceId) => twinRegistryInstances?.viewInstanceDetails?.(instanceId);
        
        // Configuration functions (using new configuration module)
        window.twinRegistrySaveAllConfigurations = () => twinRegistryConfiguration?.saveConfiguration?.();
        window.twinRegistryResetToDefaults = () => twinRegistryConfiguration?.resetConfiguration?.();
        window.twinRegistryRefreshConfiguration = () => twinRegistryConfiguration?.loadConfiguration?.();
        
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
                twinRegistryChartUpdater,
                twinRegistryInstances,
                twinRegistryLifecycle,
                twinRegistryRelationships,
                twinRegistryAnalytics,
                twinRegistryConfiguration,
                twinRegistryTwinManagement
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
 * Get Twin Registry Health Instance
 */
export function getTwinRegistryHealth() {
    return twinRegistryHealth;
}

/**
 * Get Twin Registry Performance Instance
 */
export function getTwinRegistryPerformance() {
    return twinRegistryPerformance;
}

/**
 * Get Twin Registry Realtime Instance
 */
export function getTwinRegistryRealtime() {
    return twinRegistryRealtime;
}

/**
 * Get Twin Registry UI Updater Instance
 */
export function getTwinRegistryUIUpdater() {
    return twinRegistryUIUpdater;
}

/**
 * Get Twin Registry Chart Updater Instance
 */
export function getTwinRegistryChartUpdater() {
    return twinRegistryChartUpdater;
}

/**
 * Get Lifecycle Manager Instance
 */
export function getLifecycleManager() {
    return lifecycleManager;
}

/**
 * Get Relationship Manager Instance
 */
export function getRelationshipManager() {
    return relationshipManager;
}

/**
 * Get Instance Manager Instance
 */
export function getInstanceManager() {
    return instanceManager;
}

/**
 * Get Configuration Manager Instance
 */
export function getConfigurationManager() {
    return configurationManager;
}

/**
 * Cleanup Twin Registry Module
 * Cleans up all resources and event listeners
 */
export function cleanupTwinRegistryModule() {
    console.log('🧹 Cleaning up Twin Registry Module...');
    
    try {
        // Cleanup existing modules
        if (twinRegistryCore) {
            twinRegistryCore.cleanup();
            twinRegistryCore = null;
        }
        
        if (twinRegistryHealth) {
            twinRegistryHealth.cleanup();
            twinRegistryHealth = null;
        }
        
        if (twinRegistryPerformance) {
            twinRegistryPerformance.cleanup();
            twinRegistryPerformance = null;
        }
        
        if (twinRegistryRealtime) {
            twinRegistryRealtime.cleanup();
            twinRegistryRealtime = null;
        }
        
        if (twinRegistryUIUpdater) {
            twinRegistryUIUpdater.cleanup();
            twinRegistryUIUpdater = null;
        }
        
        if (twinRegistryChartUpdater) {
            twinRegistryChartUpdater.cleanup();
            twinRegistryChartUpdater = null;
        }
        
        // Cleanup new modular managers
        if (lifecycleManager) {
            lifecycleManager.cleanup();
            lifecycleManager = null;
        }
        
        if (relationshipManager) {
            relationshipManager.cleanup();
            relationshipManager = null;
        }
        
        if (instanceManager) {
            instanceManager.cleanup();
            instanceManager = null;
        }
        
        if (configurationManager) {
            configurationManager.cleanup();
            configurationManager = null;
        }
        
        // Remove global references
        delete window.twinRegistryCore;
        delete window.twinRegistryHealth;
        delete window.twinRegistryPerformance;
        delete window.twinRegistryRealtime;
        delete window.twinRegistryUIUpdater;
        delete window.twinRegistryChartUpdater;
        delete window.lifecycleManager;
        delete window.relationshipManager;
        delete window.instanceManager;
        delete window.configurationManager;
        
        console.log('✅ Twin Registry Module cleaned up');
        
    } catch (error) {
        console.error('❌ Error during Twin Registry Module cleanup:', error);
    }
}

/**
 * Check if Twin Registry Module is Ready
 */
export function isTwinRegistryModuleReady() {
    return twinRegistryCore && twinRegistryCore.isInitialized &&
           lifecycleManager && lifecycleManager.isInitialized &&
           relationshipManager && relationshipManager.isInitialized;
}

/**
 * Refresh Twin Registry Data
 * Refreshes all data across all modules
 */
export async function refreshTwinRegistryData() {
    console.log('🔄 Refreshing Twin Registry data...');
    
    try {
        // Refresh UI updater which handles all tab data
        if (twinRegistryUIUpdater) {
            await twinRegistryUIUpdater.refreshAllData();
        }
        
        // Refresh charts
        if (twinRegistryChartUpdater) {
            await twinRegistryChartUpdater.refreshCharts();
        }
        
        console.log('✅ Twin Registry data refreshed');
        
    } catch (error) {
        console.error('❌ Error refreshing Twin Registry data:', error);
        throw error;
    }
}

/**
 * Setup Tab Switching to Load Data for Each Tab
 */
function setupTabSwitching() {
    console.log('🔧 Setting up tab switching for data loading...');
    
    // Get all tab buttons
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', async (event) => {
            const targetId = event.target.getAttribute('data-bs-target');
            console.log(`🔄 Tab switched to: ${targetId}`);
            
            try {
                // Load data based on which tab is active
                switch (targetId) {
                    case '#twin_registry_monitoring':
                        console.log('🏥 Loading Health Monitoring data...');
                        if (window.twinRegistryHealth) {
                            await window.twinRegistryHealth.loadHealthData();
                            await window.twinRegistryHealth.updateHealthUI();
                        }
                        break;
                        
                    case '#twin_registry_performance':
                        console.log('📊 Loading Performance data...');
                        if (window.twinRegistryPerformance) {
                            await window.twinRegistryPerformance.loadPerformanceData();
                            await window.twinRegistryPerformance.updatePerformanceUI();
                        }
                        break;
                        
                    case '#twin_registry_analytics':
                        console.log('📈 Loading Analytics data...');
                        if (window.twinRegistryAnalytics) {
                            await window.twinRegistryAnalytics.loadAnalyticsData();
                            await window.twinRegistryAnalytics.updateAnalyticsUI();
                        }
                        break;
                        
                    case '#twin_registry_lifecycle':
                        console.log('🔄 Loading Lifecycle data...');
                        if (window.twinRegistryLifecycle) {
                            await window.twinRegistryLifecycle.loadLifecycleData();
                            await window.twinRegistryLifecycle.updateLifecycleUI();
                        }
                        break;
                        
                    case '#twin_registry_instances':
                        console.log('🔧 Loading Instances data...');
                        if (window.twinRegistryInstances) {
                            await window.twinRegistryInstances.loadInstancesData();
                            await window.twinRegistryInstances.updateInstancesUI();
                        }
                        break;
                        
                    case '#twin_registry_configuration':
                        console.log('⚙️ Loading Configuration data...');
                        if (window.twinRegistryConfiguration) {
                            await window.twinRegistryConfiguration.loadConfigurationData();
                            await window.twinRegistryConfiguration.updateConfigurationUI();
                        }
                        break;
                        
                    case '#twin_registry_management':
                        console.log('📋 Management tab active - data already loaded');
                        break;
                        
                    default:
                        console.log(`⚠️ Unknown tab: ${targetId}`);
                }
            } catch (error) {
                console.error(`❌ Error loading data for tab ${targetId}:`, error);
            }
        });
    });
    
    console.log('✅ Tab switching setup complete');
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initTwinRegistryModule().catch(error => {
        console.error('Failed to initialize Twin Registry Module:', error);
    });
}); 