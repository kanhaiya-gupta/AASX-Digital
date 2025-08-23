/**
 * System Core Monitoring Module
 * 
 * Main system monitoring service for the AASX-ETL platform.
 * Provides real-time system health, resource monitoring, and service status
 * with user-based access control and authentication integration.
 * 
 * Phase 6: System Monitoring & Management
 */

class SystemCore {
    constructor() {
        this.baseUrl = '/api/aasx-etl/system';
        this.isInitialized = false;
        this.isMonitoring = false;
        this.monitoringInterval = null;
        this.updateFrequency = 10000; // 10 seconds
        
        // Authentication state
        this.isAuthenticated = false;
        this.currentUser = null;
        this.currentOrg = null;
        
        // Monitoring data
        this.systemHealth = null;
        this.resourceMetrics = null;
        this.serviceStatus = null;
        this.activeAlerts = [];
        
        // Event listeners
        this.healthUpdateCallbacks = [];
        this.alertCallbacks = [];
        this.errorCallbacks = [];
        
        // Initialize
        this.init();
    }
    
    async init() {
        try {
            console.log('🔄 System Core: Initializing...');
            
            // Wait for authentication system
            await this.waitForAuthManager();
            
            // Update authentication state
            this.updateAuthState();
            
            // Start monitoring if authenticated
            if (this.isAuthenticated) {
                await this.startMonitoring();
            }
            
            this.isInitialized = true;
            console.log('✅ System Core: Initialized successfully');
            
        } catch (error) {
            console.error('❌ System Core: Initialization failed:', error);
            this.handleError(error);
        }
    }
    
    async waitForAuthManager() {
        return new Promise((resolve, reject) => {
            const maxWaitTime = 10000; // 10 seconds
            const startTime = Date.now();
            
            const checkAuth = () => {
                if (window.authManager && window.authManager.isInitialized) {
                    resolve();
                } else if (Date.now() - startTime > maxWaitTime) {
                    reject(new Error('Timeout waiting for auth manager'));
                } else {
                    setTimeout(checkAuth, 100);
                }
            };
            
            checkAuth();
        });
    }
    
    updateAuthState() {
        try {
            if (window.authManager) {
                const authState = window.authManager.getCurrentAuthState();
                this.isAuthenticated = authState.isAuthenticated;
                this.currentUser = authState.user;
                this.currentOrg = authState.organization;
                
                console.log(`🔐 System Core: Auth state updated - User: ${this.currentUser?.id}, Org: ${this.currentOrg?.id}`);
            }
        } catch (error) {
            console.error('❌ System Core: Failed to update auth state:', error);
        }
    }
    
    getAuthHeaders() {
        try {
            if (window.authManager) {
                return window.authManager.getAuthHeaders();
            }
            return {};
        } catch (error) {
            console.error('❌ System Core: Failed to get auth headers:', error);
            return {};
        }
    }
    
    async startMonitoring() {
        try {
            if (this.isMonitoring) {
                console.log('🔄 System Core: Monitoring already active');
                return;
            }
            
            if (!this.isAuthenticated) {
                console.warn('⚠️ System Core: Cannot start monitoring - not authenticated');
                return;
            }
            
            console.log('🚀 System Core: Starting system monitoring...');
            
            // Initial data fetch
            await this.fetchSystemData();
            
            // Start periodic updates
            this.monitoringInterval = setInterval(() => {
                this.fetchSystemData();
            }, this.updateFrequency);
            
            this.isMonitoring = true;
            console.log('✅ System Core: Monitoring started successfully');
            
        } catch (error) {
            console.error('❌ System Core: Failed to start monitoring:', error);
            this.handleError(error);
        }
    }
    
    stopMonitoring() {
        try {
            if (this.monitoringInterval) {
                clearInterval(this.monitoringInterval);
                this.monitoringInterval = null;
            }
            
            this.isMonitoring = false;
            console.log('🛑 System Core: Monitoring stopped');
            
        } catch (error) {
            console.error('❌ System Core: Failed to stop monitoring:', error);
        }
    }
    
    async fetchSystemData() {
        try {
            if (!this.isAuthenticated) {
                return;
            }
            
            // Fetch system health
            await this.fetchSystemHealth();
            
            // Fetch resource metrics
            await this.fetchResourceMetrics();
            
            // Fetch service status
            await this.fetchServiceStatus();
            
            // Fetch active alerts
            await this.fetchActiveAlerts();
            
        } catch (error) {
            console.error('❌ System Core: Failed to fetch system data:', error);
            this.handleError(error);
        }
    }
    
    async fetchSystemHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.systemHealth = data;
            
            // Notify listeners
            this.notifyHealthUpdate(data);
            
