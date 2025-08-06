/**
 * Twin Lifecycle Management Module
 * Handles twin lifecycle operations (start/stop/sync) and status tracking
 */

export default class TwinLifecycleManager {
    constructor() {
        this.apiBaseUrl = '/api/twin-registry';
        this.endpoints = {
            start: '/twins/{twin_id}/lifecycle/start',
            stop: '/twins/{twin_id}/lifecycle/stop',
            sync: '/twins/{twin_id}/lifecycle/sync',
            status: '/twins/{twin_id}/lifecycle/status',
            events: '/twins/{twin_id}/lifecycle/events'
        };
        this.isInitialized = false;
        this.activeOperations = new Map(); // Track ongoing operations
    }

    async init() {
        try {
            console.log('🔄 Initializing Twin Lifecycle Manager...');
            
            // Set up event listeners
            this.setupEventListeners();
            
            this.isInitialized = true;
            console.log('✅ Twin Lifecycle Manager initialized');
        } catch (error) {
            console.error('❌ Twin Lifecycle Manager initialization failed:', error);
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
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'starting');
            this.updateTwinStatusUI(twinId, 'starting', 'Starting twin...');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.start.replace('{twin_id}', twinId)}?user=${user}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.updateTwinStatusUI(twinId, 'running', 'Twin started successfully');
                this.dispatchLifecycleEvent('twinStarted', { twinId, user, result });
            } else {
                this.updateTwinStatusUI(twinId, 'error', result.message || 'Failed to start twin');
                this.dispatchLifecycleEvent('twinStartFailed', { twinId, user, error: result.message });
            }

            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            console.error(`❌ Failed to start twin ${twinId}:`, error);
            this.updateTwinStatusUI(twinId, 'error', `Start failed: ${error.message}`);
            this.activeOperations.delete(twinId);
            this.dispatchLifecycleEvent('twinStartFailed', { twinId, user, error: error.message });
            throw error;
        }
    }

    async stopTwin(twinId, user = 'system') {
        try {
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'stopping');
            this.updateTwinStatusUI(twinId, 'stopping', 'Stopping twin...');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.stop.replace('{twin_id}', twinId)}?user=${user}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.updateTwinStatusUI(twinId, 'stopped', 'Twin stopped successfully');
                this.dispatchLifecycleEvent('twinStopped', { twinId, user, result });
            } else {
                this.updateTwinStatusUI(twinId, 'error', result.message || 'Failed to stop twin');
                this.dispatchLifecycleEvent('twinStopFailed', { twinId, user, error: result.message });
            }

            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            console.error(`❌ Failed to stop twin ${twinId}:`, error);
            this.updateTwinStatusUI(twinId, 'error', `Stop failed: ${error.message}`);
            this.activeOperations.delete(twinId);
            this.dispatchLifecycleEvent('twinStopFailed', { twinId, user, error: error.message });
            throw error;
        }
    }

    async syncTwin(twinId, syncData = {}, user = 'system') {
        try {
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'syncing');
            this.updateTwinStatusUI(twinId, 'syncing', 'Syncing twin...');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.sync.replace('{twin_id}', twinId)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    twin_id: twinId,
                    sync_type: syncData.sync_type || 'full',
                    force: syncData.force || false
                })
            });

            const result = await response.json();

            if (result.success) {
                this.updateTwinStatusUI(twinId, 'running', 'Twin synced successfully');
                this.dispatchLifecycleEvent('twinSynced', { twinId, user, syncData, result });
            } else {
                this.updateTwinStatusUI(twinId, 'error', result.message || 'Failed to sync twin');
                this.dispatchLifecycleEvent('twinSyncFailed', { twinId, user, syncData, error: result.message });
            }

            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            console.error(`❌ Failed to sync twin ${twinId}:`, error);
            this.updateTwinStatusUI(twinId, 'error', `Sync failed: ${error.message}`);
            this.activeOperations.delete(twinId);
            this.dispatchLifecycleEvent('twinSyncFailed', { twinId, user, syncData, error: error.message });
            throw error;
        }
    }

    async getTwinStatus(twinId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.status.replace('{twin_id}', twinId)}`);
            const result = await response.json();

            if (response.ok) {
                this.updateTwinStatusUI(twinId, result.lifecycle_status, null, result);
                this.dispatchLifecycleEvent('twinStatusUpdated', { twinId, status: result });
            } else {
                console.error(`Failed to get status for twin ${twinId}:`, result);
            }

            return result;

        } catch (error) {
            console.error(`❌ Failed to get status for twin ${twinId}:`, error);
            throw error;
        }
    }

    async getTwinEvents(twinId, limit = 10) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.events.replace('{twin_id}', twinId)}?limit=${limit}`);
            const result = await response.json();

            if (response.ok) {
                this.updateTwinEventsUI(twinId, result.events);
                this.dispatchLifecycleEvent('twinEventsUpdated', { twinId, events: result.events });
            } else {
                console.error(`Failed to get events for twin ${twinId}:`, result);
            }

            return result;

        } catch (error) {
            console.error(`❌ Failed to get events for twin ${twinId}:`, error);
            throw error;
        }
    }

    updateTwinStatusUI(twinId, status, message = null, data = null) {
        // Find twin row in the table
        const twinRow = document.querySelector(`[data-twin-id="${twinId}"]`);
        if (!twinRow) return;

        // Update status badge
        const statusBadge = twinRow.querySelector('.twin-status-badge');
        if (statusBadge) {
            statusBadge.className = `badge twin-status-badge ${this.getStatusBadgeClass(status)}`;
            statusBadge.textContent = status;
        }

        // Update health score
        const healthScore = twinRow.querySelector('.twin-health-score');
        if (healthScore && data && data.health_score !== undefined) {
            healthScore.textContent = `${data.health_score}%`;
            healthScore.className = `twin-health-score ${this.getHealthScoreClass(data.health_score)}`;
        }

        // Update last sync time
        const lastSync = twinRow.querySelector('.twin-last-sync');
        if (lastSync && data && data.last_lifecycle_update) {
            lastSync.textContent = new Date(data.last_lifecycle_update).toLocaleString();
        }

        // Show operation message if provided
        if (message) {
            this.showOperationMessage(twinId, message, status);
        }
    }

    updateTwinEventsUI(twinId, events) {
        // Update events display if it exists
        const eventsContainer = document.querySelector(`[data-twin-events="${twinId}"]`);
        if (eventsContainer) {
            eventsContainer.innerHTML = events.map(event => `
                <div class="event-item">
                    <span class="event-type">${event.event_type}</span>
                    <span class="event-time">${new Date(event.timestamp).toLocaleString()}</span>
                    <span class="event-status">${event.status}</span>
                </div>
            `).join('');
        }
    }

    showOperationMessage(twinId, message, status) {
        // Create or update operation message
        let messageElement = document.querySelector(`[data-operation-message="${twinId}"]`);
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.setAttribute('data-operation-message', twinId);
            messageElement.className = 'operation-message';
            document.body.appendChild(messageElement);
        }

        messageElement.className = `operation-message alert alert-${this.getStatusAlertClass(status)} alert-dismissible fade show`;
        messageElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.remove();
            }
        }, 5000);
    }

    getStatusBadgeClass(status) {
        const statusClasses = {
            'running': 'bg-success',
            'stopped': 'bg-secondary',
            'syncing': 'bg-warning',
            'error': 'bg-danger',
            'starting': 'bg-info',
            'stopping': 'bg-warning',
            'unknown': 'bg-light text-dark'
        };
        return statusClasses[status] || 'bg-light text-dark';
    }

    getHealthScoreClass(score) {
        if (score >= 90) return 'text-success';
        if (score >= 75) return 'text-warning';
        if (score >= 60) return 'text-info';
        return 'text-danger';
    }

    getStatusAlertClass(status) {
        const alertClasses = {
            'running': 'success',
            'stopped': 'secondary',
            'syncing': 'warning',
            'error': 'danger',
            'starting': 'info',
            'stopping': 'warning'
        };
        return alertClasses[status] || 'info';
    }

    dispatchLifecycleEvent(eventName, data) {
        document.dispatchEvent(new CustomEvent(eventName, { detail: data }));
    }

    // Public methods for external use
    async restartTwin(twinId, user = 'system') {
        try {
            await this.stopTwin(twinId, user);
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
            await this.startTwin(twinId, user);
        } catch (error) {
            console.error(`❌ Failed to restart twin ${twinId}:`, error);
            throw error;
        }
    }

    isOperationInProgress(twinId) {
        return this.activeOperations.has(twinId);
    }

    getActiveOperations() {
        return Array.from(this.activeOperations.entries());
    }

    // Cleanup method
    cleanup() {
        this.activeOperations.clear();
        this.isInitialized = false;
        console.log('🧹 Twin Lifecycle Manager cleaned up');
    }
} 