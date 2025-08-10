/**
 * AI RAG Query Processor Module
 * Handles query parsing, semantic search, and document retrieval
 */

export default class AIRAGQueryProcessor {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/ai-rag',
            maxResults: 10,
            similarityThreshold: 0.7,
            maxQueryLength: 1000,
            searchStrategies: ['semantic', 'keyword', 'hybrid'],
            defaultStrategy: 'hybrid'
        };
        
        this.queryHistory = [];
        this.searchCache = new Map();
        this.activeQueries = new Set();
        this.queryTemplates = new Map();
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        // Initialize authentication
        this.initAuthentication();
    }

    /**
     * Initialize authentication
     */
    initAuthentication() {
        try {
            // Check if user is authenticated
            if (typeof getCurrentUser === 'function') {
                this.currentUser = getCurrentUser();
                if (this.currentUser) {
                    this.isAuthenticated = true;
                    this.authToken = this.getAuthToken();
                    console.log('🔐 AI RAG Query Processor: User authenticated:', this.currentUser.username);
                } else {
                    console.log('🔐 AI RAG Query Processor: User not authenticated');
                    this.isAuthenticated = false;
                }
            } else {
                console.warn('⚠️ AI RAG Query Processor: getCurrentUser function not available');
                this.isAuthenticated = false;
            }
        } catch (error) {
            console.error('❌ AI RAG Query Processor: Authentication initialization error:', error);
            this.isAuthenticated = false;
        }
    }

    /**
     * Get authentication token
     */
    getAuthToken() {
        try {
            // Try to get token from localStorage/sessionStorage
            return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
        } catch (error) {
            console.warn('⚠️ AI RAG Query Processor: Could not get auth token:', error);
            return null;
        }
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
     * Initialize the Query Processor
     */
    async init() {
        console.log('🔧 Initializing AI RAG Query Processor...');
        
        try {
            // Load configuration
            await this.loadConfiguration();
            
            // Initialize query templates
            this.initializeQueryTemplates();
            
            // Load query history
            this.loadQueryHistory();
            
            this.isInitialized = true;
            console.log('✅ AI RAG Query Processor initialized');
            
        } catch (error) {
            console.error('❌ AI RAG Query Processor initialization failed:', error);
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
                const serverConfig = await response.json();
                this.config = { ...this.config, ...serverConfig };
            }
        } catch (error) {
            console.warn('Could not load query configuration, using defaults:', error);
        }
    }

    /**
     * Initialize query templates
     */
    initializeQueryTemplates() {
        this.queryTemplates.set('general', {
            name: 'General Search',
            description: 'Search across all documents',
            template: 'Find information about {query}',
            filters: {}
        });
        
        this.queryTemplates.set('technical', {
            name: 'Technical Documentation',
            description: 'Search technical specifications and documentation',
            template: 'Find technical details about {query}',
            filters: { category: 'technical' }
        });
        
        this.queryTemplates.set('procedure', {
            name: 'Procedures and Processes',
            description: 'Search for procedures and step-by-step processes',
            template: 'Find procedures related to {query}',
            filters: { category: 'procedure' }
        });
        
        this.queryTemplates.set('troubleshooting', {
            name: 'Troubleshooting',
            description: 'Search for troubleshooting and problem-solving information',
            template: 'Find troubleshooting information for {query}',
            filters: { category: 'troubleshooting' }
        });
        
        // AASX-specific query templates
        this.queryTemplates.set('aasx_structure', {
            name: 'AASX Structure Analysis',
            description: 'Analyze asset structure in digital twins',
            template: 'Analyze the asset structure in our digital twin for {query}',
            filters: { type: 'digital_twin' }
        });
        
        this.queryTemplates.set('aasx_submodels', {
            name: 'Submodel Analysis',
            description: 'Find submodels in AASX files',
            template: 'What are the submodels in our AASX file for {query}',
            filters: { type: 'digital_twin' }
        });
        
        this.queryTemplates.set('aasx_properties', {
            name: 'Asset Properties',
            description: 'Show properties of manufacturing assets',
            template: 'Show me the properties of our manufacturing assets for {query}',
            filters: { type: 'digital_twin' }
        });
        
        this.queryTemplates.set('aasx_quality', {
            name: 'Data Quality Check',
            description: 'Identify quality issues in asset data',
            template: 'Identify quality issues in our asset data for {query}',
            filters: { type: 'digital_twin' }
        });
    }

    /**
     * Load query history from local storage
     */
    loadQueryHistory() {
        const stored = localStorage.getItem('ai_rag_query_history');
        if (stored) {
            try {
                this.queryHistory = JSON.parse(stored);
            } catch (error) {
                console.warn('Failed to load query history:', error);
                this.queryHistory = [];
            }
        }
    }

    /**
     * Save query history to local storage
     */
    saveQueryHistory() {
        localStorage.setItem('ai_rag_query_history', JSON.stringify(this.queryHistory));
    }

    /**
     * Process a query
     */
    async processQuery(query, options = {}) {
        const queryId = this.generateQueryId();
        
        try {
            this.activeQueries.add(queryId);
            
            // Validate query
            this.validateQuery(query);
            
            // Parse query
            const parsedQuery = this.parseQuery(query);
            
            // Check cache first
            const cacheKey = this.generateCacheKey(parsedQuery, options);
            if (this.searchCache.has(cacheKey)) {
                const cachedResult = this.searchCache.get(cacheKey);
                this.addToQueryHistory(query, 'cached', cachedResult);
                return cachedResult;
            }
            
            // Perform search
            const searchStrategy = options.strategy || this.config.defaultStrategy;
            const results = await this.performSearch(parsedQuery, searchStrategy, options);
            
            // Cache results
            this.searchCache.set(cacheKey, results);
            
            // Add to history
            this.addToQueryHistory(query, 'success', results);
            
            return results;
            
        } catch (error) {
            console.error('Query processing failed:', error);
            this.addToQueryHistory(query, 'error', { error: error.message });
            throw error;
        } finally {
            this.activeQueries.delete(queryId);
        }
    }

    /**
     * Generate query ID
     */
    generateQueryId() {
        return `query_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Generate cache key
     */
    generateCacheKey(parsedQuery, options) {
        const key = JSON.stringify({
            query: parsedQuery,
            strategy: options.strategy || this.config.defaultStrategy,
            filters: options.filters || {},
            maxResults: options.maxResults || this.config.maxResults
        });
        return btoa(key).substring(0, 32);
    }

    /**
     * Validate query
     */
    validateQuery(query) {
        if (!query || typeof query !== 'string') {
            throw new Error('Query must be a non-empty string');
        }
        
        if (query.trim().length === 0) {
            throw new Error('Query cannot be empty');
        }
        
        if (query.length > this.config.maxQueryLength) {
            throw new Error(`Query too long. Maximum length is ${this.config.maxQueryLength} characters`);
        }
    }

    /**
     * Parse query
     */
    parseQuery(query) {
        const parsed = {
            original: query,
            normalized: query.toLowerCase().trim(),
            keywords: this.extractKeywords(query),
            entities: this.extractEntities(query),
            intent: this.detectIntent(query),
            filters: this.extractFilters(query)
        };
        
        return parsed;
    }

    /**
     * Extract keywords from query
     */
    extractKeywords(query) {
        // Remove common stop words and extract meaningful keywords
        const stopWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'];
        const words = query.toLowerCase().split(/\s+/);
        return words.filter(word => 
            word.length > 2 && 
            !stopWords.includes(word) && 
            !/^[0-9]+$/.test(word)
        );
    }

    /**
     * Extract entities from query
     */
    extractEntities(query) {
        // Simple entity extraction - can be enhanced with NLP libraries
        const entities = [];
        
        // Extract technical terms (words with numbers or special characters)
        const technicalTerms = query.match(/\b[A-Za-z0-9_-]+\b/g) || [];
        entities.push(...technicalTerms);
        
        // Extract potential product names (capitalized words)
        const productNames = query.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g) || [];
        entities.push(...productNames);
        
        return [...new Set(entities)];
    }

    /**
     * Detect query intent
     */
    detectIntent(query) {
        const lowerQuery = query.toLowerCase();
        
        if (lowerQuery.includes('how to') || lowerQuery.includes('procedure') || lowerQuery.includes('steps')) {
            return 'procedure';
        } else if (lowerQuery.includes('error') || lowerQuery.includes('problem') || lowerQuery.includes('fix')) {
            return 'troubleshooting';
        } else if (lowerQuery.includes('specification') || lowerQuery.includes('technical') || lowerQuery.includes('details')) {
            return 'technical';
        } else {
            return 'general';
        }
    }

    /**
     * Extract filters from query
     */
    extractFilters(query) {
        const filters = {};
        const lowerQuery = query.toLowerCase();
        
        // Extract date filters
        const dateMatch = lowerQuery.match(/(\d{4})-(\d{2})-(\d{2})/);
        if (dateMatch) {
            filters.date = dateMatch[0];
        }
        
        // Extract category filters
        if (lowerQuery.includes('technical')) {
            filters.category = 'technical';
        } else if (lowerQuery.includes('procedure')) {
            filters.category = 'procedure';
        } else if (lowerQuery.includes('troubleshooting')) {
            filters.category = 'troubleshooting';
        }
        
        return filters;
    }

    /**
     * Perform search
     */
    async performSearch(parsedQuery, strategy, options) {
        const searchParams = {
            query: parsedQuery.original,
            strategy: strategy,
            maxResults: options.maxResults || this.config.maxResults,
            filters: { ...parsedQuery.filters, ...options.filters },
            similarityThreshold: options.similarityThreshold || this.config.similarityThreshold
        };
        
        const response = await fetch(`${this.config.apiBaseUrl}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchParams)
        });
        
        if (!response.ok) {
            throw new Error('Search request failed');
        }
        
        const results = await response.json();
        
        // Process and rank results
        return this.processSearchResults(results, parsedQuery);
    }

    /**
     * Process and rank search results
     */
    processSearchResults(results, parsedQuery) {
        const processed = {
            query: parsedQuery.original,
            totalResults: results.total || 0,
            results: [],
            metadata: {
                searchTime: results.searchTime || 0,
                strategy: results.strategy || 'unknown',
                filters: results.filters || {}
            }
        };
        
        if (results.results) {
            processed.results = results.results.map(result => ({
                ...result,
                relevance: this.calculateRelevance(result, parsedQuery),
                snippet: this.generateSnippet(result, parsedQuery)
            }));
            
            // Sort by relevance
            processed.results.sort((a, b) => b.relevance - a.relevance);
        }
        
        return processed;
    }

    /**
     * Calculate relevance score for a result
     */
    calculateRelevance(result, parsedQuery) {
        let score = 0;
        
        // Base similarity score
        if (result.similarity) {
            score += result.similarity * 0.6;
        }
        
        // Keyword matching
        const resultText = (result.content || result.text || '').toLowerCase();
        const keywordMatches = parsedQuery.keywords.filter(keyword => 
            resultText.includes(keyword)
        ).length;
        score += (keywordMatches / parsedQuery.keywords.length) * 0.3;
        
        // Entity matching
        const entityMatches = parsedQuery.entities.filter(entity => 
            resultText.includes(entity.toLowerCase())
        ).length;
        score += (entityMatches / Math.max(parsedQuery.entities.length, 1)) * 0.1;
        
        return Math.min(score, 1.0);
    }

    /**
     * Generate snippet for result
     */
    generateSnippet(result, parsedQuery) {
        const content = result.content || result.text || '';
        const query = parsedQuery.original.toLowerCase();
        
        // Find the best position to start the snippet
        const queryWords = query.split(/\s+/);
        let bestPosition = 0;
        let maxMatches = 0;
        
        for (let i = 0; i <= content.length - 100; i += 50) {
            const snippet = content.substring(i, i + 200).toLowerCase();
            const matches = queryWords.filter(word => snippet.includes(word)).length;
            
            if (matches > maxMatches) {
                maxMatches = matches;
                bestPosition = i;
            }
        }
        
        // Generate snippet
        let snippet = content.substring(bestPosition, bestPosition + 200);
        
        // Add ellipsis if needed
        if (bestPosition > 0) {
            snippet = '...' + snippet;
        }
        if (bestPosition + 200 < content.length) {
            snippet = snippet + '...';
        }
        
        return snippet;
    }

    /**
     * Add query to history
     */
    addToQueryHistory(query, status, results) {
        const historyEntry = {
            id: this.generateQueryId(),
            query: query,
            status: status,
            timestamp: new Date().toISOString(),
            resultCount: results?.results?.length || 0,
            searchTime: results?.metadata?.searchTime || 0
        };
        
        this.queryHistory.unshift(historyEntry);
        
        // Keep only last 100 queries
        if (this.queryHistory.length > 100) {
            this.queryHistory = this.queryHistory.slice(0, 100);
        }
        
        this.saveQueryHistory();
    }

    /**
     * Get query history
     */
    getQueryHistory(limit = 20) {
        return this.queryHistory.slice(0, limit);
    }

    /**
     * Clear query history
     */
    clearQueryHistory() {
        this.queryHistory = [];
        this.saveQueryHistory();
    }

    /**
     * Get query templates
     */
    getQueryTemplates() {
        return Array.from(this.queryTemplates.values());
    }

    /**
     * Apply query template
     */
    applyQueryTemplate(templateId, query) {
        const template = this.queryTemplates.get(templateId);
        if (template) {
            return template.template.replace('{query}', query);
        }
        return query;
    }

    /**
     * Get search suggestions
     */
    async getSearchSuggestions(partialQuery) {
        if (!partialQuery || partialQuery.length < 2) {
            return [];
        }
        
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/suggestions?q=${encodeURIComponent(partialQuery)}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Failed to get search suggestions:', error);
        }
        
        // Fallback: generate suggestions from history
        return this.generateSuggestionsFromHistory(partialQuery);
    }

    /**
     * Generate suggestions from query history
     */
    generateSuggestionsFromHistory(partialQuery) {
        const suggestions = [];
        const lowerPartial = partialQuery.toLowerCase();
        
        // Find matching queries from history
        this.queryHistory.forEach(entry => {
            if (entry.query.toLowerCase().includes(lowerPartial)) {
                suggestions.push(entry.query);
            }
        });
        
        // Remove duplicates and limit results
        return [...new Set(suggestions)].slice(0, 5);
    }

    /**
     * Clear search cache
     */
    clearSearchCache() {
        this.searchCache.clear();
    }

    /**
     * Get cache statistics
     */
    getCacheStatistics() {
        return {
            size: this.searchCache.size,
            entries: Array.from(this.searchCache.keys())
        };
    }

    /**
     * Refresh queries
     */
    async refreshQueries() {
        this.clearSearchCache();
        await this.loadConfiguration();
        console.log('🔄 AI RAG Query Processor refreshed');
    }

    /**
     * Get active queries
     */
    getActiveQueries() {
        return Array.from(this.activeQueries);
    }

    /**
     * Destroy the query processor
     */
    destroy() {
        this.activeQueries.clear();
        this.searchCache.clear();
        this.queryHistory = [];
        this.queryTemplates.clear();
        this.isInitialized = false;
        
        console.log('🧹 AI RAG Query Processor destroyed');
    }
} 