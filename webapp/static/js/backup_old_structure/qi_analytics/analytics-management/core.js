/**
 * Quality Intelligence Analytics Core Module
 * Handles core analytics operations, metrics calculation, and analytics functionality
 */

export default class QIAnalyticsCore {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/qi-analytics',
            maxDataPoints: 100000,
            maxMetrics: 1000,
            batchSize: 100,
            timeout: 30000,
            retryAttempts: 3,
            retryDelay: 1000,
            cacheEnabled: true,
            cacheExpiry: 300000, // 5 minutes
            realtimeEnabled: true,
            aggregationEnabled: true
        };

        this.metrics = new Map();
        this.kpis = new Map();
        this.dimensions = new Map();
        this.filters = new Map();
        this.cache = new Map();
        this.operations = [];
        this.isProcessing = false;
        this.realtimeConnections = new Map();
        this.statistics = {
            totalMetrics: 0,
            totalKPIs: 0,
            totalDimensions: 0,
            totalDataPoints: 0,
            lastUpdate: null,
            dataSize: 0
        };
    }

    /**
     * Initialize the QI Analytics Core
     */
    async init() {
        console.log('🔧 Initializing Quality Intelligence Analytics Core...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize analytics storage
            await this.initializeAnalyticsStorage();

            // Load existing analytics data
            await this.loadExistingAnalyticsData();

            // Initialize cache
            if (this.config.cacheEnabled) {
                this.initializeCache();
            }

            // Start operation queue
            this.startOperationQueue();

            // Initialize realtime connections
            if (this.config.realtimeEnabled) {
                this.initializeRealtimeConnections();
            }

            this.isInitialized = true;
            console.log('✅ Quality Intelligence Analytics Core initialized');

        } catch (error) {
            console.error('❌ Quality Intelligence Analytics Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize analytics storage
     */
    async initializeAnalyticsStorage() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/initialize`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to initialize analytics storage: ${response.statusText}`);
            }
            
            console.log('Analytics storage initialized');
        } catch (error) {
            console.error('Analytics storage initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load existing analytics data
     */
    async loadExistingAnalyticsData() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/analytics-data`);
            if (response.ok) {
                const data = await response.json();
                
                // Load metrics
                if (data.metrics) {
                    data.metrics.forEach(metric => {
                        this.metrics.set(metric.id, metric);
                    });
                }

                // Load KPIs
                if (data.kpis) {
                    data.kpis.forEach(kpi => {
                        this.kpis.set(kpi.id, kpi);
                    });
                }

                // Load dimensions
                if (data.dimensions) {
                    data.dimensions.forEach(dimension => {
                        this.dimensions.set(dimension.id, dimension);
                    });
                }

                // Update statistics
                this.updateStatistics();
            }
        } catch (error) {
            console.error('Failed to load existing analytics data:', error);
        }
    }

    /**
     * Initialize cache system
     */
    initializeCache() {
        // Set up cache cleanup interval
        setInterval(() => {
            this.cleanupCache();
        }, this.config.cacheExpiry);
    }

    /**
     * Start operation queue
     */
    startOperationQueue() {
        setInterval(() => {
            this.processOperationQueue();
        }, 1000);
    }

    /**
     * Initialize realtime connections
     */
    initializeRealtimeConnections() {
        // Set up WebSocket connections for real-time data
        this.setupRealtimeConnections();
    }

    /**
     * Create a new metric
     */
    async createMetric(name, type, definition, options = {}) {
        const metricData = {
            name,
            type,
            definition,
            options,
            created: new Date().toISOString(),
            status: 'active'
        };

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/metrics`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(metricData)
            });

            if (response.ok) {
                const metric = await response.json();
                this.metrics.set(metric.id, metric);
                
                // Update cache
                this.cache.set(`metric:${metric.id}`, {
                    data: metric,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('qiMetricCreated', {
                    detail: { metric }
                }));

                return metric;
            } else {
                throw new Error(`Failed to create metric: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Metric creation failed:', error);
            throw error;
        }
    }

    /**
     * Update an existing metric
     */
    async updateMetric(metricId, updates = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/metrics/${metricId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });

            if (response.ok) {
                const updatedMetric = await response.json();
                this.metrics.set(metricId, updatedMetric);
                
                // Update cache
                this.cache.set(`metric:${metricId}`, {
                    data: updatedMetric,
                    timestamp: Date.now()
                });

                // Dispatch event
                window.dispatchEvent(new CustomEvent('qiMetricUpdated', {
                    detail: { metric: updatedMetric }
                }));

                return updatedMetric;
            } else {
                throw new Error(`Failed to update metric: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Metric update failed:', error);
            throw error;
        }
    }

    /**
     * Delete a metric
     */
    async deleteMetric(metricId) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/metrics/${metricId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.metrics.delete(metricId);
                this.cache.delete(`metric:${metricId}`);
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('qiMetricDeleted', {
                    detail: { metricId }
                }));

                return true;
            } else {
                throw new Error(`Failed to delete metric: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Metric deletion failed:', error);
            throw error;
        }
    }

    /**
     * Create a new KPI
     */
    async createKPI(name, target, current, unit, thresholds = {}) {
        const kpiData = {
            name,
            target,
            current,
            unit,
            thresholds,
            created: new Date().toISOString(),
            status: 'active'
        };

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/kpis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(kpiData)
            });

            if (response.ok) {
                const kpi = await response.json();
                this.kpis.set(kpi.id, kpi);
                
                // Update cache
                this.cache.set(`kpi:${kpi.id}`, {
                    data: kpi,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('qiKPICreated', {
                    detail: { kpi }
                }));

                return kpi;
            } else {
                throw new Error(`Failed to create KPI: ${response.statusText}`);
            }
        } catch (error) {
            console.error('KPI creation failed:', error);
            throw error;
        }
    }

    /**
     * Update KPI value
     */
    async updateKPIValue(kpiId, newValue, timestamp = null) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/kpis/${kpiId}/value`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    value: newValue,
                    timestamp: timestamp || new Date().toISOString()
                })
            });

            if (response.ok) {
                const updatedKPI = await response.json();
                this.kpis.set(kpiId, updatedKPI);
                
                // Update cache
                this.cache.set(`kpi:${kpiId}`, {
                    data: updatedKPI,
                    timestamp: Date.now()
                });

                // Dispatch event
                window.dispatchEvent(new CustomEvent('qiKPIUpdated', {
                    detail: { kpi: updatedKPI }
                }));

                return updatedKPI;
            } else {
                throw new Error(`Failed to update KPI value: ${response.statusText}`);
            }
        } catch (error) {
            console.error('KPI value update failed:', error);
            throw error;
        }
    }

    /**
     * Calculate metric value
     */
    async calculateMetric(metricId, parameters = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/metrics/${metricId}/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ parameters })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update cache
                this.cache.set(`metric_calc:${metricId}`, {
                    data: result,
                    timestamp: Date.now()
                });

                return result;
            } else {
                throw new Error(`Failed to calculate metric: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Metric calculation failed:', error);
            throw error;
        }
    }

    /**
     * Get analytics data
     */
    async getAnalyticsData(filters = {}, dimensions = [], metrics = [], timeRange = null) {
        const queryParams = new URLSearchParams();
        
        if (filters && Object.keys(filters).length > 0) {
            queryParams.append('filters', JSON.stringify(filters));
        }
        
        if (dimensions && dimensions.length > 0) {
            queryParams.append('dimensions', JSON.stringify(dimensions));
        }
        
        if (metrics && metrics.length > 0) {
            queryParams.append('metrics', JSON.stringify(metrics));
        }
        
        if (timeRange) {
            queryParams.append('timeRange', JSON.stringify(timeRange));
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/data?${queryParams.toString()}`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to get analytics data: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get analytics data failed:', error);
            throw error;
        }
    }

    /**
     * Get metric by ID
     */
    async getMetric(metricId) {
        // Check cache first
        const cacheKey = `metric:${metricId}`;
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            return cached.data;
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/metrics/${metricId}`);
            if (response.ok) {
                const metric = await response.json();
                
                // Update cache
                this.cache.set(cacheKey, {
                    data: metric,
                    timestamp: Date.now()
                });

                return metric;
            } else {
                throw new Error(`Failed to get metric: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get metric failed:', error);
            throw error;
        }
    }

    /**
     * Get KPI by ID
     */
    async getKPI(kpiId) {
        // Check cache first
        const cacheKey = `kpi:${kpiId}`;
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            return cached.data;
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/kpis/${kpiId}`);
            if (response.ok) {
                const kpi = await response.json();
                
                // Update cache
                this.cache.set(cacheKey, {
                    data: kpi,
                    timestamp: Date.now()
                });

                return kpi;
            } else {
                throw new Error(`Failed to get KPI: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get KPI failed:', error);
            throw error;
        }
    }

    /**
     * Get analytics statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Update statistics
     */
    updateStatistics() {
        this.statistics = {
            totalMetrics: this.metrics.size,
            totalKPIs: this.kpis.size,
            totalDimensions: this.dimensions.size,
            totalDataPoints: this.calculateTotalDataPoints(),
            lastUpdate: new Date().toISOString(),
            dataSize: this.calculateDataSize()
        };
    }

    /**
     * Calculate total data points
     */
    calculateTotalDataPoints() {
        let total = 0;
        
        // Sum data points from all metrics
        for (const metric of this.metrics.values()) {
            total += metric.dataPoints || 0;
        }
        
        return total;
    }

    /**
     * Calculate data size in bytes
     */
    calculateDataSize() {
        let size = 0;
        
        // Calculate metrics size
        for (const metric of this.metrics.values()) {
            size += JSON.stringify(metric).length;
        }
        
        // Calculate KPIs size
        for (const kpi of this.kpis.values()) {
            size += JSON.stringify(kpi).length;
        }
        
        // Calculate dimensions size
        for (const dimension of this.dimensions.values()) {
            size += JSON.stringify(dimension).length;
        }
        
        return size;
    }

    /**
     * Process operation queue
     */
    async processOperationQueue() {
        if (this.isProcessing || this.operations.length === 0) {
            return;
        }

        this.isProcessing = true;

        try {
            const batch = this.operations.splice(0, this.config.batchSize);
            
            for (const operation of batch) {
                try {
                    await this.executeOperation(operation);
                } catch (error) {
                    console.error('Operation execution failed:', error);
                    // Add back to queue for retry if retries remaining
                    if (operation.retries < this.config.retryAttempts) {
                        operation.retries++;
                        this.operations.unshift(operation);
                    }
                }
            }
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Execute a single operation
     */
    async executeOperation(operation) {
        switch (operation.type) {
            case 'createMetric':
                await this.createMetric(operation.name, operation.type, operation.definition, operation.options);
                break;
            case 'updateMetric':
                await this.updateMetric(operation.metricId, operation.updates);
                break;
            case 'deleteMetric':
                await this.deleteMetric(operation.metricId);
                break;
            case 'createKPI':
                await this.createKPI(operation.name, operation.target, operation.current, operation.unit, operation.thresholds);
                break;
            case 'updateKPI':
                await this.updateKPIValue(operation.kpiId, operation.value, operation.timestamp);
                break;
            default:
                throw new Error(`Unknown operation type: ${operation.type}`);
        }
    }

    /**
     * Add operation to queue
     */
    addToQueue(operation) {
        operation.retries = 0;
        this.operations.push(operation);
    }

    /**
     * Cleanup cache
     */
    cleanupCache() {
        const now = Date.now();
        for (const [key, value] of this.cache.entries()) {
            if (now - value.timestamp > this.config.cacheExpiry) {
                this.cache.delete(key);
            }
        }
    }

    /**
     * Setup realtime connections
     */
    setupRealtimeConnections() {
        // Set up WebSocket connections for real-time data updates
        const wsUrl = this.config.apiBaseUrl.replace('http', 'ws') + '/realtime';
        
        try {
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('QI Analytics realtime connection established');
                this.realtimeConnections.set('main', ws);
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealtimeData(data);
            };
            
            ws.onerror = (error) => {
                console.error('QI Analytics realtime connection error:', error);
            };
            
            ws.onclose = () => {
                console.log('QI Analytics realtime connection closed');
                this.realtimeConnections.delete('main');
                
                // Attempt to reconnect
                setTimeout(() => {
                    this.setupRealtimeConnections();
                }, 5000);
            };
        } catch (error) {
            console.error('Failed to setup realtime connection:', error);
        }
    }

    /**
     * Handle realtime data
     */
    handleRealtimeData(data) {
        switch (data.type) {
            case 'metric_update':
                this.handleMetricUpdate(data.payload);
                break;
            case 'kpi_update':
                this.handleKPIUpdate(data.payload);
                break;
            case 'alert':
                this.handleAlert(data.payload);
                break;
            default:
                console.log('Unknown realtime data type:', data.type);
        }
    }

    /**
     * Handle metric update
     */
    handleMetricUpdate(payload) {
        const { metricId, value, timestamp } = payload;
        
        // Update cache
        this.cache.set(`metric_calc:${metricId}`, {
            data: { value, timestamp },
            timestamp: Date.now()
        });
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('qiMetricRealtimeUpdate', {
            detail: { metricId, value, timestamp }
        }));
    }

    /**
     * Handle KPI update
     */
    handleKPIUpdate(payload) {
        const { kpiId, value, timestamp } = payload;
        
        // Update KPI in memory
        const kpi = this.kpis.get(kpiId);
        if (kpi) {
            kpi.current = value;
            kpi.lastUpdate = timestamp;
            this.kpis.set(kpiId, kpi);
        }
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('qiKPIRealtimeUpdate', {
            detail: { kpiId, value, timestamp }
        }));
    }

    /**
     * Handle alert
     */
    handleAlert(payload) {
        // Dispatch alert event
        window.dispatchEvent(new CustomEvent('qiAlert', {
            detail: payload
        }));
    }

    /**
     * Refresh analytics data
     */
    async refreshData() {
        try {
            await this.loadExistingAnalyticsData();
            this.updateStatistics();
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('qiDataRefreshed', {
                detail: { statistics: this.statistics }
            }));
        } catch (error) {
            console.error('Data refresh failed:', error);
            throw error;
        }
    }

    /**
     * Clear all data
     */
    async clearAllData() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/clear`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.metrics.clear();
                this.kpis.clear();
                this.dimensions.clear();
                this.cache.clear();
                this.operations = [];
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('qiDataCleared'));
            } else {
                throw new Error(`Failed to clear data: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Clear data failed:', error);
            throw error;
        }
    }

    /**
     * Export analytics data
     */
    async exportAnalytics(format = 'json', filters = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ format, filters })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to export analytics: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Export failed:', error);
            throw error;
        }
    }

    /**
     * Import analytics data
     */
    async importAnalytics(data, format = 'json') {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/import`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ data, format })
            });

            if (response.ok) {
                await this.loadExistingAnalyticsData();
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('qiDataImported', {
                    detail: { data, format }
                }));
            } else {
                throw new Error(`Failed to import analytics: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Import failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the core module
     */
    destroy() {
        this.isInitialized = false;
        
        // Close realtime connections
        for (const [key, connection] of this.realtimeConnections) {
            if (connection && connection.readyState === WebSocket.OPEN) {
                connection.close();
            }
        }
        this.realtimeConnections.clear();
        
        this.metrics.clear();
        this.kpis.clear();
        this.dimensions.clear();
        this.cache.clear();
        this.operations = [];
        console.log('🧹 Quality Intelligence Analytics Core destroyed');
    }
} 