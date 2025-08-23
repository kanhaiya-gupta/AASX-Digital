/**
 * Authentication UI Components - Reusable Interface Elements
 * @description Library of reusable authentication UI components with role-based rendering
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-ui/auth-components
 */

/**
 * Authentication UI Components
 * @description Provides reusable UI components for authentication interfaces
 * @class AuthComponents
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class AuthComponents {
    // Private fields
    #isInitialized = false;
    #components = new Map();
    #templates = new Map();
    #renderQueue = [];
    #componentRegistry = new Map();
    #config = {};
    #componentDefinitions = {};
    #htmlTemplates = {};
    
    /**
     * Create an AuthComponents instance
     * @param {Object} options - Configuration options
     * @param {boolean} options.autoRender - Enable automatic component rendering
     * @param {boolean} options.roleBased - Enable role-based component rendering
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            autoRender: options.autoRender ?? true,
            roleBased: options.roleBased ?? true,
            debug: options.debug ?? false
        };
        
        // Component definitions
        this.#componentDefinitions = {
            // Authentication components
            loginButton: {
                name: 'Login Button',
                description: 'Primary login button with role-based visibility',
                template: 'login-button-template',
                roles: ['guest'],
                attributes: { 'data-auth': 'login', 'class': 'btn btn-primary' }
            },
            signupButton: {
                name: 'Signup Button',
                description: 'User registration button',
                template: 'signup-button-template',
                roles: ['guest'],
                attributes: { 'data-auth': 'signup', 'class': 'btn btn-outline-primary' }
            },
            logoutButton: {
                name: 'Logout Button',
                description: 'User logout button',
                template: 'logout-button-template',
                roles: ['user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'logout', 'class': 'btn btn-outline-danger' }
            },
            profileButton: {
                name: 'Profile Button',
                description: 'User profile access button',
                template: 'profile-button-template',
                roles: ['user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'profile', 'class': 'btn btn-outline-secondary' }
            },
            
            // User interface components
            userMenu: {
                name: 'User Menu',
                description: 'Dropdown user menu with profile options',
                template: 'user-menu-template',
                roles: ['user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'user-menu', 'class': 'dropdown' }
            },
            userInfo: {
                name: 'User Info',
                description: 'Display user information',
                template: 'user-info-template',
                roles: ['user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'user-info', 'class': 'user-info' }
            },
            userAvatar: {
                name: 'User Avatar',
                description: 'User avatar or initials display',
                template: 'user-avatar-template',
                roles: ['user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'user-avatar', 'class': 'user-avatar' }
            },
            userRole: {
                name: 'User Role',
                description: 'Display user role information',
                template: 'user-role-template',
                roles: ['user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'user-role', 'class': 'user-role' }
            },
            
            // Content area components
            guestContent: {
                name: 'Guest Content',
                description: 'Content visible to unauthenticated users',
                template: 'guest-content-template',
                roles: ['guest'],
                attributes: { 'data-auth': 'guest-content', 'class': 'guest-content' }
            },
            authenticatedContent: {
                name: 'Authenticated Content',
                description: 'Content visible to authenticated users',
                template: 'authenticated-content-template',
                roles: ['user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'authenticated-content', 'class': 'authenticated-content' }
            },
            adminPanel: {
                name: 'Admin Panel',
                description: 'Administrative interface panel',
                template: 'admin-panel-template',
                roles: ['admin', 'super_admin'],
                attributes: { 'data-auth': 'admin-panel', 'class': 'admin-panel' }
            },
            userManagement: {
                name: 'User Management',
                description: 'User management interface',
                template: 'user-management-template',
                roles: ['admin', 'super_admin'],
                attributes: { 'data-auth': 'user-management', 'class': 'user-management' }
            },
            
            // Status and loading components
            loadingSpinner: {
                name: 'Loading Spinner',
                description: 'Authentication state loading indicator',
                template: 'loading-spinner-template',
                roles: ['guest', 'user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'loading', 'class': 'loading-spinner' }
            },
            authStatus: {
                name: 'Auth Status',
                description: 'Authentication status display',
                template: 'auth-status-template',
                roles: ['guest', 'user', 'manager', 'admin', 'super_admin'],
                attributes: { 'data-auth': 'status', 'class': 'auth-status' }
            }
        };
        
        // HTML templates
        this.#htmlTemplates = {
            'login-button-template': `
                <button data-auth="login" class="btn btn-primary">
                    <i class="fas fa-sign-in-alt me-2"></i>Login
                </button>
            `,
            'signup-button-template': `
                <button data-auth="signup" class="btn btn-outline-primary">
                    <i class="fas fa-user-plus me-2"></i>Sign Up
                </button>
            `,
            'logout-button-template': `
                <button data-auth="logout" class="btn btn-outline-danger">
                    <i class="fas fa-sign-out-alt me-2"></i>Logout
                </button>
            `,
            'profile-button-template': `
                <button data-auth="profile" class="btn btn-outline-secondary">
                    <i class="fas fa-user me-2"></i>Profile
                </button>
            `,
            'user-menu-template': `
                <div data-auth="user-menu" class="dropdown">
                    <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user me-2"></i><span data-auth="user-info">User</span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" data-auth="profile">
                            <i class="fas fa-user-edit me-2"></i>Edit Profile
                        </a></li>
                        <li><a class="dropdown-item" href="#" data-auth="change-password">
                            <i class="fas fa-key me-2"></i>Change Password
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" data-auth="logout">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
            `,
            'user-info-template': `
                <span data-auth="user-info" class="user-info">
                    <i class="fas fa-user me-2"></i>User
                </span>
            `,
            'user-avatar-template': `
                <div data-auth="user-avatar" class="user-avatar">
                    <img src="" alt="User Avatar" class="avatar-image" style="display: none;">
                    <span class="avatar-initials">U</span>
                </div>
            `,
            'user-role-template': `
                <span data-auth="user-role" class="user-role badge bg-secondary">
                    <i class="fas fa-shield-alt me-1"></i>User
                </span>
            `,
            'guest-content-template': `
                <div data-auth="guest-content" class="guest-content">
                    <div class="welcome-message">
                        <h3>Welcome to AASX Framework</h3>
                        <p>Explore our platform and discover the power of Asset Administration Shells.</p>
                        <div class="cta-buttons">
                            <button data-auth="login" class="btn btn-primary me-2">
                                <i class="fas fa-sign-in-alt me-2"></i>Login
                            </button>
                            <button data-auth="signup" class="btn btn-outline-primary">
                                <i class="fas fa-user-plus me-2"></i>Sign Up
                            </button>
                        </div>
                    </div>
                </div>
            `,
            'authenticated-content-template': `
                <div data-auth="authenticated-content" class="authenticated-content">
                    <div class="user-welcome">
                        <h4>Welcome back, <span data-auth="user-info">User</span>!</h4>
                        <p>You're logged in as a <span data-auth="user-role">User</span>.</p>
                    </div>
                </div>
            `,
            'admin-panel-template': `
                <div data-auth="admin-panel" class="admin-panel">
                    <div class="admin-header">
                        <h4><i class="fas fa-cogs me-2"></i>Administration Panel</h4>
                        <p>Manage system settings and user accounts</p>
                    </div>
                    <div class="admin-actions">
                        <button class="btn btn-primary me-2" data-action="user-management">
                            <i class="fas fa-users me-2"></i>User Management
                        </button>
                        <button class="btn btn-info me-2" data-action="system-logs">
                            <i class="fas fa-file-alt me-2"></i>System Logs
                        </button>
                        <button class="btn btn-warning" data-action="system-metrics">
                            <i class="fas fa-chart-line me-2"></i>System Metrics
                        </button>
                    </div>
                </div>
            `,
            'user-management-template': `
                <div data-auth="user-management" class="user-management">
                    <div class="user-management-header">
                        <h5><i class="fas fa-users me-2"></i>User Management</h5>
                        <button class="btn btn-success btn-sm" data-action="create-user">
                            <i class="fas fa-plus me-1"></i>Add User
                        </button>
                    </div>
                    <div class="user-list">
                        <p class="text-muted">User management interface will be populated here.</p>
                    </div>
                </div>
            `,
            'loading-spinner-template': `
                <div data-auth="loading" class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Checking authentication...</p>
                </div>
            `,
            'auth-status-template': `
                <div data-auth="status" class="auth-status">
                    <div class="status-indicator">
                        <i class="fas fa-circle status-dot"></i>
                        <span class="status-text">Checking...</span>
                    </div>
                </div>
            `,
            
            // Super admin specific templates
            'super-admin-panel-template': `
                <div data-auth="super-admin-panel" class="super-admin-panel">
                    <div class="super-admin-header">
                        <h4><i class="fas fa-crown me-2"></i>Super Administrator Panel</h4>
                        <p>Full system control and configuration</p>
                    </div>
                    <div class="super-admin-actions">
                        <button class="btn btn-danger me-2" data-action="system-config">
                            <i class="fas fa-cog me-2"></i>System Config
                        </button>
                        <button class="btn btn-dark me-2" data-action="backup-restore">
                            <i class="fas fa-database me-2"></i>Backup/Restore
                        </button>
                        <button class="btn btn-warning" data-action="role-management">
                            <i class="fas fa-user-shield me-2"></i>Role Management
                        </button>
                    </div>
                </div>
            `
        };
        
        console.log('🎨 AuthComponents created with config:', this.#config);
    }
    
    /**
     * Initialize the components library
     * @returns {Promise<boolean>} Success status
     * @throws {Error} Initialization error
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ AuthComponents already initialized');
                return true;
            }
            
            console.log('🎨 Initializing AuthComponents...');
            
            // Setup component registry
            this.#setupComponentRegistry();
            
            // Setup HTML templates
            this.#setupHTMLTemplates();
            
            // Setup event listeners
            this.#setupEventListeners();
            
            this.#isInitialized = true;
            console.log('✅ AuthComponents initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ AuthComponents initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Setup component registry
     * @private
     */
    #setupComponentRegistry() {
        try {
            for (const [componentName, definition] of Object.entries(this.#componentDefinitions)) {
                this.#componentRegistry.set(componentName, definition);
            }
            
            console.log(`📋 Component registry setup complete: ${this.#componentRegistry.size} components registered`);
            
        } catch (error) {
            console.error('❌ Component registry setup failed:', error);
        }
    }
    
    /**
     * Setup HTML templates
     * @private
     */
    #setupHTMLTemplates() {
        try {
            for (const [templateName, html] of Object.entries(this.#htmlTemplates)) {
                this.#templates.set(templateName, html);
            }
            
            console.log(`📋 HTML templates setup complete: ${this.#templates.size} templates loaded`);
            
        } catch (error) {
            console.error('❌ HTML templates setup failed:', error);
        }
    }
    
    /**
     * Setup event listeners
     * @private
     */
    #setupEventListeners() {
        try {
            // Listen for component render requests
            window.addEventListener('renderComponent', (event) => {
                this.renderComponent(event.detail.componentName, event.detail.container, event.detail.options);
            });
            
            // Listen for role changes
            window.addEventListener('userRoleChanged', (event) => {
                this.#updateRoleBasedComponents(event.detail.role);
            });
            
            console.log('👂 Event listeners setup complete');
            
        } catch (error) {
            console.error('❌ Event listener setup failed:', error);
        }
    }
    
    /**
     * Render a component
     * @param {string} componentName - Name of the component to render
     * @param {HTMLElement} container - Container element to render into
     * @param {Object} options - Rendering options
     * @returns {HTMLElement|null} Rendered component element
     */
    renderComponent(componentName, container, options = {}) {
        try {
            if (!container) {
                console.warn('⚠️ No container provided for component rendering');
                return null;
            }
            
            const componentDef = this.#componentRegistry.get(componentName);
            if (!componentDef) {
                console.warn(`⚠️ Unknown component: ${componentName}`);
                return null;
            }
            
            // Check role-based access
            if (this.#config.roleBased && options.userRole) {
                if (!componentDef.roles.includes(options.userRole)) {
                    console.log(`🚫 Component ${componentName} not accessible for role: ${options.userRole}`);
                    return null;
                }
            }
            
            // Get template
            const template = this.#templates.get(componentDef.template);
            if (!template) {
                console.warn(`⚠️ Template not found for component: ${componentName}`);
                return null;
            }
            
            // Create component element
            const componentElement = this.#createComponentElement(template, componentDef, options);
            
            // Apply attributes
            this.#applyComponentAttributes(componentElement, componentDef.attributes);
            
            // Render into container
            container.innerHTML = '';
            container.appendChild(componentElement);
            
            // Store component reference
            this.#components.set(componentName, {
                element: componentElement,
                container: container,
                options: options,
                renderedAt: Date.now()
            });
            
            console.log(`✅ Component ${componentName} rendered successfully`);
            
            // Dispatch component rendered event
            this.#dispatchComponentRendered(componentName, componentElement);
            
            return componentElement;
            
        } catch (error) {
            console.error(`❌ Component rendering failed for ${componentName}:`, error);
            return null;
        }
    }
    
    /**
     * Create component element from template
     * @private
     * @param {string} template - HTML template
     * @param {Object} componentDef - Component definition
     * @param {Object} options - Rendering options
     * @returns {HTMLElement} Component element
     */
    #createComponentElement(template, componentDef, options) {
        try {
            // Create temporary container
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = template;
            
            // Get the first child element
            const componentElement = tempContainer.firstElementChild;
            
            // Apply dynamic content if provided
            if (options.content) {
                this.#applyDynamicContent(componentElement, options.content);
            }
            
            // Apply role-specific modifications
            if (options.userRole) {
                this.#applyRoleSpecificModifications(componentElement, options.userRole);
            }
            
            return componentElement;
            
        } catch (error) {
            console.error('❌ Component element creation failed:', error);
            // Return fallback element
            const fallbackElement = document.createElement('div');
            fallbackElement.className = 'component-error';
            fallbackElement.textContent = `Error rendering ${componentDef.name}`;
            return fallbackElement;
        }
    }
    
    /**
     * Apply component attributes
     * @private
     * @param {HTMLElement} element - Component element
     * @param {Object} attributes - Attributes to apply
     */
    #applyComponentAttributes(element, attributes) {
        try {
            for (const [attr, value] of Object.entries(attributes)) {
                if (attr === 'class') {
                    element.classList.add(...value.split(' '));
                } else {
                    element.setAttribute(attr, value);
                }
            }
        } catch (error) {
            console.error('❌ Component attributes application failed:', error);
        }
    }
    
    /**
     * Apply dynamic content to component
     * @private
     * @param {HTMLElement} element - Component element
     * @param {Object} content - Dynamic content
     */
    #applyDynamicContent(element, content) {
        try {
            for (const [selector, value] of Object.entries(content)) {
                const targetElement = element.querySelector(selector);
                if (targetElement) {
                    if (typeof value === 'string') {
                        targetElement.textContent = value;
                    } else if (typeof value === 'object' && value.html) {
                        targetElement.innerHTML = value.html;
                    } else if (typeof value === 'object' && value.attributes) {
                        for (const [attr, attrValue] of Object.entries(value.attributes)) {
                            targetElement.setAttribute(attr, attrValue);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('❌ Dynamic content application failed:', error);
        }
    }
    
    /**
     * Apply role-specific modifications
     * @private
     * @param {HTMLElement} element - Component element
     * @param {string} userRole - User role
     */
    #applyRoleSpecificModifications(element, userRole) {
        try {
            // Add role-specific CSS classes
            element.classList.add(`role-${userRole}`);
            
            // Special handling for super_admin
            if (userRole === 'super_admin') {
                element.classList.add('super-admin');
                
                // Add super admin specific elements
                const superAdminElements = element.querySelectorAll('[data-super-admin]');
                superAdminElements.forEach(el => {
                    el.style.display = '';
                    el.classList.remove('d-none');
                });
            }
            
        } catch (error) {
            console.error('❌ Role-specific modifications failed:', error);
        }
    }
    
    /**
     * Update role-based components
     * @private
     * @param {string} newRole - New user role
     */
    #updateRoleBasedComponents(newRole) {
        try {
            console.log(`🔄 Updating role-based components for role: ${newRole}`);
            
            // Re-render components based on new role
            for (const [componentName, componentInfo] of this.#components) {
                const componentDef = this.#componentRegistry.get(componentName);
                if (componentDef && componentDef.roles.includes(newRole)) {
                    this.renderComponent(componentName, componentInfo.container, {
                        ...componentInfo.options,
                        userRole: newRole
                    });
                }
            }
            
        } catch (error) {
            console.error('❌ Role-based component update failed:', error);
        }
    }
    
    /**
     * Dispatch component rendered event
     * @private
     * @param {string} componentName - Component name
     * @param {HTMLElement} element - Rendered element
     */
    #dispatchComponentRendered(componentName, element) {
        try {
            const event = new CustomEvent('componentRendered', {
                detail: {
                    componentName,
                    element,
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            
        } catch (error) {
            console.error('❌ Component rendered event dispatch failed:', error);
        }
    }
    
    /**
     * Get component definition
     * @param {string} componentName - Component name
     * @returns {Object|null} Component definition
     */
    getComponentDefinition(componentName) {
        return this.#componentRegistry.get(componentName) || null;
    }
    
    /**
     * Get all component definitions
     * @readonly
     * @returns {Object} All component definitions
     */
    get allComponentDefinitions() {
        return Object.fromEntries(this.#componentRegistry);
    }
    
    /**
     * Get HTML template
     * @param {string} templateName - Template name
     * @returns {string|null} HTML template
     */
    getTemplate(templateName) {
        return this.#templates.get(templateName) || null;
    }
    
    /**
     * Get all templates
     * @readonly
     * @returns {Object} All HTML templates
     */
    get allTemplates() {
        return Object.fromEntries(this.#templates);
    }
    
    /**
     * Get rendered component
     * @param {string} componentName - Component name
     * @returns {Object|null} Component information
     */
    getRenderedComponent(componentName) {
        return this.#components.get(componentName) || null;
    }
    
    /**
     * Get all rendered components
     * @readonly
     * @returns {Object} All rendered components
     */
    get allRenderedComponents() {
        return Object.fromEntries(this.#components);
    }
    
    /**
     * Check if component is initialized
     * @readonly
     * @returns {boolean} Initialization status
     */
    get isInitialized() {
        return this.#isInitialized;
    }
    
    /**
     * Get components status
     * @returns {Object} Components status
     */
    getComponentsStatus() {
        return {
            isInitialized: this.#isInitialized,
            autoRender: this.#config.autoRender,
            roleBased: this.#config.roleBased,
            componentRegistrySize: this.#componentRegistry.size,
            templatesSize: this.#templates.size,
            renderedComponentsSize: this.#components.size
        };
    }
    
    /**
     * Create a default AuthComponents instance
     * @static
     * @returns {AuthComponents} New instance with default config
     */
    static createDefault() {
        return new AuthComponents({
            autoRender: true,
            roleBased: true,
            debug: false
        });
    }
}
