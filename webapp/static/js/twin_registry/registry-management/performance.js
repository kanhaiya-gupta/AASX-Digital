/**
 * Twin Registry Performance Monitoring Module
 * Handles performance monitoring, metrics collection, and performance analysis
 */

export default class TwinRegistryPerformance {
    constructor() {
        this.isInitialized = false;
        this.performanceData = {
            metrics: {},
            history: [],
            alerts: [],
            thresholds: {
                responseTime: 2000,
                throughput: 100,
                errorRate: 5,
                cpuUsage: 80,
                memoryUsage: 85
            }
        };
        this.metricsCollector = new Map();
        this.monitoringInterval = null;
        this.config = {
            collectionInterval: 30000, // 30 seconds
            historyRetention: 100, // Keep last 100 data points
            alertCooldown: 300000, // 5 minutes
            maxAlerts: 50
        };
        this.lastAlertTime = {};
        this.performanceCounters = {
            requests: 0,
            errors: 0,
            startTime: Date.now()
        };
    }

    /**
     * Initialize Performance Monitoring
     */
    async init() {
        console.log('⚡ Initializing Twin Registry Performance Monitoring...');

        try {
            // Setup metrics collection
            this.setupMetricsCollection();

            // Start monitoring
            this.startMonitoring();

            // Perform initial performance check
            await this.collectPerformanceMetrics();

            this.isInitialized = true;
            console.log('✅ Twin Registry Performance Monitoring initialized');

        } catch (error) {
            console.error('❌ Twin Registry Performance Monitoring initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup metrics collection
     */
    setupMetricsCollection() {
        // Response time metrics
        this.metricsCollector.set('responseTime', {
            name: 'Response Time',
            collect: () => this.collectResponseTimeMetrics(),
            unit: 'ms'
        });

        // Throughput metrics
        this.metricsCollector.set('throughput', {
            name: 'Throughput',
            collect: () => this.collectThroughputMetrics(),
            unit: 'requests/sec'
        });

        // Error rate metrics
        this.metricsCollector.set('errorRate', {
            name: 'Error Rate',
            collect: () => this.collectErrorRateMetrics(),
            unit: '%'
        });

        // System performance metrics
        this.metricsCollector.set('system', {
            name: 'System Performance',
            collect: () => this.collectSystemMetrics(),
            unit: 'various'
        });

        // Registry-specific metrics
        this.metricsCollector.set('registry', {
            name: 'Registry Performance',
            collect: () => this.collectRegistryMetrics(),
            unit: 'various'
        });
    }

    /**
     * Start performance monitoring
     */
    startMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }

        this.monitoringInterval = setInterval(async () => {
            await this.collectPerformanceMetrics();
        }, this.config.collectionInterval);
    }

    /**
     * Collect all performance metrics
     */
    async collectPerformanceMetrics() {
        console.log('📊 Collecting performance metrics...');

        const metrics = {};
        const timestamp = Date.now();

        // Collect all metrics
        for (const [key, collector] of this.metricsCollector) {
            try {
                const data = await collector.collect();
                metrics[key] = {
                    ...data,
                    timestamp
                };
            } catch (error) {
                console.error(`❌ Failed to collect ${key} metrics:`, error);
                metrics[key] = {
                    value: 0,
                    status: 'error',
                    message: error.message,
                    timestamp
                };
            }
        }

        // Update performance data
        this.performanceData.metrics = metrics;

        // Add to history
        this.performanceData.history.push({
            timestamp,
            metrics
        });

        // Limit history size
        if (this.performanceData.history.length > this.config.historyRetention) {
            this.performanceData.history = this.performanceData.history.slice(-this.config.historyRetention);
        }

        // Check for performance alerts
        await this.checkPerformanceAlerts();

        // Dispatch performance update event
        window.dispatchEvent(new CustomEvent('twinRegistryPerformanceUpdate', {
            detail: this.performanceData
        }));

        console.log('✅ Performance metrics collected');
    }

    /**
     * Collect response time metrics
     */
    async collectResponseTimeMetrics() {
        try {
            const startTime = Date.now();
            const response = await fetch('/api/twin-registry/performance/response-time');
            const responseTime = Date.now() - startTime;

            if (response.ok) {
                const data = await response.json();
                return {
                    value: responseTime,
                    status: responseTime <= this.performanceData.thresholds.responseTime ? 'good' : 'warning',
                    details: data
                };
            } else {
                return {
                    value: responseTime,
                    status: 'error',
                    message: 'Response time check failed'
                };
            }
        } catch (error) {
            return {
                value: 0,
                status: 'error',
                message: error.message
            };
        }
    }

    /**
     * Collect throughput metrics
     */
    async collectThroughputMetrics() {
        try {
            const response = await fetch('/api/twin-registry/performance/throughput');
            if (response.ok) {
                const data = await response.json();
                const throughput = data.requestsPerSecond || 0;

                return {
                    value: throughput,
                    status: throughput >= this.performanceData.thresholds.throughput ? 'good' : 'warning',
                    details: data
                };
            } else {
                return {
                    value: 0,
                    status: 'error',
                    message: 'Throughput check failed'
                };
            }
        } catch (error) {
            return {
                value: 0,
                status: 'error',
                message: error.message
            };
        }
    }

    /**
     * Collect error rate metrics
     */
    async collectErrorRateMetrics() {
        try {
            const response = await fetch('/api/twin-registry/performance/error-rate');
            if (response.ok) {
                const data = await response.json();
                const errorRate = data.errorRate || 0;

                return {
                    value: errorRate,
                    status: errorRate <= this.performanceData.thresholds.errorRate ? 'good' : 'warning',
                    details: data
                };
            } else {
                return {
                    value: 0,
                    status: 'error',
                    message: 'Error rate check failed'
                };
            }
        } catch (error) {
            return {
                value: 0,
                status: 'error',
                message: error.message
            };
        }
    }

    /**
     * Collect system performance metrics
     */
    async collectSystemMetrics() {
        try {
            const response = await fetch('/api/twin-registry/performance/system');
            if (response.ok) {
                const data = await response.json();
                
                const cpuStatus = data.cpu <= this.performanceData.thresholds.cpuUsage ? 'good' : 'warning';
                const memoryStatus = data.memory <= this.performanceData.thresholds.memoryUsage ? 'good' : 'warning';

                return {
                    value: {
                        cpu: data.cpu,
                        memory: data.memory,
                        disk: data.disk,
                        network: data.network
                    },
                    status: cpuStatus === 'good' && memoryStatus === 'good' ? 'good' : 'warning',
                    details: data
                };
            } else {
                return {
                    value: {},
                    status: 'error',
                    message: 'System performance check failed'
                };
            }
        } catch (error) {
            return {
                value: {},
                status: 'error',
                message: error.message
            };
        }
    }

    /**
     * Collect registry-specific metrics
     */
    async collectRegistryMetrics() {
        try {
                                const response = await fetch('/api/twin-registry/twins/statistics');
            if (response.ok) {
                const data = await response.json();
                
                return {
                    value: {
                        twinCount: data.total_twins || 0,
                        activeTwins: data.active_twins || 0,
                        failedTwins: data.failed_twins || 0,
                        registrationRate: data.registration_rate || 0,
                        updateRate: data.update_rate || 0
                    },
                    status: 'good',
                    details: data
                };
            } else {
                return {
                    value: {},
                    status: 'error',
                    message: 'Registry performance check failed'
                };
            }
        } catch (error) {
            return {
                value: {},
                status: 'error',
                message: error.message
            };
        }
    }

    /**
     * Check for performance alerts
     */
    async checkPerformanceAlerts() {
        const alerts = [];
        const metrics = this.performanceData.metrics;

        // Check response time
        if (metrics.responseTime && metrics.responseTime.value > this.performanceData.thresholds.responseTime) {
            alerts.push({
                type: 'warning',
                metric: 'responseTime',
                message: `High response time: ${metrics.responseTime.value}ms`,
                value: metrics.responseTime.value,
                threshold: this.performanceData.thresholds.responseTime,
                timestamp: Date.now()
            });
        }

        // Check throughput
        if (metrics.throughput && metrics.throughput.value < this.performanceData.thresholds.throughput) {
            alerts.push({
                type: 'warning',
                metric: 'throughput',
                message: `Low throughput: ${metrics.throughput.value} requests/sec`,
                value: metrics.throughput.value,
                threshold: this.performanceData.thresholds.throughput,
                timestamp: Date.now()
            });
        }

        // Check error rate
        if (metrics.errorRate && metrics.errorRate.value > this.performanceData.thresholds.errorRate) {
            alerts.push({
                type: 'error',
                metric: 'errorRate',
                message: `High error rate: ${metrics.errorRate.value}%`,
                value: metrics.errorRate.value,
                threshold: this.performanceData.thresholds.errorRate,
                timestamp: Date.now()
            });
        }

        // Check system metrics
        if (metrics.system && metrics.system.value) {
            if (metrics.system.value.cpu > this.performanceData.thresholds.cpuUsage) {
                alerts.push({
                    type: 'warning',
                    metric: 'cpu',
                    message: `High CPU usage: ${metrics.system.value.cpu}%`,
                    value: metrics.system.value.cpu,
                    threshold: this.performanceData.thresholds.cpuUsage,
                    timestamp: Date.now()
                });
            }

            if (metrics.system.value.memory > this.performanceData.thresholds.memoryUsage) {
                alerts.push({
                    type: 'warning',
                    metric: 'memory',
                    message: `High memory usage: ${metrics.system.value.memory}%`,
                    value: metrics.system.value.memory,
                    threshold: this.performanceData.thresholds.memoryUsage,
                    timestamp: Date.now()
                });
            }
        }

        // Add new alerts
        this.performanceData.alerts.push(...alerts);

        // Limit alert history
        if (this.performanceData.alerts.length > this.config.maxAlerts) {
            this.performanceData.alerts = this.performanceData.alerts.slice(-this.config.maxAlerts);
        }

        // Dispatch alerts
        alerts.forEach(alert => {
            this.dispatchPerformanceAlert(alert);
        });
    }

    /**
     * Dispatch performance alert
     */
    dispatchPerformanceAlert(alert) {
        const alertKey = `${alert.metric}_${alert.type}`;
        const now = Date.now();

        // Check cooldown
        if (this.lastAlertTime[alertKey] && 
            now - this.lastAlertTime[alertKey] < this.config.alertCooldown) {
            return;
        }

        this.lastAlertTime[alertKey] = now;

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('twinRegistryPerformanceAlert', {
            detail: alert
        }));

        // Show alert if available
        if (window.showWarningAlert) {
            window.showWarningAlert(alert.message);
        }
    }

