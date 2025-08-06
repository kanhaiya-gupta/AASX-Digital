/**
 * Certificate Manager - Export Handler Module
 * Handles certificate export functionality in various formats
 */

export class ExportHandler {
    constructor() {
        this.supportedFormats = ['html', 'pdf', 'json', 'xml'];
        this.exportQueue = [];
        this.isExporting = false;
    }

    /**
     * Initialize export handler
     */
    async init() {
        console.log('📤 Initializing export handler...');
        
        try {
            this.setupEventListeners();
            
            console.log('✅ Export handler initialized');
            
        } catch (error) {
            console.error('❌ Error initializing export handler:', error);
            this.showError('Failed to initialize export handler');
        }
    }

    /**
     * Export certificate
     */
    async exportCertificate(certificateId, format = 'html', options = {}) {
        try {
            console.log(`📤 Exporting certificate ${certificateId} in ${format} format`);
            
            if (this.isExporting) {
                throw new Error('Export already in progress');
            }
            
            this.isExporting = true;
            this.showExportProgress();
            
            // Validate format
            if (!this.supportedFormats.includes(format)) {
                throw new Error(`Unsupported format: ${format}`);
            }
            
            // Get certificate data
            const certificate = await this.getCertificateData(certificateId);
            
            // Generate export content
            const content = await this.generateExportContent(certificate, format, options);
            
            // Create and download file
            const filename = this.generateFilename(certificate, format);
            await this.downloadFile(content, filename, format);
            
            this.hideExportProgress();
            this.showExportSuccess(filename);
            
            this.isExporting = false;
            
            return { success: true, filename };
            
        } catch (error) {
            console.error('❌ Export error:', error);
            this.hideExportProgress();
            this.showError(`Export failed: ${error.message}`);
            this.isExporting = false;
            
            return { success: false, error: error.message };
        }
    }

    /**
     * Get certificate data
     */
    async getCertificateData(certificateId) {
        try {
            // This would call the core module
            const core = window.CertificateManager?.modules?.core;
            if (core) {
                return await core.getCertificateById(certificateId);
            }
            
            // Fallback to mock data
            return this.getMockCertificate(certificateId);
            
        } catch (error) {
            console.error('Error getting certificate data:', error);
            throw error;
        }
    }

    /**
     * Generate export content
     */
    async generateExportContent(certificate, format, options) {
        console.log(`🎨 Generating ${format} export content`);
        
        switch (format) {
            case 'html':
                return this.generateHTMLContent(certificate, options);
            case 'pdf':
                return this.generatePDFContent(certificate, options);
            case 'json':
                return this.generateJSONContent(certificate, options);
            case 'xml':
                return this.generateXMLContent(certificate, options);
            default:
                throw new Error(`Unsupported format: ${format}`);
        }
    }

