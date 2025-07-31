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
            this.showUseCases();
        });

        // Use case click handler
        $(document).on('click', '.use-case-card', (e) => {
            const useCaseId = $(e.currentTarget).data('use-case-id');
            this.selectUseCase(useCaseId);
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
        const fileCount = project.files ? project.files.length : 0;
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
                        <button class="btn btn-sm btn-outline-primary" onclick="viewProject('${project.id}')">
                            <i class="fas fa-eye me-1"></i>View
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="uploadToProject('${project.id}')">
                            <i class="fas fa-upload me-1"></i>Upload
                        </button>
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
                        <div class="use-case-stats">
                            <small class="text-muted">
                                <i class="fas fa-folder me-1"></i>${projectCount} projects
                            </small>
                        </div>
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
        
        // Render projects by category
        let html = '';
        const categories = this.groupProjectsByCategory(useCase.projects);
        Object.keys(categories).forEach(category => {
            html += this.renderProjectCategory(category, categories[category]);
        });
        
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

    showDatabaseError(message) {
        showError(message);
        console.error('Database Error:', message);
    }
}

// Export the class
export default DataManager;