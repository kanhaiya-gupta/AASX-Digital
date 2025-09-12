/**
 * Project Management Module
 * Handles all project-related functionality for the Data Platform
 *
 * @author AAS Data Modeling Framework
 * @version 2.0.0
 * @license MIT
 */

class ProjectManagementModule {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.selectedProjects = new Set();
        this.filters = {
            status: '',
            priority: '',
            manager: '',
            dateFrom: '',
            dateTo: '',
            search: ''
        };
        this.projects = [];
        this.metrics = {};
        this.insights = {};

        this.init();
    }

    /**
     * Initialize the project management module
     */
    init() {
        this.bindEvents();
        this.loadProjectData();
        console.log('✅ Project Management Module initialized');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Search input
        const searchInput = document.getElementById('projectSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.filterProjects(), 300));
        }

        // Filter selects
        const filterSelects = document.querySelectorAll('#projectStatusFilter, #projectPriorityFilter, #projectManagerFilter');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => this.filterProjects());
        });

        // Date filters
        const dateInputs = document.querySelectorAll('#projectDateFrom, #projectDateTo');
        dateInputs.forEach(input => {
            input.addEventListener('change', () => this.filterProjects());
        });

        // Bulk action buttons
        const bulkButtons = document.querySelectorAll('[data-bulk-action]');
        bulkButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const action = e.target.dataset.bulkAction;
                this.handleBulkAction(action);
            });
        });
    }

    /**
     * Load project data
     */
    async loadProjectData() {
        try {
            // Load metrics
            await this.loadProjectMetrics();
            
            // Load projects
            await this.loadProjects();
            
            // Load insights
            await this.loadProjectInsights();
            
            this.updateUI();
        } catch (error) {
            console.error('❌ Error loading project data:', error);
            this.showErrorMessage('Failed to load project data');
        }
    }

    /**
     * Load project metrics
     */
    async loadProjectMetrics() {
        try {
            // Mock service call - replace with actual API call
            this.metrics = await this.getProjectMetrics();
        } catch (error) {
            console.error('❌ Error loading project metrics:', error);
            this.metrics = {
                totalProjects: 0,
                activeProjects: 0,
                atRiskProjects: 0,
                totalTeamMembers: 0,
                projectGrowthRate: 0,
                activeProjectRate: 0,
                riskProjectRate: 0,
                avgTeamSize: 0
            };
        }
    }

    /**
     * Load projects
     */
    async loadProjects() {
        try {
            // Mock service call - replace with actual API call
            this.projects = await this.getProjects();
        } catch (error) {
            console.error('❌ Error loading projects:', error);
            this.projects = [];
        }
    }

    /**
     * Load project insights
     */
    async loadProjectInsights() {
        try {
            // Mock service call - replace with actual API call
            this.insights = await this.getProjectInsights();
        } catch (error) {
            console.error('❌ Error loading project insights:', error);
            this.insights = {
                statusDistribution: [],
                timelineOverview: []
            };
        }
    }

    /**
     * Update the UI with loaded data
     */
    updateUI() {
        this.updateMetrics();
        this.updateProjectsTable();
        this.updatePagination();
        this.updateBulkActions();
    }

    /**
     * Update metrics display
     */
    updateMetrics() {
        // Update metric values
        const metricElements = {
            'totalProjects': this.metrics.totalProjects,
            'activeProjects': this.metrics.activeProjects,
            'atRiskProjects': this.metrics.atRiskProjects,
            'totalTeamMembers': this.metrics.totalTeamMembers,
            'projectGrowthRate': this.metrics.projectGrowthRate,
            'activeProjectRate': this.metrics.activeProjectRate,
            'riskProjectRate': this.metrics.riskProjectRate,
            'avgTeamSize': this.metrics.avgTeamSize
        };

        Object.entries(metricElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                if (id.includes('Rate') || id.includes('Growth')) {
                    element.textContent = `${value}%`;
                } else {
                    element.textContent = value;
                }
            }
        });

        // Animate metric cards
        this.animateMetrics();
    }

    /**
     * Update projects table
     */
    updateProjectsTable() {
        const tbody = document.querySelector('#projectsTable tbody');
        if (!tbody) return;

        const filteredProjects = this.getFilteredProjects();
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageProjects = filteredProjects.slice(startIndex, endIndex);

        tbody.innerHTML = '';

        if (pageProjects.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-4">
                        <div class="text-muted">
                            <i class="fas fa-inbox fa-2x mb-3"></i>
                            <p>No projects found matching your criteria</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        pageProjects.forEach(project => {
            const row = this.createProjectRow(project);
            tbody.appendChild(row);
        });

        // Update project count
        const projectCountElement = document.getElementById('projectCount');
        if (projectCountElement) {
            projectCountElement.textContent = filteredProjects.length;
        }
    }

    /**
     * Create a project table row
     */
    createProjectRow(project) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${project.id}" 
                           onchange="toggleProjectSelection('${project.id}')" 
                           ${this.selectedProjects.has(project.id) ? 'checked' : ''}>
                </div>
            </td>
            <td>
                <div class="dp-project-profile">
                    <div class="dp-project-icon ${project.type.toLowerCase()}">
                        <i class="fas fa-${this.getProjectTypeIcon(project.type)}"></i>
                    </div>
                    <div class="dp-project-info">
                        <h6 class="mb-0">${project.name}</h6>
                        <small>${project.description}</small>
                    </div>
                </div>
            </td>
            <td>
                <span class="dp-status-badge ${project.status.toLowerCase()}">
                    ${project.status}
                </span>
            </td>
            <td>
                <span class="dp-priority-badge ${project.priority.toLowerCase()}">
                    ${project.priority}
                </span>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <img src="${project.manager.avatar || '/static/images/default-avatar.png'}" 
                         alt="${project.manager.name}" 
                         class="rounded-circle me-2" 
                         width="32" height="32">
                    <span>${project.manager.name}</span>
                </div>
            </td>
            <td>
                <div class="dp-progress-container">
                    <div class="dp-progress-bar" style="width: ${project.progress}%"></div>
                </div>
                <div class="dp-progress-text">${project.progress}%</div>
            </td>
            <td>
                <small class="text-muted">
                    ${this.formatDate(project.startDate)} - ${this.formatDate(project.endDate)}
                </small>
            </td>
            <td>
                <div class="dp-action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewProjectDetails('${project.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="editProject('${project.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProject('${project.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        return row;
    }

    /**
     * Update pagination
     */
    updatePagination() {
        const filteredProjects = this.getFilteredProjects();
        const totalPages = Math.ceil(filteredProjects.length / this.itemsPerPage);
        
        const paginationElement = document.getElementById('projectPagination');
        if (!paginationElement) return;

        if (totalPages <= 1) {
            paginationElement.innerHTML = '';
            return;
        }

        let paginationHTML = `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changeProjectPage(${this.currentPage - 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;

        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                paginationHTML += `
                    <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="changeProjectPage(${i})">${i}</a>
                    </li>
                `;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changeProjectPage(${this.currentPage + 1})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;

        paginationElement.innerHTML = paginationHTML;
    }

    /**
     * Update bulk actions state
     */
    updateBulkActions() {
        const hasSelection = this.selectedProjects.size > 0;
        const bulkButtons = document.querySelectorAll('[data-bulk-action]');
        
        bulkButtons.forEach(button => {
            button.disabled = !hasSelection;
            if (hasSelection) {
                button.classList.remove('disabled');
            } else {
                button.classList.add('disabled');
            }
        });

        // Update selection count
        const selectionCountElement = document.getElementById('selectionCount');
        if (selectionCountElement) {
            selectionCountElement.textContent = this.selectedProjects.size;
        }
    }

    /**
     * Filter projects based on current filters
     */
    filterProjects() {
        this.currentPage = 1;
        this.updateProjectsTable();
        this.updatePagination();
    }

    /**
     * Get filtered projects
     */
    getFilteredProjects() {
        return this.projects.filter(project => {
            // Search filter
            if (this.filters.search) {
                const searchTerm = this.filters.search.toLowerCase();
                if (!project.name.toLowerCase().includes(searchTerm) && 
                    !project.description.toLowerCase().includes(searchTerm) &&
                    !project.manager.name.toLowerCase().includes(searchTerm)) {
                    return false;
                }
            }

            // Status filter
            if (this.filters.status && project.status !== this.filters.status) {
                return false;
            }

            // Priority filter
            if (this.filters.priority && project.priority !== this.filters.priority) {
                return false;
            }

            // Manager filter
            if (this.filters.manager && project.manager.id !== this.filters.manager) {
                return false;
            }

            // Date filters
            if (this.filters.dateFrom && new Date(project.startDate) < new Date(this.filters.dateFrom)) {
                return false;
            }

            if (this.filters.dateTo && new Date(project.endDate) > new Date(this.filters.dateTo)) {
                return false;
            }

            return true;
        });
    }

    /**
     * Handle bulk actions
     */
    handleBulkAction(action) {
        if (this.selectedProjects.size === 0) {
            this.showErrorMessage('No projects selected');
            return;
        }

        const projectIds = Array.from(this.selectedProjects);
        
        switch (action) {
            case 'activate':
                this.bulkActivateProjects(projectIds);
                break;
            case 'archive':
                this.bulkArchiveProjects(projectIds);
                break;
            case 'delete':
                this.bulkDeleteProjects(projectIds);
                break;
            case 'export':
                this.exportProjects(projectIds);
                break;
            default:
                console.warn(`Unknown bulk action: ${action}`);
        }
    }

    /**
     * Toggle project selection
     */
    toggleProjectSelection(projectId) {
        if (this.selectedProjects.has(projectId)) {
            this.selectedProjects.delete(projectId);
        } else {
            this.selectedProjects.add(projectId);
        }
        this.updateBulkActions();
    }

    /**
     * Change project page
     */
    changeProjectPage(page) {
        const filteredProjects = this.getFilteredProjects();
        const totalPages = Math.ceil(filteredProjects.length / this.itemsPerPage);
        
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.updateProjectsTable();
        this.updatePagination();
        
        // Scroll to top of table
        const tableElement = document.getElementById('projectsTable');
        if (tableElement) {
            tableElement.scrollIntoView({ behavior: 'smooth' });
        }
    }

    /**
     * Clear project search
     */
    clearProjectSearch() {
        const searchInput = document.getElementById('projectSearchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        this.filters.search = '';
        this.filterProjects();
    }

    /**
     * Show create project modal
     */
    showCreateProjectModal() {
        // Mock implementation - replace with actual modal display
        console.log('Showing create project modal');
        this.showSuccessMessage('Create project modal will be implemented');
    }

    /**
     * Show project templates
     */
    showProjectTemplates() {
        // Mock implementation - replace with actual modal display
        console.log('Showing project templates');
        this.showSuccessMessage('Project templates will be implemented');
    }

    /**
     * View project details
     */
    viewProjectDetails(projectId) {
        // Mock implementation - replace with actual modal display
        console.log(`Viewing details for project: ${projectId}`);
        this.showSuccessMessage(`Viewing details for project: ${projectId}`);
    }

    /**
     * Edit project
     */
    editProject(projectId) {
        // Mock implementation - replace with actual modal display
        console.log(`Editing project: ${projectId}`);
        this.showSuccessMessage(`Editing project: ${projectId}`);
    }

    /**
     * Delete project
     */
    deleteProject(projectId) {
        // Mock implementation - replace with actual delete confirmation
        if (confirm('Are you sure you want to delete this project?')) {
            console.log(`Deleting project: ${projectId}`);
            this.showSuccessMessage(`Project deleted: ${projectId}`);
            // Refresh project list
            this.loadProjectData();
        }
    }

    /**
     * Export project data
     */
    exportProjectData() {
        // Mock implementation - replace with actual export
        console.log('Exporting project data');
        this.showSuccessMessage('Project data export started');
    }

    /**
     * Bulk activate projects
     */
    bulkActivateProjects(projectIds) {
        // Mock implementation - replace with actual bulk operation
        console.log(`Activating projects: ${projectIds.join(', ')}`);
        this.showSuccessMessage(`${projectIds.length} projects activated`);
        this.selectedProjects.clear();
        this.updateBulkActions();
        this.loadProjectData();
    }

    /**
     * Bulk archive projects
     */
    bulkArchiveProjects(projectIds) {
        // Mock implementation - replace with actual bulk operation
        console.log(`Archiving projects: ${projectIds.join(', ')}`);
        this.showSuccessMessage(`${projectIds.length} projects archived`);
        this.selectedProjects.clear();
        this.updateBulkActions();
        this.loadProjectData();
    }

    /**
     * Bulk delete projects
     */
    bulkDeleteProjects(projectIds) {
        // Mock implementation - replace with actual bulk operation
        if (confirm(`Are you sure you want to delete ${projectIds.length} projects?`)) {
            console.log(`Deleting projects: ${projectIds.join(', ')}`);
            this.showSuccessMessage(`${projectIds.length} projects deleted`);
            this.selectedProjects.clear();
            this.updateBulkActions();
            this.loadProjectData();
        }
    }

    /**
     * Export projects
     */
    exportProjects(projectIds) {
        // Mock implementation - replace with actual export
        console.log(`Exporting projects: ${projectIds.join(', ')}`);
        this.showSuccessMessage(`Exporting ${projectIds.length} projects`);
    }

    /**
     * Animate metrics
     */
    animateMetrics() {
        const metricCards = document.querySelectorAll('.dp-metric-card');
        metricCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.6s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 100);
            }, index * 100);
        });
    }

    /**
     * Get project type icon
     */
    getProjectTypeIcon(type) {
        const iconMap = {
            'Research': 'microscope',
            'Development': 'code',
            'Implementation': 'rocket',
            'Maintenance': 'wrench',
            'Migration': 'exchange-alt'
        };
        return iconMap[type] || 'project-diagram';
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString();
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
        // Mock implementation - replace with actual toast/notification
        console.log(`✅ ${message}`);
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        // Mock implementation - replace with actual toast/notification
        console.error(`❌ ${message}`);
    }

    /**
     * Mock service methods - replace with actual API calls
     */
    async getProjectMetrics() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            totalProjects: 24,
            activeProjects: 18,
            atRiskProjects: 3,
            totalTeamMembers: 156,
            projectGrowthRate: 12,
            activeProjectRate: 75,
            riskProjectRate: 12.5,
            avgTeamSize: 6.5
        };
    }

    async getProjects() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        return [
            {
                id: '1',
                name: 'AAS Data Modeling Engine',
                description: 'Core engine development for AAS data modeling framework',
                type: 'Development',
                status: 'Active',
                priority: 'High',
                manager: { id: '1', name: 'Dr. Sarah Chen', avatar: '/static/images/avatars/sarah.jpg' },
                progress: 75,
                startDate: '2024-01-15',
                endDate: '2024-06-30'
            },
            {
                id: '2',
                name: 'Digital Twin Analytics',
                description: 'Advanced analytics for digital twin implementations',
                type: 'Research',
                status: 'Active',
                priority: 'Critical',
                manager: { id: '2', name: 'Prof. Michael Rodriguez', avatar: '/static/images/avatars/michael.jpg' },
                progress: 45,
                startDate: '2024-02-01',
                endDate: '2024-08-31'
            },
            {
                id: '3',
                name: 'Federated Learning Platform',
                description: 'Distributed machine learning infrastructure',
                type: 'Implementation',
                status: 'Planning',
                priority: 'Medium',
                manager: { id: '3', name: 'Dr. Emily Watson', avatar: '/static/images/avatars/emily.jpg' },
                progress: 15,
                startDate: '2024-03-01',
                endDate: '2024-10-31'
            },
            {
                id: '4',
                name: 'Knowledge Graph Integration',
                description: 'Neo4j integration for semantic data modeling',
                type: 'Development',
                status: 'Active',
                priority: 'High',
                manager: { id: '4', name: 'Alex Thompson', avatar: '/static/images/avatars/alex.jpg' },
                progress: 60,
                startDate: '2024-01-20',
                endDate: '2024-07-15'
            },
            {
                id: '5',
                name: 'Certificate Management System',
                description: 'Digital certificate lifecycle management',
                type: 'Maintenance',
                status: 'On Hold',
                priority: 'Low',
                manager: { id: '5', name: 'Lisa Park', avatar: '/static/images/avatars/lisa.jpg' },
                progress: 30,
                startDate: '2024-02-15',
                endDate: '2024-05-31'
            }
        ];
    }

    async getProjectInsights() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        return {
            statusDistribution: [
                { status: 'Active', count: 18, percentage: 75 },
                { status: 'Planning', count: 3, percentage: 12.5 },
                { status: 'On Hold', count: 2, percentage: 8.3 },
                { status: 'Completed', count: 1, percentage: 4.2 }
            ],
            timelineOverview: [
                { month: 'Jan', projects: 5 },
                { month: 'Feb', projects: 8 },
                { month: 'Mar', projects: 12 },
                { month: 'Apr', projects: 15 },
                { month: 'May', projects: 18 },
                { month: 'Jun', projects: 22 }
            ]
        };
    }

    /**
     * Cleanup resources
     */
    destroy() {
        // Remove event listeners
        console.log('🧹 Project Management Module destroyed');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectManagementModule;
} else if (typeof window !== 'undefined') {
    window.ProjectManagementModule = ProjectManagementModule;
}

