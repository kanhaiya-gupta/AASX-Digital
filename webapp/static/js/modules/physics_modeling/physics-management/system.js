/**
 * System Manager
 * Handles system configuration, monitoring, and maintenance
 */

export class SystemManager {
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
    }

    handleAuthStateChange() {
        if (this.isAuthenticated) {
            this.loadSystemConfiguration();
        } else {
            this.loadDemoSystemInfo();
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
        
        console.log('🔐 Initializing System Manager...');
        
        try {
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            await this.loadSystemConfiguration();
            this.startSystemMonitoring();
            
            this.isInitialized = true;
            console.log('✅ System Manager initialized');
        } catch (error) {
            console.error('❌ System Manager initialization failed:', error);
            throw error;
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
            }
        } catch (error) {
            console.error('❌ Failed to load system configuration:', error);
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
                this.updateSystemStatus();
            }
        } catch (error) {
            console.error('❌ Failed to collect system metrics:', error);
        }
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
        }
    }

    async updateSystemConfiguration(config) {
        try {
            const response = await fetch('/api/physics-modeling/system/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(config)
            });

            if (response.ok) {
                this.systemConfig = { ...this.systemConfig, ...config };
                return true;
            }
        } catch (error) {
            console.error('❌ Failed to update system configuration:', error);
        }
        return false;
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
                this.updateSystemStatus();
                return true;
            }
        } catch (error) {
            console.error('❌ Failed to toggle maintenance mode:', error);
        }
        return false;
    }

    async createBackup() {
        try {
            const response = await fetch('/api/physics-modeling/system/backup', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const result = await response.json();
                return result.backupId;
            }
        } catch (error) {
            console.error('❌ Failed to create backup:', error);
        }
        return null;
    }

    async restartSystem() {
        try {
            const response = await fetch('/api/physics-modeling/system/restart', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                return true;
            }
        } catch (error) {
            console.error('❌ Failed to restart system:', error);
        }
        return false;
    }

    async getSystemLogs(level = null, limit = 100) {
        try {
            const params = new URLSearchParams();
            if (level) params.append('level', level);
            if (limit) params.append('limit', limit);

            const response = await fetch(`/api/physics-modeling/system/logs?${params}`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('❌ Failed to get system logs:', error);
        }
        return null;
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
    }

    getSystemConfiguration() {
        return { ...this.systemConfig };
    }

    getSystemMetrics() {
        return { ...this.systemMetrics };
    }

    getSystemStatus() {
        return this.systemStatus;
    }

    isMaintenanceMode() {
        return this.maintenanceMode;
    }

    async cleanup() {
        console.log('🧹 Cleaning up System Manager...');
        
        // Stop metrics collection
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
            this.metricsInterval = null;
        }
        
        this.clearSensitiveData();
        this.isInitialized = false;
        console.log('✅ System Manager cleaned up');
    }
}
