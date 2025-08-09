/**
 * AASX File Upload Module - Bidirectional
 * Handles both AASX → Structured Data and Structured Data → AASX conversions
 */

class AasxFileUploadManager {
    constructor() {
        this.currentMode = 'aasx-to-structured';
        this.uploadHistory = [];
        this.init();
    }

    init() {
        this.setupModeSwitching();
        this.setupEventListeners();
        this.loadUploadHistory();
        this.updateStatistics();
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
            browseAasxFilesBtn.addEventListener('click', () => aasxFileInput.click());
            aasxFileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e, 'aasx');
            });
        }

        // Structured Data Input
        const structuredDataInput = document.getElementById('structuredDataInput');
        const browseStructuredFilesBtn = document.getElementById('browseStructuredFilesBtn');
        
        if (browseStructuredFilesBtn && structuredDataInput) {
            browseStructuredFilesBtn.addEventListener('click', () => structuredDataInput.click());
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
        formData.append('use_case', useCase);
        formData.append('project', project);
        formData.append('description', description);
        formData.append('extract_structured_data', document.getElementById('extractStructuredData').checked);
        formData.append('extract_documents', document.getElementById('extractDocuments').checked);

        await this.uploadFile(formData, 'aasx-extraction');
    }

    async handleStructuredDataUpload() {
        const formData = new FormData();
        const fileInput = document.getElementById('structuredDataInput');
        const useCase = document.getElementById('structuredUploadUseCaseSelect').value;
        const project = document.getElementById('structuredUploadProjectSelect').value;
        const description = document.getElementById('structuredFileDescription').value;
        const outputFileName = document.getElementById('outputAasxFileName').value;

        if (!fileInput.files[0]) {
            this.showError('Please select a structured data ZIP file');
            return;
        }

        if (!useCase || !project) {
            this.showError('Please select use case and project');
            return;
        }

        if (!outputFileName) {
            this.showError('Please specify output AASX file name');
            return;
        }

        formData.append('file', fileInput.files[0]);
        formData.append('use_case', useCase);
        formData.append('project', project);
        formData.append('description', description);
        formData.append('output_filename', outputFileName);
        formData.append('include_structured_data', document.getElementById('includeStructuredData').checked);
        formData.append('include_documents', document.getElementById('includeDocuments').checked);

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
            use_case: useCase,
            project: project,
            description: description,
            extract_structured_data: document.getElementById('extractStructuredData').checked,
            extract_documents: document.getElementById('extractDocuments').checked
        };

        await this.uploadFromUrl(data, 'aasx-extraction');
    }

    async handleStructuredUrlUpload() {
        const url = document.getElementById('structuredDataUrl').value;
        const useCase = document.getElementById('structuredUrlUseCaseSelect').value;
        const project = document.getElementById('structuredUrlProjectSelect').value;
        const description = document.getElementById('structuredUrlFileDescription').value;
        const outputFileName = document.getElementById('urlOutputAasxFileName').value;

        if (!url || !useCase || !project || !outputFileName) {
            this.showError('Please fill in all required fields');
            return;
        }

        const data = {
            url: url,
            use_case: useCase,
            project: project,
            description: description,
            output_filename: outputFileName,
            include_structured_data: document.getElementById('includeStructuredData').checked,
            include_documents: document.getElementById('includeDocuments').checked
        };

        await this.uploadFromUrl(data, 'aasx-generation');
    }

    async uploadFile(formData, operation) {
        try {
            this.showLoading(`Processing ${operation === 'aasx-extraction' ? 'AASX extraction' : 'AASX generation'}...`);
            
            // Simulate upload progress
            this.simulateUploadProgress(operation === 'aasx-extraction' ? 'aasx' : 'structured');

            // Mock API call (replace with actual endpoint)
            await new Promise(resolve => setTimeout(resolve, 3000));

            const uploadRecord = {
                id: Date.now(),
                fileName: formData.get('file').name,
                operation: operation,
                status: 'completed',
                timestamp: new Date().toISOString(),
                size: formData.get('file').size
            };

            this.uploadHistory.unshift(uploadRecord);
            this.updateUploadHistory();
            this.updateStatistics();
            this.showSuccess(`${operation === 'aasx-extraction' ? 'AASX extraction' : 'AASX generation'} completed successfully!`);

        } catch (error) {
            this.showError(`Upload failed: ${error.message}`);
        }
    }

    async uploadFromUrl(data, operation) {
        try {
            this.showLoading(`Processing ${operation === 'aasx-extraction' ? 'AASX extraction' : 'AASX generation'} from URL...`);
            
            // Mock API call (replace with actual endpoint)
            await new Promise(resolve => setTimeout(resolve, 2500));

            const uploadRecord = {
                id: Date.now(),
                fileName: data.url.split('/').pop(),
                operation: operation,
                status: 'completed',
                timestamp: new Date().toISOString(),
                size: 'Unknown'
            };

            this.uploadHistory.unshift(uploadRecord);
            this.updateUploadHistory();
            this.updateStatistics();
            this.showSuccess(`${operation === 'aasx-extraction' ? 'AASX extraction' : 'AASX generation'} from URL completed successfully!`);

        } catch (error) {
            this.showError(`URL upload failed: ${error.message}`);
        }
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

// Initialize the upload manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aasxUploadManager = new AasxFileUploadManager();
});

export default AasxFileUploadManager; 