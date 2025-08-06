/**
 * Authentication Permissions Management
 * Handles user permissions, roles, and admin functionality
 */

export default class AuthPermissions {
    constructor(authCore) {
        this.authCore = authCore;
        this.permissionsTable = null;
        this.rolesTable = null;
        this.adminPanel = null;
        this.isInitialized = false;
        this.currentPermissions = [];
        this.availableRoles = [];
    }

    /**
     * Initialize the permissions management system
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔒 Initializing Auth Permissions Management...');
        
        try {
            // Initialize components
            this.initializeComponents();
            
            // Setup event handlers
            this.setupEventHandlers();
            
            // Load permissions data
            await this.loadPermissionsData();
            
            // Setup real-time updates
            this.setupRealTimeUpdates();
            
            this.isInitialized = true;
            console.log('✅ Auth Permissions Management initialized');
            
        } catch (error) {
            console.error('❌ Auth Permissions Management initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load user permissions
     */
    async loadUserPermissions() {
        try {
            // Get auth core instance
            const authCore = this.authCore;
            if (!authCore) {
                throw new Error('Authentication core not available');
            }

            const user = authCore.getCurrentUser();
            if (user) {
                this.currentUser = user;
                this.userRoles = user.roles || [];
                this.userPermissions = user.permissions || [];

                // If no permissions loaded, fetch from API
                if (this.userPermissions.length === 0) {
                    await this.fetchUserPermissions();
                }

                console.log('🔑 User permissions loaded:', {
                    roles: this.userRoles,
                    permissions: this.userPermissions
                });
            }

        } catch (error) {
            console.error('Failed to load user permissions:', error);
            // Set default permissions for unauthenticated users
            this.userRoles = ['guest'];
            this.userPermissions = this.roleDefinitions.guest.permissions;
        }
    }

