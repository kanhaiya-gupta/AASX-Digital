/**
 * Twin Registry Core Module
 * Handles core twin registry functionality, registration, and data management
 */

export default class TwinRegistryCore {
    constructor() {
        this.isInitialized = false;
        this.registryData = [];
        this.twinCache = new Map();
        this.registrationQueue = [];
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        this.config = {
            apiBaseUrl: '/api/twin-registry',
            endpoints: {
                twins: '/api/twin-registry/twins',
                register: '/api/twin-registry/twins',
                update: '/api/twin-registry/twins',
                delete: '/api/twin-registry/twins',
                search: '/api/twin-registry/twins/search',
                status: '/api/twin-registry/status',
                health: '/api/twin-registry/health',
                performance: '/api/twin-registry/twins/statistics'
            },
            refreshInterval: 30000, // 30 seconds
            maxRetries: 3,
            retryDelay: 1000
        };
        this.refreshInterval = null;
        this.isProcessing = false;
    }

    /**
     * Initialize Twin Registry Core
     */
    async init() {
        console.log('🔧 Initializing Twin Registry Core...');

        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();

            // Load configuration
            await this.loadConfiguration();

            // Load initial registry data
            await this.loadRegistryData();

            // Setup auto-refresh
            this.setupAutoRefresh();

            // Process any pending registrations
            await this.processRegistrationQueue();

            this.isInitialized = true;
            console.log('✅ Twin Registry Core initialized');

        } catch (error) {
            console.error('❌ Twin Registry Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * Initialize authentication
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Registry: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Registry: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Registry: Auth system ready event received');
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
                console.warn('⚠️ Twin Registry: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state from central auth manager
     */
    updateAuthState() {
        if (!window.authManager) {
            console.log('⚠️ Twin Registry: No auth manager available');
            return;
        }
        
        try {
            const sessionInfo = window.authManager.getSessionInfo();
            console.log('🔐 Twin Registry: Auth state update:', sessionInfo);
            
            if (sessionInfo && sessionInfo.isAuthenticated) {
                this.isAuthenticated = true;
                this.currentUser = {
                    user_id: sessionInfo.user_id,
                    username: sessionInfo.username,
                    role: sessionInfo.role,
                    organization_id: sessionInfo.organization_id
                };
                this.authToken = window.authManager.getStoredToken();
                console.log('🔐 Twin Registry: User authenticated:', this.currentUser.username);
            } else {
                this.isAuthenticated = false;
                this.currentUser = null;
                this.authToken = null;
                console.log('🔐 Twin Registry: User not authenticated (demo mode)');
            }
        } catch (error) {
            console.warn('⚠️ Twin Registry: Error updating auth state:', error);
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
        }
    }

    /**
     * Setup authentication listeners
     */
    setupAuthListeners() {
        // Listen for auth state changes
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 Twin Registry: Auth state changed, updating...');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
        
        // Listen for login success
        window.addEventListener('loginSuccess', async () => {
            console.log('🔐 Twin Registry: Login success detected');
            this.updateAuthState();
            await this.handleLoginSuccess();
        });
        
        // Listen for logout
        window.addEventListener('logout', () => {
            console.log('🔐 Twin Registry: Logout detected');
            this.updateAuthState();
            this.handleLogout();
        });
    }

    /**
     * Handle login success
     */
    async handleLoginSuccess() {
        // Refresh user-specific data after login
        try {
            await this.loadRegistryData();
            console.log('✅ Twin Registry: User data refreshed after login');
        } catch (error) {
            console.error('❌ Twin Registry: Failed to refresh user data after login:', error);
        }
    }

    /**
     * Handle logout
     */
    handleLogout() {
        // Clear user-specific data
        this.registryData = [];
        this.twinCache.clear();
        this.currentUser = null;
        this.isAuthenticated = false;
        console.log('🔐 Twin Registry: User data cleared after logout');
    }

    /**
     * Handle auth state change
     */
    handleAuthStateChange() {
        if (this.isAuthenticated && this.currentUser) {
            if (this.currentUser.is_demo) {
                // Show demo features prominently
                this.showDemoFeatures();
                this.showLoginPrompt();
            } else {
                // Show authenticated user features
                this.showAuthenticatedFeatures();
                this.hideLoginPrompt();
            }
        } else {
            // Show demo mode
            this.showDemoMode();
        }
    }

    /**
     * Show demo features
     */
    showDemoFeatures() {
        // Highlight impressive demo capabilities
        this.displayMessage(
            '🎉 Experience the full power of Digital Twin management! ' +
            'Create your account to save your work and access advanced features.'
        );
        
        // Show login/signup buttons prominently
        this.showLoginButtons();
    }

    /**
     * Show login buttons
     */
    showLoginButtons() {
        // Add login/signup buttons to the UI
        const loginButton = document.createElement('button');
        loginButton.textContent = 'Sign In to Save Your Work';
        loginButton.className = 'btn btn-primary btn-lg';
        loginButton.onclick = () => window.location.href = '/auth';
        
        const signupButton = document.createElement('button');
        signupButton.textContent = 'Create Free Account';
        signupButton.className = 'btn btn-outline-primary btn-lg';
        signupButton.onclick = () => window.location.href = '/auth?mode=signup';
        
        // Add to prominent location in UI
        this.addProminentButtons(loginButton, signupButton);
    }

    /**
     * Show authenticated features
     */
    showAuthenticatedFeatures() {
        // Hide demo prompts and show authenticated user features
        this.hideLoginPrompt();
        console.log('🔐 Twin Registry: Showing authenticated user features');
    }

    /**
     * Show demo mode
     */
    showDemoMode() {
        // Show demo content and encourage signup
        this.showDemoFeatures();
    }

    /**
     * Hide login prompt
     */
    hideLoginPrompt() {
        // Remove login/signup buttons from UI
        const loginButtons = document.querySelectorAll('.twin-registry-login-buttons');
        loginButtons.forEach(button => button.remove());
    }

    /**
     * Add prominent buttons to UI
     */
    addProminentButtons(loginButton, signupButton) {
        // Add a container for the buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'twin-registry-login-buttons';
        buttonContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        
        buttonContainer.appendChild(loginButton);
        buttonContainer.appendChild(signupButton);
        
        // Add to body
        document.body.appendChild(buttonContainer);
    }

    /**
     * Display message to user
     */
    displayMessage(message) {
        console.log('💬 Twin Registry:', message);
        // You can implement a more sophisticated message display system here
    }

    /**
     * Create demo user context
     */
    createDemoUserContext() {
        return {
            user_id: 'demo-user',
            username: 'demo_user',
            role: 'demo',
            organization_id: null,
            permissions: ['read', 'write', 'manage'],
            is_demo: true
        };
    }

    /**
     * Load demo data
     */
    loadDemoData() {
        return {
            twins: this.getDemoTwins(),
            relationships: this.getDemoRelationships(),
            instances: this.getDemoInstances(),
            statistics: this.getDemoStatistics()
        };
    }

    /**
     * Get demo twins
     */
    getDemoTwins() {
        return [
            {
                twin_id: 'demo-industrial-plant',
                twin_name: 'Industrial Plant Digital Twin',
                twin_type: 'industrial',
                status: 'active',
                description: 'Advanced digital twin for industrial plant monitoring',
                health_score: 95,
                last_update: new Date().toISOString()
            },
            {
                twin_id: 'demo-smart-city',
                twin_name: 'Smart City Infrastructure',
                twin_type: 'urban',
                status: 'active',
                description: 'Comprehensive smart city digital twin system',
                health_score: 92,
                last_update: new Date().toISOString()
            }
        ];
    }

    /**
     * Get demo relationships
     */
    getDemoRelationships() {
        return [
            {
                relationship_id: 'demo-rel-1',
                source_twin: 'demo-industrial-plant',
                target_twin: 'demo-smart-city',
                relationship_type: 'supports',
                description: 'Industrial plant supports smart city infrastructure'
            }
        ];
    }

    /**
     * Get demo instances
     */
    getDemoInstances() {
        return [
            {
                instance_id: 'demo-inst-1',
                twin_id: 'demo-industrial-plant',
                instance_name: 'Plant Alpha Instance',
                status: 'running',
                last_heartbeat: new Date().toISOString()
            }
        ];
    }

    /**
     * Get demo statistics
     */
    getDemoStatistics() {
        return {
            total_twins: 2,
            active_twins: 2,
            total_relationships: 1,
            average_health_score: 93.5,
            last_updated: new Date().toISOString()
        };
    }



    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // ✅ CORRECT: Get token from central auth manager
        if (window.authManager) {
            const token = window.authManager.getStoredToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        
        return headers;
    }

    /**
     * Load registry configuration
     */
    async loadConfiguration() {
        try {
            const response = await fetch(this.config.endpoints.status, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const status = await response.json();
                // Use status data to update config if needed
                console.log('✅ Registry status loaded:', status);
            }
        } catch (error) {
            console.warn('⚠️ Could not load registry status, using defaults:', error);
        }
    }

    /**
     * Load registry data
     */
    async loadRegistryData() {
        try {
            const response = await fetch(this.config.endpoints.twins, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                this.registryData = data.twins || [];
                
                // Update cache
                this.twinCache.clear();
                this.registryData.forEach(twin => {
                    this.twinCache.set(twin.twin_id || twin.id, twin);
                });

                console.log(`📊 Loaded ${this.registryData.length} twins from registry`);
            }
        } catch (error) {
            console.error('❌ Failed to load registry data:', error);
            throw error;
        }
    }

    /**
     * Setup auto-refresh
     */
    setupAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(async () => {
            if (!this.isProcessing) {
                await this.refreshData();
            }
        }, this.config.refreshInterval);
    }

    /**
     * Register a new twin
     * @param {Object} twinData - Twin data to register
     * @returns {Object} Registration result
     */
    async registerTwin(twinData) {
        try {
            console.log('📝 Registering new twin:', twinData.id);

            const response = await fetch(this.config.endpoints.register, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(twinData)
            });

            const result = await response.json();

            if (response.ok) {
                // Add to local cache
                this.twinCache.set(result.twin.id, result.twin);
                this.registryData.push(result.twin);

                console.log('✅ Twin registered successfully:', result.twin.id);
                return { success: true, twin: result.twin };
            } else {
                console.error('❌ Twin registration failed:', result.error);
                return { success: false, error: result.error };
            }

        } catch (error) {
            console.error('❌ Twin registration error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    /**
     * Update an existing twin
     * @param {string} twinId - Twin ID to update
     * @param {Object} updateData - Data to update
     * @returns {Object} Update result
     */
    async updateTwin(twinId, updateData) {
        try {
            console.log('🔄 Updating twin:', twinId);

            const response = await fetch(`${this.config.endpoints.update}/${twinId}`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(updateData)
            });

            const result = await response.json();

            if (response.ok) {
                // Update local cache
                const updatedTwin = { ...this.twinCache.get(twinId), ...result.twin };
                this.twinCache.set(twinId, updatedTwin);

                // Update registry data
                const index = this.registryData.findIndex(t => t.id === twinId);
                if (index !== -1) {
                    this.registryData[index] = updatedTwin;
                }

                console.log('✅ Twin updated successfully:', twinId);
                return { success: true, twin: updatedTwin };
            } else {
                console.error('❌ Twin update failed:', result.error);
                return { success: false, error: result.error };
            }

        } catch (error) {
            console.error('❌ Twin update error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    /**
     * Delete a twin
     * @param {string} twinId - Twin ID to delete
     * @returns {Object} Deletion result
     */
    async deleteTwin(twinId) {
        try {
            console.log('🗑️ Deleting twin:', twinId);

            const response = await fetch(`${this.config.endpoints.delete}/${twinId}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            const result = await response.json();

            if (response.ok) {
                // Remove from local cache
                this.twinCache.delete(twinId);

                // Remove from registry data
                this.registryData = this.registryData.filter(t => t.id !== twinId);

                console.log('✅ Twin deleted successfully:', twinId);
                return { success: true };
            } else {
                console.error('❌ Twin deletion failed:', result.error);
                return { success: false, error: result.error };
            }

        } catch (error) {
            console.error('❌ Twin deletion error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    /**
     * Search twins
     * @param {Object} searchCriteria - Search criteria
     * @returns {Array} Search results
     */
    async searchTwins(searchCriteria) {
        try {
            const response = await fetch(this.config.endpoints.search, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                return result.twins || [];
            } else {
                console.error('❌ Twin search failed');
                return [];
            }

        } catch (error) {
            console.error('❌ Twin search error:', error);
            return [];
        }
    }

    /**
     * Get twin by ID
     * @param {string} twinId - Twin ID
     * @returns {Object|null} Twin data
     */
    getTwinById(twinId) {
        return this.twinCache.get(twinId) || null;
    }

    /**
     * Get all twins
     * @returns {Array} All twins
     */
    getAllTwins() {
        return [...this.registryData];
    }

    /**
     * Get twins by status
     * @param {string} status - Twin status
     * @returns {Array} Filtered twins
     */
    getTwinsByStatus(status) {
        return this.registryData.filter(twin => twin.status === status);
    }

    /**
     * Get twins by type
     * @param {string} type - Twin type
     * @returns {Array} Filtered twins
     */
    getTwinsByType(type) {
        return this.registryData.filter(twin => twin.type === type);
    }

    /**
     * Get registry statistics
     * @returns {Object} Registry statistics
     */
    getRegistryStats() {
        const stats = {
            total: this.registryData.length,
            byStatus: {},
            byType: {},
            byProject: {}
        };

        this.registryData.forEach(twin => {
            // Count by status
            stats.byStatus[twin.status] = (stats.byStatus[twin.status] || 0) + 1;
            
            // Count by type
            stats.byType[twin.type] = (stats.byType[twin.type] || 0) + 1;
            
            // Count by project
            if (twin.project) {
                stats.byProject[twin.project] = (stats.byProject[twin.project] || 0) + 1;
            }
        });

        return stats;
    }

    /**
     * Add twin to registration queue
     * @param {Object} twinData - Twin data
     */
    addToRegistrationQueue(twinData) {
        this.registrationQueue.push({
            data: twinData,
            timestamp: Date.now(),
            retries: 0
        });
    }

    /**
     * Process registration queue
     */
    async processRegistrationQueue() {
        if (this.isProcessing || this.registrationQueue.length === 0) {
            return;
        }

        this.isProcessing = true;

        try {
            const queue = [...this.registrationQueue];
            this.registrationQueue = [];

            for (const item of queue) {
                try {
                    const result = await this.registerTwin(item.data);
                    if (!result.success && item.retries < this.config.maxRetries) {
                        item.retries++;
                        this.registrationQueue.push(item);
                    }
                } catch (error) {
                    console.error('❌ Failed to process queued registration:', error);
                    if (item.retries < this.config.maxRetries) {
                        item.retries++;
                        this.registrationQueue.push(item);
                    }
                }

                // Add delay between retries
                if (item.retries > 0) {
                    await new Promise(resolve => setTimeout(resolve, this.config.retryDelay));
                }
            }

        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Get registry status
     * @returns {Object} Registry status
     */
    async getRegistryStatus() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/status`, {
                headers: this.getAuthHeaders()
            });
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('❌ Failed to get registry status:', error);
        }

        return {
            status: 'unknown',
            message: 'Unable to determine registry status'
        };
    }

    /**
     * Refresh registry data
     */
    async refreshData() {
        try {
            await this.loadRegistryData();
            await this.processRegistrationQueue();
        } catch (error) {
            console.error('❌ Failed to refresh registry data:', error);
        }
    }

    /**
     * Get registry configuration
     * @returns {Object} Configuration
     */
    getConfiguration() {
        return this.config;
    }

    /**
     * Update registry configuration
     * @param {Object} newConfig - New configuration
     */
    updateConfiguration(newConfig) {
        this.config = { ...this.config, ...newConfig };
        this.setupAutoRefresh();
    }

    /**
     * Destroy Twin Registry Core
     */
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.twinCache.clear();
        this.registrationQueue = [];
        this.isInitialized = false;
        console.log('🧹 Twin Registry Core destroyed');
    }
} 