/**
 * Quality Intelligence Analytics Data Processor Module
 * Handles data processing, analysis, aggregation, and transformation
 */

export default class QIDataProcessor {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/qi-analytics',
            maxDataPoints: 1000000,
            maxProcessingTime: 300000, // 5 minutes
            batchSize: 1000,
            aggregationEnabled: true,
            filteringEnabled: true,
            transformationEnabled: true,
            validationEnabled: true,
            cacheEnabled: true,
            cacheExpiry: 600000, // 10 minutes
            parallelProcessing: true,
            maxWorkers: 4
        };

        this.processors = new Map();
        this.aggregators = new Map();
        this.filters = new Map();
        this.transformers = new Map();
        this.validators = new Map();
        this.cache = new Map();
        this.processingQueue = [];
        this.isProcessing = false;
        this.workers = [];
        this.statistics = {
            processedRecords: 0,
            processedBatches: 0,
            processingErrors: 0,
            cacheHits: 0,
            cacheMisses: 0,
            lastProcessed: null,
            averageProcessingTime: 0
        };
    }

    /**
     * Initialize the Data Processor
     */
    async init() {
        console.log('🔧 Initializing Quality Intelligence Data Processor...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize processors
            this.initializeProcessors();

            // Initialize aggregators
            this.initializeAggregators();

            // Initialize filters
            this.initializeFilters();

            // Initialize transformers
            this.initializeTransformers();

            // Initialize validators
            this.initializeValidators();

            // Initialize workers
            if (this.config.parallelProcessing) {
                this.initializeWorkers();
            }

            // Start processing queue
            this.startProcessingQueue();

            this.isInitialized = true;
            console.log('✅ Quality Intelligence Data Processor initialized');

        } catch (error) {
            console.error('❌ Quality Intelligence Data Processor initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/processor-config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load processor configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize data processors
     */
    initializeProcessors() {
        // Time series processor
        this.processors.set('timeseries', {
            process: (data, options = {}) => {
                const { timeField = 'timestamp', valueField = 'value', interval = '1h' } = options;
                
                // Group data by time intervals
                const grouped = this.groupByTimeInterval(data, timeField, interval);
                
                // Aggregate values within each interval
                return this.aggregateTimeSeries(grouped, valueField);
            },
            validate: (data) => {
                return data && Array.isArray(data) && data.length > 0;
            }
        });

        // Categorical processor
        this.processors.set('categorical', {
            process: (data, options = {}) => {
                const { categoryField = 'category', valueField = 'value' } = options;
                
                // Group data by category
                const grouped = this.groupByCategory(data, categoryField);
                
                // Calculate statistics for each category
                return this.calculateCategoryStats(grouped, valueField);
            },
            validate: (data) => {
                return data && Array.isArray(data) && data.length > 0;
            }
        });

        // Numerical processor
        this.processors.set('numerical', {
            process: (data, options = {}) => {
                const { valueField = 'value', bins = 10 } = options;
                
                // Extract numerical values
                const values = data.map(item => parseFloat(item[valueField])).filter(v => !isNaN(v));
                
                // Calculate statistics
                const stats = this.calculateNumericalStats(values);
                
                // Create histogram
                const histogram = this.createHistogram(values, bins);
                
                return { stats, histogram };
            },
            validate: (data) => {
                return data && Array.isArray(data) && data.length > 0;
            }
        });
    }

    /**
     * Initialize aggregators
     */
    initializeAggregators() {
        // Sum aggregator
        this.aggregators.set('sum', (values) => {
            return values.reduce((sum, val) => sum + (parseFloat(val) || 0), 0);
        });

        // Average aggregator
        this.aggregators.set('avg', (values) => {
            const validValues = values.filter(val => !isNaN(parseFloat(val)));
            if (validValues.length === 0) return 0;
            return validValues.reduce((sum, val) => sum + parseFloat(val), 0) / validValues.length;
        });

        // Count aggregator
        this.aggregators.set('count', (values) => {
            return values.length;
        });

        // Min aggregator
        this.aggregators.set('min', (values) => {
            const validValues = values.filter(val => !isNaN(parseFloat(val)));
            return validValues.length > 0 ? Math.min(...validValues.map(v => parseFloat(v))) : null;
        });

        // Max aggregator
        this.aggregators.set('max', (values) => {
            const validValues = values.filter(val => !isNaN(parseFloat(val)));
            return validValues.length > 0 ? Math.max(...validValues.map(v => parseFloat(v))) : null;
        });

        // Median aggregator
        this.aggregators.set('median', (values) => {
            const validValues = values.filter(val => !isNaN(parseFloat(val))).map(v => parseFloat(v)).sort((a, b) => a - b);
            if (validValues.length === 0) return null;
            
            const mid = Math.floor(validValues.length / 2);
            return validValues.length % 2 === 0 
                ? (validValues[mid - 1] + validValues[mid]) / 2 
                : validValues[mid];
        });

        // Standard deviation aggregator
        this.aggregators.set('std', (values) => {
            const validValues = values.filter(val => !isNaN(parseFloat(val))).map(v => parseFloat(v));
            if (validValues.length === 0) return 0;
            
            const mean = validValues.reduce((sum, val) => sum + val, 0) / validValues.length;
            const squaredDiffs = validValues.map(val => Math.pow(val - mean, 2));
            const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / validValues.length;
            
            return Math.sqrt(variance);
        });
    }

    /**
     * Initialize filters
     */
    initializeFilters() {
        // Range filter
        this.filters.set('range', (data, field, min, max) => {
            return data.filter(item => {
                const value = parseFloat(item[field]);
                return !isNaN(value) && value >= min && value <= max;
            });
        });

        // Date range filter
        this.filters.set('dateRange', (data, field, startDate, endDate) => {
            const start = new Date(startDate);
            const end = new Date(endDate);
            
            return data.filter(item => {
                const date = new Date(item[field]);
                return date >= start && date <= end;
            });
        });

        // Category filter
        this.filters.set('category', (data, field, categories) => {
            return data.filter(item => categories.includes(item[field]));
        });

        // Text filter
        this.filters.set('text', (data, field, searchTerm, exact = false) => {
            return data.filter(item => {
                const value = String(item[field] || '').toLowerCase();
                const term = searchTerm.toLowerCase();
                return exact ? value === term : value.includes(term);
            });
        });

        // Null filter
        this.filters.set('null', (data, field, includeNull = false) => {
            return data.filter(item => {
                const isNull = item[field] === null || item[field] === undefined || item[field] === '';
                return includeNull ? isNull : !isNull;
            });
        });
    }

    /**
     * Initialize transformers
     */
    initializeTransformers() {
        // Normalize transformer
        this.transformers.set('normalize', (data, field, method = 'minmax') => {
            const values = data.map(item => parseFloat(item[field])).filter(v => !isNaN(v));
            
            if (values.length === 0) return data;
            
            const min = Math.min(...values);
            const max = Math.max(...values);
            const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
            const std = this.aggregators.get('std')(values);
            
            return data.map(item => {
                const value = parseFloat(item[field]);
                if (isNaN(value)) return item;
                
                let normalized;
                switch (method) {
                    case 'minmax':
                        normalized = (value - min) / (max - min);
                        break;
                    case 'zscore':
                        normalized = (value - mean) / std;
                        break;
                    case 'decimal':
                        normalized = value / Math.pow(10, Math.floor(Math.log10(max)));
                        break;
                    default:
                        normalized = value;
                }
                
                return { ...item, [field + '_normalized']: normalized };
            });
        });

        // Log transform
        this.transformers.set('log', (data, field, base = 10) => {
            return data.map(item => {
                const value = parseFloat(item[field]);
                if (isNaN(value) || value <= 0) return item;
                
                const transformed = Math.log(value) / Math.log(base);
                return { ...item, [field + '_log']: transformed };
            });
        });

        // Bin transformer
        this.transformers.set('bin', (data, field, bins = 10) => {
            const values = data.map(item => parseFloat(item[field])).filter(v => !isNaN(v));
            
            if (values.length === 0) return data;
            
            const min = Math.min(...values);
            const max = Math.max(...values);
            const binSize = (max - min) / bins;
            
            return data.map(item => {
                const value = parseFloat(item[field]);
                if (isNaN(value)) return item;
                
                const binIndex = Math.min(Math.floor((value - min) / binSize), bins - 1);
                const binStart = min + binIndex * binSize;
                const binEnd = min + (binIndex + 1) * binSize;
                
                return { 
                    ...item, 
                    [field + '_bin']: binIndex,
                    [field + '_bin_range']: `${binStart.toFixed(2)}-${binEnd.toFixed(2)}`
                };
            });
        });
    }

    /**
     * Initialize validators
     */
    initializeValidators() {
        // Data type validator
        this.validators.set('dataType', (data, field, expectedType) => {
            const errors = [];
            
            data.forEach((item, index) => {
                const value = item[field];
                let isValid = true;
                
                switch (expectedType) {
                    case 'number':
                        isValid = !isNaN(parseFloat(value));
                        break;
                    case 'string':
                        isValid = typeof value === 'string';
                        break;
                    case 'boolean':
                        isValid = typeof value === 'boolean' || value === 'true' || value === 'false';
                        break;
                    case 'date':
                        isValid = !isNaN(new Date(value).getTime());
                        break;
                    default:
                        isValid = true;
                }
                
                if (!isValid) {
                    errors.push({
                        index,
                        field,
                        value,
                        expectedType,
                        message: `Invalid data type for field ${field}`
                    });
                }
            });
            
            return { isValid: errors.length === 0, errors };
        });

        // Range validator
        this.validators.set('range', (data, field, min, max) => {
            const errors = [];
            
            data.forEach((item, index) => {
                const value = parseFloat(item[field]);
                if (!isNaN(value) && (value < min || value > max)) {
                    errors.push({
                        index,
                        field,
                        value,
                        min,
                        max,
                        message: `Value ${value} is outside valid range [${min}, ${max}]`
                    });
                }
            });
            
            return { isValid: errors.length === 0, errors };
        });

        // Required field validator
        this.validators.set('required', (data, field) => {
            const errors = [];
            
            data.forEach((item, index) => {
                if (item[field] === null || item[field] === undefined || item[field] === '') {
                    errors.push({
                        index,
                        field,
                        message: `Required field ${field} is missing or empty`
                    });
                }
            });
            
            return { isValid: errors.length === 0, errors };
        });
    }

    /**
     * Initialize workers for parallel processing
     */
    initializeWorkers() {
        for (let i = 0; i < this.config.maxWorkers; i++) {
            const worker = {
                id: i,
                busy: false,
                currentTask: null
            };
            this.workers.push(worker);
        }
    }

    /**
     * Start processing queue
     */
    startProcessingQueue() {
        setInterval(() => {
            this.processQueue();
        }, 100);
    }

    /**
     * Process data with specified processor
     */
    async processData(data, processorType, options = {}) {
        const startTime = Date.now();
        
        try {
            // Check cache first
            if (this.config.cacheEnabled) {
                const cacheKey = this.generateCacheKey(data, processorType, options);
                const cached = this.cache.get(cacheKey);
                if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
                    this.statistics.cacheHits++;
                    return cached.data;
                }
            }

            // Get processor
            const processor = this.processors.get(processorType);
            if (!processor) {
                throw new Error(`Processor type '${processorType}' not found`);
            }

            // Validate data
            if (processor.validate) {
                const validation = processor.validate(data);
                if (!validation.isValid) {
                    throw new Error(`Data validation failed: ${validation.errors.join(', ')}`);
                }
            }

            // Process data
            const result = await this.executeProcessing(data, processor, options);
            
            const processingTime = Date.now() - startTime;
            this.statistics.averageProcessingTime = 
                (this.statistics.averageProcessingTime * this.statistics.processedBatches + processingTime) / 
                (this.statistics.processedBatches + 1);

            // Cache result
            if (this.config.cacheEnabled) {
                const cacheKey = this.generateCacheKey(data, processorType, options);
                this.cache.set(cacheKey, {
                    data: result,
                    timestamp: Date.now()
                });
            }

            this.statistics.processedRecords += data.length;
            this.statistics.processedBatches++;
            this.statistics.lastProcessed = new Date().toISOString();

            return result;

        } catch (error) {
            this.statistics.processingErrors++;
            console.error('Data processing failed:', error);
            throw error;
        }
    }

    /**
     * Execute processing with timeout
     */
    async executeProcessing(data, processor, options) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Processing timeout exceeded'));
            }, this.config.maxProcessingTime);

            try {
                const result = processor.process(data, options);
                clearTimeout(timeout);
                resolve(result);
            } catch (error) {
                clearTimeout(timeout);
                reject(error);
            }
        });
    }

    /**
     * Apply filters to data
     */
    applyFilters(data, filters = []) {
        let filteredData = [...data];
        
        for (const filter of filters) {
            const { type, field, ...params } = filter;
            const filterFn = this.filters.get(type);
            
            if (filterFn) {
                filteredData = filterFn(filteredData, field, ...Object.values(params));
            }
        }
        
        return filteredData;
    }

    /**
     * Apply transformations to data
     */
    applyTransformations(data, transformations = []) {
        let transformedData = [...data];
        
        for (const transform of transformations) {
            const { type, field, ...params } = transform;
            const transformer = this.transformers.get(type);
            
            if (transformer) {
                transformedData = transformer(transformedData, field, ...Object.values(params));
            }
        }
        
        return transformedData;
    }

    /**
     * Validate data
     */
    validateData(data, validations = []) {
        const results = [];
        
        for (const validation of validations) {
            const { type, field, ...params } = validation;
            const validator = this.validators.get(type);
            
            if (validator) {
                const result = validator(data, field, ...Object.values(params));
                results.push({ type, field, ...result });
            }
        }
        
        return results;
    }

    /**
     * Aggregate data
     */
    aggregateData(data, groupBy, aggregations = []) {
        const groups = {};
        
        // Group data
        data.forEach(item => {
            const key = groupBy.map(field => item[field]).join('|');
            if (!groups[key]) {
                groups[key] = [];
            }
            groups[key].push(item);
        });
        
        // Apply aggregations
        const results = [];
        for (const [key, groupData] of Object.entries(groups)) {
            const result = {};
            
            // Add group values
            const groupValues = key.split('|');
            groupBy.forEach((field, index) => {
                result[field] = groupValues[index];
            });
            
            // Apply aggregations
            aggregations.forEach(agg => {
                const { field, operation, alias } = agg;
                const values = groupData.map(item => item[field]);
                const aggregator = this.aggregators.get(operation);
                
                if (aggregator) {
                    result[alias || `${field}_${operation}`] = aggregator(values);
                }
            });
            
            results.push(result);
        }
        
        return results;
    }

    /**
     * Group data by time interval
     */
    groupByTimeInterval(data, timeField, interval) {
        const groups = {};
        
        data.forEach(item => {
            const timestamp = new Date(item[timeField]);
            const intervalKey = this.getTimeIntervalKey(timestamp, interval);
            
            if (!groups[intervalKey]) {
                groups[intervalKey] = [];
            }
            groups[intervalKey].push(item);
        });
        
        return groups;
    }

    /**
     * Get time interval key
     */
    getTimeIntervalKey(timestamp, interval) {
        const date = new Date(timestamp);
        
        switch (interval) {
            case '1m':
                return date.toISOString().slice(0, 16);
            case '5m':
                const minutes = Math.floor(date.getMinutes() / 5) * 5;
                return new Date(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), minutes).toISOString();
            case '1h':
                return date.toISOString().slice(0, 13);
            case '1d':
                return date.toISOString().slice(0, 10);
            case '1w':
                const weekStart = new Date(date);
                weekStart.setDate(date.getDate() - date.getDay());
                return weekStart.toISOString().slice(0, 10);
            case '1M':
                return date.toISOString().slice(0, 7);
            case '1y':
                return date.toISOString().slice(0, 4);
            default:
                return date.toISOString();
        }
    }

    /**
     * Aggregate time series data
     */
    aggregateTimeSeries(groupedData, valueField) {
        const results = [];
        
        for (const [interval, data] of Object.entries(groupedData)) {
            const values = data.map(item => parseFloat(item[valueField])).filter(v => !isNaN(v));
            
            results.push({
                interval,
                count: values.length,
                sum: this.aggregators.get('sum')(values),
                avg: this.aggregators.get('avg')(values),
                min: this.aggregators.get('min')(values),
                max: this.aggregators.get('max')(values)
            });
        }
        
        return results.sort((a, b) => new Date(a.interval) - new Date(b.interval));
    }

    /**
     * Group data by category
     */
    groupByCategory(data, categoryField) {
        const groups = {};
        
        data.forEach(item => {
            const category = item[categoryField] || 'Unknown';
            if (!groups[category]) {
                groups[category] = [];
            }
            groups[category].push(item);
        });
        
        return groups;
    }

    /**
     * Calculate category statistics
     */
    calculateCategoryStats(groupedData, valueField) {
        const results = [];
        
        for (const [category, data] of Object.entries(groupedData)) {
            const values = data.map(item => parseFloat(item[valueField])).filter(v => !isNaN(v));
            
            results.push({
                category,
                count: values.length,
                sum: this.aggregators.get('sum')(values),
                avg: this.aggregators.get('avg')(values),
                min: this.aggregators.get('min')(values),
                max: this.aggregators.get('max')(values)
            });
        }
        
        return results.sort((a, b) => b.count - a.count);
    }

    /**
     * Calculate numerical statistics
     */
    calculateNumericalStats(values) {
        return {
            count: values.length,
            sum: this.aggregators.get('sum')(values),
            avg: this.aggregators.get('avg')(values),
            min: this.aggregators.get('min')(values),
            max: this.aggregators.get('max')(values),
            median: this.aggregators.get('median')(values),
            std: this.aggregators.get('std')(values)
        };
    }

    /**
     * Create histogram
     */
    createHistogram(values, bins) {
        if (values.length === 0) return [];
        
        const min = Math.min(...values);
        const max = Math.max(...values);
        const binSize = (max - min) / bins;
        
        const histogram = new Array(bins).fill(0).map((_, i) => ({
            bin: i,
            start: min + i * binSize,
            end: min + (i + 1) * binSize,
            count: 0
        }));
        
        values.forEach(value => {
            const binIndex = Math.min(Math.floor((value - min) / binSize), bins - 1);
            histogram[binIndex].count++;
        });
        
        return histogram;
    }

    /**
     * Process queue
     */
    async processQueue() {
        if (this.isProcessing || this.processingQueue.length === 0) {
            return;
        }

        this.isProcessing = true;

        try {
            const batch = this.processingQueue.splice(0, this.config.batchSize);
            
            if (this.config.parallelProcessing && this.workers.length > 0) {
                await this.processBatchParallel(batch);
            } else {
                await this.processBatchSequential(batch);
            }
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Process batch sequentially
     */
    async processBatchSequential(batch) {
        for (const task of batch) {
            try {
                const result = await this.processData(task.data, task.processorType, task.options);
                task.resolve(result);
            } catch (error) {
                task.reject(error);
            }
        }
    }

    /**
     * Process batch in parallel
     */
    async processBatchParallel(batch) {
        const promises = batch.map(task => {
            return new Promise((resolve, reject) => {
                const worker = this.getAvailableWorker();
                if (worker) {
                    worker.busy = true;
                    worker.currentTask = task;
                    
                    this.processData(task.data, task.processorType, task.options)
                        .then(result => {
                            worker.busy = false;
                            worker.currentTask = null;
                            resolve(result);
                        })
                        .catch(error => {
                            worker.busy = false;
                            worker.currentTask = null;
                            reject(error);
                        });
                } else {
                    reject(new Error('No available workers'));
                }
            });
        });
        
        await Promise.all(promises);
    }

    /**
     * Get available worker
     */
    getAvailableWorker() {
        return this.workers.find(worker => !worker.busy);
    }

    /**
     * Add task to processing queue
     */
    addToQueue(data, processorType, options = {}) {
        return new Promise((resolve, reject) => {
            this.processingQueue.push({
                data,
                processorType,
                options,
                resolve,
                reject
            });
        });
    }

    /**
     * Generate cache key
     */
    generateCacheKey(data, processorType, options) {
        const dataHash = btoa(JSON.stringify(data)).slice(0, 50);
        const optionsHash = btoa(JSON.stringify(options)).slice(0, 50);
        return `${processorType}_${dataHash}_${optionsHash}`;
    }

    /**
     * Get statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('Data processor cache cleared');
    }

    /**
     * Refresh data
     */
    async refreshData() {
        try {
            // Clear cache
            this.clearCache();
            
            // Reset statistics
            this.statistics = {
                processedRecords: 0,
                processedBatches: 0,
                processingErrors: 0,
                cacheHits: 0,
                cacheMisses: 0,
                lastProcessed: null,
                averageProcessingTime: 0
            };
            
            console.log('Data processor refreshed');
        } catch (error) {
            console.error('Data processor refresh failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the data processor
     */
    destroy() {
        this.isInitialized = false;
        this.processors.clear();
        this.aggregators.clear();
        this.filters.clear();
        this.transformers.clear();
        this.validators.clear();
        this.cache.clear();
        this.processingQueue = [];
        this.workers = [];
        console.log('🧹 Quality Intelligence Data Processor destroyed');
    }
} 