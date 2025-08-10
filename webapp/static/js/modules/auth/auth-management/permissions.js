/**
 * Authentication Permissions Management
 * Handles user permissions, roles, and access control
 * CACHE BUST: 2025-08-10-20:50
 */

export default class AuthPermissions {
    constructor(authCore) {
        console.log('🔒 AuthPermissions constructor called with authCore:', !!authCore, 'Type:', typeof authCore);
        this.authCore = authCore;
        this.permissionsTable = null;
        this.rolesTable = null;
        this.adminPanel = null;
        this.isInitialized = false;
        this.currentPermissions = [];
        this.availableRoles = [];
        
        // Initialize permission-related properties
        this.userPermissions = [];
        this.userRoles = [];
        this.roleDefinitions = {};
        this.permissionCache = new Map();
        
        // Set default permissions for unauthenticated users
        this.setDefaultPermissions();
        
        // Debug method availability
        console.log('🔍 Instance methods:', {
            initializeComponents: typeof this.initializeComponents,
            setupEventHandlers: typeof this.setupEventHandlers
        });
        console.log('🔍 Prototype methods:', {
            initializeComponents: typeof AuthPermissions.prototype.initializeComponents
        });
        
        console.log('🔒 AuthPermissions constructor completed');
    }

    /**
     * Initialize the permissions management system
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔒 Initializing Auth Permissions Management...');
        console.log('🔍 AuthCore instance:', !!this.authCore, 'Type:', typeof this.authCore);
        
        try {
            // Debug method availability before calling
            console.log('🔍 Before calling initializeComponents:', {
                initializeComponents: typeof this.initializeComponents,
                this: this,
                methods: Object.getOwnPropertyNames(Object.getPrototypeOf(this))
            });
            
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
     * Initialize permissions UI components
     */
    initializeComponents() {
        console.log('🔧 Initializing permissions UI components...');

        try {
            // Get DOM elements
            this.permissionsTable = document.getElementById('permissions-table');
            this.rolesTable = document.getElementById('roles-table');
            this.adminPanel = document.getElementById('admin-panel');

            console.log('🔧 Permissions components initialized:', {
                permissionsTable: this.permissionsTable,
                rolesTable: this.rolesTable,
                adminPanel: this.adminPanel
            });

        } catch (error) {
            console.warn('⚠️ Could not initialize all components:', error);
        }
    }

    /**
     * Setup event handlers for permissions management
     */
    setupEventHandlers() {
        console.log('🔧 Setting up permissions event handlers...');

        try {
            // Setup permissions table event handlers
            if (this.permissionsTable) {
                this.setupPermissionsTableHandlers();
            }

            // Setup roles table event handlers
            if (this.rolesTable) {
                this.setupRolesTableHandlers();
            }

            // Setup admin panel event handlers
            if (this.adminPanel) {
                this.setupAdminPanelHandlers();
            }

            console.log('✅ Permissions event handlers configured');

        } catch (error) {
            console.warn('⚠️ Could not setup all event handlers:', error);
        }
    }

    /**
     * Setup permissions table event handlers
     */
    setupPermissionsTableHandlers() {
        // Add event listeners for permissions table interactions
        // This will be implemented when the permissions table is available
    }

    /**
     * Setup roles table event handlers
     */
    setupRolesTableHandlers() {
        // Add event listeners for roles table interactions
        // This will be implemented when the roles table is available
    }

    /**
     * Setup admin panel event handlers
     */
    setupAdminPanelHandlers() {
        // Add event listeners for admin panel interactions
        // This will be implemented when the admin panel is available
    }

    /**
     * Load permissions data
     */
    async loadPermissionsData() {
        console.log('📊 Loading permissions data...');
        
        try {
            // Load user permissions
            await this.loadUserPermissions();
            
            // Load available roles
            await this.loadAvailableRoles();
            
            console.log('✅ Permissions data loaded successfully');
            
        } catch (error) {
            console.warn('⚠️ Could not load permissions data:', error);
            // Set default permissions for unauthenticated users
            this.setDefaultPermissions();
        }
    }

    /**
     * Setup real-time updates
     */
    setupRealTimeUpdates() {
        console.log('🔄 Setting up real-time permission updates...');
        
        try {
            // Setup permission checking
            if (typeof this.setupPermissionChecking === 'function') {
                this.setupPermissionChecking();
            }
            
            // Setup role-based UI
            if (typeof this.setupRoleBasedUI === 'function') {
                this.setupRoleBasedUI();
            }
            
            // Setup permission-based elements
            if (typeof this.setupPermissionBasedElements === 'function') {
                this.setupPermissionBasedElements();
            }
            
            console.log('✅ Real-time updates configured');
        } catch (error) {
            console.warn('⚠️ Error in setupRealTimeUpdates:', error);
        }
    }

    /**
     * Set default permissions for unauthenticated users
     */
    setDefaultPermissions() {
        this.availableRoles = ['guest'];
        this.currentPermissions = ['read:public'];
        
        // Initialize role definitions with default guest role
        if (!this.roleDefinitions) this.roleDefinitions = {};
        this.roleDefinitions.guest = {
            permissions: ['read:public', 'read:dashboard']
        };
        
        // Set default user permissions
        this.userRoles = ['guest'];
        this.userPermissions = ['read:public', 'read:dashboard'];
        
        console.log('🔒 Default permissions set for unauthenticated user');
    }

