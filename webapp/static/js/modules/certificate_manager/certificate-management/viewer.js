/**
 * Certificate Manager - Viewer Module
 * Handles certificate viewing, display, and interaction
 */

export class CertificateViewer {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.currentCertificate = null;
        this.sections = [];
        this.activeSection = null;
        this.zoomLevel = 1;
        this.isFullscreen = false;
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Certificate Viewer: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Certificate Viewer: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Certificate Viewer: Auth system ready event received');
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
                console.warn('⚠️ Certificate Viewer: Timeout waiting for auth system');
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
            console.log('🔐 Certificate Viewer: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Certificate Viewer: No auth manager available');
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
     * Clear sensitive data on logout
     */
    clearSensitiveData() {
        // Clear any cached data that might be user-specific
        this.currentCertificate = null;
        this.sections = [];
        this.activeSection = null;
        console.log('🧹 Certificate Viewer: Sensitive data cleared');
    }

    /**
     * Get authentication headers
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
     * Initialize viewer
     */
    async init() {
        console.log('👁️ Initializing certificate viewer...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.setupEventListeners();
            this.setupKeyboardShortcuts();
            
            console.log('✅ Certificate viewer initialized');
            
        } catch (error) {
            console.error('❌ Error initializing certificate viewer:', error);
            this.showError('Failed to initialize certificate viewer');
        }
    }

    /**
     * Load certificate for viewing
     */
    async loadCertificate(certificateId) {
        try {
            console.log('📋 Loading certificate for viewing:', certificateId);
            
            this.setLoading(true);
            
            // Load certificate data
            const certificate = await this.fetchCertificateData(certificateId);
            this.currentCertificate = certificate;
            
            // Load certificate sections
            this.sections = await this.loadCertificateSections(certificateId);
            
            // Update viewer content
            this.updateCertificateHeader();
            this.updateCertificateMetadata();
            this.updateCertificateSections();
            this.updateCertificateValidation();
            
            this.setLoading(false);
            
            console.log('✅ Certificate loaded for viewing');
            
        } catch (error) {
            console.error('❌ Error loading certificate:', error);
            this.setLoading(false);
            this.showError('Failed to load certificate');
        }
    }

    /**
     * Fetch certificate data
     */
    async fetchCertificateData(certificateId) {
        try {
            // This would call the core module
            const core = window.CertificateManager?.modules?.core;
            if (core) {
                return await core.getCertificateById(certificateId);
            }
            
            // Fallback to mock data
            return this.getMockCertificate(certificateId);
            
        } catch (error) {
            console.error('Error fetching certificate data:', error);
            throw error;
        }
    }

    /**
     * Load certificate sections
     */
    async loadCertificateSections(certificateId) {
        try {
            // Simulate loading sections
            await new Promise(resolve => setTimeout(resolve, 500));
            
            return [
                {
                    id: 'etl',
                    name: 'ETL Processing',
                    icon: 'fa-database',
                    status: 'completed',
                    data: {
                        processed_files: 15,
                        data_quality_score: 98,
                        processing_time: '2.3s',
                        errors: 0,
                        warnings: 2
                    }
                },
                {
                    id: 'ai_rag',
                    name: 'AI/RAG Analysis',
                    icon: 'fa-brain',
                    status: 'completed',
                    data: {
                        insights_generated: 8,
                        confidence_score: 92,
                        processing_time: '1.8s',
                        queries_processed: 12
                    }
                },
                {
                    id: 'physics',
                    name: 'Physics Modeling',
                    icon: 'fa-atom',
                    status: 'completed',
                    data: {
                        simulations_run: 3,
                        accuracy_score: 89,
                        processing_time: '45.2s',
                        models_used: ['thermal', 'structural']
                    }
                },
                {
                    id: 'twin_registry',
                    name: 'Twin Registry',
                    icon: 'fa-registered',
                    status: 'completed',
                    data: {
                        twins_registered: 5,
                        registry_health: 96,
                        last_sync: '2025-01-20T14:30:00Z',
                        sync_status: 'synchronized',
                        metadata_completeness: 94
                    }
                },
                {
                    id: 'federated_learning',
                    name: 'Federated Learning',
                    icon: 'fa-network-wired',
                    status: 'completed',
                    data: {
                        models_trained: 3,
                        federated_rounds: 15,
                        global_accuracy: 91,
                        participants: 8,
                        privacy_score: 95
                    }
                },
                {
                    id: 'knowledge_graph',
                    name: 'Knowledge Graph',
                    icon: 'fa-project-diagram',
                    status: 'completed',
                    data: {
                        nodes_created: 156,
                        relationships_found: 342,
                        graph_density: 0.78,
                        processing_time: '3.1s'
                    }
                }
            ];
            
        } catch (error) {
            console.error('Error loading certificate sections:', error);
            return [];
        }
    }

