/**
 * Authentication UI Manager
 * Handles dynamic UI updates based on authentication state
 * CACHE BUST: 2025-08-10-20:07
 */

export class AuthUIManager {
    constructor() {
        this.isInitialized = false;
        this.currentUser = null;
        this.isAuthenticated = false;
        this.authToken = null;
        
        // UI Elements
        this.authenticatedMenu = null;
        this.unauthenticatedMenu = null;
        this.userDisplayName = null;
        this.adminUsersLink = null;
        this.userTab = null;
        
        // Event listeners
        this.authStateChangeCallbacks = [];
    }

    /**
     * Initialize the Auth UI Manager
     */
    async init() {
        console.log('🔐 Initializing Auth UI Manager...');
        
        try {
            // Get UI elements
            this.getUIElements();
            
            // Check initial authentication state
            await this.checkAuthenticationState();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup authentication state monitoring
            this.setupAuthStateMonitoring();
            
            this.isInitialized = true;
            console.log('✅ Auth UI Manager initialized');
            
        } catch (error) {
            console.error('❌ Error initializing Auth UI Manager:', error);
        }
    }

    /**
     * Get UI elements
     */
    getUIElements() {
        // Check if we're on the auth page or main page
        const isAuthPage = window.location.pathname.includes('/auth');
        console.log('🔍 getUIElements called, isAuthPage:', isAuthPage);
        
        if (isAuthPage) {
            // On auth page - look for auth-specific elements
            this.authenticatedMenu = document.getElementById('authAuthenticatedMenu');
            this.unauthenticatedMenu = document.getElementById('authUnauthenticatedMenu');
            this.userDisplayName = document.getElementById('authUserDisplayName');
            this.adminUsersLink = document.getElementById('authAdminUsersLink');
            this.userTab = document.getElementById('authUserTab');
            
            // Also try to find main navigation elements (in case they exist)
            this.mainAuthenticatedMenu = document.getElementById('authenticatedMenu');
            this.mainUnauthenticatedMenu = document.getElementById('unauthenticatedMenu');
            this.mainUserDisplayName = document.getElementById('userDisplayName');
            this.mainAdminUsersLink = document.getElementById('adminUsersLink');
            this.mainUserTab = document.getElementById('userTab');
            
            console.log('🔐 Auth page detected - using auth-specific UI elements');
            console.log('🔍 Auth-specific elements found:', {
                authenticatedMenu: !!this.authenticatedMenu,
                unauthenticatedMenu: !!this.unauthenticatedMenu,
                userDisplayName: !!this.userDisplayName,
                adminUsersLink: !!this.adminUsersLink,
                userTab: !!this.userTab
            });
            console.log('🔍 Main navigation elements found:', {
                mainAuthenticatedMenu: !!this.mainAuthenticatedMenu,
                mainUnauthenticatedMenu: !!this.mainUnauthenticatedMenu,
                mainUserDisplayName: !!this.mainUserDisplayName,
                mainAdminUsersLink: !!this.mainAdminUsersLink,
                mainUserTab: !!this.mainUserTab
            });
        } else {
            // On main page - use main navigation elements
            this.authenticatedMenu = document.getElementById('authenticatedMenu');
            this.unauthenticatedMenu = document.getElementById('unauthenticatedMenu');
            this.userDisplayName = document.getElementById('userDisplayName');
            this.adminUsersLink = document.getElementById('adminUsersLink');
            this.userTab = document.getElementById('userTab');
            
            console.log('🏠 Main page detected - using main navigation elements');
            console.log('🔍 Main navigation elements found:', {
                authenticatedMenu: !!this.authenticatedMenu,
                unauthenticatedMenu: !!this.unauthenticatedMenu,
                userDisplayName: !!this.userDisplayName,
                adminUsersLink: !!this.adminUsersLink,
                userTab: !!this.userTab
            });
        }
        
        if (!this.authenticatedMenu || !this.unauthenticatedMenu) {
            console.warn('⚠️ Auth UI elements not found on current page');
            console.warn('⚠️ authenticatedMenu:', !!this.authenticatedMenu);
            console.warn('⚠️ unauthenticatedMenu:', !!this.unauthenticatedMenu);
        }
    }