    /**
     * Fetch user permissions from API
     */
    async fetchUserPermissions() {
        try {
            const authCore = this.authCore;
            if (!authCore) {
                throw new Error('Authentication core not available');
            }

            const response = await fetch('/api/auth/permissions', {
                headers: {
                    'Authorization': `Bearer ${authCore.getSessionToken()}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.userRoles = data.roles || [];
                this.userPermissions = data.permissions || [];

                // Update user object
                if (this.currentUser) {
                    this.currentUser.roles = this.userRoles;
                    this.currentUser.permissions = this.userPermissions;
                }
            }

        } catch (error) {
            console.error('Failed to fetch user permissions:', error);
            throw error;
        }
    }

    /**
     * Setup permission checking
     */
    setupPermissionChecking() {
        // Add global permission checking functions
        window.hasPermission = (permission) => this.hasPermission(permission);
        window.hasRole = (role) => this.hasRole(role);
        window.hasAnyRole = (roles) => this.hasAnyRole(roles);
        window.hasAllRoles = (roles) => this.hasAllRoles(roles);
        window.getUserRoles = () => this.getUserRoles();
        window.getUserPermissions = () => this.getUserPermissions();

        // Add permission-based element hiding
        this.setupPermissionBasedElements();
    }

    /**
     * Setup role-based UI updates
     */
    setupRoleBasedUI() {
        // Update navigation based on roles
        this.updateNavigationVisibility();

        // Update dashboard widgets based on permissions
        this.updateDashboardVisibility();

        // Update action buttons based on permissions
        this.updateActionButtons();
    }

    /**
     * Setup permission-based elements
     */
    setupPermissionBasedElements() {
        // Find all elements with data-permission attribute
        const permissionElements = document.querySelectorAll('[data-permission]');
        permissionElements.forEach(element => {
            const permission = element.getAttribute('data-permission');
            if (!this.hasPermission(permission)) {
                element.style.display = 'none';
            }
        });

        // Find all elements with data-role attribute
        const roleElements = document.querySelectorAll('[data-role]');
        roleElements.forEach(element => {
            const role = element.getAttribute('data-role');
            if (!this.hasRole(role)) {
                element.style.display = 'none';
            }
        });

        // Find all elements with data-any-role attribute
        const anyRoleElements = document.querySelectorAll('[data-any-role]');
        anyRoleElements.forEach(element => {
            const roles = element.getAttribute('data-any-role').split(',');
            if (!this.hasAnyRole(roles)) {
                element.style.display = 'none';
            }
        });
    }

    /**
     * Update navigation visibility based on permissions
     */
    updateNavigationVisibility() {
        const navItems = {
            'aasx': ['aasx:read'],
            'physics-modeling': ['physics:read'],
            'qi-analytics': ['analytics:read'],
            'twin-registry': ['system:read'],
            'kg-neo4j': ['system:read'],
            'ai-rag': ['analytics:read'],
            'certificate-manager': ['system:read'],
            'dashboard-builder': ['dashboard:read'],
            'admin': ['role:read']
        };

        Object.entries(navItems).forEach(([navId, requiredPermissions]) => {
            const navElement = document.querySelector(`[href*="${navId}"]`);
            if (navElement) {
                const hasAccess = requiredPermissions.some(permission => 
                    this.hasPermission(permission)
                );
                if (!hasAccess) {
                    navElement.style.display = 'none';
                }
            }
        });
    }

    /**
     * Update dashboard visibility based on permissions
     */
    updateDashboardVisibility() {
        const dashboardWidgets = {
            'user-stats': ['user:read'],
            'project-stats': ['project:read'],
            'system-stats': ['system:read'],
            'analytics-widget': ['analytics:read'],
            'admin-panel': ['role:read']
        };

        Object.entries(dashboardWidgets).forEach(([widgetId, requiredPermissions]) => {
            const widget = document.getElementById(widgetId);
            if (widget) {
                const hasAccess = requiredPermissions.some(permission => 
                    this.hasPermission(permission)
                );
                if (!hasAccess) {
                    widget.style.display = 'none';
                }
            }
        });
    }

    /**
     * Update action buttons based on permissions
     */
    updateActionButtons() {
        const actionButtons = {
            'create-project': ['project:write'],
            'edit-project': ['project:write'],
            'delete-project': ['project:delete'],
            'upload-aasx': ['aasx:write'],
            'delete-aasx': ['aasx:delete'],
            'create-use-case': ['physics:write'],
            'edit-use-case': ['physics:write'],
            'delete-use-case': ['physics:delete'],
            'export-data': ['analytics:read'],
            'import-data': ['analytics:write'],
            'manage-users': ['user:read'],
            'system-settings': ['system:read']
        };

        Object.entries(actionButtons).forEach(([buttonId, requiredPermissions]) => {
            const button = document.getElementById(buttonId);
            if (button) {
                const hasAccess = requiredPermissions.some(permission => 
                    this.hasPermission(permission)
                );
                if (!hasAccess) {
                    button.style.display = 'none';
                }
            }
        });
    }

    /**
     * Check if user has specific permission
     * @param {string} permission - Permission to check
     * @returns {boolean} Permission status
     */
    hasPermission(permission) {
        if (!permission) return false;

        // Check cache first
        if (this.permissionCache.has(permission)) {
            return this.permissionCache.get(permission);
        }

        // Check direct permissions
        const hasDirectPermission = this.userPermissions.includes(permission);
        
        // Check role-based permissions
        const hasRolePermission = this.userRoles.some(role => {
            const roleDef = this.roleDefinitions[role];
            return roleDef && roleDef.permissions.includes(permission);
        });

        const result = hasDirectPermission || hasRolePermission;
        this.permissionCache.set(permission, result);
        
        return result;
    }

    /**
     * Check if user has specific role
     * @param {string} role - Role to check
     * @returns {boolean} Role status
     */
    hasRole(role) {
        if (!role) return false;
        return this.userRoles.includes(role);
    }

    /**
     * Check if user has any of the specified roles
     * @param {Array} roles - Roles to check
     * @returns {boolean} Role status
     */
    hasAnyRole(roles) {
        if (!Array.isArray(roles) || roles.length === 0) return false;
        return roles.some(role => this.hasRole(role));
    }

    /**
     * Check if user has all of the specified roles
     * @param {Array} roles - Roles to check
     * @returns {boolean} Role status
     */
    hasAllRoles(roles) {
        if (!Array.isArray(roles) || roles.length === 0) return false;
        return roles.every(role => this.hasRole(role));
    }

    /**
     * Get user roles
     * @returns {Array} User roles
     */
    getUserRoles() {
        return [...this.userRoles];
    }

    /**
     * Get user permissions
     * @returns {Array} User permissions
     */
    getUserPermissions() {
        return [...this.userPermissions];
    }

    /**
     * Get role definitions
     * @returns {Object} Role definitions
     */
    getRoleDefinitions() {
        return { ...this.roleDefinitions };
    }

    /**
     * Get permissions for a specific role
     * @param {string} role - Role name
     * @returns {Array} Role permissions
     */
    getRolePermissions(role) {
        const roleDef = this.roleDefinitions[role];
        return roleDef ? [...roleDef.permissions] : [];
    }

    /**
     * Check if user can access a specific resource
     * @param {string} resource - Resource name
     * @param {string} action - Action (read, write, delete)
     * @returns {boolean} Access status
     */
    canAccess(resource, action) {
        const permission = `${resource}:${action}`;
        return this.hasPermission(permission);
    }

    /**
     * Check if user can read a resource
     * @param {string} resource - Resource name
     * @returns {boolean} Read access
     */
    canRead(resource) {
        return this.canAccess(resource, 'read');
    }

    /**
     * Check if user can write to a resource
     * @param {string} resource - Resource name
     * @returns {boolean} Write access
     */
    canWrite(resource) {
        return this.canAccess(resource, 'write');
    }

    /**
     * Check if user can delete a resource
     * @param {string} resource - Resource name
     * @returns {boolean} Delete access
     */
    canDelete(resource) {
        return this.canAccess(resource, 'delete');
    }

    /**
     * Get effective permissions for current user
     * @returns {Object} Effective permissions
     */
    getEffectivePermissions() {
        const effectivePermissions = new Set();

        // Add direct permissions
        this.userPermissions.forEach(permission => {
            effectivePermissions.add(permission);
        });

        // Add role-based permissions
        this.userRoles.forEach(role => {
            const roleDef = this.roleDefinitions[role];
            if (roleDef) {
                roleDef.permissions.forEach(permission => {
                    effectivePermissions.add(permission);
                });
            }
        });

        return Array.from(effectivePermissions);
    }

    /**
     * Check if user is admin
     * @returns {boolean} Admin status
     */
    isAdmin() {
        return this.hasRole('admin');
    }

    /**
     * Check if user is manager
     * @returns {boolean} Manager status
     */
    isManager() {
        return this.hasRole('manager');
    }

    /**
     * Check if user is analyst
     * @returns {boolean} Analyst status
     */
    isAnalyst() {
        return this.hasRole('analyst');
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isAuthenticated() {
        return this.currentUser !== null && this.userRoles.length > 0;
    }

    /**
     * Require authentication for a function
     * @param {Function} callback - Function to execute if authenticated
     * @param {Function} fallback - Function to execute if not authenticated
     */
    requireAuth(callback, fallback = null) {
        if (this.isAuthenticated()) {
            return callback();
        } else {
            if (fallback) {
                return fallback();
            } else {
                // Redirect to login
                window.location.href = '/auth/login';
            }
        }
    }

    /**
     * Require specific permission for a function
     * @param {string} permission - Required permission
     * @param {Function} callback - Function to execute if permission granted
     * @param {Function} fallback - Function to execute if permission denied
     */
    requirePermission(permission, callback, fallback = null) {
        if (this.hasPermission(permission)) {
            return callback();
        } else {
            if (fallback) {
                return fallback();
            } else {
                this.showErrorMessage('You do not have permission to perform this action');
            }
        }
    }

    /**
     * Require specific role for a function
     * @param {string} role - Required role
     * @param {Function} callback - Function to execute if role granted
     * @param {Function} fallback - Function to execute if role denied
     */
    requireRole(role, callback, fallback = null) {
        if (this.hasRole(role)) {
            return callback();
        } else {
            if (fallback) {
                return fallback();
            } else {
                this.showErrorMessage('You do not have the required role to perform this action');
            }
        }
    }

    /**
     * Clear permission cache
     */
    clearPermissionCache() {
        this.permissionCache.clear();
    }

    /**
     * Refresh permissions
     */
    async refreshPermissions() {
        this.clearPermissionCache();
        await this.loadUserPermissions();
        this.setupPermissionBasedElements();
        this.updateNavigationVisibility();
        this.updateDashboardVisibility();
        this.updateActionButtons();
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showErrorMessage(message) {
        // Use shared alerts if available
        if (window.showErrorAlert) {
            window.showErrorAlert(message);
        } else {
            alert(message);
        }
    }

    /**
     * Destroy permissions management
     */
    destroy() {
        // Remove global functions
        delete window.hasPermission;
        delete window.hasRole;
        delete window.hasAnyRole;
        delete window.hasAllRoles;
        delete window.getUserRoles;
        delete window.getUserPermissions;

        // Clear cache
        this.clearPermissionCache();

        this.isInitialized = false;
        console.log('🧹 Permissions Management destroyed');
    }
} 