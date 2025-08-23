/**
 * Lifecycle UI Module
 * Handles UI updates for lifecycle operations
 */

export default class LifecycleUI {
    constructor() {
        this.messageTimeout = 5000;
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('🔄 Initializing Lifecycle UI...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            console.log('✅ Lifecycle UI initialized');
        } catch (error) {
            console.error('❌ Lifecycle UI initialization failed:', error);
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

        // Auto-dismiss after timeout
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.remove();
            }
        }, this.messageTimeout);
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

    setMessageTimeout(timeout) {
        this.messageTimeout = timeout;
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Lifecycle UI: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Lifecycle UI: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Lifecycle UI: Auth system ready event received');
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
                console.warn('⚠️ Lifecycle UI: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state
     */
    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated();
            this.currentUser = null; // User info not needed currently
            this.authToken = window.authManager.getStoredToken();
            console.log('🔐 Lifecycle UI: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Lifecycle UI: No auth manager available');
        }
    }

    /**
     * Setup authentication event listeners
     */
    setupAuthListeners() {
        window.addEventListener('authStateChanged', () => {
            this.updateAuthState();
        });

        window.addEventListener('loginSuccess', () => {
            this.updateAuthState();
        });

        window.addEventListener('logout', () => {
            this.updateAuthState();
            // Clear sensitive data when user logs out
            this.clearSensitiveData();
        });
    }

    /**
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        console.log('🧹 Lifecycle UI: Sensitive data cleared');
    }
}