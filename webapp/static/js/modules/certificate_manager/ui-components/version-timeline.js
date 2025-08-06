/**
 * Certificate Manager - Version Timeline UI Component
 * Handles version history, timeline display, and version comparison
 */

export class VersionTimeline {
    constructor() {
        this.currentCertificate = null;
        this.versions = [];
        this.selectedVersions = [];
    }

    /**
     * Initialize version timeline
     */
    async init() {
        console.log('📜 Initializing version timeline...');
        
        try {
            this.setupEventListeners();
            
            console.log('✅ Version timeline initialized');
            
        } catch (error) {
            console.error('❌ Error initializing version timeline:', error);
            this.showError('Failed to initialize version timeline');
        }
    }

    /**
     * Load version history
     */
    async loadVersionHistory(certificateId) {
        try {
            console.log('📜 Loading version history for certificate:', certificateId);
            
            this.setLoading(true);
            
            // Get certificate data
            const certificate = await this.getCertificateData(certificateId);
            this.currentCertificate = certificate;
            
            // Load version history
            this.versions = await this.getVersionHistory(certificateId);
            
            // Update timeline display
            this.updateTimeline();
            this.updateVersionStats();
            
            this.setLoading(false);
            
            console.log(`✅ Loaded ${this.versions.length} versions`);
            
        } catch (error) {
            console.error('❌ Error loading version history:', error);
            this.setLoading(false);
            this.showError('Failed to load version history');
        }
    }

