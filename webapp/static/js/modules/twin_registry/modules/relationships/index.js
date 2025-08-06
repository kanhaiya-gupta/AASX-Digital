/**
 * Relationship Manager - Main Module
 * Orchestrates relationship operations and UI updates
 */

import RelationshipOperations from './operations.js';
import RelationshipUI from './ui.js';

export default class RelationshipManager {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.isInitialized = false;
        this.relationships = new Map(); // Cache relationships
        
        // Initialize sub-modules
        this.operations = new RelationshipOperations(apiBaseUrl);
        this.ui = new RelationshipUI();
    }

    async init() {
        try {
            console.log('🔗 Initializing Relationship Manager...');
            this.setupEventListeners();
            this.isInitialized = true;
            console.log('✅ Relationship Manager initialized');
        } catch (error) {
            console.error('❌ Relationship Manager initialization failed:', error);
            throw error;
        }
    }

    setupEventListeners() {
        // Listen for relationship creation requests
        document.addEventListener('twinRelationshipCreate', (event) => {
            this.createRelationship(event.detail.sourceTwinId, event.detail.targetTwinId, event.detail.relationshipType, event.detail.relationshipData);
        });

        // Listen for relationship fetch requests
        document.addEventListener('twinRelationshipFetch', (event) => {
            this.getTwinRelationships(event.detail.twinId);
        });

        // Listen for relationship deletion requests
        document.addEventListener('twinRelationshipDelete', (event) => {
            this.deleteRelationship(event.detail.relationshipId);
        });
    }

    async createRelationship(sourceTwinId, targetTwinId, relationshipType, relationshipData = {}) {
        try {
            const result = await this.operations.createRelationship(sourceTwinId, targetTwinId, relationshipType, relationshipData);

            if (result.success) {
                this.ui.updateRelationshipUI(sourceTwinId, targetTwinId, relationshipType, 'created');
                this.dispatchEvent('relationshipCreated', { 
                    sourceTwinId, 
                    targetTwinId, 
                    relationshipType, 
                    relationship: result.relationship 
                });
                this.ui.showRelationshipMessage('Relationship created successfully', 'success');
            } else {
                this.ui.showRelationshipMessage(result.message || 'Failed to create relationship', 'error');
                this.dispatchEvent('relationshipCreateFailed', { 
                    sourceTwinId, 
                    targetTwinId, 
                    relationshipType, 
                    error: result.message 
                });
            }

            return result;

        } catch (error) {
            console.error('❌ Failed to create relationship:', error);
            this.ui.showRelationshipMessage(`Failed to create relationship: ${error.message}`, 'error');
            this.dispatchEvent('relationshipCreateFailed', { 
                sourceTwinId, 
                targetTwinId, 
                relationshipType, 
                error: error.message 
            });
            throw error;
        }
    }

    async getTwinRelationships(twinId) {
        try {
            const result = await this.operations.getTwinRelationships(twinId);

            if (result.success) {
                this.ui.updateRelationshipsUI(twinId, result.relationships);
                this.cacheRelationships(twinId, result.relationships);
                this.dispatchEvent('relationshipsFetched', { twinId, relationships: result.relationships });
            } else {
                this.dispatchEvent('relationshipsFetchFailed', { twinId, error: result.message });
            }

            return result;

        } catch (error) {
            console.error(`❌ Failed to fetch relationships for twin ${twinId}:`, error);
            this.dispatchEvent('relationshipsFetchFailed', { twinId, error: error.message });
            throw error;
        }
    }

    async getAllRelationships(sourceTwinId = null, targetTwinId = null) {
        try {
            const result = await this.operations.getAllRelationships(sourceTwinId, targetTwinId);

            if (result.success) {
                this.dispatchEvent('allRelationshipsFetched', { relationships: result.relationships });
            } else {
                console.error('Failed to fetch all relationships:', result);
            }

            return result;

        } catch (error) {
            console.error('❌ Failed to fetch all relationships:', error);
            throw error;
        }
    }

    async deleteRelationship(relationshipId) {
        try {
            const result = await this.operations.deleteRelationship(relationshipId);

            if (result.success) {
                this.ui.updateRelationshipUI(null, null, null, 'deleted', relationshipId);
                this.dispatchEvent('relationshipDeleted', { relationshipId });
                this.ui.showRelationshipMessage('Relationship deleted successfully', 'success');
            } else {
                this.ui.showRelationshipMessage(result.message || 'Failed to delete relationship', 'error');
                this.dispatchEvent('relationshipDeleteFailed', { relationshipId, error: result.message });
            }

            return result;

        } catch (error) {
            console.error('❌ Failed to delete relationship:', error);
            this.ui.showRelationshipMessage(`Failed to delete relationship: ${error.message}`, 'error');
            this.dispatchEvent('relationshipDeleteFailed', { relationshipId, error: error.message });
            throw error;
        }
    }

    cacheRelationships(twinId, relationships) {
        this.relationships.set(twinId, relationships);
    }

    getCachedRelationships(twinId) {
        return this.relationships.get(twinId) || [];
    }

    dispatchEvent(eventName, data) {
        document.dispatchEvent(new CustomEvent(eventName, { detail: data }));
    }

    // Public methods for external use
    async createParentChildRelationship(parentTwinId, childTwinId, metadata = {}) {
        return this.createRelationship(parentTwinId, childTwinId, 'parent-child', metadata);
    }

    async createDependencyRelationship(dependentTwinId, dependencyTwinId, metadata = {}) {
        return this.createRelationship(dependentTwinId, dependencyTwinId, 'dependency', metadata);
    }

    async createSiblingRelationship(twinId1, twinId2, metadata = {}) {
        return this.createRelationship(twinId1, twinId2, 'sibling', metadata);
    }

    getRelationshipTypes() {
        return [
            'parent-child',
            'dependency',
            'sibling',
            'composition',
            'aggregation',
            'association'
        ];
    }

    setMessageTimeout(timeout) {
        this.ui.setMessageTimeout(timeout);
    }

    // Cleanup method
    cleanup() {
        this.relationships.clear();
        this.isInitialized = false;
        console.log('🧹 Relationship Manager cleaned up');
    }
} 