    /**
     * Check current authentication state
     */
    async checkAuthenticationState() {
        try {
            console.log('🔍 Checking authentication state...');
            
            // Check for stored token
            this.authToken = this.getStoredToken();
            console.log('🔑 Stored token found:', this.authToken ? 'YES' : 'NO');
            
            if (this.authToken) {
                console.log('🔑 Token length:', this.authToken.length);
                console.log('🔑 Token preview:', this.authToken.substring(0, 20) + '...');
                
                // Validate token and get user info
                console.log('🔍 Validating token...');
                const user = await this.validateTokenAndGetUser(this.authToken);
                console.log('👤 User validation result:', user ? 'SUCCESS' : 'FAILED');
                
                if (user) {
                    console.log('✅ User authenticated:', user.username);
                    this.currentUser = user;
                    this.isAuthenticated = true;
                    this.updateUIForAuthenticatedUser();
                } else {
                    console.log('❌ Token validation failed, clearing state');
                    this.clearAuthenticationState();
                }
            } else {
                console.log('❌ No stored token found');
                this.updateUIForUnauthenticatedUser();
            }
        } catch (error) {
            console.error('❌ Error checking authentication state:', error);
            this.updateUIForUnauthenticatedUser();
        }
    }

    /**
     * Get stored authentication token
     */
    getStoredToken() {
        try {
            const localToken = localStorage.getItem('auth_token');
            const sessionToken = sessionStorage.getItem('auth_token');
            
            console.log('🔍 getStoredToken called:', { 
                localToken: !!localToken, 
                sessionToken: !!sessionToken,
                localTokenPreview: localToken ? localToken.substring(0, 20) + '...' : 'NO TOKEN',
                sessionTokenPreview: sessionToken ? sessionToken.substring(0, 20) + '...' : 'NO TOKEN'
            });
            
            const token = localToken || sessionToken;
            console.log('🔑 Returning token:', !!token);
            
            return token;
        } catch (error) {
            console.warn('⚠️ Could not get stored token:', error);
            return null;
        }
    }

