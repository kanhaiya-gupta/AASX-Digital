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
    }

    /**
     * Initialize Health Monitoring
     */
    async init() {
        console.log('🏥 Initializing Twin Registry Health Monitoring...');

        try {
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
            const response = await fetch('/api/twin-registry/health/system');
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
            const response = await fetch('/api/twin-registry/health/database');
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
            const response = await fetch('/api/twin-registry/health/api');
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
            const response = await fetch('/api/twin-registry/health/registry');
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
            const response = await fetch('/api/twin-registry/health/network');
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
            const response = await fetch('/api/twin-registry/health/storage');
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
} 