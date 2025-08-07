/**
 * Dropdown Manager for AASX Module
 * Manages dropdown functionality across the AASX module
 */

import { showError } from '/static/js/shared/alerts.js';

export class DropdownManager {
    constructor() {
        this.useCases = [];
        this.projects = [];
        this.files = [];
        this.currentUseCaseId = null;
        this.currentProjectId = null;
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) {
            console.log('⚠️ Dropdown Manager already initialized, skipping...');
            return;
        }
        
        console.log('🔄 Dropdown Manager initializing...');
        await this.loadUseCases();
        this.setupEventListeners();
        this.isInitialized = true;
        console.log('✅ Dropdown Manager initialized');
    }

    setupEventListeners() {
        // Use case selection handlers
        $('.use-case-select').on('change', (e) => {
            const useCaseId = $(e.target).val();
            this.onUseCaseChange(useCaseId, $(e.target).closest('.dropdown-section'));
        });

        // Project selection handlers
        $('.project-select').on('change', (e) => {
            const projectId = $(e.target).val();
            this.onProjectChange(projectId, $(e.target).closest('.dropdown-section'));
        });
    }

    async loadUseCases() {
        try {
            const response = await fetch('/api/aasx-etl/use-cases');
            if (response.ok) {
                this.useCases = await response.json();
                this.populateUseCaseDropdowns();
                console.log(`📋 Loaded ${this.useCases.length} use cases`);
            } else {
                console.error('Failed to load use cases');
            }
        } catch (error) {
            console.error('Error loading use cases:', error);
        }
    }

    async loadProjectsForUseCase(useCaseId) {
        try {
            console.log(`🔍 Dropdown Manager: Loading projects for use case ${useCaseId}`);
            const response = await fetch(`/api/aasx-etl/use-cases/${useCaseId}/projects`);
            if (response.ok) {
                this.projects = await response.json();
                console.log(`📁 Dropdown Manager: Loaded ${this.projects.length} projects for use case ${useCaseId}`);
                console.log(`📋 Dropdown Manager: Project names:`, this.projects.map(p => p.name));
                return this.projects;
            } else {
                console.error('Failed to load projects for use case');
                return [];
            }
        } catch (error) {
            console.error('Error loading projects:', error);
            return [];
        }
    }

    async loadFilesForProject(projectId) {
        try {
            const response = await fetch(`/api/aasx-etl/projects/${projectId}/files`);
            if (response.ok) {
                this.files = await response.json();
                console.log(`📄 Loaded ${this.files.length} files for project ${projectId}`);
                return this.files;
            } else {
                console.error('Failed to load files for project');
                return [];
            }
        } catch (error) {
            console.error('Error loading files:', error);
            return [];
        }
    }

    populateUseCaseDropdowns() {
        $('.use-case-select').each((index, element) => {
            const $select = $(element);
            $select.empty();
            $select.append('<option value="">Choose a use case...</option>');
            
            this.useCases.forEach(useCase => {
                $select.append(`<option value="${useCase.id}">${useCase.name}</option>`);
            });
        });
    }

    async populateProjectDropdown(useCaseId, container) {
        const $projectSelect = container.find('.project-select');
        $projectSelect.empty();
        $projectSelect.append('<option value="">Choose a project...</option>');
        
        if (!useCaseId) {
            $projectSelect.append('<option value="" disabled>Select a use case first to see available projects</option>');
            return;
        }

        const projects = await this.loadProjectsForUseCase(useCaseId);
        console.log(`🔧 Dropdown Manager: Populating dropdown with ${projects.length} projects`);
        projects.forEach(project => {
            $projectSelect.append(`<option value="${project.project_id}">${project.name}</option>`);
        });
        console.log(`✅ Dropdown Manager: Dropdown populated with ${$projectSelect.find('option').length - 1} project options`);
    }

    async populateFileDropdown(projectId, container) {
        const $fileSelect = container.find('.file-select');
        const $fileList = container.find('.file-list');
        
        if (!projectId) {
            $fileList.html('<p class="text-muted">Select a project to view available files for ETL processing</p>');
            return;
        }

        const files = await this.loadFilesForProject(projectId);
        const unprocessedFiles = files.filter(file => file.status !== 'processed');
        
        if (unprocessedFiles.length === 0) {
            $fileList.html('<p class="text-muted">No unprocessed files available for ETL processing</p>');
            return;
        }

        let html = '<div class="file-selection-list">';
        unprocessedFiles.forEach(file => {
            const statusColor = this.getFileStatusColor(file.status);
            const statusText = this.getFileStatusText(file.status);
            
            html += `
                <div class="file-item d-flex align-items-center p-2 border-bottom">
                    <div class="form-check me-3">
                        <input class="form-check-input file-checkbox" type="checkbox" 
                               value="${file.file_id}" id="file_${file.file_id}">
                    </div>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${file.filename}</h6>
                        <small class="text-muted">${file.description || 'No description'}</small>
                        <br>
                        <small class="text-muted">
                            <i class="fas fa-hdd me-1"></i>${this.formatFileSize(file.size || 0)}
                        </small>
                    </div>
                    <span class="badge ${statusColor}">${statusText}</span>
                </div>
            `;
        });
        html += '</div>';
        
        $fileList.html(html);
    }

    async onUseCaseChange(useCaseId, container) {
        this.currentUseCaseId = useCaseId;
        
        // Reset project selection
        const $projectSelect = container.find('.project-select');
        $projectSelect.val('');
        
        // Reset file selection
        const $fileList = container.find('.file-list');
        $fileList.empty();
        
        if (useCaseId) {
            await this.populateProjectDropdown(useCaseId, container);
        } else {
            $projectSelect.empty();
            $projectSelect.append('<option value="">Choose a project...</option>');
            $projectSelect.append('<option value="" disabled>Select a use case first to see available projects</option>');
        }
    }

    async onProjectChange(projectId, container) {
        this.currentProjectId = projectId;
        
        if (projectId) {
            await this.populateFileDropdown(projectId, container);
        } else {
            const $fileList = container.find('.file-list');
            $fileList.html('<p class="text-muted">Select a project to view available files for ETL processing</p>');
        }
    }

    getSelectedFiles(container) {
        const selectedFiles = [];
        container.find('.file-checkbox:checked').each(function() {
            selectedFiles.push($(this).val());
        });
        return selectedFiles;
    }

    getFileStatusColor(status) {
        const colors = {
            'processed': 'bg-success',
            'processing': 'bg-warning',
            'failed': 'bg-danger',
            'not_processed': 'bg-secondary'
        };
        return colors[status] || 'bg-secondary';
    }

    getFileStatusText(status) {
        const texts = {
            'processed': 'Processed',
            'processing': 'Processing',
            'failed': 'Failed',
            'not_processed': 'Pending'
        };
        return texts[status] || 'Unknown';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Public methods for external access
    getCurrentUseCaseId() {
        return this.currentUseCaseId;
    }

    getCurrentProjectId() {
        return this.currentProjectId;
    }

    getUseCases() {
        return this.useCases;
    }

    getProjects() {
        return this.projects;
    }

    getFiles() {
        return this.files;
    }

    destroy() {
        // Remove event listeners
        $('.use-case-select').off('change');
        $('.project-select').off('change');
        
        // Clear data
        this.useCases = [];
        this.projects = [];
        this.files = [];
        this.currentUseCaseId = null;
        this.currentProjectId = null;
        this.isInitialized = false;
        
        console.log('🧹 Dropdown Manager destroyed');
    }
}

// Global instance
export const dropdownManager = new DropdownManager(); 