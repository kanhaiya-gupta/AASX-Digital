/**
 * Twin Registry Configuration Management Module
 * Handles system configuration functionality with central authentication integration
 */

export default class TwinRegistryConfiguration {
    constructor() {
        this.isInitialized = false;
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        this.configurationData = {
            system: {},
            security: {},
            performance: {},
            notifications: {},
            integrations: {}
        };
        
        // Configuration specific element IDs
        this.elementIds = {
            systemConfig: 'twin_registry_systemConfig',
            securityConfig: 'twin_registry_securityConfig',
            performanceConfig: 'twin_registry_performanceConfig',
            notificationConfig: 'twin_registry_notificationConfig',
            integrationConfig: 'twin_registry_integrationConfig',
            saveBtn: 'twin_registry_configSaveBtn',
            resetBtn: 'twin_registry_configResetBtn',
            refreshBtn: 'twin_registry_configRefreshBtn',
            exportBtn: 'twin_registry_configExportBtn',
            importBtn: 'twin_registry_configImportBtn'
        };
        
        this.originalConfig = {};
        this.hasChanges = false;
        this.autoSaveInterval = null;
    }

    /**
     * Initialize Configuration Management
     */
    async init() {
        console.log('⚙️ Initializing Twin Registry Configuration Management...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial configuration
            await this.loadConfiguration();
            
            // Setup auto-save
            this.setupAutoSave();
            
            this.isInitialized = true;
            console.log('✅ Twin Registry Configuration Management initialized');
            
        } catch (error) {
            console.error('❌ Twin Registry Configuration Management initialization failed:', error);
            throw error;
        }
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Registry Configuration: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Registry Configuration: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Registry Configuration: Auth system ready event received');
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
                console.warn('⚠️ Twin Registry Configuration: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state from central auth manager
     */
    updateAuthState() {
        if (!window.authManager) {
            console.log('⚠️ Twin Registry Configuration: No auth manager available');
            return;
        }
        
        try {
            // Check if new auth system is available
            if (typeof window.authManager.getSessionInfo === 'function') {
                const sessionInfo = window.authManager.getSessionInfo();
                console.log('🔐 Twin Registry Configuration: Auth state update (new system):', sessionInfo);
                
                if (sessionInfo && sessionInfo.isAuthenticated) {
                    this.isAuthenticated = true;
                    this.currentUser = {
                        user_id: sessionInfo.user_id,
                        username: sessionInfo.username,
                        role: sessionInfo.role,
                        organization_id: sessionInfo.organization_id
                    };
                    this.authToken = window.authManager.getStoredToken();
                    console.log('🔐 Twin Registry Configuration: User authenticated:', this.currentUser.username);
                } else {
                    this.isAuthenticated = false;
                    this.currentUser = null;
                    this.authToken = null;
                    console.log('🔐 Twin Registry Configuration: User not authenticated');
                }
            } else if (typeof window.authManager.isAuthenticated === 'function') {
                // Fallback to old auth system
                const isAuthenticated = window.authManager.isAuthenticated();
                console.log('🔐 Twin Registry Configuration: Auth state update (old system):', isAuthenticated);
                
                if (isAuthenticated) {
                    this.isAuthenticated = true;
                    this.currentUser = {
                        user_id: 'unknown',
                        username: 'authenticated_user',
                        role: 'user',
                        organization_id: 'unknown'
                    };
                    this.authToken = window.authManager.getStoredToken();
                    console.log('🔐 Twin Registry Configuration: User authenticated (legacy)');
                } else {
                    this.isAuthenticated = false;
                    this.currentUser = null;
                    this.authToken = null;
                    console.log('🔐 Twin Registry Configuration: User not authenticated (legacy)');
                }
            } else {
                console.log('⚠️ Twin Registry Configuration: Unknown auth manager API');
                this.isAuthenticated = false;
                this.currentUser = null;
                this.authToken = null;
            }
        } catch (error) {
            console.warn('⚠️ Twin Registry Configuration: Error updating auth state:', error);
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
            console.log('🔄 Twin Registry Configuration: Auth state changed, updating...');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
        
        // Listen for login success
        window.addEventListener('loginSuccess', async () => {
            console.log('🔐 Twin Registry Configuration: Login success detected');
            this.updateAuthState();
            await this.handleLoginSuccess();
        });
        
        // Listen for logout
        window.addEventListener('logout', () => {
            console.log('🔐 Twin Registry Configuration: Logout detected');
            this.updateAuthState();
            this.handleLogout();
        });
    }

    /**
     * Handle login success
     */
    async handleLoginSuccess() {
        try {
            await this.loadConfiguration();
            console.log('✅ Twin Registry Configuration: User data refreshed after login');
        } catch (error) {
            console.error('❌ Twin Registry Configuration: Failed to refresh user data after login:', error);
        }
    }

    /**
     * Handle logout
     */
    handleLogout() {
        this.configurationData = {
            system: {},
            security: {},
            performance: {},
            notifications: {},
            integrations: {}
        };
        this.currentUser = null;
        this.isAuthenticated = false;
        this.hasChanges = false;
        console.log('🔐 Twin Registry Configuration: User data cleared after logout');
    }

    /**
     * Handle auth state change
     */
    handleAuthStateChange() {
        if (this.isAuthenticated && this.currentUser) {
            this.showAuthenticatedFeatures();
        } else {
            this.showDemoMode();
        }
    }

    /**
     * Show authenticated user features
     */
    showAuthenticatedFeatures() {
        console.log('🔐 Twin Registry Configuration: Showing authenticated user features');
        // Enable full configuration functionality
        this.enableConfigurationEditing();
    }

    /**
     * Show demo mode
     */
    showDemoMode() {
        console.log('🔐 Twin Registry Configuration: Showing demo mode');
        // Show limited demo functionality
        this.disableConfigurationEditing();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Save button
        const saveBtn = document.getElementById(this.elementIds.saveBtn);
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveConfiguration());
        }

        // Reset button
        const resetBtn = document.getElementById(this.elementIds.resetBtn);
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetConfiguration());
        }

