/**
 * Lifecycle Manager - Main Module
 * Orchestrates lifecycle operations, status tracking, and UI updates
 */

import LifecycleOperations from './operations.js';
import LifecycleStatus from './status.js';
import LifecycleUI from './ui.js';

export default class LifecycleManager {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.isInitialized = false;
        
        // Initialize sub-modules
        this.operations = new LifecycleOperations(apiBaseUrl);
        this.status = new LifecycleStatus(apiBaseUrl);
        this.ui = new LifecycleUI();
    }

    async init() {
        try {
            console.log('🔄 Initializing Lifecycle Manager...');
            this.setupEventListeners();
            this.isInitialized = true;
            console.log('✅ Lifecycle Manager initialized');
        } catch (error) {
            console.error('❌ Lifecycle Manager initialization failed:', error);
            throw error;
        }
    }

    setupEventListeners() {
        // Listen for lifecycle operation requests
        document.addEventListener('twinLifecycleStart', (event) => {
            this.startTwin(event.detail.twinId, event.detail.user);
        });

        document.addEventListener('twinLifecycleStop', (event) => {
            this.stopTwin(event.detail.twinId, event.detail.user);
        });

        document.addEventListener('twinLifecycleSync', (event) => {
            this.syncTwin(event.detail.twinId, event.detail.syncData, event.detail.user);
        });

        // Listen for status update requests
        document.addEventListener('twinLifecycleStatusUpdate', (event) => {
            this.getTwinStatus(event.detail.twinId);
        });
    }

    async startTwin(twinId, user = 'system') {
        try {
            this.ui.updateTwinStatusUI(twinId, 'starting', 'Starting twin...');
            const result = await this.operations.startTwin(twinId, user);

            if (result.success) {
                this.ui.updateTwinStatusUI(twinId, 'running', 'Twin started successfully');
                this.dispatchEvent('twinStarted', { twinId, user, result });
            } else {
                this.ui.updateTwinStatusUI(twinId, 'error', result.message || 'Failed to start twin');
                this.dispatchEvent('twinStartFailed', { twinId, user, error: result.message });
            }

            return result;
        } catch (error) {
            console.error(`❌ Failed to start twin ${twinId}:`, error);
            this.ui.updateTwinStatusUI(twinId, 'error', `Start failed: ${error.message}`);
            this.dispatchEvent('twinStartFailed', { twinId, user, error: error.message });
            throw error;
        }
    }

    async stopTwin(twinId, user = 'system') {
        try {
            this.ui.updateTwinStatusUI(twinId, 'stopping', 'Stopping twin...');
            const result = await this.operations.stopTwin(twinId, user);

            if (result.success) {
                this.ui.updateTwinStatusUI(twinId, 'stopped', 'Twin stopped successfully');
                this.dispatchEvent('twinStopped', { twinId, user, result });
            } else {
                this.ui.updateTwinStatusUI(twinId, 'error', result.message || 'Failed to stop twin');
                this.dispatchEvent('twinStopFailed', { twinId, user, error: result.message });
            }

            return result;
        } catch (error) {
            console.error(`❌ Failed to stop twin ${twinId}:`, error);
            this.ui.updateTwinStatusUI(twinId, 'error', `Stop failed: ${error.message}`);
            this.dispatchEvent('twinStopFailed', { twinId, user, error: error.message });
            throw error;
        }
    }

    async syncTwin(twinId, syncData = {}, user = 'system') {
        try {
            this.ui.updateTwinStatusUI(twinId, 'syncing', 'Syncing twin...');
            const result = await this.operations.syncTwin(twinId, syncData, user);

            if (result.success) {
                this.ui.updateTwinStatusUI(twinId, 'running', 'Twin synced successfully');
                this.dispatchEvent('twinSynced', { twinId, user, syncData, result });
            } else {
                this.ui.updateTwinStatusUI(twinId, 'error', result.message || 'Failed to sync twin');
                this.dispatchEvent('twinSyncFailed', { twinId, user, syncData, error: result.message });
            }

            return result;
        } catch (error) {
            console.error(`❌ Failed to sync twin ${twinId}:`, error);
            this.ui.updateTwinStatusUI(twinId, 'error', `Sync failed: ${error.message}`);
            this.dispatchEvent('twinSyncFailed', { twinId, user, syncData, error: error.message });
            throw error;
        }
    }

    async getTwinStatus(twinId) {
        try {
            const result = await this.status.getTwinStatus(twinId);
            if (result) {
                this.ui.updateTwinStatusUI(twinId, result.lifecycle_status, null, result);
                this.dispatchEvent('twinStatusUpdated', { twinId, status: result });
            }
            return result;
        } catch (error) {
            console.error(`❌ Failed to get status for twin ${twinId}:`, error);
            throw error;
        }
    }

    async getTwinEvents(twinId, limit = 10) {
        try {
            const result = await this.status.getTwinEvents(twinId, limit);
            if (result && result.events) {
                this.ui.updateTwinEventsUI(twinId, result.events);
                this.dispatchEvent('twinEventsUpdated', { twinId, events: result.events });
            }
            return result;
        } catch (error) {
            console.error(`❌ Failed to get events for twin ${twinId}:`, error);
            throw error;
        }
    }

    async restartTwin(twinId, user = 'system') {
        try {
            await this.stopTwin(twinId, user);
            await new Promise(resolve => setTimeout(resolve, 1000));
            await this.startTwin(twinId, user);
        } catch (error) {
            console.error(`❌ Failed to restart twin ${twinId}:`, error);
            throw error;
        }
    }

    dispatchEvent(eventName, data) {
        document.dispatchEvent(new CustomEvent(eventName, { detail: data }));
    }

    // Public methods for external use
    isOperationInProgress(twinId) {
        return this.operations.isOperationInProgress(twinId);
    }

    getActiveOperations() {
        return this.operations.getActiveOperations();
    }

    setMessageTimeout(timeout) {
        this.ui.setMessageTimeout(timeout);
    }

    // Cleanup method
    cleanup() {
        this.isInitialized = false;
        console.log('🧹 Lifecycle Manager cleaned up');
    }
} 