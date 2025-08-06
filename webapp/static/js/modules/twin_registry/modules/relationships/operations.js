/**
 * Relationship Operations Module
 * Handles CRUD operations for twin relationships
 */

export default class RelationshipOperations {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.endpoints = {
            create: '/relationships',
            get: '/relationships',
            getByTwin: '/twins/{twin_id}/relationships',
            delete: '/relationships/{relationship_id}'
        };
    }

    async createRelationship(sourceTwinId, targetTwinId, relationshipType, relationshipData = {}) {
        try {
            console.log(`🔗 Creating relationship: ${sourceTwinId} -> ${targetTwinId} (${relationshipType})`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.create}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_twin_id: sourceTwinId,
                    target_twin_id: targetTwinId,
                    relationship_type: relationshipType,
                    relationship_data: relationshipData
                })
            });

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('❌ Failed to create relationship:', error);
            throw error;
        }
    }

    async getTwinRelationships(twinId) {
        try {
            console.log(`🔗 Fetching relationships for twin: ${twinId}`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.getByTwin.replace('{twin_id}', twinId)}`);
            const result = await response.json();

            if (result.success) {
                return result;
            } else {
                console.error(`Failed to fetch relationships for twin ${twinId}:`, result);
                return { success: false, relationships: [], count: 0 };
            }

        } catch (error) {
            console.error(`❌ Failed to fetch relationships for twin ${twinId}:`, error);
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
            return result;

        } catch (error) {
            console.error('❌ Failed to delete relationship:', error);
            throw error;
        }
    }

    // Convenience methods
    async createParentChildRelationship(parentTwinId, childTwinId, metadata = {}) {
        return this.createRelationship(parentTwinId, childTwinId, 'parent-child', metadata);
    }

    async createDependencyRelationship(dependentTwinId, dependencyTwinId, metadata = {}) {
        return this.createRelationship(dependentTwinId, dependencyTwinId, 'dependency', metadata);
    }

    async createSiblingRelationship(twinId1, twinId2, metadata = {}) {
        return this.createRelationship(twinId1, twinId2, 'sibling', metadata);
    }
} 