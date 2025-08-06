/**
 * File Upload Handler for AASX Module
 * Handles file uploads and URL downloads for AASX files
 */

import { showSuccess, showError } from '../shared/alerts.js';

export class FileUploadHandler {
    constructor() {
        this.isInitialized = false;
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        console.log('🚀 File Upload Handler initializing...');
        this.setupEventListeners();
        this.isInitialized = true;
        console.log('✅ File Upload Handler initialized');
    }

    setupEventListeners() {
        // File upload form
        $('#fileUploadForm').on('submit', (e) => this.handleFileUpload(e));
        
        // URL upload form
        $('#urlUploadForm').on('submit', (e) => this.handleUrlUpload(e));
        
        console.log('🔧 File Upload Handler: Event listeners setup complete');
    }

    async handleFileUpload(e) {
        e.preventDefault();
        
        console.log('📁 File Upload Handler: Processing file upload...');
        
        const projectId = $('#uploadProjectSelect').val();
        const fileInput = $('#aasxFileInput')[0];
        const description = $('#fileDescription').val();

        // Validation
        if (!projectId) {
            showError('Please select a project');
            return;
        }

        if (!fileInput.files[0]) {
            showError('Please select a file');
            return;
        }

        // Check file type
        const file = fileInput.files[0];
        if (!file.name.toLowerCase().endsWith('.aasx')) {
            showError('Only .aasx files are allowed');
            return;
        }

        try {
            // Show loading state
            const submitBtn = $('#fileUploadForm button[type="submit"]');
            const originalText = submitBtn.html();
            submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Uploading...');

            // Prepare form data
            const formData = new FormData();
            formData.append('file', file);
            if (description) {
                formData.append('description', description);
            }

            console.log(`📤 File Upload Handler: Uploading file ${file.name} to project ${projectId}`);

            // Upload file
            const response = await fetch(`/api/aasx/projects/${projectId}/upload`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const fileInfo = await response.json();
                console.log('✅ File Upload Handler: File uploaded successfully:', fileInfo);
                
                showSuccess(`File "${file.name}" uploaded successfully!`);
                
                // Reset form
                $('#fileUploadForm')[0].reset();
                
                // Refresh data managers
                this.refreshDataManagers();
                
            } else {
                const error = await response.json();
                console.error('❌ File Upload Handler: Upload failed:', error);
                
                if (response.status === 409) {
                    showError(`Duplicate file: ${error.detail}`);
                } else {
                    showError(`Upload failed: ${error.detail}`);
                }
            }

        } catch (error) {
            console.error('❌ File Upload Handler: Upload error:', error);
            showError(`Upload error: ${error.message}`);
        } finally {
            // Reset button state
            const submitBtn = $('#fileUploadForm button[type="submit"]');
            submitBtn.prop('disabled', false).html('<i class="fas fa-upload me-2"></i>Upload File');
        }
    }

    async handleUrlUpload(e) {
        e.preventDefault();
        
        console.log('🌐 File Upload Handler: Processing URL upload...');
        
        const projectId = $('#urlProjectSelect').val();
        const fileUrl = $('#aasxFileUrl').val();
        const description = $('#urlFileDescription').val();

        // Validation
        if (!projectId) {
            showError('Please select a project');
            return;
        }

        if (!fileUrl) {
            showError('Please enter a file URL');
            return;
        }

        // Check if URL points to .aasx file
        if (!fileUrl.toLowerCase().endsWith('.aasx')) {
            showError('URL must point to a .aasx file');
            return;
        }

        try {
            // Show loading state
            const submitBtn = $('#urlUploadForm button[type="submit"]');
            const originalText = submitBtn.html();
            submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Downloading...');

            console.log(`📥 File Upload Handler: Downloading file from ${fileUrl}`);

            // Download file from URL
            const downloadResponse = await fetch(fileUrl);
            
            if (!downloadResponse.ok) {
                throw new Error(`Failed to download file: ${downloadResponse.status} ${downloadResponse.statusText}`);
            }

            // Get filename from URL
            const urlParts = fileUrl.split('/');
            const filename = urlParts[urlParts.length - 1] || 'downloaded_file.aasx';

            // Create file object from downloaded content
            const fileContent = await downloadResponse.blob();
            const file = new File([fileContent], filename, { type: 'application/octet-stream' });

            // Prepare form data
            const formData = new FormData();
            formData.append('file', file);
            if (description) {
                formData.append('description', description);
            }

            console.log(`📤 File Upload Handler: Uploading downloaded file ${filename} to project ${projectId}`);

            // Upload file
            const uploadResponse = await fetch(`/api/aasx/projects/${projectId}/upload`, {
                method: 'POST',
                body: formData
            });

            if (uploadResponse.ok) {
                const fileInfo = await uploadResponse.json();
                console.log('✅ File Upload Handler: URL file uploaded successfully:', fileInfo);
                
                showSuccess(`File "${filename}" downloaded and uploaded successfully!`);
                
                // Reset form
                $('#urlUploadForm')[0].reset();
                
                // Refresh data managers
                this.refreshDataManagers();
                
            } else {
                const error = await uploadResponse.json();
                console.error('❌ File Upload Handler: URL upload failed:', error);
                
                if (uploadResponse.status === 409) {
                    showError(`Duplicate file: ${error.detail}`);
                } else {
                    showError(`Upload failed: ${error.detail}`);
                }
            }

        } catch (error) {
            console.error('❌ File Upload Handler: URL upload error:', error);
            showError(`URL upload error: ${error.message}`);
        } finally {
            // Reset button state
            const submitBtn = $('#urlUploadForm button[type="submit"]');
            submitBtn.prop('disabled', false).html('<i class="fas fa-download me-2"></i>Download & Upload');
        }
    }

    refreshDataManagers() {
        // Refresh the data manager to show new files
        if (window.dataManager && typeof window.dataManager.loadProjects === 'function') {
            window.dataManager.loadProjects();
        }
        
        // Refresh dropdown manager if it exists
        if (window.dropdownManager && typeof window.dropdownManager.loadUseCases === 'function') {
            window.dropdownManager.loadUseCases();
        }
        
        // Refresh ETL pipeline if it exists
        if (window.aasxETLPipeline && typeof window.aasxETLPipeline.refreshFiles === 'function') {
            window.aasxETLPipeline.refreshFiles();
        }
    }

    destroy() {
        // Clean up event listeners
        $('#fileUploadForm').off('submit');
        $('#urlUploadForm').off('submit');
        
        this.isInitialized = false;
        console.log('🧹 File Upload Handler destroyed');
    }
}

// Export for use in other modules
window.FileUploadHandler = FileUploadHandler;

export default FileUploadHandler; 