    /**
     * Get performance metrics
     */
    getPerformanceMetrics() {
        return this.performanceData.metrics;
    }

    /**
     * Get performance history
     */
    getPerformanceHistory(limit = 50) {
        return this.performanceData.history.slice(-limit);
    }

    /**
     * Get performance alerts
     */
    getPerformanceAlerts(limit = 10) {
        return this.performanceData.alerts.slice(-limit);
    }

    /**
     * Get performance statistics
     */
    getPerformanceStats() {
        const history = this.performanceData.history;
        if (history.length === 0) {
            return {};
        }

        const stats = {};
        const metrics = Object.keys(this.metricsCollector);

        metrics.forEach(metric => {
            const values = history
                .map(h => h.metrics[metric]?.value)
                .filter(v => typeof v === 'number')
                .sort((a, b) => a - b);

            if (values.length > 0) {
                stats[metric] = {
                    min: values[0],
                    max: values[values.length - 1],
                    avg: values.reduce((a, b) => a + b, 0) / values.length,
                    median: values[Math.floor(values.length / 2)]
                };
            }
        });

        return stats;
    }

    /**
     * Get uptime statistics
     */
    getUptimeStats() {
        const uptime = Date.now() - this.performanceCounters.startTime;
        const hours = Math.floor(uptime / (1000 * 60 * 60));
        const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((uptime % (1000 * 60)) / 1000);

        return {
            total: uptime,
            formatted: `${hours}h ${minutes}m ${seconds}s`,
            startTime: this.performanceCounters.startTime
        };
    }

    /**
     * Update performance thresholds
     */
    updatePerformanceThresholds(newThresholds) {
        this.performanceData.thresholds = { 
            ...this.performanceData.thresholds, 
            ...newThresholds 
        };
    }

    /**
     * Clear performance alerts
     */
    clearPerformanceAlerts() {
        this.performanceData.alerts = [];
    }

    /**
     * Get performance configuration
     */
    getConfiguration() {
        return this.config;
    }

    /**
     * Update performance configuration
     */
    updateConfiguration(newConfig) {
        this.config = { ...this.config, ...newConfig };
        this.startMonitoring();
    }

    /**
     * Refresh performance data
     */
    async refreshPerformanceData() {
        await this.collectPerformanceMetrics();
    }

    /**
     * Destroy Performance Monitoring
     */
    destroy() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }

        this.metricsCollector.clear();
        this.isInitialized = false;
        console.log('🧹 Twin Registry Performance Monitoring destroyed');
    }
} 