    /**
     * Generate HTML content
     */
    generateHTMLContent(certificate, options) {
        const template = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate - ${certificate.certificate_id}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .certificate-id { font-size: 24px; font-weight: bold; color: #333; }
        .twin-name { font-size: 18px; color: #666; margin-top: 10px; }
        .metadata { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .metadata-item { border: 1px solid #ddd; padding: 15px; }
        .metadata-label { font-weight: bold; color: #333; }
        .metadata-value { margin-top: 5px; }
        .sections { margin-top: 30px; }
        .section { border: 1px solid #ddd; margin-bottom: 20px; padding: 20px; }
        .section-header { font-weight: bold; font-size: 16px; margin-bottom: 15px; }
        .section-data { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .data-item { padding: 5px 0; }
        .data-label { font-weight: bold; }
        .footer { margin-top: 50px; text-align: center; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="certificate-id">${certificate.certificate_id}</div>
        <div class="twin-name">${certificate.twin_name}</div>
    </div>
    
    <div class="metadata">
        <div class="metadata-item">
            <div class="metadata-label">Project</div>
            <div class="metadata-value">${certificate.project_name}</div>
        </div>
        <div class="metadata-item">
            <div class="metadata-label">Use Case</div>
            <div class="metadata-value">${certificate.use_case_name}</div>
        </div>
        <div class="metadata-item">
            <div class="metadata-label">Status</div>
            <div class="metadata-value">${certificate.status}</div>
        </div>
        <div class="metadata-item">
            <div class="metadata-label">Health Score</div>
            <div class="metadata-value">${certificate.health_score}%</div>
        </div>
        <div class="metadata-item">
            <div class="metadata-label">Created</div>
            <div class="metadata-value">${this.formatDate(certificate.created_at)}</div>
        </div>
        <div class="metadata-item">
            <div class="metadata-label">Updated</div>
            <div class="metadata-value">${this.formatDate(certificate.updated_at)}</div>
        </div>
    </div>
    
    <div class="sections">
        <h3>Certificate Sections</h3>
        ${this.renderHTMLSections(certificate.sections || {})}
    </div>
    
    <div class="footer">
        <p>Generated on ${new Date().toLocaleString()}</p>
        <p>Certificate ID: ${certificate.certificate_id}</p>
    </div>
</body>
</html>`;
        
        return template;
    }

    /**
     * Generate PDF content
     */
    generatePDFContent(certificate, options) {
        // This would generate PDF content
        // For now, return HTML content that can be converted to PDF
        return this.generateHTMLContent(certificate, options);
    }

    /**
     * Generate JSON content
     */
    generateJSONContent(certificate, options) {
        const exportData = {
            certificate_id: certificate.certificate_id,
            twin_name: certificate.twin_name,
            project_name: certificate.project_name,
            use_case_name: certificate.use_case_name,
            status: certificate.status,
            health_score: certificate.health_score,
            verification_status: certificate.verification_status,
            created_at: certificate.created_at,
            updated_at: certificate.updated_at,
            version: certificate.version,
            sections: certificate.sections || {},
            export_metadata: {
                exported_at: new Date().toISOString(),
                format: 'json',
                version: '1.0'
            }
        };
        
        return JSON.stringify(exportData, null, 2);
    }

    /**
     * Generate XML content
     */
    generateXMLContent(certificate, options) {
        const xml = `<?xml version="1.0" encoding="UTF-8"?>
<certificate>
    <metadata>
        <certificate_id>${this.escapeXML(certificate.certificate_id)}</certificate_id>
        <twin_name>${this.escapeXML(certificate.twin_name)}</twin_name>
        <project_name>${this.escapeXML(certificate.project_name)}</project_name>
        <use_case_name>${this.escapeXML(certificate.use_case_name)}</use_case_name>
        <status>${this.escapeXML(certificate.status)}</status>
        <health_score>${certificate.health_score}</health_score>
        <verification_status>${this.escapeXML(certificate.verification_status)}</verification_status>
        <created_at>${this.escapeXML(certificate.created_at)}</created_at>
        <updated_at>${this.escapeXML(certificate.updated_at)}</updated_at>
        <version>${this.escapeXML(certificate.version)}</version>
    </metadata>
    <sections>
        ${this.renderXMLSections(certificate.sections || {})}
    </sections>
    <export_metadata>
        <exported_at>${new Date().toISOString()}</exported_at>
        <format>xml</format>
        <version>1.0</version>
    </export_metadata>
</certificate>`;
        
        return xml;
    }

    /**
     * Render HTML sections
     */
    renderHTMLSections(sections) {
        return Object.entries(sections).map(([key, section]) => `
            <div class="section">
                <div class="section-header">${this.formatFieldLabel(key)}</div>
                <div class="section-data">
                    ${Object.entries(section).map(([k, v]) => `
                        <div class="data-item">
                            <span class="data-label">${this.formatFieldLabel(k)}:</span>
                            <span>${v}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }

    /**
     * Render XML sections
     */
    renderXMLSections(sections) {
        return Object.entries(sections).map(([key, section]) => `
        <section name="${this.escapeXML(key)}">
            ${Object.entries(section).map(([k, v]) => `
                <${this.escapeXML(k)}>${this.escapeXML(v)}</${this.escapeXML(k)}>
            `).join('')}
        </section>`).join('');
    }

    /**
     * Generate filename
     */
    generateFilename(certificate, format) {
        const timestamp = new Date().toISOString().split('T')[0];
        return `certificate_${certificate.certificate_id}_${timestamp}.${format}`;
    }

    /**
     * Download file
     */
    async downloadFile(content, filename, format) {
        const blob = new Blob([content], { 
            type: this.getMimeType(format) 
        });
        
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**
     * Get MIME type
     */
    getMimeType(format) {
        const mimeTypes = {
            'html': 'text/html',
            'pdf': 'application/pdf',
            'json': 'application/json',
            'xml': 'application/xml'
        };
        return mimeTypes[format] || 'text/plain';
    }

    /**
     * Show export progress
     */
    showExportProgress() {
        const progress = document.getElementById('export-progress');
        if (progress) {
            progress.style.display = 'block';
        }
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
    showExportSuccess(filename) {
        this.showSuccess(`Export completed: ${filename}`);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Export buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.export-btn')) {
                const certificateId = e.target.dataset.certificateId;
                const format = e.target.dataset.format || 'html';
                this.exportCertificate(certificateId, format);
            }
        });
    }

    /**
     * Utility methods
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

    escapeXML(text) {
        return text.toString()
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
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
        this.exportQueue = [];
        this.isExporting = false;
    }
}

// Export the class
export default ExportHandler; 