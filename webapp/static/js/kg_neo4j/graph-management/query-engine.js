/**
 * Knowledge Graph Neo4j Query Engine Module
 * Handles Cypher queries, query building, optimization, and result processing
 */

export default class KGQueryEngine {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/kg-neo4j',
            maxQueryLength: 10000,
            maxResults: 1000,
            timeout: 30000,
            retryAttempts: 3,
            retryDelay: 1000,
            queryCacheEnabled: true,
            queryCacheExpiry: 300000, // 5 minutes
            autoOptimize: true,
            explainQueries: false
        };

        this.queryCache = new Map();
        this.queryHistory = [];
        this.activeQueries = new Set();
        this.queryTemplates = new Map();
        this.queryOptimizer = null;
        this.queryBuilder = null;
        this.resultProcessor = null;
    }

    /**
     * Initialize the Query Engine
     */
    async init() {
        console.log('🔧 Initializing Knowledge Graph Query Engine...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize query templates
            this.initializeQueryTemplates();

            // Initialize query optimizer
            this.initializeQueryOptimizer();

            // Initialize query builder
            this.initializeQueryBuilder();

            // Initialize result processor
            this.initializeResultProcessor();

            // Load query history
            this.loadQueryHistory();

            this.isInitialized = true;
            console.log('✅ Knowledge Graph Query Engine initialized');

        } catch (error) {
            console.error('❌ Knowledge Graph Query Engine initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/query-config`);
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
            }
        } catch (error) {
            console.warn('Could not load query configuration from server, using defaults:', error);
        }
    }

    /**
     * Initialize query templates
     */
    initializeQueryTemplates() {
        // Basic node queries
        this.queryTemplates.set('getAllNodes', {
            cypher: 'MATCH (n) RETURN n LIMIT {limit}',
            parameters: { limit: 100 },
            description: 'Get all nodes in the graph'
        });

        this.queryTemplates.set('getNodesByLabel', {
            cypher: 'MATCH (n:{label}) RETURN n LIMIT {limit}',
            parameters: { label: '', limit: 100 },
            description: 'Get nodes by label'
        });

        this.queryTemplates.set('getNodeById', {
            cypher: 'MATCH (n) WHERE id(n) = {nodeId} RETURN n',
            parameters: { nodeId: null },
            description: 'Get node by ID'
        });

        // Relationship queries
        this.queryTemplates.set('getAllRelationships', {
            cypher: 'MATCH ()-[r]->() RETURN r LIMIT {limit}',
            parameters: { limit: 100 },
            description: 'Get all relationships in the graph'
        });

        this.queryTemplates.set('getRelationshipsByType', {
            cypher: 'MATCH ()-[r:{type}]->() RETURN r LIMIT {limit}',
            parameters: { type: '', limit: 100 },
            description: 'Get relationships by type'
        });

        // Path queries
        this.queryTemplates.set('shortestPath', {
            cypher: 'MATCH path = shortestPath((start)-[*]-(end)) WHERE id(start) = {startId} AND id(end) = {endId}) RETURN path',
            parameters: { startId: null, endId: null },
            description: 'Find shortest path between two nodes'
        });

        this.queryTemplates.set('allPaths', {
            cypher: 'MATCH path = (start)-[*1..5]-(end) WHERE id(start) = {startId} AND id(end) = {endId}) RETURN path LIMIT {limit}',
            parameters: { startId: null, endId: null, limit: 10 },
            description: 'Find all paths between two nodes'
        });

        // Pattern matching
        this.queryTemplates.set('patternMatch', {
            cypher: 'MATCH (n1:{label1})-[r:{type}]->(n2:{label2}) RETURN n1, r, n2 LIMIT {limit}',
            parameters: { label1: '', type: '', label2: '', limit: 100 },
            description: 'Match specific pattern in graph'
        });

        // Aggregation queries
        this.queryTemplates.set('nodeCount', {
            cypher: 'MATCH (n) RETURN count(n) as count',
            parameters: {},
            description: 'Count total nodes'
        });

        this.queryTemplates.set('relationshipCount', {
            cypher: 'MATCH ()-[r]->() RETURN count(r) as count',
            parameters: {},
            description: 'Count total relationships'
        });

        // Property queries
        this.queryTemplates.set('nodesByProperty', {
            cypher: 'MATCH (n) WHERE n.{property} = {value} RETURN n LIMIT {limit}',
            parameters: { property: '', value: '', limit: 100 },
            description: 'Find nodes by property value'
        });

        this.queryTemplates.set('nodesByPropertyRange', {
            cypher: 'MATCH (n) WHERE n.{property} >= {min} AND n.{property} <= {max} RETURN n LIMIT {limit}',
            parameters: { property: '', min: 0, max: 100, limit: 100 },
            description: 'Find nodes by property range'
        });
    }

    /**
     * Initialize query optimizer
     */
    initializeQueryOptimizer() {
        this.queryOptimizer = {
            // Query optimization rules
            rules: [
                {
                    name: 'limit_optimization',
                    apply: (query) => {
                        if (!query.includes('LIMIT') && !query.includes('limit')) {
                            return query + ' LIMIT ' + this.config.maxResults;
                        }
                        return query;
                    }
                },
                {
                    name: 'index_hint',
                    apply: (query) => {
                        // Add index hints for common patterns
                        if (query.includes('MATCH (n:Person)') && !query.includes('USING INDEX')) {
                            return query.replace('MATCH (n:Person)', 'MATCH (n:Person) USING INDEX n:Person(id)');
                        }
                        return query;
                    }
                },
                {
                    name: 'parameter_validation',
                    apply: (query, params) => {
                        // Validate and sanitize parameters
                        const sanitizedParams = {};
                        for (const [key, value] of Object.entries(params)) {
                            if (typeof value === 'string' && value.length > 1000) {
                                throw new Error(`Parameter ${key} is too long`);
                            }
                            sanitizedParams[key] = value;
                        }
                        return { query, params: sanitizedParams };
                    }
                }
            ],

            // Optimize a query
            optimize: (query, parameters = {}) => {
                let optimizedQuery = query;
                let optimizedParams = { ...parameters };

                for (const rule of this.queryOptimizer.rules) {
                    try {
                        const result = rule.apply(optimizedQuery, optimizedParams);
                        if (typeof result === 'object' && result.query) {
                            optimizedQuery = result.query;
                            optimizedParams = result.params;
                        } else {
                            optimizedQuery = result;
                        }
                    } catch (error) {
                        console.warn(`Query optimization rule ${rule.name} failed:`, error);
                    }
                }

                return { query: optimizedQuery, parameters: optimizedParams };
            }
        };
    }

    /**
     * Initialize query builder
     */
    initializeQueryBuilder() {
        this.queryBuilder = {
            // Build a query from template
            buildFromTemplate: (templateName, parameters = {}) => {
                const template = this.queryTemplates.get(templateName);
                if (!template) {
                    throw new Error(`Query template '${templateName}' not found`);
                }

                let query = template.cypher;
                const mergedParams = { ...template.parameters, ...parameters };

                // Replace parameters in query
                for (const [key, value] of Object.entries(mergedParams)) {
                    const placeholder = `{${key}}`;
                    if (query.includes(placeholder)) {
                        if (typeof value === 'string') {
                            query = query.replace(placeholder, `'${value}'`);
                        } else {
                            query = query.replace(placeholder, value);
                        }
                    }
                }

                return { query, parameters: mergedParams };
            },

            // Build custom query
            buildCustom: (pattern, returnClause, whereClause = '', orderClause = '', limit = null) => {
                let query = `MATCH ${pattern}`;
                
                if (whereClause) {
                    query += ` WHERE ${whereClause}`;
                }
                
                query += ` RETURN ${returnClause}`;
                
                if (orderClause) {
                    query += ` ORDER BY ${orderClause}`;
                }
                
                if (limit) {
                    query += ` LIMIT ${limit}`;
                }

                return query;
            },

            // Build aggregation query
            buildAggregation: (pattern, aggregation, whereClause = '') => {
                let query = `MATCH ${pattern}`;
                
                if (whereClause) {
                    query += ` WHERE ${whereClause}`;
                }
                
                query += ` RETURN ${aggregation}`;

                return query;
            }
        };
    }

    /**
     * Initialize result processor
     */
    initializeResultProcessor() {
        this.resultProcessor = {
            // Process query results
            process: (results, options = {}) => {
                const processed = {
                    data: results,
                    count: results.length,
                    metadata: {
                        processingTime: options.processingTime || 0,
                        queryTime: options.queryTime || 0,
                        totalTime: options.totalTime || 0
                    }
                };

                // Apply transformations
                if (options.transform) {
                    processed.data = this.resultProcessor.transform(processed.data, options.transform);
                }

                // Apply filtering
                if (options.filter) {
                    processed.data = this.resultProcessor.filter(processed.data, options.filter);
                }

                // Apply sorting
                if (options.sort) {
                    processed.data = this.resultProcessor.sort(processed.data, options.sort);
                }

                return processed;
            },

            // Transform results
            transform: (data, transformType) => {
                switch (transformType) {
                    case 'flatten':
                        return data.flat();
                    case 'unique':
                        return [...new Set(data)];
                    case 'group':
                        return this.resultProcessor.groupBy(data);
                    default:
                        return data;
                }
            },

            // Filter results
            filter: (data, filterFn) => {
                return data.filter(filterFn);
            },

            // Sort results
            sort: (data, sortConfig) => {
                return data.sort((a, b) => {
                    for (const [key, direction] of Object.entries(sortConfig)) {
                        const aVal = a[key];
                        const bVal = b[key];
                        
                        if (aVal < bVal) return direction === 'asc' ? -1 : 1;
                        if (aVal > bVal) return direction === 'asc' ? 1 : -1;
                    }
                    return 0;
                });
            },

            // Group results
            groupBy: (data, key = 'type') => {
                const groups = {};
                data.forEach(item => {
                    const groupKey = item[key] || 'unknown';
                    if (!groups[groupKey]) {
                        groups[groupKey] = [];
                    }
                    groups[groupKey].push(item);
                });
                return groups;
            }
        };
    }

    /**
     * Load query history
     */
    loadQueryHistory() {
        try {
            const history = localStorage.getItem('kg_query_history');
            if (history) {
                this.queryHistory = JSON.parse(history);
            }
        } catch (error) {
            console.warn('Could not load query history:', error);
            this.queryHistory = [];
        }
    }

    /**
     * Save query to history
     */
    saveQueryToHistory(query, parameters = {}, resultCount = 0) {
        const historyEntry = {
            query,
            parameters,
            resultCount,
            timestamp: new Date().toISOString(),
            executionTime: Date.now()
        };

        this.queryHistory.unshift(historyEntry);
        
        // Keep only last 100 queries
        if (this.queryHistory.length > 100) {
            this.queryHistory = this.queryHistory.slice(0, 100);
        }

        try {
            localStorage.setItem('kg_query_history', JSON.stringify(this.queryHistory));
        } catch (error) {
            console.warn('Could not save query history:', error);
        }
    }

    /**
     * Execute a Cypher query
     */
    async executeQuery(query, parameters = {}, options = {}) {
        const queryId = this.generateQueryId();
        this.activeQueries.add(queryId);

        try {
            // Check cache first
            if (this.config.queryCacheEnabled) {
                const cacheKey = this.generateCacheKey(query, parameters);
                const cached = this.queryCache.get(cacheKey);
                if (cached && Date.now() - cached.timestamp < this.config.queryCacheExpiry) {
                    return cached.data;
                }
            }

            // Validate query
            this.validateQuery(query);

            // Optimize query if enabled
            let optimizedQuery = query;
            let optimizedParams = parameters;
            
            if (this.config.autoOptimize) {
                const optimization = this.queryOptimizer.optimize(query, parameters);
                optimizedQuery = optimization.query;
                optimizedParams = optimization.parameters;
            }

            const startTime = Date.now();

            // Execute query
            const response = await fetch(`${this.config.apiBaseUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: optimizedQuery,
                    parameters: optimizedParams,
                    explain: this.config.explainQueries,
                    timeout: options.timeout || this.config.timeout
                })
            });

            const queryTime = Date.now() - startTime;

            if (!response.ok) {
                throw new Error(`Query execution failed: ${response.statusText}`);
            }

            const result = await response.json();
            const totalTime = Date.now() - startTime;

            // Process results
            const processedResult = this.resultProcessor.process(result.data || result, {
                processingTime: totalTime - queryTime,
                queryTime,
                totalTime,
                transform: options.transform,
                filter: options.filter,
                sort: options.sort
            });

            // Cache result
            if (this.config.queryCacheEnabled) {
                const cacheKey = this.generateCacheKey(query, parameters);
                this.queryCache.set(cacheKey, {
                    data: processedResult,
                    timestamp: Date.now()
                });
            }

            // Save to history
            this.saveQueryToHistory(query, parameters, processedResult.count);

            // Dispatch event
            window.dispatchEvent(new CustomEvent('kgQueryExecuted', {
                detail: {
                    queryId,
                    query: optimizedQuery,
                    parameters: optimizedParams,
                    result: processedResult,
                    executionTime: totalTime
                }
            }));

            return processedResult;

        } catch (error) {
            console.error('Query execution failed:', error);
            
            // Dispatch error event
            window.dispatchEvent(new CustomEvent('kgQueryError', {
                detail: {
                    queryId,
                    query,
                    parameters,
                    error: error.message
                }
            }));

            throw error;
        } finally {
            this.activeQueries.delete(queryId);
        }
    }

    /**
     * Execute query from template
     */
    async executeTemplate(templateName, parameters = {}, options = {}) {
        const { query, parameters: templateParams } = this.queryBuilder.buildFromTemplate(templateName, parameters);
        return await this.executeQuery(query, templateParams, options);
    }

    /**
     * Execute custom query
     */
    async executeCustom(pattern, returnClause, whereClause = '', orderClause = '', limit = null, options = {}) {
        const query = this.queryBuilder.buildCustom(pattern, returnClause, whereClause, orderClause, limit);
        return await this.executeQuery(query, {}, options);
    }

    /**
     * Execute aggregation query
     */
    async executeAggregation(pattern, aggregation, whereClause = '', options = {}) {
        const query = this.queryBuilder.buildAggregation(pattern, aggregation, whereClause);
        return await this.executeQuery(query, {}, options);
    }

    /**
     * Explain a query
     */
    async explainQuery(query, parameters = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/explain`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    parameters
                })
            });

            if (!response.ok) {
                throw new Error(`Query explanation failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Query explanation failed:', error);
            throw error;
        }
    }

    /**
     * Profile a query
     */
    async profileQuery(query, parameters = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/profile`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    parameters
                })
            });

            if (!response.ok) {
                throw new Error(`Query profiling failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Query profiling failed:', error);
            throw error;
        }
    }

    /**
     * Get query statistics
     */
    async getQueryStatistics() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/query-stats`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to get query statistics: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get query statistics failed:', error);
            throw error;
        }
    }

    /**
     * Clear query cache
     */
    clearQueryCache() {
        this.queryCache.clear();
        console.log('Query cache cleared');
    }

    /**
     * Get query history
     */
    getQueryHistory(limit = 50) {
        return this.queryHistory.slice(0, limit);
    }

    /**
     * Clear query history
     */
    clearQueryHistory() {
        this.queryHistory = [];
        try {
            localStorage.removeItem('kg_query_history');
        } catch (error) {
            console.warn('Could not clear query history:', error);
        }
    }

    /**
     * Get active queries
     */
    getActiveQueries() {
        return Array.from(this.activeQueries);
    }

    /**
     * Cancel active query
     */
    async cancelQuery(queryId) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/cancel-query/${queryId}`, {
                method: 'POST'
            });

            if (response.ok) {
                this.activeQueries.delete(queryId);
                return true;
            } else {
                throw new Error(`Failed to cancel query: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Cancel query failed:', error);
            throw error;
        }
    }

    /**
     * Validate query
     */
    validateQuery(query) {
        if (!query || typeof query !== 'string') {
            throw new Error('Query must be a non-empty string');
        }

        if (query.length > this.config.maxQueryLength) {
            throw new Error(`Query is too long (max ${this.config.maxQueryLength} characters)`);
        }

        // Basic Cypher validation
        if (!query.trim().toUpperCase().startsWith('MATCH') && 
            !query.trim().toUpperCase().startsWith('CREATE') &&
            !query.trim().toUpperCase().startsWith('MERGE') &&
            !query.trim().toUpperCase().startsWith('DELETE') &&
            !query.trim().toUpperCase().startsWith('SET') &&
            !query.trim().toUpperCase().startsWith('REMOVE')) {
            throw new Error('Query must start with a valid Cypher clause');
        }
    }

    /**
     * Generate query ID
     */
    generateQueryId() {
        return 'query_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Generate cache key
     */
    generateCacheKey(query, parameters) {
        return btoa(query + JSON.stringify(parameters));
    }

    /**
     * Refresh queries
     */
    async refreshQueries() {
        try {
            // Clear cache
            this.clearQueryCache();
            
            // Reload configuration
            await this.loadConfiguration();
            
            // Reload query templates
            this.initializeQueryTemplates();
            
            console.log('Query engine refreshed');
        } catch (error) {
            console.error('Query engine refresh failed:', error);
            throw error;
        }
    }

    /**
     * Destroy the query engine
     */
    destroy() {
        this.isInitialized = false;
        this.queryCache.clear();
        this.queryHistory = [];
        this.activeQueries.clear();
        this.queryTemplates.clear();
        this.queryOptimizer = null;
        this.queryBuilder = null;
        this.resultProcessor = null;
        console.log('🧹 Knowledge Graph Query Engine destroyed');
    }
} 