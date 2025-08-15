/**
 * Role-Based Navigation System
 * ===========================
 * 
 * This module handles dynamic navigation based on user roles, permissions,
 * and user types (independent vs organization members).
 */

class RoleBasedNavigation {
    constructor() {
        this.userContext = null;
        this.navigationConfig = {
            'super_admin': {
                modules: ['aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j', 'certificate-manager', 'federated-learning', 'physics-modeling', 'auth'],
                features: ['all'],
                user_type: 'super_admin'
            },
            'admin': {
                modules: ['aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j', 'certificate-manager', 'federated-learning', 'physics-modeling'],
                features: ['manage_users', 'manage_projects', 'manage_organizations'],
                user_type: 'organization_member'
            },
            'manager': {
                modules: ['aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j', 'certificate-manager'],
                features: ['manage_projects', 'view_analytics'],
                user_type: 'organization_member'
            },
            'user': {
                modules: ['aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j'],
                features: ['create_projects', 'view_own_data'],
                user_type: 'both'  // Both organization_member and independent
            },
            'viewer': {
                modules: ['aasx-etl', 'twin-registry'],
                features: ['view_public_data'],
                user_type: 'both'  // Both organization_member and independent
            }
        };
        
        this.moduleConfig = {
            'aasx-etl': {
                title: 'ETL Pipeline',
                icon: 'fas fa-cogs',
                path: '/api/aasx-etl',
                permissions: ['read', 'write'],
                allowIndependent: true,
                description: 'Process and transform AASX files'
            },
            'twin-registry': {
                title: 'Twin Registry',
                icon: 'fas fa-sync',
                path: '/api/twin-registry',
                permissions: ['read', 'write'],
                allowIndependent: true,
                description: 'Manage digital twins'
            },
            'ai-rag': {
                title: 'AI/RAG System',
                icon: 'fas fa-robot',
                path: '/api/ai-rag',
                permissions: ['read', 'write'],
                allowIndependent: true,
                description: 'AI-powered analysis and retrieval'
            },
            'kg-neo4j': {
                title: 'Knowledge Graph',
                icon: 'fas fa-project-diagram',
                path: '/api/kg-neo4j',
                permissions: ['read', 'write'],
                allowIndependent: true,
                description: 'Knowledge graph management'
            },
            'certificate-manager': {
                title: 'Certificate Manager',
                icon: 'fas fa-certificate',
                path: '/api/certificate-manager',
                permissions: ['read', 'write', 'manage'],
                allowIndependent: false,
                description: 'Manage certificates and compliance'
            },
            'federated-learning': {
                title: 'Federated Learning',
                icon: 'fas fa-network-wired',
                path: '/api/federated-learning',
                permissions: ['read', 'write', 'manage'],
                allowIndependent: false,
                description: 'Federated learning system'
            },
            'physics-modeling': {
                title: 'Physics Modeling',
                icon: 'fas fa-atom',
                path: '/api/physics-modeling',
                permissions: ['read', 'write', 'manage'],
                allowIndependent: false,
                description: 'Physics-based modeling'
            },
            'auth': {
                title: 'User Management',
                icon: 'fas fa-users-cog',
                path: '/api/auth/',
                permissions: ['admin'],
                allowIndependent: false,
                description: 'User and organization management'
            }
        };
    }
    
