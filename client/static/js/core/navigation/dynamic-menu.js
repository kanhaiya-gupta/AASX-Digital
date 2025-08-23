/**
 * Dynamic Menu Generation System
 * =============================
 * 
 * This module handles dynamic menu generation based on user context,
 * permissions, and user types.
 */

class DynamicMenu {
    constructor() {
        this.menuConfig = {
            'aasx-etl': {
                title: 'ETL Pipeline',
                icon: 'fas fa-cogs',
                path: '/aasx-etl',
                permissions: ['read', 'write'],
                submenu: [
                    { title: 'Upload Files', path: '/aasx-etl/upload', permission: 'write', icon: 'fas fa-upload' },
                    { title: 'Process Files', path: '/aasx-etl/process', permission: 'write', icon: 'fas fa-play' },
                    { title: 'View Results', path: '/aasx-etl/results', permission: 'read', icon: 'fas fa-eye' },
                    { title: 'Project Management', path: '/aasx-etl/projects', permission: 'read', icon: 'fas fa-folder' }
                ],
                allowIndependent: true,
                description: 'Process and transform AASX files'
            },
            'twin-registry': {
                title: 'Twin Registry',
                icon: 'fas fa-sync',
                path: '/twin-registry',
                permissions: ['read', 'write'],
                submenu: [
                    { title: 'Create Twin', path: '/twin-registry/create', permission: 'write', icon: 'fas fa-plus' },
                    { title: 'Manage Twins', path: '/twin-registry/manage', permission: 'write', icon: 'fas fa-cog' },
                    { title: 'View Registry', path: '/twin-registry/view', permission: 'read', icon: 'fas fa-list' },
                    { title: 'Twin Analytics', path: '/twin-registry/analytics', permission: 'read', icon: 'fas fa-chart-bar' }
                ],
                allowIndependent: true,
                description: 'Manage digital twins'
            },
            'ai-rag': {
                title: 'AI/RAG System',
                icon: 'fas fa-robot',
                path: '/ai-rag',
                permissions: ['read', 'write'],
                submenu: [
                    { title: 'Analyze Files', path: '/ai-rag/analyze', permission: 'write', icon: 'fas fa-search' },
                    { title: 'Knowledge Base', path: '/ai-rag/knowledge', permission: 'read', icon: 'fas fa-database' },
                    { title: 'Query System', path: '/ai-rag/query', permission: 'read', icon: 'fas fa-question' },
                    { title: 'AI Models', path: '/ai-rag/models', permission: 'write', icon: 'fas fa-brain' }
                ],
                allowIndependent: true,
                description: 'AI-powered analysis and retrieval'
            },
            'kg-neo4j': {
                title: 'Knowledge Graph',
                icon: 'fas fa-project-diagram',
                path: '/kg-neo4j',
                permissions: ['read', 'write'],
                submenu: [
                    { title: 'Graph Explorer', path: '/kg-neo4j/explorer', permission: 'read', icon: 'fas fa-sitemap' },
                    { title: 'Query Builder', path: '/kg-neo4j/query', permission: 'write', icon: 'fas fa-code' },
                    { title: 'Graph Analytics', path: '/kg-neo4j/analytics', permission: 'read', icon: 'fas fa-chart-line' },
                    { title: 'Data Import', path: '/kg-neo4j/import', permission: 'write', icon: 'fas fa-file-import' }
                ],
                allowIndependent: true,
                description: 'Knowledge graph management'
            },
            'certificate-manager': {
                title: 'Certificate Manager',
                icon: 'fas fa-certificate',
                path: '/certificate-manager',
                permissions: ['read', 'write', 'manage'],
                submenu: [
                    { title: 'Generate Certificate', path: '/certificate-manager/generate', permission: 'write', icon: 'fas fa-plus' },
                    { title: 'Manage Certificates', path: '/certificate-manager/manage', permission: 'manage', icon: 'fas fa-cog' },
                    { title: 'Certificate Templates', path: '/certificate-manager/templates', permission: 'write', icon: 'fas fa-file-alt' },
                    { title: 'Compliance Reports', path: '/certificate-manager/reports', permission: 'read', icon: 'fas fa-chart-pie' }
                ],
                allowIndependent: false,
                description: 'Manage certificates and compliance'
            },
            'federated-learning': {
                title: 'Federated Learning',
                icon: 'fas fa-network-wired',
                path: '/federated-learning',
                permissions: ['read', 'write', 'manage'],
                submenu: [
                    { title: 'Training Sessions', path: '/federated-learning/sessions', permission: 'write', icon: 'fas fa-play' },
                    { title: 'Model Management', path: '/federated-learning/models', permission: 'manage', icon: 'fas fa-cogs' },
                    { title: 'Participant Management', path: '/federated-learning/participants', permission: 'manage', icon: 'fas fa-users' },
                    { title: 'Performance Analytics', path: '/federated-learning/analytics', permission: 'read', icon: 'fas fa-chart-bar' }
                ],
                allowIndependent: false,
                description: 'Federated learning system'
            },
            'physics-modeling': {
                title: 'Physics Modeling',
                icon: 'fas fa-atom',
                path: '/physics-modeling',
                permissions: ['read', 'write', 'manage'],
                submenu: [
                    { title: 'Model Builder', path: '/physics-modeling/builder', permission: 'write', icon: 'fas fa-hammer' },
                    { title: 'Simulation Engine', path: '/physics-modeling/simulation', permission: 'write', icon: 'fas fa-rocket' },
                    { title: 'Model Library', path: '/physics-modeling/library', permission: 'read', icon: 'fas fa-book' },
                    { title: 'Analysis Tools', path: '/physics-modeling/analysis', permission: 'read', icon: 'fas fa-tools' }
                ],
                allowIndependent: false,
                description: 'Physics-based modeling'
            },
            'auth': {
                title: 'User Management',
                icon: 'fas fa-users-cog',
                path: '/api/auth/',
                permissions: ['admin'],
                submenu: [
                    { title: 'User Management', path: '/api/auth/admin/users', permission: 'admin', icon: 'fas fa-users' },
                    { title: 'Organization Management', path: '/api/auth/admin/organizations', permission: 'admin', icon: 'fas fa-building' },
                    { title: 'Role Management', path: '/api/auth/admin/roles', permission: 'admin', icon: 'fas fa-user-tag' },
                    { title: 'System Settings', path: '/api/auth/admin/settings', permission: 'admin', icon: 'fas fa-cog' }
                ],
                allowIndependent: false,
                description: 'User and organization management'
            }
        };
    }
    
