/**
 * AASX File Upload Module - Bidirectional
 * Handles both AASX → Structured Data and Structured Data → AASX conversions
 */

import { dropdownManager } from '../shared/dropdown-manager.js';
import { getAuthHeaders } from '../../shared/auth-helper.js';

class AasxFileUploadManager {
    constructor() {
        this.currentMode = 'aasx-to-structured';
        this.uploadHistory = [];
        // Don't auto-initialize - let the caller control initialization
    }

    /**
     * Get authentication headers for API calls
     */
    getAuthHeaders() {
        return getAuthHeaders();
    }

    async init() {
        console.log('🚀 AASX File Upload Manager initializing...');
        
        // Wait for dropdown manager to be ready
        await this.waitForDropdownManager();
        
        this.setupModeSwitching();
        this.setupEventListeners();
        this.loadUploadHistory();
        this.updateStatistics();
        
        // Load use cases and projects for dropdowns using dropdown manager
        await this.loadDropdownData();
        
        console.log('✅ AASX File Upload Manager initialized');
    }

    async waitForDropdownManager() {
        console.log('⏳ File Upload Manager: Waiting for dropdown manager...');
        
        // Debug: Show current state
        if (window.dropdownManager) {
            const status = window.dropdownManager.getStatus();
            console.log('📊 File Upload Manager: Current dropdown manager status:', status);
        } else {
            console.log('📊 File Upload Manager: No dropdown manager found in window object');
        }
        
        // Wait for dropdown manager to be ready with proper timeout
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds max wait
        
        while (!window.dropdownManager || !window.dropdownManager.isReady()) {
            if (attempts >= maxAttempts) {
                console.error('❌ File Upload Manager: Timeout waiting for dropdown manager');
                throw new Error('Dropdown manager not ready after timeout');
            }
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
            
            // Debug: Show progress
            if (attempts % 10 === 0) {
                console.log(`⏳ File Upload Manager: Still waiting... (attempt ${attempts}/${maxAttempts})`);
                if (window.dropdownManager) {
                    const status = window.dropdownManager.getStatus();
                    console.log('📊 File Upload Manager: Current status:', status);
                }
            }
        }
        
        console.log('✅ File Upload Manager: Dropdown manager ready');
    }

    async loadDropdownData() {
        try {
            console.log('📋 File Upload Manager: Loading dropdown data...');
            
            // Ensure dropdown manager is ready
            if (!window.dropdownManager || !window.dropdownManager.isReady()) {
                console.error('❌ File Upload Manager: Dropdown manager not ready');
                const status = window.dropdownManager ? window.dropdownManager.getStatus() : 'No dropdown manager';
                console.log('📊 Dropdown Manager Status:', status);
                return;
            }
            
            // Use the dropdown manager to load use cases
            await window.dropdownManager.loadUseCases();
            
            // Request dropdown manager to populate dropdowns for this component
            const success = await window.dropdownManager.populateDropdownsForComponent('file-upload');
            if (!success) {
                console.warn('⚠️ File Upload Manager: Failed to populate dropdowns');
            }
            
            // Set up change event listeners for cascading dropdowns
            this.setupCascadingDropdowns();
            
            console.log('✅ File Upload Manager: Dropdown data loaded');
        } catch (error) {
            console.error('❌ File Upload Manager: Failed to load dropdown data:', error);
        }
    }