    /**
     * Load available roles
     */
    async loadAvailableRoles() {
        console.log('👥 Loading available roles...');
        
        try {
            // For now, set default roles
            this.availableRoles = ['guest', 'user', 'analyst', 'manager', 'admin'];
            console.log('✅ Available roles loaded:', this.availableRoles);
            
        } catch (error) {
            console.warn('⚠️ Could not load available roles:', error);
            this.availableRoles = ['guest'];
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

            const user = authCore.getCurrentUser ? authCore.getCurrentUser() : null;
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
            } else {
                console.log('👤 No authenticated user found, setting default permissions');
                this.setDefaultPermissions();
            }

        } catch (error) {
            console.error('Failed to load user permissions:', error);
            // Set default permissions for unauthenticated users
            this.userRoles = ['guest'];
            if (this.roleDefinitions && this.roleDefinitions.guest && this.roleDefinitions.guest.permissions) {
                this.userPermissions = this.roleDefinitions.guest.permissions;
            } else {
                this.userPermissions = ['read:public', 'read:dashboard'];
            }
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
                    'Authorization': `Bearer ${authCore.getSessionToken ? authCore.getSessionToken() : ''}`
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
        if (typeof this.setupPermissionBasedElements === 'function') {
            this.setupPermissionBasedElements();
        }
    }

    /**
     * Setup role-based UI updates
     */
    setupRoleBasedUI() {
        // Update navigation based on roles
        if (typeof this.updateNavigationVisibility === 'function') {
            this.updateNavigationVisibility();
        }

        // Update dashboard widgets based on permissions
        if (typeof this.updateDashboardVisibility === 'function') {
            this.updateDashboardVisibility();
        }

        // Update action buttons based on permissions
        if (typeof this.updateActionButtons === 'function') {
            this.updateActionButtons();
        }
    }

    /**
     * Setup permission-based elements
     */
    setupPermissionBasedElements() {
        try {
            // Find all elements with data-permission attribute
            const permissionElements = document.querySelectorAll('[data-permission]');
            permissionElements.forEach(element => {
                const permission = element.getAttribute('data-permission');
                if (permission && !this.hasPermission(permission)) {
                    element.style.display = 'none';
                }
            });

            // Find all elements with data-role attribute
            const roleElements = document.querySelectorAll('[data-role]');
            roleElements.forEach(element => {
                const role = element.getAttribute('data-role');
                if (role && !this.hasRole(role)) {
                    element.style.display = 'none';
                }
            });

            // Find all elements with data-any-role attribute
            const anyRoleElements = document.querySelectorAll('[data-any-role]');
            anyRoleElements.forEach(element => {
                const roles = element.getAttribute('data-any-role');
                if (roles) {
                    const roleArray = roles.split(',');
                    if (!this.hasAnyRole(roleArray)) {
                        element.style.display = 'none';
                    }
                }
            });
        } catch (error) {
            console.warn('⚠️ Error in setupPermissionBasedElements:', error);
        }
    }

