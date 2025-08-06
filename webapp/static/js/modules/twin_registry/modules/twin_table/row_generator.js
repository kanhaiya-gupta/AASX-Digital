/**
 * Twin Table Row Generator Module
 * Handles generation of twin table rows with actions
 */

export default class TwinTableRowGenerator {
    constructor() {
        this.actionTemplate = null;
    }

    async init() {
        try {
            // Load action template
            this.actionTemplate = await this.loadActionTemplate();
            console.log('✅ Twin Table Row Generator initialized');
        } catch (error) {
            console.error('❌ Twin Table Row Generator initialization failed:', error);
            throw error;
        }
    }

    async loadActionTemplate() {
        // For now, return the action template directly
        // In a real implementation, this could be loaded from a separate file
        return `
            <div class="btn-group" role="group">
                <!-- Lifecycle Actions -->
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-outline-success" 
                            onclick="startTwin('{{ twin_id }}', 'user')" 
                            title="Start Twin">
                        <i class="fas fa-play"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-warning" 
                            onclick="stopTwin('{{ twin_id }}', 'user')" 
                            title="Stop Twin">
                        <i class="fas fa-stop"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info" 
                            onclick="syncTwin('{{ twin_id }}', {}, 'user')" 
                            title="Sync Twin">
                        <i class="fas fa-sync"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" 
                            onclick="restartTwin('{{ twin_id }}', 'user')" 
                            title="Restart Twin">
                        <i class="fas fa-redo"></i>
                    </button>
                </div>
                
                <!-- Relationship Actions -->
                <div class="btn-group ms-1" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary" 
                            onclick="showRelationshipModal('{{ twin_id }}')" 
                            title="Manage Relationships">
                        <i class="fas fa-link"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info" 
                            onclick="showRelationships('{{ twin_id }}')" 
                            title="View Relationships">
                        <i class="fas fa-sitemap"></i>
                    </button>
                </div>
                
                <!-- Details Actions -->
                <div class="btn-group ms-1" role="group">
                    <button type="button" class="btn btn-sm btn-outline-dark" 
                            onclick="viewTwinDetails('{{ twin_id }}')" 
                            title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" 
                            onclick="editTwin('{{ twin_id }}')" 
                            title="Edit Twin">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </div>
        `;
    }

    generateTwinRow(twin) {
        const row = document.createElement('tr');
        row.setAttribute('data-twin-id', twin.twin_id);
        
        // Generate row content
        row.innerHTML = `
            <td>
                <code class="text-muted">${twin.twin_id.substring(0, 8)}...</code>
            </td>
            <td>
                <strong>${twin.name || 'Unnamed Twin'}</strong>
                <br>
                <small class="text-muted">${twin.description || 'No description'}</small>
            </td>
            <td>
                <span class="badge bg-info">${twin.twin_type || 'aasx'}</span>
            </td>
            <td>
                <span class="badge twin-status-badge ${this.getStatusBadgeClass(twin.lifecycle_status || 'unknown')}">
                    ${twin.lifecycle_status || 'unknown'}
                </span>
            </td>
            <td>
                <span class="twin-health-score ${this.getHealthScoreClass(twin.health_score || 0)}">
                    ${twin.health_score || 0}%
                </span>
            </td>
            <td>
                <span class="text-muted">${twin.owner || 'System'}</span>
            </td>
            <td>
                <span class="twin-last-sync text-muted">
                    ${twin.last_lifecycle_update ? new Date(twin.last_lifecycle_update).toLocaleString() : 'Never'}
                </span>
            </td>
            <td>
                ${this.generateActions(twin.twin_id)}
            </td>
        `;
        
        return row;
    }

    generateActions(twinId) {
        if (!this.actionTemplate) {
            return '<span class="text-muted">Loading...</span>';
        }
        
        return this.actionTemplate.replace(/\{\{ twin_id \}\}/g, twinId);
    }

    getStatusBadgeClass(status) {
        const statusClasses = {
            'running': 'bg-success',
            'stopped': 'bg-secondary',
            'syncing': 'bg-warning',
            'error': 'bg-danger',
            'starting': 'bg-info',
            'stopping': 'bg-warning',
            'unknown': 'bg-light text-dark'
        };
        return statusClasses[status] || 'bg-light text-dark';
    }

    getHealthScoreClass(score) {
        if (score >= 90) return 'text-success';
        if (score >= 75) return 'text-warning';
        if (score >= 60) return 'text-info';
        return 'text-danger';
    }

    updateTwinRow(twinId, updates) {
        const row = document.querySelector(`[data-twin-id="${twinId}"]`);
        if (!row) return;

        // Update status badge
        if (updates.lifecycle_status) {
            const statusBadge = row.querySelector('.twin-status-badge');
            if (statusBadge) {
                statusBadge.className = `badge twin-status-badge ${this.getStatusBadgeClass(updates.lifecycle_status)}`;
                statusBadge.textContent = updates.lifecycle_status;
            }
        }

        // Update health score
        if (updates.health_score !== undefined) {
            const healthScore = row.querySelector('.twin-health-score');
            if (healthScore) {
                healthScore.textContent = `${updates.health_score}%`;
                healthScore.className = `twin-health-score ${this.getHealthScoreClass(updates.health_score)}`;
            }
        }

        // Update last sync
        if (updates.last_lifecycle_update) {
            const lastSync = row.querySelector('.twin-last-sync');
            if (lastSync) {
                lastSync.textContent = new Date(updates.last_lifecycle_update).toLocaleString();
            }
        }
    }

    // Cleanup method
    cleanup() {
        this.actionTemplate = null;
        console.log('🧹 Twin Table Row Generator cleaned up');
    }
} 