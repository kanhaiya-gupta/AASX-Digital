/**
 * Certificate Manager - Status Indicator UI Component
 * Handles status display, health indicators, and validation status
 */

export class StatusIndicator {
    constructor() {
        this.currentCertificate = null;
        this.updateInterval = null;
    }

    /**
     * Initialize status indicator
     */
    async init() {
        console.log('📊 Initializing status indicator...');
        
        try {
            this.setupEventListeners();
            
            console.log('✅ Status indicator initialized');
            
        } catch (error) {
            console.error('❌ Error initializing status indicator:', error);
            this.showError('Failed to initialize status indicator');
        }
    }

    /**
     * Update status display
     */
    updateStatus(certificateId) {
        console.log('📊 Updating status for certificate:', certificateId);
        
        try {
            // Get certificate data
            const certificate = this.getCertificateData(certificateId);
            this.currentCertificate = certificate;
            
            // Update status elements
            this.updateStatusOverview();
            this.updateHealthIndicator();
            this.updateValidationStatus();
            this.updateSectionStatus();
            this.updateTimeline();
            
            console.log('✅ Status updated');
            
        } catch (error) {
            console.error('❌ Error updating status:', error);
        }
    }

    /**
     * Update status overview
     */
    updateStatusOverview() {
        const overview = document.getElementById('status-overview');
        if (!overview || !this.currentCertificate) return;
        
        overview.innerHTML = `
            <div class="status-summary">
                <div class="status-item">
                    <div class="status-label">Overall Status</div>
                    <div class="status-value">
                        <span class="badge badge-${this.getStatusClass(this.currentCertificate.status)}">
                            ${this.currentCertificate.status}
                        </span>
                    </div>
                </div>
                <div class="status-item">
                    <div class="status-label">Health Score</div>
                    <div class="status-value">
                        <div class="health-score">
                            <div class="progress">
                                <div class="progress-bar bg-${this.getHealthScoreClass(this.currentCertificate.health_score)}" 
                                     style="width: ${this.currentCertificate.health_score}%"></div>
                            </div>
                            <span class="score-text">${this.currentCertificate.health_score}%</span>
                        </div>
                    </div>
                </div>
                <div class="status-item">
                    <div class="status-label">Verification</div>
                    <div class="status-value">
                        <span class="badge badge-${this.currentCertificate.verification_status === 'verified' ? 'success' : 'warning'}">
                            ${this.currentCertificate.verification_status}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Update health indicator
     */
    updateHealthIndicator() {
        const healthIndicator = document.getElementById('health-indicator');
        if (!healthIndicator || !this.currentCertificate) return;
        
        const score = this.currentCertificate.health_score;
        const status = this.getHealthStatus(score);
        
        healthIndicator.innerHTML = `
            <div class="health-indicator ${status.class}">
                <div class="health-icon">
                    <i class="fas ${status.icon}"></i>
                </div>
                <div class="health-info">
                    <div class="health-score">${score}%</div>
                    <div class="health-status">${status.text}</div>
                </div>
                <div class="health-details">
                    <div class="health-metric">
                        <span class="metric-label">Data Quality</span>
                        <span class="metric-value">${Math.min(score + 5, 100)}%</span>
                    </div>
                    <div class="health-metric">
                        <span class="metric-label">Completeness</span>
                        <span class="metric-value">${Math.min(score + 3, 100)}%</span>
                    </div>
                    <div class="health-metric">
                        <span class="metric-label">Accuracy</span>
                        <span class="metric-value">${Math.min(score + 2, 100)}%</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Update validation status
     */
    updateValidationStatus() {
        const validationStatus = document.getElementById('validation-status');
        if (!validationStatus || !this.currentCertificate) return;
        
        const isVerified = this.currentCertificate.verification_status === 'verified';
        
        validationStatus.innerHTML = `
            <div class="validation-status ${isVerified ? 'verified' : 'pending'}">
                <div class="validation-header">
                    <i class="fas ${isVerified ? 'fa-check-circle' : 'fa-clock'}"></i>
                    <span>Digital Certificate Validation</span>
                </div>
                <div class="validation-details">
                    <div class="validation-item">
                        <span class="validation-label">Digital Signature</span>
                        <span class="validation-value ${isVerified ? 'valid' : 'pending'}">
                            <i class="fas ${isVerified ? 'fa-check' : 'fa-clock'}"></i>
                            ${isVerified ? 'Valid' : 'Pending'}
                        </span>
                    </div>
                    <div class="validation-item">
                        <span class="validation-label">Data Integrity</span>
                        <span class="validation-value ${isVerified ? 'valid' : 'pending'}">
                            <i class="fas ${isVerified ? 'fa-check' : 'fa-clock'}"></i>
                            ${isVerified ? 'Verified' : 'Checking'}
                        </span>
                    </div>
                    <div class="validation-item">
                        <span class="validation-label">Timestamp</span>
                        <span class="validation-value">
                            ${this.formatDate(this.currentCertificate.updated_at)}
                        </span>
                    </div>
                    <div class="validation-item">
                        <span class="validation-label">Certificate ID</span>
                        <span class="validation-value">${this.currentCertificate.certificate_id}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Update section status
     */
    updateSectionStatus() {
        const sectionStatus = document.getElementById('section-status');
        if (!sectionStatus || !this.currentCertificate) return;
        
        const sections = this.currentCertificate.sections || {};
        
        sectionStatus.innerHTML = `
            <div class="section-status">
                <h4>Module Status</h4>
                <div class="section-grid">
                    ${Object.entries(sections).map(([key, section]) => `
                        <div class="section-item">
                            <div class="section-header">
                                <i class="fas ${this.getSectionIcon(key)}"></i>
                                <span>${this.formatFieldLabel(key)}</span>
                            </div>
                            <div class="section-status-badge">
                                <span class="badge badge-${this.getStatusClass(section.status)}">
                                    ${section.status}
                                </span>
                            </div>
                            <div class="section-score">
                                <div class="score-bar">
                                    <div class="score-fill" style="width: ${section.score || 0}%"></div>
                                </div>
                                <span class="score-text">${section.score || 0}%</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Update timeline
     */
    updateTimeline() {
        const timeline = document.getElementById('status-timeline');
        if (!timeline || !this.currentCertificate) return;
        
        const events = this.generateTimelineEvents();
        
        timeline.innerHTML = `
            <div class="status-timeline">
                <h4>Status Timeline</h4>
                <div class="timeline">
                    ${events.map(event => `
                        <div class="timeline-item ${event.status}">
                            <div class="timeline-marker">
                                <i class="fas ${event.icon}"></i>
                            </div>
                            <div class="timeline-content">
                                <div class="timeline-title">${event.title}</div>
                                <div class="timeline-time">${event.time}</div>
                                <div class="timeline-description">${event.description}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Generate timeline events
     */
    generateTimelineEvents() {
        const events = [
            {
                title: 'Certificate Created',
                time: this.formatDate(this.currentCertificate.created_at),
                description: 'Initial certificate record created',
                status: 'completed',
                icon: 'fa-plus-circle'
            },
            {
                title: 'ETL Processing',
                time: this.formatDate(this.currentCertificate.created_at),
                description: 'Data extraction and transformation completed',
                status: 'completed',
                icon: 'fa-database'
            },
            {
                title: 'AI/RAG Analysis',
                time: this.formatDate(this.currentCertificate.updated_at),
                description: 'AI analysis and insights generated',
                status: 'completed',
                icon: 'fa-brain'
            },
            {
                title: 'Physics Modeling',
                time: this.formatDate(this.currentCertificate.updated_at),
                description: 'Physics simulations completed',
                status: 'completed',
                icon: 'fa-atom'
            },
            {
                title: 'Certificate Verified',
                time: this.formatDate(this.currentCertificate.updated_at),
                description: 'Digital signature and validation completed',
                status: this.currentCertificate.verification_status === 'verified' ? 'completed' : 'pending',
                icon: this.currentCertificate.verification_status === 'verified' ? 'fa-check-circle' : 'fa-clock'
            }
        ];
        
        return events;
    }

    /**
     * Get certificate data
     */
    getCertificateData(certificateId) {
        // This would call the core module
        const core = window.CertificateManager?.modules?.core;
        if (core) {
            return core.getCertificateById(certificateId);
        }
        
        // Fallback to mock data
        return this.getMockCertificate(certificateId);
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
     * Get health score class
     */
    getHealthScoreClass(score) {
        if (score >= 90) return 'success';
        if (score >= 70) return 'warning';
        return 'danger';
    }

    /**
     * Get health status
     */
    getHealthStatus(score) {
        if (score >= 90) {
            return { text: 'Excellent', class: 'excellent', icon: 'fa-heart' };
        } else if (score >= 70) {
            return { text: 'Good', class: 'good', icon: 'fa-thumbs-up' };
        } else if (score >= 50) {
            return { text: 'Fair', class: 'fair', icon: 'fa-exclamation-triangle' };
        } else {
            return { text: 'Poor', class: 'poor', icon: 'fa-times-circle' };
        }
    }

    /**
     * Get section icon
     */
    getSectionIcon(section) {
        const iconMap = {
            'etl': 'fa-database',
            'ai_rag': 'fa-brain',
            'physics': 'fa-atom',
            'twin_registry': 'fa-registered',
            'federated_learning': 'fa-network-wired',
            'knowledge_graph': 'fa-project-diagram'
        };
        return iconMap[section] || 'fa-cog';
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
        // Refresh button
        const refreshBtn = document.getElementById('refresh-status');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                if (this.currentCertificate) {
                    this.updateStatus(this.currentCertificate.certificate_id);
                }
            });
        }
        
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }

    /**
     * Start auto refresh
     */
    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear existing interval
        
        this.updateInterval = setInterval(() => {
            if (this.currentCertificate) {
                this.updateStatus(this.currentCertificate.certificate_id);
            }
        }, 30000); // Refresh every 30 seconds
        
        console.log('🔄 Auto-refresh started');
    }

    /**
     * Stop auto refresh
     */
    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('⏹️ Auto-refresh stopped');
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
                verification_status: 'verified',
                sections: {
                    etl: { status: 'completed', score: 98 },
                    ai_rag: { status: 'completed', score: 92 },
                    physics: { status: 'completed', score: 89 }
                }
            }
        ];
        
        return certificates.find(cert => cert.certificate_id === certificateId) || certificates[0];
    }

    /**
     * Cleanup
     */
    destroy() {
        this.stopAutoRefresh();
        this.currentCertificate = null;
    }
}

// Export the class
export default StatusIndicator; 