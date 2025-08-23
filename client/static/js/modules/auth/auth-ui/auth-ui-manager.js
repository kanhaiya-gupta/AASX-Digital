/**
 * Authentication UI Manager - Global UI State Management
 * @description Manages global authentication UI state and coordinates UI updates across all pages
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 * @module auth/auth-ui/auth-ui-manager
 */

/**
 * Authentication UI Manager
 * @description Coordinates all authentication UI elements and manages global UI state
 * @class AuthUIManager
 * @author AASX Framework Team
 * @version 1.0.0
 * @since 2025-08-12
 */
export default class AuthUIManager {
    // Private fields
    #isInitialized = false;
    #currentState = 'unauthenticated';
    #uiElements = new Map();
    #uiStates = new Map();
    #notificationQueue = [];
    #updateQueue = [];
    #config = {};
    #uiSelectors = {};
    #eventListeners = new Map();
    
    /**
     * Create an AuthUIManager instance
     * @param {Object} options - Configuration options
     * @param {boolean} options.autoUpdate - Enable automatic UI updates
     * @param {boolean} options.showNotifications - Enable user notifications
     * @param {boolean} options.debug - Enable debug logging
     */
    constructor(options = {}) {
        // Configuration
        this.#config = {
            autoUpdate: options.autoUpdate ?? true,
            showNotifications: options.showNotifications ?? true,
            debug: options.debug ?? false
        };
        