    /**
     * Validate token and get user information
     */
    async validateTokenAndGetUser(token) {
        try {
            console.log('🔍 Making API call to /api/auth/check-auth...');
            console.log('🔑 Token being sent:', token.substring(0, 20) + '...');
            
            const response = await fetch('/api/auth/check-auth', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            console.log('📡 Response status:', response.status);
            console.log('📡 Response ok:', response.ok);

            if (response.ok) {
                const data = await response.json();
                console.log('📡 Response data:', data);
                
                if (data.authenticated && data.user) {
                    console.log('✅ User authenticated successfully:', data.user.username);
                    return data.user;
                } else {
                    console.warn('⚠️ User not authenticated in response');
                    console.warn('⚠️ Response data:', data);
                    return null;
                }
            } else {
                console.warn('⚠️ Token validation failed with status:', response.status);
                const errorText = await response.text();
                console.warn('⚠️ Error response:', errorText);
                return null;
            }
        } catch (error) {
            console.error('❌ Error validating token:', error);
            return null;
        }
    }

    /**
     * Update UI for authenticated user
     */
    updateUIForAuthenticatedUser() {
        console.log('✅ Updating UI for authenticated user...');
        console.log('🔍 Current user:', this.currentUser?.username);
        console.log('🔍 Available UI elements:', {
            authenticatedMenu: !!this.authenticatedMenu,
            unauthenticatedMenu: !!this.unauthenticatedMenu,
            mainAuthenticatedMenu: !!this.mainAuthenticatedMenu,
            mainUnauthenticatedMenu: !!this.mainUnauthenticatedMenu
        });
        
        try {
            // Update current page UI elements
            if (this.authenticatedMenu && this.unauthenticatedMenu) {
                this.authenticatedMenu.style.display = 'block';
                this.unauthenticatedMenu.style.display = 'none';
                console.log('✅ Current page UI updated');
            } else {
                console.warn('⚠️ Current page UI elements not available');
            }
            
            // Update main navigation UI elements (if they exist and we're on auth page)
            if (this.mainAuthenticatedMenu && this.mainUnauthenticatedMenu) {
                this.mainAuthenticatedMenu.style.display = 'block';
                this.mainUnauthenticatedMenu.style.display = 'none';
                console.log('✅ Main navigation UI updated');
            } else {
                console.warn('⚠️ Main navigation UI elements not available');
            }
            
            // Update user display name on both pages
            if (this.userDisplayName && this.currentUser) {
                this.userDisplayName.textContent = this.currentUser.username;
                console.log('✅ Current page user display name updated');
            }
            if (this.mainUserDisplayName && this.currentUser) {
                this.mainUserDisplayName.textContent = this.currentUser.username;
                console.log('✅ Main navigation user display name updated');
            }
            
            // Show/hide admin elements based on user role
            if (this.currentUser && this.currentUser.role === 'admin') {
                if (this.adminUsersLink) this.adminUsersLink.style.display = 'block';
                if (this.mainAdminUsersLink) this.mainAdminUsersLink.style.display = 'block';
                console.log('✅ Admin elements shown');
            }
            
            console.log('✅ UI updated for authenticated user');
            
        } catch (error) {
            console.error('❌ Error updating UI for authenticated user:', error);
        }
    }

    /**
     * Update UI for unauthenticated user
     */
    updateUIForUnauthenticatedUser() {
        console.log('❌ Updating UI for unauthenticated user...');
        
        try {
            // Update current page UI elements
            if (this.authenticatedMenu && this.unauthenticatedMenu) {
                this.authenticatedMenu.style.display = 'none';
                this.unauthenticatedMenu.style.display = 'block';
                console.log('✅ Current page UI updated');
            }
            
            // Update main navigation UI elements (if they exist and we're on auth page)
            if (this.mainAuthenticatedMenu && this.mainUnauthenticatedMenu) {
                this.mainAuthenticatedMenu.style.display = 'none';
                this.mainUnauthenticatedMenu.style.display = 'block';
                console.log('✅ Main navigation UI updated');
            }
            
            // Reset user display names
            if (this.userDisplayName) {
                this.userDisplayName.textContent = 'User';
            }
            if (this.mainUserDisplayName) {
                this.mainUserDisplayName.textContent = 'User';
            }
            
            // Hide admin elements
            if (this.adminUsersLink) this.adminUsersLink.style.display = 'none';
            if (this.mainAdminUsersLink) this.mainAdminUsersLink.style.display = 'none';
            
            console.log('✅ UI updated for unauthenticated user');
            
        } catch (error) {
            console.error('❌ Error updating UI for unauthenticated user:', error);
        }
    }

    /**
     * Clear authentication state
     */
    clearAuthenticationState() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.authToken = null;
        
        // Clear stored tokens
        try {
            localStorage.removeItem('auth_token');
            sessionStorage.removeItem('auth_token');
        } catch (error) {
            console.warn('⚠️ Could not clear stored tokens:', error);
        }
        
        // Update UI
        this.updateUIForUnauthenticatedUser();
        
        // Notify listeners
        this.notifyAuthStateChange();
    }

    /**
     * Handle user login
     */
    async handleUserLogin(user, token, rememberMe = false) {
        try {
            console.log('🔐 AuthUIManager.handleUserLogin called with:', { 
                username: user?.username, 
                tokenExists: !!token, 
                tokenPreview: token ? token.substring(0, 20) + '...' : 'NO TOKEN',
                rememberMe 
            });
            
            this.currentUser = user;
            this.isAuthenticated = true;
            this.authToken = token;
            
            console.log('✅ User state updated:', { 
                isAuthenticated: this.isAuthenticated, 
                username: this.currentUser?.username 
            });
            
            // Store token
            this.storeToken(token, rememberMe);
            console.log('💾 Token stored by AuthUIManager');
            
            // Update UI
            console.log('🎨 Updating UI for authenticated user...');
            this.updateUIForAuthenticatedUser();
            
            // Notify listeners
            this.notifyAuthStateChange();
            
            console.log('✅ User logged in successfully:', user.username);
            
        } catch (error) {
            console.error('❌ Error handling user login:', error);
        }
    }