    /**
     * Update navigation visibility based on permissions
     */
    updateNavigationVisibility() {
        try {
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
                if (navElement && requiredPermissions && Array.isArray(requiredPermissions)) {
                    const hasAccess = requiredPermissions.some(permission => 
                        permission && this.hasPermission(permission)
                    );
                    if (!hasAccess) {
                        navElement.style.display = 'none';
                    }
                }
            });
        } catch (error) {
            console.warn('⚠️ Error in updateNavigationVisibility:', error);
        }
    }

    /**
     * Update dashboard visibility based on permissions
     */
    updateDashboardVisibility() {
        try {
            const dashboardWidgets = {
                'user-stats': ['user:read'],
                'project-stats': ['project:read'],
                'system-stats': ['system:read'],
                'analytics-widget': ['analytics:read'],
                'admin-panel': ['role:read']
            };

            Object.entries(dashboardWidgets).forEach(([widgetId, requiredPermissions]) => {
                const widget = document.getElementById(widgetId);
                if (widget && requiredPermissions && Array.isArray(requiredPermissions)) {
                    const hasAccess = requiredPermissions.some(permission => 
                        permission && this.hasPermission(permission)
                    );
                    if (!hasAccess) {
                        widget.style.display = 'none';
                    }
                }
            });
        } catch (error) {
            console.warn('⚠️ Error in updateDashboardVisibility:', error);
        }
    }

    /**
     * Update action buttons based on permissions
     */
    updateActionButtons() {
        try {
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
                if (button && requiredPermissions && Array.isArray(requiredPermissions)) {
                    const hasAccess = requiredPermissions.some(permission => 
                        permission && this.hasPermission(permission)
                    );
                    if (!hasAccess) {
                        button.style.display = 'none';
                    }
                }
            });
        } catch (error) {
            console.warn('⚠️ Error in updateActionButtons:', error);
        }
    }

    /**
     * Check if user has specific permission
     * @param {string} permission - Permission to check
     * @returns {boolean} Permission status
     */
    hasPermission(permission) {
        if (!permission) return false;

        // Ensure permissionCache is initialized
        if (!this.permissionCache) {
            this.permissionCache = new Map();
        }

        // Check cache first
        if (this.permissionCache.has(permission)) {
            return this.permissionCache.get(permission);
        }

        // Ensure arrays are initialized
        if (!this.userPermissions) this.userPermissions = [];
        if (!this.userRoles) this.userRoles = [];
        if (!this.roleDefinitions) this.roleDefinitions = {};
        
        // Check direct permissions
        const hasDirectPermission = this.userPermissions.includes(permission);
        
        // Check role-based permissions
        const hasRolePermission = this.userRoles.some(role => {
            const roleDef = this.roleDefinitions[role];
            return roleDef && roleDef.permissions && roleDef.permissions.includes(permission);
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
        if (!this.userRoles) this.userRoles = [];
        return this.userRoles.includes(role);
    }

    /**
     * Check if user has any of the specified roles
     * @param {Array} roles - Roles to check
     * @returns {boolean} Role status
     */
    hasAnyRole(roles) {
        if (!Array.isArray(roles) || roles.length === 0) return false;
        if (!this.userRoles) this.userRoles = [];
        return roles.some(role => this.hasRole(role));
    }

    /**
     * Check if user has all of the specified roles
     * @param {Array} roles - Roles to check
     * @returns {boolean} Role status
     */
    hasAllRoles(roles) {
        if (!Array.isArray(roles) || roles.length === 0) return false;
        if (!this.userRoles) this.userRoles = [];
        return roles.every(role => this.hasRole(role));
    }

    /**
     * Get user roles
     * @returns {Array} User roles
     */
    getUserRoles() {
        if (!this.userRoles) this.userRoles = [];
        return [...this.userRoles];
    }

    /**
     * Get user permissions
     * @returns {Array} User permissions
     */
    getUserPermissions() {
        if (!this.userPermissions) this.userPermissions = [];
        return [...this.userPermissions];
    }

    /**
     * Get role definitions
     * @returns {Object} Role definitions
     */
    getRoleDefinitions() {
        if (!this.roleDefinitions) this.roleDefinitions = {};
        return { ...this.roleDefinitions };
    }

    /**
     * Get permissions for a specific role
     * @param {string} role - Role name
     * @returns {Array} Role permissions
     */
    getRolePermissions(role) {
        if (!role) return [];
        if (!this.roleDefinitions) this.roleDefinitions = {};
        const roleDef = this.roleDefinitions[role];
        return roleDef && roleDef.permissions ? [...roleDef.permissions] : [];
    }

    /**
     * Check if user can access a specific resource
     * @param {string} resource - Resource name
     * @param {string} action - Action (read, write, delete)
     * @returns {boolean} Access status
     */
    canAccess(resource, action) {
        if (!resource || !action) return false;
        const permission = `${resource}:${action}`;
        return this.hasPermission(permission);
    }

    /**
     * Check if user can read a resource
     * @param {string} resource - Resource name
     * @returns {boolean} Read access
     */
    canRead(resource) {
        if (!resource) return false;
        return this.canAccess(resource, 'read');
    }

    /**
     * Check if user can write to a resource
     * @param {string} resource - Resource name
     * @returns {boolean} Write access
     */
    canWrite(resource) {
        if (!resource) return false;
        return this.canAccess(resource, 'write');
    }

    /**
     * Check if user can delete a resource
     * @param {string} resource - Resource name
     * @returns {boolean} Delete access
     */
    canDelete(resource) {
        if (!resource) return false;
        return this.canAccess(resource, 'delete');
    }

    /**
     * Get effective permissions for current user
     * @returns {Object} Effective permissions
     */
    getEffectivePermissions() {
        const effectivePermissions = new Set();

        // Ensure arrays are initialized
        if (!this.userPermissions) this.userPermissions = [];
        if (!this.userRoles) this.userRoles = [];
        if (!this.roleDefinitions) this.roleDefinitions = {};

        // Add direct permissions
        this.userPermissions.forEach(permission => {
            effectivePermissions.add(permission);
        });

        // Add role-based permissions
        this.userRoles.forEach(role => {
            const roleDef = this.roleDefinitions[role];
            if (roleDef && roleDef.permissions) {
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
        if (!this.userRoles) this.userRoles = [];
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
                window.location.href = '/api/auth/';
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
        if (this.permissionCache) {
            this.permissionCache.clear();
        }
    }

    /**
     * Refresh permissions
     */
    async refreshPermissions() {
        this.clearPermissionCache();
        await this.loadUserPermissions();
        if (typeof this.setupPermissionBasedElements === 'function') {
            this.setupPermissionBasedElements();
        }
        if (typeof this.updateNavigationVisibility === 'function') {
            this.updateNavigationVisibility();
        }
        if (typeof this.updateDashboardVisibility === 'function') {
            this.updateDashboardVisibility();
        }
        if (typeof this.updateActionButtons === 'function') {
            this.updateActionButtons();
        }
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