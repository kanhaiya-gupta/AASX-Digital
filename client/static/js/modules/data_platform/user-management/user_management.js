/**
 * User Management Module
 * Handles all user-related functionality for the Data Platform
 * 
 * @author AAS Data Modeling Framework
 * @version 2.0.0
 * @license MIT
 */

class UserManagementModule {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.selectedUsers = new Set();
        this.filters = {
            role: '',
            department: '',
            status: '',
            lastLogin: '',
            accountAge: '',
            permissionLevel: '',
            organization: ''
        };
        
        this.init();
    }

    /**
     * Initialize the user management module
     */
    init() {
        this.bindEvents();
        this.loadUserManagementData();
    }

    /**
     * Bind all event listeners
     */
    bindEvents() {
        // Search and filter events
        document.getElementById('userSearch')?.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        document.getElementById('roleFilter')?.addEventListener('change', this.handleFilterChange.bind(this));
        document.getElementById('departmentFilter')?.addEventListener('change', this.handleFilterChange.bind(this));
        document.getElementById('statusFilter')?.addEventListener('change', this.handleFilterChange.bind(this));
        document.getElementById('lastLoginFilter')?.addEventListener('change', this.handleFilterChange.bind(this));
        document.getElementById('accountAgeFilter')?.addEventListener('change', this.handleFilterChange.bind(this));
        document.getElementById('permissionLevelFilter')?.addEventListener('change', this.handleFilterChange.bind(this));
        document.getElementById('organizationFilter')?.addEventListener('change', this.handleFilterChange.bind(this));

        // Action bar events
        document.getElementById('toggleAdvancedFilters')?.addEventListener('click', this.toggleAdvancedFilters.bind(this));
        document.getElementById('exportUsers')?.addEventListener('click', this.exportUserData.bind(this));
        document.getElementById('importUsers')?.addEventListener('click', this.importUsers.bind(this));
        document.getElementById('createNewUser')?.addEventListener('click', this.showCreateUserModal.bind(this));

        // Bulk action events
        document.getElementById('selectAllUsers')?.addEventListener('change', this.toggleSelectAll.bind(this));
        document.getElementById('bulkActivate')?.addEventListener('click', () => this.bulkAction('activate'));
        document.getElementById('bulkSuspend')?.addEventListener('click', () => this.bulkAction('suspend'));
        document.getElementById('bulkDelete')?.addEventListener('click', () => this.bulkAction('delete'));

        // Pagination events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('page-link')) {
                e.preventDefault();
                const page = parseInt(e.target.dataset.page);
                if (page) this.changePage(page);
            }
        });

        // Modal events
        this.bindModalEvents();
    }

    /**
     * Bind modal-specific events
     */
    bindModalEvents() {
        // Create User Modal
        const createUserModal = document.getElementById('createUserModal');
        if (createUserModal) {
            createUserModal.addEventListener('show.bs.modal', this.handleCreateUserModalShow.bind(this));
            createUserModal.addEventListener('hidden.bs.modal', this.handleCreateUserModalHidden.bind(this));
            
            // Form submission
            const createUserForm = createUserModal.querySelector('#createUserForm');
            if (createUserForm) {
                createUserForm.addEventListener('submit', this.handleCreateUserSubmit.bind(this));
            }
        }

        // User Details Modal
        const userDetailsModal = document.getElementById('userDetailsModal');
        if (userDetailsModal) {
            userDetailsModal.addEventListener('show.bs.modal', this.handleUserDetailsModalShow.bind(this));
        }
    }

    /**
     * Load all user management data
     */
    async loadUserManagementData() {
        try {
            await Promise.all([
                this.loadUserMetrics(),
                this.loadUserList(this.currentPage, this.filters),
                this.loadUserActivityInsights()
            ]);
        } catch (error) {
            console.error('Error loading user management data:', error);
            this.showNotification('Error loading user data', 'error');
        }
    }

    /**
     * Load user metrics for the dashboard
     */
    async loadUserMetrics() {
        try {
            const metrics = await this.userService.getUserMetrics();
            this.updateUserMetricsDisplay(metrics);
        } catch (error) {
            console.error('Error loading user metrics:', error);
        }
    }

    /**
     * Load user list with pagination and filters
     */
    async loadUserList(page = 1, filters = {}) {
        try {
            const result = await this.userService.getUsers(page, this.itemsPerPage, filters);
            this.updateUserListDisplay(result.users);
            this.updatePagination(result.pagination);
            this.updateResultsCount(result.pagination);
        } catch (error) {
            console.error('Error loading user list:', error);
        }
    }

    /**
     * Load user activity insights for charts
     */
    async loadUserActivityInsights() {
        try {
            const insights = await this.userService.getUserActivityInsights();
            this.updateUserActivityInsights(insights);
        } catch (error) {
            console.error('Error loading user activity insights:', error);
        }
    }

    /**
     * Update user metrics display
     */
    updateUserMetricsDisplay(metrics) {
        // Update metric cards
        this.updateMetricCard('totalUsers', metrics.totalUsers);
        this.updateMetricCard('activeUsers', metrics.activeUsers);
        this.updateMetricCard('pendingApproval', metrics.pendingApproval);
        this.updateMetricCard('securityScore', metrics.securityScore);

        // Update trend indicators
        this.updateTrendIndicator('totalUsersTrend', metrics.totalUsersTrend);
        this.updateTrendIndicator('activeUsersTrend', metrics.activeUsersTrend);
        this.updateTrendIndicator('pendingApprovalTrend', metrics.pendingApprovalTrend);
        this.updateTrendIndicator('securityScoreTrend', metrics.securityScoreTrend);
    }

    /**
     * Update a specific metric card
     */
    updateMetricCard(metricId, value) {
        const element = document.getElementById(metricId);
        if (element) {
            element.textContent = this.formatNumber(value);
        }
    }

    /**
     * Update trend indicator
     */
    updateTrendIndicator(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value > 0 ? `+${value}%` : `${value}%`;
            element.className = `trend-indicator ${value >= 0 ? 'positive' : 'negative'}`;
        }
    }

    /**
     * Update user list display
     */
    updateUserListDisplay(users) {
        const tbody = document.querySelector('#userTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        users.forEach(user => {
            const row = this.createUserTableRow(user);
            tbody.appendChild(row);
        });

        // Update select all checkbox state
        this.updateSelectAllState();
    }

    /**
     * Create a user table row
     */
    createUserTableRow(user) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="form-check">
                    <input class="form-check-input user-checkbox" type="checkbox" value="${user.id}" 
                           ${this.selectedUsers.has(user.id) ? 'checked' : ''}>
                </div>
            </td>
            <td>
                <div class="user-profile">
                    <div class="user-avatar">
                        <img src="${user.avatar || '/static/images/default-avatar.png'}" alt="${user.name}" 
                             class="avatar-img" onerror="this.src='/static/images/default-avatar.png'">
                        <span class="status-indicator ${user.status}"></span>
                    </div>
                    <div class="user-info">
                        <div class="user-name">${user.name}</div>
                        <div class="user-email">${user.email}</div>
                    </div>
                </div>
            </td>
            <td>
                <div class="contact-info">
                    <div class="phone">${user.phone || 'N/A'}</div>
                    <div class="location">${user.location || 'N/A'}</div>
                </div>
            </td>
            <td>
                <div class="role-permissions">
                    <span class="role-badge ${user.role.toLowerCase()}">${user.role}</span>
                    <div class="permission-level">Level ${user.permissionLevel}</div>
                </div>
            </td>
            <td>
                <div class="department-org">
                    <div class="department">${user.department}</div>
                    <div class="organization">${user.organization}</div>
                </div>
            </td>
            <td>
                <div class="status-security">
                    <span class="status-badge ${user.status}">${user.status}</span>
                    <div class="security-score">${user.securityScore}%</div>
                </div>
            </td>
            <td>
                <div class="activity-analytics">
                    <div class="last-login">${this.formatDate(user.lastLogin)}</div>
                    <div class="login-count">${user.loginCount} logins</div>
                </div>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="userManagement.viewUserDetails('${user.id}')" 
                            title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="userManagement.editUser('${user.id}')" 
                            title="Edit User">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="userManagement.suspendUser('${user.id}')" 
                            title="Suspend User">
                        <i class="fas fa-pause"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="userManagement.deleteUser('${user.id}')" 
                            title="Delete User">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

        // Bind checkbox event
        const checkbox = row.querySelector('.user-checkbox');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.selectedUsers.add(user.id);
            } else {
                this.selectedUsers.delete(user.id);
            }
            this.updateSelectAllState();
        });

        return row;
    }

    /**
     * Update pagination controls
     */
    updatePagination(pagination) {
        const paginationElement = document.getElementById('userPagination');
        if (!paginationElement) return;

        const { currentPage, totalPages, totalItems } = pagination;
        
        let paginationHTML = '';
        
        // Previous button
        paginationHTML += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
            </li>
        `;

        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        // Next button
        paginationHTML += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
            </li>
        `;

        paginationElement.innerHTML = paginationHTML;
    }

    /**
     * Update results count display
     */
    updateResultsCount(pagination) {
        const { currentPage, totalItems, itemsPerPage } = pagination;
        const startItem = (currentPage - 1) * itemsPerPage + 1;
        const endItem = Math.min(currentPage * itemsPerPage, totalItems);
        
        const element = document.getElementById('resultsCount');
        if (element) {
            element.textContent = `Showing ${startItem} to ${endItem} of ${totalItems} users`;
        }
    }

    /**
     * Update user activity insights (placeholder for charts)
     */
    updateUserActivityInsights(insights) {
        // This would be implemented with chart libraries like Chart.js
        console.log('User activity insights:', insights);
    }

    /**
     * Update select all checkbox state
     */
    updateSelectAllState() {
        const selectAllCheckbox = document.getElementById('selectAllUsers');
        if (!selectAllCheckbox) return;

        const totalUsers = document.querySelectorAll('.user-checkbox').length;
        const selectedUsers = this.selectedUsers.size;

        if (selectedUsers === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
        } else if (selectedUsers === totalUsers) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
            selectAllCheckbox.checked = false;
        }
    }

    /**
     * Handle search input
     */
    handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        // Implement search logic
        this.loadUserList(1, { ...this.filters, search: searchTerm });
    }

    /**
     * Handle filter changes
     */
    handleFilterChange(e) {
        const filterName = e.target.id.replace('Filter', '');
        this.filters[filterName] = e.target.value;
        this.loadUserList(1, this.filters);
    }

    /**
     * Toggle advanced filters visibility
     */
    toggleAdvancedFilters() {
        const advancedFilters = document.getElementById('advancedFilters');
        const toggleButton = document.getElementById('toggleAdvancedFilters');
        
        if (advancedFilters) {
            const isVisible = !advancedFilters.classList.contains('d-none');
            advancedFilters.classList.toggle('d-none');
            
            if (toggleButton) {
                toggleButton.innerHTML = isVisible ? 
                    '<i class="fas fa-chevron-down"></i> Show Advanced Filters' :
                    '<i class="fas fa-chevron-up"></i> Hide Advanced Filters';
            }
        }
    }

    /**
     * Toggle select all users
     */
    toggleSelectAll(e) {
        const isChecked = e.target.checked;
        const checkboxes = document.querySelectorAll('.user-checkbox');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            if (isChecked) {
                this.selectedUsers.add(checkbox.value);
            } else {
                this.selectedUsers.delete(checkbox.value);
            }
        });
        
        this.updateSelectAllState();
    }

    /**
     * Change page
     */
    changePage(page) {
        this.currentPage = page;
        this.loadUserList(page, this.filters);
    }

    /**
     * Show create user modal
     */
    showCreateUserModal() {
        const modal = new bootstrap.Modal(document.getElementById('createUserModal'));
        modal.show();
    }

    /**
     * Handle create user modal show
     */
    handleCreateUserModalShow() {
        // Reset form
        const form = document.getElementById('createUserForm');
        if (form) form.reset();
        
        // Reset password strength indicator
        this.updatePasswordStrength(0);
    }

    /**
     * Handle create user modal hidden
     */
    handleCreateUserModalHidden() {
        // Clear any validation errors
        const form = document.getElementById('createUserForm');
        if (form) {
            const errorElements = form.querySelectorAll('.is-invalid');
            errorElements.forEach(el => el.classList.remove('is-invalid'));
        }
    }

    /**
     * Handle create user form submission
     */
    async handleCreateUserSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const userData = Object.fromEntries(formData.entries());
        
        try {
            await this.createUser(userData);
            const modal = bootstrap.Modal.getInstance(document.getElementById('createUserModal'));
            modal.hide();
            this.showNotification('User created successfully', 'success');
            this.loadUserList(this.currentPage, this.filters);
        } catch (error) {
            console.error('Error creating user:', error);
            this.showNotification('Error creating user', 'error');
        }
    }

    /**
     * View user details
     */
    async viewUserDetails(userId) {
        try {
            const user = await this.userService.getUserById(userId);
            this.populateUserDetailsModal(user);
            
            const modal = new bootstrap.Modal(document.getElementById('userDetailsModal'));
            modal.show();
        } catch (error) {
            console.error('Error loading user details:', error);
            this.showNotification('Error loading user details', 'error');
        }
    }

    /**
     * Populate user details modal
     */
    populateUserDetailsModal(user) {
        // Populate modal fields
        document.getElementById('detailUserName').textContent = user.name;
        document.getElementById('detailUserEmail').textContent = user.email;
        document.getElementById('detailUserRole').textContent = user.role;
        document.getElementById('detailUserDepartment').textContent = user.department;
        document.getElementById('detailUserOrganization').textContent = user.organization;
        document.getElementById('detailUserStatus').textContent = user.status;
        document.getElementById('detailUserSecurityScore').textContent = `${user.securityScore}%`;
        document.getElementById('detailUserLastLogin').textContent = this.formatDate(user.lastLogin);
        document.getElementById('detailUserLoginCount').textContent = user.loginCount;
        document.getElementById('detailUserCreated').textContent = this.formatDate(user.createdAt);
        document.getElementById('detailUserPhone').textContent = user.phone || 'N/A';
        document.getElementById('detailUserLocation').textContent = user.location || 'N/A';
    }

    /**
     * Edit user
     */
    async editUser(userId) {
        try {
            const user = await this.userService.getUserById(userId);
            // Populate edit form and show modal
            this.showNotification('Edit user functionality coming soon', 'info');
        } catch (error) {
            console.error('Error loading user for edit:', error);
            this.showNotification('Error loading user for edit', 'error');
        }
    }

    /**
     * Suspend user
     */
    async suspendUser(userId) {
        if (confirm('Are you sure you want to suspend this user?')) {
            try {
                await this.userService.updateUser(userId, { status: 'suspended' });
                this.showNotification('User suspended successfully', 'success');
                this.loadUserList(this.currentPage, this.filters);
            } catch (error) {
                console.error('Error suspending user:', error);
                this.showNotification('Error suspending user', 'error');
            }
        }
    }

    /**
     * Delete user
     */
    async deleteUser(userId) {
        if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
            try {
                await this.userService.deleteUser(userId);
                this.showNotification('User deleted successfully', 'success');
                this.loadUserList(this.currentPage, this.filters);
            } catch (error) {
                console.error('Error deleting user:', error);
                this.showNotification('Error deleting user', 'error');
            }
        }
    }

    /**
     * Bulk action on selected users
     */
    async bulkAction(action) {
        if (this.selectedUsers.size === 0) {
            this.showNotification('Please select users first', 'warning');
            return;
        }

        const actionText = action.charAt(0).toUpperCase() + action.slice(1);
        if (confirm(`Are you sure you want to ${action} ${this.selectedUsers.size} selected users?`)) {
            try {
                await this.userService.bulkAction(action, Array.from(this.selectedUsers));
                this.showNotification(`${actionText} completed successfully`, 'success');
                this.selectedUsers.clear();
                this.loadUserList(this.currentPage, this.filters);
            } catch (error) {
                console.error(`Error performing bulk ${action}:`, error);
                this.showNotification(`Error performing bulk ${action}`, 'error');
            }
        }
    }

    /**
     * Export user data
     */
    exportUserData() {
        this.showNotification('Export functionality coming soon', 'info');
    }

    /**
     * Import users
     */
    importUsers() {
        this.showNotification('Import functionality coming soon', 'info');
    }

    /**
     * Reset filters
     */
    resetFilters() {
        this.filters = {
            role: '',
            department: '',
            status: '',
            lastLogin: '',
            accountAge: '',
            permissionLevel: '',
            organization: ''
        };

        // Reset form inputs
        Object.keys(this.filters).forEach(key => {
            const element = document.getElementById(`${key}Filter`);
            if (element) element.value = '';
        });

        this.loadUserList(1, this.filters);
    }

    /**
     * Create user
     */
    async createUser(userData) {
        return await this.userService.createUser(userData);
    }

    /**
     * Update user
     */
    async updateUser(userId, userData) {
        return await this.userService.updateUser(userId, userData);
    }

    /**
     * Delete user
     */
    async deleteUser(userId) {
        return await this.userService.deleteUser(userId);
    }

    /**
     * Bulk action
     */
    async bulkAction(action, userIds) {
        return await this.userService.bulkAction(action, userIds);
    }

    /**
     * Update password strength indicator
     */
    updatePasswordStrength(strength) {
        const indicator = document.getElementById('passwordStrength');
        if (!indicator) return;

        const strengthTexts = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const strengthColors = ['danger', 'warning', 'info', 'success', 'success'];
        
        indicator.textContent = strengthTexts[strength];
        indicator.className = `badge bg-${strengthColors[strength]}`;
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Implementation depends on your notification system
        console.log(`${type.toUpperCase()}: ${message}`);
    }

    /**
     * Format number with commas
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        if (!dateString) return 'Never';
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
     * Get mock user service
     */
    get userService() {
        return this.createMockUserService();
    }

    /**
     * Create mock user service for development
     */
    createMockUserService() {
        return {
            async getUserMetrics() {
                return {
                    totalUsers: 1247,
                    activeUsers: 892,
                    pendingApproval: 23,
                    securityScore: 94,
                    totalUsersTrend: 12,
                    activeUsersTrend: 8,
                    pendingApprovalTrend: -15,
                    securityScoreTrend: 3
                };
            },

            async getUsers(page = 1, itemsPerPage = 10, filters = {}) {
                const mockUsers = this.generateMockUsers(50);
                const filteredUsers = this.filterUsers(mockUsers, filters);
                const startIndex = (page - 1) * itemsPerPage;
                const endIndex = startIndex + itemsPerPage;
                const paginatedUsers = filteredUsers.slice(startIndex, endIndex);

                return {
                    users: paginatedUsers,
                    pagination: {
                        currentPage: page,
                        totalPages: Math.ceil(filteredUsers.length / itemsPerPage),
                        totalItems: filteredUsers.length,
                        itemsPerPage
                    }
                };
            },

            async getUserActivityInsights() {
                return {
                    userGrowthTrend: [/* chart data */],
                    activeUsersByDepartment: [/* chart data */]
                };
            },

            async getUserById(userId) {
                const mockUsers = this.generateMockUsers(1);
                return mockUsers[0];
            },

            async createUser(userData) {
                console.log('Creating user:', userData);
                return { success: true, userId: 'new-user-id' };
            },

            async updateUser(userId, userData) {
                console.log('Updating user:', userId, userData);
                return { success: true };
            },

            async deleteUser(userId) {
                console.log('Deleting user:', userId);
                return { success: true };
            },

            async bulkAction(action, userIds) {
                console.log('Bulk action:', action, userIds);
                return { success: true, processed: userIds.length };
            },

            generateMockUsers(count) {
                const roles = ['Admin', 'Manager', 'Developer', 'Analyst', 'Viewer'];
                const departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'];
                const organizations = ['TechCorp', 'DataSys', 'InnovateLab'];
                const statuses = ['active', 'inactive', 'suspended', 'pending'];
                const locations = ['New York', 'London', 'Tokyo', 'Berlin', 'Sydney'];

                return Array.from({ length: count }, (_, i) => ({
                    id: `user-${i + 1}`,
                    name: `User ${i + 1}`,
                    email: `user${i + 1}@example.com`,
                    phone: `+1-555-${String(i + 1).padStart(3, '0')}`,
                    location: locations[i % locations.length],
                    role: roles[i % roles.length],
                    permissionLevel: (i % 5) + 1,
                    department: departments[i % departments.length],
                    organization: organizations[i % organizations.length],
                    status: statuses[i % statuses.length],
                    securityScore: 70 + (i % 30),
                    lastLogin: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                    loginCount: Math.floor(Math.random() * 100) + 1,
                    createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
                    avatar: null
                }));
            },

            filterUsers(users, filters) {
                return users.filter(user => {
                    if (filters.role && user.role !== filters.role) return false;
                    if (filters.department && user.department !== filters.department) return false;
                    if (filters.status && user.status !== filters.status) return false;
                    if (filters.organization && user.organization !== filters.organization) return false;
                    return true;
                });
            }
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserManagementModule;
} else if (typeof window !== 'undefined') {
    window.UserManagementModule = UserManagementModule;
}

