/**
 * System Configuration Module
 * Manages system configuration, monitoring, and administration
 */
class SystemConfigurationModule {
    constructor() {
        this.config = {};
        this.metrics = {};
        this.healthStatus = {};
        this.monitoringInterval = null;
        this.isInitialized = false;
    }

    /**
     * Initialize the module
     */
    init() {
        if (this.isInitialized) return;
        
        console.log('🚀 Initializing System Configuration Module...');
        
        this.loadConfiguration();
        this.bindEvents();
        this.startMonitoring();
        this.updateMetrics();
        this.updateHealthStatus();
        
        this.isInitialized = true;
        console.log('✅ System Configuration Module initialized');
    }

    /**
     * Load system configuration from backend
     */
    async loadConfiguration() {
        try {
            // Mock configuration data - replace with actual API call
            this.config = {
                general: {
                    systemName: 'AASX Digital Twin Analytics Framework',
                    environment: 'production',
                    timezone: 'UTC',
                    language: 'en',
                    emailNotifications: true,
                    smsNotifications: false,
                    browserNotifications: true,
                    maintenanceMode: false
                },
                security: {
                    sessionTimeout: 30,
                    maxLoginAttempts: 5,
                    passwordPolicy: 'medium',
                    twoFactorAuth: true,
                    dataEncryption: true,
                    sslEnforcement: true,
                    auditLogging: true,
                    complianceMode: false
                },
                performance: {
                    cacheTTL: 300,
                    maxConcurrentUsers: 1000,
                    dbConnectionPool: 20,
                    autoScaling: true,
                    performanceMonitoring: true,
                    errorTracking: true,
                    resourceMonitoring: true,
                    alerting: true
                },
                integration: {
                    apiRateLimit: 1000,
                    apiVersion: 'v1.0',
                    apiDocumentation: true,
                    apiMonitoring: true,
                    databaseType: 'postgresql',
                    messageQueue: 'redis',
                    webhookEnabled: true,
                    thirdPartyAPIs: false
                },
                backup: {
                    backupFrequency: 'daily',
                    retentionPeriod: 30,
                    autoBackup: true,
                    encryptedBackup: true,
                    pointInTimeRecovery: true,
                    disasterRecovery: true,
                    failoverSupport: false,
                    recoveryTimeObjective: '1hour'
                }
            };
            
            this.applyConfigurationToUI();
        } catch (error) {
            console.error('❌ Failed to load configuration:', error);
            this.showError('Failed to load system configuration');
        }
    }

    /**
     * Apply configuration to UI elements
     */
    applyConfigurationToUI() {
        // General Settings
        this.setElementValue('systemName', this.config.general.systemName);
        this.setElementValue('environment', this.config.general.environment);
        this.setElementValue('timezone', this.config.general.timezone);
        this.setElementValue('language', this.config.general.language);
        this.setElementChecked('emailNotifications', this.config.general.emailNotifications);
        this.setElementChecked('smsNotifications', this.config.general.smsNotifications);
        this.setElementChecked('browserNotifications', this.config.general.browserNotifications);
        this.setElementChecked('maintenanceMode', this.config.general.maintenanceMode);

        // Security Settings
        this.setElementValue('sessionTimeout', this.config.security.sessionTimeout);
        this.setElementValue('maxLoginAttempts', this.config.security.maxLoginAttempts);
        this.setElementValue('passwordPolicy', this.config.security.passwordPolicy);
        this.setElementChecked('twoFactorAuth', this.config.security.twoFactorAuth);
        this.setElementChecked('dataEncryption', this.config.security.dataEncryption);
        this.setElementChecked('sslEnforcement', this.config.security.sslEnforcement);
        this.setElementChecked('auditLogging', this.config.security.auditLogging);
        this.setElementChecked('complianceMode', this.config.security.complianceMode);

        // Performance Settings
        this.setElementValue('cacheTTL', this.config.performance.cacheTTL);
        this.setElementValue('maxConcurrentUsers', this.config.performance.maxConcurrentUsers);
        this.setElementValue('dbConnectionPool', this.config.performance.dbConnectionPool);
        this.setElementChecked('autoScaling', this.config.performance.autoScaling);
        this.setElementChecked('performanceMonitoring', this.config.performance.performanceMonitoring);
        this.setElementChecked('errorTracking', this.config.performance.errorTracking);
        this.setElementChecked('resourceMonitoring', this.config.performance.resourceMonitoring);
        this.setElementChecked('alerting', this.config.performance.alerting);

        // Integration Settings
        this.setElementValue('apiRateLimit', this.config.integration.apiRateLimit);
        this.setElementValue('apiVersion', this.config.integration.apiVersion);
        this.setElementChecked('apiDocumentation', this.config.integration.apiDocumentation);
        this.setElementChecked('apiMonitoring', this.config.integration.apiMonitoring);
        this.setElementValue('databaseType', this.config.integration.databaseType);
        this.setElementValue('messageQueue', this.config.integration.messageQueue);
        this.setElementChecked('webhookEnabled', this.config.integration.webhookEnabled);
        this.setElementChecked('thirdPartyAPIs', this.config.integration.thirdPartyAPIs);

        // Backup Settings
        this.setElementValue('backupFrequency', this.config.backup.backupFrequency);
        this.setElementValue('retentionPeriod', this.config.backup.retentionPeriod);
        this.setElementChecked('autoBackup', this.config.backup.autoBackup);
        this.setElementChecked('encryptedBackup', this.config.backup.encryptedBackup);
        this.setElementChecked('pointInTimeRecovery', this.config.backup.pointInTimeRecovery);
        this.setElementChecked('disasterRecovery', this.config.backup.disasterRecovery);
        this.setElementChecked('failoverSupport', this.config.backup.failoverSupport);
        this.setElementValue('recoveryTimeObjective', this.config.backup.recoveryTimeObjective);
    }

