/**
 * Configuration UI Module
 * Handles configuration UI interactions and updates
 */

export class ConfigurationUI {
    constructor() {
        this.currentConfig = {};
        this.modifiedSections = new Set();
        this.isInitialized = false;
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('🔄 Initializing Configuration UI...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Initialize UI state
            this.initializeUI();
            
            this.isInitialized = true;
            console.log('✅ Configuration UI initialized');
            
        } catch (error) {
            console.error('❌ Configuration UI initialization failed:', error);
            throw error;
        }
    }

    setupEventListeners() {
        // Configuration form changes
        this.setupFormListeners();
        
        // Save all button
        const saveAllBtn = document.querySelector('button[onclick="twinRegistrySaveAllConfigurations()"]');
        if (saveAllBtn) {
            saveAllBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.saveAllConfigurations();
            });
        }

        // Reset button
        const resetBtn = document.querySelector('button[onclick="twinRegistryResetToDefaults()"]');
        if (resetBtn) {
            resetBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.resetToDefaults();
            });
        }

        // Tab change events
        const configTabs = document.querySelectorAll('#twin_registry_configTabs .nav-link');
        configTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.handleTabChange(e.target.getAttribute('data-bs-target'));
            });
        });
    }

    setupFormListeners() {
        // Registry settings
        const registryInputs = [
            'twin_registry_registryName', 'twin_registry_defaultTwinType', 'twin_registry_maxTwinsPerProject', 
            'twin_registry_autoStartMonitoring', 'twin_registry_dataRetentionPeriod', 'twin_registry_backupFrequency',
            'twin_registry_enableDataCompression', 'twin_registry_enableDataEncryption'
        ];

        registryInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('change', () => this.markSectionModified('registry'));
                input.addEventListener('input', () => this.markSectionModified('registry'));
            }
        });

        // Monitoring settings
        const monitoringInputs = [
            'twin_registry_refreshInterval', 'twin_registry_enableWebSocket', 'twin_registry_enableBrowserNotifications',
            'twin_registry_maxConcurrentMonitors', 'twin_registry_healthThreshold', 'twin_registry_performanceThreshold',
            'twin_registry_enableEmailAlerts', 'twin_registry_alertRetentionDays'
        ];

        monitoringInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('change', () => this.markSectionModified('monitoring'));
                input.addEventListener('input', () => this.markSectionModified('monitoring'));
            }
        });

        // Security settings
        const securityInputs = [
            'twin_registry_enableAuthentication', 'twin_registry_sessionTimeout', 'twin_registry_maxLoginAttempts',
            'twin_registry_enableAuditLog', 'twin_registry_auditRetentionDays', 'twin_registry_enableDataEncryption',
            'twin_registry_encryptionAlgorithm', 'twin_registry_keyRotationDays'
        ];

        securityInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('change', () => this.markSectionModified('security'));
                input.addEventListener('input', () => this.markSectionModified('security'));
            }
        });
    }

    initializeUI() {
        // Initialize Bootstrap tabs
        this.initializeBootstrapTabs();
        
        // Initialize form validation
        this.initializeValidation();
        
        // Set up auto-save indicators
        this.setupAutoSaveIndicators();
        
        // Initialize tooltips
        this.initializeTooltips();
    }

    initializeValidation() {
        // Add validation to numeric inputs
        const numericInputs = document.querySelectorAll('input[type="number"]');
        numericInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.validateNumericInput(e.target);
            });
        });

        // Add validation to required fields
        const requiredInputs = document.querySelectorAll('input[required], select[required]');
        requiredInputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                this.validateRequiredField(e.target);
            });
        });
    }

    setupAutoSaveIndicators() {
        // Add modified indicators to sections
        const sections = ['twin_registry_registry', 'twin_registry_monitoring', 'twin_registry_security'];
        sections.forEach(section => {
            const sectionElement = document.querySelector(`#${section}`);
            if (sectionElement) {
                const indicator = document.createElement('div');
                indicator.className = 'modified-indicator';
                indicator.style.display = 'none';
                indicator.innerHTML = '<i class="fas fa-asterisk text-warning"></i> Modified';
                sectionElement.appendChild(indicator);
            }
        });
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initializeBootstrapTabs() {
        // Initialize Bootstrap tabs for configuration
        const configTabs = document.querySelector('#twin_registry_configTabs');
        if (configTabs) {
            // Ensure Bootstrap is available
            if (typeof bootstrap !== 'undefined' && bootstrap.Tab) {
                // Initialize all tab elements
                const tabElements = configTabs.querySelectorAll('.nav-link');
                tabElements.forEach(tabElement => {
                    new bootstrap.Tab(tabElement);
                });
                
                console.log('✅ Bootstrap tabs initialized for configuration');
            } else {
                console.warn('⚠️ Bootstrap not available for tab initialization');
            }
        } else {
            console.warn('⚠️ Configuration tabs container not found');
        }
    }

    markSectionModified(section) {
        this.modifiedSections.add(section);
        this.updateModifiedIndicator(section, true);
        this.updateSaveButton();
    }

    clearSectionModified(section) {
        this.modifiedSections.delete(section);
        this.updateModifiedIndicator(section, false);
        this.updateSaveButton();
    }

    updateModifiedIndicator(section, isModified) {
        const sectionElement = document.querySelector(`#${section}`);
        if (sectionElement) {
            const indicator = sectionElement.querySelector('.modified-indicator');
            if (indicator) {
                indicator.style.display = isModified ? 'block' : 'none';
            }
        }
    }

    updateSaveButton() {
        const saveAllBtn = document.querySelector('button[onclick="twinRegistrySaveAllConfigurations()"]');
        if (saveAllBtn) {
            saveAllBtn.disabled = this.modifiedSections.size === 0;
            saveAllBtn.innerHTML = this.modifiedSections.size > 0 
                ? `<i class="fas fa-save me-2"></i>Save All (${this.modifiedSections.size})`
                : '<i class="fas fa-save me-2"></i>Save All';
        }
    }

    validateNumericInput(input) {
        const value = parseFloat(input.value);
        const min = parseFloat(input.min);
        const max = parseFloat(input.max);

        if (isNaN(value)) {
            this.showInputError(input, 'Please enter a valid number');
            return false;
        }

        if (min !== undefined && value < min) {
            this.showInputError(input, `Value must be at least ${min}`);
            return false;
        }

        if (max !== undefined && value > max) {
            this.showInputError(input, `Value must be at most ${max}`);
            return false;
        }

        this.clearInputError(input);
        return true;
    }

    validateRequiredField(input) {
        if (!input.value.trim()) {
            this.showInputError(input, 'This field is required');
            return false;
        }

        this.clearInputError(input);
        return true;
    }

    showInputError(input, message) {
        // Remove existing error
        this.clearInputError(input);
        
        // Add error class
        input.classList.add('is-invalid');
        
        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        // Insert after input
        input.parentNode.appendChild(errorDiv);
    }

    clearInputError(input) {
        input.classList.remove('is-invalid');
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    handleTabChange(targetId) {
        // Update active tab
        const tabs = document.querySelectorAll('#configTabs .nav-link');
        tabs.forEach(tab => {
            tab.classList.remove('active');
            if (tab.getAttribute('data-bs-target') === targetId) {
                tab.classList.add('active');
            }
        });

        // Show corresponding content
        const contents = document.querySelectorAll('.tab-pane');
        contents.forEach(content => {
            content.classList.remove('show', 'active');
            if (content.id === targetId.replace('#', '')) {
                content.classList.add('show', 'active');
            }
        });
    }

    async saveAllConfigurations() {
        try {
            console.log('🔄 Saving all configurations...');
            
            // Collect all modified sections
            const configData = {};
            this.modifiedSections.forEach(section => {
                configData[section] = this.collectSectionData(section);
            });

            // Clear modified sections
            this.modifiedSections.clear();
            this.updateSaveButton();

            // Show success message
            this.showNotification('Configuration saved successfully', 'success');
            
            console.log('✅ All configurations saved');
            
        } catch (error) {
            console.error('❌ Failed to save configurations:', error);
            this.showNotification('Failed to save configuration', 'error');
        }
    }

    async resetToDefaults() {
        try {
            console.log('🔄 Resetting to defaults...');
            
            // Clear all form data
            this.clearAllForms();
            
            // Clear modified sections
            this.modifiedSections.clear();
            this.updateSaveButton();

            // Show success message
            this.showNotification('Configuration reset to defaults', 'success');
            
            console.log('✅ Configuration reset to defaults');
            
        } catch (error) {
            console.error('❌ Failed to reset configuration:', error);
            this.showNotification('Failed to reset configuration', 'error');
        }
    }

    collectSectionData(section) {
        const data = {};
        const sectionElement = document.querySelector(`#${section}Section`);
        
        if (sectionElement) {
            const inputs = sectionElement.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.name) {
                    data[input.name] = input.type === 'checkbox' ? input.checked : input.value;
                }
            });
        }
        
        return data;
    }

    clearAllForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.reset();
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    showError(message) {
        this.showNotification(message, 'danger');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    populateConfigurationForm(config) {
        try {
            console.log('🔄 Populating configuration form with:', config);
            
            // Populate system settings
            if (config.system) {
                this.setFormValue('autoSync', config.system.auto_sync);
                this.setFormValue('syncInterval', config.system.sync_interval);
                this.setFormValue('maxInstancesPerTwin', config.system.max_instances_per_twin);
                this.setFormValue('enableMonitoring', config.system.enable_monitoring);
                this.setFormValue('monitoringInterval', config.system.monitoring_interval);
            }
            
            // Populate registry settings
            if (config.registry) {
                this.setFormValue('maxTwins', config.registry.max_twins);
                this.setFormValue('enableRelationships', config.registry.enable_relationships);
                this.setFormValue('enableLifecycleTracking', config.registry.enable_lifecycle_tracking);
                this.setFormValue('enablePerformanceMonitoring', config.registry.enable_performance_monitoring);
            }
            
            // Populate UI settings
            if (config.ui) {
                this.setFormValue('refreshInterval', config.ui.refresh_interval);
                this.setFormValue('showAdvancedOptions', config.ui.show_advanced_options);
                this.setFormValue('enableRealTimeUpdates', config.ui.enable_real_time_updates);
            }
            
            console.log('✅ Configuration form populated');
            
        } catch (error) {
            console.error('❌ Failed to populate configuration form:', error);
        }
    }

    setFormValue(fieldName, value) {
        const element = document.getElementById(fieldName);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = Boolean(value);
            } else {
                element.value = value;
            }
        }
    }

    collectConfigurationData() {
        const data = {
            system: {},
            registry: {},
            ui: {}
        };
        
        // Collect system settings
        data.system.auto_sync = this.getFormValue('autoSync', 'checkbox');
        data.system.sync_interval = this.getFormValue('syncInterval', 'number');
        data.system.max_instances_per_twin = this.getFormValue('maxInstancesPerTwin', 'number');
        data.system.enable_monitoring = this.getFormValue('enableMonitoring', 'checkbox');
        data.system.monitoring_interval = this.getFormValue('monitoringInterval', 'number');
        
        // Collect registry settings
        data.registry.max_twins = this.getFormValue('maxTwins', 'number');
        data.registry.enable_relationships = this.getFormValue('enableRelationships', 'checkbox');
        data.registry.enable_lifecycle_tracking = this.getFormValue('enableLifecycleTracking', 'checkbox');
        data.registry.enable_performance_monitoring = this.getFormValue('enablePerformanceMonitoring', 'checkbox');
        
        // Collect UI settings
        data.ui.refresh_interval = this.getFormValue('refreshInterval', 'number');
        data.ui.show_advanced_options = this.getFormValue('showAdvancedOptions', 'checkbox');
        data.ui.enable_real_time_updates = this.getFormValue('enableRealTimeUpdates', 'checkbox');
        
        return data;
    }

    getFormValue(fieldName, type = 'text') {
        const element = document.getElementById(fieldName);
        if (element) {
            if (type === 'checkbox') {
                return element.checked;
            } else if (type === 'number') {
                return parseInt(element.value) || 0;
            } else {
                return element.value;
            }
        }
        return type === 'checkbox' ? false : '';
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Configuration UI: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Configuration UI: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Configuration UI: Auth system ready event received');
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
                console.warn('⚠️ Configuration UI: Timeout waiting for auth system');
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
            console.log('🔐 Configuration UI: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Configuration UI: No auth manager available');
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
        this.currentConfig = {};
        this.modifiedSections.clear();
        console.log('🧹 Configuration UI: Sensitive data cleared');
    }

    cleanup() {
        // Remove event listeners
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.replaceWith(input.cloneNode(true));
        });
        
        // Clear state
        this.currentConfig = {};
        this.modifiedSections.clear();
        this.isInitialized = false;
    }
} 