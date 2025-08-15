/**
 * Knowledge Graph Neo4j Core Module
 * Handles core graph operations, node/relationship management, and graph functionality
 * Now with full authentication integration
 */

export default class KGNeo4jCore {
    constructor() {
        this.isInitialized = false;
        this.isAuthenticated = false;
        this.currentUser = null;
        this.organizationId = null;
        
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
            // 🔐 CRITICAL: Wait for authentication system to be ready
            await this.waitForAuthSystem();
            
            // Update authentication state
            this.updateAuthState();
            
            // Setup authentication event listeners
            this.setupAuthEventListeners();

            // Load configuration
            await this.loadConfiguration();

            // Initialize graph storage (optional - backend may not be available)
            try {
                await this.initializeGraphStorage();
            } catch (error) {
                console.warn('⚠️ Knowledge Graph Core: Backend services not available, continuing in frontend mode');
            }

            // Load existing graph data (will use demo data if backend unavailable)
            await this.loadExistingGraphData();

            // Initialize cache
            if (this.config.cacheEnabled) {
                this.initializeCache();
            }

            // Start operation queue
            this.startOperationQueue();

            this.isInitialized = true;
            console.log('✅ Knowledge Graph Neo4j Core initialized with authentication');

        } catch (error) {
            console.error('❌ Knowledge Graph Neo4j Core initialization failed:', error);
            throw error;
        }
    }

    /**
     * 🔐 Wait for authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Knowledge Graph Core: Waiting for authentication system...');
        
        return new Promise((resolve) => {
            if (window.authSystemReady && window.authManager) {
                console.log('🔐 Knowledge Graph Core: Auth system already ready');
                resolve();
                return;
            }
            
            const handleReady = () => {
                console.log('🚀 Knowledge Graph Core: Auth system ready event received');
                window.removeEventListener('authSystemReady', handleReady);
                resolve();
            };
            
            window.addEventListener('authSystemReady', handleReady);
            
            // Fallback: check periodically
            const checkInterval = setInterval(() => {
                if (window.authSystemReady && window.authManager) {
                    clearInterval(checkInterval);
                    window.removeEventListener('authSystemReady', handleReady);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                window.removeEventListener('authSystemReady', handleReady);
                console.warn('⚠️ Knowledge Graph Core: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * 🔐 Update authentication state from global auth manager
     */
    updateAuthState() {
        if (!window.authManager) {
            console.log('⚠️ Knowledge Graph Core: No auth manager available');
            return;
        }
        
        try {
            const sessionInfo = window.authManager.getSessionInfo();
            console.log('🔐 Knowledge Graph Core: Auth state update:', sessionInfo);
            
            this.isAuthenticated = sessionInfo.isAuthenticated;
            this.currentUser = sessionInfo.user;
            this.organizationId = sessionInfo.user?.organization_id;
            
            console.log(`🔐 Knowledge Graph Core: User ${this.currentUser?.username || 'unauthenticated'} (org: ${this.organizationId || 'none'})`);
            
        } catch (error) {
            console.warn('⚠️ Knowledge Graph Core: Error updating auth state:', error);
        }
    }

    /**
     * 🔐 Setup authentication event listeners
     */
    setupAuthEventListeners() {
        window.addEventListener('authStateChanged', () => {
            console.log('🔄 Knowledge Graph Core: Auth state changed, updating...');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
        
        window.addEventListener('logout', () => {
            console.log('🔐 Knowledge Graph Core: Logout detected');
            this.updateAuthState();
            this.handleAuthStateChange();
        });
    }

    /**
     * 🔐 Handle authentication state changes
     */
    handleAuthStateChange() {
        if (this.isAuthenticated && this.organizationId) {
            console.log(`🔐 Knowledge Graph Core: User authenticated, loading organization data for ${this.currentUser.username}`);
            // Reload data for the authenticated user
            this.loadExistingGraphData();
        } else {
            console.log('🔐 Knowledge Graph Core: User not authenticated, clearing sensitive data');
            // Clear sensitive data and load demo data
            this.clearUserData();
            this.loadDemoData();
        }
    }

    /**
     * 🔐 Get authentication headers for API calls
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const token = window.authManager?.getStoredToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
            console.log(`🔐 Knowledge Graph Core: Making authenticated API call for user ${this.currentUser?.username || 'unknown'}`);
        } else {
            console.log('🔐 Knowledge Graph Core: Making unauthenticated API call');
        }
        
        return headers;
    }

    /**
     * 🔐 Load user-specific graph data based on organization
     */
    async loadExistingGraphData() {
        if (!this.isAuthenticated || !this.organizationId) {
            console.log('🔐 Knowledge Graph Core: User not authenticated, loading demo data');
            await this.loadDemoData();
            return;
        }

        console.log(`🔐 Knowledge Graph Core: Loading graph data for organization ${this.organizationId}`);
        
        try {
            const headers = this.getAuthHeaders();
            
            // Load nodes for the user's organization
            const nodesResponse = await fetch(`${this.config.apiBaseUrl}/nodes?org_id=${this.organizationId}`, {
                headers
            });
            
            if (nodesResponse.ok) {
                const nodes = await nodesResponse.json();
                this.nodes.clear();
                nodes.forEach(node => this.nodes.set(node.id, node));
                console.log(`🔐 Knowledge Graph Core: Loaded ${nodes.length} nodes for organization ${this.organizationId}`);
            }
            
            // Load relationships for the user's organization
            const relationshipsResponse = await fetch(`${this.config.apiBaseUrl}/relationships?org_id=${this.organizationId}`, {
                headers
            });
            
            if (relationshipsResponse.ok) {
                const relationships = await relationshipsResponse.json();
                this.relationships.clear();
                relationships.forEach(rel => this.relationships.set(rel.id, rel));
                console.log(`🔐 Knowledge Graph Core: Loaded ${relationships.length} relationships for organization ${this.organizationId}`);
            }
            
            this.updateStatistics();
            
        } catch (error) {
            console.error('❌ Knowledge Graph Core: Failed to load organization data:', error);
            // Fallback to demo data
            await this.loadDemoData();
        }
    }

    /**
     * 🔐 Load demo data for unauthenticated users
     */
    async loadDemoData() {
        console.log('🔐 Knowledge Graph Core: Loading demo graph data');
        
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/demo-data`);
            if (response.ok) {
                const demoData = await response.json();
                
                this.nodes.clear();
                demoData.nodes.forEach(node => this.nodes.set(node.id, node));
                
                this.relationships.clear();
                demoData.relationships.forEach(rel => this.relationships.set(rel.id, rel));
                
                this.updateStatistics();
                console.log('🔐 Knowledge Graph Core: Demo data loaded successfully');
            }
        } catch (error) {
            console.warn('⚠️ Knowledge Graph Core: Failed to load demo data:', error);
        }
    }

    /**
     * 🔐 Clear user-specific data
     */
    clearUserData() {
        console.log('🔐 Knowledge Graph Core: Clearing user-specific data');
        this.nodes.clear();
        this.relationships.clear();
        this.cache.clear();
        this.updateStatistics();
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
                console.log('✅ Knowledge Graph Core: Configuration loaded from server');
            } else {
                console.warn('⚠️ Knowledge Graph Core: Server config endpoint not available, using defaults');
            }
        } catch (error) {
            console.warn('⚠️ Knowledge Graph Core: Could not load configuration from server, using defaults:', error);
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
            
            if (response.ok) {
                console.log('✅ Knowledge Graph Core: Graph storage initialized');
            } else if (response.status === 404) {
                console.warn('⚠️ Knowledge Graph Core: Backend graph storage not available, running in frontend-only mode');
                // Continue without backend - this is acceptable for testing
            } else {
                throw new Error(`Failed to initialize graph storage: ${response.statusText}`);
            }
        } catch (error) {
            if (error.message.includes('Failed to fetch')) {
                console.warn('⚠️ Knowledge Graph Core: Backend not available, running in frontend-only mode');
                // Continue without backend - this is acceptable for testing
            } else {
                console.error('❌ Knowledge Graph Core: Graph storage initialization failed:', error);
                throw error;
            }
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
        // 🔐 Add organization ID to node properties for user-specific data
        const nodeData = {
            labels: Array.isArray(labels) ? labels : [labels],
            properties: {
                ...properties,
                org_id: this.organizationId || 'demo',
                created_by: this.currentUser?.username || 'anonymous'
            },
            created: new Date().toISOString()
        };

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/nodes`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
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
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ 
                    properties: {
                        ...properties,
                        updated_by: this.currentUser?.username || 'anonymous',
                        updated_at: new Date().toISOString()
                    }
                })
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
                method: 'DELETE',
                headers: this.getAuthHeaders()
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
        // 🔐 Add organization ID to relationship properties for user-specific data
        const relationshipData = {
            startNode: startNodeId,
            endNode: endNodeId,
            type: type,
            properties: {
                ...properties,
                org_id: this.organizationId || 'demo',
                created_by: this.currentUser?.username || 'anonymous'
            },
            created: new Date().toISOString()
        };

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/relationships`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
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
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ 
                    properties: {
                        ...properties,
                        updated_by: this.currentUser?.username || 'anonymous',
                        updated_at: new Date().toISOString()
                    }
                })
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
                method: 'DELETE',
                headers: this.getAuthHeaders()
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