    /**
     * Set element value
     */
    setElementValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.value = value;
        }
    }

    /**
     * Set element checked state
     */
    setElementChecked(elementId, checked) {
        const element = document.getElementById(elementId);
        if (element) {
            element.checked = checked;
        }
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Configuration change events
        this.bindConfigurationEvents();
        
        // Tab change events
        this.bindTabEvents();
        
        // Form submission events
        this.bindFormEvents();
    }

    /**
     * Bind configuration change events
     */
    bindConfigurationEvents() {
        // General settings
        this.bindInputChange('systemName', 'general', 'systemName');
        this.bindSelectChange('environment', 'general', 'environment');
        this.bindSelectChange('timezone', 'general', 'timezone');
        this.bindSelectChange('language', 'general', 'language');
        this.bindCheckboxChange('emailNotifications', 'general', 'emailNotifications');
        this.bindCheckboxChange('smsNotifications', 'general', 'smsNotifications');
        this.bindCheckboxChange('browserNotifications', 'general', 'browserNotifications');
        this.bindCheckboxChange('maintenanceMode', 'general', 'maintenanceMode');

        // Security settings
        this.bindInputChange('sessionTimeout', 'security', 'sessionTimeout', 'number');
        this.bindInputChange('maxLoginAttempts', 'security', 'maxLoginAttempts', 'number');
        this.bindSelectChange('passwordPolicy', 'security', 'passwordPolicy');
        this.bindCheckboxChange('twoFactorAuth', 'security', 'twoFactorAuth');
        this.bindCheckboxChange('dataEncryption', 'security', 'dataEncryption');
        this.bindCheckboxChange('sslEnforcement', 'security', 'sslEnforcement');
        this.bindCheckboxChange('auditLogging', 'security', 'auditLogging');
        this.bindCheckboxChange('complianceMode', 'security', 'complianceMode');

        // Performance settings
        this.bindInputChange('cacheTTL', 'performance', 'cacheTTL', 'number');
        this.bindInputChange('maxConcurrentUsers', 'performance', 'maxConcurrentUsers', 'number');
        this.bindInputChange('dbConnectionPool', 'performance', 'dbConnectionPool', 'number');
        this.bindCheckboxChange('autoScaling', 'performance', 'autoScaling');
        this.bindCheckboxChange('performanceMonitoring', 'performance', 'performanceMonitoring');
        this.bindCheckboxChange('errorTracking', 'performance', 'errorTracking');
        this.bindCheckboxChange('resourceMonitoring', 'performance', 'resourceMonitoring');
        this.bindCheckboxChange('alerting', 'performance', 'alerting');

        // Integration settings
        this.bindInputChange('apiRateLimit', 'integration', 'apiRateLimit', 'number');
        this.bindSelectChange('databaseType', 'integration', 'databaseType');
        this.bindSelectChange('messageQueue', 'integration', 'messageQueue');
        this.bindCheckboxChange('webhookEnabled', 'integration', 'webhookEnabled');
        this.bindCheckboxChange('thirdPartyAPIs', 'integration', 'thirdPartyAPIs');

        // Backup settings
        this.bindSelectChange('backupFrequency', 'backup', 'backupFrequency');
        this.bindInputChange('retentionPeriod', 'backup', 'retentionPeriod', 'number');
        this.bindCheckboxChange('autoBackup', 'backup', 'autoBackup');
        this.bindCheckboxChange('encryptedBackup', 'backup', 'encryptedBackup');
        this.bindCheckboxChange('pointInTimeRecovery', 'backup', 'pointInTimeRecovery');
        this.bindCheckboxChange('disasterRecovery', 'backup', 'disasterRecovery');
        this.bindCheckboxChange('failoverSupport', 'backup', 'failoverSupport');
        this.bindSelectChange('recoveryTimeObjective', 'backup', 'recoveryTimeObjective');
    }

    /**
     * Bind input change events
     */
    bindInputChange(elementId, category, key, type = 'string') {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener('change', (e) => {
                let value = e.target.value;
                if (type === 'number') {
                    value = parseInt(value) || 0;
                }
                this.config[category][key] = value;
                this.onConfigurationChange(category, key, value);
            });
        }
    }

    /**
     * Bind select change events
     */
    bindSelectChange(elementId, category, key) {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener('change', (e) => {
                this.config[category][key] = e.target.value;
                this.onConfigurationChange(category, key, e.target.value);
            });
        }
    }

    /**
     * Bind checkbox change events
     */
    bindCheckboxChange(elementId, category, key) {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener('change', (e) => {
                this.config[category][key] = e.target.checked;
                this.onConfigurationChange(category, key, e.target.checked);
            });
        }
    }

    /**
     * Handle configuration changes
     */
    onConfigurationChange(category, key, value) {
        console.log(`🔧 Configuration changed: ${category}.${key} = ${value}`);
        
        // Update metrics if needed
        if (category === 'performance' || category === 'security') {
            this.updateMetrics();
        }
        
        // Show change indicator
        this.showChangeIndicator();
    }

    /**
     * Show change indicator
     */
    showChangeIndicator() {
        const saveButton = document.querySelector('button[onclick="saveAllConfigurations()"]');
        if (saveButton) {
            saveButton.innerHTML = '<i class="fas fa-save me-1"></i>Save All Changes *';
            saveButton.classList.add('btn-warning');
        }
    }

    /**
     * Bind tab events
     */
    bindTabEvents() {
        const tabLinks = document.querySelectorAll('#configTabs .nav-link');
        tabLinks.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const targetId = e.target.getAttribute('data-bs-target');
                this.onTabChange(targetId);
            });
        });
    }

    /**
     * Handle tab changes
     */
    onTabChange(tabId) {
        console.log(`📑 Tab changed to: ${tabId}`);
        
        // Update metrics for performance tab
        if (tabId === '#performance') {
            this.updatePerformanceMetrics();
        }
        
        // Update backup status for backup tab
        if (tabId === '#backup') {
            this.updateBackupStatus();
        }
    }

    /**
     * Bind form events
     */
    bindFormEvents() {
        // Prevent form submission on enter key
        const forms = document.querySelectorAll('.dp-system-configuration form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => e.preventDefault());
        });
    }

    /**
     * Start system monitoring
     */
    startMonitoring() {
        this.monitoringInterval = setInterval(() => {
            this.updateMetrics();
            this.updateHealthStatus();
            this.updatePerformanceMetrics();
        }, 5000); // Update every 5 seconds
    }

    /**
     * Update system metrics
     */
    async updateMetrics() {
        try {
            // Mock metrics data - replace with actual API call
            this.metrics = {
                systemUptime: '99.9%',
                securityScore: '98.5%',
                performanceScore: '95.2%',
                complianceScore: '100%'
            };
            
            this.updateMetricsUI();
        } catch (error) {
            console.error('❌ Failed to update metrics:', error);
        }
    }

    /**
     * Update metrics UI
     */
    updateMetricsUI() {
        Object.keys(this.metrics).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = this.metrics[key];
            }
        });
    }

    /**
     * Update performance metrics
     */
    async updatePerformanceMetrics() {
        try {
            // Mock performance data - replace with actual API call
            const performanceData = {
                cpuUsage: Math.floor(Math.random() * 30) + 30, // 30-60%
                memoryUsage: Math.floor(Math.random() * 20) + 50, // 50-70%
                diskUsage: Math.floor(Math.random() * 15) + 70, // 70-85%
                networkLatency: Math.floor(Math.random() * 10) + 8 // 8-18ms
            };
            
            this.updatePerformanceUI(performanceData);
        } catch (error) {
            console.error('❌ Failed to update performance metrics:', error);
        }
    }

    /**
     * Update performance UI
     */
    updatePerformanceUI(data) {
        Object.keys(data).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = key.includes('Usage') ? `${data[key]}%` : `${data[key]}ms`;
                
                // Update progress bar
                const progressBar = element.parentElement.querySelector('.progress-bar');
                if (progressBar) {
                    progressBar.style.width = `${data[key]}%`;
                }
            }
        });
    }

    /**
     * Update backup status
     */
    async updateBackupStatus() {
        try {
            // Mock backup status - replace with actual API call
            const backupStatus = {
                lastBackupTime: '2 hours ago',
                nextBackupTime: '22 hours',
                backupSize: '2.4 GB',
                backupStatus: 'Healthy'
            };
            
            this.updateBackupStatusUI(backupStatus);
        } catch (error) {
            console.error('❌ Failed to update backup status:', error);
        }
    }

    /**
     * Update backup status UI
     */
    updateBackupStatusUI(data) {
        Object.keys(data).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = data[key];
            }
        });
    }

    /**
     * Update system health status
     */
    async updateHealthStatus() {
        try {
            // Mock health status - replace with actual API call
            this.healthStatus = {
                database: 'healthy',
                network: 'healthy',
                memory: 'warning',
                storage: 'healthy',
                security: 'healthy',
                backup: 'healthy'
            };
            
            this.updateHealthStatusUI();
        } catch (error) {
            console.error('❌ Failed to update health status:', error);
        }
    }

    /**
     * Update health status UI
     */
    updateHealthStatusUI() {
        const healthItems = document.querySelectorAll('.health-item');
        healthItems.forEach(item => {
            const icon = item.querySelector('i');
            const span = item.querySelector('span');
            
            if (icon && span) {
                const status = this.healthStatus[span.textContent.toLowerCase()];
                if (status) {
                    item.className = `health-item ${status}`;
                    
                    // Update icon color based on status
                    if (status === 'healthy') {
                        icon.className = 'fas fa-check-circle text-success fa-2x mb-2';
                    } else if (status === 'warning') {
                        icon.className = 'fas fa-exclamation-triangle text-warning fa-2x mb-2';
                    } else if (status === 'critical') {
                        icon.className = 'fas fa-times-circle text-danger fa-2x mb-2';
                    }
                }
            }
        });
        
        // Update overall health score
        this.updateOverallHealthScore();
    }

    /**
     * Update overall health score
     */
    updateOverallHealthScore() {
        const statuses = Object.values(this.healthStatus);
        const healthyCount = statuses.filter(s => s === 'healthy').length;
        const totalCount = statuses.length;
        const healthScore = Math.round((healthyCount / totalCount) * 100);
        
        const element = document.getElementById('overallHealthScore');
        if (element) {
            element.textContent = `${healthScore}%`;
        }
    }

    /**
     * Save all configurations
     */
    async saveAllConfigurations() {
        try {
            console.log('💾 Saving all configurations...');
            
            // Mock API call - replace with actual save endpoint
            await this.saveConfigurationToBackend(this.config);
            
            this.showSuccess('All configurations saved successfully');
            this.hideChangeIndicator();
            
        } catch (error) {
            console.error('❌ Failed to save configurations:', error);
            this.showError('Failed to save configurations');
        }
    }

    /**
     * Save configuration to backend
     */
    async saveConfigurationToBackend(config) {
        // Mock API call - replace with actual implementation
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log('✅ Configuration saved to backend:', config);
                resolve(true);
            }, 1000);
        });
    }

    /**
     * Export system configuration
     */
    async exportSystemConfig() {
        try {
            console.log('📤 Exporting system configuration...');
            
            const configData = JSON.stringify(this.config, null, 2);
            const blob = new Blob([configData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `system-config-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showSuccess('Configuration exported successfully');
            
        } catch (error) {
            console.error('❌ Failed to export configuration:', error);
            this.showError('Failed to export configuration');
        }
    }

    /**
     * Backup system configuration
     */
    async backupSystemConfig() {
        try {
            console.log('💾 Creating system configuration backup...');
            
            // Mock backup process - replace with actual implementation
            await this.createConfigurationBackup();
            
            this.showSuccess('Configuration backup created successfully');
            
        } catch (error) {
            console.error('❌ Failed to create backup:', error);
            this.showError('Failed to create backup');
        }
    }

    /**
     * Create configuration backup
     */
    async createConfigurationBackup() {
        // Mock backup process - replace with actual implementation
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log('✅ Configuration backup created');
                resolve(true);
            }, 2000);
        });
    }

    /**
     * Hide change indicator
     */
    hideChangeIndicator() {
        const saveButton = document.querySelector('button[onclick="saveAllConfigurations()"]');
        if (saveButton) {
            saveButton.innerHTML = '<i class="fas fa-save me-1"></i>Save All Changes';
            saveButton.classList.remove('btn-warning');
            saveButton.classList.add('btn-primary');
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        // Create or update success notification
        this.showNotification(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        // Create or update error notification
        this.showNotification(message, 'danger');
    }

    /**
     * Show notification
     */
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Destroy the module
     */
    destroy() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
        
        this.isInitialized = false;
        console.log('🔄 System Configuration Module destroyed');
    }
}

// Export the module
window.SystemConfigurationModule = SystemConfigurationModule;

