/**
 * Twin Instance Management Module
 * Handles twin instances and versioning
 */

export default class TwinInstanceManager {
    constructor() {
        this.apiBaseUrl = '/api/twin-registry';
        this.endpoints = {
            create: '/instances',
            get: '/instances',
            getByTwin: '/twins/{twin_id}/instances',
            getById: '/instances/{instance_id}'
        };
        this.isInitialized = false;
        this.instances = new Map(); // Cache instances
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('📦 Initializing Twin Instance Manager...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Set up event listeners
            this.setupEventListeners();
            
            this.isInitialized = true;
            console.log('✅ Twin Instance Manager initialized');
        } catch (error) {
            console.error('❌ Twin Instance Manager initialization failed:', error);
            throw error;
        }
    }

    setupEventListeners() {
        // Listen for instance creation requests
        document.addEventListener('twinInstanceCreate', (event) => {
            this.createInstance(event.detail.twinId, event.detail.instanceData, event.detail.instanceMetadata, event.detail.createdBy);
        });

        // Listen for instance fetch requests
        document.addEventListener('twinInstanceFetch', (event) => {
            this.getTwinInstances(event.detail.twinId);
        });

        // Listen for instance details requests
        document.addEventListener('twinInstanceDetails', (event) => {
            this.getInstanceById(event.detail.instanceId);
        });
    }