    /**
     * Update certificate header
     */
    updateCertificateHeader() {
        const header = document.getElementById('certificate-header');
        if (!header || !this.currentCertificate) return;
        
        header.innerHTML = `
            <div class="certificate-title">
                <h2>${this.currentCertificate.twin_name}</h2>
                <span class="certificate-id">${this.currentCertificate.certificate_id}</span>
            </div>
            <div class="certificate-status">
                <span class="badge badge-${this.getStatusClass(this.currentCertificate.status)}">
                    ${this.currentCertificate.status}
                </span>
                <span class="badge badge-${this.currentCertificate.verification_status === 'verified' ? 'success' : 'warning'}">
                    ${this.currentCertificate.verification_status}
                </span>
            </div>
        `;
    }

    /**
     * Update certificate metadata
     */
    updateCertificateMetadata() {
        const metadata = document.getElementById('certificate-metadata');
        if (!metadata || !this.currentCertificate) return;
        
        metadata.innerHTML = `
            <div class="metadata-grid">
                <div class="metadata-item">
                    <label>Project</label>
                    <span>${this.currentCertificate.project_name}</span>
                </div>
                <div class="metadata-item">
                    <label>Use Case</label>
                    <span>${this.currentCertificate.use_case_name}</span>
                </div>
                <div class="metadata-item">
                    <label>Created</label>
                    <span>${this.formatDate(this.currentCertificate.created_at)}</span>
                </div>
                <div class="metadata-item">
                    <label>Updated</label>
                    <span>${this.formatDate(this.currentCertificate.updated_at)}</span>
                </div>
                <div class="metadata-item">
                    <label>Version</label>
                    <span>${this.currentCertificate.version}</span>
                </div>
                <div class="metadata-item">
                    <label>Health Score</label>
                    <span>${this.currentCertificate.health_score}%</span>
                </div>
            </div>
        `;
    }

    /**
     * Update certificate sections
     */
    updateCertificateSections() {
        const sectionsContainer = document.getElementById('certificate-sections');
        if (!sectionsContainer) return;
        
        sectionsContainer.innerHTML = this.sections.map(section => 
            this.renderSection(section)
        ).join('');
    }

    /**
     * Render section
     */
    renderSection(section) {
        return `
            <div class="certificate-section" data-section="${section.id}">
                <div class="section-header">
                    <i class="fas ${section.icon}"></i>
                    <h4>${section.name}</h4>
                    <span class="badge badge-${this.getStatusClass(section.status)}">
                        ${section.status}
                    </span>
                </div>
                <div class="section-content">
                    ${this.renderSectionData(section.data)}
                </div>
            </div>
        `;
    }

    /**
     * Render section data
     */
    renderSectionData(data) {
        return Object.entries(data).map(([key, value]) => `
            <div class="data-item">
                <label>${this.formatFieldLabel(key)}</label>
                <span>${value}</span>
            </div>
        `).join('');
    }

