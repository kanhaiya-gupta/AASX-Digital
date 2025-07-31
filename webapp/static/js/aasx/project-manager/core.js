/**
 * AASX Project Manager Core
 * Main ProjectManager class for managing projects and use cases
 */

import { formatFileSize, getFileStatusInfo, getStatusBadgeColor } from '../../shared/utils.js';
import { showSuccess, showError, showWarning } from '../../shared/alerts.js';

export class ProjectManager {
    constructor() {
        this.projects = [];
        this.useCases = [];
        this.categories = {};
        this.isInitialized = false;
        this.autoRefreshInterval = null;
        this.progressInterval = null;
    }

    async init() {
        console.log('🚀 Project Manager initializing...');
        
        try {
            // Initialize alert system
            if (typeof initAlertSystem === 'function') {
                initAlertSystem();
            }
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize flow chart
            this.initFlowChart();
            
            // Load initial data
            await this.loadProjects();
            
            // Start auto-refresh
            this.startAutoRefresh();
            
            this.isInitialized = true;
            console.log('✅ Project Manager initialized successfully');
            
        } catch (error) {
            console.error('❌ Project Manager initialization failed:', error);
            showError('Failed to initialize Project Manager');
        }
    }

    setupEventListeners() {
        // File upload forms
        $('#fileUploadForm').on('submit', (e) => this.handleFileUpload(e));
        $('#urlUploadForm').on('submit', (e) => this.handleUrlUpload(e));
        
        // Use case change handlers
        $('#uploadUseCaseSelect').on('change', () => this.onUseCaseChange('upload'));
        $('#urlUseCaseSelect').on('change', () => this.onUseCaseChange('url'));
        $('#etlUseCaseSelect').on('change', () => this.onUseCaseChange('etl'));
        
        // Data management
        $('#createProjectForm').on('submit', (e) => this.createProject(e));
        $('#refreshProjects').on('click', () => this.loadProjects());
        $('#syncProjects').on('click', () => this.refreshAndSync());
        
        // ETL pipeline
        $('#refreshEtlFiles').on('click', () => this.refreshEtlFiles());
        
        // Modal events
        $('#createProjectModal').on('hidden.bs.modal', () => this.resetCreateProjectForm());
        
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
                4: 'Select a project category to view files',
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
            // Load projects and use cases in parallel
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
                
                // Categorize and render projects
                this.categories = this.groupProjectsByCategory();
                this.renderProjects();
                
                // Update stats
                await this.updateStats();
                
                // Update project selects
                this.updateProjectSelects();
                
            } else {
                // Handle API errors properly
                const projectsError = projectsResponse.ok ? null : `Projects API: ${projectsResponse.status} ${projectsResponse.statusText}`;
                const useCasesError = useCasesResponse.ok ? null : `Use Cases API: ${useCasesResponse.status} ${useCasesResponse.statusText}`;
                
                const errorMessage = [projectsError, useCasesError].filter(Boolean).join(', ');
                console.error('❌ API calls failed:', errorMessage);
                
                // Show user-friendly error message
                this.showDatabaseError('Failed to load data from database. Please ensure the database is properly initialized.');
                
                // Clear data to prevent stale state
                this.projects = [];
                this.useCases = [];
                this.categories = {};
                this.renderProjects();
                this.updateStatsWithFallback();
            }
            
        } catch (error) {
            console.error('Error loading projects:', error);
            this.showDatabaseError('Database connection error. Please check your database setup.');
            
            // Clear data to prevent stale state
            this.projects = [];
            this.useCases = [];
            this.categories = {};
            this.renderProjects();
            this.updateStatsWithFallback();
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
    groupProjectsByCategory() {
        const categories = {};
        
        this.projects.forEach(project => {
            const category = project.category || 'uncategorized';
            if (!categories[category]) {
                categories[category] = [];
            }
            categories[category].push(project);
        });
        
        return categories;
    }

    // Render projects in the UI
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
export default ProjectManager;