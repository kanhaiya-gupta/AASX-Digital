/**
 * Twin Registry Configuration Management Module
 * Provides world-class configuration management functionality
 */

class ConfigurationManager {
    constructor() {
        this.config = null;
        this.history = [];
        this.currentUser = null;
        this.isInitialized = false;
        this.monitoringInterval = null;
        this.configCache = new Map();
        this.cacheTTL = 300000; // 5 minutes
        
        // Initialize the module
        this.init();
    }
    
    async init() {
        try {
            // Check authentication
            if (window.authManager && window.authManager.isAuthenticated) {
                this.currentUser = window.authManager.getCurrentUser();
            }
            
            // Load initial configuration
            await this.loadConfiguration();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Start monitoring
            this.startMonitoring();
            
            this.isInitialized = true;
            console.log('✅ Configuration Manager initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize Configuration Manager:', error);
        }
    }
    
    setupEventListeners() {
        // Configuration form submission
        const configForm = document.getElementById('twin_registry_configForm');
        if (configForm) {
            configForm.addEventListener('submit', (e) => this.handleConfigSubmit(e));
        }
        
        // Save all configurations button
        const saveAllBtn = document.getElementById('twin_registry_saveAllConfigurations');
        if (saveAllBtn) {
            saveAllBtn.addEventListener('click', () => this.saveAllConfigurations());
        }
        
        // Reset to defaults button
        const resetBtn = document.getElementById('twin_registry_resetToDefaults');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetToDefaults());
        }
        
        // Export configuration button
        const exportBtn = document.getElementById('twin_registry_exportConfiguration');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportConfiguration());
        }
        
        // Import configuration button
        const importBtn = document.getElementById('twin_registry_importConfiguration');
        if (importBtn) {
            importBtn.addEventListener('click', () => this.importConfiguration());
        }
        
        // Configuration history button
        const historyBtn = document.getElementById('twin_registry_showConfigurationHistory');
        if (historyBtn) {
            historyBtn.addEventListener('click', () => this.showConfigurationHistory());
        }
        
        // Environment selector
        const envSelector = document.getElementById('twin_registry_environmentSelector');
        if (envSelector) {
            envSelector.addEventListener('change', (e) => this.applyEnvironmentOverrides(e.target.value));
        }
        
        // Configuration validation button
        const validateBtn = document.getElementById('twin_registry_validateConfiguration');
        if (validateBtn) {
            validateBtn.addEventListener('click', () => this.validateConfiguration());
        }
        
        // Real-time monitoring toggle
        const monitoringToggle = document.getElementById('twin_registry_enableRealTimeMonitoring');
        if (monitoringToggle) {
            monitoringToggle.addEventListener('change', (e) => this.toggleRealTimeMonitoring(e.target.checked));
        }
        
        // Configuration search
        const searchInput = document.getElementById('twin_registry_configSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.searchConfiguration(e.target.value));
        }
        
        // Configuration filters
        const filterSelects = document.querySelectorAll('.twin_registry_config-filter');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => this.applyConfigurationFilters());
        });
        
        // Configuration tabs
        const configTabs = document.querySelectorAll('#twin_registry_configTabs .nav-link');
        configTabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.handleConfigTabClick(e));
        });
        
        // Individual setting inputs
        this.setupSettingInputs();
    }
    
    setupSettingInputs() {
        // Set up real-time validation for all configuration inputs
        const configInputs = document.querySelectorAll('#twin_registry_configTabContent input, #twin_registry_configTabContent select, #twin_registry_configTabContent textarea');
        
        configInputs.forEach(input => {
            // Add validation on blur
            input.addEventListener('blur', (e) => this.validateSetting(e.target));
            
            // Add real-time feedback
            input.addEventListener('input', (e) => this.handleSettingChange(e.target));
            
            // Add keyboard shortcuts
            input.addEventListener('keydown', (e) => this.handleSettingKeyboard(e));
        });
    }
    
    async loadConfiguration() {
        try {
            const response = await fetch('/api/twin-registry/configuration', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.config = data.configuration;
                    this.updateConfigurationUI();
                    this.cacheConfiguration();
                } else {
                    throw new Error(data.message || 'Failed to load configuration');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to load configuration:', error);
            this.showNotification('Failed to load configuration', 'error');
        }
    }
    
    async loadConfigurationHistory() {
        try {
            const response = await fetch('/api/twin-registry/configuration/history', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.history = data.history;
                    this.updateHistoryUI();
                }
            }
            
        } catch (error) {
            console.error('Failed to load configuration history:', error);
        }
    }
    
    updateConfigurationUI() {
        if (!this.config) return;
        
        // Update configuration summary
        this.updateConfigurationSummary();
        
        // Update form fields
        this.updateConfigurationForm();
        
        // Update status indicators
        this.updateStatusIndicators();
        
        // Update configuration overview
        this.updateConfigurationOverview();
    }
    
    updateConfigurationSummary() {
        const summaryContainer = document.getElementById('twin_registry_configSummary');
        if (!summaryContainer || !this.config) return;
        
        const summary = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h6 class="card-title">Version</h6>
                            <h4>${this.config.version || '1.0.0'}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h6 class="card-title">Environment</h6>
                            <h4>${this.config.environment || 'development'}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h6 class="card-title">Security Level</h6>
                            <h4>${this.config.security_level || 'internal'}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body">
                            <h6 class="card-title">Last Updated</h6>
                            <h6>${this.formatTimestamp(this.config.updated_at)}</h6>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        summaryContainer.innerHTML = summary;
    }
    
    updateConfigurationForm() {
        if (!this.config) return;
        
        // Update registry settings
        this.updateFormSection('registry', this.config.registry);
        
        // Update monitoring settings
        this.updateFormSection('monitoring', this.config.monitoring);
        
        // Update security settings
        this.updateFormSection('security', this.config.security);
        
        // Update integration settings
        this.updateFormSection('integration', this.config.integration);
        
        // Update UI settings
        this.updateFormSection('ui', this.config.ui);
        
        // Update performance settings
        this.updateFormSection('performance', this.config.performance);
        
        // Update notification settings
        this.updateFormSection('notifications', this.config.notifications);
        
        // Update backup settings
        this.updateFormSection('backup', this.config.backup);
    }
    
    updateFormSection(section, sectionConfig) {
        if (!sectionConfig) return;
        
        Object.keys(sectionConfig).forEach(key => {
            const input = document.getElementById(`twin_registry_${section}_${key}`);
            if (input) {
                const value = sectionConfig[key];
                
                if (input.type === 'checkbox') {
                    input.checked = Boolean(value);
                } else if (input.type === 'number') {
                    input.value = value;
                } else {
                    input.value = value;
                }
                
                // Add visual feedback
                this.addSettingFeedback(input, 'loaded');
            }
        });
    }
    
    updateStatusIndicators() {
        // Update configuration status
        const statusIndicator = document.getElementById('twin_registry_configStatus');
        if (statusIndicator && this.config) {
            const isValid = this.config.is_valid !== false;
            const statusClass = isValid ? 'success' : 'danger';
            const statusText = isValid ? 'Valid' : 'Invalid';
            
            statusIndicator.className = `badge bg-${statusClass}`;
            statusIndicator.textContent = statusText;
        }
        
        // Update last modified info
        const lastModified = document.getElementById('twin_registry_lastModified');
        if (lastModified && this.config) {
            lastModified.textContent = this.formatTimestamp(this.config.updated_at);
        }
        
        // Update modified by info
        const modifiedBy = document.getElementById('twin_registry_modifiedBy');
        if (modifiedBy && this.config) {
            modifiedBy.textContent = this.config.updated_by || 'System';
        }
    }
    
    updateConfigurationOverview() {
        const overviewContainer = document.getElementById('twin_registry_configOverview');
        if (!overviewContainer || !this.config) return;
        
        const overview = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Registry Configuration</h6>
                    <ul class="list-unstyled">
                        <li><strong>Max Twins:</strong> ${this.config.registry?.max_twins || 'N/A'}</li>
                        <li><strong>Enable Relationships:</strong> ${this.config.registry?.enable_relationships ? 'Yes' : 'No'}</li>
                        <li><strong>Enable Monitoring:</strong> ${this.config.registry?.enable_performance_monitoring ? 'Yes' : 'No'}</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Monitoring Configuration</h6>
                    <ul class="list-unstyled">
                        <li><strong>Enabled:</strong> ${this.config.monitoring?.enable_monitoring ? 'Yes' : 'No'}</li>
                        <li><strong>Interval:</strong> ${this.config.monitoring?.monitoring_interval_seconds || 'N/A'}s</li>
                        <li><strong>Real-time:</strong> ${this.config.monitoring?.enable_real_time_monitoring ? 'Yes' : 'No'}</li>
                    </ul>
                </div>
            </div>
        `;
        
        overviewContainer.innerHTML = overview;
    }
    
    async saveAllConfigurations() {
        try {
            this.showNotification('Saving configuration...', 'info');
            
            // Collect all configuration values
            const configData = this.collectConfigurationData();
            
            // Validate configuration
            const validationResult = await this.validateConfigurationData(configData);
            if (!validationResult.isValid) {
                this.showValidationErrors(validationResult.errors);
                return;
            }
            
            // Save configuration
            const response = await fetch('/api/twin-registry/configuration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify(configData)
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.showNotification('Configuration saved successfully!', 'success');
                    this.config = { ...this.config, ...configData };
                    this.updateConfigurationUI();
                    this.cacheConfiguration();
                } else {
                    throw new Error(data.message || 'Failed to save configuration');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to save configuration:', error);
            this.showNotification('Failed to save configuration', 'error');
        }
    }
    
    collectConfigurationData() {
        const configData = {};
        
        // Registry settings
        configData.registry = this.collectSectionData('registry');
        
        // Monitoring settings
        configData.monitoring = this.collectSectionData('monitoring');
        
        // Security settings
        configData.security = this.collectSectionData('security');
        
        // Integration settings
        configData.integration = this.collectSectionData('integration');
        
        // UI settings
        configData.ui = this.collectSectionData('ui');
        
        // Performance settings
        configData.performance = this.collectSectionData('performance');
        
        // Notification settings
        configData.notifications = this.collectSectionData('notifications');
        
        // Backup settings
        configData.backup = this.collectSectionData('backup');
        
        return configData;
    }
    
    collectSectionData(section) {
        const sectionData = {};
        const inputs = document.querySelectorAll(`#twin_registry_${section}Tab input, #twin_registry_${section}Tab select, #twin_registry_${section}Tab textarea`);
        
        inputs.forEach(input => {
            const key = input.id.replace(`twin_registry_${section}_`, '');
            let value;
            
            if (input.type === 'checkbox') {
                value = input.checked;
            } else if (input.type === 'number') {
                value = parseFloat(input.value) || 0;
            } else {
                value = input.value;
            }
            
            sectionData[key] = value;
        });
        
        return sectionData;
    }
    
    async validateConfigurationData(configData) {
        try {
            const response = await fetch('/api/twin-registry/configuration/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    config_data: configData,
                    validation_level: 'strict'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                return {
                    isValid: data.valid,
                    errors: data.errors || [],
                    warnings: data.warnings || []
                };
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to validate configuration:', error);
            return { isValid: false, errors: ['Validation failed'], warnings: [] };
        }
    }
    
    showValidationErrors(errors) {
        if (errors.length === 0) return;
        
        const errorHtml = errors.map(error => `<li>${error}</li>`).join('');
        const errorMessage = `
            <div class="alert alert-danger">
                <h6>Configuration Validation Failed</h6>
                <ul class="mb-0">${errorHtml}</ul>
            </div>
        `;
        
        this.showNotification(errorMessage, 'error', true);
    }
    
    async resetToDefaults() {
        try {
            if (!confirm('Are you sure you want to reset all configuration to defaults? This action cannot be undone.')) {
                return;
            }
            
            this.showNotification('Resetting configuration to defaults...', 'info');
            
            const response = await fetch('/api/twin-registry/configuration/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    reset_type: 'defaults',
                    user: this.currentUser?.id || 'system'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.showNotification('Configuration reset to defaults successfully!', 'success');
                    await this.loadConfiguration();
                } else {
                    throw new Error(data.message || 'Failed to reset configuration');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to reset configuration:', error);
            this.showNotification('Failed to reset configuration', 'error');
        }
    }
    
    async exportConfiguration() {
        try {
            const format = document.getElementById('twin_registry_exportFormat')?.value || 'json';
            
            const response = await fetch(`/api/twin-registry/configuration/export?format=${format}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.downloadConfiguration(data.config, format);
                } else {
                    throw new Error(data.message || 'Failed to export configuration');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to export configuration:', error);
            this.showNotification('Failed to export configuration', 'error');
        }
    }
    
    downloadConfiguration(config, format) {
        const filename = `twin_registry_config_${new Date().toISOString().split('T')[0]}.${format}`;
        const content = format === 'yaml' ? config : JSON.stringify(config, null, 2);
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification(`Configuration exported to ${filename}`, 'success');
    }
    
    async importConfiguration() {
        try {
            const fileInput = document.getElementById('twin_registry_configFile');
            if (!fileInput.files[0]) {
                this.showNotification('Please select a configuration file', 'warning');
                return;
            }
            
            const file = fileInput.files[0];
            const format = file.name.endsWith('.yaml') || file.name.endsWith('.yml') ? 'yaml' : 'json';
            
            const content = await file.text();
            
            this.showNotification('Importing configuration...', 'info');
            
            const response = await fetch('/api/twin-registry/configuration/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    config_data: content,
                    import_type: format
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.showNotification('Configuration imported successfully!', 'success');
                    await this.loadConfiguration();
                } else {
                    throw new Error(data.message || 'Failed to import configuration');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to import configuration:', error);
            this.showNotification('Failed to import configuration', 'error');
        }
    }
    
    async showConfigurationHistory() {
        try {
            await this.loadConfigurationHistory();
            
            const historyModal = new bootstrap.Modal(document.getElementById('twin_registry_configHistoryModal'));
            historyModal.show();
            
        } catch (error) {
            console.error('Failed to show configuration history:', error);
            this.showNotification('Failed to load configuration history', 'error');
        }
    }
    
    updateHistoryUI() {
        const historyContainer = document.getElementById('twin_registry_configHistoryList');
        if (!historyContainer || !this.history) return;
        
        const historyHtml = this.history.map(entry => `
            <div class="config-history-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">Version ${entry.version}</h6>
                        <p class="text-muted mb-1">${entry.environment} • ${this.formatTimestamp(entry.created_at)}</p>
                        <p class="mb-1">${entry.change_summary || 'No changes recorded'}</p>
                        <small class="text-muted">By: ${entry.created_by || 'System'}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-primary" onclick="window.configurationManager.rollbackToVersion('${entry.config_id}')">
                        Rollback
                    </button>
                </div>
            </div>
        `).join('');
        
        historyContainer.innerHTML = historyHtml;
    }
    
    async rollbackToVersion(configId) {
        try {
            if (!confirm('Are you sure you want to rollback to this configuration version? This action cannot be undone.')) {
                return;
            }
            
            this.showNotification('Rolling back configuration...', 'info');
            
            const response = await fetch(`/api/twin-registry/configuration/rollback/${configId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.showNotification('Configuration rolled back successfully!', 'success');
                    await this.loadConfiguration();
                    
                    // Close history modal
                    const historyModal = bootstrap.Modal.getInstance(document.getElementById('twin_registry_configHistoryModal'));
                    if (historyModal) {
                        historyModal.hide();
                    }
                } else {
                    throw new Error(data.message || 'Failed to rollback configuration');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to rollback configuration:', error);
            this.showNotification('Failed to rollback configuration', 'error');
        }
    }
    
    async applyEnvironmentOverrides(environment) {
        try {
            if (!environment || environment === 'current') return;
            
            this.showNotification(`Applying ${environment} environment overrides...`, 'info');
            
            const response = await fetch(`/api/twin-registry/configuration/environment/${environment}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.showNotification(`Environment overrides applied for ${environment}!`, 'success');
                    await this.loadConfiguration();
                } else {
                    throw new Error(data.message || 'Failed to apply environment overrides');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to apply environment overrides:', error);
            this.showNotification('Failed to apply environment overrides', 'error');
        }
    }
    
    async validateConfiguration() {
        try {
            this.showNotification('Validating configuration...', 'info');
            
            const response = await fetch('/api/twin-registry/configuration/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    config_data: this.config || {},
                    validation_level: 'strict'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showValidationResults(data);
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Failed to validate configuration:', error);
            this.showNotification('Failed to validate configuration', 'error');
        }
    }
    
    showValidationResults(validationData) {
        const resultsHtml = `
            <div class="alert alert-${validationData.valid ? 'success' : 'danger'}">
                <h6>Configuration Validation Results</h6>
                <p><strong>Status:</strong> ${validationData.valid ? 'Valid' : 'Invalid'}</p>
                ${validationData.errors.length > 0 ? `<p><strong>Errors:</strong></p><ul>${validationData.errors.map(e => `<li>${e}</li>`).join('')}</ul>` : ''}
                ${validationData.warnings.length > 0 ? `<p><strong>Warnings:</strong></p><ul>${validationData.warnings.map(w => `<li>${w}</li>`).join('')}</ul>` : ''}
            </div>
        `;
        
        this.showNotification(resultsHtml, validationData.valid ? 'success' : 'error', true);
    }
    
    toggleRealTimeMonitoring(enabled) {
        if (enabled) {
            this.startMonitoring();
        } else {
            this.stopMonitoring();
        }
    }
    
    startMonitoring() {
        if (this.monitoringInterval) return;
        
        this.monitoringInterval = setInterval(async () => {
            await this.refreshConfiguration();
        }, 30000); // Refresh every 30 seconds
        
        console.log('🔄 Real-time configuration monitoring started');
    }
    
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
            console.log('⏹️ Real-time configuration monitoring stopped');
        }
    }
    
    async refreshConfiguration() {
        try {
            await this.loadConfiguration();
            this.showNotification('Configuration refreshed', 'info');
        } catch (error) {
            console.error('Failed to refresh configuration:', error);
        }
    }
    
    searchConfiguration(query) {
        if (!query) {
            this.showAllConfigurationSections();
            return;
        }
        
            const sections = document.querySelectorAll('#twin_registry_configTabContent .tab-pane');
            sections.forEach(section => {
                const sectionId = section.id;
                const sectionTitle = document.querySelector(`[data-bs-target="#${sectionId}"]`)?.textContent || '';
                
                if (sectionTitle.toLowerCase().includes(query.toLowerCase()) || 
                    sectionId.toLowerCase().includes(query.toLowerCase())) {
                    section.style.display = 'block';
                } else {
                    section.style.display = 'none';
                }
            });
    }
    
    applyConfigurationFilters() {
        const filters = {};
        const filterSelects = document.querySelectorAll('.twin_registry_config-filter');
        
        filterSelects.forEach(select => {
            if (select.value) {
                filters[select.name] = select.value;
            }
        });
        
        // Apply filters to configuration display
        this.filterConfigurationDisplay(filters);
    }
    
    filterConfigurationDisplay(filters) {
        // Implementation for filtering configuration display
        // This could filter by category, importance, etc.
        console.log('Applying configuration filters:', filters);
    }
    
    handleConfigTabClick(event) {
        const targetId = event.target.getAttribute('data-bs-target');
        if (targetId) {
            // Hide all tab content
            const tabContents = document.querySelectorAll('#twin_registry_configTabContent .tab-pane');
            tabContents.forEach(content => content.classList.remove('show', 'active'));
            
            // Show target tab content
            const targetContent = document.querySelector(targetId);
            if (targetContent) {
                targetContent.classList.add('show', 'active');
            }
            
            // Update active tab
            const navLinks = document.querySelectorAll('#twin_registry_configTabs .nav-link');
            navLinks.forEach(link => link.classList.remove('active'));
            event.target.classList.add('active');
        }
    }
    
    validateSetting(input) {
        const value = input.value;
        const validationRules = this.getValidationRules(input);
        
        let isValid = true;
        let errorMessage = '';
        
        // Apply validation rules
        if (validationRules.required && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        } else if (validationRules.min && parseFloat(value) < validationRules.min) {
            isValid = false;
            errorMessage = `Value must be at least ${validationRules.min}`;
        } else if (validationRules.max && parseFloat(value) > validationRules.max) {
            isValid = false;
            errorMessage = `Value must be at most ${validationRules.max}`;
        } else if (validationRules.pattern && !validationRules.pattern.test(value)) {
            isValid = false;
            errorMessage = 'Invalid format';
        }
        
        // Update UI feedback
        this.addSettingFeedback(input, isValid ? 'valid' : 'invalid', errorMessage);
        
        return isValid;
    }
    
    getValidationRules(input) {
        const rules = {
            required: input.hasAttribute('required'),
            min: input.getAttribute('min') ? parseFloat(input.getAttribute('min')) : null,
            max: input.getAttribute('max') ? parseFloat(input.getAttribute('max')) : null,
            pattern: input.getAttribute('pattern') ? new RegExp(input.getAttribute('pattern')) : null
        };
        
        return rules;
    }
    
    addSettingFeedback(input, type, message = '') {
        // Remove existing feedback
        input.classList.remove('is-valid', 'is-invalid');
        const feedbackElement = input.parentNode.querySelector('.invalid-feedback, .valid-feedback');
        if (feedbackElement) {
            feedbackElement.remove();
        }
        
        // Add new feedback
        if (type === 'valid') {
            input.classList.add('is-valid');
        } else if (type === 'invalid') {
            input.classList.add('is-invalid');
            if (message) {
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = message;
                input.parentNode.appendChild(feedback);
            }
        } else if (type === 'loaded') {
            input.classList.add('is-valid');
        }
    }
    
    handleSettingChange(input) {
        // Clear validation state on input
        input.classList.remove('is-valid', 'is-invalid');
        
        // Mark as modified
        input.classList.add('is-modified');
        
        // Auto-save after delay (if enabled)
        if (this.config?.ui?.enable_auto_save) {
            this.debounce(() => this.autoSaveSetting(input), 2000);
        }
    }
    
    handleSettingKeyboard(event) {
        // Ctrl+S to save
        if (event.ctrlKey && event.key === 's') {
            event.preventDefault();
            this.saveAllConfigurations();
        }
        
        // Ctrl+Z to undo (if implemented)
        if (event.ctrlKey && event.key === 'z') {
            event.preventDefault();
            // Implement undo functionality
        }
    }
    
    async autoSaveSetting(input) {
        try {
            const settingPath = input.id.replace('twin_registry_', '').replace(/_/g, '.');
            const value = input.type === 'checkbox' ? input.checked : input.value;
            
            const response = await fetch(`/api/twin-registry/configuration/setting/${settingPath}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify(value)
            });
            
            if (response.ok) {
                this.addSettingFeedback(input, 'valid');
                input.classList.remove('is-modified');
            }
            
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }
    
    debounce(func, wait) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(func, wait);
    }
    
    cacheConfiguration() {
        if (this.config) {
            this.configCache.set('current', {
                data: this.config,
                timestamp: Date.now()
            });
        }
    }
    
    getCachedConfiguration() {
        const cached = this.configCache.get('current');
        if (cached && (Date.now() - cached.timestamp) < this.cacheTTL) {
            return cached.data;
        }
        return null;
    }
    
    getAuthToken() {
        if (window.authManager && window.authManager.getToken) {
            return window.authManager.getToken();
        }
        return null;
    }
    
    formatTimestamp(timestamp) {
        if (!timestamp) return 'N/A';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleString();
        } catch (error) {
            return timestamp;
        }
    }
    
    showNotification(message, type = 'info', isHtml = false) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        if (isHtml) {
            notification.innerHTML = message;
        } else {
            notification.textContent = message;
        }
        
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'btn-close';
        closeBtn.setAttribute('data-bs-dismiss', 'alert');
        notification.appendChild(closeBtn);
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    destroy() {
        this.stopMonitoring();
        this.isInitialized = false;
        console.log('🗑️ Configuration Manager destroyed');
    }
}

// Initialize Configuration Manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.configurationManager) {
        window.configurationManager = new ConfigurationManager();
    }
});

// Export for module usage
export default ConfigurationManager; 