    setupCascadingDropdowns() {
        console.log('🔗 File Upload Manager: Setting up cascading dropdowns...');
        
        // AASX Upload Form
        const aasxUseCaseSelect = document.getElementById('aasxUploadUseCaseSelect');
        if (aasxUseCaseSelect) {
            aasxUseCaseSelect.addEventListener('change', (e) => {
                const useCaseId = e.target.value;
                this.onUseCaseChange(useCaseId, 'aasxUploadProjectSelect');
            });
        }
        
        // Structured Upload Form
        const structuredUseCaseSelect = document.getElementById('structuredUploadUseCaseSelect');
        if (structuredUseCaseSelect) {
            structuredUseCaseSelect.addEventListener('change', (e) => {
                const useCaseId = e.target.value;
                this.onUseCaseChange(useCaseId, 'structuredUploadProjectSelect');
            });
        }
        
        // AASX URL Form
        const aasxUrlUseCaseSelect = document.getElementById('aasxUrlUseCaseSelect');
        if (aasxUrlUseCaseSelect) {
            aasxUrlUseCaseSelect.addEventListener('change', (e) => {
                const useCaseId = e.target.value;
                this.onUseCaseChange(useCaseId, 'aasxUrlProjectSelect');
            });
        }
        
        // Structured URL Form
        const structuredUrlUseCaseSelect = document.getElementById('structuredUrlUseCaseSelect');
        if (structuredUrlUseCaseSelect) {
            structuredUrlUseCaseSelect.addEventListener('change', (e) => {
                const useCaseId = e.target.value;
                this.onUseCaseChange(useCaseId, 'structuredUrlProjectSelect');
            });
        }
    }

    async onUseCaseChange(useCaseId, projectSelectId) {
        console.log(`🔄 File Upload Manager: Use case changed to ${useCaseId}, updating project dropdown ${projectSelectId}`);
        
        const projectSelect = document.getElementById(projectSelectId);
        if (!projectSelect) {
            console.error(`❌ File Upload Manager: Project select element not found: ${projectSelectId}`);
            return;
        }
        
        if (useCaseId && window.dropdownManager) {
            try {
                // Load projects for the selected use case
                const projects = await window.dropdownManager.loadProjectsForUseCase(useCaseId);
                
                // Clear existing options
                projectSelect.innerHTML = '<option value="">Choose a project...</option>';
                
                // Add projects to dropdown
                if (projects && projects.length > 0) {
                    projects.forEach(project => {
                        const option = document.createElement('option');
                        option.value = project.project_id;
                        option.textContent = project.name;
                        projectSelect.appendChild(option);
                    });
                    console.log(`✅ File Upload Manager: Populated ${projectSelectId} with ${projects.length} projects`);
                } else {
                    projectSelect.innerHTML = '<option value="">Choose a project...</option><option value="" disabled>No projects available for this use case</option>';
                    console.log(`⚠️ File Upload Manager: No projects found for use case ${useCaseId}`);
                }
            } catch (error) {
                console.error(`❌ File Upload Manager: Failed to load projects for use case ${useCaseId}:`, error);
                projectSelect.innerHTML = '<option value="">Choose a project...</option><option value="" disabled>Error loading projects</option>';
            }
        } else {
            // Clear project dropdown
            projectSelect.innerHTML = '<option value="">Choose a project...</option><option value="" disabled>Select a use case first</option>';
        }
    }

