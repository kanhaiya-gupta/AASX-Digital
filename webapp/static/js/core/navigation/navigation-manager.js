/**
 * Navigation Manager
 * =================
 * 
 * This is the main navigation manager that coordinates all navigation
 * components and handles the overall navigation system.
 */

class NavigationManager {
    constructor() {
        this.roleBasedNavigation = null;
        this.dynamicMenu = null;
        this.userContextDisplay = null;
        this.userContext = null;
        this.initialized = false;
    }
    
    /**
     * Initialize the navigation system
     */
    async initialize() {
        if (this.initialized) return;
        
        try {
            // Initialize components
            this.roleBasedNavigation = new RoleBasedNavigation();
            this.dynamicMenu = new DynamicMenu();
            this.userContextDisplay = new UserContextDisplay();
            
            // Get user context
            this.userContext = await this.getUserContext();
            
            // Initialize role-based navigation
            await this.roleBasedNavigation.initialize();
            
            // Initialize dynamic menu
            this.dynamicMenu.updateNavigation(this.userContext);
            
            // Initialize user context display
            await this.userContextDisplay.initialize();
            
            // Update navigation with user context
            this.updateNavigation();
            
            // Set up event listeners
            this.setupEventListeners();
            
            this.initialized = true;
            console.log('Navigation system initialized successfully');
            
        } catch (error) {
            console.error('Error initializing navigation system:', error);
        }
    }
    