    /**
     * Initialize the navigation system
     */
    async initialize() {
        try {
            // Get user context from server
            this.userContext = await this.getUserContext();
            
            if (this.userContext) {
                this.updateNavigation();
                this.updateUserMenu();
                this.updateQuickActions();
                this.updateNotifications();
            } else {
                this.showUnauthenticatedState();
            }
        } catch (error) {
            console.error('Error initializing navigation:', error);
            this.showUnauthenticatedState();
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
        const userRole = this.userContext?.role || 'viewer';
        const userType = this.userContext?.getUserType?.() || this.getUserType();
        const config = this.navigationConfig[userRole];
        
        if (config) {
            // Check if user type is allowed
            if (this.isUserTypeAllowed(config.user_type, userType)) {
                this.showModules(config.modules);
                this.showFeatures(config.features);
            } else {
                // Show limited modules for independent users
                const independentModules = this.getIndependentUserModules(userRole);
                this.showModules(independentModules);
                const independentFeatures = this.getIndependentUserFeatures(userRole);
                this.showFeatures(independentFeatures);
            }
        }
        
        // Update module-specific permissions
        this.updateModulePermissions();
    }
    
    /**
     * Check if user type is allowed for the configuration
     */
    isUserTypeAllowed(configUserType, userType) {
        if (configUserType === 'both') return true;
        if (configUserType === userType) return true;
        if (configUserType === 'organization_member' && userType === 'independent') return false;
        return true;
    }
    
    /**
     * Get modules for independent users
     */
    getIndependentUserModules(role) {
        const independentModules = {
            'user': ['aasx-etl', 'twin-registry', 'ai-rag'],
            'viewer': ['aasx-etl', 'twin-registry'],
            'manager': ['aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j'],
            'admin': ['aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j', 'certificate-manager'],
            'super_admin': ['aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j', 'certificate-manager', 'federated-learning', 'physics-modeling', 'auth']
        };
        return independentModules[role] || ['aasx-etl', 'twin-registry'];
    }
    
    /**
     * Get features for independent users
     */
    getIndependentUserFeatures(role) {
        const independentFeatures = {
            'user': ['create_projects', 'view_own_data'],
            'viewer': ['view_public_data'],
            'manager': ['manage_projects', 'view_analytics'],
            'admin': ['manage_projects', 'view_analytics'],
            'super_admin': ['all']
        };
        return independentFeatures[role] || ['view_public_data'];
    }
    
    /**
     * Show/hide modules based on user permissions
     */
    showModules(modules) {
        // Update main navigation dropdown
        const navItems = document.querySelectorAll('[data-module]');
        navItems.forEach(item => {
            const module = item.dataset.module;
            if (modules.includes(module)) {
                item.style.display = 'block';
                item.classList.remove('d-none');
            } else {
                item.style.display = 'none';
                item.classList.add('d-none');
            }
        });
        
        // Update quick actions
        this.updateQuickActions(modules);
    }
    
    /**
     * Show/hide features based on user permissions
     */
    showFeatures(features) {
        const featureItems = document.querySelectorAll('[data-feature]');
        featureItems.forEach(item => {
            const feature = item.dataset.feature;
            if (features.includes('all') || features.includes(feature)) {
                item.style.display = 'block';
                item.classList.remove('d-none');
            } else {
                item.style.display = 'none';
                item.classList.add('d-none');
            }
        });
    }
    
    /**
     * Update module-specific permissions
     */
    updateModulePermissions() {
        Object.entries(this.moduleConfig).forEach(([moduleKey, moduleConfig]) => {
            const moduleElements = document.querySelectorAll(`[data-module="${moduleKey}"]`);
            
            moduleElements.forEach(element => {
                // Check if user can access this module
                const canAccess = this.canAccessModule(moduleKey);
                
                if (canAccess) {
                    element.classList.remove('disabled');
                    element.removeAttribute('disabled');
                } else {
                    element.classList.add('disabled');
                    element.setAttribute('disabled', 'disabled');
                }
                
                // Update tooltips and descriptions
                if (element.hasAttribute('title')) {
                    element.title = moduleConfig.description;
                }
            });
        });
    }
    
    /**
     * Check if user can access a specific module
     */
    canAccessModule(moduleKey) {
        if (!this.userContext) return false;
        
        const moduleConfig = this.moduleConfig[moduleKey];
        if (!moduleConfig) return false;
        
        // Check if independent users are allowed
        if (this.userContext.is_independent && !moduleConfig.allowIndependent) {
            return false;
        }
        
        // Check permissions
        const requiredPermissions = moduleConfig.permissions;
        return requiredPermissions.some(permission => 
            this.userContext.has_permission?.(permission) || 
            this.userContext.permissions?.includes(permission)
        );
    }
    
    /**
     * Update user menu based on authentication status
     */
    updateUserMenu() {
        const authenticatedMenu = document.getElementById('authenticatedMenu');
        const unauthenticatedMenu = document.getElementById('unauthenticatedMenu');
        const userDisplayName = document.getElementById('userDisplayName');
        const adminUsersLink = document.getElementById('adminUsersLink');
        
        if (this.userContext) {
            // Show authenticated menu
            if (authenticatedMenu) authenticatedMenu.style.display = 'block';
            if (unauthenticatedMenu) unauthenticatedMenu.style.display = 'none';
            
            // Update user display name
            if (userDisplayName) {
                userDisplayName.textContent = this.userContext.full_name || this.userContext.username || 'User';
            }
            
            // Show admin features if user has admin role
            if (adminUsersLink) {
                if (this.userContext.role === 'admin' || this.userContext.role === 'super_admin') {
                    adminUsersLink.style.display = 'block';
                } else {
                    adminUsersLink.style.display = 'none';
                }
            }
        } else {
            // Show unauthenticated menu
            if (authenticatedMenu) authenticatedMenu.style.display = 'none';
            if (unauthenticatedMenu) unauthenticatedMenu.style.display = 'block';
        }
    }
    
    /**
     * Update quick actions based on user permissions
     */
    updateQuickActions(modules = null) {
        const quickActions = document.querySelectorAll('[data-quick-action]');
        
        quickActions.forEach(action => {
            const actionModule = action.dataset.quickAction;
            const canAccess = modules ? modules.includes(actionModule) : this.canAccessModule(actionModule);
            
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
     * Update notifications based on user context
     */
    updateNotifications() {
        // This would be implemented to show user-specific notifications
        // For now, we'll just update the notification count
        const notificationBadge = document.querySelector('.navbar-nav .badge');
        if (notificationBadge && this.userContext) {
            // You could fetch actual notification count here
            notificationBadge.textContent = '0';
        }
    }
    
    /**
     * Show unauthenticated state
     */
    showUnauthenticatedState() {
        console.log('🌐 Showing unauthenticated state - all modules visible for exploration');
        
        // Show ALL modules for public exploration (Inspire First philosophy)
        const allModules = [
            'aasx-etl', 'twin-registry', 'ai-rag', 'kg-neo4j', 
            'certificate-manager', 'federated-learning', 'physics-modeling'
        ];
        
        allModules.forEach(module => {
            const items = document.querySelectorAll(`[data-module="${module}"]`);
            items.forEach(item => {
                item.style.display = 'block';
                item.classList.remove('d-none');
                
                // Add visual indicator that this is for exploration
                item.classList.add('public-exploration');
                item.title = `Explore ${module.replace('-', ' ')} capabilities`;
            });
        });
        
        console.log('✅ All modules now visible for public exploration');
    }
    
    /**
     * Get user type from user context
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
    
    /**
     * Refresh navigation (useful after login/logout)
     */
    async refresh() {
        await this.initialize();
    }
}

// Export for use in other modules
window.RoleBasedNavigation = RoleBasedNavigation;