            console.log('📊 System Core: System health updated');
            
        } catch (error) {
            console.error('❌ System Core: Failed to fetch system health:', error);
            this.handleError(error);
        }
    }
    
    async fetchResourceMetrics() {
        try {
            const response = await fetch(`${this.baseUrl}/resources`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.resourceMetrics = data;
            
            // Notify listeners
            this.notifyHealthUpdate(data);
            
            console.log('📊 System Core: Resource metrics updated');
            
        } catch (error) {
            console.error('❌ System Core: Failed to fetch resource metrics:', error);
            this.handleError(error);
        }
    }
    
    async fetchServiceStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/services`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.serviceStatus = data;
            
            // Notify listeners
            this.notifyHealthUpdate(data);
            
            console.log('📊 System Core: Service status updated');
            
        } catch (error) {
            console.error('❌ System Core: Failed to fetch service status:', error);
            this.handleError(error);
        }
    }
    
    async fetchActiveAlerts() {
        try {
            const response = await fetch(`${this.baseUrl}/alerts/active`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.activeAlerts = data.alerts || [];
            
            // Check for new critical alerts
            this.checkCriticalAlerts();
            
            // Notify listeners
            this.notifyAlerts(data.alerts || []);
            
            console.log(`📊 System Core: Active alerts updated (${this.activeAlerts.length} alerts)`);
            
        } catch (error) {
            console.error('❌ System Core: Failed to fetch active alerts:', error);
            this.handleError(error);
        }
    }
    
    checkCriticalAlerts() {
        try {
            const criticalAlerts = this.activeAlerts.filter(alert => 
                alert.severity === 'critical' || alert.severity === 'emergency'
            );
            
            if (criticalAlerts.length > 0) {
                console.warn(`🚨 System Core: ${criticalAlerts.length} critical alerts detected`);
                
                // Show browser notification if supported
                this.showBrowserNotification(criticalAlerts);
            }
            
        } catch (error) {
            console.error('❌ System Core: Failed to check critical alerts:', error);
        }
    }
    
    showBrowserNotification(alerts) {
        try {
            if (!('Notification' in window) || Notification.permission !== 'granted') {
                return;
            }
            
            const alert = alerts[0]; // Show first critical alert
            new Notification('System Alert', {
                body: alert.message,
                icon: '/static/favicon.ico',
                tag: 'system-alert'
            });
            
        } catch (error) {
            console.error('❌ System Core: Failed to show browser notification:', error);
        }
    }
    
    async acknowledgeAlert(alertId) {
        try {
            const response = await fetch(`${this.baseUrl}/alerts/${alertId}/acknowledge`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            console.log(`✅ System Core: Alert ${alertId} acknowledged`);
            
            // Refresh alerts
            await this.fetchActiveAlerts();
            
        } catch (error) {
            console.error(`❌ System Core: Failed to acknowledge alert ${alertId}:`, error);
            this.handleError(error);
        }
    }
    
    async resolveAlert(alertId) {
        try {
            const response = await fetch(`${this.baseUrl}/alerts/${alertId}/resolve`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            console.log(`✅ System Core: Alert ${alertId} resolved`);
            
            // Refresh alerts
            await this.fetchActiveAlerts();
            
        } catch (error) {
            console.error(`❌ System Core: Failed to resolve alert ${alertId}:`, error);
            this.handleError(error);
        }
    }
    
    // Event handling methods
    onHealthUpdate(callback) {
        this.healthUpdateCallbacks.push(callback);
    }
    
    onAlert(callback) {
        this.alertCallbacks.push(callback);
    }
    
    onError(callback) {
        this.errorCallbacks.push(callback);
    }
    
    notifyHealthUpdate(data) {
        this.healthUpdateCallbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('❌ System Core: Health update callback error:', error);
            }
        });
    }
    
    notifyAlerts(alerts) {
        this.alertCallbacks.forEach(callback => {
            try {
                callback(alerts);
            } catch (error) {
                console.error('❌ System Core: Alert callback error:', error);
            }
        });
    }
    
    handleError(error) {
        console.error('❌ System Core: Error occurred:', error);
        
        this.errorCallbacks.forEach(callback => {
            try {
                callback(error);
            } catch (callbackError) {
                console.error('❌ System Core: Error callback error:', callbackError);
            }
        });
    }
    
    // Public data access methods
    getSystemHealth() {
        return this.systemHealth;
    }
    
    getResourceMetrics() {
        return this.resourceMetrics;
    }
    
    getServiceStatus() {
        return this.serviceStatus;
    }
    
    getActiveAlerts() {
        return this.activeAlerts;
    }
    
    getSystemSummary() {
        return {
            health: this.systemHealth,
            resources: this.resourceMetrics,
            services: this.serviceStatus,
            alerts: this.activeAlerts,
            timestamp: new Date().toISOString()
        };
    }
    
    // Utility methods
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatPercentage(value) {
        return `${value.toFixed(1)}%`;
    }
    
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) {
            return `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }
    
    getHealthStatusColor(status) {
        const colors = {
            'healthy': 'success',
            'warning': 'warning',
            'critical': 'danger',
            'error': 'secondary'
        };
        return colors[status] || 'secondary';
    }
    
    getSeverityColor(severity) {
        const colors = {
            'info': 'info',
            'warning': 'warning',
            'critical': 'danger',
            'emergency': 'danger'
        };
        return colors[severity] || 'secondary';
    }
    
    // Cleanup method
    cleanup() {
        this.stopMonitoring();
        this.healthUpdateCallbacks = [];
        this.alertCallbacks = [];
        this.errorCallbacks = [];
        console.log('🧹 System Core: Cleanup completed');
    }
}

// Export for use in other modules
window.SystemCore = SystemCore;

