/**
 * Plugin Management UI Component
 * Handles plugin installation, configuration, and lifecycle management
 */

export class PluginManagementUIComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.availablePlugins = [];
        this.installedPlugins = [];
        this.pluginCategories = [
            'fluid-dynamics',
            'structural-analysis',
            'thermal-analysis',
            'electromagnetic',
            'optimization',
            'visualization'
        ];
        this.pluginConfig = {
            autoUpdate: true,
            enableExperimental: false,
            maxConcurrentInstalls: 3
        };
        
        // UI elements
        this.elements = {
            pluginContainer: null,
            availablePluginsList: null,
            installedPluginsList: null,
            pluginDetails: null,
            installProgress: null,
            categoryFilter: null
        };
        
        // Event listeners
        this.eventListeners = [];
    }

    // Central Authentication Methods
    async waitForAuthSystem() {
        return new Promise((resolve) => {
            if (window.authSystemReady && window.authManager) {
                resolve();
            } else {
                const handleReady = () => {
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                };
                window.addEventListener('authSystemReady', handleReady);
            }
        });
    }

    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated;
            this.currentUser = window.authManager.currentUser;
            this.authToken = window.authManager.getStoredToken();
        }
    }

    setupAuthListeners() {
        const handleAuthChange = () => {
            this.updateAuthState();
            this.handleAuthStateChange();
        };

        window.addEventListener('authStateChanged', handleAuthChange);
        window.addEventListener('loginSuccess', handleAuthChange);
        window.addEventListener('logout', handleAuthChange);

        this.eventListeners.push(
            { event: 'authStateChanged', handler: handleAuthChange },
            { event: 'loginSuccess', handler: handleAuthChange },
            { event: 'logout', handler: handleAuthChange }
        );
    }

    handleAuthStateChange() {
        if (this.isAuthenticated) {
            this.loadUserPlugins();
            this.enableAuthenticatedFeatures();
        } else {
            this.loadDemoPlugins();
            this.disableAuthenticatedFeatures();
        }
    }

    clearSensitiveData() {
        this.currentUser = null;
        this.authToken = null;
        this.isAuthenticated = false;
    }

    getAuthHeaders() {
        return this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {};
    }

    async init() {
        if (this.isInitialized) return;
        
        console.log('🔐 Initializing Plugin Management UI Component...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.initializeUI();
            this.setupEventListeners();
            await this.loadPluginConfiguration();
            
            this.isInitialized = true;
            console.log('✅ Plugin Management UI Component initialized');
        } catch (error) {
            console.error('❌ Plugin Management UI Component initialization failed:', error);
            throw error;
        }
    }

    initializeUI() {
        // Initialize UI elements
        this.elements.pluginContainer = document.getElementById('plugin-management-container');
        this.elements.availablePluginsList = document.getElementById('available-plugins-list');
        this.elements.installedPluginsList = document.getElementById('installed-plugins-list');
        this.elements.pluginDetails = document.getElementById('plugin-details');
        this.elements.installProgress = document.getElementById('install-progress');
        this.elements.categoryFilter = document.getElementById('plugin-category-filter');

        if (!this.elements.pluginContainer) {
            console.warn('⚠️ Plugin management container not found');
            return;
        }

        // Initialize category filter
        this.initializeCategoryFilter();
    }

    initializeCategoryFilter() {
        if (!this.elements.categoryFilter) return;

        const filterHtml = `
            <option value="">All Categories</option>
            ${this.pluginCategories.map(category => 
                `<option value="${category}">${category.replace('-', ' ').toUpperCase()}</option>`
            ).join('')}
        `;

        this.elements.categoryFilter.innerHTML = filterHtml;
    }

    setupEventListeners() {
        // Category filter change
        if (this.elements.categoryFilter) {
            this.elements.categoryFilter.addEventListener('change', (e) => {
                this.filterPluginsByCategory(e.target.value);
            });
        }

        // Search functionality
        const searchInput = document.getElementById('plugin-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchPlugins(e.target.value);
            });
        }

        // Refresh plugins button
        const refreshBtn = document.getElementById('refresh-plugins');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshPlugins());
        }
    }

    async loadPluginConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/plugins/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.pluginConfig = { ...this.pluginConfig, ...config };
                this.updateConfigurationUI();
            }
        } catch (error) {
            console.error('❌ Failed to load plugin configuration:', error);
        }
    }

    updateConfigurationUI() {
        const autoUpdateCheckbox = document.getElementById('auto-update-plugins');
        if (autoUpdateCheckbox) {
            autoUpdateCheckbox.checked = this.pluginConfig.autoUpdate;
        }

        const experimentalCheckbox = document.getElementById('enable-experimental');
        if (experimentalCheckbox) {
            experimentalCheckbox.checked = this.pluginConfig.enableExperimental;
        }
    }

    async loadAvailablePlugins() {
        try {
            const response = await fetch('/api/physics-modeling/plugins/available', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.availablePlugins = data.plugins || [];
                this.displayAvailablePlugins();
            }
        } catch (error) {
            console.error('❌ Failed to load available plugins:', error);
        }
    }

    async loadInstalledPlugins() {
        try {
            const response = await fetch('/api/physics-modeling/plugins/installed', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.installedPlugins = data.plugins || [];
                this.displayInstalledPlugins();
            }
        } catch (error) {
            console.error('❌ Failed to load installed plugins:', error);
        }
    }

    displayAvailablePlugins() {
        if (!this.elements.availablePluginsList) return;

        const pluginsHtml = this.availablePlugins.map(plugin => `
            <div class="plugin-item" data-plugin-id="${plugin.id}" data-category="${plugin.category}">
                <div class="plugin-header">
                    <h5 class="plugin-name">${plugin.name}</h5>
                    <span class="plugin-version">v${plugin.version}</span>
                </div>
                <div class="plugin-description">${plugin.description}</div>
                <div class="plugin-meta">
                    <span class="plugin-category">${plugin.category}</span>
                    <span class="plugin-size">${plugin.size}</span>
                    <span class="plugin-downloads">${plugin.downloads} downloads</span>
                </div>
                <div class="plugin-actions">
                    <button onclick="installPlugin('${plugin.id}')" class="btn btn-sm btn-primary">Install</button>
                    <button onclick="viewPluginDetails('${plugin.id}')" class="btn btn-sm btn-secondary">Details</button>
                </div>
            </div>
        `).join('');

        this.elements.availablePluginsList.innerHTML = pluginsHtml;
    }

    displayInstalledPlugins() {
        if (!this.elements.installedPluginsList) return;

        const pluginsHtml = this.installedPlugins.map(plugin => `
            <div class="plugin-item installed" data-plugin-id="${plugin.id}">
                <div class="plugin-header">
                    <h5 class="plugin-name">${plugin.name}</h5>
                    <span class="plugin-version">v${plugin.version}</span>
                    <span class="plugin-status ${plugin.status}">${plugin.status}</span>
                </div>
                <div class="plugin-description">${plugin.description}</div>
                <div class="plugin-meta">
                    <span class="plugin-category">${plugin.category}</span>
                    <span class="plugin-installed-date">Installed: ${new Date(plugin.installedAt).toLocaleDateString()}</span>
                </div>
                <div class="plugin-actions">
                    <button onclick="configurePlugin('${plugin.id}')" class="btn btn-sm btn-primary">Configure</button>
                    <button onclick="updatePlugin('${plugin.id}')" class="btn btn-sm btn-warning">Update</button>
                    <button onclick="uninstallPlugin('${plugin.id}')" class="btn btn-sm btn-danger">Uninstall</button>
                </div>
            </div>
        `).join('');

        this.elements.installedPluginsList.innerHTML = pluginsHtml;
    }

    async installPlugin(pluginId) {
        try {
            this.showInstallProgress(pluginId, 'Installing...');
            
            const response = await fetch(`/api/physics-modeling/plugins/${pluginId}/install`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                this.showInstallProgress(pluginId, 'Installed successfully');
                this.loadInstalledPlugins();
                this.loadAvailablePlugins();
            } else {
                throw new Error('Installation failed');
            }
        } catch (error) {
            console.error('❌ Failed to install plugin:', error);
            this.showInstallProgress(pluginId, 'Installation failed');
        }
    }

    async uninstallPlugin(pluginId) {
        if (!confirm('Are you sure you want to uninstall this plugin?')) return;

        try {
            this.showInstallProgress(pluginId, 'Uninstalling...');
            
            const response = await fetch(`/api/physics-modeling/plugins/${pluginId}/uninstall`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.showInstallProgress(pluginId, 'Uninstalled successfully');
                this.loadInstalledPlugins();
                this.loadAvailablePlugins();
            } else {
                throw new Error('Uninstallation failed');
            }
        } catch (error) {
            console.error('❌ Failed to uninstall plugin:', error);
            this.showInstallProgress(pluginId, 'Uninstallation failed');
        }
    }

    async updatePlugin(pluginId) {
        try {
            this.showInstallProgress(pluginId, 'Updating...');
            
            const response = await fetch(`/api/physics-modeling/plugins/${pluginId}/update`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.showInstallProgress(pluginId, 'Updated successfully');
                this.loadInstalledPlugins();
            } else {
                throw new Error('Update failed');
            }
        } catch (error) {
            console.error('❌ Failed to update plugin:', error);
            this.showInstallProgress(pluginId, 'Update failed');
        }
    }

    showInstallProgress(pluginId, message) {
        if (!this.elements.installProgress) return;

        this.elements.installProgress.innerHTML = `
            <div class="install-progress-item">
                <span class="plugin-name">${pluginId}</span>
                <span class="progress-message">${message}</span>
            </div>
        `;

        // Clear progress after 3 seconds
        setTimeout(() => {
            if (this.elements.installProgress) {
                this.elements.installProgress.innerHTML = '';
            }
        }, 3000);
    }

    async viewPluginDetails(pluginId) {
        try {
            const response = await fetch(`/api/physics-modeling/plugins/${pluginId}/details`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const plugin = await response.json();
                this.displayPluginDetails(plugin);
            }
        } catch (error) {
            console.error('❌ Failed to load plugin details:', error);
        }
    }

    displayPluginDetails(plugin) {
        if (!this.elements.pluginDetails) return;

        const detailsHtml = `
            <div class="plugin-details">
                <div class="plugin-details-header">
                    <h4>${plugin.name}</h4>
                    <button onclick="closePluginDetails()" class="btn btn-sm btn-secondary">Close</button>
                </div>
                <div class="plugin-details-content">
                    <div class="detail-section">
                        <h5>Description</h5>
                        <p>${plugin.description}</p>
                    </div>
                    <div class="detail-section">
                        <h5>Version Information</h5>
                        <ul>
                            <li><strong>Current Version:</strong> ${plugin.version}</li>
                            <li><strong>Latest Version:</strong> ${plugin.latestVersion}</li>
                            <li><strong>Release Date:</strong> ${new Date(plugin.releaseDate).toLocaleDateString()}</li>
                        </ul>
                    </div>
                    <div class="detail-section">
                        <h5>Requirements</h5>
                        <ul>
                            <li><strong>Minimum Version:</strong> ${plugin.requirements.minVersion}</li>
                            <li><strong>Dependencies:</strong> ${plugin.requirements.dependencies.join(', ') || 'None'}</li>
                        </ul>
                    </div>
                    <div class="detail-section">
                        <h5>Features</h5>
                        <ul>
                            ${plugin.features.map(feature => `<li>${feature}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;

        this.elements.pluginDetails.innerHTML = detailsHtml;
    }

    filterPluginsByCategory(category) {
        const pluginItems = document.querySelectorAll('.plugin-item');
        
        pluginItems.forEach(item => {
            const itemCategory = item.getAttribute('data-category');
            if (!category || itemCategory === category) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    searchPlugins(query) {
        const pluginItems = document.querySelectorAll('.plugin-item');
        const searchTerm = query.toLowerCase();
        
        pluginItems.forEach(item => {
            const pluginName = item.querySelector('.plugin-name').textContent.toLowerCase();
            const pluginDescription = item.querySelector('.plugin-description').textContent.toLowerCase();
            
            if (pluginName.includes(searchTerm) || pluginDescription.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async refreshPlugins() {
        try {
            await Promise.all([
                this.loadAvailablePlugins(),
                this.loadInstalledPlugins()
            ]);
            console.log('✅ Plugins refreshed');
        } catch (error) {
            console.error('❌ Failed to refresh plugins:', error);
        }
    }

    async loadUserPlugins() {
        await Promise.all([
            this.loadAvailablePlugins(),
            this.loadInstalledPlugins()
        ]);
    }

    async loadDemoPlugins() {
        try {
            const response = await fetch('/api/physics-modeling/plugins/demo');
            
            if (response.ok) {
                const data = await response.json();
                this.availablePlugins = data.available || [];
                this.installedPlugins = data.installed || [];
                this.displayAvailablePlugins();
                this.displayInstalledPlugins();
            }
        } catch (error) {
            console.error('❌ Failed to load demo plugins:', error);
        }
    }

    enableAuthenticatedFeatures() {
        // Enable features that require authentication
        const authOnlyElements = document.querySelectorAll('[data-auth-only]');
        authOnlyElements.forEach(element => {
            element.disabled = false;
            element.style.display = 'block';
        });
    }

    disableAuthenticatedFeatures() {
        // Disable features that require authentication
        const authOnlyElements = document.querySelectorAll('[data-auth-only]');
        authOnlyElements.forEach(element => {
            element.disabled = true;
            element.style.display = 'none';
        });
    }

    async cleanup() {
        console.log('🧹 Cleaning up Plugin Management UI Component...');
        
        // Remove event listeners
        this.eventListeners.forEach(({ event, handler }) => {
            window.removeEventListener(event, handler);
        });
        
        // Clear sensitive data
        this.clearSensitiveData();
        
        this.isInitialized = false;
        console.log('✅ Plugin Management UI Component cleaned up');
    }

    async refresh() {
        if (this.isAuthenticated) {
            await this.loadUserPlugins();
        } else {
            await this.loadDemoPlugins();
        }
    }
}
