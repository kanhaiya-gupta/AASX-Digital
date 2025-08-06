/**
 * Relationship UI Module
 * Handles UI updates for relationship operations
 */

export default class RelationshipUI {
    constructor() {
        this.messageTimeout = 5000;
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

        // Auto-dismiss after timeout
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.remove();
            }
        }, this.messageTimeout);
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

    setMessageTimeout(timeout) {
        this.messageTimeout = timeout;
    }
} 