        // UI state definitions
        this.#uiStates = new Map([
            ['unauthenticated', {
                name: 'Unauthenticated',
                description: 'User is not logged in',
                showElements: ['loginButton', 'signupButton', 'guestContent'],
                hideElements: ['userMenu', 'logoutButton', 'profileButton', 'authenticatedContent'],
                cssClasses: ['unauthenticated', 'guest-mode'],
                removeClasses: ['authenticated', 'user-mode', 'admin-mode']
            }],
            ['authenticated', {
                name: 'Authenticated',
                description: 'User is logged in',
                showElements: ['userMenu', 'logoutButton', 'profileButton', 'authenticatedContent'],
                hideElements: ['loginButton', 'signupButton', 'guestContent'],
                cssClasses: ['authenticated', 'user-mode'],
                removeClasses: ['unauthenticated', 'guest-mode']
            }],
            ['admin', {
                name: 'Administrator',
                description: 'User has administrative privileges',
                showElements: ['userMenu', 'logoutButton', 'profileButton', 'authenticatedContent', 'adminPanel', 'userManagement'],
                hideElements: ['loginButton', 'signupButton', 'guestContent'],
                cssClasses: ['authenticated', 'admin-mode'],
                removeClasses: ['unauthenticated', 'guest-mode', 'user-mode']
            }],
            ['loading', {
                name: 'Loading',
                description: 'Authentication state is being determined',
                showElements: ['loadingSpinner'],
                hideElements: ['loginButton', 'signupButton', 'userMenu', 'logoutButton'],
                cssClasses: ['loading'],
                removeClasses: ['authenticated', 'unauthenticated', 'guest-mode', 'user-mode', 'admin-mode']
            }]
        ]);
        
        // UI element selectors - Updated to work with existing navigation
        this.#uiSelectors = {
            // Authentication buttons
            loginButton: '[data-auth="login"]',
            signupButton: '[data-auth="signup"]',
            logoutButton: '#logoutButton',  // Use existing ID
            profileButton: '[data-auth="profile"]',
            
            // User interface elements
            userMenu: '#userTab',  // Use existing ID
            userInfo: '#userDisplayName',  // Use existing ID
            userAvatar: '[data-auth="user-avatar"]',
            userRole: '[data-auth="user-role"]',
            
            // Content areas
            guestContent: '#unauthenticatedMenu',  // Use existing ID
            authenticatedContent: '#authenticatedMenu',  // Use existing ID
            adminPanel: '[data-auth="admin-panel"]',
            userManagement: '#adminUsersLink',  // Use existing ID
            
            // Loading and status
            loadingSpinner: '[data-auth="loading"]',
            authStatus: '[data-auth="status"]',
            notificationArea: '[data-auth="notifications"]'
        };
        
        // Event listeners
        this.#eventListeners = new Map();
        
        console.log('🎨 AuthUIManager created with config:', this.#config);
    }
    
    /**
     * Initialize Bootstrap tabs for the authentication interface
     * @private
     */
    #initializeBootstrapTabs() {
        try {
            console.log('🔧 Initializing Bootstrap tabs...');
            
            // Wait for Bootstrap to be fully loaded
            if (typeof bootstrap === 'undefined') {
                console.log('⏳ Waiting for Bootstrap to load...');
                setTimeout(() => this.#initializeBootstrapTabs(), 100);
                return;
            }
            
            // Get all tab buttons
            const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
            console.log(`Found ${tabButtons.length} tab buttons`);
            
            // Initialize each tab with proper error handling
            tabButtons.forEach((tabButton, index) => {
                try {
                    // Check if tab is already initialized
                    if (tabButton._tab) {
                        console.log(`✅ Tab ${index + 1} already initialized: ${tabButton.id}`);
                        return;
                    }
                    
                    // Create Bootstrap Tab instance using the correct API
                    const tab = new bootstrap.Tab(tabButton);
                    
                    // Store reference to prevent double initialization
                    tabButton._tab = tab;
                    
                    console.log(`✅ Tab ${index + 1} initialized: ${tabButton.id}`);
                    
                    // Add click event listener for debugging
                    tabButton.addEventListener('click', (e) => {
                        console.log(`🖱️ Tab clicked: ${tabButton.id} -> ${tabButton.getAttribute('data-bs-target')}`);
                    });
                    
                } catch (error) {
                    console.error(`❌ Failed to initialize tab ${index + 1}:`, error);
                }
            });
            
            console.log('✅ Bootstrap tabs initialization complete');
        } catch (error) {
            console.error('❌ Bootstrap tabs initialization failed:', error);
        }
    }
    
    /**
     * Setup fallback tab handling to ensure tabs work even if Bootstrap fails
     * @private
     */
    #setupFallbackTabHandling() {
        try {
            console.log('🔧 Setting up fallback tab handling...');
            
            // Get all tab buttons and content panes
            const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
            const tabPanes = document.querySelectorAll('.tab-pane');
            
            console.log(`Found ${tabButtons.length} tab buttons and ${tabPanes.length} tab panes`);
            
            // Add fallback click handlers
            tabButtons.forEach((tabButton) => {
                const targetId = tabButton.getAttribute('data-bs-target');
                if (!targetId) return;
                
                // Remove existing fallback listeners to prevent duplicates
                tabButton.removeEventListener('click', tabButton._fallbackHandler);
                
                // Create fallback handler
                tabButton._fallbackHandler = (e) => {
                    e.preventDefault();
                    
                    console.log(`🔄 Fallback tab handler: ${tabButton.id} -> ${targetId}`);
                    
                    // Hide all tab panes
                    tabPanes.forEach(pane => {
                        pane.classList.remove('show', 'active');
                    });
                    
                    // Remove active class from all tab buttons
                    tabButtons.forEach(btn => {
                        btn.classList.remove('active');
                    });
                    
                    // Show target tab pane
                    const targetPane = document.querySelector(targetId);
                    if (targetPane) {
                        targetPane.classList.add('show', 'active');
                        console.log(`✅ Showed tab pane: ${targetId}`);
                    } else {
                        console.warn(`⚠️ Target tab pane not found: ${targetId}`);
                    }
                    
                    // Activate clicked tab button
                    tabButton.classList.add('active');
                    
                    console.log(`✅ Fallback tab switching completed for: ${targetId}`);
                };
                
                // Add fallback listener
                tabButton.addEventListener('click', tabButton._fallbackHandler);
                console.log(`✅ Fallback handler added for tab: ${tabButton.id}`);
            });
            
            console.log('✅ Fallback tab handling setup complete');
            
        } catch (error) {
            console.error('❌ Fallback tab handling setup failed:', error);
        }
    }

    /**
     * Initialize the AuthUIManager
     * @returns {Promise<boolean>} Success status
     */
    async initialize() {
        try {
            if (this.#isInitialized) {
                console.log('⚠️ AuthUIManager already initialized');
                return true;
            }
            
            console.log('🎨 Initializing AuthUIManager...');
            
            // Initialize Bootstrap tabs
            this.#initializeBootstrapTabs();
            
            // Setup fallback tab handling
            this.#setupFallbackTabHandling();
            
            // Discover UI elements
            await this.#discoverUIElements();
            
            // Setup event listeners
            this.#setupEventListeners();
            
            // Setup notification system
            this.#setupNotificationSystem();
            
            // CRITICAL FIX: Initialize proper authentication state
            await this.#initializeAuthenticationState();
            
            this.#isInitialized = true;
            console.log('✅ AuthUIManager initialized successfully');
            
            return true;
            
        } catch (error) {
            console.error('❌ AuthUIManager initialization failed:', error);
            return false;
        }
    }
    
    /**
     * Initialize proper authentication state after UI elements are discovered
     * @private
     */
    async #initializeAuthenticationState() {
        try {
            console.log('🔐 Initializing authentication state...');
            
            // Check if we have an auth manager with session info
            if (window.authManager) {
                const sessionInfo = window.authManager.getSessionInfo();
                console.log('📋 Session info from auth manager:', sessionInfo);
                
                if (sessionInfo.isAuthenticated) {
                    console.log('✅ User is authenticated, transitioning to authenticated state');
                    this.#updateUIState('authenticated');
                    this.#updateUserInfo(sessionInfo.user);
                    this.#updateUserRole(sessionInfo.role);
                } else {
                    console.log('🔓 User is not authenticated, transitioning to unauthenticated state');
                    this.#updateUIState('unauthenticated');
                }
            } else {
                console.log('⚠️ No auth manager found, defaulting to unauthenticated state');
                this.#updateUIState('unauthenticated');
            }
            
            console.log('✅ Authentication state initialization complete');
            
        } catch (error) {
            console.error('❌ Authentication state initialization failed:', error);
            // Fallback to unauthenticated state
            this.#updateUIState('unauthenticated');
        }
    }
    
    /**
     * Discover UI elements on the page
     * @private
     */
    async #discoverUIElements() {
        try {
            console.log('🔍 Discovering UI elements...');
            
            for (const [elementName, selector] of Object.entries(this.#uiSelectors)) {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    this.#uiElements.set(elementName, elements);
                    console.log(`✅ Found ${elements.length} ${elementName} elements`);
                } else {
                    console.log(`⚠️ No ${elementName} elements found`);
                }
            }
            
            console.log(`📋 UI discovery complete: ${this.#uiElements.size} element types found`);
            
        } catch (error) {
            console.error('❌ UI element discovery failed:', error);
        }
    }
    
    /**
     * Setup event listeners
     * @private
     */
    #setupEventListeners() {
        try {
            // Listen for authentication state changes
            window.addEventListener('authStateChanged', (event) => {
                this.#handleAuthStateChange(event.detail);
            });
            
            // Listen for logout requests
            window.addEventListener('logoutRequested', (event) => {
                this.showUnauthenticatedState();
            });
            
            // Listen for user profile updates
            window.addEventListener('userProfileUpdated', (event) => {
                this.#updateUserInfo(event.detail);
            });
            
            // Listen for permission changes
            window.addEventListener('permissionsChanged', (event) => {
                this.#updatePermissions(event.detail);
            });
            
            console.log('👂 Event listeners setup complete');
            
        } catch (error) {
            console.error('❌ Event listener setup failed:', error);
        }
    }
    
    /**
     * Setup notification system
     * @private
     */
    #setupNotificationSystem() {
        try {
            // Create notification area if it doesn't exist
            if (!document.querySelector(this.#uiSelectors.notificationArea)) {
                const notificationArea = document.createElement('div');
                notificationArea.setAttribute('data-auth', 'notifications');
                notificationArea.className = 'auth-notifications';
                notificationArea.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    max-width: 400px;
                `;
                document.body.appendChild(notificationArea);
            }
            
            console.log('🔔 Notification system setup complete');
            
        } catch (error) {
            console.error('❌ Notification system setup failed:', error);
        }
    }
    
    /**
     * Handle authentication state changes
     * @private
     * @param {Object} state - New authentication state
     */
    #handleAuthStateChange(state) {
        try {
            console.log('🔄 Handling auth state change:', state);
            
            if (state.isAuthenticated) {
                const userRole = state.role || 'user';
                this.#updateUIState('authenticated');
                this.#updateUserInfo(state.user);
                this.#updateUserRole(userRole);
                
                // Check if user is admin
                if (['admin', 'super_admin'].includes(userRole)) {
                    this.#updateUIState('admin');
                }
            } else {
                this.#updateUIState('unauthenticated');
                this.#clearUserInfo();
            }
            
        } catch (error) {
            console.error('❌ Auth state change handling failed:', error);
        }
    }
    
    /**
     * Update UI to a specific state
     * @private
     * @param {string} stateName - State name to transition to
     */
    #updateUIState(stateName) {
        try {
            console.log(`🎨 Updating UI to state: ${stateName}`);
            
            const state = this.#uiStates.get(stateName);
            if (!state) {
                console.error(`❌ Unknown UI state: ${stateName}`);
                return;
            }
            
            console.log(`📋 State definition: ${state.name} - ${state.description}`);
            console.log(`👁️ Show elements: ${state.showElements.join(', ')}`);
            console.log(`🙈 Hide elements: ${state.hideElements.join(', ')}`);
            
            // Apply state changes
            this.#showElements(state.showElements);
            this.#hideElements(state.hideElements);
            this.#addCSSClasses(state.cssClasses);
            this.#removeCSSClasses(state.removeClasses);
            
            // Update current state
            this.#currentState = stateName;
            
            // Also update existing navigation for backward compatibility
            this.#updateExistingNavigation(stateName);
            
            // Dispatch UI state change event
            this.#dispatchUIStateChange(stateName, state);
            
            console.log(`✅ UI state updated to: ${stateName}`);
            
        } catch (error) {
            console.error(`❌ UI state update failed for ${stateName}:`, error);
        }
    }
    
    /**
     * Show specified elements
     * @private
     * @param {Array} elementNames - Names of elements to show
     */
    #showElements(elementNames) {
        console.log(`🔍 Showing elements: ${elementNames.join(', ')}`);
        for (const elementName of elementNames) {
            const elements = this.#uiElements.get(elementName);
            if (elements) {
                elements.forEach(element => {
                    element.style.display = '';
                    element.classList.remove('d-none', 'hidden');
                    console.log(`✅ Shown: ${elementName} (${element.id || element.className})`);
                });
            } else {
                console.log(`⚠️ No elements found for: ${elementName}`);
            }
        }
    }
    
    /**
     * Hide specified elements
     * @private
     * @param {Array} elementNames - Names of elements to hide
     */
    #hideElements(elementNames) {
        console.log(`🔍 Hiding elements: ${elementNames.join(', ')}`);
        for (const elementName of elementNames) {
            const elements = this.#uiElements.get(elementName);
            if (elements) {
                elements.forEach(element => {
                    element.style.display = 'none';
                    console.log(`✅ Hidden: ${elementName} (${element.id || element.className})`);
                });
            } else {
                console.log(`⚠️ No elements found for: ${elementName}`);
            }
        }
    }
    
    /**
     * Add CSS classes to body
     * @private
     * @param {Array} classes - CSS classes to add
     */
    #addCSSClasses(classes) {
        for (const className of classes) {
            document.body.classList.add(className);
        }
    }
    
    /**
     * Remove CSS classes from body
     * @private
     * @param {Array} classes - CSS classes to remove
     */
    #removeCSSClasses(classes) {
        for (const className of classes) {
            document.body.classList.remove(className);
        }
    }
    
    /**
     * Update user information in UI
     * @private
     * @param {Object} user - User information
     */
    #updateUserInfo(user) {
        try {
            if (!user) {
                console.log('⚠️ No user data provided for updateUserInfo');
                return;
            }
            
            console.log(`👤 Updating user info for: ${user.username || user.email || 'Unknown'}`);
            
            // Update user info elements
            const userInfoElements = this.#uiElements.get('userInfo');
            if (userInfoElements) {
                userInfoElements.forEach(element => {
                    element.textContent = user.username || user.email || 'User';
                    console.log(`✅ Updated userInfo element: ${element.textContent}`);
                });
            } else {
                console.log('⚠️ No userInfo elements found in uiElements');
            }
            
            // Also update existing navigation user display
            const existingUserDisplay = document.getElementById('userDisplayName');
            if (existingUserDisplay) {
                existingUserDisplay.textContent = user.username || user.email || 'User';
                console.log(`🔧 Updated existing navigation user display: ${existingUserDisplay.textContent}`);
            } else {
                console.log('⚠️ No userDisplayName element found in navigation');
            }
            
            // Update user avatar elements
            const userAvatarElements = this.#uiElements.get('userAvatar');
            if (userAvatarElements) {
                userAvatarElements.forEach(element => {
                    if (user.avatar) {
                        element.src = user.avatar;
                        element.alt = user.username || 'User Avatar';
                    } else {
                        // Generate initials avatar
                        const initials = this.#generateInitials(user.username || user.email || 'U');
                        element.textContent = initials;
                        element.className = 'user-avatar-initials';
                    }
                });
            }
            
            console.log('✅ User info update completed');
            
        } catch (error) {
            console.error('❌ User info update failed:', error);
        }
    }
    
    /**
     * Update user role in UI
     * @private
     * @param {string} role - User role
     */
    #updateUserRole(role) {
        try {
            const userRoleElements = this.#uiElements.get('userRole');
            if (userRoleElements) {
                userRoleElements.forEach(element => {
                    element.textContent = role;
                    element.className = `user-role user-role-${role}`;
                });
            }
            
        } catch (error) {
            console.error('❌ User role update failed:', error);
        }
    }
    
    /**
     * Clear user information from UI
     * @private
     */
    #clearUserInfo() {
        try {
            // Clear user info elements
            const userInfoElements = this.#uiElements.get('userInfo');
            if (userInfoElements) {
                userInfoElements.forEach(element => {
                    element.textContent = '';
                });
            }
            
            // Clear user avatar elements
            const userAvatarElements = this.#uiElements.get('userAvatar');
            if (userAvatarElements) {
                userAvatarElements.forEach(element => {
                    element.src = '';
                    element.alt = '';
                    element.textContent = '';
                    element.className = '';
                });
            }
            
            // Clear user role elements
            const userRoleElements = this.#uiElements.get('userRole');
            if (userRoleElements) {
                userRoleElements.forEach(element => {
                    element.textContent = '';
                    element.className = '';
                });
            }
            
        } catch (error) {
            console.error('❌ User info clear failed:', error);
        }
    }
    
    /**
     * Update permissions in UI
     * @private
     * @param {Object} permissions - User permissions
     */
    #updatePermissions(permissions) {
        try {
            // Update admin panel visibility
            if (permissions.admin || permissions.super_admin) {
                this.#showElements(['adminPanel', 'userManagement']);
            } else {
                this.#hideElements(['adminPanel', 'userManagement']);
            }
            
        } catch (error) {
            console.error('❌ Permissions update failed:', error);
        }
    }
    
    /**
     * Generate user initials for avatar
     * @private
     * @param {string} text - Text to generate initials from
     * @returns {string} User initials
     */
    #generateInitials(text) {
        try {
            if (!text) return 'U';
            
            const words = text.split(' ');
            if (words.length === 1) {
                return text.substring(0, 2).toUpperCase();
            } else {
                return (words[0][0] + words[words.length - 1][0]).toUpperCase();
            }
            
        } catch (error) {
            return 'U';
        }
    }
    
    /**
     * Dispatch UI state change event
     * @private
     * @param {string} stateName - New state name
     * @param {Object} state - State definition
     */
    #dispatchUIStateChange(stateName, state) {
        try {
            const event = new CustomEvent('uiStateChanged', {
                detail: {
                    state: stateName,
                    stateDefinition: state,
                    timestamp: Date.now()
                }
            });
            
            window.dispatchEvent(event);
            console.log('🔄 UI state change event dispatched');
            
        } catch (error) {
            console.error('❌ UI state change event dispatch failed:', error);
        }
    }
    
    /**
     * Show unauthenticated state
     * @public
     */
    showUnauthenticatedState() {
        this.#updateUIState('unauthenticated');
    }
    
    /**
     * Show authenticated state
     * @public
     */
    showAuthenticatedState() {
        this.#updateUIState('authenticated');
        
        // Also update the existing navigation structure
        this.#updateExistingNavigation('authenticated');
    }
    
    /**
     * Show unauthenticated state
     * @public
     */
    showUnauthenticatedState() {
        this.#updateUIState('unauthenticated');
        
        // Also update the existing navigation structure
        this.#updateExistingNavigation('unauthenticated');
    }
    
    /**
     * Update existing navigation structure (for backward compatibility)
     * @private
     * @param {string} state - Authentication state
     */
    #updateExistingNavigation(state) {
        try {
            console.log(`🔧 Updating existing navigation for state: ${state}`);
            
            const unauthenticatedMenu = document.getElementById('unauthenticatedMenu');
            const authenticatedMenu = document.getElementById('authenticatedMenu');
            const loginButtonContainer = document.getElementById('loginButtonContainer');
            
            if (state === 'authenticated') {
                // Show authenticated menu, hide unauthenticated
                if (unauthenticatedMenu) {
                    unauthenticatedMenu.style.display = 'none';
                    console.log('✅ Hidden unauthenticated menu');
                }
                if (authenticatedMenu) {
                    authenticatedMenu.style.display = 'block';
                    console.log('✅ Shown authenticated menu');
                }
                if (loginButtonContainer) {
                    loginButtonContainer.style.display = 'none';
                    console.log('✅ Hidden login button container');
                }
            } else if (state === 'unauthenticated') {
                // Show unauthenticated menu, hide authenticated
                if (unauthenticatedMenu) {
                    unauthenticatedMenu.style.display = 'block';
                    console.log('✅ Shown unauthenticated menu');
                }
                if (authenticatedMenu) {
                    authenticatedMenu.style.display = 'none';
                    console.log('✅ Hidden authenticated menu');
                }
                if (loginButtonContainer) {
                    loginButtonContainer.style.display = 'block';
                    console.log('✅ Shown login button container');
                }
            } else if (state === 'loading') {
                // Hide both menus during loading
                if (unauthenticatedMenu) unauthenticatedMenu.style.display = 'none';
                if (authenticatedMenu) authenticatedMenu.style.display = 'none';
                if (loginButtonContainer) loginButtonContainer.style.display = 'none';
                console.log('⏳ Hidden all menus during loading');
            }
            
            console.log(`✅ Updated existing navigation for state: ${state}`);
        } catch (error) {
            console.error('❌ Failed to update existing navigation:', error);
        }
    }
    
    /**
     * Show loading state
     * @public
     */
    showLoadingState() {
        this.#updateUIState('loading');
    }
    
    /**
     * Show notification
     * @param {Object} notification - Notification object
     * @param {string} notification.type - Notification type (success, error, warning, info)
     * @param {string} notification.message - Notification message
     * @param {number} notification.duration - Display duration in milliseconds
     */
    showNotification(notification) {
        try {
            if (!this.#config.showNotifications) return;
            
            const { type = 'info', message, duration = 5000 } = notification;
            
            // Create notification element
            const notificationElement = document.createElement('div');
            notificationElement.className = `auth-notification auth-notification-${type}`;
            notificationElement.innerHTML = `
                <div class="notification-content">
                    <span class="notification-message">${message}</span>
                    <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
                </div>
            `;
            
            // Add to notification area
            const notificationArea = document.querySelector(this.#uiSelectors.notificationArea);
            if (notificationArea) {
                notificationArea.appendChild(notificationElement);
                
                // Auto-remove after duration
                setTimeout(() => {
                    if (notificationElement.parentElement) {
                        notificationElement.remove();
                    }
                }, duration);
                
                console.log(`🔔 Notification shown: ${type} - ${message}`);
            }
            
        } catch (error) {
            console.error('❌ Notification display failed:', error);
        }
    }
    
    /**
     * Update UI based on authentication data
     * @param {Object} authData - Authentication data
     */
    updateUI(authData) {
        try {
            console.log('🎨 AuthUIManager.updateUI called with:', authData);
            
            if (!authData) {
                console.log('⚠️ No auth data provided, defaulting to unauthenticated');
                this.#updateUIState('unauthenticated');
                this.#updateExistingNavigation('unauthenticated');
                return;
            }
            
            if (authData.isAuthenticated) {
                console.log('✅ Updating UI to authenticated state for user:', authData.user?.username);
                this.#updateUIState('authenticated');
                this.#updateUserInfo(authData.user);
                this.#updateUserRole(authData.role);
                this.#updateExistingNavigation('authenticated');
            } else {
                console.log('🔓 Updating UI to unauthenticated state');
                this.#updateUIState('unauthenticated');
                this.#updateExistingNavigation('unauthenticated');
            }
            
            console.log('✅ UI update completed successfully');
            
        } catch (error) {
            console.error('❌ UI update failed:', error);
            // Fallback to unauthenticated state
            this.#updateUIState('unauthenticated');
            this.#updateExistingNavigation('unauthenticated');
        }
    }
    
    /**
     * Refresh UI elements
     * @returns {Promise<boolean>} Success status
     */
    async refreshUI() {
        try {
            console.log('🔄 Refreshing UI elements...');
            
            // Re-discover UI elements
            await this.#discoverUIElements();
            
            // Re-apply current state
            this.#updateUIState(this.#currentState);
            
            // If we're still in loading state and have auth data, transition to proper state
            if (this.#currentState === 'loading' && window.authManager) {
                const sessionInfo = window.authManager.getSessionInfo();
                if (sessionInfo.isAuthenticated) {
                    console.log('🔄 Transitioning from loading to authenticated state');
                    this.#updateUIState('authenticated');
                } else {
                    console.log('🔄 Transitioning from loading to unauthenticated state');
                    this.#updateUIState('unauthenticated');
                }
            }
            
            console.log('✅ UI refresh complete');
            return true;
            
        } catch (error) {
            console.error('❌ UI refresh failed:', error);
            return false;
        }
    }
    
    /**
     * Get current UI state
     * @readonly
     * @returns {string} Current UI state
     */
    get currentState() {
        return this.#currentState;
    }
    
    /**
     * Get UI state definition
     * @param {string} stateName - State name
     * @returns {Object|null} State definition
     */
    getUIState(stateName) {
        return this.#uiStates.get(stateName) || null;
    }
    
    /**
     * Get all UI states
     * @readonly
     * @returns {Object} All UI states
     */
    get allUIStates() {
        return Object.fromEntries(this.#uiStates);
    }
    
    /**
     * Get UI elements
     * @param {string} elementName - Element name
     * @returns {NodeList|null} UI elements
     */
    getUIElements(elementName) {
        return this.#uiElements.get(elementName) || null;
    }
    
    /**
     * Check if UI manager is initialized
     * @readonly
     * @returns {boolean} Initialization status
     */
    get isInitialized() {
        return this.#isInitialized;
    }
    
    /**
     * Get UI manager status
     * @returns {Object} Manager status
     */
    getUIStatus() {
        return {
            isInitialized: this.#isInitialized,
            currentState: this.#currentState,
            autoUpdate: this.#config.autoUpdate,
            showNotifications: this.#config.showNotifications,
            uiElementsCount: this.#uiElements.size,
            uiStatesCount: this.#uiStates.size
        };
    }
    
    /**
     * Manually switch to a specific tab (for debugging and manual control)
     * @param {string} tabId - ID of the tab to switch to
     * @returns {boolean} Success status
     */
    switchToTab(tabId) {
        try {
            console.log(`🔄 Manually switching to tab: ${tabId}`);
            
            // Find the tab button
            const tabButton = document.querySelector(`[data-bs-target="#${tabId}"]`);
            if (!tabButton) {
                console.error(`❌ Tab button not found for target: ${tabId}`);
                return false;
            }
            
            // Find the tab pane
            const tabPane = document.querySelector(`#${tabId}`);
            if (!tabPane) {
                console.error(`❌ Tab pane not found: ${tabId}`);
                return false;
            }
            
            // Hide all tab panes
            const allPanes = document.querySelectorAll('.tab-pane');
            allPanes.forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Remove active class from all tab buttons
            const allButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
            allButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show target tab pane
            tabPane.classList.add('show', 'active');
            
            // Activate target tab button
            tabButton.classList.add('active');
            
            console.log(`✅ Successfully switched to tab: ${tabId}`);
            return true;
            
        } catch (error) {
            console.error(`❌ Manual tab switch failed for ${tabId}:`, error);
            return false;
        }
    }
    
    /**
     * Get all available tab information
     * @returns {Array} Array of tab information objects
     */
    getTabInfo() {
        try {
            const tabs = [];
            const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
            
            tabButtons.forEach((button, index) => {
                const targetId = button.getAttribute('data-bs-target');
                const tabId = button.id;
                
                tabs.push({
                    index,
                    buttonId: tabId,
                    targetId: targetId,
                    targetElement: targetId ? document.querySelector(targetId) : null,
                    isActive: button.classList.contains('active'),
                    isInitialized: !!button._tab,
                    hasFallbackHandler: !!button._fallbackHandler
                });
            });
            
            return tabs;
        } catch (error) {
            console.error('❌ Failed to get tab info:', error);
            return [];
        }
    }
    
    /**
     * Create a default AuthUIManager instance
     * @static
     * @returns {AuthUIManager} New instance with default config
     */
    static createDefault() {
        return new AuthUIManager({
            autoUpdate: true,
            showNotifications: true,
            debug: false
        });
    }
}