    /**
     * Generate menu for user context
     */
    generateMenu(userContext) {
        const menu = [];
        
        for (const [moduleKey, moduleConfig] of Object.entries(this.menuConfig)) {
            if (this.canAccessModule(userContext, moduleKey)) {
                const menuItem = this.createMenuItem(moduleKey, moduleConfig, userContext);
                menu.push(menuItem);
            }
        }
        
        return menu;
    }
    
    /**
     * Check if user can access module
     */
    canAccessModule(userContext, moduleKey) {
        const moduleConfig = this.menuConfig[moduleKey];
        if (!moduleConfig) return false;
        
        const requiredPermissions = moduleConfig.permissions;
        
        // Check permissions
        const hasPermissions = requiredPermissions.some(permission => 
            this.userHasPermission(userContext, permission)
        );
        
        // Check if independent users are allowed
        if (userContext.is_independent && !moduleConfig.allowIndependent) {
            return false;
        }
        
        return hasPermissions;
    }
    
    /**
     * Check if user has specific permission
     */
    userHasPermission(userContext, permission) {
        if (!userContext) return false;
        
        // Check if user has the permission
        if (userContext.has_permission) {
            return userContext.has_permission(permission);
        }
        
        // Check permissions array
        if (userContext.permissions && Array.isArray(userContext.permissions)) {
            return userContext.permissions.includes(permission);
        }
        
        // Check role-based permissions
        const rolePermissions = this.getRolePermissions(userContext.role);
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
     * Create menu item for module
     */
    createMenuItem(moduleKey, moduleConfig, userContext) {
        const menuItem = {
            key: moduleKey,
            title: moduleConfig.title,
            icon: moduleConfig.icon,
            path: moduleConfig.path,
            description: moduleConfig.description,
            allowIndependent: moduleConfig.allowIndependent,
            submenu: this.generateSubmenu(moduleConfig.submenu, userContext)
        };
        
        return menuItem;
    }
    
    /**
     * Generate submenu for module
     */
    generateSubmenu(submenuConfig, userContext) {
        if (!submenuConfig) return [];
        
        const submenu = [];
        
        for (const item of submenuConfig) {
            if (this.userHasPermission(userContext, item.permission)) {
                submenu.push({
                    title: item.title,
                    path: item.path,
                    icon: item.icon,
                    permission: item.permission
                });
            }
        }
        
        return submenu;
    }
    
    /**
     * Render menu to DOM
     */
    renderMenu(container, userContext) {
        if (!container) return;
        
        const menu = this.generateMenu(userContext);
        
        // Clear existing menu
        container.innerHTML = '';
        
        // Render menu items
        menu.forEach(item => {
            const menuElement = this.createMenuElement(item);
            container.appendChild(menuElement);
        });
    }
    
    /**
     * Create menu element
     */
    createMenuElement(menuItem) {
        const li = document.createElement('li');
        li.className = 'nav-item';
        li.setAttribute('data-module', menuItem.key);
        
        if (menuItem.submenu && menuItem.submenu.length > 0) {
            // Create dropdown menu
            li.innerHTML = `
                <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                    <i class="${menuItem.icon}"></i> ${menuItem.title}
                </a>
                <ul class="dropdown-menu">
                    ${menuItem.submenu.map(subItem => `
                        <li>
                            <a class="dropdown-item" href="${subItem.path}">
                                <i class="${subItem.icon} me-2"></i>${subItem.title}
                            </a>
                        </li>
                    `).join('')}
                </ul>
            `;
        } else {
            // Create simple menu item
            li.innerHTML = `
                <a class="nav-link" href="${menuItem.path}" title="${menuItem.description}">
                    <i class="${menuItem.icon}"></i> ${menuItem.title}
                </a>
            `;
        }
        
        return li;
    }
    
    /**
     * Update existing navigation with dynamic menu
     */
    updateNavigation(userContext) {
        // Update main navigation dropdown
        const applicationsDropdown = document.querySelector('.navbar-nav .dropdown-menu.mega-dropdown');
        if (applicationsDropdown) {
            this.updateApplicationsDropdown(applicationsDropdown, userContext);
        }
        
        // Update quick actions
        this.updateQuickActions(userContext);
        
        // Update sidebar if exists
        const sidebar = document.querySelector('.sidebar-nav');
        if (sidebar) {
            this.updateSidebar(sidebar, userContext);
        }
    }
    
    /**
     * Update applications dropdown
     */
    updateApplicationsDropdown(container, userContext) {
        const menu = this.generateMenu(userContext);
        
        // Group modules by category
        const categories = {
            'Core Processing': ['aasx-etl', 'twin-registry'],
            'Intelligence': ['ai-rag', 'kg-neo4j'],
            'Advanced Features': ['federated-learning', 'physics-modeling'],
            'Management': ['certificate-manager', 'auth']
        };
        
        // Clear existing content
        const row = container.querySelector('.row');
        if (row) {
            row.innerHTML = '';
            
            // Render categories
            Object.entries(categories).forEach(([categoryName, moduleKeys]) => {
                const categoryModules = menu.filter(item => moduleKeys.includes(item.key));
                if (categoryModules.length > 0) {
                    const categoryElement = this.createCategoryElement(categoryName, categoryModules);
                    row.appendChild(categoryElement);
                }
            });
        }
    }
    
    /**
     * Create category element
     */
    createCategoryElement(categoryName, modules) {
        const col = document.createElement('div');
        col.className = 'col-md-6';
        
        col.innerHTML = `
            <h6 class="dropdown-header">${categoryName}</h6>
            ${modules.map(module => `
                <a class="dropdown-item" href="${module.path}" data-module="${module.key}">
                    <i class="${module.icon} text-primary"></i> ${module.title}
                </a>
            `).join('')}
        `;
        
        return col;
    }
    
    /**
     * Update quick actions
     */
    updateQuickActions(userContext) {
        const quickActionsContainer = document.querySelector('.navbar-nav .dropdown-menu');
        if (!quickActionsContainer) return;
        
        const menu = this.generateMenu(userContext);
        const quickActions = menu.filter(item => 
            ['aasx-etl', 'twin-registry', 'ai-rag'].includes(item.key)
        );
        
        // Update quick actions
        const quickActionsList = quickActionsContainer.querySelectorAll('[data-quick-action]');
        quickActionsList.forEach(action => {
            const actionModule = action.dataset.quickAction;
            const canAccess = quickActions.some(item => item.key === actionModule);
            
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
     * Update sidebar navigation
     */
    updateSidebar(container, userContext) {
        const menu = this.generateMenu(userContext);
        
        container.innerHTML = `
            <ul class="nav flex-column">
                ${menu.map(item => `
                    <li class="nav-item" data-module="${item.key}">
                        <a class="nav-link" href="${item.path}">
                            <i class="${item.icon}"></i> ${item.title}
                        </a>
                        ${item.submenu && item.submenu.length > 0 ? `
                            <ul class="nav flex-column ms-3">
                                ${item.submenu.map(subItem => `
                                    <li class="nav-item">
                                        <a class="nav-link" href="${subItem.path}">
                                            <i class="${subItem.icon}"></i> ${subItem.title}
                                        </a>
                                    </li>
                                `).join('')}
                            </ul>
                        ` : ''}
                    </li>
                `).join('')}
            </ul>
        `;
    }
}

// Export for use in other modules
window.DynamicMenu = DynamicMenu;

