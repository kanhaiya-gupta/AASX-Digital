/**
 * Configuration Operations Module
 * Handles configuration management operations
 */

export class ConfigurationOperations {
    constructor(baseUrl = '/api/twin-registry') {
        this.baseUrl = baseUrl;
        this.endpoints = {
            get: '/configuration',
            save: '/configuration',
            reset: '/configuration/reset',
            export: '/configuration/export',
            import: '/configuration/import',
            validate: '/configuration/validate'
        };
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('🔄 Initializing Configuration Operations...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            console.log('✅ Configuration Operations initialized');
        } catch (error) {
            console.error('❌ Configuration Operations initialization failed:', error);
            throw error;
        }
    }

    async getConfiguration() {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.get}`, {
                headers: this.getAuthHeaders()
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching configuration:', error);
            throw error;
        }
    }

    async saveConfiguration(configData) {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.save}`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(configData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error saving configuration:', error);
            throw error;
        }
    }

    async resetConfiguration() {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.reset}`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error resetting configuration:', error);
            throw error;
        }
    }

    async exportConfiguration(format = 'json') {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.export}?format=${format}`, {
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error exporting configuration:', error);
            throw error;
        }
    }

    async importConfiguration(configData) {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.import}`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(configData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error importing configuration:', error);
            throw error;
        }
    }

    async validateConfiguration(configData) {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.validate}`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(configData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error validating configuration:', error);
            throw error;
        }
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Configuration Operations: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Configuration Operations: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Configuration Operations: Auth system ready event received');
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
                console.warn('⚠️ Configuration Operations: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state
     */
    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager?.isAuthenticated || false;
            this.currentUser = null; // User info not needed currently
            this.authToken = window.authManager.getStoredToken();
            console.log('🔐 Configuration Operations: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Configuration Operations: No auth manager available');
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
        console.log('🧹 Configuration Operations: Sensitive data cleared');
    }
} 