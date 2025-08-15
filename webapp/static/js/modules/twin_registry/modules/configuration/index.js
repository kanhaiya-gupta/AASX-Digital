/**
 * System Configuration Module - Main Orchestrator
 * Handles system configuration management and settings
 */

import { ConfigurationOperations } from './operations.js';
import { ConfigurationUI } from './ui.js';

class ConfigurationManager {
    constructor(baseUrl = '/api/twin-registry') {
        this.baseUrl = baseUrl;
        this.operations = null;
        this.ui = null;
        this.isInitialized = false;
        this.currentConfig = {};
        this.modifiedSections = new Set();
    }

    async init() {
        try {
            console.log('🔄 Initializing Configuration Manager...');
            
            // Wait for central authentication system
            await new Promise((resolve) => {
                if (window.authSystemReady && window.authManager) {
                    resolve();
                } else {
                    window.addEventListener('authSystemReady', resolve, { once: true });
                }
            });
            
            // Initialize sub-modules
            this.operations = new ConfigurationOperations(this.baseUrl);
            this.ui = new ConfigurationUI();
            
            // Initialize sub-modules with auth
            await this.operations.init();
            await this.ui.init();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load initial configuration
            await this.loadConfiguration();
            
            this.isInitialized = true;
            console.log('✅ Configuration Manager initialized');
            
            // Dispatch ready event
            document.dispatchEvent(new CustomEvent('configurationManagerReady'));
            
        } catch (error) {
            console.error('❌ Configuration Manager initialization failed:', error);
            throw error;
        }
    }

