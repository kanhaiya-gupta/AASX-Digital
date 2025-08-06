/**
 * Twin Relationship Management Module
 * Handles twin relationships (parent-child, dependencies, etc.)
 */

export default class TwinRelationshipManager {
    constructor() {
        this.apiBaseUrl = '/api/twin-registry';
        this.endpoints = {
            create: '/relationships',
            get: '/relationships',
            getByTwin: '/twins/{twin_id}/relationships',
            delete: '/relationships/{relationship_id}'
        };
        this.isInitialized = false;
        this.relationships = new Map(); // Cache relationships
    }

    async init() {
        try {
            console.log('🔗 Initializing Twin Relationship Manager...');
            
            // Set up event listeners
            this.setupEventListeners();
            
            this.isInitialized = true;
            console.log('✅ Twin Relationship Manager initialized');
        } catch (error) {
            console.error('❌ Twin Relationship Manager initialization failed:', error);
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
            console.log(`🔗 Creating relationship: ${sourceTwinId} -> ${targetTwinId} (${relationshipType})`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.create}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source_twin_id: sourceTwinId,
                    target_twin_id: targetTwinId,
                    relationship_type: relationshipType,
                    relationship_data: relationshipData
                })
            });

            const result = await response.json();

            if (result.success) {
                this.updateRelationshipUI(sourceTwinId, targetTwinId, relationshipType, 'created');
                this.dispatchRelationshipEvent('relationshipCreated', { 
                    sourceTwinId, 
                    targetTwinId, 
                    relationshipType, 
                    relationship: result.relationship 
                });
                this.showRelationshipMessage('Relationship created successfully', 'success');
            } else {
                this.showRelationshipMessage(result.message || 'Failed to create relationship', 'error');
                this.dispatchRelationshipEvent('relationshipCreateFailed', { 
                    sourceTwinId, 
                    targetTwinId, 
                    relationshipType, 
                    error: result.message 
                });
            }

            return result;

        } catch (error) {
            console.error('❌ Failed to create relationship:', error);
            this.showRelationshipMessage(`Failed to create relationship: ${error.message}`, 'error');
            this.dispatchRelationshipEvent('relationshipCreateFailed', { 
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
            console.log(`🔗 Fetching relationships for twin: ${twinId}`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.getByTwin.replace('{twin_id}', twinId)}`);
            const result = await response.json();

            if (result.success) {
                this.updateRelationshipsUI(twinId, result.relationships);
                this.cacheRelationships(twinId, result.relationships);
                this.dispatchRelationshipEvent('relationshipsFetched', { twinId, relationships: result.relationships });
            } else {
                console.error(`Failed to fetch relationships for twin ${twinId}:`, result);
                this.dispatchRelationshipEvent('relationshipsFetchFailed', { twinId, error: result.message });
            }

            return result;

        } catch (error) {
            console.error(`❌ Failed to fetch relationships for twin ${twinId}:`, error);
            this.dispatchRelationshipEvent('relationshipsFetchFailed', { twinId, error: error.message });
            throw error;
        }
    }

    async getAllRelationships(sourceTwinId = null, targetTwinId = null) {
        try {
            let url = `${this.apiBaseUrl}${this.endpoints.get}`;
            const params = new URLSearchParams();
            
            if (sourceTwinId) params.append('source_twin_id', sourceTwinId);
            if (targetTwinId) params.append('target_twin_id', targetTwinId);
            
            if (params.toString()) {
                url += `?${params.toString()}`;
            }

            const response = await fetch(url);
            const result = await response.json();

            if (result.success) {
                this.dispatchRelationshipEvent('allRelationshipsFetched', { relationships: result.relationships });
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
            console.log(`🔗 Deleting relationship: ${relationshipId}`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.delete.replace('{relationship_id}', relationshipId)}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.updateRelationshipUI(null, null, null, 'deleted', relationshipId);
                this.dispatchRelationshipEvent('relationshipDeleted', { relationshipId });
                this.showRelationshipMessage('Relationship deleted successfully', 'success');
            } else {
                this.showRelationshipMessage(result.message || 'Failed to delete relationship', 'error');
                this.dispatchRelationshipEvent('relationshipDeleteFailed', { relationshipId, error: result.message });
            }

            return result;

        } catch (error) {
            console.error('❌ Failed to delete relationship:', error);
            this.showRelationshipMessage(`Failed to delete relationship: ${error.message}`, 'error');
            this.dispatchRelationshipEvent('relationshipDeleteFailed', { relationshipId, error: error.message });
            throw error;
        }
    }

    updateRelationshipsUI(twinId, relationships) {
        // Update relationships display in the UI
        const relationshipsContainer = document.querySelector(`[data-twin-relationships="${twinId}"]`);
        if (relationshipsContainer) {
            if (relationships.length === 0) {
                relationshipsContainer.innerHTML = '<p class="text-muted">No relationships found</p>';
            } else {
                relationshipsContainer.innerHTML = relationships.map(rel => `
                    <div class="relationship-item" data-relationship-id="${rel.relationship_id}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <span class="badge bg-primary me-2">${rel.relationship_type}</span>
                                <span class="relationship-target">${rel.target_twin_id}</span>
                            </div>
                            <div class="relationship-actions">
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteRelationship('${rel.relationship_id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <small class="text-muted">Created: ${new Date(rel.created_at).toLocaleString()}</small>
                    </div>
                `).join('');
            }
        }

        // Update relationship count in twin row
        const twinRow = document.querySelector(`[data-twin-id="${twinId}"]`);
        if (twinRow) {
            const relationshipCount = twinRow.querySelector('.twin-relationship-count');
            if (relationshipCount) {
                relationshipCount.textContent = relationships.length;
            }
        }
    }

    updateRelationshipUI(sourceTwinId, targetTwinId, relationshipType, action, relationshipId = null) {
        // Update specific relationship UI elements
        if (action === 'created') {
            this.showRelationshipMessage(`Relationship created: ${sourceTwinId} -> ${targetTwinId}`, 'success');
        } else if (action === 'deleted') {
            this.showRelationshipMessage(`Relationship deleted: ${relationshipId}`, 'success');
        }
    }

    cacheRelationships(twinId, relationships) {
        this.relationships.set(twinId, relationships);
    }

    getCachedRelationships(twinId) {
        return this.relationships.get(twinId) || [];
    }

    showRelationshipMessage(message, type = 'info') {
        // Create or update relationship message
        let messageElement = document.querySelector('[data-relationship-message]');
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.setAttribute('data-relationship-message', '');
            messageElement.className = 'relationship-message';
            document.body.appendChild(messageElement);
        }

        messageElement.className = `relationship-message alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        messageElement.innerHTML = `
            <i class="fas fa-link me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.remove();
            }
        }, 5000);
    }

    dispatchRelationshipEvent(eventName, data) {
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

    getRelationshipTypeIcon(relationshipType) {
        const icons = {
            'parent-child': 'fas fa-sitemap',
            'dependency': 'fas fa-link',
            'sibling': 'fas fa-code-branch',
            'composition': 'fas fa-cube',
            'aggregation': 'fas fa-object-group',
            'association': 'fas fa-arrows-alt-h'
        };
        return icons[relationshipType] || 'fas fa-link';
    }

    getRelationshipTypeColor(relationshipType) {
        const colors = {
            'parent-child': 'primary',
            'dependency': 'warning',
            'sibling': 'info',
            'composition': 'success',
            'aggregation': 'secondary',
            'association': 'dark'
        };
        return colors[relationshipType] || 'light';
    }

    // Cleanup method
    cleanup() {
        this.relationships.clear();
        this.isInitialized = false;
        console.log('🧹 Twin Relationship Manager cleaned up');
    }
} 