    /**
     * Update timeline display
     */
    updateTimeline() {
        const timeline = document.getElementById('version-timeline');
        if (!timeline) return;
        
        timeline.innerHTML = `
            <div class="version-timeline">
                ${this.versions.map((version, index) => `
                    <div class="timeline-item ${version.status}" data-version="${version.version}">
                        <div class="timeline-marker">
                            <i class="fas ${this.getVersionIcon(version)}"></i>
                        </div>
                        <div class="timeline-content">
                            <div class="version-header">
                                <div class="version-number">v${version.version}</div>
                                <div class="version-date">${this.formatDate(version.created_at)}</div>
                                <div class="version-status">
                                    <span class="badge badge-${this.getStatusClass(version.status)}">
                                        ${version.status}
                                    </span>
                                </div>
                            </div>
                            <div class="version-description">${version.description}</div>
                            <div class="version-changes">
                                ${this.renderVersionChanges(version.changes)}
                            </div>
                            <div class="version-actions">
                                <button class="btn btn-sm btn-outline-primary" onclick="viewVersion('${version.version}')">
                                    <i class="fas fa-eye"></i> View
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="compareVersion('${version.version}')">
                                    <i class="fas fa-exchange-alt"></i> Compare
                                </button>
                                <input type="checkbox" class="version-select" value="${version.version}">
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Update version statistics
     */
    updateVersionStats() {
        const stats = document.getElementById('version-stats');
        if (!stats) return;
        
        const totalVersions = this.versions.length;
        const majorVersions = this.versions.filter(v => v.version.split('.')[1] === '0').length;
        const minorVersions = this.versions.filter(v => v.version.split('.')[1] !== '0').length;
        const latestVersion = this.versions[0]?.version || 'N/A';
        
        stats.innerHTML = `
            <div class="version-stats">
                <div class="stat-item">
                    <div class="stat-number">${totalVersions}</div>
                    <div class="stat-label">Total Versions</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${majorVersions}</div>
                    <div class="stat-label">Major Releases</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${minorVersions}</div>
                    <div class="stat-label">Minor Updates</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${latestVersion}</div>
                    <div class="stat-label">Latest Version</div>
                </div>
            </div>
        `;
    }

    /**
     * Render version changes
     */
    renderVersionChanges(changes) {
        if (!changes || changes.length === 0) {
            return '<div class="no-changes">No changes recorded</div>';
        }
        
        return `
            <div class="version-changes-list">
                ${changes.map(change => `
                    <div class="change-item ${change.type}">
                        <i class="fas ${this.getChangeIcon(change.type)}"></i>
                        <span class="change-text">${change.description}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Compare versions
     */
    async compareVersions(version1, version2) {
        try {
            console.log(`🔍 Comparing versions ${version1} and ${version2}`);
            
            const v1 = this.versions.find(v => v.version === version1);
            const v2 = this.versions.find(v => v.version === version2);
            
            if (!v1 || !v2) {
                throw new Error('One or both versions not found');
            }
            
            // Generate comparison
            const comparison = this.generateComparison(v1, v2);
            
            // Show comparison modal
            this.showComparisonModal(comparison);
            
        } catch (error) {
            console.error('❌ Error comparing versions:', error);
            this.showError('Failed to compare versions');
        }
    }

    /**
     * Generate comparison
     */
    generateComparison(v1, v2) {
        const comparison = {
            version1: v1,
            version2: v2,
            changes: {
                added: [],
                removed: [],
                modified: []
            },
            summary: {
                totalChanges: 0,
                sectionsChanged: 0,
                healthScoreChange: (v2.health_score || 0) - (v1.health_score || 0)
            }
        };
        
        // Compare sections
        const sections1 = v1.sections || {};
        const sections2 = v2.sections || {};
        
        // Find added sections
        for (const [key, section] of Object.entries(sections2)) {
            if (!sections1[key]) {
                comparison.changes.added.push({
                    type: 'section',
                    name: key,
                    description: `Added ${this.formatFieldLabel(key)} section`
                });
            }
        }
        
        // Find removed sections
        for (const [key, section] of Object.entries(sections1)) {
            if (!sections2[key]) {
                comparison.changes.removed.push({
                    type: 'section',
                    name: key,
                    description: `Removed ${this.formatFieldLabel(key)} section`
                });
            }
        }
        
        // Find modified sections
        for (const [key, section] of Object.entries(sections1)) {
            if (sections2[key] && JSON.stringify(section) !== JSON.stringify(sections2[key])) {
                comparison.changes.modified.push({
                    type: 'section',
                    name: key,
                    description: `Modified ${this.formatFieldLabel(key)} section`
                });
            }
        }
        
        comparison.summary.totalChanges = 
            comparison.changes.added.length + 
            comparison.changes.removed.length + 
            comparison.changes.modified.length;
        
        comparison.summary.sectionsChanged = 
            new Set([
                ...comparison.changes.added.map(c => c.name),
                ...comparison.changes.removed.map(c => c.name),
                ...comparison.changes.modified.map(c => c.name)
            ]).size;
        
        return comparison;
    }

    /**
     * Show comparison modal
     */
    showComparisonModal(comparison) {
        const modal = document.getElementById('versionComparisonModal');
        if (!modal) return;
        
        const modalBody = modal.querySelector('.modal-body');
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="version-comparison">
                    <div class="comparison-header">
                        <div class="version-info">
                            <h5>v${comparison.version1.version}</h5>
                            <span>${this.formatDate(comparison.version1.created_at)}</span>
                        </div>
                        <div class="comparison-arrow">
                            <i class="fas fa-arrow-right"></i>
                        </div>
                        <div class="version-info">
                            <h5>v${comparison.version2.version}</h5>
                            <span>${this.formatDate(comparison.version2.created_at)}</span>
                        </div>
                    </div>
                    
                    <div class="comparison-summary">
                        <div class="summary-item">
                            <span class="summary-label">Total Changes:</span>
                            <span class="summary-value">${comparison.summary.totalChanges}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Sections Changed:</span>
                            <span class="summary-value">${comparison.summary.sectionsChanged}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Health Score Change:</span>
                            <span class="summary-value ${comparison.summary.healthScoreChange >= 0 ? 'positive' : 'negative'}">
                                ${comparison.summary.healthScoreChange >= 0 ? '+' : ''}${comparison.summary.healthScoreChange}%
                            </span>
                        </div>
                    </div>
                    
                    <div class="comparison-changes">
                        <h6>Changes</h6>
                        ${this.renderComparisonChanges(comparison.changes)}
                    </div>
                </div>
            `;
        }
        
        // Show modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }

    /**
     * Render comparison changes
     */
    renderComparisonChanges(changes) {
        const allChanges = [
            ...changes.added.map(c => ({ ...c, type: 'added' })),
            ...changes.removed.map(c => ({ ...c, type: 'removed' })),
            ...changes.modified.map(c => ({ ...c, type: 'modified' }))
        ];
        
        if (allChanges.length === 0) {
            return '<div class="no-changes">No changes detected</div>';
        }
        
        return `
            <div class="changes-list">
                ${allChanges.map(change => `
                    <div class="change-item ${change.type}">
                        <i class="fas ${this.getChangeIcon(change.type)}"></i>
                        <span class="change-text">${change.description}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Get certificate data
     */
    async getCertificateData(certificateId) {
        // This would call the core module
        const core = window.CertificateManager?.modules?.core;
        if (core) {
            return await core.getCertificateById(certificateId);
        }
        
        // Fallback to mock data
        return this.getMockCertificate(certificateId);
    }

    /**
     * Get version history
     */
    async getVersionHistory(certificateId) {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return this.getMockVersionHistory(certificateId);
    }

    /**
     * Get version icon
     */
    getVersionIcon(version) {
        if (version.version.split('.')[1] === '0') {
            return 'fa-star'; // Major version
        } else if (version.version.split('.')[2] === '0') {
            return 'fa-circle'; // Minor version
        } else {
            return 'fa-dot-circle'; // Patch version
        }
    }

    /**
     * Get change icon
     */
    getChangeIcon(changeType) {
        const iconMap = {
            'added': 'fa-plus-circle',
            'removed': 'fa-minus-circle',
            'modified': 'fa-edit',
            'section': 'fa-folder'
        };
        return iconMap[changeType] || 'fa-circle';
    }

    /**
     * Get status class
     */
    getStatusClass(status) {
        const statusMap = {
            'active': 'success',
            'pending': 'warning',
            'completed': 'info',
            'error': 'danger',
            'in_progress': 'primary'
        };
        return statusMap[status] || 'secondary';
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        } catch (error) {
            return dateString;
        }
    }

    /**
     * Format field label
     */
    formatFieldLabel(key) {
        return key.split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Version selection
        document.addEventListener('change', (e) => {
            if (e.target.matches('.version-select')) {
                this.handleVersionSelection(e.target);
            }
        });
        
        // Compare selected versions
        const compareBtn = document.getElementById('compare-versions');
        if (compareBtn) {
            compareBtn.addEventListener('click', () => {
                this.compareSelectedVersions();
            });
        }
    }

    /**
     * Handle version selection
     */
    handleVersionSelection(checkbox) {
        const version = checkbox.value;
        
        if (checkbox.checked) {
            this.selectedVersions.push(version);
        } else {
            this.selectedVersions = this.selectedVersions.filter(v => v !== version);
        }
        
        // Update compare button state
        const compareBtn = document.getElementById('compare-versions');
        if (compareBtn) {
            compareBtn.disabled = this.selectedVersions.length !== 2;
        }
    }

    /**
     * Compare selected versions
     */
    compareSelectedVersions() {
        if (this.selectedVersions.length === 2) {
            this.compareVersions(this.selectedVersions[0], this.selectedVersions[1]);
        }
    }

    /**
     * Set loading state
     */
    setLoading(loading) {
        const loadingIndicator = document.getElementById('timeline-loading');
        if (loadingIndicator) {
            loadingIndicator.style.display = loading ? 'flex' : 'none';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error('❌ Error:', message);
        if (typeof showNotification === 'function') {
            showNotification(message, 'error');
        } else {
            alert('Error: ' + message);
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        console.log('✅ Success:', message);
        if (typeof showNotification === 'function') {
            showNotification(message, 'success');
        }
    }

    /**
     * Mock data methods
     */
    getMockCertificate(certificateId) {
        const certificates = [
            {
                certificate_id: 'CERT-001',
                twin_name: 'Additive Manufacturing Facility',
                project_name: 'AM Production Line',
                use_case_name: 'Quality Assurance',
                status: 'active',
                created_at: '2024-01-15T10:30:00Z',
                updated_at: '2024-01-15T14:45:00Z',
                version: '1.2.3',
                health_score: 95,
                verification_status: 'verified'
            }
        ];
        
        return certificates.find(cert => cert.certificate_id === certificateId) || certificates[0];
    }

    /**
     * Get mock version history
     */
    getMockVersionHistory(certificateId) {
        return [
            {
                version: '1.2.3',
                status: 'active',
                created_at: '2024-01-15T14:45:00Z',
                description: 'Final release with all modules completed',
                health_score: 95,
                changes: [
                    { type: 'added', description: 'Added Knowledge Graph integration' },
                    { type: 'modified', description: 'Enhanced Twin Registry synchronization' }
                ],
                sections: {
                    etl: { status: 'completed', score: 98 },
                    ai_rag: { status: 'completed', score: 92 },
                    physics: { status: 'completed', score: 89 },
                    twin_registry: { status: 'completed', score: 96 },
                    federated_learning: { status: 'completed', score: 91 },
                    knowledge_graph: { status: 'completed', score: 93 }
                }
            },
            {
                version: '1.2.0',
                status: 'completed',
                created_at: '2024-01-15T12:30:00Z',
                description: 'Added Twin Registry and Federated Learning modules',
                health_score: 87,
                changes: [
                    { type: 'added', description: 'Added Twin Registry module' },
                    { type: 'added', description: 'Added Federated Learning module' },
                    { type: 'modified', description: 'Enhanced ETL processing' }
                ],
                sections: {
                    etl: { status: 'completed', score: 95 },
                    ai_rag: { status: 'completed', score: 87 },
                    physics: { status: 'completed', score: 89 },
                    twin_registry: { status: 'completed', score: 92 },
                    federated_learning: { status: 'completed', score: 88 }
                }
            },
            {
                version: '1.1.0',
                status: 'completed',
                created_at: '2024-01-15T11:15:00Z',
                description: 'Enhanced ETL processing and AI/RAG analysis',
                health_score: 82,
                changes: [
                    { type: 'modified', description: 'Improved ETL processing' },
                    { type: 'added', description: 'Added AI/RAG analysis module' }
                ],
                sections: {
                    etl: { status: 'completed', score: 90 },
                    ai_rag: { status: 'completed', score: 85 },
                    physics: { status: 'completed', score: 89 }
                }
            },
            {
                version: '1.0.0',
                status: 'completed',
                created_at: '2024-01-15T10:30:00Z',
                description: 'Initial certificate creation with ETL and Physics modules',
                health_score: 75,
                changes: [
                    { type: 'added', description: 'Created initial certificate' },
                    { type: 'added', description: 'Added basic ETL processing' },
                    { type: 'added', description: 'Added Physics modeling' }
                ],
                sections: {
                    etl: { status: 'completed', score: 75 },
                    physics: { status: 'completed', score: 78 }
                }
            }
        ];
    }

    /**
     * Cleanup
     */
    destroy() {
        this.currentCertificate = null;
        this.versions = [];
        this.selectedVersions = [];
    }
}

// Export the class
export default VersionTimeline; 