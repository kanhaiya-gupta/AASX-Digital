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
        this.config = {
            apiBaseUrl: '/api/twin-registry',
            endpoints: {
                twins: '/twins',
                register: '/register',
                update: '/update',
                delete: '/delete',
                search: '/search',
                status: '/status',
                health: '/health',
                performance: '/performance'
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
     * Load registry configuration
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('⚠️ Could not load registry config, using defaults:', error);
        }
    }

    /**
     * Load registry data
     */
    async loadRegistryData() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.twins}`);
            if (response.ok) {
                const data = await response.json();
                this.registryData = data.twins || [];
                
                // Update cache
                this.twinCache.clear();
                this.registryData.forEach(twin => {
                    this.twinCache.set(twin.id, twin);
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

            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.register}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
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

            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.update}/${twinId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
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

            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.delete}/${twinId}`, {
                method: 'DELETE'
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
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.search}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchCriteria)
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
            const response = await fetch(`${this.config.apiBaseUrl}${this.config.endpoints.status}`);
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