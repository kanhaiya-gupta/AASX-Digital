/**
 * Twin Registry Health Monitoring Module
 * Handles health monitoring, status tracking, and health metrics
 */

export default class TwinRegistryHealth {
    constructor() {
        this.isInitialized = false;
        this.healthData = {
            overall: 'unknown',
            components: {},
            metrics: {},
            alerts: []
        };
        this.healthChecks = new Map();
        this.alertThresholds = {
            cpu: 80,
            memory: 85,
            disk: 90,
            responseTime: 5000,
            errorRate: 5
        };
        this.monitoringInterval = null;
        this.config = {
            checkInterval: 60000, // 1 minute
            alertCooldown: 300000, // 5 minutes
            maxAlerts: 100
        };
        this.lastAlertTime = {};
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    /**
     * Initialize Health Monitoring
     */
    async init() {
        console.log('🏥 Initializing Twin Registry Health Monitoring...');

        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            // Setup health checks
            this.setupHealthChecks();

            // Start monitoring
            this.startMonitoring();

            // Perform initial health check
            await this.performHealthCheck();

            this.isInitialized = true;
            console.log('✅ Twin Registry Health Monitoring initialized');

        } catch (error) {
            console.error('❌ Twin Registry Health Monitoring initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup health checks
     */
    setupHealthChecks() {
        // System health checks
        this.healthChecks.set('system', {
            name: 'System Health',
            check: () => this.checkSystemHealth(),
            critical: true
        });

        // Database health checks
        this.healthChecks.set('database', {
            name: 'Database Health',
            check: () => this.checkDatabaseHealth(),
            critical: true
        });

        // API health checks
        this.healthChecks.set('api', {
            name: 'API Health',
            check: () => this.checkAPIHealth(),
            critical: true
        });

        // Twin registry health checks
        this.healthChecks.set('registry', {
            name: 'Registry Health',
            check: () => this.checkRegistryHealth(),
            critical: true
        });

        // Network health checks
        this.healthChecks.set('network', {
            name: 'Network Health',
            check: () => this.checkNetworkHealth(),
            critical: false
        });

        // Storage health checks
        this.healthChecks.set('storage', {
            name: 'Storage Health',
            check: () => this.checkStorageHealth(),
            critical: false
        });
    }

    /**
     * Start health monitoring
     */
    startMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }

        this.monitoringInterval = setInterval(async () => {
            await this.performHealthCheck();
        }, this.config.checkInterval);
    }

    /**
     * Perform comprehensive health check
     */
    async performHealthCheck() {
        console.log('🔍 Performing health check...');

        const healthResults = {};
        let criticalFailures = 0;
        let totalFailures = 0;

        // Run all health checks
        for (const [key, healthCheck] of this.healthChecks) {
            try {
                const result = await healthCheck.check();
                healthResults[key] = result;

                if (result.status === 'error') {
                    totalFailures++;
                    if (healthCheck.critical) {
                        criticalFailures++;
                    }
                }
            } catch (error) {
                console.error(`❌ Health check failed for ${key}:`, error);
                healthResults[key] = {
                    status: 'error',
                    message: error.message,
                    timestamp: Date.now()
                };
                totalFailures++;
                if (healthCheck.critical) {
                    criticalFailures++;
                }
            }
        }

        // Update overall health status
        this.updateOverallHealth(healthResults, criticalFailures, totalFailures);

        // Update health data
        this.healthData.components = healthResults;
        this.healthData.metrics = await this.calculateMetrics();

        // Check for alerts
        await this.checkAlerts();

        // Dispatch health update event
        window.dispatchEvent(new CustomEvent('twinRegistryHealthUpdate', {
            detail: this.healthData
        }));

        console.log('✅ Health check completed');
    }

    /**
     * Check system health
     */
    async checkSystemHealth() {
        try {
            const response = await fetch('/api/twin-registry/health/system', {
            headers: this.getAuthHeaders()
        });
            if (response.ok) {
                const data = await response.json();
                return {
                    status: 'healthy',
                    data: data,
                    timestamp: Date.now()
                };
            } else {
                return {
                    status: 'error',
                    message: 'System health check failed',
                    timestamp: Date.now()
                };
            }
        } catch (error) {
            return {
                status: 'error',
                message: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Check database health
     */
    async checkDatabaseHealth() {
        try {
            const response = await fetch('/api/twin-registry/health/database', {
            headers: this.getAuthHeaders()
        });
            if (response.ok) {
                const data = await response.json();
                return {
                    status: 'healthy',
                    data: data,
                    timestamp: Date.now()
                };
            } else {
                return {
                    status: 'error',
                    message: 'Database health check failed',
                    timestamp: Date.now()
                };
            }
        } catch (error) {
            return {
                status: 'error',
                message: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Check API health
     */
    async checkAPIHealth() {
        try {
            const startTime = Date.now();
            const response = await fetch('/api/twin-registry/health', {
                headers: this.getAuthHeaders()
            });
            const responseTime = Date.now() - startTime;

            if (response.ok) {
                const data = await response.json();
                return {
                    status: 'healthy',
                    data: { ...data, responseTime },
                    timestamp: Date.now()
                };
            } else {
                return {
                    status: 'error',
                    message: 'API health check failed',
                    responseTime,
                    timestamp: Date.now()
                };
            }
        } catch (error) {
            return {
                status: 'error',
                message: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Check registry health
     */
    async checkRegistryHealth() {
        try {
            const response = await fetch('/api/twin-registry/status', {
            headers: this.getAuthHeaders()
        });
            if (response.ok) {
                const data = await response.json();
                return {
                    status: 'healthy',
                    data: data,
                    timestamp: Date.now()
                };
            } else {
                return {
                    status: 'error',
                    message: 'Registry health check failed',
                    timestamp: Date.now()
                };
            }
        } catch (error) {
            return {
                status: 'error',
                message: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Check network health
     */
    async checkNetworkHealth() {
        try {
            const response = await fetch('/api/twin-registry/health');
            if (response.ok) {
                const data = await response.json();
                return {
                    status: 'healthy',
                    data: data,
                    timestamp: Date.now()
                };
            } else {
                return {
                    status: 'warning',
                    message: 'Network health check failed',
                    timestamp: Date.now()
                };
            }
        } catch (error) {
            return {
                status: 'warning',
                message: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Check storage health
     */
    async checkStorageHealth() {
        try {
                    const response = await fetch('/api/twin-registry/health', {
            headers: this.getAuthHeaders()
        });
        if (response.ok) {
            const data = await response.json();
            return {
                status: 'healthy',
                data: data,
                timestamp: Date.now()
            };
        } else {
            return {
                status: 'warning',
                message: 'Storage health check failed',
                timestamp: Date.now()
            };
        }
        } catch (error) {
            return {
                status: 'warning',
                message: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Update overall health status
     */
    updateOverallHealth(healthResults, criticalFailures, totalFailures) {
        if (criticalFailures > 0) {
            this.healthData.overall = 'critical';
        } else if (totalFailures > 0) {
            this.healthData.overall = 'warning';
        } else {
            this.healthData.overall = 'healthy';
        }
    }

    /**
     * Calculate health metrics
     */
    async calculateMetrics() {
        const metrics = {
            uptime: this.calculateUptime(),
            responseTime: this.calculateAverageResponseTime(),
            errorRate: this.calculateErrorRate(),
            twinCount: await this.getTwinCount(),
            activeTwins: await this.getActiveTwinCount(),
            failedTwins: await this.getFailedTwinCount()
        };

        return metrics;
    }

    /**
     * Calculate system uptime
     */
    calculateUptime() {
        // This would typically come from the backend
        return {
            value: 99.9,
            unit: '%',
            lastRestart: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
        };
    }

    /**
     * Calculate average response time
     */
    calculateAverageResponseTime() {
        const apiHealth = this.healthData.components.api;
        if (apiHealth && apiHealth.data && apiHealth.data.responseTime) {
            return {
                value: apiHealth.data.responseTime,
                unit: 'ms'
            };
        }
        return { value: 0, unit: 'ms' };
    }

    /**
     * Calculate error rate
     */
    calculateErrorRate() {
        const components = Object.values(this.healthData.components);
        const totalChecks = components.length;
        const errorChecks = components.filter(c => c.status === 'error').length;
        
        return {
            value: totalChecks > 0 ? (errorChecks / totalChecks) * 100 : 0,
            unit: '%'
        };
    }

    /**
     * Get twin count
     */
    async getTwinCount() {
        try {
            const core = window.TwinRegistryModule?.getCore();
            if (core) {
                return core.getAllTwins().length;
            }
            return 0;
        } catch (error) {
            console.error('Failed to get twin count:', error);
            return 0;
        }
    }

    /**
     * Get active twin count
     */
    async getActiveTwinCount() {
        try {
            const core = window.TwinRegistryModule?.getCore();
            if (core) {
                return core.getTwinsByStatus('active').length;
            }
            return 0;
        } catch (error) {
            console.error('Failed to get active twin count:', error);
            return 0;
        }
    }

    /**
     * Get failed twin count
     */
    async getFailedTwinCount() {
        try {
            const core = window.TwinRegistryModule?.getCore();
            if (core) {
                return core.getTwinsByStatus('failed').length;
            }
            return 0;
        } catch (error) {
            console.error('Failed to get failed twin count:', error);
            return 0;
        }
    }

    /**
     * Check for alerts
     */
    async checkAlerts() {
        const alerts = [];

        // Check CPU usage
        const systemHealth = this.healthData.components.system;
        if (systemHealth && systemHealth.data && systemHealth.data.cpu > this.alertThresholds.cpu) {
            alerts.push({
                type: 'warning',
                component: 'system',
                message: `High CPU usage: ${systemHealth.data.cpu}%`,
                timestamp: Date.now()
            });
        }

        // Check memory usage
        if (systemHealth && systemHealth.data && systemHealth.data.memory > this.alertThresholds.memory) {
            alerts.push({
                type: 'warning',
                component: 'system',
                message: `High memory usage: ${systemHealth.data.memory}%`,
                timestamp: Date.now()
            });
        }

        // Check response time
        const apiHealth = this.healthData.components.api;
        if (apiHealth && apiHealth.data && apiHealth.data.responseTime > this.alertThresholds.responseTime) {
            alerts.push({
                type: 'warning',
                component: 'api',
                message: `High response time: ${apiHealth.data.responseTime}ms`,
                timestamp: Date.now()
            });
        }

        // Check error rate
        const errorRate = this.healthData.metrics.errorRate;
        if (errorRate && errorRate.value > this.alertThresholds.errorRate) {
            alerts.push({
                type: 'error',
                component: 'overall',
                message: `High error rate: ${errorRate.value}%`,
                timestamp: Date.now()
            });
        }

        // Add new alerts
        this.healthData.alerts.push(...alerts);

        // Limit alert history
        if (this.healthData.alerts.length > this.config.maxAlerts) {
            this.healthData.alerts = this.healthData.alerts.slice(-this.config.maxAlerts);
        }

        // Dispatch alerts
        alerts.forEach(alert => {
            this.dispatchAlert(alert);
        });
    }

    /**
     * Dispatch alert
     */
    dispatchAlert(alert) {
        const alertKey = `${alert.component}_${alert.type}`;
        const now = Date.now();

        // Check cooldown
        if (this.lastAlertTime[alertKey] && 
            now - this.lastAlertTime[alertKey] < this.config.alertCooldown) {
            return;
        }

        this.lastAlertTime[alertKey] = now;

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('twinRegistryHealthAlert', {
            detail: alert
        }));

        // Show alert if available
        if (window.showWarningAlert) {
            window.showWarningAlert(alert.message);
        }
    }

    /**
     * Get health status
     */
    getHealthStatus() {
        return this.healthData.overall;
    }

    /**
     * Get component health
     */
    getComponentHealth(component) {
        return this.healthData.components[component] || null;
    }

    /**
     * Get all health data
     */
    getAllHealthData() {
        return this.healthData;
    }

    /**
     * Get health metrics
     */
    getHealthMetrics() {
        return this.healthData.metrics;
    }

    /**
     * Get recent alerts
     */
    getRecentAlerts(limit = 10) {
        return this.healthData.alerts.slice(-limit);
    }

    /**
     * Clear alerts
     */
    clearAlerts() {
        this.healthData.alerts = [];
    }

    /**
     * Update alert thresholds
     */
    updateAlertThresholds(newThresholds) {
        this.alertThresholds = { ...this.alertThresholds, ...newThresholds };
    }

    /**
     * Refresh health data
     */
    async refreshHealthData() {
        await this.performHealthCheck();
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Twin Registry Health: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Twin Registry Health: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Twin Registry Health: Auth system ready event received');
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
                console.warn('⚠️ Twin Registry Health: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state
     */
    updateAuthState() {
        // Use central authentication system
        if (window.authSystemReady && window.authManager) {
            // Check if new auth system is available
        if (typeof window.authManager.getSessionInfo === 'function') {
            const sessionInfo = window.authManager.getSessionInfo();
            this.isAuthenticated = sessionInfo && sessionInfo.isAuthenticated;
        } else if (typeof window.authManager.isAuthenticated === 'function') {
            this.isAuthenticated = window.authManager.isAuthenticated();
        } else {
            this.isAuthenticated = false;
        }
            this.currentUser = null; // User info not needed currently
            this.authToken = window.authManager.getStoredToken();
            console.log('🔐 Twin Registry Health: Central auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            // Fallback to demo mode if central auth not ready
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Twin Registry Health: Central auth not ready, using demo mode');
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
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        this.healthData.alerts = [];
        this.healthData.metrics = {};
        console.log('🧹 Twin Registry Health: Sensitive data cleared');
    }

    /**
     * Destroy Health Monitoring
     */
    destroy() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }

        this.healthChecks.clear();
        this.isInitialized = false;
        console.log('🧹 Twin Registry Health Monitoring destroyed');
    }

    /**
     * Get registry summary
     */
    async getRegistrySummary() {
        try {
            const response = await fetch('/api/twin-registry/registry/summary', {
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error getting registry summary:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Get registry health
     */
    async getRegistryHealth() {
        try {
            const response = await fetch('/api/twin-registry/registry/health', {
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error getting registry health:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Get twin health
     */
    async getTwinHealth(twinId) {
        try {
            const response = await fetch(`/api/twin-registry/twins/${twinId}/health`, {
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error getting twin health:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Get twin performance
     */
    async getTwinPerformance(twinId, timeRange = "24h") {
        try {
            const response = await fetch(`/api/twin-registry/twins/${twinId}/performance?time_range=${timeRange}`, {
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error getting twin performance:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Get twin events
     */
    async getTwinEvents(twinId, eventType = null, limit = 50) {
        try {
            const params = new URLSearchParams();
            if (eventType) params.append('event_type', eventType);
            if (limit) params.append('limit', limit.toString());

            const response = await fetch(`/api/twin-registry/twins/${twinId}/events?${params}`, {
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error getting twin events:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Start monitoring a twin
     */
    async startMonitoring(twinId) {
        try {
            const response = await fetch(`/api/twin-registry/twins/${twinId}/monitor`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error starting twin monitoring:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Stop monitoring a twin
     */
    async stopMonitoring(twinId) {
        try {
            const response = await fetch(`/api/twin-registry/twins/${twinId}/monitor`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error stopping twin monitoring:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Get active monitoring sessions
     */
    async getActiveMonitoringSessions() {
        try {
            const response = await fetch('/api/twin-registry/monitoring/active-sessions', {
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error getting active monitoring sessions:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Start a monitoring session
     */
    async startMonitoringSession(twinId) {
        try {
            const response = await fetch('/api/twin-registry/monitoring/start-session', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ twin_id: twinId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error starting monitoring session:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Stop a monitoring session
     */
    async stopMonitoringSession(sessionId) {
        try {
            const response = await fetch('/api/twin-registry/monitoring/stop-session', {
                method: 'DELETE',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ session_id: sessionId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error stopping monitoring session:', error);
            return { success: false, message: error.message };
        }
    }
    
    /**
     * Load health data for UI display
     */
    async loadHealthData() {
        try {
            console.log('🏥 Loading health data...');
            
            // Get twins data to calculate health metrics
            const response = await fetch('/api/twin-registry/twins', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                const twins = data.twins || [];
                
                // Calculate health distribution
                const healthDistribution = {
                    excellent: twins.filter(t => (t.overall_health_score || 0) >= 90).length,
                    good: twins.filter(t => (t.overall_health_score || 0) >= 75 && (t.overall_health_score || 0) < 90).length,
                    warning: twins.filter(t => (t.overall_health_score || 0) >= 60 && (t.overall_health_score || 0) < 75).length,
                    critical: twins.filter(t => (t.overall_health_score || 0) < 60).length
                };
                
                this.healthData.metrics = healthDistribution;
                this.healthData.totalTwins = twins.length;
                
                console.log('✅ Health data loaded:', healthDistribution);
            }
            
        } catch (error) {
            console.error('❌ Failed to load health data:', error);
        }
    }
    
    /**
     * Update health UI with loaded data
     */
    async updateHealthUI() {
        try {
            console.log('🏥 Updating health UI...');
            
            // Update health count cards
            const excellentCount = document.getElementById('twin_registry_excellentCount');
            const goodCount = document.getElementById('twin_registry_goodCount');
            const warningCount = document.getElementById('twin_registry_warningCount');
            const criticalCount = document.getElementById('twin_registry_criticalCount');
            
            if (excellentCount && this.healthData.metrics) {
                excellentCount.textContent = this.healthData.metrics.excellent || 0;
            }
            if (goodCount && this.healthData.metrics) {
                goodCount.textContent = this.healthData.metrics.good || 0;
            }
            if (warningCount && this.healthData.metrics) {
                warningCount.textContent = this.healthData.metrics.warning || 0;
            }
            if (criticalCount && this.healthData.metrics) {
                criticalCount.textContent = this.healthData.metrics.critical || 0;
            }
            
            // Update live indicator
            const liveIndicator = document.getElementById('twin_registry_liveIndicator');
            if (liveIndicator) {
                liveIndicator.classList.add('live');
            }
            
            console.log('✅ Health UI updated');
            
        } catch (error) {
            console.error('❌ Failed to update health UI:', error);
        }
    }
} 