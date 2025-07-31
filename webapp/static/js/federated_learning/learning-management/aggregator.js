/**
 * Federated Learning Aggregator Module
 * Handles model aggregation, algorithm management, and convergence tracking
 */

export default class FederatedLearningAggregator {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/federated-learning',
            aggregationEnabled: true,
            supportedAlgorithms: {
                fedavg: {
                    name: 'Federated Averaging',
                    description: 'Standard federated averaging algorithm',
                    parameters: ['learning_rate', 'momentum']
                },
                fedprox: {
                    name: 'Federated Proximal',
                    description: 'Proximal term for better convergence',
                    parameters: ['mu', 'learning_rate']
                },
                fedsgd: {
                    name: 'Federated SGD',
                    description: 'Federated stochastic gradient descent',
                    parameters: ['learning_rate', 'batch_size']
                },
                scaffold: {
                    name: 'SCAFFOLD',
                    description: 'Control variates for federated learning',
                    parameters: ['learning_rate', 'control_variates']
                }
            },
            defaultAlgorithm: 'fedavg',
            aggregationTimeout: 600000, // 10 minutes
            convergenceThreshold: 0.001,
            maxConvergenceRounds: 50,
            modelCompression: true,
            compressionRatio: 0.8,
            cacheEnabled: true,
            cacheExpiry: 300000, // 5 minutes
            batchAggregation: true,
            batchSize: 10
        };

        this.aggregators = new Map();
        this.models = new Map();
        this.gradients = new Map();
        this.weights = new Map();
        this.convergenceHistory = [];
        this.aggregationQueue = [];
        this.isProcessing = false;
        this.cache = new Map();
        this.statistics = {
            totalAggregations: 0,
            successfulAggregations: 0,
            failedAggregations: 0,
            averageConvergenceTime: 0,
            totalConvergenceRounds: 0,
            lastAggregation: null,
            cacheHits: 0,
            cacheMisses: 0
        };
    }

    /**
     * Initialize the Federated Learning Aggregator
     */
    async init() {
        console.log('🔧 Initializing Federated Learning Aggregator...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize aggregators
            this.initializeAggregators();

            // Initialize cache
            if (this.config.cacheEnabled) {
                this.initializeCache();
            }

            // Start aggregation queue
            this.startAggregationQueue();

            this.isInitialized = true;
            console.log('✅ Federated Learning Aggregator initialized');

        } catch (error) {
            console.error('❌ Federated Learning Aggregator initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/aggregator-config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load aggregator configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize aggregators
     */
    initializeAggregators() {
        // FedAvg aggregator
        this.aggregators.set('fedavg', {
            aggregate: (models, weights) => this.fedAvgAggregate(models, weights),
            name: 'Federated Averaging',
            description: 'Standard federated averaging algorithm'
        });

        // FedProx aggregator
        this.aggregators.set('fedprox', {
            aggregate: (models, weights, mu) => this.fedProxAggregate(models, weights, mu),
            name: 'Federated Proximal',
            description: 'Proximal term for better convergence'
        });

        // FedSGD aggregator
        this.aggregators.set('fedsgd', {
            aggregate: (gradients, weights) => this.fedSGDAggregate(gradients, weights),
            name: 'Federated SGD',
            description: 'Federated stochastic gradient descent'
        });

        // SCAFFOLD aggregator
        this.aggregators.set('scaffold', {
            aggregate: (models, weights, controlVariates) => this.scaffoldAggregate(models, weights, controlVariates),
            name: 'SCAFFOLD',
            description: 'Control variates for federated learning'
        });
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
     * Start aggregation queue
     */
    startAggregationQueue() {
        setInterval(() => {
            this.processAggregationQueue();
        }, 1000);
    }

    /**
     * Aggregate models using FedAvg
     */
    async fedAvgAggregate(models, weights = null) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/aggregate/fedavg`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ models, weights })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update statistics
                this.statistics.successfulAggregations++;
                this.statistics.lastAggregation = new Date().toISOString();
                
                // Cache result
                this.cacheAggregationResult('fedavg', models, result);
                
                return result;
            } else {
                throw new Error(`FedAvg aggregation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('FedAvg aggregation error:', error);
            this.statistics.failedAggregations++;
            throw error;
        }
    }

    /**
     * Aggregate models using FedProx
     */
    async fedProxAggregate(models, weights = null, mu = 0.01) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/aggregate/fedprox`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ models, weights, mu })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update statistics
                this.statistics.successfulAggregations++;
                this.statistics.lastAggregation = new Date().toISOString();
                
                // Cache result
                this.cacheAggregationResult('fedprox', models, result);
                
                return result;
            } else {
                throw new Error(`FedProx aggregation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('FedProx aggregation error:', error);
            this.statistics.failedAggregations++;
            throw error;
        }
    }

    /**
     * Aggregate gradients using FedSGD
     */
    async fedSGDAggregate(gradients, weights = null) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/aggregate/fedsgd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ gradients, weights })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update statistics
                this.statistics.successfulAggregations++;
                this.statistics.lastAggregation = new Date().toISOString();
                
                // Cache result
                this.cacheAggregationResult('fedsgd', gradients, result);
                
                return result;
            } else {
                throw new Error(`FedSGD aggregation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('FedSGD aggregation error:', error);
            this.statistics.failedAggregations++;
            throw error;
        }
    }

    /**
     * Aggregate models using SCAFFOLD
     */
    async scaffoldAggregate(models, weights = null, controlVariates = null) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/aggregate/scaffold`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ models, weights, controlVariates })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update statistics
                this.statistics.successfulAggregations++;
                this.statistics.lastAggregation = new Date().toISOString();
                
                // Cache result
                this.cacheAggregationResult('scaffold', models, result);
                
                return result;
            } else {
                throw new Error(`SCAFFOLD aggregation failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('SCAFFOLD aggregation error:', error);
            this.statistics.failedAggregations++;
            throw error;
        }
    }

    /**
     * Aggregate models with specified algorithm
     */
    async aggregateModels(models, algorithm = 'fedavg', parameters = {}) {
        try {
            // Check cache first
            const cacheKey = this.generateCacheKey(algorithm, models);
            const cached = this.cache.get(cacheKey);
            if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
                this.statistics.cacheHits++;
                return cached.result;
            }

            this.statistics.cacheMisses++;
            this.statistics.totalAggregations++;

            // Get aggregator
            const aggregator = this.aggregators.get(algorithm);
            if (!aggregator) {
                throw new Error(`Unsupported aggregation algorithm: ${algorithm}`);
            }

            // Perform aggregation
            const result = await aggregator.aggregate(models, parameters.weights, parameters.mu, parameters.controlVariates);

            // Check convergence
            const convergenceResult = await this.checkConvergence(result, models);

            // Update convergence history
            this.convergenceHistory.push({
                round: this.convergenceHistory.length + 1,
                algorithm,
                convergence: convergenceResult.convergence,
                timestamp: new Date().toISOString()
            });

            // Dispatch event
            window.dispatchEvent(new CustomEvent('modelsAggregated', {
                detail: { algorithm, result, convergence: convergenceResult }
            }));

            return {
                aggregatedModel: result,
                convergence: convergenceResult,
                metadata: {
                    algorithm,
                    parameters,
                    timestamp: new Date().toISOString()
                }
            };

        } catch (error) {
            console.error('Model aggregation failed:', error);
            throw error;
        }
    }

    /**
     * Check model convergence
     */
    async checkConvergence(aggregatedModel, previousModels) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/convergence/check`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ aggregatedModel, previousModels })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Convergence check failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Convergence check error:', error);
            return {
                converged: false,
                convergence: 0,
                error: error.message
            };
        }
    }

    /**
     * Compress model for efficient transmission
     */
    async compressModel(model, compressionRatio = null) {
        try {
            const ratio = compressionRatio || this.config.compressionRatio;
            
            const response = await fetch(`${this.config.apiBaseUrl}/compress`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ model, compressionRatio: ratio })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Model compression failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Model compression error:', error);
            throw error;
        }
    }

    /**
     * Decompress model
     */
    async decompressModel(compressedModel) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/decompress`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ compressedModel })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Model decompression failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Model decompression error:', error);
            throw error;
        }
    }

    /**
     * Get aggregation algorithms
     */
    getAggregationAlgorithms() {
        return this.config.supportedAlgorithms;
    }

    /**
     * Get algorithm parameters
     */
    getAlgorithmParameters(algorithm) {
        const algo = this.config.supportedAlgorithms[algorithm];
        return algo ? algo.parameters : [];
    }

    /**
     * Get convergence history
     */
    getConvergenceHistory() {
        return [...this.convergenceHistory];
    }

    /**
     * Get aggregation statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Generate cache key
     */
    generateCacheKey(algorithm, models) {
        const modelHashes = models.map(model => this.hashModel(model)).join('_');
        return `${algorithm}_${modelHashes}`;
    }

    /**
     * Hash model for caching
     */
    hashModel(model) {
        // Simple hash function for model identification
        const modelStr = JSON.stringify(model);
        let hash = 0;
        for (let i = 0; i < modelStr.length; i++) {
            const char = modelStr.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return hash.toString(36);
    }

    /**
     * Cache aggregation result
     */
    cacheAggregationResult(algorithm, models, result) {
        if (this.config.cacheEnabled) {
            const cacheKey = this.generateCacheKey(algorithm, models);
            this.cache.set(cacheKey, {
                result,
                timestamp: Date.now()
            });
        }
    }

    /**
     * Process aggregation queue
     */
    async processAggregationQueue() {
        if (this.isProcessing || this.aggregationQueue.length === 0) {
            return;
        }

        this.isProcessing = true;

        try {
            const batch = this.aggregationQueue.splice(0, this.config.batchSize);
            
            for (const aggregation of batch) {
                try {
                    const result = await this.aggregateModels(
                        aggregation.models,
                        aggregation.algorithm,
                        aggregation.parameters
                    );
                    aggregation.resolve(result);
                } catch (error) {
                    aggregation.reject(error);
                }
            }
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Add aggregation to queue
     */
    addToAggregationQueue(models, algorithm = 'fedavg', parameters = {}) {
        return new Promise((resolve, reject) => {
            this.aggregationQueue.push({
                models,
                algorithm,
                parameters,
                resolve,
                reject
            });
        });
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
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('Aggregator cache cleared');
    }

    /**
     * Refresh data
     */
    async refreshData() {
        try {
            // Clear cache to force fresh aggregations
            this.clearCache();
            
            // Reset statistics
            this.statistics = {
                totalAggregations: 0,
                successfulAggregations: 0,
                failedAggregations: 0,
                averageConvergenceTime: 0,
                totalConvergenceRounds: 0,
                lastAggregation: null,
                cacheHits: 0,
                cacheMisses: 0
            };
            
            // Clear convergence history
            this.convergenceHistory = [];
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('aggregatorDataRefreshed'));
        } catch (error) {
            console.error('Aggregator data refresh failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the aggregator module
     */
    destroy() {
        this.isInitialized = false;
        
        this.aggregators.clear();
        this.models.clear();
        this.gradients.clear();
        this.weights.clear();
        this.convergenceHistory = [];
        this.aggregationQueue = [];
        this.cache.clear();
        
        console.log('🧹 Federated Learning Aggregator destroyed');
    }
} 