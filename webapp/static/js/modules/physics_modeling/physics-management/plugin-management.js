/**
 * Physics Modeling Plugin Management
 * Handles plugin installation, configuration, and lifecycle management
 */

export class PluginManager {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.availablePlugins = [];
        this.installedPlugins = [];
        this.pluginCategories = [
            'thermal',
            'structural',
            'fluid',
            'electromagnetic',
            'mechanical',
            'chemical',
            'multiphysics'
        ];
        this.pluginConfig = {
            maxPlugins: 50,
            autoUpdateEnabled: true,
            pluginTimeout: 300000, // 5 minutes
            maxConcurrentInstalls: 3
        };
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Plugin Manager: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Plugin Manager: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Plugin Manager: Auth system ready event received');
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
                console.warn('⚠️ Plugin Manager: Timeout waiting for auth system');
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
            console.log('🔐 Plugin Manager: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Plugin Manager: No auth manager available');
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
        this.availablePlugins = [];
        this.installedPlugins = [];
        console.log('🧹 Plugin Manager: Sensitive data cleared');
    }

    /**
     * Get authentication headers
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
     * Initialize the plugin manager
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔐 Initializing Plugin Manager...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Load plugin configuration
            await this.loadPluginConfiguration();
            
            // Load available and installed plugins
            await this.loadAvailablePlugins();
            await this.loadInstalledPlugins();
            
            this.isInitialized = true;
            console.log('✅ Plugin Manager initialized');
            
        } catch (error) {
            console.error('❌ Plugin Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load plugin configuration
     */
    async loadPluginConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/plugins/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.pluginConfig = { ...this.pluginConfig, ...config };
                console.log('✅ Plugin configuration loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load plugin config, using defaults:', error);
        }
    }

    /**
     * Load available plugins
     */
    async loadAvailablePlugins() {
        try {
            const response = await fetch('/api/physics-modeling/plugins/available', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                this.availablePlugins = await response.json();
                console.log(`✅ Loaded ${this.availablePlugins.length} available plugins`);
            } else {
                // Fallback to mock data
                this.loadMockAvailablePlugins();
            }
        } catch (error) {
            console.warn('⚠️ Could not load available plugins, using mock data:', error);
            this.loadMockAvailablePlugins();
        }
    }

    /**
     * Load installed plugins
     */
    async loadInstalledPlugins() {
        try {
            const response = await fetch('/api/physics-modeling/plugins/installed', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                this.installedPlugins = await response.json();
                console.log(`✅ Loaded ${this.installedPlugins.length} installed plugins`);
            } else {
                // Fallback to mock data
                this.loadMockInstalledPlugins();
            }
        } catch (error) {
            console.warn('⚠️ Could not load installed plugins, using mock data:', error);
            this.loadMockInstalledPlugins();
        }
    }

    /**
     * Install a plugin
     */
    async installPlugin(pluginId) {
        try {
            console.log(`🔌 Installing plugin: ${pluginId}`);
            
            // Check if plugin is already installed
            if (this.isPluginInstalled(pluginId)) {
                throw new Error('Plugin is already installed');
            }
            
            // Check if we can install more plugins
            if (this.installedPlugins.length >= this.pluginConfig.maxPlugins) {
                throw new Error('Maximum number of plugins reached');
            }
            
            // Find plugin details
            const plugin = this.availablePlugins.find(p => p.id === pluginId);
            if (!plugin) {
                throw new Error('Plugin not found');
            }
            
            // Make API call to install plugin
            const response = await fetch('/api/physics-modeling/plugins/install', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ pluginId: pluginId })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to install plugin: ${response.statusText}`);
            }
            
            // Add to installed plugins
            const installedPlugin = {
                ...plugin,
                installedAt: new Date().toISOString(),
                status: 'active',
                version: plugin.version || '1.0.0'
            };
            
            this.installedPlugins.push(installedPlugin);
            
            // Emit event
            if (window.PhysicsModeling) {
                window.PhysicsModeling.events.emit('pluginInstalled', installedPlugin);
            }
            
            console.log(`✅ Plugin ${pluginId} installed successfully`);
            return installedPlugin;
            
        } catch (error) {
            console.error(`❌ Error installing plugin ${pluginId}:`, error);
            throw error;
        }
    }

    /**
     * Uninstall a plugin
     */
    async uninstallPlugin(pluginId) {
        try {
            console.log(`🗑️ Uninstalling plugin: ${pluginId}`);
            
            // Check if plugin is installed
            if (!this.isPluginInstalled(pluginId)) {
                throw new Error('Plugin is not installed');
            }
            
            // Make API call to uninstall plugin
            const response = await fetch('/api/physics-modeling/plugins/uninstall', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ pluginId: pluginId })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to uninstall plugin: ${response.statusText}`);
            }
            
            // Remove from installed plugins
            this.installedPlugins = this.installedPlugins.filter(p => p.id !== pluginId);
            
            console.log(`✅ Plugin ${pluginId} uninstalled successfully`);
            
        } catch (error) {
            console.error(`❌ Error uninstalling plugin ${pluginId}:`, error);
            throw error;
        }
    }

    /**
     * Update a plugin
     */
    async updatePlugin(pluginId) {
        try {
            console.log(`🔄 Updating plugin: ${pluginId}`);
            
            // Check if plugin is installed
            if (!this.isPluginInstalled(pluginId)) {
                throw new Error('Plugin is not installed');
            }
            
            // Make API call to update plugin
            const response = await fetch('/api/physics-modeling/plugins/update', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ pluginId: pluginId })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to update plugin: ${response.statusText}`);
            }
            
            // Update plugin version
            const plugin = this.installedPlugins.find(p => p.id === pluginId);
            if (plugin) {
                plugin.version = response.json().version || plugin.version;
                plugin.updatedAt = new Date().toISOString();
            }
            
            console.log(`✅ Plugin ${pluginId} updated successfully`);
            
        } catch (error) {
            console.error(`❌ Error updating plugin ${pluginId}:`, error);
            throw error;
        }
    }

    /**
     * Enable/disable a plugin
     */
    async togglePluginStatus(pluginId, enabled) {
        try {
            console.log(`${enabled ? '✅' : '❌'} ${enabled ? 'Enabling' : 'Disabling'} plugin: ${pluginId}`);
            
            // Check if plugin is installed
            if (!this.isPluginInstalled(pluginId)) {
                throw new Error('Plugin is not installed');
            }
            
            // Make API call to toggle plugin status
            const response = await fetch('/api/physics-modeling/plugins/toggle', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ 
                    pluginId: pluginId, 
                    enabled: enabled 
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to toggle plugin status: ${response.statusText}`);
            }
            
            // Update plugin status
            const plugin = this.installedPlugins.find(p => p.id === pluginId);
            if (plugin) {
                plugin.status = enabled ? 'active' : 'disabled';
            }
            
            console.log(`✅ Plugin ${pluginId} ${enabled ? 'enabled' : 'disabled'} successfully`);
            
        } catch (error) {
            console.error(`❌ Error toggling plugin ${pluginId} status:`, error);
            throw error;
        }
    }

    /**
     * Get plugin by ID
     */
    getPluginById(pluginId) {
        const installed = this.installedPlugins.find(p => p.id === pluginId);
        if (installed) return installed;
        
        return this.availablePlugins.find(p => p.id === pluginId);
    }

    /**
     * Check if plugin is installed
     */
    isPluginInstalled(pluginId) {
        return this.installedPlugins.some(p => p.id === pluginId);
    }

    /**
     * Get plugins by category
     */
    getPluginsByCategory(category) {
        return this.availablePlugins.filter(p => p.category === category);
    }

    /**
     * Get active plugins
     */
    getActivePlugins() {
        return this.installedPlugins.filter(p => p.status === 'active');
    }

    /**
     * Get disabled plugins
     */
    getDisabledPlugins() {
        return this.installedPlugins.filter(p => p.status === 'disabled');
    }

    /**
     * Search plugins
     */
    searchPlugins(query) {
        const searchTerm = query.toLowerCase();
        return this.availablePlugins.filter(plugin => 
            plugin.name.toLowerCase().includes(searchTerm) ||
            plugin.description.toLowerCase().includes(searchTerm) ||
            plugin.category.toLowerCase().includes(searchTerm)
        );
    }

    /**
     * Get plugin statistics
     */
    getPluginStatistics() {
        const totalAvailable = this.availablePlugins.length;
        const totalInstalled = this.installedPlugins.length;
        const activePlugins = this.getActivePlugins().length;
        const disabledPlugins = this.getDisabledPlugins().length;
        
        const categoryStats = {};
        this.pluginCategories.forEach(category => {
            categoryStats[category] = this.availablePlugins.filter(p => p.category === category).length;
        });
        
        return {
            totalAvailable,
            totalInstalled,
            activePlugins,
            disabledPlugins,
            categoryStats,
            installRate: totalAvailable > 0 ? (totalInstalled / totalAvailable * 100).toFixed(1) : 0
        };
    }

    /**
     * Mock data methods
     */
    loadMockAvailablePlugins() {
        this.availablePlugins = [
            {
                id: 'thermal-plugin-001',
                name: 'Advanced Thermal Analysis',
                category: 'thermal',
                description: 'High-precision thermal simulation with advanced heat transfer models',
                version: '2.1.0',
                author: 'Thermal Dynamics Inc.',
                size: '15.2 MB',
                downloads: 1250,
                rating: 4.8
            },
            {
                id: 'structural-plugin-001',
                name: 'Structural Mechanics Pro',
                category: 'structural',
                description: 'Comprehensive structural analysis with finite element methods',
                version: '1.9.5',
                author: 'Structural Solutions',
                size: '22.8 MB',
                downloads: 980,
                rating: 4.6
            },
            {
                id: 'fluid-plugin-001',
                name: 'Fluid Dynamics Suite',
                category: 'fluid',
                description: 'Advanced fluid flow simulation with turbulence modeling',
                version: '3.0.2',
                author: 'Fluid Dynamics Lab',
                size: '18.5 MB',
                downloads: 750,
                rating: 4.9
            },
            {
                id: 'electromagnetic-plugin-001',
                name: 'EM Field Simulator',
                category: 'electromagnetic',
                description: 'Electromagnetic field analysis and wave propagation',
                version: '2.5.1',
                author: 'EM Technologies',
                size: '12.3 MB',
                downloads: 420,
                rating: 4.7
            },
            {
                id: 'mechanical-plugin-001',
                name: 'Mechanical Assembly Analyzer',
                category: 'mechanical',
                description: 'Mechanical system analysis with motion and stress simulation',
                version: '1.8.3',
                author: 'Mechanical Systems Corp',
                size: '16.7 MB',
                downloads: 680,
                rating: 4.5
            },
            {
                id: 'chemical-plugin-001',
                name: 'Chemical Process Simulator',
                category: 'chemical',
                description: 'Chemical reaction modeling and process optimization',
                version: '2.3.0',
                author: 'Chemical Dynamics',
                size: '14.1 MB',
                downloads: 320,
                rating: 4.4
            }
        ];
    }

    loadMockInstalledPlugins() {
        this.installedPlugins = [
            {
                id: 'thermal-plugin-001',
                name: 'Advanced Thermal Analysis',
                category: 'thermal',
                description: 'High-precision thermal simulation with advanced heat transfer models',
                version: '2.1.0',
                author: 'Thermal Dynamics Inc.',
                status: 'active',
                installedAt: '2024-01-15T10:00:00Z',
                size: '15.2 MB'
            },
            {
                id: 'structural-plugin-001',
                name: 'Structural Mechanics Pro',
                category: 'structural',
                description: 'Comprehensive structural analysis with finite element methods',
                version: '1.9.5',
                author: 'Structural Solutions',
                status: 'active',
                installedAt: '2024-01-15T11:00:00Z',
                size: '22.8 MB'
            }
        ];
    }

    /**
     * Cleanup
     */
    destroy() {
        this.availablePlugins = [];
        this.installedPlugins = [];
        this.isInitialized = false;
        console.log('🧹 Plugin Manager destroyed');
    }
}
