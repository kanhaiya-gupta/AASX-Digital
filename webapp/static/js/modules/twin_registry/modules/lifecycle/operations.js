/**
 * Lifecycle Operations Module
 * Handles start/stop/sync operations for twins
 */

export default class LifecycleOperations {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.endpoints = {
            start: '/twins/{twin_id}/lifecycle/start',
            stop: '/twins/{twin_id}/lifecycle/stop',
            sync: '/twins/{twin_id}/lifecycle/sync'
        };
        this.activeOperations = new Map();
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('🔄 Initializing Lifecycle Operations...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            console.log('✅ Lifecycle Operations initialized');
        } catch (error) {
            console.error('❌ Lifecycle Operations initialization failed:', error);
            throw error;
        }
    }

    async startTwin(twinId, user = 'system') {
        try {
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'starting');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.start.replace('{twin_id}', twinId)}?user=${user}`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            const result = await response.json();
            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            this.activeOperations.delete(twinId);
            throw error;
        }
    }

    async stopTwin(twinId, user = 'system') {
        try {
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'stopping');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.stop.replace('{twin_id}', twinId)}?user=${user}`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            const result = await response.json();
            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            this.activeOperations.delete(twinId);
            throw error;
        }
    }

    async syncTwin(twinId, syncData = {}, user = 'system') {
        try {
            if (this.activeOperations.has(twinId)) {
                throw new Error(`Operation already in progress for twin ${twinId}`);
            }

            this.activeOperations.set(twinId, 'syncing');

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.sync.replace('{twin_id}', twinId)}`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    twin_id: twinId,
                    sync_type: syncData.sync_type || 'full',
                    force: syncData.force || false
                })
            });

            const result = await response.json();
            this.activeOperations.delete(twinId);
            return result;

        } catch (error) {
            this.activeOperations.delete(twinId);
            throw error;
        }
    }

    async restartTwin(twinId, user = 'system') {
        try {
            await this.stopTwin(twinId, user);
            await new Promise(resolve => setTimeout(resolve, 1000));
            await this.startTwin(twinId, user);
        } catch (error) {
            throw error;
        }
    }

    isOperationInProgress(twinId) {
        return this.activeOperations.has(twinId);
    }

    getActiveOperations() {
        return Array.from(this.activeOperations.entries());
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Lifecycle Operations: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Lifecycle Operations: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Lifecycle Operations: Auth system ready event received');
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
                console.warn('⚠️ Lifecycle Operations: Timeout waiting for auth system');
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
            console.log('🔐 Lifecycle Operations: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Lifecycle Operations: No auth manager available');
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
        this.activeOperations.clear();
        console.log('🧹 Lifecycle Operations: Sensitive data cleared');
    }
}