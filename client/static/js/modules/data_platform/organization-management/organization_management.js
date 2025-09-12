/**
 * Organization Management Module
 * Handles all organization-related functionality for the Data Platform
 * 
 * @author AAS Data Modeling Framework
 * @version 2.0.0
 * @license MIT
 */

class OrganizationManagementModule {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.selectedOrganizations = new Set();
        this.filters = {
            industry: '',
            status: '',
            size: '',
            location: '',
            search: ''
        };
        
        this.init();
    }

    /**
     * Initialize the organization management module
     */
    init() {
        this.bindEvents();
        this.loadOrganizationData();
        console.log('✅ Organization Management Module initialized');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Search input
        const searchInput = document.getElementById('orgSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.filters.search = searchInput.value;
                this.filterOrganizations();
            }, 300));
        }

        // Filter changes
        const filterSelects = ['industryFilter', 'statusFilter', 'sizeFilter', 'locationFilter'];
        filterSelects.forEach(filterId => {
            const select = document.getElementById(filterId);
            if (select) {
                select.addEventListener('change', () => {
                    this.filters[filterId.replace('Filter', '')] = select.value;
                    this.filterOrganizations();
                });
            }
        });

        // Select all checkbox
        const selectAllCheckbox = document.getElementById('selectAllOrgs');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAllOrgs(e.target.checked);
            });
        }
    }

    /**
     * Load organization data
     */
    async loadOrganizationData() {
        try {
            // Load metrics
            await this.loadOrganizationMetrics();
            
            // Load organization list
            await this.loadOrganizationList();
            
            // Load insights
            await this.loadOrganizationInsights();
            
        } catch (error) {
            console.error('❌ Error loading organization data:', error);
            this.showErrorMessage('Failed to load organization data.');
        }
    }

    /**
     * Load organization metrics
     */
    async loadOrganizationMetrics() {
        try {
            const metrics = await this.getOrganizationMetrics();
            this.updateMetricsDisplay(metrics);
        } catch (error) {
            console.error('Error loading organization metrics:', error);
            // Use fallback data
            this.updateMetricsDisplay({
                totalOrganizations: 156,
                activeOrganizations: 142,
                totalMembers: 2847,
                totalProjects: 89,
                growthRate: 12,
                activeRate: 91,
                memberGrowthRate: 8,
                projectSuccessRate: 94
            });
        }
    }

    /**
     * Load organization list
     */
    async loadOrganizationList(page = 1, filters = {}) {
        try {
            const organizations = await this.getOrganizations(page, filters);
            this.updateOrganizationListDisplay(organizations);
            this.updatePagination(organizations.pagination);
            this.updateResultsCount(organizations.pagination);
        } catch (error) {
            console.error('Error loading organization list:', error);
            // Use fallback data
            this.updateOrganizationListDisplay(this.getFallbackOrganizationData());
        }
    }

    /**
     * Load organization insights
     */
    async loadOrganizationInsights() {
        try {
            const insights = await this.getOrganizationInsights();
            this.updateInsightsDisplay(insights);
        } catch (error) {
            console.error('Error loading organization insights:', error);
        }
    }

    /**
     * Update metrics display
     */
    updateMetricsDisplay(metrics) {
        // Update metric numbers with animation
        this.animateMetric('totalOrganizations', metrics.totalOrganizations);
        this.animateMetric('activeOrganizations', metrics.activeOrganizations);
        this.animateMetric('totalMembers', metrics.totalMembers);
        this.animateMetric('totalProjects', metrics.totalProjects);

        // Update trend indicators
        this.updateTrendIndicator('orgGrowthRate', metrics.growthRate + '%');
        this.updateTrendIndicator('activeOrgRate', metrics.activeRate + '%');
        this.updateTrendIndicator('memberGrowthRate', metrics.memberGrowthRate + '%');
        this.updateTrendIndicator('projectSuccessRate', metrics.projectSuccessRate + '%');
    }

    /**
     * Update organization list display
     */
    updateOrganizationListDisplay(organizations) {
        const tbody = document.getElementById('organizationsTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        organizations.data.forEach(org => {
            const row = this.createOrganizationTableRow(org);
            tbody.appendChild(row);
        });
    }

    /**
     * Create organization table row
     */
    createOrganizationTableRow(org) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="form-check">
                    <input class="form-check-input org-checkbox" type="checkbox" value="${org.id}" onchange="toggleOrgSelection()">
                </div>
            </td>
            <td>
                <div class="dp-org-profile">
                    <div class="dp-org-avatar">
                        ${org.name.charAt(0).toUpperCase()}
                    </div>
                    <div class="dp-org-info">
                        <h6>${org.name}</h6>
                        <small>${org.industry} • ${org.type}</small>
                    </div>
                </div>
            </td>
            <td>
                <div>
                    <div class="fw-bold">${org.industry}</div>
                    <small class="text-muted">${org.type} • ${org.size}</small>
                </div>
            </td>
            <td>
                <div>
                    <div class="fw-bold">${org.memberCount} members</div>
                    <small class="text-muted">${org.projectCount} active projects</small>
                </div>
            </td>
            <td>
                <div>
                    <div class="fw-bold">${org.city}, ${org.country}</div>
                    <small class="text-muted">${org.email}</small>
                </div>
            </td>
            <td>
                <div>
                    <span class="dp-status-badge ${org.status}">${org.status}</span>
                    <br>
                    <small class="text-muted">Health: ${org.healthScore}%</small>
                </div>
            </td>
            <td>
                <div>
                    <div class="fw-bold">${org.performanceScore}%</div>
                    <small class="text-muted">${org.lastActivity}</small>
                </div>
            </td>
            <td>
                <div class="dp-action-buttons">
                    <button class="btn btn-outline-info btn-sm" onclick="viewOrgDetails('${org.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-primary btn-sm" onclick="editOrganization('${org.id}')" title="Edit Organization">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-warning btn-sm" onclick="suspendOrganization('${org.id}')" title="Suspend Organization">
                        <i class="fas fa-pause"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteOrganization('${org.id}')" title="Delete Organization">
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
    updatePagination(pagination) {
        const paginationEl = document.getElementById('orgsPagination');
        if (!paginationEl) return;

        paginationEl.innerHTML = '';

        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${pagination.currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `
            <a class="page-link" href="#" onclick="changeOrgPage(${pagination.currentPage - 1})" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
            </a>
        `;
        paginationEl.appendChild(prevLi);

        // Page numbers
        for (let i = 1; i <= pagination.totalPages; i++) {
            if (i === 1 || i === pagination.totalPages || 
                (i >= pagination.currentPage - 2 && i <= pagination.currentPage + 2)) {
                const li = document.createElement('li');
                li.className = `page-item ${i === pagination.currentPage ? 'active' : ''}`;
                li.innerHTML = `
                    <a class="page-link" href="#" onclick="changeOrgPage(${i})">${i}</a>
                `;
                paginationEl.appendChild(li);
            } else if (i === pagination.currentPage - 3 || i === pagination.currentPage + 3) {
                const li = document.createElement('li');
                li.className = 'page-item disabled';
                li.innerHTML = '<span class="page-link">...</span>';
                paginationEl.appendChild(li);
            }
        }

        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${pagination.currentPage === pagination.totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `
            <a class="page-link" href="#" onclick="changeOrgPage(${pagination.currentPage + 1})" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
            </a>
        `;
        paginationEl.appendChild(nextLi);
    }

    /**
     * Update results count
     */
    updateResultsCount(pagination) {
        const resultsCountEl = document.getElementById('orgResultsCount');
        if (resultsCountEl) {
            resultsCountEl.textContent = `Showing ${pagination.startItem} to ${pagination.endItem} of ${pagination.totalItems} organizations`;
        }
    }

    /**
     * Update insights display
     */
    updateInsightsDisplay(insights) {
        // This would update charts and insights
        console.log('Organization insights updated:', insights);
    }

    /**
     * Update trend indicator
     */
    updateTrendIndicator(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Filter organizations
     */
    filterOrganizations() {
        this.currentPage = 1;
        this.loadOrganizationList(this.currentPage, this.filters);
    }

    /**
     * Clear organization search
     */
    clearOrgSearch() {
        const searchInput = document.getElementById('orgSearchInput');
        if (searchInput) {
            searchInput.value = '';
            this.filters.search = '';
            this.filterOrganizations();
        }
    }

    /**
     * Toggle advanced filters
     */
    toggleAdvancedFilters() {
        const advancedFilters = document.getElementById('advancedFilters');
        if (advancedFilters) {
            const isVisible = advancedFilters.style.display !== 'none';
            advancedFilters.style.display = isVisible ? 'none' : 'block';
        }
    }

    /**
     * Toggle select all organizations
     */
    toggleSelectAllOrgs(checked) {
        const checkboxes = document.querySelectorAll('.org-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            if (checked) {
                this.selectedOrganizations.add(checkbox.value);
            } else {
                this.selectedOrganizations.delete(checkbox.value);
            }
        });
        this.updateBulkActionButtons();
    }

    /**
     * Toggle organization selection
     */
    toggleOrgSelection() {
        const checkboxes = document.querySelectorAll('.org-checkbox:checked');
        this.selectedOrganizations.clear();
        checkboxes.forEach(checkbox => {
            this.selectedOrganizations.add(checkbox.value);
        });
        this.updateBulkActionButtons();
    }

    /**
     * Update bulk action buttons
     */
    updateBulkActionButtons() {
        const hasSelection = this.selectedOrganizations.size > 0;
        const bulkButtons = ['bulkActivateBtn', 'bulkSuspendBtn', 'bulkDeleteBtn'];
        
        bulkButtons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.disabled = !hasSelection;
            }
        });
    }

    /**
     * Show create organization modal
     */
    showCreateOrgModal() {
        const modal = new bootstrap.Modal(document.getElementById('organizationModal'));
        this.resetOrganizationForm();
        modal.show();
    }

    /**
     * Reset organization form
     */
    resetOrganizationForm() {
        const form = document.getElementById('organizationForm');
        if (form) {
            form.reset();
        }
        
        // Reset modal title
        const modalTitle = document.getElementById('organizationModalLabel');
        if (modalTitle) {
            modalTitle.innerHTML = '<i class="fas fa-building me-2"></i>Create New Organization';
        }
    }

    /**
     * Save organization
     */
    async saveOrganization() {
        try {
            const formData = this.getOrganizationFormData();
            
            if (this.validateOrganizationData(formData)) {
                // Save organization logic here
                console.log('Saving organization:', formData);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('organizationModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Refresh organization list
                await this.loadOrganizationList();
                
                this.showSuccessMessage('Organization saved successfully!');
            }
        } catch (error) {
            console.error('Error saving organization:', error);
            this.showErrorMessage('Failed to save organization.');
        }
    }

    /**
     * Get organization form data
     */
    getOrganizationFormData() {
        const formData = {};
        const form = document.getElementById('organizationForm');
        
        if (form) {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.id) {
                    formData[input.id.replace('org', '').toLowerCase()] = input.value;
                }
            });
        }
        
        return formData;
    }

    /**
     * Validate organization data
     */
    validateOrganizationData(data) {
        const required = ['name', 'industry', 'type', 'email', 'country'];
        
        for (const field of required) {
            if (!data[field] || data[field].trim() === '') {
                this.showErrorMessage(`Please fill in the ${field} field.`);
                return false;
            }
        }
        
        // Validate email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            this.showErrorMessage('Please enter a valid email address.');
            return false;
        }
        
        return true;
    }

    /**
     * View organization details
     */
    viewOrgDetails(orgId) {
        console.log('Viewing organization details:', orgId);
        // Implementation for viewing organization details
    }

    /**
     * Edit organization
     */
    editOrganization(orgId) {
        console.log('Editing organization:', orgId);
        // Implementation for editing organization
    }

    /**
     * Suspend organization
     */
    suspendOrganization(orgId) {
        console.log('Suspending organization:', orgId);
        // Implementation for suspending organization
    }

    /**
     * Delete organization
     */
    deleteOrganization(orgId) {
        if (confirm('Are you sure you want to delete this organization? This action cannot be undone.')) {
            console.log('Deleting organization:', orgId);
            // Implementation for deleting organization
        }
    }

    /**
     * Bulk activate organizations
     */
    bulkActivateOrgs() {
        if (this.selectedOrganizations.size > 0) {
            console.log('Bulk activating organizations:', Array.from(this.selectedOrganizations));
            // Implementation for bulk activation
        }
    }

    /**
     * Bulk suspend organizations
     */
    bulkSuspendOrgs() {
        if (this.selectedOrganizations.size > 0) {
            console.log('Bulk suspending organizations:', Array.from(this.selectedOrganizations));
            // Implementation for bulk suspension
        }
    }

    /**
     * Bulk delete organizations
     */
    bulkDeleteOrgs() {
        if (this.selectedOrganizations.size > 0) {
            if (confirm(`Are you sure you want to delete ${this.selectedOrganizations.size} organizations? This action cannot be undone.`)) {
                console.log('Bulk deleting organizations:', Array.from(this.selectedOrganizations));
                // Implementation for bulk deletion
            }
        }
    }

    /**
     * Export organization data
     */
    exportOrganizationData() {
        console.log('Exporting organization data...');
        // Implementation for exporting organization data
    }

    /**
     * Import organizations
     */
    importOrganizations() {
        console.log('Importing organizations...');
        // Implementation for importing organizations
    }

    /**
     * Change organization page
     */
    changeOrgPage(page) {
        this.currentPage = page;
        this.loadOrganizationList(page, this.filters);
    }

    /**
     * Animate metric number
     */
    animateMetric(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = 0;
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutQuart);
            
            element.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    /**
     * Show success message
     */
    showSuccessMessage(message) {
        // Implementation for showing success messages
        console.log('✅ Success:', message);
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        // Implementation for showing error messages
        console.error('❌ Error:', message);
    }

    /**
     * Get organization metrics (mock service)
     */
    async getOrganizationMetrics() {
        // Mock service - replace with actual API call
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    totalOrganizations: 156,
                    activeOrganizations: 142,
                    totalMembers: 2847,
                    totalProjects: 89,
                    growthRate: 12,
                    activeRate: 91,
                    memberGrowthRate: 8,
                    projectSuccessRate: 94
                });
            }, 500);
        });
    }

    /**
     * Get organizations (mock service)
     */
    async getOrganizations(page = 1, filters = {}) {
        // Mock service - replace with actual API call
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    data: this.getFallbackOrganizationData(),
                    pagination: {
                        currentPage: page,
                        totalPages: 16,
                        totalItems: 156,
                        startItem: (page - 1) * 10 + 1,
                        endItem: Math.min(page * 10, 156)
                    }
                });
            }, 500);
        });
    }

    /**
     * Get organization insights (mock service)
     */
    async getOrganizationInsights() {
        // Mock service - replace with actual API call
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    growthTrend: [12, 15, 18, 22, 25, 28, 30, 32, 35, 38, 40, 42],
                    industryDistribution: [
                        { industry: 'Technology', count: 45, percentage: 29 },
                        { industry: 'Healthcare', count: 32, percentage: 21 },
                        { industry: 'Finance', count: 28, percentage: 18 },
                        { industry: 'Manufacturing', count: 25, percentage: 16 },
                        { industry: 'Education', count: 16, percentage: 10 },
                        { industry: 'Other', count: 10, percentage: 6 }
                    ]
                });
            }, 500);
        });
    }

    /**
     * Get fallback organization data
     */
    getFallbackOrganizationData() {
        return [
            {
                id: '1',
                name: 'TechCorp Solutions',
                industry: 'Technology',
                type: 'Corporation',
                size: 'Large (201-1000)',
                memberCount: 450,
                projectCount: 12,
                city: 'San Francisco',
                country: 'United States',
                email: 'contact@techcorp.com',
                status: 'active',
                healthScore: 95,
                performanceScore: 92,
                lastActivity: '2 hours ago'
            },
            {
                id: '2',
                name: 'HealthFirst Medical',
                industry: 'Healthcare',
                type: 'LLC',
                size: 'Medium (51-200)',
                memberCount: 125,
                projectCount: 8,
                city: 'Boston',
                country: 'United States',
                email: 'info@healthfirst.com',
                status: 'active',
                healthScore: 88,
                performanceScore: 85,
                lastActivity: '1 day ago'
            },
            {
                id: '3',
                name: 'Global Finance Group',
                industry: 'Finance',
                type: 'Corporation',
                size: 'Enterprise (1000+)',
                memberCount: 1200,
                projectCount: 25,
                city: 'New York',
                country: 'United States',
                email: 'contact@gfg.com',
                status: 'active',
                healthScore: 92,
                performanceScore: 89,
                lastActivity: '30 minutes ago'
            },
            {
                id: '4',
                name: 'Innovate Manufacturing',
                industry: 'Manufacturing',
                type: 'Partnership',
                size: 'Medium (51-200)',
                memberCount: 180,
                projectCount: 15,
                city: 'Detroit',
                country: 'United States',
                email: 'hello@innovate.com',
                status: 'pending',
                healthScore: 75,
                performanceScore: 78,
                lastActivity: '3 days ago'
            },
            {
                id: '5',
                name: 'EduTech Institute',
                industry: 'Education',
                type: 'Non-Profit',
                size: 'Small (11-50)',
                memberCount: 35,
                projectCount: 6,
                city: 'Austin',
                country: 'United States',
                email: 'info@edutech.edu',
                status: 'active',
                healthScore: 90,
                performanceScore: 87,
                lastActivity: '5 hours ago'
            }
        ];
    }

    /**
     * Utility function: debounce
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
     * Cleanup resources
     */
    destroy() {
        // Remove event listeners
        console.log('🧹 Organization Management Module destroyed');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OrganizationManagementModule;
} else if (typeof window !== 'undefined') {
    window.OrganizationManagementModule = OrganizationManagementModule;
}

