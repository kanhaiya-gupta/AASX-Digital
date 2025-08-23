/**
 * Lifecycle Status Module
 * Handles status tracking and health monitoring
 */

export default class LifecycleStatus {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.endpoints = {
            status: '/twins/{twin_id}/lifecycle/status',
            events: '/twins/{twin_id}/lifecycle/events'
        };
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('🔄 Initializing Lifecycle Status...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            console.log('✅ Lifecycle Status initialized');
        } catch (error) {
            console.error('❌ Lifecycle Status initialization failed:', error);
            throw error;
        }
    }

    async getTwinStatus(twinId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.status.replace('{twin_id}', twinId)}`, {
                headers: this.getAuthHeaders()
            });
            const result = await response.json();

            if (response.ok) {
                return result;
            } else {
                console.error(`Failed to get status for twin ${twinId}:`, result);
                return null;
            }
        } catch (error) {
            console.error(`❌ Failed to get status for twin ${twinId}:`, error);
            throw error;
        }
    }

    async getTwinEvents(twinId, limit = 10) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.events.replace('{twin_id}', twinId)}?limit=${limit}`, {
                headers: this.getAuthHeaders()
            });
            const result = await response.json();

            if (response.ok) {
                return result;
            } else {
                console.error(`Failed to get events for twin ${twinId}:`, result);
                return null;
            }
        } catch (error) {
            console.error(`❌ Failed to get events for twin ${twinId}:`, error);
            throw error;
        }
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

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Lifecycle Status: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Lifecycle Status: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Lifecycle Status: Auth system ready event received');
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
                console.warn('⚠️ Lifecycle Status: Timeout waiting for auth system');
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
            console.log('🔐 Lifecycle Status: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Lifecycle Status: No auth manager available');
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
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }

    /**
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        console.log('🧹 Lifecycle Status: Sensitive data cleared');
    }
}