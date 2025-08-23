/**
 * Permissions Service - Role-Based Access Control
 * @description Manages user permissions, roles, and access control
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-services/permissions
 */

/**
 * Permissions Service
 * @description Provides comprehensive role-based access control and permission management
 * @class Permissions
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class Permissions {
    // Private fields
    #isInitialized = false;
    #permissionCache = new Map();
    #roleCache = new Map();
    #userPermissions = new Map();
    #config = {};
    #roleHierarchy = {};
    #permissionDefinitions = {};
    #roleDefinitions = {};
    
    /**
     * Create a Permissions instance
     * @param {Object} options - Configuration options
     * @param {boolean} options.strictMode - Enable strict permission checking
     * @param {boolean} options.cachePermissions - Enable permission caching
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            strictMode: options.strictMode ?? true,
            cachePermissions: options.cachePermissions ?? true,
            debug: options.debug ?? false
        };
        
        // Role hierarchy (higher number = more privileges)
        this.#roleHierarchy = {
            guest: 0,
            viewer: 1,
            user: 2,
            manager: 3,
            admin: 4,
            super_admin: 5
        };
        
        // Permission definitions
        this.#permissionDefinitions = {
            // Authentication permissions
            auth: {
                login: ['guest', 'viewer', 'user', 'manager', 'admin', 'super_admin'],
                logout: ['user', 'manager', 'admin', 'super_admin'],
                signup: ['guest'],
                change_password: ['user', 'manager', 'admin', 'super_admin'],
                view_profile: ['user', 'manager', 'admin', 'super_admin'],
                edit_profile: ['user', 'manager', 'admin', 'super_admin']
            },
            
            // Dashboard permissions
            dashboard: {
                view: ['guest', 'viewer', 'user', 'manager', 'admin', 'super_admin'],
                view_charts: ['viewer', 'user', 'manager', 'admin', 'super_admin'],
                view_kpis: ['viewer', 'user', 'manager', 'admin', 'super_admin'],
                view_activity: ['viewer', 'user', 'manager', 'admin', 'super_admin']
            },
            
            // Project permissions
            projects: {
                view_public: ['guest', 'viewer', 'user', 'manager', 'admin', 'super_admin'],
                view_own: ['user', 'manager', 'admin', 'super_admin'],
                view_all: ['manager', 'admin', 'super_admin'],
                create: ['user', 'manager', 'admin', 'super_admin'],
                edit_own: ['user', 'manager', 'admin', 'super_admin'],
                edit_all: ['manager', 'admin', 'super_admin'],
                delete_own: ['user', 'manager', 'admin', 'super_admin'],
                delete_all: ['admin', 'super_admin']
            },
            
            // User management permissions
            users: {
                view_own: ['user', 'manager', 'admin', 'super_admin'],
                view_all: ['manager', 'admin', 'super_admin'],
                create: ['admin', 'super_admin'],
                edit_own: ['user', 'manager', 'admin', 'super_admin'],
                edit_all: ['admin', 'super_admin'],
                delete: ['super_admin'],
                manage_roles: ['admin', 'super_admin']
            },
            
            // System permissions
            system: {
                view_logs: ['admin', 'super_admin'],
                view_metrics: ['admin', 'super_admin'],
            },
            
            // Knowledge Graph permissions
            kg_neo4j: {
                view: ['viewer', 'user', 'manager', 'admin', 'super_admin'],
                view_relationships: ['user', 'manager', 'admin', 'super_admin'],
                edit: ['manager', 'admin', 'super_admin'],
                export: ['manager', 'admin', 'super_admin'],
                admin: ['admin', 'super_admin']
            },
                manage_config: ['super_admin'],
                backup_restore: ['super_admin']
            }
        };
        
        // Role definitions with descriptions
        this.#roleDefinitions = {
            guest: {
                name: 'Guest',
                description: 'Unauthenticated user with limited public access',
                permissions: ['dashboard:view', 'projects:view_public'],
                can_login: false,
                can_signup: true
            },
            viewer: {
                name: 'Viewer',
                description: 'Authenticated user with read-only access',
                permissions: ['dashboard:view', 'dashboard:view_charts', 'dashboard:view_kpis', 'dashboard:view_activity', 'projects:view_public'],
                can_login: true,
                can_signup: false
            },
            user: {
                name: 'User',
                description: 'Standard authenticated user with basic permissions',
                permissions: ['dashboard:view', 'dashboard:view_charts', 'dashboard:view_kpis', 'dashboard:view_activity', 'projects:view_public', 'projects:view_own', 'projects:create', 'projects:edit_own', 'projects:delete_own'],
                can_login: true,
                can_signup: false
            },
            manager: {
                name: 'Manager',
                description: 'User with elevated permissions for team management',
                permissions: ['dashboard:view', 'dashboard:view_charts', 'dashboard:view_kpis', 'dashboard:view_activity', 'projects:view_public', 'projects:view_own', 'projects:view_all', 'projects:create', 'projects:edit_own', 'projects:edit_all', 'projects:delete_own', 'users:view_own', 'users:edit_own'],
                can_login: true,
                can_signup: false
            },
            admin: {
                name: 'Administrator',
                description: 'System administrator with extensive permissions',
                permissions: ['dashboard:view', 'dashboard:view_charts', 'dashboard:view_kpis', 'dashboard:view_activity', 'projects:view_public', 'projects:view_own', 'projects:view_all', 'projects:create', 'projects:edit_own', 'projects:edit_all', 'projects:delete_own', 'projects:delete_all', 'users:view_own', 'users:view_all', 'users:create', 'users:edit_own', 'users:edit_all', 'users:manage_roles', 'system:view_logs', 'system:view_metrics'],
                can_login: true,
                can_signup: false
            },
            super_admin: {
                name: 'Super Administrator',
                description: 'Highest level administrator with all permissions',
                permissions: ['dashboard:view', 'dashboard:view_charts', 'dashboard:view_kpis', 'dashboard:view_activity', 'projects:view_public', 'projects:view_own', 'projects:view_all', 'projects:create', 'projects:edit_own', 'projects:edit_all', 'projects:delete_own', 'projects:delete_all', 'users:view_own', 'users:view_all', 'users:create', 'users:edit_own', 'users:edit_all', 'users:delete', 'users:manage_roles', 'system:view_logs', 'system:view_metrics', 'system:manage_config', 'system:backup_restore'],
                can_login: true,
                can_signup: false
            }
        };
        
        console.log('🔐 Permissions service created with config:', this.#config);
    }
    
    /**
     * Initialize the permissions service
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ Permissions service already initialized');
                return true;
            }
            
            console.log('🔐 Initializing permissions service...');
            
            // Setup permission cache
            this.#buildPermissionCache();
            
            // Setup role cache
            this.#buildRoleCache();
            
            this.#isInitialized = true;
            console.log('✅ Permissions service initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ Permissions service initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Build permission cache for fast lookups
     * @private
     */
    #buildPermissionCache() {
        try {
            for (const [category, permissions] of Object.entries(this.#permissionDefinitions)) {
                for (const [permission, roles] of Object.entries(permissions)) {
                    const permissionKey = `${category}:${permission}`;
                    this.#permissionCache.set(permissionKey, roles);
                }
            }
            
            console.log(`📋 Permission cache built with ${this.#permissionCache.size} permissions`);
            
        } catch (error) {
            console.error('❌ Permission cache build failed:', error);
        }
    }
    
    /**
     * Build role cache for fast lookups
     * @private
     */
    #buildRoleCache() {
        try {
            for (const [role, definition] of Object.entries(this.#roleDefinitions)) {
                this.#roleCache.set(role, definition);
            }
            
            console.log(`📋 Role cache built with ${this.#roleCache.size} roles`);
            
        } catch (error) {
            console.error('❌ Role cache build failed:', error);
        }
    }
    
    /**
     * Check if user has specific permission
     * @param {string} permission - Permission to check (e.g., 'projects:create')
     * @param {string} userRole - User's role
     * @returns {boolean} Has permission
     */
    hasPermission(permission, userRole) {
        try {
            if (!permission || !userRole) {
                return false;
            }
            
            // Check cache first
            if (this.#config.cachePermissions) {
                const cachedRoles = this.#permissionCache.get(permission);
                if (cachedRoles) {
                    return cachedRoles.includes(userRole);
                }
            }
            
            // Fallback to direct lookup
            const [category, action] = permission.split(':');
            if (!category || !action) {
                return false;
            }
            
            const categoryPermissions = this.#permissionDefinitions[category];
            if (!categoryPermissions) {
                return false;
            }
            
            const allowedRoles = categoryPermissions[action];
            if (!allowedRoles) {
                return false;
            }
            
            return allowedRoles.includes(userRole);
            
        } catch (error) {
            console.error(`❌ Permission check failed for ${permission}:`, error);
            return false;
        }
    }
    
    /**
     * Check if user has any of the specified permissions
     * @param {Array} permissions - Array of permissions to check
     * @param {string} userRole - User's role
     * @returns {boolean} Has any permission
     */
    hasAnyPermission(permissions, userRole) {
        try {
            if (!Array.isArray(permissions) || !userRole) {
                return false;
            }
            
            return permissions.some(permission => this.hasPermission(permission, userRole));
            
        } catch (error) {
            console.error('❌ Any permission check failed:', error);
            return false;
        }
    }
    
    /**
     * Check if user has all of the specified permissions
     * @param {Array} permissions - Array of permissions to check
     * @param {string} userRole - User's role
     * @returns {boolean} Has all permissions
     */
    hasAllPermissions(permissions, userRole) {
        try {
            if (!Array.isArray(permissions) || !userRole) {
                return false;
            }
            
            return permissions.every(permission => this.hasPermission(permission, userRole));
            
        } catch (error) {
            console.error('❌ All permissions check failed:', error);
            return false;
        }
    }
    
    /**
     * Check if user role can perform action on resource
     * @param {string} action - Action to perform (e.g., 'create', 'edit', 'delete')
     * @param {string} resource - Resource type (e.g., 'projects', 'users')
     * @param {string} userRole - User's role
     * @param {Object} context - Additional context (e.g., resource ownership)
     * @returns {boolean} Can perform action
     */
    canPerformAction(action, resource, userRole, context = {}) {
        try {
            const permission = `${resource}:${action}`;
            
            // Check basic permission
            if (!this.hasPermission(permission, userRole)) {
                return false;
            }
            
            // Check ownership for edit/delete actions
            if (['edit', 'delete'].includes(action)) {
                if (action === 'edit' && this.hasPermission(`${resource}:edit_all`, userRole)) {
                    return true; // Can edit all
                }
                if (action === 'delete' && this.hasPermission(`${resource}:delete_all`, userRole)) {
                    return true; // Can delete all
                }
                
                // Check if user owns the resource
                if (context.ownerId && context.userId) {
                    return context.ownerId === context.userId;
                }
            }
            
            return true;
            
        } catch (error) {
            console.error(`❌ Action check failed for ${action} on ${resource}:`, error);
            return false;
        }
    }
    
    /**
     * Check if user role can access specific route
     * @param {string} route - Route path (e.g., '/api/projects')
     * @param {string} userRole - User's role
     * @returns {boolean} Can access route
     */
    canAccessRoute(route, userRole) {
        try {
            if (!route || !userRole) {
                return false;
            }
            
            // Public routes
            const publicRoutes = ['/api/dashboard', '/api/auth/login', '/api/auth/signup'];
            if (publicRoutes.includes(route)) {
                return true;
            }
            
            // Route permission mapping
            const routePermissions = {
                '/api/projects': 'projects:view_public',
                '/api/projects/create': 'projects:create',
                '/api/users': 'users:view_all',
                '/api/users/create': 'users:create',
                '/api/system/logs': 'system:view_logs',
                '/api/system/metrics': 'system:view_metrics'
            };
            
            const requiredPermission = routePermissions[route];
            if (!requiredPermission) {
                // Default to requiring authentication
                return userRole !== 'guest';
            }
            
            return this.hasPermission(requiredPermission, userRole);
            
        } catch (error) {
            console.error(`❌ Route access check failed for ${route}:`, error);
            return false;
        }
    }
    
    /**
     * Get all permissions for a role
     * @param {string} role - Role name
     * @returns {Array} Array of permissions
     */
    getRolePermissions(role) {
        try {
            const roleDef = this.#roleDefinitions[role];
            if (!roleDef) {
                return [];
            }
            
            return roleDef.permissions || [];
            
        } catch (error) {
            console.error(`❌ Failed to get permissions for role ${role}:`, error);
            return [];
        }
    }
    
    /**
     * Get all roles that have a specific permission
     * @param {string} permission - Permission to check
     * @returns {Array} Array of roles
     */
    getRolesWithPermission(permission) {
        try {
            const roles = this.#permissionCache.get(permission);
            return roles || [];
            
        } catch (error) {
            console.error(`❌ Failed to get roles for permission ${permission}:`, error);
            return [];
        }
    }
    
    /**
     * Check if role can be assigned by another role
     * @param {string} targetRole - Role to be assigned
     * @param {string} assignerRole - Role doing the assignment
     * @returns {boolean} Can assign role
     */
    canAssignRole(targetRole, assignerRole) {
        try {
            if (!targetRole || !assignerRole) {
                return false;
            }
            
            // Only admins and super_admins can assign roles
            if (!['admin', 'super_admin'].includes(assignerRole)) {
                return false;
            }
            
            // Check role hierarchy
            const assignerLevel = this.#roleHierarchy[assignerRole] || 0;
            const targetLevel = this.#roleHierarchy[targetRole] || 0;
            
            // Can only assign roles at or below assigner's level
            return targetLevel <= assignerLevel;
            
        } catch (error) {
            console.error(`❌ Role assignment check failed:`, error);
            return false;
        }
    }
    
    /**
     * Get role information
     * @param {string} role - Role name
     * @returns {Object|null} Role definition
     */
    getRoleInfo(role) {
        try {
            return this.#roleCache.get(role) || null;
            
        } catch (error) {
            console.error(`❌ Failed to get role info for ${role}:`, error);
            return null;
        }
    }
    
    /**
     * Get all available roles
     * @returns {Object} All role definitions
     */
    getAllRoles() {
        try {
            return { ...this.#roleDefinitions };
            
        } catch (error) {
            console.error('❌ Failed to get all roles:', error);
            return {};
        }
    }
    
    /**
     * Get role hierarchy
     * @returns {Object} Role hierarchy
     */
    getRoleHierarchy() {
        try {
            return { ...this.#roleHierarchy };
            
        } catch (error) {
            console.error('❌ Failed to get role hierarchy:', error);
            return {};
        }
    }
    
    /**
     * Check if role exists
     * @param {string} role - Role name
     * @returns {boolean} Role exists
     */
    roleExists(role) {
        return this.#roleCache.has(role);
    }
    
    /**
     * Check if permission exists
     * @param {string} permission - Permission name
     * @returns {boolean} Permission exists
     */
    permissionExists(permission) {
        return this.#permissionCache.has(permission);
    }
    
    /**
     * Get user permissions summary
     * @param {string} userRole - User's role
     * @returns {Object} Permissions summary
     */
    getUserPermissionsSummary(userRole) {
        try {
            if (!userRole) {
                return { permissions: [], role: null, level: 0 };
            }
            
            const roleInfo = this.getRoleInfo(userRole);
            const permissions = this.getRolePermissions(userRole);
            const level = this.#roleHierarchy[userRole] || 0;
            
            return {
                permissions,
                role: roleInfo,
                level,
                canLogin: roleInfo?.can_login || false,
                canSignup: roleInfo?.can_signup || false
            };
            
        } catch (error) {
            console.error(`❌ Failed to get permissions summary for role ${userRole}:`, error);
            return { permissions: [], role: null, level: 0 };
        }
    }
    
    /**
     * Check if permissions service is initialized
     * @readonly
     * @returns {boolean} Initialization status
     */
    get isInitialized() {
        return this.#isInitialized;
    }
    
    /**
     * Get permissions service status
     * @returns {Object} Service status
     */
    getPermissionsStatus() {
        return {
            isInitialized: this.#isInitialized,
            strictMode: this.#config.strictMode,
            cachePermissions: this.#config.cachePermissions,
            permissionCacheSize: this.#permissionCache.size,
            roleCacheSize: this.#roleCache.size,
            userPermissionsSize: this.#userPermissions.size
        };
    }
    
    /**
     * Create a default Permissions instance
     * @static
     * @returns {Permissions} New instance with default config
     */
    static createDefault() {
        return new Permissions({
            strictMode: true,
            cachePermissions: true,
            debug: false
        });
    }
}
