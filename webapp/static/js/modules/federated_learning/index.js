/**
 * Federated Learning Module Entry Point
 * AASX-style modular pattern for federated learning functionality
 */

import { showAlert } from '../shared/alerts.js';
import { formatDate, generateId } from '../shared/utils.js';

// Import UI components
import FederationStatusComponent from './ui-components/federation_status.js';
import TwinPerformanceComponent from './ui-components/twin_performance.js';
import CrossTwinInsightsComponent from './ui-components/cross_twin_insights.js';
import PrivacySecurityComponent from './ui-components/privacy_security.js';
import FederationMetricsComponent from './ui-components/federation_metrics.js';
import RealTimeMetricsComponent from './ui-components/real_time_metrics.js';
import TrainingManagementComponent from './ui-components/training_management.js';

// Module state
let components = {};
let isModuleReady = false;

/**
 * Initialize the Federated Learning Module
 */
async function initFederatedLearningModule() {
    try {
        console.log('🧠 Initializing Federated Learning Module...');

        // Initialize all UI components
        components.federationStatus = new FederationStatusComponent();
        components.twinPerformance = new TwinPerformanceComponent();
        components.crossTwinInsights = new CrossTwinInsightsComponent();
        components.privacySecurity = new PrivacySecurityComponent();
        components.federationMetrics = new FederationMetricsComponent();
        components.realTimeMetrics = new RealTimeMetricsComponent();
        components.trainingManagement = new TrainingManagementComponent();

        // Initialize all components
        await Promise.all([
            components.federationStatus.init(),
            components.twinPerformance.init(),
            components.crossTwinInsights.init(),
            components.privacySecurity.init(),
            components.federationMetrics.init(),
            components.realTimeMetrics.init(),
            components.trainingManagement.init()
        ]);

        isModuleReady = true;
        console.log('✅ Federated Learning Module initialized');

        // Dispatch ready event
        window.dispatchEvent(new CustomEvent('federatedLearningModuleReady', {
            detail: { module: 'federated_learning' }
        }));

    } catch (error) {
        console.error('❌ Federated Learning Module initialization failed:', error);
        showAlert('Failed to initialize Federated Learning Module', 'error');
        throw error;
    }
}

/**
 * Get a specific component
 */
function getComponent(componentName) {
    if (!isModuleReady) {
        throw new Error('Federated Learning Module is not ready');
    }
    return components[componentName];
}

/**
 * Check if module is ready
 */
function isFederatedLearningModuleReady() {
    return isModuleReady;
}

/**
 * Cleanup the module
 */
async function cleanupFederatedLearningModule() {
    try {
        console.log('🧹 Cleaning up Federated Learning Module...');
        
        // Cleanup all components
        for (const [name, component] of Object.entries(components)) {
            if (component && typeof component.cleanup === 'function') {
                await component.cleanup();
            }
        }
        
        components = {};
        isModuleReady = false;
        
        console.log('✅ Federated Learning Module cleaned up');
    } catch (error) {
        console.error('❌ Error cleaning up Federated Learning Module:', error);
    }
}

/**
 * Refresh all data
 */
async function refreshFederatedLearningData() {
    try {
        if (!isModuleReady) {
            console.warn('⚠️ Module not ready, cannot refresh data');
            return;
        }

        console.log('🔄 Refreshing Federated Learning data...');
        
        // Refresh all components
        await Promise.all([
            components.federationStatus.refresh(),
            components.twinPerformance.refresh(),
            components.crossTwinInsights.refresh(),
            components.privacySecurity.refresh(),
            components.federationMetrics.refresh(),
            components.realTimeMetrics.refresh()
        ]);
        
        console.log('✅ Federated Learning data refreshed');
    } catch (error) {
        console.error('❌ Error refreshing Federated Learning data:', error);
        showAlert('Failed to refresh data', 'error');
    }
}

// Export module functions
export {
    initFederatedLearningModule,
    getComponent,
    isFederatedLearningModuleReady,
    cleanupFederatedLearningModule,
    refreshFederatedLearningData
};

// Initialize module when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM ready, initializing Federated Learning Module...');
    initFederatedLearningModule();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (isModuleReady) {
        cleanupFederatedLearningModule();
    }
}); 