        // Refresh button
        const refreshBtn = document.getElementById(this.elementIds.refreshBtn);
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadConfiguration());
        }

        // Export button
        const exportBtn = document.getElementById(this.elementIds.exportBtn);
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportConfiguration());
        }

        // Import button
        const importBtn = document.getElementById(this.elementIds.importBtn);
        if (importBtn) {
            importBtn.addEventListener('click', () => this.importConfiguration());
        }

        // Listen for custom refresh events
        window.addEventListener('twinRegistryRefresh', () => {
            this.loadConfiguration();
        });

        // Setup form change listeners
        this.setupFormChangeListeners();
    }

    /**
     * Setup form change listeners
     */
    setupFormChangeListeners() {
        // Listen for changes in configuration forms
        const configForms = document.querySelectorAll('.twin-registry-config-form');
        configForms.forEach(form => {
            form.addEventListener('change', () => {
                this.markAsChanged();
            });
        });
    }

    /**
     * Mark configuration as changed
     */
    markAsChanged() {
        this.hasChanges = true;
        this.updateSaveButtonState();
    }

    /**
     * Update save button state
     */
    updateSaveButtonState() {
        const saveBtn = document.getElementById(this.elementIds.saveBtn);
        if (saveBtn) {
            saveBtn.disabled = !this.hasChanges;
            saveBtn.classList.toggle('btn-primary', this.hasChanges);
            saveBtn.classList.toggle('btn-secondary', !this.hasChanges);
        }
    }

    /**
     * Load configuration
     */
    async loadConfiguration() {
        try {
            console.log('⚙️ Loading configuration...');
            this.showLoading();
            
            // Load system configuration
            await this.loadSystemConfiguration();
            
            // Load security configuration
            await this.loadSecurityConfiguration();
            
            // Load performance configuration
            await this.loadPerformanceConfiguration();
            
            // Load notification configuration
            await this.loadNotificationConfiguration();
            
            // Load integration configuration
            await this.loadIntegrationConfiguration();
            
            // Store original configuration
            this.originalConfig = JSON.parse(JSON.stringify(this.configurationData));
            
            // Update UI
            this.updateConfigurationDisplay();
            
            // Reset change tracking
            this.hasChanges = false;
            this.updateSaveButtonState();
            
            this.hideLoading();
            console.log('✅ Configuration loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load configuration:', error);
            this.hideLoading();
            this.showError('Failed to load configuration. Please try again.');
        }
    }

    /**
     * Load system configuration
     */
    async loadSystemConfiguration() {
        try {
            const response = await fetch('/api/twin-registry/configuration/system', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.configurationData.system = data;
            }
        } catch (error) {
            console.error('❌ Failed to load system configuration:', error);
        }
    }

    /**
     * Load security configuration
     */
    async loadSecurityConfiguration() {
        try {
            const response = await fetch('/api/twin-registry/configuration/security', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.configurationData.security = data;
            }
        } catch (error) {
            console.error('❌ Failed to load security configuration:', error);
        }
    }

    /**
     * Load performance configuration
     */
    async loadPerformanceConfiguration() {
        try {
            const response = await fetch('/api/twin-registry/configuration/performance', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.configurationData.performance = data;
            }
        } catch (error) {
            console.error('❌ Failed to load performance configuration:', error);
        }
    }

    /**
     * Load notification configuration
     */
    async loadNotificationConfiguration() {
        try {
            const response = await fetch('/api/twin-registry/configuration/notifications', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.configurationData.notifications = data;
            }
        } catch (error) {
            console.error('❌ Failed to load notification configuration:', error);
        }
    }

    /**
     * Load integration configuration
     */
    async loadIntegrationConfiguration() {
        try {
            const response = await fetch('/api/twin-registry/configuration/integrations', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.configurationData.integrations = data;
            }
        } catch (error) {
            console.error('❌ Failed to load integration configuration:', error);
        }
    }

    /**
     * Save configuration
     */
    async saveConfiguration() {
        try {
            console.log('💾 Saving configuration...');
            this.showSaving();
            
            // Collect form data
            const formData = this.collectFormData();
            
            // Validate configuration
            if (!this.validateConfiguration(formData)) {
                this.hideSaving();
                return;
            }
            
            // Save system configuration
            await this.saveSystemConfiguration(formData.system);
            
            // Save security configuration
            await this.saveSecurityConfiguration(formData.security);
            
            // Save performance configuration
            await this.savePerformanceConfiguration(formData.performance);
            
            // Save notification configuration
            await this.saveNotificationConfiguration(formData.notifications);
            
            // Save integration configuration
            await this.saveIntegrationConfiguration(formData.integrations);
            
            // Update local data
            this.configurationData = formData;
            this.originalConfig = JSON.parse(JSON.stringify(this.configurationData));
            
            // Reset change tracking
            this.hasChanges = false;
            this.updateSaveButtonState();
            
            this.hideSaving();
            this.showSuccess('Configuration saved successfully');
            console.log('✅ Configuration saved successfully');
            
        } catch (error) {
            console.error('❌ Failed to save configuration:', error);
            this.hideSaving();
            this.showError('Failed to save configuration. Please try again.');
        }
    }

    /**
     * Collect form data
     */
    collectFormData() {
        const formData = {
            system: {},
            security: {},
            performance: {},
            notifications: {},
            integrations: {}
        };

        // Collect system configuration
        const systemForm = document.getElementById(this.elementIds.systemConfig);
        if (systemForm) {
            const formElements = systemForm.querySelectorAll('input, select, textarea');
            formElements.forEach(element => {
                if (element.name) {
                    formData.system[element.name] = element.value;
                }
            });
        }

        // Collect other configuration sections
        // ... similar collection logic for other sections

        return formData;
    }

    /**
     * Validate configuration
     */
    validateConfiguration(config) {
        // Basic validation
        if (!config.system || Object.keys(config.system).length === 0) {
            this.showError('System configuration is required');
            return false;
        }
        
        return true;
    }

    /**
     * Save system configuration
     */
    async saveSystemConfiguration(systemConfig) {
        const response = await fetch('/api/twin-registry/configuration/system', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(systemConfig)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save system configuration');
        }
    }

    /**
     * Save security configuration
     */
    async saveSecurityConfiguration(securityConfig) {
        const response = await fetch('/api/twin-registry/configuration/security', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(securityConfig)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save security configuration');
        }
    }

    /**
     * Save performance configuration
     */
    async savePerformanceConfiguration(performanceConfig) {
        const response = await fetch('/api/twin-registry/configuration/performance', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(performanceConfig)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save performance configuration');
        }
    }

    /**
     * Save notification configuration
     */
    async saveNotificationConfiguration(notificationConfig) {
        const response = await fetch('/api/twin-registry/configuration/notifications', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(notificationConfig)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save notification configuration');
        }
    }

    /**
     * Save integration configuration
     */
    async saveIntegrationConfiguration(integrationConfig) {
        const response = await fetch('/api/twin-registry/configuration/integrations', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(integrationConfig)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save integration configuration');
        }
    }

    /**
     * Reset configuration to defaults
     */
    async resetConfiguration() {
        if (!confirm('Are you sure you want to reset all configuration to defaults? This action cannot be undone.')) {
            return;
        }

        try {
            console.log('🔄 Resetting configuration to defaults...');
            this.showLoading();
            
            const response = await fetch('/api/twin-registry/configuration/reset', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                await this.loadConfiguration();
                this.showSuccess('Configuration reset to defaults successfully');
                console.log('✅ Configuration reset to defaults successfully');
            } else {
                throw new Error('Failed to reset configuration');
            }
            
        } catch (error) {
            console.error('❌ Failed to reset configuration:', error);
            this.showError('Failed to reset configuration. Please try again.');
        }
    }

    /**
     * Export configuration
     */
    exportConfiguration() {
        try {
            const dataStr = JSON.stringify(this.configurationData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = 'twin-registry-configuration.json';
            link.click();
            
            URL.revokeObjectURL(url);
            console.log('📤 Configuration exported successfully');
        } catch (error) {
            console.error('❌ Failed to export configuration:', error);
            this.showError('Failed to export configuration');
        }
    }

    /**
     * Import configuration
     */
    importConfiguration() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            try {
                const text = await file.text();
                const config = JSON.parse(text);
                
                // Validate imported configuration
                if (this.validateConfiguration(config)) {
                    this.configurationData = config;
                    this.updateConfigurationDisplay();
                    this.markAsChanged();
                    this.showSuccess('Configuration imported successfully');
                    console.log('📥 Configuration imported successfully');
                }
            } catch (error) {
                console.error('❌ Failed to import configuration:', error);
                this.showError('Failed to import configuration. Invalid file format.');
            }
        };
        
        input.click();
    }

    /**
     * Update configuration display
     */
    updateConfigurationDisplay() {
        this.updateSystemConfiguration();
        this.updateSecurityConfiguration();
        this.updatePerformanceConfiguration();
        this.updateNotificationConfiguration();
        this.updateIntegrationConfiguration();
    }

    /**
     * Update system configuration display
     */
    updateSystemConfiguration() {
        const container = document.getElementById(this.elementIds.systemConfig);
        if (!container) return;

        const config = this.configurationData.system;
        
        // Update form fields with configuration values
        Object.keys(config).forEach(key => {
            const element = container.querySelector(`[name="${key}"]`);
            if (element) {
                element.value = config[key];
            }
        });
    }

    /**
     * Update security configuration display
     */
    updateSecurityConfiguration() {
        const container = document.getElementById(this.elementIds.securityConfig);
        if (!container) return;

        const config = this.configurationData.security;
        
        // Update form fields with configuration values
        Object.keys(config).forEach(key => {
            const element = container.querySelector(`[name="${key}"]`);
            if (element) {
                element.value = config[key];
            }
        });
    }

    /**
     * Update performance configuration display
     */
    updatePerformanceConfiguration() {
        const container = document.getElementById(this.elementIds.performanceConfig);
        if (!container) return;

        const config = this.configurationData.performance;
        
        // Update form fields with configuration values
        Object.keys(config).forEach(key => {
            const element = container.querySelector(`[name="${key}"]`);
            if (element) {
                element.value = config[key];
            }
        });
    }

    /**
     * Update notification configuration display
     */
    updateNotificationConfiguration() {
        const container = document.getElementById(this.elementIds.notificationConfig);
        if (!container) return;

        const config = this.configurationData.notifications;
        
        // Update form fields with configuration values
        Object.keys(config).forEach(key => {
            const element = container.querySelector(`[name="${key}"]`);
            if (element) {
                element.value = config[key];
            }
        });
    }

    /**
     * Update integration configuration display
     */
    updateIntegrationConfiguration() {
        const container = document.getElementById(this.elementIds.integrationConfig);
        if (!container) return;

        const config = this.configurationData.integrations;
        
        // Update form fields with configuration values
        Object.keys(config).forEach(key => {
            const element = container.querySelector(`[name="${key}"]`);
            if (element) {
                element.value = config[key];
            }
        });
    }

    /**
     * Enable configuration editing
     */
    enableConfigurationEditing() {
        const forms = document.querySelectorAll('.twin-registry-config-form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.disabled = false;
            });
        });
    }

    /**
     * Disable configuration editing
     */
    disableConfigurationEditing() {
        const forms = document.querySelectorAll('.twin-registry-config-form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.disabled = true;
            });
        });
    }

    /**
     * Setup auto-save
     */
    setupAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }

        // Auto-save every 5 minutes if there are changes
        this.autoSaveInterval = setInterval(() => {
            if (this.hasChanges && this.isAuthenticated) {
                console.log('💾 Auto-saving configuration...');
                this.saveConfiguration();
            }
        }, 300000); // 5 minutes
    }

    /**
     * Show loading state
     */
    showLoading() {
        const containers = document.querySelectorAll('.twin-registry-config-section');
        containers.forEach(container => {
            container.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading configuration...</div>';
        });
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        // Loading state will be replaced by actual configuration
    }

    /**
     * Show saving state
     */
    showSaving() {
        const saveBtn = document.getElementById(this.elementIds.saveBtn);
        if (saveBtn) {
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            saveBtn.disabled = true;
        }
    }

    /**
     * Hide saving state
     */
    hideSaving() {
        const saveBtn = document.getElementById(this.elementIds.saveBtn);
        if (saveBtn) {
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Configuration';
            saveBtn.disabled = !this.hasChanges;
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        console.log('✅ Configuration Success:', message);
        // You can implement a toast notification system here
        alert(message);
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error('❌ Configuration Error:', message);
        // You can implement a toast notification system here
        alert(message);
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
     * Cleanup resources
     */
    destroy() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
        this.isInitialized = false;
        console.log('🧹 Twin Registry Configuration Management destroyed');
    }
}
