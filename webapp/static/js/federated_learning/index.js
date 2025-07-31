/**
 * Federated Learning Module Entry Point
 * AASX-style modular pattern for federated learning functionality
 */

import { showAlert } from '../shared/alerts.js';
import { formatDate, generateId } from '../shared/utils.js';

// Import sub-modules
import FederatedLearningCore from './learning-management/core.js';
import FederatedLearningAggregator from './learning-management/aggregator.js';
import FederatedLearningPrivacy from './learning-management/privacy.js';
import FederatedLearningUI from './learning-management/ui.js';

// Module state
let federatedLearningCore = null;
let federatedLearningAggregator = null;
let federatedLearningPrivacy = null;
let federatedLearningUI = null;
let isModuleReady = false;

/**
 * Initialize the Federated Learning Module
 */
async function initFederatedLearningModule() {
    try {
        console.log('🧠 Initializing Federated Learning Module...');

        // Initialize core module
        federatedLearningCore = new FederatedLearningCore();
        await federatedLearningCore.init();

        // Initialize aggregator module
        federatedLearningAggregator = new FederatedLearningAggregator();
        await federatedLearningAggregator.init();

        // Initialize privacy module
        federatedLearningPrivacy = new FederatedLearningPrivacy();
        await federatedLearningPrivacy.init();

        // Initialize UI module
        federatedLearningUI = new FederatedLearningUI();
        await federatedLearningUI.init();

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
 * Get the core federated learning instance
 */
function getFederatedLearningCore() {
    if (!isModuleReady) {
        throw new Error('Federated Learning Module is not ready');
    }
    return federatedLearningCore;
}

/**
 * Get the aggregator instance
 */
function getFederatedLearningAggregator() {
    if (!isModuleReady) {
        throw new Error('Federated Learning Module is not ready');
    }
    return federatedLearningAggregator;
}

/**
 * Get the privacy instance
 */
function getFederatedLearningPrivacy() {
    if (!isModuleReady) {
        throw new Error('Federated Learning Module is not ready');
    }
    return federatedLearningPrivacy;
}

/**
 * Get the UI instance
 */
function getFederatedLearningUI() {
    if (!isModuleReady) {
        throw new Error('Federated Learning Module is not ready');
    }
    return federatedLearningUI;
}

/**
 * Check if the module is ready
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

        if (federatedLearningUI) {
            await federatedLearningUI.destroy();
        }
        if (federatedLearningPrivacy) {
            await federatedLearningPrivacy.destroy();
        }
        if (federatedLearningAggregator) {
            await federatedLearningAggregator.destroy();
        }
        if (federatedLearningCore) {
            await federatedLearningCore.destroy();
        }

        federatedLearningCore = null;
        federatedLearningAggregator = null;
        federatedLearningPrivacy = null;
        federatedLearningUI = null;
        isModuleReady = false;

        console.log('✅ Federated Learning Module cleaned up');

    } catch (error) {
        console.error('❌ Federated Learning Module cleanup failed:', error);
        throw error;
    }
}

/**
 * Refresh federated learning data
 */
async function refreshFederatedLearningData() {
    try {
        if (!isModuleReady) {
            throw new Error('Federated Learning Module is not ready');
        }

        await federatedLearningCore.refreshData();
        await federatedLearningAggregator.refreshData();
        await federatedLearningPrivacy.refreshData();
        await federatedLearningUI.refreshUI();

        // Dispatch refresh event
        window.dispatchEvent(new CustomEvent('federatedLearningDataRefreshed'));

    } catch (error) {
        console.error('Failed to refresh federated learning data:', error);
        showAlert('Failed to refresh federated learning data', 'error');
        throw error;
    }
}

// Auto-initialize on page load for federated learning routes
$(document).ready(function() {
    const currentPath = window.location.pathname;
    
    // Check if we're on a federated learning page
    if (currentPath.includes('/federated-learning') || 
        currentPath.includes('/federated') || 
        currentPath.includes('/fl-')) {
        
        console.log('🚀 Auto-initializing Federated Learning Module...');
        initFederatedLearningModule().catch(error => {
            console.error('Auto-initialization failed:', error);
        });
    }
});

// Export module functions globally
window.FederatedLearningModule = {
    init: initFederatedLearningModule,
    getCore: getFederatedLearningCore,
    getAggregator: getFederatedLearningAggregator,
    getPrivacy: getFederatedLearningPrivacy,
    getUI: getFederatedLearningUI,
    isReady: isFederatedLearningModuleReady,
    cleanup: cleanupFederatedLearningModule,
    refresh: refreshFederatedLearningData
};

// Export for ES6 modules
export {
    initFederatedLearningModule,
    getFederatedLearningCore,
    getFederatedLearningAggregator,
    getFederatedLearningPrivacy,
    getFederatedLearningUI,
    isFederatedLearningModuleReady,
    cleanupFederatedLearningModule,
    refreshFederatedLearningData
}; 