    async createInstance(twinId, instanceData, instanceMetadata = {}, createdBy = 'system') {
        try {
            console.log(`📦 Creating instance for twin: ${twinId}`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.create}`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    twin_id: twinId,
                    instance_data: instanceData,
                    instance_metadata: instanceMetadata,
                    created_by: createdBy
                })
            });

            const result = await response.json();

            if (result.success) {
                this.updateInstanceUI(twinId, result.instance, 'created');
                this.dispatchInstanceEvent('instanceCreated', { 
                    twinId, 
                    instance: result.instance,
                    createdBy 
                });
                this.showInstanceMessage('Instance created successfully', 'success');
            } else {
                this.showInstanceMessage(result.message || 'Failed to create instance', 'error');
                this.dispatchInstanceEvent('instanceCreateFailed', { 
                    twinId, 
                    error: result.message 
                });
            }

            return result;

        } catch (error) {
            console.error('❌ Failed to create instance:', error);
            this.showInstanceMessage(`Failed to create instance: ${error.message}`, 'error');
            this.dispatchInstanceEvent('instanceCreateFailed', { 
                twinId, 
                error: error.message 
            });
            throw error;
        }
    }

    async getTwinInstances(twinId) {
        try {
            console.log(`📦 Fetching instances for twin: ${twinId}`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.getByTwin.replace('{twin_id}', twinId)}`, {
                headers: this.getAuthHeaders()
            });
            const result = await response.json();

            if (result.success) {
                this.updateInstancesUI(twinId, result.instances);
                this.cacheInstances(twinId, result.instances);
                this.dispatchInstanceEvent('instancesFetched', { twinId, instances: result.instances });
            } else {
                console.error(`Failed to fetch instances for twin ${twinId}:`, result);
                this.dispatchInstanceEvent('instancesFetchFailed', { twinId, error: result.message });
            }

            return result;

        } catch (error) {
            console.error(`❌ Failed to fetch instances for twin ${twinId}:`, error);
            this.dispatchInstanceEvent('instancesFetchFailed', { twinId, error: error.message });
            throw error;
        }
    }

    async getInstanceById(instanceId) {
        try {
            console.log(`📦 Fetching instance details: ${instanceId}`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.getById.replace('{instance_id}', instanceId)}`, {
                headers: this.getAuthHeaders()
            });
            const result = await response.json();

            if (response.ok) {
                this.dispatchInstanceEvent('instanceDetailsFetched', { instanceId, instance: result });
            } else {
                console.error(`Failed to fetch instance ${instanceId}:`, result);
                this.dispatchInstanceEvent('instanceDetailsFetchFailed', { instanceId, error: result.message });
            }

            return result;

        } catch (error) {
            console.error(`❌ Failed to fetch instance ${instanceId}:`, error);
            this.dispatchInstanceEvent('instanceDetailsFetchFailed', { instanceId, error: error.message });
            throw error;
        }
    }

    async getAllInstances(twinId = null) {
        try {
            let url = `${this.apiBaseUrl}${this.endpoints.get}`;
            if (twinId) {
                url += `?twin_id=${twinId}`;
            }

            const response = await fetch(url, {
                headers: this.getAuthHeaders()
            });
            const result = await response.json();

            if (result.success) {
                this.dispatchInstanceEvent('allInstancesFetched', { instances: result.instances });
            } else {
                console.error('Failed to fetch all instances:', result);
            }

            return result;

        } catch (error) {
            console.error('❌ Failed to fetch all instances:', error);
            throw error;
        }
    }

    updateInstancesUI(twinId, instances) {
        // Update instances display in the UI
        const instancesContainer = document.querySelector(`[data-twin-instances="${twinId}"]`);
        if (instancesContainer) {
            if (instances.length === 0) {
                instancesContainer.innerHTML = '<p class="text-muted">No instances found</p>';
            } else {
                instancesContainer.innerHTML = instances.map(instance => `
                    <div class="instance-item" data-instance-id="${instance.instance_id}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <span class="badge bg-info me-2">v${instance.version}</span>
                                <span class="instance-id">${instance.instance_id.substring(0, 8)}...</span>
                            </div>
                            <div class="instance-actions">
                                <button class="btn btn-sm btn-outline-primary" onclick="viewInstanceDetails('${instance.instance_id}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success" onclick="activateInstance('${instance.instance_id}')">
                                    <i class="fas fa-play"></i>
                                </button>
                            </div>
                        </div>
                        <small class="text-muted">
                            Created: ${new Date(instance.created_at).toLocaleString()} 
                            by ${instance.created_by || 'system'}
                        </small>
                        <div class="instance-status">
                            <span class="badge ${instance.is_active ? 'bg-success' : 'bg-secondary'}">
                                ${instance.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                    </div>
                `).join('');
            }
        }

        // Update instance count in twin row
        const twinRow = document.querySelector(`[data-twin-id="${twinId}"]`);
        if (twinRow) {
            const instanceCount = twinRow.querySelector('.twin-instance-count');
            if (instanceCount) {
                instanceCount.textContent = instances.length;
            }

            // Update latest version
            const latestVersion = twinRow.querySelector('.twin-latest-version');
            if (latestVersion && instances.length > 0) {
                const latestInstance = instances.reduce((latest, current) => 
                    current.version > latest.version ? current : latest
                );
                latestVersion.textContent = `v${latestInstance.version}`;
            }
        }
    }

    updateInstanceUI(twinId, instance, action) {
        // Update specific instance UI elements
        if (action === 'created') {
            this.showInstanceMessage(`Instance created for twin ${twinId} (v${instance.version})`, 'success');
        }
    }

    cacheInstances(twinId, instances) {
        this.instances.set(twinId, instances);
    }

    getCachedInstances(twinId) {
        return this.instances.get(twinId) || [];
    }

    showInstanceMessage(message, type = 'info') {
        // Create or update instance message
        let messageElement = document.querySelector('[data-instance-message]');
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.setAttribute('data-instance-message', '');
            messageElement.className = 'instance-message';
            document.body.appendChild(messageElement);
        }

        messageElement.className = `instance-message alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        messageElement.innerHTML = `
            <i class="fas fa-cube me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.remove();
            }
        }, 5000);
    }

    dispatchInstanceEvent(eventName, data) {
        document.dispatchEvent(new CustomEvent(eventName, { detail: data }));
    }

    // Public methods for external use
    async createSnapshot(twinId, snapshotData, metadata = {}) {
        return this.createInstance(twinId, snapshotData, { ...metadata, type: 'snapshot' });
    }

    async createBackup(twinId, backupData, metadata = {}) {
        return this.createInstance(twinId, backupData, { ...metadata, type: 'backup' });
    }

    async createVersion(twinId, versionData, metadata = {}) {
        return this.createInstance(twinId, versionData, { ...metadata, type: 'version' });
    }

    getInstanceTypes() {
        return [
            'snapshot',
            'backup',
            'version',
            'checkpoint',
            'milestone'
        ];
    }

    getInstanceTypeIcon(instanceType) {
        const icons = {
            'snapshot': 'fas fa-camera',
            'backup': 'fas fa-save',
            'version': 'fas fa-code-branch',
            'checkpoint': 'fas fa-flag-checkered',
            'milestone': 'fas fa-flag'
        };
        return icons[instanceType] || 'fas fa-cube';
    }

    getInstanceTypeColor(instanceType) {
        const colors = {
            'snapshot': 'info',
            'backup': 'warning',
            'version': 'primary',
            'checkpoint': 'success',
            'milestone': 'danger'
        };
        return colors[instanceType] || 'secondary';
    }

    // Utility methods
    getLatestInstance(twinId) {
        const instances = this.getCachedInstances(twinId);
        if (instances.length === 0) return null;
        
        return instances.reduce((latest, current) => 
            current.version > latest.version ? current : latest
        );
    }

    getActiveInstances(twinId) {
        const instances = this.getCachedInstances(twinId);
        return instances.filter(instance => instance.is_active);
    }

    getInstanceHistory(twinId) {
        const instances = this.getCachedInstances(twinId);
        return instances.sort((a, b) => b.version - a.version);
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Instance Manager: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Instance Manager: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Instance Manager: Auth system ready event received');
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
                console.warn('⚠️ Twin Instance Manager: Timeout waiting for auth system');
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
            console.log('🔐 Twin Instance Manager: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Twin Instance Manager: No auth manager available');
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
        this.instances.clear();
        console.log('🧹 Twin Instance Manager: Sensitive data cleared');
    }

    // Cleanup method
    cleanup() {
        this.instances.clear();
        this.isInitialized = false;
        console.log('🧹 Twin Instance Manager cleaned up');
    }
} 