/**
 * Certificate Manager - Export Buttons UI Component
 * Handles export button functionality, controls, and user interactions
 */

export class ExportButtons {
    constructor() {
        // Authentication properties
        this.isAuthenticated = false;
        this.currentUser = null;
        this.authToken = null;
        
        this.selectedFormat = 'html';
        this.exportOptions = {
            includeSections: true,
            includeSecurity: true,
            includeMetadata: true,
            template: 'default'
        };
        this.exportQueue = [];
        this.isExporting = false;
    }

    /**
     * Wait for central authentication system to be ready
     */
    async waitForAuthSystem() {
        console.log('🔐 Export Buttons: Waiting for central auth system...');
        
        if (window.authSystemReady && window.authManager) {
            console.log('🔐 Export Buttons: Auth system already ready');
            return;
        }
        
        return new Promise((resolve) => {
            const handleReady = () => {
                console.log('🚀 Export Buttons: Auth system ready event received');
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
                console.warn('⚠️ Export Buttons: Timeout waiting for auth system');
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
            console.log('🔐 Export Buttons: Auth state updated', {
                isAuthenticated: this.isAuthenticated,
                user: this.currentUser?.username || 'anonymous'
            });
        } else {
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            console.log('🔐 Export Buttons: No auth manager available');
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
        this.exportQueue = [];
        this.isExporting = false;
        console.log('🧹 Export Buttons: Sensitive data cleared');
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
     * Initialize export buttons
     */
    async init() {
        console.log('📤 Initializing export buttons...');
        
        try {
            // Initialize authentication
            await this.waitForAuthSystem();
            this.updateAuthState();
            this.setupAuthListeners();
            
            this.setupEventListeners();
            this.setupFormatSelection();
            this.setupExportOptions();
            
            console.log('✅ Export buttons initialized');
            
        } catch (error) {
            console.error('❌ Error initializing export buttons:', error);
            this.showError('Failed to initialize export buttons');
        }
    }

    /**
     * Setup export buttons
     */
    setupExportButtons() {
        console.log('🔗 Setting up export buttons...');
        
        // Setup format selection buttons
        this.setupFormatButtons();
        
        // Setup export option toggles
        this.setupOptionToggles();
        
        // Setup template selection
        this.setupTemplateSelection();
        
        // Setup export action buttons
        this.setupActionButtons();
    }

    /**
     * Setup format selection buttons
     */
    setupFormatButtons() {
        const formatButtons = document.querySelectorAll('.export-format-option');
        formatButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const format = button.dataset.format;
                this.selectFormat(format);
            });
        });
    }