    /**
     * Update certificate validation
     */
    updateCertificateValidation() {
        const validation = document.getElementById('certificate-validation');
        if (!validation || !this.currentCertificate) return;
        
        const isVerified = this.currentCertificate.verification_status === 'verified';
        
        validation.innerHTML = `
            <div class="validation-status ${isVerified ? 'verified' : 'pending'}">
                <i class="fas ${isVerified ? 'fa-check-circle' : 'fa-clock'}"></i>
                <span>${isVerified ? 'Certificate Verified' : 'Verification Pending'}</span>
            </div>
            <div class="validation-details">
                <div class="validation-item">
                    <label>Digital Signature</label>
                    <span class="${isVerified ? 'valid' : 'pending'}">
                        ${isVerified ? 'Valid' : 'Pending'}
                    </span>
                </div>
                <div class="validation-item">
                    <label>Data Integrity</label>
                    <span class="${isVerified ? 'valid' : 'pending'}">
                        ${isVerified ? 'Verified' : 'Checking'}
                    </span>
                </div>
                <div class="validation-item">
                    <label>Timestamp</label>
                    <span>${this.formatDate(this.currentCertificate.updated_at)}</span>
                </div>
            </div>
        `;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Print button
        const printBtn = document.getElementById('print-certificate');
        if (printBtn) {
            printBtn.addEventListener('click', () => this.printCertificate());
        }
        
        // Share button
        const shareBtn = document.getElementById('share-certificate');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareCertificate());
        }
        
        // Export button
        const exportBtn = document.getElementById('export-certificate');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportCurrentCertificate());
        }
        
        // Zoom controls
        const zoomInBtn = document.getElementById('zoom-in');
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => this.zoomIn());
        }
        
        const zoomOutBtn = document.getElementById('zoom-out');
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => this.zoomOut());
        }
        
        const resetZoomBtn = document.getElementById('reset-zoom');
        if (resetZoomBtn) {
            resetZoomBtn.addEventListener('click', () => this.resetZoom());
        }
        
        // Fullscreen button
        const fullscreenBtn = document.getElementById('toggle-fullscreen');
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        }
        
        // Section navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('.section-header')) {
                const section = e.target.closest('.certificate-section');
                this.toggleSection(section);
            }
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        this.handleKeydown = (e) => {
            // Only handle shortcuts when viewer is active
            const viewer = document.getElementById('certificateViewerModal');
            if (!viewer || !viewer.classList.contains('show')) return;
            
            switch (e.key) {
                case 'Escape':
                    // Close modal
                    const closeBtn = viewer.querySelector('.btn-close');
                    if (closeBtn) closeBtn.click();
                    break;
                case 'p':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.printCertificate();
                    }
                    break;
                case 's':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.shareCertificate();
                    }
                    break;
                case 'e':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.exportCurrentCertificate();
                    }
                    break;
                case 'f':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.toggleFullscreen();
                    }
                    break;
                case '+':
                case '=':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.zoomIn();
                    }
                    break;
                case '-':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.zoomOut();
                    }
                    break;
                case '0':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.resetZoom();
                    }
                    break;
            }
        };
        
        document.addEventListener('keydown', this.handleKeydown);
    }

    /**
     * Print certificate
     */
    printCertificate() {
        console.log('🖨️ Printing certificate...');
        
        const printWindow = window.open('', '_blank');
        const certificateContent = document.getElementById('certificate-content');
        
        if (printWindow && certificateContent) {
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Certificate - ${this.currentCertificate?.certificate_id}</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 20px; }
                            .certificate-header { text-align: center; margin-bottom: 30px; }
                            .certificate-section { margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; }
                            .section-header { font-weight: bold; margin-bottom: 10px; }
                            .data-item { margin-bottom: 5px; }
                            .data-item label { font-weight: bold; }
                        </style>
                    </head>
                    <body>
                        ${certificateContent.innerHTML}
                    </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
        } else {
            window.print();
        }
    }

    /**
     * Share certificate
     */
    shareCertificate() {
        console.log('📤 Sharing certificate...');
        
        if (navigator.share) {
            navigator.share({
                title: 'Certificate',
                text: `Check out this certificate: ${this.currentCertificate?.twin_name}`,
                url: window.location.href
            }).catch(error => {
                console.log('Error sharing:', error);
                this.copyToClipboard();
            });
        } else {
            this.copyToClipboard();
        }
    }

    /**
     * Copy to clipboard
     */
    copyToClipboard() {
        const url = window.location.href;
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(() => {
                this.showSuccess('Certificate link copied to clipboard');
            }).catch(() => {
                this.fallbackCopyToClipboard(url);
            });
        } else {
            this.fallbackCopyToClipboard(url);
        }
    }

    /**
     * Fallback copy to clipboard
     */
    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showSuccess('Certificate link copied to clipboard');
        } catch (err) {
            this.showError('Failed to copy link');
        }
        
        document.body.removeChild(textArea);
    }

    /**
     * Export current certificate
     */
    exportCurrentCertificate() {
        console.log('📤 Exporting current certificate...');
        
        // This would trigger the export modal
        const exportModal = document.getElementById('exportOptionsModal');
        if (exportModal) {
            const modal = new bootstrap.Modal(exportModal);
            modal.show();
        }
    }

    /**
     * Zoom controls
     */
    zoomIn() {
        this.zoomLevel = Math.min(this.zoomLevel * 1.2, 3);
        this.applyZoom();
    }

    zoomOut() {
        this.zoomLevel = Math.max(this.zoomLevel / 1.2, 0.5);
        this.applyZoom();
    }

    resetZoom() {
        this.zoomLevel = 1;
        this.applyZoom();
    }

    applyZoom() {
        const content = document.getElementById('certificate-content');
        if (content) {
            content.style.transform = `scale(${this.zoomLevel})`;
            content.style.transformOrigin = 'top left';
        }
        
        // Update zoom display
        const zoomDisplay = document.getElementById('zoom-level');
        if (zoomDisplay) {
            zoomDisplay.textContent = `${Math.round(this.zoomLevel * 100)}%`;
        }
    }

    /**
     * Toggle fullscreen
     */
    toggleFullscreen() {
        const viewer = document.getElementById('certificateViewerModal');
        if (!viewer) return;
        
        if (!this.isFullscreen) {
            viewer.classList.add('fullscreen');
            this.isFullscreen = true;
        } else {
            viewer.classList.remove('fullscreen');
            this.isFullscreen = false;
        }
    }

    /**
     * Set loading state
     */
    setLoading(loading) {
        const loadingIndicator = document.getElementById('viewer-loading');
        if (loadingIndicator) {
            loadingIndicator.style.display = loading ? 'flex' : 'none';
        }
    }

    /**
     * Get status class
     */
    getStatusClass(status) {
        const statusMap = {
            'completed': 'success',
            'active': 'primary',
            'pending': 'warning',
            'error': 'danger',
            'in_progress': 'info'
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

    formatFieldLabel(key) {
        return key.split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    showError(message) {
        console.error('❌ Error:', message);
        if (typeof showNotification === 'function') {
            showNotification(message, 'error');
        } else {
            alert('Error: ' + message);
        }
    }

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
                sections_count: 4,
                version: '1.2.3',
                health_score: 95,
                verification_status: 'verified'
            },
            {
                certificate_id: 'CERT-002',
                twin_name: 'Hydrogen Filling Station',
                project_name: 'H2 Infrastructure',
                use_case_name: 'Safety Compliance',
                status: 'pending',
                created_at: '2024-01-10T09:15:00Z',
                updated_at: '2024-01-10T09:15:00Z',
                sections_count: 3,
                version: '1.1.0',
                health_score: 78,
                verification_status: 'pending'
            },
            {
                certificate_id: 'CERT-003',
                twin_name: 'Servo DC Motor Assembly',
                project_name: 'Motor Production',
                use_case_name: 'Performance Testing',
                status: 'completed',
                created_at: '2024-01-05T11:20:00Z',
                updated_at: '2024-01-05T16:30:00Z',
                sections_count: 5,
                version: '1.0.0',
                health_score: 92,
                verification_status: 'verified'
            }
        ];
        
        return certificates.find(cert => cert.certificate_id === certificateId) || certificates[0];
    }

    /**
     * Cleanup
     */
    destroy() {
        // Remove event listeners
        document.removeEventListener('keydown', this.handleKeydown);
        
        // Reset state
        this.currentCertificate = null;
        this.sections = [];
        this.zoomLevel = 1;
        this.isFullscreen = false;
    }
}

// Export the class
export default CertificateViewer; 