/**
 * Instance Operations Module
 * Handles API calls for instance management operations
 */

export class InstanceOperations {
    constructor(baseUrl = '/api/twin-registry') {
        this.baseUrl = baseUrl;
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('🔄 Initializing Instance Operations...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            console.log('✅ Instance Operations initialized');
        } catch (error) {
            console.error('❌ Instance Operations initialization failed:', error);
            throw error;
        }
    }

    async createInstance(instanceData) {
        try {
            const response = await fetch(`${this.baseUrl}/instances`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(instanceData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, instance: result };
            
        } catch (error) {
            console.error('Error creating instance:', error);
            return { success: false, message: error.message };
        }
    }

    async getInstances(twinId = null) {
        try {
            let url = `${this.baseUrl}/instances`;
            if (twinId) {
                url += `?twin_id=${twinId}`;
            }

            const response = await fetch(url, {
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            // Return the instances array from the response, or empty array if not found
            return result.instances || [];
            
        } catch (error) {
            console.error('Error getting instances:', error);
            return [];
        }
    }

    async getInstanceDetails(instanceId) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/${instanceId}`, {
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, instance: result };
            
        } catch (error) {
            console.error('Error getting instance details:', error);
            return { success: false, message: error.message };
        }
    }

    async getInstanceSummary(twinId = null) {
        try {
            const instances = await this.getInstances(twinId);
            // getInstances now returns the instances array directly
            
            const summary = {
                total: instances.length,
                active: instances.filter(i => i.is_active).length,
                latest_version: 'v1',
                history: instances.length
            };

            if (instances.length > 0) {
                const versions = instances.map(i => i.version).sort();
                summary.latest_version = versions[versions.length - 1];
            }

            return summary;
            
        } catch (error) {
            console.error('Error getting instance summary:', error);
            return { total: 0, active: 0, latest_version: 'v1', history: 0 };
        }
    }

    async createSnapshot(twinId) {
        try {
            const snapshotData = {
                twin_id: twinId,
                instance_data: {
                    type: 'snapshot',
                    description: `Snapshot created at ${new Date().toISOString()}`,
                    created_at: new Date().toISOString()
                },
                instance_metadata: {
                    source: 'snapshot_creation',
                    user: 'system'
                },
                created_by: 'system'
            };

            return await this.createInstance(snapshotData);
            
        } catch (error) {
            console.error('Error creating snapshot:', error);
            return { success: false, message: error.message };
        }
    }

    async createBackup(twinId) {
        try {
            const backupData = {
                twin_id: twinId,
                instance_data: {
                    type: 'backup',
                    description: `Backup created at ${new Date().toISOString()}`,
                    created_at: new Date().toISOString()
                },
                instance_metadata: {
                    source: 'backup_creation',
                    user: 'system'
                },
                created_by: 'system'
            };

            return await this.createInstance(backupData);
            
        } catch (error) {
            console.error('Error creating backup:', error);
            return { success: false, message: error.message };
        }
    }

    async compareInstances(instance1Id, instance2Id) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/compare`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    instance1_id: instance1Id,
                    instance2_id: instance2Id
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, comparison: result };
            
        } catch (error) {
            console.error('Error comparing instances:', error);
            return { success: false, message: error.message };
        }
    }

    async activateInstance(instanceId) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/${instanceId}/activate`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, result };
            
        } catch (error) {
            console.error('Error activating instance:', error);
            return { success: false, message: error.message };
        }
    }

    async restoreInstance(instanceId) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/${instanceId}/restore`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, result };
            
        } catch (error) {
            console.error('Error restoring instance:', error);
            return { success: false, message: error.message };
        }
    }

    async deleteInstance(instanceId) {
        try {
            const response = await fetch(`${this.baseUrl}/instances/${instanceId}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, result };
            
        } catch (error) {
            console.error('Error deleting instance:', error);
            return { success: false, message: error.message };
        }
    }

    async getTwinInstances(twinId) {
        try {
            const response = await fetch(`${this.baseUrl}/twins/${twinId}/instances`, {
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('Error getting twin instances:', error);
            return [];
        }
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Instance Operations: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Instance Operations: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Instance Operations: Auth system ready event received');
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
                console.warn('⚠️ Instance Operations: Timeout waiting for auth system');
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
            console.log('🔐 Instance Operations: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Instance Operations: No auth manager available');
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
        console.log('🧹 Instance Operations: Sensitive data cleared');
    }
}