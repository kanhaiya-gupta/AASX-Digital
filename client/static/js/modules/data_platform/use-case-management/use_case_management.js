/**
 * Use Case Management Module
 * Handles all use case-related functionality for the Data Platform
 *
 * @author AAS Data Modeling Framework
 * @version 2.0.0
 * @license MIT
 */

class UseCaseManagementModule {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.selectedUseCases = new Set();
        this.filters = {
            status: '',
            priority: '',
            domain: '',
            owner: '',
            dateFrom: '',
            dateTo: '',
            search: ''
        };
        this.useCases = [];
        this.metrics = {};
        this.insights = {};

        this.init();
    }

    /**
     * Initialize the use case management module
     */
    init() {
        this.bindEvents();
        this.loadUseCaseData();
        console.log('✅ Use Case Management Module initialized');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Search input
        const searchInput = document.getElementById('useCaseSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.filterUseCases(), 300));
        }

        // Filter selects
        const filterSelects = document.querySelectorAll('#useCaseStatusFilter, #useCasePriorityFilter, #useCaseDomainFilter, #useCaseOwnerFilter');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => this.filterUseCases());
        });

        // Date filters
        const dateInputs = document.querySelectorAll('#useCaseDateFrom, #useCaseDateTo');
        dateInputs.forEach(input => {
            input.addEventListener('change', () => this.filterUseCases());
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
     * Load use case data
     */
    async loadUseCaseData() {
        try {
            // Load metrics
            await this.loadUseCaseMetrics();
            
            // Load use cases
            await this.loadUseCases();
            
            // Load insights
            await this.loadUseCaseInsights();
            
            this.updateUI();
        } catch (error) {
            console.error('❌ Error loading use case data:', error);
            this.showErrorMessage('Failed to load use case data');
        }
    }

    /**
     * Load use case metrics
     */
    async loadUseCaseMetrics() {
        try {
            // Mock service call - replace with actual API call
            this.metrics = await this.getUseCaseMetrics();
        } catch (error) {
            console.error('❌ Error loading use case metrics:', error);
            this.metrics = {
                totalUseCases: 0,
                approvedUseCases: 0,
                pendingUseCases: 0,
                implementedUseCases: 0,
                useCaseGrowthRate: 0,
                approvalRate: 0,
                pendingRate: 0,
                implementationRate: 0
            };
        }
    }

    /**
     * Load use cases
     */
    async loadUseCases() {
        try {
            // Mock service call - replace with actual API call
            this.useCases = await this.getUseCases();
        } catch (error) {
            console.error('❌ Error loading use cases:', error);
            this.useCases = [];
        }
    }

    /**
     * Load use case insights
     */
    async loadUseCaseInsights() {
        try {
            // Mock service call - replace with actual API call
            this.insights = await this.getUseCaseInsights();
        } catch (error) {
            console.error('❌ Error loading use case insights:', error);
            this.insights = {
                statusDistribution: [],
                domainAnalysis: []
            };
        }
    }

    /**
     * Update the UI with loaded data
     */
    updateUI() {
        this.updateMetrics();
        this.updateUseCasesTable();
        this.updatePagination();
        this.updateBulkActions();
    }

    /**
     * Update metrics display
     */
    updateMetrics() {
        // Update metric values
        const metricElements = {
            'totalUseCases': this.metrics.totalUseCases,
            'approvedUseCases': this.metrics.approvedUseCases,
            'pendingUseCases': this.metrics.pendingUseCases,
            'implementedUseCases': this.metrics.implementedUseCases,
            'useCaseGrowthRate': this.metrics.useCaseGrowthRate,
            'approvalRate': this.metrics.approvalRate,
            'pendingRate': this.metrics.pendingRate,
            'implementationRate': this.metrics.implementationRate
        };

        Object.entries(metricElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                if (id.includes('Rate')) {
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
     * Update use cases table
     */
    updateUseCasesTable() {
        const tbody = document.querySelector('#useCasesTableBody');
        if (!tbody) return;

        const filteredUseCases = this.getFilteredUseCases();
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageUseCases = filteredUseCases.slice(startIndex, endIndex);

        tbody.innerHTML = '';

        if (pageUseCases.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-4">
                        <div class="text-muted">
                            <i class="fas fa-inbox fa-2x mb-3"></i>
                            <p>No use cases found matching your criteria</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        pageUseCases.forEach(useCase => {
            const row = this.createUseCaseRow(useCase);
            tbody.appendChild(row);
        });

        // Update use case count
        const useCaseCountElement = document.getElementById('useCaseResultsCount');
        if (useCaseCountElement) {
            useCaseCountElement.textContent = `Showing ${filteredUseCases.length} use cases`;
        }
    }

    /**
     * Create a use case table row
     */
    createUseCaseRow(useCase) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${useCase.id}" 
                           onchange="toggleUseCaseSelection('${useCase.id}')" 
                           ${this.selectedUseCases.has(useCase.id) ? 'checked' : ''}>
                </div>
            </td>
            <td>
                <div class="dp-use-case-profile">
                    <div class="dp-use-case-icon ${useCase.domain.toLowerCase()}">
                        <i class="fas fa-${this.getDomainIcon(useCase.domain)}"></i>
                    </div>
                    <div class="dp-use-case-info">
                        <h6 class="mb-0">${useCase.name}</h6>
                        <small>${useCase.description}</small>
                    </div>
                </div>
            </td>
            <td>
                <div class="mb-2">
                    <span class="dp-status-badge ${useCase.status.toLowerCase()}">
                        ${useCase.status}
                    </span>
                </div>
                <div>
                    <span class="dp-priority-badge ${useCase.priority.toLowerCase()}">
                        ${useCase.priority}
                    </span>
                </div>
            </td>
            <td>
                <span class="badge bg-light text-dark">${useCase.domain}</span>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <img src="${useCase.owner.avatar || '/static/images/default-avatar.png'}" 
                         alt="${useCase.owner.name}" 
                         class="rounded-circle me-2" 
                         width="32" height="32">
                    <span>${useCase.owner.name}</span>
                </div>
            </td>
            <td>
                <div class="dp-business-value">
                    <span class="dp-value-indicator ${useCase.businessValue}"></span>
                    <span class="dp-value-text">${useCase.businessValue}</span>
                </div>
            </td>
            <td>
                <small class="text-muted">
                    ${this.formatDate(useCase.lastUpdated)}
                </small>
            </td>
            <td>
                <div class="dp-action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewUseCaseDetails('${useCase.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="editUseCase('${useCase.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteUseCase('${useCase.id}')" title="Delete">
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
        const filteredUseCases = this.getFilteredUseCases();
        const totalPages = Math.ceil(filteredUseCases.length / this.itemsPerPage);
        
        const paginationElement = document.getElementById('useCasesPagination');
        if (!paginationElement) return;

        if (totalPages <= 1) {
            paginationElement.innerHTML = '';
            return;
        }

        let paginationHTML = `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changeUseCasePage(${this.currentPage - 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;

        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                paginationHTML += `
                    <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="changeUseCasePage(${i})">${i}</a>
                    </li>
                `;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changeUseCasePage(${this.currentPage + 1})">
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
        const hasSelection = this.selectedUseCases.size > 0;
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
            selectionCountElement.textContent = this.selectedUseCases.size;
        }
    }

    /**
     * Filter use cases based on current filters
     */
    filterUseCases() {
        this.currentPage = 1;
        this.updateUseCasesTable();
        this.updatePagination();
    }

    /**
     * Get filtered use cases
     */
    getFilteredUseCases() {
        return this.useCases.filter(useCase => {
            // Search filter
            if (this.filters.search) {
                const searchTerm = this.filters.search.toLowerCase();
                if (!useCase.name.toLowerCase().includes(searchTerm) && 
                    !useCase.description.toLowerCase().includes(searchTerm) &&
                    !useCase.owner.name.toLowerCase().includes(searchTerm)) {
                    return false;
                }
            }

            // Status filter
            if (this.filters.status && useCase.status !== this.filters.status) {
                return false;
            }

            // Priority filter
            if (this.filters.priority && useCase.priority !== this.filters.priority) {
                return false;
            }

            // Domain filter
            if (this.filters.domain && useCase.domain !== this.filters.domain) {
                return false;
            }

            // Owner filter
            if (this.filters.owner && useCase.owner.id !== this.filters.owner) {
                return false;
            }

            // Date filters
            if (this.filters.dateFrom && new Date(useCase.lastUpdated) < new Date(this.filters.dateFrom)) {
                return false;
            }

            if (this.filters.dateTo && new Date(useCase.lastUpdated) > new Date(this.filters.dateTo)) {
                return false;
            }

            return true;
        });
    }

    /**
     * Handle bulk actions
     */
    handleBulkAction(action) {
        if (this.selectedUseCases.size === 0) {
            this.showErrorMessage('No use cases selected');
            return;
        }

        const useCaseIds = Array.from(this.selectedUseCases);
        
        switch (action) {
            case 'approve':
                this.bulkApproveUseCases(useCaseIds);
                break;
            case 'reject':
                this.bulkRejectUseCases(useCaseIds);
                break;
            case 'archive':
                this.bulkArchiveUseCases(useCaseIds);
                break;
            default:
                console.warn(`Unknown bulk action: ${action}`);
        }
    }

    /**
     * Toggle use case selection
     */
    toggleUseCaseSelection(useCaseId) {
        if (this.selectedUseCases.has(useCaseId)) {
            this.selectedUseCases.delete(useCaseId);
        } else {
            this.selectedUseCases.add(useCaseId);
        }
        this.updateBulkActions();
    }

    /**
     * Change use case page
     */
    changeUseCasePage(page) {
        const filteredUseCases = this.getFilteredUseCases();
        const totalPages = Math.ceil(filteredUseCases.length / this.itemsPerPage);
        
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.updateUseCasesTable();
        this.updatePagination();
        
        // Scroll to top of table
        const tableElement = document.getElementById('useCasesTable');
        if (tableElement) {
            tableElement.scrollIntoView({ behavior: 'smooth' });
        }
    }

    /**
     * Clear use case search
     */
    clearUseCaseSearch() {
        const searchInput = document.getElementById('useCaseSearchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        this.filters.search = '';
        this.filterUseCases();
    }

    /**
     * Show create use case modal
     */
    showCreateUseCaseModal() {
        // Mock implementation - replace with actual modal display
        console.log('Showing create use case modal');
        this.showSuccessMessage('Create use case modal will be implemented');
    }

    /**
     * Show use case templates
     */
    showUseCaseTemplates() {
        // Mock implementation - replace with actual modal display
        console.log('Showing use case templates');
        this.showSuccessMessage('Use case templates will be implemented');
    }

    /**
     * View use case details
     */
    viewUseCaseDetails(useCaseId) {
        // Mock implementation - replace with actual modal display
        console.log(`Viewing details for use case: ${useCaseId}`);
        this.showSuccessMessage(`Viewing details for use case: ${useCaseId}`);
    }

    /**
     * Edit use case
     */
    editUseCase(useCaseId) {
        // Mock implementation - replace with actual modal display
        console.log(`Editing use case: ${useCaseId}`);
        this.showSuccessMessage(`Editing use case: ${useCaseId}`);
    }

    /**
     * Delete use case
     */
    deleteUseCase(useCaseId) {
        // Mock implementation - replace with actual delete confirmation
        if (confirm('Are you sure you want to delete this use case?')) {
            console.log(`Deleting use case: ${useCaseId}`);
            this.showSuccessMessage(`Use case deleted: ${useCaseId}`);
            // Refresh use case list
            this.loadUseCaseData();
        }
    }

    /**
     * Export use case data
     */
    exportUseCaseData() {
        // Mock implementation - replace with actual export
        console.log('Exporting use case data');
        this.showSuccessMessage('Use case data export started');
    }

    /**
     * Bulk approve use cases
     */
    bulkApproveUseCases(useCaseIds) {
        // Mock implementation - replace with actual bulk operation
        console.log(`Approving use cases: ${useCaseIds.join(', ')}`);
        this.showSuccessMessage(`${useCaseIds.length} use cases approved`);
        this.selectedUseCases.clear();
        this.updateBulkActions();
        this.loadUseCaseData();
    }

    /**
     * Bulk reject use cases
     */
    bulkRejectUseCases(useCaseIds) {
        // Mock implementation - replace with actual bulk operation
        console.log(`Rejecting use cases: ${useCaseIds.join(', ')}`);
        this.showSuccessMessage(`${useCaseIds.length} use cases rejected`);
        this.selectedUseCases.clear();
        this.updateBulkActions();
        this.loadUseCaseData();
    }

    /**
     * Bulk archive use cases
     */
    bulkArchiveUseCases(useCaseIds) {
        // Mock implementation - replace with actual bulk operation
        if (confirm(`Are you sure you want to archive ${useCaseIds.length} use cases?`)) {
            console.log(`Archiving use cases: ${useCaseIds.join(', ')}`);
            this.showSuccessMessage(`${useCaseIds.length} use cases archived`);
            this.selectedUseCases.clear();
            this.updateBulkActions();
            this.loadUseCaseData();
        }
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
     * Get domain icon
     */
    getDomainIcon(domain) {
        const iconMap = {
            'Manufacturing': 'industry',
            'Healthcare': 'heartbeat',
            'Finance': 'university',
            'Energy': 'bolt',
            'Transportation': 'truck',
            'Retail': 'shopping-cart'
        };
        return iconMap[domain] || 'building';
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
    async getUseCaseMetrics() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            totalUseCases: 42,
            approvedUseCases: 28,
            pendingUseCases: 8,
            implementedUseCases: 18,
            useCaseGrowthRate: 15,
            approvalRate: 66.7,
            pendingRate: 19.0,
            implementationRate: 42.9
        };
    }

    async getUseCases() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        return [
            {
                id: '1',
                name: 'Predictive Maintenance System',
                description: 'AI-powered predictive maintenance for manufacturing equipment',
                status: 'Approved',
                priority: 'High',
                domain: 'Manufacturing',
                owner: { id: '1', name: 'Dr. Sarah Chen', avatar: '/static/images/avatars/sarah.jpg' },
                businessValue: 'High',
                lastUpdated: '2024-01-15'
            },
            {
                id: '2',
                name: 'Patient Data Analytics',
                description: 'Advanced analytics for healthcare patient outcomes',
                status: 'Under Review',
                priority: 'Critical',
                domain: 'Healthcare',
                owner: { id: '2', name: 'Prof. Michael Rodriguez', avatar: '/static/images/avatars/michael.jpg' },
                businessValue: 'High',
                lastUpdated: '2024-01-20'
            },
            {
                id: '3',
                name: 'Fraud Detection Engine',
                description: 'Machine learning-based financial fraud detection',
                status: 'Draft',
                priority: 'Medium',
                domain: 'Finance',
                owner: { id: '3', name: 'Dr. Emily Watson', avatar: '/static/images/avatars/emily.jpg' },
                businessValue: 'Medium',
                lastUpdated: '2024-01-18'
            },
            {
                id: '4',
                name: 'Smart Grid Optimization',
                description: 'IoT-based energy grid optimization and monitoring',
                status: 'Implemented',
                priority: 'High',
                domain: 'Energy',
                owner: { id: '4', name: 'Alex Thompson', avatar: '/static/images/avatars/alex.jpg' },
                businessValue: 'High',
                lastUpdated: '2024-01-10'
            },
            {
                id: '5',
                name: 'Supply Chain Visibility',
                description: 'Real-time supply chain tracking and analytics',
                status: 'Submitted',
                priority: 'Medium',
                domain: 'Transportation',
                owner: { id: '5', name: 'Lisa Park', avatar: '/static/images/avatars/lisa.jpg' },
                businessValue: 'Medium',
                lastUpdated: '2024-01-22'
            }
        ];
    }

    async getUseCaseInsights() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        return {
            statusDistribution: [
                { status: 'Approved', count: 28, percentage: 66.7 },
                { status: 'Under Review', count: 8, percentage: 19.0 },
                { status: 'Draft', count: 4, percentage: 9.5 },
                { status: 'Implemented', count: 18, percentage: 42.9 },
                { status: 'Rejected', count: 2, percentage: 4.8 }
            ],
            domainAnalysis: [
                { domain: 'Manufacturing', count: 12, percentage: 28.6 },
                { domain: 'Healthcare', count: 8, percentage: 19.0 },
                { domain: 'Finance', count: 6, percentage: 14.3 },
                { domain: 'Energy', count: 5, percentage: 11.9 },
                { domain: 'Transportation', count: 4, percentage: 9.5 },
                { domain: 'Retail', count: 3, percentage: 7.1 }
            ]
        };
    }

    /**
     * Cleanup resources
     */
    destroy() {
        // Remove event listeners
        console.log('🧹 Use Case Management Module destroyed');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UseCaseManagementModule;
} else if (typeof window !== 'undefined') {
    window.UseCaseManagementModule = UseCaseManagementModule;
}

