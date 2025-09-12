/**
 * File Operations Module
 * Handles all file-related functionality for the Data Platform
 * 
 * @author AAS Data Modeling Framework
 * @version 2.0.0
 * @license MIT
 */

class FileOperationsModule {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.selectedFiles = new Set();
        this.filters = {
            type: '',
            project: '',
            tags: '',
            status: '',
            dateFrom: '',
            dateTo: '',
            search: ''
        };
        this.uploadQueue = [];
        this.isUploading = false;

        this.init();
    }

    /**
     * Initialize the file operations module
     */
    init() {
        this.bindEvents();
        this.loadFileData();
        console.log('✅ File Operations Module initialized');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Search and filter events
        const searchInput = document.getElementById('fileSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.filterFiles(), 300));
        }

        // Filter change events
        const filterSelects = document.querySelectorAll('#fileTypeFilter, #fileProjectFilter, #fileStatusFilter');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => this.filterFiles());
        });

        // Date filter events
        const dateInputs = document.querySelectorAll('#fileDateFrom, #fileDateTo');
        dateInputs.forEach(input => {
            input.addEventListener('change', () => this.filterFiles());
        });

        // Bulk action events
        const selectAllCheckbox = document.getElementById('selectAllFiles');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => this.toggleSelectAllFiles(e.target.checked));
        }

        // Upload modal events
        this.setupUploadModalEvents();
    }

    /**
     * Setup upload modal event listeners
     */
    setupUploadModalEvents() {
        const uploadModal = document.getElementById('uploadModal');
        if (uploadModal) {
            // File input change
            const fileInput = uploadModal.querySelector('#fileInput');
            if (fileInput) {
                fileInput.addEventListener('change', (e) => this.handleFileSelection(e.target.files));
            }

            // Drop zone events
            const dropZone = uploadModal.querySelector('.drop-zone-large');
            if (dropZone) {
                dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
                dropZone.addEventListener('drop', (e) => this.handleFileDrop(e));
                dropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            }

            // Upload button
            const uploadBtn = uploadModal.querySelector('#uploadFilesBtn');
            if (uploadBtn) {
                uploadBtn.addEventListener('click', () => this.uploadFiles());
            }
        }
    }

    /**
     * Load file data and metrics
     */
    async loadFileData() {
        try {
            // Load metrics
            const metrics = await this.getFileMetrics();
            this.updateMetrics(metrics);

            // Load files
            const files = await this.getFiles();
            this.updateFilesTable(files);

            // Load analytics
            const analytics = await this.getFileAnalytics();
            this.updateAnalytics(analytics);

        } catch (error) {
            console.error('Error loading file data:', error);
            this.showErrorMessage('Failed to load file data');
        }
    }

    /**
     * Get file metrics from service
     */
    async getFileMetrics() {
        // Mock service call - replace with actual API call
        return {
            totalFiles: 1247,
            storageUsed: '2.4 GB',
            pendingProcessing: 23,
            securedFiles: 1189,
            fileGrowthRate: 12.5,
            storageGrowthRate: 8.3,
            processingRate: 95.2,
            securityRate: 98.7
        };
    }

    /**
     * Get files from service
     */
    async getFiles() {
        // Mock service call - replace with actual API call
        return [
            {
                id: 1,
                name: 'Project_Requirements.pdf',
                type: 'document',
                size: '2.4 MB',
                project: 'Digital Twin Analytics',
                tags: ['requirements', 'documentation'],
                status: 'active',
                uploadedBy: 'John Doe',
                uploadedAt: '2024-01-15',
                lastModified: '2024-01-20'
            },
            {
                id: 2,
                name: 'Data_Model_Schema.json',
                type: 'data',
                size: '156 KB',
                project: 'AAS Framework',
                tags: ['schema', 'json', 'data-model'],
                status: 'active',
                uploadedBy: 'Jane Smith',
                uploadedAt: '2024-01-18',
                lastModified: '2024-01-19'
            },
            {
                id: 3,
                name: 'System_Architecture.png',
                type: 'image',
                size: '1.8 MB',
                project: 'Core Infrastructure',
                tags: ['architecture', 'diagram'],
                status: 'active',
                uploadedBy: 'Mike Johnson',
                uploadedAt: '2024-01-16',
                lastModified: '2024-01-16'
            },
            {
                id: 4,
                name: 'API_Documentation.md',
                type: 'code',
                size: '89 KB',
                project: 'Integration Services',
                tags: ['api', 'documentation', 'markdown'],
                status: 'processing',
                uploadedBy: 'Sarah Wilson',
                uploadedAt: '2024-01-20',
                lastModified: '2024-01-20'
            },
            {
                id: 5,
                name: 'Legacy_Data_Archive.zip',
                type: 'archive',
                size: '45.2 MB',
                project: 'Data Migration',
                tags: ['legacy', 'archive', 'migration'],
                status: 'archived',
                uploadedBy: 'Tom Brown',
                uploadedAt: '2024-01-10',
                lastModified: '2024-01-10'
            }
        ];
    }

    /**
     * Get file analytics from service
     */
    async getFileAnalytics() {
        // Mock service call - replace with actual API call
        return {
            typeDistribution: {
                document: 35,
                image: 25,
                data: 20,
                code: 15,
                archive: 5
            },
            storageUsage: {
                document: '850 MB',
                image: '600 MB',
                data: '480 MB',
                code: '360 MB',
                archive: '110 MB'
            }
        };
    }

    /**
     * Update metrics display
     */
    updateMetrics(metrics) {
        // Update metric cards
        const totalFilesEl = document.getElementById('totalFiles');
        if (totalFilesEl) totalFilesEl.textContent = metrics.totalFiles.toLocaleString();

        const storageUsedEl = document.getElementById('storageUsed');
        if (storageUsedEl) storageUsedEl.textContent = metrics.storageUsed;

        const pendingProcessingEl = document.getElementById('pendingProcessing');
        if (pendingProcessingEl) pendingProcessingEl.textContent = metrics.pendingProcessing;

        const securedFilesEl = document.getElementById('securedFiles');
        if (securedFilesEl) securedFilesEl.textContent = metrics.securedFiles;

        // Update growth rates
        const fileGrowthEl = document.getElementById('fileGrowthRate');
        if (fileGrowthEl) fileGrowthEl.textContent = `${metrics.fileGrowthRate}%`;

        const storageGrowthEl = document.getElementById('storageGrowthRate');
        if (storageGrowthEl) storageGrowthEl.textContent = `${metrics.storageGrowthRate}%`;

        const processingRateEl = document.getElementById('processingRate');
        if (processingRateEl) processingRateEl.textContent = `${metrics.processingRate}%`;

        const securityRateEl = document.getElementById('securityRate');
        if (securityRateEl) securityRateEl.textContent = `${metrics.securityRate}%`;

        // Animate metrics
        this.animateMetrics();
    }

    /**
     * Update files table
     */
    updateFilesTable(files) {
        const tbody = document.querySelector('#filesTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        files.forEach(file => {
            const row = this.createFileRow(file);
            tbody.appendChild(row);
        });

        // Update pagination
        this.updatePagination(files.length);
    }

    /**
     * Create file table row
     */
    createFileRow(file) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${file.id}" 
                           onchange="toggleFileSelection(${file.id})">
                </div>
            </td>
            <td>
                <div class="dp-file-profile">
                    <div class="dp-file-icon ${file.type}">
                        <i class="fas ${this.getFileTypeIcon(file.type)}"></i>
                    </div>
                    <div class="dp-file-info">
                        <h6>${file.name}</h6>
                        <small>${file.size}</small>
                    </div>
                </div>
            </td>
            <td>
                <span class="dp-status-badge ${file.status}">
                    ${file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                </span>
            </td>
            <td>${file.project}</td>
            <td>
                <div class="d-flex flex-wrap gap-1">
                    ${file.tags.map(tag => `<span class="badge bg-light text-dark">${tag}</span>`).join('')}
                </div>
            </td>
            <td>${file.uploadedBy}</td>
            <td>${this.formatDate(file.uploadedAt)}</td>
            <td>
                <div class="dp-action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewFileDetails(${file.id})" 
                            title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="downloadFile(${file.id})" 
                            title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="editFile(${file.id})" 
                            title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteFile(${file.id})" 
                            title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        return row;
    }

    /**
     * Get file type icon
     */
    getFileTypeIcon(type) {
        const icons = {
            document: 'fa-file-alt',
            image: 'fa-file-image',
            video: 'fa-file-video',
            audio: 'fa-file-audio',
            archive: 'fa-file-archive',
            data: 'fa-file-csv',
            code: 'fa-file-code'
        };
        return icons[type] || 'fa-file';
    }

    /**
     * Update analytics charts
     */
    updateAnalytics(analytics) {
        // Update file type distribution
        const typeDistributionEl = document.getElementById('fileTypeDistribution');
        if (typeDistributionEl) {
            typeDistributionEl.innerHTML = `
                <div class="dp-chart-placeholder">
                    <i class="fas fa-chart-pie fa-3x"></i>
                    <p>File Type Distribution Chart</p>
                    <small>Document: ${analytics.typeDistribution.document}% | 
                           Image: ${analytics.typeDistribution.image}% | 
                           Data: ${analytics.typeDistribution.data}%</small>
                </div>
            `;
        }

        // Update storage usage
        const storageUsageEl = document.getElementById('storageUsageChart');
        if (storageUsageEl) {
            storageUsageEl.innerHTML = `
                <div class="dp-chart-placeholder">
                    <i class="fas fa-chart-bar fa-3x"></i>
                    <p>Storage Usage Chart</p>
                    <small>Document: ${analytics.storageUsage.document} | 
                           Image: ${analytics.storageUsage.image} | 
                           Data: ${analytics.storageUsage.data}</small>
                </div>
            `;
        }
    }

    /**
     * Filter files based on current filters
     */
    filterFiles() {
        const searchTerm = this.filters.search.toLowerCase();
        const typeFilter = this.filters.type;
        const projectFilter = this.filters.project;
        const statusFilter = this.filters.status;
        const dateFrom = this.filters.dateFrom;
        const dateTo = this.filters.dateTo;

        const rows = document.querySelectorAll('#filesTable tbody tr');
        
        rows.forEach(row => {
            const fileName = row.querySelector('.dp-file-info h6').textContent.toLowerCase();
            const fileType = row.querySelector('.dp-file-icon').className.split(' ').find(cls => 
                ['document', 'image', 'video', 'audio', 'archive', 'data', 'code'].includes(cls));
            const fileProject = row.querySelector('td:nth-child(4)').textContent;
            const fileStatus = row.querySelector('.dp-status-badge').textContent.toLowerCase();
            const fileDate = row.querySelector('td:nth-child(7)').textContent;

            let show = true;

            // Search filter
            if (searchTerm && !fileName.includes(searchTerm)) {
                show = false;
            }

            // Type filter
            if (typeFilter && fileType !== typeFilter) {
                show = false;
            }

            // Project filter
            if (projectFilter && fileProject !== projectFilter) {
                show = false;
            }

            // Status filter
            if (statusFilter && fileStatus !== statusFilter) {
                show = false;
            }

            // Date filters
            if (dateFrom && new Date(fileDate) < new Date(dateFrom)) {
                show = false;
            }
            if (dateTo && new Date(fileDate) > new Date(dateTo)) {
                show = false;
            }

            row.style.display = show ? '' : 'none';
        });

        // Update pagination
        this.updatePagination(Array.from(rows).filter(row => row.style.display !== 'none').length);
    }

    /**
     * Update pagination
     */
    updatePagination(totalItems) {
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        const paginationEl = document.getElementById('filesPagination');
        
        if (!paginationEl) return;

        let paginationHTML = '';
        
        // Previous button
        paginationHTML += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changeFilePage(${this.currentPage - 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                paginationHTML += `
                    <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="changeFilePage(${i})">${i}</a>
                    </li>
                `;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        // Next button
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changeFilePage(${this.currentPage + 1})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;

        paginationEl.innerHTML = paginationHTML;
    }

    /**
     * Toggle select all files
     */
    toggleSelectAllFiles(checked) {
        const checkboxes = document.querySelectorAll('#filesTable tbody .form-check-input');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            if (checked) {
                this.selectedFiles.add(parseInt(checkbox.value));
            } else {
                this.selectedFiles.delete(parseInt(checkbox.value));
            }
        });
        this.updateBulkActions();
    }

    /**
     * Toggle individual file selection
     */
    toggleFileSelection(fileId) {
        if (this.selectedFiles.has(fileId)) {
            this.selectedFiles.delete(fileId);
        } else {
            this.selectedFiles.add(fileId);
        }
        this.updateBulkActions();
    }

    /**
     * Update bulk actions visibility
     */
    updateBulkActions() {
        const bulkActions = document.getElementById('bulkActions');
        if (bulkActions) {
            bulkActions.style.display = this.selectedFiles.size > 0 ? 'block' : 'none';
        }

        // Update select all checkbox
        const selectAllCheckbox = document.getElementById('selectAllFiles');
        if (selectAllCheckbox) {
            const totalCheckboxes = document.querySelectorAll('#filesTable tbody .form-check-input').length;
            const checkedCheckboxes = document.querySelectorAll('#filesTable tbody .form-check-input:checked').length;
            selectAllCheckbox.indeterminate = checkedCheckboxes > 0 && checkedCheckboxes < totalCheckboxes;
            selectAllCheckbox.checked = checkedCheckboxes === totalCheckboxes;
        }
    }

    /**
     * Show upload modal
     */
    showUploadModal() {
        const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
        modal.show();
        this.resetUploadForm();
    }

    /**
     * Handle file selection
     */
    handleFileSelection(files) {
        this.uploadQueue = Array.from(files);
        this.updateFileList();
    }

    /**
     * Handle drag over
     */
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    /**
     * Handle file drop
     */
    handleFileDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        this.uploadQueue = [...this.uploadQueue, ...files];
        this.updateFileList();
    }

    /**
     * Handle drag leave
     */
    handleDragLeave(e) {
        e.currentTarget.classList.remove('dragover');
    }

    /**
     * Update file list display
     */
    updateFileList() {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;

        fileList.innerHTML = '';

        this.uploadQueue.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-item-info">
                    <div class="file-item-icon ${this.getFileTypeFromName(file.name)}">
                        <i class="fas ${this.getFileTypeIcon(this.getFileTypeFromName(file.name))}"></i>
                    </div>
                    <div class="file-item-details">
                        <h6>${file.name}</h6>
                        <small>${this.formatFileSize(file.size)}</small>
                    </div>
                </div>
                <div class="file-item-actions">
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFileFromQueue(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            fileList.appendChild(fileItem);
        });
    }

    /**
     * Get file type from filename
     */
    getFileTypeFromName(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const typeMap = {
            'pdf': 'document', 'doc': 'document', 'docx': 'document', 'txt': 'document',
            'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'svg': 'image',
            'mp4': 'video', 'avi': 'video', 'mov': 'video', 'wmv': 'video',
            'mp3': 'audio', 'wav': 'audio', 'flac': 'audio', 'aac': 'audio',
            'zip': 'archive', 'rar': 'archive', '7z': 'archive', 'tar': 'archive',
            'csv': 'data', 'json': 'data', 'xml': 'data', 'xlsx': 'data',
            'js': 'code', 'py': 'code', 'java': 'code', 'cpp': 'code', 'html': 'code', 'css': 'code'
        };
        return typeMap[ext] || 'document';
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Upload files
     */
    async uploadFiles() {
        if (this.uploadQueue.length === 0) {
            this.showErrorMessage('No files selected for upload');
            return;
        }

        if (this.isUploading) {
            this.showErrorMessage('Upload already in progress');
            return;
        }

        this.isUploading = true;
        this.showUploadProgress();

        try {
            for (let i = 0; i < this.uploadQueue.length; i++) {
                const file = this.uploadQueue[i];
                await this.uploadSingleFile(file, i);
            }

            this.showSuccessMessage(`Successfully uploaded ${this.uploadQueue.length} files`);
            this.resetUploadForm();
            
            // Refresh file list
            this.loadFileData();

        } catch (error) {
            console.error('Upload error:', error);
            this.showErrorMessage('Some files failed to upload');
        } finally {
            this.isUploading = false;
            this.hideUploadProgress();
        }
    }

    /**
     * Upload single file
     */
    async uploadSingleFile(file, index) {
        // Simulate upload progress
        return new Promise((resolve) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    this.updateUploadProgress(index, progress, 'Completed');
                    setTimeout(resolve, 500);
                } else {
                    this.updateUploadProgress(index, progress, 'Uploading...');
                }
            }, 200);
        });
    }

    /**
     * Show upload progress
     */
    showUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress');
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }
    }

    /**
     * Hide upload progress
     */
    hideUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }

    /**
     * Update upload progress
     */
    updateUploadProgress(index, progress, status) {
        const progressBar = document.querySelector(`#uploadProgress .upload-progress-item:nth-child(${index + 1}) .upload-progress-fill`);
        const statusEl = document.querySelector(`#uploadProgress .upload-progress-item:nth-child(${index + 1}) .upload-progress-status`);
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        if (statusEl) {
            statusEl.textContent = status;
        }
    }

    /**
     * Reset upload form
     */
    resetUploadForm() {
        this.uploadQueue = [];
        this.updateFileList();
        
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.value = '';
        }
        
        this.hideUploadProgress();
    }

    /**
     * Remove file from upload queue
     */
    removeFileFromQueue(index) {
        this.uploadQueue.splice(index, 1);
        this.updateFileList();
    }

    /**
     * Export file data
     */
    exportFileData() {
        // Mock export functionality
        const data = {
            timestamp: new Date().toISOString(),
            totalFiles: 1247,
            filters: this.filters
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `file_export_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showSuccessMessage('File data exported successfully');
    }

    /**
     * Show bulk upload modal
     */
    showBulkUploadModal() {
        const modal = new bootstrap.Modal(document.getElementById('bulkUploadModal'));
        modal.show();
    }

    /**
     * Bulk actions
     */
    async bulkAction(action) {
        if (this.selectedFiles.size === 0) {
            this.showErrorMessage('No files selected');
            return;
        }

        const actionNames = {
            'activate': 'activate',
            'archive': 'archive',
            'delete': 'delete',
            'download': 'download'
        };

        const actionName = actionNames[action];
        if (!actionName) {
            this.showErrorMessage('Invalid action');
            return;
        }

        try {
            // Mock bulk action
            await this.performBulkAction(action, Array.from(this.selectedFiles));
            
            this.showSuccessMessage(`Successfully ${actionName}d ${this.selectedFiles.size} files`);
            this.selectedFiles.clear();
            this.updateBulkActions();
            
            // Refresh file list
            this.loadFileData();
            
        } catch (error) {
            console.error(`Bulk ${action} error:`, error);
            this.showErrorMessage(`Failed to ${action} some files`);
        }
    }

    /**
     * Perform bulk action
     */
    async performBulkAction(action, fileIds) {
        // Mock API call - replace with actual implementation
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log(`Performing bulk ${action} on files:`, fileIds);
                resolve({ success: true, processed: fileIds.length });
            }, 1000);
        });
    }

    /**
     * Clear file search
     */
    clearFileSearch() {
        const searchInput = document.getElementById('fileSearchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        
        // Reset all filters
        this.filters = {
            type: '',
            project: '',
            tags: '',
            status: '',
            dateFrom: '',
            dateTo: '',
            search: ''
        };
        
        // Reset filter selects
        const filterSelects = document.querySelectorAll('#fileTypeFilter, #fileProjectFilter, #fileStatusFilter');
        filterSelects.forEach(select => {
            select.value = '';
        });
        
        // Reset date inputs
        const dateInputs = document.querySelectorAll('#fileDateFrom, #fileDateTo');
        dateInputs.forEach(input => {
            input.value = '';
        });
        
        // Refresh filter
        this.filterFiles();
    }

    /**
     * Change file page
     */
    changeFilePage(page) {
        if (page < 1) return;
        
        this.currentPage = page;
        // In a real implementation, you would fetch data for the new page
        // For now, just scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Animate metrics
     */
    animateMetrics() {
        const metricElements = document.querySelectorAll('.dp-metric-content h4');
        metricElements.forEach(element => {
            const finalValue = element.textContent;
            const numericValue = parseFloat(finalValue.replace(/[^\d.]/g, ''));
            
            if (!isNaN(numericValue)) {
                element.textContent = '0';
                this.animateNumber(element, 0, numericValue, 1000);
            }
        });
    }

    /**
     * Animate number
     */
    animateNumber(element, start, end, duration) {
        const startTime = performance.now();
        
        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Show success message
     */
    showSuccessMessage(message) {
        // In a real application, you'd use a toast notification system
        console.log('✅ Success:', message);
        // You can implement a toast notification here
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        // In a real application, you'd use a toast notification system
        console.error('❌ Error:', message);
        // You can implement a toast notification here
    }

    /**
     * View file details
     */
    viewFileDetails(fileId) {
        // Mock implementation - replace with actual modal display
        console.log(`Viewing details for file: ${fileId}`);
        this.showSuccessMessage(`Viewing details for file: ${fileId}`);
    }

    /**
     * Download file
     */
    downloadFile(fileId) {
        // Mock implementation - replace with actual download
        console.log(`Downloading file: ${fileId}`);
        this.showSuccessMessage(`Downloading file: ${fileId}`);
    }

    /**
     * Edit file
     */
    editFile(fileId) {
        // Mock implementation - replace with actual edit modal
        console.log(`Editing file: ${fileId}`);
        this.showSuccessMessage(`Editing file: ${fileId}`);
    }

    /**
     * Delete file
     */
    deleteFile(fileId) {
        // Mock implementation - replace with actual delete confirmation
        if (confirm('Are you sure you want to delete this file?')) {
            console.log(`Deleting file: ${fileId}`);
            this.showSuccessMessage(`File deleted: ${fileId}`);
            // Refresh file list
            this.loadFileData();
        }
    }

    /**
     * Cleanup resources
     */
    destroy() {
        // Remove event listeners
        console.log('🧹 File Operations Module destroyed');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FileOperationsModule;
} else if (typeof window !== 'undefined') {
    window.FileOperationsModule = FileOperationsModule;
}
