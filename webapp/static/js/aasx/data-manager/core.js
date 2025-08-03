/**
 * AASX Data Manager Core
 * Main DataManager class for managing data, use cases, and projects
 */

import { formatFileSize, getFileStatusInfo, getStatusBadgeColor } from '../../shared/utils.js';
import { showSuccess, showError, showWarning } from '../../shared/alerts.js';

export class DataManager {
    constructor() {
        this.projects = [];
        this.useCases = [];
        this.categories = {};
        this.selectedUseCase = null;
        this.autoRefreshInterval = null;
    }

    async init() {
        console.log('🚀 Data Manager initializing...');
        
        try {
            this.setupEventListeners();
            this.initFlowChart();
            await this.loadProjects();
            this.startAutoRefresh();
            
            console.log('✅ Data Manager initialized successfully');
        } catch (error) {
            console.error('❌ Data Manager initialization failed:', error);
        }
    }

    setupEventListeners() {
        // Back to use cases button
        $(document).on('click', '#backToUseCases', () => {
            this.showUseCasesSimple();
        });

        // Use case click handler
        $(document).on('click', '.use-case-card', (e) => {
            const useCaseId = $(e.currentTarget).data('use-case-id');
            this.selectUseCase(useCaseId);
        });

        // Project view button handler
        $(document).on('click', '.btn-view-project', (e) => {
            e.preventDefault();
            const projectId = $(e.currentTarget).data('project-id');
            this.viewProject(projectId);
        });

        // Project upload button handler
        $(document).on('click', '.btn-upload-project', (e) => {
            e.preventDefault();
            const projectId = $(e.currentTarget).data('project-id');
            this.uploadToProject(projectId);
        });

        // Project delete button handler
        $(document).on('click', '.btn-delete-project', (e) => {
            e.preventDefault();
            const projectId = $(e.currentTarget).data('project-id');
            this.deleteProject(projectId);
        });

        console.log('📋 Event listeners setup complete');
    }

    // Initialize flow chart
    initFlowChart() {
        this.addFlowStepTooltips();
        
        // Add click handlers for flow steps
        $('.flow-step').on('click', function() {
            const stepNumber = $(this).index() / 2 + 1;
            const stepActions = {
                1: () => $('#fileUpload').click(),
                2: () => $('#createProject').click(),
                3: () => $('#refreshFiles').click(),
                4: () => $('.category-card').first().click(),
                5: () => window.location.href = '/aasx/analytics'
            };
            
            if (stepActions[stepNumber]) {
                stepActions[stepNumber]();
            }
        });
        
        // Add cursor pointer to flow steps
        $('.flow-step').css('cursor', 'pointer');
        
        // Initialize Mermaid flowchart
        this.initMermaidFlowchart();
    }