    setupModeSwitching() {
        const modeTabs = document.querySelectorAll('.aasx-mode-tab');
        const aasxMode = document.getElementById('aasxToStructuredMode');
        const structuredMode = document.getElementById('structuredToAasxMode');

        modeTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const mode = tab.dataset.mode;
                this.switchMode(mode);
            });
        });
    }

    switchMode(mode) {
        // Update active tab
        document.querySelectorAll('.aasx-mode-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');

        // Show/hide mode content
        const aasxMode = document.getElementById('aasxToStructuredMode');
        const structuredMode = document.getElementById('structuredToAasxMode');

        if (mode === 'aasx-to-structured') {
            aasxMode.style.display = 'block';
            structuredMode.style.display = 'none';
            this.currentMode = 'aasx-to-structured';
        } else {
            aasxMode.style.display = 'none';
            structuredMode.style.display = 'block';
            this.currentMode = 'structured-to-aasx';
        }

        // Update page title and description
        this.updateModeDisplay();
    }

    updateModeDisplay() {
        const sectionTitle = document.querySelector('.aasx-section-title');
        const sectionDescription = document.querySelector('.aasx-section-description');

        if (this.currentMode === 'aasx-to-structured') {
            sectionTitle.innerHTML = '<i class="fas fa-file-archive aasx-section-icon"></i> AASX → Structured Data';
            sectionDescription.textContent = 'Extract structured data and documents from AASX files';
        } else {
            sectionTitle.innerHTML = '<i class="fas fa-file-code aasx-section-icon"></i> Structured Data → AASX';
            sectionDescription.textContent = 'Convert structured data and documents back to AASX files';
        }
    }

    setupEventListeners() {
        // AASX File Upload Form
        const aasxFileUploadForm = document.getElementById('aasxFileUploadForm');
        if (aasxFileUploadForm) {
            aasxFileUploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAasxFileUpload();
            });
        }

        // Structured Data Upload Form
        const structuredDataUploadForm = document.getElementById('structuredDataUploadForm');
        if (structuredDataUploadForm) {
            structuredDataUploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleStructuredDataUpload();
            });
        }

        // URL Upload Forms
        const aasxUrlUploadForm = document.getElementById('aasxUrlUploadForm');
        if (aasxUrlUploadForm) {
            aasxUrlUploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAasxUrlUpload();
            });
        }

        const structuredUrlUploadForm = document.getElementById('structuredUrlUploadForm');
        if (structuredUrlUploadForm) {
            structuredUrlUploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleStructuredUrlUpload();
            });
        }

        // File input handlers
        this.setupFileInputHandlers();
        this.setupUrlValidationHandlers();
        this.setupQuickActionHandlers();
    }

    setupFileInputHandlers() {
        // AASX File Input
        const aasxFileInput = document.getElementById('aasxFileInput');
        const browseAasxFilesBtn = document.getElementById('browseAasxFilesBtn');
        
        if (browseAasxFilesBtn && aasxFileInput) {
            browseAasxFilesBtn.addEventListener('click', () => {
                aasxFileInput.click();
            });
            aasxFileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e, 'aasx');
            });
        }
        
        // Structured Data Input
        const structuredDataInput = document.getElementById('structuredDataInput');
        const browseStructuredFilesBtn = document.getElementById('browseStructuredFilesBtn');
        
        if (browseStructuredFilesBtn && structuredDataInput) {
            browseStructuredFilesBtn.addEventListener('click', () => {
                structuredDataInput.click();
            });
            structuredDataInput.addEventListener('change', (e) => {
                this.handleFileSelection(e, 'structured');
            });
        }
        
        // Drag and drop handlers
        this.setupDragAndDrop();
    }

    setupDragAndDrop() {
        const uploadAreas = document.querySelectorAll('.aasx-upload-area');
        
        uploadAreas.forEach(area => {
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('drag-over');
            });

            area.addEventListener('dragleave', (e) => {
                e.preventDefault();
                area.classList.remove('drag-over');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    const file = files[0];
                    const fileType = area.id === 'aasxUploadArea' ? 'aasx' : 'structured';
                    this.handleDroppedFile(file, fileType);
                }
            });
        });
    }

    handleFileSelection(event, type) {
        const file = event.target.files[0];
        if (file) {
            this.handleDroppedFile(file, type);
        }
    }

    handleDroppedFile(file, type) {
        const fileName = file.name;
        const fileSize = this.formatFileSize(file.size);
        
        if (type === 'aasx') {
            document.getElementById('aasxSelectedFileName').textContent = fileName;
            document.getElementById('aasxSelectedFileSize').textContent = fileSize;
        } else {
            document.getElementById('structuredSelectedFileName').textContent = fileName;
            document.getElementById('structuredSelectedFileSize').textContent = fileSize;
        }

        // Validate file type
        if (!this.validateFileType(file, type)) {
            this.showError(`Invalid file type. Expected ${type === 'aasx' ? '.aasx' : '.zip'} file.`);
            return;
        }

        this.showSuccess(`File "${fileName}" selected successfully.`);
    }

    validateFileType(file, type) {
        if (type === 'aasx') {
            return file.name.toLowerCase().endsWith('.aasx');
        } else {
            return file.name.toLowerCase().endsWith('.zip');
        }
    }

    setupUrlValidationHandlers() {
        // AASX URL validation
        const validateAasxUrlBtn = document.getElementById('validateAasxUrlBtn');
        const aasxFileUrl = document.getElementById('aasxFileUrl');
        
        if (validateAasxUrlBtn && aasxFileUrl) {
            validateAasxUrlBtn.addEventListener('click', () => {
                this.validateUrl(aasxFileUrl.value, 'aasx');
            });
        }

        // Structured Data URL validation
        const validateStructuredUrlBtn = document.getElementById('validateStructuredUrlBtn');
        const structuredDataUrl = document.getElementById('structuredDataUrl');
        
        if (validateStructuredUrlBtn && structuredDataUrl) {
            validateStructuredUrlBtn.addEventListener('click', () => {
                this.validateUrl(structuredDataUrl.value, 'structured');
            });
        }
    }

    async validateUrl(url, type) {
        if (!url) {
            this.showError('Please enter a URL');
            return;
        }

        try {
            // Show loading state
            this.showLoading(`Validating ${type === 'aasx' ? 'AASX' : 'structured data'} URL...`);

            // Simulate URL validation (replace with actual API call)
            await new Promise(resolve => setTimeout(resolve, 1000));

            const fileName = url.split('/').pop();
            const fileSize = '2.5 MB'; // Mock size

            if (type === 'aasx') {
                document.getElementById('aasxUrlFileName').textContent = fileName;
                document.getElementById('aasxUrlFileSize').textContent = fileSize;
                document.getElementById('aasxUrlPreview').style.display = 'block';
            } else {
                document.getElementById('structuredUrlFileName').textContent = fileName;
                document.getElementById('structuredUrlFileSize').textContent = fileSize;
                document.getElementById('structuredUrlPreview').style.display = 'block';
            }

            this.showSuccess('URL validated successfully!');
        } catch (error) {
            this.showError('Failed to validate URL. Please check the link and try again.');
        }
    }

    async handleAasxFileUpload() {
        const formData = new FormData();
        const fileInput = document.getElementById('aasxFileInput');
        const useCase = document.getElementById('aasxUploadUseCaseSelect').value;
        const project = document.getElementById('aasxUploadProjectSelect').value;
        const description = document.getElementById('aasxFileDescription').value;

        if (!fileInput.files[0]) {
            this.showError('Please select an AASX file');
            return;
        }

        if (!useCase || !project) {
            this.showError('Please select use case and project');
            return;
        }

        formData.append('file', fileInput.files[0]);
        formData.append('project_id', project);  // Send project ID directly
        formData.append('description', description);
        formData.append('job_type', 'extraction');

        await this.uploadFile(formData, 'aasx-extraction');
    }

    async handleStructuredDataUpload() {
        const formData = new FormData();
        const fileInput = document.getElementById('structuredDataInput');
        const useCase = document.getElementById('structuredUploadUseCaseSelect').value;
        const project = document.getElementById('structuredUploadProjectSelect').value;
        const description = document.getElementById('structuredFileDescription').value;

        if (!fileInput.files[0]) {
            this.showError('Please select a structured data ZIP file');
            return;
        }

        if (!useCase || !project) {
            this.showError('Please select use case and project');
            return;
        }

        formData.append('file', fileInput.files[0]);
        formData.append('project_id', project);  // Send project ID directly
        formData.append('description', description);
        formData.append('job_type', 'generation');

        await this.uploadFile(formData, 'aasx-generation');
    }

    async handleAasxUrlUpload() {
        const url = document.getElementById('aasxFileUrl').value;
        const useCase = document.getElementById('aasxUrlUseCaseSelect').value;
        const project = document.getElementById('aasxUrlProjectSelect').value;
        const description = document.getElementById('aasxUrlFileDescription').value;

        if (!url || !useCase || !project) {
            this.showError('Please fill in all required fields');
            return;
        }

        const data = {
            url: url,
            project_id: project,  // Send project ID directly
            description: description
        };

        await this.uploadFromUrl(data, 'aasx-extraction');
    }

    async handleStructuredUrlUpload() {
        const url = document.getElementById('structuredDataUrl').value;
        const useCase = document.getElementById('structuredUrlUseCaseSelect').value;
        const project = document.getElementById('structuredUrlProjectSelect').value;
        const description = document.getElementById('structuredUrlFileDescription').value;

        if (!url || !useCase || !project) {
            this.showError('Please fill in all required fields');
            return;
        }

        const data = {
            url: url,
            project_id: project,  // Send project ID directly
            description: description
        };

        await this.uploadFromUrl(data, 'aasx-generation');
    }

    async uploadFile(formData, operation) {
        try {
            this.showLoading(`Processing ${operation === 'aasx-extraction' ? 'AASX extraction' : 'AASX generation'}...`);
            
            // Show upload progress
            this.simulateUploadProgress(operation === 'aasx-extraction' ? 'aasx' : 'structured');

            // Get form data
            const file = formData.get('file');
            const projectId = formData.get('project_id');
            const description = formData.get('description');
            
            // Determine job type based on operation
            const jobType = operation === 'aasx-extraction' ? 'extraction' : 'generation';
            
            // Get authentication headers
            const authHeaders = this.getAuthHeaders();
            
            // Debug: Log what's being sent
            console.log('📤 Upload FormData contents:');
            for (let [key, value] of formData.entries()) {
                console.log(`  ${key}: ${value}`);
            }
            console.log('🔐 Auth headers:', authHeaders);
            
            // Remove Content-Type header to let browser set it automatically for FormData
            const uploadHeaders = { ...authHeaders };
            delete uploadHeaders['Content-Type'];
            
            // Make real API call to upload file
            const response = await fetch(`/api/aasx-etl/files/upload`, {
                method: 'POST',
                headers: uploadHeaders,
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ Upload response error:', errorData);
                console.error('❌ Error details:', JSON.stringify(errorData, null, 2));
                
                // Handle different error response formats
                let errorMessage = '';
                if (errorData.detail) {
                    if (Array.isArray(errorData.detail)) {
                        errorMessage = errorData.detail.map(err => {
                            if (typeof err === 'object') {
                                return `${err.loc?.join('.') || 'field'}: ${err.msg || err.message || JSON.stringify(err)}`;
                            }
                            return err;
                        }).join(', ');
                    } else {
                        errorMessage = errorData.detail;
                    }
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                } else if (Array.isArray(errorData)) {
                    errorMessage = errorData.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
                } else if (typeof errorData === 'object') {
                    errorMessage = JSON.stringify(errorData);
                } else {
                    errorMessage = `Upload failed with status ${response.status}`;
                }
                
                throw new Error(errorMessage);
            }

            const result = await response.json();
            
            // Create upload record for history
            const uploadRecord = {
                id: Date.now(),
                fileName: file.name,
                operation: operation,
                status: 'completed',
                timestamp: new Date().toISOString(),
                size: file.size,
                projectId: projectId,
                fileId: result.file_id
            };

            this.uploadHistory.unshift(uploadRecord);
            this.updateUploadHistory();
            this.updateStatistics();
            
            // Show success message
            this.showSuccess(`${operation === 'aasx-extraction' ? 'AASX extraction' : 'AASX generation'} completed successfully!`);
            
            // Refresh Data Management view to show new files
            if (window.dataManager) {
                console.log('🔄 Refreshing Data Management view after file upload...');
                await window.dataManager.refreshData();
            }
            
            // Reset form
            this.resetUploadForm(operation === 'aasx-extraction' ? 'aasx' : 'structured');

        } catch (error) {
            console.error('❌ Upload failed:', error);
            this.showError(`Upload failed: ${error.message}`);
        }
    }

    async uploadFromUrl(data, operation) {
        try {
            this.showLoading(`Processing ${operation === 'aasx-extraction' ? 'AASX extraction' : 'AASX generation'} from URL...`);
            
            // Determine job type based on operation
            const jobType = operation === 'aasx-extraction' ? 'extraction' : 'generation';
            
            // Make real API call to upload from URL
            const formData = new FormData();
            formData.append('url', data.url);
            formData.append('project_id', data.project_id);
            formData.append('description', data.description || '');
            formData.append('job_type', jobType);  // Send job type for URL uploads
            
            // Get authentication headers (but don't set Content-Type for FormData)
            const authHeaders = this.getAuthHeaders();
            // Remove Content-Type header to let browser set it automatically for FormData
            const uploadHeaders = { ...authHeaders };
            delete uploadHeaders['Content-Type'];
            
            const response = await fetch('/api/aasx-etl/files/upload-from-url', {
                method: 'POST',
                headers: uploadHeaders,
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ URL upload response error:', errorData);
                
                // Handle different error response formats
                let errorMessage = '';
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                } else if (Array.isArray(errorData)) {
                    errorMessage = errorData.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
                } else if (typeof errorData === 'object') {
                    errorMessage = JSON.stringify(errorData);
                } else {
                    errorMessage = `URL upload failed with status ${response.status}`;
                }
                
                throw new Error(errorMessage);
            }

            const result = await response.json();
            
            // Create upload record for history
            const uploadRecord = {
                id: Date.now(),
                fileName: data.url.split('/').pop(),
                operation: operation,
                status: 'completed',
                timestamp: new Date().toISOString(),
                size: 'Unknown',
                projectId: data.project_id,
                fileId: result.file_id
            };

            this.uploadHistory.unshift(uploadRecord);
            this.updateUploadHistory();
            this.updateStatistics();
            
            // Show success message
            this.showSuccess(`${operation === 'aasx-extraction' ? 'AASX extraction' : 'AASX generation'} from URL completed successfully!`);
            
            // Refresh Data Management view to show new files
            if (window.dataManager) {
                console.log('🔄 Refreshing Data Management view after URL upload...');
                await window.dataManager.refreshData();
            }

        } catch (error) {
            console.error('❌ URL upload failed:', error);
            this.showError(`URL upload failed: ${error.message}`);
        }
    }

    // Reset upload form after successful upload
    resetUploadForm(type) {
        if (type === 'aasx') {
            const form = document.getElementById('aasxFileUploadForm');
            if (form) {
                form.reset();
                // Reset file input
                const fileInput = document.getElementById('aasxFileInput');
                if (fileInput) {
                    fileInput.value = '';
                }
            }
        } else if (type === 'structured') {
            const form = document.getElementById('structuredDataUploadForm');
            if (form) {
                form.reset();
                // Reset file input
                const fileInput = document.getElementById('structuredDataInput');
                if (fileInput) {
                    fileInput.value = '';
                }
            }
        }
        
        // Hide progress bars
        const progressElements = document.querySelectorAll('.aasx-upload-progress');
        progressElements.forEach(element => {
            element.style.display = 'none';
        });
    }

    simulateUploadProgress(type) {
        const progressElement = type === 'aasx' ? 
            document.getElementById('aasxUploadProgress') : 
            document.getElementById('structuredUploadProgress');
        const progressFill = type === 'aasx' ? 
            document.getElementById('aasxUploadProgressFill') : 
            document.getElementById('structuredUploadProgressFill');
        const progressText = type === 'aasx' ? 
            document.getElementById('aasxUploadProgressText') : 
            document.getElementById('structuredUploadProgressText');

        if (progressElement && progressFill && progressText) {
            progressElement.style.display = 'block';
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                }
                progressFill.style.width = `${progress}%`;
                progressText.textContent = `${Math.round(progress)}%`;
            }, 200);
        }
    }

    setupQuickActionHandlers() {
        const quickActions = {
            'bulkUploadBtn': () => this.handleBulkUpload(),
            'uploadHistoryBtn': () => this.showUploadHistory(),
            'refreshUploadsBtn': () => this.refreshUploads(),
            'clearUploadsBtn': () => this.clearUploads(),
            'exportUploadsBtn': () => this.exportUploads()
        };

        Object.entries(quickActions).forEach(([id, handler]) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('click', handler);
            }
        });
    }

    handleBulkUpload() {
        this.showInfo('Bulk upload feature coming soon!');
    }

    showUploadHistory() {
        this.showInfo('Upload history modal coming soon!');
    }

    refreshUploads() {
        this.loadUploadHistory();
        this.updateStatistics();
        this.showSuccess('Upload data refreshed!');
    }

    clearUploads() {
        if (confirm('Are you sure you want to clear all upload history?')) {
            this.uploadHistory = [];
            this.updateUploadHistory();
            this.updateStatistics();
            this.showSuccess('Upload history cleared!');
        }
    }

    exportUploads() {
        const dataStr = JSON.stringify(this.uploadHistory, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'aasx_upload_history.json';
        link.click();
        URL.revokeObjectURL(url);
        this.showSuccess('Upload history exported!');
    }

    loadUploadHistory() {
        // Load from localStorage or API
        const saved = localStorage.getItem('aasxUploadHistory');
        if (saved) {
            this.uploadHistory = JSON.parse(saved);
        }
        this.updateUploadHistory();
    }

    updateUploadHistory() {
        // Save to localStorage
        localStorage.setItem('aasxUploadHistory', JSON.stringify(this.uploadHistory));
        
        // Update table (if exists)
        const tableBody = document.getElementById('recentUploadsTable');
        if (tableBody) {
            tableBody.innerHTML = this.uploadHistory.slice(0, 10).map(record => `
                <tr>
                    <td>
                        <i class="fas fa-${record.operation === 'aasx-extraction' ? 'file-archive' : 'file-code'} text-primary me-2"></i>
                        ${record.fileName}
                    </td>
                    <td>${this.formatFileSize(record.size)}</td>
                    <td>${record.operation === 'aasx-extraction' ? 'AASX → Structured' : 'Structured → AASX'}</td>
                    <td><span class="badge bg-success">${record.status}</span></td>
                    <td>${this.formatTimestamp(record.timestamp)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="aasxUploadManager.viewUpload(${record.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="aasxUploadManager.downloadUpload(${record.id})">
                            <i class="fas fa-download"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    }

    updateStatistics() {
        const stats = {
            totalUploads: this.uploadHistory.length,
            aasxExtractions: this.uploadHistory.filter(r => r.operation === 'aasx-extraction').length,
            aasxGenerations: this.uploadHistory.filter(r => r.operation === 'aasx-generation').length,
            failedUploads: this.uploadHistory.filter(r => r.status === 'failed').length
        };

        Object.entries(stats).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = value;
            }
        });
    }

    viewUpload(id) {
        const record = this.uploadHistory.find(r => r.id === id);
        if (record) {
            this.showInfo(`Viewing upload: ${record.fileName}`);
        }
    }

    downloadUpload(id) {
        const record = this.uploadHistory.find(r => r.id === id);
        if (record) {
            this.showSuccess(`Downloading: ${record.fileName}`);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 'Unknown') return 'Unknown';
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        return date.toLocaleDateString();
    }

    showSuccess(message) {
        // Implement success notification
        console.log('Success:', message);
    }

    showError(message) {
        // Implement error notification
        console.error('Error:', message);
    }

    showInfo(message) {
        // Implement info notification
        console.log('Info:', message);
    }

    showLoading(message) {
        // Implement loading notification
        console.log('Loading:', message);
    }
}

export default AasxFileUploadManager; 