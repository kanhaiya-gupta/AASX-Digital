/**
 * AI RAG Vector Store Module
 * Handles vector storage, similarity search, and vector operations
 */

export default class AIRAGVectorStore {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/ai-rag',
            vectorDimension: 1536, // OpenAI ada-002 dimension
            maxVectors: 100000,
            similarityThreshold: 0.7,
            batchSize: 100,
            indexType: 'faiss', // or 'pinecone', 'weaviate', etc.
            updateInterval: 5000 // 5 seconds
        };
        
        this.vectors = new Map();
        this.metadata = new Map();
        this.index = null;
        this.updateQueue = [];
        this.isUpdating = false;
        this.statistics = {
            totalVectors: 0,
            totalDocuments: 0,
            lastUpdate: null,
            indexSize: 0
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
            
            // Initialize vector storage
            await this.initializeVectorStorage();
            
            // Load existing vectors
            await this.loadExistingVectors();
            
            // Initialize index
            await this.initializeIndex();
            
            // Start update queue
            this.startUpdateQueue();
            
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
                this.config = { ...this.config, ...serverConfig };
            }
        } catch (error) {
            console.warn('Could not load vector configuration, using defaults:', error);
        }
    }

    /**
     * Initialize vector storage
     */
    async initializeVectorStorage() {
        // Initialize local storage for vectors metadata
        const storedVectors = localStorage.getItem('ai_rag_vectors_metadata');
        if (storedVectors) {
            try {
                const vectors = JSON.parse(storedVectors);
                vectors.forEach(vector => {
                    this.metadata.set(vector.id, vector);
                });
            } catch (error) {
                console.warn('Failed to load stored vectors metadata:', error);
            }
        }
    }

    /**
     * Load existing vectors from server
     */
    async loadExistingVectors() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vectors`);
            if (response.ok) {
                const vectors = await response.json();
                vectors.forEach(vector => {
                    this.vectors.set(vector.id, vector.embedding);
                    this.metadata.set(vector.id, {
                        id: vector.id,
                        documentId: vector.documentId,
                        chunkId: vector.chunkId,
                        text: vector.text,
                        createdAt: vector.createdAt,
                        metadata: vector.metadata || {}
                    });
                });
                
                this.updateStatistics();
            }
        } catch (error) {
            console.warn('Could not load existing vectors:', error);
        }
    }

    /**
     * Initialize vector index
     */
    async initializeIndex() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vector-index/init`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dimension: this.config.vectorDimension,
                    indexType: this.config.indexType,
                    maxVectors: this.config.maxVectors
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.index = result.indexId;
                console.log('Vector index initialized:', this.index);
            } else {
                throw new Error('Failed to initialize vector index');
            }
        } catch (error) {
            console.error('Error initializing vector index:', error);
            throw error;
        }
    }

    /**
     * Start update queue
     */
    startUpdateQueue() {
        setInterval(() => {
            this.processUpdateQueue();
        }, this.config.updateInterval);
    }

    /**
     * Process update queue
     */
    async processUpdateQueue() {
        if (this.isUpdating || this.updateQueue.length === 0) {
            return;
        }

        this.isUpdating = true;
        
        try {
            const batch = this.updateQueue.splice(0, this.config.batchSize);
            await this.updateVectorsBatch(batch);
        } catch (error) {
            console.error('Error processing update queue:', error);
        } finally {
            this.isUpdating = false;
        }
    }

    /**
     * Add vector to store
     */
    async addVector(vectorId, embedding, metadata) {
        const vector = {
            id: vectorId,
            embedding: embedding,
            documentId: metadata.documentId,
            chunkId: metadata.chunkId,
            text: metadata.text,
            createdAt: new Date().toISOString(),
            metadata: metadata.metadata || {}
        };
        
        // Store locally
        this.vectors.set(vectorId, embedding);
        this.metadata.set(vectorId, {
            id: vectorId,
            documentId: metadata.documentId,
            chunkId: metadata.chunkId,
            text: metadata.text,
            createdAt: vector.createdAt,
            metadata: metadata.metadata || {}
        });
        
        // Add to update queue
        this.updateQueue.push(vector);
        
        // Update statistics
        this.updateStatistics();
        
        return vector;
    }

    /**
     * Add vectors in batch
     */
    async addVectorsBatch(vectors) {
        const addedVectors = [];
        
        for (const vector of vectors) {
            const added = await this.addVector(
                vector.id,
                vector.embedding,
                vector.metadata
            );
            addedVectors.push(added);
        }
        
        return addedVectors;
    }

    /**
     * Update vectors batch
     */
    async updateVectorsBatch(vectors) {
        if (vectors.length === 0) return;
        
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vectors/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    vectors: vectors,
                    indexId: this.index
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to update vectors batch');
            }
            
            const result = await response.json();
            console.log(`Updated ${vectors.length} vectors in batch`);
            
            // Update statistics
            this.updateStatistics();
            
        } catch (error) {
            console.error('Error updating vectors batch:', error);
            throw error;
        }
    }

    /**
     * Search similar vectors
     */
    async searchSimilar(queryEmbedding, options = {}) {
        const searchParams = {
            query: queryEmbedding,
            k: options.k || 10,
            threshold: options.threshold || this.config.similarityThreshold,
            filters: options.filters || {},
            indexId: this.index
        };
        
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vectors/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchParams)
            });
            
            if (!response.ok) {
                throw new Error('Vector search failed');
            }
            
            const results = await response.json();
            
            // Enhance results with metadata
            return this.enhanceSearchResults(results);
            
        } catch (error) {
            console.error('Error searching vectors:', error);
            throw error;
        }
    }

    /**
     * Enhance search results with metadata
     */
    enhanceSearchResults(results) {
        if (!results.results) return results;
        
        const enhanced = {
            ...results,
            results: results.results.map(result => {
                const metadata = this.metadata.get(result.id);
                return {
                    ...result,
                    metadata: metadata || {},
                    text: metadata?.text || '',
                    documentId: metadata?.documentId || '',
                    chunkId: metadata?.chunkId || ''
                };
            })
        };
        
        return enhanced;
    }

    /**
     * Get vector by ID
     */
    getVector(vectorId) {
        const embedding = this.vectors.get(vectorId);
        const metadata = this.metadata.get(vectorId);
        
        if (embedding && metadata) {
            return {
                id: vectorId,
                embedding: embedding,
                ...metadata
            };
        }
        
        return null;
    }

    /**
     * Get vectors by document ID
     */
    getVectorsByDocument(documentId) {
        const vectors = [];
        
        for (const [vectorId, metadata] of this.metadata.entries()) {
            if (metadata.documentId === documentId) {
                const embedding = this.vectors.get(vectorId);
                if (embedding) {
                    vectors.push({
                        id: vectorId,
                        embedding: embedding,
                        ...metadata
                    });
                }
            }
        }
        
        return vectors;
    }

    /**
     * Delete vector
     */
    async deleteVector(vectorId) {
        try {
            // Delete from server
            const response = await fetch(`${this.config.apiBaseUrl}/vectors/${vectorId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete vector from server');
            }
            
            // Remove from local storage
            this.vectors.delete(vectorId);
            this.metadata.delete(vectorId);
            
            // Update statistics
            this.updateStatistics();
            
            return true;
            
        } catch (error) {
            console.error('Error deleting vector:', error);
            throw error;
        }
    }

    /**
     * Delete vectors by document ID
     */
    async deleteVectorsByDocument(documentId) {
        const vectorsToDelete = this.getVectorsByDocument(documentId);
        const deletePromises = vectorsToDelete.map(vector => this.deleteVector(vector.id));
        
        try {
            await Promise.all(deletePromises);
            console.log(`Deleted ${vectorsToDelete.length} vectors for document ${documentId}`);
            return vectorsToDelete.length;
        } catch (error) {
            console.error('Error deleting vectors by document:', error);
            throw error;
        }
    }

    /**
     * Update vector metadata
     */
    async updateVectorMetadata(vectorId, updates) {
        const metadata = this.metadata.get(vectorId);
        if (metadata) {
            Object.assign(metadata, updates);
            this.metadata.set(vectorId, metadata);
            
            // Save to local storage
            this.saveToLocalStorage();
            
            // Update on server
            try {
                const response = await fetch(`${this.config.apiBaseUrl}/vectors/${vectorId}/metadata`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updates)
                });
                
                if (!response.ok) {
                    console.warn('Failed to update vector metadata on server');
                }
            } catch (error) {
                console.warn('Error updating vector metadata on server:', error);
            }
        }
    }

    /**
     * Save to local storage
     */
    saveToLocalStorage() {
        const metadataArray = Array.from(this.metadata.values());
        localStorage.setItem('ai_rag_vectors_metadata', JSON.stringify(metadataArray));
    }

    /**
     * Update statistics
     */
    updateStatistics() {
        this.statistics = {
            totalVectors: this.vectors.size,
            totalDocuments: new Set(Array.from(this.metadata.values()).map(v => v.documentId)).size,
            lastUpdate: new Date().toISOString(),
            indexSize: this.updateQueue.length
        };
    }

    /**
     * Get statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Get vector store health
     */
    async getHealth() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vector-health`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Could not get vector store health:', error);
        }
        
        // Fallback health check
        return {
            status: 'unknown',
            totalVectors: this.vectors.size,
            indexStatus: this.index ? 'initialized' : 'not_initialized',
            queueSize: this.updateQueue.length,
            isUpdating: this.isUpdating
        };
    }

    /**
     * Optimize vector store
     */
    async optimize() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vectors/optimize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    indexId: this.index
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Vector store optimized:', result);
                return result;
            } else {
                throw new Error('Failed to optimize vector store');
            }
        } catch (error) {
            console.error('Error optimizing vector store:', error);
            throw error;
        }
    }

    /**
     * Backup vector store
     */
    async backup() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vectors/backup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    indexId: this.index
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Vector store backup created:', result);
                return result;
            } else {
                throw new Error('Failed to create vector store backup');
            }
        } catch (error) {
            console.error('Error creating vector store backup:', error);
            throw error;
        }
    }

    /**
     * Restore vector store from backup
     */
    async restore(backupId) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/vectors/restore`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    backupId: backupId,
                    indexId: this.index
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Vector store restored from backup:', result);
                
                // Reload vectors after restore
                await this.loadExistingVectors();
                
                return result;
            } else {
                throw new Error('Failed to restore vector store');
            }
        } catch (error) {
            console.error('Error restoring vector store:', error);
            throw error;
        }
    }

    /**
     * Refresh vectors
     */
    async refreshVectors() {
        await this.loadExistingVectors();
        this.updateStatistics();
        console.log('🔄 AI RAG Vector Store refreshed');
    }

    /**
     * Clear update queue
     */
    clearUpdateQueue() {
        this.updateQueue = [];
        console.log('Vector update queue cleared');
    }

    /**
     * Get update queue status
     */
    getUpdateQueueStatus() {
        return {
            queueSize: this.updateQueue.length,
            isUpdating: this.isUpdating,
            batchSize: this.config.batchSize,
            updateInterval: this.config.updateInterval
        };
    }

    /**
     * Destroy the vector store
     */
    destroy() {
        this.isUpdating = false;
        this.updateQueue = [];
        this.vectors.clear();
        this.metadata.clear();
        this.index = null;
        this.isInitialized = false;
        
        console.log('🧹 AI RAG Vector Store destroyed');
    }
} 