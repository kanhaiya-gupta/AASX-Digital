/**
 * AI RAG Vector Store Module
 * Handles vector querying and similarity search for processed data
 * Query-only interface for Qdrant vector database
 */

export default class AIRAGVectorStore {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/ai-rag',
            vectorDimension: 1536, // OpenAI ada-002 dimension
            similarityThreshold: 0.7,
            maxResults: 100
        };
        
        this.statistics = {
            totalVectors: 0,
            lastQuery: null,
            queryCount: 0
        };
    }

    /**
     * Initialize the Vector Store
     */
    async init() {
        console.log('🔧 Initializing AI RAG Vector Store...');
        
        try {
            // Load configuration
            await this.loadConfiguration();
            
            // Load vector database info
            await this.loadVectorDbInfo();
            
            this.isInitialized = true;
            console.log('✅ AI RAG Vector Store initialized');
            
        } catch (error) {
            console.error('❌ AI RAG Vector Store initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vector-config`);
            if (response.ok) {
                const serverConfig = await response.json();
                this.config = { ...this.config, ...serverConfig.config };
            }
        } catch (error) {
            console.warn('Could not load vector configuration, using defaults:', error);
        }
    }

    /**
     * Load vector database information
     */
    async loadVectorDbInfo() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vector-db-info`);
            if (response.ok) {
                const dbInfo = await response.json();
                this.statistics.totalVectors = dbInfo.total_vectors || 0;
                console.log('Vector DB info loaded:', dbInfo);
            }
        } catch (error) {
            console.warn('Could not load vector DB info:', error);
        }
    }

    /**
     * Query vectors from vector database
     */
    async queryVectors(collection_name = null, limit = 100) {
        try {
            const params = new URLSearchParams();
            if (collection_name) params.append('collection_name', collection_name);
            params.append('limit', limit.toString());

            const response = await fetch(`${this.config.apiBaseUrl}/vectors?${params}`);
            
            if (!response.ok) {
                throw new Error(`Failed to query vectors: ${response.statusText}`);
            }

            const result = await response.json();
            
            // Update statistics
            this.statistics.lastQuery = new Date().toISOString();
            this.statistics.queryCount++;
            
            return result;

        } catch (error) {
            console.error('Error querying vectors:', error);
            throw error;
        }
    }

    /**
     * Search for similar vectors (query only)
     */
    async searchSimilar(queryEmbedding, options = {}) {
        try {
            const searchParams = {
                query_embedding: queryEmbedding,
                limit: options.limit || 10,
                threshold: options.threshold || this.config.similarityThreshold,
                collection_name: options.collection_name || null
            };

            // Use the query endpoint with vector search
            const response = await fetch(`${this.config.apiBaseUrl}/search`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Search failed: ${response.statusText}`);
            }

            const results = await response.json();
            
            // Update statistics
            this.statistics.lastQuery = new Date().toISOString();
            this.statistics.queryCount++;
            
            return this.enhanceSearchResults(results);

        } catch (error) {
            console.error('Error searching similar vectors:', error);
            throw error;
        }
    }

    /**
     * Enhance search results with metadata
     */
    enhanceSearchResults(results) {
        if (!results || !Array.isArray(results)) {
            return [];
        }

        return results.map(result => ({
            ...result,
            similarity_score: result.score || result.similarity || 0,
            enhanced: true,
            timestamp: new Date().toISOString()
        }));
    }

    /**
     * Get vector database health status
     */
    async getHealth() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vector-db-info`);
            if (response.ok) {
                const health = await response.json();
                return {
                    status: health.status || 'unknown',
                    total_vectors: health.total_vectors || 0,
                    collections: health.collections || [],
                    last_check: new Date().toISOString()
                };
            }
        } catch (error) {
            console.warn('Could not get vector DB health:', error);
        }
        
        return {
            status: 'error',
            total_vectors: 0,
            collections: [],
            last_check: new Date().toISOString()
        };
    }

    /**
     * Refresh vectors from server
     */
    async refreshVectors() {
        try {
            await this.loadVectorDbInfo();
            console.log('✅ Vectors refreshed successfully');
        } catch (error) {
            console.error('❌ Failed to refresh vectors:', error);
        }
    }

    /**
     * Get vector store statistics
     */
    getStatistics() {
        return {
            ...this.statistics,
            isInitialized: this.isInitialized,
            config: this.config
        };
    }

    /**
     * Clean up resources
     */
    destroy() {
        this.isInitialized = false;
        console.log('🧹 AI RAG Vector Store destroyed');
    }
}