    // Initialize Mermaid flowchart
    initMermaidFlowchart() {
        try {
            // Configure Mermaid
            if (typeof mermaid !== 'undefined') {
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default',
                    flowchart: {
                        useMaxWidth: true,
                        htmlLabels: true,
                        curve: 'basis'
                    },
                    themeVariables: {
                        primaryColor: '#007bff',
                        primaryTextColor: '#ffffff',
                        primaryBorderColor: '#0056b3',
                        lineColor: '#333333',
                        secondaryColor: '#28a745',
                        tertiaryColor: '#ffc107'
                    }
                });
                
                // Render the flowchart
                mermaid.init(undefined, '.mermaid');
                
                console.log('✅ Mermaid flowchart initialized successfully');
            } else {
                console.warn('⚠️ Mermaid not available, using fallback');
                this.showFlowchartFallback();
            }
            
        } catch (error) {
            console.error('❌ Failed to initialize Mermaid flowchart:', error);
            // Fallback: show a simple text representation
            this.showFlowchartFallback();
        }
    }

    // Fallback for when Mermaid fails to load
    showFlowchartFallback() {
        const fallbackHtml = `
            <div class="flowchart-fallback">
                <div class="text-center">
                    <h6 class="text-primary mb-3">Data Management Hierarchy</h6>
                    <div class="hierarchy-tree">
                        <div class="level-1">
                            <div class="node primary">📊 Data Management</div>
                            <div class="arrow">↓</div>
                        </div>
                        <div class="level-2">
                            <div class="node success">🔥 Thermal Analysis</div>
                            <div class="node warning">🏗️ Structural Analysis</div>
                            <div class="node info">💧 Fluid Dynamics</div>
                            <div class="node secondary">🔗 Multi-Physics</div>
                            <div class="node dark">🏭 Industrial Applications</div>
                        </div>
                        <div class="arrow">↓</div>
                        <div class="level-3">
                            <div class="node light">📁 Projects</div>
                        </div>
                        <div class="arrow">↓</div>
                        <div class="level-4">
                            <div class="node light">📄 AASX Files</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('.mermaid').html(fallbackHtml);
    }

    // Add tooltips to flow steps
    addFlowStepTooltips() {
        $('.flow-step').each(function() {
            const stepNumber = $(this).index() / 2 + 1;
            const tooltips = {
                1: 'Upload AASX files to get started',
                2: 'Create a new project to organize your files',
                3: 'Refresh to see your uploaded files',
                4: () => $('.category-card').first().attr('title'), // Tooltip for category card
                5: 'View analytics and insights'
            };
            
            if (tooltips[stepNumber]) {
                $(this).attr('title', tooltips[stepNumber]);
            }
        });
    }

    async loadProjects() {
        console.log('🔄 Loading projects and use cases...');
        
        try {
            // Load both projects and use cases
            const [projectsResponse, useCasesResponse] = await Promise.all([
                fetch('/api/aasx/projects'),
                fetch('/api/aasx/use-cases')
            ]);
            
            console.log('📡 Projects response status:', projectsResponse.status);
            console.log('📡 Use cases response status:', useCasesResponse.status);
            
            if (projectsResponse.ok && useCasesResponse.ok) {
                this.projects = await projectsResponse.json();
                this.useCases = await useCasesResponse.json();
                
                console.log('📦 Loaded projects:', this.projects.length);
                console.log('📋 Loaded use cases:', this.useCases.length);
                
                if (this.projects.length > 0) {
                    console.log('🔍 Sample project structure:', this.projects[0]);
                }
                
                // Group projects by use case (now async)
                await this.groupProjectsByUseCase();
                
                // Show use cases by default
                await this.showUseCases();
                
                // Update stats
                await this.updateStats();
                
            } else {
                console.error('❌ API calls failed:', {
                    'Projects API': projectsResponse.status + ' ' + projectsResponse.statusText,
                    'Use Cases API': useCasesResponse.status + ' ' + useCasesResponse.statusText
                });
                this.showDatabaseError('Failed to load data from database. Please ensure the database is properly initialized.');
            }
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.showDatabaseError('Database error while loading data');
        }
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        this.autoRefreshInterval = setInterval(() => {
            this.autoRefresh();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    async autoRefresh() {
        await this.loadProjects();
    }

    async refreshAndSync() {
        try {
            const response = await fetch('/aasx/api/projects/sync', {
                method: 'POST'
            });
            
            if (response.ok) {
                showSuccess('Projects synchronized successfully!');
                await this.loadProjects();
            } else {
                showError('Failed to synchronize projects');
            }
        } catch (error) {
            showError(`Sync error: ${error.message}`);
        }
    }

    // Utility methods
    showSuccessMessage(message) {
        if (typeof showSuccess === 'function') {
            showSuccess(message);
        } else {
            console.log('✅', message);
        }
    }

    showErrorMessage(message) {
        if (typeof showError === 'function') {
            showError(message);
        } else {
            console.error('❌', message);
        }
    }

    showWarningMessage(message) {
        if (typeof showWarning === 'function') {
            showWarning(message);
        } else {
            console.warn('⚠️', message);
        }
    }

    // Cleanup method
    destroy() {
        this.stopAutoRefresh();
        this.isInitialized = false;
        console.log('🧹 Project Manager destroyed');
    }

    // Database error handler
    showDatabaseError(message) {
        if (typeof showError === 'function') {
            showError(message);
        } else {
            console.error('❌ Database Error:', message);
        }
    }

    // Update stats with fallback values
    async updateStatsWithFallback() {
        console.log('📊 Stats API not available, using fallback values');
        
        const stats = {
            total_projects: 0,
            total_files: 0,
            processed_files: 0,
            success_rate: 0.0,
            last_updated: new Date().toISOString()
        };
        
        // Update UI with fallback stats
        $('#totalProjects').text(stats.total_projects);
        $('#totalFiles').text(stats.total_files);
        $('#processedFiles').text(stats.processed_files);
        $('#successRate').text(stats.success_rate.toFixed(1) + '%');
        
        return stats;
    }

    // Update stats from API
    async updateStats() {
        try {
            const response = await fetch('/api/aasx/stats');
            if (response.ok) {
                const stats = await response.json();
                
                // Update UI
                $('#totalProjects').text(stats.total_projects);
                $('#totalFiles').text(stats.total_files);
                $('#processedFiles').text(stats.processed_files);
                $('#successRate').text(stats.success_rate.toFixed(1) + '%');
                
                return stats;
            } else {
                console.error('Stats API failed:', response.status, response.statusText);
                this.showDatabaseError('Failed to load statistics from database');
                return this.updateStatsWithFallback();
            }
        } catch (error) {
            console.error('Error updating stats:', error);
            this.showDatabaseError('Database error while loading statistics');
            return this.updateStatsWithFallback();
        }
    }

    // Group projects by category
    groupProjectsByCategory(projects = null) {
        const projectsToGroup = projects || this.projects;
        const categories = {};
        
        projectsToGroup.forEach(project => {
            const category = project.category || 'uncategorized';
            if (!categories[category]) {
                categories[category] = [];
            }
            categories[category].push(project);
        });
        
        return categories;
    }

    // Group projects by use case
    async groupProjectsByUseCase() {
        const useCasesWithProjects = [];
        
        for (const useCase of this.useCases) {
            try {
                // Load projects for each use case using the same API as dropdown manager
                console.log(`🔍 Data Manager: Loading projects for use case ${useCase.id} (${useCase.name})`);
                const response = await fetch(`/api/aasx/use-cases/${useCase.id}/projects`);
                if (response.ok) {
                    const projects = await response.json();
                    console.log(`📁 Data Manager: Raw projects response for ${useCase.name}:`, projects);
                    
                    // Debug: Check file_count for each project
                    projects.forEach(project => {
                        console.log(`🔍 Project ${project.name}: file_count = ${project.file_count}, files array length = ${project.files ? project.files.length : 'no files array'}`);
                    });
                    
                    useCasesWithProjects.push({
                        id: useCase.id,
                        name: useCase.name,
                        description: useCase.description,
                        projects: projects
                    });
                    console.log(`📁 Data Manager: Loaded ${projects.length} projects for use case: ${useCase.name}`);
                    console.log(`📋 Data Manager: Project names:`, projects.map(p => p.name));
                } else {
                    console.warn(`Failed to load projects for use case: ${useCase.name}`);
                    useCasesWithProjects.push({
                        id: useCase.id,
                        name: useCase.name,
                        description: useCase.description,
                        projects: []
                    });
                }
            } catch (error) {
                console.error(`Error loading projects for use case ${useCase.name}:`, error);
                useCasesWithProjects.push({
                    id: useCase.id,
                    name: useCase.name,
                    description: useCase.description,
                    projects: []
                });
            }
        }
        
        this.useCases = useCasesWithProjects;
        return this.useCases;
    }

    // Render projects in the UI (legacy method - now handled by showProjectsForUseCase)
    renderProjects() {
        const container = $('#projectsContainer');
        if (!container.length) {
            console.warn('Projects container not found');
            return;
        }
        
        if (this.projects.length === 0) {
            container.html(`
                <div class="text-center py-5">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No projects found</h5>
                    <p class="text-muted">Create your first project to get started</p>
                    <button class="btn btn-primary" onclick="showCreateProjectModal()">
                        <i class="fas fa-plus me-2"></i>Create Project
                    </button>
                </div>
            `);
            return;
        }
        
        // Render projects by category
        let html = '';
        Object.keys(this.categories).forEach(category => {
            html += this.renderProjectCategory(category, this.categories[category]);
        });
        
        container.html(html);
    }

    // Render a project category
    renderProjectCategory(category, projects) {
        const categoryName = category.charAt(0).toUpperCase() + category.slice(1);
        const categoryIcon = this.getCategoryIcon(category);
        
        let html = `
            <div class="category-section mb-4">
                <h5 class="category-title">
                    <i class="${categoryIcon} me-2"></i>${categoryName}
                    <span class="badge bg-primary ms-2">${projects.length}</span>
                </h5>
                <div class="row">
        `;
        
        projects.forEach(project => {
            html += this.renderProjectCard(project);
        });
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }

    // Render a single project card
    renderProjectCard(project) {
        console.log(`🔍 renderProjectCard: Project ${project.name}:`, project);
        console.log(`🔍 renderProjectCard: file_count = ${project.file_count}, type = ${typeof project.file_count}`);
        
        const fileCount = project.file_count || 0;
        const status = project.status || 'active';
        const statusColor = this.getStatusColor(status);
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card project-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">${project.name}</h6>
                            <span class="badge bg-${statusColor}">${status}</span>
                        </div>
                        <p class="card-text text-muted small">${project.description || 'No description'}</p>
                        <div class="project-stats">
                            <small class="text-muted">
                                <i class="fas fa-file me-1"></i>${fileCount} files
                            </small>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent">
                        <div class="d-flex gap-1 justify-content-center">
                            <button class="btn btn-xs btn-outline-primary btn-view-project" data-project-id="${project.project_id}" title="View Project Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-xs btn-outline-success btn-upload-project" data-project-id="${project.project_id}" title="Upload Files">
                                <i class="fas fa-upload"></i>
                            </button>
                            <button class="btn btn-xs btn-outline-danger btn-delete-project" data-project-id="${project.project_id}" title="Delete Project">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Show use cases in the UI
    async showUseCases() {
        const container = $('#useCasesContainer');
        const projectsSection = $('#projectsSection');
        
        if (!container.length) {
            console.warn('Use cases container not found');
            return;
        }
        
        // Hide projects section, show use cases
        projectsSection.hide();
        container.show(); // Make sure use cases container is visible
        
        // Show loading state
        container.html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5 class="text-muted">Loading Use Cases...</h5>
                <p class="text-muted">Please wait while we load the use cases</p>
            </div>
        `);
        
        try {
            // Group projects by use case (now async)
            const useCasesWithProjects = await this.groupProjectsByUseCase();
            
            if (useCasesWithProjects.length === 0) {
                container.html(`
                    <div class="text-center py-5">
                        <i class="fas fa-sitemap fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">No use cases found</h5>
                        <p class="text-muted">Create your first use case to get started</p>
                    </div>
                `);
                return;
            }
            
            // Render use cases
            let html = '<div class="row">';
            useCasesWithProjects.forEach(useCase => {
                html += this.renderUseCaseCard(useCase);
            });
            html += '</div>';
            
            container.html(html);
        } catch (error) {
            console.error('Error loading use cases:', error);
            container.html(`
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h5 class="text-danger">Error Loading Use Cases</h5>
                    <p class="text-muted">Please refresh the page to try again</p>
                </div>
            `);
        }
    }

    // Simple method to show use cases without reloading data
    showUseCasesSimple() {
        const container = $('#useCasesContainer');
        const projectsSection = $('#projectsSection');
        
        if (!container.length) {
            console.warn('Use cases container not found');
            return;
        }
        
        // Hide projects section, show use cases
        projectsSection.hide();
        container.show();
        
        // Render use cases from existing data
        if (!this.useCases || this.useCases.length === 0) {
            container.html(`
                <div class="text-center py-5">
                    <i class="fas fa-sitemap fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No use cases found</h5>
                    <p class="text-muted">Create your first use case to get started</p>
                </div>
            `);
            return;
        }
        
        // Render use cases
        let html = '<div class="row">';
        this.useCases.forEach(useCase => {
            html += this.renderUseCaseCard(useCase);
        });
        html += '</div>';
        
        container.html(html);
    }

    // Render a single use case card
    renderUseCaseCard(useCase) {
        const projectCount = useCase.projects ? useCase.projects.length : 0;
        const categoryIcon = this.getCategoryIcon(useCase.category || 'general');
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card use-case-card h-100" data-use-case-id="${useCase.id}" style="cursor: pointer;">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">
                                <i class="${categoryIcon} me-2"></i>${useCase.name}
                            </h6>
                            <span class="badge bg-primary">${projectCount} projects</span>
                        </div>
                        <p class="card-text text-muted small">${useCase.description || 'No description'}</p>
                    </div>
                    <div class="card-footer bg-transparent">
                        <button class="btn btn-sm btn-outline-primary w-100">
                            <i class="fas fa-eye me-1"></i>View Projects
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    // Handle use case selection
    selectUseCase(useCaseId) {
        const useCase = this.useCases.find(uc => uc.id === useCaseId);
        if (!useCase) {
            console.error('Use case not found:', useCaseId);
            return;
        }
        
        this.selectedUseCase = useCase;
        this.showProjectsForUseCase(useCase);
    }

    // Show projects for a specific use case
    showProjectsForUseCase(useCase) {
        const projectsSection = $('#projectsSection');
        const useCasesContainer = $('#useCasesContainer');
        const selectedUseCaseName = $('#selectedUseCaseName');
        const projectsContainer = $('#projectsContainer');
        
        // Update UI
        selectedUseCaseName.text(useCase.name);
        useCasesContainer.hide();
        projectsSection.show();
        
        console.log(`🔍 showProjectsForUseCase: Use case ${useCase.name} has ${useCase.projects ? useCase.projects.length : 0} projects`);
        if (useCase.projects) {
            useCase.projects.forEach(project => {
                console.log(`🔍 Project ${project.name}: file_count = ${project.file_count}`);
            });
        }
        
        // Render projects
        if (!useCase.projects || useCase.projects.length === 0) {
            projectsContainer.html(`
                <div class="text-center py-5">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No projects found</h5>
                    <p class="text-muted">This use case has no projects yet</p>
                    <button class="btn btn-primary" onclick="showCreateProjectModal()">
                        <i class="fas fa-plus me-2"></i>Create Project
                    </button>
                </div>
            `);
            return;
        }
        
        // Render projects directly (no category grouping needed for use case view)
        let html = '<div class="row">';
        useCase.projects.forEach(project => {
            html += this.renderProjectCard(project);
        });
        html += '</div>';
        
        projectsContainer.html(html);
    }

    // Get category icon
    getCategoryIcon(category) {
        const icons = {
            'thermal': 'fas fa-fire',
            'structural': 'fas fa-cube',
            'fluid': 'fas fa-water',
            'multi_physics': 'fas fa-atom',
            'industrial': 'fas fa-industry',
            'applications': 'fas fa-cogs',
            'physics': 'fas fa-atom',
            'general': 'fas fa-chart-line'
        };
        return icons[category] || 'fas fa-folder';
    }

    // Get status color
    getStatusColor(status) {
        const colors = {
            'active': 'success',
            'inactive': 'secondary',
            'error': 'danger',
            'processing': 'warning'
        };
        return colors[status] || 'secondary';
    }

    // Update project selects
    updateProjectSelects() {
        const selects = ['#uploadProjectSelect', '#urlProjectSelect', '#etlProjectSelect'];
        
        selects.forEach(selectId => {
            const select = $(selectId);
            if (select.length) {
                select.empty();
                select.append('<option value="">Select a project...</option>');
                
                this.projects.forEach(project => {
                    select.append(`<option value="${project.id}">${project.name}</option>`);
                });
            }
        });
    }

    // View project details
    viewProject(projectId) {
        console.log(`🔍 Viewing project: ${projectId}`);
        
        // Find the project
        const project = this.findProjectById(projectId);
        if (!project) {
            showError('Project not found');
            return;
        }
        
        // Show project details modal or navigate to project details page
        this.showProjectDetails(project);
    }

    // Upload to project
    uploadToProject(projectId) {
        console.log(`📤 Uploading to project: ${projectId}`);
        
        // Find the project
        const project = this.findProjectById(projectId);
        if (!project) {
            showError('Project not found');
            return;
        }
        
        // Navigate to file upload section with pre-selected project
        this.navigateToUploadWithProject(project);
    }

    // Delete project
    async deleteProject(projectId) {
        console.log(`🗑️ Deleting project: ${projectId}`);
        
        // Find the project
        const project = this.findProjectById(projectId);
        if (!project) {
            showError('Project not found');
            return;
        }
        
        // Show confirmation dialog
        const confirmed = await this.showDeleteConfirmation(project);
        if (!confirmed) {
            return;
        }
        
        // Delete the project
        await this.performProjectDeletion(project);
    }

    // Find project by ID across all use cases
    findProjectById(projectId) {
        for (const useCase of this.useCases) {
            if (useCase.projects) {
                const project = useCase.projects.find(p => p.project_id === projectId);
                if (project) {
                    return { ...project, useCase: useCase };
                }
            }
        }
        return null;
    }

    // Show project details
    async showProjectDetails(project) {
        console.log(`🔍 showProjectDetails: Loading details for project ${project.name}`);
        
        // Show loading state first
        const modalHtml = `
            <div class="modal fade" id="projectDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-folder me-2"></i>${project.name}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center py-4">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p class="mt-2">Loading project details...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        $('#projectDetailsModal').remove();
        
        // Add modal to body and show it
        $('body').append(modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('projectDetailsModal'));
        modal.show();
        
        try {
            // Fetch detailed project information including files
            const response = await fetch(`/api/aasx/projects/${project.project_id}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch project details: ${response.status}`);
            }
            
            const projectDetails = await response.json();
            console.log(`🔍 Project details loaded:`, projectDetails);
            
            // Update modal with detailed information
            this.updateProjectDetailsModal(projectDetails);
            
        } catch (error) {
            console.error('❌ Error loading project details:', error);
            this.updateProjectDetailsModal(project, error.message);
        }
    }
    
    // Update project details modal with comprehensive information
    updateProjectDetailsModal(projectDetails, errorMessage = null) {
        const modalBody = $('#projectDetailsModal .modal-body');
        
        if (errorMessage) {
            modalBody.html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading project details: ${errorMessage}
                </div>
            `);
            return;
        }
        
        const files = projectDetails.files || [];
        const useCase = projectDetails.use_case;
        
        const modalContent = `
            <div class="row mb-4">
                <div class="col-md-8">
                    <h6>Description</h6>
                    <p class="text-muted">${projectDetails.description || 'No description available'}</p>
                    
                    <h6>Project Details</h6>
                    <ul class="list-unstyled">
                        <li><strong>Project ID:</strong> <code>${projectDetails.project_id}</code></li>
                        <li><strong>Status:</strong> <span class="badge bg-${this.getStatusColor(projectDetails.status || 'active')}">${projectDetails.status || 'active'}</span></li>
                        <li><strong>Files:</strong> ${files.length} files</li>
                        <li><strong>Created:</strong> ${new Date(projectDetails.created_at).toLocaleDateString()}</li>
                        <li><strong>Last Updated:</strong> ${new Date(projectDetails.updated_at).toLocaleDateString()}</li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h6>Use Case</h6>
                    <p class="text-primary">${useCase ? useCase.name : 'Unknown'}</p>
                    
                    <h6>Tags</h6>
                    <div class="mb-3">
                        ${this.renderTags(projectDetails.tags)}
                    </div>
                    
                    <h6>Metadata</h6>
                    <div class="mb-3">
                        ${this.renderMetadata(projectDetails.metadata)}
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <h6>Files in Project</h6>
                    ${this.renderProjectFiles(files)}
                </div>
            </div>
        `;
        
                 modalBody.html(modalContent);
         
         // Add modal footer
         const modalFooter = `
             <div class="modal-footer">
                 <button type="button" class="btn btn-danger" onclick="dataManager.deleteProject('${projectDetails.project_id}')">
                     <i class="fas fa-trash me-1"></i>Delete Project
                 </button>
                 <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                 <button type="button" class="btn btn-primary" onclick="dataManager.uploadToProject('${projectDetails.project_id}')">
                     <i class="fas fa-upload me-1"></i>Upload Files
                 </button>
             </div>
         `;
         
         modalBody.after(modalFooter);
     }
    
    // Render project files with detailed information
    renderProjectFiles(files) {
        if (!files || files.length === 0) {
            return `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No files uploaded to this project yet.
                </div>
            `;
        }
        
        let filesHtml = '<div class="table-responsive"><table class="table table-hover">';
        filesHtml += `
            <thead class="table-light">
                <tr>
                    <th style="min-width: 200px; color: #000; font-weight: 600;">File Name</th>
                    <th style="min-width: 100px; color: #000; font-weight: 600;">Status</th>
                    <th style="min-width: 140px; color: #000; font-weight: 600;">Federated Learning</th>
                    <th style="min-width: 80px; color: #000; font-weight: 600;">Size</th>
                    <th style="min-width: 100px; color: #000; font-weight: 600;">Upload Date</th>
                    <th style="min-width: 120px; color: #000; font-weight: 600;">Actions</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        files.forEach(file => {
            const statusColor = this.getFileStatusColor(file.status);
            const federatedLearningColor = this.getFederatedLearningColor(file.federated_learning);
            const fileSize = this.formatFileSize(file.size);
            const uploadDate = new Date(file.upload_date).toLocaleDateString();
            
            filesHtml += `
                <tr>
                    <td>
                        <div class="d-flex flex-column">
                            <strong class="text-break">${file.filename}</strong>
                            ${file.original_filename !== file.filename ? `<small class="text-muted text-break">Original: ${file.original_filename}</small>` : ''}
                        </div>
                    </td>
                    <td>
                        <span class="badge bg-${statusColor} fs-6">${file.status || 'unknown'}</span>
                    </td>
                    <td>
                        <span class="badge bg-${federatedLearningColor} fs-6">${file.federated_learning || 'not_allowed'}</span>
                    </td>
                    <td>${fileSize}</td>
                    <td>${uploadDate}</td>
                    <td>
                        <div class="d-flex gap-1">
                            <button class="btn btn-outline-primary btn-sm" onclick="dataManager.viewFileDetails('${file.file_id}')" title="View File Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="dataManager.deleteFile('${file.file_id}')" title="Delete File">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        filesHtml += '</tbody></table></div>';
        return filesHtml;
    }
    
    // Get color for file status
    getFileStatusColor(status) {
        const colors = {
            'not_processed': 'warning',
            'processing': 'info',
            'processed': 'success',
            'failed': 'danger',
            'error': 'danger'
        };
        return colors[status] || 'secondary';
    }
    
    // Get color for federated learning status
    getFederatedLearningColor(federatedLearning) {
        const colors = {
            'allowed': 'success',
            'not_allowed': 'danger',
            'conditional': 'warning'
        };
        return colors[federatedLearning] || 'secondary';
    }
    
    // Format file size
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    // Render metadata
    renderMetadata(metadata) {
        if (!metadata) {
            return '<p class="text-muted small">No metadata available</p>';
        }
        
        try {
            const metadataObj = typeof metadata === 'string' ? JSON.parse(metadata) : metadata;
            let html = '<div class="small">';
            Object.entries(metadataObj).forEach(([key, value]) => {
                html += `<div><strong>${key}:</strong> ${value}</div>`;
            });
            html += '</div>';
            return html;
        } catch (e) {
            return '<p class="text-muted small">Invalid metadata format</p>';
        }
        }
    
    // View file details
    viewFileDetails(fileId) {
        console.log(`🔍 Viewing file details for file ID: ${fileId}`);
        // TODO: Implement file details view
        showInfo('File details view will be implemented soon');
    }
    
    // Delete file
    async deleteFile(fileId) {
        console.log(`🗑️ Deleting file with ID: ${fileId}`);
        if (confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
            try {
                const response = await fetch(`/api/aasx/files/${fileId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    showSuccess('File deleted successfully');
                    // Refresh the current view
                    await this.refreshCurrentView();
                } else {
                    showError('Failed to delete file');
                }
            } catch (error) {
                console.error('Error deleting file:', error);
                showError('Error deleting file');
            }
        }
    }
    
    // Navigate to upload section with pre-selected project
    navigateToUploadWithProject(project) {
        // Scroll to file upload section
        const uploadSection = $('.card-header:contains("File Upload & Management")').closest('.card');
        if (uploadSection.length) {
            $('html, body').animate({
                scrollTop: uploadSection.offset().top - 100
            }, 500);
            
            // Pre-select the use case and project in upload dropdowns
            setTimeout(() => {
                this.preSelectUploadOptions(project);
            }, 600);
        } else {
            showError('File upload section not found');
        }
    }

    // Pre-select upload options
    preSelectUploadOptions(project) {
        // Find the use case ID for this project
        const useCaseId = project.useCase ? project.useCase.id : null;
        
        if (useCaseId) {
            // Select use case in upload dropdowns
            $('.use-case-select').val(useCaseId).trigger('change');
            
            // Wait for projects to load, then select the project
            setTimeout(() => {
                $('.project-select').val(project.project_id).trigger('change');
            }, 1000);
            
            showSuccess(`Ready to upload files to "${project.name}"`);
        }
    }

    // Show delete confirmation dialog
    showDeleteConfirmation(project) {
        return new Promise((resolve) => {
            const modalHtml = `
                <div class="modal fade" id="deleteConfirmationModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">
                                    <i class="fas fa-exclamation-triangle me-2"></i>Delete Project
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="text-center mb-3">
                                    <i class="fas fa-trash fa-3x text-danger mb-3"></i>
                                    <h5>Are you sure you want to delete this project?</h5>
                                </div>
                                <div class="alert alert-warning">
                                    <strong>Project:</strong> ${project.name}<br>
                                    <strong>Use Case:</strong> ${project.useCase ? project.useCase.name : 'Unknown'}<br>
                                    <strong>Files:</strong> ${project.file_count || 0} files
                                </div>
                                <div class="alert alert-danger">
                                    <i class="fas fa-exclamation-triangle me-1"></i>
                                    <strong>Warning:</strong> This action cannot be undone. All project files and data will be permanently deleted.
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                                    <i class="fas fa-trash me-1"></i>Delete Project
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            $('#deleteConfirmationModal').remove();
            
            // Add modal to body
            $('body').append(modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
            
            // Handle confirmation
            $('#confirmDeleteBtn').on('click', () => {
                modal.hide();
                resolve(true);
            });
            
            // Handle cancellation
            $('#deleteConfirmationModal').on('hidden.bs.modal', () => {
                resolve(false);
            });
            
            modal.show();
        });
    }

    // Perform project deletion
    async performProjectDeletion(project) {
        try {
            // Show loading state
            showWarning('Deleting project...');
            
            // Call API to delete project
            const response = await fetch(`/api/aasx/projects/${project.project_id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                showSuccess(`Project "${project.name}" deleted successfully`);
                
                // Remove project from local data
                this.removeProjectFromData(project.project_id);
                
                // Refresh the current view
                await this.refreshCurrentView();
                
            } else {
                const errorData = await response.json();
                showError(`Failed to delete project: ${errorData.detail || 'Unknown error'}`);
            }
            
        } catch (error) {
            console.error('Error deleting project:', error);
            showError('Failed to delete project. Please try again.');
        }
    }

    // Remove project from local data
    removeProjectFromData(projectId) {
        for (const useCase of this.useCases) {
            if (useCase.projects) {
                const projectIndex = useCase.projects.findIndex(p => p.project_id === projectId);
                if (projectIndex !== -1) {
                    useCase.projects.splice(projectIndex, 1);
                    break;
                }
            }
        }
    }

    // Refresh current view
    async refreshCurrentView() {
        // If we're viewing a specific use case, refresh that view
        if (this.selectedUseCase) {
            this.showProjectsForUseCase(this.selectedUseCase);
        } else {
            // If we're viewing all use cases, refresh that view
            await this.showUseCases();
        }
    }

    // Render tags
    renderTags(tags) {
        if (!tags) return '<span class="text-muted">No tags</span>';
        
        try {
            const tagArray = typeof tags === 'string' ? JSON.parse(tags) : tags;
            return tagArray.map(tag => 
                `<span class="badge bg-light text-dark me-1">${tag}</span>`
            ).join('');
        } catch (e) {
            return '<span class="text-muted">Invalid tags</span>';
        }
    }

    showDatabaseError(message) {
        showError(message);
        console.error('Database Error:', message);
    }
}

// Export the class
export default DataManager;