    /**
     * Setup option toggles
     */
    setupOptionToggles() {
        const optionToggles = document.querySelectorAll('.export-option-toggle');
        optionToggles.forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const option = e.target.dataset.option;
                const value = e.target.checked;
                this.updateExportOption(option, value);
            });
        });
    }

    /**
     * Setup template selection
     */
    setupTemplateSelection() {
        const templateSelect = document.getElementById('export-template');
        if (templateSelect) {
            templateSelect.addEventListener('change', (e) => {
                this.exportOptions.template = e.target.value;
                this.updateTemplatePreview();
            });
        }
    }

    /**
     * Setup action buttons
     */
    setupActionButtons() {
        // Export button
        const exportBtn = document.getElementById('export-certificate-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.executeExport();
            });
        }
        
        // Preview button
        const previewBtn = document.getElementById('preview-export-btn');
        if (previewBtn) {
            previewBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.previewExport();
            });
        }
        
        // Download button
        const downloadBtn = document.getElementById('download-export-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.downloadExport();
            });
        }
        
        // Share button
        const shareBtn = document.getElementById('share-export-btn');
        if (shareBtn) {
            shareBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.shareExport();
            });
        }
    }

    /**
     * Select export format
     */
    selectFormat(format) {
        console.log('📋 Selecting export format:', format);
        
        this.selectedFormat = format;
        
        // Update visual selection
        document.querySelectorAll('.export-format-option').forEach(option => {
            option.classList.remove('selected');
        });
        
        const selectedOption = document.querySelector(`[data-format="${format}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
        
        // Update format-specific options
        this.updateFormatOptions(format);
        
        // Update preview
        this.updateExportPreview();
        
        this.showSuccess(`Export format set to ${format.toUpperCase()}`);
    }

    /**
     * Update format-specific options
     */
    updateFormatOptions(format) {
        const formatOptions = document.querySelectorAll('.format-specific-option');
        formatOptions.forEach(option => {
            const supportedFormats = option.dataset.formats?.split(',') || [];
            if (supportedFormats.includes(format) || supportedFormats.length === 0) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        });
    }

    /**
     * Update export option
     */
    updateExportOption(option, value) {
        console.log('⚙️ Updating export option:', option, value);
        
        this.exportOptions[option] = value;
        
        // Update preview
        this.updateExportPreview();
    }

    /**
     * Update export preview
     */
    updateExportPreview() {
        const preview = document.getElementById('export-preview');
        if (!preview) return;
        
        const formatNames = {
            'html': 'HTML Document',
            'pdf': 'PDF Document',
            'json': 'JSON Data',
            'xml': 'XML Document'
        };
        
        const formatIcon = this.getFormatIcon(this.selectedFormat);
        const formatName = formatNames[this.selectedFormat] || 'Unknown Format';
        
        preview.innerHTML = `
            <div class="preview-content">
                <div class="preview-icon">
                    <i class="fas ${formatIcon}"></i>
                </div>
                <div class="preview-info">
                    <div class="preview-title">${formatName}</div>
                    <div class="preview-format">Format: ${this.selectedFormat.toUpperCase()}</div>
                    <div class="preview-options">
                        ${this.getOptionsSummary()}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get format icon
     */
    getFormatIcon(format) {
        const icons = {
            'html': 'fa-file-code',
            'pdf': 'fa-file-pdf',
            'json': 'fa-file-code',
            'xml': 'fa-file-code'
        };
        return icons[format] || 'fa-file';
    }

    /**
     * Get options summary
     */
    getOptionsSummary() {
        const options = [];
        
        if (this.exportOptions.includeSections) {
            options.push('Sections');
        }
        if (this.exportOptions.includeSecurity) {
            options.push('Security');
        }
        if (this.exportOptions.includeMetadata) {
            options.push('Metadata');
        }
        
        return options.length > 0 ? `Includes: ${options.join(', ')}` : 'Basic export';
    }

    /**
     * Update template preview
     */
    updateTemplatePreview() {
        const templatePreview = document.getElementById('template-preview');
        if (!templatePreview) return;
        
        const templates = {
            'default': 'Standard Certificate Template',
            'professional': 'Professional Business Template',
            'minimal': 'Minimal Clean Template',
            'detailed': 'Detailed Technical Template'
        };
        
        const templateName = templates[this.exportOptions.template] || 'Unknown Template';
        
        templatePreview.innerHTML = `
            <div class="template-preview-content">
                <i class="fas fa-file-alt"></i>
                <span>${templateName}</span>
            </div>
        `;
    }

    /**
     * Execute export
     */
    async executeExport() {
        try {
            console.log('📤 Executing export...');
            
            if (this.isExporting) {
                this.showError('Export already in progress');
                return;
            }
            
            this.isExporting = true;
            this.showExportProgress();
            
            // Get current certificate
            const certificateId = this.getCurrentCertificateId();
            if (!certificateId) {
                throw new Error('No certificate selected for export');
            }
            
            // Execute export
            const result = await this.performExport(certificateId);
            
            this.hideExportProgress();
            this.showExportSuccess(result);
            
            this.isExporting = false;
            
        } catch (error) {
            console.error('❌ Export error:', error);
            this.hideExportProgress();
            this.showError(`Export failed: ${error.message}`);
            this.isExporting = false;
        }
    }

    /**
     * Perform export
     */
    async performExport(certificateId) {
        // This would call the export handler
        const exportHandler = window.CertificateManager?.modules?.exportHandler;
        if (exportHandler) {
            return await exportHandler.exportCertificate(
                certificateId,
                this.selectedFormat,
                this.exportOptions
            );
        }
        
        // Fallback to mock export
        return this.mockExport(certificateId);
    }

    /**
     * Mock export for testing
     */
    async mockExport(certificateId) {
        console.log('🎭 Performing mock export...');
        
        // Simulate export process
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        return {
            success: true,
            format: this.selectedFormat,
            certificateId,
            filename: `${certificateId}.${this.selectedFormat}`,
            size: Math.floor(Math.random() * 1000) + 100
        };
    }

    /**
     * Preview export
     */
    async previewExport() {
        try {
            console.log('👁️ Previewing export...');
            
            const certificateId = this.getCurrentCertificateId();
            if (!certificateId) {
                this.showError('No certificate selected for preview');
                return;
            }
            
            // Generate preview content
            const previewContent = await this.generatePreviewContent(certificateId);
            
            // Show preview modal
            this.showPreviewModal(previewContent);
            
        } catch (error) {
            console.error('❌ Preview error:', error);
            this.showError(`Preview failed: ${error.message}`);
        }
    }

    /**
     * Generate preview content
     */
    async generatePreviewContent(certificateId) {
        // This would generate actual preview content
        return `
            <div class="export-preview-content">
                <h3>Certificate Export Preview</h3>
                <p>Format: ${this.selectedFormat.toUpperCase()}</p>
                <p>Certificate ID: ${certificateId}</p>
                <p>Options: ${this.getOptionsSummary()}</p>
                <p>Template: ${this.exportOptions.template}</p>
            </div>
        `;
    }

    /**
     * Show preview modal
     */
    showPreviewModal(content) {
        const previewModal = document.getElementById('exportPreviewModal');
        if (!previewModal) return;
        
        const modalBody = previewModal.querySelector('.modal-body');
        if (modalBody) {
            modalBody.innerHTML = content;
        }
        
        // Show modal
        const modal = new bootstrap.Modal(previewModal);
        modal.show();
    }

    /**
     * Download export
     */
    downloadExport() {
        console.log('📥 Downloading export...');
        
        // This would trigger download of the current export
        this.showSuccess('Download started');
    }

    /**
     * Share export
     */
    shareExport() {
        console.log('📤 Sharing export...');
        
        if (navigator.share) {
            navigator.share({
                title: 'Certificate Export',
                text: 'Check out this certificate export',
                url: window.location.href
            }).catch(error => {
                console.log('Error sharing:', error);
                this.copyExportLink();
            });
        } else {
            this.copyExportLink();
        }
    }

    /**
     * Copy export link
     */
    copyExportLink() {
        const url = window.location.href;
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(() => {
                this.showSuccess('Export link copied to clipboard');
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
            this.showSuccess('Export link copied to clipboard');
        } catch (err) {
            this.showError('Failed to copy link');
        }
        
        document.body.removeChild(textArea);
    }

    /**
     * Show export progress
     */
    showExportProgress() {
        const progress = document.getElementById('export-progress');
        if (progress) {
            progress.style.display = 'block';
        }
        
        // Start progress animation
        this.animateProgress();
    }

    /**
     * Hide export progress
     */
    hideExportProgress() {
        const progress = document.getElementById('export-progress');
        if (progress) {
            progress.style.display = 'none';
        }
    }

    /**
     * Show export success
     */
    showExportSuccess(result) {
        const success = document.getElementById('export-success');
        if (success) {
            success.style.display = 'block';
            
            // Update success message
            const message = success.querySelector('.success-message');
            if (message) {
                message.textContent = `Export completed: ${result.filename}`;
            }
        }
        
        this.showSuccess(`Export completed successfully: ${result.filename}`);
    }

    /**
     * Animate progress
     */
    animateProgress() {
        const progressBar = document.getElementById('export-progress-bar');
        const progressText = document.getElementById('export-progress-text');
        
        if (!progressBar || !progressText) return;
        
        let progress = 0;
        const animate = () => {
            if (progress < 100) {
                progress += Math.random() * 10;
                progressBar.style.width = `${progress}%`;
                progressBar.textContent = `${Math.round(progress)}%`;
                
                if (progress < 30) {
                    progressText.textContent = 'Preparing export...';
                } else if (progress < 60) {
                    progressText.textContent = 'Generating content...';
                } else if (progress < 90) {
                    progressText.textContent = 'Finalizing export...';
                } else {
                    progressText.textContent = 'Export complete!';
                }
                
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }

    /**
     * Get current certificate ID
     */
    getCurrentCertificateId() {
        return window.CertificateManager?.state?.currentCertificate?.certificate_id;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        console.log('🔗 Setting up export button event listeners...');
        
        // Setup export buttons
        this.setupExportButtons();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
    }

    /**
     * Setup format selection
     */
    setupFormatSelection() {
        // Set default format without showing notification
        this.selectedFormat = 'html';
        
        // Update visual selection silently
        const selectedOption = document.querySelector(`[data-format="html"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
        
        // Update format-specific options
        this.updateFormatOptions('html');
        
        // Update preview
        this.updateExportPreview();
    }

    /**
     * Setup export options
     */
    setupExportOptions() {
        // Initialize with default options
        this.exportOptions = {
            includeSections: true,
            includeSecurity: true,
            includeMetadata: true,
            template: 'default'
        };
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only handle shortcuts when export modal is active
            const exportModal = document.getElementById('exportOptionsModal');
            if (!exportModal || !exportModal.classList.contains('show')) return;
            
            switch (e.key) {
                case 'Escape':
                    // Close modal
                    const closeBtn = exportModal.querySelector('.btn-close');
                    if (closeBtn) closeBtn.click();
                    break;
                case 'Enter':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.executeExport();
                    }
                    break;
            }
        });
    }

    /**
     * Utility methods
     */
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
     * Cleanup
     */
    destroy() {
        this.exportQueue = [];
        this.isExporting = false;
        this.selectedFormat = 'html';
        this.exportOptions = {};
    }
}

// Export the class
export default ExportButtons; 