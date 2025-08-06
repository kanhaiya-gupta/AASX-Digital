/**
 * Knowledge Graph Neo4j Core Module
 * Handles core graph operations, node/relationship management, and graph functionality
 */

export default class KGNeo4jCore {
    constructor() {
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: '/api/kg-neo4j',
            maxNodes: 10000,
            maxRelationships: 50000,
            batchSize: 100,
            timeout: 30000,
            retryAttempts: 3,
            retryDelay: 1000,
            cacheEnabled: true,
            cacheExpiry: 300000 // 5 minutes
        };

        this.nodes = new Map();
        this.relationships = new Map();
        this.labels = new Set();
        this.relationshipTypes = new Set();
        this.properties = new Map();
        this.cache = new Map();
        this.operations = [];
        this.isProcessing = false;
        this.statistics = {
            totalNodes: 0,
            totalRelationships: 0,
            totalLabels: 0,
            totalRelationshipTypes: 0,
            lastUpdate: null,
            graphSize: 0
        };
    }

    /**
     * Initialize the Knowledge Graph Core
     */
    async init() {
        console.log('🔧 Initializing Knowledge Graph Neo4j Core...');

        try {
            // Load configuration
            await this.loadConfiguration();

            // Initialize graph storage
            await this.initializeGraphStorage();

            // Load existing graph data
            await this.loadExistingGraphData();

            // Initialize cache
            if (this.config.cacheEnabled) {
                this.initializeCache();
            }

            // Start operation queue
            this.startOperationQueue();

            this.isInitialized = true;
            console.log('✅ Knowledge Graph Neo4j Core initialized');

        } catch (error) {
            console.error('❌ Knowledge Graph Neo4j Core initialization failed:', error);
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
     * Initialize graph storage
     */
    async initializeGraphStorage() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/initialize`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to initialize graph storage: ${response.statusText}`);
            }
            
            console.log('Graph storage initialized');
        } catch (error) {
            console.error('Graph storage initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load existing graph data
     */
    async loadExistingGraphData() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/graph-data`);
            if (response.ok) {
                const data = await response.json();
                
                // Load nodes
                if (data.nodes) {
                    data.nodes.forEach(node => {
                        this.nodes.set(node.id, node);
                        if (node.labels) {
                            node.labels.forEach(label => this.labels.add(label));
                        }
                    });
                }

                // Load relationships
                if (data.relationships) {
                    data.relationships.forEach(rel => {
                        this.relationships.set(rel.id, rel);
                        this.relationshipTypes.add(rel.type);
                    });
                }

                // Update statistics
                this.updateStatistics();
            }
        } catch (error) {
            console.error('Failed to load existing graph data:', error);
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
     * Create a new node
     */
    async createNode(labels, properties = {}) {
        const nodeData = {
            labels: Array.isArray(labels) ? labels : [labels],
            properties: properties,
            created: new Date().toISOString()
        };

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/nodes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(nodeData)
            });

            if (response.ok) {
                const node = await response.json();
                this.nodes.set(node.id, node);
                
                // Update labels
                node.labels.forEach(label => this.labels.add(label));
                
                // Update cache
                this.cache.set(`node:${node.id}`, {
                    data: node,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('kgNodeCreated', {
                    detail: { node }
                }));

                return node;
            } else {
                throw new Error(`Failed to create node: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Node creation failed:', error);
            throw error;
        }
    }

    /**
     * Update an existing node
     */
    async updateNode(nodeId, properties = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/nodes/${nodeId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ properties })
            });

            if (response.ok) {
                const updatedNode = await response.json();
                this.nodes.set(nodeId, updatedNode);
                
                // Update cache
                this.cache.set(`node:${nodeId}`, {
                    data: updatedNode,
                    timestamp: Date.now()
                });

                // Dispatch event
                window.dispatchEvent(new CustomEvent('kgNodeUpdated', {
                    detail: { node: updatedNode }
                }));

                return updatedNode;
            } else {
                throw new Error(`Failed to update node: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Node update failed:', error);
            throw error;
        }
    }

    /**
     * Delete a node
     */
    async deleteNode(nodeId) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/nodes/${nodeId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.nodes.delete(nodeId);
                this.cache.delete(`node:${nodeId}`);
                
                // Remove relationships connected to this node
                for (const [relId, rel] of this.relationships) {
                    if (rel.startNode === nodeId || rel.endNode === nodeId) {
                        this.relationships.delete(relId);
                        this.cache.delete(`relationship:${relId}`);
                    }
                }

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('kgNodeDeleted', {
                    detail: { nodeId }
                }));

                return true;
            } else {
                throw new Error(`Failed to delete node: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Node deletion failed:', error);
            throw error;
        }
    }

    /**
     * Create a relationship between nodes
     */
    async createRelationship(startNodeId, endNodeId, type, properties = {}) {
        const relationshipData = {
            startNode: startNodeId,
            endNode: endNodeId,
            type: type,
            properties: properties,
            created: new Date().toISOString()
        };

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/relationships`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(relationshipData)
            });

            if (response.ok) {
                const relationship = await response.json();
                this.relationships.set(relationship.id, relationship);
                this.relationshipTypes.add(type);
                
                // Update cache
                this.cache.set(`relationship:${relationship.id}`, {
                    data: relationship,
                    timestamp: Date.now()
                });

                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('kgRelationshipCreated', {
                    detail: { relationship }
                }));

                return relationship;
            } else {
                throw new Error(`Failed to create relationship: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Relationship creation failed:', error);
            throw error;
        }
    }

    /**
     * Update a relationship
     */
    async updateRelationship(relationshipId, properties = {}) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/relationships/${relationshipId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ properties })
            });

            if (response.ok) {
                const updatedRelationship = await response.json();
                this.relationships.set(relationshipId, updatedRelationship);
                
                // Update cache
                this.cache.set(`relationship:${relationshipId}`, {
                    data: updatedRelationship,
                    timestamp: Date.now()
                });

                // Dispatch event
                window.dispatchEvent(new CustomEvent('kgRelationshipUpdated', {
                    detail: { relationship: updatedRelationship }
                }));

                return updatedRelationship;
            } else {
                throw new Error(`Failed to update relationship: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Relationship update failed:', error);
            throw error;
        }
    }

    /**
     * Delete a relationship
     */
    async deleteRelationship(relationshipId) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/relationships/${relationshipId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.relationships.delete(relationshipId);
                this.cache.delete(`relationship:${relationshipId}`);
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('kgRelationshipDeleted', {
                    detail: { relationshipId }
                }));

                return true;
            } else {
                throw new Error(`Failed to delete relationship: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Relationship deletion failed:', error);
            throw error;
        }
    }

    /**
     * Get node by ID
     */
    async getNode(nodeId) {
        // Check cache first
        const cacheKey = `node:${nodeId}`;
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            return cached.data;
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/nodes/${nodeId}`);
            if (response.ok) {
                const node = await response.json();
                
                // Update cache
                this.cache.set(cacheKey, {
                    data: node,
                    timestamp: Date.now()
                });

                return node;
            } else {
                throw new Error(`Failed to get node: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get node failed:', error);
            throw error;
        }
    }

    /**
     * Get relationship by ID
     */
    async getRelationship(relationshipId) {
        // Check cache first
        const cacheKey = `relationship:${relationshipId}`;
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheExpiry) {
            return cached.data;
        }

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/relationships/${relationshipId}`);
            if (response.ok) {
                const relationship = await response.json();
                
                // Update cache
                this.cache.set(cacheKey, {
                    data: relationship,
                    timestamp: Date.now()
                });

                return relationship;
            } else {
                throw new Error(`Failed to get relationship: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get relationship failed:', error);
            throw error;
        }
    }

    /**
     * Get nodes by label
     */
    async getNodesByLabel(label, limit = 100) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/nodes/label/${label}?limit=${limit}`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to get nodes by label: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get nodes by label failed:', error);
            throw error;
        }
    }

    /**
     * Get relationships by type
     */
    async getRelationshipsByType(type, limit = 100) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/relationships/type/${type}?limit=${limit}`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to get relationships by type: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Get relationships by type failed:', error);
            throw error;
        }
    }

    /**
     * Get graph statistics
     */
    getStatistics() {
        return { ...this.statistics };
    }

    /**
     * Update statistics
     */
    updateStatistics() {
        this.statistics = {
            totalNodes: this.nodes.size,
            totalRelationships: this.relationships.size,
            totalLabels: this.labels.size,
            totalRelationshipTypes: this.relationshipTypes.size,
            lastUpdate: new Date().toISOString(),
            graphSize: this.calculateGraphSize()
        };
    }

    /**
     * Calculate graph size in bytes
     */
    calculateGraphSize() {
        let size = 0;
        
        // Calculate nodes size
        for (const node of this.nodes.values()) {
            size += JSON.stringify(node).length;
        }
        
        // Calculate relationships size
        for (const rel of this.relationships.values()) {
            size += JSON.stringify(rel).length;
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
            case 'createNode':
                await this.createNode(operation.labels, operation.properties);
                break;
            case 'updateNode':
                await this.updateNode(operation.nodeId, operation.properties);
                break;
            case 'deleteNode':
                await this.deleteNode(operation.nodeId);
                break;
            case 'createRelationship':
                await this.createRelationship(operation.startNode, operation.endNode, operation.type, operation.properties);
                break;
            case 'updateRelationship':
                await this.updateRelationship(operation.relationshipId, operation.properties);
                break;
            case 'deleteRelationship':
                await this.deleteRelationship(operation.relationshipId);
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
     * Refresh graph data
     */
    async refreshData() {
        try {
            await this.loadExistingGraphData();
            this.updateStatistics();
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('kgDataRefreshed', {
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
                this.nodes.clear();
                this.relationships.clear();
                this.labels.clear();
                this.relationshipTypes.clear();
                this.cache.clear();
                this.operations = [];
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('kgDataCleared'));
            } else {
                throw new Error(`Failed to clear data: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Clear data failed:', error);
            throw error;
        }
    }

    /**
     * Export graph data
     */
    async exportGraph(format = 'json') {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/export?format=${format}`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Failed to export graph: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Export failed:', error);
            throw error;
        }
    }

    /**
     * Import graph data
     */
    async importGraph(data, format = 'json') {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/import`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ data, format })
            });

            if (response.ok) {
                await this.loadExistingGraphData();
                this.updateStatistics();
                
                // Dispatch event
                window.dispatchEvent(new CustomEvent('kgDataImported', {
                    detail: { data, format }
                }));
            } else {
                throw new Error(`Failed to import graph: ${response.statusText}`);
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
        this.nodes.clear();
        this.relationships.clear();
        this.labels.clear();
        this.relationshipTypes.clear();
        this.cache.clear();
        this.operations = [];
        console.log('🧹 Knowledge Graph Neo4j Core destroyed');
    }
} 