    /**
     * Get user context from server
     */
    async getUserContext() {
        try {
            const response = await fetch('/api/auth/check-auth', {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.user_context || data;
            }
            
            return null;
        } catch (error) {
            console.error('Error getting user context:', error);
            return null;
        }
    }
    
    /**
     * Update navigation based on user context
     */
    updateNavigation() {
        if (!this.userContext) {
            this.showUnauthenticatedState();
            return;
        }
        
        // Update role-based navigation
        this.roleBasedNavigation.updateNavigation();
        
        // Update dynamic menu
        this.dynamicMenu.updateNavigation(this.userContext);
        
        // Update user context display
        this.userContextDisplay.render();
        
        // Update navigation indicators
        this.updateNavigationIndicators();
        
        // Update quick actions
        this.updateQuickActions();
        
        // Update notifications
        this.updateNotifications();
    }
    
    /**
     * Show unauthenticated state
     */
    showUnauthenticatedState() {
        // Hide authenticated-only elements
        const authenticatedElements = document.querySelectorAll('[data-auth-required]');
        authenticatedElements.forEach(element => {
            element.style.display = 'none';
        });
        
        // Show unauthenticated elements
        const unauthenticatedElements = document.querySelectorAll('[data-auth-optional]');
        unauthenticatedElements.forEach(element => {
            element.style.display = 'block';
        });
        
        // Update navigation to show only public modules
        this.roleBasedNavigation.showUnauthenticatedState();
    }
    
    /**
     * Update navigation indicators
     */
    updateNavigationIndicators() {
        // Update current page indicator
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
        
        // Update breadcrumb if exists
        this.updateBreadcrumb();
    }
    
    /**
     * Update breadcrumb navigation
     */
    updateBreadcrumb() {
        const breadcrumbContainer = document.querySelector('.breadcrumb');
        if (!breadcrumbContainer) return;
        
        const currentPath = window.location.pathname;
        const pathSegments = currentPath.split('/').filter(segment => segment);
        
        let breadcrumbHTML = '<ol class="breadcrumb">';
        breadcrumbHTML += '<li class="breadcrumb-item"><a href="/"><i class="fas fa-home"></i> Home</a></li>';
        
        let currentPathBuilder = '';
        pathSegments.forEach((segment, index) => {
            currentPathBuilder += `/${segment}`;
            const isLast = index === pathSegments.length - 1;
            
            if (isLast) {
                breadcrumbHTML += `<li class="breadcrumb-item active" aria-current="page">${this.formatSegment(segment)}</li>`;
            } else {
                breadcrumbHTML += `<li class="breadcrumb-item"><a href="${currentPathBuilder}">${this.formatSegment(segment)}</a></li>`;
            }
        });
        
        breadcrumbHTML += '</ol>';
        breadcrumbContainer.innerHTML = breadcrumbHTML;
    }
    
    /**
     * Format path segment for display
     */
    formatSegment(segment) {
        // Convert kebab-case to Title Case
        return segment
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    /**
     * Update quick actions
     */
    updateQuickActions() {
        if (!this.userContext) return;
        
        const quickActions = document.querySelectorAll('[data-quick-action]');
        quickActions.forEach(action => {
            const actionModule = action.dataset.quickAction;
            const canAccess = this.canAccessModule(actionModule);
            
            if (canAccess) {
                action.style.display = 'block';
                action.classList.remove('d-none');
            } else {
                action.style.display = 'none';
                action.classList.add('d-none');
            }
        });
    }
    
    /**
     * Check if user can access module
     */
    canAccessModule(moduleKey) {
        if (!this.userContext) return false;
        
        // Check if module exists in dynamic menu config
        const moduleConfig = this.dynamicMenu.menuConfig[moduleKey];
        if (!moduleConfig) return false;
        
        // Check if independent users are allowed
        if (this.userContext.is_independent && !moduleConfig.allowIndependent) {
            return false;
        }
        
        // Check permissions
        const requiredPermissions = moduleConfig.permissions;
        return requiredPermissions.some(permission => 
            this.userHasPermission(permission)
        );
    }
    
    /**
     * Check if user has specific permission
     */
    userHasPermission(permission) {
        if (!this.userContext) return false;
        
        // Check if user has the permission
        if (this.userContext.has_permission) {
            return this.userContext.has_permission(permission);
        }
        
        // Check permissions array
        if (this.userContext.permissions && Array.isArray(this.userContext.permissions)) {
            return this.userContext.permissions.includes(permission);
        }
        
        // Check role-based permissions
        const rolePermissions = this.getRolePermissions(this.userContext.role);
        return rolePermissions.includes(permission);
    }
    
    /**
     * Get permissions for a role
     */
    getRolePermissions(role) {
        const rolePermissions = {
            'super_admin': ['read', 'write', 'manage', 'admin'],
            'admin': ['read', 'write', 'manage'],
            'manager': ['read', 'write'],
            'user': ['read', 'write'],
            'viewer': ['read']
        };
        
        return rolePermissions[role] || ['read'];
    }
    
    /**
     * Update notifications
     */
    updateNotifications() {
        if (!this.userContext) return;
        
        // Update notification count
        const notificationBadge = document.querySelector('.navbar-nav .badge');
        if (notificationBadge) {
            // You could fetch actual notification count here
            notificationBadge.textContent = '0';
        }
        
        // Update notification content based on user context
        this.updateNotificationContent();
    }
    
    /**
     * Update notification content
     */
    updateNotificationContent() {
        const notificationContainer = document.querySelector('.dropdown-menu .dropdown-item');
        if (!notificationContainer) return;
        
        // This would be implemented to show user-specific notifications
        // For now, we'll just update the notification text
        const notifications = document.querySelectorAll('.dropdown-menu .dropdown-item');
        notifications.forEach(notification => {
            // Update notification content based on user context
            // This is a placeholder for actual notification logic
        });
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for authentication state changes
        window.addEventListener('storage', (event) => {
            if (event.key === 'auth_state') {
                this.handleAuthStateChange(event.newValue);
            }
        });
        
        // Listen for navigation changes
        window.addEventListener('popstate', () => {
            this.updateNavigationIndicators();
        });
        
        // Listen for user context updates
        document.addEventListener('userContextUpdated', () => {
            this.refresh();
        });
    }
    
    /**
     * Handle authentication state changes
     */
    async handleAuthStateChange(newState) {
        if (newState === 'logged_out') {
            this.userContext = null;
            this.showUnauthenticatedState();
        } else if (newState === 'logged_in') {
            this.userContext = await this.getUserContext();
            this.updateNavigation();
        }
    }
    
    /**
     * Refresh navigation system
     */
    async refresh() {
        this.userContext = await this.getUserContext();
        this.updateNavigation();
    }
    
    /**
     * Get current user context
     */
    getCurrentUserContext() {
        return this.userContext;
    }
    
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return this.userContext !== null;
    }
    
    /**
     * Check if user has specific role
     */
    hasRole(role) {
        return this.userContext && this.userContext.role === role;
    }
    
    /**
     * Check if user has specific permission
     */
    hasPermission(permission) {
        return this.userHasPermission(permission);
    }
    
    /**
     * Get user type
     */
    getUserType() {
        if (!this.userContext) return 'independent';
        
        if (this.userContext.role === 'super_admin') {
            return 'super_admin';
        } else if (this.userContext.is_independent || !this.userContext.organization_id) {
            return 'independent';
        } else {
            return 'organization_member';
        }
    }
}

// Create global navigation manager instance
window.navigationManager = new NavigationManager();

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.navigationManager.initialize();
});

// Export for use in other modules
window.NavigationManager = NavigationManager;

