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
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
    }

    async init() {
        try {
            console.log('🔄 Initializing Relationship Operations...');
            
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            console.log('✅ Relationship Operations initialized');
        } catch (error) {
            console.error('❌ Relationship Operations initialization failed:', error);
            throw error;
        }
    }

    async createRelationship(sourceTwinId, targetTwinId, relationshipType, relationshipData = {}) {
        try {
            console.log(`🔗 Creating relationship: ${sourceTwinId} -> ${targetTwinId} (${relationshipType})`);

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.create}`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
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

            const response = await fetch(`${this.apiBaseUrl}${this.endpoints.getByTwin.replace('{twin_id}', twinId)}`, {
                headers: this.getAuthHeaders()
            });
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

            const response = await fetch(url, {
                headers: this.getAuthHeaders()
            });
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
                method: 'DELETE',
                headers: this.getAuthHeaders()
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

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Relationship Operations: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Relationship Operations: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Relationship Operations: Auth system ready event received');
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
                console.warn('⚠️ Relationship Operations: Timeout waiting for auth system');
                resolve();
            }, 10000);
        });
    }

    /**
     * Update authentication state
     */
    updateAuthState() {
        if (window.authManager) {
            this.isAuthenticated = window.authManager.isAuthenticated();
            this.currentUser = null; // User info not needed currently
            this.authToken = window.authManager.getStoredToken();
            console.log('🔐 Relationship Operations: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Relationship Operations: No auth manager available');
        }
    }

    /**
     * Setup authentication event listeners
     */
    setupAuthListeners() {
        window.addEventListener('authStateChanged', () => {
            this.updateAuthState();
        });

        window.addEventListener('loginSuccess', () => {
            this.updateAuthState();
        });

        window.addEventListener('logout', () => {
            this.updateAuthState();
            // Clear sensitive data when user logs out
            this.clearSensitiveData();
        });
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
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        console.log('🧹 Relationship Operations: Sensitive data cleared');
    }
}