    /**
     * Handle user logout
     */
    async handleUserLogout() {
        try {
            // Call logout API
            if (this.authToken) {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`
                    }
                });
            }
            
            // Clear local state
            this.clearAuthenticationState();
            
            console.log('✅ User logged out successfully');
            
        } catch (error) {
            console.error('❌ Error during logout:', error);
            // Still clear local state even if API call fails
            this.clearAuthenticationState();
        }
    }

    /**
     * Store authentication token
     */
    storeToken(token, rememberMe = false) {
        try {
            console.log('💾 storeToken called:', { 
                tokenExists: !!token, 
                rememberMe, 
                storageType: rememberMe ? 'localStorage' : 'sessionStorage' 
            });
            
            if (rememberMe) {
                localStorage.setItem('auth_token', token);
                console.log('💾 Token stored in localStorage');
            } else {
                sessionStorage.setItem('auth_token', token);
                console.log('💾 Token stored in sessionStorage');
            }
            
            // Verify storage
            const storedToken = rememberMe ? localStorage.getItem('auth_token') : sessionStorage.getItem('auth_token');
            console.log('✅ Token storage verified:', !!storedToken);
            
        } catch (error) {
            console.warn('⚠️ Could not store token:', error);
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for logout button clicks
        document.addEventListener('click', (event) => {
            if (event.target.closest('#logoutButton')) {
                event.preventDefault();
                this.handleUserLogout();
            }
        });
        
        // Listen for profile link clicks
        document.addEventListener('click', (event) => {
            if (event.target.closest('#authenticatedMenu a[href="/api/auth/"]')) {
                event.preventDefault();
                this.openUserProfile();
            }
        });
    }

    /**
     * Open user profile
     */
    openUserProfile() {
        try {
            // Open profile in new tab or redirect
            window.open('/api/auth/profile', '_blank');
        } catch (error) {
            console.error('❌ Error opening user profile:', error);
        }
    }

    /**
     * Setup authentication state monitoring
     */
    setupAuthStateMonitoring() {
        // Monitor storage changes (for multi-tab scenarios)
        window.addEventListener('storage', (event) => {
            if (event.key === 'auth_token') {
                this.checkAuthenticationState();
            }
        });
        
        // Monitor visibility changes to refresh auth state
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkAuthenticationState();
            }
        });
    }

    /**
     * Register callback for authentication state changes
     */
    onAuthStateChange(callback) {
        this.authStateChangeCallbacks.push(callback);
    }

    /**
     * Notify listeners of authentication state change
     */
    notifyAuthStateChange() {
        this.authStateChangeCallbacks.forEach(callback => {
            try {
                callback({
                    isAuthenticated: this.isAuthenticated,
                    currentUser: this.currentUser,
                    authToken: this.authToken
                });
            } catch (error) {
                console.error('❌ Error in auth state change callback:', error);
            }
        });
    }

    /**
     * Get current authentication state
     */
    getAuthState() {
        return {
            isAuthenticated: this.isAuthenticated,
            currentUser: this.currentUser,
            authToken: this.authToken
        };
    }

    /**
     * Check if user has specific permission
     */
    hasPermission(permission) {
        if (!this.isAuthenticated || !this.currentUser) {
            return false;
        }
        
        return this.currentUser.permissions?.includes(permission) || 
               this.currentUser.role === 'admin';
    }

    /**
     * Check if user has specific role
     */
    hasRole(role) {
        if (!this.isAuthenticated || !this.currentUser) {
            return false;
        }
        
        return this.currentUser.role === role || this.currentUser.role === 'admin';
    }

    /**
     * Check authentication state and update UI
     */
    async checkAuthenticationAndUpdateUI() {
        try {
            const token = this.getStoredToken();
            if (token) {
                const user = await this.validateTokenAndGetUser(token);
                if (user) {
                    await this.handleUserLogin(user, token);
                    return true;
                } else {
                    this.clearAuthenticationState();
                    return false;
                }
            } else {
                this.clearAuthenticationState();
                return false;
            }
        } catch (error) {
            console.error('❌ Error checking authentication:', error);
            this.clearAuthenticationState();
            return false;
        }
    }
    
    /**
     * Force update UI based on current authentication state
     */
    forceUpdateUI() {
        try {
            const token = this.getStoredToken();
            if (token && this.currentUser) {
                this.updateUIForAuthenticatedUser();
                return true;
            } else {
                this.updateUIForUnauthenticatedUser();
                return false;
            }
        } catch (error) {
            console.error('❌ Error forcing UI update:', error);
            this.updateUIForUnauthenticatedUser();
            return false;
        }
    }

    /**
     * Destroy the Auth UI Manager
     */
    destroy() {
        this.authStateChangeCallbacks = [];
        this.isInitialized = false;
        console.log('🗑️ Auth UI Manager destroyed');
    }
}

// Export for module usage