    setupEventListeners() {
        // Configuration form changes
        this.setupFormListeners();
        
        // Save all button
        const saveAllBtn = document.querySelector('button[onclick="saveAllConfigurations()"]');
        if (saveAllBtn) {
            saveAllBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.saveAllConfigurations();
            });
        }

        // Reset button
        const resetBtn = document.querySelector('button[onclick="resetToDefaults()"]');
        if (resetBtn) {
            resetBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.resetToDefaults();
            });
        }

        // Tab change events
        const configTabs = document.querySelectorAll('#configTabs .nav-link');
        configTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.handleTabChange(e.target.getAttribute('data-bs-target'));
            });
        });
    }

    setupFormListeners() {
        // Registry settings
        const registryInputs = [
            'registryName', 'defaultTwinType', 'maxTwinsPerProject', 
            'autoStartMonitoring', 'dataRetentionPeriod', 'backupFrequency',
            'enableDataCompression', 'enableDataEncryption'
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
            'refreshInterval', 'enableWebSocket', 'enableBrowserNotifications',
            'maxConcurrentMonitors', 'healthThreshold', 'performanceThreshold',
            'enableEmailAlerts', 'alertRetentionDays'
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
            'enableAuthentication', 'sessionTimeout', 'maxLoginAttempts',
            'enableTwoFactor', 'enableRoleBasedAccess', 'enableAuditLogging',
            'ipWhitelist', 'enableCORS'
        ];

        securityInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('change', () => this.markSectionModified('security'));
                input.addEventListener('input', () => this.markSectionModified('security'));
            }
        });

        // Integration settings
        const integrationInputs = [
            'enableAASXIntegration', 'aasxSyncInterval', 'enableAASXValidation',
            'enableExternalSync', 'externalSyncTimeout', 'enableRetryOnFailure'
        ];

        integrationInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('change', () => this.markSectionModified('integration'));
                input.addEventListener('input', () => this.markSectionModified('integration'));
            }
        });
    }

    markSectionModified(section) {
        this.modifiedSections.add(section);
        this.ui.updateSaveButtonState(this.modifiedSections.size > 0);
    }

    async loadConfiguration() {
        try {
            console.log('📊 Loading system configuration...');
            
            const config = await this.operations.getConfiguration();
            this.currentConfig = config;
            
            // Populate form fields
            this.ui.populateConfigurationForm(config);
            
            console.log('✅ Configuration loaded');
            
        } catch (error) {
            console.error('❌ Failed to load configuration:', error);
            this.ui.showError('Failed to load configuration');
        }
    }

    async saveAllConfigurations() {
        try {
            if (this.modifiedSections.size === 0) {
                this.ui.showInfo('No changes to save');
                return;
            }

            console.log('💾 Saving all configurations...');
            
            // Collect all form data
            const configData = this.ui.collectConfigurationData();
            
            // Show save progress
            this.ui.showSaveProgress();
            
            const result = await this.operations.saveConfiguration(configData);
            
            if (result.success) {
                this.ui.showSuccess('Configuration saved successfully');
                this.modifiedSections.clear();
                this.ui.updateSaveButtonState(false);
                this.currentConfig = configData;
                
                // Dispatch event
                document.dispatchEvent(new CustomEvent('configurationSaved', { 
                    detail: { config: configData } 
                }));
            } else {
                this.ui.showError(result.message || 'Failed to save configuration');
            }
            
        } catch (error) {
            console.error('❌ Failed to save configuration:', error);
            this.ui.showError('Failed to save configuration');
        } finally {
            this.ui.hideSaveProgress();
        }
    }

    async resetToDefaults() {
        try {
            if (!confirm('Are you sure you want to reset all configuration to defaults? This action cannot be undone.')) {
                return;
            }

            console.log('🔄 Resetting configuration to defaults...');
            
            const result = await this.operations.resetToDefaults();
            
            if (result.success) {
                this.ui.showSuccess('Configuration reset to defaults');
                await this.loadConfiguration();
                this.modifiedSections.clear();
                this.ui.updateSaveButtonState(false);
            } else {
                this.ui.showError(result.message || 'Failed to reset configuration');
            }
            
        } catch (error) {
            console.error('❌ Failed to reset configuration:', error);
            this.ui.showError('Failed to reset configuration');
        }
    }

    async saveSection(section) {
        try {
            console.log(`💾 Saving ${section} configuration...`);
            
            const sectionData = this.ui.collectSectionData(section);
            const result = await this.operations.saveSection(section, sectionData);
            
            if (result.success) {
                this.ui.showSuccess(`${section} configuration saved`);
                this.modifiedSections.delete(section);
                this.ui.updateSaveButtonState(this.modifiedSections.size > 0);
            } else {
                this.ui.showError(result.message || `Failed to save ${section} configuration`);
            }
            
        } catch (error) {
            console.error(`❌ Failed to save ${section} configuration:`, error);
            this.ui.showError(`Failed to save ${section} configuration`);
        }
    }

    handleTabChange(targetId) {
        const section = targetId.replace('#', '');
        this.ui.updateTabUI(section);
        
        // Check if section has unsaved changes
        if (this.modifiedSections.has(section)) {
            this.ui.showUnsavedChangesWarning(section);
        }
    }

    async validateConfiguration(configData) {
        try {
            const result = await this.operations.validateConfiguration(configData);
            return result;
        } catch (error) {
            console.error('❌ Configuration validation failed:', error);
            return { valid: false, errors: [error.message] };
        }
    }

    async exportConfiguration(format = 'json') {
        try {
            const result = await this.operations.exportConfiguration(format);
            
            if (result.success) {
                this.ui.downloadConfiguration(result.data, format);
            } else {
                this.ui.showError(result.message || 'Failed to export configuration');
            }
            
        } catch (error) {
            console.error('❌ Failed to export configuration:', error);
            this.ui.showError('Failed to export configuration');
        }
    }

    async importConfiguration(file) {
        try {
            const result = await this.operations.importConfiguration(file);
            
            if (result.success) {
                this.ui.showSuccess('Configuration imported successfully');
                await this.loadConfiguration();
            } else {
                this.ui.showError(result.message || 'Failed to import configuration');
            }
            
        } catch (error) {
            console.error('❌ Failed to import configuration:', error);
            this.ui.showError('Failed to import configuration');
        }
    }

    // Public methods for external use
    async refreshConfiguration() {
        await this.loadConfiguration();
    }

    async getCurrentConfiguration() {
        return this.currentConfig;
    }

    async hasUnsavedChanges() {
        return this.modifiedSections.size > 0;
    }

    // Cleanup method
    cleanup() {
        console.log('🧹 Cleaning up Configuration Manager...');
        this.isInitialized = false;
        this.modifiedSections.clear();
        this.ui.cleanup();
    }
}

export default ConfigurationManager; 