/**
 * System Management UI Component
 * Handles system configuration, monitoring, and maintenance
 */

export class SystemManagementUIComponent {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.isInitialized = false;
        this.systemConfig = {
            maxSimulations: 10,
            maxMemoryUsage: '8GB',
            enableLogging: true,
            logLevel: 'INFO',
            backupFrequency: 'daily',
            autoUpdate: true
        };
        this.systemMetrics = {
            cpuUsage: 0,
            memoryUsage: 0,
            diskUsage: 0,
            activeSimulations: 0,
            queueLength: 0
        };
        this.systemStatus = 'healthy';
        this.maintenanceMode = false;
        
        // UI elements
        this.elements = {
            systemContainer: null,
            statusPanel: null,
            metricsPanel: null,
            configPanel: null,
            logsPanel: null,
            maintenancePanel: null
        };
        
        // Event listeners
        this.eventListeners = [];
        this.metricsInterval = null;
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
            { event: 'loginSuccess', handleAuthChange },
            { event: 'logout', handleAuthChange }
        );
    }

    handleAuthStateChange() {
        if (this.isAuthenticated) {
            this.loadSystemConfiguration();
            this.enableAuthenticatedFeatures();
        } else {
            this.loadDemoSystemInfo();
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
        
        console.log('🔐 Initializing System Management UI Component...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.initializeUI();
            this.setupEventListeners();
            await this.loadSystemConfiguration();
            this.startSystemMonitoring();
            
            this.isInitialized = true;
            console.log('✅ System Management UI Component initialized');
        } catch (error) {
            console.error('❌ System Management UI Component initialization failed:', error);
            throw error;
        }
    }

    initializeUI() {
        // Initialize UI elements
        this.elements.systemContainer = document.getElementById('system-container');
        this.elements.statusPanel = document.getElementById('system-status-panel');
        this.elements.metricsPanel = document.getElementById('system-metrics-panel');
        this.elements.configPanel = document.getElementById('system-config-panel');
        this.elements.logsPanel = document.getElementById('system-logs-panel');
        this.elements.maintenancePanel = document.getElementById('maintenance-panel');

        if (!this.elements.systemContainer) {
            console.warn('⚠️ System container not found');
            return;
        }

        // Initialize status indicators
        this.initializeStatusIndicators();
    }

    initializeStatusIndicators() {
        if (!this.elements.statusPanel) return;

        const statusHtml = `
            <div class="system-status">
                <div class="status-header">
                    <h4>System Status</h4>
                    <span class="status-indicator ${this.systemStatus}">${this.systemStatus.toUpperCase()}</span>
                </div>
                <div class="status-details">
                    <div class="status-item">
                        <span class="label">Maintenance Mode:</span>
                        <span class="value" id="maintenance-status">${this.maintenanceMode ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    <div class="status-item">
                        <span class="label">Last Update:</span>
                        <span class="value" id="last-update">${new Date().toLocaleString()}</span>
                    </div>
                </div>
            </div>
        `;

        this.elements.statusPanel.innerHTML = statusHtml;
    }

    setupEventListeners() {
        // Configuration form
        const configForm = document.getElementById('system-config-form');
        if (configForm) {
            configForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateSystemConfiguration();
            });
        }

        // Maintenance toggle
        const maintenanceToggle = document.getElementById('maintenance-toggle');
        if (maintenanceToggle) {
            maintenanceToggle.addEventListener('change', (e) => {
                this.toggleMaintenanceMode(e.target.checked);
            });
        }

        // Backup button
        const backupBtn = document.getElementById('create-backup');
        if (backupBtn) {
            backupBtn.addEventListener('click', () => this.createBackup());
        }

        // Restart button
        const restartBtn = document.getElementById('restart-system');
        if (restartBtn) {
            restartBtn.addEventListener('click', () => this.restartSystem());
        }

        // Log refresh
        const refreshLogsBtn = document.getElementById('refresh-logs');
        if (refreshLogsBtn) {
            refreshLogsBtn.addEventListener('click', () => this.refreshSystemLogs());
        }
    }

    async loadSystemConfiguration() {
        try {
            const response = await fetch('/api/physics-modeling/system/config', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const config = await response.json();
                this.systemConfig = { ...this.systemConfig, ...config };
                this.updateConfigurationUI();
            }
        } catch (error) {
            console.error('❌ Failed to load system configuration:', error);
        }
    }

    updateConfigurationUI() {
        const maxSimulationsInput = document.getElementById('max-simulations');
        if (maxSimulationsInput) {
            maxSimulationsInput.value = this.systemConfig.maxSimulations;
        }

        const maxMemoryInput = document.getElementById('max-memory-usage');
        if (maxMemoryInput) {
            maxMemoryInput.value = this.systemConfig.maxMemoryUsage;
        }

        const enableLoggingCheckbox = document.getElementById('enable-logging');
        if (enableLoggingCheckbox) {
            enableLoggingCheckbox.checked = this.systemConfig.enableLogging;
        }

        const logLevelSelect = document.getElementById('log-level');
        if (logLevelSelect) {
            logLevelSelect.value = this.systemConfig.logLevel;
        }

        const backupFrequencySelect = document.getElementById('backup-frequency');
        if (backupFrequencySelect) {
            backupFrequencySelect.value = this.systemConfig.backupFrequency;
        }

        const autoUpdateCheckbox = document.getElementById('auto-update');
        if (autoUpdateCheckbox) {
            autoUpdateCheckbox.checked = this.systemConfig.autoUpdate;
        }
    }

    startSystemMonitoring() {
        // Start metrics collection
        this.collectSystemMetrics();
        
        // Set up periodic metrics collection
        this.metricsInterval = setInterval(() => {
            this.collectSystemMetrics();
        }, 5000); // Every 5 seconds
    }

    async collectSystemMetrics() {
        try {
            const response = await fetch('/api/physics-modeling/system/metrics', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const metrics = await response.json();
                this.systemMetrics = { ...this.systemMetrics, ...metrics };
                this.updateMetricsDisplay();
                this.updateSystemStatus();
            }
        } catch (error) {
            console.error('❌ Failed to collect system metrics:', error);
        }
    }

    updateMetricsDisplay() {
        if (!this.elements.metricsPanel) return;

        const metricsHtml = `
            <div class="system-metrics">
                <h4>System Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">CPU Usage</span>
                        <div class="metric-value">
                            <div class="progress">
                                <div class="progress-bar" style="width: ${this.systemMetrics.cpuUsage}%"></div>
                            </div>
                            <span class="metric-text">${this.systemMetrics.cpuUsage}%</span>
                        </div>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Memory Usage</span>
                        <div class="metric-value">
                            <div class="progress">
                                <div class="progress-bar" style="width: ${this.systemMetrics.memoryUsage}%"></div>
                            </div>
                            <span class="metric-text">${this.systemMetrics.memoryUsage}%</span>
                        </div>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Disk Usage</span>
                        <div class="metric-value">
                            <div class="progress">
                                <div class="progress-bar" style="width: ${this.systemMetrics.diskUsage}%"></div>
                            </div>
                            <span class="metric-text">${this.systemMetrics.diskUsage}%</span>
                        </div>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Active Simulations</span>
                        <span class="metric-text">${this.systemMetrics.activeSimulations}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Queue Length</span>
                        <span class="metric-text">${this.systemMetrics.queueLength}</span>
                    </div>
                </div>
            </div>
        `;

        this.elements.metricsPanel.innerHTML = metricsHtml;
    }

    updateSystemStatus() {
        // Determine system status based on metrics
        let newStatus = 'healthy';
        
        if (this.systemMetrics.cpuUsage > 90 || this.systemMetrics.memoryUsage > 90) {
            newStatus = 'critical';
        } else if (this.systemMetrics.cpuUsage > 80 || this.systemMetrics.memoryUsage > 80) {
            newStatus = 'warning';
        }
        
        if (this.maintenanceMode) {
            newStatus = 'maintenance';
        }
        
        if (this.systemStatus !== newStatus) {
            this.systemStatus = newStatus;
            this.updateStatusDisplay();
        }
    }

    updateStatusDisplay() {
        const statusIndicator = document.querySelector('.status-indicator');
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${this.systemStatus}`;
            statusIndicator.textContent = this.systemStatus.toUpperCase();
        }
    }

    async updateSystemConfiguration() {
        try {
            const form = document.getElementById('system-config-form');
            if (!form) return;

            const formData = new FormData(form);
            const config = {};
            
            for (const [key, value] of formData.entries()) {
                if (key === 'enableLogging' || key === 'autoUpdate') {
                    config[key] = value === 'on';
                } else if (key === 'maxSimulations') {
                    config[key] = parseInt(value);
                } else {
                    config[key] = value;
                }
            }

            this.systemConfig = { ...this.systemConfig, ...config };
            
            const response = await fetch('/api/physics-modeling/system/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(config)
            });

            if (response.ok) {
                console.log('✅ System configuration updated');
                this.showMessage('System configuration updated successfully', 'success');
            }
        } catch (error) {
            console.error('❌ Failed to update system configuration:', error);
            this.showMessage('Failed to update system configuration', 'error');
        }
    }

    async toggleMaintenanceMode(enabled) {
        try {
            const response = await fetch('/api/physics-modeling/system/maintenance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({ enabled: enabled })
            });

            if (response.ok) {
                this.maintenanceMode = enabled;
                this.updateStatusDisplay();
                this.showMessage(`Maintenance mode ${enabled ? 'enabled' : 'disabled'}`, 'info');
            }
        } catch (error) {
            console.error('❌ Failed to toggle maintenance mode:', error);
            this.showMessage('Failed to toggle maintenance mode', 'error');
        }
    }

    async createBackup() {
        try {
            this.showMessage('Creating backup...', 'info');
            
            const response = await fetch('/api/physics-modeling/system/backup', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                this.showMessage(`Backup created successfully: ${result.backupId}`, 'success');
            } else {
                throw new Error('Failed to create backup');
            }
        } catch (error) {
            console.error('❌ Failed to create backup:', error);
            this.showMessage('Failed to create backup', 'error');
        }
    }

    async restartSystem() {
        if (!confirm('Are you sure you want to restart the system? This will stop all active simulations.')) {
            return;
        }

        try {
            this.showMessage('Restarting system...', 'warning');
            
            const response = await fetch('/api/physics-modeling/system/restart', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.showMessage('System restart initiated', 'success');
                // Wait a moment then refresh the page
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            } else {
                throw new Error('Failed to restart system');
            }
        } catch (error) {
            console.error('❌ Failed to restart system:', error);
            this.showMessage('Failed to restart system', 'error');
        }
    }

    async refreshSystemLogs() {
        try {
            const response = await fetch('/api/physics-modeling/system/logs', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const logs = await response.json();
                this.displaySystemLogs(logs);
            }
        } catch (error) {
            console.error('❌ Failed to refresh system logs:', error);
        }
    }

    displaySystemLogs(logs) {
        if (!this.elements.logsPanel) return;

        const logsHtml = `
            <div class="system-logs">
                <h4>System Logs</h4>
                <div class="logs-controls">
                    <select id="log-level-filter">
                        <option value="">All Levels</option>
                        <option value="DEBUG">DEBUG</option>
                        <option value="INFO">INFO</option>
                        <option value="WARNING">WARNING</option>
                        <option value="ERROR">ERROR</option>
                    </select>
                    <button onclick="clearLogs()" class="btn btn-sm btn-secondary">Clear</button>
                </div>
                <div class="logs-content">
                    ${logs.entries.map(log => `
                        <div class="log-entry log-${log.level.toLowerCase()}">
                            <span class="log-timestamp">${new Date(log.timestamp).toLocaleString()}</span>
                            <span class="log-level">${log.level}</span>
                            <span class="log-message">${log.message}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        this.elements.logsPanel.innerHTML = logsHtml;
    }

    async loadDemoSystemInfo() {
        // Load demo system information for unauthenticated users
        this.systemMetrics = {
            cpuUsage: 45,
            memoryUsage: 62,
            diskUsage: 78,
            activeSimulations: 3,
            queueLength: 1
        };
        
        this.systemStatus = 'healthy';
        this.maintenanceMode = false;
        
        this.updateMetricsDisplay();
        this.updateStatusDisplay();
    }

    showMessage(message, type = 'info') {
        // Create a simple message display
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type} alert-dismissible fade show`;
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the container
        if (this.elements.systemContainer) {
            this.elements.systemContainer.insertBefore(messageDiv, this.elements.systemContainer.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 5000);
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
        console.log('🧹 Cleaning up System Management UI Component...');
        
        // Stop metrics collection
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
            this.metricsInterval = null;
        }
        
        // Remove event listeners
        this.eventListeners.forEach(({ event, handler }) => {
            window.removeEventListener(event, handler);
        });
        
        // Clear sensitive data
        this.clearSensitiveData();
        
        this.isInitialized = false;
        console.log('✅ System Management UI Component cleaned up');
    }

    async refresh() {
        if (this.isAuthenticated) {
            await this.loadSystemConfiguration();
            this.collectSystemMetrics();
        } else {
            this.loadDemoSystemInfo();
        }
    }
}
